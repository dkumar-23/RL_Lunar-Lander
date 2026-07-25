"""Tests for raw evaluation metric aggregation."""

from __future__ import annotations

import pytest

from src.evaluation import EpisodeMetrics, MetricsError, aggregate_metrics


def test_aggregate_metrics_preserves_required_population_statistics() -> None:
    """Reward, length, success, and Q summaries use all raw episodes."""
    episodes = [
        EpisodeMetrics(1, 1.0, 2, True, 3.0),
        EpisodeMetrics(2, 3.0, 4, False, 5.0),
    ]

    summary = aggregate_metrics(episodes)

    assert summary["reward_mean"] == 2.0
    assert summary["reward_median"] == 2.0
    assert summary["reward_minimum"] == 1.0
    assert summary["reward_maximum"] == 3.0
    assert summary["reward_variance"] == 1.0
    assert summary["reward_standard_deviation"] == 1.0
    assert summary["success_rate"] == 0.5
    assert summary["episode_length_mean"] == 3.0
    assert summary["q_mean"] == 4.0


def test_aggregate_metrics_rejects_missing_raw_episodes() -> None:
    """An empty result cannot become a misleading report statistic."""
    with pytest.raises(MetricsError):
        aggregate_metrics([])
