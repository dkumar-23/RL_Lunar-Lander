# Command Permissions

## Status

Approved for Implementation.

## Purpose

This document defines the local OpenCode execution boundary for the
repository. It implements CON-011: full DQN and DDQN training, including
resumed training and EXP-001 through EXP-004, runs only in Google Colab.

## Default Policy

Unmatched commands require user approval. Specific rules in
`opencode.jsonc` follow the default because OpenCode resolves the last
matching permission rule.

No permission rule authorizes behavior forbidden by repository
documentation. Permission prompts are safeguards, not substitutes for
runtime validation.

## Allowed Local Responsibilities

Local OpenCode may perform:

- implementation and code review,
- formatting, linting, and type checking,
- unit and bounded integration tests,
- configuration validation,
- bounded smoke tests,
- exactly-one-step learning validation,
- Colab notebook preparation and static validation,
- imported training artifact validation,
- evaluation of validated checkpoints,
- visualization and report generation from validated artifacts,
- documentation maintenance,
- non-destructive Git inspection,
- Git changes explicitly approved by the repository owner.

## Prohibited Local Responsibilities

Local OpenCode shall not:

- execute full or resumed DQN training,
- execute full or resumed DDQN training,
- launch EXP-001 through EXP-004,
- execute `notebooks/train_colab.ipynb` locally,
- use smoke output as experiment evidence,
- create a training completion marker,
- fabricate checkpoints, metrics, manifests, or completion status,
- evaluate an imported checkpoint before its artifact bundle passes
  validation.

## Approved Local Entry Points

The following scripts are the only repository entry points intended for
local training-related validation:

```text
scripts/validate_config.py
scripts/run_smoke_test.py
scripts/validate_one_step.py
scripts/validate_training_artifacts.py
scripts/evaluate.py
scripts/generate_plots.py
scripts/generate_report.py
```

These entry points are invoked as modules, for example:

```text
python3 -m scripts.validate_config
python3 -m scripts.validate_training_artifacts
```

Smoke and one-step scripts shall enforce their limits internally and shall
never emit promotable experiment artifacts.

## Colab-Only Entry Points

The following entry points are Colab-only:

```text
scripts/train.py
scripts/experiment.py
notebooks/train_colab.ipynb
```

The training implementation shall also enforce this boundary in code.
Shell permissions alone are not an operating-system sandbox and cannot
determine semantic intent for every possible command.

## Artifact Boundary

Human operators transfer complete Google Drive bundles to:

```text
outputs/colab/incoming/<experiment_id>/<run_id>/
```

Local tools may validate and consume those bundles. They shall not modify
the imported payload. Validation reports and promoted artifacts use the
locations defined by `COLAB_TRAINING.md`.

## Configuration Reload

Changes to `opencode.jsonc` take effect only after OpenCode is restarted.
