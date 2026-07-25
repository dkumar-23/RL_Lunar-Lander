"""Fixed validation-state construction and Q-value aggregation."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
import torch

from src.agents import BaseAgent


@dataclass(frozen=True)
class FixedValidationSet:
    """One immutable synthetic state set shared across an entire run."""

    states: npt.NDArray[np.float32]
    seed: int
    construction: str
    sha256: str

    @classmethod
    def create(cls, count: int, input_dim: int, seed: int) -> FixedValidationSet:
        """Generate deterministic standard-normal states without global RNG use."""
        if (
            isinstance(count, bool)
            or not isinstance(count, int)
            or count <= 0
            or isinstance(input_dim, bool)
            or not isinstance(input_dim, int)
            or input_dim <= 0
        ):
            raise ValueError("count and input_dim must be positive integers.")
        if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
            raise ValueError("seed must be a non-negative integer.")
        rng = np.random.default_rng(seed)
        states = rng.standard_normal((count, input_dim)).astype(np.float32)
        states.flags.writeable = False
        return cls(
            states=states,
            seed=seed,
            construction="numpy-pcg64-standard-normal-float32-v1",
            sha256=hashlib.sha256(states.tobytes(order="C")).hexdigest(),
        )


def mean_max_predicted_q(agent: BaseAgent, validation_set: FixedValidationSet) -> float:
    """Return mean maximum online-network Q over unchanged validation states."""
    was_training = agent.online_network.training
    agent.online_network.eval()
    with torch.no_grad():
        states = torch.tensor(
            validation_set.states, dtype=torch.float32, device=agent.device
        )
        value = agent.online_network(states).max(dim=1).values.mean().item()
    if was_training:
        agent.online_network.train()
    return float(value)
