# F5: Pipeline 与 Node Execution 统一设计规范

> 文档类型: 设计规范 (Design Specification)  
> 对应研究报告: `2026-03-25-f5-pipeline-node-execution-convergence-research-report.md`  
> 状态: Draft - 待评审

---

## 1. 设计目标

### 1.1 核心原则

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         单一主干原则 (Single Backbone)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  Pipeline 模块          →  负责业务编排 (Orchestration)                      │
│  Node Execution 模块    →  负责节点执行 (Execution)                          │
│  PipelineAdapter        →  唯一合法边界 (Single Boundary)                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 禁止事项

| 禁止项 | 违规示例 | 正确做法 |
|-------|---------|---------|
| Silent Fallback | `if session_manager is None: use_default()` | `if session_manager is None: raise ValueError` |
| 直接创建 synthetic ID | `f"node-{node_id}-{run_id}"` | `PipelineAdapter.create_pipeline_id(...)` |
| 跨模块直接状态转换 | `pipeline/graph.py` 直接操作 `NodeRunState` | 通过 `PipelineAdapter` 转换 |
| Deprecated 代码继续使用 | 调用 `_create_default_node_executor` | 使用 `_create_integrated_node_executor` |

---

## 2. 接口规范

### 2.1 create_pipeline_graph (修改后)

```python
# autoBMAD/docuswarm/pipeline/graph.py

from __future__ import annotations

from typing import Any
import structlog

from autoBMAD.docuswarm.llm.session_manager import KimiSessionManager
# ... other imports

logger = structlog.get_logger(__name__)

# =============================================================================
# REMOVED: _create_default_node_executor (Story 11.6 completed)
# REMOVED: create_enhanced_node_executor (no longer needed)
# =============================================================================

def create_pipeline_graph(
    db_path: str | None = None,
    checkpointer: BaseCheckpointSaver[Any] | None = None,
    compile_graph: bool = True,
    session_manager: KimiSessionManager,  # CHANGED: Removed `| None`, now required
) -> Any:
    """Create the pipeline StateGraph with all nodes and edges.
    
    This creates a LangGraph StateGraph with:
    - 5 nodes: analyst, pm, ux, architect, po
    - Sequential edges: analyst → pm → ux → architect → po
    - START and END connections
    - Integrated node execution via node_execution.executor (required)
    
    Args:
        db_path: Optional database path for SqliteSaver checkpointer.
        checkpointer: Optional existing checkpointer to use.
        compile_graph: If True (default), returns compiled graph.
        session_manager: **REQUIRED** KimiSessionManager for integrated node 
            execution. The deprecated default executor has been removed.
    
    Returns:
        StateGraph (uncompiled) or CompiledStateGraph ready for execution.
    
    Raises:
        ValueError: If session_manager is None.
        OrchestratorError: If graph creation fails.
    
    Example:
        >>> from autoBMAD.docuswarm.llm.session_manager import KimiSessionManager
        >>> session_manager = KimiSessionManager(...)
        >>> graph = create_pipeline_graph(session_manager=session_manager)
        >>> compiled = graph.compile()
    """
    # CHANGED: Hard fail on missing session_manager
    if session_manager is None:
        raise ValueError(
            "session_manager is required for pipeline execution. "
            "The deprecated default executor was removed in Story 11.6. "
            "Please provide a valid KimiSessionManager instance. "
            "See: docs/migration/session-manager-required.md"
        )
    
    # Create the StateGraph with PipelineState schema
    graph = StateGraph(PipelineState)
    
    # CHANGED: Always use integrated executor
    logger.info(
        "using_integrated_node_executor",
        message="Using integrated node_execution.executor for node execution",
    )
    
    # Add all 5 nodes to the graph
    for node_id in PIPELINE_NODES:
        node_executor = _create_integrated_node_executor(node_id, session_manager)
        graph.add_node(node_id, node_executor)
    
    # Add finalization node
    def finalize_executor(state: dict[str, Any]) -> PipelineState:
        return finalize_pipeline_state(state)
    
    graph.add_node("__finalize__", finalize_executor)
    
    # Add sequential edges
    graph.add_edge("__start__", "analyst")
    for i in range(len(PIPELINE_NODES) - 1):
        current_node = PIPELINE_NODES[i]
        next_node = PIPELINE_NODES[i + 1]
        graph.add_edge(current_node, next_node)
    
    graph.add_edge("po", "__finalize__")
    graph.add_edge("__finalize__", END)
    
    # Compile if requested
    if compile_graph:
        # ... checkpointer setup (unchanged)
        compiled: Runnable[dict[str, Any], dict[str, Any]] = graph.compile(
            checkpointer=checkpointer
        )
        return compiled
    
    return graph
```

### 2.2 PipelineAdapter (增强版)

```python
# autoBMAD/docuswarm/node_execution/pipeline_adapter.py

"""Pipeline Adapter for node_execution to pipeline integration.

TD-4: This module provides a **SINGLE** boundary layer for adapting node_execution
to the pipeline interface. It centralizes:
- Synthetic ID creation and parsing
- State format conversion (both directions)
- Node ID extraction from pipeline IDs

ALL cross-module interactions MUST go through this adapter.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from autoBMAD.docuswarm.pipeline.state import PipelineState, create_initial_state


class PipelineAdapter:
    """Adapter for node_execution to pipeline integration.
    
    This class is the **ONLY** legal boundary between node_execution and pipeline
    modules. All code that needs to:
    - Create synthetic pipeline IDs
    - Convert between PipelineState and NodeRunState
    - Extract node_id from pipeline_id
    
    MUST use this adapter.
    
    Example:
        >>> # Creating synthetic pipeline ID
        >>> pipeline_id = PipelineAdapter.create_pipeline_id("analyst", "run-123")
        >>> pipeline_id
        'node-analyst-run-123'
        
        >>> # State conversion
        >>> node_state = PipelineAdapter.convert_pipeline_to_node_state(
        ...     pipeline_state, "analyst"
        ... )
        >>> pipeline_state = PipelineAdapter.convert_node_to_pipeline_state(
        ...     node_state, original_pipeline_state
        ... )
    """
    
    # ==========================================================================
    # Synthetic Pipeline ID Management
    # ==========================================================================
    
    @staticmethod
    def create_pipeline_id(node_id: str, run_id: str) -> str:
        """Create a synthetic pipeline_id for a node run.
        
        This is the **SINGLE** place where synthetic pipeline IDs are created.
        All code that needs a synthetic pipeline_id MUST use this method.
        
        Args:
            node_id: The node identifier (e.g., 'analyst', 'pm').
            run_id: The run identifier.
        
        Returns:
            Synthetic pipeline_id in format: node-{node_id}-{run_id}
        
        Example:
            >>> PipelineAdapter.create_pipeline_id("analyst", "run-123")
            'node-analyst-run-123'
        """
        return f"node-{node_id}-{run_id}"
    
    @staticmethod
    def create_run_pipeline_id(run_id: str) -> str:
        """Create a run-level synthetic pipeline_id.
        
        Args:
            run_id: The run identifier.
        
        Returns:
            Synthetic pipeline_id in format: node-run-{run_id}
        
        Example:
            >>> PipelineAdapter.create_run_pipeline_id("run-123")
            'node-run-run-123'
        """
        return f"node-run-{run_id}"
    
    @staticmethod
    def parse_pipeline_id(pipeline_id: str) -> dict[str, str] | None:
        """Parse a synthetic pipeline_id to extract components.
        
        Args:
            pipeline_id: The synthetic pipeline_id.
        
        Returns:
            Dictionary with 'node_id' and 'run_id' keys, or None if not synthetic.
        
        Example:
            >>> PipelineAdapter.parse_pipeline_id("node-analyst-run-123")
            {'node_id': 'analyst', 'run_id': 'run-123', 'type': 'node'}
            
            >>> PipelineAdapter.parse_pipeline_id("node-run-run-123")
            {'node_id': '', 'run_id': 'run-123', 'type': 'run'}
            
            >>> PipelineAdapter.parse_pipeline_id("pipeline-123")  # Not synthetic
            None
        """
        if not pipeline_id.startswith("node-"):
            return None
        
        rest = pipeline_id[5:]  # Remove 'node-' prefix
        
        # Check for run-level format: node-run-{run_id}
        if rest.startswith("run-"):
            return {
                "node_id": "",
                "run_id": rest[4:],
                "type": "run",
            }
        
        # Check for node-level format: node-{node_id}-{run_id}
        parts = rest.split("-", 1)
        if len(parts) == 2:
            return {
                "node_id": parts[0],
                "run_id": parts[1],
                "type": "node",
            }
        
        return None
    
    @staticmethod
    def is_synthetic_pipeline_id(pipeline_id: str) -> bool:
        """Check if a pipeline_id is synthetic (created by this adapter).
        
        Args:
            pipeline_id: The pipeline_id to check.
        
        Returns:
            True if it's a synthetic pipeline_id.
        
        Example:
            >>> PipelineAdapter.is_synthetic_pipeline_id("node-analyst-run-123")
            True
            
            >>> PipelineAdapter.is_synthetic_pipeline_id("pipeline-123")
            False
        """
        return pipeline_id.startswith("node-")
    
    @staticmethod
    def extract_node_id_from_pipeline(pipeline_id: str, default: str = "") -> str:
        """Extract node_id from a synthetic pipeline_id.
        
        Args:
            pipeline_id: The pipeline_id.
            default: Default value if not a synthetic ID.
        
        Returns:
            The node_id or default value.
        
        Example:
            >>> PipelineAdapter.extract_node_id_from_pipeline("node-analyst-run-123")
            'analyst'
        """
        parsed = PipelineAdapter.parse_pipeline_id(pipeline_id)
        if parsed and parsed["type"] == "node":
            return parsed["node_id"]
        return default
    
    # ==========================================================================
    # State Conversion (MOVED from pipeline/graph.py)
    # ==========================================================================
    
    @staticmethod
    def convert_pipeline_to_node_state(
        pipeline_state: PipelineState,
        node_id: str,
    ) -> dict[str, Any]:
        """Convert PipelineState to NodeRunState for node execution.
        
        **RESPONSIBILITY TRANSFERRED**: This logic was previously in 
        pipeline/graph.py:_convert_pipeline_to_node_state but has been moved here
        to centralize boundary crossing logic.
        
        This function transforms a PipelineState into the format expected by
        the node_execution.executor module's create_node_executor().
        
        Args:
            pipeline_state: The current PipelineState.
            node_id: The node identifier being executed.
        
        Returns:
            A dictionary in NodeRunState format suitable for node execution.
        
        Example:
            >>> from autoBMAD.docuswarm.pipeline.state import create_initial_state
            >>> pipeline_state = create_initial_state("test-123", {"task": "Build X"})
            >>> node_state = PipelineAdapter.convert_pipeline_to_node_state(
            ...     pipeline_state, "analyst"
            ... )
            >>> node_state["pipeline_id"]
            'test-123'
            >>> node_state["node_id"]
            'analyst'
        """
        # Generate context_hash from subject_context and node_id
        subject_context = pipeline_state.get("subject_context", {})
        context_str = json.dumps(subject_context, sort_keys=True)
        context_hash = hashlib.md5(context_str.encode()).hexdigest()
        
        # Build accumulated context
        deliverables = pipeline_state.get("deliverables", {})
        accumulated = PipelineAdapter._accumulate_context(
            subject_context, deliverables, node_id
        )
        context_file = json.dumps(accumulated)
        
        # Get current iteration for this node
        node_iterations = pipeline_state.get("node_iterations", {})
        iteration = node_iterations.get(node_id, 0) + 1
        
        # Build chained_context from previous deliverables
        from autoBMAD.docuswarm.pipeline.state import PIPELINE_NODES
        
        chained_context: dict[str, dict[str, Any]] = {}
        for prev_node_id in PIPELINE_NODES:
            if prev_node_id == node_id:
                break
            if prev_node_id in deliverables:
                chained_context[prev_node_id] = {
                    "deliverable": deliverables.get(prev_node_id),
                    "iteration": node_iterations.get(prev_node_id, 1),
                }
        
        return {
            "run_id": pipeline_state.get("pipeline_id", "unknown"),
            "pipeline_id": pipeline_state.get("pipeline_id", "unknown"),
            "node_id": node_id,
            "context_hash": context_hash,
            "context_file": context_file,
            "iteration": iteration,
            "deliverable": None,
            "questions": [],
            "evaluation": None,
            "answers": {},
            "chained_context": chained_context,
            "status": "pending",
        }
    
    @staticmethod
    def convert_node_to_pipeline_state(
        node_state: dict[str, Any],
        original_state: PipelineState,
    ) -> PipelineState:
        """Convert NodeRunState back to PipelineState after node execution.
        
        **RESPONSIBILITY TRANSFERRED**: This logic was previously in 
        pipeline/graph.py:_convert_node_to_pipeline_state but has been moved here
        to centralize boundary crossing logic.
        
        This function transforms the results from node execution back into
        the PipelineState format, preserving all original fields and updating
        only the node-specific fields.
        
        Args:
            node_state: The NodeRunState after node execution.
            original_state: The original PipelineState before node execution.
        
        Returns:
            Updated PipelineState with node execution results merged in.
        
        Example:
            >>> from autoBMAD.docuswarm.pipeline.state import create_initial_state
            >>> original = create_initial_state("test", {"task": "Build X"})
            >>> node_result = {"node_id": "analyst", "deliverable": {"content": "Analysis"}}
            >>> result = PipelineAdapter.convert_node_to_pipeline_state(
            ...     node_result, original
            ... )
            >>> "analyst" in result["deliverables"]
            True
        """
        import copy
        
        new_state = copy.deepcopy(original_state)
        node_id = node_state.get("node_id")
        
        # Update deliverable if present
        if node_state.get("deliverable") is not None:
            if "deliverables" not in new_state:
                new_state["deliverables"] = {}
            new_state["deliverables"][node_id] = node_state["deliverable"]
        
        # Update questions if present
        questions = node_state.get("questions", [])
        if questions:
            if "questions" not in new_state:
                new_state["questions"] = {}
            new_state["questions"][node_id] = questions
        
        # Update evaluation if present
        evaluation = node_state.get("evaluation")
        if evaluation is not None:
            if "evaluations" not in new_state:
                new_state["evaluations"] = {}
            new_state["evaluations"][node_id] = evaluation
        
        # Update iteration count
        if "node_iterations" not in new_state:
            new_state["node_iterations"] = {}
        new_state["node_iterations"][node_id] = node_state.get("iteration", 1)
        
        # Add node to completed_nodes
        if "completed_nodes" not in new_state:
            new_state["completed_nodes"] = []
        if node_id not in new_state["completed_nodes"]:
            new_state["completed_nodes"] = new_state["completed_nodes"] + [node_id]
        
        # Update current_node
        new_state["current_node"] = node_id
        
        return new_state
    
    @staticmethod
    def _accumulate_context(
        subject_context: dict[str, Any],
        deliverables: dict[str, dict[str, Any]],
        current_node: str,
    ) -> dict[str, Any]:
        """Accumulate context by merging subject context with previous deliverables.
        
        Private helper moved from pipeline.state module.
        
        Args:
            subject_context: The initial subject/context of the pipeline.
            deliverables: Dictionary of node deliverables (key: node_id).
            current_node: The node that will receive this context.
        
        Returns:
            A new context dictionary containing subject_context and all previous deliverables.
        """
        from autoBMAD.docuswarm.pipeline.state import PIPELINE_NODES
        
        try:
            current_index = PIPELINE_NODES.index(current_node)
        except ValueError:
            return {"subject_context": subject_context}
        
        previous_nodes = PIPELINE_NODES[:current_index]
        
        accumulated: dict[str, Any] = {
            "subject_context": subject_context.copy() if subject_context else {},
        }
        
        for node_id in previous_nodes:
            if node_id in deliverables and deliverables[node_id]:
                accumulated[f"{node_id}_deliverable"] = deliverables[node_id].copy()
        
        return accumulated
    
    # ==========================================================================
    # Legacy adapter (for backward compatibility during migration)
    # ==========================================================================
    
    @staticmethod
    def adapt_state(node_execution_state: dict[str, Any]) -> PipelineState:
        """Convert node_execution state to PipelineState format (legacy).
        
        DEPRECATED: Use convert_node_to_pipeline_state instead.
        This method is kept for backward compatibility during migration.
        
        Args:
            node_execution_state: State from node_execution.
        
        Returns:
            PipelineState compatible state dictionary.
        """
        import warnings
        warnings.warn(
            "adapt_state is deprecated, use convert_node_to_pipeline_state",
            DeprecationWarning,
            stacklevel=2,
        )
        
        pipeline_id = node_execution_state.get("run_id", "")
        node_id = node_execution_state.get("node_id", "")
        
        if pipeline_id and not pipeline_id.startswith("node-"):
            pipeline_id = PipelineAdapter.create_pipeline_id(node_id, pipeline_id)
        
        subject_context = node_execution_state.get("subject_context", {})
        state = create_initial_state(pipeline_id, subject_context)
        
        state["current_node"] = node_id
        state["status"] = node_execution_state.get("status", "running")
        
        if "deliverable" in node_execution_state:
            state["deliverables"][node_id] = node_execution_state["deliverable"]
            if node_id not in state["completed_nodes"]:
                state["completed_nodes"].append(node_id)
        
        return state


# ==============================================================================
# Type aliases for clarity
# ==============================================================================

NodeRunState = dict[str, Any]
"""Type alias for node execution state format."""

__all__ = [
    "PipelineAdapter",
    "NodeRunState",
]
```

### 2.3 flow.py (修改后)

```python
# autoBMAD/docuswarm/node_execution/flow.py

"""Node execution flow module for DocuSwarm (Story 3.7).

This module provides the complete node execution flow from context file
to output persistence. All pipeline_id creation MUST use PipelineAdapter.
"""

from __future__ import annotations

# ... other imports

# CHANGED: Import PipelineAdapter
from autoBMAD.docuswarm.node_execution.pipeline_adapter import PipelineAdapter

# ... other code ...

async def execute_node_flow(
    node_id: str,
    context_file: str,
    run_id: str,
    no_chain: bool = False,
    output_dir: Path | str | None = None,
    db_path: str | None = None,
) -> dict[str, Any]:
    """Execute the complete node flow from context to output."""
    context_file_path = Path(context_file)
    
    # Step 1-3: Unchanged
    validator = ContextValidator()
    await validator.validate_context(context_file_path)
    context_hash = await validator.generate_context_hash(context_file_path)
    
    state_manager = StateManager(db_path=db_path)
    chained_context = await get_chained_context(
        node_id=node_id,
        context_hash=context_hash,
        no_chain=no_chain,
        state_manager=state_manager,
    )
    
    initial_state = create_node_run_state(
        run_id=run_id,
        node_id=node_id,
        context_hash=context_hash,
        context_file=str(context_file_path),
        iteration=1,
        chained_context=chained_context,
        status=PENDING,
    )
    
    # Step 4: Execute node via LangGraph
    from autoBMAD.docuswarm.node_execution.graph import create_node_execution_graph
    
    graph = create_node_execution_graph(node_id)
    config = {"configurable": {"thread_id": run_id}}
    
    result = cast(dict[str, Any], await graph.ainvoke(initial_state, config))
    
    # Step 5: Persist to database
    # CHANGED: Use PipelineAdapter instead of direct string formatting
    pipeline_id = PipelineAdapter.create_pipeline_id(node_id, run_id)
    
    # Ensure pipeline exists
    try:
        pipeline = state_manager.get_pipeline(pipeline_id)
        if pipeline is None:
            pipeline_id = state_manager.create_pipeline(
                subject=f"Node: {node_id}",
                subject_context={
                    "run_id": run_id,
                    "node_id": node_id,
                    "context_hash": context_hash,
                },
            )
    except Exception:
        pass
    
    # Save the node result
    deliverable = cast(dict[str, Any] | None, result.get("deliverable"))
    questions = cast(list[dict[str, Any]] | None, result.get("questions"))
    evaluation = cast(dict[str, Any] | None, result.get("evaluation"))
    
    state_manager.save_node_result(
        pipeline_id=pipeline_id,
        node_id=node_id,
        deliverable=deliverable,
        questions=questions,
        evaluation=evaluation,
    )
    
    # Step 6: Export output files
    await export_output(node_id, run_id, result, output_dir)
    
    return result


async def save_node_run(
    state_manager: StateManager,
    run_id: str,
    node_id: str,
    context_hash: str,
    deliverable: dict[str, Any] | None = None,
    questions: list[dict[str, Any]] | None = None,
    evaluation: dict[str, Any] | None = None,
    iteration: int = 1,
    status: str = "completed",
) -> bool:
    """Save node run to database."""
    _ = iteration  # Mark as intentionally unused
    _ = status
    
    # CHANGED: Use PipelineAdapter
    pipeline_id = PipelineAdapter.create_run_pipeline_id(run_id)
    
    # Ensure pipeline exists
    try:
        pipeline = state_manager.get_pipeline(pipeline_id)
        if pipeline is None:
            pipeline_id = state_manager.create_pipeline(
                subject=f"Node run: {node_id}",
                subject_context={
                    "run_id": run_id,
                    "node_id": node_id,
                    "context_hash": context_hash,
                },
            )
    except Exception:
        pass
    
    return state_manager.save_node_result(
        pipeline_id=pipeline_id,
        node_id=node_id,
        deliverable=deliverable,
        questions=questions,
        evaluation=evaluation,
    )
```

---

## 3. 迁移检查清单

### Phase 1: Hard Fail & Boundary Enforcement

```markdown
- [ ] 1.1 修改 `create_pipeline_graph()` 签名，移除 `session_manager` 的可空性
  - [ ] 更新函数签名
  - [ ] 添加 `ValueError` 抛出
  - [ ] 更新 docstring
  - [ ] 移除 `use_integrated` 条件判断

- [ ] 1.2 删除 `_create_default_node_executor` 函数
  - [ ] 删除函数定义 (lines 55-158)
  - [ ] 删除 `create_enhanced_node_executor` (如果存在)
  - [ ] 更新 `__all__` 列表
  - [ ] 更新所有导入该函数的地方

- [ ] 1.3 更新 `node_execution/flow.py` 使用 PipelineAdapter
  - [ ] 添加导入 `from ...pipeline_adapter import PipelineAdapter`
  - [ ] 替换 `f"node-{node_id}-{run_id}"`
  - [ ] 替换 `f"node-run-{run_id}"`
  - [ ] 运行单元测试验证

- [ ] 1.4 更新所有调用 `create_pipeline_graph()` 的代码
  - [ ] `pipeline/orchestrator.py`
  - [ ] `cli/services/pipeline_service.py` (如果存在)
  - [ ] 所有测试文件

- [ ] 1.5 运行全量测试并修复失败
  - [ ] 单元测试
  - [ ] 集成测试
  - [ ] 冒烟测试
```

### Phase 2: Adapter Enhancement

```markdown
- [ ] 2.1 迁移状态转换函数到 PipelineAdapter
  - [ ] 将 `_convert_pipeline_to_node_state` 移至 `PipelineAdapter.convert_pipeline_to_node_state`
  - [ ] 将 `_convert_node_to_pipeline_state` 移至 `PipelineAdapter.convert_node_to_pipeline_state`
  - [ ] 添加辅助方法 `_accumulate_context`
  - [ ] 确保所有依赖导入正确

- [ ] 2.2 更新 `pipeline/graph.py` 使用 Adapter
  - [ ] 导入 `PipelineAdapter`
  - [ ] 在 `_create_integrated_node_executor` 中使用 Adapter 方法
  - [ ] 删除旧的转换函数

- [ ] 2.3 验证状态转换功能
  - [ ] 运行状态转换单元测试
  - [ ] 运行完整流水线测试
  - [ ] 验证 resume/restart 功能

- [ ] 2.4 更新文档
  - [ ] 更新架构文档
  - [ ] 添加边界使用规范
  - [ ] 更新 API 文档
```

### Phase 3: Cleanup

```markdown
- [ ] 3.1 重命名冲突文件
  - [ ] `node_execution/escalation.py` -> `node_execution/node_escalation.py`
  - [ ] 更新所有导入
  - [ ] 运行测试验证

- [ ] 3.2 统一或合并 metrics 模块
  - [ ] 分析两个 metrics 模块的使用情况
  - [ ] 决定统一方案
  - [ ] 实施合并或重构

- [ ] 3.3 添加架构守护测试
  - [ ] 创建 `tests/architecture/test_boundary_enforcement.py`
  - [ ] 添加 CI 检查脚本
  - [ ] 更新 PR 模板要求

- [ ] 3.4 最终清理
  - [ ] 删除所有 deprecated 标记
  - [ ] 清理未使用的导入
  - [ ] 更新 CHANGELOG
```

---

## 4. 验证方案

### 4.1 单元测试

```python
# tests/node_execution/test_pipeline_adapter.py

import pytest
from autoBMAD.docuswarm.node_execution.pipeline_adapter import PipelineAdapter
from autoBMAD.docuswarm.pipeline.state import create_initial_state


class TestPipelineAdapter:
    """Test suite for PipelineAdapter - the single boundary between modules."""
    
    def test_create_pipeline_id_format(self):
        """Synthetic pipeline_id must follow expected format."""
        result = PipelineAdapter.create_pipeline_id("analyst", "run-123")
        assert result == "node-analyst-run-123"
        assert result.startswith("node-")
    
    def test_create_run_pipeline_id_format(self):
        """Run-level synthetic pipeline_id must follow expected format."""
        result = PipelineAdapter.create_run_pipeline_id("run-123")
        assert result == "node-run-run-123"
    
    def test_parse_pipeline_id_valid(self):
        """Parsing valid synthetic IDs must work."""
        node_id = PipelineAdapter.parse_pipeline_id("node-analyst-run-123")
        assert node_id == {"node_id": "analyst", "run_id": "run-123", "type": "node"}
        
        run_id = PipelineAdapter.parse_pipeline_id("node-run-run-123")
        assert run_id == {"node_id": "", "run_id": "run-123", "type": "run"}
    
    def test_parse_pipeline_id_invalid(self):
        """Parsing non-synthetic IDs must return None."""
        result = PipelineAdapter.parse_pipeline_id("pipeline-123")
        assert result is None
    
    def test_is_synthetic_pipeline_id(self):
        """Detection of synthetic IDs must be accurate."""
        assert PipelineAdapter.is_synthetic_pipeline_id("node-analyst-run-123") is True
        assert PipelineAdapter.is_synthetic_pipeline_id("pipeline-123") is False
    
    def test_convert_pipeline_to_node_state(self):
        """PipelineState -> NodeRunState conversion must work."""
        pipeline_state = create_initial_state("test-123", {"task": "Build X"})
        
        node_state = PipelineAdapter.convert_pipeline_to_node_state(
            pipeline_state, "analyst"
        )
        
        assert node_state["pipeline_id"] == "test-123"
        assert node_state["node_id"] == "analyst"
        assert node_state["status"] == "pending"
        assert "context_hash" in node_state
        assert "context_file" in node_state
    
    def test_convert_node_to_pipeline_state(self):
        """NodeRunState -> PipelineState conversion must work."""
        original = create_initial_state("test-123", {"task": "Build X"})
        node_state = {
            "node_id": "analyst",
            "deliverable": {"content": "Analysis complete"},
            "questions": [],
            "evaluation": {"verdict": "APPROVED"},
            "iteration": 2,
        }
        
        result = PipelineAdapter.convert_node_to_pipeline_state(node_state, original)
        
        assert "analyst" in result["deliverables"]
        assert result["deliverables"]["analyst"]["content"] == "Analysis complete"
        assert "analyst" in result["completed_nodes"]
        assert result["current_node"] == "analyst"


# tests/pipeline/test_create_pipeline_graph.py

import pytest
from autoBMAD.docuswarm.pipeline.graph import create_pipeline_graph
from autoBMAD.docuswarm.llm.session_manager import KimiSessionManager


class TestCreatePipelineGraph:
    """Test suite for create_pipeline_graph - single backbone enforcement."""
    
    def test_session_manager_required(self):
        """session_manager is now required - must raise ValueError if None."""
        with pytest.raises(ValueError) as exc_info:
            create_pipeline_graph(session_manager=None)  # type: ignore
        
        assert "session_manager is required" in str(exc_info.value)
        assert "deprecated default executor was removed" in str(exc_info.value)
    
    def test_session_manager_provided(self, mock_session_manager):
        """Providing session_manager must work."""
        # Should not raise
        graph = create_pipeline_graph(
            session_manager=mock_session_manager,
            compile_graph=False
        )
        assert graph is not None
    
    def test_no_default_executor_fallback(self):
        """Deprecated _create_default_node_executor must not be used."""
        # This test ensures the deprecated function doesn't exist
        from autoBMAD.docuswarm.pipeline import graph
        
        assert not hasattr(graph, '_create_default_node_executor')
        assert not hasattr(graph, 'create_enhanced_node_executor')


# tests/architecture/test_no_direct_synthetic_id.py

import ast
import pytest
from pathlib import Path


class TestNoDirectSyntheticIdCreation:
    """Architecture test: No direct f-string synthetic ID creation."""
    
    def test_flow_py_no_direct_id_creation(self):
        """flow.py must not contain direct f-string synthetic ID creation."""
        flow_path = Path("autoBMAD/docuswarm/node_execution/flow.py")
        content = flow_path.read_text()
        
        # Check for direct f-string patterns
        assert 'f"node-' not in content, "Found direct f-string ID creation"
        assert "f'node-" not in content, "Found direct f-string ID creation"
    
    def test_all_synthetic_ids_use_adapter(self):
        """All synthetic ID creation must use PipelineAdapter."""
        ne_path = Path("autoBMAD/docuswarm/node_execution")
        
        for py_file in ne_path.glob("*.py"):
            if py_file.name == "pipeline_adapter.py":
                continue
            
            content = py_file.read_text()
            
            # If file creates synthetic IDs, it must import PipelineAdapter
            if 'f"node-' in content or "f'node-" in content:
                assert "PipelineAdapter" in content, \
                    f"{py_file.name} creates synthetic IDs without using PipelineAdapter"
```

### 4.2 CI 检查脚本

```python
# tools/ci/check_boundary_violations.py

#!/usr/bin/env python3
"""CI 检查脚本: 确保没有边界违规"""

import sys
from pathlib import Path

# Import from the analyzer
from tools.pipeline_node_execution_analyzer import (
    analyze_boundary_violations,
    analyze_fallback_paths,
)


def main() -> int:
    """Check for boundary violations."""
    violations = analyze_boundary_violations()
    fallbacks = analyze_fallback_paths()
    
    exit_code = 0
    
    # Check boundary violations
    if violations:
        print("❌ BOUNDARY VIOLATIONS DETECTED:")
        for v in violations:
            print(f"  - [{v.violation_type}] {v.location}")
            print(f"    {v.description}")
        exit_code = 1
    else:
        print("✅ No boundary violations detected")
    
    # Check fallback paths
    silent_fallbacks = [fb for fb in fallbacks 
                       if fb.fallback_type in ("deprecated", "silent")]
    if silent_fallbacks:
        print("\n❌ DEPRECATED/SILENT FALLBACK PATHS DETECTED:")
        for fb in silent_fallbacks:
            print(f"  - [{fb.fallback_type}] {fb.location}")
        exit_code = 1
    else:
        print("✅ No deprecated fallback paths detected")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
```

---

## 5. 决策记录 (ADR)

### ADR-001: 强制 session_manager 必填

**状态**: Accepted  
**日期**: 2026-03-25

**背景**: `create_pipeline_graph()` 当前接受 `session_manager: Any | None = None`，当为 None 时静默降级到 deprecated default executor。

**决策**: 将 `session_manager` 改为必需参数，如果为 None 则抛出 `ValueError`。

**后果**:
- ✅ 消除静默降级路径
- ✅ 明确依赖关系
- ✅ 更早暴露问题
- ⚠️ 需要更新所有调用点

### ADR-002: PipelineAdapter 作为唯一边界

**状态**: Accepted  
**日期**: 2026-03-25

**背景**: Synthetic pipeline_id 创建散落在多个文件中，导致责任边界不清。

**决策**: 所有 synthetic ID 创建和状态转换必须通过 `PipelineAdapter`。

**后果**:
- ✅ 单一可信源
- ✅ 易于测试边界
- ✅ 便于未来重构
- ⚠️ 初期需要迁移工作

---

## 6. 参考

- 研究报告: `docs/research/2026-03-25-f5-pipeline-node-execution-convergence-research-report.md`
- 评估报告: `docs/evaluation/2026-03-25-docuswarm-deep-evaluation-report.md`
- 分析工具: `tools/pipeline_node_execution_analyzer.py`
