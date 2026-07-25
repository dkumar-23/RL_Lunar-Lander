"""Validate and promote immutable Google Colab training artifact bundles."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from .configuration import ConfigurationError, configuration_sha256


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


CheckpointLoader = Callable[[Path], None]

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


def _default_checkpoint_loader(path: Path) -> None:
    try:
        import torch
    except ImportError as exc:
        raise ArtifactValidationError(
            "PyTorch is required to validate checkpoint loadability."
        ) from exc

    try:
        state = torch.load(path, map_location="cpu", weights_only=True)
    except Exception as exc:
        raise ArtifactValidationError(
            f"Checkpoint could not be loaded: {path}"
        ) from exc

    def check_finite(value: object) -> None:
        if isinstance(value, torch.Tensor) and not torch.isfinite(value).all().item():
            raise ArtifactValidationError(
                f"Checkpoint contains non-finite data: {path}"
            )
        if isinstance(value, Mapping):
            for child in value.values():
                check_finite(child)
        elif isinstance(value, (list, tuple)):
            for child in value:
                check_finite(child)

    check_finite(state)


class TrainingArtifactValidator:
    """Validate one immutable Colab training bundle.

    Args:
        checkpoint_loader: Checkpoint loadability validator. Production uses
            restrictive PyTorch loading; tests may inject a deterministic loader.
    """

    def __init__(self, checkpoint_loader: CheckpointLoader | None = None) -> None:
        self._checkpoint_loader = checkpoint_loader or _default_checkpoint_loader

    def validate(self, bundle: Path) -> ValidationReport:
        """Validate a bundle without mutating it."""
        bundle = bundle.resolve()
        issues: list[ValidationIssue] = []
        artifacts_checked = 0
        checkpoints_checked = 0
        experiment_id: str | None = None
        run_id: str | None = None
        manifest_hash: str | None = None

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
            if missing_fields:
                issue(
                    "manifest.fields",
                    f"Manifest is missing fields: {', '.join(missing_fields)}",
                )
            experiment_id = manifest.get("experiment_id")
            run_id = manifest.get("run_id")
            if not isinstance(experiment_id, str) or _EXPERIMENT_PATTERN.fullmatch(
                experiment_id
            ) is None:
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
            if not isinstance(expected_hash, str) or _SHA256_PATTERN.fullmatch(
                expected_hash
            ) is None:
                issue("artifact.sha256", f"Invalid hash for {relative_text}")
                continue
            if not isinstance(expected_size, int) or expected_size < 0:
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
                resolved_hash = configuration_sha256(config)
                if manifest.get("configuration_hash") != resolved_hash:
                    issue("configuration.hash", "Resolved configuration hash differs.")
            except ConfigurationError as exc:
                issue("configuration.invalid", str(exc))

        self._validate_csv(bundle / "metrics.csv", _METRIC_COLUMNS, issue)
        self._validate_csv(
            bundle / "episode_metrics.csv", _EPISODE_COLUMNS, issue
        )
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
                    self._checkpoint_loader(checkpoint)
                    checkpoints_checked += 1
                except Exception as exc:
                    issue("checkpoint.invalid", str(exc))

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
                relative = path.relative_to(bundle).as_posix()
                if relative not in declared and relative not in allowed_undeclared:
                    issue("bundle.undeclared", f"Undeclared file: {relative}")

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
