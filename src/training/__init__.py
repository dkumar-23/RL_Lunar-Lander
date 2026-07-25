"""Training orchestration and execution-boundary services."""

from .runtime_guard import (
    ExecutionBoundaryError,
    ExecutionContext,
    attest_colab_full_training,
    validate_local_test_limits,
)

__all__ = [
    "ExecutionBoundaryError",
    "ExecutionContext",
    "attest_colab_full_training",
    "validate_local_test_limits",
]
