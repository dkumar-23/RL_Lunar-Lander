# Document Metadata

| Field | Value |
|--------|--------|
| Document ID | DSGN-001 |
| Version | 1.1.0 |
| Status | Approved for Implementation |
| Purpose | Define the detailed software design for every architectural component, class, module, interface, and internal interaction required to implement the repository. |
| Scope | Complete software design including class decomposition, module contracts, algorithms, interfaces, configuration, data models, and implementation responsibilities |
| Audience | AI Coding Agents, Software Engineers, ML Engineers, Teaching Assistants, Repository Maintainers |
| Dependencies | PRD.md, ARCHITECTURE.md, CODING_STANDARDS.md |
| Related Documents | TASKS.md, WORKFLOW.md, EXPERIMENTS.md, EVALUATION.md |
| Revision History | v1.0.0 - Initial Detailed Design Specification; v1.1.0 - Approved Colab-exclusive full-training design |

---

# 1. Design Philosophy

This document refines the architecture into concrete implementation guidance.

Where:

- **PRD** defines **what** the repository must accomplish.
- **ARCHITECTURE** defines **how the repository is organized**.
- **DESIGN** defines **how every module, class, function, and interface shall be implemented**.

The design specification is normative.

AI Coding Agents shall implement software directly from this document.

---

# 2. Design Objectives

The detailed design shall satisfy the following objectives.

| Objective ID | Description |
|--------------|-------------|
| DO-001 | Preserve architectural boundaries |
| DO-002 | Minimize implementation ambiguity |
| DO-003 | Enable deterministic AI implementation |
| DO-004 | Support extensibility without architectural modification |
| DO-005 | Maximize readability |
| DO-006 | Minimize hidden state |
| DO-007 | Externalize configuration |
| DO-008 | Maintain assignment compliance |
| DO-009 | Enforce Colab-exclusive full and resumed training |
| DO-010 | Preserve an explicit artifact trust boundary for local downstream use |

---

# 3. Design Principles

The repository adopts the following implementation principles.

## DP-001 — Single Responsibility

Each module owns one implementation concern.

---

## DP-002 — Explicit Interfaces

Every public capability shall be exposed through documented interfaces.

---

## DP-003 — Immutable Inputs

Public methods shall avoid mutating caller-provided objects unless explicitly documented.

---

## DP-004 — Deterministic Behavior

Given identical configuration, checkpoint, and random seed, identical observable behavior shall be produced.

---

## DP-005 — Dependency Injection

Dependencies shall be supplied externally rather than constructed inside business logic whenever practical.

---

## DP-006 — Composition over Inheritance

Inheritance shall be reserved for polymorphic abstractions such as reinforcement learning agents.

---

## DP-007 — Defensive Validation

Public interfaces shall validate inputs and fail with informative exceptions.

---

# 4. Design Layer Mapping

The implementation shall mirror the architectural decomposition.

| Design Layer | Architecture Component |
|--------------|------------------------|
| Environment | COMP-001 |
| Agent | COMP-002 |
| Replay Buffer | COMP-003 |
| Model | COMP-004 |
| Training | COMP-005 |
| Evaluation | COMP-006 |
| Visualization | COMP-007 |
| Reporting | COMP-008 |
| Infrastructure | COMP-009 |

No implementation shall span multiple ownership boundaries.

---

# 5. Module Decomposition

The `src` directory is decomposed into cohesive implementation modules.

```
src/

environment/
agents/
memory/
models/
training/
evaluation/
visualization/
reporting/
common/
```

Each module is further decomposed into classes and implementation units.

---

# 6. Environment Module Design (COMP-001)

## Purpose

Encapsulate all environment-specific behavior while preserving Gymnasium compatibility.

---

## Primary Classes

```
EnvironmentFactory

ModifiedLunarLander

RewardModifier

ActionFailureModel

SeedController
```

---

## Responsibilities

### EnvironmentFactory

Owns creation of configured environments.

Inputs:

- configuration
- seed

Outputs:

- configured environment instance

---

### ModifiedLunarLander

Owns runtime interaction with Gymnasium.

Responsibilities include:

- reset
- step
- close
- wrapper coordination

This class shall remain API-compatible with Gymnasium environments.

---

### RewardModifier

Owns all reward transformations required by assignment specifications.

Responsibilities:

- landing bonus
- fuel penalty
- reward adjustment

Reward transformations shall be deterministic.

---

### ActionFailureModel

Implements stochastic action replacement logic.

Responsibilities:

- determine action replacement
- preserve action-space validity
- maintain configured probability

Randomness shall originate exclusively from the configured random generator.

---

### SeedController

Coordinates environment-specific random state.

Responsibilities:

- seed initialization
- reproducibility
- environment reset synchronization

---

# 7. Environment Collaboration

```
Training Engine

      │

      ▼

EnvironmentFactory

      │

      ▼

ModifiedLunarLander

      │

      ├────────► RewardModifier

      │

      └────────► ActionFailureModel
```

---

# 8. Agent Module Design (COMP-002)

## Purpose

Implement reinforcement learning algorithms independently of orchestration.

---

## Class Hierarchy

```
BaseAgent

├── DQNAgent

└── DDQNAgent
```

Only algorithm-specific behavior shall differ between subclasses.

---

## BaseAgent Responsibilities

Owns:

- action selection interface
- epsilon scheduling
- optimizer ownership
- checkpoint serialization
- target synchronization interface

Subclasses implement algorithm-specific learning.

---

## DQNAgent

Responsibilities:

- Bellman target computation
- Q-learning update
- target network synchronization

---

## DDQNAgent

Responsibilities:

- online network action selection
- target network evaluation
- Double DQN target computation

No duplicated code between DQN and DDQN shall exist unless algorithmically necessary.

---

# 9. Agent Public Interface

Every concrete agent shall expose the following interface.

```
select_action()

learn()

update_target()

save()

load()

train()

eval()
```

No external component shall invoke internal helper methods.

---

# 10. Replay Buffer Design (COMP-003)

## Purpose

Provide deterministic storage and sampling of transitions.

---

## Primary Class

```
ReplayBuffer
```

---

## Internal Data Model

Each transition contains:

```
state

action

reward

next_state

done
```

Additional metadata may be stored if required for experimentation but shall not alter algorithm behavior.

---

## Responsibilities

ReplayBuffer owns:

- insertion
- eviction
- random sampling
- capacity enforcement
- statistics

---

## Capacity Policy

The replay buffer shall implement fixed-capacity storage.

When capacity is exceeded:

- oldest transition removed
- newest transition inserted

Behavior shall be deterministic.

---

# 11. Replay Buffer Interface

```
push()

sample()

clear()

size()

capacity()
```

Sampling shall not mutate stored transitions.

---

# 12. Replay Buffer Collaboration

```
Environment

      │

      ▼

ReplayBuffer

      │

      ▼

RL Agent
```

ReplayBuffer remains unaware of learning algorithms.

---

# 13. Neural Network Module Design (COMP-004)

## Purpose

Approximate the action-value function.

---

## Primary Class

```
QNetwork
```

---

## Responsibilities

- parameter storage
- forward propagation
- weight initialization
- serialization support

The network shall remain independent of optimization logic.

---

## Public Interface

```
forward()

parameters()

state_dict()

load_state_dict()
```

---

## Internal Responsibilities

Private implementation may include:

- hidden layer construction
- activation functions
- initialization strategy
- tensor validation

---

# 14. Neural Network Collaboration

```
Agent

      │

      ▼

QNetwork

      │

      ▼

PyTorch Runtime
```

The network shall not reference replay buffers or environments.

---

# 15. Design Constraints

The following implementation constraints are mandatory.

| Constraint | Rationale |
|------------|-----------|
| No global mutable state | Reproducibility |
| No hidden configuration | Maintainability |
| No environment logic inside agents | Separation of Concerns |
| No learning logic inside environment | Architectural integrity |
| No filesystem logic inside algorithms | Testability |
| No plotting during training | Layer separation |
| No duplicated RL equations | Maintainability |

---

# 16. Design Invariants

## DSGN-INV-001

Every public class owns one responsibility.

---

## DSGN-INV-002

Every module maps to exactly one architectural component.

---

## DSGN-INV-003

Business logic shall remain independent of execution scripts.

---

## DSGN-INV-004

Configuration shall remain external.

---

## DSGN-INV-005

Public interfaces shall remain stable throughout repository evolution unless accompanied by an Architecture Decision Record (ADR).

---

# 17. Training Engine Design (COMP-005)

## Purpose

The Training Engine is responsible for orchestrating reinforcement learning execution.

It shall coordinate all lower-level components without implementing reinforcement learning algorithms.

Algorithm-specific logic shall remain inside COMP-002.

---

# Responsibilities

The Training Engine owns:

- experiment initialization
- component construction
- episode orchestration
- replay scheduling
- checkpoint scheduling
- metric aggregation
- logging coordination
- graceful shutdown
- runtime state transitions
- execution-context enforcement
- local one-step and smoke-test cap enforcement

---

# Primary Class

```
TrainingEngine
```

---

# Collaborating Components

```
Configuration

↓

EnvironmentFactory

↓

ReplayBuffer

↓

Agent

↓

MetricsCollector

↓

CheckpointManager

↓

Logger
```

---

# Internal Composition

```
TrainingEngine

├── EpisodeRunner

├── MetricsCollector

├── CheckpointScheduler

├── RuntimeState

├── ProgressTracker

└── RuntimeGuard
```

Each internal class owns one responsibility.

---

# Public Interface

```
initialize()

run()

run_episode()

save_checkpoint()

finalize()
```

---

# Internal Responsibilities

Private methods may include:

```
_initialize_components()

_initialize_random_state()

_create_environment()

_create_agent()

_create_replay()

_run_step()

_update_statistics()

_checkpoint_if_required()

_finalize_episode()

_finalize_training()
```

Internal methods shall not be exposed outside the module.

---

# EpisodeRunner Design

## Purpose

Execute one complete environment episode.

Responsibilities:

- reset environment
- interaction loop
- transition collection
- termination detection

---

## Public Interface

```
run_episode()
```

---

## Outputs

Produces:

- episode reward
- episode length
- transition count
- termination reason

---

# MetricsCollector Design

## Purpose

Aggregate runtime statistics.

Metrics include:

- episode reward
- moving average reward
- epsilon
- loss
- episode duration
- replay size

---

## Public Interface

```
update()

summarize()

export()
```

---

# ProgressTracker Design

Tracks:

- episode count
- training steps
- replay occupancy
- checkpoint count
- elapsed runtime

Progress tracking shall remain independent from logging.

---

# RuntimeState Design

Encapsulates execution state.

```
UNINITIALIZED

↓

READY

↓

CONTEXT_VALIDATED

↓

TRAINING

↓

CHECKPOINTING

↓

FINISHED
```

Only valid transitions are permitted.

`LOCAL_VERIFIED` and `COLAB_RUN_COMPLETE` shall be represented as distinct terminal outcomes. Neither notebook existence nor notebook startup may produce a completion outcome.

---

# ExecutionContext Design

```
ExecutionContext

├── LOCAL_TEST

└── COLAB_FULL
```

`LOCAL_TEST` permits unit and integration tests, one environment-step validation, and a smoke path bounded by immutable repository-approved maxima for episodes, environment steps, optimizer steps, and wall-clock duration. The RuntimeGuard shall reject rather than silently expand a request above any cap.

`COLAB_FULL` permits full and resumed training only after runtime attestation confirms Google Colab, the exact approved Git commit is checked out, pinned dependencies are installed, the configuration hash is known, and the run-specific Google Drive destination is mounted and writable. A caller-provided context value alone is not runtime attestation.

The same COMP-005 implementation is used in both contexts. The notebook shall not contain an alternative training implementation.

---

# RuntimeGuard Design

Responsibilities:

- derive and validate execution context,
- classify requests as one-step, smoke, full, or resumed,
- enforce local hard caps before constructing a training loop,
- reject full and resumed requests outside validated Colab,
- verify exact source commit and Drive persistence preconditions for `COLAB_FULL`,
- emit an auditable guard decision into experiment metadata.

Public interface:

```
validate_context()

authorize_training()

enforce_local_limits()
```

RuntimeGuard failure is terminal for the requested training invocation.

---

# 18. Evaluation Engine Design (COMP-006)

## Purpose

Evaluate trained checkpoints independently from training.

Evaluation shall never update trainable parameters.

---

# Primary Class

```
EvaluationEngine
```

---

# Responsibilities

- checkpoint loading
- promoted-checkpoint prerequisite validation
- deterministic inference
- reward collection
- metric aggregation
- summary generation

---

# Internal Composition

```
EvaluationEngine

├── EvaluationRunner

├── StatisticsAggregator

└── EvaluationExporter
```

---

# Public Interface

```
load_checkpoint()

evaluate()

aggregate()

export()
```

`load_checkpoint()` shall require a COMP-009 promotion record and shall verify that the checkpoint hash, manifest identity, source commit, and configuration hash match that record. Missing, quarantined, or mismatched inputs fail closed before model construction.

---

# EvaluationRunner

Responsible for:

- environment initialization
- deterministic action selection
- reward accumulation
- episode execution

---

# StatisticsAggregator

Computes:

- mean reward
- median reward
- maximum reward
- minimum reward
- standard deviation
- success rate

No visualization shall occur here.

---

# EvaluationExporter

Produces:

```
evaluation_metrics.csv

evaluation_summary.json

comparison_results.json
```

Export format shall remain stable.

---

# 19. Visualization Engine Design (COMP-007)

## Purpose

Generate publication-quality figures using persisted experiment outputs.

---

# Primary Class

```
VisualizationEngine
```

---

# Responsibilities

- dataset loading
- chart generation
- figure export
- formatting

COMP-007 executes locally and loads only promoted training and evaluation artifacts.

---

# Internal Composition

```
VisualizationEngine

├── DatasetLoader

├── FigureGenerator

├── StyleManager

└── FigureExporter
```

---

# DatasetLoader

Responsibilities:

- metric loading
- validation
- normalization

---

# FigureGenerator

Generates:

- reward curves
- loss curves
- evaluation comparisons
- convergence plots

---

# StyleManager

Defines:

- fonts
- colors
- line styles
- DPI
- figure dimensions

Styling remains centralized.

---

# FigureExporter

Produces:

```
PNG

PDF

SVG
```

Output formats are configurable.

---

# Public Interface

```
generate_training_plots()

generate_evaluation_plots()

export()
```

---

# 20. Reporting Engine Design (COMP-008)

## Purpose

Generate assignment deliverables using persisted artifacts.

---

# Primary Class

```
ReportingEngine
```

---

# Responsibilities

- collect artifacts
- organize report assets
- generate tables
- verify completeness

COMP-008 executes locally and loads only promoted or locally generated downstream artifacts.

---

# Internal Composition

```
ReportingEngine

├── FigureCollector

├── TableGenerator

├── AssetIndexer

└── ReportValidator
```

---

# FigureCollector

Collects:

- generated plots
- diagrams
- evaluation charts

---

# TableGenerator

Produces:

- hyperparameter tables
- evaluation summaries
- experiment comparisons

---

# AssetIndexer

Maintains:

```
asset_manifest.json
```

The manifest shall contain every exported artifact.

---

# ReportValidator

Verifies:

- missing figures
- missing tables
- duplicate assets
- broken references

---

# Public Interface

```
collect()

generate()

validate()

export()
```

---

# 21. Infrastructure Design (COMP-009)

Infrastructure services remain reusable and domain-independent.

---

# Module Decomposition

```
common/

configuration/

logging/

filesystem/

random/

checkpoint/

serialization/

validation/

artifact_integrity/

artifact_import/

execution_context/

utilities/
```

Each infrastructure module owns exactly one concern.

---

# Configuration Module

Primary class:

```
ConfigurationManager
```

Responsibilities:

- load YAML
- merge defaults
- validate schema
- freeze configuration

---

# Logging Module

Primary class:

```
LoggerFactory
```

Responsibilities:

- logger creation
- log formatting
- file handlers
- console handlers

---

# Filesystem Module

Primary class:

```
FilesystemManager
```

Responsibilities:

- directory creation
- path resolution
- atomic writes
- cleanup

---

# Random Module

Primary class:

```
RandomManager
```

Responsibilities:

- initialize Python RNG
- initialize NumPy RNG
- initialize PyTorch RNG
- initialize Gymnasium RNG

---

# Checkpoint Module

Primary class:

```
CheckpointManager
```

Responsibilities:

- save checkpoint
- load checkpoint
- validate checkpoint
- enumerate checkpoints

---

# Serialization Module

Responsibilities:

- JSON serialization
- YAML serialization
- metadata persistence

---

# Validation Module

Responsibilities:

- configuration validation
- runtime assertions
- experiment verification

---

# Artifact Integrity Module

Primary classes:

```
ArtifactManifest

ArtifactHasher

ManifestValidator
```

Responsibilities:

- generate a canonical run manifest,
- compute and verify cryptographic hashes for every declared file,
- validate bundle completeness and terminal status,
- bind artifacts to experiment identity, exact Git commit, configuration hash, and execution context.

The manifest shall not validate when undeclared required files, missing declared files, duplicate paths, unsafe paths, or hash mismatches are present.

---

# Artifact Import Module

Primary class:

```
ArtifactImporter
```

Public interface:

```
quarantine()

validate()

promote()
```

Transferred Google Drive bundles enter a non-consumable local quarantine. Validation performs manifest, hash, commit, configuration, safe-path, schema, and checkpoint-load checks. Promotion is atomic and writes an immutable validation record. Failed candidates remain quarantined and are never exposed to COMP-006, COMP-007, or COMP-008.

---

# Execution Context Module

Provides the context attestation and RuntimeGuard services consumed by COMP-005. It owns no training policy beyond enforcing the approved deployment boundary.

---

# Utilities Module

Contains only:

- helper functions
- formatting helpers
- reusable utilities

Utilities shall never own business logic.

---

# 22. Dependency Injection Strategy

The repository adopts constructor injection.

Example dependency graph:

```
TrainingEngine

│

├── Environment

├── Agent

├── ReplayBuffer

├── MetricsCollector

├── Logger

└── Configuration
```

Dependencies shall never be created lazily inside business methods unless explicitly justified.

---

# Injection Rules

Allowed:

```
Constructor Injection

Factory Injection
```

Discouraged:

```
Service Locator

Global Singleton
```

Forbidden:

```
Hidden Dependency Creation
```

---

# 23. Persistence Design

Persistent artifacts include:

```
Checkpoints

Experiment Metadata

Evaluation Results

Training Metrics

Plots

Logs

Tables

Configuration Snapshot

Artifact Manifest

Import Validation Record
```

Each artifact shall have one authoritative storage location.

During `COLAB_FULL`, run artifacts and recoverable checkpoints shall persist to a run-specific Google Drive directory. After human transfer, local quarantine is non-authoritative and non-consumable; the promoted local bundle becomes authoritative for COMP-006 through COMP-008.

The thin notebook is an execution entry point, not a persistence location or completion artifact.

---

# Artifact Naming Convention

```
<experiment>

↓

<run>

↓

<artifact_type>

↓

timestamp
```

Example:

```
exp001/

run_003/

reward_curve.png
```

---

# 24. Error Handling Design

Errors are categorized.

| Category | Owner |
|-----------|-------|
| Configuration | ConfigurationManager |
| Runtime | TrainingEngine |
| Environment | Environment Module |
| Checkpoint | CheckpointManager |
| Evaluation | EvaluationEngine |
| Visualization | VisualizationEngine |
| Execution context | RuntimeGuard |
| Artifact integrity and import | COMP-009 ArtifactImporter |

---

# Error Handling Principles

- fail early
- fail loudly
- preserve diagnostics
- never suppress unexpected exceptions
- never continue from corrupted state

---

# 25. State Management Design

Mutable state shall be minimized.

Preferred ownership:

```
TrainingEngine

↓

RuntimeState

↓

EpisodeState

↓

ReplayBuffer
```

Hidden mutable global state is prohibited.

---

# 26. Factory Pattern Usage

Factories are permitted only when object construction requires multiple dependencies.

Examples:

```
EnvironmentFactory

AgentFactory

ConfigurationFactory
```

Factories shall not implement business logic.

---

# 27. Design Verification Checklist

Before implementation, AI Coding Agents shall verify:

- every class has one responsibility
- dependencies follow architecture
- configuration is external
- public interfaces are documented
- internal helpers remain private
- persistence follows repository layout
- no duplicated algorithm implementations
- no hidden mutable state
- no circular dependencies

---

# 28. Design Completion Criteria

The design is complete when:

- every architectural component has a corresponding design
- every public interface is specified
- ownership boundaries are preserved
- persistence is fully defined
- dependency injection strategy is documented
- infrastructure responsibilities are centralized
- runtime state management is deterministic

---

# 29. Object Model Overview

The repository object model follows strict ownership boundaries.

```
Configuration
        │
        ▼
TrainingEngine
        │
 ┌──────┼──────────────┐
 ▼      ▼              ▼
Agent Environment ReplayBuffer
 │
 ▼
QNetwork
```

Every runtime object has exactly one owner responsible for its lifecycle.

---

# 30. Core Domain Objects

The implementation shall revolve around the following primary domain objects.

| Object | Owner | Purpose |
|---------|-------|---------|
| Configuration | Infrastructure | Immutable runtime configuration |
| Environment | COMP-001 | RL environment wrapper |
| Agent | COMP-002 | Learning algorithm |
| ReplayBuffer | COMP-003 | Experience storage |
| Transition | COMP-003 | Experience tuple |
| QNetwork | COMP-004 | Function approximator |
| EpisodeStatistics | COMP-005 | Episode metrics |
| TrainingMetrics | COMP-005 | Aggregated training data |
| EvaluationMetrics | COMP-006 | Evaluation summaries |
| ExperimentMetadata | COMP-009 | Experiment identity |

---

# 31. Transition Data Model

Every replay entry shall conform to the following structure.

```
Transition

state

action

reward

next_state

terminated

truncated
```

The implementation may represent this object using:

- dataclass
- NamedTuple
- immutable object

The chosen implementation shall preserve immutability after creation.

---

# 32. Transition Object Contract

## Required Fields

| Field | Type |
|---------|------|
| state | ndarray |
| action | integer |
| reward | float |
| next_state | ndarray |
| terminated | boolean |
| truncated | boolean |

---

## Responsibilities

A Transition object:

- stores experience
- contains no business logic
- remains immutable
- supports serialization

---

## Forbidden Responsibilities

Transition shall never:

- compute rewards
- modify observations
- own neural networks
- contain optimizer state

---

# 33. EpisodeStatistics Object

Purpose:

Represent one completed episode.

---

## Required Fields

```
episode_id

episode_reward

episode_length

steps

epsilon

loss

elapsed_time
```

---

## Responsibilities

Stores only completed episode metrics.

Does not perform aggregation.

---

# 34. TrainingMetrics Object

Purpose:

Aggregate experiment-wide statistics.

---

## Required Collections

```
episode_rewards

moving_average

episode_lengths

loss_history

epsilon_history

evaluation_scores
```

---

## Public Operations

```
append()

export()

reset()

summarize()
```

Aggregation shall remain deterministic.

---

# 35. EvaluationMetrics Object

Stores evaluation-only outputs.

Fields include:

```
mean_reward

median_reward

std_reward

minimum_reward

maximum_reward

success_rate

episode_count
```

EvaluationMetrics shall never contain training losses.

---

# 36. ExperimentMetadata

Purpose:

Provide traceability for every generated artifact.

---

## Required Fields

```
experiment_id

run_id

timestamp

algorithm

environment

random_seed

configuration_hash

git_commit

repository_version

execution_context

training_request_type

artifact_manifest_id

drive_run_uri

runtime_guard_decision
```

Every generated artifact shall reference ExperimentMetadata.

---

# 37. Configuration Schema

Configuration objects shall be immutable after validation.

Logical organization:

```
Configuration

├── EnvironmentConfig

├── TrainingConfig

├── EvaluationConfig

├── VisualizationConfig

├── LoggingConfig

├── CheckpointConfig

└── ExperimentConfig
```

`ExecutionContext` is a validated runtime input, not an ordinary configuration override. Configuration may request a mode, but COMP-009 runtime attestation determines the effective context.

---

# 38. EnvironmentConfig

Required fields include:

| Field | Description |
|---------|-------------|
| environment_name | Gymnasium environment identifier |
| random_seed | Environment seed |
| action_failure_probability | Probability of action replacement |
| landing_bonus | Positive terminal reward |
| fuel_penalty | Fuel consumption coefficient |
| render_mode | Rendering strategy |

Validation shall occur before runtime initialization.

---

# 39. TrainingConfig

Required fields include:

```
algorithm

episodes

learning_rate

discount_factor

batch_size

buffer_capacity

target_update_frequency

optimizer

epsilon_initial

epsilon_final

epsilon_decay
```

---

# 40. EvaluationConfig

Fields include:

```
evaluation_episodes

checkpoint_selection

deterministic_actions

render

save_metrics
```

---

# 41. LoggingConfig

Fields include:

```
console_logging

file_logging

tensorboard

log_level

metrics_frequency
```

---

# 42. CheckpointConfig

Fields include:

```
checkpoint_directory

save_frequency

save_best_model

retain_last

retain_best

atomic_save
```

---

# 43. VisualizationConfig

Fields include:

```
figure_format

dpi

theme

figure_size

export_directory
```

---

# 44. Interface Contracts

Every public interface shall define:

- inputs
- outputs
- side effects
- exceptions
- completion criteria

No undocumented public method is permitted.

---

# 45. Training Engine Contract

```
initialize()

Input:
Configuration

ExecutionContext request

Output:
Initialized runtime

Side Effects:
Creates dependencies

Exceptions:
ConfigurationError
InitializationError
ExecutionContextError
RuntimeGuardError
```

---

```
run()

Input:
None

Output:
TrainingMetrics

Side Effects:
Training execution

Exceptions:
RuntimeError
EnvironmentError
CheckpointError
ExecutionContextError
```

`run()` shall dispatch one of the following guarded paths:

| Path | Required Context | Result |
|------|------------------|--------|
| One-step validation | `LOCAL_TEST` | Test evidence only |
| Smoke validation | `LOCAL_TEST` | Test evidence only, hard-capped |
| Full training | `COLAB_FULL` | Drive-persisted run bundle |
| Resumed training | `COLAB_FULL` | Drive-persisted resumed run bundle |

No local path returns an experiment-complete result.

---

# 46. Agent Contract

```
select_action()

Input:
Observation

Output:
Action

Side Effects:
None
```

---

```
learn()

Input:
MiniBatch

Output:
Loss

Side Effects:
Updates network parameters
```

---

```
update_target()

Input:
None

Output:
None

Side Effects:
Synchronizes target network
```

---

# 47. Replay Buffer Contract

```
push()

Input:
Transition

Output:
None

Side Effects:
Stores transition
```

---

```
sample()

Input:
Batch Size

Output:
Transition Collection
```

Sampling shall never alter internal ordering.

---

# 48. Environment Contract

```
reset()

Output

Observation

Info
```

---

```
step()

Input

Action

Output

Observation

Reward

Terminated

Truncated

Info
```

API compatibility with Gymnasium shall be preserved.

---

# 49. Sequence Interaction

One learning step proceeds as follows.

```
Environment

↓

Observation

↓

Agent.select_action()

↓

Environment.step()

↓

Transition

↓

ReplayBuffer.push()

↓

ReplayBuffer.sample()

↓

Agent.learn()

↓

MetricsCollector.update()
```

No additional interactions shall occur.

---

# 50. Object Lifecycle

```
Configuration

↓

ExecutionContext Validation

↓

Environment

↓

Agent

↓

Replay Buffer

↓

Training

↓

Drive Persistence

↓

Human Artifact Transfer

↓

Quarantine and COMP-009 Validation

↓

Promotion

↓

Local Evaluation

↓

Local Visualization

↓

Local Reporting

↓

Termination
```

Objects shall be destroyed in reverse dependency order.

The human operator starts Colab and performs the transfer. The thin notebook mounts Drive, checks out the exact approved commit, installs pinned dependencies, validates preconditions, and delegates to COMP-005. Notebook cells shall not own domain or training logic.

---

# 51. Extension Points

Future extensions shall be introduced through documented extension interfaces.

Supported extension categories include:

- reinforcement learning algorithms
- neural network architectures
- environments
- evaluation metrics
- visualization styles
- reporting exporters

Extensions shall preserve architectural boundaries.

---

# 52. Object Invariants

## OBJ-INV-001

Configuration remains immutable after validation.

---

## OBJ-INV-002

Transition objects remain immutable after creation.

---

## OBJ-INV-003

ReplayBuffer owns all stored transitions.

---

## OBJ-INV-004

TrainingMetrics contains aggregated statistics only.

---

## OBJ-INV-005

EvaluationMetrics contains evaluation-only statistics.

---

## OBJ-INV-006

ExperimentMetadata uniquely identifies every execution.

---

## OBJ-INV-007

Public interfaces shall not expose internal mutable state.

---

## OBJ-INV-008

Component ownership shall never be ambiguous.

---

# 53. Requirement Traceability

| Requirement | Design Element |
|-------------|----------------|
| FR-001 – FR-011 | EnvironmentConfig, Modified Environment |
| FR-012 | Agent Hierarchy |
| FR-013 | ReplayBuffer |
| FR-014 | QNetwork |
| FR-015 | TrainingEngine |
| FR-016 | EvaluationEngine |
| FR-017 | VisualizationEngine |
| FR-018 | ReportingEngine |
| NFR-001 – NFR-* | Infrastructure Services |

Every design element shall trace back to at least one requirement.

---

# 54. Design Verification Checklist

AI Coding Agents shall verify that:

- every object has one owner
- every interface has documented contracts
- every configuration field is validated
- every lifecycle is deterministic
- every extension point preserves architecture
- object invariants are enforced
- no mutable global state exists
- traceability to requirements is maintained
- local full and resumed training are rejected
- local one-step and smoke execution cannot exceed hard caps
- Colab bootstrap checks out the exact approved commit and persists to Drive
- imported bundles remain quarantined until manifest, hash, commit, configuration, and checkpoint validation pass
- COMP-006 rejects checkpoints without a valid promotion record
- COMP-007 and COMP-008 operate locally on promoted artifacts
- notebook existence is never interpreted as experiment completion

---

# 55. Definition of Design Done

The design phase is complete when:

- all architectural components have detailed class specifications
- all public interfaces are documented
- all data models are defined
- configuration schemas are complete
- object lifecycles are specified
- interface contracts are explicit
- extension mechanisms are documented
- requirement traceability is complete
- implementation ambiguity is eliminated
- execution-context and artifact-trust boundaries are explicit

---
