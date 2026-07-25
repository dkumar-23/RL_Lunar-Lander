# Document Metadata

| Field | Value |
|--------|--------|
| Document ID | WF-001 |
| Version | 1.1.0 |
| Status | Approved for Implementation |
| Purpose | Define the complete engineering workflow governing repository implementation, AI Coding Agent execution, Git workflow, experiment lifecycle, review process, quality gates, and artifact promotion. |
| Scope | End-to-end development workflow from repository initialization through final report generation |
| Audience | AI Coding Agents, Software Engineers, ML Engineers, Repository Maintainers, Teaching Assistants |
| Dependencies | PRD.md, ARCHITECTURE.md, DESIGN.md, CODING_STANDARDS.md |
| Related Documents | TASKS.md, EXPERIMENTS.md, EVALUATION.md, AGENTS.md |
| Revision History | v1.0.0 - Engineering Workflow Specification; v1.1.0 - Approved Colab-exclusive full-training workflow |

---

# 1. Workflow Objectives

The repository workflow exists to ensure:

- deterministic development
- reproducible experiments
- AI-agent collaboration
- traceable implementation
- maintainable source code
- verifiable assignment compliance

The workflow is normative.

AI Coding Agents shall follow this workflow exactly unless superseded by an approved Architecture Decision Record (ADR).

---

# 2. Engineering Workflow Principles

The engineering process adopts the following principles.

| ID | Principle |
|----|-----------|
| WF-001 | One responsibility per task |
| WF-002 | Small incremental commits |
| WF-003 | Build before optimize |
| WF-004 | Verify before merge |
| WF-005 | Experiments are immutable |
| WF-006 | Configuration over hardcoding |
| WF-007 | Documentation precedes implementation |
| WF-008 | Every artifact is reproducible |
| WF-009 | Full and resumed training are Colab-exclusive |
| WF-010 | Imported artifacts are untrusted until validated and promoted |

---

# 3. Repository Development Lifecycle

Development progresses through sequential phases.

```
Repository Initialization

↓

Documentation Complete

↓

Architecture Review

↓

Implementation

↓

Testing

↓

Colab Readiness

↓

Human-Started Colab Experiment Execution

↓

Drive Persistence

↓

Local Quarantine, Validation, and Promotion

↓

Local Evaluation

↓

Visualization

↓

Report Generation

↓

Submission
```

Skipping lifecycle stages is prohibited.

---

# 4. AI Coding Agent Workflow

Every AI Coding Agent shall execute work using the following lifecycle.

```
Read Documentation

↓

Identify Assigned Task

↓

Identify Dependencies

↓

Validate Preconditions

↓

Implement

↓

Self Verification

↓

Unit Testing

↓

Static Analysis

↓

Commit

↓

Await Next Task
```

Agents shall never begin implementation before understanding the assigned component.

---

# 5. AI Agent Operating Rules

Before modifying any source file, every AI Coding Agent shall:

1. Read README.md.

2. Read AI_INSTRUCTIONS.md.

3. Read AGENTS.md.

4. Read ARCHITECTURE.md.

5. Read DESIGN.md.

6. Read TASKS.md.

7. Read CODING_STANDARDS.md.

Partial understanding is prohibited.

---

# 6. Repository Initialization Workflow

Repository creation follows this sequence.

```
Initialize Git Repository

↓

Create Directory Structure

↓

Add Documentation

↓

Configure Tooling

↓

Configure Python Environment

↓

Install Dependencies

↓

Verify Repository

↓

Begin Development
```

No implementation shall begin before repository verification succeeds.

---

# 7. Feature Development Workflow

Every feature shall progress through the following stages.

```
Requirement

↓

Task Assignment

↓

Implementation

↓

Unit Test

↓

Integration Test

↓

Static Analysis

↓

Code Review

↓

Merge
```

Each stage must complete successfully before progressing.

---

# 8. Requirement-to-Implementation Workflow

Requirements are implemented individually.

```
Requirement

↓

Architecture Component

↓

Design Element

↓

Implementation Module

↓

Verification

↓

Requirement Closed
```

Traceability shall be maintained throughout.

---

# 9. Task Execution Workflow

Each task shall follow the lifecycle below.

```
READY

↓

IN_PROGRESS

↓

IMPLEMENTED

↓

LOCAL_VERIFIED

↓

TESTED

↓

REVIEWED

↓

COMPLETED
```

Tasks shall never bypass intermediate states.

For COMP-005 implementation tasks, `LOCAL_VERIFIED` means only that unit, integration, one-step, and hard-capped smoke checks passed. It does not mean an experiment completed.

Experiment-bearing work uses the following additional states:

```
CODE_COMPLETE

↓

LOCAL_VERIFIED

↓

COLAB_READY

↓

COLAB_RUNNING

↓

COLAB_RUN_COMPLETE

↓

ARTIFACTS_QUARANTINED

↓

ARTIFACTS_VALIDATED

↓

ARTIFACTS_PROMOTED

↓

EXPERIMENT_COMPLETED

↓

DELIVERABLES_COMPLETE
```

Notebook existence, successful notebook startup, or a local smoke result shall not advance work to `COLAB_RUN_COMPLETE` or `EXPERIMENT_COMPLETED`.

---

# 10. Git Branch Workflow

The repository adopts a simplified branching strategy suitable for assignment development.

```
main

│

├── feature/environment

├── feature/dqn

├── feature/ddqn

├── feature/evaluation

├── feature/visualization

└── feature/reporting
```

Each feature branch owns one implementation objective.

---

# 11. Branch Responsibilities

| Branch | Responsibility |
|----------|----------------|
| main | Stable repository |
| feature/environment | Environment implementation |
| feature/dqn | DQN implementation |
| feature/ddqn | DDQN implementation |
| feature/evaluation | Evaluation pipeline |
| feature/visualization | Plot generation |
| feature/reporting | Report asset generation |

No branch shall implement unrelated features.

---

# 12. Commit Workflow

Each commit shall represent one logical unit of work.

Recommended sequence:

```
Implement

↓

Verify

↓

Commit
```

Large multi-purpose commits are prohibited.

---

# 13. Commit Message Convention

Format:

```
TYPE(scope): summary
```

Examples:

```
feat(environment): implement stochastic action replacement

feat(agent): implement Double DQN target calculation

fix(training): correct target synchronization interval

refactor(memory): simplify replay sampling

docs(architecture): update dependency diagram

test(environment): add reward verification
```

---

# 14. Pull Request Workflow

Every pull request shall satisfy the following sequence.

```
Implementation Complete

↓

Local Verification

↓

Static Analysis

↓

Unit Tests

↓

Documentation Updated

↓

Review

↓

Merge
```

Unverified pull requests shall not be merged.

---

# 15. Code Review Workflow

Review order:

```
Architecture Compliance

↓

Requirement Compliance

↓

Design Compliance

↓

Coding Standards

↓

Testing

↓

Documentation
```

Architecture compliance has highest priority.

---

# 16. Development Phase Ownership

| Phase | Owner |
|---------|------|
| Requirements | PRD |
| Architecture | Architect |
| Design | Design Specification |
| Implementation | AI Coding Agent |
| Verification | Tests |
| Evaluation | Evaluation Engine |
| Reporting | Reporting Engine |

Ownership shall remain explicit.

---

# 17. Dependency Resolution Workflow

Dependencies shall be implemented in topological order.

```
Infrastructure

↓

Environment

↓

Models

↓

Replay Buffer

↓

Agents

↓

Training

↓

Local Training Verification

↓

Thin Colab Entry Point Validation

↓

Exact Commit and Configuration Freeze

↓

Human-Started Colab Full or Resumed Training

↓

Google Drive Persistence

↓

Local Artifact Quarantine

↓

COMP-009 Manifest, Hash, and Import Validation

↓

Artifact Promotion

↓

Local Evaluation

↓

Visualization

↓

Reporting
```

Reverse implementation order is prohibited.
Full and resumed training are never a local dependency-resolution step.

---

# 18. Definition of Ready

A task is READY only when:

- requirements identified
- architecture referenced
- dependencies implemented
- interfaces documented
- acceptance criteria defined
- verification strategy available

Otherwise implementation shall not begin.

---

# 19. Definition of Done

A development task is DONE only when:

- implementation complete
- coding standards satisfied
- tests pass
- documentation updated
- traceability maintained
- no known regressions introduced
- review completed

Implementation alone is insufficient.

For an experiment, DONE additionally requires a complete Drive-persisted bundle, successful local quarantine and COMP-009 validation, artifact promotion, and required local evaluation. A checkpoint without its validated manifest and promotion record is insufficient.

---

# 20. Workflow Invariants

## WF-INV-001

Documentation precedes implementation.

---

## WF-INV-002

Architecture governs implementation.

---

## WF-INV-003

Every implementation traces to at least one requirement.

---

## WF-INV-004

No feature is merged without verification.

---

## WF-INV-005

Generated artifacts are not edited manually.

---

## WF-INV-006

Experiment outputs remain immutable.

---

## WF-INV-007

Source code remains independent from generated artifacts.

---

## WF-INV-008

AI Coding Agents shall never infer undocumented requirements.

---

## WF-INV-009

Full and resumed training shall never execute locally.

---

## WF-INV-010

The human operator starts Colab; notebook existence or startup is not experiment completion.

---

## WF-INV-011

COMP-006, COMP-007, and COMP-008 shall not consume quarantined or unvalidated Colab artifacts.

---

# 21. Experiment Execution Workflow

Experiments are first-class engineering artifacts.

Every experiment shall be reproducible, isolated, traceable, and independently executable.

Execution lifecycle:

```
Experiment Selected

↓

Exact Git Commit Selected

↓

Configuration Loaded, Frozen, and Hashed

↓

Local One-Step and Hard-Capped Smoke Validation

↓

Colab Readiness Validated

↓

Human Starts Thin Colab Notebook

↓

Notebook Checks Out Exact Commit and Mounts Drive

↓

Full or Resumed Training Begins in Colab

↓

Metrics, Checkpoints, Manifest, and Hashes Persisted to Drive

↓

Human Transfers Complete Bundle to Local Quarantine

↓

COMP-009 Validates and Promotes Bundle

↓

COMP-006 Evaluates Promoted Checkpoint Locally

↓

COMP-007 and COMP-008 Execute Locally

↓

Experiment Archived
```

No experiment may reuse runtime artifacts from another experiment.

---

# 22. Experiment Preparation Workflow

Prior to execution, the following validations shall succeed.

```
Configuration Exists

↓

Configuration Schema Valid

↓

Random Seed Specified

↓

Exact Git Commit Recorded

↓

Configuration Hash Recorded

↓

Google Drive Run Directory Selected

↓

Drive Checkpoint Directory Empty or Versioned

↓

Dependencies Installed

↓

Environment Verified

↓

Thin Notebook Delegation Verified

↓

Colab Execution Approved for Human Start
```

Failure at any stage terminates execution.
Colab readiness does not imply that the run has started or completed.

---

# 23. Training Workflow

Training follows a deterministic orchestration sequence.

```
Validate ExecutionContext

↓

LOCAL_TEST?

├── Yes: Apply Non-Bypassable One-Step or Smoke Caps

└── No: Require Attested COLAB_FULL

↓

For COLAB_FULL, Verify Exact Commit and Writable Drive Target

↓

Initialize Components

↓

Reset Environment

↓

Begin Episode

↓

Observe State

↓

Agent Chooses Action

↓

Environment Executes Step

↓

Receive Transition

↓

Replay Buffer Updated

↓

Learning Step

↓

Metrics Updated

↓

Episode Ends?

↓

Checkpoint Trigger?

↓

Next Episode
```

All training metrics shall be written before checkpoint creation.
Local execution ends when the one-step or smoke cap is reached and can produce only local verification evidence. Full and resumed paths execute only in Colab and persist recoverable state directly to Google Drive.

---

# 24. Learning Update Workflow

Each optimization step follows the sequence below.

```
Replay Buffer

↓

Random Mini-Batch

↓

Forward Pass

↓

Target Calculation

↓

Loss Calculation

↓

Backpropagation

↓

Optimizer Step

↓

Target Synchronization (if scheduled)

↓

Loss Recorded
```

Learning updates shall never directly modify evaluation components.

---

# 25. DQN Workflow

The DQN implementation shall execute the following sequence.

```
Current State

↓

Online Network

↓

Q(s,a)

↓

Target Network

↓

max(Q')

↓

Bellman Target

↓

Loss

↓

Gradient Update
```

The Bellman target shall follow FR-012 requirements.

---

# 26. DDQN Workflow

Double DQN separates action selection from target evaluation.

```
Next State

↓

Online Network

↓

argmax(Q)

↓

Target Network

↓

Evaluate Selected Action

↓

Bellman Target

↓

Loss

↓

Optimizer
```

The online network shall not evaluate the target value selected by itself.

---

# 27. Evaluation Workflow

Evaluation executes independently of training.

```
Promoted Checkpoint Selected

↓

COMP-009 Promotion Record Verified

↓

Model Loaded

↓

Evaluation Episodes

↓

Metrics Aggregated

↓

Statistics Generated

↓

Evaluation Exported
```

Evaluation shall disable exploration unless explicitly configured otherwise.
Evaluation executes locally and fails closed if the checkpoint remains quarantined or any manifest, artifact hash, exact-commit, configuration-hash, or import check is absent or mismatched.

---

# 28. Visualization Workflow

Visualization begins only after successful evaluation.

```
Metrics Loaded

↓

Validation

↓

Reward Curves

↓

Loss Curves

↓

Evaluation Charts

↓

Export PNG

↓

Export PDF

↓

Export SVG
```

Visualization consumes persisted data only.

---

# 29. Report Generation Workflow

```
Collect Figures

↓

Collect Tables

↓

Collect Metrics

↓

Validate Assets

↓

Generate Report Resources

↓

Verify Completeness
```

Report generation shall not recompute experiment statistics.

---

# 30. Checkpoint Workflow

Checkpoint creation shall follow the sequence below.

```
Training State Frozen

↓

Model Serialized

↓

Optimizer Serialized

↓

Metadata Serialized

↓

Configuration Snapshot

↓

Integrity Check

↓

Atomic Rename

↓

Checkpoint Available
```

Incomplete checkpoints shall never be visible to downstream workflows.
During Colab full or resumed training, checkpoints shall be written atomically to the run-specific Google Drive destination and declared in the run manifest. A checkpoint alone is not a transferable or complete experiment bundle.

---

# 31. Checkpoint Resume Workflow

```
Locate Checkpoint

↓

Attest COLAB_FULL Runtime

↓

Integrity Validation

↓

Metadata Loaded

↓

Configuration Compared

↓

Weights Restored

↓

Optimizer Restored

↓

Replay State Restored (if supported)

↓

Resume Training
```

Configuration incompatibilities shall terminate recovery.
Resume training shall never execute locally. Local code may test checkpoint deserialization under hard caps but shall not transition into resumed training.

---

# 32. Artifact Promotion Workflow

Artifacts move through defined lifecycle stages.

```
Google Drive Bundle

↓

Human Transfer

↓

Local Quarantine

↓

Manifest Schema and Completeness Validation

↓

Per-File Cryptographic Hash Validation

↓

Exact Commit and Configuration Hash Validation

↓

Safe Import and Checkpoint Load Validation

├── Failure: Remain Quarantined

└── Success: Atomic Promotion

↓

Published for Local Downstream Use

↓

Archived
```

Artifacts shall never skip validation.
Promotion shall create an immutable validation record. A failed bundle shall not be edited in place; a corrected bundle enters quarantine as a new candidate.

---

# 33. Artifact Directory Workflow

Generated outputs shall follow:

```
outputs/

↓

metrics/

↓

evaluation/

↓

plots/

↓

tables/

↓

summary/
```

Every artifact shall include experiment metadata.

---

# 34. Logging Workflow

Logging proceeds continuously throughout runtime.

```
Initialize Logger

↓

Execution Events

↓

Warnings

↓

Metrics

↓

Errors

↓

Shutdown Summary
```

Logging failures shall not silently discard critical diagnostics.

---

# 35. Failure Recovery Workflow

Recoverable failures:

- interrupted execution
- checkpoint restoration
- temporary filesystem errors
- interrupted Colab runtime with a complete Drive-persisted recovery checkpoint

Workflow:

```
Failure Detected

↓

Classify Failure

↓

Recoverable?

↓

Yes

↓

Recover

↓

Verify State

↓

Resume
```

If recovery requires further training, `Resume` means a new human-started `COLAB_FULL` session at the exact compatible commit. It never means local resumed training.

If unrecoverable:

```
Log Failure

↓

Preserve Diagnostics

↓

Graceful Shutdown
```

---

# 36. Quality Gate Workflow

Every implementation passes through mandatory gates.

```
Implementation

↓

Formatting

↓

Linting

↓

Type Checking

↓

Unit Tests

↓

Integration Tests

↓

Documentation Validation

↓

Ready for Review
```

No gate may be bypassed.

---

# 37. Static Analysis Workflow

```
Source Code

↓

Import Validation

↓

Style Validation

↓

Architecture Rules

↓

Naming Rules

↓

Dependency Rules

↓

Pass
```

Architecture violations take precedence over style violations.

---

# 38. Continuous Verification Workflow

Verification occurs continuously during development.

```
Commit

↓

Static Analysis

↓

Unit Tests

↓

Integration Tests

↓

Repository Validation

↓

Merge Candidate
```

Verification is continuous rather than deferred.

---

# 39. Merge Workflow

```
Branch Ready

↓

Review

↓

Quality Gates

↓

Approval

↓

Merge

↓

Delete Feature Branch
```

Only reviewed branches may merge into `main`.

---

# 40. Release Workflow

Repository release sequence:

```
Implementation Frozen

↓

Colab Runs Completed and Persisted to Drive

↓

Artifacts Transferred, Validated, and Promoted

↓

Local Evaluation Complete

↓

Figures Generated

↓

Report Assets Verified

↓

Documentation Finalized

↓

Submission Package Created
```

---

# 41. Final Submission Workflow

The submission package shall contain only assignment-required deliverables.

```
Repository

↓

Verification

↓

Clean Generated Files

↓

Generate Required Artifacts

↓

Validate Submission

↓

Package

↓

Submit
```

Intermediate runtime files shall not be included unless required by the assignment specification.

---

# 42. Workflow Metrics

The workflow shall track:

| Metric | Description |
|---------|-------------|
| Build Success Rate | Successful executions |
| Test Pass Rate | Passing verification percentage |
| Experiment Success Rate | Completed experiment ratio |
| Checkpoint Recovery Success | Recovery reliability |
| Documentation Coverage | Implemented vs documented components |
| Requirement Coverage | Verified requirements implemented |

---

# 43. Engineering Governance Rules

The following governance policies are mandatory.

## GOV-001

Documentation changes precede architectural changes.

---

## GOV-002

Architectural changes require an ADR.

---

## GOV-003

Implementation shall not contradict documented interfaces.

---

## GOV-004

Generated artifacts remain immutable.

---

## GOV-005

Configuration changes shall be version controlled.

---

## GOV-006

Experiment definitions shall be reproducible.

---

## GOV-007

Evaluation scripts shall remain deterministic.

---

## GOV-008

Repository structure shall follow ARCHITECTURE.md.

---

# 44. Workflow Completion Criteria

The engineering workflow is considered complete when:

- all implementation tasks are complete
- all requirements trace to code
- all quality gates pass
- all full and resumed experiments execute successfully only in human-started Colab sessions
- each Colab run checks out its exact approved commit and persists a complete bundle to Google Drive
- transferred bundles pass COMP-009 manifest, hash, commit, configuration, and import validation before promotion
- evaluation metrics are generated
- plots are exported
- report assets are complete
- documentation reflects the implemented system
- repository is reproducible on a clean environment
- no notebook, local smoke result, quarantined bundle, or unvalidated checkpoint is counted as experiment completion

---

# 45. Workflow Definition of Done

The repository satisfies the workflow specification when:

- implementation follows documented task order
- runtime execution is deterministic
- experiments are reproducible
- local COMP-005 execution remains hard-capped and cannot perform full or resumed training
- the human-started Colab boundary and thin-notebook delegation are preserved
- COMP-006 consumes only promoted validated checkpoints
- COMP-007 and COMP-008 execute as local downstream stages
- evaluation is independent
- reporting consumes persisted artifacts only
- governance rules remain satisfied
- architectural integrity is preserved
- AI Coding Agents can execute the complete development lifecycle without additional clarification

---
