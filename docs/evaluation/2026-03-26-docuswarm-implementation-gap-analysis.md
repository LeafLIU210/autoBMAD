# DocuSwarm 实现差距分析报告

**日期**: 2026-03-26  
**分析基础**: @docs/evaluation/2026-03-26-docuswarm-unified-context-system-analysis.md  
**分析范围**: autoBMAD.docuswarm 模块  
**配套深度分析**: [@docs/evaluation/2026-03-26-docuswarm-deep-architecture-analysis.md](./2026-03-26-docuswarm-deep-architecture-analysis.md)

---

## 执行摘要

本报告基于统一上下文体系分析文档，对 autoBMAD.docuswarm 的实际实现与 @docs/epics 中定义的需求进行差距分析。发现多项 EPIC 要求尚未完全实现，同时某些设计原则已得到良好贯彻。

**配套文档**：[深度架构分析](./2026-03-26-docuswarm-deep-architecture-analysis.md) 深入探讨了 5 个关键架构决策：
1. Context Validator 提取重构的必要性
2. MemoryManager 的意义评估
3. Task 任务契约的存废分析（奥卡姆剃刀）
4. 节点 Agent 文档读取能力评估
5. Evaluator Agent 上下文选择

---

## 1. 未实现的文档要求

### 1.1 EPIC-15: Context Resolver（@路径注入）— **完全未实现**

| 要求项 | 状态 | 说明 |
|--------|------|------|
| `utils/context_resolver.py` | ❌ 不存在 | 基础文件缺失 |
| `@docs/` 路径解析 | ❌ 未实现 | 无法引用 docs 目录文件 |
| `@./` 相对路径解析 | ❌ 未实现 | 无法引用 context_file 相对路径 |
| 路径遍历防护 | ❌ 未实现 | 无安全校验 |
| `ContextSummarizer` | ❌ 未实现 | 无法自动生成文档摘要 |
| Orchestrator 集成 | ❌ 未实现 | 引用文档摘要不自动注入 PipelineState |

**影响**: 用户无法在 context 文件中使用 `@` 语法引用其他文档，限制了大项目的上下文管理能力。

**深度分析**: 见 [第4节：节点 Agent 文档读取能力评估](./2026-03-26-docuswarm-deep-architecture-analysis.md#4-节点-agent-文档读取能力评估)

### 1.2 EPIC-13: Context Validator 提取重构 — **部分未实现**

| 要求项 | 状态 | 说明 |
|--------|------|------|
| `pipeline/context_validator.py` | ❌ 不存在 | 独立组件未提取 |
| `ValidationResult` 数据类 | ❌ 未定义 | 结构化结果缺失 |
| 结构化重试逻辑 | ❌ 未实现 | Orchestrator 仍为 fail-open |
| Orchestrator 移除 `_validate_context` | ❌ 未移除 | 方法仍在 orchestrator.py 第262-345行 |
| fail_open/fail_close 策略 | ❌ 未实现 | 无法配置验证失败策略 |

**当前状态**: Orchestrator 仍内联包含约 80 行验证逻辑，未达到单一职责分离。

**深度分析**: 见 [第1节：Context Validator 提取重构的必要性](./2026-03-26-docuswarm-deep-architecture-analysis.md#1-context-validator-提取重构的必要性)

### 1.3 EPIC-04: 上下文隔离 — **部分实现，MemoryManager 评估建议延迟启用**

| 要求项 | 状态 | 说明 |
|--------|------|------|
| ContextManager | ✅ 已实现 | `context/isolation.py` 完整实现 |
| ContextFilter | ✅ 已实现 | `context/filter.py` 完整实现 |
| IsolationAuditLogger | ✅ 已实现 | `context/audit.py` 完整实现 |
| **MemoryManager** | ⚠️ **未启用** | 代码存在但未在 DualAgentNode 中集成 |
| 三层隔离集成 | ⚠️ **部分实现** | Layer 1/2/3 实现，但 Memory Scope 隔离未启用 |

**深度分析**: 见 [第2节：MemoryManager 的意义评估](./2026-03-26-docuswarm-deep-architecture-analysis.md#2-memorymanager-的意义评估)

**建议**: 基于奥卡姆剃刀原则，建议**延迟启用** MemoryManager。当前 `PipelineState.shared_context` 已能满足跨节点共享需求，增加三层内存模型会增加复杂度却无即时收益。

### 1.4 EPIC-03: 节点配置 — **Schema 已更新，建议移除冗余 Task 契约**

| 要求项 | 状态 | 说明 |
|--------|------|------|
| NodeConfig dataclass | ✅ 已实现 | `nodes/loader.py` 第26-76行 |
| task 部分支持 | ✅ 已实现 | `task` 字段已添加到 NodeConfig |
| deliverable 部分支持 | ✅ 已实现 | `deliverable` 字段已添加 |
| 旧字段兼容 | ✅ 已兼容 | `name`, `description` 仍支持 |

**深度分析**: 见 [第3节：Task 任务契约的存废分析](./2026-03-26-docuswarm-deep-architecture-analysis.md#3-task-任务契约的存废分析)

**建议**: 基于奥卡姆剃刀原则和单一职责原则，建议**移除 Task 契约**。节点职责可通过 `node_id` 推导，task_name/task_description/role_supplement 与 node_name/persona 存在重复。

---

## 2. `task` 的定义和设计目的

### 2.1 定义

`task` 是 **NodeExecutionContext** 中的**任务契约**分组，包含三个字段：

| 字段 | 来源 | 说明 |
|------|------|------|
| `task_name` | `node.yaml` `task.name` | 任务名称，回退到 `node_name` |
| `task_description` | `node.yaml` `description` | 任务描述，新 schema 中为 `task.description` |
| `role_supplement` | `node.yaml` `task.role_supplement` | 角色补充说明 |

**代码实现** (`context_builder.py` 第61-64行):
```python
# 任务契约 - 从 task 部分读取
task_name=node_config.task.get("name", node_config.name),
task_description=node_config.description or node_config.task.get("description", ""),
role_supplement=node_config.task.get("role_supplement", ""),
```

### 2.2 设计目的和理念

**核心理念**: **单一职责分离与契约明确化**

```
┌─────────────────────────────────────────────────────────────┐
│                    设计目标                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 消除歧义                                                │
│     - 旧设计：node.name 既是节点名又是任务名                  │
│     - 新设计：task_name 专门描述"做什么"                     │
│                                                             │
│  2. 分离契约类型                                            │
│     ┌─────────────────┐  ┌─────────────────────┐           │
│     │   任务契约       │  │     交付物契约       │           │
│     │   task_*        │  │  deliverable_*      │           │
│     │   (做什么)       │  │   (产出什么)         │           │
│     └─────────────────┘  └─────────────────────┘           │
│                                                             │
│  3. 避免与 subject_context 重复                             │
│     - task 描述节点职责（不变）                              │
│     - subject_context 描述具体项目（每次运行不同）            │
│                                                             │
│  4. 支持角色精细化                                          │
│     - role_supplement 允许为特定节点补充角色说明             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 奥卡姆剃刀：建议移除 Task 契约

**分析结论**：每个节点应该只执行一个明确的任务，task 契约是冗余的。

```
节点职责矩阵（单一职责）：

┌─────────────┬─────────────────────────────┬─────────────────────────────┐
│   节点      │       职责 (单一)            │        Task 契约冗余度       │
├─────────────┼─────────────────────────────┼─────────────────────────────┤
│ analyst     │ 分析需求，产出 Product Brief │ task_name: create-product-   │
│             │                             │ brief → 与节点职责完全相同   │
├─────────────┼─────────────────────────────┼─────────────────────────────┤
│ pm          │ 定义产品需求，产出 PRD        │ task_name: create-prd →      │
│             │                             │ 与节点职责完全相同           │
├─────────────┼─────────────────────────────┼─────────────────────────────┤
│ ux          │ 设计用户体验                  │ task_name: create-ux-design  │
│             │                             │ → 与节点职责完全相同         │
├─────────────┼─────────────────────────────┼─────────────────────────────┤
│ architect   │ 设计系统架构                  │ task_name: create-arch-doc   │
│             │                             │ → 与节点职责完全相同         │
├─────────────┼─────────────────────────────┼─────────────────────────────┤
│ po          │ 拆分用户故事                  │ task_name: create-epics-     │
│             │                             │ stories → 与节点职责相同     │
└─────────────┴─────────────────────────────┴─────────────────────────────┘
```

**建议**：
- `task_name` → 使用 `node_id` 推导
- `task_description` → 使用 `persona.identity` 或从 node_id 推导
- `role_supplement` → 合并到 `persona.role`

---

## 3. 节点交付物以什么形式进入主体上下文

### 3.1 数据流概述

```
用户 context file (任意格式文本)
        │
        ▼
PipelineService.start()
  subject_context = {subject, context_file, content}
        │
        ▼
HybridOrchestrator → LangGraph PipelineState
        │
        ▼ (每个节点)
executor._execute_node()
  _parse_original_context() → original_context: dict
  NodeExecutionContextBuilder.build() → NodeExecutionContext
        │
        ▼
DualAgentNode.execute_with_context()
        │
        ├─ ContextManager.build_independent_input()
        │         → IndependentAgentInput
        │                   │
        │                   ▼
        │       IndependentAgent.execute_with_input()
        │
        └─ ContextManager.build_evaluator_input()
                  → EvaluatorAgentInput
                            │
                            ▼
                    EvaluatorAgent.execute_with_input()
```

### 3.2 交付物传递形式

**上游交付物以摘要形式注入，非全文**:

| 层级 | 字段名 | 内容形式 | 示例 |
|------|--------|----------|------|
| `NodeExecutionContext` | `chained_deliverables` | 完整交付物列表 | `[{node_id, deliverable}, ...]` |
| `IndependentAgentInput` | `chained_deliverables_summary` | 截断摘要（200字符） | `[{node_id, title, summary[:200]}]` |
| `EvaluatorAgentInput` | ❌ 无此字段 | 完全隔离 | 无法访问上游交付物 |

**代码实现** (`isolation.py` 第91-100行):
```python
# 构建上游交付物摘要
chained_summary: list[dict[str, Any]] = []
for item in execution_context["chained_deliverables"]:
    deliverable = item.get("deliverable", {})
    chained_summary.append(
        {
            "node_id": item.get("node_id"),
            "title": deliverable.get("title", "Untitled"),
            "summary": deliverable.get("summary", "")[:200],  # P0-3: Use summary
        }
    )
```

### 3.3 各节点 chained_deliverables_summary 内容

| 节点 | 包含的上游交付物 |
|------|------------------|
| `analyst` | `[]`（首节点，无上游） |
| `pm` | `[analyst]` |
| `ux` | `[analyst, pm]` |
| `architect` | `[analyst, pm, ux]` |
| `po` | `[analyst, pm, ux, architect]` |

---

## 4. 节点的两个 Agent 都会更新主体上下文吗？

### 4.1 答案：**否**

只有 **Independent Agent** 能更新主体上下文，**Evaluator Agent 是只读的**。

### 4.2 更新机制对比

| 方面 | Independent Agent | Evaluator Agent |
|------|-------------------|-----------------|
| **写入 shared_context** | ✅ 可以 | ❌ 不可以 |
| **访问 chained_deliverables** | ✅ 可以（摘要） | ❌ 不可以 |
| **访问 iteration_feedback** | ✅ 可以 | ❌ 不可以 |
| **访问 private_reasoning** | ✅ 可以（自己生成） | ❌ 不可以（被隔离） |

### 4.3 三层隔离架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   Three-Layer Context Isolation                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LAYER 1 — 提示模板隔离 (Prompt Separation)                                  │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Independent Prompt        Evaluator Prompt                           │ │
│  │  ├── BMAD Persona          ├── Evaluation Role                        │ │
│  │  ├── Creation Task         ├── Criteria List                          │ │
│  │  ├── Chained Deliverables  ├── Deliverable Body ONLY                  │ │
│  │  └── shared_context ✓      └── NO shared_context ✗                    │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  LAYER 2 — 运行时访问控制 (ContextManager)                                   │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  build_independent_input()         build_evaluator_input()            │ │
│  │  ├── original_context_summary ✓    ├── original_context_summary ✓    │ │
│  │  ├── chained_deliverables_summary ✓├── deliverable_artifact ✓       │ │
│  │  ├── shared_context ✓              ├── deliverable_body ✓            │ │
│  │  └── iteration_feedback ✓          └── NO shared_context ✗           │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  LAYER 3 — 消息级过滤 (ContextFilter)                                        │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Independent Output → Filter → Evaluator Input                        │ │
│  │  ├── deliverable ✓              ├── deliverable ✓                    │ │
│  │  ├── questions ✓                ├── questions ✓                      │ │
│  │  ├── private_reasoning ✗ REMOVED                                       │ │
│  │  └── tool_call_history ✗ REMOVED                                       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  AUDIT LAYER — 审计日志 (IsolationAuditLogger)                               │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  ├── Log all context builds                                           │ │
│  │  ├── Log all filtering operations                                     │ │
│  │  └── Log potential violations                                         │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.4 Independent Agent 如何更新 shared_context

**代码位置** (`independent.py` 第620-708行):
```python
async def execute_with_input(self, agent_input: IndependentAgentInput, ...):
    # 读取 shared_context
    shared_context = agent_input.get("shared_context", {})
    
    # 在 contract 构建时传递 shared_context
    context = NodeExecutionContext(
        ...
        shared_context=shared_context,  # P1-1: 传递 shared_context
        ...
    )
    
    # Agent 可以通过 update_context tool 更新 shared_context
    # 更新后的 shared_context 会流向下一个节点
```

### 4.5 shared_context 的持久化流程

```
Node A (analyst)
  │
  ├─ IndependentAgent 执行
  │   ├─ 读取 shared_context = {}
  │   └─ 写入 shared_context["analyst_insights"] = "..."
  │
  └─ PipelineState.shared_context = {"analyst_insights": "..."}
            │
            ▼
Node B (pm)
  │
  ├─ IndependentAgent 执行
  │   ├─ 读取 shared_context = {"analyst_insights": "..."}
  │   └─ 写入 shared_context["pm_decisions"] = "..."
  │
  └─ PipelineState.shared_context = {
       "analyst_insights": "...",
       "pm_decisions": "..."
     }
```

---

## 5. EvaluatorAgentInput 没有读取主体上下文，能做好评估工作吗？

### 5.1 前提澄清：**Evaluator 确实读取了原始上下文**

根据代码分析，**EvaluatorAgentInput 包含 `original_context_summary` 字段**，这是 P0-2 原则的强制要求。

**代码证据** (`isolation.py` 第153-163行):
```python
def build_evaluator_input(...):
    # P0-2: Extract original context summary
    original_context = execution_context.get("original_context", {})
    original_summary = _extract_original_context_summary(original_context)

    return EvaluatorAgentInput(
        task_name=execution_context["task_name"],
        task_description=execution_context["task_description"],
        original_context_summary=original_summary,  # P0-2: 原始需求摘要
        deliverable_artifact=deliverable,
        deliverable_body=deliverable_body,
        criteria=execution_context.get("evaluator_criteria", []),
    )
```

### 5.2 Evaluator 的输入组成

| 字段 | 内容 | 用途 |
|------|------|------|
| `task_name` | 任务名 | 理解节点职责 |
| `task_description` | 任务描述 | 理解期望产出 |
| `original_context_summary` | 原始需求摘要 | **对照需求评审** |
| `deliverable_artifact` | 交付物元数据 | 获取文件路径、SHA256 |
| `deliverable_body` | 交付物全文（从磁盘读取） | **评审主要内容** |
| `criteria` | 评审标准列表 | 评分依据 |

### 5.3 评估能力分析

**Evaluator 能够做好评估工作，原因如下**：

#### 5.3.1 核心评估要素已具备

```
Evaluator 评审三角:

        原始需求 (original_context_summary)
                    /\
                   /  \
                  /    \
                 /      \
                /   ?    \
               /          \
              /____________\
    交付物正文    ←→    评审标准
(deliverable_body)    (criteria)
```

- ✅ **原始需求**: 知道"应该做什么"
- ✅ **交付物正文**: 知道"实际做了什么"
- ✅ **评审标准**: 知道"如何评判"

#### 5.3.2 设计哲学：评审客观性

**Evaluator 被有意设计为不访问以下信息**，以确保评估客观性：

| 被隔离的信息 | 隔离原因 |
|--------------|----------|
| `chained_deliverables` | 防止受上游风格影响，只评当前交付物 |
| `shared_context` | 防止受其他节点判断影响 |
| `iteration_feedback` | 防止累积偏见，每轮独立评审 |
| `private_reasoning` | 防止受作者思路影响，只看结果 |

### 5.4 结论

**Evaluator 能够做好评估工作**，因为：

1. **P0-2 原则保证**: `original_context_summary` 已传入 Evaluator
2. **P0-3 原则保证**: Evaluator 从磁盘读取完整交付物正文 (`deliverable_body`)
3. **客观性设计**: 刻意隔离非必要信息，确保评审公正
4. **反馈闭环**: Independent Agent 收到 feedback 后会改进，下轮 Evaluator 重新独立评审

**深度分析**: 见 [第5节：Evaluator Agent 上下文选择](./2026-03-26-docuswarm-deep-architecture-analysis.md#5-evaluator-agent-上下文选择)

---

## 6. 建议与行动项

### 高优先级（P0）

| 行动项 | 原因 | 建议方案 |
|--------|------|----------|
| 实现 Context Resolver | EPIC-15 完全未实现，影响大项目使用 | 按 US-15.1~15.7 逐步实现，采用混合策略（小文档预读 + 大文档按需读取） |
| 提取 Context Validator | EPIC-13 未完成，Orchestrator 职责过重 | 按 US-13.1~13.6 重构，支持 fail_open/close 策略 |

### 中优先级（P1）

| 行动项 | 原因 | 建议方案 |
|--------|------|----------|
| 移除 Task 契约 | 与 persona 重复，违反单一职责 | 简化 node.yaml，从 node_id 推导任务描述 |
| 添加 read_document 工具 | 支持按需读取大文档 | 在 independent_agent.yaml 中添加文件读取工具 |

### 低优先级（P2）

| 行动项 | 原因 | 建议方案 |
|--------|------|----------|
| 延迟启用 MemoryManager | 当前架构已满足需求 | 保留代码，文档说明预留用途 |
| 完善 Evaluator 上下文长度 | 原始上下文可能被截断 | 评估是否需要增加限制或分段注入 |

---

## 附录：关键决策汇总

| # | 决策 | 优先级 | 理由 | 深度分析链接 |
|---|------|--------|------|-------------|
| 1 | 提取 ContextValidator | P0 | 职责分离，提升可配置性 | [第1节](./2026-03-26-docuswarm-deep-architecture-analysis.md#1-context-validator-提取重构的必要性) |
| 2 | 延迟启用 MemoryManager | P2 | 避免过度设计 | [第2节](./2026-03-26-docuswarm-deep-architecture-analysis.md#2-memorymanager-的意义评估) |
| 3 | 移除 Task 契约 | P1 | 单一职责，消除重复 | [第3节](./2026-03-26-docuswarm-deep-architecture-analysis.md#3-task-任务契约的存废分析) |
| 4 | 添加 read_document 工具 | P1 | 支持按需读取大文档 | [第4节](./2026-03-26-docuswarm-deep-architecture-analysis.md#4-节点-agent-文档读取能力评估) |
| 5 | 保持 Evaluator 原始上下文 | - | 评审一致性和客观性 | [第5节](./2026-03-26-docuswarm-deep-architecture-analysis.md#5-evaluator-agent-上下文选择) |

### A.1 NodeExecutionContext 定义 (`contracts.py`)
```python
class NodeExecutionContext(NodeExecutionContextRequired, total=False):
    evaluator_criteria: list[dict[str, Any]]
```

### A.2 IndependentAgentInput 定义 (`contracts.py`)
```python
class IndependentAgentInput(TypedDict, total=False):
    task_name: str
    task_description: str
    role_supplement: str
    deliverable_requirements: DeliverableRequirements
    original_context_summary: str
    chained_deliverables_summary: list[dict[str, Any]]
    iteration_feedback: dict[str, Any] | None
    persona_context: dict[str, Any]
    shared_context: dict[str, Any]  # P1-1: 跨节点共享上下文
```

### A.3 EvaluatorAgentInput 定义 (`contracts.py`)
```python
class EvaluatorAgentInput(TypedDict, total=False):
    task_name: str
    task_description: str
    original_context_summary: str  # P0-2: 原始需求摘要
    deliverable_artifact: dict[str, Any]
    deliverable_body: str
    criteria: list[dict[str, Any]]
```

---

**报告完成**
