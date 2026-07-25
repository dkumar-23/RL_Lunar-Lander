"""Centralized random seeding and deterministic PyTorch configuration."""

from __future__ import annotations

import random

import numpy as np
import torch

_MAX_NUMPY_SEED = 2**32 - 1


def initialize_seed(seed: int, *, deterministic: bool) -> np.random.Generator:
    """Seed Python, NumPy, and PyTorch and return an isolated NumPy generator.

    Args:
        seed: Non-negative seed supported by NumPy's legacy global generator.
        deterministic: Whether PyTorch must reject nondeterministic algorithms.

    Returns:
        A NumPy ``Generator`` initialized with the same seed for dependency
        injection into components that avoid global random state.

    Raises:
        ValueError: ``seed`` is outside NumPy's supported unsigned 32-bit range.
        TypeError: ``seed`` is not an integer or ``deterministic`` is not a bool.
    """
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise TypeError("seed must be an integer.")
    if not 0 <= seed <= _MAX_NUMPY_SEED:
        raise ValueError(f"seed must be in [0, {_MAX_NUMPY_SEED}].")
    if not isinstance(deterministic, bool):
        raise TypeError("deterministic must be a bool.")

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(deterministic)
    torch.backends.cudnn.deterministic = deterministic
    if deterministic:
        torch.backends.cudnn.benchmark = False

    return np.random.default_rng(seed)
