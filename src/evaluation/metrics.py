"""Raw evaluation records and deterministic descriptive statistics."""

from __future__ import annotations

import math
import statistics
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from typing import Any


class MetricsError(ValueError):
    """Raised when evaluation observations cannot form valid statistics."""


@dataclass(frozen=True)
class EpisodeMetrics:
    """One immutable raw evaluation episode observation."""

    episode: int
    total_reward: float
    episode_length: int
    landing_success: bool
    mean_selected_q: float

    def to_dict(self) -> dict[str, int | float | bool]:
        """Return one CSV/JSON-safe raw episode record."""
        return asdict(self)


def aggregate_metrics(episodes: Sequence[EpisodeMetrics]) -> dict[str, Any]:
    """Compute required population statistics without replacing raw episodes."""
    if not episodes:
        raise MetricsError("At least one evaluation episode is required.")
    rewards = [item.total_reward for item in episodes]
    lengths = [float(item.episode_length) for item in episodes]
    q_values = [item.mean_selected_q for item in episodes]
    if not all(math.isfinite(value) for value in (*rewards, *lengths, *q_values)):
        raise MetricsError("Evaluation metrics must be finite.")
    summary: dict[str, Any] = {
        "episode_count": len(episodes),
        "success_rate": statistics.fmean(
            float(item.landing_success) for item in episodes
        ),
        "variance_definition": "population",
    }
    for prefix, values in (
        ("reward", rewards),
        ("episode_length", lengths),
        ("q", q_values),
    ):
        summary.update(_statistics(prefix, values))
    return summary


def _statistics(prefix: str, values: Sequence[float]) -> dict[str, float]:
    variance = statistics.pvariance(values)
    return {
        f"{prefix}_mean": statistics.fmean(values),
        f"{prefix}_median": statistics.median(values),
        f"{prefix}_minimum": min(values),
        f"{prefix}_maximum": max(values),
        f"{prefix}_variance": variance,
        f"{prefix}_standard_deviation": math.sqrt(variance),
    }
