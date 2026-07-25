"""Immutable replay transition data owned by COMP-003."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

type Observation = npt.NDArray[np.generic]


@dataclass(frozen=True, slots=True, eq=False)
class Transition:
    """One immutable Gymnasium transition.

    Observation arrays are defensively copied and made read-only so mutation of
    caller-owned arrays cannot alter replay history. ``terminated`` and
    ``truncated`` remain separate to preserve Gymnasium bootstrapping semantics.

    Args:
        state: Observation before the action.
        action: Selected discrete action.
        reward: Scalar reward received from the environment.
        next_state: Observation after the action.
        terminated: Whether an MDP terminal state was reached.
        truncated: Whether an external episode limit ended the episode.
    """

    state: Observation
    action: int
    reward: float
    next_state: Observation
    terminated: bool
    truncated: bool

    def __post_init__(self) -> None:
        state = np.array(self.state, copy=True)
        next_state = np.array(self.next_state, copy=True)
        state.flags.writeable = False
        next_state.flags.writeable = False
        object.__setattr__(self, "state", state)
        object.__setattr__(self, "next_state", next_state)
