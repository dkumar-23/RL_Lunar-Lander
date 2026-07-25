"""Tests for centralized random seed management."""

from __future__ import annotations

import random

import numpy as np
import pytest
import torch

from src.common.seed import initialize_seed


def test_identical_seed_reproduces_all_cpu_random_sources() -> None:
    first_generator = initialize_seed(17, deterministic=True)
    first = (
        random.random(),
        float(np.random.random()),
        float(first_generator.random()),
        float(torch.rand(1).item()),
    )

    second_generator = initialize_seed(17, deterministic=True)
    second = (
        random.random(),
        float(np.random.random()),
        float(second_generator.random()),
        float(torch.rand(1).item()),
    )

    assert first == second
    assert torch.are_deterministic_algorithms_enabled()
    assert torch.backends.cudnn.deterministic
    assert not torch.backends.cudnn.benchmark


def test_invalid_seed_is_rejected() -> None:
    with pytest.raises(ValueError, match="seed"):
        initialize_seed(-1, deterministic=True)
    with pytest.raises(TypeError, match="seed"):
        initialize_seed(True, deterministic=True)
