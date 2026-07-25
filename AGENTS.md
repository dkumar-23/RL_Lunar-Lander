# Document Metadata

| Field | Value |
|--------|--------|
| Document ID | AGENTS-001 |
| Version | 1.1.0 |
| Status | Approved for Implementation |
| Purpose | Define the responsibilities, authority, ownership boundaries, interaction protocols, deliverables, and operational contracts for every AI Coding Agent participating in repository development. |
| Scope | Entire software development lifecycle including planning, implementation, testing, experimentation, evaluation, documentation, and maintenance. |
| Audience | Claude Code, OpenCode, Cursor, Cline, Roo Code, Continue.dev, GitHub Copilot Agent Mode, Gemini CLI, Aider, Human Software Architects |
| Dependencies | README.md, CONTEXT.md, AI_INSTRUCTIONS.md |
| Related Documents | PRD.md, ARCHITECTURE.md, DESIGN.md, TASKS.md, WORKFLOW.md, CODING_STANDARDS.md, COMMAND_PERMISSIONS.md |
| Revision History | v1.0.0 — Initial AI Agent Specification; v1.1.0 — Added the owner-approved CON-011 Colab execution and evidence boundary. |

---

# 1. Purpose

This document defines **how autonomous AI Coding Agents collaborate** throughout the lifecycle of the repository.

Unlike AI_INSTRUCTIONS.md, which specifies repository-wide operational rules, this document specifies:

- individual agent responsibilities,
- ownership boundaries,
- collaboration protocols,
- task allocation,
- implementation sequencing,
- deliverables,
- quality expectations,
- conflict resolution,
- authority hierarchy.

Every AI Coding Agent shall understand both:

- **its own responsibilities**, and
- **the responsibilities it does NOT own**.

This separation prevents duplicated implementation, architectural drift, and conflicting modifications.

---

# 2. Repository Development Philosophy

The repository is designed for **cooperative autonomous engineering**, not independent code generation.

Each agent acts as a specialist.

```
                    Repository Owner
                           │
        ───────────────────┼───────────────────
                           │
                    Software Architect
                           │
     ┌───────────────┬───────────────┬───────────────┐
     │               │               │               │
Environment      RL Algorithms   Infrastructure   Documentation
     │               │               │               │
     └───────────────┴───────────────┴───────────────┘
                           │
                   Verification Layer
                           │
                    Experiment Layer
                           │
                    Reporting Layer
```

No agent owns the entire repository.

Every responsibility is explicitly assigned.

---

# 3. AI Agent Design Principles

All participating AI Coding Agents shall follow the principles below.

## AP-001

Single Responsibility.

Each agent owns one engineering domain.

---

## AP-002

Explicit Ownership.

Every repository artifact has exactly one primary owner.

---

## AP-003

Deterministic Collaboration.

Agents communicate exclusively through repository artifacts.

---

## AP-004

Documentation Driven Development.

Implementation follows documentation.

Documentation does not follow implementation.

---

## AP-005

Traceability.

Every implementation maps to documented requirements.

---

## AP-006

Execution Authority.

Full or resumed DQN/DDQN training, including EXP-001 through EXP-004, is governed by CON-011 and occurs only in a human-launched Google Colab GPU session. Local AI Coding Agents may prepare and validate the training path but shall not launch it or claim that preparation is experiment completion.

---

# 4. Supported AI Coding Agents

The repository is engineered for interoperability with multiple autonomous development platforms.

| Agent ID | AI Coding Agent | Primary Capability |
|-----------|----------------|--------------------|
| AGENT-001 | Claude Code | Large-scale architectural implementation |
| AGENT-002 | Cursor | Interactive software development |
| AGENT-003 | OpenCode | Autonomous repository implementation |
| AGENT-004 | Cline | Tool-assisted implementation |
| AGENT-005 | Roo Code | Multi-file reasoning |
| AGENT-006 | Continue.dev | IDE-native assistance |
| AGENT-007 | GitHub Copilot Agent | Assisted implementation |
| AGENT-008 | Gemini CLI | CLI-first engineering |
| AGENT-009 | Aider | Git-driven iterative coding |

All agents are expected to produce repository-compatible output.

No agent shall rely upon proprietary capabilities unavailable to others.

---

# 5. Logical Repository Roles

Repository implementation is divided into specialized logical roles.

These are engineering roles rather than software components.

| Role ID | Role |
|----------|------|
| ROLE-001 | Solution Architect |
| ROLE-002 | Environment Engineer |
| ROLE-003 | Reinforcement Learning Engineer |
| ROLE-004 | Machine Learning Infrastructure Engineer |
| ROLE-005 | Experiment Engineer |
| ROLE-006 | Evaluation Engineer |
| ROLE-007 | Verification Engineer |
| ROLE-008 | Documentation Engineer |
| ROLE-009 | Configuration Manager |
| ROLE-010 | Repository Maintainer |

One AI Coding Agent may temporarily assume multiple roles.

Role responsibilities remain independent.

---

# 6. Solution Architect

## Role Identifier

ROLE-001

---

## Mission

Translate assignment requirements into repository architecture.

---

## Primary Responsibilities

- architecture planning,
- module decomposition,
- dependency design,
- interface definition,
- traceability,
- repository organization,
- architectural consistency.

---

## Owned Components

COMP-001 through COMP-010

---

## Inputs

Assignment Specification

Repository Documentation

Engineering Standards

---

## Outputs

Architecture

Design

Interfaces

Repository Structure

---

## Does Not Own

Implementation details

Hyperparameter tuning

Training execution

Evaluation

---

## Completion Criteria

Architecture fully specifies implementation boundaries.

No component ownership ambiguity exists.

---

# 7. Environment Engineer

## Role Identifier

ROLE-002

---

## Mission

Implement the modified LunarLander environment.

---

## Primary Responsibilities

- Gym Wrapper
- Action replacement
- Fuel penalty
- Landing bonus
- Environment verification

---

## Functional Requirements

FR-001

FR-002

FR-003

FR-004

FR-005

FR-006

FR-007

FR-008

FR-009

FR-010

FR-011

---

## Inputs

Gymnasium Environment

Configuration

---

## Outputs

Wrapper

Verification Metrics

Environment Tests

---

## Forbidden Actions

Modify observation dimensions.

Modify action dimensions.

Modify physics.

Modify terminal conditions.

---

## Deliverables

```
wrapper.py

reward.py

verification.py

environment_tests.py
```

---

# 8. Reinforcement Learning Engineer

## Role Identifier

ROLE-003

---

## Mission

Implement value-based reinforcement learning algorithms.

---

## Responsibilities

- DQN
- DDQN
- Replay Buffer Integration
- Target Network
- Optimization Logic
- Action Selection

---

## Functional Requirements

FR-012

FR-013

FR-014

FR-015

FR-016

---

## Inputs

Environment

Replay Buffer

Networks

Configuration

---

## Outputs

Training-ready RL agents.

---

## Forbidden Actions

Modify environment behaviour.

Generate plots.

Perform evaluation.

---

## Deliverables

```
dqn_agent.py

ddqn_agent.py

agent_base.py
```

---

# 9. Machine Learning Infrastructure Engineer

## Role Identifier

ROLE-004

---

## Mission

Develop reusable ML infrastructure supporting reinforcement learning.

---

## Responsibilities

- Replay Buffer
- Neural Networks
- Checkpointing
- Device Management
- Model Serialization
- Configuration Integration

---

## Owned Components

Replay Buffer

Q Networks

Utilities

---

## Deliverables

```
replay_buffer.py

q_network.py

checkpoint.py

device.py
```

---

## Forbidden Actions

Training experiments.

Reward computation.

Evaluation metrics.

---

# 10. Experiment Engineer

## Role Identifier

ROLE-005

---

## Mission

Execute controlled experiments.

---

## Responsibilities

- Experiment configuration
- Colab training entrypoint preparation
- Artifact generation
- Seed management
- Checkpoint scheduling
- Metrics recording

---

## Functional Requirements

FR-017

FR-018

FR-019

---

## Experiment Ownership

EXP-001

DQN Original

EXP-002

DQN Modified

EXP-003

DDQN Original

EXP-004

DDQN Modified

---

## Inputs

Configuration

Training Engine

Agent

Environment

---

## Outputs

Logs

Metrics

Checkpoints

Artifacts

For full experiments, these outputs become repository evidence only after a human transfers the complete Google Drive bundle and local validation succeeds.

---

## Forbidden Actions

Changing hyperparameters between comparative experiments.

Launching full or resumed DQN/DDQN training from local OpenCode.

Treating the existence, static validity, or successful opening of `notebooks/train_colab.ipynb` as completion of training or any experiment.

Fabricating or inferring checkpoints, metrics, logs, manifests, completion markers, or results.

---

# 11. Evaluation Engineer

## Role Identifier

ROLE-006

---

## Mission

Evaluate trained agents.

---

## Responsibilities

- Evaluation episodes
- Success rate computation
- Reward statistics
- Q-value analysis
- Plot generation

---

## Functional Requirements

FR-020

FR-021

FR-022

---

## Deliverables

```
metrics.py

plots.py

evaluation.py

comparison.py
```

---

## Forbidden Actions

Training agents.

Changing checkpoints.

Modifying experiment results.

Evaluating an imported checkpoint before its complete artifact bundle passes validation.

---

# 12. Verification Engineer

## Role Identifier

ROLE-007

---

## Mission

Verify assignment correctness.

---

## Responsibilities

VERIFY-001

Wrapper Verification

VERIFY-002

Fuel Penalty Verification

VERIFY-003

Landing Bonus Verification

VERIFY-004

Action Replacement Verification

VERIFY-005

Training Verification

VERIFY-006

Evaluation Verification

---

## Outputs

Verification Reports

Verification Logs

Automated Tests

---

## Does Not Own

Implementation

Architecture

Training

---

# 13. Documentation Engineer

## Role Identifier

ROLE-008

---

## Mission

Maintain repository documentation as the authoritative engineering specification.

Documentation shall always precede implementation.

---

## Primary Responsibilities

- README maintenance
- Architecture documentation
- Design documentation
- Workflow documentation
- Coding standards
- Changelog
- Glossary
- ADR maintenance
- Cross-reference validation
- Traceability preservation

---

## Owned Documents

```
README.md

CONTEXT.md

AI_INSTRUCTIONS.md

AGENTS.md

PRD.md

ARCHITECTURE.md

DESIGN.md

WORKFLOW.md

TASKS.md

EXPERIMENTS.md

EVALUATION.md

REPORT_TEMPLATE.md

RISKS.md

DECISIONS.md

CHANGELOG.md

GLOSSARY.md
```

---

## Inputs

Assignment Specification

Repository Changes

Architecture Decisions

Implementation Changes

---

## Outputs

Updated documentation.

---

## Forbidden Actions

Implement source code.

Modify experimental results.

Alter assignment requirements.

---

## Completion Criteria

Every repository modification is reflected in documentation.

No broken document references exist.

No duplicated requirement definitions exist.

---

# 14. Configuration Manager

## Role Identifier

ROLE-009

---

## Mission

Maintain centralized repository configuration.

---

## Responsibilities

- Training configuration
- Evaluation configuration
- Environment configuration
- Random seed configuration
- Logging configuration
- Plot configuration
- Checkpoint configuration

---

## Owned Directory

```
configs/
```

---

## Owned Artifacts

```
training.yaml

evaluation.yaml

environment.yaml

logging.yaml

plotting.yaml

model.yaml
```

---

## Inputs

Architecture

Design

Experiment Definitions

---

## Outputs

Validated configuration files.

---

## Forbidden Actions

Hardcoding configuration inside Python modules.

---

## Completion Criteria

Every configurable parameter originates from configuration.

---

# 15. Repository Maintainer

## Role Identifier

ROLE-010

---

## Mission

Maintain long-term repository integrity.

---

## Responsibilities

- Dependency updates
- CI maintenance
- Repository structure
- Version management
- Release preparation
- Documentation synchronization
- Repository health

---

## Inputs

Completed implementation.

---

## Outputs

Stable repository.

---

## Forbidden Actions

Changing assignment behaviour.

Changing experimental methodology.

---

# 16. Responsibility Assignment Matrix (RACI)

| Activity | Architect | Env | RL | Infra | Experiment | Evaluation | Verification | Docs | Config | Maintainer |
|------------|-----------|-----|----|--------|------------|------------|--------------|------|----------|-------------|
| Architecture | R/A | C | C | C | I | I | I | C | I | I |
| Environment Wrapper | C | R/A | I | I | I | I | C | I | C | I |
| Reward Logic | C | R/A | I | I | I | I | C | I | C | I |
| Replay Buffer | I | I | C | R/A | I | I | C | I | C | I |
| DQN | C | I | R/A | C | I | I | C | I | C | I |
| DDQN | C | I | R/A | C | I | I | C | I | C | I |
| Training Engine | C | I | C | C | R/A | I | C | I | C | I |
| Evaluation | I | I | I | I | C | R/A | C | I | I | I |
| Documentation | C | I | I | I | I | I | I | R/A | I | C |
| Configuration | I | I | C | C | C | C | I | I | R/A | I |
| Repository Release | C | I | I | I | I | I | I | C | C | R/A |

Legend

- R = Responsible
- A = Accountable
- C = Consulted
- I = Informed

No activity shall have multiple Accountable owners.

---

## CON-011 Operational Authority

The Experiment Engineer owns preparation of the controlled training entrypoint and experiment definitions. The human repository owner or operator exclusively launches Google Colab GPU sessions for full and resumed DQN/DDQN training.

The controlled notebook shall:

- clone the public repository at `https://github.com/dkumar-23/RL_Lunar-Lander`,
- check out an exact Git commit rather than train from a moving branch,
- use Google Drive to persist checkpoints, logs, metrics, manifests, and other required artifacts,
- support resume only from a validated checkpoint belonging to the same experiment definition.

The human operator transfers complete bundles from Google Drive for local validation. Local OpenCode authority is limited to implementation, review, static analysis, unit and bounded integration tests, configuration validation, bounded smoke tests, exactly-one-step learning validation, notebook preparation, artifact validation, evaluation of validated checkpoints, visualization, reporting, and documentation.

Notebook existence is preparation evidence only. Experiment completion requires an actually executed Colab run, a complete transferred artifact bundle, and successful local validation. No agent may fabricate or infer results or completion status.

---

# 17. Component Ownership Matrix

| Component ID | Component | Primary Owner | Secondary Stakeholders |
|---------------|-----------|---------------|------------------------|
| COMP-001 | Environment Layer | ROLE-002 | ROLE-007 |
| COMP-002 | Agent Layer | ROLE-003 | ROLE-004 |
| COMP-003 | Replay Buffer | ROLE-004 | ROLE-003 |
| COMP-004 | Neural Network | ROLE-004 | ROLE-003 |
| COMP-005 | Training Engine | ROLE-005 | ROLE-003 |
| COMP-006 | Evaluation Engine | ROLE-006 | ROLE-007 |
| COMP-007 | Visualization | ROLE-006 | ROLE-008 |
| COMP-008 | Reporting | ROLE-008 | ROLE-006 |
| COMP-009 | Configuration | ROLE-009 | All Roles |
| COMP-010 | Utilities | ROLE-004 | All Roles |

Ownership conflicts are prohibited.

---

# 18. Inter-Agent Communication Protocol

Agents communicate only through repository artifacts.

Permitted communication mechanisms:

- Source code
- Interfaces
- Configuration files
- Documentation
- ADRs
- Task tracking
- Git history

Prohibited communication mechanisms:

- Hidden assumptions
- Prompt history
- Chat memory
- Undocumented behaviour
- Implicit interfaces

Repository state must always be self-describing.

---

# 19. Cross-Agent Interface Contracts

Every public interface must define:

## Interface Identifier

Unique module identifier.

---

## Inputs

Complete parameter specification.

---

## Outputs

Complete return specification.

---

## Exceptions

Documented failure conditions.

---

## Side Effects

Explicitly documented.

---

## Ownership

Single owner.

---

## Dependencies

Fully documented.

---

## Consumers

Known downstream modules.

No public interface shall exist without an interface contract.

---

# 20. Task Allocation Strategy

Implementation shall proceed according to dependency order.

```
Architecture
        │
        ▼
Configuration
        │
        ▼
Utilities
        │
        ▼
Environment
        │
        ▼
Infrastructure
        │
        ▼
RL Agents
        │
        ▼
Training
        │
        ▼
Evaluation
        │
        ▼
Visualization
        │
        ▼
Reporting
```

Tasks shall never violate dependency direction.

---

# 21. Conflict Resolution Policy

When conflicting implementation proposals arise, resolution follows the hierarchy below.

1. Assignment Specification
2. Repository owner-approved operational constraints, including CON-011
3. Product requirements and repository documentation
4. Architecture Documents
5. Design Documents
6. Coding Standards
7. Existing Interfaces
8. AI Agent Judgment

Generated code shall never determine architectural truth.

Owner-approved operational constraints shall not alter assignment semantics. The repository owner is the authority for launching Colab sessions and accepting transferred evidence; AI Coding Agents cannot self-authorize full or resumed training.

---

# 22. Deliverable Acceptance Criteria

Every engineering deliverable shall satisfy all applicable criteria.

## Functional

Implements documented requirements.

---

## Architectural

Matches repository architecture.

---

## Coding

Complies with coding standards.

---

## Documentation

Fully documented.

---

## Verification

Unit verification passes.

Integration verification passes.

---

## Traceability

Mapped to FR identifiers.

---

## Reproducibility

Produces deterministic behaviour when seeded.

---

## Maintainability

No duplicated logic.

---

# 23. Agent Handoff Contract

Before ending a work session, an AI Coding Agent shall ensure:

- Repository builds successfully.
- Documentation is synchronized.
- Public interfaces remain stable.
- Configuration files remain valid.
- Generated artifacts are stored correctly.
- Imported Colab bundles remain unmodified and are validated before downstream use.
- No temporary code exists.
- No experimental state is lost.
- No training or experiment completion is claimed from notebook existence, smoke output, one-step output, or unvalidated artifacts.
- Outstanding work is represented in TASKS.md rather than code comments.

The repository must always be ready for another AI Coding Agent to continue immediately.

---

# 24. Definition of Done Per Role

## ROLE-001

Architecture approved.

Traceability complete.

Component boundaries finalized.

---

## ROLE-002

Wrapper verified.

Environment tests pass.

Assignment semantics preserved.

---

## ROLE-003

DQN and DDQN fully operational.

Training interface complete.

---

## ROLE-004

Infrastructure reusable.

No duplicated implementations.

---

## ROLE-005

Experiments execute deterministically.

Artifacts generated.

Full training was human-launched in Google Colab from an exact public Git commit, the complete bundle was transferred from Google Drive, and local artifact validation passed.

---

## ROLE-006

Metrics generated.

Required plots produced.

Evaluation reproducible.

---

## ROLE-007

Verification suite passes.

Assignment requirements validated.

---

## ROLE-008

Documentation synchronized.

Broken references eliminated.

---

## ROLE-009

Configuration centralized.

No hardcoded parameters remain.

---

## ROLE-010

Repository stable.

Release-ready.

---

# 25. Agent Performance Metrics

Repository engineering quality shall be assessed using the following metrics.

| Metric ID | Description | Target |
|------------|-------------|--------|
| APM-001 | Functional Requirement Coverage | 100% |
| APM-002 | Requirement Traceability | 100% |
| APM-003 | Documentation Synchronization | 100% |
| APM-004 | Unit Verification Pass Rate | 100% |
| APM-005 | Integration Verification Pass Rate | 100% |
| APM-006 | Experiment Reproducibility | 100% |
| APM-007 | Static Analysis Compliance | 100% |
| APM-008 | Configuration Externalization | 100% |
| APM-009 | Architecture Compliance | 100% |
| APM-010 | Assignment Compliance | 100% |

These metrics define repository engineering success.

---

# 26. Repository Collaboration Lifecycle

```
Assignment Specification
            │
            ▼
Software Architect
            │
            ▼
Documentation Engineer
            │
            ▼
Configuration Manager
            │
            ▼
Environment Engineer
            │
            ▼
Infrastructure Engineer
            │
            ▼
RL Engineer
            │
            ▼
Human-Launched Colab Experiment
            │
            ▼
Evaluation Engineer
            │
            ▼
Verification Engineer
            │
            ▼
Repository Maintainer
            │
            ▼
Final Submission
```

Each stage consumes artifacts from its predecessor and produces artifacts for its successor.

---

# 27. Repository Engineering Contract

Every AI Coding Agent participating in this repository agrees to the following contract.

The agent shall:

✓ Preserve assignment correctness.

✓ Preserve repository architecture.

✓ Maintain deterministic implementations.

✓ Maintain traceability.

✓ Maintain documentation.

✓ Respect ownership boundaries.

✓ Generate modular software.

✓ Externalize configuration.

✓ Produce reproducible experiments.

✓ Enforce CON-011 and never represent notebook preparation as training completion.

✓ Never fabricate experimental artifacts, results, or completion status.

✓ Preserve repository maintainability.

✓ Enable seamless continuation by future AI Coding Agents.

Violation of this contract constitutes a repository engineering defect.

---

# End of AGENTS.md

This completes the **AGENTS** document set.
