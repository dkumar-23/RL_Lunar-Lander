"""Trust boundary for promoted Google Colab training bundles."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from src.common import TrainingArtifactValidator, file_sha256


class BundleTrustError(RuntimeError):
    """Raised before downstream code can consume an untrusted bundle."""


@dataclass(frozen=True)
class ValidatedBundle:
    """A promoted bundle whose receipt and current bytes have been rechecked."""

    path: Path
    validation_report: Path
    manifest: Mapping[str, Any]
    manifest_sha256: str

    @property
    def experiment_id(self) -> str:
        """Return the validated experiment identifier."""
        return str(self.manifest["experiment_id"])

    @property
    def run_id(self) -> str:
        """Return the validated run identifier."""
        return str(self.manifest["run_id"])


def require_validated_bundle(
    bundle: Path,
    *,
    validated_root: Path,
    validation_root: Path,
    validator: TrainingArtifactValidator | None = None,
) -> ValidatedBundle:
    """Fail closed unless a promoted bundle and its receipt remain valid.

    Receipt checks happen before invoking the shared validator. The validator
    then rechecks the complete artifact inventory, integrity file, metrics, and
    both restrictive checkpoint payloads against the promoted bytes.
    """
    root = validated_root.resolve()
    candidate = bundle.resolve()
    try:
        relative = candidate.relative_to(root)
    except ValueError as exc:
        raise BundleTrustError(
            f"Bundle must be under the validated root: {root}"
        ) from exc
    if len(relative.parts) != 2:
        raise BundleTrustError("Validated bundle path must be EXP-NNN/RUN-NNN.")
    if not candidate.is_dir():
        raise BundleTrustError(f"Validated bundle does not exist: {candidate}")

    manifest_path = candidate / "manifest.json"
    manifest = _read_object(manifest_path, "manifest")
    manifest_hash = file_sha256(manifest_path)
    experiment_id, run_id = relative.parts
    if manifest.get("experiment_id") != experiment_id:
        raise BundleTrustError("Manifest experiment does not match its promoted path.")
    if manifest.get("run_id") != run_id:
        raise BundleTrustError("Manifest run does not match its promoted path.")
    if manifest.get("algorithm") not in {"DQN", "DDQN"}:
        raise BundleTrustError("Manifest algorithm must be DQN or DDQN.")
    if manifest.get("environment_variant") not in {"original", "modified"}:
        raise BundleTrustError(
            "Manifest environment_variant must be original or modified."
        )

    receipt_root = validation_root.resolve()
    receipt_candidate = receipt_root / relative / "validation_report.json"
    receipt_path = receipt_candidate.resolve()
    try:
        receipt_path.relative_to(receipt_root)
    except ValueError as exc:
        raise BundleTrustError(
            "Validation report resolves outside the validation root."
        ) from exc
    if receipt_path != receipt_candidate:
        raise BundleTrustError("Validation report path must not contain symlinks.")
    receipt = _read_object(receipt_path, "validation report")
    if receipt.get("valid") is not True:
        raise BundleTrustError("Validation report does not record a passing result.")
    if receipt.get("issues") != []:
        raise BundleTrustError("Passing validation report must contain no issues.")
    if receipt.get("manifest_sha256") != manifest_hash:
        raise BundleTrustError(
            "Validation report manifest hash does not match the promoted bundle."
        )
    if receipt.get("experiment_id") != experiment_id or receipt.get("run_id") != run_id:
        raise BundleTrustError("Validation report identity does not match the bundle.")

    current_report = (validator or TrainingArtifactValidator()).validate(candidate)
    if not current_report.valid:
        details = "; ".join(issue.code for issue in current_report.issues)
        raise BundleTrustError(f"Promoted bundle failed integrity recheck: {details}")
    if current_report.manifest_sha256 != manifest_hash:
        raise BundleTrustError("Integrity recheck returned a different manifest hash.")
    if current_report.experiment_id != experiment_id or current_report.run_id != run_id:
        raise BundleTrustError(
            "Integrity recheck returned a different bundle identity."
        )

    return ValidatedBundle(
        path=candidate,
        validation_report=receipt_path,
        manifest=MappingProxyType(dict(manifest)),
        manifest_sha256=manifest_hash,
    )


def _read_object(path: Path, description: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise BundleTrustError(f"Missing or unsafe {description}: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BundleTrustError(f"Unable to read {description}: {path}") from exc
    if not isinstance(value, dict):
        raise BundleTrustError(f"{description.capitalize()} must be a JSON object.")
    return value
