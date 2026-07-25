"""Construct shared training dependencies from validated configuration."""

from __future__ import annotations

import numpy as np
import torch
from gymnasium import spaces
from torch import nn

from src.agents import BaseAgent, DDQNAgent, DQNAgent, EpsilonScheduler
from src.memory import ReplayBuffer
from src.models import QNetwork

from .config import Algorithm, TrainingConfig


def environment_dimensions(environment: object) -> tuple[int, int]:
    """Return flat observation width and discrete action count for training."""
    observation_space = getattr(environment, "observation_space", None)
    action_space = getattr(environment, "action_space", None)
    if (
        not isinstance(observation_space, spaces.Box)
        or len(observation_space.shape) != 1
    ):
        raise ValueError("Training requires a one-dimensional Box observation space.")
    if not isinstance(action_space, spaces.Discrete):
        raise ValueError("Training requires a Discrete action space.")
    return int(observation_space.shape[0]), int(action_space.n)


def resolve_device(requested: str) -> torch.device:
    """Resolve a configured device while failing when explicit CUDA is absent."""
    if requested == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if requested == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was explicitly configured but is unavailable.")
    return torch.device(requested)


def create_agent(
    config: TrainingConfig,
    algorithm: Algorithm,
    input_dim: int,
    action_count: int,
    rng: np.random.Generator,
    *,
    device: torch.device | str | None = None,
) -> BaseAgent:
    """Create a DQN or DDQN agent with otherwise identical dependencies.

    Args:
        config: Shared canonical training controls.
        algorithm: The sole algorithm-specific construction choice.
        input_dim: Number of scalar observation features.
        action_count: Number of discrete environment actions.
        rng: Centrally initialized generator used for exploration.
        device: Optional bounded-validation device override.

    Returns:
        A configured agent whose online and target networks are independent.
    """
    selected_device = resolve_device(config.device if device is None else str(device))
    online_network = QNetwork(input_dim, action_count, config.hidden_sizes, nn.ReLU)
    target_network = QNetwork(input_dim, action_count, config.hidden_sizes, nn.ReLU)
    optimizer = torch.optim.Adam(online_network.parameters(), lr=config.learning_rate)
    loss_function: nn.Module
    if config.loss_function == "mse":
        loss_function = nn.MSELoss()
    else:
        loss_function = nn.SmoothL1Loss()
    scheduler = EpsilonScheduler(
        config.epsilon_initial,
        config.epsilon_final,
        config.epsilon_decay,
    )
    agent_type = DQNAgent if algorithm is Algorithm.DQN else DDQNAgent
    return agent_type(
        online_network=online_network,
        target_network=target_network,
        optimizer=optimizer,
        loss_function=loss_function,
        epsilon_scheduler=scheduler,
        action_count=action_count,
        discount_factor=config.discount_factor,
        target_sync_interval=config.target_sync_interval,
        rng=rng,
        device=selected_device,
    )


def create_replay_buffer(
    config: TrainingConfig, rng: np.random.Generator
) -> ReplayBuffer:
    """Create the shared deterministic replay implementation."""
    return ReplayBuffer(config.replay_capacity, rng)
