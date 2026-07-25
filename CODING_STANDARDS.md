# Document Metadata

| Field | Value |
|--------|--------|
| Document ID | CODESTD-001 |
| Version | 1.1.0 |
| Status | Approved for Implementation |
| Purpose | Define mandatory coding standards, software engineering practices, repository conventions, implementation rules, and quality requirements governing every source file in the repository. |
| Scope | Entire Python codebase, configuration files, scripts, tests, documentation generators, experiment pipelines, and supporting tooling. |
| Audience | AI Coding Agents, Software Engineers, ML Engineers, Teaching Assistants, Code Reviewers |
| Dependencies | README.md, CONTEXT.md, AI_INSTRUCTIONS.md, AGENTS.md |
| Related Documents | ARCHITECTURE.md, DESIGN.md, WORKFLOW.md, TASKS.md, COMMAND_PERMISSIONS.md |
| Revision History | v1.0.0 — Initial Repository Coding Standard; v1.1.0 — Added implementation standards enforcing the CON-011 Colab execution boundary. |

---

# 1. Purpose

This document establishes the authoritative software engineering standard for every implementation within the repository.

Unlike language-specific style guides, this document specifies:

- repository architecture conventions,
- implementation constraints,
- coding patterns,
- interface design,
- Python standards,
- reinforcement learning implementation standards,
- testing conventions,
- documentation requirements,
- quality gates.

Compliance is mandatory.

---

# 2. Scope

These standards apply to every implementation artifact including:

- Python source code
- Configuration loaders
- YAML files
- Training pipelines
- Evaluation modules
- Experiment definitions
- Plot generation
- Utility modules
- Tests
- Build scripts
- CLI entry points
- Controlled Colab notebooks

Generated artifacts are excluded.

---

# 3. Engineering Philosophy

The repository adopts the following engineering principles.

## CP-001

Readability over cleverness.

---

## CP-002

Determinism over convenience.

---

## CP-003

Configuration over hardcoding.

---

## CP-004

Composition over duplication.

---

## CP-005

Explicit interfaces over implicit behaviour.

---

## CP-006

Small reusable modules.

---

## CP-007

Single responsibility.

---

## CP-008

Traceable implementations.

---

## CP-009

Documented behaviour.

---

## CP-010

Repository consistency over individual preference.

---

# 4. Repository Language Standards

The repository standardizes on the following technologies.

| Category | Standard |
|-----------|----------|
| Language | Python |
| Minimum Version | 3.11 |
| Primary ML Framework | PyTorch |
| Environment API | Gymnasium |
| Numerical Computing | NumPy |
| Plotting | Matplotlib |
| Configuration | YAML |
| Testing | PyTest |
| Static Analysis | Ruff + MyPy |
| Formatting | Black |

Alternative implementations require explicit architectural approval.

---

# 5. Repository Directory Rules

Every directory owns exactly one engineering responsibility.

| Directory | Responsibility |
|------------|---------------|
| src/environment | Environment implementation |
| src/agents | RL algorithms |
| src/networks | Neural networks |
| src/memory | Replay buffer |
| src/training | Optimization |
| src/evaluation | Metrics |
| src/visualization | Plot generation |
| src/utils | Shared utilities |
| configs | Configuration |
| scripts | CLI automation |
| notebooks | Controlled Google Colab training entrypoint |
| tests | Verification |

Responsibilities shall not overlap.

---

# 6. Source File Rules

Each source file shall own one primary concern.

Correct examples:

```
dqn_agent.py

ddqn_agent.py

replay_buffer.py

trainer.py

metrics.py
```

Incorrect examples:

```
trainer_and_plotting.py

network_utils_metrics.py

environment_training.py
```

Mixed responsibilities are prohibited.

---

# 7. Python Package Organization

Every package shall expose a clear public API.

Example:

```
agents/

    __init__.py

    base_agent.py

    dqn_agent.py

    ddqn_agent.py
```

Internal helper modules shall not expose unnecessary symbols.

---

# 8. Import Hierarchy

Imports shall follow a deterministic order.

```
Standard Library

↓

Third-party Libraries

↓

Repository Packages

↓

Relative Imports
```

Example:

```python
import random
from pathlib import Path

import gymnasium as gym
import numpy as np
import torch

from src.memory.replay_buffer import ReplayBuffer
from src.networks.q_network import QNetwork

from .base_agent import BaseAgent
```

Wildcard imports are prohibited.

---

# 9. Import Restrictions

The following practices are forbidden.

```
from module import *
```

```
import everything
```

```
circular imports
```

```
runtime path modification
```

```
sys.path.append(...)
```

---

# 10. Naming Conventions

Repository-wide naming standards.

## Packages

Lowercase.

Example

```
environment

training

evaluation
```

---

## Modules

snake_case.py

Examples

```
reward_function.py

checkpoint_manager.py

plot_metrics.py
```

---

## Classes

PascalCase.

Examples

```
DQNAgent

ReplayBuffer

TrainingEngine

QNetwork
```

---

## Functions

snake_case()

Examples

```
train_episode()

update_target_network()

compute_loss()

sample_batch()
```

---

## Variables

snake_case

```
episode_reward

learning_rate

failure_probability
```

---

## Constants

UPPER_CASE

```
DEFAULT_BATCH_SIZE

MAX_EPISODES

LANDING_REWARD
```

---

## Private Members

Leading underscore.

```
_hidden_state

_initialize_weights()
```

---

# 11. File Naming Policy

Files shall reflect their primary responsibility.

Examples

```
wrapper.py

trainer.py

metrics.py

logger.py

config_loader.py
```

Avoid ambiguous names.

Incorrect

```
utils2.py

misc.py

helper.py

new.py

final.py
```

---

# 12. Class Design Standards

Every class shall represent one conceptual entity.

Correct

```
ReplayBuffer

TrainingEngine

EnvironmentWrapper
```

Incorrect

```
TrainingEvaluationReplayManager
```

Large multi-purpose classes are prohibited.

---

# 13. Constructor Rules

Constructors shall perform only initialization.

Constructors shall not:

- train models,
- launch Colab sessions,
- allocate datasets,
- start experiments,
- create files,
- perform evaluation,
- launch threads.

Constructors may:

- validate configuration,
- initialize members,
- allocate lightweight objects.

---

# 14. Function Design Standards

Functions shall satisfy:

Single responsibility.

Small scope.

Deterministic behaviour.

Documented inputs.

Documented outputs.

Predictable exceptions.

---

Recommended function size

20–40 lines.

Maximum recommended size

75 lines.

Functions exceeding this threshold should be decomposed.

---

# 15. Function Signature Policy

Public functions shall include:

- type hints,
- descriptive parameter names,
- explicit return types.

Example

```python
def train_episode(
    agent: BaseAgent,
    environment: gym.Env,
    replay_buffer: ReplayBuffer,
) -> EpisodeMetrics:
```

Untyped public functions are prohibited.

---

# 16. Type Hint Standards

Type hints are mandatory.

Required for:

- public functions,
- methods,
- constructors,
- return values,
- class attributes.

Preferred typing constructs

```
Sequence

Mapping

Iterable

Optional

Callable

Protocol

TypeAlias
```

Avoid generic `Any` unless unavoidable.

---

# 17. Dataclass Policy

Structured immutable data should use dataclasses.

Appropriate examples:

```
TrainingMetrics

EvaluationResult

EpisodeStatistics

ExperimentMetadata
```

Mutable algorithmic state should remain regular classes.

---

# 18. Enumeration Standards

Finite categorical values shall use Enum.

Examples

```
AlgorithmType

EnvironmentType

ExperimentStatus

DeviceType
```

Avoid string literals for state management.

---

# 19. Documentation Standards

Every public module shall contain:

- module description,
- ownership,
- dependencies,
- public interface,
- related components.

Every public class shall include:

- responsibility,
- usage,
- dependencies.

Every public method shall include:

- purpose,
- parameters,
- returns,
- exceptions.

Docstrings shall follow the Google Python Style Guide.

---

# 20. Comment Policy

Comments explain **why**, not **what**.

Appropriate:

```python
# The target network is updated periodically to stabilize
# temporal-difference learning and reduce oscillation.
```

Inappropriate:

```python
# Increment i
i += 1
```

Self-explanatory code is preferred over excessive comments.

---

# 21. Code Readability Standards

Code shall emphasize clarity.

Preferred:

- descriptive identifiers,
- short functions,
- meaningful abstractions,
- explicit control flow.

Avoid:

- deeply nested conditionals,
- cryptic variable names,
- excessive inline lambdas,
- implicit behaviour.

Maximum recommended nesting depth: 3 levels.

---

# 22. Exception Handling Standards

Exceptions are part of the public interface.

Every exception shall:

- communicate a single failure,
- preserve debugging information,
- avoid masking root causes,
- remain deterministic,
- provide actionable messages.

---

## EH-001

Catch only exceptions that can be meaningfully handled.

Correct

```python
try:
    config = load_config(path)
except FileNotFoundError as exc:
    raise ConfigurationError(
        f"Configuration file not found: {path}"
    ) from exc
```

Incorrect

```python
try:
    ...
except Exception:
    pass
```

---

## EH-002

Never silently ignore exceptions.

Forbidden

```python
except Exception:
    return
```

---

## EH-003

Every public API shall document raised exceptions.

Example

```python
Raises:
    ConfigurationError:
        Invalid configuration file.

    ValueError:
        Invalid replay buffer capacity.
```

---

## EH-004

Repository-defined exceptions shall inherit from common base classes.

Example hierarchy

```
RepositoryError

├── ConfigurationError
├── EnvironmentError
├── ReplayBufferError
├── TrainingError
├── EvaluationError
├── CheckpointError
└── ExperimentError
```

---

# 23. Logging Standards

Logging is mandatory for every major repository subsystem.

Logging supports:

- debugging,
- experiment reproducibility,
- grading verification,
- engineering diagnostics.

---

## LG-001

Never use `print()` inside production modules.

Use centralized logging.

---

## LG-002

Every logger shall originate from repository logging utilities.

Example

```python
logger = get_logger(__name__)
```

---

## LG-003

Log Levels

| Level | Usage |
|---------|-------|
| DEBUG | Internal algorithm diagnostics |
| INFO | Experiment progress |
| WARNING | Recoverable anomalies |
| ERROR | Recoverable failures |
| CRITICAL | Repository cannot continue |

---

## LG-004

Training Logs

Each training episode should record:

- episode number,
- episode reward,
- moving average reward,
- epsilon,
- average loss,
- learning rate,
- replay buffer size,
- elapsed time.

---

## LG-005

Evaluation Logs

Evaluation shall record:

- average reward,
- landing success,
- crash count,
- timeout count,
- average episode length,
- average predicted Q-value.

---

## LG-006

Environment Verification Logs

Verification shall record:

- requested actions,
- executed actions,
- replaced actions,
- replacement ratio,
- fuel penalties,
- landing bonus events.

---

## LG-007

Checkpoint Logs

Each checkpoint shall log:

- experiment identifier,
- checkpoint number,
- episode,
- timestamp,
- configuration hash,
- random seed.

---

# 24. Configuration Management Standards

Configuration is the single source of runtime parameters.

---

## CFG-001

Every configurable value must exist in configuration files.

Examples:

```
learning_rate

batch_size

gamma

seed

epsilon_decay

buffer_size

failure_probability

fuel_penalty

landing_bonus
```

---

## CFG-002

Configuration values shall never be duplicated.

Correct

```
configs/training.yaml
```

Incorrect

```
training.py

evaluation.py

wrapper.py
```

containing the same value.

---

## CFG-003

Configuration loading shall occur once.

Configuration objects are immutable after validation.

---

## CFG-004

Configuration validation is mandatory.

Validation shall verify:

- required fields,
- numeric ranges,
- supported algorithms,
- supported environments,
- filesystem paths.

---

# 25. Reinforcement Learning Implementation Standards

All reinforcement learning implementations shall satisfy assignment requirements while maintaining modularity.

---

## RL-001

Algorithms shall inherit from a common abstract base class.

```
BaseAgent

├── DQNAgent

└── DDQNAgent
```

---

## RL-002

Common logic shall reside in the base implementation.

Duplicated code between DQN and DDQN is prohibited.

---

## RL-003

Algorithm-specific behavior shall override only the necessary methods.

Example:

```
compute_target_q_values()
```

---

## RL-004

Target network synchronization shall be isolated.

No training logic shall directly manipulate target parameters.

---

## RL-005

Action selection shall be independent of optimization logic.

---

## RL-006

Replay buffer access shall occur through its public interface.

Direct internal access is prohibited.

---

## RL-007

Algorithms shall never directly manipulate Gymnasium internals.

Environment interactions shall occur exclusively through the public environment API.

---

# 26. Neural Network Standards

Neural networks shall remain independent from reinforcement learning algorithms.

---

## NN-001

Networks compute Q-values only.

Networks shall never:

- update replay buffers,
- compute rewards,
- execute optimizers,
- manage checkpoints.

---

## NN-002

Weight initialization shall be deterministic.

Initialization strategy shall be documented.

---

## NN-003

Forward passes shall contain no side effects.

---

## NN-004

Model architecture shall be configurable.

Hidden layer sizes shall not be hardcoded.

---

## NN-005

Networks shall inherit from:

```python
torch.nn.Module
```

---

## NN-006

Device movement shall occur outside model definitions.

---

# 27. Replay Buffer Standards

Replay buffer implementation shall remain reusable.

---

## RB-001

Replay buffer stores transitions only.

---

## RB-002

Replay buffer performs no optimization.

---

## RB-003

Replay buffer performs no preprocessing.

---

## RB-004

Sampling shall be deterministic when seeded.

---

## RB-005

Capacity shall be configurable.

---

## RB-006

Replay buffer interface

```
push()

sample()

clear()

size()

capacity()
```

Internal implementation details remain private.

---

# 28. Environment Wrapper Standards

The environment wrapper is the only module permitted to modify environment behavior.

---

## ENV-001

Wrapper preserves observation space.

Reference:

FR-002

---

## ENV-002

Wrapper preserves action space.

Reference:

FR-003

---

## ENV-003

Wrapper applies stochastic action replacement.

Reference:

FR-004

FR-005

---

## ENV-004

Wrapper hides action replacement from the learning algorithm.

Reference:

FR-006

---

## ENV-005

Wrapper computes reward modifications only.

No learning logic shall exist inside the wrapper.

---

## ENV-006

Wrapper shall remain compatible with Gymnasium interfaces.

---

## ENV-007

Wrapper shall expose identical reset() and step() signatures.

---

# 29. Training Loop Standards

Training engine responsibilities include:

- episode execution,
- optimization scheduling,
- logging,
- checkpointing,
- evaluation scheduling.

Training engine shall not:

- generate plots,
- modify configuration,
- alter environment semantics.

Under CON-011, full and resumed DQN/DDQN training and EXP-001 through EXP-004 shall execute only in a human-launched Google Colab GPU session. Local OpenCode may invoke only bounded smoke and exactly-one-step learning validation entrypoints; those entrypoints shall enforce their limits internally and shall not emit promotable experiment artifacts.

---

## TRAIN-001

Training loop controls episode lifecycle.

---

## TRAIN-002

Optimization frequency shall be configurable.

---

## TRAIN-003

Evaluation frequency shall be configurable.

---

## TRAIN-004

Checkpoint frequency shall be configurable.

---

## TRAIN-005

Episode termination shall respect Gymnasium termination semantics.

---

## TRAIN-006

Training metrics shall be accumulated separately from evaluation metrics.

---

## TRAIN-007

`notebooks/train_colab.ipynb` is the controlled full-training entrypoint. It shall clone `https://github.com/dkumar-23/RL_Lunar-Lander`, check out an exact public Git commit, and record that commit in run metadata before training.

---

## TRAIN-008

The notebook shall persist complete run artifacts to Google Drive. Resume shall use only a validated checkpoint with matching experiment identity, configuration, seed, and source commit.

---

## TRAIN-009

A human operator shall launch Colab GPU sessions and transfer complete artifact bundles for local validation. Local code shall reject incomplete or inconsistent bundles before checkpoint evaluation.

---

## TRAIN-010

Notebook existence, notebook execution readiness, bounded smoke output, and exactly-one-step output shall never create training completion markers or promotable experiment evidence.

---

# 30. Evaluation Standards

Evaluation is independent from training.

---

## EVAL-001

Evaluation shall disable exploration.

---

## EVAL-002

Evaluation shall never modify replay buffer.

---

## EVAL-003

Evaluation shall never update network weights.

---

## EVAL-004

Evaluation shall use frozen checkpoints.

---

## EVAL-005

Evaluation metrics shall remain reproducible.

---

# 31. Visualization Standards

Visualization consumes stored metrics only.

Visualization shall never:

- retrain models,
- evaluate agents,
- modify checkpoints.

Generated plots shall include:

- title,
- axes,
- legend,
- units,
- experiment identifier.

---

# 32. Testing Standards

Repository testing consists of multiple verification layers.

## Static Analysis

- Ruff
- Black
- MyPy

---

## Unit Tests

Every public component shall possess unit tests.

Examples

```
ReplayBuffer

Wrapper

Network

Configuration Loader
```

---

## Integration Tests

Examples

```
Training Pipeline

Evaluation Pipeline

Checkpoint Pipeline
```

Local training-related integration tests shall be bounded. Exactly-one-step validation shall perform no more than one learning update, and smoke tests shall use explicit limits that prevent them from becoming full or resumed training.

---

## Assignment Verification

Examples

```
15% action replacement

Fuel penalty

Landing bonus

Plot generation
```

---

# 33. Repository Quality Gates

Every implementation batch shall satisfy:

| Quality Gate | Requirement |
|--------------|-------------|
| QG-001 | Builds successfully |
| QG-002 | Static analysis passes |
| QG-003 | Formatting passes |
| QG-004 | Type checking passes |
| QG-005 | Unit tests pass |
| QG-006 | Integration tests pass |
| QG-007 | Assignment verification passes |
| QG-008 | Documentation synchronized |
| QG-009 | Architecture preserved |
| QG-010 | Traceability maintained |
| QG-011 | CON-011 local execution boundary enforced |
| QG-012 | Imported Colab bundle validated before checkpoint evaluation |

Failure of any gate blocks repository integration.

---

# 34. Performance Engineering Standards

Performance optimization shall always preserve:

- assignment correctness,
- reproducibility,
- readability,
- maintainability.

Premature optimization is prohibited.

Optimization shall occur only after correctness has been verified.

---

## PERF-001

Correctness has higher priority than execution speed.

---

## PERF-002

Deterministic execution has higher priority than parallel execution.

---

## PERF-003

Readability has higher priority than micro-optimizations.

---

## PERF-004

Configuration-driven optimization is preferred over source-code modification.

---

## PERF-005

Every optimization shall remain measurable.

Undocumented optimizations are prohibited.

---

# 35. Computational Complexity Guidelines

Repository algorithms shall document expected computational complexity where appropriate.

Examples include:

| Component | Expected Complexity |
|------------|--------------------|
| Replay Buffer Insertion | O(1) |
| Replay Buffer Sampling | O(batch_size) |
| Forward Pass | O(network_size) |
| Target Network Update | O(parameter_count) |
| Evaluation Episode | O(environment_steps) |

Complexity shall not be unnecessarily increased through implementation choices.

---

# 36. Memory Management Standards

Memory consumption shall remain predictable.

---

## MEM-001

Avoid unnecessary tensor duplication.

---

## MEM-002

Reuse allocated objects whenever practical.

---

## MEM-003

Release temporary tensors after use.

---

## MEM-004

Avoid storing duplicated experiment metrics.

---

## MEM-005

Replay Buffer shall store transitions efficiently.

---

## MEM-006

Training history shall be streamed to persistent storage where appropriate instead of indefinitely retained in memory.

---

# 37. Filesystem Standards

Repository filesystem organization is considered part of the architecture.

---

## FS-001

Source code shall never generate files inside:

```
src/
```

---

## FS-002

Generated artifacts belong only inside:

```
outputs/

logs/

plots/

checkpoints/

reports/
```

Human-transferred Colab bundles shall enter only through the documented incoming artifact location. Validation shall not mutate the imported payload.

---

## FS-003

Temporary files shall be written only to documented temporary directories.

---

## FS-004

Repository-relative paths shall be preferred.

Absolute paths are prohibited except for documented Google Colab and Google Drive mount paths required by CON-011. Those paths shall remain isolated to the controlled notebook or its runtime adapter.

---

## FS-005

Filesystem operations shall use:

```python
pathlib.Path
```

String-based path manipulation is discouraged.

---

# 38. Dependency Management Standards

Dependencies shall remain minimal.

Every dependency shall have a documented purpose.

---

## DEP-001

Unused dependencies are prohibited.

---

## DEP-002

Indirect dependency usage should be minimized.

---

## DEP-003

Repository shall pin compatible dependency versions.

---

## DEP-004

Experimental dependencies shall remain isolated from production dependencies.

---

## DEP-005

Platform-specific dependencies shall be documented.

---

## DEP-006

Dependencies requiring internet connectivity during runtime are prohibited unless explicitly documented.

---

# 39. External Library Usage

The repository standardizes on the following primary libraries.

| Category | Approved Library |
|-----------|------------------|
| Reinforcement Learning Environment | Gymnasium |
| Deep Learning | PyTorch |
| Numerical Computing | NumPy |
| Plotting | Matplotlib |
| Configuration | PyYAML |
| Logging | Python logging |
| Testing | PyTest |

Alternative libraries require architectural approval.

---

# 40. Randomness and Reproducibility Standards

Reproducibility is a first-class engineering requirement.

---

## REP-001

Every experiment shall specify a random seed.

---

## REP-002

All random generators shall be initialized before environment creation.

---

## REP-003

Experiment configuration shall record the random seed.

---

## REP-004

Evaluation shall reuse documented seeds when deterministic comparison is required.

---

## REP-005

Random initialization shall occur through a centralized repository utility.

Independent initialization is prohibited.

---

## REP-006

Changing a seed shall create a new experiment identifier.

---

# 41. Experiment Artifact Standards

Experiment artifacts shall be immutable after generation.

---

## ART-001

Every experiment receives a unique identifier.

Example:

```
EXP-001

EXP-002

EXP-003

EXP-004
```

---

## ART-002

Each experiment directory shall contain:

```
configuration/

metrics/

plots/

logs/

checkpoints/

metadata.json
```

---

## ART-003

Artifacts shall include version information.

---

## ART-004

Metrics shall be stored separately from plots.

---

## ART-005

Generated reports shall reference experiment identifiers rather than filenames.

---

# 42. Metadata Standards

Every experiment shall generate machine-readable metadata.

Required metadata includes:

- experiment identifier,
- algorithm,
- environment,
- repository version,
- configuration hash,
- random seed,
- timestamp,
- dependency versions,
- execution duration,
- exact public Git commit,
- Colab runtime and dependency metadata,
- artifact bundle validation status.

Metadata enables deterministic experiment reconstruction.

---

# 43. Security Standards

Although this repository is not security-critical, secure engineering practices shall be followed.

---

## SEC-001

No credentials shall exist inside source code.

---

## SEC-002

Configuration files containing secrets shall never be committed.

---

## SEC-003

User input shall be validated.

---

## SEC-004

Filesystem operations shall validate destination paths.

---

## SEC-005

Dynamic code execution is prohibited.

Examples:

```python
eval()

exec()
```

---

## SEC-006

Downloading executable code during runtime is prohibited except for the controlled CON-011 notebook clone from `https://github.com/dkumar-23/RL_Lunar-Lander`. The notebook shall check out an exact Git commit before importing or executing repository code.

---

# 44. Command Line Interface Standards

Repository scripts shall expose consistent command-line interfaces.

Preferred implementation:

```
argparse
```

Every CLI shall support:

```
--config

--seed

--output

--device

--help
```

Error messages shall be descriptive.

Full-training and experiment entrypoints shall fail closed outside Google Colab. Local validation entrypoints shall enforce bounded smoke or exactly-one-step semantics and shall not expose flags that silently remove those limits.

---

# 45. Static Analysis Standards

Every source file shall satisfy static verification.

Mandatory tools:

| Tool | Responsibility |
|------|----------------|
| Black | Formatting |
| Ruff | Linting |
| MyPy | Type Analysis |

Repository integration shall fail if static analysis fails.

---

# 46. AI Code Generation Standards

This repository is optimized for autonomous implementation.

AI-generated code shall satisfy all repository standards without requiring post-generation cleanup.

---

## AI-001

Generate complete implementations.

Placeholder implementations are prohibited.

---

## AI-002

Every generated file shall satisfy architectural ownership.

---

## AI-003

Generated implementations shall preserve documented interfaces.

---

## AI-004

Generated source shall include meaningful names.

---

## AI-005

AI-generated code shall never infer undocumented repository behaviour.

---

## AI-006

Generated implementations shall remain deterministic.

---

## AI-007

Generated code shall never bypass repository abstractions.

---

## AI-008

AI-generated modifications shall update documentation when interfaces change.

---

## AI-009

AI Coding Agents shall not launch full or resumed DQN/DDQN training or EXP-001 through EXP-004 from the local OpenCode environment.

---

## AI-010

AI Coding Agents shall not fabricate checkpoints, metrics, logs, manifests, completion markers, results, or experiment status. Notebook preparation is not training completion.

---

# 47. Code Review Standards

Every completed implementation shall undergo repository-level review.

Review checklist:

## Architecture

- [ ] Component ownership preserved.
- [ ] Dependency direction preserved.
- [ ] Repository organization maintained.

---

## Source Code

- [ ] Type hints complete.
- [ ] Docstrings complete.
- [ ] Naming conventions satisfied.
- [ ] No duplicated logic.
- [ ] No dead code.
- [ ] No unused imports.

---

## Functionality

- [ ] Functional requirements implemented.
- [ ] Assignment constraints preserved.
- [ ] Configuration externalized.
- [ ] Logging implemented.
- [ ] CON-011 boundary enforced for full, resumed, smoke, and exactly-one-step entrypoints.

---

## Verification

- [ ] Unit tests pass.
- [ ] Integration tests pass.
- [ ] Static analysis passes.
- [ ] Imported checkpoints are evaluated only after complete bundle validation passes.

---

## Documentation

- [ ] Documentation synchronized.
- [ ] Cross references remain valid.
- [ ] Traceability preserved.

---

# 48. Repository Maintainability Standards

Maintainability shall guide implementation decisions.

Repository code shall prioritize:

- modularity,
- readability,
- extensibility,
- explicit interfaces,
- deterministic behaviour.

Future contributors shall be able to understand any module without requiring repository history.

---

# 49. Reinforcement Learning Maintainability Standards

RL-specific implementations shall remain extensible.

Future algorithms shall be addable without modifying existing algorithm implementations.

Preferred architecture:

```
BaseAgent

├── DQNAgent

├── DDQNAgent

└── Future Algorithms
```

Existing algorithms shall not require modification to support future extensions.

---

# 50. Long-Term Evolution Standards

Repository evolution shall preserve backward compatibility where practical.

Future architectural improvements shall:

- preserve experiment reproducibility,
- preserve traceability,
- preserve repository organization,
- preserve configuration compatibility.

Repository evolution shall be documented through Architecture Decision Records (ADRs).

---

# 51. Repository Definition of Done

Source code is considered complete only when all of the following conditions are satisfied.

Source-code completion does not imply training or experiment completion. Under CON-011, experiment completion additionally requires a human-launched Colab run from an exact public Git commit, human transfer of the complete Google Drive bundle, and successful local validation. Notebook existence alone satisfies none of those conditions.

## Functional

All assigned functional requirements implemented.

---

## Engineering

Architecture preserved.

No duplicated logic.

Configuration externalized.

---

## Verification

Unit tests pass.

Integration tests pass.

Assignment verification passes.

---

## Documentation

Documentation synchronized.

Interfaces documented.

Traceability maintained.

---

## Reproducibility

Experiments reproducible.

Random seed documented.

Artifacts generated correctly.

No artifact, result, or completion status fabricated.

---

## Quality

Formatting passes.

Linting passes.

Type checking passes.

No repository standards violated.

---

# 52. Repository Engineering Principles Summary

Every implementation within this repository shall satisfy the following engineering principles.

| Principle ID | Principle |
|---------------|-----------|
| EP-001 | Assignment Correctness |
| EP-002 | Architectural Integrity |
| EP-003 | Single Responsibility |
| EP-004 | Explicit Interfaces |
| EP-005 | Configuration over Hardcoding |
| EP-006 | Deterministic Behaviour |
| EP-007 | Reproducibility |
| EP-008 | Maintainability |
| EP-009 | Traceability |
| EP-010 | AI Readability |
| EP-011 | Documentation Driven Development |
| EP-012 | Long-Term Extensibility |

These principles collectively define the engineering identity of the repository.

---

# End of CODING_STANDARDS.md
