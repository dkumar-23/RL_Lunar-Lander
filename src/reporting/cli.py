"""Command-line interface for strict persisted-evidence report assets."""

from __future__ import annotations

import argparse
from pathlib import Path

from .engine import ReportingEngine, ReportInputs


def parse_args() -> argparse.Namespace:
    """Parse explicit evidence locations without scanning arbitrary outputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundles", type=Path, nargs=4)
    parser.add_argument(
        "--validated-root", type=Path, default=Path("outputs/colab/validated")
    )
    parser.add_argument(
        "--validation-root", type=Path, default=Path("outputs/colab/validation")
    )
    parser.add_argument(
        "--evaluation-root", type=Path, default=Path("outputs/evaluation")
    )
    parser.add_argument("--plot-root", type=Path, default=Path("outputs/plots"))
    parser.add_argument("--output", type=Path, default=Path("outputs/reports"))
    return parser.parse_args()


def main() -> int:
    """Generate complete report tables and print their paths."""
    args = parse_args()
    outputs = ReportingEngine(
        ReportInputs(
            bundles=tuple(args.bundles),
            validated_root=args.validated_root,
            validation_root=args.validation_root,
            evaluation_root=args.evaluation_root,
            plot_root=args.plot_root,
            output_root=args.output,
        )
    ).generate()
    for path in outputs:
        print(path)
    return 0
