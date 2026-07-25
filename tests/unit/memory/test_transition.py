"""Unit tests for immutable Gymnasium transitions."""

from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

import numpy as np

from src.memory import Transition


class TransitionTests(unittest.TestCase):
    """Verify structural and observation-array immutability."""

    def test_transition_preserves_separate_episode_end_flags(self) -> None:
        transition = Transition(np.array([1.0]), 2, 3.0, np.array([4.0]), False, True)

        self.assertFalse(transition.terminated)
        self.assertTrue(transition.truncated)

    def test_transition_copies_and_freezes_observations(self) -> None:
        state = np.array([1.0, 2.0])
        transition = Transition(state, 0, 1.0, state, True, False)
        state[0] = 9.0

        self.assertEqual(transition.state[0], 1.0)
        with self.assertRaises(ValueError):
            transition.state[0] = 5.0
        field_name = "reward"
        with self.assertRaises(FrozenInstanceError):
            setattr(transition, field_name, 2.0)

    def test_transition_copies_state_and_next_state_independently(self) -> None:
        observation = np.array([1.0, 2.0])

        transition = Transition(observation, 0, 1.0, observation, False, False)

        self.assertIsNot(transition.state, transition.next_state)
        self.assertFalse(transition.state.flags.writeable)
        self.assertFalse(transition.next_state.flags.writeable)


if __name__ == "__main__":
    unittest.main()
