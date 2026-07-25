"""Fixed-capacity deterministic replay buffer owned by COMP-003."""

from __future__ import annotations

from collections import deque

import numpy as np

from .transition import Transition


class ReplayBuffer:
    """Store transitions with O(1) insertion and FIFO eviction.

    Args:
        capacity: Maximum number of retained transitions.
        rng: Externally initialized NumPy generator used for all sampling.

    Raises:
        ValueError: ``capacity`` is not a positive integer.
        TypeError: ``rng`` is not a NumPy ``Generator``.
    """

    def __init__(self, capacity: int, rng: np.random.Generator) -> None:
        if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity <= 0:
            raise ValueError("capacity must be a positive integer.")
        if not isinstance(rng, np.random.Generator):
            raise TypeError("rng must be a numpy.random.Generator.")
        self._capacity = capacity
        self._rng = rng
        self._transitions: deque[Transition] = deque(maxlen=capacity)

    def push(self, transition: Transition) -> None:
        """Append one transition, evicting the oldest at capacity.

        Args:
            transition: Immutable transition to retain.

        Raises:
            TypeError: ``transition`` is not a ``Transition``.
        """
        if not isinstance(transition, Transition):
            raise TypeError("transition must be a Transition.")
        self._transitions.append(transition)

    def sample(self, batch_size: int) -> tuple[Transition, ...]:
        """Sample transitions without replacement or reordering storage.

        Args:
            batch_size: Number of distinct transitions to return.

        Returns:
            A tuple in the deterministic order emitted by the injected RNG.

        Raises:
            ValueError: The batch size is invalid or exceeds current occupancy.
        """
        if (
            isinstance(batch_size, bool)
            or not isinstance(batch_size, int)
            or batch_size <= 0
        ):
            raise ValueError("batch_size must be a positive integer.")
        if batch_size > len(self._transitions):
            raise ValueError("batch_size cannot exceed replay buffer size.")

        stored = tuple(self._transitions)
        indices = self._rng.choice(len(stored), size=batch_size, replace=False)
        return tuple(stored[int(index)] for index in indices)

    def clear(self) -> None:
        """Remove every retained transition without changing RNG state."""
        self._transitions.clear()

    def size(self) -> int:
        """Return the current number of retained transitions."""
        return len(self._transitions)

    def capacity(self) -> int:
        """Return the configured maximum occupancy."""
        return self._capacity

    def __len__(self) -> int:
        """Return the current number of retained transitions."""
        return self.size()
