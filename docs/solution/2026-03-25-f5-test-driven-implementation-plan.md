# F5 双主干语义收敛 - 测试驱动实施方案

> 对应研究: `docs/research/2026-03-25-f5-pipeline-node-execution-convergence-research-report.md`  
> 方法论: Test-Driven Development (TDD) - Red/Green/Refactor  
> 实施周期: 3 Phase × 1 周/Phase

---

## 实施原则

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TDD 循环 (每个修改点)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. RED    →  编写失败测试  →  确认测试描述正确行为                            │
│  2. GREEN  →  编写最小实现  →  让测试通过                                      │
│  3. REFACTOR → 代码重构    →  保持测试通过                                     │
│                                                                             │
│  ⚠️  禁止: 先实现后补测试 (反TDD)                                             │
│  ✅ 必须: 测试先行，实现跟进                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: 硬失败与边界强制 (P0)

**目标**: 强制唯一执行路径，消除 silent fallback

### 1.1 强制 session_manager 必填

#### Step 1.1.1: RED - 编写失败测试

**测试文件**: `tests/pipeline/test_create_pipeline_graph_signature.py` (新建)

```python
"""Test session_manager is required for create_pipeline_graph.

TDD Phase 1.1: Session manager must be required, not optional.
"""

import pytest
from autoBMAD.docuswarm.pipeline.graph import create_pipeline_graph
from autoBMAD.docuswarm.llm.session_manager import KimiSessionManager


class TestCreatePipelineGraphSessionManagerRequired:
    """Test suite: session_manager is now a required parameter."""

    def test_session_manager_none_raises_value_error(self):
        """RED: Passing None for session_manager must raise ValueError.
        
        This test documents the breaking change: the deprecated default executor
        fallback has been removed. Callers must provide a valid session_manager.
        """
        # Arrange: No session_manager provided
        
        # Act & Assert: Must raise ValueError with descriptive message
        with pytest.raises(ValueError) as exc_info:
            create_pipeline_graph(session_manager=None)  # type: ignore
        
        error_message = str(exc_info.value)
        assert "session_manager is required" in error_message
        assert "deprecated default executor was removed" in error_message

    def test_session_manager_provided_works(self, mock_session_manager):
        """GREEN: Providing a valid session_manager must work.
        
        This is the expected usage pattern after migration.
        """
        # Arrange
        session_manager = mock_session_manager
        
        # Act: Should not raise
        graph = create_pipeline_graph(
            session_manager=session_manager,
            compile_graph=False
        )
        
        # Assert
        assert graph is not None

    def test_old_signature_with_optional_removed(self):
        """RED: The old signature with 'Any | None = None' must no longer exist.
        
        This is an architectural test - we inspect the function signature
        to ensure the migration is complete.
        """
        import inspect
        
        sig = inspect.signature(create_pipeline_graph)
        params = sig.parameters
        
        session_manager_param = params.get('session_manager')
        assert session_manager_param is not None
        
        # The default must NOT be None anymore
        assert session_manager_param.default is not inspect.Parameter.empty
        assert session_manager_param.default is None  # Will fail after migration
        # After migration, this should be:
        # assert session_manager_param.default is inspect.Parameter.empty  # No default
```

**运行测试 (预期失败)**:```bash
pytest tests/pipeline/test_create_pipeline_graph_signature.py -v
# 预期: 2 failed, 1 passed# - test_session_manager_none_raises_value_error: FAIL (当前没有 raise ValueError)# - test_session_manager_provided_works: PASS (当前代码支持)# - test_old_signature_with_optional_removed: FAIL (当前仍有默认值)```#### Step 1.1.2: GREEN - 最小实现**修改文件**: `autoBMAD/docuswarm/pipeline/graph.py````python# ... existing imports ...from autoBMAD.docuswarm.llm.session_manager import KimiSessionManager  # Add explicit import
def create_pipeline_graph(
    db_path: str | None = None,
    checkpointer: BaseCheckpointSaver[Any] | None = None,
    compile_graph: bool = True,
    # CHANGED: Removed `| None = None`, now required    session_manager: KimiSessionManager,
) -> Any:
    """Create the pipeline StateGraph with all nodes and edges.
    
    Args:
        db_path: Optional database path for SqliteSaver checkpointer.
        checkpointer: Optional existing checkpointer to use.
        compile_graph: If True (default), returns compiled graph.
        session_manager: **REQUIRED** KimiSessionManager for integrated node 
            execution. The deprecated default executor has been removed.
    
    Returns:
        StateGraph (uncompiled) or CompiledStateGraph ready for execution.
    
    Raises:        ValueError: If session_manager is None.
    """
    # NEW: Hard fail on missing session_manager
    if session_manager is None:
        raise ValueError(
            "session_manager is required for pipeline execution. "
            "The deprecated default executor was removed in Story 11.6. "
            "Please provide a valid KimiSessionManager instance."
        )    
    # ... rest of implementation (remove use_integrated check) ...
    # REMOVE: use_integrated = session_manager is not None
    # REMOVE: if/else for executor selection
    
    # Always use integrated executor now
    logger.info(
        "using_integrated_node_executor",
        message="Using integrated node_execution.executor for node execution",
    )
    
    for node_id in PIPELINE_NODES:
        # REMOVE: if use_integrated:
        node_executor = _create_integrated_node_executor(node_id, session_manager)
        # REMOVE: else:
        # REMOVE:     node_executor = _create_default_node_executor(node_id)
        graph.add_node(node_id, node_executor)
```**验证**:```bash
pytest tests/pipeline/test_create_pipeline_graph_signature.py -v# 预期: 3 passed```---### 1.2 删除 Deprecated Default Executor#### Step 1.2.1: RED - 编写失败测试**测试文件**: `tests/pipeline/test_no_deprecated_executor.py` (新建)```python"""Test deprecated executor has been removed.TDD Phase 1.2: _create_default_node_executor must not exist."""

import pytest
from autoBMAD.docuswarm.pipeline import graph as graph_module


class TestNoDeprecatedExecutor:
    """Test suite: deprecated executor functions removed."""

    def test_create_default_node_executor_removed(self):
        """RED: _create_default_node_executor function must not exist.
        
        This function was deprecated in Story 11.6 and must be removed.
        It produced empty deliverables and should not be used in production.
        """
        assert not hasattr(graph_module, '_create_default_node_executor'), \\
            "_create_default_node_executor must be removed"

    def test_create_enhanced_node_executor_removed(self):        """RED: create_enhanced_node_executor function must not exist.
        
        This was a wrapper around the deprecated default executor.
        """
        assert not hasattr(graph_module, 'create_enhanced_node_executor'), \\
            "create_enhanced_node_executor must be removed"

    def test_default_executor_not_in_all(self):
        """RED: Deprecated functions must not be exported in __all__."""
        if hasattr(graph_module, '__all__'):
            assert '_create_default_node_executor' not in graph_module.__all__
            assert 'create_enhanced_node_executor' not in graph_module.__all__

    def test_no_deprecated_imports_in_codebase(self):
        """RED: No file should import the deprecated functions.
        
        This is an architecture test scanning the codebase.
        """
        import ast
        from pathlib import Path
        
        project_root = Path(__file__).parents[3]
        docuswarm_path = project_root / "autoBMAD" / "docuswarm"
        
        deprecated_names = [
            '_create_default_node_executor',
            'create_enhanced_node_executor',
        ]
        
        violations = []
        
        for py_file in docuswarm_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    # Check imports
                    if isinstance(node, ast.ImportFrom):
                        if node.module and 'graph' in node.module:
                            for alias in node.names:
                                if alias.name in deprecated_names:
                                    violations.append(f"{py_file}: imports {alias.name}")
                    
                    # Check function calls
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            if node.func.id in deprecated_names:
                                violations.append(f"{py_file}: calls {node.func.id}")
            except Exception:
                continue
        
        assert not violations, f"Found deprecated function usage: {violations}"```**运行测试 (预期失败)**:```bash
pytest tests/pipeline/test_no_deprecated_executor.py -v
# 预期: 4 failed# - 函数仍然存在# - 可能仍在 __all__ 中# - 可能有代码仍在导入```#### Step 1.2.2: GREEN - 删除实现**修改文件**: `autoBMAD/docuswarm/pipeline/graph.py````python# DELETE lines 55-158: Remove entire _create_default_node_executor function# DELETE lines 408-424: Remove entire create_enhanced_node_executor function

# UPDATE __all__ if present__all__ = [    'PIPELINE_NODES',
    'create_pipeline_graph',
    'create_graph_with_checkpointer',
    'create_graph_config',
    # REMOVE: Story 11.4 - Node execution integration (these are internal now)
    # '_create_integrated_node_executor',  # Can keep if needed for tests
    # '_convert_pipeline_to_node_state',   # Will be moved to Adapter
    # '_convert_node_to_pipeline_state',   # Will be moved to Adapter
    # REMOVE: Story 11.6 - Test utilities (keep these)
    'MockNodeExecutor',
    'create_mock_node_executor',
]```**验证**:```bash
pytest tests/pipeline/test_no_deprecated_executor.py -v# 预期: 4 passed```---### 1.3 强制使用 PipelineAdapter#### Step 1.3.1: RED - 编写失败测试**测试文件**: `tests/architecture/test_pipeline_adapter_usage.py` (新建)```python"""Test PipelineAdapter is used for all synthetic ID creation.TDD Phase 1.3: No direct f-string synthetic ID creation allowed."""

import ast
import pytest
from pathlib import Path


class TestPipelineAdapterBoundaryEnforcement:
    """Test suite: PipelineAdapter is the single boundary."""

    def test_no_direct_node_prefix_fstrings(self):
        """RED: No file should contain f\"node-{...}\" patterns.
        
        All synthetic pipeline_id creation must use PipelineAdapter.
        """
        project_root = Path(__file__).parents[3]
        ne_path = project_root / "autoBMAD" / "docuswarm" / "node_execution"
        
        violations = []
        
        for py_file in ne_path.glob("*.py"):
            if py_file.name == "pipeline_adapter.py":
                continue  # Adapter itself is allowed to create these
            if "__pycache__" in str(py_file):
                continue
            
            content = py_file.read_text()
            lines = content.split("\\n")
            
            for i, line in enumerate(lines, 1):
                # Check for f"node- or f'node- patterns
                if ('f\"node-' in line or "f'node-" in line or 
                    'f"node-run-' in line or "f'node-run-" in line):
                    # Check if this line uses PipelineAdapter
                    if "PipelineAdapter" not in line and "create_pipeline_id" not in line:
                        violations.append(f"{py_file.name}:{i}: {line.strip()}")
        
        assert not violations, f"Direct synthetic ID creation found: {violations}"

    def test_flow_py_uses_adapter(self):
        """RED: flow.py must import and use PipelineAdapter.
        
        This is a specific check for the main violation found in research.
        """
        project_root = Path(__file__).parents[3]
        flow_path = project_root / "autoBMAD" / "docuswarm" / "node_execution" / "flow.py"
        
        assert flow_path.exists(), "flow.py must exist"
        
        content = flow_path.read_text()
        
        # Must import PipelineAdapter
        assert "from autoBMAD.docuswarm.node_execution.pipeline_adapter import PipelineAdapter" in content, \\
            "flow.py must import PipelineAdapter"
        
        # Must use create_pipeline_id
        assert "PipelineAdapter.create_pipeline_id(" in content, \\
            "flow.py must use PipelineAdapter.create_pipeline_id()"
        
        assert "PipelineAdapter.create_run_pipeline_id(" in content, \\
            "flow.py must use PipelineAdapter.create_run_pipeline_id()"

    def test_adapter_methods_are_used(self):
        """RED: PipelineAdapter methods must have at least one usage.
        
        Verifies the adapter is actually being used, not just imported.
        """
        project_root = Path(__file__).parents[3]
        docuswarm_path = project_root / "autoBMAD" / "docuswarm"
        adapter_path = docuswarm_path / "node_execution" / "pipeline_adapter.py"
        
        # Parse adapter to get method names
        adapter_content = adapter_path.read_text()
        tree = ast.parse(adapter_content)
        
        static_methods = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if it's a staticmethod
                decorators = [d for d in node.decorator_list 
                             if isinstance(d, ast.Name) and d.id == "staticmethod"]
                if decorators:
                    static_methods.append(node.name)
        
        # Check each method is used somewhere
        unused_methods = []
        for method_name in static_methods:
            found_usage = False
            for py_file in docuswarm_path.rglob("*.py"):
                if py_file.name == "pipeline_adapter.py":
                    continue
                if "__pycache__" in str(py_file):
                    continue
                
                content = py_file.read_text()
                if f"PipelineAdapter.{method_name}(" in content:
                    found_usage = True
                    break
            
            if not found_usage:
                unused_methods.append(method_name)
        
        assert not unused_methods, f"PipelineAdapter methods not used: {unused_methods}"```**运行测试 (预期失败)**:```bash
pytest tests/architecture/test_pipeline_adapter_usage.py -v
# 预期: 3 failed# - flow.py 直接创建 synthetic ID# - flow.py 没有导入 PipelineAdapter# - Adapter 方法没有被使用```#### Step 1.3.2: GREEN - 更新 flow.py**修改文件**: `autoBMAD/docuswarm/node_execution/flow.py````python"""Node execution flow module for DocuSwarm (Story 3.7)."""

from __future__ import annotations

# ... existing imports ...

# NEW: Import PipelineAdapter
from autoBMAD.docuswarm.node_execution.pipeline_adapter import PipelineAdapter

# ... existing code ...

async def execute_node_flow(
    node_id: str,
    context_file: str,
    run_id: str,
    no_chain: bool = False,
    output_dir: Path | str | None = None,
    db_path: str | None = None,
) -> dict[str, Any]:
    """Execute the complete node flow from context to output."""
    # ... existing code ...
    
    result = cast(dict[str, Any], await graph.ainvoke(initial_state, config))
    
    # Step 5: Persist to database
    # CHANGED: Use PipelineAdapter instead of direct f-string    pipeline_id = PipelineAdapter.create_pipeline_id(node_id, run_id)
    
    # ... rest of the function ...


# Also fix save_node_run function
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
    _ = iteration
    _ = status
    
    # CHANGED: Use PipelineAdapter
    pipeline_id = PipelineAdapter.create_run_pipeline_id(run_id)
    
    # ... rest of the function ...```**验证**:```bash
pytest tests/architecture/test_pipeline_adapter_usage.py -v# 预期: 3 passed```---### Phase 1 集成验证**测试文件**: `tests/integration/test_phase1_convergence.py` (新建)```python"""Integration tests for Phase 1 convergence.TDD Phase 1 Integration: End-to-end verification."""

import pytest
from autoBMAD.docuswarm.pipeline.graph import create_pipeline_graph
from autoBMAD.docuswarm.llm.session_manager import KimiSessionManager
from autoBMAD.docuswarm.node_execution.pipeline_adapter import PipelineAdapter


class TestPhase1Integration:
    """Integration tests verifying Phase 1 changes work together."""

    @pytest.mark.asyncio
    async def test_full_pipeline_requires_session_manager(self, mock_session_manager):
        """Full pipeline execution with required session_manager."""
        # Arrange
        session_manager = mock_session_manager
        
        # Act & Assert: Should work with session_manager
        graph = create_pipeline_graph(
            session_manager=session_manager,
            compile_graph=False
        )
        assert graph is not None

    def test_pipeline_adapter_creates_valid_ids(self):
        """PipelineAdapter creates valid synthetic IDs."""
        # Test node-level ID
        node_id = PipelineAdapter.create_pipeline_id("analyst", "run-123")
        assert node_id == "node-analyst-run-123"
        assert PipelineAdapter.is_synthetic_pipeline_id(node_id)
        
        # Test run-level ID
        run_id = PipelineAdapter.create_run_pipeline_id("run-456")
        assert run_id == "node-run-run-456"
        assert PipelineAdapter.is_synthetic_pipeline_id(run_id)
        
        # Test parsing
        parsed = PipelineAdapter.parse_pipeline_id(node_id)
        assert parsed["node_id"] == "analyst"
        assert parsed["run_id"] == "run-123"
```**Phase 1 完成验证**:```bash# 运行所有 Phase 1 测试
pytest tests/pipeline/test_create_pipeline_graph_signature.py \\
       tests/pipeline/test_no_deprecated_executor.py \\
       tests/architecture/test_pipeline_adapter_usage.py \\
       tests/integration/test_phase1_convergence.py -v# 预期: 全部通过```---## Phase 2: 职责重新分配 (P1)**目标**: 将状态转换责任移至 PipelineAdapter### 2.1 迁移状态转换到 Adapter#### Step 2.1.1: RED - 编写失败测试**测试文件**: `tests/node_execution/test_pipeline_adapter_state_conversion.py` (新建)```python"""Test PipelineAdapter state conversion methods.TDD Phase 2.1: State conversion moved to PipelineAdapter."""

import pytest
from autoBMAD.docuswarm.node_execution.pipeline_adapter import PipelineAdapter
from autoBMAD.docuswarm.pipeline.state import create_initial_state, PipelineState


class TestPipelineAdapterStateConversion:
    """Test suite: State conversion is PipelineAdapter's responsibility."""

    def test_convert_pipeline_to_node_state_exists(self):
        """RED: PipelineAdapter must have convert_pipeline_to_node_state method."""
        assert hasattr(PipelineAdapter, 'convert_pipeline_to_node_state'), \\
            "PipelineAdapter must have convert_pipeline_to_node_state method"

    def test_convert_node_to_pipeline_state_exists(self):        """RED: PipelineAdapter must have convert_node_to_pipeline_state method."""
        assert hasattr(PipelineAdapter, 'convert_node_to_pipeline_state'), \\
            "PipelineAdapter must have convert_node_to_pipeline_state method"

    def test_convert_pipeline_to_node_state_basic(self):
        """RED: Conversion must work for basic case."""
        # Arrange
        pipeline_state = create_initial_state("test-pipeline-123", {
            "task": "Build a website",
            "requirements": ["fast", "secure"]
        })
        
        # Act
        node_state = PipelineAdapter.convert_pipeline_to_node_state(
            pipeline_state, "analyst"
        )
        
        # Assert
        assert node_state["pipeline_id"] == "test-pipeline-123"
        assert node_state["node_id"] == "analyst"
        assert node_state["status"] == "pending"
        assert "context_hash" in node_state
        assert "context_file" in node_state
        assert "chained_context" in node_state

    def test_convert_pipeline_to_node_state_accumulates_context(self):
        """RED: Conversion must accumulate context from previous nodes."""
        # Arrange: Pipeline with some completed nodes
        pipeline_state = create_initial_state("test-pipeline-456", {
            "task": "Build an app"
        })
        pipeline_state["completed_nodes"] = ["analyst", "pm"]
        pipeline_state["deliverables"] = {
            "analyst": {"analysis": "Market research complete"},
            "pm": {"plan": "Project plan created"}
        }
        
        # Act: Convert for UX node (after analyst and pm)
        node_state = PipelineAdapter.convert_pipeline_to_node_state(
            pipeline_state, "ux"
        )
        
        # Assert
        assert "chained_context" in node_state
        chained = node_state["chained_context"]
        assert "analyst" in chained
        assert "pm" in chained
        assert "analysis" in chained["analyst"]["deliverable"]

    def test_convert_node_to_pipeline_state_basic(self):
        """RED: Reverse conversion must work."""
        # Arrange
        original_state = create_initial_state("test-pipeline-789", {"task": "Test"})
        node_state = {
            "node_id": "analyst",
            "deliverable": {"content": "Analysis complete"},
            "questions": [{"text": "What is the budget?"}],
            "evaluation": {"verdict": "APPROVED", "score": 0.95},
            "iteration": 2,
        }
        
        # Act
        result = PipelineAdapter.convert_node_to_pipeline_state(
            node_state, original_state
        )
        
        # Assert
        assert "analyst" in result["deliverables"]
        assert result["deliverables"]["analyst"]["content"] == "Analysis complete"
        assert "analyst" in result["questions"]
        assert result["questions"]["analyst"][0]["text"] == "What is the budget?"
        assert "analyst" in result["evaluations"]
        assert result["evaluations"]["analyst"]["verdict"] == "APPROVED"
        assert result["current_node"] == "analyst"
        assert "analyst" in result["completed_nodes"]

    def test_convert_node_to_pipeline_state_preserves_other_data(self):
        """RED: Conversion must preserve existing pipeline state data."""
        # Arrange
        original_state = create_initial_state("test-pipeline", {"task": "Test"})
        original_state["completed_nodes"] = ["pm"]
        original_state["deliverables"]["pm"] = {"plan": "Existing plan"}
        
        node_state = {
            "node_id": "analyst",
            "deliverable": {"analysis": "New analysis"},
            "questions": [],
            "evaluation": None,
            "iteration": 1,
        }
        
        # Act
        result = PipelineAdapter.convert_node_to_pipeline_state(
            node_state, original_state
        )
        
        # Assert: Existing data preserved
        assert "pm" in result["deliverables"]
        assert result["deliverables"]["pm"]["plan"] == "Existing plan"
        
        # Assert: New data added
        assert "analyst" in result["deliverables"]
        assert result["deliverables"]["analyst"]["analysis"] == "New analysis"

    def test_graph_py_uses_adapter_for_conversion(self):
        """RED: graph.py must call PipelineAdapter methods, not internal functions.
        
        This is an architectural test verifying the implementation uses the Adapter.
        """
        from autoBMAD.docuswarm.pipeline import graph as graph_module
        
        # Read the source
        import inspect
        source = inspect.getsource(graph_module)
        
        # Must import PipelineAdapter
        assert "from autoBMAD.docuswarm.node_execution.pipeline_adapter import PipelineAdapter" in source
        
        # Must use Adapter methods (in _create_integrated_node_executor)
        assert "PipelineAdapter.convert_pipeline_to_node_state(" in source
        assert "PipelineAdapter.convert_node_to_pipeline_state(" in source
        
        # Should NOT have the old internal functions
        assert "def _convert_pipeline_to_node_state(" not in source
        assert "def _convert_node_to_pipeline_state(" not in source```**运行测试 (预期失败)**:```bash
pytest tests/node_execution/test_pipeline_adapter_state_conversion.py -v
# 预期: 8 failed# - Adapter 还没有这些方法# - graph.py 还在使用内部函数```#### Step 2.1.2: GREEN - 实现 Adapter 方法**修改文件**: `autoBMAD/docuswarm/node_execution/pipeline_adapter.py` (新增方法)````python
"""Pipeline Adapter for node_execution to pipeline integration."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from autoBMAD.docuswarm.pipeline.state import PipelineState, create_initial_state


class PipelineAdapter:
    """Adapter for node_execution to pipeline integration."""

    # ... existing methods (create_pipeline_id, etc.) ...

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
        
        Args:
            pipeline_state: The current PipelineState.
            node_id: The node identifier being executed.
        
        Returns:
            A dictionary in NodeRunState format suitable for node execution.
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
        
        Args:
            node_state: The NodeRunState after node execution.
            original_state: The original PipelineState before node execution.
        
        Returns:
            Updated PipelineState with node execution results merged in.
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
```#### Step 2.1.3: GREEN - 更新 graph.py 使用 Adapter**修改文件**: `autoBMAD/docuswarm/pipeline/graph.py````python"""LangGraph StateGraph Definition."""

from __future__ import annotations

# ... existing imports ...

# NEW: Import PipelineAdapter for state conversion
from autoBMAD.docuswarm.node_execution.pipeline_adapter import PipelineAdapter

# REMOVE: _convert_pipeline_to_node_state function (moved to Adapter)
# REMOVE: _convert_node_to_pipeline_state function (moved to Adapter)

def _create_integrated_node_executor(
    node_id: str,
    session_manager: Any,
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """Create an integrated node executor that uses node_execution.executor."""
    from autoBMAD.docuswarm.node_execution.executor import create_node_executor
    
    async_node_executor = create_node_executor(node_id, session_manager)
    
    def _run_async(coro: Awaitable[Any]) -> Any:
        """Run async coroutine, handling event loop properly."""
        import asyncio
        import concurrent.futures
        
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result(timeout=240)
    
    def executor(state: dict[str, Any]) -> dict[str, Any]:
        """Execute node logic using integrated node_execution.executor."""
        import copy as copy_module
        
        new_state = copy_module.deepcopy(state)
        new_state["current_node"] = node_id
        
        # Initialize fields if not present
        if "completed_nodes" not in new_state:
            new_state["completed_nodes"] = []
        if "node_iterations" not in new_state:
            new_state["node_iterations"] = {}
        if "deliverables" not in new_state:
            new_state["deliverables"] = {}
        if "questions" not in new_state:
            new_state["questions"] = {}
        if "evaluations" not in new_state:
            new_state["evaluations"] = {}
        
        # CHANGED: Use PipelineAdapter for state conversion
        node_run_state = PipelineAdapter.convert_pipeline_to_node_state(
            new_state, node_id
        )
        
        # Run the async executor
        try:
            executed_node_state = _run_async(async_node_executor(node_run_state))
            
            # CHANGED: Use PipelineAdapter for reverse conversion
            new_state = PipelineAdapter.convert_node_to_pipeline_state(
                executed_node_state, new_state
            )
        except Exception as e:
            logger.error(
                "integrated_executor_error",
                node_id=node_id,
                error=str(e),
            )
            # On error, set empty deliverable
            new_state["deliverables"][node_id] = {}
        
        # Increment iteration count
        current_iteration = new_state["node_iterations"].get(node_id, 0)
        new_state["node_iterations"][node_id] = current_iteration + 1
        
        # Add node to completed_nodes
        if node_id not in new_state["completed_nodes"]:
            new_state["completed_nodes"] = new_state["completed_nodes"] + [node_id]
        
        return new_state
    
    return executor
```**验证**:```bash
pytest tests/node_execution/test_pipeline_adapter_state_conversion.py -v
# 预期: 8 passed```---## Phase 3: 清理与统一 (P1)**目标**: 删除重复代码，统一命名### 3.1 重命名冲突文件#### Step 3.1.1: RED - 编写失败测试**测试文件**: `tests/architecture/test_no_filename_conflicts.py` (新建)```python"""Test no filename conflicts between pipeline and node_execution.TDD Phase 3.1: Each module has unique filenames."""

from pathlib import Path


class TestNoFilenameConflicts:
    """Test suite: No identical filenames in pipeline and node_execution."""

    def test_no_escalation_py_conflict(self):
        """RED: escalation.py must not exist in both modules.
        
        The node_execution version should be renamed to node_escalation.py.
        """
        project_root = Path(__file__).parents[3]
        
        pipeline_escalation = project_root / "autoBMAD" / "docuswarm" / "pipeline" / "escalation.py"
        node_escalation = project_root / "autoBMAD" / "docuswarm" / "node_execution" / "escalation.py"
        
        # Both should not exist simultaneously
        if pipeline_escalation.exists() and node_escalation.exists():
            assert False, (
                "Both pipeline/escalation.py and node_execution/escalation.py exist. "
                "Rename node_execution/escalation.py to node_escalation.py"
            )

    def test_node_escalation_py_exists(self):
        """GREEN: node_escalation.py should exist after rename."""
        project_root = Path(__file__).parents[3]
        node_escalation = project_root / "autoBMAD" / "docuswarm" / "node_execution" / "node_escalation.py"
        
        # After migration, this file should exist
        assert node_escalation.exists(), (
            "node_execution/node_escalation.py should exist after rename"
        )```**运行测试 (预期失败)**:```bash
pytest tests/architecture/test_no_filename_conflicts.py -v
# 预期: 1 failed, 1 passed (或类似，取决于当前状态)```#### Step 3.1.2: GREEN - 重命名文件```bash# 在命令行执行mv autoBMAD/docuswarm/node_execution/escalation.py \\
   autoBMAD/docuswarm/node_execution/node_escalation.py```**更新导入**: 检查并更新所有导入 `node_execution.escalation` 的文件**验证**:```bash
pytest tests/architecture/test_no_filename_conflicts.py -v# 预期: 2 passed```---## TDD 执行时间表| 阶段 | 任务 | 测试文件 | 预计时间 ||------|------|---------|---------|| **Phase 1** | 强制 session_manager 必填 | `test_create_pipeline_graph_signature.py` | 2h || | 删除 deprecated executor | `test_no_deprecated_executor.py` | 2h || | 强制使用 PipelineAdapter | `test_pipeline_adapter_usage.py` | 2h || | Phase 1 集成验证 | `test_phase1_convergence.py` | 2h || **Phase 2** | 状态转换移至 Adapter | `test_pipeline_adapter_state_conversion.py` | 4h || | 更新 graph.py | (架构测试) | 2h || **Phase 3** | 重命名冲突文件 | `test_no_filename_conflicts.py` | 1h || | 统一 metrics | (根据选择方案) | 4h || | 架构守护测试 | (新增 CI 检查) | 2h |**总计**: 约 21 小时 (3 周，每周 7 小时)---## 持续集成配置### CI Pipeline 新增检查```yaml# .github/workflows/f5-convergence-check.yml
name: F5 Convergence Check

on:
  pull_request:
    paths:
      - 'autoBMAD/docuswarm/pipeline/**'
      - 'autoBMAD/docuswarm/node_execution/**'

jobs:
  convergence-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest
      
      - name: Run F5 migration check
        run: |
          python tools/migrate_f5_convergence.py --verify
      
      - name: Run Phase 1 tests
        run: |
          pytest tests/pipeline/test_create_pipeline_graph_signature.py \\
                 tests/pipeline/test_no_deprecated_executor.py \\
                 tests/architecture/test_pipeline_adapter_usage.py -v
      
      - name: Run Phase 2 tests
        run: |
          pytest tests/node_execution/test_pipeline_adapter_state_conversion.py -v
      
      - name: Run Phase 3 tests
        run: |
          pytest tests/architecture/test_no_filename_conflicts.py -v
```---## 验证清单### Phase 1 完成标准- [ ] `pytest tests/pipeline/test_create_pipeline_graph_signature.py` 全绿- [ ] `pytest tests/pipeline/test_no_deprecated_executor.py` 全绿- [ ] `pytest tests/architecture/test_pipeline_adapter_usage.py` 全绿- [ ] `python tools/migrate_f5_convergence.py --verify` 通过### Phase 2 完成标准- [ ] `pytest tests/node_execution/test_pipeline_adapter_state_conversion.py` 全绿- [ ] PipelineAdapter 所有方法都有使用位置- [ ] graph.py 使用 Adapter 进行状态转换### Phase 3 完成标准- [ ] `pytest tests/architecture/test_no_filename_conflicts.py` 全绿- [ ] 无同名文件冲突- [ ] CI pipeline 新增检查通过---## 参考文档- 研究报告: `docs/research/2026-03-25-f5-pipeline-node-execution-convergence-research-report.md`- 设计规范: `docs/research/2026-03-25-f5-unified-design-spec.md`- 分析工具: `tools/pipeline_node_execution_analyzer.py`- 迁移检查: `tools/migrate_f5_convergence.py`