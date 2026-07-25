# Google Colab Training

## Document Metadata

| Field | Value |
|---|---|
| Document ID | COLAB-001 |
| Version | 1.0.0 |
| Status | Approved for Implementation |
| Purpose | Define the controlled Google Colab full-training workflow and artifact handoff contract |
| Scope | EXP-001 through EXP-004, resumed training, Google Drive persistence, and local artifact validation |
| Authority | CON-011, ADR-014, ADR-015 |
| Repository | `https://github.com/dkumar-23/RL_Lunar-Lander` |

## 1. Execution Authority

Full and resumed DQN or DDQN training shall execute only in a
human-launched Google Colab GPU session. Local OpenCode shall not launch
full training.

The human operator:

- starts the Colab GPU session,
- supplies the approved commit, experiment, run, configuration, and seed,
- authorizes Google Drive access,
- monitors execution,
- transfers each complete bundle to the local incoming directory.

Local OpenCode:

- implements and verifies the code path,
- prepares the notebook,
- performs bounded smoke and exactly-one-step validation,
- validates transferred bundles,
- evaluates validated checkpoints,
- generates plots, report assets, and documentation.

Notebook creation, successful notebook opening, or partial cell execution is
preparation evidence only. It is not evidence of completed training.

## 2. Canonical Experiments

| Experiment | Algorithm | Environment |
|---|---|---|
| EXP-001 | DQN | Original LunarLander-v3 |
| EXP-002 | DQN | Assignment-modified LunarLander-v3 |
| EXP-003 | DDQN | Original LunarLander-v3 |
| EXP-004 | DDQN | Assignment-modified LunarLander-v3 |

One experiment and run shall execute per notebook invocation.

## 3. Required Inputs

The notebook shall require:

```text
repository_url
git_commit_sha
experiment_id
run_id
configuration_path
random_seed
drive_artifact_root
```

The default Drive root is:

```text
/content/drive/MyDrive/RL_Lunar-Lander/runs
```

The Git commit shall be a complete immutable object identifier. A branch or
tag name alone is insufficient.

## 4. Exact Source Checkout

The notebook shall use an ephemeral worktree under `/content`, not Google
Drive. The required sequence is equivalent to:

```bash
git init /content/work/RL_Lunar-Lander
git -C /content/work/RL_Lunar-Lander remote add origin \
  https://github.com/dkumar-23/RL_Lunar-Lander
git -C /content/work/RL_Lunar-Lander fetch --depth=1 origin <git_commit_sha>
git -C /content/work/RL_Lunar-Lander checkout --detach FETCH_HEAD
```

Before importing repository code, the notebook shall verify:

```text
git rev-parse HEAD == requested git_commit_sha
git status --porcelain is empty
```

Training from a moving branch head or dirty worktree is prohibited.

## 5. Dependency Bootstrap

The notebook shall install only dependencies declared by
`requirements-colab.txt` and the repository's approved dependency files.
It shall then record:

- Python version,
- installed package versions,
- PyTorch version,
- Gymnasium version,
- CUDA version,
- accelerator and device name,
- Colab runtime release identifier when available,
- operating-system metadata.

Credentials, tokens, environment secrets, and Google account identifiers
shall not be written to metadata or logs.

## 6. Configuration and Seed Validation

The selected configuration shall be fully resolved and validated before
training. The resolved representation shall be immutable for the run.

The configuration hash is SHA-256 over the canonical resolved
configuration bytes. The run shall record the master, Python, NumPy,
PyTorch CPU, PyTorch CUDA, and Gymnasium environment seeds.

A resumed run shall use the same experiment definition, source commit,
configuration hash, and seed map. A mismatch requires a new run identifier.

## 7. Persistent Storage

The canonical Drive destination is:

```text
<drive_artifact_root>/<git_commit_sha>/<experiment_id>/<run_id>/
```

High-frequency writes should occur under ephemeral `/content` storage.
Checkpoints and logs shall be copied to Drive through temporary names,
closed, re-read, and hash-verified before being exposed under final names.

The notebook shall never overwrite a completed or failed run directory.

## 8. Required Training Bundle

```text
<experiment_id>/<run_id>/
├── manifest.json
├── resolved_config.yaml
├── metrics.csv
├── episode_metrics.csv
├── checkpoints/
│   ├── best_checkpoint.pt
│   └── final_checkpoint.pt
├── training.log
├── software_versions.json
├── provenance.json
├── integrity.sha256
└── status/
    └── COMPLETED.json or FAILED.json
```

A bundle shall contain exactly one terminal marker. No marker means the
bundle is incomplete.

## 9. Metrics Contract

`metrics.csv` shall contain at least:

```text
global_step
episode
optimization_step
loss
mean_predicted_q
epsilon
learning_rate
replay_size
```

`episode_metrics.csv` shall contain at least:

```text
episode
total_reward
episode_length
terminated
truncated
landing_success
thruster_actions_selected
thruster_actions_executed
thruster_failures
fuel_penalty_total
landing_bonus_total
mean_predicted_q
epsilon
duration_seconds
```

Final reward and landing-success semantics shall follow the approved PRD
and assignment specification. Metric files shall be generated by training
code, never entered manually.

## 10. Manifest Contract

`manifest.json` shall include:

```text
schema_version
experiment_id
run_id
algorithm
environment_variant
repository_url
requested_git_commit
resolved_git_commit
git_worktree_clean
configuration_path
configuration_hash
random_seed
execution_platform
started_at_utc
completed_at_utc
duration_seconds
status
best_checkpoint_selection_metric
software_versions_path
artifacts
artifact_set_sha256
```

Each artifact entry shall include:

```text
path
role
size_bytes
sha256
```

Artifact paths shall be bundle-relative POSIX paths. Absolute paths,
backslashes, symlinks, duplicate paths, and `.` or `..` path segments are
prohibited.

## 11. Integrity Rules

- SHA-256 hashes use lowercase hexadecimal.
- Payload hashes cover exact stored bytes.
- `manifest.json` lists every required payload and its hash.
- `integrity.sha256` covers payload files and `manifest.json`, excluding
  itself and terminal markers.
- The notebook shall verify Drive-side bytes after transfer.
- `COMPLETED.json` shall be written last.
- A failure shall produce `FAILED.json` and diagnostics, never fabricated
  success artifacts.

Hashes establish integrity, not authorship. Git provenance and the human
operator's accepted handoff remain separate requirements.

## 12. Local Handoff

The human operator transfers the complete bundle to:

```text
outputs/colab/incoming/<experiment_id>/<run_id>/
```

Individual files shall not be selected or renamed during transfer. Local
OpenCode then runs `scripts/validate_training_artifacts.py`.

The validator shall:

- reject missing or multiple terminal markers,
- validate manifest structure and identifiers,
- compare requested and resolved commits,
- verify the configuration hash,
- verify every file size and SHA-256 hash,
- reject undeclared files and unsafe paths,
- validate metrics schemas and required rows,
- load best and final checkpoints safely,
- verify algorithm, model dimensions, seed, and configuration metadata,
- reject NaN or infinite model parameters,
- write a separate validation report.

Imported payloads remain immutable. Validation reports are written under:

```text
outputs/colab/validation/<experiment_id>/<run_id>/validation_report.json
```

Accepted bundles are promoted to:

```text
outputs/colab/validated/<experiment_id>/<run_id>/
```

Evaluation shall recheck the manifest and validation receipt before loading
a checkpoint.

## 13. Completion Definition

Training is complete only when:

1. Colab executed from the recorded exact Git commit.
2. The full payload exists in Google Drive.
3. `COMPLETED.json` exists and `FAILED.json` does not.
4. The human transferred the complete bundle.
5. Local artifact validation passed.
6. Best and final checkpoints loaded successfully.
7. The bundle was promoted for local consumption.

Notebook existence, smoke output, one-step output, logs without a complete
bundle, or unvalidated checkpoints do not satisfy this definition.

## 14. Failure and Resume

Colab interruptions shall preserve available diagnostics and validated
periodic checkpoints in Drive. Full or resumed training remains Colab-only.

Resume is permitted only when the checkpoint, exact source commit,
configuration hash, experiment identity, and seed map pass validation. A
resume operation shall retain lineage metadata and shall never overwrite a
terminal bundle.

## 15. Prohibited Conduct

- Local full or resumed DQN/DDQN training.
- Training from a branch tip without exact commit resolution.
- Writing training only to ephemeral Colab storage.
- Treating notebook preparation as execution evidence.
- Fabricating, inferring, or manually editing metrics or checkpoints.
- Evaluating an unvalidated imported checkpoint.
- Publishing a run before the terminal marker and local validation pass.
