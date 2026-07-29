"""Unit tests for configured epsilon decay."""

from __future__ import annotations

import math
import unittest

from src.agents import EpsilonScheduler


class EpsilonSchedulerTests(unittest.TestCase):
    """Verify multiplicative decay, flooring, and reset behavior."""

    def test_schedule_decays_to_configured_floor(self) -> None:
        scheduler = EpsilonScheduler(1.0, 0.2, 0.5)

        self.assertEqual(scheduler.step(), 0.5)
        self.assertEqual(scheduler.step(), 0.25)
        self.assertEqual(scheduler.step(), 0.2)
        self.assertEqual(scheduler.step(), 0.2)
        self.assertEqual(scheduler.reset(), 1.0)

    def test_run_002_exact_epsilon_values(self) -> None:
        """RUN-002: decay=0.9995, episodes=2000, initial=1.0, final=0.01.
        Formula: epsilon(N)_start = max(0.01, 1.0 * 0.9995^(N-1))
        """
        scheduler = EpsilonScheduler(1.0, 0.01, 0.9995)
        # Episode 0 / before training
        self.assertAlmostEqual(scheduler.value, 1.0)
        # Episode 1 start
        self.assertAlmostEqual(scheduler.value, 1.0)
        for _ in range(499):
            scheduler.step()
        # Episode 500 start
        self.assertAlmostEqual(scheduler.value, 0.77914166, places=6)
        for _ in range(500):
            scheduler.step()
        # Episode 1000 start
        self.assertAlmostEqual(scheduler.value, 0.60675820, places=6)
        for _ in range(500):
            scheduler.step()
        # Episode 1500 start
        self.assertAlmostEqual(scheduler.value, 0.47251422, places=6)
        for _ in range(500):
            scheduler.step()
        # Episode 2000 start
        self.assertAlmostEqual(scheduler.value, 0.36797144, places=6)

    def test_run_003_exact_epsilon_values(self) -> None:
        """RUN-003: decay=0.9985, episodes=2000, initial=1.0, final=0.01.
        Formula: epsilon(N)_start = max(0.01, 1.0 * 0.9985^(N-1))
        """
        scheduler = EpsilonScheduler(1.0, 0.01, 0.9985)
        # Episode 0 / before training
        self.assertAlmostEqual(scheduler.value, 1.0)
        # Episode 1 start
        self.assertAlmostEqual(scheduler.value, 1.0)
        for _ in range(499):
            scheduler.step()
        # Episode 500 start
        self.assertAlmostEqual(scheduler.value, 0.47280987, places=6)
        for _ in range(500):
            scheduler.step()
        # Episode 1000 start
        self.assertAlmostEqual(scheduler.value, 0.22321385, places=6)
        for _ in range(500):
            scheduler.step()
        # Episode 1500 start
        self.assertAlmostEqual(scheduler.value, 0.10537940, places=6)
        for _ in range(500):
            scheduler.step()
        # Episode 2000 start
        self.assertAlmostEqual(scheduler.value, 0.04974969, places=6)

    def test_invalid_schedule_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            EpsilonScheduler(0.1, 0.2, 0.9)
        with self.assertRaises(ValueError):
            EpsilonScheduler(1.0, 0.1, 0.0)
        with self.assertRaises(ValueError):
            EpsilonScheduler(math.inf, 0.1, 0.9)


if __name__ == "__main__":
    unittest.main()
