"""Tests for centralized logger creation."""

from __future__ import annotations

import logging
from pathlib import Path

from src.common.logging import get_logger


def test_reinitialization_does_not_duplicate_handlers(tmp_path: Path) -> None:
    path = tmp_path / "logs" / "run.log"
    first = get_logger(
        "tests.common.no_duplicates",
        level=logging.INFO,
        format_string="%(levelname)s:%(message)s",
        console=True,
        file_path=path,
    )
    second = get_logger(
        "tests.common.no_duplicates",
        level=logging.INFO,
        format_string="%(levelname)s:%(message)s",
        console=True,
        file_path=path,
    )
    second.info("one record")
    for handler in second.handlers:
        handler.flush()

    assert first is second
    assert len(second.handlers) == 2
    assert path.read_text(encoding="utf-8") == "INFO:one record\n"


def test_logger_requires_an_explicit_output() -> None:
    try:
        get_logger(
            "tests.common.no_output",
            level=logging.INFO,
            format_string="%(message)s",
            console=False,
            file_path=None,
        )
    except ValueError as exc:
        assert "output" in str(exc)
    else:
        raise AssertionError("Expected a logger without outputs to be rejected.")
