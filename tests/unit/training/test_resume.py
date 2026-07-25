"""Tests for identity-bound checkpoint restoration."""

from __future__ import annotations

import numpy as np
import pytest
import torch
from torch import nn

from src.agents import DQNAgent, EpsilonScheduler
from src.common import LoadedCheckpoint, RunMetadata
from src.memory import Transition
from src.models import QNetwork
from src.training import ResumeError, restore_training_checkpoint


def _agent(seed: int) -> DQNAgent:
    torch.manual_seed(seed)
    online = QNetwork(2, 2, (3,), nn.ReLU)
    target = QNetwork(2, 2, (3,), nn.ReLU)
    return DQNAgent(
        online,
        target,
        torch.optim.Adam(online.parameters(), lr=0.001),
        nn.MSELoss(),
        EpsilonScheduler(1.0, 0.1, 0.9),
        2,
        0.99,
        10,
        np.random.default_rng(seed),
        "cpu",
    )


def _checkpoint(source: DQNAgent) -> LoadedCheckpoint:
    source.learn(
        (
            Transition(
                np.array([1.0, 0.0]),
                0,
                1.0,
                np.array([0.0, 1.0]),
                False,
                False,
            ),
        )
    )
    return LoadedCheckpoint(
        model_state=source.online_network.state_dict(),
        target_state=source.target_network.state_dict(),
        optimizer_state=source.optimizer.state_dict(),
        scheduler_state={"epsilon": 0.5, "optimization_steps": 7},
        metadata=RunMetadata(
            experiment_id="EXP-001",
            run_id="RUN-001",
            episode=12,
            global_step=345,
            configuration_hash="a" * 64,
            seed=42,
            git_sha="b" * 40,
        ),
    )


def test_restore_applies_agent_state_and_returns_next_progress() -> None:
    source = _agent(1)
    destination = _agent(2)

    progress = restore_training_checkpoint(
        destination,
        _checkpoint(source),
        experiment_id="EXP-001",
        configuration_hash="a" * 64,
        seed=42,
        git_sha="b" * 40,
    )

    for expected, actual in zip(
        source.online_network.parameters(),
        destination.online_network.parameters(),
        strict=True,
    ):
        torch.testing.assert_close(actual, expected)
    assert destination.epsilon == 0.5
    assert destination.optimization_steps == 7
    assert len(destination.optimizer.state) > 0
    assert progress.next_episode == 13
    assert progress.global_steps == 345


def test_restore_rejects_identity_mismatch_before_mutation() -> None:
    source = _agent(1)
    destination = _agent(2)
    before = tuple(
        parameter.detach().clone()
        for parameter in destination.online_network.parameters()
    )

    with pytest.raises(ResumeError, match="does not match"):
        restore_training_checkpoint(
            destination,
            _checkpoint(source),
            experiment_id="EXP-002",
            configuration_hash="a" * 64,
            seed=42,
            git_sha="b" * 40,
        )

    for expected, actual in zip(
        before, destination.online_network.parameters(), strict=True
    ):
        torch.testing.assert_close(actual, expected)


def test_restore_rejects_incomplete_scheduler_progress() -> None:
    source = _agent(1)
    checkpoint = _checkpoint(source)
    incomplete = LoadedCheckpoint(
        checkpoint.model_state,
        checkpoint.target_state,
        checkpoint.optimizer_state,
        {"epsilon": 0.5},
        checkpoint.metadata,
    )

    with pytest.raises(ResumeError, match="incomplete"):
        restore_training_checkpoint(
            _agent(2),
            incomplete,
            experiment_id="EXP-001",
            configuration_hash="a" * 64,
            seed=42,
            git_sha="b" * 40,
        )
