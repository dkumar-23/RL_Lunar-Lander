"""Bounded inference integration tests with injected checkpoint and environment."""

from __future__ import annotations

import csv
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

import numpy as np
import pytest
import torch
from gymnasium import spaces
from torch import nn

from src.common import LoadedCheckpoint, RunMetadata, configuration_sha256
from src.evaluation import (
    BundleTrustError,
    EvaluationConfig,
    EvaluationEngine,
    EvaluationError,
    require_validated_bundle,
)
from src.evaluation.engine import EvaluationAgent, EvaluationEnvironment
from src.models import QNetwork
from tests.unit.evaluation.fixtures import create_validated_bundle


class FakeAgent:
    """Small deterministic policy exposing the production inference contract."""

    def __init__(self) -> None:
        self.device = torch.device("cpu")
        self.online_network = nn.Linear(8, 4)
        self.target_network = nn.Linear(8, 4)
        self.exploration_arguments: list[bool] = []

    def select_action(self, observation: np.ndarray[Any, Any], explore: bool) -> int:
        """Record that evaluation explicitly disables exploration."""
        self.exploration_arguments.append(explore)
        values = self.online_network(torch.as_tensor(observation).float().unsqueeze(0))
        return int(values.argmax(dim=1).item())

    def eval(self) -> None:
        """Place both injected networks in inference mode."""
        self.online_network.eval()
        self.target_network.eval()


class SafeLandingEnvironment:
    """One-step environment ending in the shared safe-landing state."""

    def __init__(self) -> None:
        self.seeds: list[int | None] = []
        self.closed = False
        self.observation_space = spaces.Box(
            low=-1.0, high=1.0, shape=(8,), dtype=np.float32
        )
        self.action_space: spaces.Discrete[np.int64] = spaces.Discrete(4)

    def reset(
        self, *, seed: int | None = None
    ) -> tuple[np.ndarray[Any, Any], dict[str, Any]]:
        """Return a fixed initial observation."""
        self.seeds.append(seed)
        return np.zeros(8, dtype=np.float32), {}

    def step(
        self, action: int
    ) -> tuple[np.ndarray[Any, Any], float, bool, bool, dict[str, Any]]:
        """Return a terminal observation satisfying every landing predicate."""
        observation = np.zeros(8, dtype=np.float32)
        observation[6:] = 1.0
        return observation, 2.5, True, False, {}

    def close(self) -> None:
        """Record deterministic resource cleanup."""
        self.closed = True


def test_engine_runs_inference_without_exploration_gradients_or_mutation(
    tmp_path: Path,
) -> None:
    """A trusted synthetic bundle produces raw and aggregate local outputs."""
    fixture = create_validated_bundle(tmp_path)
    agent = FakeAgent()
    environment = SafeLandingEnvironment()
    online_state = {
        key: value.clone() for key, value in agent.online_network.state_dict().items()
    }
    target_state = {
        key: value.clone() for key, value in agent.target_network.state_dict().items()
    }
    config_hash = configuration_sha256(fixture.bundle / "resolved_config.yaml")

    def checkpoint_loader(
        path: Path, *, map_location: str | torch.device
    ) -> LoadedCheckpoint:
        del path, map_location
        return LoadedCheckpoint(
            model_state=online_state,
            target_state=target_state,
            optimizer_state={},
            scheduler_state=None,
            metadata=RunMetadata("EXP-001", "RUN-001", 2, 2, config_hash, 7, "a" * 40),
        )

    config = EvaluationConfig(
        fixture.validated_root,
        fixture.validation_root,
        tmp_path / "evaluation",
        episodes=2,
        max_steps_per_episode=3,
        random_seed=11,
        checkpoint="best",
        device="cpu",
    )

    def agent_factory(
        algorithm: str,
        values: Mapping[str, Any],
        device: str,
        active_environment: EvaluationEnvironment,
    ) -> EvaluationAgent:
        del algorithm, values, device, active_environment
        return cast(EvaluationAgent, agent)

    engine = EvaluationEngine(
        config,
        validator=fixture.validator,
        checkpoint_loader=checkpoint_loader,
        agent_factory=agent_factory,
        environment_factory=lambda variant, environment_config: environment,
    )

    episodes, summary = engine.evaluate(fixture.bundle)

    assert [item.total_reward for item in episodes] == [2.5, 2.5]
    assert all(item.landing_success for item in episodes)
    assert agent.exploration_arguments == [False, False]
    assert not torch.is_grad_enabled() or summary["gradients_enabled"] is False
    assert summary["parameters_unchanged"] is True
    assert environment.seeds == [11, 12]
    assert environment.closed
    output = tmp_path / "evaluation" / "EXP-001" / "RUN-001"
    with (output / "evaluation_metrics.csv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream))
    persisted_summary = json.loads(
        (output / "evaluation_summary.json").read_text(encoding="utf-8")
    )
    assert {row["experiment_id"] for row in rows} == {"EXP-001"}
    assert {row["run_id"] for row in rows} == {"RUN-001"}
    assert {row["source_manifest_sha256"] for row in rows} == {
        summary["source_manifest_sha256"]
    }
    assert persisted_summary == summary


def test_engine_reuses_canonical_agent_factory_with_resolved_training_config(
    tmp_path: Path,
) -> None:
    """Production construction consumes the persisted training/environment shape."""
    fixture = create_validated_bundle(tmp_path)
    environment = SafeLandingEnvironment()
    online = QNetwork(8, 4, [8], nn.ReLU)
    target = QNetwork(8, 4, [8], nn.ReLU)
    config_hash = configuration_sha256(fixture.bundle / "resolved_config.yaml")

    def checkpoint_loader(
        path: Path, *, map_location: str | torch.device
    ) -> LoadedCheckpoint:
        del path, map_location
        return LoadedCheckpoint(
            model_state=online.state_dict(),
            target_state=target.state_dict(),
            optimizer_state={},
            scheduler_state=None,
            metadata=RunMetadata("EXP-001", "RUN-001", 2, 2, config_hash, 7, "a" * 40),
        )

    config = EvaluationConfig(
        fixture.validated_root,
        fixture.validation_root,
        tmp_path / "evaluation",
        episodes=1,
        max_steps_per_episode=2,
        random_seed=3,
        checkpoint="final",
        device="cpu",
    )

    episodes, summary = EvaluationEngine(
        config,
        validator=fixture.validator,
        checkpoint_loader=checkpoint_loader,
        environment_factory=lambda variant, environment_config: environment,
    ).evaluate(fixture.bundle)

    assert episodes[0].landing_success is True
    assert summary["checkpoint"] == "final"
    assert summary["parameters_unchanged"] is True


def test_engine_rejects_untrusted_bundle_before_checkpoint_load(
    tmp_path: Path,
) -> None:
    fixture = create_validated_bundle(tmp_path)
    receipt = fixture.validation_root / "EXP-001" / "RUN-001" / "validation_report.json"
    receipt.write_text('{"valid": false}', encoding="utf-8")
    loader_called = False

    def checkpoint_loader(
        path: Path, *, map_location: str | torch.device
    ) -> LoadedCheckpoint:
        del path, map_location
        nonlocal loader_called
        loader_called = True
        raise AssertionError("Untrusted checkpoint must not be loaded.")

    config = EvaluationConfig(
        fixture.validated_root,
        fixture.validation_root,
        tmp_path / "evaluation",
        episodes=1,
        max_steps_per_episode=1,
        random_seed=1,
        checkpoint="best",
        device="cpu",
    )

    with pytest.raises(BundleTrustError):
        EvaluationEngine(
            config,
            validator=fixture.validator,
            checkpoint_loader=checkpoint_loader,
        ).evaluate(fixture.bundle)

    assert loader_called is False


def test_export_refuses_to_overwrite_existing_evaluation(tmp_path: Path) -> None:
    fixture = create_validated_bundle(tmp_path)
    output = tmp_path / "evaluation" / "EXP-001" / "RUN-001"
    output.mkdir(parents=True)
    marker = output / "existing.txt"
    marker.write_text("preserve\n", encoding="utf-8")
    engine = EvaluationEngine(
        EvaluationConfig(
            fixture.validated_root,
            fixture.validation_root,
            tmp_path / "evaluation",
            episodes=1,
            max_steps_per_episode=1,
            random_seed=1,
            checkpoint="best",
            device="cpu",
        )
    )

    with pytest.raises(EvaluationError, match="will not be overwritten"):
        engine.export(
            require_validated_bundle(
                fixture.bundle,
                validated_root=fixture.validated_root,
                validation_root=fixture.validation_root,
                validator=fixture.validator,
            ),
            [],
            {},
        )

    assert marker.read_text(encoding="utf-8") == "preserve\n"
