"""Unit tests for configured environment construction."""

from __future__ import annotations

import pytest

from src.environment import ModifiedLunarLander, create_environment

from .fakes import FakeLanderEnv
from .test_wrapper import make_config


def test_factory_constructs_and_wraps_configured_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The public factory must preserve Gymnasium construction controls."""
    base = FakeLanderEnv()
    captured: dict[str, object] = {}

    def fake_make(
        environment_name: str,
        *,
        render_mode: str | None,
    ) -> FakeLanderEnv:
        captured.update(
            environment_name=environment_name,
            render_mode=render_mode,
        )
        return base

    monkeypatch.setattr("src.environment.factory.gym.make", fake_make)
    config = make_config()

    environment = create_environment(config)

    assert isinstance(environment, ModifiedLunarLander)
    assert environment.env is base
    assert captured == {
        "environment_name": config.environment_name,
        "render_mode": config.render_mode,
    }
