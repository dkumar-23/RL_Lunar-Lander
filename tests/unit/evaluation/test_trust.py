"""Tests for promoted-bundle receipt and integrity gates."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.evaluation import BundleTrustError, require_validated_bundle

from .fixtures import create_validated_bundle


def test_valid_receipt_and_rechecked_bundle_are_accepted(tmp_path: Path) -> None:
    """The current promoted bytes remain bound to their passing receipt."""
    fixture = create_validated_bundle(tmp_path)

    trusted = require_validated_bundle(
        fixture.bundle,
        validated_root=fixture.validated_root,
        validation_root=fixture.validation_root,
        validator=fixture.validator,
    )

    assert trusted.experiment_id == "EXP-001"
    assert trusted.run_id == "RUN-001"


def test_changed_receipt_manifest_hash_fails_closed(tmp_path: Path) -> None:
    """A stale passing report cannot authorize current bundle bytes."""
    fixture = create_validated_bundle(tmp_path)
    receipt = fixture.validation_root / "EXP-001" / "RUN-001" / "validation_report.json"
    data = json.loads(receipt.read_text(encoding="utf-8"))
    data["manifest_sha256"] = "0" * 64
    receipt.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(BundleTrustError, match="manifest hash"):
        require_validated_bundle(
            fixture.bundle,
            validated_root=fixture.validated_root,
            validation_root=fixture.validation_root,
            validator=fixture.validator,
        )


def test_tampered_payload_fails_integrity_recheck(tmp_path: Path) -> None:
    """A previously passed receipt does not bypass current file hashes."""
    fixture = create_validated_bundle(tmp_path)
    (fixture.bundle / "training.log").write_text("tampered\n", encoding="utf-8")

    with pytest.raises(BundleTrustError, match="integrity recheck"):
        require_validated_bundle(
            fixture.bundle,
            validated_root=fixture.validated_root,
            validation_root=fixture.validation_root,
            validator=fixture.validator,
        )
