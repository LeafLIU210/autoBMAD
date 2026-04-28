# Phase 3: P0-2 - Evaluator 上下文补完 - TDD 执行计划

> 基于: `docs/solution/2026-03-17-docuswarm-context-refactor-tdd-master-plan.md`  
> 优先级: 🟡 中  
> 目标: Evaluator prompt 包含原始上下文摘要

## 研究问题回顾

来自研究报告:
- **P0-2-003**: EvaluatorAgentInput 缺少原始上下文摘要字段
- **P0-2-001/002/004**: NodePromptContractBuilder 和 IndependentAgent 已完成 (✅ 部分完成)

## 实施步骤

### Step 1: EvaluatorAgentInput 添加 original_context_summary

#### TDD Cycle 1.1

**Red - 编写失败测试:**
```python
# tests/unit/node_execution/test_contracts.py

from autoBMAD.docuswarm.node_execution.contracts import EvaluatorAgentInput


class TestEvaluatorAgentInputSchema:
    """Test EvaluatorAgentInput has original context"""
    
    def test_has_original_context_field(self):
        """EvaluatorAgentInput should have original_context_summary field"""
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
            "criteria": [
                {"name": "clarity", "description": "Clear and concise", "weight": 0.5}
            ]
        }
        
        # Should not raise
        validate_evaluator_agent_input(input_data)
    
    def test_original_context_summary_is_optional(self):
        """original_context_summary should be optional for backward compatibility"""
        input_data: EvaluatorAgentInput = {
            "task_name": "test-task",
            "task_description": "test description",
            # original_context_summary missing
            "deliverable_artifact": {"title": "Test", "file_path": "/tmp/test.md", "sha256": "abc"},
            "deliverable_body": "Content",
            "criteria": []
        }
        
        # Should not raise
        validate_evaluator_agent_input(input_data)
```

运行测试:
```bash
pytest tests/unit/node_execution/test_contracts.py::TestEvaluatorAgentInputSchema -v
# Expected: FAIL (field doesn't exist)
```

**Green - 实现:**
```python
# autoBMAD/docuswarm/node_execution/contracts.py

class EvaluatorAgentInput(TypedDict, total=False):
    """EvaluatorAgent 的输入 - 由 ContextManager 从 NodeExecutionContext 裁剪。"""
    
    task_name: str
    task_description: str
    original_context_summary: str  # P0-2: NEW FIELD
    deliverable_artifact: dict[str, Any]
    deliverable_body: str
    criteria: list[dict[str, Any]]
```

运行测试:
```bash
pytest tests/unit/node_execution/test_contracts.py::TestEvaluatorAgentInputSchema -v
# Expected: PASS
```

---

### Step 2: ContextManager.build_evaluator_input 传递原始上下文

#### TDD Cycle 2.1

**Red - 编写失败测试:**
```python
# tests/unit/context/test_isolation.py

class TestEvaluatorOriginalContext:
    """Test Evaluator gets original context"""
    
    def test_includes_original_context_from_execution_context(self):
        """build_evaluator_input should include original context summary"""
        manager = ContextManager()
        execution_context = NodeExecutionContext(
            pipeline_id="test",
            node_id="pm",
            node_name="PM",
            node_order=2,
            task_name="Create PRD",
            task_description="Create PRD document",
            role_supplement="",
            deliverable_type="prd",
            deliverable_requirements={},
            original_context={
                "content": "User wants a collaborative task management app with real-time sync",
                "project_name": "TaskApp"
            },
            chained_deliverables=[],
            shared_context={},
            iteration_feedback=None,
            docs_context=[]
        )
        
        deliverable = {
            "title": "Analysis",
            "file_path": "/tmp/test.md",
            "sha256": "abc123"
        }
        
        result = manager.build_evaluator_input(execution_context, deliverable)
        
        assert "original_context_summary" in result
        assert "collaborative task management" in result["original_context_summary"]
        assert "TaskApp" in result["original_context_summary"]
    
    def test_handles_missing_original_context(self):
        """build_evaluator_input should handle missing original_context"""
        manager = ContextManager()
        execution_context = NodeExecutionContext(
            # ... other fields ...
            original_context={},  # Empty
            # ...
        )
        
        deliverable = {
            "title": "Analysis",
            "file_path": "/tmp/test.md",
            "sha256": "abc123"
        }
        
        result = manager.build_evaluator_input(execution_context, deliverable)
        
        assert "original_context_summary" in result
        assert result["original_context_summary"] == ""
```

**Green - 实现:**
```python
# autoBMAD/docuswarm/context/isolation.py

def build_evaluator_input(
    self,
    execution_context: NodeExecutionContext,
    deliverable: dict[str, Any] | None,
) -> EvaluatorAgentInput:
    """构建 EvaluatorAgent 的输入。"""
    # ... existing file reading logic from P0-3 ...
    
    # P0-2: Extract original context summary
    original_context = execution_context.get("original_context", {})
    if isinstance(original_context, dict):
        original_summary = original_context.get("content", "")
        if not original_summary and "subject_context" in original_context:
            # Handle nested structure
            nested = original_context["subject_context"]
            if isinstance(nested, dict):
                original_summary = nested.get("content", "")
    else:
        original_summary = str(original_context)
    
    return EvaluatorAgentInput(
        task_name=execution_context["task_name"],
        task_description=execution_context["task_description"],
        original_context_summary=original_summary,  # P0-2: NEW
        deliverable_artifact=deliverable,
        deliverable_body=deliverable_body,
        criteria=execution_context.get("evaluator_criteria", []),
    )
```

---

### Step 3: NodePromptContractBuilder 渲染原始上下文章节

#### TDD Cycle 3.1

**Red - 编写失败测试:**
```python
# tests/unit/prompts/test_contract_builder.py

class TestEvaluatorOriginalContextSection:
    """Test Evaluator prompt includes original context section"""
    
    def test_build_evaluator_context_section_includes_original(self):
        """_build_evaluator_context_section should include original context"""
        builder = NodePromptContractBuilder()
        context = NodeExecutionContext(
            original_context={
                "content": "User wants a task management app with real-time collaboration"
            }
        )
        
        section = builder._build_evaluator_context_section(context)
        
        assert "原始需求摘要" in section or "Original Context" in section
        assert "task management app" in section
    
    def test_evaluator_contract_includes_context_section(self):
        """build_evaluator_contract should include context_section with original context"""
        builder = NodePromptContractBuilder()
        context = NodeExecutionContext(
            original_context={
                "content": "Build a collaborative task app"
            }
        )
        
        contract = builder.build_evaluator_contract(
            context,
            deliverable_body="# Full content"
        )
        
        assert "context_section" in contract
        assert "collaborative task app" in contract["context_section"]
    
    def test_render_evaluator_prompt_includes_original_context(self):
        """render_evaluator_prompt should include original context section"""
        builder = NodePromptContractBuilder()
        contract = EvaluatorPromptContract(
            task_section="## Task",
            criteria_section="## Criteria",
            deliverable_section="## Deliverable",
            context_section="## 原始需求摘要\n\nUser wants a task app",
            deliverable_body="# Content"
        )
        
        prompt = builder.render_evaluator_prompt(contract)
        
        assert "原始需求摘要" in prompt
        assert "User wants a task app" in prompt
```

**Green - 实现:**
```python
# autoBMAD/docuswarm/prompts/contract_builder.py

def _build_evaluator_context_section(self, context: NodeExecutionContext) -> str:
    """构建 Evaluator 的最小上下文章节。"""
    # P0-2: Include original context summary
    original_context = context.get("original_context", {})
    
    content = ""
    if isinstance(original_context, dict):
        content = original_context.get("content", "")
        # Handle nested structure
        if not content and "subject_context" in original_context:
            nested = original_context["subject_context"]
            if isinstance(nested, dict):
                content = nested.get("content", "")
    elif isinstance(original_context, str):
        content = original_context
    
    if content:
        # Truncate to reasonable length for Evaluator
        max_len = 500
        if len(content) > max_len:
            content = content[:max_len] + "..."
        
        return f"""## 原始需求摘要

{content}
"""
    return ""


def build_evaluator_contract(
    self,
    context: NodeExecutionContext,
    deliverable_body: str,
) -> EvaluatorPromptContract:
    """构建 EvaluatorPromptContract."""
    return {
        "task_section": self._build_evaluator_task_section(context),
        "criteria_section": self._build_criteria_section(context),
        "deliverable_section": self._build_evaluator_deliverable_section(deliverable_body),
        "context_section": self._build_evaluator_context_section(context),  # P0-2
        "deliverable_body": deliverable_body,
    }
```

---

### Step 4: EvaluatorAgent.execute_with_input 使用原始上下文

#### TDD Cycle 4.1

**Red - 编写失败测试:**
```python
# tests/unit/agents/test_evaluator.py

class TestEvaluatorAgentOriginalContext:
    """Test EvaluatorAgent uses original context"""
    
    @pytest.mark.asyncio
    async def test_execute_with_input_includes_original_context(self):
        """execute_with_input should build context with original_context"""
        # Arrange
        agent = EvaluatorAgent(
            config=mock_config,
            session_manager=mock_session_manager,
            node_id="test"
        )
        
        agent_input = EvaluatorAgentInput(
            task_name="Create PRD",
            task_description="Create PRD document",
            original_context_summary="User wants a task app",  # P0-2
            deliverable_artifact={"title": "Doc", "file_path": "/tmp/doc.md", "sha256": "abc"},
            deliverable_body="# Full content",
            criteria=[]
        )
        
        # Mock the LLM call to capture the prompt
        captured_prompt = None
        async def mock_call_llm(prompt):
            nonlocal captured_prompt
            captured_prompt = prompt
            return mock_evaluator_response()
        
        agent._call_llm_with_prompt = mock_call_llm
        
        # Act
        await agent.execute_with_input(agent_input)
        
        # Assert
        assert captured_prompt is not None
        assert "User wants a task app" in captured_prompt
```

**Green - 实现:**
```python
# autoBMAD/docuswarm/agents/evaluator.py

async def execute_with_input(self, agent_input: EvaluatorAgentInput) -> EvaluatorOutput:
    """Execute the Evaluator Agent with structured input."""
    task_name = agent_input["task_name"]
    task_description = agent_input["task_description"]
    original_context = agent_input.get("original_context_summary", "")  # P0-2
    deliverable_body = agent_input["deliverable_body"]
    criteria = agent_input["criteria"] or self.criteria
    
    # P0-2: Build NodeExecutionContext with original_context
    context = NodeExecutionContext(
        pipeline_id="",
        node_id=self.node_id,
        node_name=task_name,
        node_order=0,
        task_name=task_name,
        task_description=task_description,
        role_supplement="",
        deliverable_type="",
        deliverable_requirements={},
        original_context={"content": original_context},  # P0-2
        chained_deliverables=[],
        shared_context={},
        iteration_feedback=None,
        docs_context=[],
        evaluator_criteria=criteria,
    )
    
    # Build contract from context
    contract = self.contract_builder.build_evaluator_contract(
        context,
        deliverable_body=deliverable_body,
    )
    
    # Render full prompt from contract
    prompt = self.contract_builder.render_evaluator_prompt(contract)
    
    # Call LLM
    response = await self._call_llm_with_prompt(prompt)
    
    # Parse and return
    return self._parse_response(response)
```

---

### Step 5: 集成测试

#### TDD Cycle 5.1

**Red - 编写失败测试:**
```python
# tests/integration/test_evaluator_original_context.py

class TestEvaluatorOriginalContextIntegration:
    """Integration test: Evaluator sees original context"""
    
    @pytest.mark.asyncio
    async def test_evaluator_prompt_contains_original_context(self, tmp_path):
        """End-to-end: Evaluator prompt should contain original context"""
        # Arrange
        original_request = "Build a real-time collaborative task management application"
        
        execution_context = NodeExecutionContext(
            pipeline_id="test",
            node_id="pm",
            # ... other fields ...
            original_context={"content": original_request},
            # ...
        )
        
        # Create deliverable file
        deliverable_file = tmp_path / "prd.md"
        deliverable_file.write_text("# PRD\n\nContent here")
        
        deliverable = {
            "title": "PRD",
            "file_path": str(deliverable_file),
            "sha256": "abc123"
        }
        
        # Act
        manager = ContextManager()
        evaluator_input = manager.build_evaluator_input(
            execution_context,
            deliverable
        )
        
        builder = NodePromptContractBuilder()
        contract = builder.build_evaluator_contract(
            execution_context,
            deliverable_body=deliverable_file.read_text()
        )
        prompt = builder.render_evaluator_prompt(contract)
        
        # Assert
        assert "原始需求摘要" in prompt or original_request in prompt
        assert original_request[:50] in prompt  # At least part of it
```

---

## 验收清单

- [ ] `EvaluatorAgentInput` 包含 `original_context_summary` 字段
- [ ] `build_evaluator_input()` 从 `execution_context["original_context"]` 提取摘要
- [ ] `NodePromptContractBuilder._build_evaluator_context_section()` 渲染原始上下文
- [ ] `build_evaluator_contract()` 包含 `context_section`
- [ ] `render_evaluator_prompt()` 包含原始上下文章节
- [ ] `EvaluatorAgent.execute_with_input()` 传递原始上下文到 contract builder
- [ ] Evaluator prompt 稳定出现"原始需求摘要"章节
- [ ] 集成测试验证端到端流程
- [ ] 所有测试通过率 100%
- [ ] 代码覆盖率 > 80%

## 与 Phase 1/2 的依赖关系

Phase 3 依赖:
- Phase 1: `NodeExecutionContext` 结构 (P1-1)
- Phase 2: `build_evaluator_input()` 签名和文件读取逻辑 (P0-3)

建议: **按顺序执行 Phase 1 -> Phase 2 -> Phase 3**

## 参考文档

- 研究报告: `docs/research/2026-03-17-docuswarm-context-refactor-deep-research-report.md`
- 主 TDD 方案: `docs/solution/2026-03-17-docuswarm-context-refactor-tdd-master-plan.md`
- Phase 1 计划: `docs/solution/2026-03-17-phase1-p1-1-update-context-tdd-execution-plan.md`
- Phase 2 计划: `docs/solution/2026-03-17-phase2-p0-3-single-truth-tdd-execution-plan.md`
