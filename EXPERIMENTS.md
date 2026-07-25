# Document Metadata

| Field | Value |
|--------|--------|
| Document ID | EXP-001 |
| Version | 1.1.0 |
| Status | Approved for Implementation |
| Purpose | Define the complete experimentation methodology, governance, execution strategy, reproducibility policy, and experiment lifecycle for the reinforcement learning project. |
| Scope | Four canonical assignment training experiments, Google Colab execution, reproducibility, artifact generation, local validation, and downstream comparison |
| Audience | AI Coding Agents, ML Engineers, Research Engineers, Teaching Assistants, Repository Maintainers |
| Dependencies | PRD.md, DESIGN.md, WORKFLOW.md, EVALUATION.md |
| Related Documents | REPORT_TEMPLATE.md, TASKS.md, ARCHITECTURE.md |
| Revision History | v1.1.0 - Canonicalized four Colab-only training experiments and local artifact validation |

---

# 1. Purpose

This document defines every experiment that shall be conducted within the repository.

Experiments are considered first-class engineering artifacts.

Every experiment shall be:

- reproducible
- traceable
- statistically valid
- independently executable
- version controlled
- fully documented

Full training depends on an explicitly documented human Colab operator stage.
No hidden or undocumented manual step is permitted.

---

# 2. Experiment Philosophy

The experimentation process follows the scientific method.

```
Hypothesis

↓

Configuration

↓

Execution

↓

Measurement

↓

Analysis

↓

Conclusion

↓

Archival
```

No experiment may bypass any stage.

---

# 3. Experiment Objectives

The repository shall satisfy the following experimentation objectives.

| ID | Objective |
|----|-----------|
| EXP-OBJ-001 | Train DQN in the original and modified environments |
| EXP-OBJ-002 | Train DDQN in the original and modified environments |
| EXP-OBJ-003 | Compare algorithm performance under controlled conditions |
| EXP-OBJ-004 | Measure the effect of assignment environment modifications |
| EXP-OBJ-005 | Produce assignment-required artifacts and visualizations |
| EXP-OBJ-006 | Produce statistically reproducible results |

Environment compatibility, reward equations, landing bonus, fuel penalty, and
stochastic action replacement correctness are verified by VERIFY-009 through
VERIFY-012 before canonical training; they are not experiments.

---

# 4. Experiment Governance

Every experiment shall satisfy the following governance policies.

## GOV-EXP-001

Each experiment receives a unique Experiment Identifier.

---

## GOV-EXP-002

Experiment configuration shall never change after execution begins.

---

## GOV-EXP-003

Every experiment records:

- configuration
- seed
- software version
- checkpoint
- execution timestamp

---

## GOV-EXP-004

Generated artifacts are immutable.

---

## GOV-EXP-005

Experiments may be repeated.

Original artifacts shall never be overwritten.

---

## GOV-EXP-006

Every experiment shall be independently executable.

---

## GOV-EXP-007

Full training for every canonical experiment is Google Colab-only. Local
execution is limited to bounded smoke and one-optimizer-step validation.

---

## GOV-EXP-008

A canonical run is not complete until its downloaded bundle passes the local
validator. Colab completion and download are necessary but insufficient.

---

# 5. Experiment Identification

The complete canonical identifier set is:

```
EXP-001

EXP-002

EXP-003

EXP-004
```

Run identifiers:

```
RUN-001

RUN-002

RUN-003
```

Combined identity:

```
EXP-003

RUN-005
```

---

# 6. Experiment Directory Structure

```
experiments/

    configs/

    definitions/

    results/

    manifests/

    metadata/

outputs/

    metrics/

    evaluation/

    plots/

    reports/
```

Every experiment owns its own result directory.

---

# 7. Experiment Lifecycle and Operators

Every experiment follows the lifecycle below.

```
Registered

↓

Configured

↓

Configuration Validated Locally

↓

Human Colab Operator Preflight

↓

Human Colab Operator Full Training

↓

Bundle Downloaded

↓

Local Validator Artifact Validation

↓

Run Complete

↓

Local Evaluation

↓

Archived and Referenced
```

Lifecycle stages shall never be skipped.

The **human Colab operator** is the person who selects one immutable canonical
configuration, reviews preflight, explicitly starts full training in Google
Colab, waits for termination, and downloads the immutable run bundle. The
operator does not edit generated artifacts.

The **local validator** is the local automated stage that validates safe paths,
required files, schema, SHA-256 hashes, experiment/run identity, configuration
hash, checkpoint compatibility, metrics completeness, and termination status.
It runs before any checkpoint is loaded for evaluation.

No AI coding agent or unattended local process may represent itself as the
human operator or execute full assignment training.

---

# 8. Experiment Metadata

Each experiment records:

| Field | Required |
|---------|----------|
| Experiment ID | Yes |
| Run ID | Yes |
| Timestamp | Yes |
| Algorithm | Yes |
| Random Seed | Yes |
| Environment Version | Yes |
| Git Commit | Yes |
| Configuration Hash | Yes |
| Runtime Duration | Yes |
| Artifact SHA-256 Hashes | Yes |
| Colab Runtime Identity | Yes |
| Local Validation Result | Yes |

Metadata shall accompany every generated artifact.

---

# 9. Canonical Assignment Experiments

Exactly four canonical experiments exist. Each is a full training run executed
only in Google Colab by the human Colab operator. Evaluation is not a separate
experiment and runs locally only after the downloaded bundle passes validation.

| Experiment | Algorithm | Environment | Full-training runtime | Run task |
|------------|-----------|-------------|-----------------------|----------|
| EXP-001 | DQN | Original LunarLander | Google Colab only | TASK-052 |
| EXP-002 | DQN | Assignment-modified LunarLander | Google Colab only | TASK-053 |
| EXP-003 | DDQN | Original LunarLander | Google Colab only | TASK-054 |
| EXP-004 | DDQN | Assignment-modified LunarLander | Google Colab only | TASK-055 |

## EXP-001 - DQN Original

Train DQN with the canonical full-training budget in the original environment.
Its immutable configuration differs from EXP-002 only by the documented
environment variant and from EXP-003 only by the documented algorithm.

## EXP-002 - DQN Modified

Train DQN with the same canonical controls in the assignment-modified
environment, including configured reward and action modifications.

## EXP-003 - DDQN Original

Train DDQN with the canonical full-training budget in the original environment.
Its immutable configuration differs from EXP-004 only by the documented
environment variant and from EXP-001 only by the documented algorithm.

## EXP-004 - DDQN Modified

Train DDQN with the same canonical controls in the assignment-modified
environment, including configured reward and action modifications.

Every run bundle shall contain at least the immutable configuration snapshot,
manifest, final/best checkpoint required by configuration, complete training
metrics, logs, runtime/dependency metadata, seed record, repository revision,
termination status, and SHA-256 hashes. Plots and local evaluation outputs are
derived later and do not substitute for required training artifacts.

---

# 10. Verification Activities Outside Experiments

The following are prerequisites, not EXP identifiers:

| Verification | Scope |
|--------------|-------|
| VERIFY-009 | Gymnasium and original/modified environment compatibility |
| VERIFY-010 | Reward equations, landing bonus, and fuel penalty |
| VERIFY-011 | Stochastic action replacement behavior and probability |
| VERIFY-012 | Integrated modified-environment behavior and preserved interfaces |

Bounded local smoke and one-step checks are VERIFY activities under TASK-048.
They provide implementation confidence but never count as canonical training.

---

# 11. Controlled Variables

Unless the canonical matrix explicitly varies them, the following remain
constant across all four experiments.

- environment implementation/version within each original or modified pair
- reward equations
- random seed policy
- replay implementation
- neural architecture
- optimizer
- evaluation methodology

Controlled variables shall be documented in experiment metadata.

---

# 12. Independent Variables

The only canonical independent variables are algorithm (DQN or DDQN) and
environment variant (original or modified). Hyperparameter sweeps are outside
the canonical assignment experiment set and shall not receive EXP-001 through
EXP-004 identifiers.

---

# 13. Dependent Variables

Measured variables include:

- cumulative reward
- average reward
- loss
- convergence episode
- success rate
- evaluation score
- runtime

Dependent variables shall never be manually modified.

---

# 14. Random Seed Strategy

The repository shall implement deterministic execution through centralized seed management.

Every experiment records:

- Python seed
- NumPy seed
- PyTorch seed
- Gymnasium seed

Seed initialization occurs before environment construction.

---

# 15. Repetition Policy

Every experiment shall be repeatable.

Repeated executions shall produce:

- identical configuration
- unique run identifier
- independent artifact directory

Original artifacts remain preserved.

---

# 16. Statistical Methodology

Experimental conclusions shall be supported using descriptive statistical analysis.

Every evaluation shall compute the following statistics from the complete evaluation dataset.

| Statistic | Required |
|-----------|----------|
| Sample Count | Yes |
| Arithmetic Mean | Yes |
| Median | Yes |
| Minimum | Yes |
| Maximum | Yes |
| Variance | Yes |
| Standard Deviation | Yes |

No experiment shall report only the maximum reward.

Performance claims shall be supported by aggregate statistics.

---

# 17. Independent Experimental Runs

A single execution shall never be interpreted as representative algorithm performance.

Each experiment definition shall support multiple independent runs.

```
Experiment

↓

Run 001

Run 002

Run 003

...

Run N
```

Each run shall receive:

- unique Run Identifier
- independent output directory
- recorded random seed
- independent metadata

---

# 18. Random Seed Governance

The repository shall centralize random seed management.

The following generators shall receive synchronized seeds.

```
Python

↓

NumPy

↓

PyTorch

↓

Gymnasium
```

Every experiment shall record:

```
python_seed

numpy_seed

torch_seed

environment_seed
```

Seed initialization shall occur before any object creation.

---

# 19. Configuration Governance

Experiment configuration shall be immutable.

Each execution records:

```
configuration.yaml

↓

validation

↓

configuration_hash

↓

execution
```

Configuration changes require a new experiment execution.

Historical experiment configurations shall never be modified.

---

# 20. Hyperparameter Governance

Hyperparameters belong exclusively to configuration files.

The implementation shall not hardcode hyperparameters.

Typical configurable parameters include:

| Category | Examples |
|----------|----------|
| Optimization | Learning rate, optimizer |
| Replay | Capacity, batch size |
| Exploration | Initial epsilon, final epsilon, decay |
| Discounting | Gamma |
| Target Network | Synchronization frequency |
| Environment | Stochastic probability |

---

# 21. Non-Canonical Hyperparameter Study Policy

Any future non-canonical hyperparameter study shall isolate variables and use a
separate identifier namespace approved in documentation before execution. It
is not one of the four assignment experiments.

Preferred methodology:

```
Baseline

↓

Modify One Variable

↓

Execute

↓

Evaluate

↓

Compare
```

Changing multiple variables simultaneously is discouraged unless explicitly performing factorial experimentation.

---

# 22. Experiment Manifest

Each experiment shall generate a manifest.

Example:

```
experiment_manifest.json
```

Minimum contents:

```
Experiment ID

Run ID

Algorithm

Configuration Hash

Environment Version

Git Commit

Timestamp

Generated Artifacts

Random Seed

Artifact SHA-256 Hashes

Colab Runtime Identity

Termination Status
```

The manifest is the authoritative index for the experiment.

---

# 23. Artifact Lifecycle

Every generated artifact follows the lifecycle below.

```
Generated

↓

Validated

↓

Referenced

↓

Archived
```

Artifacts shall never be overwritten.

---

# 24. Artifact Categories

Artifacts include:

```
Metrics

↓

Checkpoints

↓

Evaluation

↓

Plots

↓

Tables

↓

Metadata

↓

Logs

↓

Manifest
```

Each artifact category has a dedicated repository location.

---

# 25. Artifact Naming Convention

Naming format:

```
<experiment>

↓

<run>

↓

artifact_type

↓

timestamp
```

Examples:

```
EXP-001_RUN-002_rewards.csv

EXP-001_RUN-002_loss.csv

EXP-001_RUN-002_checkpoint.pt

EXP-001_RUN-002_manifest.json

EXP-001_RUN-002_reward_curve.png
```

Naming conventions shall remain deterministic.

---

# 26. Checkpoint Strategy

Checkpoint creation shall occur according to configuration.

Supported strategies include:

| Strategy | Description |
|----------|-------------|
| Periodic | Save every N episodes |
| Best | Save highest-performing checkpoint |
| Final | Save final model |
| Manual | Explicit save request |

Multiple strategies may execute simultaneously.

---

# 27. Checkpoint Contents

Each checkpoint shall include:

```
Model Parameters

Optimizer State

Episode Number

Configuration Snapshot

Experiment Metadata

Random Seed
```

Replay memory persistence is optional and shall be documented if supported.

---

# 28. Checkpoint and Bundle Validation

Before a checkpoint may be loaded or a run accepted, the complete downloaded
bundle shall pass the local validator:

- serialization succeeds
- every manifest SHA-256 hash passes
- metadata complete
- configuration compatible
- model parameters valid

Corrupted checkpoints shall be rejected.

Validation occurs before deserialization. Validators shall reject unsafe paths,
unexpected identity/configuration, incomplete training, and malformed bundles.

---

# 29. Experiment Validation

Every completed experiment shall satisfy:

- configuration valid
- runtime completed
- metrics collected
- checkpoint created
- metadata complete
- artifacts exported
- local bundle validation passed

Validation failures shall prevent publication.

---

# 30. Failure Handling Policy

Failure categories include:

| Category | Action |
|----------|--------|
| Configuration Error | Abort immediately |
| Environment Failure | Preserve diagnostics |
| Training Failure | Save logs and terminate |
| Checkpoint Failure | Retry if recoverable |
| Evaluation Failure | Preserve training artifacts |
| Visualization Failure | Continue after recording failure |

No failure shall silently terminate execution.

---

# 31. Resume Policy

Interrupted experiments may resume only from validated checkpoints.

Resume workflow:

```
Locate Checkpoint

↓

Validate

↓

Restore

↓

Verify Configuration

↓

Resume
```

Configuration mismatches invalidate resume operations.

---

# 32. Metric Collection Policy

Metric collection shall occur automatically.

Collection frequencies include:

| Metric | Frequency |
|---------|-----------|
| Episode Reward | Every Episode |
| Loss | Every Optimization Step |
| Epsilon | Every Episode |
| Evaluation Reward | Every Evaluation Episode |
| Runtime | Continuous |
| Replay Size | Periodic |

Manual metric entry is prohibited.

---

# 33. Visualization Generation Policy

Visualizations shall consume persisted metrics only.

Required plots include:

- training reward
- moving average reward
- loss
- evaluation reward
- DQN vs DDQN comparison

Figures shall be reproducible.

---

# 34. Publication Quality Requirements

Generated figures shall satisfy:

- consistent axis labels
- descriptive titles
- readable fonts
- legend placement
- high resolution
- deterministic styling

Visualization styling shall remain centralized.

---

# 35. Experiment Comparison Methodology

Comparisons shall use identical experimental conditions.

Comparison dimensions include:

| Dimension | Required |
|-----------|----------|
| Mean Reward | Yes |
| Convergence | Yes |
| Stability | Yes |
| Runtime | Yes |
| Success Rate | Yes |
| Variance | Yes |

Algorithms shall not be compared using inconsistent configurations.

---

# 36. Reproducibility Verification

The repository shall support reproducibility verification.

Verification includes:

- identical configuration
- identical random seeds
- identical software versions
- identical repository revision
- identical environment implementation

Expected outcome:

Equivalent statistical behavior under repeated execution.

---

# 37. Experiment Traceability

Each experiment shall trace to:

- Functional Requirements
- Design Components
- Training Configuration
- Evaluation Results
- Generated Figures
- Report Sections

Traceability example:

| Experiment | Requirements | Evaluation |
|------------|--------------|-----------|
| EXP-001 | DQN, original environment | EVAL-001 |
| EXP-002 | DQN, modified environment | EVAL-002 |
| EXP-003 | DDQN, original environment | EVAL-003 |
| EXP-004 | DDQN, modified environment | EVAL-004 |

Environment/reward/action correctness traces to VERIFY-009 through VERIFY-012,
not to an EXP identifier.

---

# 38. Experiment Acceptance Criteria

An experiment is accepted only if:

- execution completed successfully
- mandatory metrics collected
- checkpoint generated
- evaluation completed
- plots generated
- metadata complete
- experiment manifest created
- reproducibility information recorded
- local bundle validation passed before any local evaluation
- no validation failures remain

---

# 39. Experiment Quality Gates

Every experiment shall pass the following gates.

```
Configuration Validation

↓

Human Colab Preflight and Explicit Start

↓

Full Training and Bundle Download

↓

Local Schema and Hash Validation

↓

Run Completion

↓

Local Evaluation and Metric Validation

↓

Publication Approval
```

No experiment may bypass any quality gate.

---

# 40. Experiment Definition of Done

An experiment is complete when:

- objectives are satisfied
- outputs generated
- statistical summaries computed
- evaluation completed
- artifacts archived
- figures exported
- report assets generated
- metadata validated
- full training was human-operated in Google Colab
- downloaded bundle passed local validation before checkpoint loading
- traceability established
- repository remains reproducible

---

# 41. Human and Automated Responsibilities

Experiment-related AI Coding Agents shall:

- prepare and bounded-test experiment infrastructure exactly as configured
- never execute or claim completion of full assignment training
- never modify historical artifacts
- preserve experiment manifests
- validate outputs before publication
- maintain reproducibility
- record failures completely
- avoid undocumented experimental changes

The human Colab operator alone starts full training. The local validator alone
grants artifact-validation passage. Neither stage may claim a run complete
without the other.

---
