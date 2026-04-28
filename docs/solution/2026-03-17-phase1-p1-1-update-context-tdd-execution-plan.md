# Phase 1: P1-1 - update_context 持久化真闭环 - TDD 执行计划

> 基于: `docs/solution/2026-03-17-docuswarm-context-refactor-tdd-master-plan.md`  
> 优先级: 🔴 最高  
> 目标: 让 `update_context` 工具真正可用，实现跨节点共享上下文

## 研究问题回顾

来自研究报告:
- **P1-1-001**: update_context 仍未形成可用的运行时闭环
- **P1-1-002**: shared_context 未进入 IndependentAgentInput  
- **P1-1-003**: 恢复链路不会回填 shared_context
- **P1-1-004**: StateManager.update_shared_context 已实现 (✅ 已完成)

## 实施步骤

### Step 1: UpdateContextTool 强制依赖注入

#### TDD Cycle 1.1

**Red - 编写失败测试:**
```python
# tests/unit/tools/test_update_context_binding.py
# Test: tool_requires_state_manager

import pytest
from autoBMAD.docuswarm.tools.update_context import UpdateContextTool


def test_tool_requires_state_manager():
    """UpdateContextTool should require StateManager at initialization"""
    with pytest.raises(ValueError, match="StateManager is required"):
        UpdateContextTool()  # No state_manager
```

运行测试:
```bash
pytest tests/unit/tools/test_update_context_binding.py::test_tool_requires_state_manager -v
# Expected: FAIL (AttributeError or no error currently)
```

**Green - 最小实现:**
```python
# autoBMAD/docuswarm/tools/update_context.py

class UpdateContextTool(CallableTool2[UpdateContextParams]):
    
    def __init__(
        self,
        state_manager: StateManager | None = None,
        pipeline_id: str | None = None,
    ) -> None:
        super().__init__()
        
        # P1-1: Make dependencies required
        if state_manager is None:
            raise ValueError("StateManager is required")
        if pipeline_id is None:
            raise ValueError("pipeline_id is required")
            
        self._state_manager = state_manager
        self._pipeline_id = pipeline_id
```

运行测试:
```bash
pytest tests/unit/tools/test_update_context_binding.py::test_tool_requires_state_manager -v
# Expected: PASS
```

**Refactor:**
- 考虑自定义异常类型
- 添加文档字符串说明依赖要求

---

#### TDD Cycle 1.2

**Red - 编写失败测试:**
```python
# Test: tool_accepts_valid_dependencies

def test_tool_accepts_valid_dependencies():
    """UpdateContextTool should accept valid dependencies"""
    mock_state_manager = Mock(spec=StateManager)
    
    tool = UpdateContextTool(
        state_manager=mock_state_manager,
        pipeline_id="pipeline-test-001"
    )
    
    assert tool._state_manager is mock_state_manager
    assert tool._pipeline_id == "pipeline-test-001"
```

运行测试:
```bash
pytest tests/unit/tools/test_update_context_binding.py::test_tool_accepts_valid_dependencies -v
# Expected: PASS (if implementation above is done)
```

---

#### TDD Cycle 1.3

**Red - 编写失败测试:**
```python
# Test: tool_call_uses_state_manager

@pytest.mark.asyncio
async def test_tool_call_uses_state_manager():
    """Tool call should delegate to StateManager.update_shared_context"""
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
    
    result = await tool(params)
    
    assert result.success is True
    mock_state_manager.update_shared_context.assert_called_once_with(
        pipeline_id="pipeline-test-001",
        update="global",
        operation="set",
        key_path="facts.market_scope"
    )
```

**Green - 确保实现:**
```python
# Verify the __call__ method uses self._state_manager

@override
async def __call__(self, params: UpdateContextParams) -> ToolReturnValue:
    """Update context with the given parameters."""
    # Validate key against whitelist
    if not self._is_key_allowed(params.key):
        return ToolError(...)
    
    try:
        # Use StateManager for persistence
        result = await self._state_manager.update_shared_context(
            pipeline_id=self._pipeline_id,
            update=params.value,
            operation=params.operation,
            key_path=params.key,
        )
        
        if result:
            return ToolOk(output=f"Context updated: {params.operation} on '{params.key}'")
        else:
            return ToolError(...)
    except Exception as e:
        return ToolError(...)
```

---

### Step 2: IndependentAgentInput 添加 shared_context 字段

#### TDD Cycle 2.1

**Red - 编写失败测试:**
```python
# tests/unit/node_execution/test_contracts.py

def test_independent_agent_input_has_shared_context():
    """IndependentAgentInput should have shared_context field"""
    input_data = {
        "task_name": "test-task",
        "task_description": "test description",
        "role_supplement": "",
        "deliverable_requirements": {},
        "original_context_summary": "test context",
        "chained_deliverables_summary": [],
        "iteration_feedback": None,
        "persona_context": {},
        "shared_context": {
            "facts": {"key": "value"},
            "decisions": []
        }
    }
    
    # Should not raise
    validate_independent_agent_input(input_data)
```

**Green - 实现:**
```python
# autoBMAD/docuswarm/node_execution/contracts.py

class IndependentAgentInput(TypedDict, total=False):
    """IndependentAgent 的输入"""
    
    task_name: str
    task_description: str
    role_supplement: str
    deliverable_requirements: DeliverableRequirements
    original_context_summary: str
    chained_deliverables_summary: list[dict[str, Any]]
    iteration_feedback: dict[str, Any] | None
    persona_context: dict[str, Any]
    shared_context: dict[str, Any]  # P1-1: NEW FIELD
```

---

### Step 3: ContextManager.build_independent_input 传递 shared_context

#### TDD Cycle 3.1

**Red - 编写失败测试:**
```python
# tests/unit/context/test_isolation.py

def test_build_independent_input_includes_shared_context():
    """build_independent_input should include shared_context from execution_context"""
    manager = ContextManager()
    execution_context = create_execution_context(
        shared_context={
            "facts": {"market_scope": "global"},
            "open_questions": ["Q1", "Q2"]
        }
    )
    
    result = manager.build_independent_input(execution_context)
    
    assert "shared_context" in result
    assert result["shared_context"]["facts"]["market_scope"] == "global"
```

**Green - 实现:**
```python
# autoBMAD/docuswarm/context/isolation.py

def build_independent_input(
    self,
    execution_context: NodeExecutionContext,
    iteration_feedback: dict[str, Any] | None = None,
) -> IndependentAgentInput:
    """构建 IndependentAgent 的输入。"""
    summary = _extract_original_context_summary(
        execution_context["original_context"]
    )
    
    chained_summary = []
    for item in execution_context["chained_deliverables"]:
        deliverable = item.get("deliverable", {})
        chained_summary.append({
            "node_id": item.get("node_id"),
            "title": deliverable.get("title", "Untitled"),
            "summary": deliverable.get("summary", "")[:200],  # P1-1: Use summary
        })
    
    return IndependentAgentInput(
        task_name=execution_context["task_name"],
        task_description=execution_context["task_description"],
        role_supplement=execution_context["role_supplement"],
        deliverable_requirements=execution_context["deliverable_requirements"],
        original_context_summary=summary,
        chained_deliverables_summary=chained_summary,
        iteration_feedback=iteration_feedback,
        persona_context={},
        shared_context=execution_context.get("shared_context", {}),  # P1-1: NEW
    )
```

---

### Step 4: NodePromptContractBuilder 渲染 shared_context

#### TDD Cycle 4.1

**Red - 编写失败测试:**
```python
# tests/unit/prompts/test_contract_builder.py

def test_build_context_section_includes_shared_context():
    """_build_context_section should include shared_context section"""
    builder = NodePromptContractBuilder()
    context = create_execution_context(
        shared_context={
            "facts": {"architecture": "microservices"},
            "open_questions": ["How to scale?"]
        }
    )
    
    section = builder._build_context_section(context)
    
    assert "共享上下文" in section or "shared_context" in section
    assert "microservices" in section
    assert "How to scale?" in section
```

**Green - 实现:**
```python
# autoBMAD/docuswarm/prompts/contract_builder.py

def _build_context_section(self, context: NodeExecutionContext) -> str:
    """构建上下文章节。"""
    sections = []
    
    # 原始上下文
    original_context = context.get("original_context", {})
    if original_context:
        content = original_context.get("content", "")
        if content:
            sections.append(f"## 原始上下文\n{content}")
    
    # P1-1: 共享上下文
    shared = context.get("shared_context", {})
    if shared:
        sections.append("\n## 共享上下文 (Shared Context)")
        
        if "facts" in shared:
            sections.append("\n**已确认事实**:")
            for key, value in shared["facts"].items():
                sections.append(f"- {key}: {value}")
        
        if "decisions" in shared:
            sections.append("\n**已做决策**:")
            for decision in shared["decisions"]:
                sections.append(f"- {decision}")
        
        if "open_questions" in shared:
            sections.append("\n**待解答问题**:")
            for question in shared["open_questions"]:
                sections.append(f"- {question}")
    
    # 上游交付物
    chained = context.get("chained_deliverables", [])
    if chained:
        sections.append("\n## 上游交付物摘要")
        for item in chained:
            node_id = item.get("node_id", "unknown")
            title = item.get("title", "未命名")
            sections.append(f"- **{node_id}**: {title}")
    
    return "\n".join(sections)
```

---

### Step 5: PipelineState 添加 shared_context 字段

#### TDD Cycle 5.1

**Red - 编写失败测试:**
```python
# tests/unit/pipeline/test_state.py

def test_pipeline_state_has_shared_context():
    """PipelineState should have shared_context field"""
    state = create_initial_state(
        pipeline_id="test-pipeline",
        subject_context={"task": "Build app"}
    )
    
    assert "shared_context" in state
    assert state["shared_context"] == {}


def test_create_initial_state_initializes_shared_context():
    """create_initial_state should initialize shared_context"""
    state = create_initial_state("test", {})
    assert isinstance(state["shared_context"], dict)
```

**Green - 实现:**
```python
# autoBMAD/docuswarm/pipeline/state.py

class PipelineState(TypedDict):
    """Main pipeline state schema for LangGraph StateGraph."""
    
    pipeline_id: str
    subject_context: dict[str, Any]
    current_node: str | None
    completed_nodes: list[str]
    deliverables: dict[str, dict[str, Any]]
    questions: dict[str, list[dict[str, Any]]]
    evaluations: dict[str, dict[str, Any]]
    node_iterations: dict[str, int]
    session_ids: dict[str, str]
    session_metadata: dict[str, dict[str, Any]]
    current_node_session_id: str | None
    status: str
    error: dict[str, Any] | None
    shared_context: dict[str, Any]  # P1-1: NEW FIELD


def create_initial_state(
    pipeline_id: str, 
    subject_context: dict[str, Any]
) -> PipelineState:
    """Create an initial PipelineState with default values."""
    from autoBMAD.docuswarm.utils.session_ids import generate_session_id
    
    pipeline_session_id = generate_session_id(pipeline_id)
    
    return PipelineState(
        pipeline_id=pipeline_id,
        subject_context=subject_context,
        current_node=None,
        completed_nodes=[],
        deliverables={},
        questions={},
        evaluations={},
        node_iterations={},
        session_ids={"pipeline": pipeline_session_id},
        session_metadata={},
        current_node_session_id=None,
        status=PENDING,
        error=None,
        shared_context={},  # P1-1: NEW - Initialize shared_context
    )
```

---

### Step 6: 集成测试 - 跨节点共享上下文

#### TDD Cycle 6.1

**Red - 编写失败测试:**
```python
# tests/integration/test_shared_context_cross_node.py

@pytest.mark.asyncio
async def test_shared_context_persists_across_nodes():
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
    # (This requires executor to load shared_context from state)
```

**Green - 实现 executor 加载:**
```python
# autoBMAD/docuswarm/node_execution/executor.py

async def _execute_node(...) -> NodeRunState:
    # ... existing code ...
    
    # P1-1: Load shared_context from state
    shared_context = state.get("shared_context", {})
    
    execution_context = context_builder.build(
        pipeline_id=pipeline_id,
        node_id=node_id,
        original_context=original_context,
        chained_deliverables=_extract_chained_deliverables(state),
        shared_context=shared_context,  # P1-1: Pass shared_context
    )
    
    # ... rest of execution ...
```

---

## 验收清单

- [ ] `UpdateContextTool` 初始化时必须提供 `StateManager` 和 `pipeline_id`
- [ ] `UpdateContextTool` 调用时实际写入 `StateManager.update_shared_context()`
- [ ] `IndependentAgentInput` 包含 `shared_context` 字段
- [ ] `ContextManager.build_independent_input()` 传递 `shared_context`
- [ ] `NodePromptContractBuilder._build_context_section()` 渲染 `shared_context`
- [ ] `PipelineState` 声明 `shared_context` 字段
- [ ] `create_initial_state()` 初始化 `shared_context`
- [ ] `executor` 从 state 加载 `shared_context` 并传递给 context builder
- [ ] 集成测试验证跨节点 `shared_context` 持久化
- [ ] 所有测试通过率 100%
- [ ] 代码覆盖率 > 80%

## 潜在风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 向后兼容性破坏 | 高 | `shared_context` 使用 `total=False` TypedDict |
| Agent 配置未更新 | 中 | 同步更新 `independent_agent.yaml` 工具绑定 |
| State 序列化问题 | 中 | 确保 `shared_context` 可 JSON 序列化 |
| 性能下降 | 低 | `shared_context` 按需加载，不重复存储 |

## 参考文档

- 研究报告: `docs/research/2026-03-17-docuswarm-context-refactor-deep-research-report.md`
- 主 TDD 方案: `docs/solution/2026-03-17-docuswarm-context-refactor-tdd-master-plan.md`
- StateManager API: `autoBMAD/docuswarm/storage/state_manager.py`
