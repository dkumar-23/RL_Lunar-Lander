"""Training orchestration and execution-boundary services."""

from .config import (
    Algorithm,
    EnvironmentVariant,
    ExperimentConfig,
    TrainingConfig,
    load_experiment_config,
    load_training_config,
)
from .engine import (
    EpisodeMetrics,
    LocalLimits,
    OptimizationMetrics,
    TrainingEngine,
    TrainingResult,
)
from .factory import (
    create_agent,
    create_replay_buffer,
    environment_dimensions,
    resolve_device,
)
from .resume import ResumeError, ResumeProgress, restore_training_checkpoint
from .runtime_guard import (
    ColabTrainingAttestation,
    ExecutionBoundaryError,
    ExecutionContext,
    attest_colab_full_training,
    validate_local_test_limits,
)
from .validation import FixedValidationSet, mean_max_predicted_q

__all__ = [
    "Algorithm",
    "ColabTrainingAttestation",
    "EnvironmentVariant",
    "EpisodeMetrics",
    "ExecutionBoundaryError",
    "ExecutionContext",
    "ExperimentConfig",
    "FixedValidationSet",
    "LocalLimits",
    "OptimizationMetrics",
    "ResumeError",
    "ResumeProgress",
    "TrainingConfig",
    "TrainingEngine",
    "TrainingResult",
    "attest_colab_full_training",
    "create_agent",
    "create_replay_buffer",
    "environment_dimensions",
    "load_experiment_config",
    "load_training_config",
    "mean_max_predicted_q",
    "resolve_device",
    "restore_training_checkpoint",
    "validate_local_test_limits",
]
