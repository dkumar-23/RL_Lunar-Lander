"""Algorithm-agnostic episode orchestration for DQN and DDQN."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol, cast

import numpy as np

from src.agents import BaseAgent
from src.environment import EnvironmentConfig, is_safe_landing
from src.memory import Observation, ReplayBuffer, Transition

from .config import TrainingConfig
from .runtime_guard import (
    ColabTrainingAttestation,
    ExecutionBoundaryError,
    ExecutionContext,
    validate_local_test_limits,
)
from .validation import FixedValidationSet, mean_max_predicted_q


class TrainingEnvironment(Protocol):
    """Environment contract consumed by the training orchestrator."""

    @property
    def replaced_actions(self) -> int:
        """Return the cumulative wrapper action-replacement count."""

    def reset(
        self, *, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[Observation, dict[str, Any]]:
        """Reset and return one observation and base information mapping."""

    def step(
        self, action: int
    ) -> tuple[Observation, float, bool, bool, dict[str, Any]]:
        """Apply one selected action through the public environment API."""


@dataclass(frozen=True)
class LocalLimits:
    """Non-promotable local execution limits authorized by RuntimeGuard."""

    max_environment_steps: int
    max_optimization_steps: int
    max_episodes: int = 1
    max_duration_seconds: float = 60.0


@dataclass(frozen=True)
class OptimizationMetrics:
    """Episode-level optimization summary persisted in ``metrics.csv``."""

    global_step: int
    episode: int
    optimization_step: int
    loss: float | None
    mean_predicted_q: float
    epsilon: float
    learning_rate: float
    replay_size: int


@dataclass(frozen=True)
class EpisodeMetrics:
    """Complete per-episode measurements needed by downstream plots."""

    episode: int
    total_reward: float
    episode_length: int
    terminated: bool
    truncated: bool
    landing_success: bool
    thruster_actions_selected: int
    thruster_actions_executed: int
    thruster_failures: int
    fuel_penalty_total: float
    landing_bonus_total: float
    mean_predicted_q: float
    epsilon: float
    duration_seconds: float


@dataclass(frozen=True)
class TrainingResult:
    """Bounded in-memory summary returned after one engine invocation."""

    optimization_metrics: tuple[OptimizationMetrics, ...]
    episode_metrics: tuple[EpisodeMetrics, ...]
    global_steps: int
    optimization_steps: int


CheckpointCallback = Callable[[str, int, int, dict[str, object] | None], None]


class TrainingEngine:
    """Coordinate episodes, replay, learning schedules, metrics, and checkpoints.

    Algorithm-specific target computation remains entirely in the injected agent.
    Local execution requires explicit RuntimeGuard-validated hard limits.
    """

    def __init__(
        self,
        config: TrainingConfig,
        environment_config: EnvironmentConfig,
        environment: TrainingEnvironment,
        agent: BaseAgent,
        replay_buffer: ReplayBuffer,
        validation_set: FixedValidationSet,
        execution_context: ExecutionContext,
        *,
        colab_attestation: ColabTrainingAttestation | None = None,
        logger: logging.Logger | None = None,
        checkpoint_callback: CheckpointCallback | None = None,
        start_episode: int = 1,
        global_steps: int = 0,
    ) -> None:
        """Initialize orchestration dependencies without starting execution."""
        if (
            isinstance(start_episode, bool)
            or not isinstance(start_episode, int)
            or start_episode <= 0
            or isinstance(global_steps, bool)
            or not isinstance(global_steps, int)
            or global_steps < 0
        ):
            raise ValueError("Resume episode and global steps are invalid.")
        self.config = config
        self.environment_config = environment_config
        self.environment = environment
        self.agent = agent
        self.replay_buffer = replay_buffer
        self.validation_set = validation_set
        self.execution_context = execution_context
        self.colab_attestation = colab_attestation
        self.logger = logger or logging.getLogger(__name__)
        self.checkpoint_callback = checkpoint_callback
        self.start_episode = start_episode
        self._global_steps = global_steps
        self._has_run = False

    def initialize(self) -> None:
        """Place agent networks in their required training modes."""
        self.agent.train()

    def run(self, local_limits: LocalLimits | None = None) -> TrainingResult:
        """Run one full Colab experiment or one bounded local smoke path.

        Args:
            local_limits: Mandatory non-promotable limits for ``LOCAL_TEST``.

        Returns:
            Episode and optimization summaries from this invocation.

        Raises:
            ExecutionBoundaryError: Local limits are absent or exceed hard caps.
            RuntimeError: This one-invocation engine has already run.
            ValueError: Full execution is supplied local-only limits.
        """
        if self._has_run:
            raise RuntimeError("A TrainingEngine instance can run only once.")
        step_limit: int | None = None
        optimization_limit: int | None = None
        episode_limit: int | None = None
        duration_limit: float | None = None
        if self.execution_context is ExecutionContext.LOCAL_TEST:
            if local_limits is None:
                raise ExecutionBoundaryError(
                    "Local execution requires explicit RuntimeGuard limits."
                )
            validate_local_test_limits(
                local_limits.max_environment_steps,
                local_limits.max_optimization_steps,
                local_limits.max_episodes,
                local_limits.max_duration_seconds,
            )
            step_limit = local_limits.max_environment_steps
            optimization_limit = local_limits.max_optimization_steps
            episode_limit = local_limits.max_episodes
            duration_limit = local_limits.max_duration_seconds
        elif local_limits is not None:
            raise ValueError("Local limits cannot be supplied to full training.")
        elif self.colab_attestation is None:
            raise ExecutionBoundaryError(
                "Full training requires a successful Colab runtime attestation."
            )

        self._has_run = True
        self.initialize()
        try:
            return self._execute(
                step_limit,
                optimization_limit,
                episode_limit,
                duration_limit,
            )
        finally:
            self.finalize()

    def _execute(
        self,
        step_limit: int | None,
        optimization_limit: int | None,
        episode_limit: int | None,
        duration_limit: float | None,
    ) -> TrainingResult:
        """Execute the validated episode range and collect in-memory metrics."""
        optimization_rows: list[OptimizationMetrics] = []
        episode_rows: list[EpisodeMetrics] = []
        best_reward = float("-inf")
        best_moving_avg = float("-inf")
        recent_rewards: list[float] = []
        deadline = (
            time.monotonic() + duration_limit if duration_limit is not None else None
        )
        for episode in range(self.start_episode, self.config.episodes + 1):
            if step_limit is not None and self._global_steps >= step_limit:
                break
            if episode_limit is not None and len(episode_rows) >= episode_limit:
                break
            episode_row, losses = self.train_episode(
                episode,
                step_limit,
                optimization_limit,
                deadline,
            )
            episode_rows.append(episode_row)
            mean_loss = sum(losses) / len(losses) if losses else None
            optimization_rows.append(
                OptimizationMetrics(
                    global_step=self._global_steps,
                    episode=episode,
                    optimization_step=self.agent.optimization_steps,
                    loss=mean_loss,
                    mean_predicted_q=episode_row.mean_predicted_q,
                    epsilon=episode_row.epsilon,
                    learning_rate=float(self.agent.optimizer.param_groups[0]["lr"]),
                    replay_size=len(self.replay_buffer),
                )
            )
            self.agent.epsilon_scheduler.step()
            if episode_row.total_reward > best_reward:
                best_reward = episode_row.total_reward
                self.checkpoint("best", episode)

            recent_rewards.append(episode_row.total_reward)
            if len(recent_rewards) > self.config.success_window:
                recent_rewards.pop(0)
            if len(recent_rewards) == self.config.success_window:
                window_avg = sum(recent_rewards) / self.config.success_window
                if window_avg > best_moving_avg:
                    best_moving_avg = window_avg
                    extra: dict[str, object] = {
                        "moving_average_reward": window_avg,
                        "window_size": self.config.success_window,
                        "window_start": episode - self.config.success_window + 1,
                        "window_end": episode,
                    }
                    self.checkpoint("best_moving_average", episode, extra)

            if episode % self.config.checkpoint_interval == 0:
                self.checkpoint("periodic", episode)
            self.logger.info(
                "episode=%d reward=%.6f length=%d success=%d selected=%d "
                "executed=%d failures=%d epsilon=%.6f loss=%s q=%.6f",
                episode,
                episode_row.total_reward,
                episode_row.episode_length,
                episode_row.landing_success,
                episode_row.thruster_actions_selected,
                episode_row.thruster_actions_executed,
                episode_row.thruster_failures,
                episode_row.epsilon,
                "" if mean_loss is None else f"{mean_loss:.6f}",
                episode_row.mean_predicted_q,
            )
        return TrainingResult(
            tuple(optimization_rows),
            tuple(episode_rows),
            self._global_steps,
            self.agent.optimization_steps,
        )

    def train_episode(
        self,
        episode: int,
        global_step_limit: int | None = None,
        optimization_limit: int | None = None,
        deadline: float | None = None,
    ) -> tuple[EpisodeMetrics, tuple[float, ...]]:
        """Execute one episode with configured replay and optimization schedules."""
        started = time.monotonic()
        observation, _ = self.environment.reset(
            seed=self.config.random_seed + episode - 1
        )
        state = np.asarray(observation)
        replaced_before = self.environment.replaced_actions
        total_reward = 0.0
        selected_thrusters = 0
        losses: list[float] = []
        terminated = False
        truncated = False
        final_observation = state

        for episode_step in range(1, self.config.max_steps_per_episode + 1):
            if deadline is not None and time.monotonic() >= deadline:
                raise ExecutionBoundaryError(
                    "Local validation exceeded its wall-clock limit."
                )
            action = self.agent.select_action(state, explore=True)
            if action != 0:
                selected_thrusters += 1
            next_observation, reward, terminated, truncated, _ = self.environment.step(
                action
            )
            self._check_deadline(deadline)
            self._global_steps += 1
            reached_episode_limit = episode_step == self.config.max_steps_per_episode
            reached_global_limit = (
                global_step_limit is not None
                and self._global_steps >= global_step_limit
            )
            if (
                not terminated
                and not truncated
                and (reached_episode_limit or reached_global_limit)
            ):
                truncated = True
            next_state = np.asarray(next_observation)
            self.collect_transition(
                Transition(
                    state,
                    action,
                    float(reward),
                    next_state,
                    terminated,
                    truncated,
                )
            )
            total_reward += float(reward)
            final_observation = next_state
            if self._should_optimize(optimization_limit):
                losses.append(
                    self.agent.learn(self.replay_buffer.sample(self.config.batch_size))
                )
                self._check_deadline(deadline)
            state = next_state
            if terminated or truncated:
                break

        failures = self.environment.replaced_actions - replaced_before
        executed_thrusters = selected_thrusters - failures
        success = is_safe_landing(
            cast(Any, final_observation),
            terminated,
            truncated,
            self.environment_config.landing_tolerance,
        )
        predicted_q = mean_max_predicted_q(self.agent, self.validation_set)
        self._check_deadline(deadline)
        return (
            EpisodeMetrics(
                episode=episode,
                total_reward=total_reward,
                episode_length=episode_step,
                terminated=terminated,
                truncated=truncated,
                landing_success=success,
                thruster_actions_selected=selected_thrusters,
                thruster_actions_executed=executed_thrusters,
                thruster_failures=failures,
                fuel_penalty_total=(
                    selected_thrusters * self.environment_config.fuel_penalty
                ),
                landing_bonus_total=(
                    self.environment_config.landing_bonus if success else 0.0
                ),
                mean_predicted_q=predicted_q,
                epsilon=self.agent.epsilon,
                duration_seconds=time.monotonic() - started,
            ),
            tuple(losses),
        )

    def collect_transition(self, transition: Transition) -> None:
        """Store one immutable transition through the replay public interface."""
        self.replay_buffer.push(transition)

    def checkpoint(
        self,
        kind: str,
        episode: int,
        extra_scheduler_state: dict[str, object] | None = None,
    ) -> None:
        """Request a configured checkpoint from the injected persistence service."""
        if (
            self.execution_context is ExecutionContext.COLAB_FULL
            and self.checkpoint_callback is not None
        ):
            self.checkpoint_callback(
                kind, episode, self._global_steps, extra_scheduler_state
            )

    def finalize(self) -> None:
        """Place the agent in evaluation mode after orchestration ends."""
        self.agent.eval()

    def _should_optimize(self, optimization_limit: int | None) -> bool:
        if (
            optimization_limit is not None
            and self.agent.optimization_steps >= optimization_limit
        ):
            return False
        return (
            len(self.replay_buffer) >= self.config.warmup_steps
            and self._global_steps % self.config.optimization_frequency == 0
        )

    @staticmethod
    def _check_deadline(deadline: float | None) -> None:
        """Fail a local invocation once an operation exceeds its deadline."""
        if deadline is not None and time.monotonic() >= deadline:
            raise ExecutionBoundaryError(
                "Local validation exceeded its wall-clock limit."
            )
