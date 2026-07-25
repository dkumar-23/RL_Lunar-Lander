"""Private, reproducible stochastic replacement of thruster actions."""

from __future__ import annotations

import numpy as np

THRUSTER_ACTIONS = frozenset({1, 2, 3})
DO_NOTHING_ACTION = 0


class ActionFailureModel:
    """Replace eligible actions using an isolated Bernoulli random process."""

    def __init__(self, failure_probability: float, seed: int) -> None:
        """Initialize action failure behavior.

        Args:
            failure_probability: Bernoulli probability for each thruster request.
            seed: Seed for the model's private random generator.

        Raises:
            ValueError: The probability is outside the closed interval [0, 1].
        """
        if not 0.0 <= failure_probability <= 1.0:
            raise ValueError("failure_probability must be between 0 and 1.")
        self._failure_probability = failure_probability
        self._rng = np.random.default_rng(seed)
        self._thruster_actions_selected = 0
        self._replaced_actions = 0

    @property
    def thruster_actions_selected(self) -> int:
        """Return the number of eligible actions requested."""
        return self._thruster_actions_selected

    @property
    def replaced_actions(self) -> int:
        """Return the number of eligible actions replaced with action zero."""
        return self._replaced_actions

    def reseed(self, seed: int) -> None:
        """Restart the private replacement sequence from ``seed``.

        Args:
            seed: Non-negative NumPy-compatible random seed.
        """
        self._rng = np.random.default_rng(seed)

    def resolve(self, requested_action: int) -> int:
        """Resolve one requested action to the action executed by Gymnasium.

        Args:
            requested_action: Action selected by the learning algorithm.

        Returns:
            Action zero on an eligible failure, otherwise the requested action.
        """
        if requested_action not in THRUSTER_ACTIONS:
            return requested_action

        self._thruster_actions_selected += 1
        if self._rng.random() < self._failure_probability:
            self._replaced_actions += 1
            return DO_NOTHING_ACTION
        return requested_action
