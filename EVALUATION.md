# Document Metadata

| Field | Value |
|--------|--------|
| Document ID | EVAL-001 |
| Version | 1.1.0 |
| Status | Approved for Implementation |
| Purpose | Define the complete evaluation methodology, metric definitions, statistical analysis procedures, comparison framework, and acceptance criteria for assessing reinforcement learning performance and assignment compliance. |
| Scope | Local-only inference evaluation of locally validated Colab run bundles, experiment comparison, statistical validation, reproducibility verification, and assignment outcome assessment |
| Audience | AI Coding Agents, ML Engineers, Research Engineers, Teaching Assistants, Repository Maintainers |
| Dependencies | PRD.md, DESIGN.md, WORKFLOW.md, EXPERIMENTS.md |
| Related Documents | REPORT_TEMPLATE.md, TASKS.md, ARCHITECTURE.md |
| Revision History | v1.0.0 - Initial Evaluation Specification; v1.1.0 - Required validated run bundles and local-only evaluation before checkpoint load |

---

# 1. Purpose

This document defines the authoritative evaluation methodology for the repository.

Evaluation exists to determine:

- implementation correctness
- learning effectiveness
- convergence characteristics
- assignment objective fulfillment
- reproducibility
- comparative algorithm performance

Evaluation procedures defined herein are normative.

No evaluation script shall implement metrics inconsistent with this document.

All evaluation execution is local. Google Colab is reserved for human-operated
full training of EXP-001 through EXP-004 and shall not perform canonical
evaluation.

---

# 2. Evaluation Philosophy

Evaluation is an independent process.

Training and evaluation shall remain completely separated.

Evaluation shall never:

- modify model parameters
- update replay memory
- alter optimizer state
- perform gradient computation
- change exploration schedules

Evaluation is strictly observational.

---

# 3. Evaluation Lifecycle

Every evaluation follows the lifecycle below. Validation precedes checkpoint
selection, checkpoint deserialization, and inference.

```
Colab Run Bundle Downloaded

↓

Local Bundle Validator Executed

↓

Validation Receipt Passed

↓

Manifest, Hashes, Identity, and Configuration Verified

↓

Checkpoint Selected from Validated Manifest

↓

Local Evaluation Environment Created

↓

Checkpoint Loaded Locally

↓

Inference Executed Locally

↓

Metrics Collected

↓

Statistics Computed

↓

Results Persisted

↓

Visualization Generated

↓

Comparison Performed

↓

Archived
```

No stage may be omitted. A failed or missing local validation receipt aborts
evaluation before checkpoint bytes are deserialized.

---

# 4. Evaluation Objectives

| ID | Objective |
|----|-----------|
| EVAL-OBJ-001 | Verify trained policy correctness |
| EVAL-OBJ-002 | Measure cumulative reward |
| EVAL-OBJ-003 | Measure policy stability |
| EVAL-OBJ-004 | Compare DQN and DDQN |
| EVAL-OBJ-005 | Measure convergence quality |
| EVAL-OBJ-006 | Verify stochastic robustness |
| EVAL-OBJ-007 | Produce assignment-required figures |
| EVAL-OBJ-008 | Verify reproducibility |

---

# 5. Evaluation Principles

Every evaluation shall satisfy:

- deterministic execution
- documented configuration
- clean local runtime
- immutable artifacts
- reproducible outputs
- traceable metrics
- statistically valid summaries
- validated source bundle before checkpoint loading

---

# 6. Evaluation Categories

| Category | Identifier | Purpose |
|-----------|------------|---------|
| Functional | CAT-001 | Verify implementation correctness |
| Performance | CAT-002 | Measure training effectiveness |
| Statistical | CAT-003 | Aggregate quantitative results |
| Comparative | CAT-004 | Compare algorithms |
| Robustness | CAT-005 | Measure resilience to stochasticity |
| Reproducibility | CAT-006 | Verify deterministic behavior |

---

# 7. Evaluation Inputs

The evaluation engine consumes only a complete downloaded run bundle that has
passed TASK-047 local validation during TASK-052, TASK-053, TASK-054, or
TASK-055. A loose checkpoint is never a valid input.

Required inputs include:

- trained checkpoint
- configuration snapshot
- experiment metadata
- evaluation configuration
- environment configuration
- experiment manifest
- per-file SHA-256 hashes
- passed local validation receipt tied to the bundle hash

Runtime training state shall never be used.
Validation shall complete before checkpoint selection or deserialization.

---

# 8. Evaluation Outputs

The evaluation process shall generate:

```
evaluation_metrics.csv

evaluation_summary.json

comparison_summary.csv

statistics.json

plots/

tables/
```

Every output shall reference the originating Experiment ID and Run ID.

---

# 9. Evaluation Environment

Evaluation shall execute locally within a clean runtime.

Requirements:

- identical environment implementation
- identical reward equations
- identical preprocessing
- deterministic action selection (unless otherwise configured)
- isolated execution state

No training-only dependencies shall remain active.
Evaluation shall not execute in Google Colab.

---

# 10. Checkpoint Selection Policy

Evaluation shall explicitly define the checkpoint source from the passed
validated bundle manifest. Selection policy is applied only after validation.

Supported policies include:

| Policy | Description |
|----------|-------------|
| Latest | Most recent checkpoint |
| Best | Highest validation performance |
| Explicit | User-specified checkpoint |
| All | Evaluate every checkpoint |

Checkpoint selection shall be recorded in experiment metadata.
Unvalidated, hash-mismatched, loose, or manually substituted checkpoints shall
be rejected before loading.

---

# 11. Deterministic Inference Policy

During evaluation:

- epsilon = 0.0 unless explicitly configured otherwise
- gradients disabled
- optimizer inactive
- replay memory unused
- target synchronization disabled

Inference shall be deterministic under identical seeds.

---

# 12. Primary Evaluation Metrics

The following metrics are mandatory.

| Metric | Identifier | Description |
|---------|------------|-------------|
| Mean Reward | MET-001 | Average reward across evaluation episodes |
| Median Reward | MET-002 | Median cumulative reward |
| Maximum Reward | MET-003 | Best observed episode reward |
| Minimum Reward | MET-004 | Worst observed episode reward |
| Reward Standard Deviation | MET-005 | Reward variability |
| Episode Length | MET-006 | Average episode duration |
| Success Rate | MET-007 | Percentage of successful landings |

These metrics shall appear in every evaluation report.

---

# 13. Training Metrics

Training metrics remain separate from evaluation metrics.

Mandatory training metrics include:

- episode reward
- moving average reward
- loss
- epsilon
- replay buffer occupancy
- training duration
- checkpoint count

Training metrics are consumed from persisted logs only.

---

# 14. Convergence Metrics

Convergence shall be evaluated using:

| Metric | Purpose |
|---------|---------|
| Convergence Episode | First sustained performance threshold |
| Reward Stability | Oscillation analysis |
| Reward Trend | Long-term improvement |
| Loss Trend | Optimization behavior |

Convergence thresholds shall be documented in experiment metadata.

---

# 15. Statistical Metrics

For every evaluation dataset compute:

- arithmetic mean
- median
- variance
- standard deviation
- minimum
- maximum
- sample count

No derived metric shall overwrite raw observations.

---

# 16. Comparative Metrics

Algorithm comparisons shall include:

- average reward difference
- convergence speed
- variance difference
- stability comparison
- success rate difference
- runtime difference

Comparisons shall use identical evaluation conditions.

---

# 17. Robustness Metrics

Robustness evaluation shall measure:

- performance degradation
- recovery behavior
- reward stability
- successful landing frequency
- variance under stochastic action replacement

These metrics directly support assignment-specific evaluation.

---

# 18. Runtime Metrics

Execution metrics shall include:

- training duration
- evaluation duration
- average episode duration
- checkpoint serialization time
- visualization generation time

Runtime measurements shall be collected independently from reward statistics.

---

# 19. Metric Collection Policy

Metrics shall be collected automatically.

Manual recording is prohibited.

Collection frequency:

| Metric Type | Frequency |
|-------------|-----------|
| Reward | Every episode |
| Loss | Every optimization step |
| Evaluation Reward | Every evaluation episode |
| Runtime | Continuous |
| Checkpoint Events | Every checkpoint |

---

# 20. Metric Persistence

All collected metrics shall be exported in machine-readable formats.

Mandatory formats:

```
CSV

JSON
```

Human-readable summaries shall be generated separately.

---

# 21. Evaluation Validation Rules

Before metrics are accepted, the evaluation engine shall verify:

- passed source-bundle validation receipt
- source bundle hash and per-file SHA-256 hashes
- checkpoint integrity
- configuration compatibility
- environment compatibility
- metric completeness
- metadata completeness
- absence of runtime failures

Invalid evaluations shall be rejected and clearly reported.

---

# 22. Statistical Evaluation Methodology

Evaluation statistics shall be calculated exclusively from persisted evaluation results.

The repository shall compute descriptive statistics for every evaluation dataset.

Mandatory statistics include:

| Statistic | Required |
|-----------|----------|
| Sample Count | Yes |
| Arithmetic Mean | Yes |
| Median | Yes |
| Minimum | Yes |
| Maximum | Yes |
| Variance | Yes |
| Standard Deviation | Yes |

The repository shall preserve raw observations.

Aggregated statistics shall never replace original evaluation records.

---

# 23. Evaluation Dataset Requirements

Evaluation datasets shall satisfy the following properties.

- complete
- reproducible
- independently generated
- immutable
- traceable

Every dataset shall include metadata linking it to:

- Experiment ID
- Run ID
- Configuration Hash
- Git Commit
- Random Seed

---

# 24. Comparative Evaluation Methodology

Comparisons shall be performed under identical evaluation conditions.

Comparison workflow:

```
Load DQN Results

↓

Load DDQN Results

↓

Validate Compatibility

↓

Aggregate Metrics

↓

Generate Comparison Tables

↓

Generate Comparison Figures

↓

Export Summary
```

Evaluation environments shall remain identical across compared algorithms.

---

# 25. Algorithm Comparison Dimensions

Mandatory comparison dimensions include:

| Identifier | Metric |
|------------|--------|
| CMP-001 | Mean Reward |
| CMP-002 | Median Reward |
| CMP-003 | Maximum Reward |
| CMP-004 | Reward Variance |
| CMP-005 | Success Rate |
| CMP-006 | Average Episode Length |
| CMP-007 | Convergence Episode |
| CMP-008 | Runtime Duration |

Every comparison shall include all mandatory dimensions.

---

# 26. Convergence Analysis

Convergence analysis shall evaluate:

- learning stability
- reward improvement
- sustained performance
- reward oscillation

Outputs include:

```
convergence_summary.csv

convergence_statistics.json

convergence_plot.png
```

---

# 27. Learning Stability Analysis

Learning stability evaluates consistency of learning.

Measurements include:

- reward variance
- moving average stability
- reward oscillation
- loss oscillation

Lower variance indicates more stable learning under equivalent experimental conditions.

---

# 28. Robustness Analysis

Robustness evaluation shall measure algorithm performance under assignment-specific stochastic action replacement.

Evaluation dimensions:

- reward degradation
- landing success
- convergence degradation
- variance increase

Robustness analysis directly supports FR-005.

---

# 29. Reward Shaping Analysis

Reward shaping shall be evaluated independently.

Evaluation shall quantify:

- landing bonus contribution
- fuel penalty influence
- cumulative reward changes
- learning behavior differences

Outputs:

```
reward_analysis.csv

reward_breakdown.json

reward_comparison_plot.png
```

---

# 30. Runtime Performance Analysis

The evaluation engine shall measure runtime characteristics.

Metrics include:

| Metric | Purpose |
|---------|---------|
| Training Duration | Training efficiency |
| Evaluation Duration | Evaluation efficiency |
| Average Episode Time | Runtime behavior |
| Checkpoint Save Time | Serialization performance |
| Visualization Time | Reporting overhead |

Runtime analysis shall remain independent of learning metrics.

---

# 31. Evaluation Artifact Validation

Every generated artifact shall undergo validation.

Validation checks include:

- file exists
- readable
- non-empty
- metadata complete
- Experiment ID present
- Run ID present
- source bundle hash present
- source validation receipt reference present

Corrupted artifacts shall be rejected.

---

# 32. Visualization Validation

Generated figures shall satisfy the following requirements.

Mandatory elements:

- title
- axis labels
- legend (where applicable)
- readable font
- deterministic styling

Validation shall confirm:

- image successfully generated
- expected dimensions
- supported export format
- artifact registration

---

# 33. Evaluation Quality Assurance

Evaluation quality assurance follows the sequence below.

```
Metric Validation

↓

Artifact Validation

↓

Visualization Validation

↓

Comparison Validation

↓

Repository Validation
```

Failure at any stage invalidates the evaluation.

---

# 34. Evaluation Failure Categories

Failures shall be classified.

| Category | Action |
|----------|--------|
| Missing/Failed Bundle Validation | Abort before checkpoint load |
| Missing Checkpoint | Abort evaluation |
| Invalid Metadata | Reject results |
| Configuration Mismatch | Abort comparison |
| Corrupted Artifact | Regenerate artifact |
| Missing Metrics | Reject evaluation |
| Runtime Failure | Preserve diagnostics |

Failures shall never be ignored.

---

# 35. Reproducibility Verification

Evaluation reproducibility shall verify:

- configuration hash
- repository revision
- random seed
- environment version
- package versions
- algorithm implementation

Equivalent evaluation conditions shall produce statistically equivalent outcomes.

---

# 36. Assignment Evidence Generation

The repository shall automatically generate evidence supporting assignment deliverables.

Evidence categories include:

| Evidence | Generated |
|----------|-----------|
| Reward Curves | Yes |
| Loss Curves | Yes |
| Evaluation Tables | Yes |
| Algorithm Comparison | Yes |
| Hyperparameter Summary | Yes |
| Experiment Metadata | Yes |

Evidence generation shall not require manual editing.

---

# 37. Report Asset Verification

Before report generation, verify the presence of:

```
Reward Plot

Loss Plot

Evaluation Plot

Comparison Plot

Metrics CSV

Evaluation JSON

Experiment Manifest

Configuration Snapshot
```

Missing assets invalidate report generation.

---

# 38. Evaluation Traceability

Every evaluation artifact shall trace to:

```
Requirement

↓

Experiment

↓

Training Run

↓

Evaluation

↓

Visualization

↓

Report Section
```

Example mapping:

| Experiment | Canonical condition | Evaluation |
|------------|---------------------|------------|
| EXP-001 | DQN original | EVAL-001 |
| EXP-002 | DQN modified | EVAL-002 |
| EXP-003 | DDQN original | EVAL-003 |
| EXP-004 | DDQN modified | EVAL-004 |

Environment compatibility, reward, fuel, landing-bonus, and action-replacement
correctness map to VERIFY-009 through VERIFY-012, not to experiment IDs.

---

# 39. Repository Acceptance Gates

Repository acceptance requires successful completion of all evaluation gates.

```
Four Colab Bundles Downloaded

↓

Four Local Bundle Validations Passed

↓

Cross-Run Fairness and Completeness Passed

↓

Local Evaluation Completed

↓

Metrics Validated

↓

Comparison Generated

↓

Figures Generated

↓

Artifacts Verified

↓

Documentation Updated

↓

Repository Accepted
```

Skipping gates is prohibited.

---

# 40. Evaluation Completion Criteria

Evaluation is complete when:

- evaluation ran locally
- source bundle validation passed before checkpoint load
- all required metrics are computed
- comparison tables generated
- visualization exported
- artifacts validated
- metadata verified
- experiment traceability established
- repository quality gates satisfied

---

# 41. Definition of Evaluation Done

Evaluation satisfies repository requirements when:

- each source is a locally validated bundle from EXP-001 through EXP-004
- deterministic evaluation completed
- descriptive statistics computed
- DQN and DDQN compared
- stochastic environment evaluated
- reward shaping analyzed
- required plots generated
- assignment evidence generated
- artifacts archived
- reproducibility verified
- evaluation documentation synchronized with repository outputs

---

# 42. AI Coding Agent Responsibilities

Evaluation-focused AI Coding Agents shall:

- execute evaluation without modifying training artifacts
- execute evaluation locally only
- reject a source before checkpoint loading unless its bundle validation passed
- validate checkpoint compatibility
- compute all mandatory metrics
- preserve raw evaluation data
- generate comparison artifacts
- verify reproducibility metadata
- reject incomplete evaluations
- maintain traceability between experiments, metrics, and report assets

---

# 43. Evaluation Governance Rules

The following governance policies are mandatory.

## GOV-EVAL-001

Evaluation shall consume complete, persisted, locally validated run bundles
only. Loose checkpoints are prohibited.

---

## GOV-EVAL-002

Evaluation shall never retrain models.

---

## GOV-EVAL-003

Evaluation scripts shall remain deterministic.

---

## GOV-EVAL-004

Every reported metric shall be traceable to raw observations.

---

## GOV-EVAL-005

Comparison reports shall only compare compatible experiments.

---

## GOV-EVAL-006

Generated evaluation artifacts shall never be edited manually.

---

## GOV-EVAL-007

Evaluation metadata shall remain synchronized with experiment metadata.

---

## GOV-EVAL-008

Repository acceptance requires successful completion of all evaluation quality gates.

---

## GOV-EVAL-009

Evaluation is local-only and shall not run in Google Colab.

---

## GOV-EVAL-010

The complete bundle shall pass schema, identity, configuration, safe-path, and
SHA-256 validation before checkpoint selection or deserialization.

---
