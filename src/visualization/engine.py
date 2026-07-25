"""Deterministic assignment plots from persisted training episode metrics."""

from __future__ import annotations

import csv
import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from src.common import TrainingArtifactValidator
from src.evaluation import require_validated_bundle

from .config import VisualizationConfig


class VisualizationError(RuntimeError):
    """Raised when canonical persisted metrics cannot produce valid figures."""


@dataclass(frozen=True)
class TrainingSeries:
    """Validated episode-level training series for one canonical experiment."""

    experiment_id: str
    run_id: str
    label: str
    episodes: tuple[int, ...]
    rewards: tuple[float, ...]
    mean_predicted_q: tuple[float, ...]
    landing_success: tuple[float, ...]
    executed_thruster_activations: tuple[float, ...]


_CANONICAL = {
    "EXP-001": ("DQN", "original", "DQN Original"),
    "EXP-002": ("DQN", "modified", "DQN Modified"),
    "EXP-003": ("DDQN", "original", "DDQN Original"),
    "EXP-004": ("DDQN", "modified", "DDQN Modified"),
}
_COLORS = ("#1B4965", "#CA6702", "#5F0F40", "#2A9D8F")
_LINE_STYLES = ("-", "--", "-.", ":")


class VisualizationEngine:
    """Load four trusted runs and emit only the four assignment figures."""

    def __init__(
        self,
        config: VisualizationConfig,
        *,
        validator: TrainingArtifactValidator | None = None,
    ) -> None:
        """Store configuration and optional shared-validator injection."""
        self._config = config
        self._validator = validator

    def generate(self, bundles: Sequence[Path]) -> tuple[Path, ...]:
        """Generate all configured formats for the four canonical plots."""
        series = self.load(bundles)
        specs = (
            (
                "episode_reward",
                "Episode Reward versus Training Episode",
                "Episode Reward",
                lambda item: item.rewards,
            ),
            (
                "average_predicted_q",
                "Fixed-Validation Average Predicted Q versus Training Episode",
                "Average Predicted Q",
                lambda item: item.mean_predicted_q,
            ),
            (
                "landing_success_100_episode_moving",
                "100-Episode Moving Successful Landing Rate",
                "Successful Landing Rate",
                lambda item: moving_average(
                    item.landing_success, self._config.moving_window
                ),
            ),
            (
                "average_thruster_activations",
                "Executed Thruster Activations per Training Episode",
                "Executed Thruster Activations",
                lambda item: item.executed_thruster_activations,
            ),
        )
        destinations = tuple(
            self._config.output_root / f"{filename}.{file_format}"
            for filename, _, _, _ in specs
            for file_format in self._config.formats
        )
        existing = [path for path in destinations if path.exists()]
        if existing:
            raise VisualizationError(
                "Figure output already exists and will not be overwritten: "
                f"{existing[0]}"
            )
        self._config.output_root.mkdir(parents=True, exist_ok=True)
        outputs: list[Path] = []
        with plt.rc_context():
            plt.rcParams["font.family"] = "DejaVu Sans"
            plt.rcParams["font.size"] = 10
            plt.rcParams["axes.grid"] = True
            plt.rcParams["grid.alpha"] = 0.25
            plt.rcParams["figure.autolayout"] = True
            plt.rcParams["svg.hashsalt"] = "rl-lunar-lander"
            for filename, title, ylabel, selector in specs:
                figure, axis = plt.subplots(
                    figsize=(self._config.width_inches, self._config.height_inches)
                )
                for index, item in enumerate(series):
                    axis.plot(
                        item.episodes,
                        selector(item),
                        color=_COLORS[index],
                        linestyle=_LINE_STYLES[index],
                        linewidth=1.4,
                        label=item.label,
                    )
                axis.set_title(title)
                axis.set_xlabel("Training Episode")
                axis.set_ylabel(ylabel)
                axis.legend(frameon=False)
                for file_format in self._config.formats:
                    destination = self._config.output_root / f"{filename}.{file_format}"
                    figure.savefig(
                        destination,
                        format=file_format,
                        dpi=self._config.dpi,
                        metadata=_metadata(file_format),
                    )
                    outputs.append(destination)
                plt.close(figure)
        return tuple(outputs)

    def load(self, bundles: Sequence[Path]) -> tuple[TrainingSeries, ...]:
        """Load persisted episode metrics for exactly the canonical four runs."""
        if len(bundles) != len(_CANONICAL):
            raise VisualizationError("Exactly four canonical bundles are required.")
        loaded: dict[str, TrainingSeries] = {}
        for path in bundles:
            trusted = require_validated_bundle(
                path,
                validated_root=self._config.validated_root,
                validation_root=self._config.validation_root,
                validator=self._validator,
            )
            experiment_id = trusted.experiment_id
            if experiment_id not in _CANONICAL or experiment_id in loaded:
                raise VisualizationError(
                    "Canonical experiments must be unique EXP-001-004."
                )
            expected_algorithm, expected_variant, label = _CANONICAL[experiment_id]
            if (
                trusted.manifest.get("algorithm") != expected_algorithm
                or trusted.manifest.get("environment_variant") != expected_variant
            ):
                raise VisualizationError(
                    f"Canonical identity mismatch for {experiment_id}."
                )
            loaded[experiment_id] = _read_series(
                trusted.path / "episode_metrics.csv",
                experiment_id,
                trusted.run_id,
                label,
            )
        return tuple(loaded[key] for key in _CANONICAL)


def moving_average(values: Sequence[float], window: int) -> tuple[float, ...]:
    """Return trailing-window means, using available history before one window."""
    if window <= 0:
        raise ValueError("window must be positive.")
    result: list[float] = []
    running_sum = 0.0
    for index, value in enumerate(values):
        running_sum += value
        if index >= window:
            running_sum -= values[index - window]
        result.append(running_sum / min(index + 1, window))
    return tuple(result)


def _read_series(
    path: Path, experiment_id: str, run_id: str, label: str
) -> TrainingSeries:
    required = {
        "episode",
        "total_reward",
        "landing_success",
        "thruster_actions_executed",
        "mean_predicted_q",
    }
    rows: list[dict[str, str]] = []
    try:
        with path.open("r", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            missing = required - set(reader.fieldnames or ())
            if missing:
                raise VisualizationError(
                    f"{path} is missing columns: {', '.join(sorted(missing))}"
                )
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise VisualizationError(f"Unable to read persisted metrics: {path}") from exc
    if not rows:
        raise VisualizationError(f"Persisted metrics are empty: {path}")
    try:
        episodes = tuple(int(row["episode"]) for row in rows)
        rewards = tuple(float(row["total_reward"]) for row in rows)
        q_values = tuple(float(row["mean_predicted_q"]) for row in rows)
        success = tuple(_boolean(row["landing_success"]) for row in rows)
        activations = tuple(float(row["thruster_actions_executed"]) for row in rows)
    except (TypeError, ValueError) as exc:
        raise VisualizationError(f"Invalid value in persisted metrics: {path}") from exc
    numeric: Iterable[float] = (*rewards, *q_values, *success, *activations)
    if episodes != tuple(sorted(set(episodes))) or episodes[0] < 1:
        raise VisualizationError("Episode identifiers must be unique and increasing.")
    if not all(math.isfinite(value) for value in numeric):
        raise VisualizationError("Persisted plot metrics must be finite.")
    return TrainingSeries(
        experiment_id,
        run_id,
        label,
        episodes,
        rewards,
        q_values,
        success,
        activations,
    )


def _boolean(value: str) -> float:
    normalized = value.strip().lower()
    if normalized in {"true", "1"}:
        return 1.0
    if normalized in {"false", "0"}:
        return 0.0
    raise ValueError("Boolean metric must be true/false or 1/0.")


def _metadata(file_format: str) -> dict[str, Any]:
    if file_format == "pdf":
        return {
            "Creator": "rl-lunar-lander",
            "CreationDate": None,
            "ModDate": None,
        }
    if file_format == "svg":
        return {"Creator": "rl-lunar-lander", "Date": None}
    return {"Software": "rl-lunar-lander"}
