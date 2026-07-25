# Document Metadata

| Field | Value |
|--------|--------|
| Document ID | AIINST-001 |
| Version | 1.1.0 |
| Status | Approved for Implementation |
| Purpose | Define mandatory operational instructions, implementation rules, constraints, workflows, and engineering expectations for AI Coding Agents responsible for implementing the repository. |
| Scope | Entire software repository from initial implementation through experiment completion and report generation. |
| Audience | Claude Code, Cursor, OpenCode, Cline, Roo Code, Continue.dev, GitHub Copilot Agent Mode, Gemini CLI, Aider, Human Maintainers |
| Dependencies | README.md, CONTEXT.md |
| Related Documents | PRD.md, ARCHITECTURE.md, DESIGN.md, CODING_STANDARDS.md, WORKFLOW.md, TASKS.md, COMMAND_PERMISSIONS.md |
| Revision History | v1.0.0 — Initial AI Agent Operational Specification; v1.1.0 — Added the owner-approved CON-011 Colab execution and evidence boundary. |

---

# 1. Purpose

This document defines the **operating contract** for every AI Coding Agent interacting with this repository.

Unlike traditional documentation intended primarily for human developers, this document is specifically optimized for autonomous software engineering systems.

Every AI Coding Agent shall consider this document authoritative for:

- implementation workflow,
- engineering constraints,
- architectural compliance,
- repository modification rules,
- software quality expectations,
- experiment reproducibility,
- code generation standards.

This document is **normative**, not informative.

The instructions contained herein are mandatory unless explicitly overridden by the repository owner.

---

# 2. Repository Philosophy

The repository is engineered according to the following hierarchy of authority.

```
Assignment Specification
        │
        ▼
Repository Owner-Approved Operational Constraints
        │
        ▼
Repository Documentation
        │
        ▼
Architecture and Design
        │
        ▼
Implementation
```

AI agents shall never invert this hierarchy.

Implementation decisions shall never redefine architecture.

Architecture shall never redefine assignment requirements.

Owner-approved operational constraints govern where and by whom execution occurs when they do not change assignment semantics. CON-011 is such a constraint and is mandatory.

---

# 3. Primary Mission

The objective of every AI Coding Agent is **not merely to produce working code**.

The primary objective is to construct a repository satisfying all of the following simultaneously:

- Assignment correctness
- Engineering correctness
- Modularity
- Maintainability
- Reproducibility
- Traceability
- AI readability
- Software quality
- Research reproducibility

Producing executable code that violates these principles is considered an implementation failure.

---

# 4. AI Agent Responsibilities

Every AI Coding Agent assumes responsibility for the following engineering domains.

| Responsibility ID | Description |
|-------------------|-------------|
| AIR-001 | Read documentation before implementation |
| AIR-002 | Preserve assignment constraints |
| AIR-003 | Follow repository architecture |
| AIR-004 | Maintain modular implementation |
| AIR-005 | Maintain deterministic behaviour |
| AIR-006 | Generate documented source code only |
| AIR-007 | Maintain traceability |
| AIR-008 | Produce maintainable implementations |
| AIR-009 | Preserve reproducibility |
| AIR-010 | Never introduce undocumented behaviour |

---

# 5. Required Reading Order

Before modifying any source file, every AI Coding Agent shall process repository documentation in the following order.

```
README.md
        │
        ▼
CONTEXT.md
        │
        ▼
AI_INSTRUCTIONS.md
        │
        ▼
AGENTS.md
        │
        ▼
PRD.md
        │
        ▼
ARCHITECTURE.md
        │
        ▼
DESIGN.md
        │
        ▼
CODING_STANDARDS.md
        │
        ▼
WORKFLOW.md
        │
        ▼
TASKS.md
        │
        ▼
COMMAND_PERMISSIONS.md
        │
        ▼
EXPERIMENTS.md
        │
        ▼
EVALUATION.md
```

Implementation shall not begin before these documents have been consumed.

---

# 6. Assignment Compliance Rules

The assignment specification is the authoritative source of functional behaviour.

The AI agent shall implement exactly what is specified.

The AI agent shall never:

- simplify assignment requirements,
- reinterpret grading criteria,
- modify environment behaviour,
- alter mathematical definitions,
- invent additional functionality,
- remove required experimental comparisons.

Whenever repository engineering decisions extend beyond the assignment, those extensions shall remain orthogonal to assignment functionality.

---

## 6.1 CON-011 Local Execution Authority

Local OpenCode authority is limited to:

- implementation and review,
- static analysis,
- unit and bounded integration tests,
- configuration validation,
- bounded smoke tests,
- exactly-one-step learning validation,
- controlled Colab notebook preparation and static validation,
- artifact validation,
- evaluation of validated checkpoints,
- visualization, reporting, and documentation.

The human repository owner or operator exclusively launches Google Colab GPU sessions for full and resumed DQN/DDQN training. This authority split changes no assignment behavior, algorithm, hyperparameter, environment semantic, or evaluation definition.

---

# 7. Functional Requirement Compliance

The repository maintains a normalized requirement catalogue.

Functional requirements are identified by:

```
FR-001
FR-002
...
FR-022
```

Implementation shall reference these identifiers internally where appropriate.

The description of a functional requirement shall exist in exactly one document.

AI agents shall never duplicate requirement definitions.

---

# 8. Non-Functional Compliance

Every implementation shall satisfy the following repository objectives.

## NFR-001

Reproducibility.

Every experiment shall be executable from repository state alone.

---

## NFR-002

Maintainability.

Implementation shall favour readability over clever optimizations.

---

## NFR-003

Deterministic execution.

Random behaviour shall originate exclusively from documented random generators.

---

## NFR-004

Configuration-driven execution.

Magic numbers are prohibited.

---

## NFR-005

Traceability.

Every implementation artifact shall map to documented repository responsibilities.

---

# 9. AI Agent Workflow

Every development task shall follow the workflow below.

```
Read Documentation
        │
        ▼
Locate Requirements
        │
        ▼
Identify Responsible Component
        │
        ▼
Review Dependencies
        │
        ▼
Implement Module
        │
        ▼
Execute Unit Verification
        │
        ▼
Execute Integration Verification
        │
        ▼
Generate Artifacts
        │
        ▼
Update Documentation (if required)
```

Skipping workflow stages is prohibited.

---

# 10. Repository Ownership Model

Every directory has one owner.

Ownership shall never overlap.

| Directory | Owner |
|------------|------|
| configs | Configuration Layer |
| src/environment | Environment Layer |
| src/agents | Agent Layer |
| src/networks | Neural Network Layer |
| src/memory | Replay Buffer Layer |
| src/training | Training Layer |
| src/evaluation | Evaluation Layer |
| src/utils | Utility Layer |
| reports | Reporting Layer |
| plots | Visualization Layer |
| checkpoints | Model Lifecycle Layer |

AI agents shall not introduce responsibilities into directories that do not own them.

---

# 11. Single Responsibility Enforcement

Every module shall own one responsibility.

Examples:

Correct

```
environment/
    wrapper.py
```

Incorrect

```
environment/
    wrapper.py
    plotting.py
    report_generator.py
```

Correct

```
evaluation/
    metrics.py
```

Incorrect

```
evaluation/
    metrics.py
    neural_network.py
```

---

# 12. Mandatory Design Principles

Every generated implementation shall comply with the following engineering principles.

## DP-001

Single Responsibility Principle

---

## DP-002

Separation of Concerns

---

## DP-003

Dependency Direction

Higher-level modules shall never depend upon lower-level implementation details.

---

## DP-004

Configuration over Hardcoding

---

## DP-005

Explicit Interfaces

Hidden module coupling is prohibited.

---

## DP-006

Immutable Experiment Definitions

Training configuration shall never be modified dynamically during execution.

---

## DP-007

Deterministic Initialization

Random generators shall always be initialized through documented repository utilities.

---

# 13. Implementation Constraints

The following implementation constraints are mandatory.

## IC-001

Python implementation.

---

## IC-002

PyTorch backend.

---

## IC-003

Gymnasium environment interface.

---

## IC-004

Object-oriented architecture.

---

## IC-005

Type hints required.

---

## IC-006

Docstrings required.

---

## IC-007

Static analysis compliance.

---

## IC-008

PEP8 compliance.

---

## IC-009

No circular dependencies.

---

## IC-010

No duplicated business logic.

---

## IC-011

CON-011 Colab training boundary.

Full DQN/DDQN training, resumed training, and EXP-001 through EXP-004 shall execute exclusively through the controlled Google Colab training entrypoint in a human-launched GPU session. Local OpenCode shall not execute these workloads.

---

# 14. Repository Modification Rules

AI agents shall preserve repository organization.

Forbidden modifications include:

- relocating documented modules,
- renaming architectural components,
- merging unrelated responsibilities,
- embedding configuration values into source code,
- introducing undocumented directories,
- changing experiment outputs.

Every structural modification requires an accompanying architecture update.

---

# 15. Forbidden Actions

The following actions are explicitly prohibited.

## FA-001

Changing assignment semantics.

---

## FA-002

Changing reward equations beyond specification.

---

## FA-003

Changing stochastic failure probability.

---

## FA-004

Modifying observation dimensions.

---

## FA-005

Modifying action dimensions.

---

## FA-006

Changing termination behaviour.

---

## FA-007

Embedding hyperparameters directly into source code.

---

## FA-008

Using undocumented third-party libraries.

---

## FA-009

Removing logging.

---

## FA-010

Introducing hidden state.

---

## FA-011

Executing full or resumed DQN/DDQN training, launching EXP-001 through EXP-004, or executing `notebooks/train_colab.ipynb` from local OpenCode.

---

## FA-012

Using notebook existence, bounded smoke output, exactly-one-step output, or an unvalidated imported artifact as evidence of training or experiment completion.

---

## FA-013

Fabricating checkpoints, metrics, logs, manifests, completion markers, plots, report findings, or any other experimental result.

---

# 16. Completion Criteria

An implementation task is complete only if all of the following conditions hold.

- Functional requirements implemented.
- Unit verification passes.
- Integration verification passes.
- Type checking passes.
- Linting passes.
- Documentation remains valid.
- No architectural violations introduced.
- Repository traceability preserved.

---

# 17. Autonomous Development Lifecycle

Every AI Coding Agent shall perform work using a disciplined engineering lifecycle.

```
Repository Initialization
            │
            ▼
Read Documentation
            │
            ▼
Understand Architecture
            │
            ▼
Map Requirements
            │
            ▼
Review Existing Source Code
            │
            ▼
Determine Dependencies
            │
            ▼
Implement Smallest Independent Component
            │
            ▼
Static Verification
            │
            ▼
Runtime Verification
            │
            ▼
Integration Verification
            │
            ▼
Artifact Generation
            │
            ▼
Repository Validation
```

No stage may be skipped unless explicitly instructed by the repository owner.

---

# 18. Engineering Decision Hierarchy

Whenever conflicting implementation choices exist, AI agents shall resolve them using the following priority.

| Priority | Authority |
|-----------|-----------|
| 1 | Assignment Specification |
| 2 | Repository owner-approved operational constraints, including CON-011 |
| 3 | Product requirements and repository documentation |
| 4 | Architecture |
| 5 | Design Specification |
| 6 | Coding Standards |
| 7 | Existing Repository Code |
| 8 | AI Agent Judgment |

Lower-priority decisions shall never override higher-priority decisions.

---

# 19. Dependency Resolution Policy

Before implementing any component, AI agents shall identify every dependency.

Each dependency shall be classified.

| Dependency Type | Description |
|-----------------|-------------|
| Internal | Source modules within repository |
| External | Python packages |
| Runtime | Environment resources |
| Configuration | YAML/JSON configuration |
| Experimental | Checkpoints, datasets |
| Documentation | Design references |

Implementation shall begin only after dependencies are understood.

---

# 20. Component Development Order

Components shall be implemented in dependency order.

```
Configuration
        │
        ▼
Utility Modules
        │
        ▼
Environment Wrapper
        │
        ▼
Replay Buffer
        │
        ▼
Neural Networks
        │
        ▼
Agent Classes
        │
        ▼
Training Engine
        │
        ▼
Evaluation Engine
        │
        ▼
Visualization
        │
        ▼
Report Generation
```

Reverse dependency implementation is prohibited.

---

# 21. Component Completion Contract

Every repository component must satisfy the following completion contract.

## Inputs

Clearly defined.

## Outputs

Clearly documented.

## Dependencies

Fully identified.

## Public Interface

Stable.

## Internal State

Encapsulated.

## Configuration

Externalized.

## Tests

Passing.

## Documentation

Current.

Failure to satisfy any item renders the component incomplete.

---

# 22. Experiment Execution Policy

Experiments constitute first-class repository artifacts.

Each experiment shall be reproducible.

Each experiment shall possess:

- experiment identifier,
- configuration snapshot,
- random seed,
- model version,
- source commit,
- generated metrics,
- generated plots,
- generated checkpoints,
- execution logs.

Experiments are immutable after completion.

Under CON-011, the controlled entrypoint for full and resumed DQN/DDQN training is `notebooks/train_colab.ipynb`. A human operator shall launch the Google Colab GPU session. The notebook shall clone `https://github.com/dkumar-23/RL_Lunar-Lander` and check out the exact public Git commit recorded for the run; training from an unresolved branch tip is prohibited.

Google Drive shall persist the complete run bundle, including checkpoints, logs, metrics, configuration, metadata, and manifests required by repository policy. The human operator transfers the complete bundle to the repository's documented incoming location. Local OpenCode may validate the bundle and may evaluate checkpoints only after validation passes.

Creating, opening, or statically validating the notebook establishes entrypoint readiness only. It does not establish training completion, experiment completion, or the existence of results.

---

# 23. Random Seed Policy

All stochastic behaviour shall originate from a centralized seed initialization utility.

The following generators shall be synchronized.

- Python random
- NumPy
- PyTorch CPU
- PyTorch CUDA (future compatibility)
- Gymnasium Environment

No module may independently initialize random generators.

---

# 24. Configuration Policy

Every configurable value shall originate from configuration files.

Examples include:

Training

- Learning rate
- Batch size
- Gamma
- Replay capacity
- Target update interval

Environment

- Failure probability
- Fuel penalty
- Landing bonus

Evaluation

- Validation episodes
- Moving average window
- Plot interval

Visualization

- Figure size
- Output format
- DPI

Logging

- Save frequency
- Checkpoint interval

Hardcoded configuration values are prohibited.

---

# 25. Source Code Generation Policy

AI agents shall generate production-quality Python.

Generated source code shall include:

- type hints,
- docstrings,
- meaningful identifiers,
- logical decomposition,
- deterministic behaviour,
- exception handling,
- descriptive comments where algorithmically valuable.

Source code shall not include:

- placeholder functions,
- commented-out logic,
- dead code,
- unused imports,
- duplicated implementations.

---

# 26. Documentation Synchronization Rules

Documentation and implementation must remain synchronized.

Whenever implementation changes:

Documentation requiring review includes:

- Architecture
- Design
- Tasks
- Workflow
- Evaluation
- Decisions
- Changelog

Repository documentation is considered part of the software product.

---

# 27. Error Handling Policy

Every public interface shall implement explicit failure behaviour.

Error handling shall satisfy:

- deterministic,
- descriptive,
- recoverable where appropriate,
- logged,
- documented.

Silent failures are prohibited.

Broad exception handling without justification is prohibited.

---

# 28. Logging Policy

Logging is mandatory.

Logging shall support:

Training

- episode number,
- reward,
- epsilon,
- loss,
- learning rate.

Evaluation

- landing success,
- average reward,
- average Q-value.

Environment Verification

- attempted thrusters,
- failed thrusters,
- replacement ratio,
- fuel penalty count,
- landing bonus count.

Checkpointing

- save time,
- checkpoint identifier,
- configuration hash.

---

# 29. Artifact Lifecycle Policy

Generated artifacts shall follow deterministic storage rules.

```
Human-Launched Colab Training
     │
     ▼
Google Drive Persistence
     │
     ▼
Human Transfer of Complete Bundle
     │
     ▼
Local Artifact Validation
     │
     ▼
Validated Checkpoint Evaluation
     │
     ▼
Metrics and Plots
     │
     ▼
Assignment Report
```

Artifacts shall never overwrite previous experiment outputs unless explicitly configured.

Imported bundle payloads shall not be modified during local validation. Failed or incomplete bundles are not experiment evidence and shall not be promoted.

---

# 30. Model Lifecycle Policy

Every trained model progresses through the following lifecycle.

```
Initialization
        │
        ▼
Training
        │
        ▼
Checkpoint
        │
        ▼
Evaluation
        │
        ▼
Selection
        │
        ▼
Final Artifact
```

Every lifecycle transition shall be logged.

---

# 31. Checkpoint Policy

Checkpoint generation shall be deterministic.

Checkpoint metadata shall include:

- timestamp,
- experiment identifier,
- algorithm,
- environment,
- episode,
- optimizer state,
- scheduler state (if applicable),
- replay buffer state (optional),
- configuration hash,
- random seed.

---

# 32. Plot Generation Policy

Every required assignment plot shall originate from stored metrics rather than live visualization.

Plots shall be reproducible.

Raw metric data shall remain available after plot generation.

Plot generation scripts shall not retrain models.

---

# 33. Verification Strategy

Verification shall occur at multiple levels.

## Level 1

Static verification.

Examples:

- linting,
- formatting,
- type checking.

---

## Level 2

Component verification.

Examples:

- replay buffer,
- wrapper,
- Q-network.

---

## Level 3

Integration verification.

Examples:

- training loop,
- evaluation loop.

---

## Level 4

Assignment verification.

Examples:

- stochastic failure rate,
- fuel penalty,
- landing bonus,
- required plots.

---

# 34. Autonomous Decision Boundaries

AI agents may autonomously decide:

- helper function decomposition,
- internal class organization,
- file-level implementation details,
- local optimizations,
- variable names.

AI agents shall NOT autonomously decide:

- assignment semantics,
- reward equations,
- stochastic probabilities,
- architecture restructuring,
- algorithm substitution,
- evaluation methodology.

These require explicit repository-owner approval.

---

# 35. Code Review Checklist

Before considering a task complete, every AI agent shall verify:

✓ Functional requirements satisfied

✓ Assignment constraints preserved

✓ Documentation remains correct

✓ No duplicated logic

✓ Modular implementation

✓ Configuration externalized

✓ Deterministic execution

✓ Logging implemented

✓ Exceptions handled

✓ Tests pass

✓ Formatting correct

✓ Public interfaces documented

✓ Repository architecture preserved

---

# 36. Repository Quality Gates

Every pull request or implementation batch shall satisfy the following gates.

| Gate | Requirement |
|------|-------------|
| QG-001 | Functional correctness |
| QG-002 | Architectural compliance |
| QG-003 | Documentation compliance |
| QG-004 | Static analysis passes |
| QG-005 | Unit verification passes |
| QG-006 | Integration verification passes |
| QG-007 | Experiment reproducibility confirmed |
| QG-008 | Artifact generation verified |
| QG-009 | Assignment requirements preserved |
| QG-010 | Traceability maintained |
| QG-011 | CON-011 execution boundary preserved |
| QG-012 | Colab artifact bundle validated before evaluation or reporting |

Failure of any quality gate blocks repository integration.

---

# 37. AI Agent Definition of Done

An AI Coding Agent has completed its responsibility only when all of the following conditions hold.

1. Assigned functional requirements are fully implemented.

2. No architectural violations exist.

3. Repository documentation remains synchronized.

4. All dependent modules continue functioning.

5. Verification passes.

6. Generated artifacts conform to repository policy.

7. Code quality satisfies coding standards.

8. Implementation introduces no undocumented behaviour.

9. Assignment compliance remains intact.

10. Another AI Coding Agent can continue implementation without requiring clarification.

---

# 38. Multi-Agent Collaboration Philosophy

This repository is intentionally designed for collaborative autonomous software engineering.

Multiple AI Coding Agents may contribute sequentially or concurrently.

Every AI agent shall assume:

- another agent has previously worked on the repository,
- another agent will continue work later,
- repository consistency is more important than local optimization.

Therefore:

No implementation shall depend upon hidden conversational context.

Everything required for continuation must exist inside the repository.

---

# 39. Repository Communication Protocol

AI agents communicate exclusively through repository artifacts.

Permitted communication channels:

- Documentation
- Source Code
- Configuration Files
- Commit Messages
- ADR Documents
- Task Status
- Experiment Metadata

Forbidden communication mechanisms:

- Hidden assumptions
- Memory of previous prompts
- Implicit design decisions
- Undocumented shortcuts
- Temporary notes
- External conversations

---

# 40. AI-to-AI Handoff Protocol

Every implementation must leave the repository in a state that enables another autonomous AI agent to continue immediately.

A successful handoff guarantees:

- all implemented functionality is documented,
- interfaces are stable,
- configuration files are complete,
- generated artifacts are stored correctly,
- unfinished work is represented through repository task management rather than code comments.

No AI agent shall require prompt history to understand repository state.

---

# 41. Repository Navigation Rules

Every AI agent shall treat the repository as a structured software system.

Navigation order:

```
Repository Root
        │
        ▼
Documentation
        │
        ▼
Architecture
        │
        ▼
Source Code
        │
        ▼
Configuration
        │
        ▼
Experiments
        │
        ▼
Artifacts
```

Navigation shall never begin inside implementation directories.

Architecture always precedes implementation.

---

# 42. Branch Strategy

Recommended Git workflow:

```
main
 │
 ├─────────────── release/*
 │
 ├─────────────── feature/*
 │
 ├─────────────── experiment/*
 │
 ├─────────────── hotfix/*
 │
 └─────────────── documentation/*
```

Branch purposes:

| Branch | Purpose |
|---------|---------|
| main | Stable implementation |
| feature | New functionality |
| experiment | Experimental work |
| documentation | Documentation updates |
| hotfix | Critical fixes |
| release | Submission preparation |

AI agents shall not commit experimental work directly into `main`.

---

# 43. Commit Message Policy

Every commit shall describe engineering intent.

Recommended format:

```
<type>: <summary>

Affected Components:
Requirements:
Verification:
Artifacts:
```

Example:

```
feat: implement stochastic environment wrapper

Affected Components:
Environment Layer

Requirements:
FR-001
FR-004
FR-005
FR-006

Verification:
VERIFY-001

Artifacts:
None
```

Meaningful commit history is considered part of repository documentation.

---

# 44. File Ownership Matrix

Each source file has one logical owner.

| Layer | Owner |
|---------|--------|
| Environment | Environment Team |
| Replay Buffer | Memory Layer |
| Networks | Neural Network Layer |
| Agents | RL Algorithm Layer |
| Training | Training Engine |
| Evaluation | Evaluation Engine |
| Visualization | Plot Generation Layer |
| Reporting | Reporting Layer |
| Utilities | Shared Infrastructure |
| Configuration | Configuration Layer |

Cross-layer ownership is prohibited.

---

# 45. Prompt Engineering Guidelines

AI Coding Agents shall interpret prompts according to repository authority.

When implementing functionality:

Priority order:

1. Assignment Specification
2. Repository Documentation
3. Architecture
4. Existing Interfaces
5. User Prompt

If a prompt conflicts with documented architecture, the conflict shall be reported before implementation.

AI agents shall never silently violate repository documentation.

---

# 46. Source Code Modification Policy

Before modifying any file:

The AI agent shall determine:

- file ownership,
- dependent modules,
- public interfaces,
- downstream consumers,
- test impact,
- documentation impact.

Only then may modifications begin.

---

# 47. Refactoring Policy

Refactoring is permitted only if:

- behaviour remains identical,
- requirements remain satisfied,
- interfaces remain compatible,
- documentation remains synchronized,
- verification continues passing.

Refactoring shall never introduce assignment risk.

---

# 48. Anti-Pattern Catalogue

The following implementation patterns are prohibited.

## AP-001

God Classes

One class performing multiple unrelated responsibilities.

---

## AP-002

Hidden Configuration

Magic constants embedded inside algorithms.

---

## AP-003

Duplicated Logic

Identical implementations across modules.

---

## AP-004

Circular Imports

Modules depending recursively upon one another.

---

## AP-005

Hidden Side Effects

Functions modifying unrelated global state.

---

## AP-006

Mixed Responsibilities

Training code performing evaluation.

Evaluation code performing plotting.

Plotting code modifying metrics.

---

## AP-007

Repository Leakage

Generated artifacts inside source directories.

---

## AP-008

Assignment Drift

Engineering improvements modifying assignment behaviour.

---

# 49. Reinforcement Learning Engineering Constraints

The repository shall maintain strict experimental fairness.

The following experimental variables must remain identical between DQN and DDQN experiments.

- Random Seed
- Replay Buffer
- Optimizer
- Learning Rate
- Network Architecture
- Exploration Schedule
- Batch Size
- Discount Factor
- Training Episodes
- Evaluation Frequency

Only target-Q computation may differ.

This preserves assignment validity.

---

# 50. Experiment Reproducibility Guarantees

Every completed experiment shall be reproducible using only repository contents.

Required reproducibility artifacts:

- configuration snapshot,
- random seed,
- dependency versions,
- checkpoint,
- metrics,
- plots,
- logs,
- experiment identifier,
- algorithm identifier,
- environment identifier.
- exact public Git commit.
- Colab runtime and dependency metadata.
- complete transferred and validated artifact bundle.

No experiment shall depend upon undocumented runtime state.

The clone source is `https://github.com/dkumar-23/RL_Lunar-Lander`. Google Drive is the persistence boundary during Colab execution, not an undocumented source of truth; the complete bundle must be transferred and validated locally.

---

# 51. Documentation Evolution Policy

Documentation evolves alongside implementation.

Whenever implementation introduces:

- new component,
- new interface,
- architectural change,
- configuration option,
- evaluation metric,

the corresponding document shall be updated before task completion.

Documentation lag is considered a repository defect.

---

# 52. Repository Maintenance Policy

The repository shall remain maintainable after assignment submission.

Maintenance objectives:

- dependency updates,
- bug fixes,
- documentation improvements,
- architecture preservation,
- experiment reproducibility.

Maintenance shall never invalidate historical experiment results.

---

# 53. Extension Policy

Future repository extensions shall preserve existing architecture.

Potential future extensions include:

- Prioritized Replay
- Rainbow DQN
- Dueling Networks
- Noisy Networks
- Distributional RL
- Multi-step Learning
- Continuous Control
- Additional Gymnasium Environments

Future work shall be implemented as new modules.

Existing modules shall not be rewritten unless required.

---

# 54. Repository Governance

Repository governance follows the following hierarchy.

```
Assignment Specification
        │
        ▼
Repository Owner
        │
        ▼
Owner-Approved Constraints and Product Requirements
        │
        ▼
Architecture Documents
        │
        ▼
AI Coding Agents
        │
        ▼
Generated Source Code and Generated Results
```

Generated source code possesses the lowest authority.

Documentation always supersedes implementation.

---

# 55. Long-Term Repository Vision

Although developed to satisfy an academic assignment, the repository shall remain suitable as:

- a reinforcement learning reference implementation,
- a teaching resource,
- an experimentation platform,
- a benchmark repository,
- a software engineering portfolio project.

Engineering quality shall therefore exceed minimum assignment expectations without altering assignment semantics.

---

# 56. Final Operational Contract

Every AI Coding Agent interacting with this repository agrees to the following contract.

The AI agent shall:

✓ Read repository documentation before implementation.

✓ Preserve assignment requirements.

✓ Preserve repository architecture.

✓ Maintain traceability.

✓ Maintain reproducibility.

✓ Maintain deterministic behaviour.

✓ Generate maintainable code.

✓ Respect module ownership.

✓ Externalize configuration.

✓ Produce verifiable implementations.

✓ Preserve documentation consistency.

✓ Generate reproducible experiment artifacts.

✓ Restrict full and resumed DQN/DDQN training to human-launched Google Colab under CON-011.

✓ Treat notebook preparation as readiness, never as training completion.

✓ Never fabricate experimental results or completion status.

✓ Enable seamless continuation by future AI agents.

Failure to satisfy any of the above constitutes a violation of repository engineering standards.

---

# 57. AI Agent Exit Checklist

Before terminating an implementation session, every AI Coding Agent shall verify:

## Documentation

- [ ] Documentation synchronized
- [ ] No undocumented behaviour introduced
- [ ] Traceability preserved

## Source Code

- [ ] Functional requirements implemented
- [ ] Coding standards satisfied
- [ ] Type hints complete
- [ ] Docstrings complete

## Repository

- [ ] Architecture preserved
- [ ] Configuration externalized
- [ ] No temporary files
- [ ] No debug code

## Experiments

- [ ] If full training was performed, it was human-launched in Google Colab from the recorded exact public Git commit
- [ ] Complete Google Drive bundle transferred by a human
- [ ] Imported artifact validation passed before evaluation
- [ ] Configuration and seed stored
- [ ] Metrics, logs, manifests, and checkpoints present and valid
- [ ] No completion claim relies on notebook existence, smoke output, or one-step output
- [ ] No result or status was fabricated

## Quality

- [ ] Static analysis passes
- [ ] Unit verification passes
- [ ] Integration verification passes
- [ ] Assignment compliance maintained

Completion of this checklist signifies that the repository is ready for continued development by another autonomous AI Coding Agent without requiring additional clarification.

---

# End of AI_INSTRUCTIONS.md
