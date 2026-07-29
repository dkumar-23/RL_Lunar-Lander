"""Tests for canonical persisted-metric plotting."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pytest

from src.common import file_sha256
from src.visualization import (
    VisualizationConfig,
    VisualizationEngine,
    VisualizationError,
    moving_average,
)
from tests.unit.evaluation.fixtures import BundleFixture, create_validated_bundle


def test_moving_average_uses_previous_hundred_available_episodes() -> None:
    """The fixed success window uses trailing observations only."""
    values = (1.0,) * 100 + (0.0,)

    result = moving_average(values, 100)

    assert result[0] == 1.0
    assert result[99] == 1.0
    assert result[100] == 0.99


def _fixtures(tmp_path: Path) -> list[BundleFixture]:
    definitions = (
        ("EXP-001", "DQN", "original"),
        ("EXP-002", "DQN", "modified"),
        ("EXP-003", "DDQN", "original"),
        ("EXP-004", "DDQN", "modified"),
    )
    return [
        create_validated_bundle(tmp_path, experiment, algorithm, variant)
        for experiment, algorithm, variant in definitions
    ]


def _config(
    fixtures: Sequence[BundleFixture],
    output: Path,
    formats: tuple[str, ...] = ("png",),
) -> VisualizationConfig:
    return VisualizationConfig(
        fixtures[0].validated_root,
        fixtures[0].validation_root,
        output,
        formats=formats,
        dpi=72,
        width_inches=4.0,
        height_inches=3.0,
        moving_window=100,
    )


def test_generate_emits_exactly_four_deterministic_assignment_plots(
    tmp_path: Path,
) -> None:
    """Canonical bundles produce no optional or training-time figures."""
    fixtures = _fixtures(tmp_path)
    first_engine = VisualizationEngine(
        _config(fixtures, tmp_path / "plots-first"), validator=fixtures[0].validator
    )
    second_engine = VisualizationEngine(
        _config(fixtures, tmp_path / "plots-second"), validator=fixtures[0].validator
    )

    first = first_engine.generate([item.bundle for item in fixtures])
    first_hashes = [file_sha256(path) for path in first]
    second = second_engine.generate([item.bundle for item in reversed(fixtures)])

    assert len(first) == 5
    assert {path.stem for path in first} == {
        "episode_reward",
        "average_predicted_q",
        "landing_success_100_episode_moving",
        "average_thruster_activations",
        "average_thruster_activations_selected_vs_executed",
    }
    assert [file_sha256(path) for path in second] == first_hashes


def test_load_includes_both_selected_and_executed_thruster_activations(
    tmp_path: Path,
) -> None:
    fixtures = _fixtures(tmp_path)
    engine = VisualizationEngine(
        _config(fixtures, tmp_path / "plots"), validator=fixtures[0].validator
    )

    series = engine.load([item.bundle for item in fixtures])

    assert series[0].selected_thruster_activations == (3.0, 2.0)
    assert series[0].executed_thruster_activations == (2.0, 2.0)


def test_generate_refuses_to_overwrite_existing_figures(tmp_path: Path) -> None:
    fixtures = _fixtures(tmp_path)
    engine = VisualizationEngine(
        _config(fixtures, tmp_path / "plots"), validator=fixtures[0].validator
    )
    engine.generate([item.bundle for item in fixtures])

    with pytest.raises(VisualizationError, match="will not be overwritten"):
        engine.generate([item.bundle for item in fixtures])


def test_generate_exports_png_pdf_and_svg(tmp_path: Path) -> None:
    fixtures = _fixtures(tmp_path)
    engine = VisualizationEngine(
        _config(
            fixtures,
            tmp_path / "plots",
            formats=("png", "pdf", "svg"),
        ),
        validator=fixtures[0].validator,
    )

    outputs = engine.generate([item.bundle for item in fixtures])

    assert len(outputs) == 15
    assert {path.suffix for path in outputs} == {".png", ".pdf", ".svg"}
    assert all(path.stat().st_size > 0 for path in outputs)
