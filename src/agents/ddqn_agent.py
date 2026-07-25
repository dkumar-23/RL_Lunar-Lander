"""Double Deep Q-Network target computation for COMP-002."""

from __future__ import annotations

from typing import cast

import torch

from .base_agent import BaseAgent


class DDQNAgent(BaseAgent):
    """Select next actions online and evaluate them with the target network."""

    def _next_state_values(self, next_states: torch.Tensor) -> torch.Tensor:
        """Return target Q-values gathered at online-network greedy actions."""
        online_q_values = cast(torch.Tensor, self.online_network(next_states))
        target_q_values = cast(torch.Tensor, self.target_network(next_states))
        next_actions = online_q_values.argmax(dim=1, keepdim=True)
        return target_q_values.gather(1, next_actions).squeeze(1)
