"""Enforce the CON-011 local and Google Colab execution boundary."""

from __future__ import annotations

import importlib.util
import re
import subprocess
from enum import Enum
from pathlib import Path


class ExecutionBoundaryError(RuntimeError):
    """Raised when execution would violate CON-011."""


class ExecutionContext(str, Enum):
    """Supported training execution contexts."""

    LOCAL_TEST = "local-test"
    COLAB_FULL = "colab-full"


_COMMIT_PATTERN = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
_MAX_LOCAL_SMOKE_STEPS = 32
_MAX_LOCAL_OPTIMIZATION_STEPS = 1


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
) -> None:
    """Fail unless full training is running in an approved Colab checkout.

    Args:
        repository: Detached, clean repository worktree used for training.
        expected_commit: Exact approved Git object identifier.
        drive_root: Mounted Google Drive destination for persistent artifacts.

    Raises:
        ExecutionBoundaryError: The runtime, source, or storage is not approved.
    """
    if not _is_google_colab():
        raise ExecutionBoundaryError(
            "Full training is permitted only in a Google Colab runtime."
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


def validate_local_test_limits(max_steps: int, optimization_steps: int) -> None:
    """Validate non-promotable local smoke and learning-step limits.

    Args:
        max_steps: Maximum environment transitions requested.
        optimization_steps: Number of optimizer updates requested.

    Raises:
        ExecutionBoundaryError: A local validation exceeds its hard limit.
    """
    if not 1 <= max_steps <= _MAX_LOCAL_SMOKE_STEPS:
        raise ExecutionBoundaryError(
            f"Local smoke tests permit 1-{_MAX_LOCAL_SMOKE_STEPS} steps."
        )
    if not 0 <= optimization_steps <= _MAX_LOCAL_OPTIMIZATION_STEPS:
        raise ExecutionBoundaryError(
            "Local validation permits at most one optimizer update."
        )
