"""Atomic, restrictive PyTorch checkpoint serialization."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import torch

from .metadata import RunMetadata

_CHECKPOINT_FIELDS = {
    "model_state",
    "target_state",
    "optimizer_state",
    "scheduler_state",
    "metadata",
}


class CheckpointError(RuntimeError):
    """Raised when a checkpoint cannot be saved or loaded safely."""


@dataclass(frozen=True)
class LoadedCheckpoint:
    """Validated state loaded from one restrictive checkpoint payload."""

    model_state: Mapping[str, Any]
    target_state: Mapping[str, Any]
    optimizer_state: Mapping[str, Any]
    scheduler_state: Mapping[str, Any] | None
    metadata: RunMetadata


def save_checkpoint(
    path: Path,
    *,
    model_state: Mapping[str, Any],
    target_state: Mapping[str, Any],
    optimizer_state: Mapping[str, Any],
    scheduler_state: Mapping[str, Any] | None,
    metadata: RunMetadata,
) -> None:
    """Atomically save supplied model, target, optimizer, and scheduler state.

    Args:
        path: Final checkpoint path.
        model_state: Online model state mapping supplied by the caller.
        target_state: Target model state mapping supplied by the caller.
        optimizer_state: Optimizer state mapping supplied by the caller.
        scheduler_state: Scheduler-like state mapping, or explicit ``None``.
        metadata: Validated run identity and progress metadata.

    Raises:
        CheckpointError: Serialization or atomic replacement fails.
        TypeError: A path, state mapping, or metadata value has the wrong type.

    Side Effects:
        Creates parent directories. A failure never replaces an existing valid
        checkpoint and removes its temporary file when possible.
    """
    if not isinstance(path, Path):
        raise TypeError("path must be a pathlib.Path.")
    states = {
        "model_state": model_state,
        "target_state": target_state,
        "optimizer_state": optimizer_state,
    }
    if any(not isinstance(state, Mapping) for state in states.values()):
        raise TypeError("model, target, and optimizer state must be mappings.")
    if scheduler_state is not None and not isinstance(scheduler_state, Mapping):
        raise TypeError("scheduler_state must be a mapping or None.")
    if not isinstance(metadata, RunMetadata):
        raise TypeError("metadata must be RunMetadata.")

    payload = {
        **states,
        "scheduler_state": scheduler_state,
        "metadata": metadata.to_dict(),
    }
    temporary_path: Path | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
        torch.save(payload, temporary_path)
        with temporary_path.open("rb") as stream:
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
    except Exception as exc:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise CheckpointError(f"Unable to save checkpoint: {path}") from exc


def load_checkpoint(
    path: Path,
    *,
    map_location: str | torch.device,
) -> LoadedCheckpoint:
    """Restrictively load and validate one checkpoint without applying state.

    Args:
        path: Existing checkpoint path.
        map_location: Explicit PyTorch destination for loaded tensors.

    Returns:
        Validated state mappings and immutable run metadata.

    Raises:
        CheckpointError: Restrictive deserialization or schema validation fails.
        TypeError: ``path`` or ``map_location`` has an unsupported type.
    """
    if not isinstance(path, Path):
        raise TypeError("path must be a pathlib.Path.")
    if not isinstance(map_location, (str, torch.device)):
        raise TypeError("map_location must be a string or torch.device.")
    try:
        loaded: object = torch.load(
            path,
            map_location=map_location,
            weights_only=True,
        )
        if not isinstance(loaded, Mapping) or set(loaded) != _CHECKPOINT_FIELDS:
            raise CheckpointError("Checkpoint fields do not match the schema.")
        model_state = _state_mapping(loaded, "model_state")
        target_state = _state_mapping(loaded, "target_state")
        optimizer_state = _state_mapping(loaded, "optimizer_state")
        raw_scheduler = loaded["scheduler_state"]
        if raw_scheduler is not None and not isinstance(raw_scheduler, Mapping):
            raise CheckpointError("scheduler_state must be a mapping or None.")
        raw_metadata = loaded["metadata"]
        if not isinstance(raw_metadata, Mapping):
            raise CheckpointError("metadata must be a mapping.")
        metadata = RunMetadata.from_mapping(raw_metadata)
    except CheckpointError:
        raise
    except Exception as exc:
        raise CheckpointError(f"Unable to load checkpoint: {path}") from exc

    return LoadedCheckpoint(
        model_state=model_state,
        target_state=target_state,
        optimizer_state=optimizer_state,
        scheduler_state=cast(Mapping[str, Any] | None, raw_scheduler),
        metadata=metadata,
    )


def _state_mapping(checkpoint: Mapping[object, object], name: str) -> Mapping[str, Any]:
    value = checkpoint[name]
    if not isinstance(value, Mapping):
        raise CheckpointError(f"{name} must be a mapping.")
    return cast(Mapping[str, Any], value)
