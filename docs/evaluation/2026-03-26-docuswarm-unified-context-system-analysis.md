# DocuSwarm 统一上下文体系全解析报告

**日期**: 2026-03-26  
**类型**: 架构分析报告  
**主题**: DocuSwarm Single Context Protocol — 从 context file 到 Agent 输入的完整数据流

---

## 1. 概述

DocuSwarm 的上下文体系以 **Single Context Protocol** 为核心设计原则，通过 `NodeExecutionContext` 这一统一结构承载跨越 executor → DualAgentNode → IndependentAgent/EvaluatorAgent 全链路的数据传递。本报告记录该体系的完整组成、构建流程、以及各节点阶段的上下文差异。

> **注意**：EPIC-15 设计的 `ContextResolver` 与 `ResolvedContext`（含 `@` 路径引用展开能力）尚未实现，`utils/context_resolver.py` 文件不存在。当前 context file 以原始全文字符串传递，`@` 引用不会自动展开。

---

## 2. Context File 读取流程

### 2.1 CLI 入口

用户通过以下命令启动流水线：

```bash
python -m autoBMAD.docuswarm start --context <file>
```

### 2.2 读取链路

```
start.py (Click命令)
  └─ PipelineService.start(context_file)
       └─ context_path.read_text(encoding="utf-8")   # 直接读取原始文本
            └─ subject_context = {
                   "subject":      context_path.stem,      # 文件名（无扩展名）
                   "context_file": str(context_path),      # 绝对路径
                   "content":      content,                # 全文字符串
               }
                    └─ HybridOrchestrator.start_pipeline(subject_context)
```

context file 内容以**纯文本字符串**整体读取，不做任何结构化解析，直接打包进 `subject_context["content"]`。

### 2.3 格式说明

context file 支持任意文本格式（Markdown、JSON、纯文本）。若为 JSON，executor 层会尝试 `json.loads()` 解析；若解析失败，则回退为 `{"content": <原始文本>}`。

---

## 3. PipelineState：流水线状态结构

`HybridOrchestrator` 将 `subject_context` 传入 LangGraph，构建初始 `PipelineState`：

```python
PipelineState = {
    pipeline_id:            str,              # 流水线唯一ID
    subject_context:        dict[str, Any],   # 用户输入（subject, context_file, content）
    current_node:           str | None,       # 当前执行节点
    completed_nodes:        list[str],        # 已完成节点列表
    deliverables:           dict[str, dict],  # 各节点交付物（元数据）
    questions:              dict[str, list],  # 各节点生成的问题
    evaluations:            dict[str, dict],  # 各节点评审结果
    node_iterations:        dict[str, int],   # 各节点迭代次数
    session_ids:            dict[str, str],   # 各节点的 SDK Session ID
    session_metadata:       dict[str, dict],  # Session 元数据（用于恢复）
    current_node_session_id: str | None,      # 当前执行节点的 Session ID
    status:                 str,              # pending/running/completed/failed/paused/cancelled
    error:                  dict | None,      # 错误信息
    shared_context:         dict[str, Any],   # 跨节点共享上下文（可写入）
}
```

流水线节点顺序固定为：`analyst → pm → ux → architect → po`

---

## 4. NodeExecutionContext：统一节点执行上下文

### 4.1 完整字段定义

`NodeExecutionContext` 是贯穿所有层的核心结构，由 `NodeExecutionContextBuilder.build()` 在每个节点执行前构建：

| 分组 | 字段 | 类型 | 来源 |
|---|---|---|---|
| **身份标识** | `pipeline_id` | `str` | 运行时生成 |
| | `node_id` | `str` | 节点配置（如 `analyst`） |
| | `node_name` | `str` | `node.yaml` 中的 `name` |
| | `node_order` | `int` | `node.yaml` 中的 `sequence` |
| **任务契约** | `task_name` | `str` | `node.yaml` `task.name` |
| | `task_description` | `str` | `node.yaml` `description` |
| | `role_supplement` | `str` | `node.yaml` `task.role_supplement` |
| **交付物契约** | `deliverable_type` | `str` | `node.yaml` |
| | `deliverable_requirements` | `DeliverableRequirements` | 含 `required_sections`、`template_title`、`output_filename`、`format_hints` |
| **上下文数据** | `original_context` | `dict[str, Any]` | 用户 context file 解析后的 dict，含 `content` 字段 |
| | `chained_deliverables` | `list[dict]` | 上游节点已完成的交付物列表 |
| | `shared_context` | `dict[str, Any]` | `PipelineState.shared_context`（跨节点共享可写） |
| **迭代状态** | `iteration_feedback` | `dict | None` | 上一轮 Evaluator 的反馈（含 `verdict`、`issues_found`、`suggestions`） |
| **扩展上下文** | `docs_context` | `list[dict]` | 固定为 `[]`（已停用） |
| **可选** | `evaluator_criteria` | `list[dict]` | `node.yaml` `evaluator.criteria` |

### 4.2 构建逻辑

```python
# executor._execute_node() 中
original_context = _parse_original_context(state.get("context_file", ""))
# 解析优先级：文件路径 → JSON字符串 → 纯文本回退

execution_context = context_builder.build(
    pipeline_id=pipeline_id,
    node_id=node_id,
    original_context=original_context,
    chained_deliverables=_extract_chained_deliverables(state),  # 从 chained_context 提取
    shared_context=state.get("shared_context", {}),
)
```

`_parse_original_context()` 的三路解析策略：
1. 若参数是有效文件路径 → 读取文件内容
2. 尝试 `json.loads()` → 成功则标准化为 dict
3. 失败则回退为 `{"content": <原始文本>}`

---

## 5. 三层上下文隔离架构

DocuSwarm 通过三层机制确保 IndependentAgent 与 EvaluatorAgent 之间的信息隔离：

```
Layer 1 — 提示模板隔离 (Prompt Separation)
  Independent 和 Evaluator 使用完全不同的 .yaml 提示模板

Layer 2 — 运行时访问控制 (ContextManager)
  ContextManager.build_independent_input()  →  IndependentAgentInput
  ContextManager.build_evaluator_input()    →  EvaluatorAgentInput
  Evaluator 不得访问：chained_deliverables / shared_context / iteration_feedback

Layer 3 — 消息级过滤 (ContextFilter)
  移除字段：private_reasoning / tool_call_history / internal_notes / iteration_feedback
  移除标记：[PRIVATE] / [/PRIVATE] / [INTERNAL] / <!-- PRIVATE --> 等
```

---

## 6. IndependentAgentInput：Independent Agent 的上下文

### 6.1 字段组成

由 `ContextManager.build_independent_input()` 从 `NodeExecutionContext` 裁剪：

| 字段 | 内容 | 来源字段 |
|---|---|---|
| `task_name` | 任务名 | `task_name` |
| `task_description` | 任务描述 | `task_description` |
| `role_supplement` | 角色补充说明 | `role_supplement` |
| `deliverable_requirements` | 交付物要求（章节、格式等） | `deliverable_requirements` |
| `original_context_summary` | 原始上下文摘要字符串 | `original_context["content"]` 提取 |
| `chained_deliverables_summary` | 上游交付物摘要（**截断至 200 字符**） | `chained_deliverables` 中每项的 `title` + `summary[:200]` |
| `iteration_feedback` | 迭代反馈（可选，仅修订轮有） | 传入参数，来自上轮 Evaluator |
| `persona_context` | Persona 上下文 | `{}` — 由 IndependentAgent 自行加载 |
| `shared_context` | 跨节点共享上下文 | `shared_context` |

### 6.2 注入 LLM 提示的格式

IndependentAgent 将结构化输入组装为 enriched_task：

```
## Original Context

{original_context_summary}

## Task

{task_description}

Please create the deliverable based on the original context above.
Reference specific details from the context in your analysis.
```

若存在 `iteration_feedback`（修订轮），在 task 末尾追加：

```
## Previous Feedback

The previous attempt received the following feedback:

**Verdict**: NEEDS_REVISION
**Alignment Score**: 0.65

**Issues Found**:
- 缺少风险分析
- ...

**Suggestions**:
- 补充第3节
- ...

Please address these issues in your revised deliverable.
```

---

## 7. EvaluatorAgentInput：Evaluator Agent 的上下文（严格隔离）

### 7.1 字段组成

由 `ContextManager.build_evaluator_input()` 构建，强制从磁盘读取交付物正文（**P0-3 原则**）：

| 字段 | 内容 | 来源 |
|---|---|---|
| `task_name` | 任务名 | `NodeExecutionContext.task_name` |
| `task_description` | 任务描述 | `NodeExecutionContext.task_description` |
| `original_context_summary` | 原始需求摘要（**P0-2 修复**） | `original_context` 提取 |
| `deliverable_artifact` | 交付物元数据 dict | 经 `ContextFilter` 过滤后的 deliverable（已移除私有字段） |
| `deliverable_body` | 交付物**正文全文** | **强制从 `deliverable["file_path"]` 读取磁盘文件** |
| `criteria` | 评审标准列表 | `NodeExecutionContext.evaluator_criteria` |

### 7.2 关键约束

- `file_path` 为**必填字段**，缺失时直接抛出 `ValueError`
- 若文件不存在则抛出 `FileNotFoundError`，不允许回退到 `deliverable.summary`
- Evaluator **不拥有** `chained_deliverables`、`shared_context`、`iteration_feedback`

### 7.3 DeliverableArtifact 元数据结构

```python
DeliverableArtifact = {
    title:         str,        # 交付物标题
    summary:       str,        # 简短摘要（1-2句）
    file_path:     str,        # 磁盘文件路径（唯一真相来源）
    sha256:        str,        # 文件内容 SHA256 哈希（64字符）
    word_count:    int,        # 字数统计
    section_index: list[str],  # 章节索引（## 标题列表）
    content_type:  str,        # "markdown"
}
```

---

## 8. 各节点上下文随流水线阶段的变化

### 8.1 总览

```
Pipeline 初始化:
  subject_context = {subject, context_file, content}
  PipelineState.shared_context = {}
  PipelineState.deliverables = {}
  PipelineState.chained_context = {}

analyst → pm → ux → architect → po
  ↑           ↑         ↑           ↑         ↑
 0个上游    1个上游   2个上游    3个上游  4个上游
```

### 8.2 各节点 `chained_deliverables` 内容

| 节点 | `chained_deliverables` 包含 |
|---|---|
| `analyst` | `[]`（首节点，无上游） |
| `pm` | `[analyst]` |
| `ux` | `[analyst, pm]` |
| `architect` | `[analyst, pm, ux]` |
| `po` | `[analyst, pm, ux, architect]` |

每个上游交付物在 `IndependentAgentInput` 中以摘要形式呈现（`title` + `summary[:200]`），不注入全文，避免上下文膨胀。

### 8.3 各阶段上下文对比图

```
┌─ analyst 节点 ─────────────────────────────────────────┐
│ IndependentAgentInput:                                   │
│   original_context_summary: <用户context文件全文>       │
│   chained_deliverables_summary: []                       │
│   iteration_feedback: None                               │
│   shared_context: {}                                     │
│                                                          │
│ EvaluatorAgentInput:                                     │
│   original_context_summary: <用户context文件全文>       │
│   deliverable_body: <analyst写盘的MD文件全文>           │
│   criteria: [analyst节点评审标准]                       │
└──────────────────────────────────────────────────────────┘

┌─ pm 节点 ──────────────────────────────────────────────┐
│ IndependentAgentInput:                                   │
│   original_context_summary: <用户context文件全文>       │
│   chained_deliverables_summary: [                        │
│     {node_id:"analyst", title:"...", summary:"..."[:200]}│
│   ]                                                      │
│   shared_context: {可能含analyst写入的共享信息}          │
│                                                          │
│ EvaluatorAgentInput:                                     │
│   deliverable_body: <pm写盘的MD文件全文>                │
│   criteria: [pm节点评审标准]                            │
└──────────────────────────────────────────────────────────┘

┌─ po 节点（最后节点）───────────────────────────────────┐
│ IndependentAgentInput:                                   │
│   original_context_summary: <用户context文件全文>       │
│   chained_deliverables_summary: [                        │
│     {analyst}, {pm}, {ux}, {architect}   ← 全部4个摘要 │
│   ]                                                      │
│   shared_context: {所有上游节点累积写入}                │
│                                                          │
│ EvaluatorAgentInput:                                     │
│   deliverable_body: <po写盘的MD文件全文>                │
│   criteria: [po节点评审标准]                            │
└──────────────────────────────────────────────────────────┘
```

---

## 9. 迭代循环中的上下文变化

当 Evaluator 返回 `NEEDS_REVISION` 时，下一轮迭代：

```
iteration 1:
  IndependentAgentInput.iteration_feedback = None
        ↓ Evaluator → NEEDS_REVISION (score: 0.65)

iteration 2:
  IndependentAgentInput.iteration_feedback = {
      "alignment_score": 0.65,
      "verdict":         "NEEDS_REVISION",
      "issues_found":    ["缺少风险分析", "章节结构不符合模板"],
      "suggestions":     ["补充第3节风险矩阵", "按 required_sections 调整结构"]
  }
        ↓ Evaluator → APPROVED (score: 0.88)

iteration 3（若需要）: 同上，feedback 来自 iteration 2
```

**Evaluator 始终只看当前轮的 `deliverable_body`**（每轮重新从磁盘读取），不累积历史反馈，保持评审客观性。

最大迭代次数默认为 **3**（`DualAgentNode.DEFAULT_MAX_ITERATIONS = 3`），超出后触发 `FORCE_APPROVED` 或 `BLOCKED`。

---

## 10. Verdict 状态机

```
IndependentAgent 执行
       ↓
EvaluatorAgent 执行
       ↓
verdict = ?

  APPROVED       → 节点完成，进入下一节点
  NEEDS_REVISION → 带 feedback 重新执行 Independent（最多3轮）
  FORCE_APPROVED → 超出最大迭代，强制通过（记录警告）
  BLOCKED        → 节点阻塞，触发升级（EscalationHandler）
```

---

## 11. 数据流汇总图

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
PipelineAdapter.convert_pipeline_to_node_state()
        │
        ▼
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
        │           IndependentAgent.execute_with_input()
        │           → 生成 deliverable（写盘）+ questions
        │
        ├─ ContextFilter.filter_for_evaluator()
        │   移除: private_reasoning / tool_call_history / internal_notes
        │
        └─ ContextManager.build_evaluator_input()
                  → EvaluatorAgentInput
                  (从磁盘读取 deliverable_body，P0-3)
                            │
                            ▼
                    EvaluatorAgent.execute_with_input()
                    → verdict / alignment_score / issues / suggestions
```

---

## 12. 关键设计原则总结

| 原则 | 说明 |
|---|---|
| **P0-1 Single Context Protocol** | 全链路使用 `NodeExecutionContext` 单一结构，禁止层间传 JSON 字符串或重复包装 |
| **P0-2 原始上下文传递** | Evaluator 也必须收到 `original_context_summary`，以便对照原始需求评审 |
| **P0-3 文件即真相 (Single Truth)** | Evaluator 必须读取磁盘上的正式文档正文，不允许使用 `deliverable.summary` 替代 |
| **P1-1 共享上下文** | `shared_context` 跨节点持久化，供节点间传递协商信息 |
| **上游交付物摘要截断** | `chained_deliverables_summary` 中每项 summary 截断至 200 字符，防止上下文膨胀 |
| **Evaluator 信息最小化** | Evaluator 不得访问 `chained_deliverables`、`shared_context`、`iteration_feedback`、`private_reasoning` |
| **docs_context 已停用** | `NodeExecutionContext.docs_context` 固定为 `[]`，文档驱动模式已移除 |
