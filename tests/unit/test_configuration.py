"""Tests for safe deterministic configuration resolution."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.common.configuration import ConfigurationError, resolve_configuration


class ConfigurationTests(unittest.TestCase):
    """Verify canonical hashing and unsafe-value rejection."""

    def test_key_order_does_not_change_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.yaml"
            second = Path(directory) / "second.yaml"
            first.write_text("algorithm: DQN\nseed: 7\n", encoding="utf-8")
            second.write_text("seed: 7\nalgorithm: DQN\n", encoding="utf-8")
            self.assertEqual(
                resolve_configuration(first).sha256,
                resolve_configuration(second).sha256,
            )

    def test_non_mapping_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.yaml"
            path.write_text("- one\n- two\n", encoding="utf-8")
            with self.assertRaises(ConfigurationError):
                resolve_configuration(path)

    def test_non_finite_number_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.yaml"
            path.write_text("value: .nan\n", encoding="utf-8")
            with self.assertRaises(ConfigurationError):
                resolve_configuration(path)


if __name__ == "__main__":
    unittest.main()
