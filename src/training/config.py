"""Immutable configuration contracts for shared DQN/DDQN training."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from src.common import resolve_configuration
from src.environment import EnvironmentConfig


class Algorithm(StrEnum):
    """Supported value-learning algorithms."""

    DQN = "DQN"
    DDQN = "DDQN"


class EnvironmentVariant(StrEnum):
    """Canonical LunarLander environment variants."""

    ORIGINAL = "original"
    MODIFIED = "modified"


@dataclass(frozen=True)
class TrainingConfig:
    """Validated controls shared by every canonical experiment."""

    random_seed: int
    episodes: int
    max_steps_per_episode: int
    hidden_sizes: tuple[int, ...]
    activation: str
    optimizer: str
    learning_rate: float
    discount_factor: float
    replay_capacity: int
    batch_size: int
    warmup_steps: int
    optimization_frequency: int
    target_sync_interval: int
    epsilon_initial: float
    epsilon_final: float
    epsilon_decay: float
    validation_state_count: int
    validation_seed: int
    checkpoint_interval: int
    success_window: int
    loss_function: str
    device: str
    deterministic: bool

    def __post_init__(self) -> None:
        """Reject controls that cannot produce a valid shared training run."""
        positive = {
            "episodes": self.episodes,
            "max_steps_per_episode": self.max_steps_per_episode,
            "replay_capacity": self.replay_capacity,
            "batch_size": self.batch_size,
            "warmup_steps": self.warmup_steps,
            "optimization_frequency": self.optimization_frequency,
            "target_sync_interval": self.target_sync_interval,
            "validation_state_count": self.validation_state_count,
            "checkpoint_interval": self.checkpoint_interval,
            "success_window": self.success_window,
        }
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value <= 0
            for value in positive.values()
        ):
            raise ValueError("Training counts and intervals must be positive integers.")
        if (
            isinstance(self.random_seed, bool)
            or not isinstance(self.random_seed, int)
            or self.random_seed < 0
            or isinstance(self.validation_seed, bool)
            or not isinstance(self.validation_seed, int)
            or self.validation_seed < 0
        ):
            raise ValueError(
                "Training and validation seeds must be non-negative integers."
            )
        if not self.hidden_sizes or any(
            isinstance(size, bool) or not isinstance(size, int) or size <= 0
            for size in self.hidden_sizes
        ):
            raise ValueError("hidden_sizes must contain positive integers.")
        if self.batch_size > self.replay_capacity:
            raise ValueError("batch_size cannot exceed replay_capacity.")
        if self.warmup_steps < self.batch_size:
            raise ValueError("warmup_steps cannot be smaller than batch_size.")
        if self.activation != "relu":
            raise ValueError("Only the canonical relu activation is supported.")
        if self.optimizer != "adam":
            raise ValueError("Only the canonical adam optimizer is supported.")
        if self.loss_function not in {"mse", "smooth_l1"}:
            raise ValueError("loss_function must be mse or smooth_l1.")
        if self.device not in {"auto", "cpu", "cuda"}:
            raise ValueError("device must be auto, cpu, or cuda.")
        if not isinstance(self.deterministic, bool):
            raise ValueError("deterministic must be a bool.")
        if not math.isfinite(self.learning_rate) or self.learning_rate <= 0.0:
            raise ValueError("learning_rate must be finite and positive.")
        if (
            not math.isfinite(self.discount_factor)
            or not 0.0 <= self.discount_factor <= 1.0
        ):
            raise ValueError("discount_factor must be finite and in [0, 1].")
        epsilon_values = (
            self.epsilon_initial,
            self.epsilon_final,
            self.epsilon_decay,
        )
        if not all(math.isfinite(value) for value in epsilon_values):
            raise ValueError("Epsilon controls must be finite.")
        if not 0.0 <= self.epsilon_final <= self.epsilon_initial <= 1.0:
            raise ValueError("Epsilon bounds are invalid.")
        if not 0.0 < self.epsilon_decay <= 1.0:
            raise ValueError("epsilon_decay must be in (0, 1].")

    @classmethod
    def from_mapping(cls, values: Mapping[str, object]) -> TrainingConfig:
        """Construct a validated configuration from resolved YAML values."""
        try:
            hidden_sizes = values["hidden_sizes"]
            if not isinstance(hidden_sizes, list):
                raise ValueError("hidden_sizes must be a list.")
            return cls(
                random_seed=_integer(values, "random_seed"),
                episodes=_integer(values, "episodes"),
                max_steps_per_episode=_integer(values, "max_steps_per_episode"),
                hidden_sizes=tuple(
                    _integer_item(item, "hidden_sizes") for item in hidden_sizes
                ),
                activation=_string(values, "activation"),
                optimizer=_string(values, "optimizer"),
                learning_rate=_number(values, "learning_rate"),
                discount_factor=_number(values, "discount_factor"),
                replay_capacity=_integer(values, "replay_capacity"),
                batch_size=_integer(values, "batch_size"),
                warmup_steps=_integer(values, "warmup_steps"),
                optimization_frequency=_integer(values, "optimization_frequency"),
                target_sync_interval=_integer(values, "target_sync_interval"),
                epsilon_initial=_number(values, "epsilon_initial"),
                epsilon_final=_number(values, "epsilon_final"),
                epsilon_decay=_number(values, "epsilon_decay"),
                validation_state_count=_integer(values, "validation_state_count"),
                validation_seed=_integer(values, "validation_seed"),
                checkpoint_interval=_integer(values, "checkpoint_interval"),
                success_window=_integer(values, "success_window"),
                loss_function=_string(values, "loss_function"),
                device=_string(values, "device"),
                deterministic=_boolean(values, "deterministic"),
            )
        except KeyError as exc:
            raise ValueError(
                f"Missing training configuration field: {exc.args[0]}"
            ) from exc

    def to_dict(self) -> dict[str, object]:
        """Return a YAML-safe representation of the immutable controls."""
        result = asdict(self)
        result["hidden_sizes"] = list(self.hidden_sizes)
        return result


@dataclass(frozen=True)
class ExperimentConfig:
    """One canonical experiment identity and its fully resolved controls."""

    experiment_id: str
    algorithm: Algorithm
    environment_variant: EnvironmentVariant
    training: TrainingConfig
    environment: EnvironmentConfig
    source_path: Path

    def resolved_values(self) -> dict[str, Any]:
        """Return the complete immutable run configuration for persistence."""
        environment = asdict(self.environment)
        return {
            "experiment_id": self.experiment_id,
            "algorithm": self.algorithm.value,
            "environment_variant": self.environment_variant.value,
            "training": self.training.to_dict(),
            "environment": environment,
        }


_CANONICAL_MATRIX = {
    "EXP-001": (Algorithm.DQN, EnvironmentVariant.ORIGINAL),
    "EXP-002": (Algorithm.DQN, EnvironmentVariant.MODIFIED),
    "EXP-003": (Algorithm.DDQN, EnvironmentVariant.ORIGINAL),
    "EXP-004": (Algorithm.DDQN, EnvironmentVariant.MODIFIED),
}


def load_experiment_config(path: Path, repository_root: Path) -> ExperimentConfig:
    """Resolve one canonical definition and its shared referenced configuration.

    Args:
        path: Canonical experiment YAML selected for this invocation.
        repository_root: Repository root used to resolve controlled references.

    Returns:
        Validated experiment identity, shared training controls, and environment.

    Raises:
        ValueError: The definition is non-canonical or references an unsafe path.
    """
    repository_root = repository_root.resolve()
    definition_path = path.resolve()
    definition = resolve_configuration(definition_path).values
    experiment_id = _string(definition, "experiment_id")
    try:
        algorithm = Algorithm(_string(definition, "algorithm"))
        variant = EnvironmentVariant(_string(definition, "environment_variant"))
    except ValueError as exc:
        raise ValueError("Unsupported algorithm or environment variant.") from exc
    if _CANONICAL_MATRIX.get(experiment_id) != (algorithm, variant):
        raise ValueError("Experiment identity does not match the canonical matrix.")

    training_path = _repository_path(
        repository_root, _string(definition, "training_config")
    )
    environment_path = _repository_path(
        repository_root, _string(definition, "environment_config")
    )
    training = TrainingConfig.from_mapping(resolve_configuration(training_path).values)
    environment = EnvironmentConfig.from_mapping(
        resolve_configuration(environment_path).values
    )
    if training.random_seed != environment.random_seed:
        raise ValueError("Training and environment random seeds must match.")
    if variant is EnvironmentVariant.ORIGINAL:
        environment = EnvironmentConfig(
            environment_name=environment.environment_name,
            random_seed=environment.random_seed,
            action_failure_probability=0.0,
            fuel_penalty=0.0,
            landing_bonus=0.0,
            landing_tolerance=environment.landing_tolerance,
            render_mode=environment.render_mode,
        )
    return ExperimentConfig(
        experiment_id=experiment_id,
        algorithm=algorithm,
        environment_variant=variant,
        training=training,
        environment=environment,
        source_path=definition_path,
    )


def load_training_config(path: Path) -> TrainingConfig:
    """Load and validate shared training controls for bounded local checks."""
    return TrainingConfig.from_mapping(resolve_configuration(path).values)


def resolved_experiment_sha256(experiment: ExperimentConfig) -> str:
    """Return the canonical identity persisted as the run configuration hash."""
    canonical = json.dumps(
        experiment.resolved_values(),
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def validate_registered_configuration(
    experiment: ExperimentConfig,
    repository_root: Path,
) -> str:
    """Require one experiment to match the tracked canonical hash registry."""
    repository_root = repository_root.resolve()
    registry_path = repository_root / "experiments" / "canonical_hashes.json"
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Canonical configuration hash registry is invalid.") from exc
    if not isinstance(registry, dict) or set(registry) != {
        "schema_version",
        "experiments",
    }:
        raise ValueError("Canonical configuration hash registry fields are invalid.")
    entries = registry.get("experiments")
    if registry.get("schema_version") != "1.0.0" or not isinstance(entries, dict):
        raise ValueError("Canonical configuration hash registry schema is invalid.")
    if set(entries) != set(_CANONICAL_MATRIX):
        raise ValueError(
            "Canonical configuration hash registry must contain four runs."
        )
    entry = entries.get(experiment.experiment_id)
    if not isinstance(entry, dict) or set(entry) != {
        "configuration_path",
        "resolved_configuration_sha256",
    }:
        raise ValueError("Canonical configuration hash entry is invalid.")
    expected_path = experiment.source_path.relative_to(repository_root).as_posix()
    if entry.get("configuration_path") != expected_path:
        raise ValueError("Selected configuration path is not preregistered.")
    observed_hash = resolved_experiment_sha256(experiment)
    if entry.get("resolved_configuration_sha256") != observed_hash:
        raise ValueError("Resolved configuration differs from its preregistered hash.")
    return observed_hash


def _repository_path(root: Path, value: str) -> Path:
    candidate = (root / value).resolve()
    if root not in (candidate, *candidate.parents):
        raise ValueError("Configuration references must remain in the repository.")
    return candidate


def _integer(values: Mapping[str, object], name: str) -> int:
    return _integer_item(values[name], name)


def _integer_item(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must contain integers.")
    return value


def _number(values: Mapping[str, object], name: str) -> float:
    value = values[name]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric.")
    return float(value)


def _string(values: Mapping[str, object], name: str) -> str:
    value = values[name]
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a non-empty string.")
    return value


def _boolean(values: Mapping[str, object], name: str) -> bool:
    value = values[name]
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be a bool.")
    return value
