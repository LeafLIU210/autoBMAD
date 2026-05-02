# DocuSwarm Context Refactor 测试驱动主方案

> 基于研究: `docs/research/2026-03-17-docuswarm-context-refactor-deep-research-report.md`  
> 日期: 2026-03-17  
> 目标: 通过测试驱动开发完成 Context Refactor 剩余工作

## 执行摘要

本方案采用**测试驱动开发 (TDD)** 方法，按研究报告建议的顺序分阶段实施：

1. **Phase 1: P1-1** - update_context 持久化真闭环 (优先级: 🔴 最高)
2. **Phase 2: P0-3** - 单一交付物真相收口 (优先级: 🔴 最高)
3. **Phase 3: P0-2** - Evaluator 上下文补完 (优先级: 🟡 中)
4. **Phase 4: P0-1/P1-2** - 状态层收敛与清理 (优先级: 🟢 低)
5. **Phase 5: TEST** - 测试补全与回归 (优先级: 🔴 最高)

---

## 核心原则

### TDD 循环
```
Red: 编写失败的测试 -> Green: 最小实现通过测试 -> Refactor: 重构代码
```

### 测试分层
- **单元测试**: 单个函数/类，隔离依赖 ( mocks )
- **集成测试**: 跨组件协作，使用内存存储
- **端到端测试**: 完整流程，使用真实文件系统

### 完成标准
每个 Phase 必须满足:
- [ ] 所有测试通过
- [ ] 代码覆盖率 > 80%
- [ ] 类型检查通过 (pyright)
- [ ] 静态检查通过 (ruff)

---

## Phase 1: P1-1 - update_context 持久化真闭环

**目标**: 让 `update_context` 工具真正可用，实现跨节点共享上下文

### 1.1 测试设计: UpdateContextTool 绑定机制

#### Test 1.1.1: Tool 实例化需要 StateManager (Red)
```python
# tests/unit/tools/test_update_context_binding.py

import pytest
from autoBMAD.docuswarm.tools.update_context import UpdateContextTool


class TestUpdateContextToolBinding:
    """Test UpdateContextTool dependency injection"""
    
    def test_tool_requires_state_manager(self):
        """Tool should require StateManager at initialization"""
        # Act & Assert
        with pytest.raises(ValueError, match="StateManager is required"):
            UpdateContextTool()  # No state_manager provided
    
    def test_tool_requires_pipeline_id(self):
        """Tool should require pipeline_id at initialization"""
        # Arrange
        mock_state_manager = Mock(spec=StateManager)
        
        # Act & Assert
        with pytest.raises(ValueError, match="pipeline_id is required"):
            UpdateContextTool(state_manager=mock_state_manager)  # No pipeline_id
    
    def test_tool_accepts_valid_dependencies(self):
        """Tool should accept valid dependencies"""
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
```

#### Implementation 1.1.1 (Green)
```python
# autoBMAD/docuswarm/tools/update_context.py

class UpdateContextTool(CallableTool2[UpdateContextParams]):
    """Tool for updating the shared context with key-value operations."""
    
    name: str = "update_context"
    description: str = "Update the shared context with key-value operations"
    params: type[UpdateContextParams] = UpdateContextParams
    
    def __init__(
        self,
        state_manager: StateManager | None = None,
        pipeline_id: str | None = None,
    ) -> None:
        """Initialize the tool.
        
        Args:
            state_manager: StateManager for persistence. Required.
            pipeline_id: Pipeline ID to update. Required.
            
        Raises:
            ValueError: If required dependencies are not provided.
        """
        super().__init__()
        
        # P1-1: Make dependencies required
        if state_manager is None:
            raise ValueError("StateManager is required")
        if pipeline_id is None:
            raise ValueError("pipeline_id is required")
            
        self._state_manager = state_manager
        self._pipeline_id = pipeline_id
```

#### Test 1.1.2: Tool 绑定到 Agent 配置
```python
# tests/unit/agents/test_tool_binding.py

class TestAgentToolBinding:
    """Test that agents bind tools with correct dependencies"""
    
    @pytest.mark.asyncio
    async def test_independent_agent_binds_update_context_tool(self):
        """IndependentAgent should bind UpdateContextTool with StateManager"""
        # Arrange
        mock_state_manager = Mock(spec=StateManager)
        session_manager = create_mock_session_manager()
        config = create_test_config()
        
        agent = IndependentAgent(
            config=config,
            session_manager=session_manager,
            node_id="test-node",
            state_manager=mock_state_manager,  # P1-1: Accept state_manager
            pipeline_id="pipeline-test-001"
        )
        
        # Act
        tools = agent.get_tools()
        update_context_tool = next(
            (t for t in tools if t.name == "update_context"), 
            None
        )
        
        # Assert
        assert update_context_tool is not None
        assert update_context_tool._state_manager is mock_state_manager
        assert update_context_tool._pipeline_id == "pipeline-test-001"
```

### 1.2 测试设计: shared_context 进入 Agent Input

#### Test 1.2.1: IndependentAgentInput 包含 shared_context
```python
# tests/unit/node_execution/test_contracts.py

class TestIndependentAgentInputSchema:
    """Test IndependentAgentInput has shared_context field"""
    
    def test_independent_agent_input_has_shared_context(self):
        """IndependentAgentInput should have shared_context field"""
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
            "shared_context": {  # P1-1: New field
                "facts": {"key": "value"},
                "decisions": []
            }
        }
        
        # Act & Assert - Should not raise
        validate_independent_agent_input(input_data)
    
    def test_shared_context_is_optional_for_backward_compat(self):
        """shared_context should be optional for backward compatibility"""
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
            # shared_context missing
        }
        
        # Act & Assert - Should not raise
        validate_independent_agent_input(input_data)
```

#### Implementation 1.2.1 (Green)
```python
# autoBMAD/docuswarm/node_execution/contracts.py

class IndependentAgentInput(TypedDict, total=False):
    """IndependentAgent 的输入 - 由 ContextManager 从 NodeExecutionContext 裁剪。"""
    
    task_name: str
    task_description: str
    role_supplement: str
    deliverable_requirements: DeliverableRequirements
    original_context_summary: str
    chained_deliverables_summary: list[dict[str, Any]]
    iteration_feedback: dict[str, Any] | None
    persona_context: dict[str, Any]
    shared_context: dict[str, Any]  # P1-1: New field
```

#### Test 1.2.2: build_independent_input 传递 shared_context
```python
# tests/unit/context/test_isolation.py

class TestContextManagerSharedContext:
    """Test ContextManager handles shared_context correctly"""
    
    def test_build_independent_input_includes_shared_context(self):
        """build_independent_input should include shared_context from execution_context"""
        # Arrange
        manager = ContextManager()
        execution_context = NodeExecutionContext(
            # ... other fields
            shared_context={
                "facts": {"market_scope": "global"},
                "decisions": [{"id": 1, "text": "Use Python"}]
            }
        )
        
        # Act
        result = manager.build_independent_input(execution_context)
        
        # Assert
        assert "shared_context" in result
        assert result["shared_context"]["facts"]["market_scope"] == "global"
    
    def test_build_independent_input_defaults_empty_shared_context(self):
        """build_independent_input should default to empty dict if no shared_context"""
        # Arrange
        manager = ContextManager()
        execution_context = NodeExecutionContext(
            # ... other fields
            shared_context={}
        )
        
        # Act
        result = manager.build_independent_input(execution_context)
        
        # Assert
        assert "shared_context" in result
        assert result["shared_context"] == {}
```

#### Implementation 1.2.2 (Green)
```python
# autoBMAD/docuswarm/context/isolation.py

def build_independent_input(
    self,
    execution_context: NodeExecutionContext,
    iteration_feedback: dict[str, Any] | None = None,
) -> IndependentAgentInput:
    """构建 IndependentAgent 的输入。"""
    # ... existing code ...
    
    return IndependentAgentInput(
        task_name=execution_context["task_name"],
        task_description=execution_context["task_description"],
        role_supplement=execution_context["role_supplement"],
        deliverable_requirements=execution_context["deliverable_requirements"],
        original_context_summary=summary,
        chained_deliverables_summary=chained_summary,
        iteration_feedback=iteration_feedback,
        persona_context={},
        shared_context=execution_context.get("shared_context", {}),  # P1-1
    )
```

### 1.3 测试设计: Prompt 渲染 shared_context

#### Test 1.3.1: Contract Builder 渲染 shared_context
```python
# tests/unit/prompts/test_contract_builder.py

class TestSharedContextSection:
    """Test shared_context rendering in prompt"""
    
    def test_build_context_section_includes_shared_context(self):
        """_build_context_section should include shared_context"""
        # Arrange
        builder = NodePromptContractBuilder()
        context = NodeExecutionContext(
            # ... other fields
            shared_context={
                "facts": {"architecture": "microservices"},
                "open_questions": ["Q1", "Q2"]
            }
        )
        
        # Act
        section = builder._build_context_section(context)
        
        # Assert
        assert "shared_context" in section.lower() or "共享上下文" in section
        assert "microservices" in section
        assert "Q1" in section
```

### 1.4 测试设计: PipelineState 恢复 shared_context

#### Test 1.4.1: PipelineState 包含 shared_context
```python
# tests/unit/pipeline/test_state.py

class TestPipelineStateSharedContext:
    """Test PipelineState has shared_context field"""
    
    def test_pipeline_state_has_shared_context(self):
        """PipelineState should have shared_context field"""
        # Arrange
        state = create_initial_state(
            pipeline_id="test-pipeline",
            subject_context={"task": "Build app"}
        )
        
        # Assert
        assert "shared_context" in state
        assert state["shared_context"] == {}
    
    def test_create_initial_state_initializes_shared_context(self):
        """create_initial_state should initialize shared_context"""
        # Act
        state = create_initial_state(
            pipeline_id="test-pipeline",
            subject_context={"task": "Build app"}
        )
        
        # Assert
        assert isinstance(state["shared_context"], dict)
```

#### Implementation 1.4.1 (Green)
```python
# autoBMAD/docuswarm/pipeline/state.py

class PipelineState(TypedDict):
    """Main pipeline state schema for LangGraph StateGraph."""
    
    # ... existing fields ...
    shared_context: dict[str, Any]  # P1-1: New field


def create_initial_state(pipeline_id: str, subject_context: dict[str, Any]) -> PipelineState:
    """Create an initial PipelineState with default values."""
    # ... existing code ...
    
    return PipelineState(
        # ... existing fields ...
        shared_context={},  # P1-1: Initialize shared_context
    )
```

### 1.5 Phase 1 验收测试

```python
# tests/integration/test_shared_context_cross_node.py

class TestSharedContextCrossNode:
    """Integration test: shared_context flows across nodes"""
    
    @pytest.mark.asyncio
    async def test_shared_context_persists_across_nodes(self):
        """shared_context updated in node 1 should be visible in node 2"""
        # Arrange
        pipeline_id = "pipeline-test-001"
        state_manager = StateManager(db_path=":memory:")
        
        # Node 1: Analyst updates shared_context
        analyst_context = create_execution_context(
            pipeline_id=pipeline_id,
            node_id="analyst",
            shared_context={}
        )
        
        # Simulate agent calling update_context tool
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
        
        # Node 2: PM should see the updated shared_context
        pm_context = create_execution_context(
            pipeline_id=pipeline_id,
            node_id="pm",
            # P1-1: shared_context should be loaded from StateManager
        )
        
        pm_input = ContextManager().build_independent_input(pm_context)
        
        # Assert
        assert pm_input["shared_context"]["facts"]["market_scope"] == "global"
```

---

## Phase 2: P0-3 - 单一交付物真相收口

**目标**: 消除摘要/正文双轨，确保 Evaluator 始终评审正式文档

### 2.1 测试设计: file_path/sha256 强制验证

#### Test 2.1.1: 验证强制字段
```python
# tests/unit/llm/test_response_validation.py

class TestDeliverableValidationSingleTruth:
    """Test deliverable validation enforces single truth"""
    
    def test_validates_file_path_required(self):
        """deliverable.file_path should be required"""
        # Arrange
        data = {
            "deliverable": {
                "title": "Test",
                "content": "Summary",  # P0-3: This is just summary now
                # file_path missing!
                "sha256": "abc123..."
            },
            "questions": []
        }
        
        # Act & Assert
        with pytest.raises(ValidationError, match="file_path is required"):
            validate_independent_output(data)
    
    def test_validates_sha256_required(self):
        """deliverable.sha256 should be required"""
        # Arrange
        data = {
            "deliverable": {
                "title": "Test",
                "content": "Summary",
                "file_path": "/path/to/file.md",
                # sha256 missing!
            },
            "questions": []
        }
        
        # Act & Assert
        with pytest.raises(ValidationError, match="sha256 is required"):
            validate_independent_output(data)
    
    def test_accepts_valid_metadata_only_deliverable(self):
        """Should accept deliverable with metadata only (no full content)"""
        # Arrange
        data = {
            "deliverable": {
                "title": "Test Deliverable",
                "summary": "Brief summary",  # P0-3: Use summary, not content
                "file_path": "output/pipeline-001/test.md",
                "sha256": "a3f5c8e9d2b1...",
                "word_count": 1500,
                "section_index": ["Overview", "Details"]
            },
            "questions": []
        }
        
        # Act & Assert - Should not raise
        validate_independent_output(data)
```

#### Implementation 2.1.1 (Green)
```python
# autoBMAD/docuswarm/llm/response.py

def validate_independent_output(data: dict[str, Any]) -> None:
    """Validate Independent Agent output against schema."""
    
    deliverable: dict[str, Any] = data["deliverable"]
    
    # ... existing title validation ...
    
    # P0-3: file_path is now required
    if "file_path" not in deliverable:
        raise ValidationError("deliverable.file_path: required field missing")
    if not isinstance(deliverable["file_path"], str):
        raise ValidationError("deliverable.file_path: must be a string")
    
    # P0-3: sha256 is now required
    if "sha256" not in deliverable:
        raise ValidationError("deliverable.sha256: required field missing")
    if not isinstance(deliverable["sha256"], str):
        raise ValidationError("deliverable.sha256: must be a string")
    
    # P0-3: Prefer summary over content
    if "summary" not in deliverable and "content" not in deliverable:
        raise ValidationError("deliverable.summary: required field missing")
```

### 2.2 测试设计: DeliverableArtifact 与运行时一致

#### Test 2.2.1: 统一字段命名
```python
# tests/unit/node_execution/test_contracts.py

class TestDeliverableArtifactSchema:
    """Test DeliverableArtifact schema consistency"""
    
    def test_deliverable_artifact_uses_summary_not_content(self):
        """DeliverableArtifact should use 'summary' field"""
        # Arrange
        artifact: DeliverableArtifact = {
            "title": "Test",
            "summary": "Brief summary",  # Not 'content'
            "file_path": "/path/to/file.md",
            "sha256": "abc123",
            "word_count": 100,
            "section_index": ["Section 1"],
            "content_type": "markdown"
        }
        
        # Act & Assert - Should not raise
        # Type checker should catch 'content' usage
        assert "summary" in artifact
        assert "content" not in artifact
```

### 2.3 测试设计: Evaluator 禁止 fallback 到摘要

#### Test 2.3.1: build_evaluator_input 强制读取文件
```python
# tests/unit/context/test_isolation.py

class TestEvaluatorInputSingleTruth:
    """Test Evaluator input enforces single truth"""
    
    def test_build_evaluator_input_reads_file_content(self, tmp_path):
        """build_evaluator_input should read full content from file"""
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
    
    def test_build_evaluator_input_raises_if_file_missing(self):
        """build_evaluator_input should raise if file_path doesn't exist"""
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
    
    def test_build_evaluator_input_raises_if_file_path_missing(self):
        """build_evaluator_input should raise if file_path is None"""
        # Arrange
        manager = ContextManager()
        execution_context = create_execution_context()
        deliverable = {
            "title": "Test",
            "summary": "Only summary",
            # file_path missing!
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="file_path is required for evaluation"):
            manager.build_evaluator_input(execution_context, deliverable)
```

#### Implementation 2.3.1 (Green)
```python
# autoBMAD/docuswarm/context/isolation.py

def build_evaluator_input(
    self,
    execution_context: NodeExecutionContext,
    deliverable: dict[str, Any] | None,
) -> EvaluatorAgentInput:
    """构建 EvaluatorAgent 的输入。"""
    
    if not deliverable:
        raise ValueError("deliverable is required for evaluation")
    
    # P0-3: file_path is required, no fallback to content
    file_path = deliverable.get("file_path")
    if not file_path:
        raise ValueError("file_path is required for evaluation")
    
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Deliverable file not found: {file_path}")
    
    # P0-3: Always read full content from file
    deliverable_body = path.read_text(encoding="utf-8")
    
    return EvaluatorAgentInput(
        task_name=execution_context["task_name"],
        task_description=execution_context["task_description"],
        deliverable_artifact=deliverable,
        deliverable_body=deliverable_body,
        criteria=execution_context.get("evaluator_criteria", []),
    )
```

### 2.4 测试设计: 下游传播限制为 metadata + summary

#### Test 2.4.1: 链式上下文只传播摘要
```python
# tests/unit/pipeline/test_state_accumulation.py

class TestChainedContextPropagation:
    """Test that chained context only propagates metadata + summary"""
    
    def test_accumulate_context_excludes_full_content(self):
        """accumulate_context should exclude full deliverable content"""
        # Arrange
        subject_context = {"task": "Build app"}
        deliverables = {
            "analyst": {
                "title": "Analysis",
                "summary": "Brief analysis summary",
                "file_path": "output/analysis.md",
                "sha256": "abc123",
                # Note: full content is in the file, not here
            }
        }
        
        # Act
        result = accumulate_context(subject_context, deliverables, "pm")
        
        # Assert
        assert "analyst_deliverable" in result
        analyst_output = result["analyst_deliverable"]
        assert "summary" in analyst_output
        assert "file_path" in analyst_output
        assert analyst_output["summary"] == "Brief analysis summary"
```

---

## Phase 3: P0-2 - Evaluator 上下文补完

**目标**: Evaluator prompt 包含原始上下文摘要

### 3.1 测试设计: EvaluatorAgentInput 包含原始上下文

#### Test 3.1.1: 输入结构包含 original_context
```python
# tests/unit/node_execution/test_contracts.py

class TestEvaluatorAgentInputSchema:
    """Test EvaluatorAgentInput has original context"""
    
    def test_evaluator_agent_input_has_original_context(self):
        """EvaluatorAgentInput should have original_context field"""
        # Arrange
        input_data: EvaluatorAgentInput = {
            "task_name": "test-task",
            "task_description": "test description",
            "original_context_summary": "Original user request: Build a task app",  # P0-2
            "deliverable_artifact": {...},
            "deliverable_body": "# Full content...",
            "criteria": []
        }
        
        # Act & Assert
        validate_evaluator_agent_input(input_data)
```

#### Implementation 3.1.1 (Green)
```python
# autoBMAD/docuswarm/node_execution/contracts.py

class EvaluatorAgentInput(TypedDict):
    """EvaluatorAgent 的输入 - 由 ContextManager 从 NodeExecutionContext 裁剪。"""
    
    task_name: str
    task_description: str
    original_context_summary: str  # P0-2: New field
    deliverable_artifact: dict[str, Any]
    deliverable_body: str
    criteria: list[dict[str, Any]]
```

### 3.2 测试设计: build_evaluator_input 传递原始上下文

#### Test 3.2.1: 提取并传递原始上下文
```python
# tests/unit/context/test_isolation.py

class TestEvaluatorOriginalContext:
    """Test Evaluator gets original context"""
    
    def test_build_evaluator_input_includes_original_context(self):
        """build_evaluator_input should include original context summary"""
        # Arrange
        manager = ContextManager()
        execution_context = NodeExecutionContext(
            # ...
            original_context={
                "content": "User wants a collaborative task management app"
            }
        )
        
        # Act
        result = manager.build_evaluator_input(
            execution_context, 
            deliverable={"file_path": "/tmp/test.md", "sha256": "abc"}
        )
        
        # Assert
        assert "original_context_summary" in result
        assert "collaborative task management" in result["original_context_summary"]
```

### 3.3 测试设计: Prompt 渲染原始上下文

#### Test 3.3.1: Contract Builder 渲染原始上下文章节
```python
# tests/unit/prompts/test_contract_builder.py

class TestEvaluatorOriginalContextSection:
    """Test Evaluator prompt includes original context section"""
    
    def test_evaluator_prompt_has_original_context_section(self):
        """render_evaluator_prompt should include '原始需求摘要' section"""
        # Arrange
        builder = NodePromptContractBuilder()
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
        assert "task app" in prompt
```

---

## Phase 4: P0-1/P1-2 - 状态层收敛与清理

### 4.1 测试设计: PipelineState 收敛到 execution_context

```python
# tests/unit/pipeline/test_state_convergence.py

class TestPipelineStateConvergence:
    """Test PipelineState converges to execution_context protocol"""
    
    def test_pipeline_state_has_execution_context_field(self):
        """PipelineState should have execution_context field"""
        # P0-1 (optional): Add execution_context field
        state = create_initial_state("test", {})
        assert "execution_context" in state
```

### 4.2 测试设计: Docs-free 边界验证

```python
# tests/unit/test_docs_free_boundary.py

class TestDocsFreeBoundary:
    """Test that workflow never reads from docs/"""
    
    def test_context_builder_docs_context_empty(self):
        """Context builder should always set docs_context to empty"""
        builder = NodeExecutionContextBuilder()
        context = builder.build(...)
        assert context["docs_context"] == []
    
    def test_no_docs_path_in_cli(self):
        """CLI should not reference docs/ paths in examples"""
        # Static analysis test
        main_py = read_file("autoBMAD/docuswarm/main.py")
        assert "docs/epics/" not in main_py
        assert "docs/proposal.md" not in main_py
```

---

## Phase 5: TEST - 测试补全与回归

### 5.1 必须创建的测试文件清单

```
tests/
├── unit/
│   ├── node_execution/
│   │   ├── test_contracts.py           # NodeExecutionContext, IndependentAgentInput, EvaluatorAgentInput
│   │   ├── test_context_builder.py     # NodeExecutionContextBuilder
│   │   └── test_executor.py            # Single context protocol
│   ├── prompts/
│   │   └── test_contract_builder.py    # NodePromptContractBuilder
│   ├── tools/
│   │   └── test_update_context.py      # UpdateContextTool binding & persistence
│   ├── context/
│   │   └── test_isolation.py           # ContextManager with shared_context
│   ├── pipeline/
│   │   └── test_state_shared_context.py # PipelineState shared_context
│   └── llm/
│       └── test_response_validation.py  # Single truth validation
├── integration/
│   ├── test_shared_context_cross_node.py    # Cross-node shared_context flow
│   ├── test_single_truth_deliverable.py     # File-based deliverable truth
│   └── test_evaluator_original_context.py   # Evaluator original context
└── e2e/
    └── test_docs_free_workflow.py      # End-to-end docs-free verification
```

### 5.2 测试覆盖率要求

| 模块 | 目标覆盖率 | 关键路径 |
|------|-----------|----------|
| `node_execution/contracts.py` | 100% | 所有 TypedDict |
| `node_execution/context_builder.py` | 90% | build(), from_node_config() |
| `tools/update_context.py` | 90% | __call__(), all operations |
| `context/isolation.py` | 85% | build_*_input() methods |
| `prompts/contract_builder.py` | 85% | All build_*_contract() methods |
| `llm/response.py` | 90% | validate_*_output() |

### 5.3 回归测试套件

```python
# tests/regression/test_context_refactor.py

class TestContextRefactorRegression:
    """Regression tests for context refactor"""
    
    def test_no_extract_task_from_state_guessing(self):
        """Should not use _extract_task_from_state heuristic"""
        # Verify old guessing code is removed
        executor_py = read_file("autoBMAD/docuswarm/node_execution/executor.py")
        assert "_extract_task_from_state" not in executor_py
    
    def test_no_dual_agent_wrapping(self):
        """DualAgentNode should not wrap context in {subject, task}"""
        dual_agent_py = read_file("autoBMAD/docuswarm/nodes/dual_agent.py")
        assert 'subject_context={"subject":' not in dual_agent_py
    
    def test_no_independent_agent_parsing(self):
        """IndependentAgent should not parse nested context"""
        independent_py = read_file("autoBMAD/docuswarm/agents/independent.py")
        assert "json_module.loads" not in independent_py  # For context parsing
```

---

## 执行计划

### Week 1: Phase 1 - P1-1 真闭环
- Day 1-2: Test 1.1.x + Implementation (Tool binding)
- Day 3-4: Test 1.2.x + Implementation (shared_context in Input)
- Day 5: Test 1.3.x + Implementation (Prompt rendering)
- Day 6-7: Test 1.4.x + Implementation (State recovery)

### Week 2: Phase 2 - P0-3 单一真相
- Day 1-2: Test 2.1.x + Implementation (强制验证)
- Day 3: Test 2.2.x + Implementation (字段统一)
- Day 4-5: Test 2.3.x + Implementation (禁止 fallback)
- Day 6-7: Test 2.4.x + Implementation (传播限制)

### Week 3: Phase 3 & 4
- Day 1-2: P0-2 Evaluator 上下文补完
- Day 3-4: P0-1/P1-2 清理
- Day 5-7: Phase 5 测试补全

### Week 4: 集成与回归
- Day 1-3: 集成测试
- Day 4-5: 回归测试
- Day 6-7: 文档更新与 Code Review

---

## 附录: 快速开始模板

### 创建新测试文件模板

```python
# tests/unit/<module>/test_<feature>.py

"""
Test <Feature> - TDD Phase X

Context: <Link to research finding>
Goal: <What this test verifies>
"""

import pytest
from unittest.mock import Mock, AsyncMock


class Test<Feature>:
    """Test <feature description>"""
    
    def setup_method(self):
        """Set up test fixtures"""
        pass
    
    # === Red: Write failing test ===
    def test_<condition>_<expected_result>(self):
        """<Test description>"""
        # Arrange
        
        # Act
        
        # Assert
        pass
    
    # === Green: Make it pass ===
    # (Implementation goes in source file)
    
    # === Refactor: Improve design ===
    # (Both test and production code)
```

### TDD 工作流 Checklist

- [ ] 理解研究报告中对应的问题
- [ ] 编写失败的测试 (Red)
- [ ] 运行测试确认失败
- [ ] 编写最小实现 (Green)
- [ ] 运行测试确认通过
- [ ] 重构代码 (Refactor)
- [ ] 确保类型检查通过
- [ ] 确保静态检查通过
- [ ] 提交代码
