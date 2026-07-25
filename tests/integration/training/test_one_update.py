"""Exactly-one-update integration through the real agent and engine."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any, cast

import numpy as np
import pytest
import torch

from src.common.seed import initialize_seed
from src.environment import EnvironmentConfig
from src.training import (
    Algorithm,
    ExecutionContext,
    FixedValidationSet,
    LocalLimits,
    TrainingEngine,
    create_agent,
    create_replay_buffer,
    load_training_config,
)


class _OneStepEnvironment:
    replaced_actions = 0

    def reset(
        self, *, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[np.ndarray[Any, Any], dict[str, Any]]:
        del seed, options
        return np.zeros(8, dtype=np.float32), {}

    def step(
        self, action: int
    ) -> tuple[np.ndarray[Any, Any], float, bool, bool, dict[str, Any]]:
        del action
        return np.ones(8, dtype=np.float32), 1.0, True, False, {}


@pytest.mark.parametrize("algorithm", [Algorithm.DQN, Algorithm.DDQN])
def test_shared_engine_performs_exactly_one_real_update(
    algorithm: Algorithm,
) -> None:
    """Exercise replay sampling and one real optimizer step under local caps."""
    config = replace(
        load_training_config(Path("configs/training.yaml")),
        episodes=1,
        max_steps_per_episode=1,
        replay_capacity=2,
        batch_size=1,
        warmup_steps=1,
        validation_state_count=2,
    )
    rng = initialize_seed(config.random_seed, deterministic=True)
    agent = create_agent(config, algorithm, 8, 4, rng, device="cpu")
    before = tuple(
        parameter.detach().clone() for parameter in agent.online_network.parameters()
    )
    engine = TrainingEngine(
        config,
        EnvironmentConfig("fake", 42, 0.0, 0.0, 0.0, 0.1),
        cast(Any, _OneStepEnvironment()),
        agent,
        create_replay_buffer(config, rng),
        FixedValidationSet.create(2, 8, 4242),
        ExecutionContext.LOCAL_TEST,
    )

    result = engine.run(LocalLimits(1, 1))

    assert result.global_steps == 1
    assert result.optimization_steps == 1
    assert any(
        not torch.equal(old, new.detach())
        for old, new in zip(before, agent.online_network.parameters(), strict=True)
    )
