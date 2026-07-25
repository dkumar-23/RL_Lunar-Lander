"""Run a non-promotable local smoke check capped at 32 environment steps."""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

from src.common.seed import initialize_seed
from src.environment import create_environment
from src.training import (
    ExecutionContext,
    FixedValidationSet,
    LocalLimits,
    TrainingEngine,
    create_agent,
    create_replay_buffer,
    environment_dimensions,
    load_experiment_config,
    validate_local_test_limits,
    validate_registered_configuration,
)


def parse_args() -> argparse.Namespace:
    """Parse bounded smoke options without exposing limit-removal flags."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--experiment-config",
        type=Path,
        required=True,
    )
    parser.add_argument("--max-steps", type=int, default=32)
    return parser.parse_args()


def main() -> int:
    """Execute the shared engine under immutable local RuntimeGuard limits."""
    args = parse_args()
    validate_local_test_limits(args.max_steps, 1)
    experiment = load_experiment_config(args.experiment_config, Path.cwd())
    validate_registered_configuration(experiment, Path.cwd())
    training = replace(
        experiment.training,
        episodes=1,
        max_steps_per_episode=min(
            experiment.training.max_steps_per_episode,
            args.max_steps,
        ),
    )
    environment_config = experiment.environment
    rng = initialize_seed(training.random_seed, deterministic=training.deterministic)
    environment = create_environment(environment_config)
    try:
        input_dim, action_count = environment_dimensions(environment)
        agent = create_agent(
            training,
            experiment.algorithm,
            input_dim,
            action_count,
            rng,
            device="cpu",
        )
        replay = create_replay_buffer(training, rng)
        validation_set = FixedValidationSet.create(
            training.validation_state_count,
            input_dim,
            training.validation_seed,
        )
        engine = TrainingEngine(
            training,
            environment_config,
            environment,
            agent,
            replay,
            validation_set,
            ExecutionContext.LOCAL_TEST,
        )
        result = engine.run(LocalLimits(args.max_steps, 1))
    finally:
        environment.close()
    print(
        json.dumps(
            {
                "status": "LOCAL_VERIFIED",
                "promotable": False,
                "experiment_id": experiment.experiment_id,
                "algorithm": experiment.algorithm.value,
                "environment_variant": experiment.environment_variant.value,
                "environment_steps": result.global_steps,
                "optimization_steps": result.optimization_steps,
                "episodes": len(result.episode_metrics),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
