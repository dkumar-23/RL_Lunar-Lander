"""Tests for Colab training artifact validation."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.common.artifacts import (
    TrainingArtifactValidator,
    artifact_set_sha256,
    file_sha256,
)
from src.common.configuration import configuration_sha256


class ArtifactValidationTests(unittest.TestCase):
    """Build deterministic fixtures and verify validation failures."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.bundle = Path(self.temporary.name) / "EXP-001" / "RUN-001"
        (self.bundle / "checkpoints").mkdir(parents=True)
        (self.bundle / "status").mkdir()
        self._write_payloads()
        self._write_manifest_and_markers()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _write_payloads(self) -> None:
        payloads = {
            "resolved_config.yaml": "algorithm: DQN\nseed: 7\n",
            "metrics.csv": (
                "global_step,episode,optimization_step,loss,mean_predicted_q,"
                "epsilon,learning_rate,replay_size\n1,1,1,0.5,0.1,1.0,0.001,1\n"
            ),
            "episode_metrics.csv": (
                "episode,total_reward,episode_length,terminated,truncated,"
                "landing_success,thruster_actions_selected,"
                "thruster_actions_executed,thruster_failures,"
                "fuel_penalty_total,landing_bonus_total,mean_predicted_q,"
                "epsilon,duration_seconds\n1,1.0,1,true,false,false,1,1,0,0,0,"
                "0.1,1.0,0.01\n"
            ),
            "checkpoints/best_checkpoint.pt": "checkpoint",
            "checkpoints/final_checkpoint.pt": "checkpoint",
            "training.log": "completed\n",
            "software_versions.json": "{}\n",
            "provenance.json": "{}\n",
        }
        for relative, content in payloads.items():
            path = self.bundle / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    def _write_manifest_and_markers(self) -> None:
        artifacts = []
        for path in sorted(
            item for item in self.bundle.rglob("*") if item.is_file()
        ):
            relative = path.relative_to(self.bundle).as_posix()
            artifacts.append(
                {
                    "path": relative,
                    "role": "fixture",
                    "size_bytes": path.stat().st_size,
                    "sha256": file_sha256(path),
                }
            )
        commit = "a" * 40
        manifest = {
            "schema_version": "1.0.0",
            "experiment_id": "EXP-001",
            "run_id": "RUN-001",
            "algorithm": "DQN",
            "environment_variant": "original",
            "repository_url": "https://github.com/dkumar-23/RL_Lunar-Lander",
            "requested_git_commit": commit,
            "resolved_git_commit": commit,
            "git_worktree_clean": True,
            "configuration_path": "resolved_config.yaml",
            "configuration_hash": configuration_sha256(
                self.bundle / "resolved_config.yaml"
            ),
            "random_seed": 7,
            "execution_platform": "google-colab",
            "started_at_utc": "2026-01-01T00:00:00Z",
            "completed_at_utc": "2026-01-01T00:00:01Z",
            "duration_seconds": 1.0,
            "status": "COMPLETED",
            "best_checkpoint_selection_metric": "episode_reward",
            "software_versions_path": "software_versions.json",
            "artifacts": artifacts,
            "artifact_set_sha256": artifact_set_sha256(artifacts),
        }
        manifest_path = self.bundle / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
        )
        integrity_paths = [entry["path"] for entry in artifacts] + ["manifest.json"]
        integrity = "".join(
            f"{file_sha256(self.bundle / relative)}  {relative}\n"
            for relative in integrity_paths
        )
        (self.bundle / "integrity.sha256").write_text(integrity, encoding="ascii")
        marker = {
            "experiment_id": "EXP-001",
            "run_id": "RUN-001",
            "manifest_sha256": file_sha256(manifest_path),
        }
        (self.bundle / "status" / "COMPLETED.json").write_text(
            json.dumps(marker), encoding="utf-8"
        )

    def test_complete_bundle_is_valid(self) -> None:
        validator = TrainingArtifactValidator(checkpoint_loader=lambda path: None)
        report = validator.validate(self.bundle)
        self.assertTrue(report.valid, report.issues)
        self.assertEqual(report.artifacts_checked, 8)
        self.assertEqual(report.checkpoints_checked, 2)

    def test_modified_payload_is_rejected(self) -> None:
        (self.bundle / "training.log").write_text("tampered\n", encoding="utf-8")
        validator = TrainingArtifactValidator(checkpoint_loader=lambda path: None)
        report = validator.validate(self.bundle)
        self.assertFalse(report.valid)
        codes = {issue.code for issue in report.issues}
        self.assertIn("artifact.hash_mismatch", codes)

    def test_hash_uses_exact_bytes(self) -> None:
        expected = hashlib.sha256(b"completed\n").hexdigest()
        self.assertEqual(file_sha256(self.bundle / "training.log"), expected)


if __name__ == "__main__":
    unittest.main()
