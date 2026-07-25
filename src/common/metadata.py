"""Immutable, secret-free software and run metadata."""

from __future__ import annotations

import platform
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from importlib import metadata as importlib_metadata
from types import MappingProxyType

_EXPERIMENT_PATTERN = re.compile(r"EXP-[0-9]{3}")
_RUN_PATTERN = re.compile(r"RUN-[0-9]{3}")
_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
_GIT_SHA_PATTERN = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
_MAX_NUMPY_SEED = 2**32 - 1


class MetadataError(ValueError):
    """Raised when metadata cannot be captured or validated."""


@dataclass(frozen=True)
class SoftwareMetadata:
    """Immutable software identity without environment variables or user data."""

    python_version: str
    python_implementation: str
    platform_system: str
    platform_release: str
    platform_machine: str
    package_versions: Mapping[str, str]

    def __post_init__(self) -> None:
        """Copy package versions into an immutable, deterministic mapping."""
        values = {
            "python_version": self.python_version,
            "python_implementation": self.python_implementation,
            "platform_system": self.platform_system,
            "platform_release": self.platform_release,
            "platform_machine": self.platform_machine,
        }
        if any(not isinstance(value, str) or not value for value in values.values()):
            raise MetadataError("Software metadata fields must not be empty.")
        packages = dict(self.package_versions)
        if any(
            not isinstance(name, str)
            or not name
            or not isinstance(version, str)
            or not version
            for name, version in packages.items()
        ):
            raise MetadataError("Package names and versions must be non-empty strings.")
        object.__setattr__(
            self,
            "package_versions",
            MappingProxyType(dict(sorted(packages.items()))),
        )

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable copy of the metadata."""
        return {
            "python_version": self.python_version,
            "python_implementation": self.python_implementation,
            "platform_system": self.platform_system,
            "platform_release": self.platform_release,
            "platform_machine": self.platform_machine,
            "package_versions": dict(self.package_versions),
        }


@dataclass(frozen=True)
class RunMetadata:
    """Immutable identity and progress metadata for one checkpointed run."""

    experiment_id: str
    run_id: str
    episode: int
    global_step: int
    configuration_hash: str
    seed: int
    git_sha: str

    def __post_init__(self) -> None:
        """Validate identities and counters at the metadata boundary."""
        if not all(
            isinstance(value, str)
            for value in (
                self.experiment_id,
                self.run_id,
                self.configuration_hash,
                self.git_sha,
            )
        ):
            raise MetadataError("Run identity fields must be strings.")
        if _EXPERIMENT_PATTERN.fullmatch(self.experiment_id) is None:
            raise MetadataError("experiment_id must match EXP-NNN.")
        if _RUN_PATTERN.fullmatch(self.run_id) is None:
            raise MetadataError("run_id must match RUN-NNN.")
        _validate_counter(self.episode, "episode")
        _validate_counter(self.global_step, "global_step")
        if _SHA256_PATTERN.fullmatch(self.configuration_hash) is None:
            raise MetadataError("configuration_hash must be a lowercase SHA-256.")
        if (
            isinstance(self.seed, bool)
            or not isinstance(self.seed, int)
            or not 0 <= self.seed <= _MAX_NUMPY_SEED
        ):
            raise MetadataError(f"seed must be in [0, {_MAX_NUMPY_SEED}].")
        if _GIT_SHA_PATTERN.fullmatch(self.git_sha) is None:
            raise MetadataError("git_sha must be a lowercase 40- or 64-digit SHA.")

    def to_dict(self) -> dict[str, str | int]:
        """Return a serialization-safe metadata dictionary."""
        return {
            "experiment_id": self.experiment_id,
            "run_id": self.run_id,
            "episode": self.episode,
            "global_step": self.global_step,
            "configuration_hash": self.configuration_hash,
            "seed": self.seed,
            "git_sha": self.git_sha,
        }

    @classmethod
    def from_mapping(cls, values: Mapping[str, object]) -> RunMetadata:
        """Validate and construct metadata from a loaded checkpoint mapping."""
        expected = {
            "experiment_id",
            "run_id",
            "episode",
            "global_step",
            "configuration_hash",
            "seed",
            "git_sha",
        }
        if set(values) != expected:
            raise MetadataError(
                "Run metadata fields do not match the checkpoint schema."
            )
        experiment_id = values["experiment_id"]
        run_id = values["run_id"]
        configuration_hash = values["configuration_hash"]
        git_sha = values["git_sha"]
        if (
            not isinstance(experiment_id, str)
            or not isinstance(run_id, str)
            or not isinstance(configuration_hash, str)
            or not isinstance(git_sha, str)
        ):
            raise MetadataError("Run metadata identity fields must be strings.")
        episode = values["episode"]
        global_step = values["global_step"]
        seed = values["seed"]
        if (
            isinstance(episode, bool)
            or not isinstance(episode, int)
            or isinstance(global_step, bool)
            or not isinstance(global_step, int)
            or isinstance(seed, bool)
            or not isinstance(seed, int)
        ):
            raise MetadataError("Run metadata counters and seed must be integers.")
        return cls(
            experiment_id=experiment_id,
            run_id=run_id,
            episode=episode,
            global_step=global_step,
            configuration_hash=configuration_hash,
            seed=seed,
            git_sha=git_sha,
        )


def capture_software_metadata(packages: Iterable[str]) -> SoftwareMetadata:
    """Capture versions for explicitly requested packages and safe runtime fields.

    Environment variables, command-line arguments, host names, user names, and
    arbitrary process state are deliberately excluded.

    Args:
        packages: Distribution names whose installed versions must be recorded.

    Returns:
        Frozen software metadata with package names sorted deterministically.

    Raises:
        MetadataError: A name is invalid or a package is not installed.
    """
    if isinstance(packages, (str, bytes)):
        raise MetadataError("packages must be an iterable of distribution names.")
    names = tuple(packages)
    if any(not isinstance(name, str) or not name for name in names):
        raise MetadataError("Package names must be non-empty strings.")
    try:
        versions = {
            name: importlib_metadata.version(name) for name in sorted(set(names))
        }
    except importlib_metadata.PackageNotFoundError as exc:
        raise MetadataError(f"Package is not installed: {exc.name}") from exc

    return SoftwareMetadata(
        python_version=platform.python_version(),
        python_implementation=platform.python_implementation(),
        platform_system=platform.system(),
        platform_release=platform.release(),
        platform_machine=platform.machine(),
        package_versions=versions,
    )


def _validate_counter(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise MetadataError(f"{name} must be a non-negative integer.")
