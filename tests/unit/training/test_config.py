"""Tests for canonical shared training configuration."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.training import (
    Algorithm,
    EnvironmentVariant,
    load_experiment_config,
    validate_registered_configuration,
)


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
    assert [
        validate_registered_configuration(item, repository) for item in experiments
    ] == [
        "da315e68d3d21324fc4775715f4faa3c84d859e2ab49bb9973092fe8b0bfd490",
        "1494b939bf5b707eb5fedf77dadcfbb19206df69bd9b1f8b995c9ab97801bb67",
        "6de2b51eac37f458f214d78aee8f5050997a27c7acc10a4fe1e6edaeb04c69a0",
        "5770d945e9d0c7ecd32f97db930ebd605a393eee3998d464beba1e13276743fb",
    ]


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
