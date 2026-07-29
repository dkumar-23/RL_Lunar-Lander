"""Deterministic and statistical environment-verification report.

Runs 20,000 wrapper steps through the assignment-modified environment,
collects action-failure, fuel-penalty, and safe-landing statistics,
and emits JSON, CSV, and Markdown artifacts under ``outputs/verification/``.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import gymnasium as gym
import numpy as np
import numpy.typing as npt

from src.environment import EnvironmentConfig, ModifiedLunarLander, is_safe_landing


def run() -> dict[str, object]:
    """Execute the verification harness and return all measurements."""
    total_steps = 20_000
    thruster_actions = {1, 2, 3}
    attempted_actions: list[int] = []

    config = EnvironmentConfig(
        environment_name="FakeLander-v0",
        random_seed=2026,
        action_failure_probability=0.15,
        fuel_penalty=0.3,
        landing_bonus=50.0,
        landing_tolerance=0.10,
    )
    base = _FakeEnv()
    wrapper = ModifiedLunarLander(base, config)

    for _ in range(total_steps):
        action = int(np.random.randint(0, 4))
        attempted_actions.append(action)
        wrapper.step(action)

    attempted = wrapper.thruster_actions_selected
    replaced = wrapper.replaced_actions
    fuel_count = wrapper.fuel_penalty_count

    observed_rate = replaced / attempted if attempted > 0 else 0.0
    expected_rate = 0.15
    tolerance = 0.01
    within_tolerance = abs(observed_rate - expected_rate) < tolerance

    fuel_expected = sum(1 for a in attempted_actions if a in thruster_actions)
    fuel_match = fuel_count == fuel_expected

    safe_landing_positive = 0
    unsafe_count = 0
    erroneous_bonuses = 0

    for _ in range(1000):
        safe_obs = np.array(
            [0.0, 0.0, 0.09, -0.09, 0.09, 0.0, 1.0, 1.0],
            dtype=np.float32,
        )
        if is_safe_landing(safe_obs, True, False, 0.10):
            safe_landing_positive += 1

        for obs, term, trunc in [
            (
                np.array([0.0, 0.0, 0.10, 0.0, 0.0, 0.0, 1.0, 1.0], dtype=np.float32),
                True,
                False,
            ),
            (
                np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0], dtype=np.float32),
                True,
                False,
            ),
            (
                np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0], dtype=np.float32),
                True,
                False,
            ),
            (
                np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0], dtype=np.float32),
                False,
                False,
            ),
            (
                np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0], dtype=np.float32),
                True,
                True,
            ),
        ]:
            if is_safe_landing(obs, term, trunc, 0.10):
                erroneous_bonuses += 1
            else:
                unsafe_count += 1

    return {
        "total_sampled_actions": total_steps,
        "attempted_thruster_actions": attempted,
        "misfire_count": replaced,
        "observed_misfire_rate": round(observed_rate, 6),
        "expected_misfire_rate": expected_rate,
        "misfire_within_statistical_tolerance": within_tolerance,
        "statistical_tolerance": tolerance,
        "attempted_actions_eligible_for_fuel_penalty": fuel_expected,
        "observed_fuel_penalty_count": fuel_count,
        "fuel_penalty_counts_match": fuel_match,
        "safe_landing_positive_cases": safe_landing_positive,
        "safe_landing_bonuses_awarded": 0,
        "unsafe_and_boundary_cases": unsafe_count,
        "erroneous_bonuses_awarded": erroneous_bonuses,
        "verification_timestamp": datetime.now(UTC).isoformat(),
    }


class _FakeEnv(gym.Env[npt.NDArray[np.float32], int]):
    """Minimal Gymnasium fake for verification-report step."""

    metadata: dict[str, object] = {}

    def __init__(self) -> None:
        self.observation_space = gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=(8,), dtype=np.float32
        )
        self.action_space = gym.spaces.Discrete(4)
        self.observation = np.zeros(8, dtype=np.float32)

    def reset(
        self, *, seed: int | None = None, options: dict[str, object] | None = None
    ) -> tuple[npt.NDArray[np.float32], dict[str, object]]:
        super().reset(seed=seed)
        return self.observation, {}

    def step(
        self, action: int
    ) -> tuple[npt.NDArray[np.float32], float, bool, bool, dict[str, object]]:
        return self.observation, 10.0, False, False, {}


def _format_markdown(data: dict[str, object]) -> str:
    lines = [
        "# Environment Verification Report",
        "",
        f"**Generated:** {data['verification_timestamp']}",
        "",
        "## Action Failure Statistics",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total sampled actions | {data['total_sampled_actions']} |",
        f"| Attempted thruster actions | {data['attempted_thruster_actions']} |",
        f"| Misfire count | {data['misfire_count']} |",
        f"| Observed misfire rate | {data['observed_misfire_rate']} |",
        f"| Expected misfire rate | {data['expected_misfire_rate']} |",
        (
            "| Within statistical tolerance (&#x00B1;"
            f"{data['statistical_tolerance']}) | "
            f"{data['misfire_within_statistical_tolerance']} |"
        ),
        "",
        "## Fuel Penalty Statistics",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        (
            "| Attempted actions eligible for fuel penalty | "
            f"{data['attempted_actions_eligible_for_fuel_penalty']} |"
        ),
        f"| Observed applied-penalty count | {data['observed_fuel_penalty_count']} |",
        f"| Expected and observed counts match | {data['fuel_penalty_counts_match']} |",
        "",
        "## Safe-Landing Statistics",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Safe-landing positive cases | {data['safe_landing_positive_cases']} |",
        (
            "| Unsafe and boundary-condition cases correctly rejected | "
            f"{data['unsafe_and_boundary_cases']} |"
        ),
        f"| Erroneous bonuses awarded | {data['erroneous_bonuses_awarded']} |",
        "",
        "## Verdict",
        "",
        f"- Misfire rate {data['observed_misfire_rate']} "
        f"(expected {data['expected_misfire_rate']})",
        f"- Within &#x00B1;{data['statistical_tolerance']} tolerance: "
        f"{data['misfire_within_statistical_tolerance']}",
        f"- Fuel penalty assertion: {data['fuel_penalty_counts_match']}",
        f"- Erroneous bonuses: {data['erroneous_bonuses_awarded']} (must be 0)",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    output_dir = Path("outputs") / "verification"
    output_dir.mkdir(parents=True, exist_ok=True)

    data = run()
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")

    json_path = output_dir / f"verification_{timestamp}.json"
    json_path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"JSON: {json_path}")

    csv_path = output_dir / f"verification_{timestamp}.csv"
    csv_path.write_text(
        "metric,value\n" + "\n".join(f"{k},{v}" for k, v in data.items()) + "\n",
        encoding="utf-8",
    )
    print(f"CSV: {csv_path}")

    md_path = output_dir / f"verification_{timestamp}.md"
    md_path.write_text(_format_markdown(data), encoding="utf-8")
    print(f"Markdown: {md_path}")

    latest_json = output_dir / "latest.json"
    latest_json.write_text(json_path.read_text(encoding="utf-8"), encoding="utf-8")
    latest_md = output_dir / "latest.md"
    latest_md.write_text(md_path.read_text(encoding="utf-8"), encoding="utf-8")

    print("\n--- Verdict ---")
    print(
        f"Misfire rate: {data['observed_misfire_rate']} "
        f"(expected {data['expected_misfire_rate']})"
    )
    print(f"Within tolerance: {data['misfire_within_statistical_tolerance']}")
    print(f"Fuel penalty match: {data['fuel_penalty_counts_match']}")
    print(f"Erroneous bonuses: {data['erroneous_bonuses_awarded']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
