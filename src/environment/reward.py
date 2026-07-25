"""Deterministic assignment-specific reward modification."""

from __future__ import annotations

from typing import Any

import numpy.typing as npt

from .action_failure import THRUSTER_ACTIONS

Observation = npt.NDArray[Any]


def is_safe_landing(
    observation: Observation,
    terminated: bool,
    truncated: bool,
    tolerance: float,
) -> bool:
    """Return whether all assignment safe-landing criteria are satisfied.

    Args:
        observation: LunarLander observation returned by the base environment.
        terminated: Whether the base environment reached a terminal state.
        truncated: Whether an external time limit ended the episode.
        tolerance: Strict bound for velocities and orientation angle.

    Raises:
        ValueError: The observation lacks the required LunarLander fields.
    """
    if len(observation) < 8:
        raise ValueError("LunarLander observation must contain eight values.")
    return (
        terminated
        and not truncated
        and observation[6] == 1
        and observation[7] == 1
        and abs(observation[2]) < tolerance
        and abs(observation[3]) < tolerance
        and abs(observation[4]) < tolerance
    )


class RewardModifier:
    """Apply selected-action fuel cost and safe-landing reward."""

    def __init__(
        self,
        fuel_penalty: float,
        landing_bonus: float,
        landing_tolerance: float,
    ) -> None:
        """Initialize fixed reward values.

        Args:
            fuel_penalty: Amount deducted for any selected thruster action.
            landing_bonus: Amount added when all landing criteria are satisfied.
            landing_tolerance: Strict bound for horizontal speed, vertical speed,
                and angle.
        """
        self._fuel_penalty = fuel_penalty
        self._landing_bonus = landing_bonus
        self._landing_tolerance = landing_tolerance
        self._fuel_penalty_count = 0
        self._landing_bonus_count = 0

    @property
    def fuel_penalty_count(self) -> int:
        """Return the number of selected thruster actions charged for fuel."""
        return self._fuel_penalty_count

    @property
    def landing_bonus_count(self) -> int:
        """Return the number of safe landing bonuses awarded."""
        return self._landing_bonus_count

    def modify(
        self,
        base_reward: float,
        selected_action: int,
        observation: Observation,
        terminated: bool,
        truncated: bool,
    ) -> float:
        """Return the assignment reward for one base transition.

        Args:
            base_reward: Reward returned by the wrapped environment.
            selected_action: Original action selected before possible replacement.
            observation: Observation returned by the wrapped environment.
            terminated: Whether the base environment reached a terminal state.
            truncated: Whether the base environment reached an external time limit.

        Returns:
            Base reward minus applicable fuel cost plus applicable landing bonus.

        Raises:
            ValueError: The observation cannot contain LunarLander landing fields.
        """
        reward = base_reward
        if selected_action in THRUSTER_ACTIONS:
            reward -= self._fuel_penalty
            self._fuel_penalty_count += 1

        if is_safe_landing(
            observation,
            terminated,
            truncated,
            self._landing_tolerance,
        ):
            reward += self._landing_bonus
            self._landing_bonus_count += 1
        return reward
