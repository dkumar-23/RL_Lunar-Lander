# Document Metadata

| Field | Value |
|--------|--------|
| Document ID | ARCH-001 |
| Version | 1.1.0 |
| Status | Approved for Implementation |
| Purpose | Define the complete software architecture, architectural principles, component model, dependency structure, and implementation boundaries for the reinforcement learning repository. |
| Scope | Entire software system including runtime architecture, package organization, subsystem decomposition, interfaces, data flow, and extensibility model |
| Audience | AI Coding Agents, Software Architects, ML Engineers, Teaching Assistants, Repository Maintainers |
| Dependencies | PRD.md, README.md, CONTEXT.md, AI_INSTRUCTIONS.md, AGENTS.md, CODING_STANDARDS.md |
| Related Documents | DESIGN.md, TASKS.md, WORKFLOW.md, EXPERIMENTS.md, EVALUATION.md |
| Revision History | v1.0.0 - Initial Architecture Specification; v1.1.0 - Approved Colab-exclusive full-training runtime boundary |

---

# 1. Architecture Purpose

This document defines the authoritative software architecture governing the repository.

Unlike the Product Requirements Document, which specifies **what** the repository shall accomplish, this document specifies **how the system is organized** to satisfy those requirements.

This document is the primary architectural reference for:

- AI Coding Agents
- Human Developers
- Repository Maintainers
- Code Reviewers

Every implementation decision shall conform to this document.

---

# 2. Architectural Objectives

The architecture shall satisfy the following primary objectives.

## AO-001

Implement every assignment requirement without altering assignment semantics.

References:

FR-001 through FR-022

---

## AO-002

Support deterministic experimentation.

References:

NFR-005

---

## AO-003

Enable reproducible research.

---

## AO-004

Minimize coupling between subsystems.

---

## AO-005

Maximize cohesion inside each component.

---

## AO-006

Enable future reinforcement learning algorithm extensions.

---

## AO-007

Support autonomous implementation by AI Coding Agents.

---

## AO-008

Maintain strict separation between:

- environment logic
- reinforcement learning algorithms
- training
- evaluation
- visualization
- experiment management

---

# 3. Architectural Drivers

Architecture is driven by four categories of forces.

```
                   Assignment Requirements
                            │
                            ▼
                    Functional Behavior
                            │
                            ▼
                 Software Architecture
                            │
      ┌─────────────────────┼─────────────────────┐
      ▼                     ▼                     ▼
Engineering           Maintainability      Reproducibility
Quality
```

Every architectural decision traces back to one or more drivers.

---

# 4. Architectural Principles

The repository adopts the following governing principles.

---

## AP-001

Single Responsibility Principle

Every component owns exactly one engineering responsibility.

---

## AP-002

Dependency Inversion

High-level policies shall never depend on implementation details.

---

## AP-003

Configuration over Hardcoding

Runtime behavior shall originate from configuration files.

---

## AP-004

Explicit Interfaces

Component interaction shall occur only through documented interfaces.

---

## AP-005

Deterministic Execution

Randomness shall be externally controlled.

---

## AP-006

Reproducibility

Every experiment shall be reconstructable.

---

## AP-007

Modular Evolution

Future algorithms shall integrate without architectural modification.

---

## AP-008

Documentation-Driven Development

Documentation governs implementation.

Implementation does not redefine documentation.

---

## AP-009

AI Readability

Repository organization shall prioritize deterministic interpretation by AI Coding Agents.

---

## AP-010

Assignment Integrity

Engineering improvements shall never modify assignment-defined behavior.

---

# 5. Architectural Constraints

The following constraints are mandatory.

| Constraint | Source |
|------------|--------|
| Python implementation | Assignment |
| Gymnasium environment | Assignment |
| LunarLander-v3 | Assignment |
| DQN | Assignment |
| DDQN | Assignment |
| Action-space preservation | FR-003 |
| Observation preservation | FR-002 |
| Hidden stochastic failures | FR-006 |
| Modular repository | NFR-001 |
| Reproducible experiments | NFR-005 |
| Full and resumed training execute only in Google Colab | Approved deployment boundary |
| Local training execution is limited to guarded one-step and smoke validation | Approved deployment boundary |

Architectural decisions shall never violate these constraints.

---

# 6. Architectural Style

The repository adopts a layered modular architecture influenced by Clean Architecture principles.

```
                +----------------------------+
                |     Configuration Layer    |
                +-------------+--------------+
                              │
                              ▼
                +----------------------------+
                |   Experiment Orchestration |
                +-------------+--------------+
                              │
          +-------------------+-------------------+
          ▼                                       ▼
+----------------------+               +----------------------+
| Reinforcement Agents |               | Environment Wrapper  |
+----------+-----------+               +----------+-----------+
           │                                      │
           ▼                                      ▼
+----------------------+               +----------------------+
| Neural Network Layer |               | Gymnasium Runtime    |
+----------+-----------+               +----------------------+
           │
           ▼
+----------------------+
| PyTorch Runtime      |
+----------------------+
```

Each layer depends only on lower-level abstractions.

Reverse dependencies are prohibited.

---

# 7. High-Level System Architecture

```
                         User
                          │
                          ▼
                 Configuration Loader
                          │
                          ▼
                Experiment Controller
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
Environment        RL Algorithm      Logging System
 Wrapper                                │
    │                 │                 │
    ▼                 ▼                 ▼
Gymnasium        Replay Buffer      Experiment Logs
    │                 │
    ▼                 ▼
Environment      Neural Network
                     │
                     ▼
                Target Network
                     │
                     ▼
               Optimizer Engine
                     │
                     ▼
               Checkpoint System
                     │
                     ▼
              Evaluation Pipeline
                     │
                     ▼
             Visualization Engine
                     │
                     ▼
               Assignment Report
```

This represents the logical runtime organization of the repository.

---

# 8. Architectural Layers

The repository is divided into distinct architectural layers.

| Layer | Responsibility |
|---------|---------------|
| Configuration | Runtime configuration |
| Orchestration | Workflow coordination |
| Reinforcement Learning | Agent implementation |
| Environment | Environment behavior |
| Infrastructure | Logging, checkpoints, metrics |
| Evaluation | Performance assessment |
| Visualization | Plot generation |
| Reporting | Assignment deliverables |

Layer boundaries are strict.

Cross-layer shortcuts are prohibited.

---

# 9. Component Model

The repository consists of nine primary components.

| Component ID | Component |
|--------------|-----------|
| COMP-001 | Environment Wrapper |
| COMP-002 | Reinforcement Learning Agent |
| COMP-003 | Replay Buffer |
| COMP-004 | Neural Network |
| COMP-005 | Training Engine |
| COMP-006 | Evaluation Engine |
| COMP-007 | Visualization Engine |
| COMP-008 | Reporting Engine |
| COMP-009 | Infrastructure Services |

Subsequent sections define each component.

---

# 10. Component Dependency Graph

```
Training Engine
      │
      ├──────────────► Environment Wrapper
      │
      ├──────────────► RL Agent
      │
      ├──────────────► Infrastructure
      │
      ▼
Evaluation Engine
      │
      ▼
Visualization
      │
      ▼
Reporting
```

No component shall bypass this dependency hierarchy.

---

# 11. Component Ownership Rules

Every repository file shall belong to exactly one architectural component.

Examples:

| Directory | Owner |
|------------|-------|
| src/environment | COMP-001 |
| src/agents | COMP-002 |
| src/memory | COMP-003 |
| src/models | COMP-004 |
| src/training | COMP-005 |
| src/evaluation | COMP-006 |
| src/visualization | COMP-007 |
| src/reporting | COMP-008 |
| src/common | COMP-009 |

Ownership is exclusive.

Components shall not contain unrelated functionality.

---

# 12. Architectural Quality Attributes

The architecture optimizes for the following quality attributes.

| Attribute | Priority |
|------------|----------|
| Correctness | Critical |
| Assignment Compliance | Critical |
| Reproducibility | Critical |
| Maintainability | High |
| Extensibility | High |
| Testability | High |
| AI Readability | High |
| Modularity | High |
| Performance | Medium |
| Scalability | Low |

Quality attributes guide architectural trade-offs.

---

# 13. Component Architecture Overview

The repository is partitioned into independent architectural components.

Each component owns:

- one engineering responsibility,
- one implementation namespace,
- one public interface,
- one lifecycle,
- one dependency boundary.

The architecture intentionally avoids monolithic implementations.

```
                Repository

                      │

      ┌───────────────┼────────────────┐

      ▼               ▼                ▼

 Environment      Reinforcement      Infrastructure
                  Learning

      ▼               ▼                ▼

 Evaluation    Visualization     Reporting
```

Every source file shall belong to exactly one component.

---

# 14. Component Summary

| Component | Identifier | Responsibility |
|------------|------------|----------------|
| Environment Wrapper | COMP-001 | Modified Gymnasium Environment |
| RL Agent | COMP-002 | DQN / DDQN |
| Replay Buffer | COMP-003 | Experience Storage |
| Neural Network | COMP-004 | Q Function Approximation |
| Training Engine | COMP-005 | Training Orchestration |
| Evaluation Engine | COMP-006 | Agent Evaluation |
| Visualization Engine | COMP-007 | Plot Generation |
| Reporting Engine | COMP-008 | Assignment Deliverables |
| Infrastructure Services | COMP-009 | Shared Services |

---

# 15. COMP-001 — Environment Wrapper

## Purpose

Implements every assignment-required environment modification while preserving complete Gymnasium compatibility.

References:

FR-001

through

FR-011

---

## Responsibilities

COMP-001 owns:

- environment creation,
- stochastic action replacement,
- reward modification,
- landing bonus,
- fuel penalty,
- random seed management,
- Gymnasium compatibility,
- transition generation.

---

## Inputs

- Gymnasium environment
- selected action
- random seed
- wrapper configuration

---

## Outputs

- observation
- reward
- terminated
- truncated
- info

identical to Gymnasium API.

---

## Public Interface

```
create_environment()

reset()

step()

close()

seed()
```

Only these methods may be consumed externally.

---

## Internal Responsibilities

Internal helper functions may include:

```
_should_replace_action()

_apply_reward_modification()

_compute_fuel_penalty()

_compute_landing_bonus()

_validate_action()
```

These remain private.

---

## Dependencies

Consumes:

```
Gymnasium

Configuration

Random Generator

Logging
```

Provides services to:

```
Training Engine

Evaluation Engine
```

---

## Forbidden Responsibilities

COMP-001 shall never:

- train neural networks,
- update replay buffer,
- compute gradients,
- save checkpoints,
- generate plots,
- perform evaluation,
- compute metrics unrelated to environment execution.

---

## Lifecycle

```
Configuration

      │

      ▼

Create Environment

      │

      ▼

Reset

      │

      ▼

Episode Execution

      │

      ▼

Close
```

---

## Completion Criteria

COMP-001 is complete when:

- FR-001 through FR-011 implemented,
- Gymnasium compatibility verified,
- deterministic seeds verified,
- assignment verification passed.

---

# 16. COMP-002 — Reinforcement Learning Agent

## Purpose

Implements learning algorithms independently from environment implementation.

---

## Responsibilities

COMP-002 owns:

- action selection,
- optimization,
- loss computation,
- target estimation,
- epsilon scheduling,
- checkpoint loading,
- checkpoint saving.

---

## Supported Algorithms

```
BaseAgent

├── DQNAgent

└── DDQNAgent
```

Future algorithms shall inherit from BaseAgent.

---

## Inputs

- transitions,
- observations,
- replay samples,
- optimizer,
- neural network.

---

## Outputs

- selected actions,
- updated network parameters,
- loss values,
- training statistics.

---

## Public Interface

```
select_action()

learn()

optimize()

save()

load()

update_target()

train()

eval()
```

---

## Internal Responsibilities

```
_compute_loss()

_compute_targets()

_update_parameters()

_compute_q_values()

_sample_batch()
```

---

## Consumed Services

Replay Buffer

Neural Network

Optimizer

Configuration

Logging

---

## Provided Services

Training Engine

Evaluation Engine

---

## Forbidden Responsibilities

COMP-002 shall never:

- modify environment,
- generate plots,
- write reports,
- manipulate filesystem directly,
- own configuration parsing.

---

## Completion Criteria

All DQN and DDQN assignment functionality implemented.

---

# 17. COMP-003 — Replay Buffer

## Purpose

Provide deterministic transition storage.

---

## Responsibilities

- transition storage,
- transition retrieval,
- capacity management,
- sampling,
- replay statistics.

---

## Public Interface

```
push()

sample()

clear()

size()

capacity()
```

---

## Internal Data

```
State

Action

Reward

Next State

Done
```

---

## Dependencies

Consumes:

NumPy

Random Generator

Configuration

---

Provides:

Mini-batches

---

## Forbidden Responsibilities

Replay Buffer shall never:

- compute gradients,
- update models,
- compute losses,
- modify rewards.

---

## Completion Criteria

Replay buffer passes deterministic verification.

---

# 18. COMP-004 — Neural Network

## Purpose

Approximate Q-values.

---

## Responsibilities

- forward propagation,
- parameter storage,
- weight initialization,
- serialization.

---

## Public Interface

```
forward()

state_dict()

load_state_dict()

parameters()
```

---

## Internal Responsibilities

Hidden layers

Activation functions

Weight initialization

---

## Dependencies

Consumes:

PyTorch

Configuration

---

Provides:

Q-values

---

## Forbidden Responsibilities

Network shall never:

- optimize itself,
- compute Bellman targets,
- sample replay buffer,
- modify environment.

---

## Completion Criteria

Forward pass verified.

Architecture configurable.

---

# 19. Component Interaction Summary

```
Training Engine

      │

      ├────────► Environment

      │

      ├────────► RL Agent

      │

      ├────────► Replay Buffer

      │

      └────────► Infrastructure
```

No reverse dependencies permitted.

---

# 20. Component Ownership Matrix

| Responsibility | Owner |
|----------------|-------|
| Environment | COMP-001 |
| Action Failure | COMP-001 |
| Reward Modification | COMP-001 |
| DQN | COMP-002 |
| DDQN | COMP-002 |
| Replay Memory | COMP-003 |
| Q Network | COMP-004 |
| Training | COMP-005 |
| Evaluation | COMP-006 |
| Visualization | COMP-007 |
| Report | COMP-008 |
| Logging | COMP-009 |
| Configuration | COMP-009 |
| Checkpoints | COMP-009 |

Ownership shall remain exclusive.

Shared ownership is prohibited.

---

# 21. Runtime Architecture Philosophy

The first four architectural components define the computational core.

The remaining components define repository orchestration.

Unlike the computational components, orchestration components coordinate execution but do not own learning logic.

The orchestration layer shall remain algorithm-agnostic.

Its responsibility is to coordinate execution while preserving reproducibility and traceability.

```
                 Configuration
                        │
                        ▼
               Training Engine
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
 Environment      RL Algorithm     Infrastructure
        │               │               │
        └───────────────┼───────────────┘
                        ▼
                Evaluation Engine
                        ▼
             Visualization Engine
                        ▼
                Reporting Engine
```

---

# 22. COMP-005 — Training Engine

## Purpose

COMP-005 owns complete orchestration of reinforcement learning training.

It coordinates all lower-level components while remaining independent of algorithm-specific implementations.

The Training Engine shall never contain reinforcement learning equations.

Algorithm implementations remain exclusively inside COMP-002.

---

# Responsibilities

COMP-005 owns:

- experiment initialization
- configuration validation
- environment creation
- random seed initialization
- training loop execution
- replay buffer coordination
- checkpoint scheduling
- logging coordination
- metric collection
- graceful shutdown
- experiment completion
- execution-context enforcement

---

# Inputs

- experiment configuration
- algorithm selection
- environment selection
- random seed
- checkpoint configuration
- validated execution context

---

# Outputs

- trained agent
- checkpoints
- experiment metadata
- metrics
- training logs

---

# Public Interface

```
TrainingEngine

initialize()

run()

train_episode()

collect_transition()

checkpoint()

finalize()
```

No additional public methods shall exist without architectural review.

---

# Internal Responsibilities

Private implementation may include:

```
_initialize_components()

_create_environment()

_create_agent()

_initialize_replay()

_initialize_logging()

_run_episode()

_process_transition()

_checkpoint_if_required()

_collect_metrics()

_finalize_training()
```

Internal methods remain inaccessible outside COMP-005.

---

# Consumed Components

COMP-005 consumes:

```
COMP-001

Environment Wrapper

COMP-002

RL Agent

COMP-003

Replay Buffer

COMP-004

Neural Network

COMP-009

Infrastructure
```

---

# Provided Services

Provides execution services for:

```
Evaluation Engine

Visualization Engine

Reporting Engine
```

---

# Lifecycle

```
Load Configuration

        │

        ▼

Validate Configuration

        │

        ▼

Validate Execution Context

        │

        ▼

Initialize Components

        │

        ▼

Initialize Random Seeds

        │

        ▼

Create Environment

        │

        ▼

Training Loop

        │

        ▼

Checkpoint

        │

        ▼

Save Metrics

        │

        ▼

Finalize
```

---

# State Model

```
UNINITIALIZED

↓

INITIALIZED

↓

READY

↓

CONTEXT_VALIDATED

↓

TRAINING

↓

CHECKPOINTING

↓

COMPLETED
```

Transition backwards is prohibited.

---

# Forbidden Responsibilities

Training Engine shall never:

- modify Gymnasium implementation
- compute Bellman equations
- implement DQN
- implement DDQN
- generate plots
- generate reports
- perform statistical evaluation
- execute full or resumed training in a local execution context
- treat notebook existence, notebook startup, or a smoke run as experiment completion

---

# Completion Criteria

COMP-005 is complete when:

- its code is locally testable through hard-capped one-step and smoke execution
- all full experiment configurations execute in Google Colab
- reproducibility verified
- checkpoint scheduling verified
- experiment artifacts generated
- logging complete
- imported artifact bundles pass COMP-009 validation

---

# 23. COMP-006 — Evaluation Engine

## Purpose

Evaluate trained agents independently of training.

Evaluation shall never modify trained models.

---

# Responsibilities

COMP-006 owns:

- checkpoint loading
- evaluation episodes
- deterministic execution
- metric computation
- performance comparison
- statistical aggregation
- rejection of unvalidated, quarantined, or hash-mismatched checkpoints

---

# Inputs

- COMP-009-validated and promoted trained checkpoint
- evaluation configuration
- random seed
- evaluation environment

---

# Outputs

- evaluation metrics
- summary statistics
- comparison datasets

---

# Public Interface

```
EvaluationEngine

load_checkpoint()

evaluate()

evaluate_episode()

aggregate()

export_results()
```

---

# Internal Responsibilities

```
_initialize_environment()

_disable_exploration()

_collect_rewards()

_compute_statistics()

_finalize_results()
```

---

# Consumed Components

Consumes:

```
Environment Wrapper

RL Agent

Infrastructure
```

---

# Produced Artifacts

```
evaluation_metrics.csv

evaluation_summary.json

comparison_statistics.json
```

---

# Forbidden Responsibilities

Evaluation Engine shall never:

- update neural network weights
- optimize parameters
- modify replay buffer
- save training checkpoints

---

# Completion Criteria

Evaluation metrics generated locally for every completed experiment from a COMP-009-validated and promoted checkpoint.

---

# 24. COMP-007 — Visualization Engine

## Purpose

Generate publication-quality visualizations directly from stored experiment artifacts.

Visualization shall remain independent of training.
Visualization is a local downstream workload and shall consume only promoted artifacts.

---

# Responsibilities

COMP-007 owns:

- reward curves
- loss curves
- comparison charts
- evaluation plots
- export-ready figures

---

# Inputs

Stored metrics.

Experiment metadata.

Evaluation summaries.

---

# Outputs

```
PNG

PDF

SVG
```

(configurable)

---

# Public Interface

```
VisualizationEngine

plot_training()

plot_rewards()

plot_losses()

plot_comparison()

export()
```

---

# Internal Responsibilities

```
_prepare_dataset()

_validate_metrics()

_render_plot()

_save_plot()
```

---

# Forbidden Responsibilities

Visualization shall never:

- train models
- evaluate agents
- alter metrics
- modify experiment results

---

# Completion Criteria

All assignment-required figures generated automatically.

---

# 25. COMP-008 — Reporting Engine

## Purpose

Generate assignment deliverables using stored experiment artifacts.
Reporting is a local downstream workload and shall consume only promoted artifacts.

---

# Responsibilities

- collect figures
- summarize metrics
- generate report tables
- export report assets
- maintain traceability

---

# Inputs

```
Metrics

Plots

Experiment Metadata

Evaluation Results
```

---

# Outputs

```
Report Figures

Tables

Summary Data

Report Assets
```

---

# Public Interface

```
ReportingEngine

collect()

generate_tables()

generate_figures()

export_assets()
```

---

# Forbidden Responsibilities

Reporting Engine shall never:

- train agents
- evaluate checkpoints
- generate raw metrics
- modify experiment outputs

---

# Completion Criteria

Every figure referenced by the assignment report generated successfully.

---

# 26. COMP-009 — Infrastructure Services

## Purpose

Provide reusable cross-cutting services shared across the repository.

Infrastructure owns no reinforcement learning logic.

---

# Responsibilities

Infrastructure includes:

- configuration
- logging
- checkpoint management
- filesystem utilities
- random seed management
- serialization
- metadata generation
- validation
- artifact manifest generation
- cryptographic hash generation and verification
- artifact import, quarantine, validation, and promotion
- execution-context validation and runtime guarding
- utility helpers

---

# Infrastructure Modules

```
Configuration

Logging

Checkpoint Manager

Random Manager

Filesystem Manager

Experiment Metadata

Validators

Utilities
```

Each module owns one responsibility.

---

# Public Interfaces

## Configuration

```
load_config()

validate_config()
```

---

## Logging

```
initialize_logger()

log_metrics()

close_logger()
```

---

## Checkpoint Manager

```
save_checkpoint()

load_checkpoint()

list_checkpoints()
```

---

## Random Manager

```
initialize_seed()

initialize_numpy()

initialize_torch()

initialize_environment()
```

---

## Metadata

```
create_metadata()

save_metadata()

load_metadata()
```

---

## Artifact Integrity and Import

```
create_manifest()

hash_artifact()

validate_manifest()

quarantine_import()

validate_import()

promote_import()
```

COMP-009 shall verify bundle completeness, manifest schema, every declared artifact hash, configuration hash, source commit, execution context, and checkpoint loadability before promotion. Quarantined artifacts are unavailable to COMP-006, COMP-007, and COMP-008.

---

## Execution Context

```
validate_execution_context()

guard_training_request()
```

The runtime guard shall distinguish local test execution from Colab full execution. A configuration flag alone is not sufficient evidence of a Colab runtime.

---

# Consumed By

Every architectural component may consume infrastructure services.

Infrastructure itself shall remain dependency-free except for external libraries.

---

# Forbidden Responsibilities

Infrastructure shall never:

- implement RL algorithms
- modify environments
- compute losses
- generate reports
- own experiment logic

---

# Completion Criteria

All reusable services centralized.

No duplicated infrastructure utilities exist elsewhere.

Manifest, hash, import, quarantine, promotion, and execution-context validation are verified.

---

# 27. Runtime Service Interaction

The orchestration architecture follows the sequence below.

```
Configuration
        │
        ▼
Training Engine
        │
        ▼
Environment Wrapper
        │
        ▼
RL Agent
        │
        ▼
Replay Buffer
        │
        ▼
Checkpoint
        │
        ▼
Evaluation Engine
        │
        ▼
Visualization
        │
        ▼
Reporting
```

Every interaction shall occur through documented interfaces.

---

# 28. Component Communication Matrix

| Provider | Consumer | Communication |
|-----------|----------|---------------|
| COMP-001 | COMP-005 | Environment API |
| COMP-002 | COMP-005 | Agent API |
| COMP-003 | COMP-002 | Replay Interface |
| COMP-004 | COMP-002 | Neural Network API |
| COMP-005 | COMP-009 | Colab artifact bundle and checkpoint |
| COMP-009 | COMP-006 | Validated promoted checkpoint |
| COMP-006 | COMP-007 | Metrics |
| COMP-007 | COMP-008 | Figures |
| COMP-009 | All Components | Shared Services |

Direct communication outside this matrix is prohibited unless approved through an Architecture Decision Record (ADR).

---

# 29. Architectural Invariants

The following invariants shall hold throughout repository evolution.

## AI-ARCH-001

Training logic shall remain isolated from algorithm implementation.

---

## AI-ARCH-002

Environment logic shall remain isolated from learning logic.

---

## AI-ARCH-003

Evaluation shall never modify trained models.

---

## AI-ARCH-004

Visualization shall operate only on persisted artifacts.

---

## AI-ARCH-005

Reporting shall consume generated artifacts rather than recomputing results.

---

## AI-ARCH-006

Infrastructure services shall remain reusable and free of domain-specific logic.

---

## AI-ARCH-007

All component communication shall occur through documented public interfaces.

---

# 30. Repository Architecture Philosophy

The repository structure is itself an architectural artifact.

Its organization shall communicate:

- ownership,
- responsibilities,
- dependencies,
- lifecycle,
- implementation boundaries,

without requiring additional explanation.

Every directory has exactly one responsibility.

Generated artifacts shall never coexist with implementation source.

Configuration shall never be embedded inside implementation modules.

Documentation shall never be mixed with executable source code.

---

# 31. Physical Repository Layout

```
repository-root/

├── README.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
├── .editorconfig
├── .pre-commit-config.yaml

├── configs/
│
├── docs/
│
├── src/
│
├── scripts/
│
├── tests/
│
├── experiments/
│
├── outputs/
│
├── checkpoints/
│
├── logs/
│
├── reports/
│
├── assets/
│
├── notebooks/
│
└── tools/
```

No additional top-level directories shall be introduced without architectural approval.

---

# 32. Top-Level Directory Ownership

| Directory | Owner | Responsibility |
|------------|-------|----------------|
| configs | COMP-009 | Runtime configuration |
| docs | Documentation | Engineering documentation |
| src | Software Components | Source implementation |
| tests | Verification | Automated testing |
| experiments | Experiment Framework | Experiment definitions |
| outputs | Runtime | Generated artifacts |
| checkpoints | Infrastructure | Saved models |
| logs | Infrastructure | Execution logs |
| reports | Reporting | Assignment deliverables |
| assets | Repository | Static resources |
| notebooks | COMP-005 entry point | Thin Colab launcher only; no training business logic |
| scripts | Infrastructure | Utility execution |
| tools | Infrastructure | Developer tooling |

Ownership shall remain exclusive.

---

# 33. Source Tree Architecture

```
src/

├── environment/
│
├── agents/
│
├── memory/
│
├── models/
│
├── training/
│
├── evaluation/
│
├── visualization/
│
├── reporting/
│
├── common/
│
└── __init__.py
```

Each package maps directly to one architectural component.

---

# 34. Source Package Responsibilities

## src/environment

Owner:

COMP-001

Contains:

- modified environment
- wrappers
- reward logic
- stochastic action replacement
- environment factories

Forbidden:

- neural networks
- replay buffer
- optimizers
- plotting

---

## src/agents

Owner:

COMP-002

Contains:

- BaseAgent
- DQN
- DDQN
- epsilon scheduling
- Bellman updates
- optimization

Forbidden:

- plotting
- report generation
- filesystem management

---

## src/memory

Owner:

COMP-003

Contains:

- replay buffer
- transition storage
- sampling logic

Forbidden:

- learning algorithms
- environment logic

---

## src/models

Owner:

COMP-004

Contains:

- neural architectures
- initialization
- forward propagation

Forbidden:

- optimization
- replay
- evaluation

---

## src/training

Owner:

COMP-005

Contains:

- training loop
- orchestration
- checkpoint scheduling
- metric collection
- execution-context guard

Forbidden:

- plotting
- report writing

---

## src/evaluation

Owner:

COMP-006

Contains:

- evaluation runner
- checkpoint evaluation
- statistical summaries

Forbidden:

- gradient computation
- optimization

---

## src/visualization

Owner:

COMP-007

Contains:

- plotting
- chart generation
- figure export

Forbidden:

- model training
- checkpoint creation

---

## src/reporting

Owner:

COMP-008

Contains:

- report assets
- table generation
- figure indexing

Forbidden:

- RL logic
- evaluation logic

---

## src/common

Owner:

COMP-009

Contains:

- configuration
- logging
- utilities
- serialization
- filesystem
- validation
- random seed management

Forbidden:

- assignment-specific logic

---

# 35. Package Dependency Rules

The permitted dependency graph is shown below.

```
training
    │
    ├────────► agents
    │
    ├────────► environment
    │
    ├────────► memory
    │
    ├────────► models
    │
    └────────► common

evaluation
    │
    ├────────► agents
    │
    ├────────► environment
    │
    └────────► common

visualization
    │
    └────────► common

reporting
    │
    ├────────► visualization
    └────────► common
```

No reverse dependency shall exist.

---

# 36. Forbidden Package Dependencies

The following dependencies are architecturally prohibited.

| Source | Forbidden Dependency |
|----------|---------------------|
| environment | agents |
| environment | training |
| environment | evaluation |
| memory | environment |
| models | replay buffer |
| visualization | training |
| reporting | training |
| reporting | replay buffer |
| agents | reporting |
| agents | visualization |

Violation of these rules constitutes an architectural defect.

---

# 37. Namespace Architecture

Python namespaces shall mirror repository structure.

```
src.environment

src.agents

src.memory

src.models

src.training

src.evaluation

src.visualization

src.reporting

src.common
```

Namespaces shall never expose internal implementation details.

---

# 38. Public API Policy

Every package shall explicitly expose its public interface.

Example:

```
src.agents

    __init__.py

        exports

        BaseAgent

        DQNAgent

        DDQNAgent
```

Internal helper classes shall not be exported.

---

# 39. Import Policy

Permitted imports:

```
Standard Library

↓

Third-Party Libraries

↓

Internal Packages
```

Within internal packages:

```
common

↓

environment

↓

models

↓

memory

↓

agents

↓

training

↓

evaluation

↓

visualization

↓

reporting
```

Circular imports are prohibited.

Wildcard imports are prohibited.

Relative imports crossing architectural boundaries are prohibited.

---

# 40. Configuration Architecture

Configuration shall be entirely external.

```
configs/

├── base.yaml

├── training.yaml

├── environment.yaml

├── evaluation.yaml

├── visualization.yaml

├── experiment.yaml

└── logging.yaml
```

No configuration values shall be hardcoded.

---

# 41. Configuration Ownership

| File | Owner |
|------|-------|
| base.yaml | Infrastructure |
| environment.yaml | Environment |
| training.yaml | Training |
| evaluation.yaml | Evaluation |
| experiment.yaml | Experiment Framework |
| logging.yaml | Infrastructure |
| visualization.yaml | Visualization |

Each configuration file owns one configuration domain.

---

# 42. Artifact Architecture

Generated outputs shall remain isolated from implementation.

```
outputs/

├── metrics/

├── figures/

├── tables/

├── evaluation/

└── summaries/
```

Artifacts are immutable after generation.

---

# 43. Checkpoint Architecture

```
checkpoints/

experiment_name/

    run_001/

        latest.pt

        best.pt

        metadata.json

        config.yaml
```

Each experiment owns independent checkpoints.

Shared checkpoints are prohibited.

---

# 44. Logging Architecture

```
logs/

experiment_name/

    execution.log

    training.log

    evaluation.log

    metrics.csv

    runtime.json
```

Logs shall never overwrite previous experiment executions.

---

# 45. Experiment Architecture

```
experiments/

exp001/

exp002/

exp003/

exp004/
```

Each experiment directory contains:

- configuration
- launch script
- metadata
- expected outputs

Experiment implementations shall remain independent.

---

# 46. Documentation Architecture

```
docs/

README.md

CONTEXT.md

AI_INSTRUCTIONS.md

AGENTS.md

CODING_STANDARDS.md

PRD.md

ARCHITECTURE.md

DESIGN.md

WORKFLOW.md

TASKS.md

EXPERIMENTS.md

EVALUATION.md

RISKS.md

DECISIONS.md

REPORT_TEMPLATE.md

CHANGELOG.md

GLOSSARY.md
```

Documentation is version-controlled and immutable with respect to experiment outputs.

---

# 47. Testing Architecture

```
tests/

unit/

integration/

verification/

fixtures/

test_data/
```

Testing code shall never reside inside source packages.

---

# 48. Script Architecture

```
scripts/

train.py

evaluate.py

experiment.py

generate_plots.py

generate_report.py

verify_environment.py
```

Scripts provide executable entry points only.

Business logic belongs inside source packages.

---

# 49. Repository Dependency Matrix

| Package | Depends On |
|----------|------------|
| common | None |
| environment | common |
| memory | common |
| models | common |
| agents | memory, models, common |
| training | agents, environment, common |
| evaluation | agents, environment, common |
| visualization | common |
| reporting | visualization, common |

This matrix is normative.

---

# 50. Architectural Structural Invariants

## ARCH-INV-001

Every source file belongs to exactly one package.

---

## ARCH-INV-002

Every package belongs to exactly one architectural component.

---

## ARCH-INV-003

Generated artifacts shall never be committed as source code.

---

## ARCH-INV-004

Configuration remains external.

---

## ARCH-INV-005

Documentation remains independent of implementation.

---

## ARCH-INV-006

Package dependencies follow the documented dependency graph.

---

## ARCH-INV-007

Business logic shall never exist inside execution scripts.

---

## ARCH-INV-008

Tests remain isolated from production implementation.

---

## ARCH-INV-009

Experiment outputs shall never overwrite previous executions.

---

## ARCH-INV-010

Repository organization shall remain deterministic to support autonomous implementation by AI Coding Agents.

---

# 51. Runtime Architecture Overview

Runtime architecture specifies **how the repository executes**, independent of how source code is physically organized.

The runtime architecture governs:

- initialization
- dependency construction
- configuration loading
- experiment execution
- reinforcement learning lifecycle
- evaluation lifecycle
- visualization workflow
- reporting workflow
- artifact persistence
- termination

The runtime architecture shall remain deterministic for identical configurations and random seeds.

---

# 52. Runtime Design Goals

The runtime architecture is designed to satisfy the following objectives.

| Goal ID | Objective |
|----------|-----------|
| RT-001 | Deterministic execution |
| RT-002 | Modular orchestration |
| RT-003 | Reproducible experiments |
| RT-004 | Failure isolation |
| RT-005 | Recoverability through checkpoints |
| RT-006 | Independent evaluation |
| RT-007 | Artifact traceability |
| RT-008 | AI Coding Agent readability |

---

# 53. High-Level Runtime Flow

The logical flow below is split across deployment contexts: COMP-005 full and resumed training runs only in Colab; after Drive persistence and COMP-009 import validation and promotion, COMP-006 through COMP-008 run locally. Local COMP-005 execution is restricted to guarded one-step and smoke validation.

```
User
 │
 ▼
CLI / Script
 │
 ▼
Configuration Loader
 │
 ▼
Validation
 │
 ▼
Dependency Construction
 │
 ▼
Training Engine
 │
 ├────────► Environment
 │
 ├────────► Agent
 │
 ├────────► Replay Buffer
 │
 ├────────► Neural Network
 │
 └────────► Infrastructure
 │
 ▼
Training Complete
 │
 ▼
Checkpoint Saved
 │
 ▼
Evaluation Engine
 │
 ▼
Visualization Engine
 │
 ▼
Reporting Engine
 │
 ▼
Repository Outputs
```

Each runtime stage consumes only verified outputs from the preceding stage. The human operator starts the Colab session; no local process or AI Coding Agent initiates full or resumed training.

---

# 54. Application Bootstrap Sequence

Application startup shall follow the sequence below.

```
main()

│

├── Parse CLI arguments

├── Locate configuration

├── Validate configuration

├── Resolve and validate ExecutionContext

├── Apply runtime guard and local hard caps

├── Initialize logging

├── Initialize random seeds

├── Build dependency graph

├── Construct environment

├── Construct agent

├── Construct replay buffer

├── Construct training engine

└── Begin execution
```

No training shall begin before bootstrap completes successfully. In `LOCAL_TEST`, bootstrap may dispatch only a hard-capped one-step or smoke path. In `COLAB_FULL`, bootstrap shall verify Colab runtime evidence, the exact checked-out commit, dependency installation, and mounted Google Drive persistence before full or resumed training.

---

# 55. Configuration Loading Lifecycle

Configuration loading is a dedicated lifecycle independent of training.

```
Locate Configuration

        │

        ▼

Read YAML

        │

        ▼

Schema Validation

        │

        ▼

Semantic Validation

        │

        ▼

Normalize Defaults

        │

        ▼

Freeze Configuration

        │

        ▼

Distribute to Components
```

After freezing, configuration objects shall be treated as immutable.

---

# 56. Dependency Construction

Component dependencies shall be instantiated in topological order.

```
Configuration

        │

        ▼

Infrastructure

        │

        ▼

Environment

        │

        ▼

Neural Network

        │

        ▼

Replay Buffer

        │

        ▼

RL Agent

        │

        ▼

Training Engine

        │

        ▼

Evaluation Engine

        │

        ▼

Visualization Engine

        │

        ▼

Reporting Engine
```

Construction order shall never violate dependency relationships defined in this `ARCHITECTURE.md` document.

---

# 57. Training Runtime Sequence

The following sequence defines one complete training execution.

```
Training Engine

        │

        ▼

Environment.reset()

        │

        ▼

Receive Initial State

        │

        ▼

Loop Until Episode Ends

        │

        ▼

Agent.select_action()

        │

        ▼

Environment.step()

        │

        ▼

Receive Transition

        │

        ▼

ReplayBuffer.push()

        │

        ▼

Enough Samples?

        │

   ┌────┴─────┐

   │          │

 No          Yes

   │          │

Continue   ReplayBuffer.sample()

               │

               ▼

Agent.learn()

               │

               ▼

Target Update?

        ┌─────┴──────┐

        │            │

       No           Yes

        │            │

 Continue   Update Target Network

        │

        ▼

Episode Complete?

        │

        ▼

Checkpoint?

        │

        ▼

Metrics Saved

        │

        ▼

Next Episode
```

---

# 58. Episode Lifecycle

Each episode shall follow the lifecycle below.

```
Episode Created

        │

        ▼

Environment Reset

        │

        ▼

Interaction Loop

        │

        ▼

Termination

        │

        ▼

Statistics Aggregated

        │

        ▼

Metrics Persisted

        │

        ▼

Episode Closed
```

Episodes are independent execution units.

---

# 59. Replay Buffer Runtime

Replay buffer interactions occur continuously during training.

```
Transition Produced

        │

        ▼

Push Into Buffer

        │

        ▼

Capacity Exceeded?

        │

   ┌────┴─────┐

   │          │

 No          Yes

   │          │

 Continue   Remove Oldest

        │

        ▼

Minimum Sample Size?

        │

   ┌────┴─────┐

   │          │

 No          Yes

   │          │

Wait      Random Sampling

              │

              ▼

Return Mini-Batch
```

Sampling shall never mutate stored transitions.

---

# 60. Neural Network Runtime

Neural network execution shall follow the lifecycle below.

```
Input State

      │

      ▼

Forward Pass

      │

      ▼

Q Values

      │

      ▼

Loss Computation

      │

      ▼

Backpropagation

      │

      ▼

Optimizer Step

      │

      ▼

Updated Parameters
```

Inference during evaluation skips backpropagation.

---

# 61. Target Network Lifecycle

Target network synchronization shall remain deterministic.

```
Training Starts

        │

        ▼

Initialize Target

        │

        ▼

Training Steps

        │

        ▼

Synchronization Interval Reached?

        │

   ┌────┴─────┐

   │          │

 No          Yes

   │          │

Continue   Copy Parameters

        │

        ▼

Resume Training
```

Synchronization frequency is externally configurable.

---

# 62. Checkpoint Lifecycle

Checkpoint generation follows the lifecycle below.

```
Training Progress

        │

        ▼

Checkpoint Trigger

        │

        ▼

Serialize Model

        │

        ▼

Serialize Optimizer

        │

        ▼

Serialize Configuration

        │

        ▼

Serialize Metadata

        │

        ▼

Integrity Verification

        │

        ▼

Checkpoint Stored
```

Checkpoint creation shall be atomic.

Incomplete checkpoints shall never overwrite valid checkpoints.

---

# 63. Checkpoint Recovery

Recovery begins only from validated checkpoints.
Training recovery and resumed training execute only under `COLAB_FULL`; local recovery may validate deserialization but shall not continue training.

```
Locate Checkpoint

        │

        ▼

Integrity Verification

        │

        ▼

Load Metadata

        │

        ▼

Load Configuration

        │

        ▼

Restore Network

        │

        ▼

Restore Optimizer

        │

        ▼

Restore Training State

        │

        ▼

Resume Execution
```

Recovery shall fail fast when integrity verification fails.

---

# 64. Evaluation Runtime Sequence

Evaluation remains completely independent from training.
Evaluation executes locally and requires a promoted checkpoint produced by COMP-009 validation.

```
Evaluation Engine

        │

        ▼

Load Checkpoint

        │

        ▼

Disable Exploration

        │

        ▼

Create Evaluation Environment

        │

        ▼

Run Episodes

        │

        ▼

Collect Rewards

        │

        ▼

Aggregate Metrics

        │

        ▼

Export Results
```

Evaluation shall never modify model parameters.

---

# 65. Visualization Runtime

Visualization consumes persisted artifacts only.

```
Locate Metrics

        │

        ▼

Load Dataset

        │

        ▼

Validate Data

        │

        ▼

Generate Figures

        │

        ▼

Export Images
```

Visualization shall never recompute metrics.

---

# 66. Reporting Runtime

```
Load Metrics

        │

        ▼

Load Figures

        │

        ▼

Generate Tables

        │

        ▼

Export Report Assets
```

Reporting consumes artifacts without altering them.

---

# 67. Runtime State Machine

```
UNINITIALIZED

        │

        ▼

INITIALIZING

        │

        ▼

READY

        │

        ▼

TRAINING

        │

        ▼

CHECKPOINTING

        │

        ▼

EVALUATING

        │

        ▼

VISUALIZING

        │

        ▼

REPORTING

        │

        ▼

COMPLETED
```

Failure transitions enter the ERROR state. The displayed state machine is the logical processing sequence; deployment-boundary transfer states are normative in Section 75. `LOCAL_VERIFIED` is not `COMPLETED`, and notebook existence or startup does not complete an experiment.

---

# 68. Error Propagation Model

Errors shall propagate upward until handled by the owning component.

```
Environment Error

        │

        ▼

Training Engine

        │

        ▼

Application Controller

        │

        ▼

Logger

        │

        ▼

Graceful Shutdown
```

Lower-level components shall not terminate the application directly.

---

# 69. Runtime Invariants

The following invariants shall hold throughout execution.

## RT-INV-001

Configuration remains immutable after initialization.

---

## RT-INV-002

Replay buffer shall never expose mutable internal storage.

---

## RT-INV-003

Evaluation shall never update trainable parameters.

---

## RT-INV-004

Checkpoint writes shall be atomic.

---

## RT-INV-005

Training metrics shall be persisted before visualization.

---

## RT-INV-006

Reporting shall consume persisted artifacts only.

---

## RT-INV-007

Random seeds shall be initialized before any stochastic operation.

---

## RT-INV-008

All runtime outputs shall be associated with a unique experiment identifier.

---

## RT-INV-009

Component lifecycles shall follow documented state transitions.

---

## RT-INV-010

Runtime failures shall never silently continue after unrecoverable errors.

---

## RT-INV-011

Full training and resumed training shall execute only in Google Colab under `COLAB_FULL`.

---

## RT-INV-012

Local execution shall be limited by non-bypassable one-step and smoke-test caps enforced before environment interaction and optimization.

---

## RT-INV-013

COMP-006 shall load only checkpoints promoted by COMP-009 after manifest, hash, source-commit, configuration-hash, and import validation.

---

## RT-INV-014

COMP-007 and COMP-008 shall execute locally against promoted persisted artifacts.

---

# 70. Deployment and Runtime Boundary

The approved deployment model has two execution contexts.

| ExecutionContext | Permitted Work | Prohibited Work |
|------------------|----------------|-----------------|
| `LOCAL_TEST` | Unit and integration tests, import checks, checkpoint load checks, one-step validation, hard-capped smoke validation, evaluation, visualization, reporting | Full training, resumed training, experiment completion claims |
| `COLAB_FULL` | Full training, resumed training, checkpointing, metrics and manifest generation, Drive persistence | Local-only artifact promotion and downstream reporting |

COMP-005 remains one component and one codebase. Its implementation shall be fully local-testable, while its full and resumed execution paths are Colab-exclusive.

The runtime guard shall reject:

- a full or resumed training request in `LOCAL_TEST`,
- a `COLAB_FULL` request without independently validated Colab runtime evidence,
- a local test request exceeding any hard cap,
- a resumed run whose checkpoint manifest, configuration hash, or source commit is incompatible.

---

# 71. Colab Bootstrap Boundary

The human operator starts Colab and invokes the thin notebook. The notebook shall contain only bootstrap and delegation steps:

1. Mount Google Drive.
2. Clone or fetch the repository.
3. Check out the exact approved Git commit recorded for the run.
4. Install pinned dependencies.
5. Verify the checkout, configuration hash, runtime context, and Drive destination.
6. Delegate to the repository-owned COMP-005 entry point.

Training algorithms, environment modifications, checkpoint semantics, and artifact validation logic shall not be implemented in notebook cells. Notebook existence, successful parsing, successful startup, or reaching the training call is not evidence of training completion.

---

# 72. Colab Persistence and Artifact Boundary

Colab full and resumed runs shall write recoverable checkpoints and run artifacts to a run-specific Google Drive location. Ephemeral Colab storage shall not be the authoritative copy.

Each transferable run bundle shall contain at minimum:

- checkpoint and optimizer/training state required for recovery,
- training metrics and logs,
- frozen configuration snapshot,
- experiment metadata,
- exact Git commit identifier,
- configuration hash,
- artifact manifest with a cryptographic hash for every imported file,
- terminal run status.

A bundle is not complete merely because a checkpoint file exists.

---

# 73. Artifact Transfer and Trust Boundary

Google Drive artifacts cross a trust boundary before local downstream use.

```
Google Drive Run Bundle
        │
        ▼
Local Quarantine
        │
        ▼
Manifest Schema and Completeness Validation
        │
        ▼
Per-File Hash Validation
        │
        ▼
Commit and Configuration Hash Validation
        │
        ▼
Safe Import and Checkpoint Load Validation
        │
        ├────────► Failure: Remain Quarantined
        │
        └────────► Success: Atomic Promotion
```

Promotion creates an immutable validation record. Files shall not be edited to make a failed bundle pass. Corrected bundles are imported as new immutable candidates.

---

# 74. Downstream Runtime Boundary

COMP-006, COMP-007, and COMP-008 execute locally after artifact promotion. COMP-006 has a validated checkpoint prerequisite and shall fail closed when the validation record is absent or inconsistent. COMP-007 and COMP-008 remain independent local downstream components and never invoke COMP-005 training.

---

# 75. Runtime Completion Semantics

Completion is deliberately separated:

| State | Meaning |
|-------|---------|
| `CODE_COMPLETE` | COMP-005 implementation and tests are present |
| `LOCAL_VERIFIED` | Hard-capped local one-step and smoke checks passed |
| `COLAB_READY` | Exact commit, configuration, notebook delegation, dependencies, and Drive target are validated |
| `COLAB_RUN_COMPLETE` | Colab training reached its terminal state and persisted a complete bundle to Drive |
| `ARTIFACTS_PROMOTED` | The transferred bundle passed COMP-009 validation |
| `EXPERIMENT_COMPLETED` | Required promoted checkpoint and training artifacts exist and local COMP-006 evaluation completed |
| `DELIVERABLES_COMPLETE` | Local COMP-007 and COMP-008 outputs passed validation |

No earlier state implies a later state. In particular, code completion, local verification, and notebook existence do not imply experiment completion.

---
