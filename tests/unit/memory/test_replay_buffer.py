"""Unit tests for deterministic fixed-capacity replay."""

from __future__ import annotations

import unittest
from typing import cast

import numpy as np

from src.memory import ReplayBuffer, Transition


def _transition(action: int) -> Transition:
    return Transition(
        np.array([float(action)]),
        action,
        float(action),
        np.array([float(action + 1)]),
        False,
        False,
    )


class ReplayBufferTests(unittest.TestCase):
    """Verify FIFO eviction and injected-RNG no-replacement sampling."""

    def test_capacity_evicts_oldest_transition(self) -> None:
        buffer = ReplayBuffer(2, np.random.default_rng(1))
        for action in range(3):
            buffer.push(_transition(action))

        sampled = buffer.sample(2)

        self.assertEqual(buffer.size(), 2)
        self.assertEqual(buffer.capacity(), 2)
        self.assertEqual({item.action for item in sampled}, {1, 2})

    def test_sampling_is_deterministic_and_without_replacement(self) -> None:
        first = ReplayBuffer(5, np.random.default_rng(23))
        second = ReplayBuffer(5, np.random.default_rng(23))
        for action in range(5):
            first.push(_transition(action))
            second.push(_transition(action))

        first_actions = [item.action for item in first.sample(4)]
        second_actions = [item.action for item in second.sample(4)]

        self.assertEqual(first_actions, second_actions)
        self.assertEqual(len(set(first_actions)), 4)

    def test_oversized_sample_is_rejected(self) -> None:
        buffer = ReplayBuffer(2, np.random.default_rng(3))
        buffer.push(_transition(0))

        with self.assertRaises(ValueError):
            buffer.sample(2)

    def test_sampling_does_not_change_occupancy(self) -> None:
        buffer = ReplayBuffer(3, np.random.default_rng(5))
        for action in range(3):
            buffer.push(_transition(action))

        buffer.sample(2)

        self.assertEqual(len(buffer), 3)

    def test_clear_removes_transitions_without_changing_capacity(self) -> None:
        buffer = ReplayBuffer(2, np.random.default_rng(7))
        buffer.push(_transition(0))

        buffer.clear()

        self.assertEqual(buffer.size(), 0)
        self.assertEqual(buffer.capacity(), 2)

    def test_invalid_construction_and_operations_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ReplayBuffer(0, np.random.default_rng(1))
        with self.assertRaises(TypeError):
            ReplayBuffer(2, cast(np.random.Generator, object()))

        buffer = ReplayBuffer(2, np.random.default_rng(1))
        with self.assertRaises(TypeError):
            buffer.push(cast(Transition, object()))
        with self.assertRaises(ValueError):
            buffer.sample(0)


if __name__ == "__main__":
    unittest.main()
