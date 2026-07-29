"""Tests for deterministic checkpoint-selection policies."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import torch

from src.common.checkpoint_selection import (
    CheckpointSelectionError,
    final_checkpoint,
    moving_average_reward_checkpoint,
)


def _bundle(tmp_path: Path) -> Path:
    bundle = tmp_path / "EXP-001" / "RUN-001"
    (bundle / "checkpoints").mkdir(parents=True)
    return bundle


def _manifest(path: Path, episode: int = 2000) -> None:
    (path / "manifest.json").write_text(
        json.dumps({"experiment_id": "EXP-001", "episode": episode}),
        encoding="utf-8",
    )


def _episode_metrics(path: Path, rewards: list[float]) -> None:
    lines = ["episode,total_reward"]
    for index, reward in enumerate(rewards, start=1):
        lines.append(f"{index},{reward}")
    (path / "episode_metrics.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _best_moving_avg_checkpoint(path: Path, episode: int, global_step: int = 0) -> None:
    payload = {
        "model_state": {"dummy": torch.zeros(1)},
        "target_state": {"dummy": torch.zeros(1)},
        "optimizer_state": {"dummy": torch.zeros(1)},
        "scheduler_state": None,
        "metadata": {
            "experiment_id": "EXP-001",
            "run_id": "RUN-001",
            "episode": episode,
            "global_step": global_step,
            "configuration_hash": "a" * 64,
            "seed": 42,
            "git_sha": "b" * 40,
        },
    }
    torch.save(payload, path / "checkpoints" / "best_moving_average_checkpoint.pt")


def test_final_checkpoint_selects_final_checkpoint_file(tmp_path: Path) -> None:
    bundle = _bundle(tmp_path)
    (bundle / "checkpoints" / "final_checkpoint.pt").write_text("dummy")
    _manifest(bundle)

    selection = final_checkpoint(bundle)

    assert selection.checkpoint_name == "final_checkpoint.pt"
    assert selection.selection_criterion == "final"
    assert selection.episode == 2000


def test_final_checkpoint_fails_when_checkpoint_missing(tmp_path: Path) -> None:
    bundle = _bundle(tmp_path)
    _manifest(bundle)

    with pytest.raises(CheckpointSelectionError, match="Final checkpoint not found"):
        final_checkpoint(bundle)


def test_moving_average_selects_peak_episode(tmp_path: Path) -> None:
    bundle = _bundle(tmp_path)
    (bundle / "checkpoints" / "periodic_checkpoint.pt").write_text("dummy")
    _episode_metrics(bundle, [0.0] * 100 + [100.0] * 100 + [0.0] * 100)

    selection = moving_average_reward_checkpoint(bundle, window=100)

    assert selection.episode == 200
    assert selection.checkpoint_name == "periodic_checkpoint.pt"
    assert "moving_average_reward" in selection.selection_criterion


def test_moving_average_with_specific_checkpoint_file(tmp_path: Path) -> None:
    bundle = _bundle(tmp_path)
    (bundle / "checkpoints" / "checkpoint_0200.pt").write_text("dummy")
    rewards = [0.0] * 100 + [100.0] * 100 + [0.0] * 100
    _episode_metrics(bundle, rewards)

    selection = moving_average_reward_checkpoint(bundle, window=100)

    assert selection.checkpoint_name == "checkpoint_0200.pt"
    assert selection.episode == 200


def test_moving_average_selects_best_moving_avg_checkpoint(tmp_path: Path) -> None:
    bundle = _bundle(tmp_path)
    _best_moving_avg_checkpoint(bundle, episode=150)
    _episode_metrics(bundle, [float(i % 100) for i in range(300)])

    selection = moving_average_reward_checkpoint(bundle, window=100)

    assert selection.checkpoint_name == "best_moving_average_checkpoint.pt"
    assert selection.episode == 150
    assert selection.selection_criterion == "best_100_episode_moving_average_reward"


def test_moving_average_selects_best_moving_avg_prefers_embedded_metadata(
    tmp_path: Path,
) -> None:
    bundle = _bundle(tmp_path)
    _best_moving_avg_checkpoint(bundle, episode=50)
    _episode_metrics(bundle, [0.0] * 100 + [100.0] * 100 + [0.0] * 100)

    selection = moving_average_reward_checkpoint(bundle, window=100)

    assert selection.checkpoint_name == "best_moving_average_checkpoint.pt"
    assert selection.episode == 50


def test_moving_average_fails_on_missing_metrics(tmp_path: Path) -> None:
    bundle = _bundle(tmp_path)

    with pytest.raises(CheckpointSelectionError, match="Episode metrics not found"):
        moving_average_reward_checkpoint(bundle)


def test_moving_average_fails_on_empty_metrics(tmp_path: Path) -> None:
    bundle = _bundle(tmp_path)
    _episode_metrics(bundle, [])

    with pytest.raises(CheckpointSelectionError, match="empty"):
        moving_average_reward_checkpoint(bundle)


def test_both_selectors_are_deterministic(tmp_path: Path) -> None:
    bundle = _bundle(tmp_path)
    (bundle / "checkpoints" / "final_checkpoint.pt").write_text("dummy")
    (bundle / "checkpoints" / "periodic_checkpoint.pt").write_text("dummy")
    _manifest(bundle, episode=300)
    rewards = [float(i % 50) for i in range(300)]
    _episode_metrics(bundle, rewards)

    first_final = final_checkpoint(bundle)
    second_final = final_checkpoint(bundle)
    assert first_final == second_final

    first_ma = moving_average_reward_checkpoint(bundle, window=100)
    second_ma = moving_average_reward_checkpoint(bundle, window=100)
    assert first_ma == second_ma
