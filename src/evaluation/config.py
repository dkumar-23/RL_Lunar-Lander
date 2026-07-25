"""Immutable configuration for local checkpoint evaluation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from src.common import resolve_configuration


class EvaluationConfigurationError(ValueError):
    """Raised when evaluation configuration is incomplete or unsafe."""


@dataclass(frozen=True)
class EvaluationConfig:
    """Configuration governing deterministic, local-only evaluation."""

    validated_root: Path
    validation_root: Path
    output_root: Path
    episodes: int
    max_steps_per_episode: int
    random_seed: int
    checkpoint: str
    device: str

    def __post_init__(self) -> None:
        """Validate values before evaluation can access a bundle."""
        if self.episodes <= 0:
            raise EvaluationConfigurationError("episodes must be positive.")
        if self.max_steps_per_episode <= 0:
            raise EvaluationConfigurationError(
                "max_steps_per_episode must be positive."
            )
        if self.random_seed < 0:
            raise EvaluationConfigurationError("random_seed must be non-negative.")
        if self.checkpoint not in {"best", "final"}:
            raise EvaluationConfigurationError("checkpoint must be best or final.")
        if not self.device:
            raise EvaluationConfigurationError("device must not be empty.")

    @classmethod
    def from_file(cls, path: Path) -> EvaluationConfig:
        """Load evaluation configuration through the shared YAML resolver."""
        values = resolve_configuration(path).values
        return cls.from_mapping(values)

    @classmethod
    def from_mapping(cls, values: Mapping[str, object]) -> EvaluationConfig:
        """Construct configuration from a validated mapping."""
        try:
            validated_root = _path(values["validated_root"], "validated_root")
            validation_root = _path(values["validation_root"], "validation_root")
            output_root = _path(values["output_root"], "output_root")
            episodes = _integer(values["episodes"], "episodes")
            max_steps = _integer(
                values["max_steps_per_episode"], "max_steps_per_episode"
            )
            random_seed = _integer(values["random_seed"], "random_seed")
            checkpoint = values["checkpoint"]
            device = values["device"]
        except KeyError as exc:
            raise EvaluationConfigurationError(
                f"Missing evaluation field: {exc.args[0]}"
            ) from exc
        if not isinstance(checkpoint, str) or not isinstance(device, str):
            raise EvaluationConfigurationError("checkpoint and device must be strings.")
        return cls(
            validated_root=validated_root,
            validation_root=validation_root,
            output_root=output_root,
            episodes=episodes,
            max_steps_per_episode=max_steps,
            random_seed=random_seed,
            checkpoint=checkpoint,
            device=device,
        )


def _path(value: object, name: str) -> Path:
    if not isinstance(value, str) or not value:
        raise EvaluationConfigurationError(f"{name} must be a non-empty path string.")
    return Path(value)


def _integer(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise EvaluationConfigurationError(f"{name} must be an integer.")
    return value
