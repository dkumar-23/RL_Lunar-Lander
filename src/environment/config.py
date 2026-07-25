"""Validated immutable configuration for the environment component."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class EnvironmentConfig:
    """Configuration needed to construct and modify LunarLander.

    Attributes:
        environment_name: Gymnasium environment identifier.
        random_seed: Initial seed for the wrapper's private random generator.
        action_failure_probability: Probability that a thruster action becomes zero.
        fuel_penalty: Reward deducted for a selected thruster action.
        landing_bonus: Reward added for a safe terminal landing.
        landing_tolerance: Strict velocity and angle bound for a safe landing.
        render_mode: Optional Gymnasium rendering mode.
    """

    environment_name: str
    random_seed: int
    action_failure_probability: float
    fuel_penalty: float
    landing_bonus: float
    landing_tolerance: float
    render_mode: str | None = None

    def __post_init__(self) -> None:
        """Reject configuration values that cannot preserve valid behavior.

        Raises:
            ValueError: A field is invalid or outside its supported range.
        """
        if not self.environment_name:
            raise ValueError("environment_name must not be empty.")
        if isinstance(self.random_seed, bool) or self.random_seed < 0:
            raise ValueError("random_seed must be a non-negative integer.")
        if not 0.0 <= self.action_failure_probability <= 1.0:
            raise ValueError("action_failure_probability must be between 0 and 1.")
        if self.fuel_penalty < 0.0:
            raise ValueError("fuel_penalty must be non-negative.")
        if self.landing_bonus < 0.0:
            raise ValueError("landing_bonus must be non-negative.")
        if self.landing_tolerance <= 0.0:
            raise ValueError("landing_tolerance must be positive.")
        if self.render_mode is not None and not self.render_mode:
            raise ValueError("render_mode must be non-empty when provided.")

    @classmethod
    def from_mapping(cls, values: Mapping[str, object]) -> EnvironmentConfig:
        """Create validated environment configuration from loaded YAML values.

        Args:
            values: Mapping produced by the repository configuration loader.

        Returns:
            Validated immutable environment configuration.

        Raises:
            ValueError: A required field is absent or has an invalid type or value.
        """
        try:
            environment_name = values["environment_name"]
            random_seed = values["random_seed"]
            failure_probability = values["action_failure_probability"]
            fuel_penalty = values["fuel_penalty"]
            landing_bonus = values["landing_bonus"]
            landing_tolerance = values["landing_tolerance"]
        except KeyError as exc:
            raise ValueError(
                f"Missing environment configuration field: {exc.args[0]}"
            ) from exc

        render_mode = values.get("render_mode")
        if not isinstance(environment_name, str):
            raise ValueError("environment_name must be a string.")
        if isinstance(random_seed, bool) or not isinstance(random_seed, int):
            raise ValueError("random_seed must be an integer.")
        if render_mode is not None and not isinstance(render_mode, str):
            raise ValueError("render_mode must be a string or null.")

        return cls(
            environment_name=environment_name,
            random_seed=random_seed,
            action_failure_probability=_as_float(
                failure_probability, "action_failure_probability"
            ),
            fuel_penalty=_as_float(fuel_penalty, "fuel_penalty"),
            landing_bonus=_as_float(landing_bonus, "landing_bonus"),
            landing_tolerance=_as_float(landing_tolerance, "landing_tolerance"),
            render_mode=render_mode,
        )


def _as_float(value: object, field_name: str) -> float:
    """Return a finite numeric configuration value as a float."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be numeric.")
    result = float(value)
    if result != result or result in {float("inf"), float("-inf")}:
        raise ValueError(f"{field_name} must be finite.")
    return result
