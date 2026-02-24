"""DocuSwarm - Multi-Agent Document Orchestration System."""

from typing import TYPE_CHECKING

from autoBMAD.docuswarm.config import Config
from autoBMAD.docuswarm.exceptions import (
    AgentError,
    ConfigurationError,
    ContextIsolationError,
    DocuSwarmError,
    LLMError,
    NodeExecutionError,
    PipelineError,
    StorageError,
    ValidationError,
)

# Type stubs for lazy-loaded classes (only used by type checkers)
if TYPE_CHECKING:
    from autoBMAD.docuswarm.agents.evaluator import EvaluatorAgent
    from autoBMAD.docuswarm.agents.independent import IndependentAgent
    from autoBMAD.docuswarm.nodes import create_node_executor as create_node_execution


# Lazy imports to avoid ImportError on modules not yet fully implemented
def __getattr__(name: str):
    if name == "IndependentAgent":
        from autoBMAD.docuswarm.agents.independent import IndependentAgent

        return IndependentAgent
    if name == "EvaluatorAgent":
        from autoBMAD.docuswarm.agents.evaluator import EvaluatorAgent

        return EvaluatorAgent
    if name == "create_node_execution":
        from autoBMAD.docuswarm.nodes import (
            create_node_executor as create_node_execution,
        )

        return create_node_execution
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__version__ = "1.0.0"

__all__ = [
    "__version__",
    "Config",
    "DocuSwarmError",
    "ConfigurationError",
    "StorageError",
    "LLMError",
    "PipelineError",
    "NodeExecutionError",
    "ContextIsolationError",
    "AgentError",
    "ValidationError",
    "IndependentAgent",
    "EvaluatorAgent",
    "create_node_execution",
]
