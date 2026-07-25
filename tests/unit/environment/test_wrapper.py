"""Unit tests for exact modified-environment transition semantics."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from src.common.configuration import resolve_configuration
from src.environment import EnvironmentConfig, ModifiedLunarLander, is_safe_landing

from .fakes import FakeLanderEnv


def make_config(
    *,
    failure_probability: float = 0.15,
    seed: int = 7,
) -> EnvironmentConfig:
    """Return assignment-valued configuration with selectable failure behavior."""
    return EnvironmentConfig(
        environment_name="FakeLander-v0",
        random_seed=seed,
        action_failure_probability=failure_probability,
        fuel_penalty=0.3,
        landing_bonus=50.0,
        landing_tolerance=0.10,
    )


def test_environment_yaml_loads_through_existing_configuration_utility() -> None:
    """Ensure the checked-in environment values are valid and exact."""
    root = Path(__file__).parents[3]
    resolved = resolve_configuration(root / "configs" / "environment.yaml")
    config = EnvironmentConfig.from_mapping(resolved.values)

    assert config.action_failure_probability == 0.15
    assert config.fuel_penalty == 0.3
    assert config.landing_bonus == 50.0
    assert config.landing_tolerance == 0.10


def test_action_zero_is_unchanged_and_does_not_count_as_thruster() -> None:
    """Action zero must bypass even a certain failure model."""
    base = FakeLanderEnv()
    wrapper = ModifiedLunarLander(base, make_config(failure_probability=1.0))

    wrapper.step(0)

    assert base.executed_actions == [0]
    assert wrapper.thruster_actions_selected == 0
    assert wrapper.replaced_actions == 0
    assert wrapper.fuel_penalty_count == 0


@pytest.mark.parametrize("selected_action", [1, 2, 3])
def test_each_thruster_can_be_replaced_before_base_step(selected_action: int) -> None:
    """A failed thruster request must execute action zero in the base environment."""
    base = FakeLanderEnv()
    wrapper = ModifiedLunarLander(base, make_config(failure_probability=1.0))

    _, reward, _, _, _ = wrapper.step(selected_action)

    assert base.executed_actions == [0]
    assert reward == pytest.approx(9.7)
    assert wrapper.thruster_actions_selected == 1
    assert wrapper.replaced_actions == 1
    assert wrapper.fuel_penalty_count == 1


@pytest.mark.parametrize("selected_action", [1, 2, 3])
def test_each_thruster_executes_when_bernoulli_does_not_fail(
    selected_action: int,
) -> None:
    """An unsuccessful failure draw must preserve the requested action."""
    base = FakeLanderEnv()
    wrapper = ModifiedLunarLander(base, make_config(failure_probability=0.0))

    wrapper.step(selected_action)

    assert base.executed_actions == [selected_action]


def test_step_preserves_spaces_transition_fields_and_info_identity() -> None:
    """Only action execution and reward may differ from the base transition."""
    base = FakeLanderEnv()
    base.terminated = True
    wrapper = ModifiedLunarLander(base, make_config(failure_probability=0.0))

    result = wrapper.step(0)

    assert wrapper.observation_space is base.observation_space
    assert wrapper.action_space is base.action_space
    assert result[0] is base.observation
    assert result[2] is True
    assert result[3] is False
    assert result[4] is base.info
    assert result[4] == {"base": "unchanged"}


def test_safe_terminal_landing_adds_bonus_and_selected_fuel_penalty() -> None:
    """All safe criteria can combine landing bonus and selected-action fuel cost."""
    base = FakeLanderEnv()
    base.observation = np.array(
        [0.0, 0.0, 0.09, -0.09, 0.09, 0.0, 1.0, 1.0],
        dtype=np.float32,
    )
    base.terminated = True
    wrapper = ModifiedLunarLander(base, make_config(failure_probability=1.0))

    _, reward, _, _, info = wrapper.step(2)

    assert reward == pytest.approx(59.7)
    assert wrapper.landing_bonus_count == 1
    assert info is base.info


def test_safe_landing_predicate_returns_python_bool() -> None:
    observation = np.array(
        [0.0, 0.0, 0.09, -0.09, 0.09, 0.0, 1.0, 1.0],
        dtype=np.float32,
    )

    result = is_safe_landing(observation, True, False, 0.10)

    assert result is True


@pytest.mark.parametrize(
    ("observation", "terminated", "truncated"),
    [
        ([0.0, 0.0, 0.10, 0.0, 0.0, 0.0, 1.0, 1.0], True, False),
        ([0.0, 0.0, 0.0, -0.10, 0.0, 0.0, 1.0, 1.0], True, False),
        ([0.0, 0.0, 0.0, 0.0, 0.10, 0.0, 1.0, 1.0], True, False),
        ([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0], True, False),
        ([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0], True, False),
        ([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0], False, False),
        ([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0], True, True),
    ],
)
def test_landing_bonus_requires_every_strict_criterion(
    observation: list[float],
    terminated: bool,
    truncated: bool,
) -> None:
    """Missing any exact success criterion must suppress the landing bonus."""
    base = FakeLanderEnv()
    base.observation = np.asarray(observation, dtype=np.float32)
    base.terminated = terminated
    base.truncated = truncated
    wrapper = ModifiedLunarLander(base, make_config(failure_probability=0.0))

    _, reward, _, _, _ = wrapper.step(0)

    assert reward == pytest.approx(10.0)
    assert wrapper.landing_bonus_count == 0


def test_reset_forwards_seed_and_preserves_base_reset_values() -> None:
    """Wrapper reset must retain the standard Gymnasium contract."""
    base = FakeLanderEnv()
    wrapper = ModifiedLunarLander(base, make_config())

    observation, info = wrapper.reset(seed=123)

    assert base.last_reset_seed == 123
    assert observation is base.observation
    assert info is base.info
