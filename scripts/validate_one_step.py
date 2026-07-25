"""Verify exactly one optimizer update using deterministic synthetic transitions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from src.common.seed import initialize_seed
from src.memory import Transition
from src.training import (
    Algorithm,
    create_agent,
    load_training_config,
    validate_local_test_limits,
)

_LUNAR_OBSERVATION_DIMENSION = 8
_LUNAR_ACTION_COUNT = 4


def parse_args() -> argparse.Namespace:
    """Parse one-step validation options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/training.yaml"))
    parser.add_argument("--algorithm", choices=list(Algorithm), default=Algorithm.DQN)
    return parser.parse_args()


def main() -> int:
    """Perform and verify one, and only one, synthetic optimizer update."""
    args = parse_args()
    validate_local_test_limits(max_steps=1, optimization_steps=1)
    config = load_training_config(args.config)
    rng = initialize_seed(config.random_seed, deterministic=config.deterministic)
    agent = create_agent(
        config,
        Algorithm(args.algorithm),
        _LUNAR_OBSERVATION_DIMENSION,
        _LUNAR_ACTION_COUNT,
        rng,
        device="cpu",
    )
    transitions = tuple(
        Transition(
            state=rng.standard_normal(_LUNAR_OBSERVATION_DIMENSION).astype(np.float32),
            action=index % _LUNAR_ACTION_COUNT,
            reward=float((index % 5) - 2),
            next_state=rng.standard_normal(_LUNAR_OBSERVATION_DIMENSION).astype(
                np.float32
            ),
            terminated=index % 11 == 0,
            truncated=False,
        )
        for index in range(config.batch_size)
    )
    before = tuple(
        parameter.detach().clone() for parameter in agent.online_network.parameters()
    )
    loss = agent.learn(transitions)
    after = tuple(agent.online_network.parameters())
    changed = any(
        not torch.equal(left, right.detach())
        for left, right in zip(before, after, strict=True)
    )
    if agent.optimization_steps != 1 or not changed or not np.isfinite(loss):
        raise RuntimeError("Exactly-one-step optimizer verification failed.")
    print(
        json.dumps(
            {
                "status": "LOCAL_VERIFIED",
                "promotable": False,
                "optimization_steps": agent.optimization_steps,
                "parameters_changed": changed,
                "loss_finite": True,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
