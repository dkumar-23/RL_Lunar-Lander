"""Configurable neural-network models for value approximation."""

from .q_network import ActivationFactory, QNetwork

__all__ = ["ActivationFactory", "QNetwork"]
