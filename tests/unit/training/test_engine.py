"""Bounded fake-environment tests for the shared training engine."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any, cast

import numpy as np
import pytest
import torch
from torch import nn

from src.environment import EnvironmentConfig
from src.memory import ReplayBuffer
from src.training import (
    ExecutionBoundaryError,
    ExecutionContext,
    FixedValidationSet,
    LocalLimits,
    TrainingEngine,
    load_training_config,
)


class _Scheduler:
    def step(self) -> float:
        return 0.5


class _Optimizer:
    param_groups = [{"lr": 0.001}]


class _Agent:
    """Minimal deterministic injected agent used only for orchestration tests."""

    def __init__(self) -> None:
        self.online_network = nn.Linear(8, 4)
        self.device = torch.device("cpu")
        self.optimizer = _Optimizer()
        self.epsilon_scheduler = _Scheduler()
        self.optimization_steps = 0
        self.epsilon = 0.5
        self._actions = iter((1, 2, 0))

    def select_action(self, observation: np.ndarray[Any, Any], explore: bool) -> int:
        del observation, explore
        return next(self._actions)

    def learn(self, transitions: object) -> float:
        del transitions
        raise AssertionError("Warmup must prevent optimization in this test.")

    def train(self) -> None:
        self.online_network.train()

    def eval(self) -> None:
        self.online_network.eval()


class _Environment:
    """Three-step environment with one hidden thruster replacement."""

    def __init__(self) -> None:
        self.replaced_actions = 0
        self._step = 0

    def reset(
        self, *, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[np.ndarray[Any, Any], dict[str, Any]]:
        del seed, options
        self._step = 0
        return np.zeros(8, dtype=np.float32), {}

    def step(
        self, action: int
    ) -> tuple[np.ndarray[Any, Any], float, bool, bool, dict[str, Any]]:
        self._step += 1
        if self._step == 1 and action == 1:
            self.replaced_actions += 1
        observation = np.zeros(8, dtype=np.float32)
        terminated = self._step == 3
        if terminated:
            observation[6:] = 1.0
        return observation, 1.0, terminated, False, {}


def test_engine_collects_assignment_metrics_without_duplicate_landing_logic() -> None:
    """Store binary success and selected/executed/failure counters separately."""
    config = replace(
        load_training_config(Path("configs/training.yaml")),
        episodes=1,
        max_steps_per_episode=3,
        validation_state_count=2,
    )
    environment_config = EnvironmentConfig(
        environment_name="fake",
        random_seed=42,
        action_failure_probability=0.15,
        fuel_penalty=0.3,
        landing_bonus=50.0,
        landing_tolerance=0.1,
    )
    replay = ReplayBuffer(10, np.random.default_rng(42))
    engine = TrainingEngine(
        config,
        environment_config,
        cast(Any, _Environment()),
        cast(Any, _Agent()),
        replay,
        FixedValidationSet.create(2, 8, 4242),
        ExecutionContext.LOCAL_TEST,
    )

    result = engine.run(LocalLimits(3, 0))
    episode = result.episode_metrics[0]

    assert episode.landing_success is True
    assert episode.thruster_actions_selected == 2
    assert episode.thruster_actions_executed == 1
    assert episode.thruster_failures == 1
    assert episode.fuel_penalty_total == 0.6
    assert episode.landing_bonus_total == 50.0
    assert len(replay) == 3
    assert result.optimization_steps == 0


def test_local_engine_requires_runtime_guard_limits() -> None:
    """A local caller cannot omit the hard execution cap."""
    config = replace(
        load_training_config(Path("configs/training.yaml")),
        episodes=1,
    )
    environment_config = EnvironmentConfig("fake", 42, 0.0, 0.0, 0.0, 0.1)
    engine = TrainingEngine(
        config,
        environment_config,
        cast(Any, _Environment()),
        cast(Any, _Agent()),
        ReplayBuffer(10, np.random.default_rng(42)),
        FixedValidationSet.create(2, 8, 4242),
        ExecutionContext.LOCAL_TEST,
    )

    with pytest.raises(ExecutionBoundaryError):
        engine.run()


def test_full_engine_requires_colab_attestation_evidence() -> None:
    """A caller cannot authorize full execution with an enum value alone."""
    config = replace(load_training_config(Path("configs/training.yaml")), episodes=1)
    environment_config = EnvironmentConfig("fake", 42, 0.0, 0.0, 0.0, 0.1)
    engine = TrainingEngine(
        config,
        environment_config,
        cast(Any, _Environment()),
        cast(Any, _Agent()),
        ReplayBuffer(10, np.random.default_rng(42)),
        FixedValidationSet.create(2, 8, 4242),
        ExecutionContext.COLAB_FULL,
    )

    with pytest.raises(ExecutionBoundaryError, match="attestation"):
        engine.run()


def test_local_engine_suppresses_checkpoints_and_finalizes() -> None:
    """Bounded local execution cannot emit checkpoint artifacts."""
    config = replace(
        load_training_config(Path("configs/training.yaml")),
        episodes=1,
        max_steps_per_episode=3,
    )
    environment_config = EnvironmentConfig("fake", 42, 0.0, 0.0, 0.0, 0.1)
    agent = _Agent()
    checkpoint_calls: list[tuple[str, int, int]] = []
    engine = TrainingEngine(
        config,
        environment_config,
        cast(Any, _Environment()),
        cast(Any, agent),
        ReplayBuffer(10, np.random.default_rng(42)),
        FixedValidationSet.create(2, 8, 4242),
        ExecutionContext.LOCAL_TEST,
        checkpoint_callback=lambda *args: checkpoint_calls.append(args),
    )

    engine.run(LocalLimits(3, 0))

    assert checkpoint_calls == []
    assert agent.online_network.training is False
