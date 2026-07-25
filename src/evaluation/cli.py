"""Command-line entrypoint for local validated-bundle evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import EvaluationConfig
from .engine import EvaluationEngine


def parse_args() -> argparse.Namespace:
    """Parse evaluation arguments without accessing a checkpoint."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, help="Promoted EXP-NNN/RUN-NNN bundle")
    parser.add_argument("--config", type=Path, default=Path("configs/evaluation.yaml"))
    return parser.parse_args()


def main() -> int:
    """Evaluate one trusted bundle and print its persisted summary."""
    args = parse_args()
    _, summary = EvaluationEngine(EvaluationConfig.from_file(args.config)).evaluate(
        args.bundle
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0
