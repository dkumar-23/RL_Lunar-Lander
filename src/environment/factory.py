"""Construction of configured Gymnasium environment wrappers."""

from __future__ import annotations

from typing import cast

import gymnasium as gym

from .config import EnvironmentConfig
from .reward import Observation
from .wrapper import ModifiedLunarLander


def create_environment(config: EnvironmentConfig) -> ModifiedLunarLander:
    """Create a configured modified LunarLander environment.

    Args:
        config: Validated environment configuration.

    Returns:
        Gymnasium environment wrapped with assignment behavior.

    Raises:
        gym.error.Error: Gymnasium cannot construct the configured environment.
    """
    base_environment = gym.make(
        config.environment_name,
        render_mode=config.render_mode,
    )
    typed_environment = cast(
        gym.Env[Observation, int],
        base_environment,
    )
    return ModifiedLunarLander(typed_environment, config)
