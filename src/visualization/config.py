"""Immutable deterministic Matplotlib configuration."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from src.common import resolve_configuration


class VisualizationConfigurationError(ValueError):
    """Raised when figure configuration is invalid."""


@dataclass(frozen=True)
class VisualizationConfig:
    """Configuration for exactly the four assignment figures."""

    validated_root: Path
    validation_root: Path
    output_root: Path
    formats: tuple[str, ...]
    dpi: int
    width_inches: float
    height_inches: float
    moving_window: int

    def __post_init__(self) -> None:
        """Reject unsupported or nondeterministic output settings."""
        if not self.formats or len(set(self.formats)) != len(self.formats):
            raise VisualizationConfigurationError(
                "formats must be unique and non-empty."
            )
        if any(item not in {"png", "pdf", "svg"} for item in self.formats):
            raise VisualizationConfigurationError("formats may contain png, pdf, svg.")
        if self.dpi <= 0 or self.width_inches <= 0 or self.height_inches <= 0:
            raise VisualizationConfigurationError(
                "Figure dimensions and DPI must be positive."
            )
        if self.moving_window != 100:
            raise VisualizationConfigurationError(
                "moving_window must be 100 for the assignment success-rate plot."
            )

    @classmethod
    def from_file(cls, path: Path) -> VisualizationConfig:
        """Load visualization configuration through the shared resolver."""
        return cls.from_mapping(resolve_configuration(path).values)

    @classmethod
    def from_mapping(cls, values: Mapping[str, object]) -> VisualizationConfig:
        """Build validated plotting configuration from a mapping."""
        try:
            formats = values["formats"]
            dpi = values["dpi"]
            width = values["width_inches"]
            height = values["height_inches"]
            moving_window = values["moving_window"]
            roots = (
                values["validated_root"],
                values["validation_root"],
                values["output_root"],
            )
        except KeyError as exc:
            raise VisualizationConfigurationError(
                f"Missing visualization field: {exc.args[0]}"
            ) from exc
        if not isinstance(formats, list) or not all(
            isinstance(item, str) for item in formats
        ):
            raise VisualizationConfigurationError("formats must be a list of strings.")
        if any(not isinstance(item, str) or not item for item in roots):
            raise VisualizationConfigurationError("Output roots must be path strings.")
        if isinstance(dpi, bool) or not isinstance(dpi, int):
            raise VisualizationConfigurationError("dpi must be an integer.")
        if isinstance(moving_window, bool) or not isinstance(moving_window, int):
            raise VisualizationConfigurationError("moving_window must be an integer.")
        if isinstance(width, bool) or not isinstance(width, (int, float)):
            raise VisualizationConfigurationError("width_inches must be numeric.")
        if isinstance(height, bool) or not isinstance(height, (int, float)):
            raise VisualizationConfigurationError("height_inches must be numeric.")
        return cls(
            validated_root=Path(cast(str, roots[0])),
            validation_root=Path(cast(str, roots[1])),
            output_root=Path(cast(str, roots[2])),
            formats=tuple(formats),
            dpi=dpi,
            width_inches=float(width),
            height_inches=float(height),
            moving_window=moving_window,
        )
