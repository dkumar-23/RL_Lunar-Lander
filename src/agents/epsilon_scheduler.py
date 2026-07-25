"""Configuration-driven multiplicative epsilon scheduling for COMP-002."""

from __future__ import annotations

import math


class EpsilonScheduler:
    """Decay epsilon multiplicatively while enforcing a configured floor.

    Args:
        initial_epsilon: Exploration probability before any decay step.
        final_epsilon: Inclusive lower bound for exploration probability.
        decay_factor: Multiplier applied by each ``step`` call.

    Raises:
        ValueError: Values are non-finite, outside probability bounds, ordered
            incorrectly, or the decay factor is outside ``(0, 1]``.
    """

    def __init__(
        self,
        initial_epsilon: float,
        final_epsilon: float,
        decay_factor: float,
    ) -> None:
        values = (initial_epsilon, final_epsilon, decay_factor)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("epsilon schedule values must be finite.")
        if not 0.0 <= final_epsilon <= initial_epsilon <= 1.0:
            raise ValueError("epsilon values must satisfy 0 <= final <= initial <= 1.")
        if not 0.0 < decay_factor <= 1.0:
            raise ValueError("decay_factor must be in (0, 1].")
        self._initial_epsilon = initial_epsilon
        self._final_epsilon = final_epsilon
        self._decay_factor = decay_factor
        self._epsilon = initial_epsilon

    @property
    def value(self) -> float:
        """Return the current exploration probability."""
        return self._epsilon

    def step(self) -> float:
        """Apply one configured decay and return the resulting epsilon."""
        self._epsilon = max(self._final_epsilon, self._epsilon * self._decay_factor)
        return self._epsilon

    def reset(self) -> float:
        """Restore and return the configured initial epsilon."""
        self._epsilon = self._initial_epsilon
        return self._epsilon
