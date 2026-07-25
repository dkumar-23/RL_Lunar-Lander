"""Configurable PyTorch action-value network owned by COMP-004."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import cast

import torch
from torch import nn

type ActivationFactory = Callable[[], nn.Module]


class QNetwork(nn.Module):
    """Map observations to one Q-value per discrete action.

    The caller supplies every architectural choice. PyTorch's active random
    state controls linear-layer initialization, allowing the repository's seed
    infrastructure to govern reproducibility without hidden generators.

    Args:
        input_dim: Number of features in one observation.
        output_dim: Number of discrete-action Q-values.
        hidden_sizes: Width of each hidden layer. An empty sequence creates a
            linear action-value model.
        activation_factory: Factory creating a fresh activation for each hidden
            layer.

    Raises:
        ValueError: A layer dimension is not a positive integer.
        TypeError: The activation factory does not return an ``nn.Module``.
    """

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        hidden_sizes: Sequence[int],
        activation_factory: ActivationFactory,
    ) -> None:
        super().__init__()
        self.input_dim = self._validate_dimension(input_dim, "input_dim")
        self.output_dim = self._validate_dimension(output_dim, "output_dim")
        self.hidden_sizes = tuple(
            self._validate_dimension(size, f"hidden_sizes[{index}]")
            for index, size in enumerate(hidden_sizes)
        )

        dimensions = (self.input_dim, *self.hidden_sizes, self.output_dim)
        layers: list[nn.Module] = []
        for index, (in_features, out_features) in enumerate(
            zip(dimensions, dimensions[1:], strict=False)
        ):
            layers.append(nn.Linear(in_features, out_features))
            if index < len(dimensions) - 2:
                activation = activation_factory()
                if not isinstance(activation, nn.Module):
                    raise TypeError("activation_factory must return an nn.Module.")
                layers.append(activation)
        self.network = nn.Sequential(*layers)

    @staticmethod
    def _validate_dimension(value: int, name: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} must be a positive integer.")
        return value

    def forward(self, observations: torch.Tensor) -> torch.Tensor:
        """Compute Q-values without modifying model or input state.

        Args:
            observations: Tensor whose final dimension equals ``input_dim``.

        Returns:
            Tensor with the same leading dimensions and ``output_dim`` as its
            final dimension.

        Raises:
            ValueError: The input has no feature dimension or has the wrong
                feature width.
        """
        if observations.ndim == 0 or observations.shape[-1] != self.input_dim:
            raise ValueError(
                f"Expected observations with final dimension {self.input_dim}."
            )
        return cast(torch.Tensor, self.network(observations))
