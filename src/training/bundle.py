"""Creation of complete, integrity-protected Colab training bundles."""

from __future__ import annotations

import csv
import json
import logging
import time
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import torch
import yaml

from src.agents import BaseAgent
from src.common import (
    RunMetadata,
    artifact_set_sha256,
    capture_software_metadata,
    configuration_sha256,
    file_sha256,
    get_logger,
    save_checkpoint,
)

from .config import ExperimentConfig
from .engine import TrainingResult
from .runtime_guard import ColabTrainingAttestation, ExecutionBoundaryError
from .validation import FixedValidationSet


def utc_now() -> str:
    """Return a stable ISO-8601 UTC timestamp."""
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


class ColabBundleWriter:
    """Persist one non-overwriting canonical run beneath Google Drive."""

    def __init__(
        self,
        root: Path,
        experiment: ExperimentConfig,
        run_id: str,
        repository_url: str,
        git_commit: str,
        expected_configuration_hash: str,
        agent: BaseAgent,
        validation_set: FixedValidationSet,
        attestation: ColabTrainingAttestation,
    ) -> None:
        """Create an empty run directory and immutable run identity files.

        Raises:
            FileExistsError: The requested run destination already exists.
        """
        self.root = root.resolve()
        if attestation.git_commit != git_commit:
            raise ExecutionBoundaryError(
                "Bundle commit differs from the Colab runtime attestation."
            )
        if attestation.drive_root not in (self.root, *self.root.parents):
            raise ExecutionBoundaryError(
                "Bundle destination is outside the attested Google Drive root."
            )
        self.experiment = experiment
        self.run_id = run_id
        self.repository_url = repository_url
        self.git_commit = git_commit
        self.expected_configuration_hash = expected_configuration_hash
        self.agent = agent
        self.validation_set = validation_set
        self.started_at = utc_now()
        self.started_monotonic = time.monotonic()
        self.root.mkdir(parents=True, exist_ok=False)
        (self.root / "checkpoints").mkdir()
        (self.root / "status").mkdir()
        self._write_resolved_configuration()
        self.configuration_hash = configuration_sha256(
            self.root / "resolved_config.yaml"
        )
        if self.configuration_hash != self.expected_configuration_hash:
            raise ValueError("Persisted configuration differs from preregistration.")
        self._write_validation_set()
        self._write_provenance()
        self._write_software_versions()
        self.logger = get_logger(
            f"training.{experiment.experiment_id}.{run_id}",
            level=logging.INFO,
            format_string="%(asctime)s %(levelname)s %(message)s",
            console=True,
            file_path=self.root / "training.log",
        )

    def save_checkpoint(
        self,
        kind: str,
        episode: int,
        global_step: int,
        extra_scheduler_state: dict[str, object] | None = None,
    ) -> None:
        """Save a best, best_moving_average, periodic, or final checkpoint."""
        if kind == "best":
            name = "best_checkpoint.pt"
        elif kind == "best_moving_average":
            name = "best_moving_average_checkpoint.pt"
        elif kind == "final":
            name = "final_checkpoint.pt"
        elif kind == "periodic":
            name = f"episode_{episode:04d}_checkpoint.pt"
        else:
            raise ValueError(f"Unsupported checkpoint kind: {kind}")
        metadata = RunMetadata(
            experiment_id=self.experiment.experiment_id,
            run_id=self.run_id,
            episode=episode,
            global_step=global_step,
            configuration_hash=self.configuration_hash,
            seed=self.experiment.training.random_seed,
            git_sha=self.git_commit,
        )
        scheduler_state: dict[str, object] = {
            "epsilon": self.agent.epsilon,
            "optimization_steps": self.agent.optimization_steps,
        }
        if extra_scheduler_state is not None:
            scheduler_state.update(extra_scheduler_state)
        save_checkpoint(
            self.root / "checkpoints" / name,
            model_state=self.agent.online_network.state_dict(),
            target_state=self.agent.target_network.state_dict(),
            optimizer_state=self.agent.optimizer.state_dict(),
            scheduler_state=scheduler_state,
            metadata=metadata,
        )
        self.logger.info(
            "checkpoint=%s episode=%d global_step=%d configuration_hash=%s",
            name,
            episode,
            global_step,
            self.configuration_hash,
        )

    def write_metrics(self, result: TrainingResult) -> None:
        """Persist complete optimization and binary episode-success metrics."""
        optimization_fields = [
            "global_step",
            "episode",
            "optimization_step",
            "loss",
            "mean_predicted_q",
            "epsilon",
            "learning_rate",
            "replay_size",
        ]
        episode_fields = [
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
        ]
        self._write_csv(
            self.root / "metrics.csv",
            optimization_fields,
            [asdict(row) for row in result.optimization_metrics],
        )
        self._write_csv(
            self.root / "episode_metrics.csv",
            episode_fields,
            [
                {**asdict(row), "landing_success": int(row.landing_success)}
                for row in result.episode_metrics
            ],
        )

    def complete(self) -> None:
        """Write manifest, integrity index, and the completion marker last."""
        self._flush_log()
        artifacts = self._artifact_entries()
        completed_at = utc_now()
        manifest = {
            "schema_version": "1.0.0",
            "experiment_id": self.experiment.experiment_id,
            "run_id": self.run_id,
            "algorithm": self.experiment.algorithm.value,
            "environment_variant": self.experiment.environment_variant.value,
            "repository_url": self.repository_url,
            "requested_git_commit": self.git_commit,
            "resolved_git_commit": self.git_commit,
            "git_worktree_clean": True,
            "configuration_path": "resolved_config.yaml",
            "configuration_hash": self.configuration_hash,
            "random_seed": self.experiment.training.random_seed,
            "execution_platform": "google-colab",
            "started_at_utc": self.started_at,
            "completed_at_utc": completed_at,
            "duration_seconds": time.monotonic() - self.started_monotonic,
            "status": "COMPLETED",
            "best_checkpoint_selection_metric": "episode_total_reward",
            "software_versions_path": "software_versions.json",
            "artifacts": artifacts,
            "artifact_set_sha256": artifact_set_sha256(artifacts),
        }
        manifest_path = self.root / "manifest.json"
        self._write_json(manifest_path, manifest)
        integrity_paths = [str(entry["path"]) for entry in artifacts] + [
            "manifest.json"
        ]
        integrity = "".join(
            f"{file_sha256(self.root / relative)}  {relative}\n"
            for relative in sorted(integrity_paths)
        )
        (self.root / "integrity.sha256").write_text(integrity, encoding="ascii")
        self._write_json(
            self.root / "status" / "COMPLETED.json",
            {
                "experiment_id": self.experiment.experiment_id,
                "run_id": self.run_id,
                "manifest_sha256": file_sha256(manifest_path),
                "completed_at_utc": completed_at,
            },
        )

    def fail(self, error: BaseException) -> None:
        """Write a failure marker without creating completion evidence."""
        completed = self.root / "status" / "COMPLETED.json"
        completed.unlink(missing_ok=True)
        self._flush_log()
        self._write_json(
            self.root / "status" / "FAILED.json",
            {
                "experiment_id": self.experiment.experiment_id,
                "run_id": self.run_id,
                "failed_at_utc": utc_now(),
                "error_type": type(error).__name__,
                "error": str(error),
            },
        )

    def _write_resolved_configuration(self) -> None:
        path = self.root / "resolved_config.yaml"
        path.write_text(
            yaml.safe_dump(
                self.experiment.resolved_values(),
                sort_keys=True,
                allow_unicode=False,
            ),
            encoding="utf-8",
        )

    def _write_validation_set(self) -> None:
        np.save(self.root / "validation_states.npy", self.validation_set.states)
        self._write_json(
            self.root / "validation_states.json",
            {
                "seed": self.validation_set.seed,
                "count": int(self.validation_set.states.shape[0]),
                "input_dim": int(self.validation_set.states.shape[1]),
                "dtype": str(self.validation_set.states.dtype),
                "construction": self.validation_set.construction,
                "raw_state_bytes_sha256": self.validation_set.sha256,
                "aggregation": "mean(max(online_network_q_values, axis=actions))",
            },
        )

    def _write_provenance(self) -> None:
        seed = self.experiment.training.random_seed
        self._write_json(
            self.root / "provenance.json",
            {
                "repository_url": self.repository_url,
                "git_commit": self.git_commit,
                "experiment_id": self.experiment.experiment_id,
                "run_id": self.run_id,
                "execution_context": "colab-full",
                "runtime_guard_decision": "authorized",
                "seed_map": {
                    "master": seed,
                    "python": seed,
                    "numpy": seed,
                    "torch_cpu": seed,
                    "torch_cuda": seed,
                    "gymnasium": seed,
                },
            },
        )

    def _write_software_versions(self) -> None:
        metadata = capture_software_metadata(
            ["gymnasium", "numpy", "PyYAML", "torch"]
        ).to_dict()
        metadata.update(
            {
                "torch_cuda_version": torch.version.cuda,
                "cuda_available": torch.cuda.is_available(),
                "accelerator": (
                    torch.cuda.get_device_name(0)
                    if torch.cuda.is_available()
                    else "cpu"
                ),
            }
        )
        self._write_json(self.root / "software_versions.json", metadata)

    def _artifact_entries(self) -> list[dict[str, object]]:
        entries: list[dict[str, object]] = []
        for path in sorted(item for item in self.root.rglob("*") if item.is_file()):
            relative = path.relative_to(self.root).as_posix()
            if relative in {"manifest.json", "integrity.sha256"} or relative.startswith(
                "status/"
            ):
                continue
            entries.append(
                {
                    "path": relative,
                    "role": self._artifact_role(relative),
                    "size_bytes": path.stat().st_size,
                    "sha256": file_sha256(path),
                }
            )
        return entries

    @staticmethod
    def _artifact_role(relative: str) -> str:
        if relative.startswith("checkpoints/"):
            return "checkpoint"
        if relative.endswith(".csv"):
            return "metrics"
        if relative.startswith("validation_states"):
            return "fixed-validation-states"
        if relative == "resolved_config.yaml":
            return "configuration"
        if relative == "training.log":
            return "log"
        return "metadata"

    @staticmethod
    def _write_csv(
        path: Path, fieldnames: list[str], rows: list[dict[str, Any]]
    ) -> None:
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def _write_json(path: Path, value: object) -> None:
        path.write_text(
            json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )

    def _flush_log(self) -> None:
        for handler in self.logger.handlers:
            handler.flush()
