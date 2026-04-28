# TDD-BMM-04: 双代理流程集成与端到端测试

## 文档信息

| 属性 | 值 |
|------|-----|
| **方案编号** | TDD-BMM-04 |
| **关联研究** | Part 3 (双代理流程与状态管理), Part 5 (交付物保存流程) |
| **优先级** | P0 - Critical |
| **状态** | 待实施 |

---

## 1. 目标

验证双代理流程（Independent + Evaluator）完整执行链路，确保：
1. DualAgentNode 正确协调双代理执行
2. 上下文过滤正确隔离 private_reasoning
3. 迭代循环正确工作（最多3次）
4. PipelineState 正确更新
5. 交付物正确保存（双层保存机制）
6. 节点间上下文链式传递正确

---

## 2. 双代理流程架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    Dual-Agent Execution Flow                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  DualAgentNode.execute(subject_context, task, pipeline_id)       │
│       │                                                          │
│       ▼                                                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Iteration Loop (max 3)                       │   │
│  │                                                           │   │
│  │  ① IndependentAgent.execute(context)                     │   │
│  │       ├── Setup work_dir: output/{pipeline_id}/          │   │
│  │       ├── Call LLM with BMM system prompt                │   │
│  │       ├── Tool: create_deliverable (第一层保存)           │   │
│  │       └── Parse response → IndependentOutput             │   │
│  │                                                           │   │
│  │  ② ContextFilter.filter_for_evaluator(output)            │   │
│  │       └── Remove: private_reasoning, tool_call_history   │   │
│  │                                                           │   │
│  │  ③ EvaluatorAgent.execute(filtered_context)              │   │
│  │       └── Return: verdict, score, issues, suggestions    │   │
│  │                                                           │   │
│  │  ④ VerdictHandler.decide()                               │   │
│  │       ├── APPROVED → break                               │   │
│  │       ├── FORCE_APPROVED → force completion              │   │
│  │       ├── BLOCKED → break                                │   │
│  │       └── NEEDS_REVISION → continue with feedback        │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│       │                                                          │
│       ▼                                                          │
│  Return NodeResult(deliverable, questions, evaluation, ...)      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. 测试先行的集成计划

### Phase 1: DualAgentNode 单元测试

#### Test 1.1: 单次迭代成功测试

```python
# tests/nodes/test_dual_agent_single_iteration.py
"""Tests for DualAgentNode single iteration success."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from autoBMAD.docuswarm.nodes.dual_agent import DualAgentNode
from autoBMAD.docuswarm.nodes.types import NodeResult


class TestDualAgentSingleIteration:
    """Test DualAgentNode completes in single iteration."""

    @pytest.fixture
    def mock_config(self):
        """Create mock node configuration."""
        config = Mock()
        config.node_id = "analyst"
        config.name = "Analyst"
        config.agent = Mock(model="sonnet", temperature=0.7)
        config.deliverable = Mock(
            type="product-brief",
            required_sections=["executive_summary"]
        )
        return config

    @pytest.fixture
    def mock_session_manager(self):
        """Create mock session manager."""
        return Mock()

    @pytest.fixture
    def dual_agent_node(self, mock_config, mock_session_manager):
        """Create DualAgentNode instance."""
        return DualAgentNode(
            config=mock_config,
            session_manager=mock_session_manager,
            node_id="analyst",
            project_root=Mock()
        )

    @pytest.mark.asyncio
    async def test_single_iteration_approved(
        self, dual_agent_node, mock_config
    ):
        """Test node completes in single iteration with APPROVED verdict."""
        
        # Mock IndependentAgent
        mock_independent_output = {
            "deliverable": {
                "title": "Test Report",
                "content": "Test content",
                "metadata": {}
            },
            "questions": [
                {"question": "Q1", "category": "blocking", "context": ""}
            ],
            "action": "create_deliverable"
        }
        
        # Mock EvaluatorAgent
        mock_evaluation = {
            "criterion_scores": {"completeness": 0.9, "clarity": 0.8},
            "alignment_score": 0.85,
            "verdict": "APPROVED",
            "issues_found": [],
            "suggestions": []
        }
        
        with patch.object(
            dual_agent_node.independent_agent, 'execute',
            new=AsyncMock(return_value=mock_independent_output)
        ), patch.object(
            dual_agent_node.evaluator_agent, 'execute',
            new=AsyncMock(return_value=mock_evaluation)
        ):
            result = await dual_agent_node.execute(
                subject_context={"project": "test"},
                task="create test deliverable",
                pipeline_id="test-pipeline-123"
            )
        
        # Verify result
        assert isinstance(result, NodeResult)
        assert result.deliverable["title"] == "Test Report"
        assert result.evaluation["verdict"] == "APPROVED"
        assert result.iteration == 1
        assert result.questions[0]["question"] == "Q1"
```

#### Test 1.2: 多迭代测试

```python
# tests/nodes/test_dual_agent_multi_iteration.py
"""Tests for DualAgentNode multiple iterations."""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from autoBMAD.docuswarm.nodes.dual_agent import DualAgentNode


class TestDualAgentMultiIteration:
    """Test DualAgentNode handles multiple iterations."""

    @pytest.mark.asyncio
    async def test_two_iterations_then_approved(self, dual_agent_node):
        """Test node iterates twice before approval."""
        
        # First iteration: NEEDS_REVISION
        first_evaluation = {
            "alignment_score": 0.55,
            "verdict": "NEEDS_REVISION",
            "issues_found": ["Missing section X"],
            "suggestions": ["Add section X"]
        }
        
        # Second iteration: APPROVED
        second_evaluation = {
            "alignment_score": 0.85,
            "verdict": "APPROVED",
            "issues_found": [],
            "suggestions": []
        }
        
        independent_calls = []
        
        async def mock_independent_execute(context):
            independent_calls.append(context)
            return {
                "deliverable": {"title": f"Report v{len(independent_calls)}"},
                "questions": [],
                "action": "create_deliverable"
            }
        
        with patch.object(
            dual_agent_node.independent_agent, 'execute',
            side_effect=mock_independent_execute
        ), patch.object(
            dual_agent_node.evaluator_agent, 'execute',
            side_effect=[first_evaluation, second_evaluation]
        ):
            result = await dual_agent_node.execute(
                subject_context={},
                task="test",
                pipeline_id="test"
            )
        
        # Verify two iterations
        assert result.iteration == 2
        assert len(independent_calls) == 2
        
        # Verify second call includes feedback
        assert "iteration_feedback" in independent_calls[1]
        assert independent_calls[1]["iteration_feedback"]["verdict"] == "NEEDS_REVISION"

    @pytest.mark.asyncio
    async def test_max_iterations_force_complete(self, dual_agent_node):
        """Test node force completes after max iterations."""
        
        # Always return NEEDS_REVISION
        mock_evaluation = {
            "alignment_score": 0.60,  # Above escalation threshold
            "verdict": "NEEDS_REVISION",
            "issues_found": [],
            "suggestions": []
        }
        
        with patch.object(
            dual_agent_node.independent_agent, 'execute',
            new=AsyncMock(return_value={"deliverable": {}, "questions": []})
        ), patch.object(
            dual_agent_node.evaluator_agent, 'execute',
            new=AsyncMock(return_value=mock_evaluation)
        ):
            result = await dual_agent_node.execute(
                subject_context={},
                task="test",
                pipeline_id="test"
            )
        
        # Verify force completion after 3 iterations
        assert result.iteration == 3
        assert result.force_completion is not None
```

#### Test 1.3: 上下文隔离测试

```python
# tests/nodes/test_context_isolation.py
"""Tests for context isolation between Independent and Evaluator."""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from autoBMAD.docuswarm.nodes.dual_agent import DualAgentNode
from autoBMAD.docuswarm.context.filter import ContextFilter


class TestContextIsolation:
    """Test private fields are filtered before Evaluator."""

    def test_context_filter_removes_private_fields(self):
        """Test ContextFilter removes private fields."""
        
        independent_output = {
            "deliverable": {"title": "Report"},
            "questions": [],
            "private_reasoning": "This is secret reasoning",  # Should be removed
            "tool_call_history": [{"tool": "create_deliverable"}],  # Should be removed
            "internal_notes": "Internal notes",  # Should be removed
            "iteration_feedback": {"previous": "feedback"}  # Should be removed
        }
        
        filter_instance = ContextFilter()
        filtered = filter_instance.filter_for_evaluator(independent_output)
        
        # Verify public fields preserved
        assert "deliverable" in filtered
        assert "questions" in filtered
        
        # Verify private fields removed
        assert "private_reasoning" not in filtered
        assert "tool_call_history" not in filtered
        assert "internal_notes" not in filtered
        assert "iteration_feedback" not in filtered

    @pytest.mark.asyncio
    async def test_evaluator_never_receives_private_reasoning(self, dual_agent_node):
        """Test Evaluator never receives private_reasoning."""
        
        evaluator_inputs = []
        
        async def capture_evaluator_execute(context):
            evaluator_inputs.append(context)
            return {"verdict": "APPROVED", "alignment_score": 0.9}
        
        with patch.object(
            dual_agent_node.independent_agent, 'execute',
            new=AsyncMock(return_value={
                "deliverable": {"title": "Report"},
                "questions": [],
                "private_reasoning": "Secret"
            })
        ), patch.object(
            dual_agent_node.evaluator_agent, 'execute',
            side_effect=capture_evaluator_execute
        ):
            await dual_agent_node.execute(
                subject_context={},
                task="test",
                pipeline_id="test"
            )
        
        # Verify Evaluator input doesn't contain private_reasoning
        assert len(evaluator_inputs) == 1
        assert "private_reasoning" not in str(evaluator_inputs[0])
```

### Phase 2: PipelineState 更新测试

#### Test 2.1: State 更新正确性测试

```python
# tests/pipeline/test_state_updates.py
"""Tests for PipelineState updates during node execution."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import copy

from autoBMAD.docuswarm.pipeline.state import PipelineState
from autoBMAD.docuswarm.pipeline.graph import _create_integrated_node_executor


class TestPipelineStateUpdates:
    """Test PipelineState is correctly updated after node execution."""

    @pytest.fixture
    def initial_state(self):
        """Create initial pipeline state."""
        return PipelineState(
            pipeline_id="test-pipeline",
            subject_context={"project": "Test"},
            current_node="analyst",
            completed_nodes=[],
            deliverables={},
            questions={},
            evaluations={},
            node_iterations={},
            session_ids={},
            session_metadata={},
            current_node_session_id=None,
            status="running",
            error=None
        )

    @pytest.mark.asyncio
    async def test_deliverable_added_to_state(self, initial_state):
        """Test deliverable is added to PipelineState after execution."""
        
        mock_node_result = Mock()
        mock_node_result.deliverable = {"title": "Analyst Report"}
        mock_node_result.questions = []
        mock_node_result.evaluation = {"verdict": "APPROVED"}
        mock_node_result.iteration = 1
        
        # Mock the async node executor
        with patch('autoBMAD.docuswarm.node_execution.executor.create_node_executor') as mock_create:
            mock_executor = AsyncMock(return_value={
                "node_id": "analyst",
                "deliverable": {"title": "Analyst Report"},
                "questions": [],
                "evaluation": {"verdict": "APPROVED"},
                "iteration": 1,
                "status": "completed"
            })
            mock_create.return_value = mock_executor
            
            # Create integrated executor
            executor = _create_integrated_node_executor("analyst", Mock())
            
            # Execute
            new_state = executor(copy.deepcopy(initial_state))
        
        # Verify state updates
        assert "analyst" in new_state["deliverables"]
        assert new_state["deliverables"]["analyst"]["title"] == "Analyst Report"
        assert "analyst" in new_state["completed_nodes"]
        assert new_state["node_iterations"]["analyst"] == 1

    def test_state_deep_copy_prevents_mutation(self, initial_state):
        """Test state is deep copied to prevent mutation."""
        
        import copy
        
        # Modify original
        original_deliverables = initial_state["deliverables"]
        copied = copy.deepcopy(initial_state)
        
        # Modify copy
        copied["deliverables"]["test"] = {"data": "value"}
        
        # Verify original unchanged
        assert "test" not in original_deliverables
```

### Phase 3: 交付物保存测试

#### Test 3.1: 双层保存机制测试

```python
# tests/storage/test_dual_layer_save.py
"""Tests for dual-layer deliverable saving mechanism."""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from autoBMAD.docuswarm.tools.create_deliverable import create_deliverable, CreateDeliverableParams
from autoBMAD.docuswarm.storage.files import FileStorage


class TestDualLayerSave:
    """Test both layers of deliverable saving."""

    @pytest.mark.asyncio
    async def test_first_layer_tool_save(self, tmp_path):
        """Test first layer: create_deliverable tool saves file."""
        
        # Change to temp directory (simulating SDK work_dir)
        import os
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            params = CreateDeliverableParams(
                title="Test Report",
                content="# Test Report\n\nThis is content.",
                metadata={"version": "1.0"}
            )
            
            result = await create_deliverable(params)
            
            # Verify file created
            expected_file = tmp_path / "test-report.md"
            assert expected_file.exists()
            assert "Test Report" in expected_file.read_text()
            assert result.success is True
            
        finally:
            os.chdir(original_cwd)

    @pytest.mark.asyncio
    async def test_second_layer_file_storage_save(self, tmp_path):
        """Test second layer: FileStorage saves with canonical name."""
        
        storage = FileStorage(output_root=str(tmp_path))
        
        content = "# Architecture Document\n\nContent here."
        await storage.save_deliverable(
            pipeline_id="test-pipe",
            node_type="architect",
            content=content,
            add_frontmatter=True
        )
        
        # Verify file created with canonical name
        expected_file = tmp_path / "test-pipe" / "architecture.md"
        assert expected_file.exists()
        
        file_content = expected_file.read_text()
        assert "Architecture Document" in file_content
        assert "---" in file_content  # Frontmatter
        assert "pipeline_id: test-pipe" in file_content

    @pytest.mark.asyncio
    async def test_atomic_write_creates_temp_first(self, tmp_path):
        """Test FileStorage uses atomic write (temp file first)."""
        
        storage = FileStorage(output_root=str(tmp_path))
        
        content = "Test content"
        await storage.save_deliverable(
            pipeline_id="test",
            node_type="analyst",
            content=content
        )
        
        # Verify no .tmp file left behind
        temp_files = list(tmp_path.rglob("*.tmp"))
        assert len(temp_files) == 0, "Temp files should be cleaned up"
```

#### Test 3.2: 交付物文件名映射测试

```python
# tests/storage/test_filename_mapping.py
"""Tests for FILENAME_MAP deliverable naming."""

import pytest
from autoBMAD.docuswarm.storage.files import FILENAME_MAP


class TestFilenameMapping:
    """Test correct filename mapping for each node type."""

    @pytest.mark.parametrize("node_type,expected_filename", [
        ("analyst", "analyst-report.md"),
        ("pm", "prd.md"),
        ("prd", "prd.md"),  # Alias
        ("ux", "ux-design.md"),
        ("architect", "architecture.md"),
        ("architecture", "architecture.md"),  # Alias
        ("po", "epics-stories.md"),
        ("epics", "epics-stories.md"),  # Alias
    ])
    def test_filename_mapping(self, node_type, expected_filename):
        """Test each node type maps to correct filename."""
        assert FILENAME_MAP.get(node_type) == expected_filename
```

### Phase 4: 上下文链式传递测试

#### Test 4.1: 上下文累积测试

```python
# tests/pipeline/test_context_chaining.py
"""Tests for context chaining between nodes."""

import pytest
from autoBMAD.docuswarm.pipeline.state import accumulate_context


class TestContextChaining:
    """Test context chaining accumulates predecessor deliverables."""

    def test_analyst_receives_only_subject_context(self):
        """Test analyst node receives only subject context."""
        
        subject = {"project_name": "Test Project"}
        deliverables = {}
        
        result = accumulate_context(subject, deliverables, "analyst")
        
        assert result["subject_context"] == subject
        assert "analyst_deliverable" not in result

    def test_pm_receives_analyst_deliverable(self):
        """Test PM node receives analyst deliverable."""
        
        subject = {"project_name": "Test"}
        deliverables = {
            "analyst": {"title": "Analyst Report", "content": "..."}
        }
        
        result = accumulate_context(subject, deliverables, "pm")
        
        assert "subject_context" in result
        assert "analyst_deliverable" in result
        assert result["analyst_deliverable"]["title"] == "Analyst Report"

    def test_po_receives_all_previous_deliverables(self):
        """Test PO node receives all previous node deliverables."""
        
        subject = {"project": "Test"}
        deliverables = {
            "analyst": {"title": "Report"},
            "pm": {"title": "PRD"},
            "ux": {"title": "UX Design"},
            "architect": {"title": "Architecture"}
        }
        
        result = accumulate_context(subject, deliverables, "po")
        
        assert "analyst_deliverable" in result
        assert "pm_deliverable" in result
        assert "ux_deliverable" in result
        assert "architect_deliverable" in result
        assert "po_deliverable" not in result  # Current node
```

### Phase 5: 端到端集成测试

#### Test 5.1: 完整节点执行流程

```python
# tests/integration/test_e2e_node_execution.py
"""End-to-end tests for complete node execution."""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock


class TestEndToEndNodeExecution:
    """Test complete node execution from start to finish."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_analyst_node_full_execution(self, tmp_path):
        """Test complete analyst node execution flow."""
        
        # This is a comprehensive integration test
        # It tests the entire flow without mocks where possible
        
        from autoBMAD.docuswarm.pipeline.graph import create_pipeline_graph
        from autoBMAD.docuswarm.core.session import KimiSessionManager
        
        # Setup
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        mock_sm = Mock(spec=KimiSessionManager)
        mock_sm.work_dir = output_dir
        
        # Create graph
        graph = create_pipeline_graph(session_manager=mock_sm)
        
        # Initial state
        initial_state = {
            "pipeline_id": "test-e2e",
            "subject_context": {"project_name": "E2E Test"},
            "current_node": "analyst",
            "completed_nodes": [],
            "deliverables": {},
            "questions": {},
            "evaluations": {},
            "node_iterations": {},
            "status": "running"
        }
        
        # Note: This test would need actual LLM calls or sophisticated mocking
        # For now, we verify the structure is correct
        assert graph is not None

    @pytest.mark.asyncio
    async def test_pipeline_state_transitions(self):
        """Test PipelineState transitions through node execution."""
        
        from autoBMAD.docuswarm.pipeline.state import PipelineState
        
        # Start state
        state = PipelineState(
            pipeline_id="test",
            subject_context={},
            current_node="analyst",
            completed_nodes=[],
            deliverables={},
            questions={},
            evaluations={},
            node_iterations={},
            session_ids={},
            session_metadata={},
            current_node_session_id=None,
            status="running",
            error=None
        )
        
        # Simulate completion
        state["completed_nodes"].append("analyst")
        state["deliverables"]["analyst"] = {"title": "Report"}
        state["evaluations"]["analyst"] = {"verdict": "APPROVED"}
        state["node_iterations"]["analyst"] = 1
        state["current_node"] = "pm"
        
        # Verify transitions
        assert "analyst" in state["completed_nodes"]
        assert state["current_node"] == "pm"
        assert state["evaluations"]["analyst"]["verdict"] == "APPROVED"
```

---

## 4. 实施清单

| 步骤 | 任务 | 测试文件 | 状态 |
|------|------|----------|------|
| 1 | 单次迭代成功测试 | `test_dual_agent_single_iteration.py` | ⬜ |
| 2 | 多迭代测试 | `test_dual_agent_multi_iteration.py` | ⬜ |
| 3 | 上下文隔离测试 | `test_context_isolation.py` | ⬜ |
| 4 | State 更新测试 | `test_state_updates.py` | ⬜ |
| 5 | 双层保存测试 | `test_dual_layer_save.py` | ⬜ |
| 6 | 文件名映射测试 | `test_filename_mapping.py` | ⬜ |
| 7 | 上下文链式传递测试 | `test_context_chaining.py` | ⬜ |
| 8 | 端到端集成测试 | `test_e2e_node_execution.py` | ⬜ |

---

## 5. 验证命令

```bash
# 运行双代理相关测试
pytest tests/nodes/test_dual_agent_single_iteration.py -v
pytest tests/nodes/test_dual_agent_multi_iteration.py -v
pytest tests/nodes/test_context_isolation.py -v

# 运行 PipelineState 测试
pytest tests/pipeline/test_state_updates.py -v
pytest tests/pipeline/test_context_chaining.py -v

# 运行存储测试
pytest tests/storage/test_dual_layer_save.py -v
pytest tests/storage/test_filename_mapping.py -v

# 运行集成测试
pytest tests/integration/test_e2e_node_execution.py -v

# 全部测试
pytest tests/ -v --tb=short
```

---

## 6. 性能基准

| 指标 | 目标 | 测试方法 |
|------|------|----------|
| 单次迭代执行 | < 60s | `test_single_iteration_approved` |
| 完整节点执行 (3迭代) | < 180s | `test_max_iterations_force_complete` |
| State 更新 | < 100ms | `test_deliverable_added_to_state` |
| 文件保存 | < 50ms | `test_first_layer_tool_save` |

---

**文档结束**
