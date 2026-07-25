"""Command-line interface for canonical persisted-metric figures."""

from __future__ import annotations

import argparse
from pathlib import Path

from .config import VisualizationConfig
from .engine import VisualizationEngine


def parse_args() -> argparse.Namespace:
    """Parse four promoted bundle paths and visualization configuration."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundles", type=Path, nargs=4)
    parser.add_argument(
        "--config", type=Path, default=Path("configs/visualization.yaml")
    )
    return parser.parse_args()


def main() -> int:
    """Generate and list deterministic assignment plot assets."""
    args = parse_args()
    outputs = VisualizationEngine(VisualizationConfig.from_file(args.config)).generate(
        args.bundles
    )
    for path in outputs:
        print(path)
    return 0
