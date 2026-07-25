# Document Metadata

| Field | Value |
|--------|--------|
| Document ID | CHG-001 |
| Version | 1.0.0 |
| Status | Active |
| Purpose | Provide the authoritative history of repository evolution, implementation milestones, architectural changes, experiment updates, documentation revisions, and release information. |
| Scope | Entire repository lifecycle |
| Audience | AI Coding Agents, Software Engineers, ML Engineers, Teaching Assistants, Repository Maintainers |
| Dependencies | DECISIONS.md, TASKS.md, WORKFLOW.md |
| Related Documents | README.md, ARCHITECTURE.md, EXPERIMENTS.md |
| Revision History | v1.0.0 — Initial Change Management Policy |

---

# 1. Purpose

The changelog is the **historical record** of repository evolution.

It shall record:

- implementation milestones
- architectural modifications
- experiment additions
- evaluation methodology changes
- documentation revisions
- dependency updates
- bug fixes
- releases

The changelog shall **never** contain planned work.

Future work belongs in TASKS.md.

---

# 2. Change Management Philosophy

Repository evolution shall be transparent.

Every significant change shall be:

- documented
- traceable
- reviewable
- reproducible

No significant modification shall occur without an accompanying changelog entry.

---

# 3. Versioning Policy

The repository adopts **Semantic Versioning (SemVer)**.

```
MAJOR.MINOR.PATCH
```

Example:

```
1.0.0
1.1.0
1.1.1
2.0.0
```

---

## MAJOR

Increment when:

- architecture changes
- public interfaces change
- incompatible repository structure changes
- assignment scope changes

---

## MINOR

Increment when:

- new experiments are added
- new repository features are implemented
- evaluation capabilities expand
- visualization features expand

---

## PATCH

Increment when:

- bugs are fixed
- documentation corrected
- tests improved
- configuration defaults updated
- refactoring with no behavior change

---

# 4. Change Categories

Every entry shall belong to one or more categories.

| Category | Identifier |
|------------|------------|
| Architecture | CAT-C01 |
| Implementation | CAT-C02 |
| Documentation | CAT-C03 |
| Experiments | CAT-C04 |
| Evaluation | CAT-C05 |
| Visualization | CAT-C06 |
| Reporting | CAT-C07 |
| Dependencies | CAT-C08 |
| Bug Fix | CAT-C09 |
| Repository Maintenance | CAT-C10 |

---

# 5. Entry Format

Every change entry shall include:

```
Version

↓

Date

↓

Category

↓

Summary

↓

Detailed Changes

↓

Affected Components

↓

Related Requirements

↓

Related Tasks

↓

Related ADRs
```

---

# 6. Initial Repository Release

## Version

1.0.0

## Status

Initial Development Baseline

---

### Summary

Initial implementation of the modified LunarLander reinforcement learning repository.

---

### Included Components

- repository structure
- documentation suite
- environment framework
- DQN implementation
- Double DQN implementation
- replay buffer
- training engine
- evaluation engine
- visualization engine
- reporting engine

---

### Related ADRs

ADR-001 through ADR-013

---

### Related Tasks

TASK-001 through TASK-045

---

# 7. Documentation Updates

Documentation changes shall reference affected documents.

Example:

```
Version

1.0.1

Category

Documentation

Changes

Updated ARCHITECTURE.md

Updated DESIGN.md

Corrected interface specification

Updated traceability matrix
```

Documentation updates shall never silently alter architectural intent.

---

# 8. Architecture Changes

Architecture changes require:

- new ADR
- changelog entry
- architecture update
- traceability review

Example:

```
Version

2.0.0

Category

Architecture

Summary

Introduced plugin architecture.

Related ADR

ADR-014
```

---

# 9. Experiment Changes

Experiment-related entries shall include:

- Experiment Identifier
- motivation
- configuration impact
- evaluation impact

Example:

```
Version

1.2.0

Added

EXP-011

Hyperparameter sensitivity study

Updated experiment manifest schema
```

---

# 10. Evaluation Changes

Evaluation updates shall identify:

- new metrics
- removed metrics
- statistical methodology changes
- comparison updates

Example:

```
Version

1.3.0

Added

Median reward metric

Updated comparison report generation
```

---

# 11. Dependency Updates

Dependency entries shall record:

| Item | Required |
|------|----------|
| Package | Yes |
| Previous Version | Yes |
| New Version | Yes |
| Reason | Yes |

Example:

```
PyTorch

2.4.0

→

2.5.0

Reason

Performance improvements
```

---

# 12. Bug Fix Entries

Bug fixes shall include:

- defect summary
- root cause
- affected components
- verification method

Example:

```
Version

1.0.2

Category

Bug Fix

Resolved incorrect target network synchronization interval.

Affected

Training Engine

Verification

VERIFY-024
```

---

# 13. Repository Maintenance

Maintenance entries include:

- directory restructuring
- tooling updates
- CI improvements
- linting configuration
- formatting changes

Behavior-preserving maintenance shall increment PATCH version only.

---

# 14. Release Checklist

Before creating a release entry verify:

- documentation synchronized
- tests passing
- experiments reproducible
- evaluation complete
- traceability valid
- report assets generated

---

# 15. Release History Table

| Version | Status | Summary |
|----------|--------|---------|
| 1.0.0 | Initial | First complete repository implementation |
| 1.0.1 | Reserved | Documentation corrections |
| 1.1.0 | Reserved | Functional enhancements |
| 2.0.0 | Reserved | Future architectural evolution |

Reserved versions are placeholders only and shall not be used until released.

---

# 16. Traceability Requirements

Every changelog entry shall reference, where applicable:

- Requirement IDs
- Task IDs
- ADR IDs
- Experiment IDs
- Evaluation IDs

Example:

```
Requirements

FR-012

Tasks

TASK-021

ADR

ADR-006

Experiment

EXP-004
```

---

# 17. AI Coding Agent Responsibilities

AI Coding Agents shall:

- update the changelog whenever implementation behavior changes
- avoid recording unfinished work
- preserve chronological ordering
- reference related ADRs and Tasks
- distinguish documentation-only changes from implementation changes

Agents shall **not** modify historical entries except to correct factual inaccuracies.

---

# 18. Definition of Done

The changelog satisfies repository requirements when:

- every released version is documented
- architectural changes reference ADRs
- implementation changes reference Tasks
- experiment changes reference Experiment IDs
- repository history is chronological
- change records are complete and reproducible
- AI Coding Agents can determine repository evolution without reviewing Git history

---

# 19. Current Unreleased Documentation Changes

## Date

2026-07-26

## Status

Unreleased

## Category

Architecture, Documentation, Reporting, Repository Maintenance

## Summary

Documented the Colab-exclusive Full Training boundary and the Training Artifact Bundle validation and promotion contract.

## Detailed Changes

- Added ADR-014 requiring human-started Colab Full Training at an exact Git commit while limiting local execution to bounded testing, One-Step Learning Validation, artifact validation, evaluation of Validated Checkpoints, and reporting.
- Added ADR-015 defining Google Drive bundle persistence, local validation, Validated Checkpoints, and Artifact Promotion.
- Added RISK-018 through RISK-025 and strengthened existing configuration, artifact, metadata, and dependency drift mitigations.
- Added validated Colab provenance requirements to the report specification.
- Added execution-boundary and artifact-contract terminology to the glossary.

## Affected Documents

- DECISIONS.md
- RISKS.md
- REPORT_TEMPLATE.md
- GLOSSARY.md
- CHANGELOG.md

## Related ADRs

ADR-014

ADR-015

## Evidence Statement

This entry records documentation changes only. It does not claim that Full Training, evaluation, artifact validation, or result generation has occurred.

# End of CHANGELOG.md
