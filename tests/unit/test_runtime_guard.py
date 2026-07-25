"""Tests for the CON-011 runtime guard."""

from __future__ import annotations

import unittest
from pathlib import Path

from src.training.runtime_guard import (
    ExecutionBoundaryError,
    attest_colab_full_training,
    validate_local_test_limits,
)


class RuntimeGuardTests(unittest.TestCase):
    """Verify local work remains bounded and full training fails closed."""

    def test_local_limits_accept_one_update(self) -> None:
        validate_local_test_limits(max_steps=32, optimization_steps=1)

    def test_local_limits_reject_unbounded_steps(self) -> None:
        with self.assertRaises(ExecutionBoundaryError):
            validate_local_test_limits(max_steps=33, optimization_steps=1)

    def test_local_limits_reject_multiple_updates(self) -> None:
        with self.assertRaises(ExecutionBoundaryError):
            validate_local_test_limits(max_steps=1, optimization_steps=2)

    def test_local_limits_reject_multiple_episodes(self) -> None:
        with self.assertRaises(ExecutionBoundaryError):
            validate_local_test_limits(1, 1, max_episodes=2)

    def test_local_limits_reject_excessive_duration(self) -> None:
        with self.assertRaises(ExecutionBoundaryError):
            validate_local_test_limits(1, 1, max_duration_seconds=60.1)

    def test_full_training_fails_outside_colab(self) -> None:
        with self.assertRaises(ExecutionBoundaryError):
            attest_colab_full_training(
                Path.cwd(),
                "a" * 40,
                Path("/content/drive/MyDrive/test"),
                1,
            )


if __name__ == "__main__":
    unittest.main()
