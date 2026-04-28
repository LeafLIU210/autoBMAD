# F2: Shared Context 持续参与执行深度研究报告

> 研究日期: 2026-03-17
> 研究范围: autoBMAD/docuswarm shared_context 机制
> 核心问题: shared_context 只完成"能写"，未完成"能持续参与执行"

---

## 1. 执行摘要

### 1.1 核心发现

`shared_context` 功能存在**链路断裂**问题：

1. **写入层**: `StateManager.update_shared_context()` 已能正确写入数据库
2. **传递层**: `ContextManager.build_independent_input()` 已能从 `execution_context` 读取并传递给 `IndependentAgentInput`
3. **消费层**: `IndependentAgent.execute_with_input()` **重新构造**了空的 `shared_context={}`，导致传递的上下文丢失

### 1.2 关键代码证据

```python
# autoBMAD/docuswarm/storage/state_manager.py:480
async def update_shared_context(self, pipeline_id: str, update: Any, ...) -> bool:
    # ✅ 写入功能已正确实现

# autoBMAD/docuswarm/context/isolation.py:101
shared_context = execution_context.get("shared_context", {})
# autoBMAD/docuswarm/context/isolation.py:112
shared_context=shared_context,  # ✅ 传递给 AgentInput

# autoBMAD/docuswarm/agents/independent.py:681
shared_context={},  # ❌ 重新构造为空，丢失传递的值
```

---

## 2. 详细分析

### 2.1 Shared Context 链路全图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Shared Context 数据流                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. 写入层 (Storage)                                                      │
│     ├── update_context Tool 调用                                        │
│     └── StateManager.update_shared_context()                            │
│         └── UPDATE pipelines SET state_json = ...                       │
│                                                                         │
│  2. 读取层 (Context)                                                      │
│     └── ContextManager.build_independent_input()                        │
│         └── execution_context["shared_context"]                         │
│             └── IndependentAgentInput.shared_context                    │
│                                                                         │
│  3. 消费层 (Agent)   ←─ 问题在这里                                        │
│     └── IndependentAgent.execute_with_input()                           │
│         └── NodeExecutionContext.shared_context = {}  ❌ 重置为空         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 写入层分析

#### 2.2.1 StateManager.update_shared_context()

```python
# state_manager.py:480-634
async def update_shared_context(
    self,
    pipeline_id: str,
    update: Any,
    operation: str = "set",
    key_path: str | None = None,
) -> bool:
    # 1. 读取当前 state_json
    current_state = json.loads(row["state_json"])
    
    # 2. 确保 shared_context 存在
    if "shared_context" not in current_state:
        current_state["shared_context"] = {}
    
    # 3. 执行 set/append/remove 操作
    if operation == "set":
        self._deep_merge(shared_context, update)
    
    # 4. 写回数据库
    updated_state_json = json.dumps(current_state)
```

**评估**: ✅ 写入逻辑完整，支持嵌套键路径操作

#### 2.2.2 UpdateContextTool

```python
# update_context.py:47-179
class UpdateContextTool(CallableTool2[UpdateContextParams]):
    def __init__(self, state_manager: StateManager, pipeline_id: str):
        self._state_manager = state_manager
        self._pipeline_id = pipeline_id
    
    async def __call__(self, params: UpdateContextParams) -> ToolReturnValue:
        # 调用 StateManager 更新
        result = await self._state_manager.update_shared_context(
            pipeline_id=self._pipeline_id,
            update=params.value,
            operation=params.operation,
            key_path=params.key,
        )
```

**评估**: ✅ 工具层正确依赖 StateManager

### 2.3 传递层分析

#### 2.3.1 ContextManager.build_independent_input()

```python
# isolation.py:70-113
def build_independent_input(
    self,
    execution_context: NodeExecutionContext,
    iteration_feedback: dict[str, Any] | None = None,
) -> IndependentAgentInput:
    # P1-1: Get shared_context from execution_context
    shared_context = execution_context.get("shared_context", {})  # ✅ 读取
    
    return IndependentAgentInput(
        task_name=execution_context["task_name"],
        # ... 其他字段
        shared_context=shared_context,  # ✅ 传递给 AgentInput
    )
```

**评估**: ✅ 传递逻辑正确

### 2.4 消费层分析 - 问题核心

#### 2.4.1 IndependentAgent.execute_with_input()

```python
# independent.py:613-727
async def execute_with_input(
    self,
    agent_input: IndependentAgentInput,
    pipeline_id: str,
) -> IndependentOutput:
    # 从 AgentInput 读取字段
    task_name = agent_input.get("task_name", "")
    # ... 其他字段
    
    # P0: Build NodeExecutionContext from agent_input
    context = NodeExecutionContext(
        pipeline_id=pipeline_id,
        node_id=self.node_id,
        # ... 其他字段
        shared_context={},  # ❌❌❌ 问题！重新构造为空字典
        #                    应该使用 agent_input.get("shared_context", {})
    )
```

**问题**: 
- 第 681 行明确设置 `shared_context={}`
- 应该从 `agent_input` 读取 `shared_context` 字段

#### 2.4.2 影响的场景

| 场景 | 期望行为 | 实际行为 |
|------|----------|----------|
| Node A 调用 update_context | 更新写入 state_json | ✅ 成功写入 |
| Node B 读取 shared_context | 能看到 Node A 的更新 | ❌ 看不到，context 被重置为空 |
| Resume 后读取 | 能看到之前的 shared_context | ❌ 丢失 |

---

## 3. 收敛方案

### 3.1 修复 IndependentAgent.execute_with_input()

```python
async def execute_with_input(
    self,
    agent_input: IndependentAgentInput,
    pipeline_id: str,
) -> IndependentOutput:
    # Single Context Protocol: 直接从结构化输入读取字段
    task_name = agent_input.get("task_name", "")
    task_description = agent_input.get("task_description", "")
    role_supplement = agent_input.get("role_supplement", "")
    deliverable_reqs = agent_input.get("deliverable_requirements", {})
    original_context = agent_input.get("original_context_summary", "")
    chained_deliverables = agent_input.get("chained_deliverables_summary", [])
    iteration_feedback = agent_input.get("iteration_feedback")
    
    # ✅ 修复: 读取 shared_context
    shared_context = agent_input.get("shared_context", {})
    
    # ...
    
    # P0: Build NodeExecutionContext from agent_input
    context = NodeExecutionContext(
        pipeline_id=pipeline_id,
        node_id=self.node_id,
        # ... 其他字段
        shared_context=shared_context,  # ✅ 使用从 AgentInput 读取的值
        # ...
    )
```

### 3.2 修复 EvaluatorAgent 中的类似问题

检查 `EvaluatorAgent.execute_with_input()` 是否存在同样的问题：

```python
# evaluator.py:519-600
def build_evaluator_context_with_input(self, agent_input: EvaluatorAgentInput):
    # 检查是否也重置了 shared_context
    # 如果是，同样修复
```

### 3.3 确保全流程传递

#### 3.3.1 写入时序

```python
# 1. Independent Agent 调用 update_context 工具
await update_context_tool({
    "key": "facts.market_scope",
    "value": {"target": "enterprise"},
    "operation": "set"
})

# 2. 工具写入 state_json
state_manager.update_shared_context(
    pipeline_id="pipeline-xxx",
    update={"facts": {"market_scope": {"target": "enterprise"}}},
    operation="set",
    key_path="facts.market_scope"
)

# 3. 下一个节点执行时
execution_context = build_execution_context(pipeline_state)
# execution_context["shared_context"] 应该包含 facts.market_scope
```

#### 3.3.2 读取时序

```python
# 1. ContextManager 从 state 构建 execution_context
execution_context = NodeExecutionContext(
    # ...
    shared_context=pipeline_state.get("shared_context", {}),
    # ...
)

# 2. 构建 AgentInput
agent_input = context_manager.build_independent_input(execution_context)
# agent_input["shared_context"] 应该传递值

# 3. Agent 消费 AgentInput
shared_context = agent_input.get("shared_context", {})
# 应该能读取到 facts.market_scope
```

---

## 4. 测试建议

### 4.1 端到端测试

```python
async def test_shared_context_end_to_end():
    """测试 shared_context 从写入到读取的完整链路."""
    # 1. 创建 pipeline
    pipeline_id = await orchestrator.start_pipeline(subject_context)
    
    # 2. 模拟第一个节点写入 shared_context
    await state_manager.update_shared_context(
        pipeline_id=pipeline_id,
        update={"facts": {"key_insight": "important_value"}},
        operation="set",
        key_path="facts.key_insight"
    )
    
    # 3. 构建 execution_context（模拟下一个节点）
    pipeline = state_manager.get_pipeline(pipeline_id)
    execution_context = NodeExecutionContext(
        # ... 其他字段
        shared_context=pipeline["state"].get("shared_context", {}),
        # ...
    )
    
    # 4. 构建 AgentInput
    agent_input = context_manager.build_independent_input(execution_context)
    
    # 5. 验证 shared_context 被正确传递
    assert agent_input.get("shared_context", {}).get("facts", {}).get("key_insight") == "important_value"
    
    # 6. 验证 Agent 能正确读取
    # 创建 mock Agent 验证 execute_with_input 中的处理
```

### 4.2 Resume 后 Shared Context 持久化测试

```python
async def test_shared_context_persists_after_resume():
    """验证 resume 后 shared_context 仍然可用."""
    # 1. 创建并执行 pipeline 到某节点
    # 2. 写入 shared_context
    # 3. 暂停 pipeline
    # 4. Resume
    # 5. 验证下一个节点仍能看到 shared_context
```

### 4.3 Prompt 快照测试

```python
async def test_shared_context_in_prompt():
    """验证 shared_context 最终出现在 Agent 的 prompt 中."""
    # 构建包含 shared_context 的 AgentInput
    # 调用 Agent 的 prompt 构建
    # 验证 prompt 中包含 shared_context 的内容
```

---

## 5. 代码修改清单

### 5.1 必须修复

- [ ] `autoBMAD/docuswarm/agents/independent.py:681`
  - 修改 `shared_context={}` 为 `shared_context=agent_input.get("shared_context", {})`

### 5.2 需要检查

- [ ] `autoBMAD/docuswarm/agents/evaluator.py`
  - 检查是否有类似的 shared_context 重置问题

### 5.3 测试覆盖

- [ ] 创建 `test_shared_context_integration.py`
  - 端到端链路测试
  - Resume 持久化测试
  - Prompt 内容快照测试

---

## 6. 结论

1. **shared_context 写入和传递层功能正常**，问题仅在消费层
2. **修复成本较低**，只需修改 `IndependentAgent.execute_with_input()` 中的 context 构建逻辑
3. **测试是关键**，需要端到端测试验证完整链路
4. **Resume 场景需要特别关注**，确保恢复后 shared_context 不丢失

---

## 相关文档 (2026-03-18 更新)

### 技术债务关联

Shared Context 链路与 **TD-1** 和 **TD-4** 技术债务相关：

| 技术债务 | 关联说明 |
|---------|---------|
| **TD-1** | shared_context 持久化依赖 state_json 作为唯一真相源 |
| **TD-4** | shared_context 链路跨越 pipeline/node_execution 边界，需要清晰的骨架边界 |

### 参考文档

- [技术债务评估报告](../evaluation/2026-03-18-docuswarm-technical-debt-evaluation.md)
- [技术债务深度研究报告](2026-03-18-docuswarm-p0-p1-technical-debt-deep-research-report.md)
- [P0/P1 TDD 主方案](../solution/2026-03-18-docuswarm-p0-p1-tdd-master-plan.md)

---

## 附录: 数据流对比图

### 修复前 (问题状态)

```
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
NodeExecutionContext.shared_context = {}  (❌ 重置为空，值丢失)
```

### 修复后 (期望状态)

```
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
