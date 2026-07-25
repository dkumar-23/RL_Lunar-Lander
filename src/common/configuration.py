"""Load, validate, and canonically hash repository YAML configuration."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

import yaml


class ConfigurationError(ValueError):
    """Raised when configuration cannot be safely resolved."""


@dataclass(frozen=True)
class ResolvedConfiguration:
    """Immutable validated configuration and canonical SHA-256 identity."""

    values: Mapping[str, Any]
    canonical_json: bytes
    sha256: str


def _json_compatible(value: object, location: str = "configuration") -> Any:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if value != value or value in {float("inf"), float("-inf")}:
            raise ConfigurationError(f"{location} contains a non-finite number.")
        return value
    if isinstance(value, list):
        return [
            _json_compatible(item, f"{location}[{index}]")
            for index, item in enumerate(value)
        ]
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, child in value.items():
            if not isinstance(key, str):
                raise ConfigurationError(f"{location} contains a non-string key.")
            normalized[key] = _json_compatible(child, f"{location}.{key}")
        return normalized
    raise ConfigurationError(
        f"{location} contains unsupported value type {type(value).__name__}."
    )


def resolve_configuration(path: Path) -> ResolvedConfiguration:
    """Safely load a YAML mapping and compute its canonical identity.

    Args:
        path: YAML configuration file.

    Returns:
        Immutable values, canonical JSON bytes, and SHA-256 hash.

    Raises:
        ConfigurationError: The file is missing, malformed, or unsupported.
    """
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigurationError(f"Configuration file not found: {path}") from exc
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ConfigurationError(f"Unable to read configuration: {path}") from exc
    if not isinstance(raw, dict):
        raise ConfigurationError("Configuration root must be a mapping.")

    values = _json_compatible(raw)
    canonical = json.dumps(
        values,
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return ResolvedConfiguration(
        values=MappingProxyType(values),
        canonical_json=canonical,
        sha256=hashlib.sha256(canonical).hexdigest(),
    )


def configuration_sha256(path: Path) -> str:
    """Return the canonical SHA-256 identity of one YAML configuration."""
    return resolve_configuration(path).sha256
