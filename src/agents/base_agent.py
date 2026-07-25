"""Shared DQN/DDQN action selection and optimization owned by COMP-002."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

import numpy as np
import torch
from torch import nn
from torch.optim import Optimizer

from src.memory import Observation, Transition

from .epsilon_scheduler import EpsilonScheduler


class BaseAgent(ABC):
    """Own common epsilon-greedy, learning, and target-sync behavior.

    Args:
        online_network: Trainable action-value network.
        target_network: Independently allocated target action-value network.
        optimizer: Optimizer configured for ``online_network`` parameters.
        loss_function: Configured scalar temporal-difference loss.
        epsilon_scheduler: Exploration schedule used during action selection.
        action_count: Number of valid discrete actions.
        discount_factor: Bellman discount in ``[0, 1]``.
        target_sync_interval: Optimizer-step interval for hard target copies.
        rng: Externally initialized NumPy generator for exploration.
        device: Device on which network inference and learning execute.

    Raises:
        ValueError: A scalar configuration value is invalid or both network
            arguments reference the same object.
        TypeError: ``rng`` is not a NumPy ``Generator``.
    """

    def __init__(
        self,
        online_network: nn.Module,
        target_network: nn.Module,
        optimizer: Optimizer,
        loss_function: nn.Module,
        epsilon_scheduler: EpsilonScheduler,
        action_count: int,
        discount_factor: float,
        target_sync_interval: int,
        rng: np.random.Generator,
        device: torch.device | str,
    ) -> None:
        if online_network is target_network:
            raise ValueError("online_network and target_network must be distinct.")
        if (
            isinstance(action_count, bool)
            or not isinstance(action_count, int)
            or action_count <= 0
        ):
            raise ValueError("action_count must be a positive integer.")
        if not np.isfinite(discount_factor) or not 0.0 <= discount_factor <= 1.0:
            raise ValueError("discount_factor must be finite and in [0, 1].")
        if (
            isinstance(target_sync_interval, bool)
            or not isinstance(target_sync_interval, int)
            or target_sync_interval <= 0
        ):
            raise ValueError("target_sync_interval must be a positive integer.")
        if not isinstance(rng, np.random.Generator):
            raise TypeError("rng must be a numpy.random.Generator.")

        self.device = torch.device(device)
        self.online_network = online_network.to(self.device)
        self.target_network = target_network.to(self.device)
        self.optimizer = optimizer
        self.loss_function = loss_function
        self.epsilon_scheduler = epsilon_scheduler
        self.action_count = action_count
        self.discount_factor = discount_factor
        self.target_sync_interval = target_sync_interval
        self._rng = rng
        self._optimization_steps = 0

        self.target_network.requires_grad_(False)
        self.update_target()

    @property
    def epsilon(self) -> float:
        """Return the current exploration probability."""
        return self.epsilon_scheduler.value

    @property
    def optimization_steps(self) -> int:
        """Return the number of completed optimizer steps."""
        return self._optimization_steps

    def select_action(self, observation: Observation, explore: bool) -> int:
        """Select one action using the configured epsilon-greedy policy.

        Args:
            observation: One unbatched environment observation.
            explore: Whether epsilon exploration is permitted.

        Returns:
            A valid discrete action index.

        Raises:
            ValueError: The observation is not one-dimensional or the network
                output does not match ``action_count``.
        """
        if explore and self._rng.random() < self.epsilon:
            return int(self._rng.integers(self.action_count))

        observation_tensor = torch.as_tensor(
            observation, dtype=torch.float32, device=self.device
        )
        if observation_tensor.ndim != 1:
            raise ValueError("select_action expects one unbatched observation.")
        with torch.no_grad():
            q_values = self.online_network(observation_tensor.unsqueeze(0))
        if q_values.shape != (1, self.action_count):
            raise ValueError(
                "online_network must return one Q-value per configured action."
            )
        return int(q_values.argmax(dim=1).item())

    def learn(self, transitions: Sequence[Transition]) -> float:
        """Perform exactly one optimizer step from one transition mini-batch.

        Truncated transitions retain bootstrapping because only a true MDP
        termination removes the next-state value.

        Args:
            transitions: Non-empty mini-batch of immutable transitions.

        Returns:
            Scalar loss value before the optimizer update.

        Raises:
            ValueError: The batch is empty, contains invalid actions, or the
                configured loss does not return a scalar.
        """
        if not transitions:
            raise ValueError("transitions must contain at least one item.")
        if any(
            transition.action < 0 or transition.action >= self.action_count
            for transition in transitions
        ):
            raise ValueError("transition action is outside the configured range.")

        states = torch.as_tensor(
            np.stack([transition.state for transition in transitions]),
            dtype=torch.float32,
            device=self.device,
        )
        actions = torch.tensor(
            [transition.action for transition in transitions],
            dtype=torch.long,
            device=self.device,
        )
        rewards = torch.tensor(
            [transition.reward for transition in transitions],
            dtype=torch.float32,
            device=self.device,
        )
        next_states = torch.as_tensor(
            np.stack([transition.next_state for transition in transitions]),
            dtype=torch.float32,
            device=self.device,
        )
        terminated = torch.tensor(
            [transition.terminated for transition in transitions],
            dtype=torch.bool,
            device=self.device,
        )

        self.online_network.train()
        self.target_network.eval()
        predicted_q = (
            self.online_network(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        )
        targets = self._compute_targets(rewards, next_states, terminated)
        loss = self.loss_function(predicted_q, targets)
        if loss.ndim != 0:
            raise ValueError("loss_function must return a scalar tensor.")

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        self._optimization_steps += 1
        if self._optimization_steps % self.target_sync_interval == 0:
            self.update_target()
        return float(loss.detach().item())

    def _compute_targets(
        self,
        rewards: torch.Tensor,
        next_states: torch.Tensor,
        terminated: torch.Tensor,
    ) -> torch.Tensor:
        """Compute detached Bellman targets for fixed-tensor verification."""
        with torch.no_grad():
            next_q_values = self._next_state_values(next_states)
            bootstrap_mask = (~terminated).to(dtype=rewards.dtype)
            return rewards + self.discount_factor * bootstrap_mask * next_q_values

    @abstractmethod
    def _next_state_values(self, next_states: torch.Tensor) -> torch.Tensor:
        """Return one algorithm-specific target value per next state."""

    def update_target(self) -> None:
        """Hard-copy online parameters and buffers into the target network."""
        self.target_network.load_state_dict(self.online_network.state_dict())
        self.target_network.eval()

    def train(self) -> None:
        """Place the online network in training mode."""
        self.online_network.train()
        self.target_network.eval()

    def eval(self) -> None:
        """Place both networks in evaluation mode without changing weights."""
        self.online_network.eval()
        self.target_network.eval()
