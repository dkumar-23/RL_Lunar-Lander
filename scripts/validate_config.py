"""Validate and identify one repository YAML configuration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.common.configuration import ConfigurationError, resolve_configuration
from src.training.config import (
    load_experiment_config,
    validate_registered_configuration,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument(
        "--resolved-json",
        type=Path,
        help="Optional canonical resolved JSON output path",
    )
    parser.add_argument(
        "--check-hash",
        action="store_true",
        help="Validate resolved experiment hash against canonical_hashes.json",
    )
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root for relative path resolution",
    )
    return parser.parse_args()


def validate_single_config(config: Path) -> int:
    """Validate a single YAML configuration file."""
    try:
        resolved = resolve_configuration(config)
    except ConfigurationError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}))
        return 1
    print(json.dumps({"valid": True, "sha256": resolved.sha256}, sort_keys=True))
    return 0


def validate_experiment_hash(config: Path, repository_root: Path) -> int:
    """Load an experiment config, compute resolved hash, verify canonical."""
    try:
        experiment = load_experiment_config(config, repository_root)
    except (ValueError, ConfigurationError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}))
        return 1
    try:
        observed_hash = validate_registered_configuration(experiment, repository_root)
    except ValueError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}))
        return 1
    print(
        json.dumps(
            {
                "valid": True,
                "experiment_id": experiment.experiment_id,
                "algorithm": experiment.algorithm.value,
                "environment_variant": experiment.environment_variant.value,
                "resolved_configuration_sha256": observed_hash,
            },
            sort_keys=True,
        )
    )
    return 0


def main() -> int:
    """Validate the requested configuration."""
    args = parse_args()
    if args.check_hash:
        return validate_experiment_hash(args.config, args.repository_root)
    return validate_single_config(args.config)


if __name__ == "__main__":
    raise SystemExit(main())
