"""Validate and optionally promote one imported Colab training bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.common.artifacts import TrainingArtifactValidator


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, help="Imported immutable bundle")
    parser.add_argument(
        "--report",
        required=True,
        type=Path,
        help="Validation report destination outside the imported bundle",
    )
    parser.add_argument(
        "--promote-to",
        type=Path,
        help="Optional new destination used only when validation passes",
    )
    return parser.parse_args()


def main() -> int:
    """Validate the requested bundle and return a process exit status."""
    args = parse_args()
    validator = TrainingArtifactValidator()
    report = validator.validate(args.bundle)
    validator.write_report(report, args.report)
    if report.valid and args.promote_to is not None:
        validator.promote(report, args.promote_to)
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0 if report.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
