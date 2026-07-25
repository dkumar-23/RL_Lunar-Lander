"""Deterministic Gymnasium fake used by environment-only tests."""

from __future__ import annotations

from typing import Any

import gymnasium as gym
import numpy as np

from src.environment.reward import Observation


class FakeLanderEnv(gym.Env[Observation, int]):
    """Record actions and return a configurable deterministic transition."""

    metadata: dict[str, Any] = {}

    def __init__(self) -> None:
        """Initialize standard LunarLander-shaped spaces and transition values."""
        self.observation_space = gym.spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(8,),
            dtype=np.float32,
        )
        self.action_space = gym.spaces.Discrete(4)
        self.observation = np.zeros(8, dtype=np.float32)
        self.reward = 10.0
        self.terminated = False
        self.truncated = False
        self.info: dict[str, Any] = {"base": "unchanged"}
        self.executed_actions: list[int] = []
        self.last_reset_seed: int | None = None

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[Observation, dict[str, Any]]:
        """Return the configured observation and information mapping."""
        super().reset(seed=seed)
        self.last_reset_seed = seed
        return self.observation, self.info

    def step(
        self, action: int
    ) -> tuple[Observation, float, bool, bool, dict[str, Any]]:
        """Record ``action`` and return the configured transition."""
        self.executed_actions.append(action)
        return (
            self.observation,
            self.reward,
            self.terminated,
            self.truncated,
            self.info,
        )
