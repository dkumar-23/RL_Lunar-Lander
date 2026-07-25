"""Tests for atomic and restrictive checkpoint serialization."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
import torch

from src.common.checkpoint import CheckpointError, load_checkpoint, save_checkpoint
from src.common.metadata import RunMetadata


class _UnsafeObject:
    pass


def _metadata() -> RunMetadata:
    return RunMetadata(
        experiment_id="EXP-001",
        run_id="RUN-001",
        episode=3,
        global_step=100,
        configuration_hash="a" * 64,
        seed=42,
        git_sha="b" * 40,
    )


def test_checkpoint_round_trip_preserves_all_supplied_state(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "checkpoint.pt"
    save_checkpoint(
        path,
        model_state={"weight": torch.tensor([1.0])},
        target_state={"weight": torch.tensor([2.0])},
        optimizer_state={"state": {}, "param_groups": [{"lr": 0.001}]},
        scheduler_state={"last_epoch": 7},
        metadata=_metadata(),
    )

    loaded = load_checkpoint(path, map_location="cpu")

    assert torch.equal(loaded.model_state["weight"], torch.tensor([1.0]))
    assert torch.equal(loaded.target_state["weight"], torch.tensor([2.0]))
    assert loaded.optimizer_state["param_groups"][0]["lr"] == 0.001
    assert loaded.scheduler_state == {"last_epoch": 7}
    assert loaded.metadata == _metadata()


def test_failed_save_does_not_replace_existing_checkpoint(tmp_path: Path) -> None:
    path = tmp_path / "checkpoint.pt"
    path.write_bytes(b"valid existing bytes")

    with patch("src.common.checkpoint.torch.save", side_effect=RuntimeError("boom")):
        with pytest.raises(CheckpointError, match="save"):
            save_checkpoint(
                path,
                model_state={},
                target_state={},
                optimizer_state={},
                scheduler_state=None,
                metadata=_metadata(),
            )

    assert path.read_bytes() == b"valid existing bytes"
    assert not tuple(tmp_path.glob("*.tmp"))


def test_restrictive_load_rejects_pickled_custom_objects(tmp_path: Path) -> None:
    path = tmp_path / "unsafe.pt"
    torch.save(_UnsafeObject(), path)

    with pytest.raises(CheckpointError, match="load"):
        load_checkpoint(path, map_location="cpu")
