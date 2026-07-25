"""Strict report-asset tables and hashing from persisted downstream evidence."""

from __future__ import annotations

import csv
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.common import TrainingArtifactValidator, file_sha256, resolve_configuration
from src.evaluation import ValidatedBundle, require_validated_bundle


class ReportingError(RuntimeError):
    """Raised instead of generating unsupported or incomplete report claims."""


@dataclass(frozen=True)
class ReportInputs:
    """Explicit persisted evidence roots consumed by report generation."""

    bundles: tuple[Path, ...]
    validated_root: Path
    validation_root: Path
    evaluation_root: Path
    plot_root: Path
    output_root: Path


_CANONICAL = {
    "EXP-001": ("DQN", "original"),
    "EXP-002": ("DQN", "modified"),
    "EXP-003": ("DDQN", "original"),
    "EXP-004": ("DDQN", "modified"),
}
_PLOT_STEMS = (
    "episode_reward",
    "average_predicted_q",
    "landing_success_100_episode_moving",
    "average_thruster_activations",
)


class ReportingEngine:
    """Generate factual tables and a complete hash-aware asset manifest."""

    def __init__(
        self,
        inputs: ReportInputs,
        *,
        validator: TrainingArtifactValidator | None = None,
    ) -> None:
        """Store source locations without creating report outputs."""
        self._inputs = inputs
        self._validator = validator

    def generate(self) -> tuple[Path, ...]:
        """Validate complete evidence, then generate tables and asset index."""
        bundles = self._load_bundles()
        training_controls = self._load_training_controls(bundles)
        summaries = self._load_summaries(bundles)
        evaluation_metrics = self._require_evaluation_metrics(bundles, summaries)
        plots = self._load_plots()

        try:
            self._inputs.output_root.mkdir(parents=True, exist_ok=False)
        except FileExistsError as exc:
            raise ReportingError(
                "Report output already exists and will not be overwritten: "
                f"{self._inputs.output_root}"
            ) from exc
        experiment_table = self._inputs.output_root / "experiment_table.csv"
        hyperparameter_table = self._inputs.output_root / "hyperparameter_table.csv"
        evaluation_table = self._inputs.output_root / "evaluation_table.csv"
        _write_csv(
            experiment_table,
            (
                "experiment_id",
                "run_id",
                "algorithm",
                "environment_variant",
                "configuration_hash",
                "git_commit",
                "random_seed",
                "execution_platform",
                "manifest_sha256",
            ),
            [
                {
                    "experiment_id": item.experiment_id,
                    "run_id": item.run_id,
                    "algorithm": item.manifest["algorithm"],
                    "environment_variant": item.manifest["environment_variant"],
                    "configuration_hash": item.manifest["configuration_hash"],
                    "git_commit": item.manifest["resolved_git_commit"],
                    "random_seed": item.manifest["random_seed"],
                    "execution_platform": item.manifest["execution_platform"],
                    "manifest_sha256": item.manifest_sha256,
                }
                for item in bundles
            ],
        )
        training_fields = tuple(sorted(training_controls[0]))
        _write_csv(
            hyperparameter_table,
            ("experiment_id", "run_id", *training_fields),
            [
                {
                    "experiment_id": bundle.experiment_id,
                    "run_id": bundle.run_id,
                    **{field: _csv_value(controls[field]) for field in training_fields},
                }
                for bundle, controls in zip(bundles, training_controls, strict=True)
            ],
        )
        evaluation_fields = (
            "experiment_id",
            "run_id",
            "algorithm",
            "environment_variant",
            "episode_count",
            "reward_mean",
            "reward_median",
            "reward_minimum",
            "reward_maximum",
            "reward_variance",
            "reward_standard_deviation",
            "success_rate",
            "episode_length_mean",
            "q_mean",
            "source_manifest_sha256",
            "checkpoint",
        )
        _write_csv(
            evaluation_table,
            evaluation_fields,
            [
                {field: summary[field] for field in evaluation_fields}
                for summary in summaries
            ],
        )

        assets: list[tuple[Path, str, str, str | None, str | None]] = []
        for bundle in bundles:
            assets.append(
                (
                    bundle.path / "manifest.json",
                    f"training/{bundle.experiment_id}/{bundle.run_id}/manifest.json",
                    "training_manifest",
                    bundle.experiment_id,
                    bundle.run_id,
                )
            )
        for path, bundle in zip(evaluation_metrics, bundles, strict=True):
            assets.append(
                (
                    path,
                    f"evaluation/{bundle.experiment_id}/{bundle.run_id}/{path.name}",
                    "evaluation_metrics",
                    bundle.experiment_id,
                    bundle.run_id,
                )
            )
            assets.append(
                (
                    path.parent / "evaluation_summary.json",
                    f"evaluation/{bundle.experiment_id}/{bundle.run_id}/evaluation_summary.json",
                    "evaluation_summary",
                    bundle.experiment_id,
                    bundle.run_id,
                )
            )
        assets.extend(
            (path, f"plots/{path.name}", "assignment_plot", None, None)
            for path in plots
        )
        assets.extend(
            (
                (
                    experiment_table,
                    f"report/{experiment_table.name}",
                    "report_table",
                    None,
                    None,
                ),
                (
                    hyperparameter_table,
                    f"report/{hyperparameter_table.name}",
                    "report_table",
                    None,
                    None,
                ),
                (
                    evaluation_table,
                    f"report/{evaluation_table.name}",
                    "report_table",
                    None,
                    None,
                ),
            )
        )
        manifest_path = self._inputs.output_root / "asset_manifest.json"
        payload = {
            "schema_version": "1.0.0",
            "complete": True,
            "canonical_experiments": list(_CANONICAL),
            "assets": [
                {
                    "path": logical_path,
                    "role": role,
                    "experiment_id": experiment_id,
                    "run_id": run_id,
                    "size_bytes": path.stat().st_size,
                    "sha256": file_sha256(path),
                }
                for path, logical_path, role, experiment_id, run_id in sorted(
                    assets, key=lambda item: item[1]
                )
            ],
        }
        _write_json(manifest_path, payload)
        return experiment_table, hyperparameter_table, evaluation_table, manifest_path

    def _load_bundles(self) -> tuple[ValidatedBundle, ...]:
        if len(self._inputs.bundles) != len(_CANONICAL):
            raise ReportingError("Exactly four canonical bundles are required.")
        loaded: dict[str, ValidatedBundle] = {}
        for path in self._inputs.bundles:
            bundle = require_validated_bundle(
                path,
                validated_root=self._inputs.validated_root,
                validation_root=self._inputs.validation_root,
                validator=self._validator,
            )
            if bundle.experiment_id not in _CANONICAL or bundle.experiment_id in loaded:
                raise ReportingError(
                    "Canonical experiments must be unique EXP-001-004."
                )
            expected = _CANONICAL[bundle.experiment_id]
            observed = (
                bundle.manifest.get("algorithm"),
                bundle.manifest.get("environment_variant"),
            )
            if observed != expected:
                raise ReportingError(
                    f"Canonical identity mismatch for {bundle.experiment_id}."
                )
            loaded[bundle.experiment_id] = bundle
        return tuple(loaded[key] for key in _CANONICAL)

    @staticmethod
    def _load_training_controls(
        bundles: Sequence[ValidatedBundle],
    ) -> tuple[Mapping[str, Any], ...]:
        controls: list[Mapping[str, Any]] = []
        fingerprints: set[str] = set()
        seeds: set[object] = set()
        for bundle in bundles:
            resolved = resolve_configuration(bundle.path / "resolved_config.yaml")
            training = resolved.values.get("training")
            if not isinstance(training, Mapping) or not training:
                raise ReportingError(
                    f"Training configuration is missing: {bundle.path}"
                )
            normalized = dict(training)
            fingerprints.add(
                json.dumps(normalized, sort_keys=True, separators=(",", ":"))
            )
            configured_seed = normalized.get("random_seed")
            manifest_seed = bundle.manifest.get("random_seed")
            if configured_seed != manifest_seed:
                raise ReportingError(
                    f"Training seed provenance mismatch: {bundle.path}"
                )
            seeds.add(manifest_seed)
            controls.append(normalized)
        if len(fingerprints) != 1 or len(seeds) != 1:
            raise ReportingError(
                "Canonical experiments do not share identical training controls."
            )
        return tuple(controls)

    def _load_summaries(
        self, bundles: Sequence[ValidatedBundle]
    ) -> tuple[Mapping[str, Any], ...]:
        summaries: list[Mapping[str, Any]] = []
        required = {
            "experiment_id",
            "run_id",
            "algorithm",
            "environment_variant",
            "episode_count",
            "reward_mean",
            "reward_median",
            "reward_minimum",
            "reward_maximum",
            "reward_variance",
            "reward_standard_deviation",
            "success_rate",
            "episode_length_mean",
            "q_mean",
            "source_manifest_sha256",
            "checkpoint",
            "parameters_unchanged",
        }
        for bundle in bundles:
            path = (
                self._inputs.evaluation_root
                / bundle.experiment_id
                / bundle.run_id
                / "evaluation_summary.json"
            )
            summary = _read_object(path, "evaluation summary")
            if required - summary.keys():
                raise ReportingError(f"Evaluation summary is incomplete: {path}")
            if (
                summary["experiment_id"] != bundle.experiment_id
                or summary["run_id"] != bundle.run_id
                or summary["source_manifest_sha256"] != bundle.manifest_sha256
                or summary["algorithm"] != bundle.manifest["algorithm"]
                or summary["environment_variant"]
                != bundle.manifest["environment_variant"]
                or summary["parameters_unchanged"] is not True
            ):
                raise ReportingError(f"Evaluation summary provenance mismatch: {path}")
            summaries.append(summary)
        return tuple(summaries)

    def _require_evaluation_metrics(
        self,
        bundles: Sequence[ValidatedBundle],
        summaries: Sequence[Mapping[str, Any]],
    ) -> tuple[Path, ...]:
        paths: list[Path] = []
        required = {
            "experiment_id",
            "run_id",
            "source_manifest_sha256",
            "episode",
            "total_reward",
            "episode_length",
            "landing_success",
            "mean_selected_q",
        }
        for bundle, summary in zip(bundles, summaries, strict=True):
            path = (
                self._inputs.evaluation_root
                / bundle.experiment_id
                / bundle.run_id
                / "evaluation_metrics.csv"
            )
            if path.is_symlink() or not path.is_file() or path.stat().st_size == 0:
                raise ReportingError(f"Missing evaluation metrics: {path}")
            try:
                with path.open("r", encoding="utf-8", newline="") as stream:
                    reader = csv.DictReader(stream)
                    if required - set(reader.fieldnames or ()):
                        raise ReportingError(
                            f"Evaluation metrics are incomplete: {path}"
                        )
                    rows = list(reader)
            except (OSError, UnicodeError, csv.Error) as exc:
                raise ReportingError(
                    f"Unable to read evaluation metrics: {path}"
                ) from exc
            if len(rows) != summary["episode_count"]:
                raise ReportingError(f"Evaluation metric count mismatch: {path}")
            if any(
                row["experiment_id"] != bundle.experiment_id
                or row["run_id"] != bundle.run_id
                or row["source_manifest_sha256"] != bundle.manifest_sha256
                for row in rows
            ):
                raise ReportingError(f"Evaluation metric provenance mismatch: {path}")
            paths.append(path)
        return tuple(paths)

    def _load_plots(self) -> tuple[Path, ...]:
        plots: list[Path] = []
        for stem in _PLOT_STEMS:
            matches = tuple(
                path
                for suffix in ("png", "pdf", "svg")
                if (path := self._inputs.plot_root / f"{stem}.{suffix}").is_file()
                and not path.is_symlink()
                and path.stat().st_size > 0
            )
            if not matches:
                raise ReportingError(f"Missing assignment plot: {stem}")
            plots.extend(matches)
        return tuple(plots)


def _read_object(path: Path, description: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ReportingError(f"Missing {description}: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReportingError(f"Unable to read {description}: {path}") from exc
    if not isinstance(value, dict):
        raise ReportingError(f"{description.capitalize()} must be a JSON object.")
    return value


def _write_csv(
    path: Path,
    fieldnames: Sequence[str],
    rows: Sequence[Mapping[str, object]],
) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, value: Mapping[str, object]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(dict(value), indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _csv_value(value: object) -> object:
    if isinstance(value, (list, dict)):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    return value
