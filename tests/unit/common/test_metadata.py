"""Tests for immutable software and run metadata."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from src.common.metadata import RunMetadata, capture_software_metadata


def test_software_metadata_is_immutable_and_excludes_process_secrets() -> None:
    metadata = capture_software_metadata(["torch", "numpy"])
    serialized = metadata.to_dict()

    assert tuple(metadata.package_versions) == ("numpy", "torch")
    assert "environment" not in serialized
    assert "username" not in serialized
    with pytest.raises(TypeError):
        metadata.package_versions["other"] = "1"  # type: ignore[index]
    with pytest.raises(FrozenInstanceError):
        metadata.python_version = "changed"  # type: ignore[misc]


def test_run_metadata_round_trip_is_validated_and_immutable() -> None:
    metadata = RunMetadata(
        experiment_id="EXP-001",
        run_id="RUN-001",
        episode=12,
        global_step=345,
        configuration_hash="a" * 64,
        seed=42,
        git_sha="b" * 40,
    )

    assert RunMetadata.from_mapping(metadata.to_dict()) == metadata
    with pytest.raises(FrozenInstanceError):
        metadata.episode = 13  # type: ignore[misc]
