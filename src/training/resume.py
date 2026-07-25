"""Validated application of portable checkpoint state for Colab resume."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from src.agents import BaseAgent
from src.common import LoadedCheckpoint


class ResumeError(ValueError):
    """Raised before mutation when checkpoint identity cannot authorize resume."""


@dataclass(frozen=True)
class ResumeProgress:
    """Training counters required to continue after a completed episode."""

    next_episode: int
    global_steps: int


def restore_training_checkpoint(
    agent: BaseAgent,
    checkpoint: LoadedCheckpoint,
    *,
    experiment_id: str,
    configuration_hash: str,
    seed: int,
    git_sha: str,
) -> ResumeProgress:
    """Validate checkpoint identity and restore all agent training state.

    The caller remains responsible for loading only a checkpoint from a bundle
    that passed artifact validation and for supplying a Colab-attested commit.
    """
    metadata = checkpoint.metadata
    expected = (experiment_id, configuration_hash, seed, git_sha)
    actual = (
        metadata.experiment_id,
        metadata.configuration_hash,
        metadata.seed,
        metadata.git_sha,
    )
    if actual != expected:
        raise ResumeError(
            "Checkpoint experiment, configuration, seed, or commit does not match."
        )

    epsilon, optimization_steps = _scheduler_progress(checkpoint.scheduler_state)
    agent.online_network.load_state_dict(checkpoint.model_state)
    agent.target_network.load_state_dict(checkpoint.target_state)
    agent.optimizer.load_state_dict(dict(checkpoint.optimizer_state))
    agent.restore_training_progress(
        epsilon=epsilon,
        optimization_steps=optimization_steps,
    )
    agent.target_network.requires_grad_(False)
    return ResumeProgress(metadata.episode + 1, metadata.global_step)


def _scheduler_progress(state: Mapping[str, object] | None) -> tuple[float, int]:
    if state is None or set(state) != {"epsilon", "optimization_steps"}:
        raise ResumeError("Checkpoint scheduler state is incomplete.")
    epsilon = state["epsilon"]
    optimization_steps = state["optimization_steps"]
    if isinstance(epsilon, bool) or not isinstance(epsilon, (int, float)):
        raise ResumeError("Checkpoint epsilon must be numeric.")
    if (
        isinstance(optimization_steps, bool)
        or not isinstance(optimization_steps, int)
        or optimization_steps < 0
    ):
        raise ResumeError("Checkpoint optimization_steps must be non-negative.")
    return float(epsilon), optimization_steps
