"""Tests for strict persisted-evidence report asset generation."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from src.common import file_sha256
from src.reporting import ReportingEngine, ReportingError, ReportInputs
from tests.unit.evaluation.fixtures import BundleFixture, create_validated_bundle


def _inputs(
    tmp_path: Path,
    learning_rates: tuple[float, ...] = (0.001, 0.001, 0.001, 0.001),
) -> tuple[ReportInputs, list[BundleFixture]]:
    definitions = (
        ("EXP-001", "DQN", "original"),
        ("EXP-002", "DQN", "modified"),
        ("EXP-003", "DDQN", "original"),
        ("EXP-004", "DDQN", "modified"),
    )
    fixtures = [
        create_validated_bundle(
            tmp_path,
            experiment,
            algorithm,
            variant,
            learning_rate,
        )
        for (experiment, algorithm, variant), learning_rate in zip(
            definitions, learning_rates, strict=True
        )
    ]
    evaluation_root = tmp_path / "evaluation"
    for fixture, (_, algorithm, variant) in zip(fixtures, definitions, strict=True):
        destination = evaluation_root / fixture.bundle.parent.name / "RUN-001"
        destination.mkdir(parents=True)
        manifest_hash = file_sha256(fixture.bundle / "manifest.json")
        summary = {
            "experiment_id": fixture.bundle.parent.name,
            "run_id": "RUN-001",
            "algorithm": algorithm,
            "environment_variant": variant,
            "episode_count": 2,
            "reward_mean": 1.5,
            "reward_median": 1.5,
            "reward_minimum": 1.0,
            "reward_maximum": 2.0,
            "reward_variance": 0.25,
            "reward_standard_deviation": 0.5,
            "success_rate": 0.5,
            "episode_length_mean": 3.0,
            "q_mean": 0.75,
            "source_manifest_sha256": manifest_hash,
            "checkpoint": "best",
            "parameters_unchanged": True,
        }
        (destination / "evaluation_summary.json").write_text(
            json.dumps(summary), encoding="utf-8"
        )
        with (destination / "evaluation_metrics.csv").open(
            "w", encoding="utf-8", newline=""
        ) as stream:
            writer = csv.writer(stream)
            writer.writerow(
                (
                    "experiment_id",
                    "run_id",
                    "source_manifest_sha256",
                    "episode",
                    "total_reward",
                    "episode_length",
                    "landing_success",
                    "mean_selected_q",
                )
            )
            writer.writerow(
                (
                    fixture.bundle.parent.name,
                    "RUN-001",
                    manifest_hash,
                    1,
                    1.0,
                    3,
                    True,
                    0.5,
                )
            )
            writer.writerow(
                (
                    fixture.bundle.parent.name,
                    "RUN-001",
                    manifest_hash,
                    2,
                    2.0,
                    3,
                    False,
                    1.0,
                )
            )
    plot_root = tmp_path / "plots"
    plot_root.mkdir()
    for stem in (
        "episode_reward",
        "average_predicted_q",
        "landing_success_100_episode_moving",
        "average_thruster_activations",
    ):
        (plot_root / f"{stem}.png").write_bytes(b"synthetic plot")
    return (
        ReportInputs(
            tuple(item.bundle for item in fixtures),
            fixtures[0].validated_root,
            fixtures[0].validation_root,
            evaluation_root,
            plot_root,
            tmp_path / "report",
        ),
        fixtures,
    )


def test_reporting_generates_tables_and_hash_aware_asset_manifest(
    tmp_path: Path,
) -> None:
    """Only complete persisted evidence is transcribed into report assets."""
    inputs, fixtures = _inputs(tmp_path)

    outputs = ReportingEngine(inputs, validator=fixtures[0].validator).generate()

    assert [path.name for path in outputs] == [
        "experiment_table.csv",
        "hyperparameter_table.csv",
        "evaluation_table.csv",
        "asset_manifest.json",
    ]
    manifest = json.loads(outputs[-1].read_text(encoding="utf-8"))
    assert manifest["complete"] is True
    assert len(manifest["canonical_experiments"]) == 4
    assert all(len(item["sha256"]) == 64 for item in manifest["assets"])
    assert all(not Path(item["path"]).is_absolute() for item in manifest["assets"])
    with outputs[1].open(encoding="utf-8", newline="") as stream:
        hyperparameters = list(csv.DictReader(stream))
    assert len(hyperparameters) == 4
    assert {row["learning_rate"] for row in hyperparameters} == {"0.001"}


def test_reporting_refuses_to_claim_completion_when_plot_is_absent(
    tmp_path: Path,
) -> None:
    """Missing evidence aborts before any report table is generated."""
    inputs, fixtures = _inputs(tmp_path)
    (inputs.plot_root / "episode_reward.png").unlink()

    with pytest.raises(ReportingError, match="Missing assignment plot"):
        ReportingEngine(inputs, validator=fixtures[0].validator).generate()

    assert not inputs.output_root.exists()


def test_reporting_rejects_unmatched_training_controls(tmp_path: Path) -> None:
    inputs, fixtures = _inputs(
        tmp_path,
        learning_rates=(0.001, 0.001, 0.001, 0.002),
    )

    with pytest.raises(ReportingError, match="identical training controls"):
        ReportingEngine(inputs, validator=fixtures[0].validator).generate()

    assert not inputs.output_root.exists()


def test_reporting_refuses_to_overwrite_existing_assets(tmp_path: Path) -> None:
    inputs, fixtures = _inputs(tmp_path)
    inputs.output_root.mkdir(parents=True)
    marker = inputs.output_root / "existing.txt"
    marker.write_text("preserve\n", encoding="utf-8")

    with pytest.raises(ReportingError, match="will not be overwritten"):
        ReportingEngine(inputs, validator=fixtures[0].validator).generate()

    assert marker.read_text(encoding="utf-8") == "preserve\n"
