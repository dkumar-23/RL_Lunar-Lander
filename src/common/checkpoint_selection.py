"""Deterministic checkpoint-selection policies for canonical evaluation."""

from __future__ import annotations

import csv
import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import torch


class CheckpointSelectionError(RuntimeError):
    """Raised when a checkpoint policy cannot resolve a valid selection."""


@dataclass(frozen=True)
class CheckpointSelection:
    """One deterministic selection from a validated bundle manifest."""

    checkpoint_name: str
    episode: int
    global_step: int
    selection_criterion: str


Selector = Callable[[Path], CheckpointSelection]


def final_checkpoint(path: Path) -> CheckpointSelection:
    """Select the final checkpoint from a validated bundle.

    Args:
        path: A validated bundle directory with ``checkpoints/final_checkpoint.pt``.

    Returns:
        Selection identifying the final checkpoint.

    Raises:
        CheckpointSelectionError: The final checkpoint does not exist.
    """
    checkpoint_path = path / "checkpoints" / "final_checkpoint.pt"
    if not checkpoint_path.is_file():
        raise CheckpointSelectionError(
            "Final checkpoint not found: checkpoints/final_checkpoint.pt"
        )
    metadata_path = path / "manifest.json"
    episode = _manifest_episode(metadata_path)
    return CheckpointSelection(
        checkpoint_name="final_checkpoint.pt",
        episode=episode,
        global_step=0,
        selection_criterion="final",
    )


def moving_average_reward_checkpoint(
    path: Path, window: int = 100
) -> CheckpointSelection:
    """Select the episode with highest trailing-window average training reward.

    Prefers ``checkpoints/best_moving_average_checkpoint.pt``, then falls back
    to per-episode or periodic checkpoints for legacy bundles.

    Args:
        path: A validated bundle directory containing ``episode_metrics.csv``.
        window: Trailing-episode window for the moving-average reward.

    Returns:
        Selection identifying the checkpoint with peak moving-average reward.

    Raises:
        CheckpointSelectionError: Metrics are missing, empty, or invalid.
    """
    moving_avg_path = path / "checkpoints" / "best_moving_average_checkpoint.pt"
    if moving_avg_path.is_file():
        metadata = _moving_avg_metadata(moving_avg_path)
        episode = metadata["episode"]
        global_step = metadata.get("global_step", 0)
        if not isinstance(episode, int) or not isinstance(global_step, int):
            raise CheckpointSelectionError(
                "best_moving_average checkpoint metadata must contain "
                "integer episode and global_step."
            )
        return CheckpointSelection(
            checkpoint_name="best_moving_average_checkpoint.pt",
            episode=episode,
            global_step=global_step,
            selection_criterion="best_100_episode_moving_average_reward",
        )
    metrics_path = path / "episode_metrics.csv"
    if not metrics_path.is_file():
        raise CheckpointSelectionError("Episode metrics not found: episode_metrics.csv")
    try:
        with metrics_path.open("r", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise CheckpointSelectionError(
            f"Unable to read episode metrics: {exc}"
        ) from exc
    if not rows:
        raise CheckpointSelectionError("Episode metrics are empty.")
    try:
        rewards = [float(row["total_reward"]) for row in rows]
        episodes = [int(row["episode"]) for row in rows]
    except (TypeError, ValueError) as exc:
        raise CheckpointSelectionError(
            f"Invalid reward or episode value: {exc}"
        ) from exc
    if not rewards or not episodes:
        raise CheckpointSelectionError("Episode metrics contain no valid rows.")
    if len(rewards) < window:
        window = len(rewards)
    running_sum = sum(rewards[:window])
    best_avg = running_sum / window
    best_index = window - 1
    for index in range(window, len(rewards)):
        running_sum += rewards[index] - rewards[index - window]
        avg = running_sum / window
        if avg > best_avg:
            best_avg = avg
            best_index = index
    best_episode = episodes[best_index]
    checkpoint_name = f"checkpoint_{best_episode:04d}.pt"
    checkpoint_path = path / "checkpoints" / checkpoint_name
    if checkpoint_path.is_file():
        return CheckpointSelection(
            checkpoint_name=checkpoint_name,
            episode=best_episode,
            global_step=0,
            selection_criterion="best_100_episode_moving_average_reward_legacy",
        )
    periodic_checkpoint = path / "checkpoints" / "periodic_checkpoint.pt"
    if periodic_checkpoint.is_file():
        return CheckpointSelection(
            checkpoint_name="periodic_checkpoint.pt",
            episode=best_episode,
            global_step=0,
            selection_criterion="best_100_episode_moving_average_reward_fallback",
        )
    raise CheckpointSelectionError(
        f"No checkpoint found for best episode {best_episode} "
        f"and no fallback periodic_checkpoint.pt exists."
    )


def _moving_avg_metadata(path: Path) -> dict[str, object]:
    """Read best-moving-average metadata from a checkpoint."""
    try:
        loaded = torch.load(path, map_location="cpu", weights_only=True)
    except Exception as exc:
        raise CheckpointSelectionError(
            f"Unable to load best_moving_average checkpoint: {exc}"
        ) from exc
    metadata = loaded.get("metadata", {})
    if not isinstance(metadata, dict):
        raise CheckpointSelectionError(
            "best_moving_average checkpoint metadata is invalid."
        )
    return metadata


def _manifest_episode(path: Path) -> int:
    if not path.is_file():
        raise CheckpointSelectionError("Manifest not found.")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CheckpointSelectionError(f"Unable to read manifest: {exc}") from exc
    episode = manifest.get("episode", 0)
    if not isinstance(episode, int) or episode <= 0:
        raise CheckpointSelectionError("Manifest episode must be a positive integer.")
    return episode
