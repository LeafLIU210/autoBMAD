# BMM NodeExecutor 重构研究报告 Part 3: 双代理流程与状态管理分析

**文档编号**: BMM-Research-03
**日期**: 2026-03-02
**范围**: 双代理（Independent + Evaluator）创建-评估审查交付物流程、状态更新机制
**修订**: v2 - 确保双代理流程运行时零外部依赖

---

## 0. 核心约束

> **`autoBMAD/docuswarm` 运行时绝不引用 `_bmad` 或任何外部文件夹。**
>
> 双代理流程的所有输入（persona、task、evaluator criteria）均来自 `autoBMAD/nodes/{id}/` 内的自包含配置文件。

---

## 1. 双代理模式架构概览

### 1.1 当前架构

`DualAgentNode`（[dual_agent.py](autoBMAD/docuswarm/nodes/dual_agent.py)）实现 Independent + Evaluator 双代理模式：

```
┌──────────────────────────────────────────────────────────┐
│                  DualAgentNode.execute()                  │
│                                                            │
│  ┌───────────────┐  ┌────────────┐  ┌───────────────┐    │
│  │  Independent   │→│  Context    │→│  Evaluator    │    │
│  │  Agent         │  │  Filter     │  │  Agent        │    │
│  │ (创建交付物)    │  │ (过滤私密)   │  │ (评估交付物)   │    │
│  └───────────────┘  └────────────┘  └───────────────┘    │
│         ↑                                    │             │
│         │     ┌────────────────┐             │             │
│         └─────│  Feedback      │←────────────┘             │
│               │ (修订反馈)      │   NEEDS_REVISION          │
│               └────────────────┘                           │
│                                                            │
│  Verdicts: APPROVED | NEEDS_REVISION | BLOCKED             │
│            | FORCE_APPROVED                                │
│                                                            │
│  数据来源: 全部来自 autoBMAD/nodes/{id}/ (自包含)            │
└──────────────────────────────────────────────────────────┘
```

### 1.2 外部依赖审计

**双代理流程中的文件读取路径审计**：

| 组件 | 读取的文件 | 路径 | 是否引用 _bmad |
|------|-----------|------|---------------|
| PersonaLoader | persona.json | `autoBMAD/nodes/{id}/persona.json` | **否** |
| EvaluatorAgent._load_criteria | evaluator.yaml | `autoBMAD/nodes/{id}/evaluator.yaml` | **否** |
| NodeLoader.load | node.yaml | `autoBMAD/nodes/{id}/node.yaml` | **否** |
| IndependentAgent.execute | create_deliverable tool | 运行时生成 | **否** |
| ContextManager | PipelineState | 内存状态 | **否** |
| ContextFilter | 过滤规则 | 硬编码在代码中 | **否** |

**结论**: 双代理核心流程（DualAgentNode、IndependentAgent、EvaluatorAgent、ContextFilter）**当前无 `_bmad` 外部依赖**。所有外部依赖集中在配置文件内容层面（persona.json/node.yaml的内容不对齐），不在代码路径层面。

**唯一例外**: `autoBMAD/docuswarm/templates/*_templates.yaml` 中的 `standards.style_guide` 引用了 `_bmad/_memory/` 路径，但这些模板文件不被双代理流程直接使用（由待评估的templates子系统使用）。

---

## 2. 执行流程详细分析

### 2.1 Step 1: Independent Agent 执行

```python
# dual_agent.py
# 1. 构建Independent上下文
independent_context = self.context_manager.build_independent_context(
    subject_context={"subject": subject_context, "task": task},
    iteration_feedback=previous_feedback,
)
independent_context["pipeline_id"] = pipeline_id

# 2. 执行Independent Agent (system prompt来自persona.json + node.yaml)
independent_output = await self.independent_agent.execute(independent_context)

# 3. 提取deliverable和questions
final_deliverable = independent_output.get("deliverable", {})
final_questions = independent_output.get("questions", [])
```

**重构影响**:
- `self.independent_agent` 的system prompt将包含BMM角色上下文（来自重构后的persona.json）
- `task` 参数将基于 `node.yaml.task` 配置
- **执行逻辑不变**，仅输入内容变化

### 2.2 Step 2: Context Filter（上下文过滤）

```python
# ContextFilter过滤private_reasoning等私密字段
filtered_output = self.context_filter.filter_for_evaluator(independent_output)
```

- `ContextFilter.filter_for_evaluator()` 移除 `private_reasoning`, `tool_call_history`, `internal_notes`, `iteration_feedback`
- `IsolationAuditLogger` 记录所有过滤操作
- `ContextIsolationError` 在发现泄露时抛出
- **此部分无需任何改动**

### 2.3 Step 3: Evaluator Agent 执行

```python
# 1. 构建Evaluator上下文
evaluator_context = self.context_manager.build_evaluator_context(
    subject_context={"subject": subject_context},
    deliverable=filtered_output.get("deliverable"),
)

# 2. 执行Evaluator Agent (criteria来自evaluator.yaml)
evaluation = await self.evaluator_agent.execute(evaluator_context)

# evaluation 结构:
# {
#   "criterion_scores": {"criterion_name": float},
#   "alignment_score": float,  # 加权平均分 (0.0-1.0)
#   "verdict": "APPROVED" | "NEEDS_REVISION" | "BLOCKED",
#   "issues_found": [...],
#   "suggestions": [...]
# }
```

**重构影响**:
- `evaluator.yaml` 的评估标准描述文本微调（对齐实际交付物）
- 评估标准的权重和阈值保持不变
- **执行逻辑不变**

### 2.4 Step 4: Verdict 处理与迭代

```python
verdict = evaluation.get("verdict", "NEEDS_REVISION")

if verdict == "APPROVED":
    break  # 成功退出
elif verdict == "FORCE_APPROVED":
    final_force_completion = create_force_completion(...)
    break
elif verdict == "BLOCKED":
    break
else:  # NEEDS_REVISION
    previous_feedback = {
        "alignment_score": ...,
        "verdict": ...,
        "issues_found": [...],
        "suggestions": [...],
    }
    # 继续下一轮迭代
```

- 最大迭代次数默认3次（`DEFAULT_MAX_ITERATIONS = 3`）
- 反馈正确传递给下一轮IndependentAgent
- **此部分无需任何改动**

---

## 3. 状态更新机制分析

### 3.1 Pipeline State 结构

```python
class PipelineState(TypedDict):
    pipeline_id: str
    subject_context: dict[str, Any]
    current_node: str
    completed_nodes: list[str]
    deliverables: dict[str, dict[str, Any]]   # 各节点交付物
    questions: dict[str, list[dict[str, Any]]] # 各节点问题
    evaluations: dict[str, dict[str, Any]]     # 各节点评估
    node_iterations: dict[str, int]            # 各节点迭代次数
```

### 3.2 状态更新链路（pipeline/graph.py → executor.py）

```python
# _create_integrated_node_executor 中
# PipelineState → NodeRunState 转换
node_state = _convert_pipeline_to_node_state(state, node_id)

# 执行节点
result_state = await executor(node_state)

# NodeRunState → PipelineState 更新
new_state["deliverables"][node_id] = result_state["deliverable"]
new_state["questions"][node_id] = result_state["questions"]
new_state["evaluations"][node_id] = result_state["evaluation"]
new_state["node_iterations"][node_id] = result_state["iteration"]

# 基于verdict更新completed_nodes
verdict = result_state["evaluation"].get("verdict")
if verdict in ("APPROVED", "FORCE_APPROVED"):
    new_state["completed_nodes"].append(node_id)
```

### 3.3 状态更新正确性验证

| 检查点 | 状态 | 说明 |
|--------|------|------|
| deliverables[node_id] 更新 | **正确** | 存储IndependentAgent输出的deliverable |
| questions[node_id] 更新 | **正确** | 存储IndependentAgent输出的questions |
| evaluations[node_id] 更新 | **正确** | 存储EvaluatorAgent的evaluation |
| node_iterations 累积 | **正确** | 从NodeRunState.iteration获取 |
| completed_nodes 追加 | **正确** | 仅在APPROVED/FORCE_APPROVED时 |
| deep copy 防mutation | **正确** | `copy.deepcopy(state)` |
| status 状态转换 | **正确** | RUNNING→COMPLETED/BLOCKED/FAILED |

---

## 4. 重构对双代理流程的影响矩阵

### 4.1 不受影响的组件（无需改动）

| 组件 | 位置 | 理由 |
|------|------|------|
| `ContextManager` | nodes/dual_agent.py | 上下文构建逻辑不变 |
| `ContextFilter` | nodes/dual_agent.py | 过滤规则不变 |
| `IsolationAuditLogger` | nodes/dual_agent.py | 审计逻辑不变 |
| `IterationController` | nodes/dual_agent.py | 迭代控制逻辑不变 |
| `VerdictDeterminer` | nodes/dual_agent.py | 裁决阈值逻辑不变 |
| `ForceCompletion` | nodes/dual_agent.py | 强制完成记录不变 |
| `EscalationHandler` | nodes/dual_agent.py | 升级处理不变 |
| `MetricsCollector` | nodes/dual_agent.py | 指标收集不变 |
| `QualityConfig` | nodes/dual_agent.py | 质量配置不变 |
| `PipelineState` 更新 | pipeline/graph.py | 状态更新逻辑不变 |
| `NodeRunState` | node_execution/state.py | 单节点状态不变 |

### 4.2 需要调整的组件

| 组件 | 变更内容 | 数据来源 | 是否引用 _bmad |
|------|----------|----------|---------------|
| `IndependentAgent._format_system_prompt()` | 使用BMM角色上下文 + task说明 | persona.json + node.yaml | **否** |
| `PersonaLoader.load()` | 加载扩展后的persona.json（含communication_style） | `autoBMAD/nodes/{id}/persona.json` | **否** |
| `Persona` dataclass | 新增communication_style字段 | persona.json | **否** |
| `NodeLoader.load()` | 新增加载task配置 | node.yaml | **否** |
| `NodeConfig` dataclass | 新增NodeTaskConfig字段 | node.yaml | **否** |
| `EvaluatorAgent._format_evaluation_prompt()` | 评估标准描述微调 | evaluator.yaml | **否** |

**所有调整的数据来源均在 `autoBMAD/` 内，运行时零外部依赖。**

### 4.3 数据流变更

**重构前**:
```
PipelineState.subject_context 
  → _execute_node() 
    → DualAgentNode.execute()
      → IndependentAgent: 通用persona + 通用task → 通用deliverable
      → EvaluatorAgent: 通用criteria → verdict
```

**重构后**:
```
PipelineState.subject_context 
  → _execute_node() 
    → NodeLoader.load() → 从 autoBMAD/nodes/{id}/ 加载BMM aligned配置
    → DualAgentNode.execute()
      → IndependentAgent: BMM persona(从persona.json) + BMM task(从node.yaml) → BMM aligned deliverable
      → EvaluatorAgent: BMM aligned criteria(从evaluator.yaml) → verdict
```

**关键**: 数据流中的配置加载层变化，但DualAgentNode的**内部执行流程不变**。

---

## 5. 双代理循环完整性检查

### 5.1 创建-评估循环

| 检查点 | 当前状态 | 重构影响 |
|--------|---------|----------|
| Independent Agent 生成 deliverable | 正确 | persona/task变化，输出结构不变 |
| private_reasoning 过滤 | 正确 | 无影响 |
| Evaluator Agent 评估 deliverable | 正确 | 评估标准描述微调 |
| NEEDS_REVISION 反馈传递 | 正确 | 无影响 |
| APPROVED 退出循环 | 正确 | 无影响 |
| FORCE_APPROVED 创建记录 | 正确 | 无影响 |
| BLOCKED 升级处理 | 正确 | 无影响 |
| 最大迭代限制 (default=3) | 正确 | 无影响 |

### 5.2 错误处理完整性

| 异常 | 当前处理 | 重构影响 |
|------|---------|----------|
| `IndependentExecutionError` | catch + re-raise | 无影响 |
| `EvaluatorExecutionError` | catch + re-raise | 无影响 |
| `ContextIsolationError` | catch + audit log + re-raise | 无影响 |
| `EscalationError` | BLOCKED时触发 | 无影响 |
| `PersonaLoadError` | 加载persona失败 | **需注意**: 新persona.json字段验证 |
| `CriteriaLoadError` | 加载evaluator.yaml失败 | 无影响 |

---

## 6. 需确保的前置条件

### 6.1 persona.json 格式兼容性

重构后的persona.json新增了 `communication_style` 字段。需确保：

1. `PersonaLoader.load()` 能处理新字段
2. `Persona` dataclass 新增 `communication_style: str = ""`（带默认值，向后兼容）
3. 旧格式persona.json（无communication_style）不会导致加载失败

### 6.2 node.yaml 格式兼容性

重构后的node.yaml新增了 `task` 块。需确保：

1. `NodeLoader.load()` 能处理新的 `task` 块
2. `NodeConfig` dataclass 新增 `task: NodeTaskConfig | None = None`（可选，向后兼容）
3. 移除 `questions`/`dependencies` 后 `_validate()` 不再验证这些字段

### 6.3 evaluator.yaml 格式不变

evaluator.yaml 的结构不变（criteria列表 + thresholds），仅修改描述文本。无兼容性风险。

---

## 7. 结论

双代理流程（Independent Agent → Context Filter → Evaluator Agent → Verdict Loop）的**核心执行逻辑设计合理且完整**。

重构影响**集中在两个层面**：
1. **配置内容层**: persona.json和node.yaml的内容对齐BMM（预处理嵌入）
2. **Prompt构建层**: IndependentAgent的system prompt使用BMM角色上下文和任务说明

**重构不影响**：
- 迭代循环逻辑
- 上下文隔离安全机制
- 裁决阈值和评分计算
- 状态更新（PipelineState和NodeRunState）
- 错误处理链路

**外部依赖审计结论**: 双代理流程当前**无 `_bmad` 运行时依赖**。重构后仍保持零外部依赖，所有配置数据均来自 `autoBMAD/nodes/{id}/` 目录。


---

## 8. 解决方案文档

本文档的研究结果（双代理流程执行、状态管理）已转化为测试驱动的实施方案：

| 方案文档 | 内容 | 位置 |
|----------|------|------|
| **TDD-BMM-04** | 双代理流程集成与端到端测试 | [`docs/solution/TDD-BMM-04-DualAgent-Integration-E2E.md`](../solution/TDD-BMM-04-DualAgent-Integration-E2E.md) |
| **TDD-BMM-05** | BMM NodeExecutor 重构主实施指南 | [`docs/solution/TDD-BMM-05-Master-Implementation-Guide.md`](../solution/TDD-BMM-05-Master-Implementation-Guide.md) |

**架构文档更新**:
- [`docs/architecture/02_AGENT_ARCHITECTURE.md`](../architecture/02_AGENT_ARCHITECTURE.md) - Agent架构 (v5.1)
- [`docs/architecture/03_PIPELINE_ARCHITECTURE.md`](../architecture/03_PIPELINE_ARCHITECTURE.md) - 节点执行架构 (v2.3)

---

**文档结束**
