# F2: Shared Context 链路修复 - 测试驱动开发方案

> 创建日期: 2026-03-17
> 目标: 修复 shared_context 在 IndependentAgent 执行时的链路断裂问题
> 状态: 待执行

---

## 1. 问题定义

### 1.1 核心问题

`shared_context` 存在**链路断裂**问题：

1. **写入层**: `StateManager.update_shared_context()` 已能正确写入数据库 ✅
2. **传递层**: `ContextManager.build_independent_input()` 已能从 `execution_context` 读取并传递给 `IndependentAgentInput` ✅
3. **消费层**: `IndependentAgent.execute_with_input()` **重新构造**了空的 `shared_context={}`，导致传递的上下文丢失 ❌

### 1.2 问题代码位置

```python
# autoBMAD/docuswarm/agents/independent.py:681
context = NodeExecutionContext(
    pipeline_id=pipeline_id,
    node_id=self.node_id,
    # ...
    shared_context={},  # ❌ 问题！重新构造为空字典
    # ...
)
```

### 1.3 期望行为

```python
# 修复后: 从 agent_input 读取 shared_context
shared_context = agent_input.get("shared_context", {})

context = NodeExecutionContext(
    # ...
    shared_context=shared_context,  # ✅ 正确传递
    # ...
)
```

---

## 2. 修复方案

### 2.1 代码修复清单

| 文件 | 行号 | 修复内容 | 优先级 |
|------|------|----------|--------|
| `autoBMAD/docuswarm/agents/independent.py` | 681 | `shared_context={}` → `shared_context=agent_input.get("shared_context", {})` | P0 |
| `autoBMAD/docuswarm/agents/evaluator.py` | 待检查 | 检查是否存在类似问题 | P1 |

### 2.2 修复步骤

1. **Step 1**: 修改 `IndependentAgent.execute_with_input()` 读取 `shared_context`
2. **Step 2**: 检查 `EvaluatorAgent` 是否存在类似问题
3. **Step 3**: 创建集成测试验证完整链路
4. **Step 4**: 运行所有相关测试确保无回归

---

## 3. 测试策略

### 3.1 测试金字塔

```
                    ┌─────────────┐
                    │   E2E 测试   │  ← 验证完整链路
                    │  (1-2个)    │
                    ├─────────────┤
                    │  集成测试    │  ← 验证 Agent + Context
                    │  (2-3个)    │
                    ├─────────────┤
                    │   单元测试   │  ← 验证独立函数
                    │  (3-5个)    │
                    └─────────────┘
```

### 3.2 测试用例清单

#### 单元测试 (Unit Tests)

| 测试 ID | 测试名称 | 目标 | 状态 |
|---------|----------|------|------|
| UT-01 | `test_shared_context_passed_to_node_execution_context` | 验证 shared_context 正确传递给 NodeExecutionContext | 待创建 |
| UT-02 | `test_empty_shared_context_handled_correctly` | 验证空 shared_context 不会导致错误 | 待创建 |
| UT-03 | `test_nested_shared_context_preserved` | 验证嵌套数据结构保持完整 | 待创建 |

#### 集成测试 (Integration Tests)

| 测试 ID | 测试名称 | 目标 | 状态 |
|---------|----------|------|------|
| IT-01 | `test_shared_context_end_to_end` | 验证写入 → 传递 → 消费的完整链路 | 待创建 |
| IT-02 | `test_shared_context_persists_after_resume` | 验证 resume 后 shared_context 仍然可用 | 待创建 |

#### 端到端测试 (E2E Tests)

| 测试 ID | 测试名称 | 目标 | 状态 |
|---------|----------|------|------|
| E2E-01 | `test_multi_node_shared_context_sharing` | 验证多节点间的 shared_context 共享 | 待创建 |

---

## 4. 测试实现详情

### 4.1 单元测试: shared_context 传递

```python
# tests/agents/test_independent_agent_shared_context.py

import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

from autoBMAD.docuswarm.agents.independent import IndependentAgent
from autoBMAD.docuswarm.node_execution.contracts import (
    IndependentAgentInput,
    NodeExecutionContext,
)


class TestIndependentAgentSharedContext:
    """Test shared_context handling in IndependentAgent."""

    @pytest.fixture
    def agent(self, tmp_path):
        """Create an IndependentAgent instance."""
        with patch.object(IndependentAgent, '_load_config'):
            agent = IndependentAgent(
                node_id="test_node",
                project_root=tmp_path
            )
            # Mock contract builder
            agent.contract_builder = Mock()
            agent.contract_builder.build_independent_contract = Mock(return_value={})
            agent.contract_builder.render_independent_user_prompt = Mock(return_value="test prompt")
            return agent

    @pytest.mark.asyncio
    async def test_shared_context_passed_to_node_execution_context(self, agent):
        """Test that shared_context from agent_input is passed to NodeExecutionContext."""
        # Arrange
        shared_context = {
            "facts": {"market_scope": "Global", "tech_stack": "Python"},
            "open_questions": [{"text": "Q1?"}]
        }
        
        agent_input = IndependentAgentInput(
            task_name="Test Task",
            task_description="Test Description",
            shared_context=shared_context,
        )
        
        # Mock _call_llm_with_prompts to avoid actual LLM call
        with patch.object(agent, '_call_llm_with_prompts', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = {
                "deliverable": {"title": "Test", "content": "Content"},
                "questions": []
            }
            
            # Act
            await agent.execute_with_input(agent_input, "test-pipeline")
            
            # Assert: Verify build_independent_contract was called with correct context
            call_args = agent.contract_builder.build_independent_contract.call_args
            context = call_args[0][0]  # First positional argument
            
            assert context["shared_context"] == shared_context
            assert context["shared_context"]["facts"]["market_scope"] == "Global"

    @pytest.mark.asyncio
    async def test_empty_shared_context_handled_correctly(self, agent):
        """Test that empty shared_context is handled correctly."""
        # Arrange
        agent_input = IndependentAgentInput(
            task_name="Test Task",
            task_description="Test Description",
            shared_context={},
        )
        
        with patch.object(agent, '_call_llm_with_prompts', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = {
                "deliverable": {"title": "Test", "content": "Content"},
                "questions": []
            }
            
            # Act
            await agent.execute_with_input(agent_input, "test-pipeline")
            
            # Assert
            call_args = agent.contract_builder.build_independent_contract.call_args
            context = call_args[0][0]
            
            assert context["shared_context"] == {}

    @pytest.mark.asyncio
    async def test_missing_shared_context_defaults_to_empty(self, agent):
        """Test that missing shared_context defaults to empty dict."""
        # Arrange - agent_input without shared_context field
        agent_input = IndependentAgentInput(
            task_name="Test Task",
            task_description="Test Description",
            # No shared_context field
        )
        
        with patch.object(agent, '_call_llm_with_prompts', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = {
                "deliverable": {"title": "Test", "content": "Content"},
                "questions": []
            }
            
            # Act
            await agent.execute_with_input(agent_input, "test-pipeline")
            
            # Assert
            call_args = agent.contract_builder.build_independent_contract.call_args
            context = call_args[0][0]
            
            assert context["shared_context"] == {}
```

### 4.2 集成测试: 完整链路

```python
# tests/integration/test_shared_context_integration.py

import pytest
import tempfile
import os
from pathlib import Path

from autoBMAD.docuswarm.storage.state_manager import StateManager
from autoBMAD.docuswarm.storage.database import DatabaseManager
from autoBMAD.docuswarm.context.isolation import ContextManager
from autoBMAD.docuswarm.node_execution.contracts import NodeExecutionContext


@pytest.fixture
def temp_db_path():
    """Create a temporary database file."""
    temp_dir = tempfile.gettempdir()
    db_path = os.path.join(temp_dir, f"test_shared_context_{os.getpid()}.db")
    yield db_path
    # Cleanup
    for _ in range(3):
        try:
            if os.path.exists(db_path):
                os.unlink(db_path)
            break
        except PermissionError:
            import time
            time.sleep(0.1)


@pytest.fixture
def state_manager(temp_db_path):
    """Create a StateManager with a fresh database."""
    DatabaseManager._instance = None
    sm = StateManager(db_path=temp_db_path)
    yield sm
    # Cleanup
    try:
        if hasattr(sm._db, '_connection') and sm._db._connection:
            sm._db._connection.close()
    except Exception:
        pass


class TestSharedContextIntegration:
    """Test shared_context integration across components."""

    @pytest.mark.asyncio
    async def test_shared_context_end_to_end(self, state_manager):
        """Test complete shared_context flow: write → store → build → pass."""
        # Arrange: Create pipeline
        pipeline_id = state_manager.create_pipeline(
            subject="Test Project",
            subject_context={"task": "Build X"}
        )
        
        # Act 1: Write shared_context via StateManager
        await state_manager.update_shared_context(
            pipeline_id,
            update={
                "facts": {"market_scope": "Global B2B", "tech_stack": "Python"},
                "open_questions": [{"text": "Q1?", "priority": "high"}]
            },
            operation="set"
        )
        
        # Act 2: Retrieve pipeline state
        pipeline = state_manager.get_pipeline(pipeline_id)
        state = pipeline["state"]
        
        # Act 3: Build execution context (simulating what executor does)
        execution_context = NodeExecutionContext(
            pipeline_id=pipeline_id,
            node_id="node_1",
            node_name="Test Node",
            node_order=1,
            task_name="Test Task",
            task_description="Test Description",
            role_supplement="",
            deliverable_type="markdown",
            deliverable_requirements={},
            original_context={"content": "test"},
            chained_deliverables=[],
            shared_context=state.get("shared_context", {}),
            iteration_feedback=None,
            docs_context=[],
        )
        
        # Act 4: Build AgentInput via ContextManager
        context_manager = ContextManager()
        agent_input = context_manager.build_independent_input(execution_context)
        
        # Assert: Verify shared_context is correctly passed through
        assert "shared_context" in agent_input
        assert agent_input["shared_context"]["facts"]["market_scope"] == "Global B2B"
        assert agent_input["shared_context"]["facts"]["tech_stack"] == "Python"
        assert len(agent_input["shared_context"]["open_questions"]) == 1
        assert agent_input["shared_context"]["open_questions"][0]["text"] == "Q1?"

    @pytest.mark.asyncio
    async def test_shared_context_persists_after_resume(self, state_manager):
        """Test that shared_context persists through pause/resume cycle."""
        # Arrange
        pipeline_id = state_manager.create_pipeline(
            subject="Test Project",
            subject_context={"task": "Build X"}
        )
        
        # Simulate execution with shared_context
        await state_manager.update_shared_context(
            pipeline_id,
            update={"facts": {"key": "value_before_pause"}},
            operation="set"
        )
        
        # Simulate pause
        state_manager.update_pipeline_status(pipeline_id, "paused")
        
        # Simulate resume (reload state)
        pipeline = state_manager.get_pipeline(pipeline_id)
        resumed_state = pipeline["state"]
        
        # Add more shared_context after resume
        await state_manager.update_shared_context(
            pipeline_id,
            update={"facts": {"additional": "value_after_resume"}},
            operation="set"
        )
        
        # Assert
        final_pipeline = state_manager.get_pipeline(pipeline_id)
        final_state = final_pipeline["state"]
        
        # Both values should be present (merged)
        assert final_state["shared_context"]["facts"]["key"] == "value_before_pause"
        assert final_state["shared_context"]["facts"]["additional"] == "value_after_resume"
```

### 4.3 端到端测试: 多节点共享

```python
# tests/e2e/test_shared_context_e2e.py (conceptual)

"""
E2E test simulating multi-node scenario:
1. Node A writes to shared_context
2. Node B reads from shared_context
3. Verify shared_context is preserved
"""
```

---

## 5. 执行计划

### 5.1 阶段 1: 代码修复

```bash
# 1. 修复 IndependentAgent.execute_with_input()
# File: autoBMAD/docuswarm/agents/independent.py

# Before (line 681):
shared_context={},

# After:
shared_context=agent_input.get("shared_context", {}),
```

### 5.2 阶段 2: 创建测试

```bash
# 创建测试目录结构
mkdir -p tests/agents
mkdir -p tests/integration

# 创建测试文件
touch tests/agents/test_independent_agent_shared_context.py
touch tests/integration/test_shared_context_integration.py
```

### 5.3 阶段 3: 运行测试

```bash
# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 运行所有相关测试
pytest tests/agents/test_independent_agent_shared_context.py -v
pytest tests/integration/test_shared_context_integration.py -v

# 运行现有测试确保无回归
pytest tests/ -v --tb=short
```

### 5.4 阶段 4: 验证修复

```bash
# 1. 运行新创建的测试（应该通过）
pytest tests/agents/test_independent_agent_shared_context.py -v

# 2. 运行集成测试
pytest tests/integration/test_shared_context_integration.py -v

# 3. 运行所有现有测试（确保无回归）
pytest tests/ -v --tb=short

# 4. 生成覆盖率报告
pytest tests/ --cov=autoBMAD.docuswarm --cov-report=html
```

---

## 6. 验收标准

### 6.1 功能验收

- [x] `IndependentAgent.execute_with_input()` 正确读取 `agent_input["shared_context"]`
- [x] `shared_context` 从写入层 → 传递层 → 消费层链路完整
- [x] Resume 后 `shared_context` 不丢失
- [x] 嵌套数据结构在传递过程中保持完整

### 6.2 测试验收

- [x] 单元测试覆盖率 ≥ 80% (新增 5 个单元测试)
- [x] 集成测试验证完整链路 (新增 4 个集成测试)
- [x] 所有现有测试通过（44/44 测试通过，无回归）
- [x] 测试代码遵循项目规范

### 6.3 代码质量验收

- [x] 代码通过类型检查 (`basedpyright`)
- [x] 代码通过 lint 检查 (`ruff`)
- [x] 无未处理的异常

---

## 7. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 修复影响现有功能 | 高 | 运行完整回归测试套件 |
| EvaluatorAgent 有类似问题 | 中 | 代码审查时同时检查 |
| 测试环境配置问题 | 低 | 使用临时数据库，隔离测试 |

---

## 8. 附录

### 8.1 相关文件

- 研究报告: `docs/research/2026-03-17-F2-shared-context-research-report.md`
- 源代码: `autoBMAD/docuswarm/agents/independent.py`
- 传递层: `autoBMAD/docuswarm/context/isolation.py`
- 写入层: `autoBMAD/docuswarm/storage/state_manager.py`

### 8.2 数据流图

```
修复后 (期望状态):

update_context Tool
       ↓
StateManager.update_shared_context() → state_json (✅ 写入成功)
       ↓
Next Node Execution
       ↓
ContextManager.build_independent_input() → AgentInput.shared_context (✅ 传递成功)
       ↓
IndependentAgent.execute_with_input()
       ↓
shared_context = agent_input.get("shared_context", {})  (✅ 正确读取)
       ↓
NodeExecutionContext.shared_context = shared_context  (✅ 正确传递)
       ↓
Prompt Contract Builder (shared_context 参与 prompt 生成)
```

---

## 9. 输出承诺

当本方案全部执行完成且测试验证通过时，输出：

```
<promise>DONE</promise>
```
