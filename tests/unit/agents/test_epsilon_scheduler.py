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

    def test_invalid_schedule_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            EpsilonScheduler(0.1, 0.2, 0.9)
        with self.assertRaises(ValueError):
            EpsilonScheduler(1.0, 0.1, 0.0)
        with self.assertRaises(ValueError):
            EpsilonScheduler(math.inf, 0.1, 0.9)


if __name__ == "__main__":
    unittest.main()
