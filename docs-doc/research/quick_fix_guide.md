# DocuSwarm Type Errors Quick Fix Guide

This guide provides copy-paste solutions for the most critical type errors found in the DocuSwarm project.

---

## Critical Fix 1: TypedDict NotRequired Access

### Problem

Direct access to TypedDict keys that are marked as optional (`total=False`) can cause `KeyError` at runtime.

### Files to Fix

- `autoBMAD/docuswarm/agents/evaluator.py` (lines 544-549)
- `autoBMAD/docuswarm/agents/independent.py` (lines 640-646)

### Current Code (evaluator.py)

```python
# Line 544-549
task_name = agent_input["task_name"]
task_description = agent_input["task_description"]
# deliverable_artifact reserved for future use
_ = agent_input["deliverable_artifact"]
deliverable_body = agent_input["deliverable_body"]
criteria = agent_input["criteria"] or self.criteria
```

### Fixed Code

```python
# Line 544-549
task_name = agent_input.get("task_name", "")
task_description = agent_input.get("task_description", "")
# deliverable_artifact reserved for future use
_ = agent_input.get("deliverable_artifact", {})
deliverable_body = agent_input.get("deliverable_body", "")
criteria = agent_input.get("criteria") or self.criteria
```

### Current Code (independent.py)

```python
# Line 640-646
task_name = agent_input["task_name"]
task_description = agent_input["task_description"]
role_supplement = agent_input["role_supplement"]
deliverable_reqs = agent_input["deliverable_requirements"]
original_context = agent_input["original_context_summary"]
chained_deliverables = agent_input["chained_deliverables_summary"]
iteration_feedback = agent_input["iteration_feedback"]
```

### Fixed Code

```python
# Line 640-646
task_name = agent_input.get("task_name", "")
task_description = agent_input.get("task_description", "")
role_supplement = agent_input.get("role_supplement", "")
deliverable_reqs = agent_input.get("deliverable_requirements", {})
original_context = agent_input.get("original_context_summary", "")
chained_deliverables = agent_input.get("chained_deliverables_summary", [])
iteration_feedback = agent_input.get("iteration_feedback")
```

---

## Critical Fix 2: Undefined Variable

### Problem

`NodeExecutionContext` is referenced but not imported in `dual_agent.py`.

### File to Fix

- `autoBMAD/docuswarm/nodes/dual_agent.py` (lines 233, 337)

### Current Code

```python
# Line 22-27
if TYPE_CHECKING:
    from structlog import BoundLogger as StructlogBoundLogger

    from autoBMAD.docuswarm.config import Config as AgentConfig
    from autoBMAD.docuswarm.pipeline.state import PipelineState

# Line 233
def _build_execution_context_from_legacy(...) -> "NodeExecutionContext":

# Line 337
def _execute_agent_with_context(
    self,
    *,
    execution_context: NodeExecutionContext,  # Error here
    agent_callable: Callable[..., Any],
) -> AgentOutput:
```

### Fixed Code

```python
# Line 22-28
if TYPE_CHECKING:
    from structlog import BoundLogger as StructlogBoundLogger

    from autoBMAD.docuswarm.config import Config as AgentConfig
    from autoBMAD.docuswarm.node_execution.contracts import NodeExecutionContext
    from autoBMAD.docuswarm.pipeline.state import PipelineState

# Line 233 - Keep as string literal (already correct)
def _build_execution_context_from_legacy(...) -> "NodeExecutionContext":

# Line 337-343
def _execute_agent_with_context(
    self,
    *,
    execution_context: "NodeExecutionContext",  # Add quotes
    agent_callable: Callable[..., Any],
) -> AgentOutput:
```

---

## Fix 3: Dunder All Mismatch

### Problem

`__all__` lists items that aren't directly defined in the module.

### Files to Fix

- `autoBMAD/docuswarm/models/__init__.py`
- `autoBMAD/docuswarm/node_execution/__init__.py`

### Option A: Explicit Re-exports (Recommended for models/__init__.py)

```python
"""Models module for DocuSwarm."""

from autoBMAD.docuswarm.tools.tool_result import ToolResult as ToolResult
from autoBMAD.docuswarm.tools.tool_registry import ToolRegistry as ToolRegistry

__all__ = [
    "ToolResult",
    "ToolRegistry",
]
```

### Option B: Type Ignore Comments (Recommended for node_execution/__init__.py)

```python
"""Node execution module for LangGraph individual node state management."""

# Single Context Protocol contracts (these have no dependencies)
from autoBMAD.docuswarm.node_execution.contracts import (
    DeliverableRequirements,
    EvaluatorAgentInput,
    EvaluatorOutput,
    IndependentAgentInput,
    IndependentOutput,
    NodeExecutionContext,
)

__all__ = [
    # Single Context Protocol contracts
    "NodeExecutionContext",
    "IndependentAgentInput",
    "EvaluatorAgentInput",
    "DeliverableRequirements",
    "IndependentOutput",
    "EvaluatorOutput",
    # Builder - type: ignore for lazy imports
    "NodeExecutionContextBuilder",  # type: ignore  # noqa: F822
    "create_context_builder",  # type: ignore  # noqa: F822
    # ... rest of __all__
]
```

---

## Fix 4: Missing Type Annotations

### Problem

Function parameters and return types lack type annotations.

### Example Fix for models/__init__.py

```python
# Before
def __getattr__(name):

# After  
from typing import Any

def __getattr__(name: str) -> Any:
```

### Example Fix for node_execution/__init__.py

```python
# Before
def __getattr__(name):
    if name == "create_node_executor":
        ...
    elif name in [...]:
        ...

# After
from typing import Any

def __getattr__(name: str) -> Any:
    if name == "create_node_executor":
        ...
    elif name in [...]:
        ...
```

---

## Fix 5: Implicit Override

### Problem

Method overrides parent class without `@override` decorator.

### File to Fix

- `autoBMAD/docuswarm/models/tool_registry.py:70`

### Current Code

```python
# Line 69-70
def clear(self) -> None:
    super().clear()
```

### Fixed Code

```python
# Add import at top
from typing import override

# Line 69-71
@override
def clear(self) -> None:
    super().clear()
```

---

## Fix 6: Unnecessary Type Checks

### Problem

Type checks that are always true or false.

### File: node_execution/executor.py

```python
# Line 259-260 - REMOVE THIS CHECK
if isinstance(original_context, dict[str, Any]):  # Always true
```

### File: prompts/contract_builder.py

```python
# Line 154-155 - REMOVE THIS CHECK  
if deliverable_requirements is None:  # Never None for TypedDict
```

---

## Verification

After applying fixes, run basedpyright to verify:

```bash
python -m basedpyright autoBMAD/docuswarm
```

Expected output after all fixes:
```
0 errors, 0 warnings, 0 informations
```

---

## Testing

Ensure all fixes pass existing tests:

```bash
pytest autoBMAD/docuswarm/tests -v
```

Pay special attention to:
- Agent execution tests
- Node execution tests  
- Integration tests

---

## Rollback Plan

If issues arise:

1. Revert the specific file causing problems
2. Run tests to confirm functionality
3. Apply fixes one file at a time with test runs between

---

*Quick fix guide for DocuSwarm type errors*
