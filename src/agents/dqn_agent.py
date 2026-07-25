"""Deep Q-Network target computation for COMP-002."""

from __future__ import annotations

from typing import cast

import torch

from .base_agent import BaseAgent


class DQNAgent(BaseAgent):
    """Use the target network maximum for DQN Bellman targets."""

    def _next_state_values(self, next_states: torch.Tensor) -> torch.Tensor:
        """Return maximum target-network Q-values for each next state."""
        target_q_values = cast(torch.Tensor, self.target_network(next_states))
        return target_q_values.max(dim=1).values
