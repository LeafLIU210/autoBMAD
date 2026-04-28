"""
DocuSwarm Context Refactor - TDD 测试模板

使用说明:
1. 根据实施的 Phase 复制对应模板
2. 填写具体的测试逻辑
3. 运行测试确保失败 (Red)
4. 实现代码使测试通过 (Green)
5. 重构代码 (Refactor)

参考:
- TDD 主方案: docs/solution/2026-03-17-docuswarm-context-refactor-tdd-master-plan.md
- 实施路线图: docs/solution/2026-03-17-docuswarm-context-refactor-tdd-implementation-roadmap.md
"""

# =============================================================================
# Template 1: Phase 1 (P1-1) - UpdateContextTool 测试
# =============================================================================

"""
File: tests/unit/tools/test_update_context_binding.py
Phase: P1-1
研究问题: P1-1-001, P1-1-002
"""

import pytest
from unittest.mock import Mock, AsyncMock
from autoBMAD.docuswarm.tools.update_context import (
    UpdateContextTool,
    UpdateContextParams
)
from autoBMAD.docuswarm.storage.state_manager import StateManager


class TestUpdateContextToolBinding:
    """Test UpdateContextTool dependency injection (P1-1)"""
    
    def test_tool_requires_state_manager(self):
        """[Red] Tool should require StateManager at initialization"""
        # Act & Assert
        with pytest.raises(ValueError, match="StateManager is required"):
            UpdateContextTool()  # No state_manager provided
    
    def test_tool_requires_pipeline_id(self):
        """[Red] Tool should require pipeline_id at initialization"""
        # Arrange
        mock_state_manager = Mock(spec=StateManager)
        
        # Act & Assert
        with pytest.raises(ValueError, match="pipeline_id is required"):
            UpdateContextTool(state_manager=mock_state_manager)  # No pipeline_id
    
    def test_tool_accepts_valid_dependencies(self):
        """[Red] Tool should accept valid dependencies"""
        # Arrange
        mock_state_manager = Mock(spec=StateManager)
        
        # Act
        tool = UpdateContextTool(
            state_manager=mock_state_manager,
            pipeline_id="pipeline-test-001"
        )
        
        # Assert
        assert tool._state_manager is mock_state_manager
        assert tool._pipeline_id == "pipeline-test-001"
    
    @pytest.mark.asyncio
    async def test_tool_call_delegates_to_state_manager(self):
        """[Red] Tool call should delegate to StateManager.update_shared_context"""
        # Arrange
        mock_state_manager = Mock(spec=StateManager)
        mock_state_manager.update_shared_context = AsyncMock(return_value=True)
        
        tool = UpdateContextTool(
            state_manager=mock_state_manager,
            pipeline_id="pipeline-test-001"
        )
        
        params = UpdateContextParams(
            key="facts.market_scope",
            value="global",
            operation="set"
        )
        
        # Act
        result = await tool(params)
        
        # Assert
        assert result.success is True
        mock_state_manager.update_shared_context.assert_called_once_with(
            pipeline_id="pipeline-test-001",
            update="global",
            operation="set",
            key_path="facts.market_scope"
        )


# =============================================================================
# Template 2: Phase 1 (P1-1) - IndependentAgentInput 测试
# =============================================================================

"""
File: tests/unit/node_execution/test_contracts.py
Phase: P1-1
研究问题: P1-1-002
"""

import pytest
from autoBMAD.docuswarm.node_execution.contracts import (
    IndependentAgentInput,
    validate_independent_agent_input
)


class TestIndependentAgentInputSchema:
    """Test IndependentAgentInput has shared_context field (P1-1)"""
    
    def test_has_shared_context_field(self):
        """[Red] IndependentAgentInput should have shared_context field"""
        # Arrange
        input_data: IndependentAgentInput = {
            "task_name": "test-task",
            "task_description": "test description",
            "role_supplement": "",
            "deliverable_requirements": {},
            "original_context_summary": "test context",
            "chained_deliverables_summary": [],
            "iteration_feedback": None,
            "persona_context": {},
            "shared_context": {  # P1-1: NEW FIELD
                "facts": {"key": "value"},
                "decisions": []
            }
        }
        
        # Act & Assert - Should not raise
        validate_independent_agent_input(input_data)
    
    def test_shared_context_is_optional(self):
        """[Red] shared_context should be optional for backward compatibility"""
        # Arrange - No shared_context
        input_data: IndependentAgentInput = {
            "task_name": "test-task",
            "task_description": "test description",
            "role_supplement": "",
            "deliverable_requirements": {},
            "original_context_summary": "test context",
            "chained_deliverables_summary": [],
            "iteration_feedback": None,
            "persona_context": {}
        }
        
        # Act & Assert - Should not raise
        validate_independent_agent_input(input_data)


# =============================================================================
# Template 3: Phase 1 (P1-1) - ContextManager 测试
# =============================================================================

"""
File: tests/unit/context/test_isolation.py
Phase: P1-1
研究问题: P1-1-002
"""

import pytest
from autoBMAD.docuswarm.context.isolation import ContextManager
from autoBMAD.docuswarm.node_execution.contracts import NodeExecutionContext


class TestContextManagerSharedContext:
    """Test ContextManager handles shared_context correctly (P1-1)"""
    
    def test_build_independent_input_includes_shared_context(self):
        """[Red] build_independent_input should include shared_context"""
        # Arrange
        manager = ContextManager()
        execution_context = NodeExecutionContext(
            # ... fill in required fields ...
            shared_context={
                "facts": {"market_scope": "global"},
                "open_questions": ["Q1", "Q2"]
            }
        )
        
        # Act
        result = manager.build_independent_input(execution_context)
        
        # Assert
        assert "shared_context" in result
        assert result["shared_context"]["facts"]["market_scope"] == "global"
    
    def test_build_independent_input_defaults_empty_shared_context(self):
        """[Red] build_independent_input should default to empty dict"""
        # Arrange
        manager = ContextManager()
        execution_context = NodeExecutionContext(
            # ... fill in required fields ...
            shared_context={}
        )
        
        # Act
        result = manager.build_independent_input(execution_context)
        
        # Assert
        assert "shared_context" in result
        assert result["shared_context"] == {}


# =============================================================================
# Template 4: Phase 2 (P0-3) - 单一交付物验证测试
# =============================================================================

"""
File: tests/unit/llm/test_response_validation.py
Phase: P0-3
研究问题: P0-3-002
"""

import pytest
from autoBMAD.docuswarm.llm.response import (
    validate_independent_output,
    ValidationError
)


class TestDeliverableValidationSingleTruth:
    """Test deliverable validation enforces single truth (P0-3)"""
    
    def test_file_path_is_required(self):
        """[Red] deliverable.file_path should be required"""
        # Arrange
        data = {
            "deliverable": {
                "title": "Test",
                "summary": "Brief summary",
                # file_path missing!
                "sha256": "abc123..."
            },
            "questions": []
        }
        
        # Act & Assert
        with pytest.raises(ValidationError, match="file_path is required"):
            validate_independent_output(data)
    
    def test_sha256_is_required(self):
        """[Red] deliverable.sha256 should be required"""
        # Arrange
        data = {
            "deliverable": {
                "title": "Test",
                "summary": "Brief summary",
                "file_path": "/path/to/file.md",
                # sha256 missing!
            },
            "questions": []
        }
        
        # Act & Assert
        with pytest.raises(ValidationError, match="sha256 is required"):
            validate_independent_output(data)
    
    def test_accepts_valid_metadata_only_deliverable(self):
        """[Red] Should accept deliverable with metadata only"""
        # Arrange
        data = {
            "deliverable": {
                "title": "Test Deliverable",
                "summary": "Brief summary of the document",
                "file_path": "output/pipeline-001/test.md",
                "sha256": "a3f5c8e9d2b1...",
                "word_count": 1500,
                "section_index": ["Overview", "Details"]
            },
            "questions": []
        }
        
        # Act & Assert - Should not raise
        validate_independent_output(data)


# =============================================================================
# Template 5: Phase 2 (P0-3) - Evaluator 单一真相测试
# =============================================================================

"""
File: tests/unit/context/test_isolation_evaluator.py
Phase: P0-3
研究问题: P0-3-004
"""

import pytest
from pathlib import Path
from autoBMAD.docuswarm.context.isolation import ContextManager


class TestEvaluatorInputSingleTruth:
    """Test Evaluator input enforces single truth (P0-3)"""
    
    def test_build_evaluator_input_reads_file_content(self, tmp_path):
        """[Red] build_evaluator_input should read full content from file"""
        # Arrange
        manager = ContextManager()
        
        # Create actual file
        file_path = tmp_path / "deliverable.md"
        full_content = "# Full Document\n\nThis is the complete content."
        file_path.write_text(full_content)
        
        execution_context = create_execution_context()
        deliverable = {
            "title": "Test",
            "summary": "Short summary",  # Should NOT use this
            "file_path": str(file_path),
            "sha256": "abc123"
        }
        
        # Act
        result = manager.build_evaluator_input(execution_context, deliverable)
        
        # Assert
        assert result["deliverable_body"] == full_content
        assert result["deliverable_body"] != "Short summary"
    
    def test_raises_if_file_missing(self):
        """[Red] build_evaluator_input should raise if file_path doesn't exist"""
        # Arrange
        manager = ContextManager()
        execution_context = create_execution_context()
        deliverable = {
            "title": "Test",
            "file_path": "/nonexistent/file.md",
            "sha256": "abc123"
        }
        
        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Deliverable file not found"):
            manager.build_evaluator_input(execution_context, deliverable)
    
    def test_raises_if_file_path_missing(self):
        """[Red] build_evaluator_input should raise if file_path is None"""
        # Arrange
        manager = ContextManager()
        execution_context = create_execution_context()
        deliverable = {
            "title": "Test",
            "summary": "Only summary",
            # file_path missing!
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="file_path is required"):
            manager.build_evaluator_input(execution_context, deliverable)


# =============================================================================
# Template 6: Phase 3 (P0-2) - Evaluator 原始上下文测试
# =============================================================================

"""
File: tests/unit/node_execution/test_evaluator_contracts.py
Phase: P0-2
研究问题: P0-2-003
"""

import pytest
from autoBMAD.docuswarm.node_execution.contracts import (
    EvaluatorAgentInput,
    validate_evaluator_agent_input
)


class TestEvaluatorAgentInputSchema:
    """Test EvaluatorAgentInput has original context (P0-2)"""
    
    def test_has_original_context_field(self):
        """[Red] EvaluatorAgentInput should have original_context_summary field"""
        # Arrange
        input_data: EvaluatorAgentInput = {
            "task_name": "test-task",
            "task_description": "test description",
            "original_context_summary": "Original user request: Build a task app",  # P0-2
            "deliverable_artifact": {
                "title": "Test",
                "summary": "Brief summary",
                "file_path": "/tmp/test.md",
                "sha256": "abc123"
            },
            "deliverable_body": "# Full content...",
            "criteria": []
        }
        
        # Act & Assert - Should not raise
        validate_evaluator_agent_input(input_data)
    
    def test_original_context_summary_is_optional(self):
        """[Red] original_context_summary should be optional"""
        # Arrange - No original_context_summary
        input_data: EvaluatorAgentInput = {
            "task_name": "test-task",
            "task_description": "test description",
            # original_context_summary missing
            "deliverable_artifact": {"title": "Test", "file_path": "/tmp/test.md", "sha256": "abc"},
            "deliverable_body": "Content",
            "criteria": []
        }
        
        # Act & Assert - Should not raise
        validate_evaluator_agent_input(input_data)


# =============================================================================
# Template 7: Phase 3 (P0-2) - Prompt Contract Builder 测试
# =============================================================================

"""
File: tests/unit/prompts/test_contract_builder_evaluator.py
Phase: P0-2
研究问题: P0-2-003
"""

import pytest
from autoBMAD.docuswarm.prompts.contract_builder import NodePromptContractBuilder
from autoBMAD.docuswarm.node_execution.contracts import NodeExecutionContext


class TestEvaluatorOriginalContextSection:
    """Test Evaluator prompt includes original context (P0-2)"""
    
    def test_build_evaluator_context_section_includes_original(self):
        """[Red] _build_evaluator_context_section should include original context"""
        # Arrange
        builder = NodePromptContractBuilder()
        context = NodeExecutionContext(
            # ... fill in required fields ...
            original_context={
                "content": "User wants a task management app with real-time collaboration"
            }
        )
        
        # Act
        section = builder._build_evaluator_context_section(context)
        
        # Assert
        assert "原始需求摘要" in section or "Original Context" in section
        assert "task management app" in section
    
    def test_render_evaluator_prompt_includes_original_context(self):
        """[Red] render_evaluator_prompt should include '原始需求摘要' section"""
        # Arrange
        builder = NodePromptContractBuilder()
        from autoBMAD.docuswarm.prompts.contract_builder import EvaluatorPromptContract
        
        contract = EvaluatorPromptContract(
            task_section="## Task",
            criteria_section="## Criteria",
            deliverable_section="## Deliverable",
            context_section="## 原始需求摘要\n\nUser wants a task app",  # P0-2
            deliverable_body="# Content"
        )
        
        # Act
        prompt = builder.render_evaluator_prompt(contract)
        
        # Assert
        assert "原始需求摘要" in prompt or "Original Context" in prompt
        assert "User wants a task app" in prompt


# =============================================================================
# Template 8: Phase 5 - 集成测试
# =============================================================================

"""
File: tests/integration/test_shared_context_cross_node.py
Phase: P1-1 + P0-3 + P0-2 (集成)
"""

import pytest
from autoBMAD.docuswarm.storage.state_manager import StateManager
from autoBMAD.docuswarm.tools.update_context import (
    UpdateContextTool,
    UpdateContextParams
)
from autoBMAD.docuswarm.context.isolation import ContextManager


class TestSharedContextCrossNodeIntegration:
    """Integration test: shared_context flows across nodes (P1-1)"""
    
    @pytest.mark.asyncio
    async def test_shared_context_persists_across_nodes(self):
        """shared_context updated in node 1 should be visible in node 2"""
        # Arrange
        pipeline_id = "pipeline-test-001"
        state_manager = StateManager(db_path=":memory:")
        
        # Simulate Node 1: Analyst updates shared_context
        update_tool = UpdateContextTool(
            state_manager=state_manager,
            pipeline_id=pipeline_id
        )
        
        result = await update_tool(UpdateContextParams(
            key="facts.market_scope",
            value="global",
            operation="set"
        ))
        assert result.success
        
        # Verify persistence
        pipeline = state_manager.get_pipeline(pipeline_id)
        assert pipeline["state"]["shared_context"]["facts"]["market_scope"] == "global"
        
        # Simulate Node 2: PM loads shared_context
        pm_context = create_execution_context(
            pipeline_id=pipeline_id,
            node_id="pm",
            shared_context=pipeline["state"]["shared_context"]  # Load from state
        )
        
        pm_input = ContextManager().build_independent_input(pm_context)
        
        # Assert
        assert pm_input["shared_context"]["facts"]["market_scope"] == "global"


# =============================================================================
# Template 9: Phase 5 - 回归测试
# =============================================================================

"""
File: tests/regression/test_context_refactor.py
Phase: 5 (回归测试)
"""

import pytest


class TestContextRefactorRegression:
    """Regression tests for context refactor"""
    
    def test_no_extract_task_from_state_guessing(self):
        """Should not use _extract_task_from_state heuristic"""
        # Read executor.py content
        executor_py = read_file("autoBMAD/docuswarm/node_execution/executor.py")
        
        # The old guessing function should be removed or deprecated
        assert "_extract_task_from_state" not in executor_py
    
    def test_no_dual_agent_wrapping(self):
        """DualAgentNode should not wrap context in {subject, task}"""
        dual_agent_py = read_file("autoBMAD/docuswarm/nodes/dual_agent.py")
        
        # Old wrapping pattern should be removed
        assert 'subject_context={"subject":' not in dual_agent_py
    
    def test_no_independent_agent_parsing(self):
        """IndependentAgent should not parse nested context"""
        independent_py = read_file("autoBMAD/docuswarm/agents/independent.py")
        
        # Should not have json parsing for context structure
        # (only for actual JSON deserialization)
        assert "json_module.loads" not in independent_py


def read_file(path: str) -> str:
    """Helper to read file content for static analysis"""
    from pathlib import Path
    return Path(path).read_text(encoding='utf-8')


# =============================================================================
# 辅助函数模板
# =============================================================================

def create_execution_context(**overrides) -> "NodeExecutionContext":
    """Helper to create execution context with defaults"""
    from autoBMAD.docuswarm.node_execution.contracts import NodeExecutionContext
    
    defaults = {
        "pipeline_id": "test-pipeline",
        "node_id": "test-node",
        "node_name": "Test Node",
        "node_order": 1,
        "task_name": "Test Task",
        "task_description": "Test description",
        "role_supplement": "",
        "deliverable_type": "test",
        "deliverable_requirements": {},
        "original_context": {"content": "Test context"},
        "chained_deliverables": [],
        "shared_context": {},
        "iteration_feedback": None,
        "docs_context": []
    }
    defaults.update(overrides)
    
    return NodeExecutionContext(**defaults)


def create_mock_session_manager():
    """Helper to create mock session manager"""
    from unittest.mock import Mock
    return Mock()


def create_test_config():
    """Helper to create test config"""
    from unittest.mock import Mock
    return Mock()


def mock_evaluator_response():
    """Helper to create mock evaluator response"""
    from unittest.mock import Mock
    message = Mock()
    message.role = "assistant"
    message.content = '''{
        "criterion_scores": {"clarity": 0.8},
        "alignment_score": 0.8,
        "verdict": "APPROVED",
        "issues_found": [],
        "suggestions": []
    }'''
    return [message]


# =============================================================================
# pytest fixtures 模板
# =============================================================================

import pytest


@pytest.fixture
def temp_db():
    """Create temporary in-memory database"""
    from autoBMAD.docuswarm.storage.state_manager import StateManager
    return StateManager(db_path=":memory:")


@pytest.fixture
def mock_state_manager():
    """Create mock StateManager"""
    from unittest.mock import Mock
    return Mock(spec="StateManager")


@pytest.fixture
def sample_execution_context():
    """Create sample execution context"""
    return create_execution_context()


@pytest.fixture
def sample_deliverable(tmp_path):
    """Create sample deliverable with file"""
    file_path = tmp_path / "deliverable.md"
    file_path.write_text("# Sample Deliverable\n\nContent here.")
    
    return {
        "title": "Sample",
        "summary": "Brief summary",
        "file_path": str(file_path),
        "sha256": "abc123",
        "word_count": 10,
        "section_index": ["Sample"]
    }
