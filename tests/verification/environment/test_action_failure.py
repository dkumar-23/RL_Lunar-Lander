"""Statistical and reseeding verification for stochastic action failure."""

from __future__ import annotations

from src.environment import ModifiedLunarLander
from tests.unit.environment.fakes import FakeLanderEnv
from tests.unit.environment.test_wrapper import make_config


def test_replacement_rate_matches_bernoulli_probability() -> None:
    """A large deterministic sample should closely match probability 0.15."""
    sample_size = 20_000
    wrapper = ModifiedLunarLander(FakeLanderEnv(), make_config(seed=2026))

    for _ in range(sample_size):
        wrapper.step(1)

    replacement_rate = wrapper.replaced_actions / wrapper.thruster_actions_selected
    assert abs(replacement_rate - 0.15) < 0.01


def test_reset_with_same_seed_reproduces_replacement_sequence() -> None:
    """Explicitly reseeding reset must restart the private Bernoulli sequence."""
    base = FakeLanderEnv()
    wrapper = ModifiedLunarLander(base, make_config(seed=99))

    wrapper.reset(seed=31415)
    for _ in range(200):
        wrapper.step(3)
    first_sequence = list(base.executed_actions)

    base.executed_actions.clear()
    wrapper.reset(seed=31415)
    for _ in range(200):
        wrapper.step(3)

    assert base.executed_actions == first_sequence


def test_private_rng_is_independent_of_global_numpy_state() -> None:
    """Unrelated NumPy use must not perturb wrapper replacement decisions."""
    import numpy as np

    first_base = FakeLanderEnv()
    second_base = FakeLanderEnv()
    first = ModifiedLunarLander(first_base, make_config(seed=77))
    second = ModifiedLunarLander(second_base, make_config(seed=77))

    for _ in range(100):
        first.step(2)
        np.random.random(25)
        second.step(2)

    assert first_base.executed_actions == second_base.executed_actions
