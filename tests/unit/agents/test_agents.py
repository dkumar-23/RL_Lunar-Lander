"""Fixed-tensor target and exactly-one-step agent tests."""

from __future__ import annotations

import unittest
from collections.abc import Iterator
from unittest import mock

import numpy as np
import torch
from torch import nn

from src.agents import DDQNAgent, DQNAgent, EpsilonScheduler
from src.agents.base_agent import BaseAgent
from src.memory import Transition
from src.models import QNetwork


class TableNetwork(nn.Module):
    """Return trainable table rows for deterministic target tests."""

    def __init__(self, values: list[list[float]]) -> None:
        super().__init__()
        self.values = nn.Parameter(torch.tensor(values, dtype=torch.float32))

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        """Return one configured row per input row."""
        return self.values[: inputs.shape[0]]


def _table_agent(
    agent_type: type[BaseAgent],
    online_values: list[list[float]],
    target_values: list[list[float]],
    rng: np.random.Generator,
) -> BaseAgent:
    online = TableNetwork(online_values)
    target = TableNetwork(target_values)
    optimizer = torch.optim.SGD(online.parameters(), lr=0.1)
    agent = agent_type(
        online,
        target,
        optimizer,
        nn.MSELoss(),
        EpsilonScheduler(1.0, 0.1, 0.9),
        len(online_values[0]),
        0.5,
        10,
        rng,
        "cpu",
    )
    with torch.no_grad():
        target.values.copy_(torch.tensor(target_values))
    return agent


class AgentTargetTests(unittest.TestCase):
    """Verify DQN and DDQN fixed-tensor target equations."""

    def test_dqn_uses_target_network_max_and_only_masks_termination(self) -> None:
        agent = _table_agent(
            DQNAgent,
            [[8.0, 1.0], [8.0, 1.0]],
            [[1.0, 4.0], [10.0, 20.0]],
            np.random.default_rng(1),
        )

        targets = agent._compute_targets(
            torch.tensor([1.0, 2.0]),
            torch.zeros((2, 1)),
            torch.tensor([False, True]),
        )

        torch.testing.assert_close(targets, torch.tensor([3.0, 2.0]))

    def test_ddqn_selects_online_actions_and_gathers_target_values(self) -> None:
        agent = _table_agent(
            DDQNAgent,
            [[5.0, 1.0], [1.0, 8.0]],
            [[2.0, 9.0], [7.0, 3.0]],
            np.random.default_rng(2),
        )

        targets = agent._compute_targets(
            torch.tensor([1.0, 0.5]),
            torch.zeros((2, 1)),
            torch.tensor([False, False]),
        )

        torch.testing.assert_close(targets, torch.tensor([2.0, 2.0]))

    def test_hard_target_sync_copies_online_parameters(self) -> None:
        agent = _table_agent(
            DQNAgent,
            [[1.0, 2.0]],
            [[7.0, 8.0]],
            np.random.default_rng(3),
        )
        with torch.no_grad():
            next(agent.online_network.parameters()).fill_(5.0)

        agent.update_target()

        for online, target in zip(
            agent.online_network.parameters(),
            agent.target_network.parameters(),
            strict=True,
        ):
            torch.testing.assert_close(online, target)

    def test_epsilon_greedy_uses_injected_numpy_generator(self) -> None:
        seed = 29
        expected_rng = np.random.default_rng(seed)
        expected_rng.random()
        expected_action = int(expected_rng.integers(2))
        agent = _table_agent(
            DQNAgent,
            [[1.0, 4.0]],
            [[1.0, 4.0]],
            np.random.default_rng(seed),
        )

        exploratory = agent.select_action(np.array([0.0]), explore=True)
        greedy = agent.select_action(np.array([0.0]), explore=False)

        self.assertEqual(exploratory, expected_action)
        self.assertEqual(greedy, 1)


class AgentLearningTests(unittest.TestCase):
    """Verify one learn call performs exactly one optimizer update."""

    @staticmethod
    def _batch() -> Iterator[Transition]:
        yield Transition(
            np.array([1.0, 0.0]),
            0,
            1.0,
            np.array([0.0, 1.0]),
            False,
            True,
        )
        yield Transition(
            np.array([0.0, 1.0]),
            1,
            -1.0,
            np.array([1.0, 1.0]),
            True,
            False,
        )

    def test_learn_performs_exactly_one_optimizer_step(self) -> None:
        torch.manual_seed(7)
        online = QNetwork(2, 2, (4,), nn.ReLU)
        target = QNetwork(2, 2, (4,), nn.ReLU)
        optimizer = torch.optim.SGD(online.parameters(), lr=0.05)
        agent = DQNAgent(
            online,
            target,
            optimizer,
            nn.MSELoss(),
            EpsilonScheduler(0.8, 0.1, 0.9),
            2,
            0.95,
            10,
            np.random.default_rng(5),
            "cpu",
        )

        with mock.patch.object(
            optimizer, "step", wraps=optimizer.step
        ) as optimizer_step:
            loss = agent.learn(tuple(self._batch()))

        self.assertEqual(optimizer_step.call_count, 1)
        self.assertEqual(agent.optimization_steps, 1)
        self.assertTrue(np.isfinite(loss))

    def test_target_sync_occurs_at_configured_optimizer_interval(self) -> None:
        torch.manual_seed(11)
        online = QNetwork(2, 2, (4,), nn.ReLU)
        target = QNetwork(2, 2, (4,), nn.ReLU)
        agent = DQNAgent(
            online,
            target,
            torch.optim.SGD(online.parameters(), lr=0.05),
            nn.MSELoss(),
            EpsilonScheduler(0.8, 0.1, 0.9),
            2,
            0.95,
            2,
            np.random.default_rng(6),
            "cpu",
        )

        with mock.patch.object(
            agent, "update_target", wraps=agent.update_target
        ) as target_sync:
            agent.learn(tuple(self._batch()))
            self.assertEqual(target_sync.call_count, 0)
            agent.learn(tuple(self._batch()))

        self.assertEqual(target_sync.call_count, 1)
        self.assertEqual(agent.optimization_steps, 2)

    def test_train_and_eval_control_network_modes(self) -> None:
        agent = _table_agent(
            DQNAgent,
            [[1.0, 2.0]],
            [[1.0, 2.0]],
            np.random.default_rng(8),
        )

        agent.train()
        self.assertTrue(agent.online_network.training)
        self.assertFalse(agent.target_network.training)

        agent.eval()
        self.assertFalse(agent.online_network.training)
        self.assertFalse(agent.target_network.training)


if __name__ == "__main__":
    unittest.main()
