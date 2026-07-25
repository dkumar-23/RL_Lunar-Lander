"""Validate and identify one repository YAML configuration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.common.configuration import ConfigurationError, resolve_configuration


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument(
        "--resolved-json",
        type=Path,
        help="Optional canonical resolved JSON output path",
    )
    return parser.parse_args()


def main() -> int:
    """Validate the requested configuration."""
    args = parse_args()
    try:
        resolved = resolve_configuration(args.config)
    except ConfigurationError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}))
        return 1

    if args.resolved_json is not None:
        args.resolved_json.parent.mkdir(parents=True, exist_ok=True)
        args.resolved_json.write_bytes(resolved.canonical_json + b"\n")
    print(json.dumps({"valid": True, "sha256": resolved.sha256}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
