# Document Metadata

| Field | Value |
|--------|--------|
| Document ID | README-001 |
| Version | 1.1.0 |
| Status | Approved for Implementation |
| Purpose | Primary repository specification and AI-agent entry point |
| Scope | Entire Reinforcement Learning project repository |
| Audience | AI Coding Agents, Software Engineers, Teaching Assistants, Project Reviewers, Research Engineers |
| Dependencies | Assignment Specification, PRD.md, ARCHITECTURE.md, DESIGN.md, TASKS.md |
| Related Documents | CONTEXT.md, AI_INSTRUCTIONS.md, AGENTS.md, PRD.md, CODING_STANDARDS.md, WORKFLOW.md, COMMAND_PERMISSIONS.md |
| Revision History | v1.0.0 — Initial repository specification; v1.1.0 — Added CON-011 Colab authority, evidence status, and corrected navigation references. |

---

# Robust Reinforcement Learning under Stochastic Action Failure

Production-quality implementation of a research-oriented Reinforcement Learning project for **LunarLander-v3** investigating the effect of **stochastic actuator failures** on **Deep Q-Network (DQN)** and **Double Deep Q-Network (DDQN)** learning performance.

This repository is engineered primarily for **AI-assisted software development** and secondarily for human developers.

The documentation contained in this repository is considered the **single source of truth**.

No implementation should contradict these documents.

---

# Repository Status

| Category | Status |
|-----------|---------|
| Assignment and product specification | Documented |
| Software architecture and design | Documented; implementation completion not asserted here |
| AI agent instructions and coding standards | Documented |
| Experiment and evaluation specifications | Documented; execution completion not evidenced here |
| Controlled Colab training notebook | Not present at this revision; preparation pending |
| EXP-001 through EXP-004 | Not complete without transferred, validated Colab artifact bundles |
| Evaluation results and report findings | Not available without validated training artifacts |
| Risk register | Documented |

Status statements are evidence-based. A file, notebook, configuration, or workflow specification may be complete while training and experiments remain incomplete.

---

# Repository Objectives

## Primary Objective

Develop a reproducible reinforcement learning framework capable of experimentally comparing:

- Deep Q Network (DQN)

and

- Double Deep Q Network (DDQN)

under two environments:

- Original LunarLander-v3

- Modified LunarLander-v3 with stochastic engine failures

without violating any assignment constraints.

---

## Secondary Objectives

The repository must also support:

- deterministic experimentation

- reproducible training

- reproducible evaluation

- modular implementation

- extensibility

- AI-assisted software engineering

- automated plotting

- experiment artifact management

- report generation

- assignment reproducibility

---

# Assignment Requirement Coverage

The repository is specified to implement every mandatory requirement described in the assignment specification.

The assignment requires:

| Requirement Area | Specification Coverage |
|------------------|------------------------|
| Custom Gym Wrapper | PRD FR-001 through FR-011 |
| DQN and DDQN Infrastructure | PRD FR-012 through FR-016 |
| Comparative Experiments and Artifacts | PRD FR-017 through FR-019 |
| Evaluation and Visualization | PRD FR-020 through FR-022 |

Engineering additions such as configuration management, repository organization, automated testing, documentation standards, and reproducibility policies are **repository engineering decisions** and are not assignment requirements.

---

# Functional Requirement Traceability

The assignment requirements are normalized as FR-001 through FR-022. `PRD.md` is the sole authority for their definitions and meanings; this README provides navigation only. All architecture, implementation, task, verification, experiment, evaluation, and report artifacts shall reference those identifiers without redefining them.

---

# Non-Functional Requirements

The normalized catalogue is NFR-001 through NFR-020. `PRD.md` is the sole authority for every NFR definition. CON-011 constrains execution location and evidence handling without changing any FR or NFR meaning.

---

# Repository Philosophy

The repository is organized around the following engineering principles.

## Single Source of Truth

Every engineering decision must have exactly one authoritative location.

Duplicate specifications are forbidden.

---

## Separation of Concerns

Each directory owns exactly one responsibility.

Implementation logic must never be mixed with:

- documentation

- generated figures

- experiment outputs

- checkpoints

- reports

---

## AI Readability

Repository organization is optimized for autonomous coding agents.

Every module must expose:

- responsibility

- inputs

- outputs

- dependencies

- ownership

- interfaces

---

## Reproducibility

Every experiment must be reproducible from repository state.

This includes:

- random seeds

- package versions

- hyperparameters

- configuration files

- checkpoints

- evaluation scripts

- exact public Git commit used by Colab

- complete transferred and validated artifact bundle

---

## Configuration over Hardcoding

No implementation shall contain hidden constants.

All configurable values must originate from configuration files.

Examples include:

- learning rate

- replay buffer size

- epsilon schedule

- batch size

- target update interval

- random seed

- plotting frequency

- evaluation interval

---

# Repository Design Goals

The repository is designed for long-term maintainability rather than assignment-only implementation.

Primary design goals include:

COMP-001 Environment Layer

Responsible for all Gymnasium interactions.

COMP-002 Agent Layer

Responsible for reinforcement learning algorithms.

COMP-003 Memory Layer

Responsible for replay buffers.

COMP-004 Neural Network Layer

Responsible for Q-network architectures.

COMP-005 Training Layer

Responsible for optimization.

COMP-006 Evaluation Layer

Responsible for metrics.

COMP-007 Visualization Layer

Responsible for plotting.

COMP-008 Reporting Layer

Responsible for report generation.

COMP-009 Configuration Layer

Responsible for centralized configuration.

COMP-010 Utilities Layer

Responsible for reusable utilities.

---

# High-Level Repository Architecture

```text
                    +-----------------------+
                    | Assignment Document   |
                    +-----------+-----------+
                                |
                                v
                     +----------------------+
                     | Repository Root      |
                     +----------+-----------+
                                |
       ---------------------------------------------------------
       |          |           |          |          |           |
       v          v           v          v          v           v
 Environment   Agents      Training   Evaluation  Reports   Documentation
       |          |           |          |          |           |
       ---------------------------------------------------------
                                |
                                v
                        Experiment Artifacts
```

---

# Repository Organization

```text
repository/
│
├── configs/
├── docs/
├── src/
├── experiments/
├── scripts/
├── tests/
├── reports/
├── outputs/
├── checkpoints/
├── logs/
├── plots/
├── notebooks/
├── assets/
├── requirements/
├── README.md
└── LICENSE
```

Each directory has exactly one responsibility.

Complete directory specifications are defined in **ARCHITECTURE.md**.

---

# Repository Directory Responsibilities

| Directory | Responsibility |
|------------|---------------|
| configs | Configuration files |
| docs | Engineering documentation |
| src | Source code |
| experiments | Experiment definitions |
| tests | Verification |
| reports | Assignment report generation |
| outputs | Generated artifacts |
| checkpoints | Saved models |
| logs | Training logs |
| plots | Generated figures |
| notebooks | Controlled Google Colab training entrypoint; notebook presence alone is not experiment completion |
| assets | Static resources |

Generated artifacts shall never be committed inside source directories.

---

# AI Agent First-Read Order

Every AI coding agent entering the repository shall consume documentation in the following order:

1. README.md
2. CONTEXT.md
3. AI_INSTRUCTIONS.md
4. AGENTS.md
5. PRD.md
6. ARCHITECTURE.md
7. DESIGN.md
8. CODING_STANDARDS.md
9. WORKFLOW.md
10. TASKS.md
11. COMMAND_PERMISSIONS.md
12. EXPERIMENTS.md
13. EVALUATION.md

No implementation should begin before these documents have been processed.

---

# CON-011 Colab Training Boundary

Full DQN and DDQN training, all resumed training, and EXP-001 through EXP-004 run exclusively through `notebooks/train_colab.ipynb` in a human-launched Google Colab GPU session. Local OpenCode does not launch these workloads.

The notebook is the controlled training entrypoint. It shall clone `https://github.com/dkumar-23/RL_Lunar-Lander`, check out the exact public Git commit selected for the run, and persist the complete artifact bundle to Google Drive. A human operator launches the session and transfers the complete bundle for local validation.

Local OpenCode is limited to implementation, review, static analysis, unit and bounded integration tests, configuration validation, bounded smoke tests, exactly-one-step learning validation, notebook preparation, artifact validation, evaluation of validated checkpoints, visualization, reporting, and documentation.

Notebook existence, notebook readiness, smoke output, and exactly-one-step output are not training completion. An experiment is complete only after its Colab run executes, its complete bundle is transferred, and local validation passes. Results, artifacts, and completion status shall never be fabricated.

---

# Supported AI Coding Agents

The repository has been engineered for autonomous development using:

- Claude Code
- OpenCode
- Cursor
- Cline
- Roo Code
- Continue.dev
- GitHub Copilot
- Gemini CLI
- Aider

All documentation is intentionally structured for deterministic parsing by these agents.

---

# Completion Evidence

Repository specifications and notebook preparation describe intended execution; they do not prove execution. Current experiment status shall be derived only from complete, human-transferred Google Drive bundles that pass local artifact validation. Evaluation, plots, and report conclusions shall consume only validated checkpoints and validated stored metrics.
