"""Tests for the unchanged fixed validation-state contract."""

from __future__ import annotations

import numpy as np
import pytest

from src.training import FixedValidationSet


def test_fixed_validation_states_are_seeded_and_read_only() -> None:
    """The canonical seed reproduces identical immutable state bytes."""
    first = FixedValidationSet.create(256, 8, 4242)
    second = FixedValidationSet.create(256, 8, 4242)

    assert first.states.shape == (256, 8)
    assert first.states.flags.writeable is False
    assert first.sha256 == second.sha256
    np.testing.assert_array_equal(first.states, second.states)


@pytest.mark.parametrize(("count", "input_dim"), [(0, 8), (2, 0), (True, 8)])
def test_fixed_validation_states_reject_invalid_dimensions(
    count: int, input_dim: int
) -> None:
    with pytest.raises(ValueError, match="positive integers"):
        FixedValidationSet.create(count, input_dim, 4242)
