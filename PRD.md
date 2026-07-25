# Document Metadata

| Field | Value |
|--------|--------|
| Document ID | PRD-001 |
| Version | 1.1.0 |
| Status | Approved for Implementation |
| Purpose | Define the complete product requirements, assignment requirements, engineering requirements, constraints, acceptance criteria, and traceability model for the Reinforcement Learning project. |
| Scope | Entire software system from environment implementation through experimentation and evaluation |
| Audience | AI Coding Agents, Software Architects, ML Engineers, Teaching Assistants, Repository Maintainers |
| Dependencies | README.md, CONTEXT.md, AI_INSTRUCTIONS.md, AGENTS.md, CODING_STANDARDS.md |
| Related Documents | ARCHITECTURE.md, DESIGN.md, TASKS.md, WORKFLOW.md, EXPERIMENTS.md, EVALUATION.md, COMMAND_PERMISSIONS.md |
| Revision History | v1.0.0 — Initial Product Requirements Specification; v1.1.0 — Formally added owner-approved repository constraint CON-011 without changing FR or NFR meanings. |

---

# 1. Purpose

This Product Requirements Document (PRD) is the authoritative functional specification for the repository.

It converts the academic assignment into a structured engineering specification suitable for autonomous implementation by AI Coding Agents.

Unlike implementation documents, the PRD defines **what** the repository must accomplish rather than **how** it will be implemented.

Every downstream document shall derive its implementation guidance from this document.

The PRD shall remain implementation-independent.

---

# 2. Product Vision

Develop a production-quality, research-oriented reinforcement learning repository capable of investigating the robustness of value-based reinforcement learning algorithms under stochastic actuator failures within the LunarLander-v3 environment.

The repository shall satisfy all mandatory assignment requirements while adhering to modern software engineering principles, reproducible experimentation, modular architecture, and AI-assisted development practices.

The repository is intended to serve simultaneously as:

- an academic assignment submission,
- a reinforcement learning experimentation framework,
- a software engineering portfolio project,
- an AI-agent compatible repository,
- a reproducible research implementation.

---

# 3. Product Mission

Provide an implementation that enables controlled comparison between:

- Deep Q-Network (DQN)

and

- Double Deep Q-Network (DDQN)

under two execution environments:

- Original LunarLander-v3
- Modified LunarLander-v3 with stochastic engine failures

while preserving experimental fairness and assignment correctness.

---

# 4. Product Objectives

## Primary Objective

Implement every mandatory assignment requirement exactly as specified.

---

## Secondary Objectives

Develop an extensible reinforcement learning repository suitable for future experimentation.

---

## Engineering Objectives

The repository shall provide:

- deterministic execution,
- modular architecture,
- centralized configuration,
- reproducible experiments,
- comprehensive documentation,
- automated evaluation,
- AI-agent readability,
- maintainable source code.

---

# 5. Problem Statement

Modern reinforcement learning environments commonly assume that every selected action is executed exactly as intended.

Real-world autonomous systems violate this assumption due to actuator failures, communication delays, and hardware uncertainty.

The assignment introduces stochastic engine failures into LunarLander-v3 to evaluate how value-based reinforcement learning algorithms respond when selected actions are not always executed.

The project therefore investigates algorithm robustness rather than maximizing benchmark performance.

---

# 6. Product Scope

The repository includes:

- modified Gymnasium environment,
- stochastic action replacement,
- modified reward function,
- DQN implementation,
- DDQN implementation,
- replay buffer,
- target network,
- training framework,
- evaluation framework,
- visualization,
- report generation,
- verification utilities,
- experiment management,
- documentation.

---

# 7. Out of Scope

The following capabilities are intentionally excluded.

## Reinforcement Learning Algorithms

- PPO
- SAC
- TD3
- A2C
- Rainbow DQN
- Dueling Networks
- Noisy Networks
- Distributional RL
- Prioritized Replay
- HER

---

## Environment Extensions

- Observation modifications
- Physics modifications
- Curriculum learning
- Multi-agent environments
- Continuous control
- Reward shaping beyond assignment requirements

---

## Infrastructure

- Distributed training
- Hyperparameter optimization
- Cloud deployment
- Kubernetes
- Multi-GPU training
- Online serving

---

# 8. Stakeholders

| Stakeholder | Responsibility |
|-------------|---------------|
| Student Team | Repository ownership |
| Course Faculty | Assignment evaluation |
| Teaching Assistants | Functional verification |
| AI Coding Agents | Repository implementation |
| Human Developers | Maintenance |
| Repository Reviewers | Quality assurance |

---

# 9. Product Success Criteria

The repository is considered successful only when all success dimensions are satisfied.

## Functional Success

Every functional requirement is implemented.

---

## Assignment Success

Every grading requirement is satisfied.

---

## Engineering Success

Repository architecture remains modular and maintainable.

---

## Experimental Success

All required experiments execute successfully.

---

## Evaluation Success

All required metrics and plots are generated.

---

## Documentation Success

Repository documentation enables autonomous implementation without external clarification.

---

# 10. Business Context

Although this project originates from an academic assignment, repository engineering decisions shall reflect production-quality software engineering practices.

Engineering improvements shall never alter assignment semantics.

The repository therefore distinguishes between:

## Assignment Requirements

Mandatory.

Originating from the assignment specification.

---

## Repository Engineering Decisions

Optional engineering improvements introduced solely to improve software quality.

Engineering decisions shall remain orthogonal to assignment requirements.

---

# 11. System Context

```
                 Assignment Specification
                          │
                          ▼
                Repository Documentation
                          │
                          ▼
              Reinforcement Learning System
                          │
      ┌───────────────────┼────────────────────┐
      │                   │                    │
      ▼                   ▼                    ▼
Environment         RL Algorithms        Experiment Engine
      │                   │                    │
      └───────────────────┼────────────────────┘
                          │
                          ▼
                   Evaluation Framework
                          │
                          ▼
                     Assignment Report
```

---

# 12. Product Features

The repository consists of the following logical features.

| Feature ID | Feature |
|------------|----------|
| FEAT-001 | Environment Wrapper |
| FEAT-002 | Action Failure Simulation |
| FEAT-003 | Reward Modification |
| FEAT-004 | Environment Verification |
| FEAT-005 | Replay Buffer |
| FEAT-006 | Neural Network |
| FEAT-007 | DQN |
| FEAT-008 | DDQN |
| FEAT-009 | Training Engine |
| FEAT-010 | Evaluation Engine |
| FEAT-011 | Experiment Manager |
| FEAT-012 | Plot Generation |
| FEAT-013 | Report Generation |
| FEAT-014 | Configuration Management |
| FEAT-015 | Logging Framework |

Each feature shall map to one or more functional requirements.

---

# 13. Functional Requirement Philosophy

Functional requirements define externally observable repository behaviour.

Implementation details shall never appear inside functional requirements.

Each functional requirement shall:

- describe observable behaviour,
- possess a unique identifier,
- remain implementation independent,
- map to verification procedures,
- map to architecture components,
- map to implementation tasks.

Functional requirements shall never be duplicated elsewhere in the repository.

---

# 14. Functional Requirement Categories

The repository groups functional requirements into the following domains.

| Category | Requirement Range |
|----------|-------------------|
| Environment | FR-001 – FR-011 |
| Reinforcement Learning | FR-012 – FR-016 |
| Experiments | FR-017 – FR-019 |
| Evaluation | FR-020 – FR-022 |

Subsequent sections define each requirement individually.

---

# 15. Functional Requirements

This section defines every functional requirement derived directly from the assignment specification.

These requirements are normative.

Implementations shall satisfy these requirements exactly.

Engineering improvements may enhance implementation quality but shall never modify the observable behavior specified here.

---

# 15.1 Environment Requirements

---

## FR-001 — Modified LunarLander Environment

### Requirement

The repository shall provide a modified LunarLander-v3 environment that preserves compatibility with the Gymnasium API.

### Rationale

The assignment requires experimentation using a modified environment while preserving compatibility with reinforcement learning algorithms.

### Inputs

- Gymnasium LunarLander-v3
- Environment configuration

### Outputs

- Modified Gymnasium-compatible environment

### Preconditions

- Gymnasium environment successfully initialized

### Postconditions

- Environment exposes standard Gymnasium interface

### Acceptance Criteria

- `reset()` behaves identically to Gymnasium
- `step()` preserves Gymnasium semantics
- Compatible with existing RL algorithms

### Verification

VERIFY-001

### Architecture Mapping

COMP-001

---

## FR-002 — Observation Space Preservation

### Requirement

The modified environment shall preserve the original observation space without modification.

### Rationale

The assignment specifies stochastic actuator failures rather than altered perception.

### Inputs

Environment state.

### Outputs

Original observation vector.

### Constraints

No observation element may be:

- added
- removed
- reordered
- rescaled

### Acceptance Criteria

Observation dimensions remain identical to LunarLander-v3.

### Verification

VERIFY-001

### Architecture Mapping

COMP-001

---

## FR-003 — Action Space Preservation

### Requirement

The modified environment shall preserve the original discrete action space.

### Rationale

Only executed actions change.

The available actions remain unchanged.

### Inputs

Agent-selected action.

### Outputs

Discrete action.

### Constraints

No action shall be added.

No action shall be removed.

### Acceptance Criteria

Action space equals original LunarLander-v3.

### Verification

VERIFY-001

---

## FR-004 — Stochastic Action Replacement

### Requirement

The environment shall simulate engine failure by replacing the requested action with the "do nothing" action according to the assignment probability.

### Rationale

This is the primary assignment modification.

### Inputs

Requested action.

### Outputs

Executed action.

### Constraints

Replacement probability shall match assignment specification.

### Acceptance Criteria

Observed replacement frequency converges to configured probability.

### Verification

VERIFY-002

---

## FR-005 — Action Replacement Scope

### Requirement

Action replacement shall apply only to engine actions specified by the assignment.

### Rationale

Landing control semantics must remain assignment compliant.

### Acceptance Criteria

Only eligible actions are replaced.

### Verification

VERIFY-002

---

## FR-006 — Agent Transparency

### Requirement

The learning algorithm shall receive no explicit indication that an action replacement occurred.

### Rationale

The assignment evaluates robustness under hidden actuator failures.

### Inputs

Selected action.

### Outputs

Standard environment transition.

### Constraints

No additional observation variable may reveal replacement.

### Acceptance Criteria

Learning algorithm cannot distinguish intentional and replaced actions.

### Verification

VERIFY-002

---

## FR-007 — Fuel Consumption Penalty

### Requirement

The modified reward function shall apply the assignment-defined fuel penalty whenever an engine is executed.

### Rationale

The assignment introduces fuel consumption cost.

### Inputs

Executed action.

### Outputs

Modified reward.

### Acceptance Criteria

Penalty applied exactly as specified.

### Verification

VERIFY-003

---

## FR-008 — Landing Bonus

### Requirement

A successful landing shall receive the assignment-defined landing bonus.

### Rationale

Encourages efficient landings despite fuel penalties.

### Inputs

Terminal landing state.

### Outputs

Modified reward.

### Acceptance Criteria

Landing bonus awarded only for successful landings.

### Verification

VERIFY-003

---

## FR-009 — Reward Modification

### Requirement

Final reward shall equal:

Original reward

plus

Landing bonus

minus

Fuel penalty

where applicable.

### Constraints

Reward modifications shall not alter episode termination.

### Acceptance Criteria

Reward computation matches assignment definition.

### Verification

VERIFY-003

---

## FR-010 — Environment Compatibility

### Requirement

The modified environment shall remain fully compatible with existing reinforcement learning pipelines.

### Acceptance Criteria

Existing training engine requires no environment-specific modifications.

### Verification

VERIFY-004

---

## FR-011 — Environment Determinism

### Requirement

When initialized with identical random seeds, stochastic environment behavior shall be reproducible.

### Acceptance Criteria

Repeated executions with identical seeds produce identical replacement sequences.

### Verification

VERIFY-004

---

# 15.2 Reinforcement Learning Requirements

---

## FR-012 — Deep Q-Network Implementation

### Requirement

The repository shall implement the Deep Q-Network algorithm.

### Inputs

Environment transitions.

### Outputs

Learned Q-value policy.

### Constraints

Algorithm shall follow assignment requirements.

### Acceptance Criteria

Training executes successfully.

### Verification

VERIFY-005

### Architecture Mapping

COMP-002

---

## FR-013 — Double Deep Q-Network Implementation

### Requirement

The repository shall implement Double Deep Q-Network.

### Inputs

Environment transitions.

### Outputs

Learned Q-value policy.

### Constraints

Algorithm shall correctly separate action selection from target estimation.

### Acceptance Criteria

Training executes successfully.

### Verification

VERIFY-005

---

## FR-014 — Replay Buffer

### Requirement

Both algorithms shall utilize experience replay.

### Acceptance Criteria

Transitions sampled from replay memory.

### Verification

VERIFY-005

---

## FR-015 — Target Network

### Requirement

Algorithms shall utilize target network stabilization.

### Acceptance Criteria

Target parameters updated according to configuration.

### Verification

VERIFY-005

---

## FR-016 — Shared Training Infrastructure

### Requirement

DQN and DDQN shall execute using a shared training infrastructure.

### Rationale

Ensures experimental fairness.

### Acceptance Criteria

Training pipeline reusable by both algorithms.

### Verification

VERIFY-005

---

# 15.3 Experiment Requirements

---

## FR-017 — Comparative Experiments

### Requirement

Repository shall execute all required comparative experiments defined by the assignment.

### Required Experiments

EXP-001

EXP-002

EXP-003

EXP-004

### Acceptance Criteria

All experiment outputs generated.

### Verification

VERIFY-006

---

## FR-018 — Experiment Reproducibility

### Requirement

Every experiment shall be reproducible using stored configuration and random seed.

### Acceptance Criteria

Repeated execution reproduces equivalent metrics.

### Verification

VERIFY-006

---

## FR-019 — Experiment Artifact Generation

### Requirement

Every experiment shall generate required logs, checkpoints, metrics, and plots.

### Acceptance Criteria

Artifacts stored in documented repository locations.

### Verification

VERIFY-006

---

# 15.4 Evaluation Requirements

---

## FR-020 — Performance Evaluation

### Requirement

Repository shall evaluate trained agents using assignment-required evaluation methodology.

### Outputs

Evaluation metrics.

### Acceptance Criteria

Evaluation completes without retraining.

### Verification

VERIFY-006

---

## FR-021 — Comparative Analysis

### Requirement

Repository shall support comparison between:

- DQN Original
- DQN Modified
- DDQN Original
- DDQN Modified

### Acceptance Criteria

Comparative metrics generated.

### Verification

VERIFY-006

---

## FR-022 — Visualization

### Requirement

Repository shall generate assignment-required visualizations.

### Required Outputs

- Training reward curves
- Comparative performance plots
- Evaluation summaries

### Acceptance Criteria

Plots generated automatically from stored metrics.

### Verification

VERIFY-006

---

# 16. Functional Requirement Dependency Matrix

| Requirement | Depends On |
|-------------|------------|
| FR-001 | None |
| FR-002 | FR-001 |
| FR-003 | FR-001 |
| FR-004 | FR-001 |
| FR-005 | FR-004 |
| FR-006 | FR-004 |
| FR-007 | FR-001 |
| FR-008 | FR-001 |
| FR-009 | FR-007, FR-008 |
| FR-010 | FR-001 |
| FR-011 | FR-004 |
| FR-012 | FR-014, FR-015 |
| FR-013 | FR-014, FR-015 |
| FR-014 | None |
| FR-015 | FR-012, FR-013 |
| FR-016 | FR-012, FR-013 |
| FR-017 | FR-001–FR-016 |
| FR-018 | FR-017 |
| FR-019 | FR-017 |
| FR-020 | FR-017 |
| FR-021 | FR-020 |
| FR-022 | FR-020 |

---

# 17. Non-Functional Requirements

Unlike Functional Requirements, Non-Functional Requirements specify the quality attributes that every implementation shall satisfy.

Non-functional requirements apply across the entire repository.

They shall never conflict with functional requirements.

---

# 17.1 Maintainability

---

## NFR-001 — Modular Repository

### Requirement

The repository shall follow modular software architecture.

### Rationale

Allows future extension without modifying unrelated components.

### Acceptance Criteria

Every package owns one engineering responsibility.

### Verification

VERIFY-007

---

## NFR-002 — Separation of Concerns

### Requirement

Environment logic, learning algorithms, experimentation, evaluation and visualization shall remain independent.

### Acceptance Criteria

No module owns multiple unrelated responsibilities.

### Verification

VERIFY-007

---

## NFR-003 — Low Coupling

### Requirement

Public interfaces shall minimize inter-module dependencies.

### Acceptance Criteria

Components interact only through documented interfaces.

---

## NFR-004 — High Cohesion

### Requirement

Every module shall contain closely related functionality.

### Acceptance Criteria

Module responsibilities remain singular.

---

# 17.2 Reproducibility

---

## NFR-005 — Deterministic Execution

### Requirement

Repository behavior shall be reproducible when identical configuration and random seeds are used.

### Acceptance Criteria

Repeated executions produce equivalent outputs.

### Verification

VERIFY-008

---

## NFR-006 — Configuration Traceability

### Requirement

Every experiment shall record the exact configuration used.

### Acceptance Criteria

Experiment metadata reconstructs execution.

---

## NFR-007 — Seed Traceability

### Requirement

Random seeds shall be persisted.

### Acceptance Criteria

Seed recorded with every experiment.

---

# 17.3 Reliability

---

## NFR-008 — Stable Training

### Requirement

Training shall recover gracefully from recoverable runtime failures.

### Acceptance Criteria

Checkpoint recovery available.

---

## NFR-009 — Checkpoint Integrity

### Requirement

Checkpoint files shall remain version compatible with repository implementation.

### Acceptance Criteria

Saved checkpoints load successfully.

---

## NFR-010 — Experiment Isolation

### Requirement

Independent experiments shall not overwrite one another.

### Acceptance Criteria

Each experiment owns a dedicated output directory.

---

# 17.4 Usability

---

## NFR-011 — Configuration Simplicity

### Requirement

Users shall execute experiments without modifying source code.

### Acceptance Criteria

Configuration performed exclusively through documented configuration files.

---

## NFR-012 — Repository Readability

### Requirement

Repository organization shall be understandable by humans and AI Coding Agents.

### Acceptance Criteria

Directory ownership documented.

---

# 17.5 Performance

---

## NFR-013 — Efficient Replay Buffer

### Requirement

Replay buffer insertion shall execute in constant time.

### Acceptance Criteria

Insertion complexity remains O(1).

---

## NFR-014 — Efficient Evaluation

### Requirement

Evaluation shall reuse trained checkpoints without retraining.

### Acceptance Criteria

Evaluation runtime independent of training duration.

---

# 17.6 Documentation

---

## NFR-015 — Documentation Completeness

### Requirement

Every public repository component shall possess corresponding documentation.

### Acceptance Criteria

No undocumented public interface exists.

---

## NFR-016 — Traceability

### Requirement

Requirements shall remain traceable throughout implementation.

### Acceptance Criteria

Every implementation references originating requirements.

---

# 17.7 Code Quality

---

## NFR-017 — Static Analysis Compliance

### Requirement

Repository shall satisfy configured static analysis tools.

### Acceptance Criteria

Black

Ruff

MyPy

all pass successfully.

---

## NFR-018 — Type Safety

### Requirement

Public interfaces shall provide complete type annotations.

### Acceptance Criteria

No missing public type hints.

---

# 17.8 Extensibility

---

## NFR-019 — Algorithm Extensibility

### Requirement

Future RL algorithms shall be addable without modifying existing algorithm implementations.

### Acceptance Criteria

Inheritance-based architecture supports extension.

---

## NFR-020 — Environment Extensibility

### Requirement

Future environment wrappers shall integrate without modifying training infrastructure.

### Acceptance Criteria

Environment abstraction remains reusable.

---

# 18. Repository Constraints

The following constraints originate from the assignment specification and repository engineering decisions.

---

## CON-001

The project shall use Python.

---

## CON-002

The environment shall be based on Gymnasium LunarLander-v3.

---

## CON-003

Only DQN and DDQN are required.

---

## CON-004

Environment modifications shall remain limited to assignment requirements.

---

## CON-005

Observation space shall remain unchanged.

Reference:

FR-002

---

## CON-006

Action space shall remain unchanged.

Reference:

FR-003

---

## CON-007

Action replacement probability shall follow the assignment specification.

Reference:

FR-004

---

## CON-008

Reward modifications shall remain assignment compliant.

Reference:

FR-007

FR-008

FR-009

---

## CON-009

Comparative experiments shall remain fair.

All compared algorithms shall use identical training conditions except where algorithmic differences require otherwise.

---

## CON-010

Repository organization shall remain modular.

---

## CON-011 — Google Colab Training Execution Boundary

Full DQN and DDQN training, including resumed training and EXP-001 through EXP-004, shall execute exclusively in Google Colab through the controlled training notebook. A human operator shall launch each Colab GPU session.

The controlled notebook shall clone the public repository from `https://github.com/dkumar-23/RL_Lunar-Lander` and check out the exact Git commit recorded for the run before execution. Google Drive shall persist the complete training artifacts. A human operator shall transfer complete artifact bundles for local validation.

Local OpenCode activity is limited to implementation, review, static analysis, unit and bounded integration testing, configuration validation, bounded smoke testing, exactly-one-step learning validation, Colab notebook preparation, artifact validation, evaluation of validated checkpoints, visualization, reporting, and documentation.

The existence, launchability, or static validity of the notebook is not evidence that training or an experiment completed. Training and experiment completion require an executed Colab run, a complete transferred artifact bundle, and successful local validation. Checkpoints, metrics, logs, manifests, completion markers, results, and completion status shall never be fabricated or inferred from preparation-only evidence.

### References

- FR-012 through FR-022
- NFR-005 through NFR-010
- NFR-014
- NFR-016

CON-011 governs execution location, operator authority, and evidence acceptance only. It does not modify the behavior or meaning of any FR or NFR.

---

# 19. Engineering Assumptions

The following assumptions guide repository design.

---

## ASM-001

Gymnasium APIs remain stable.

---

## ASM-002

PyTorch remains the primary deep learning framework.

---

## ASM-003

Each training run occurs in a single Google Colab runtime under CON-011.

---

## ASM-004

Configuration files remain externally editable.

---

## ASM-005

Random seeds are sufficient to reproduce stochastic behavior.

---

## ASM-006

Experiment artifacts remain available for evaluation.

---

## ASM-007

Repository users possess basic Python knowledge.

---

# 20. Assignment Assumptions

Derived directly from assignment interpretation.

---

## ASM-A001

Assignment evaluation prioritizes correctness over optimization.

---

## ASM-A002

Training duration is not part of grading unless explicitly stated.

---

## ASM-A003

Visualization forms part of assignment deliverables.

---

## ASM-A004

Report shall reference experimental evidence.

---

## ASM-A005

Comparison between original and modified environments is mandatory.

---

# 21. Acceptance Criteria

Repository acceptance requires successful completion of all categories.

---

## Functional Acceptance

- FR-001 through FR-022 satisfied.

---

## Non-Functional Acceptance

- NFR-001 through NFR-020 satisfied.

---

## Constraint Acceptance

- CON-001 through CON-011 satisfied.
- CON-011 evidence includes the exact source commit, human-launched Colab execution, complete human-transferred Google Drive bundle, and successful local validation.

---

## Verification Acceptance

- VERIFY-001 through VERIFY-008 completed.

---

## Experiment Acceptance

- EXP-001 through EXP-004 completed.

---

## Documentation Acceptance

All mandatory repository documents complete.

---

## Repository Acceptance

Static analysis passes.

Unit tests pass.

Integration tests pass.

Assignment verification passes.

---

# 22. Primary Use Cases

---

## UC-001

Train DQN on Original Environment

### Primary Actor

Researcher

### Preconditions

Configuration valid.

### Main Flow

1. Load configuration.
2. Human launches the controlled Google Colab GPU notebook.
3. Clone the public repository and check out the exact recorded Git commit.
4. Create original environment.
5. Initialize DQN.
6. Execute training and persist artifacts to Google Drive.
7. Human transfers the complete artifact bundle for local validation.

### Success Condition

Training completes successfully in Colab and the complete transferred artifact bundle passes local validation.

---

## UC-002

Train DQN on Modified Environment

Main flow identical to UC-001 except modified environment wrapper is used.

---

## UC-003

Train DDQN on Original Environment

Identical workflow using DDQN.

---

## UC-004

Train DDQN on Modified Environment

Identical workflow using modified environment.

---

## UC-005

Evaluate Trained Agent

### Preconditions

Checkpoint available.

### Flow

1. Load checkpoint.
2. Disable exploration.
3. Execute evaluation episodes.
4. Compute metrics.
5. Generate plots.

---

## UC-006

Generate Assignment Report

### Flow

1. Collect experiment metrics.
2. Generate plots.
3. Summarize results.
4. Produce report figures.

---

# 23. Actor Definitions

| Actor | Responsibility |
|---------|---------------|
| Student / Human Operator | Launches Colab GPU sessions and transfers complete Google Drive artifact bundles |
| AI Coding Agent | Implements and verifies the repository within the CON-011 local execution boundary |
| Teaching Assistant | Verifies assignment |
| Repository Maintainer | Maintains repository |
| Evaluation Framework | Produces metrics |

---

# 24. Operational Workflow

```
Configuration
      │
      ▼
Environment
      │
      ▼
RL Algorithm
      │
      ▼
Controlled Colab Notebook
      │
      ▼
Human-Launched Training
      │
      ▼
Google Drive Artifact Bundle
      │
      ▼
Human Transfer and Local Validation
      │
      ▼
Validated Checkpoint Evaluation
      │
      ▼
Plots and Report
```

Each stage consumes outputs from the previous stage.

---

# 25. Requirement Traceability Philosophy

Every engineering artifact within the repository shall be traceable back to one or more documented requirements.

Traceability ensures:

- implementation completeness,
- assignment compliance,
- verification completeness,
- experiment reproducibility,
- maintainability,
- grading transparency.

No implementation artifact shall exist without originating requirements.

Likewise, every requirement shall have corresponding implementation and verification artifacts.

---

# 26. Functional Requirement → Architecture Traceability

| Requirement | Primary Component | Supporting Components |
|--------------|-------------------|------------------------|
| FR-001 | COMP-001 | COMP-009 |
| FR-002 | COMP-001 | — |
| FR-003 | COMP-001 | — |
| FR-004 | COMP-001 | COMP-009 |
| FR-005 | COMP-001 | — |
| FR-006 | COMP-001 | COMP-002 |
| FR-007 | COMP-001 | COMP-009 |
| FR-008 | COMP-001 | COMP-009 |
| FR-009 | COMP-001 | — |
| FR-010 | COMP-001 | COMP-005 |
| FR-011 | COMP-001 | COMP-009 |
| FR-012 | COMP-002 | COMP-003, COMP-004 |
| FR-013 | COMP-002 | COMP-003, COMP-004 |
| FR-014 | COMP-003 | COMP-005 |
| FR-015 | COMP-004 | COMP-002 |
| FR-016 | COMP-005 | COMP-002 |
| FR-017 | COMP-005 | COMP-006 |
| FR-018 | COMP-005 | COMP-009 |
| FR-019 | COMP-005 | COMP-007, COMP-008 |
| FR-020 | COMP-006 | COMP-005 |
| FR-021 | COMP-006 | COMP-007 |
| FR-022 | COMP-007 | COMP-008 |

---

# 27. Functional Requirement → Task Traceability

Every functional requirement shall map to one or more implementation tasks.

| Requirement | Primary Task |
|--------------|--------------|
| FR-001 | TASK-001 |
| FR-002 | TASK-002 |
| FR-003 | TASK-003 |
| FR-004 | TASK-004 |
| FR-005 | TASK-005 |
| FR-006 | TASK-006 |
| FR-007 | TASK-007 |
| FR-008 | TASK-008 |
| FR-009 | TASK-009 |
| FR-010 | TASK-010 |
| FR-011 | TASK-011 |
| FR-012 | TASK-020 |
| FR-013 | TASK-030 |
| FR-014 | TASK-015 |
| FR-015 | TASK-016 |
| FR-016 | TASK-040 |
| FR-017 | TASK-050 |
| FR-018 | TASK-051 |
| FR-019 | TASK-052 |
| FR-020 | TASK-060 |
| FR-021 | TASK-061 |
| FR-022 | TASK-062 |

The definitive task specifications are defined in **TASKS.md**.

---

# 28. Functional Requirement → Verification Traceability

Every functional requirement shall possess explicit verification.

| Requirement | Verification |
|--------------|--------------|
| FR-001 | VERIFY-001 |
| FR-002 | VERIFY-001 |
| FR-003 | VERIFY-001 |
| FR-004 | VERIFY-002 |
| FR-005 | VERIFY-002 |
| FR-006 | VERIFY-002 |
| FR-007 | VERIFY-003 |
| FR-008 | VERIFY-003 |
| FR-009 | VERIFY-003 |
| FR-010 | VERIFY-004 |
| FR-011 | VERIFY-004 |
| FR-012 | VERIFY-005 |
| FR-013 | VERIFY-005 |
| FR-014 | VERIFY-005 |
| FR-015 | VERIFY-005 |
| FR-016 | VERIFY-005 |
| FR-017 | VERIFY-006 |
| FR-018 | VERIFY-006 |
| FR-019 | VERIFY-006 |
| FR-020 | VERIFY-006 |
| FR-021 | VERIFY-006 |
| FR-022 | VERIFY-006 |

No functional requirement shall remain unverifiable.

---

# 29. Functional Requirement → Experiment Traceability

The required experiments validate assignment objectives.

| Requirement | Experiment |
|--------------|------------|
| FR-012 | EXP-001 |
| FR-013 | EXP-003 |
| FR-017 | EXP-001–EXP-004 |
| FR-018 | EXP-001–EXP-004 |
| FR-019 | EXP-001–EXP-004 |
| FR-020 | EXP-001–EXP-004 |
| FR-021 | EXP-001–EXP-004 |
| FR-022 | EXP-001–EXP-004 |

Experiment specifications are defined in **EXPERIMENTS.md**.

---

# 30. Non-Functional Requirement Traceability

| NFR | Primary Artifact |
|------|------------------|
| NFR-001 | ARCHITECTURE.md |
| NFR-002 | DESIGN.md |
| NFR-003 | ARCHITECTURE.md |
| NFR-004 | DESIGN.md |
| NFR-005 | EXPERIMENTS.md |
| NFR-006 | WORKFLOW.md |
| NFR-007 | EXPERIMENTS.md |
| NFR-008 | DESIGN.md |
| NFR-009 | DESIGN.md |
| NFR-010 | WORKFLOW.md |
| NFR-011 | CONFIGURATION |
| NFR-012 | README.md |
| NFR-013 | DESIGN.md |
| NFR-014 | EVALUATION.md |
| NFR-015 | Documentation Set |
| NFR-016 | Entire Repository |
| NFR-017 | CODING_STANDARDS.md |
| NFR-018 | CODING_STANDARDS.md |
| NFR-019 | ARCHITECTURE.md |
| NFR-020 | ARCHITECTURE.md |

---

# 31. Requirement Coverage Matrix

Every major repository subsystem shall satisfy defined requirements.

| Subsystem | FR | NFR |
|------------|----|------|
| Environment | FR-001–FR-011 | NFR-001, NFR-002, NFR-020 |
| RL Algorithms | FR-012–FR-016 | NFR-003, NFR-019 |
| Training | FR-017 | NFR-005, NFR-008 |
| Evaluation | FR-020–FR-022 | NFR-014 |
| Experiment Management | FR-017–FR-019 | NFR-006, NFR-007 |
| Documentation | All | NFR-015, NFR-016 |

Coverage shall remain complete throughout repository evolution.

---

# 32. Assignment Compliance Matrix

The repository shall satisfy every mandatory assignment deliverable.

| Assignment Deliverable | Repository Artifact |
|-------------------------|---------------------|
| Modified Environment | COMP-001 |
| DQN Implementation | COMP-002 |
| DDQN Implementation | COMP-002 |
| Comparative Experiments | EXP-001–EXP-004 |
| Evaluation | COMP-006 |
| Plots | COMP-007 |
| Report | REPORT_TEMPLATE.md |
| Source Code | src/ |
| Documentation | docs/ |

Engineering enhancements shall never invalidate assignment compliance.

---

# 33. Engineering Key Performance Indicators (KPIs)

Repository engineering quality shall be evaluated using measurable indicators.

| KPI ID | Description | Target |
|---------|-------------|--------|
| KPI-001 | Functional Requirement Coverage | 100% |
| KPI-002 | Non-Functional Requirement Coverage | 100% |
| KPI-003 | Requirement Traceability | 100% |
| KPI-004 | Static Analysis Compliance | 100% |
| KPI-005 | Unit Test Pass Rate | 100% |
| KPI-006 | Integration Test Pass Rate | 100% |
| KPI-007 | Experiment Reproducibility | 100% |
| KPI-008 | Documentation Coverage | 100% |
| KPI-009 | Architecture Compliance | 100% |
| KPI-010 | Assignment Compliance | 100% |

These KPIs represent repository engineering objectives rather than assignment grading criteria.

---

# 34. Product Success Metrics

The repository shall be considered successful when the following outcomes are achieved.

## Functional Success

All functional requirements implemented.

---

## Experimental Success

All required experiments executed successfully.

---

## Evaluation Success

Required metrics computed.

Required plots generated.

---

## Engineering Success

Repository remains modular.

Repository remains reproducible.

Repository remains maintainable.

---

## Documentation Success

Every implementation artifact documented.

Cross-references validated.

---

## Assignment Success

All mandatory deliverables completed.

No assignment constraint violated.

---

# 35. Product Completion Criteria

The repository shall not be considered complete until every completion criterion is satisfied.

## Implementation

✓ All functional requirements implemented.

✓ All components completed.

✓ Configuration externalized.

---

## Verification

✓ Verification suite passes.

✓ Static analysis passes.

✓ Unit tests pass.

✓ Integration tests pass.

---

## Experimentation

The checklist below states completion criteria; it does not report current completion status. Notebook existence or readiness satisfies none of these items.

✓ EXP-001 completed.

✓ EXP-002 completed.

✓ EXP-003 completed.

✓ EXP-004 completed.

✓ Each run was human-launched in Google Colab from its recorded exact public Git commit.

✓ Each complete Google Drive artifact bundle was transferred and passed local validation.

---

## Evaluation

✓ Required metrics generated.

✓ Comparative analysis completed.

✓ Required plots generated.

---

## Documentation

✓ Documentation synchronized.

✓ Traceability preserved.

✓ Revision history updated.

---

## Submission

✓ Repository builds successfully.

✓ Assignment artifacts generated.

✓ Report completed.

---

# 36. Repository Lifecycle

The expected engineering lifecycle is illustrated below.

```
Assignment Specification
          │
          ▼
Product Requirements
          │
          ▼
Architecture
          │
          ▼
Detailed Design
          │
          ▼
Implementation
          │
          ▼
Verification
          │
          ▼
Experiments
          │
          ▼
Evaluation
          │
          ▼
Report Generation
          │
          ▼
Assignment Submission
```

Every lifecycle stage consumes verified outputs from the preceding stage.

---

# 37. Product Governance Principles

Repository evolution shall adhere to the following governance principles.

## GOV-001

Requirements precede implementation.

---

## GOV-002

Architecture governs implementation.

---

## GOV-003

Documentation is the primary source of truth.

---

## GOV-004

Configuration supersedes hardcoded values.

---

## GOV-005

Verification precedes experimentation.

---

## GOV-006

Experiments precede conclusions.

---

## GOV-007

Engineering improvements shall not alter assignment semantics.

---

# 38. Formal Product Definition of Done

The product is formally complete only when all of the following conditions are simultaneously satisfied.

- All Functional Requirements (FR-001–FR-022) are implemented and verified.
- All Non-Functional Requirements (NFR-001–NFR-020) are satisfied.
- All architecture components are implemented according to documented interfaces.
- All planned experiments (EXP-001–EXP-004) have been executed.
- Every full or resumed training run complied with CON-011.
- Complete Colab artifact bundles were transferred by a human and passed local validation.
- Evaluation metrics and required visualizations have been generated.
- Static analysis, unit tests, integration tests, and assignment verification all pass successfully.
- Repository documentation is complete, internally consistent, and synchronized with the implementation.
- All repository artifacts required for assignment submission have been produced.
- No result or completion claim is based solely on notebook existence, bounded validation output, or fabricated evidence.

Meeting these criteria constitutes successful completion of the repository from both an academic and software engineering perspective.

---

# End of PRD.md
