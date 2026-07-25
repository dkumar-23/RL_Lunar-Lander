"""Synthetic complete validated bundles shared by downstream tests."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from src.common import (
    TrainingArtifactValidator,
    artifact_set_sha256,
    configuration_sha256,
    file_sha256,
)


@dataclass(frozen=True)
class BundleFixture:
    """Paths and validator for one synthetic promoted bundle."""

    bundle: Path
    validated_root: Path
    validation_root: Path
    validator: TrainingArtifactValidator


def create_validated_bundle(
    root: Path,
    experiment_id: str = "EXP-001",
    algorithm: str = "DQN",
    variant: str = "original",
) -> BundleFixture:
    """Create a hash-consistent bundle without running or simulating training."""
    validated_root = root / "outputs" / "colab" / "validated"
    validation_root = root / "outputs" / "colab" / "validation"
    bundle = validated_root / experiment_id / "RUN-001"
    (bundle / "checkpoints").mkdir(parents=True)
    (bundle / "status").mkdir()
    resolved_config = (
        "environment:\n"
        "  environment_name: LunarLander-v3\n"
        "  random_seed: 7\n"
        "  action_failure_probability: 0.15\n"
        "  fuel_penalty: 0.3\n"
        "  landing_bonus: 50.0\n"
        "  landing_tolerance: 0.1\n"
        "  render_mode: null\n"
        "training:\n"
        "  random_seed: 7\n"
        "  episodes: 2\n"
        "  max_steps_per_episode: 3\n"
        "  hidden_sizes: [8]\n"
        "  activation: relu\n"
        "  optimizer: adam\n"
        "  learning_rate: 0.001\n"
        "  discount_factor: 0.99\n"
        "  replay_capacity: 10\n"
        "  batch_size: 2\n"
        "  warmup_steps: 2\n"
        "  optimization_frequency: 1\n"
        "  target_sync_interval: 2\n"
        "  epsilon_initial: 1.0\n"
        "  epsilon_final: 0.1\n"
        "  epsilon_decay: 0.9\n"
        "  validation_state_count: 2\n"
        "  validation_seed: 9\n"
        "  checkpoint_interval: 1\n"
        "  success_window: 100\n"
        "  loss_function: smooth_l1\n"
        "  device: cpu\n"
        "  deterministic: true\n"
    )
    payloads = {
        "resolved_config.yaml": resolved_config,
        "metrics.csv": (
            "global_step,episode,optimization_step,loss,mean_predicted_q,"
            "epsilon,learning_rate,replay_size\n1,1,1,0.5,0.1,1.0,0.001,1\n"
        ),
        "episode_metrics.csv": (
            "episode,total_reward,episode_length,terminated,truncated,"
            "landing_success,thruster_actions_selected,"
            "thruster_actions_executed,thruster_failures,fuel_penalty_total,"
            "landing_bonus_total,mean_predicted_q,epsilon,duration_seconds\n"
            "1,10.0,2,true,false,1,3,2,1,0.9,50.0,0.5,0.1,0.01\n"
            "2,20.0,3,true,false,0,2,2,0,0.6,0.0,0.7,0.1,0.01\n"
        ),
        "checkpoints/best_checkpoint.pt": "synthetic checkpoint\n",
        "checkpoints/final_checkpoint.pt": "synthetic checkpoint\n",
        "training.log": "synthetic completed fixture\n",
        "software_versions.json": "{}\n",
        "provenance.json": "{}\n",
    }
    for relative, content in payloads.items():
        path = bundle / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    artifacts = [
        {
            "path": path.relative_to(bundle).as_posix(),
            "role": "synthetic_fixture",
            "size_bytes": path.stat().st_size,
            "sha256": file_sha256(path),
        }
        for path in sorted(item for item in bundle.rglob("*") if item.is_file())
    ]
    commit = "a" * 40
    manifest = {
        "schema_version": "1.0.0",
        "experiment_id": experiment_id,
        "run_id": "RUN-001",
        "algorithm": algorithm,
        "environment_variant": variant,
        "repository_url": "https://github.com/dkumar-23/RL_Lunar-Lander",
        "requested_git_commit": commit,
        "resolved_git_commit": commit,
        "git_worktree_clean": True,
        "configuration_path": "resolved_config.yaml",
        "configuration_hash": configuration_sha256(bundle / "resolved_config.yaml"),
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
    manifest_path = bundle / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    integrity_paths = [str(item["path"]) for item in artifacts] + ["manifest.json"]
    (bundle / "integrity.sha256").write_text(
        "".join(
            f"{file_sha256(bundle / relative)}  {relative}\n"
            for relative in integrity_paths
        ),
        encoding="ascii",
    )
    marker = {
        "experiment_id": experiment_id,
        "run_id": "RUN-001",
        "manifest_sha256": file_sha256(manifest_path),
    }
    (bundle / "status" / "COMPLETED.json").write_text(
        json.dumps(marker), encoding="utf-8"
    )
    validator = TrainingArtifactValidator(checkpoint_loader=lambda path: None)
    report = validator.validate(bundle)
    assert report.valid, report.issues
    receipt = validation_root / experiment_id / "RUN-001" / "validation_report.json"
    receipt.parent.mkdir(parents=True)
    receipt.write_text(json.dumps(report.to_dict()), encoding="utf-8")
    return BundleFixture(bundle, validated_root, validation_root, validator)
