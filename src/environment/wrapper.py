"""Gymnasium wrapper integrating action failures and reward modification."""

from __future__ import annotations

from typing import Any

import gymnasium as gym

from .action_failure import ActionFailureModel
from .config import EnvironmentConfig
from .reward import Observation, RewardModifier


class ModifiedLunarLander(gym.Wrapper[Observation, int, Observation, int]):
    """Apply the assignment modifications without changing Gymnasium spaces."""

    def __init__(
        self,
        env: gym.Env[Observation, int],
        config: EnvironmentConfig,
    ) -> None:
        """Wrap a LunarLander-compatible environment.

        Args:
            env: Base environment whose dynamics and termination remain authoritative.
            config: Validated action-failure and reward configuration.
        """
        super().__init__(env)
        self._action_failure = ActionFailureModel(
            config.action_failure_probability,
            config.random_seed,
        )
        self._reward_modifier = RewardModifier(
            config.fuel_penalty,
            config.landing_bonus,
            config.landing_tolerance,
        )

    @property
    def thruster_actions_selected(self) -> int:
        """Return selected thruster count for out-of-band verification."""
        return self._action_failure.thruster_actions_selected

    @property
    def replaced_actions(self) -> int:
        """Return replacement count for out-of-band verification."""
        return self._action_failure.replaced_actions

    @property
    def fuel_penalty_count(self) -> int:
        """Return fuel penalty count for out-of-band verification."""
        return self._reward_modifier.fuel_penalty_count

    @property
    def landing_bonus_count(self) -> int:
        """Return landing bonus count for out-of-band verification."""
        return self._reward_modifier.landing_bonus_count

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[Observation, dict[str, Any]]:
        """Reset the base environment and optionally restart private randomness.

        Args:
            seed: Seed forwarded to Gymnasium and used to reseed action failures.
            options: Optional base-environment reset options.

        Returns:
            The unmodified base observation and information mapping.
        """
        if seed is not None:
            self._action_failure.reseed(seed)
        return self.env.reset(seed=seed, options=options)

    def step(
        self, selected_action: int
    ) -> tuple[Observation, float, bool, bool, dict[str, Any]]:
        """Execute one possibly failed action and modify only its reward.

        Args:
            selected_action: Original action requested by the learning algorithm.

        Returns:
            Base observation, modified reward, unchanged termination flags, and the
            original information mapping.
        """
        executed_action = self._action_failure.resolve(selected_action)
        observation, reward, terminated, truncated, info = self.env.step(
            executed_action
        )
        modified_reward = self._reward_modifier.modify(
            float(reward),
            selected_action,
            observation,
            terminated,
            truncated,
        )
        return observation, modified_reward, terminated, truncated, info
