"""Unit tests for the configurable Q-network."""

from __future__ import annotations

import unittest
from typing import cast

import torch
from torch import nn

from src.models import ActivationFactory, QNetwork


class QNetworkTests(unittest.TestCase):
    """Verify configured architecture, shape, and seeded initialization."""

    def test_forward_uses_configured_dimensions(self) -> None:
        network = QNetwork(3, 2, (5, 4), nn.ReLU)

        output = network(torch.ones((7, 3)))

        self.assertEqual(output.shape, (7, 2))
        linear_layers = [
            layer for layer in network.network if isinstance(layer, nn.Linear)
        ]
        self.assertEqual(
            [(layer.in_features, layer.out_features) for layer in linear_layers],
            [(3, 5), (5, 4), (4, 2)],
        )

    def test_forward_preserves_leading_dimensions(self) -> None:
        network = QNetwork(3, 2, (), nn.ReLU)

        single_output = network(torch.ones(3))
        batched_output = network(torch.ones((2, 4, 3)))

        self.assertEqual(single_output.shape, (2,))
        self.assertEqual(batched_output.shape, (2, 4, 2))
        self.assertEqual(len(network.network), 1)

    def test_forward_rejects_missing_or_wrong_feature_dimension(self) -> None:
        network = QNetwork(3, 2, (4,), nn.ReLU)

        with self.assertRaisesRegex(ValueError, "final dimension 3"):
            network(torch.tensor(1.0))
        with self.assertRaisesRegex(ValueError, "final dimension 3"):
            network(torch.ones((2, 4)))

    def test_activation_factory_must_return_module(self) -> None:
        with self.assertRaisesRegex(TypeError, "must return an nn.Module"):
            QNetwork(3, 2, (4,), cast(ActivationFactory, lambda: object()))

    def test_initialization_respects_external_torch_seed(self) -> None:
        torch.manual_seed(17)
        first = QNetwork(2, 2, (3,), nn.Tanh)
        torch.manual_seed(17)
        second = QNetwork(2, 2, (3,), nn.Tanh)

        for first_parameter, second_parameter in zip(
            first.parameters(), second.parameters(), strict=True
        ):
            torch.testing.assert_close(first_parameter, second_parameter)

    def test_state_dict_round_trip_preserves_outputs(self) -> None:
        source = QNetwork(2, 3, (4,), nn.ReLU)
        restored = QNetwork(2, 3, (4,), nn.ReLU)
        restored.load_state_dict(source.state_dict())
        observations = torch.tensor([[1.0, -1.0]])

        torch.testing.assert_close(restored(observations), source(observations))

    def test_invalid_dimension_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            QNetwork(0, 2, (3,), nn.ReLU)
        with self.assertRaises(ValueError):
            QNetwork(2, True, (3,), nn.ReLU)


if __name__ == "__main__":
    unittest.main()
