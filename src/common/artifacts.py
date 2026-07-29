"""Validate and promote immutable Google Colab training artifact bundles."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import shutil
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

import torch

from .checkpoint import LoadedCheckpoint, load_checkpoint
from .configuration import (
    ConfigurationError,
    resolve_configuration,
)


class ArtifactValidationError(RuntimeError):
    """Raised when an artifact operation cannot be completed safely."""


@dataclass(frozen=True)
class ValidationIssue:
    """One deterministic artifact validation failure."""

    code: str
    message: str


@dataclass(frozen=True)
class ValidationReport:
    """Immutable result of validating one imported training bundle."""

    valid: bool
    bundle: str
    experiment_id: str | None
    run_id: str | None
    manifest_sha256: str | None
    artifacts_checked: int
    checkpoints_checked: int
    issues: tuple[ValidationIssue, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable report."""
        data = asdict(self)
        data["issues"] = [asdict(issue) for issue in self.issues]
        return data


CheckpointLoader = Callable[[Path], LoadedCheckpoint]

_EXPERIMENT_PATTERN = re.compile(r"EXP-[0-9]{3}")
_RUN_PATTERN = re.compile(r"RUN-[0-9]{3}")
_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
_GIT_COMMIT_PATTERN = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")

_REQUIRED_PAYLOADS = {
    "resolved_config.yaml",
    "metrics.csv",
    "episode_metrics.csv",
    "checkpoints/best_checkpoint.pt",
    "checkpoints/final_checkpoint.pt",
    "training.log",
    "software_versions.json",
    "provenance.json",
}

_OPTIONAL_PAYLOADS: set[str] = {
    "checkpoints/best_moving_average_checkpoint.pt",
}

_METRIC_COLUMNS = {
    "global_step",
    "episode",
    "optimization_step",
    "loss",
    "mean_predicted_q",
    "epsilon",
    "learning_rate",
    "replay_size",
}

_EPISODE_COLUMNS = {
    "episode",
    "total_reward",
    "episode_length",
    "terminated",
    "truncated",
    "landing_success",
    "thruster_actions_selected",
    "thruster_actions_executed",
    "thruster_failures",
    "fuel_penalty_total",
    "landing_bonus_total",
    "mean_predicted_q",
    "epsilon",
    "duration_seconds",
}

_MANIFEST_FIELDS = {
    "schema_version",
    "experiment_id",
    "run_id",
    "algorithm",
    "environment_variant",
    "repository_url",
    "requested_git_commit",
    "resolved_git_commit",
    "git_worktree_clean",
    "configuration_path",
    "configuration_hash",
    "random_seed",
    "execution_platform",
    "started_at_utc",
    "completed_at_utc",
    "duration_seconds",
    "status",
    "best_checkpoint_selection_metric",
    "software_versions_path",
    "artifacts",
    "artifact_set_sha256",
}
_RESOLVED_FIELDS = {
    "experiment_id",
    "algorithm",
    "environment_variant",
    "training",
    "environment",
}
_ARTIFACT_FIELDS = {"path", "role", "size_bytes", "sha256"}
_REPOSITORY_URL = "https://github.com/dkumar-23/RL_Lunar-Lander"
_CANONICAL_IDENTITIES = {
    "EXP-001": ("DQN", "original"),
    "EXP-002": ("DQN", "modified"),
    "EXP-003": ("DDQN", "original"),
    "EXP-004": ("DDQN", "modified"),
}


def file_sha256(path: Path) -> str:
    """Compute SHA-256 over exact file bytes."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def artifact_set_sha256(artifacts: Sequence[Mapping[str, Any]]) -> str:
    """Hash a canonical path-sorted artifact entry collection."""
    normalized = sorted(
        (dict(item) for item in artifacts), key=lambda item: item["path"]
    )
    encoded = json.dumps(
        normalized,
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _safe_relative_path(value: object) -> PurePosixPath | None:
    if not isinstance(value, str) or not value or "\\" in value:
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        return None
    if path.as_posix() != value:
        return None
    return path


def _default_checkpoint_loader(path: Path) -> LoadedCheckpoint:
    return load_checkpoint(path, map_location="cpu")


def _validate_resolved_identity(
    values: Mapping[str, Any],
    manifest: Mapping[str, Any],
    issue: Callable[[str, str], None],
) -> dict[str, tuple[int, ...]] | None:
    if set(values) != _RESOLVED_FIELDS:
        issue("configuration.fields", "Resolved configuration fields are invalid.")
        return None
    training = values.get("training")
    environment = values.get("environment")
    if not isinstance(training, Mapping) or not isinstance(environment, Mapping):
        issue("configuration.sections", "Training and environment must be mappings.")
        return None
    comparisons = (
        ("experiment_id", values.get("experiment_id")),
        ("algorithm", values.get("algorithm")),
        ("environment_variant", values.get("environment_variant")),
        ("random_seed", training.get("random_seed")),
    )
    for field, configured in comparisons:
        if manifest.get(field) != configured:
            issue(
                f"configuration.{field}",
                f"Manifest {field} differs from resolved configuration.",
            )
    if environment.get("random_seed") != training.get("random_seed"):
        issue("configuration.seed", "Training and environment seeds differ.")
    if environment.get("environment_name") != "LunarLander-v3":
        issue("configuration.environment", "Unsupported canonical environment.")
        return None
    hidden_sizes = training.get("hidden_sizes")
    if not isinstance(hidden_sizes, list) or any(
        isinstance(size, bool) or not isinstance(size, int) or size <= 0
        for size in hidden_sizes
    ):
        issue("configuration.model", "hidden_sizes must contain positive integers.")
        return None
    dimensions = (8, *hidden_sizes, 4)
    shapes: dict[str, tuple[int, ...]] = {}
    for index, (input_width, output_width) in enumerate(
        zip(dimensions, dimensions[1:], strict=False)
    ):
        layer = index * 2
        shapes[f"network.{layer}.weight"] = (output_width, input_width)
        shapes[f"network.{layer}.bias"] = (output_width,)
    return shapes


def _validate_manifest_contract(
    manifest: Mapping[str, Any],
    issue: Callable[[str, str], None],
) -> None:
    """Apply the versioned manifest schema without permissive coercion."""
    experiment_id = manifest.get("experiment_id")
    identity = (manifest.get("algorithm"), manifest.get("environment_variant"))
    expected_identity = (
        _CANONICAL_IDENTITIES.get(experiment_id)
        if isinstance(experiment_id, str)
        else None
    )
    if expected_identity != identity:
        issue(
            "manifest.identity",
            "Experiment, algorithm, and variant are inconsistent.",
        )
    expected_literals = {
        "schema_version": "1.0.0",
        "repository_url": _REPOSITORY_URL,
        "configuration_path": "resolved_config.yaml",
        "execution_platform": "google-colab",
        "status": "COMPLETED",
        "software_versions_path": "software_versions.json",
    }
    for field, expected in expected_literals.items():
        if manifest.get(field) != expected:
            issue(f"manifest.{field}", f"Manifest {field} is invalid.")
    configuration_hash = manifest.get("configuration_hash")
    artifact_set_hash = manifest.get("artifact_set_sha256")
    for field, value in (
        ("configuration_hash", configuration_hash),
        ("artifact_set_sha256", artifact_set_hash),
    ):
        if not isinstance(value, str) or _SHA256_PATTERN.fullmatch(value) is None:
            issue(f"manifest.{field}", f"Manifest {field} must be SHA-256.")
    seed = manifest.get("random_seed")
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        issue("manifest.random_seed", "Manifest random_seed is invalid.")
    duration = manifest.get("duration_seconds")
    if (
        isinstance(duration, bool)
        or not isinstance(duration, (int, float))
        or not math.isfinite(float(duration))
        or duration < 0
    ):
        issue("manifest.duration", "Manifest duration_seconds is invalid.")
    for field in (
        "started_at_utc",
        "completed_at_utc",
        "best_checkpoint_selection_metric",
    ):
        value = manifest.get(field)
        if not isinstance(value, str) or not value:
            issue(f"manifest.{field}", f"Manifest {field} must be non-empty.")


def _validate_checkpoint_compatibility(
    checkpoint: LoadedCheckpoint,
    manifest: Mapping[str, Any],
    expected_shapes: Mapping[str, tuple[int, ...]],
) -> None:
    metadata = checkpoint.metadata
    comparisons = {
        "experiment_id": metadata.experiment_id,
        "run_id": metadata.run_id,
        "configuration_hash": metadata.configuration_hash,
        "random_seed": metadata.seed,
        "resolved_git_commit": metadata.git_sha,
    }
    for field, observed in comparisons.items():
        if manifest.get(field) != observed:
            raise ArtifactValidationError(
                f"Checkpoint {field} differs from the manifest."
            )
    for state_name, state in (
        ("model_state", checkpoint.model_state),
        ("target_state", checkpoint.target_state),
    ):
        if set(state) != set(expected_shapes):
            raise ArtifactValidationError(
                f"Checkpoint {state_name} parameter names are incompatible."
            )
        for name, expected_shape in expected_shapes.items():
            value = state[name]
            if not isinstance(value, torch.Tensor):
                raise ArtifactValidationError(
                    f"Checkpoint {state_name}.{name} is not a tensor."
                )
            if tuple(value.shape) != expected_shape:
                raise ArtifactValidationError(
                    f"Checkpoint {state_name}.{name} has incompatible dimensions."
                )
            if not bool(torch.isfinite(value).all().item()):
                raise ArtifactValidationError(
                    f"Checkpoint {state_name}.{name} contains non-finite values."
                )
    optimizer = checkpoint.optimizer_state
    if set(optimizer) != {"state", "param_groups"}:
        raise ArtifactValidationError("Checkpoint optimizer state is incompatible.")
    optimizer_state = optimizer["state"]
    parameter_groups = optimizer["param_groups"]
    if not isinstance(optimizer_state, Mapping) or not isinstance(
        parameter_groups, list
    ):
        raise ArtifactValidationError("Checkpoint optimizer structure is invalid.")
    parameter_ids: list[object] = []
    for group in parameter_groups:
        if not isinstance(group, Mapping) or not isinstance(group.get("params"), list):
            raise ArtifactValidationError(
                "Checkpoint optimizer parameter groups are invalid."
            )
        parameter_ids.extend(group["params"])
    if len(parameter_ids) != len(expected_shapes) or len(set(parameter_ids)) != len(
        parameter_ids
    ):
        raise ArtifactValidationError(
            "Checkpoint optimizer parameter count is incompatible."
        )
    if not set(optimizer_state).issubset(parameter_ids):
        raise ArtifactValidationError("Checkpoint optimizer parameter IDs are invalid.")
    _validate_finite_checkpoint_value(optimizer)
    scheduler = checkpoint.scheduler_state
    if scheduler is None or set(scheduler) != {"epsilon", "optimization_steps"}:
        raise ArtifactValidationError("Checkpoint scheduler state is incomplete.")
    epsilon = scheduler["epsilon"]
    optimization_steps = scheduler["optimization_steps"]
    if (
        isinstance(epsilon, bool)
        or not isinstance(epsilon, (int, float))
        or not math.isfinite(float(epsilon))
        or not 0.0 <= epsilon <= 1.0
    ):
        raise ArtifactValidationError("Checkpoint epsilon is invalid.")
    if (
        isinstance(optimization_steps, bool)
        or not isinstance(optimization_steps, int)
        or optimization_steps < 0
    ):
        raise ArtifactValidationError("Checkpoint optimization_steps is invalid.")


def _validate_finite_checkpoint_value(value: object) -> None:
    """Reject non-finite tensors nested in optimizer state."""
    if isinstance(value, torch.Tensor):
        if not bool(torch.isfinite(value).all().item()):
            raise ArtifactValidationError(
                "Checkpoint optimizer contains non-finite tensors."
            )
    elif isinstance(value, Mapping):
        for child in value.values():
            _validate_finite_checkpoint_value(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _validate_finite_checkpoint_value(child)


def _load_canonical_hashes(path: Path) -> dict[str, str]:
    """Load the tracked four-run registry used at the local trust boundary."""
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ArtifactValidationError(
            "Canonical configuration hash registry is unavailable."
        ) from exc
    if not isinstance(registry, dict) or set(registry) != {
        "schema_version",
        "experiments",
    }:
        raise ArtifactValidationError("Canonical hash registry fields are invalid.")
    experiments = registry.get("experiments")
    if registry.get("schema_version") != "1.0.0" or not isinstance(experiments, dict):
        raise ArtifactValidationError("Canonical hash registry schema is invalid.")
    if set(experiments) != set(_CANONICAL_IDENTITIES):
        raise ArtifactValidationError("Canonical hash registry must contain four runs.")
    hashes: dict[str, str] = {}
    for experiment_id, entry in experiments.items():
        if not isinstance(entry, dict) or set(entry) != {
            "configuration_path",
            "resolved_configuration_sha256",
        }:
            raise ArtifactValidationError("Canonical hash registry entry is invalid.")
        digest = entry.get("resolved_configuration_sha256")
        if not isinstance(digest, str) or _SHA256_PATTERN.fullmatch(digest) is None:
            raise ArtifactValidationError("Canonical configuration hash is invalid.")
        hashes[experiment_id] = digest
    return hashes


def _validate_completion_progress(
    bundle: Path,
    expected_episodes: int,
    checkpoints: Mapping[str, LoadedCheckpoint],
    issue: Callable[[str, str], None],
) -> None:
    """Require terminal metrics and checkpoint progress to prove full duration."""
    try:
        with (bundle / "episode_metrics.csv").open(
            "r", encoding="utf-8", newline=""
        ) as stream:
            episode_rows = list(csv.DictReader(stream))
        with (bundle / "metrics.csv").open("r", encoding="utf-8", newline="") as stream:
            optimization_rows = list(csv.DictReader(stream))
        episode_numbers = [int(row["episode"]) for row in episode_rows]
        optimization_episodes = [int(row["episode"]) for row in optimization_rows]
        episode_lengths = [int(row["episode_length"]) for row in episode_rows]
        metric_global_steps = [int(row["global_step"]) for row in optimization_rows]
    except (OSError, KeyError, TypeError, ValueError) as exc:
        issue("progress.metrics", f"Unable to validate training progress: {exc}")
        return
    expected_sequence = list(range(1, expected_episodes + 1))
    if (
        episode_numbers != expected_sequence
        or optimization_episodes != expected_sequence
    ):
        issue(
            "progress.episodes",
            "Training metrics do not cover every configured episode.",
        )
    final = checkpoints.get("final_checkpoint.pt")
    best = checkpoints.get("best_checkpoint.pt")
    if final is None or best is None:
        return
    if final.metadata.episode != expected_episodes:
        issue(
            "progress.final_episode",
            "Final checkpoint is not from the last episode.",
        )
    if not 1 <= best.metadata.episode <= expected_episodes:
        issue("progress.best_episode", "Best checkpoint episode is out of range.")
    if metric_global_steps:
        expected_global_steps = sum(episode_lengths)
        if (
            final.metadata.global_step != expected_global_steps
            or metric_global_steps[-1] != expected_global_steps
        ):
            issue(
                "progress.global_steps",
                "Final checkpoint and metrics global steps are inconsistent.",
            )


class TrainingArtifactValidator:
    """Validate one immutable Colab training bundle.

    Args:
        checkpoint_loader: Checkpoint loadability validator. Production uses
            restrictive PyTorch loading; tests may inject a deterministic loader.
    """

    def __init__(
        self,
        checkpoint_loader: CheckpointLoader | None = None,
        canonical_hashes: Mapping[str, str] | None = None,
    ) -> None:
        self._checkpoint_loader = checkpoint_loader or _default_checkpoint_loader
        self._canonical_hashes = (
            dict(canonical_hashes)
            if canonical_hashes is not None
            else _load_canonical_hashes(Path("experiments/canonical_hashes.json"))
        )

    def validate(self, bundle: Path) -> ValidationReport:
        """Validate a bundle without mutating it."""
        bundle = bundle.resolve()
        issues: list[ValidationIssue] = []
        artifacts_checked = 0
        checkpoints_checked = 0
        experiment_id: str | None = None
        run_id: str | None = None
        manifest_hash: str | None = None
        resolved_values: Mapping[str, Any] | None = None
        expected_shapes: dict[str, tuple[int, ...]] | None = None
        expected_episodes: int | None = None
        loaded_checkpoints: dict[str, LoadedCheckpoint] = {}

        def issue(code: str, message: str) -> None:
            issues.append(ValidationIssue(code, message))

        if not bundle.is_dir():
            issue("bundle.missing", f"Bundle directory does not exist: {bundle}")
            return ValidationReport(
                False, str(bundle), None, None, None, 0, 0, tuple(issues)
            )

        completed = bundle / "status" / "COMPLETED.json"
        failed = bundle / "status" / "FAILED.json"
        if completed.is_file() == failed.is_file():
            issue(
                "status.invalid",
                "Bundle must contain exactly one COMPLETED.json or FAILED.json marker.",
            )
        if failed.is_file():
            issue("status.failed", "Failed training bundles cannot be promoted.")

        manifest_path = bundle / "manifest.json"
        manifest: dict[str, Any] = {}
        if not manifest_path.is_file():
            issue("manifest.missing", "manifest.json is required.")
        else:
            manifest_hash = file_sha256(manifest_path)
            try:
                loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
                if not isinstance(loaded, dict):
                    raise TypeError("manifest root must be an object")
                manifest = loaded
            except (OSError, UnicodeError, json.JSONDecodeError, TypeError) as exc:
                issue("manifest.invalid", f"Unable to parse manifest.json: {exc}")

        if manifest:
            missing_fields = sorted(_MANIFEST_FIELDS - manifest.keys())
            extra_fields = sorted(manifest.keys() - _MANIFEST_FIELDS)
            if missing_fields or extra_fields:
                issue(
                    "manifest.fields",
                    "Manifest fields differ from schema; "
                    f"missing={missing_fields}, extra={extra_fields}",
                )
            _validate_manifest_contract(manifest, issue)
            experiment_id = manifest.get("experiment_id")
            run_id = manifest.get("run_id")
            if (
                not isinstance(experiment_id, str)
                or _EXPERIMENT_PATTERN.fullmatch(experiment_id) is None
            ):
                issue("manifest.experiment", "Invalid experiment_id.")
            if not isinstance(run_id, str) or _RUN_PATTERN.fullmatch(run_id) is None:
                issue("manifest.run", "Invalid run_id.")
            if manifest.get("execution_platform") != "google-colab":
                issue("manifest.platform", "execution_platform must be google-colab.")
            if manifest.get("status") != "COMPLETED":
                issue("manifest.status", "Manifest status must be COMPLETED.")
            requested_commit = manifest.get("requested_git_commit")
            resolved_commit = manifest.get("resolved_git_commit")
            if (
                not isinstance(requested_commit, str)
                or _GIT_COMMIT_PATTERN.fullmatch(requested_commit) is None
                or requested_commit != resolved_commit
            ):
                issue(
                    "manifest.commit",
                    "Requested and resolved exact Git commits must match.",
                )
            if manifest.get("git_worktree_clean") is not True:
                issue("manifest.worktree", "Training worktree must be recorded clean.")

        if completed.is_file() and manifest_hash is not None:
            try:
                marker = json.loads(completed.read_text(encoding="utf-8"))
                if not isinstance(marker, dict):
                    raise TypeError("completion marker root must be an object")
                if marker.get("manifest_sha256") != manifest_hash:
                    issue(
                        "status.hash",
                        "Completion marker manifest hash does not match.",
                    )
                if marker.get("experiment_id") != experiment_id:
                    issue("status.experiment", "Completion marker experiment differs.")
                if marker.get("run_id") != run_id:
                    issue("status.run", "Completion marker run differs.")
            except (OSError, UnicodeError, json.JSONDecodeError, TypeError) as exc:
                issue("status.marker", f"Invalid completion marker: {exc}")

        artifact_entries = manifest.get("artifacts", []) if manifest else []
        if not isinstance(artifact_entries, list):
            issue("artifacts.type", "Manifest artifacts must be an array.")
            artifact_entries = []

        declared: set[str] = set()
        valid_entries: list[dict[str, Any]] = []
        for entry in artifact_entries:
            if not isinstance(entry, dict):
                issue("artifact.entry", "Every artifact entry must be an object.")
                continue
            if set(entry) != _ARTIFACT_FIELDS:
                issue("artifact.fields", "Artifact entry fields are invalid.")
                continue
            role = entry.get("role")
            if not isinstance(role, str) or not role:
                issue("artifact.role", "Artifact role must be non-empty.")
                continue
            relative = _safe_relative_path(entry.get("path"))
            if relative is None:
                issue("artifact.path", f"Unsafe artifact path: {entry.get('path')!r}")
                continue
            relative_text = relative.as_posix()
            if relative_text in declared:
                issue("artifact.duplicate", f"Duplicate artifact: {relative_text}")
                continue
            declared.add(relative_text)
            expected_hash = entry.get("sha256")
            expected_size = entry.get("size_bytes")
            if (
                not isinstance(expected_hash, str)
                or _SHA256_PATTERN.fullmatch(expected_hash) is None
            ):
                issue("artifact.sha256", f"Invalid hash for {relative_text}")
                continue
            if (
                isinstance(expected_size, bool)
                or not isinstance(expected_size, int)
                or expected_size < 0
            ):
                issue("artifact.size", f"Invalid size for {relative_text}")
                continue

            path = bundle.joinpath(*relative.parts)
            if path.is_symlink() or not path.is_file():
                issue(
                    "artifact.missing",
                    f"Artifact is missing or unsafe: {relative_text}",
                )
                continue
            if path.stat().st_size != expected_size:
                issue("artifact.size_mismatch", f"Size mismatch: {relative_text}")
            if file_sha256(path) != expected_hash:
                issue("artifact.hash_mismatch", f"Hash mismatch: {relative_text}")
            valid_entries.append(entry)
            artifacts_checked += 1

        missing_payloads = sorted(_REQUIRED_PAYLOADS - declared)
        if missing_payloads:
            issue(
                "artifacts.required",
                f"Required artifacts are undeclared: {', '.join(missing_payloads)}",
            )

        if manifest:
            set_hash = manifest.get("artifact_set_sha256")
            if not isinstance(set_hash, str) or set_hash != artifact_set_sha256(
                valid_entries
            ):
                issue("artifacts.set_hash", "Artifact-set hash does not match.")

        config = bundle / "resolved_config.yaml"
        if config.is_file() and manifest:
            try:
                resolved = resolve_configuration(config)
                resolved_hash = resolved.sha256
                if manifest.get("configuration_hash") != resolved_hash:
                    issue("configuration.hash", "Resolved configuration hash differs.")
                resolved_values = resolved.values
                expected_shapes = _validate_resolved_identity(
                    resolved_values, manifest, issue
                )
                expected_hash = self._canonical_hashes.get(str(experiment_id))
                if self._canonical_hashes and expected_hash != resolved_hash:
                    issue(
                        "configuration.canonical_hash",
                        "Resolved configuration is not preregistered.",
                    )
                training = resolved_values.get("training")
                episodes = (
                    training.get("episodes") if isinstance(training, Mapping) else None
                )
                if (
                    isinstance(episodes, bool)
                    or not isinstance(episodes, int)
                    or episodes <= 0
                ):
                    issue("configuration.episodes", "Training episodes are invalid.")
                else:
                    expected_episodes = episodes
            except ConfigurationError as exc:
                issue("configuration.invalid", str(exc))

        self._validate_csv(bundle / "metrics.csv", _METRIC_COLUMNS, issue)
        self._validate_csv(bundle / "episode_metrics.csv", _EPISODE_COLUMNS, issue)
        self._validate_integrity_file(
            bundle,
            declared | ({"manifest.json"} if manifest_path.is_file() else set()),
            issue,
        )

        for checkpoint in (
            bundle / "checkpoints" / "best_checkpoint.pt",
            bundle / "checkpoints" / "final_checkpoint.pt",
        ):
            if checkpoint.is_file():
                try:
                    loaded_checkpoint = self._checkpoint_loader(checkpoint)
                    if expected_shapes is None or resolved_values is None:
                        raise ArtifactValidationError(
                            "Resolved configuration is unavailable for checkpoint "
                            "validation."
                        )
                    _validate_checkpoint_compatibility(
                        loaded_checkpoint,
                        manifest,
                        expected_shapes,
                    )
                    loaded_checkpoints[checkpoint.name] = loaded_checkpoint
                    checkpoints_checked += 1
                except Exception as exc:
                    issue("checkpoint.invalid", str(exc))

        if expected_episodes is not None:
            _validate_completion_progress(
                bundle,
                expected_episodes,
                loaded_checkpoints,
                issue,
            )

        allowed_undeclared = {
            "manifest.json",
            "integrity.sha256",
            "status/COMPLETED.json",
            "status/FAILED.json",
        }
        for path in bundle.rglob("*"):
            if path.is_symlink():
                issue("bundle.symlink", f"Symlinks are prohibited: {path}")
            if path.is_file():
                relative_file = path.relative_to(bundle).as_posix()
                if (
                    relative_file not in declared
                    and relative_file not in allowed_undeclared
                ):
                    issue("bundle.undeclared", f"Undeclared file: {relative_file}")

        return ValidationReport(
            not issues,
            str(bundle),
            experiment_id,
            run_id,
            manifest_hash,
            artifacts_checked,
            checkpoints_checked,
            tuple(issues),
        )

    @staticmethod
    def _validate_csv(
        path: Path,
        required_columns: set[str],
        issue: Callable[[str, str], None],
    ) -> None:
        if not path.is_file():
            return
        try:
            with path.open("r", encoding="utf-8", newline="") as stream:
                reader = csv.DictReader(stream)
                columns = set(reader.fieldnames or [])
                missing = sorted(required_columns - columns)
                if missing:
                    issue(
                        "metrics.columns",
                        f"{path.name} is missing columns: {', '.join(missing)}",
                    )
                if next(reader, None) is None:
                    issue("metrics.empty", f"{path.name} contains no data rows.")
        except (OSError, UnicodeError, csv.Error) as exc:
            issue("metrics.invalid", f"Unable to read {path.name}: {exc}")

    @staticmethod
    def _validate_integrity_file(
        bundle: Path,
        expected_paths: set[str],
        issue: Callable[[str, str], None],
    ) -> None:
        integrity = bundle / "integrity.sha256"
        if not integrity.is_file():
            issue("integrity.missing", "integrity.sha256 is required.")
            return
        observed: set[str] = set()
        try:
            for line in integrity.read_text(encoding="ascii").splitlines():
                parts = line.split("  ", maxsplit=1)
                if len(parts) != 2 or _SHA256_PATTERN.fullmatch(parts[0]) is None:
                    issue("integrity.format", f"Invalid integrity line: {line!r}")
                    continue
                relative = _safe_relative_path(parts[1])
                if relative is None:
                    issue("integrity.path", f"Unsafe integrity path: {parts[1]!r}")
                    continue
                relative_text = relative.as_posix()
                path = bundle.joinpath(*relative.parts)
                if relative_text in observed:
                    issue("integrity.duplicate", f"Duplicate hash: {relative_text}")
                    continue
                observed.add(relative_text)
                if not path.is_file() or file_sha256(path) != parts[0]:
                    issue("integrity.mismatch", f"Integrity mismatch: {relative_text}")
        except (OSError, UnicodeError) as exc:
            issue("integrity.invalid", f"Unable to read integrity.sha256: {exc}")
            return

        missing = sorted(expected_paths - observed)
        if missing:
            issue(
                "integrity.coverage",
                f"Integrity hashes missing: {', '.join(missing)}",
            )

    @staticmethod
    def write_report(report: ValidationReport, destination: Path) -> None:
        """Atomically write a validation report outside the imported bundle."""
        destination = destination.resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        temporary.write_text(
            json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(destination)

    @staticmethod
    def promote(report: ValidationReport, destination: Path) -> None:
        """Copy a valid immutable bundle to a new promotion destination."""
        if not report.valid:
            raise ArtifactValidationError("An invalid bundle cannot be promoted.")
        source = Path(report.bundle)
        destination = destination.resolve()
        if destination.exists():
            raise ArtifactValidationError(
                f"Promotion destination already exists: {destination}"
            )
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, destination, symlinks=False)
