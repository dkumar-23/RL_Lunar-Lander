# Document Metadata

| Field | Value |
|--------|--------|
| Document ID | GLOSSARY-001 |
| Version | 1.0.0 |
| Status | Approved |
| Purpose | Define the authoritative terminology used throughout the repository to ensure consistent understanding by AI Coding Agents, developers, reviewers, and teaching staff. |
| Scope | Repository-wide terminology including Reinforcement Learning, software architecture, experiments, evaluation, reporting, documentation, and project governance. |
| Audience | AI Coding Agents, Students, ML Engineers, Software Engineers, Teaching Assistants, Repository Maintainers |
| Dependencies | README.md, PRD.md, ARCHITECTURE.md, DESIGN.md |
| Related Documents | All repository documentation |
| Revision History | v1.0.0 — Initial Repository Glossary |

---

# 1. Purpose

This glossary is the **authoritative vocabulary** for the repository.

Every document shall use these definitions consistently.

Where multiple meanings exist in general literature, the definition in this glossary takes precedence within this repository.

---

# 2. Reinforcement Learning Terms

## Agent

The decision-making component that observes the environment and selects actions to maximize cumulative reward.

Repository Component:

```
DQNAgent

DDQNAgent
```

Reference

COMP-002

---

## Environment

The system with which the agent interacts.

For this assignment:

Modified LunarLander environment.

Reference

COMP-001

---

## State

A numerical representation of the environment observed by the agent at a given time step.

States are provided by the modified LunarLander environment.

---

## Observation

The observation returned by Gymnasium after each environment step.

Within this repository, *state* and *observation* are treated interchangeably unless explicitly distinguished.

---

## Action

A decision selected by the reinforcement learning agent.

The environment executes either:

- the intended action, or
- a substituted action according to the assignment's stochastic action replacement rule.

---

## Episode

A complete interaction sequence beginning with `env.reset()` and ending when the environment terminates or truncates.

---

## Step

One environment interaction cycle consisting of:

```
Observation

↓

Action Selection

↓

Environment Transition

↓

Reward

↓

Next Observation
```

---

## Reward

The scalar feedback returned after each environment transition.

This repository distinguishes between:

- Base Reward (environment)
- Modified Reward (assignment-specific reward shaping)

---

## Reward Shaping

The assignment-specific modification of the environment reward function to encourage desired agent behavior.

Reward shaping is implemented in the environment layer, not within the agent.

Reference:

FR-003

ADR-003

---

## Discount Factor (γ)

A value in the range `[0,1]` controlling the importance of future rewards.

Configured through repository configuration files.

---

## Policy

The strategy used by an agent to select actions.

During training:

- ε-greedy policy

During evaluation:

- greedy policy (ε = 0)

---

## Return

The cumulative discounted reward obtained during an episode.

---

## Exploration

The process of selecting non-greedy actions to discover new behaviors.

Implemented using epsilon-greedy exploration.

---

## Exploitation

Selecting the action currently believed to maximize expected return.

---

# 3. Deep Reinforcement Learning Terms

## DQN (Deep Q-Network)

A value-based reinforcement learning algorithm that approximates the action-value function using a neural network.

Repository Component:

```
DQNAgent
```

---

## Double DQN (DDQN)

An extension of DQN that reduces overestimation bias by separating action selection and action evaluation.

Repository Component:

```
DDQNAgent
```

---

## Q-Network

The neural network estimating action-value functions.

Repository Component:

```
QNetwork
```

---

## Target Network

A periodically synchronized copy of the online network used to stabilize learning.

---

## Online Network

The network updated during gradient descent.

---

## Bellman Equation

The recursive equation used to estimate future returns.

Implemented within the learning update procedure.

---

## Replay Buffer

A finite-capacity memory storing previous experiences for random sampling during training.

Repository Component:

```
ReplayBuffer
```

---

## Transition

A single experience stored in replay memory.

Contains:

```
State

Action

Reward

Next State

Done Flag
```

---

## Mini-batch

A randomly sampled subset of replay memory used for one optimization step.

---

## Loss Function

The objective minimized during neural network training.

Typically the temporal-difference (TD) error.

---

## Target Synchronization

Copying online network parameters into the target network according to a configurable schedule.

---

# 4. Assignment-Specific Terms

## Modified LunarLander

The Gymnasium LunarLander environment extended according to assignment requirements.

Includes:

- reward shaping
- stochastic action replacement

---

## Stochastic Action Replacement

Assignment requirement where the intended action may be replaced with another action according to a predefined probability.

Implemented in the Action Failure Model.

Reference:

FR-004 - FR-006

EXP-002 and EXP-004

---

## Action Failure Model

The repository component responsible for stochastic action replacement.

The learning algorithm remains unaware of this modification.

---

## Reward Modifier

The repository component responsible for assignment-specific reward shaping.

---

# 5. Experimentation Terms

## Experiment

A controlled execution of the training or evaluation pipeline using a fixed configuration.

Identified by an `EXP-xxx` identifier.

---

## Run

A single execution instance of an experiment.

Multiple runs may exist for the same experiment.

---

## Experiment Manifest

Metadata describing an experiment, including:

- configuration
- random seed
- software versions
- outputs
- checkpoints

---

## Checkpoint

A serialized snapshot of the model state that can be used to resume training or perform evaluation.

---

## Artifact

A file generated by the repository.

Examples include:

- checkpoints
- metrics
- plots
- reports
- manifests

---

## Full Training

An unbounded or assignment-scale reinforcement learning training execution intended to produce experiment results. Full Training runs only in Google Colab through a human-started Colab Training Notebook at an exact Git commit; it is prohibited during local verification.

---

## Bounded Local Test

A local execution with explicit, small limits on work, such as a fixed low number of environment steps or episodes, used to verify wiring and behavior without performing Full Training.

---

## One-Step Learning Validation

A local check that constructs the required learning components and performs at most one optimization update to verify tensor flow, loss computation, and parameter update compatibility. It is not Full Training and produces no experimental result claim.

---

## Colab Training Notebook

The notebook entry point used for Full Training in Google Colab. A human starts the notebook, it checks out and records an exact Git commit, and it persists the Training Artifact Bundle to Google Drive. Notebook presence or cell execution alone does not establish experiment completion.

---

## Training Artifact Bundle

The self-contained, run-specific collection persisted from Colab to Google Drive under the artifact contract. It includes the manifest, exact Git commit, configuration and seeds, Execution Platform and dependency metadata, status, checkpoints, required metrics and logs, and an inventory with integrity information.

---

## Validated Checkpoint

A checkpoint from a complete Training Artifact Bundle that has passed local provenance, integrity, compatibility, and loadability validation and has completed Artifact Promotion. Only a Validated Checkpoint may support evaluation, reporting, resumption, or assignment evidence.

---

## Artifact Promotion

The explicit transition of a locally validated Training Artifact Bundle, checkpoint, or result artifact from imported and untrusted status to approved downstream use. Promotion is prohibited when bundle validation is incomplete or fails.

---

## Execution Platform

The compute environment in which an execution occurs, including whether it is local or Google Colab and the relevant runtime, operating system, accelerator, Python, and dependency details. Full Training has Google Colab as its required Execution Platform.

---

# 6. Evaluation Terms

## Evaluation

The process of measuring agent performance without updating model parameters.

---

## Evaluation Episode

An episode executed with exploration disabled.

---

## Mean Reward

The average cumulative reward across evaluation episodes.

---

## Success Rate

The percentage of evaluation episodes satisfying the assignment's success criterion.

The exact criterion shall follow the assignment specification.

---

## Convergence

The stage where training metrics stabilize according to repository evaluation policy.

---

## Robustness

The consistency of agent performance under varying conditions, including stochastic action replacement.

---

# 7. Repository Architecture Terms

## Component

A logical subsystem with clearly defined responsibilities and interfaces.

Examples:

- Training Engine
- Evaluation Engine
- Replay Buffer
- Visualization Engine

---

## Module

A Python package or source file implementing one or more related responsibilities.

---

## Layer

A collection of components operating at the same abstraction level.

Examples:

- Environment Layer
- Agent Layer
- Training Layer
- Evaluation Layer

---

## Interface

The public contract through which one component interacts with another.

---

## Dependency

A relationship where one component requires another to perform its responsibilities.

---

# 8. Documentation & Governance Terms

## ADR (Architecture Decision Record)

A documented architectural decision, including context, rationale, alternatives, and consequences.

Reference:

DECISIONS.md

---

## Requirement

A functional or non-functional capability identified in the PRD.

Identifiers:

- FR-xxx
- NFR-xxx

---

## Task

A unit of implementation work identified in TASKS.md.

Identifiers:

```
TASK-001

TASK-002
```

---

## Experiment Identifier

Unique identifier for a controlled experiment.

Example:

```
EXP-004
```

---

## Evaluation Identifier

Unique identifier for an evaluation activity.

Example:

```
EVAL-003
```

---

## Traceability

The ability to connect requirements, implementation, experiments, evaluations, and report evidence.

Traceability chain:

```
Requirement

↓

Task

↓

Implementation

↓

Experiment

↓

Evaluation

↓

Report
```

---

## Definition of Done (DoD)

The measurable criteria that determine when a task, component, experiment, or document is considered complete.

---

# 9. AI Coding Agent Terms

## AI Coding Agent

An autonomous coding system (e.g., Claude Code, Cursor, Cline, Roo Code, Continue.dev, GitHub Copilot, Gemini CLI, Aider) implementing the repository according to this documentation.

---

## Repository Authority

The documentation suite is the authoritative specification for repository implementation.

Agents shall not invent undocumented behavior.

---

## Hallucination

Implementation or documentation generated by an AI Coding Agent that is unsupported by the repository specification.

Hallucinations are considered implementation defects.

---

## Deterministic Execution

Execution that produces reproducible results under identical configuration, software versions, and random seeds.

---

# 10. Repository Identifier Prefixes

| Prefix | Meaning |
|---------|---------|
| FR | Functional Requirement |
| NFR | Non-Functional Requirement |
| COMP | Architecture Component |
| TASK | Implementation Task |
| EXP | Experiment |
| EVAL | Evaluation |
| ADR | Architecture Decision Record |
| RPT | Report Section / Template |
| VERIFY | Verification Item |
| RISK | Risk Register Entry |
| FIG | Figure Identifier |
| TAB | Table Identifier |

---

# 11. Terminology Governance

To preserve consistency:

- Every new technical term introduced into the repository shall be added to this glossary.
- Existing definitions shall not be redefined elsewhere.
- Documents shall reference glossary terms rather than creating alternative terminology.
- If terminology changes, the glossary shall be updated first, followed by dependent documents.

---

# 12. Definition of Done

The glossary is complete when:

- all repository-specific terminology is defined
- reinforcement learning terms are consistently described
- assignment-specific concepts are documented
- architecture, experimentation, evaluation, and governance vocabulary are covered
- identifier prefixes are standardized
- AI Coding Agents can interpret repository documentation without relying on external terminology

# End of GLOSSARY.md
