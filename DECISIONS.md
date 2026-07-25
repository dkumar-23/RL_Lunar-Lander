# Document Metadata

| Field | Value |
|--------|--------|
| Document ID | ADR-001 |
| Version | 1.0.0 |
| Status | Accepted |
| Purpose | Record the architectural decisions governing the implementation of the repository and provide authoritative rationale for every major engineering decision. |
| Scope | Repository-wide architectural decisions, implementation constraints, design rationale, alternatives considered, consequences, and requirement traceability |
| Audience | AI Coding Agents, Software Architects, ML Engineers, Teaching Assistants, Repository Maintainers |
| Dependencies | PRD.md, DESIGN.md, ARCHITECTURE.md, WORKFLOW.md |
| Related Documents | TASKS.md, EXPERIMENTS.md, EVALUATION.md |
| Revision History | v1.0.0 — Initial Architecture Decision Record |

---

# 1. Purpose

This document serves as the repository's Architecture Decision Record (ADR).

Every significant architectural decision shall be documented.

Each ADR shall capture:

- problem statement
- selected solution
- alternatives considered
- rationale
- implications
- traceability

Architectural decisions are immutable historical records.

Future architectural changes shall create new ADR entries rather than modifying historical records.

---

# 2. ADR Lifecycle

Every architectural decision follows the lifecycle below.

```
Problem Identified

↓

Alternatives Evaluated

↓

Decision Selected

↓

Implementation

↓

Verification

↓

Historical Record
```

---

# 3. ADR Status Definitions

| Status | Description |
|---------|-------------|
| Proposed | Under review |
| Accepted | Approved for implementation |
| Superseded | Replaced by newer ADR |
| Deprecated | No longer recommended |
| Rejected | Not adopted |

All ADRs in this document are currently **Accepted**.

---

# ADR-001 — Repository Organization

## Status

Accepted

---

## Context

The repository shall support:

- modular implementation
- AI Coding Agents
- reproducibility
- maintainability

Repository organization must prevent coupling between implementation, generated artifacts and documentation.

---

## Decision

Adopt a layered repository architecture.

```
configs/

src/

tests/

scripts/

experiments/

outputs/

reports/

docs/

assets/
```

Generated artifacts shall never reside inside source directories.

---

## Alternatives Considered

### Flat Repository

Rejected.

Reason:

Poor scalability.

---

### Feature-Based Mixed Layout

Rejected.

Reason:

Generated artifacts become mixed with implementation.

---

## Consequences

Advantages:

- maintainable
- deterministic
- AI-agent friendly
- easier testing

Trade-offs:

- additional directories
- stricter organization requirements

---

## Traceability

Requirements:

FR-001

NFR-001

Components:

COMP-001

Tasks:

TASK-001

---

# ADR-002 — Configuration Management

## Status

Accepted

---

## Context

Hyperparameters shall remain configurable.

Assignment experiments require repeatability.

---

## Decision

All runtime configuration shall originate from configuration files.

Implementation shall not hardcode:

- learning rate
- gamma
- replay capacity
- epsilon schedule
- target update interval
- stochastic probability

---

## Alternatives

Hardcoded constants.

Rejected.

Runtime CLI-only configuration.

Rejected.

---

## Consequences

Benefits:

- reproducibility
- easier experimentation
- experiment traceability

---

## Traceability

FR-002

TASK-003

---

# ADR-003 — Modified Environment

## Status

Accepted

---

## Context

The assignment requires modification of the LunarLander environment.

---

## Decision

Environment modifications shall remain isolated from reinforcement learning algorithms.

Components:

```
Environment

↓

Reward Modifier

↓

Action Failure Model
```

The agent shall observe only the modified environment interface.

---

## Alternatives

Embedding reward logic inside the agent.

Rejected.

Embedding stochastic logic inside DQN.

Rejected.

---

## Consequences

Benefits:

- separation of concerns
- reusable environment
- simplified testing

---

## Traceability

FR-003

FR-005

TASK-010

TASK-011

---

# ADR-004 — Replay Memory

## Status

Accepted

---

## Context

Experience replay is required for DQN and DDQN.

---

## Decision

Replay memory shall be implemented as an independent subsystem.

Responsibilities:

- insertion
- sampling
- capacity management

Replay memory shall not implement learning logic.

---

## Alternatives

Replay inside DQN.

Rejected.

---

## Consequences

Improved reuse between algorithms.

---

## Traceability

FR-007

TASK-018

---

# ADR-005 — Shared Agent Hierarchy

## Status

Accepted

---

## Context

DQN and Double DQN share significant functionality.

---

## Decision

Introduce BaseAgent.

```
BaseAgent

├── DQNAgent

└── DDQNAgent
```

Shared responsibilities include:

- checkpoint interface
- optimizer ownership
- epsilon scheduling
- target synchronization interface

---

## Alternatives

Duplicate implementations.

Rejected.

---

## Consequences

Lower maintenance cost.

Improved consistency.

---

## Traceability

TASK-020

TASK-021

TASK-022

---

# ADR-006 — Target Network Design

## Status

Accepted

---

## Context

Target network stabilization is required.

---

## Decision

Maintain independent online and target networks.

Synchronization frequency shall be configurable.

---

## Alternatives

Single-network learning.

Rejected.

Continuous synchronization.

Rejected.

---

## Consequences

Improved learning stability.

Supports DQN and DDQN.

---

## Traceability

FR-012

FR-013

TASK-024

---

# ADR-007 — Experiment Isolation

## Status

Accepted

---

## Context

Experiments shall be reproducible.

---

## Decision

Each experiment owns:

- configuration
- metadata
- checkpoints
- metrics
- plots
- evaluation

No experiment shares runtime artifacts.

---

## Alternatives

Shared output directories.

Rejected.

---

## Consequences

Improved reproducibility.

---

## Traceability

EXP-001

TASK-029

---

# ADR-008 — Evaluation Independence

## Status

Accepted

---

## Context

Evaluation shall not influence learning.

---

## Decision

Evaluation shall consume only persisted checkpoints.

Evaluation shall:

- disable gradients
- disable exploration
- avoid replay memory

---

## Alternatives

Evaluation during training.

Rejected.

---

## Consequences

Improved scientific validity.

---

## Traceability

EVAL-001

TASK-031

---

# ADR-009 — Visualization Pipeline

## Status

Accepted

---

## Context

Plots shall remain reproducible.

---

## Decision

Visualization shall consume persisted metrics only.

Pipeline:

```
Metrics

↓

Visualization

↓

Export
```

Visualization shall never access live training objects.

---

## Alternatives

Real-time plotting.

Rejected.

---

## Consequences

Deterministic figure generation.

---

## Traceability

TASK-035

TASK-036

---

# ADR-010 — Report Generation

## Status

Accepted

---

## Context

The assignment report must remain synchronized with repository outputs.

---

## Decision

Report generation shall consume repository artifacts only.

The report shall not manually recreate:

- figures
- tables
- evaluation metrics

---

## Alternatives

Manual report creation.

Rejected.

---

## Consequences

Consistent report generation.

Reduced transcription errors.

---

## Traceability

RPT-001

TASK-040

---

# ADR-011 — Testing Strategy

## Status

Accepted

---

## Context

Repository quality shall be continuously verified.

---

## Decision

Adopt a layered testing strategy.

```
Unit Tests

↓

Integration Tests

↓

Architecture Validation

↓

Requirement Coverage

↓

Repository Validation
```

---

## Alternatives

Integration testing only.

Rejected.

---

## Consequences

Earlier defect detection.

Higher implementation confidence.

---

## Traceability

TASK-041

TASK-042

TASK-043

---

# ADR-012 — Reproducibility Policy

## Status

Accepted

---

## Context

Research repositories require deterministic execution.

---

## Decision

Every experiment shall record:

- random seeds
- configuration hash
- Git commit
- software versions
- environment version

Execution shall initialize all random number generators before environment construction.

---

## Alternatives

Partial seed initialization.

Rejected.

---

## Consequences

Supports repeatable experiments.

Improves result traceability.

---

## Traceability

EXP-001

EVAL-001

TASK-006

---

# ADR-013 — Documentation as the Primary Source of Truth

## Status

Accepted

---

## Context

The repository is intended for implementation by AI Coding Agents.

Ambiguous or undocumented behavior increases implementation risk.

---

## Decision

Repository documentation shall be the authoritative implementation specification.

Implementation shall conform to documented:

- interfaces
- workflows
- repository structure
- requirements
- constraints

When conflicts occur, documentation shall be updated through a new ADR before implementation changes.

---

## Alternatives

Code-first documentation.

Rejected.

Minimal README-only documentation.

Rejected.

---

## Consequences

Improved consistency.

Lower ambiguity for AI Coding Agents.

Better maintainability.

---

## Traceability

README.md

AI_INSTRUCTIONS.md

AGENTS.md

WORKFLOW.md

---

# ADR-014 — Colab-Exclusive Full Training and Local Execution Boundary

## Status

Accepted

---

## Context

Full reinforcement learning runs are computationally expensive and can be started accidentally while performing repository verification on a local machine. The execution boundary must distinguish full experiments from bounded checks while preserving human control over external compute.

---

## Decision

Full Training shall execute only through the Colab Training Notebook in Google Colab.

The execution contract is:

- A human starts every Colab Full Training run.
- The notebook checks out and records the exact Git commit selected for the run before training begins.
- The Colab runtime records its Execution Platform and dependency versions.
- Training artifacts are persisted as a Training Artifact Bundle in Google Drive rather than relying on ephemeral Colab storage.
- Local execution is limited to Bounded Local Tests, One-Step Learning Validation, artifact validation, evaluation of Validated Checkpoints, and report generation.
- Automated coding agents and local validation commands shall not initiate or represent completion of Full Training.

---

## Alternatives Considered

### Permit Full Training Locally

Rejected.

Reason:

It weakens the execution boundary and creates a risk of accidental long-running or resource-intensive local jobs.

### Allow Automated Agents to Start Colab Training

Rejected.

Reason:

External compute execution requires an explicit human action and observable runtime selection.

### Use the Repository's Current Branch State Without Pinning a Commit

Rejected.

Reason:

Mutable branch state does not provide reproducible provenance.

---

## Consequences

Benefits:

- prevents accidental local Full Training
- makes the execution platform explicit
- preserves human control of Colab execution
- binds training evidence to an exact Git commit

Trade-offs:

- Full Training requires a human-started Colab session
- local verification cannot establish that a full experiment completed
- Colab interruptions must be handled through persisted Drive artifacts

---

## Traceability

NFR-002

EXP-001

WORKFLOW.md

RISKS.md

---

# ADR-015 — Training Artifact Contract, Validation, and Promotion

## Status

Accepted

---

## Context

Colab runtimes are interruptible and ephemeral. A checkpoint or notebook completion indicator alone does not prove that a reproducible training run completed or that its outputs are safe to evaluate and report.

---

## Decision

Every Full Training run shall write a self-contained Training Artifact Bundle to Google Drive. The bundle is the transfer contract between Colab training and local verification.

At minimum, the bundle shall contain:

- an experiment manifest and run identifier
- the exact Git commit used by the Colab Training Notebook
- configuration snapshot and random seeds
- Execution Platform, software, and dependency version metadata
- training status and completion metadata
- checkpoints produced by the run
- persisted training metrics and logs required by downstream evaluation
- an artifact inventory with integrity information for required files

Artifacts copied or synchronized from Google Drive are unvalidated by default. Local validation shall verify bundle completeness, provenance consistency, required-file integrity, configuration readability, and checkpoint loadability without Full Training.

Artifact Promotion shall occur only after local validation succeeds. Only a promoted checkpoint may be designated a Validated Checkpoint or used as evidence for evaluation, figures, tables, conclusions, or assignment completion. Partial, interrupted, inconsistent, or unvalidated bundles shall remain unpromoted and shall not support result claims.

---

## Alternatives Considered

### Treat Any Checkpoint as Valid Training Output

Rejected.

Reason:

A serialized file does not establish run completeness, provenance, compatibility, or loadability.

### Generate Reports Directly From Google Drive Artifacts

Rejected.

Reason:

It bypasses local validation and artifact promotion.

### Treat Successful Notebook Cell Execution as Experiment Completion

Rejected.

Reason:

Notebook state can survive partial execution and does not prove that the required artifact contract was satisfied.

---

## Consequences

Benefits:

- prevents partial or incompatible outputs from entering evaluation
- provides reproducible Colab provenance
- separates artifact creation from artifact acceptance
- prevents unsupported report claims

Trade-offs:

- Drive bundles require explicit metadata and inventory files
- downloaded artifacts require a local validation step
- failed validation delays evaluation and reporting until corrected

---

## Traceability

NFR-002

EXP-001

EVAL-001

RPT-001

RISKS.md

---

# ADR Traceability Matrix

| ADR | Primary Requirements | Primary Tasks |
|------|----------------------|---------------|
| ADR-001 | FR-001, NFR-001 | TASK-001 |
| ADR-002 | FR-002 | TASK-003 |
| ADR-003 | FR-003, FR-005 | TASK-010, TASK-011 |
| ADR-004 | FR-007 | TASK-018 |
| ADR-005 | FR-008, FR-009 | TASK-020–022 |
| ADR-006 | FR-012, FR-013 | TASK-024 |
| ADR-007 | EXP-001 | TASK-029 |
| ADR-008 | EVAL-001 | TASK-031 |
| ADR-009 | FR-014 | TASK-035 |
| ADR-010 | RPT-001 | TASK-040 |
| ADR-011 | NFR-004 | TASK-041–044 |
| ADR-012 | EXP-001, EVAL-001 | TASK-006 |
| ADR-013 | NFR-001 | Repository-wide |
| ADR-014 | NFR-002, EXP-001 | Repository-wide |
| ADR-015 | NFR-002, EXP-001, EVAL-001, RPT-001 | Repository-wide |

---

# Architecture Governance

Future architectural modifications shall:

1. Create a new ADR.
2. Reference superseded ADRs where applicable.
3. Document rationale and consequences.
4. Preserve historical decisions.
5. Update traceability mappings if affected.

Existing ADR entries shall not be edited to reflect new decisions; they remain historical records.

---

# Definition of Done

The Architecture Decision Record is complete when:

- every significant architectural decision has a documented ADR
- each ADR includes context, decision, alternatives, consequences, and traceability
- repository-wide architectural policies are represented
- AI Coding Agents can determine the rationale behind implementation choices without external clarification
- architectural history can evolve through additional ADRs without rewriting prior decisions

# End of DECISIONS.md
