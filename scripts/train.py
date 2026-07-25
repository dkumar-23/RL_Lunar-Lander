"""Run exactly one attested canonical experiment in Google Colab."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from src.common.seed import initialize_seed
from src.environment import create_environment
from src.training import (
    ExecutionContext,
    FixedValidationSet,
    TrainingEngine,
    attest_colab_full_training,
    create_agent,
    create_replay_buffer,
    environment_dimensions,
    load_experiment_config,
)
from src.training.bundle import ColabBundleWriter, utc_now

_REPOSITORY_URL = "https://github.com/dkumar-23/RL_Lunar-Lander"
_RUN_PATTERN = re.compile(r"RUN-[0-9]{3}")


def parse_args() -> argparse.Namespace:
    """Parse the controlled notebook delegation contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execution-context", required=True, choices=[ExecutionContext.COLAB_FULL]
    )
    parser.add_argument("--repository-root", required=True, type=Path)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    """Attest the runtime, execute one experiment, and finalize its bundle."""
    args = parse_args()
    repository = args.repository_root.resolve()
    output = args.output.resolve()
    drive_root = output.parents[2]

    # CON-011 attestation intentionally precedes configuration or ML construction.
    attestation = attest_colab_full_training(
        repository, args.expected_commit, drive_root
    )
    if _RUN_PATTERN.fullmatch(args.run_id) is None:
        raise ValueError("run-id must match RUN-NNN.")
    expected_output = (
        drive_root / args.expected_commit / args.experiment_id / args.run_id
    )
    if output != expected_output:
        raise ValueError("output must follow <drive>/<commit>/<experiment>/<run>.")

    writer: ColabBundleWriter | None = None
    environment = None
    try:
        experiment = load_experiment_config(args.config, repository)
        if experiment.experiment_id != args.experiment_id:
            raise ValueError("CLI experiment-id differs from the selected definition.")
        if experiment.training.random_seed != args.seed:
            raise ValueError("CLI seed differs from the canonical training seed.")
        config_relative = args.config.resolve().relative_to(repository).as_posix()
        rng = initialize_seed(
            args.seed, deterministic=experiment.training.deterministic
        )
        environment = create_environment(experiment.environment)
        input_dim, action_count = environment_dimensions(environment)
        agent = create_agent(
            experiment.training,
            experiment.algorithm,
            input_dim,
            action_count,
            rng,
        )
        replay = create_replay_buffer(experiment.training, rng)
        validation_set = FixedValidationSet.create(
            experiment.training.validation_state_count,
            input_dim,
            experiment.training.validation_seed,
        )
        writer = ColabBundleWriter(
            output,
            experiment,
            args.run_id,
            _REPOSITORY_URL,
            args.expected_commit,
            config_relative,
            agent,
            validation_set,
            attestation,
        )
        engine = TrainingEngine(
            experiment.training,
            experiment.environment,
            environment,
            agent,
            replay,
            validation_set,
            ExecutionContext.COLAB_FULL,
            colab_attestation=attestation,
            logger=writer.logger,
            checkpoint_callback=writer.save_checkpoint,
        )
        result = engine.run()
        writer.write_metrics(result)
        final_episode = result.episode_metrics[-1].episode
        writer.save_checkpoint("final", final_episode, result.global_steps)
        environment.close()
        environment = None
        writer.complete()
        return 0
    except BaseException as exc:
        if writer is not None:
            writer.fail(exc)
        else:
            _write_early_failure(output, args.experiment_id, args.run_id, exc)
        raise
    finally:
        if environment is not None:
            environment.close()


def _write_early_failure(
    output: Path, experiment_id: str, run_id: str, error: BaseException
) -> None:
    """Record an attested pre-construction failure without success artifacts."""
    if output.exists():
        return
    status = output / "status"
    status.mkdir(parents=True)
    marker = {
        "experiment_id": experiment_id,
        "run_id": run_id,
        "failed_at_utc": utc_now(),
        "error_type": type(error).__name__,
        "error": str(error),
    }
    (status / "FAILED.json").write_text(
        json.dumps(marker, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    raise SystemExit(main())
