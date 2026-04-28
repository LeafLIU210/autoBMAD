# F3: Evaluator 输入契约闭环深度研究报告

> 研究日期: 2026-03-17
> 研究范围: autoBMAD/docuswarm EvaluatorAgent 输入契约
> 核心问题: Evaluator 输入契约被重新削弱，原始上下文与交付物真相未稳定闭环

---

## 1. 执行摘要

### 1.1 核心发现

`EvaluatorAgent` 的输入契约存在**二次削弱**问题：

1. **ContextManager.build_evaluator_input()** 已正确构建 `EvaluatorAgentInput`，包含：
   - `original_context_summary` (原始上下文摘要)
   - `deliverable_body` (从文件读取的正式正文)
   - `criteria` (评审标准)

2. **EvaluatorAgent.execute_with_input()** 收到 `EvaluatorAgentInput` 后，又重建了缩水的 `NodeExecutionContext`，丢失了：
   - `original_context={}` (置空)
   - `shared_context={}` (置空)

3. **结果**: Evaluator 更像在评审"文档文本质量"，而非稳定地评审"文档是否满足原始任务与约束"。

### 1.2 关键代码证据

```python
# autoBMAD/docuswarm/context/isolation.py:140-162
# ✅ ContextManager 正确构建 EvaluatorAgentInput
def build_evaluator_input(...) -> EvaluatorAgentInput:
    file_path = deliverable.get("file_path")
    deliverable_body = path.read_text(encoding="utf-8")  # P0-3: 读取正式正文
    original_summary = _extract_original_context_summary(original_context)  # P0-2: 提取摘要
    
    return EvaluatorAgentInput(
        task_name=execution_context["task_name"],
        original_context_summary=original_summary,  # ✅ 传递原始上下文
        deliverable_body=deliverable_body,          # ✅ 传递正式正文
        criteria=execution_context.get("evaluator_criteria", []),
    )

# autoBMAD/docuswarm/agents/evaluator.py:571-573
# ❌ EvaluatorAgent 重建时丢失关键字段
context = NodeExecutionContext(
    # ...
    original_context={},  # ❌ 置空！应该使用 agent_input["original_context_summary"]
    shared_context={},    # ❌ 置空！
    # ...
)
```

---

## 2. 详细分析

### 2.1 Evaluator 评审逻辑全图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Evaluator 输入契约链路                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. 交付物生成 (Independent Agent)                                        │
│     └── create_deliverable Tool → 写入文件 (file_path)                   │
│                                                                         │
│  2. 输入构建 (ContextManager)   ←─ 正确实现                                │
│     ├── 读取交付物文件 → deliverable_body                               │
│     ├── 提取原始上下文 → original_context_summary                         │
│     └── 组装 EvaluatorAgentInput                                        │
│                                                                         │
│  3. Prompt 构建 (ContractBuilder) ←─ 问题：输入被削弱                      │
│     └── 使用 NodeExecutionContext (original_context={}, shared_context={})
│                                                                         │
│  4. 评审执行 (Evaluator LLM)    ←─ 问题：评审范围不完整                     │
│     └── Prompt 缺少原始任务约束，仅评审文本质量                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 ContextManager.build_evaluator_input() 分析

```python
# isolation.py:115-162
def build_evaluator_input(
    self,
    execution_context: NodeExecutionContext,
    deliverable: dict[str, Any] | None,
) -> EvaluatorAgentInput:
    """构建 EvaluatorAgent 的输入。
    
    P0-3: Evaluator 必须评审工具写盘后的正式文档正文，
    不允许退回到 deliverable.summary。
    """
    if not deliverable:
        raise ValueError("deliverable is required for evaluation")
    
    # P0-3: file_path is REQUIRED, no fallback
    file_path = deliverable.get("file_path")
    if not file_path:
        raise ValueError("file_path is required for evaluation")
    
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Deliverable file not found: {file_path}")
    
    # P0-3: Always read full content from file ✅
    deliverable_body = path.read_text(encoding="utf-8")
    
    # P0-2: Extract original context summary ✅
    original_context = execution_context.get("original_context", {})
    original_summary = _extract_original_context_summary(original_context)
    
    return EvaluatorAgentInput(
        task_name=execution_context["task_name"],
        task_description=execution_context["task_description"],
        original_context_summary=original_summary,  # ✅ P0-2: 原始上下文摘要
        deliverable_artifact=deliverable,
        deliverable_body=deliverable_body,          # ✅ P0-3: 正式正文
        criteria=execution_context.get("evaluator_criteria", []),
    )
```

**评估**: ✅ 该层实现正确，所有必要字段都已提取和传递。

### 2.3 EvaluatorAgent.execute_with_input() 分析 - 问题核心

```python
# evaluator.py:519-600
async def execute_with_input(self, agent_input: EvaluatorAgentInput) -> EvaluatorOutput:
    """Execute the Evaluator Agent with structured input (Single Context Protocol).
    
    P0: Uses NodePromptContractBuilder to build structured prompts with criteria
    and deliverable requirements explicitly injected.
    """
    # Single Context Protocol: 直接从结构化输入读取字段
    task_name = agent_input.get("task_name", "")
    task_description = agent_input.get("task_description", "")
    # deliverable_artifact reserved for future use
    _ = agent_input.get("deliverable_artifact", {})
    deliverable_body = agent_input.get("deliverable_body", "")
    criteria = agent_input.get("criteria") or self.criteria
    
    # ...
    
    # P0: Build NodeExecutionContext from agent_input  ←─ 问题在这里
    from autoBMAD.docuswarm.node_execution.contracts import NodeExecutionContext
    
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
        original_context={},      # ❌ 第571行：置空！应该使用 agent_input["original_context_summary"]
        chained_deliverables=[],
        shared_context={},        # ❌ 第573行：置空！
        iteration_feedback=None,
        docs_context=[],
        evaluator_criteria=criteria,
    )
    
    # P0: Build contract from context using NodePromptContractBuilder
    contract = self.contract_builder.build_evaluator_contract(
        context,
        deliverable_body=deliverable_body,
    )
    
    # P0: Render full prompt from contract
    prompt = self.contract_builder.render_evaluator_prompt(contract)
    
    # P0: Call LLM with contract-based prompt
    response = await self._call_llm_with_prompt(prompt)
    
    # ...
```

**问题识别**:

| 行号 | 代码 | 问题 |
|------|------|------|
| 571 | `original_context={}` | 丢失了 `agent_input["original_context_summary"]` |
| 573 | `shared_context={}` | 丢失了可能相关的共享上下文 |

### 2.4 影响分析

#### 2.4.1 Evaluator Prompt 对比

**修复前（当前）的 Prompt 结构**:

```
## 任务
{task_name}
{task_description}

## 交付物评审
{deliverable_body}

## 评审标准
{criteria}
```

**修复后的 Prompt 结构**:

```
## 原始任务上下文
{original_context_summary}  ←─ 缺失！

## 任务
{task_name}
{task_description}

## 交付物评审
{deliverable_body}

## 评审标准
{criteria}

## 评审指引
请评估该交付物是否满足原始任务上下文中的需求和约束。
```

#### 2.4.2 评审质量问题

| 评审维度 | 修复前 | 修复后 |
|----------|--------|--------|
| 文本质量 | ✅ 可评审 | ✅ 可评审 |
| 需求符合度 | ❌ 无法判断 | ✅ 可评审 |
| 约束满足度 | ❌ 无法判断 | ✅ 可评审 |
| 业务价值 | ❌ 难以评估 | ✅ 可评估 |

---

## 3. 收敛方案

### 3.1 修复 EvaluatorAgent.execute_with_input()

```python
async def execute_with_input(self, agent_input: EvaluatorAgentInput) -> EvaluatorOutput:
    """Execute the Evaluator Agent with structured input."""
    # Single Context Protocol: 直接从结构化输入读取字段
    task_name = agent_input.get("task_name", "")
    task_description = agent_input.get("task_description", "")
    _ = agent_input.get("deliverable_artifact", {})
    deliverable_body = agent_input.get("deliverable_body", "")
    criteria = agent_input.get("criteria") or self.criteria
    
    # ✅ 修复: 读取原始上下文摘要
    original_context_summary = agent_input.get("original_context_summary", "")
    
    # ✅ 可选: 如果需要，也可以传递 shared_context
    # shared_context = agent_input.get("shared_context", {})
    
    self.logger.info(
        "executing_evaluator_agent_with_input",
        node_id=self.node_id,
        task_name=task_name,
        has_original_context=bool(original_context_summary),  # 日志记录
    )
    
    # P0: Build NodeExecutionContext from agent_input
    from autoBMAD.docuswarm.node_execution.contracts import NodeExecutionContext
    
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
        original_context={"content": original_context_summary},  # ✅ 使用读取的值
        chained_deliverables=[],
        shared_context={},  # 或 shared_context 如果已读取
        iteration_feedback=None,
        docs_context=[],
        evaluator_criteria=criteria,
    )
    
    # ... 后续逻辑不变
```

### 3.2 方案 B: 直接契约传递（推荐）

更彻底的方案是让 `ContractBuilder` 直接消费 `EvaluatorAgentInput`，而不是重建 `NodeExecutionContext`。

```python
# 新增 ContractBuilder 方法
def build_evaluator_contract_from_input(
    self,
    agent_input: EvaluatorAgentInput,
    deliverable_body: str,
) -> EvaluatorPromptContract:
    """直接从 EvaluatorAgentInput 构建契约，不经过 NodeExecutionContext."""
    return EvaluatorPromptContract(
        task_name=agent_input.get("task_name", ""),
        task_description=agent_input.get("task_description", ""),
        original_context_summary=agent_input.get("original_context_summary", ""),
        deliverable_body=deliverable_body,
        criteria=agent_input.get("criteria", []),
    )

# EvaluatorAgent.execute_with_input() 修改
async def execute_with_input(self, agent_input: EvaluatorAgentInput) -> EvaluatorOutput:
    # ... 读取字段 ...
    
    # ✅ 直接构建契约，不经过 NodeExecutionContext
    contract = self.contract_builder.build_evaluator_contract_from_input(
        agent_input,
        deliverable_body=deliverable_body,
    )
    
    prompt = self.contract_builder.render_evaluator_prompt(contract)
    # ...
```

### 3.3 ContractBuilder 渲染修改

确保渲染时包含原始上下文：

```python
def render_evaluator_prompt(self, contract: EvaluatorPromptContract) -> str:
    """渲染 Evaluator 的完整 prompt."""
    sections = []
    
    # ✅ 添加原始上下文部分
    if contract.original_context_summary:
        sections.append("## 原始任务上下文")
        sections.append(contract.original_context_summary)
        sections.append("")
    
    sections.append("## 任务")
    sections.append(f"名称: {contract.task_name}")
    sections.append(f"描述: {contract.task_description}")
    sections.append("")
    
    sections.append("## 交付物")
    sections.append(contract.deliverable_body)
    sections.append("")
    
    sections.append("## 评审标准")
    for criterion in contract.criteria:
        sections.append(f"- {criterion['name']}: {criterion['description']} (权重: {criterion['weight']})")
    
    return "\n".join(sections)
```

---

## 4. 测试建议

### 4.1 Prompt 内容快照测试

```python
def test_evaluator_prompt_contains_original_context():
    """验证 Evaluator 的 prompt 包含原始上下文."""
    agent_input = EvaluatorAgentInput(
        task_name="分析需求",
        task_description="分析业务需求并产出文档",
        original_context_summary="原始业务需求：构建一个电商平台，支持B2B交易",
        deliverable_artifact={"file_path": "/path/to/doc.md"},
        deliverable_body="# 需求分析文档\n\n内容...",
        criteria=[{"name": "完整性", "description": "覆盖所有需求", "weight": 0.5}],
    )
    
    # 构建契约
    contract = contract_builder.build_evaluator_contract_from_input(
        agent_input,
        deliverable_body=agent_input["deliverable_body"],
    )
    
    # 渲染 prompt
    prompt = contract_builder.render_evaluator_prompt(contract)
    
    # 验证包含原始上下文
    assert "原始业务需求" in prompt
    assert "构建一个电商平台" in prompt
    assert "B2B交易" in prompt
```

### 4.2 端到端契约测试

```python
async def test_evaluator_input_contract_preserved():
    """验证 EvaluatorAgentInput 的字段被完整传递到 prompt."""
    # 1. 创建包含原始上下文的 execution_context
    execution_context = NodeExecutionContext(
        # ...
        original_context={"content": "关键业务约束"},
        # ...
    )
    
    # 2. 构建 EvaluatorAgentInput
    agent_input = context_manager.build_evaluator_input(
        execution_context,
        deliverable={"file_path": "/tmp/test.md"},
    )
    
    # 3. 执行 EvaluatorAgent
    evaluator = EvaluatorAgent(config, session_manager)
    
    # 4. Mock _call_llm_with_prompt 捕获 prompt
    captured_prompt = None
    async def mock_call(prompt):
        nonlocal captured_prompt
        captured_prompt = prompt
        return [Message(role="assistant", content='{"verdict": "APPROVED"}')]
    
    evaluator._call_llm_with_prompt = mock_call
    
    # 5. 执行
    await evaluator.execute_with_input(agent_input)
    
    # 6. 验证 prompt 包含原始上下文
    assert "关键业务约束" in captured_prompt
```

### 4.3 字段映射测试

```python
def test_evaluator_agent_input_field_mapping():
    """验证所有 EvaluatorAgentInput 字段都有正确的消费点."""
    input_fields = [
        "task_name",
        "task_description", 
        "original_context_summary",  # 关键字段
        "deliverable_artifact",
        "deliverable_body",
        "criteria",
    ]
    
    for field in input_fields:
        # 验证 execute_with_input 中有对应的读取逻辑
        assert field in agent_input_access_patterns, f"字段 {field} 未被消费"
```

---

## 5. 代码修改清单

### 5.1 必须修复

- [ ] `autoBMAD/docuswarm/agents/evaluator.py:519-600`
  - 修改 `execute_with_input()` 读取 `original_context_summary`
  - 修改 NodeExecutionContext 构建，传递原始上下文

### 5.2 推荐改进

- [ ] `autoBMAD/docuswarm/prompts/contract_builder.py`
  - 新增 `build_evaluator_contract_from_input()` 方法
  - 修改 `render_evaluator_prompt()` 包含原始上下文部分

### 5.3 测试覆盖

- [ ] 创建 `test_evaluator_input_contract.py`
  - Prompt 内容快照测试
  - 端到端字段传递测试
  - 字段映射完整性测试

---

## 6. 结论

1. **ContextManager 已正确构建 EvaluatorAgentInput**，问题在 EvaluatorAgent 的消费层
2. **修复简单但关键**，只需确保原始上下文摘要被正确传递到 prompt
3. **Prompt 内容测试是质量保障的关键**，确保评审质量不受损
4. **建议采用方案 B**（直接契约传递），避免不必要的中间转换

---

## 附录: 契约对比图

### 修复前（削弱契约）

```
EvaluatorAgentInput                    NodeExecutionContext
┌─────────────────────────┐            ┌─────────────────────────┐
│ task_name               │───────────▶│ task_name               │
│ task_description        │───────────▶│ task_description        │
│ original_context_summary│────╳──────▶│ original_context = {}   │  ❌ 丢失
│ deliverable_artifact    │───────────▶│ (未使用)                 │
│ deliverable_body        │───────────▶│ (单独传递)               │
│ criteria                │───────────▶│ evaluator_criteria      │
└─────────────────────────┘            └─────────────────────────┘
```

### 修复后（完整契约）

```
EvaluatorAgentInput                    NodeExecutionContext/Prompt
┌─────────────────────────┐            ┌─────────────────────────┐
│ task_name               │───────────▶│ task_name               │
│ task_description        │───────────▶│ task_description        │
│ original_context_summary│───────────▶│ original_context        │  ✅ 保留
│ deliverable_artifact    │───────────▶│ (按需使用)               │
│ deliverable_body        │───────────▶│ deliverable_body        │
│ criteria                │───────────▶│ criteria                │
└─────────────────────────┘            └─────────────────────────┘
```
