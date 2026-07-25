"""Tests for canonical shared training configuration."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.training import Algorithm, EnvironmentVariant, load_experiment_config


def test_all_canonical_experiments_share_training_controls() -> None:
    """Only algorithm and environment variant may differ in the matrix."""
    repository = Path.cwd()
    experiments = [
        load_experiment_config(
            repository / "experiments" / f"exp{index:03d}" / "config.yaml",
            repository,
        )
        for index in range(1, 5)
    ]

    assert all(item.training == experiments[0].training for item in experiments)
    assert [(item.algorithm, item.environment_variant) for item in experiments] == [
        (Algorithm.DQN, EnvironmentVariant.ORIGINAL),
        (Algorithm.DQN, EnvironmentVariant.MODIFIED),
        (Algorithm.DDQN, EnvironmentVariant.ORIGINAL),
        (Algorithm.DDQN, EnvironmentVariant.MODIFIED),
    ]
    assert experiments[0].environment.action_failure_probability == 0.0
    assert experiments[1].environment.action_failure_probability == 0.15


def test_definition_cannot_claim_another_canonical_identity(tmp_path: Path) -> None:
    """Reject an algorithm/variant tuple inconsistent with its EXP identifier."""
    definition = tmp_path / "invalid.yaml"
    definition.write_text(
        "\n".join(
            (
                "experiment_id: EXP-001",
                "algorithm: DDQN",
                "environment_variant: original",
                "training_config: configs/training.yaml",
                "environment_config: configs/environment.yaml",
            )
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="canonical matrix"):
        load_experiment_config(definition, Path.cwd())
