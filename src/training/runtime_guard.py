"""Enforce the CON-011 local and Google Colab execution boundary."""

from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import torch


class ExecutionBoundaryError(RuntimeError):
    """Raised when execution would violate CON-011."""


class ExecutionContext(StrEnum):
    """Supported training execution contexts."""

    LOCAL_TEST = "local-test"
    COLAB_FULL = "colab-full"


@dataclass(frozen=True)
class ColabTrainingAttestation:
    """Opaque evidence that CON-011 runtime checks passed for one checkout."""

    repository: Path
    git_commit: str
    drive_root: Path


_COMMIT_PATTERN = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
_MAX_LOCAL_SMOKE_STEPS = 32
_MAX_LOCAL_OPTIMIZATION_STEPS = 1
_MAX_LOCAL_EPISODES = 1
_MAX_LOCAL_DURATION_SECONDS = 60.0


def _is_google_colab() -> bool:
    try:
        return importlib.util.find_spec("google.colab") is not None
    except ModuleNotFoundError:
        return False


def _git_output(repository: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def attest_colab_full_training(
    repository: Path,
    expected_commit: str,
    drive_root: Path,
    minimum_free_drive_bytes: int,
) -> ColabTrainingAttestation:
    """Fail unless full training is running in an approved Colab checkout.

    Args:
        repository: Detached, clean repository worktree used for training.
        expected_commit: Exact approved Git object identifier.
        drive_root: Mounted Google Drive destination for persistent artifacts.
        minimum_free_drive_bytes: Required free capacity before training starts.

    Returns:
        Immutable evidence required by the shared engine's full-training path.

    Raises:
        ExecutionBoundaryError: The runtime, source, or storage is not approved.
    """
    if not _is_google_colab():
        raise ExecutionBoundaryError(
            "Full training is permitted only in a Google Colab runtime."
        )
    if not torch.cuda.is_available() or torch.cuda.device_count() < 1:
        raise ExecutionBoundaryError(
            "Full training requires a visible CUDA GPU in Google Colab."
        )
    if (
        isinstance(minimum_free_drive_bytes, bool)
        or not isinstance(minimum_free_drive_bytes, int)
        or minimum_free_drive_bytes <= 0
    ):
        raise ExecutionBoundaryError(
            "minimum_free_drive_bytes must be a positive integer."
        )
    if _COMMIT_PATTERN.fullmatch(expected_commit) is None:
        raise ExecutionBoundaryError("An exact 40- or 64-character commit is required.")

    repository = repository.resolve()
    if not repository.is_dir():
        raise ExecutionBoundaryError(f"Repository does not exist: {repository}")

    try:
        resolved_commit = _git_output(repository, "rev-parse", "HEAD")
        worktree_status = _git_output(repository, "status", "--porcelain")
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ExecutionBoundaryError("Unable to attest the Git checkout.") from exc

    if resolved_commit != expected_commit:
        raise ExecutionBoundaryError(
            f"Checked-out commit {resolved_commit} does not match {expected_commit}."
        )
    if worktree_status:
        raise ExecutionBoundaryError("Full training requires a clean Git worktree.")

    drive_root = drive_root.resolve()
    drive_mount = Path("/content/drive")
    if drive_mount not in (drive_root, *drive_root.parents):
        raise ExecutionBoundaryError("Artifacts must persist beneath /content/drive.")
    if not drive_root.is_dir():
        raise ExecutionBoundaryError(f"Google Drive root does not exist: {drive_root}")
    probe: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=drive_root,
            prefix=".rl_lunar_lander_write_probe.",
            delete=False,
        ) as stream:
            probe = Path(stream.name)
            stream.write(b"preflight")
    except OSError as exc:
        raise ExecutionBoundaryError("Google Drive root is not writable.") from exc
    finally:
        if probe is not None:
            probe.unlink(missing_ok=True)
    if shutil.disk_usage(drive_root).free < minimum_free_drive_bytes:
        raise ExecutionBoundaryError("Google Drive has insufficient free space.")
    return ColabTrainingAttestation(repository, expected_commit, drive_root)


def validate_local_test_limits(
    max_steps: int,
    optimization_steps: int,
    max_episodes: int = _MAX_LOCAL_EPISODES,
    max_duration_seconds: float = _MAX_LOCAL_DURATION_SECONDS,
) -> None:
    """Validate non-promotable local smoke and learning-step limits.

    Args:
        max_steps: Maximum environment transitions requested.
        optimization_steps: Number of optimizer updates requested.
        max_episodes: Maximum episodes requested.
        max_duration_seconds: Maximum wall-clock duration requested.

    Raises:
        ExecutionBoundaryError: A local validation exceeds its hard limit.
    """
    if (
        isinstance(max_steps, bool)
        or not isinstance(max_steps, int)
        or not 1 <= max_steps <= _MAX_LOCAL_SMOKE_STEPS
    ):
        raise ExecutionBoundaryError(
            f"Local smoke tests permit 1-{_MAX_LOCAL_SMOKE_STEPS} steps."
        )
    if (
        isinstance(optimization_steps, bool)
        or not isinstance(optimization_steps, int)
        or not 0 <= optimization_steps <= _MAX_LOCAL_OPTIMIZATION_STEPS
    ):
        raise ExecutionBoundaryError(
            "Local validation permits at most one optimizer update."
        )
    if (
        isinstance(max_episodes, bool)
        or not isinstance(max_episodes, int)
        or not 1 <= max_episodes <= _MAX_LOCAL_EPISODES
    ):
        raise ExecutionBoundaryError("Local validation permits exactly one episode.")
    if (
        isinstance(max_duration_seconds, bool)
        or not isinstance(max_duration_seconds, (int, float))
        or not 0.0 < max_duration_seconds <= _MAX_LOCAL_DURATION_SECONDS
    ):
        raise ExecutionBoundaryError(
            "Local validation permits at most 60 seconds of execution."
        )
