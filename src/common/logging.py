"""Centralized creation of repository-owned loggers."""

from __future__ import annotations

import logging
import threading
from pathlib import Path


class LoggerFactory:
    """Create explicitly configured console and/or file loggers.

    The factory owns the direct handlers of each requested logger. Recreating a
    logger closes and replaces those handlers so repeated initialization cannot
    duplicate output.
    """

    _lock = threading.RLock()

    @classmethod
    def create(
        cls,
        name: str,
        *,
        level: int | str,
        format_string: str,
        console: bool,
        file_path: Path | None,
    ) -> logging.Logger:
        """Create or reconfigure one named logger.

        Args:
            name: Non-empty logger name.
            level: Standard library logging level name or numeric value.
            format_string: Explicit ``logging.Formatter`` format string.
            console: Whether to attach a standard error stream handler.
            file_path: UTF-8 log destination, or ``None`` for no file handler.

        Returns:
            The configured logger with propagation disabled.

        Raises:
            TypeError: An option has an unsupported type.
            ValueError: The name or format is empty, no output is selected, or
                the logging level is invalid.

        Side Effects:
            Creates the file destination's parent directories when required.
            Existing direct handlers on the named logger are closed and removed.
        """
        if not isinstance(name, str):
            raise TypeError("name must be a string.")
        if not name:
            raise ValueError("name must not be empty.")
        if not isinstance(format_string, str):
            raise TypeError("format_string must be a string.")
        if not format_string:
            raise ValueError("format_string must not be empty.")
        if not isinstance(console, bool):
            raise TypeError("console must be a bool.")
        if file_path is not None and not isinstance(file_path, Path):
            raise TypeError("file_path must be a pathlib.Path or None.")
        if not console and file_path is None:
            raise ValueError("At least one logging output must be selected.")

        formatter = logging.Formatter(format_string)
        handlers: list[logging.Handler] = []
        if console:
            handlers.append(logging.StreamHandler())
        if file_path is not None:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            handlers.append(logging.FileHandler(file_path, encoding="utf-8"))
        for handler in handlers:
            handler.setFormatter(formatter)
            handler.setLevel(level)

        with cls._lock:
            logger = logging.getLogger(name)
            logger.setLevel(level)
            logger.propagate = False
            for existing in tuple(logger.handlers):
                logger.removeHandler(existing)
                existing.close()
            for handler in handlers:
                logger.addHandler(handler)
            return logger


def get_logger(
    name: str,
    *,
    level: int | str,
    format_string: str,
    console: bool,
    file_path: Path | None,
) -> logging.Logger:
    """Create a logger through the repository's centralized factory."""
    return LoggerFactory.create(
        name,
        level=level,
        format_string=format_string,
        console=console,
        file_path=file_path,
    )
