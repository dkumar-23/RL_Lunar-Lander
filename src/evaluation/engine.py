"""Local-only deterministic inference over a trusted training bundle."""

from __future__ import annotations

import csv
import json
from collections.abc import Callable, Mapping
from contextlib import suppress
from pathlib import Path
from typing import Any, Protocol, cast

import gymnasium as gym
import numpy as np
import torch
from torch import nn

from src.common import (
    LoadedCheckpoint,
    TrainingArtifactValidator,
    file_sha256,
    load_checkpoint,
    resolve_configuration,
)
from src.environment import EnvironmentConfig, create_environment, is_safe_landing
from src.training import Algorithm, TrainingConfig, create_agent, environment_dimensions

from .config import EvaluationConfig
from .metrics import EpisodeMetrics, aggregate_metrics
from .trust import ValidatedBundle, require_validated_bundle


class EvaluationError(RuntimeError):
    """Raised when deterministic evaluation cannot proceed safely."""


class EvaluationEnvironment(Protocol):
    """Minimal Gymnasium contract consumed by evaluation."""

    def reset(
        self, *, seed: int | None = None
    ) -> tuple[np.ndarray[Any, Any], dict[str, Any]]: ...

    def step(
        self, action: int
    ) -> tuple[np.ndarray[Any, Any], float, bool, bool, dict[str, Any]]: ...

    def close(self) -> None: ...


class EvaluationAgent(Protocol):
    """Inference-only subset shared by DQN and DDQN agents."""

    device: torch.device
    online_network: nn.Module
    target_network: nn.Module

    def select_action(
        self, observation: np.ndarray[Any, Any], explore: bool
    ) -> int: ...

    def eval(self) -> None: ...


CheckpointLoader = Callable[..., LoadedCheckpoint]
AgentFactory = Callable[
    [str, Mapping[str, Any], str, EvaluationEnvironment], EvaluationAgent
]
EnvironmentFactory = Callable[[str, EnvironmentConfig], EvaluationEnvironment]


class EvaluationEngine:
    """Validate, load, infer, prove immutability, and export evaluation results."""

    def __init__(
        self,
        config: EvaluationConfig,
        *,
        validator: TrainingArtifactValidator | None = None,
        checkpoint_loader: CheckpointLoader = load_checkpoint,
        agent_factory: AgentFactory | None = None,
        environment_factory: EnvironmentFactory | None = None,
    ) -> None:
        """Store injected local-only dependencies without touching artifacts."""
        self._config = config
        self._validator = validator
        self._checkpoint_loader = checkpoint_loader
        self._agent_factory = agent_factory or _build_agent
        self._environment_factory = environment_factory or _build_environment

    def evaluate(
        self, bundle_path: Path
    ) -> tuple[list[EpisodeMetrics], dict[str, Any]]:
        """Evaluate one best/final checkpoint only after all trust gates pass."""
        trusted = require_validated_bundle(
            bundle_path,
            validated_root=self._config.validated_root,
            validation_root=self._config.validation_root,
            validator=self._validator,
        )
        resolved = resolve_configuration(trusted.path / "resolved_config.yaml")
        if resolved.sha256 != trusted.manifest.get("configuration_hash"):
            raise EvaluationError("Resolved configuration differs from the manifest.")

        checkpoint_path = (
            trusted.path / "checkpoints" / f"{self._config.checkpoint}_checkpoint.pt"
        )
        checkpoint = self._checkpoint_loader(
            checkpoint_path, map_location=self._config.device
        )
        self._validate_checkpoint_identity(trusted, checkpoint)
        algorithm = cast(str, trusted.manifest["algorithm"])
        environment_config = _environment_config(
            resolved.values, self._config.random_seed
        )
        variant = cast(str, trusted.manifest["environment_variant"])
        environment = self._environment_factory(variant, environment_config)
        try:
            agent = self._agent_factory(
                algorithm, resolved.values, self._config.device, environment
            )
            try:
                agent.online_network.load_state_dict(
                    checkpoint.model_state, strict=True
                )
                agent.target_network.load_state_dict(
                    checkpoint.target_state, strict=True
                )
            except (RuntimeError, ValueError) as exc:
                raise EvaluationError(
                    "Checkpoint state is incompatible with the model."
                ) from exc

            before = _snapshot(agent)
            agent.eval()
            agent.online_network.requires_grad_(False)
            agent.target_network.requires_grad_(False)
            episodes: list[EpisodeMetrics] = []
            with torch.inference_mode():
                for episode in range(1, self._config.episodes + 1):
                    episodes.append(
                        self._evaluate_episode(
                            agent,
                            environment,
                            episode,
                            environment_config.landing_tolerance,
                        )
                    )
            if not _state_matches(agent, before):
                raise EvaluationError(
                    "Model parameters or buffers changed during evaluation."
                )
        finally:
            with suppress(Exception):
                environment.close()
        summary = aggregate_metrics(episodes)
        summary.update(
            {
                "experiment_id": trusted.experiment_id,
                "run_id": trusted.run_id,
                "algorithm": algorithm,
                "environment_variant": variant,
                "configuration_hash": resolved.sha256,
                "source_manifest_sha256": trusted.manifest_sha256,
                "validation_report": str(trusted.validation_report),
                "checkpoint": self._config.checkpoint,
                "checkpoint_sha256": file_sha256(checkpoint_path),
                "random_seed": self._config.random_seed,
                "exploration_enabled": False,
                "gradients_enabled": False,
                "parameters_unchanged": True,
            }
        )
        self.export(trusted, episodes, summary)
        return episodes, summary

    def _evaluate_episode(
        self,
        agent: EvaluationAgent,
        environment: EvaluationEnvironment,
        episode: int,
        landing_tolerance: float,
    ) -> EpisodeMetrics:
        observation, _ = environment.reset(seed=self._config.random_seed + episode - 1)
        total_reward = 0.0
        selected_q_values: list[float] = []
        terminated = False
        truncated = False
        length = 0
        for step_number in range(1, self._config.max_steps_per_episode + 1):
            length = step_number
            action = agent.select_action(observation, explore=False)
            tensor = torch.as_tensor(
                observation, dtype=torch.float32, device=agent.device
            ).unsqueeze(0)
            q_values = cast(torch.Tensor, agent.online_network(tensor))
            if q_values.ndim != 2 or q_values.shape[0] != 1:
                raise EvaluationError("Agent returned an invalid Q-value tensor.")
            if action < 0 or action >= q_values.shape[1]:
                raise EvaluationError("Agent selected an action outside its Q-values.")
            selected_q_values.append(float(q_values[0, action].item()))
            observation, reward, terminated, truncated, _ = environment.step(action)
            total_reward += float(reward)
            if terminated or truncated:
                break
        if not (terminated or truncated):
            truncated = True
        success = bool(
            is_safe_landing(observation, terminated, truncated, landing_tolerance)
        )
        return EpisodeMetrics(
            episode=episode,
            total_reward=total_reward,
            episode_length=length,
            landing_success=success,
            mean_selected_q=float(np.mean(selected_q_values)),
        )

    def export(
        self,
        bundle: ValidatedBundle,
        episodes: list[EpisodeMetrics],
        summary: Mapping[str, Any],
    ) -> None:
        """Persist raw observations and their traceable aggregate summary."""
        destination = self._config.output_root / bundle.experiment_id / bundle.run_id
        try:
            destination.mkdir(parents=True, exist_ok=False)
        except FileExistsError as exc:
            raise EvaluationError(
                "Evaluation output already exists and will not be overwritten: "
                f"{destination}"
            ) from exc
        metrics_path = destination / "evaluation_metrics.csv"
        with metrics_path.open("w", encoding="utf-8", newline="") as stream:
            fieldnames = [
                "experiment_id",
                "run_id",
                "source_manifest_sha256",
                "episode",
                "total_reward",
                "episode_length",
                "landing_success",
                "mean_selected_q",
            ]
            writer = csv.DictWriter(stream, fieldnames=fieldnames)
            writer.writeheader()
            for episode in episodes:
                writer.writerow(
                    {
                        "experiment_id": bundle.experiment_id,
                        "run_id": bundle.run_id,
                        "source_manifest_sha256": bundle.manifest_sha256,
                        **episode.to_dict(),
                    }
                )
        _write_json(destination / "evaluation_summary.json", summary)

    @staticmethod
    def _validate_checkpoint_identity(
        bundle: ValidatedBundle, checkpoint: LoadedCheckpoint
    ) -> None:
        metadata = checkpoint.metadata
        manifest = bundle.manifest
        if metadata.experiment_id != bundle.experiment_id:
            raise EvaluationError("Checkpoint experiment does not match the bundle.")
        if metadata.run_id != bundle.run_id:
            raise EvaluationError("Checkpoint run does not match the bundle.")
        if metadata.configuration_hash != manifest.get("configuration_hash"):
            raise EvaluationError("Checkpoint configuration hash does not match.")
        if metadata.git_sha != manifest.get("resolved_git_commit"):
            raise EvaluationError("Checkpoint Git commit does not match.")
        if metadata.seed != manifest.get("random_seed"):
            raise EvaluationError("Checkpoint seed does not match.")


def _build_agent(
    algorithm: str,
    values: Mapping[str, Any],
    device: str,
    environment: EvaluationEnvironment,
) -> EvaluationAgent:
    training = TrainingConfig.from_mapping(_mapping(values.get("training"), "training"))
    try:
        selected_algorithm = Algorithm(algorithm)
    except ValueError as exc:
        raise EvaluationError(f"Unsupported algorithm: {algorithm}") from exc
    input_dim, action_count = environment_dimensions(environment)
    return create_agent(
        training,
        selected_algorithm,
        input_dim,
        action_count,
        np.random.default_rng(0),
        device=device,
    )


def _build_environment(
    variant: str, config: EnvironmentConfig
) -> EvaluationEnvironment:
    if variant == "modified":
        return cast(EvaluationEnvironment, create_environment(config))
    if variant == "original":
        return cast(
            EvaluationEnvironment,
            gym.make(config.environment_name, render_mode=config.render_mode),
        )
    raise EvaluationError(f"Unsupported environment variant: {variant}")


def _environment_config(
    values: Mapping[str, Any], evaluation_seed: int
) -> EnvironmentConfig:
    raw = values.get("environment", values)
    mapping = _mapping(raw, "environment")
    configured = EnvironmentConfig.from_mapping(mapping)
    return EnvironmentConfig(
        environment_name=configured.environment_name,
        random_seed=evaluation_seed,
        action_failure_probability=configured.action_failure_probability,
        fuel_penalty=configured.fuel_penalty,
        landing_bonus=configured.landing_bonus,
        landing_tolerance=configured.landing_tolerance,
        render_mode=configured.render_mode,
    )


def _mapping(value: object, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise EvaluationError(f"{name} must be a mapping.")
    return cast(Mapping[str, Any], value)


def _snapshot(agent: EvaluationAgent) -> dict[str, torch.Tensor]:
    return {
        f"online.{name}": value.detach().cpu().clone()
        for name, value in agent.online_network.state_dict().items()
    } | {
        f"target.{name}": value.detach().cpu().clone()
        for name, value in agent.target_network.state_dict().items()
    }


def _state_matches(
    agent: EvaluationAgent, expected: Mapping[str, torch.Tensor]
) -> bool:
    observed = _snapshot(agent)
    return observed.keys() == expected.keys() and all(
        torch.equal(observed[name], value) for name, value in expected.items()
    )


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(dict(value), indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
