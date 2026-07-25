"""Tests for Colab training artifact validation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from src.common import (
    RunMetadata,
    TrainingArtifactValidator,
    artifact_set_sha256,
    file_sha256,
    load_checkpoint,
    save_checkpoint,
)
from tests.unit.evaluation.fixtures import create_validated_bundle


def _rehash_bundle(bundle: Path) -> None:
    manifest_path = bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifacts = manifest["artifacts"]
    for entry in artifacts:
        path = bundle / entry["path"]
        entry["size_bytes"] = path.stat().st_size
        entry["sha256"] = file_sha256(path)
    manifest["artifact_set_sha256"] = artifact_set_sha256(artifacts)
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    paths = [entry["path"] for entry in artifacts] + ["manifest.json"]
    (bundle / "integrity.sha256").write_text(
        "".join(
            f"{file_sha256(bundle / relative)}  {relative}\n" for relative in paths
        ),
        encoding="ascii",
    )
    marker_path = bundle / "status" / "COMPLETED.json"
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    marker["manifest_sha256"] = file_sha256(manifest_path)
    marker_path.write_text(json.dumps(marker), encoding="utf-8")


def test_complete_bundle_is_valid(tmp_path: Path) -> None:
    fixture = create_validated_bundle(tmp_path)

    report = fixture.validator.validate(fixture.bundle)

    assert report.valid, report.issues
    assert report.artifacts_checked == 8
    assert report.checkpoints_checked == 2


def test_modified_payload_is_rejected(tmp_path: Path) -> None:
    fixture = create_validated_bundle(tmp_path)
    (fixture.bundle / "training.log").write_text("tampered\n", encoding="utf-8")

    report = fixture.validator.validate(fixture.bundle)

    assert not report.valid
    assert "artifact.hash_mismatch" in {issue.code for issue in report.issues}


def test_checkpoint_identity_mismatch_is_rejected(tmp_path: Path) -> None:
    fixture = create_validated_bundle(tmp_path)
    checkpoint_path = fixture.bundle / "checkpoints" / "best_checkpoint.pt"
    checkpoint = load_checkpoint(checkpoint_path, map_location="cpu")
    save_checkpoint(
        checkpoint_path,
        model_state=checkpoint.model_state,
        target_state=checkpoint.target_state,
        optimizer_state=checkpoint.optimizer_state,
        scheduler_state=checkpoint.scheduler_state,
        metadata=RunMetadata(
            experiment_id="EXP-001",
            run_id="RUN-001",
            episode=2,
            global_step=2,
            configuration_hash=checkpoint.metadata.configuration_hash,
            seed=99,
            git_sha=checkpoint.metadata.git_sha,
        ),
    )
    _rehash_bundle(fixture.bundle)

    report = fixture.validator.validate(fixture.bundle)

    assert not report.valid
    assert any("random_seed" in issue.message for issue in report.issues)


def test_checkpoint_optimizer_mismatch_is_rejected(tmp_path: Path) -> None:
    fixture = create_validated_bundle(tmp_path)
    checkpoint_path = fixture.bundle / "checkpoints" / "best_checkpoint.pt"
    checkpoint = load_checkpoint(checkpoint_path, map_location="cpu")
    save_checkpoint(
        checkpoint_path,
        model_state=checkpoint.model_state,
        target_state=checkpoint.target_state,
        optimizer_state={"unexpected": True},
        scheduler_state=checkpoint.scheduler_state,
        metadata=checkpoint.metadata,
    )
    _rehash_bundle(fixture.bundle)

    report = fixture.validator.validate(fixture.bundle)

    assert not report.valid
    assert any("optimizer" in issue.message for issue in report.issues)


def test_unregistered_configuration_is_rejected(tmp_path: Path) -> None:
    fixture = create_validated_bundle(tmp_path)
    validator = TrainingArtifactValidator(canonical_hashes={"EXP-001": "0" * 64})

    report = validator.validate(fixture.bundle)

    assert not report.valid
    assert "configuration.canonical_hash" in {issue.code for issue in report.issues}


def test_incomplete_episode_history_is_rejected(tmp_path: Path) -> None:
    fixture = create_validated_bundle(tmp_path)
    metrics_path = fixture.bundle / "metrics.csv"
    episode_metrics_path = fixture.bundle / "episode_metrics.csv"
    metrics_path.write_text(
        "\n".join(metrics_path.read_text(encoding="utf-8").splitlines()[:2]) + "\n",
        encoding="utf-8",
    )
    episode_metrics_path.write_text(
        "\n".join(episode_metrics_path.read_text(encoding="utf-8").splitlines()[:2])
        + "\n",
        encoding="utf-8",
    )
    _rehash_bundle(fixture.bundle)

    report = fixture.validator.validate(fixture.bundle)

    assert not report.valid
    assert "progress.episodes" in {issue.code for issue in report.issues}


def test_hash_uses_exact_bytes(tmp_path: Path) -> None:
    path = tmp_path / "payload"
    path.write_bytes(b"completed\n")

    assert file_sha256(path) == hashlib.sha256(b"completed\n").hexdigest()


def test_manifest_extra_field_is_rejected(tmp_path: Path) -> None:
    fixture = create_validated_bundle(tmp_path)
    manifest_path = fixture.bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["unexpected"] = True
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    _rehash_bundle(fixture.bundle)

    report = fixture.validator.validate(fixture.bundle)

    assert not report.valid
    assert "manifest.fields" in {issue.code for issue in report.issues}
