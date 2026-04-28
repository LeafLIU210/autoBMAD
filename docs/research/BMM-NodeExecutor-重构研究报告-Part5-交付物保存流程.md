# BMM NodeExecutor 重构研究报告 Part 5: 交付物保存流程深度分析

**文档编号**: BMM-Research-05
**日期**: 2026-03-02
**范围**: 交付物从 LLM 生成到磁盘持久化的完整数据流分析
**修订**: v1

---

## 0. 核心约束

> **`autoBMAD/docuswarm` 运行时绝不引用 `_bmad` 或任何外部文件夹。**

**验证结论**: 交付物保存流程的所有代码路径均无 `_bmad` 外部依赖。整条链路完全自包含在 `autoBMAD/` 内部。

---

## 1. 问题陈述

### 1.1 分析目标

交付物（Deliverable）是 DocuSwarm 管道的核心产出物。每个节点（analyst/pm/ux/architect/po）执行完毕后会生成一个 Markdown 交付物文档。本报告深度分析从 LLM 生成内容到文件持久化到磁盘的**完整数据流**，包括：

- 交付物在哪里创建、如何写入磁盘
- 双层保存机制的设计意图与实现
- 状态追踪与检查点持久化
- 上下文链式传递机制
- 错误处理与容错设计

### 1.2 涉及的关键模块

| 模块 | 文件 | 职责 |
|------|------|------|
| **CreateDeliverableTool** | `tools/create_deliverable.py` | 第一层保存：LLM 通过工具调用直接写入文件 |
| **IndependentAgent** | `agents/independent.py` | Agent 执行与工作目录配置 |
| **ToolResultExtractor** | `tools/tool_result_extractor.py` | 从 LLM 响应中提取工具调用参数 |
| **DualAgentNode** | `nodes/dual_agent.py` | 双代理协调：Independent + Evaluator 循环 |
| **NodeExecutor** | `node_execution/executor.py` | 节点执行器工厂，驱动 DualAgentNode |
| **PipelineGraph** | `pipeline/graph.py` | LangGraph 状态图，第二层保存入口 |
| **FileStorage** | `storage/files.py` | 第二层保存：原子写入 + 可选 frontmatter |
| **CheckpointManager** | `storage/checkpoints.py` | SQLite WAL 检查点持久化 |
| **PipelineState** | `pipeline/state.py` | 管道状态模式，deliverables 追踪 |

---

## 2. 完整数据流：端到端追踪

### 2.1 宏观流程图

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Pipeline Execution Flow                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  create_pipeline_graph(session_manager)                              │
│       │                                                              │
│       ▼                                                              │
│  _create_integrated_node_executor(node_id, sm)     [graph.py:293]   │
│       │                                                              │
│       ▼                                                              │
│  create_node_executor(node_id, sm)                 [executor.py:34] │
│       │                                                              │
│       ▼                                                              │
│  _execute_node(state, node_id, sm, logger)         [executor.py:75] │
│       │                                                              │
│       ├── NodeLoader.load(node_id)                 [loader.py]      │
│       ├── create_dual_agent_node(config, sm, id)   [dual_agent.py]  │
│       │        │                                                     │
│       │        ├── IndependentAgent(config, sm, id)                  │
│       │        └── EvaluatorAgent(config, sm, id)                    │
│       │                                                              │
│       ▼                                                              │
│  DualAgentNode.execute(subject_ctx, task, pipeline_id)               │
│       │                                                              │
│       │  ┌─────── Iteration Loop (max 3) ──────────┐                │
│       │  │                                          │                │
│       │  │  ① IndependentAgent.execute(context)     │                │
│       │  │       │                                  │                │
│       │  │       ├── Setup work_dir: output/{pid}/  │  [L509-539]   │
│       │  │       ├── _call_llm(enriched_task)       │                │
│       │  │       │       │                          │                │
│       │  │       │       ▼                          │                │
│       │  │       │  SDK Session + LLM Execution     │                │
│       │  │       │       │                          │                │
│       │  │       │       ▼                          │                │
│       │  │       │  ═══ 第一层保存 ═══              │                │
│       │  │       │  create_deliverable tool          │                │
│       │  │       │  → Path.cwd()/slugified.md       │  [L59-92]     │
│       │  │       │                                  │                │
│       │  │       ├── _parse_response(response)      │  [L377-425]   │
│       │  │       │       │                          │                │
│       │  │       │       ▼                          │                │
│       │  │       │  ToolResultExtractor              │                │
│       │  │       │  → DeliverableMetadata            │                │
│       │  │       │                                  │                │
│       │  │       └── return IndependentOutput        │                │
│       │  │                                          │                │
│       │  │  ② ContextFilter (remove private fields) │                │
│       │  │                                          │                │
│       │  │  ③ EvaluatorAgent.execute(filtered)      │                │
│       │  │       → verdict: APPROVED/NEEDS_REVISION  │                │
│       │  │                                          │                │
│       │  │  ④ If NEEDS_REVISION → loop with feedback │                │
│       │  │                                          │                │
│       │  └──────────────────────────────────────────┘                │
│       │                                                              │
│       ▼                                                              │
│  NodeResult → update PipelineState                                   │
│       │                                                              │
│       ├── state["deliverables"][node_id] = result    [graph.py:379] │
│       │                                                              │
│       ├── ═══ 第二层保存 ═══                                        │
│       │   _save_deliverable_async(pid, nid, deliverable)             │
│       │       │                                      [graph.py:428] │
│       │       ▼                                                      │
│       │   FileStorage.save_deliverable()             [files.py:107] │
│       │       → atomic write (temp + rename)                         │
│       │       → optional YAML frontmatter                            │
│       │                                                              │
│       └── ═══ 检查点持久化 ═══                                      │
│           LangGraph checkpointer                                     │
│           → AsyncSqliteSaver(WAL mode)               [checkpoints]  │
│           → PipelineState serialized to SQLite                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 输出目录结构

```
output/{pipeline_id}/
  ├── analyst-report.md        ← 第二层保存 (FileStorage canonical name)
  ├── prd.md                   ← 第二层保存
  ├── ux-design.md             ← 第二层保存
  ├── architecture.md          ← 第二层保存
  ├── epics-stories.md         ← 第二层保存
  ├── _metadata.json           ← FileStorage.save_metadata()
  └── {slugified-title}.md     ← 第一层保存 (create_deliverable tool)

checkpoints/
  └── docuswarm_{pipeline_id}.db  ← SQLite WAL checkpoint
```

---

## 3. 第一层保存：create_deliverable 工具

### 3.1 设计意图

第一层保存是 **LLM 驱动的工具调用保存**。LLM 在 Agent 模式下执行时，通过 SDK 自动调度 `create_deliverable` 工具，将生成的 Markdown 内容直接写入磁盘。

**核心特征**：

- 保存由 LLM 主动触发（通过 tool_use 块）
- 文件名由 LLM 提供的 title 通过 slugify 生成
- 写入路径由 SDK 的 `cwd` 决定（即 `output/{pipeline_id}/`）
- 无 frontmatter，纯 Markdown 内容

### 3.2 工具定义与参数

[create_deliverable.py](autoBMAD/docuswarm/tools/create_deliverable.py:20-35):

```python
class CreateDeliverableParams(BaseModel):
    title: str = Field(description="Deliverable title")
    content: str = Field(description="Deliverable content (Markdown)")
    metadata: dict[str, Any] = Field(default_factory=dict)
```

工具通过 `ToolRegistry` 全局注册：

```python
ToolRegistry.register(
    ToolDefinition(
        name="create_deliverable",
        description="Create a node deliverable document",
        parameters=CreateDeliverableParams,
        handler=create_deliverable,
    )
)
```

### 3.3 保存逻辑

[create_deliverable.py](autoBMAD/docuswarm/tools/create_deliverable.py:59-92):

```python
async def create_deliverable(params: CreateDeliverableParams) -> ToolResult:
    filename = _slugify_filename(params.title)  # title → lowercase-hyphenated.md
    file_path = Path.cwd() / filename           # cwd = output/{pipeline_id}/

    async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
        await f.write(params.content)           # 直接写入，无 frontmatter

    return ToolResult(
        success=True,
        output=f"Deliverable '{params.title}' saved to {file_path}",
        metadata={"file_path": str(file_path), "title": params.title},
    )
```

**关键细节**：

- `_slugify_filename()` 将 title 转为 `lowercase-hyphenated.md` 格式
- `Path.cwd()` 依赖 SDK 的工作目录设置（由 IndependentAgent 配置）
- 使用 `aiofiles` 异步写入
- 无原子写入保护（直接 open + write）
- 返回 `ToolResult` 含 `file_path` 和 `title` 元数据

### 3.4 工作目录配置

[independent.py](autoBMAD/docuswarm/agents/independent.py:509-539):

```python
# IndependentAgent.execute() 中：
output_dir = self.project_root / "output" / pipeline_id
output_dir.mkdir(parents=True, exist_ok=True)

self._work_dir = output_dir

# 创建新的 session manager，设置 work_dir
pipeline_session_manager = KimiSessionManager(
    work_dir=KaosPath(str(output_dir)),
    config=self.session_manager.config,
)
```

**设计决策**：每次 IndependentAgent 执行时，创建一个新的 `KimiSessionManager` 实例，其 `work_dir` 指向 `output/{pipeline_id}/`。SDK 在创建 session 时使用此 `work_dir` 作为工具执行的当前工作目录，确保 `Path.cwd()` 指向正确位置。

---

## 4. 响应解析：ToolResultExtractor

### 4.1 提取链路

LLM 执行完毕后，`IndependentAgent._parse_response()` 使用 `ToolResultExtractor` 从消息流中提取工具调用参数：

[independent.py](autoBMAD/docuswarm/agents/independent.py:377-425):

```python
def _parse_response(self, response: list[dict[str, Any]]) -> IndependentOutput:
    extractor = ToolResultExtractor()
    metadata_list = extractor.extract_from_dicts(response)

    if not metadata_list:
        raise ResponseParseAgentError("No create_deliverable tool was called")

    metadata: DeliverableMetadata = metadata_list[0]

    data = {
        "deliverable": {
            "title": metadata.title,
            "content": metadata.content_summary,  # 摘要，非全文
            "metadata": metadata.metadata,
        },
        "questions": [],
        "action": "create_deliverable",
    }

    validate_independent_output(data)
    return data
```

### 4.2 ToolResultExtractor 工作原理

[tool_result_extractor.py](autoBMAD/docuswarm/tools/tool_result_extractor.py:158-244):

```python
def extract_from_dicts(self, messages: list[dict[str, Any]]) -> list[DeliverableMetadata]:
    for message in messages:
        content = message.get("content")
        if isinstance(content, list):
            for block in content:
                if block.get("type") == "tool_use":
                    tool_name = block.get("name", "")
                    if tool_name in self.SUPPORTED_TOOLS:
                        params = block.get("input", {})
                        extracted = self.parse_tool_params(tool_name, params)
                        results.extend(extracted)
    return results
```

**提取流程**：

1. 遍历 LLM 返回的消息列表（`list[dict]` 格式）
2. 查找 `content` 为列表的消息（Assistant 消息）
3. 在列表中查找 `type == "tool_use"` 的块
4. 验证 `name` 是否在支持的工具集合中（`create_deliverable`, `create_document_set`）
5. 提取 `input` 参数，构建 `DeliverableMetadata`

### 4.3 DeliverableMetadata 数据结构

[tool_result_extractor.py](autoBMAD/docuswarm/tools/tool_result_extractor.py:19-52):

```python
@dataclass(frozen=True)
class DeliverableMetadata:
    title: str               # 交付物标题
    content: str              # 完整内容
    content_summary: str      # 截断摘要 (max 500 chars)
    file_path: str            # slugified 文件路径
    metadata: dict[str, Any]  # 额外元数据
    tool_name: str            # 工具名称
```

**关键设计**：
- `content` 保存完整内容，`content_summary` 是前 500 字符的截断
- `IndependentOutput.deliverable.content` 使用的是 `content_summary`（摘要），不是全文
- 完整内容已在第一层保存时写入磁盘，状态中只保留摘要以减小序列化体积

---

## 5. 双代理协调：DualAgentNode

### 5.1 执行流程

[dual_agent.py](autoBMAD/docuswarm/nodes/dual_agent.py:251-504):

```
DualAgentNode.execute(subject_context, task, pipeline_id)
    │
    ├── iteration = 0
    ├── while iteration < max_iterations (3):
    │       │
    │       ├── ① build_independent_context(subject, task, previous_feedback)
    │       │       → 加入 pipeline_id 到 context
    │       │
    │       ├── ② IndependentAgent.execute(context)
    │       │       → 设置 work_dir → 调用 LLM → 工具保存 → 解析响应
    │       │       → 返回 IndependentOutput {deliverable, questions, action}
    │       │
    │       ├── ③ ContextFilter.filter_for_evaluator(output)
    │       │       → 移除 private_reasoning, tool_call_history 等
    │       │
    │       ├── ④ EvaluatorAgent.execute(evaluator_context)
    │       │       → 返回 {verdict, alignment_score, issues_found, suggestions}
    │       │
    │       └── ⑤ 判断 verdict:
    │               APPROVED → break
    │               FORCE_APPROVED → create_force_completion() → break
    │               BLOCKED → break
    │               NEEDS_REVISION → 将 evaluation 作为 previous_feedback → continue
    │
    └── return NodeResult(deliverable, questions, evaluation, iteration, timestamp)
```

### 5.2 数据过滤的安全设计

`ContextFilter` 确保 `private_reasoning` 等敏感字段不会泄露到 Evaluator：

```python
# 被过滤的字段：
- private_reasoning    (Independent Agent 的内部推理)
- tool_call_history    (工具调用历史)
- internal_notes       (内部备注)
- iteration_feedback   (迭代反馈)
```

这确保了 Evaluator 只看到交付物本身和公开的问题列表。

---

## 6. 第二层保存：FileStorage 原子写入

### 6.1 触发入口

[graph.py](autoBMAD/docuswarm/pipeline/graph.py:381-404):

```python
# _create_integrated_node_executor 中，节点执行完成后：
status = executed_node_state.get("status")
if status in ("completed", "approved") and executed_node_state.get("deliverable"):
    pipeline_id = new_state.get("pipeline_id", "unknown")
    output_root = str(session_manager.work_dir) if session_manager else None
    try:
        _run_async(
            _save_deliverable_async(pipeline_id, node_id, deliverable, output_root)
        )
    except Exception as e:
        # 记录警告但不中断管道
        logger.warning("failed_to_save_deliverable", ...)
```

**设计意图**：第二层保存在节点执行成功后触发，使用规范化的文件名覆写第一层保存的 slugified 文件。

### 6.2 _save_deliverable_async

[graph.py](autoBMAD/docuswarm/pipeline/graph.py:428-471):

```python
async def _save_deliverable_async(pipeline_id, node_id, deliverable, output_root=None):
    storage = FileStorage(output_root=output_root)

    # 处理 dict 和 string 两种格式的 deliverable
    if isinstance(deliverable, str):
        content = deliverable
    else:
        content = deliverable.get("content") or deliverable.get("markdown") or str(deliverable)

    await storage.save_deliverable(
        pipeline_id=pipeline_id,
        node_type=node_id,
        content=content,
    )
```

### 6.3 FileStorage.save_deliverable

[files.py](autoBMAD/docuswarm/storage/files.py:107-179):

```python
async def save_deliverable(self, pipeline_id, node_type, content,
                           add_frontmatter=False, evaluation_score=None):
    # 1. 从 FILENAME_MAP 获取规范文件名
    filename = FILENAME_MAP.get(node_type)  # e.g., "analyst" → "analyst-report.md"

    # 2. 确保输出目录存在
    pipeline_dir = await self._ensure_output_dir(pipeline_id)
    file_path = pipeline_dir / filename

    # 3. 可选添加 YAML frontmatter
    if add_frontmatter:
        frontmatter = {
            "pipeline_id": pipeline_id,
            "node": node_type,
            "created_at": datetime.now(UTC).isoformat(),
        }
        if evaluation_score is not None:
            frontmatter["evaluation_score"] = evaluation_score
        final_content = f"---\n{yaml.dump(frontmatter)}---\n\n{content}"

    # 4. 原子写入：temp file + rename
    temp_path = file_path.with_suffix(".tmp")
    async with aiofiles.open(temp_path, "w", encoding="utf-8") as f:
        await f.write(final_content)
    temp_path.replace(file_path)  # 原子重命名
```

### 6.4 FILENAME_MAP 规范化映射

[files.py](autoBMAD/docuswarm/storage/files.py:22-31):

```python
FILENAME_MAP: dict[str, str] = {
    "analyst": "analyst-report.md",
    "prd": "prd.md",
    "pm": "prd.md",           # pm 和 prd 映射到同一文件
    "ux": "ux-design.md",
    "architecture": "architecture.md",
    "architect": "architecture.md",  # architect 映射到 architecture.md
    "epics": "epics-stories.md",
    "po": "epics-stories.md",      # po 映射到 epics-stories.md
}
```

**设计说明**：FILENAME_MAP 同时支持 node_id（`analyst`, `pm`, `ux`, `architect`, `po`）和语义名称（`prd`, `architecture`, `epics`），提供灵活的文件名映射。

### 6.5 原子写入的容错设计

```python
try:
    async with aiofiles.open(temp_path, "w", encoding="utf-8") as f:
        await f.write(final_content)
    temp_path.replace(file_path)   # 原子重命名
except Exception as e:
    if temp_path.exists():
        temp_path.unlink()         # 清理临时文件
    raise StorageError(...)
```

**原子写入模式**：先写 `.tmp` 临时文件，写入完成后用 `replace()` 原子重命名。如果写入过程中崩溃，`.tmp` 文件不会影响已有内容。`replace()` 在 POSIX 系统上是原子操作，在 Windows 上也提供了合理的安全保证。

### 6.6 路径遍历防护

[files.py](autoBMAD/docuswarm/storage/files.py:60-87):

```python
_INVALID_PATH_PATTERN = re.compile(r"[./\\]")

def _validate_pipeline_id(self, pipeline_id: str) -> None:
    if not pipeline_id or not pipeline_id.strip():
        raise StorageError("pipeline_id cannot be empty")
    if _INVALID_PATH_PATTERN.search(pipeline_id):
        raise StorageError("contains path traversal characters")
    if pipeline_id.startswith("/") or pipeline_id[1] == ":":
        raise StorageError("absolute paths not allowed")
```

**安全设计**：`pipeline_id` 经过严格验证，禁止 `.`、`/`、`\` 等路径遍历字符，防止恶意 pipeline_id 写入任意位置。

---

## 7. 双层保存对比

### 7.1 对比表

| 特性 | 第一层（create_deliverable 工具） | 第二层（FileStorage） |
|------|----------------------------------|----------------------|
| **触发方** | LLM（通过 tool_use） | Pipeline 框架（节点完成后） |
| **调用时机** | LLM 执行过程中 | 节点执行成功后 |
| **文件名** | slugify(title) → `project-analysis-report.md` | FILENAME_MAP → `analyst-report.md` |
| **内容** | LLM 生成的完整 Markdown | 从 state deliverable 提取的 content |
| **frontmatter** | 无 | 可选（pipeline_id, node, created_at, score） |
| **原子写入** | 无（直接 open+write） | 有（temp + rename） |
| **错误处理** | 返回 ToolResult.error | 记录 warning，不中断管道 |
| **路径验证** | 无（依赖 SDK cwd） | 有（防路径遍历） |
| **触发条件** | LLM 决定调用工具时 | status in ("completed", "approved") |

### 7.2 设计意图分析

**第一层保存** 的核心目的是让 LLM 通过工具调用"创造"交付物，这是 Agent 模式的自然行为。LLM 生成内容后立即持久化，确保即使后续处理失败，原始内容也已保存。

**第二层保存** 的核心目的是提供规范化的文件管理：
1. **规范文件名**：使用 FILENAME_MAP 而非 LLM 生成的 slug
2. **原子写入**：确保崩溃安全
3. **元数据增强**：可添加 pipeline_id、node_type、evaluation_score 等 frontmatter
4. **统一入口**：所有节点通过同一 FileStorage 接口保存

### 7.3 潜在问题

1. **双重写入可能导致内容不一致**：如果第二层保存的 `content` 提取逻辑与 LLM 写入的完整内容不同（例如使用 `content_summary` 而非 `content`），规范文件可能只包含摘要而非全文
2. **文件名冲突**：第一层的 slugified 文件和第二层的规范文件可能同时存在于目录中
3. **内容来源歧义**：`_save_deliverable_async` 从 deliverable dict 提取内容时，有三个候选键（`content`, `markdown`, `str(deliverable)`），可能产生不同结果

---

## 8. 状态持久化：PipelineState + Checkpoints

### 8.1 PipelineState.deliverables 追踪

[state.py](autoBMAD/docuswarm/pipeline/state.py:57-76):

```python
class PipelineState(TypedDict):
    pipeline_id: str
    subject_context: dict[str, Any]
    current_node: str | None
    completed_nodes: list[str]
    deliverables: dict[str, dict[str, Any]]      # node_id → deliverable dict
    questions: dict[str, list[dict[str, Any]]]    # node_id → questions
    evaluations: dict[str, dict[str, Any]]        # node_id → evaluation
    node_iterations: dict[str, int]               # node_id → iteration count
    session_ids: dict[str, str]
    session_metadata: dict[str, dict[str, Any]]
    current_node_session_id: str | None
    status: str
    error: dict[str, Any] | None
```

`deliverables` 字典以 `node_id` 为键，存储每个节点的交付物。这些数据通过 LangGraph 的 `SqliteSaver` 自动持久化到 SQLite 检查点中。

### 8.2 上下文链式传递

[state.py](autoBMAD/docuswarm/pipeline/state.py:184-230):

```python
def accumulate_context(subject_context, deliverables, current_node):
    # 找到当前节点在管道中的位置
    current_index = PIPELINE_NODES.index(current_node)
    previous_nodes = PIPELINE_NODES[:current_index]

    accumulated = {"subject_context": subject_context.copy()}

    # 将所有前序节点的交付物加入上下文
    for node_id in previous_nodes:
        if node_id in deliverables and deliverables[node_id]:
            accumulated[f"{node_id}_deliverable"] = deliverables[node_id].copy()

    return accumulated
```

**链式传递机制**：

```
analyst 执行时: subject_context
pm 执行时:      subject_context + analyst_deliverable
ux 执行时:      subject_context + analyst_deliverable + pm_deliverable
architect 时:   subject_context + analyst_deliverable + pm_deliverable + ux_deliverable
po 执行时:      subject_context + all 4 previous deliverables
```

### 8.3 节点状态转换在 graph.py 中的集成

[graph.py](autoBMAD/docuswarm/pipeline/graph.py:347-424):

```python
def executor(state):
    # 1. 深拷贝状态避免突变
    new_state = copy.deepcopy(state)

    # 2. 转换 PipelineState → NodeRunState
    node_run_state = _convert_pipeline_to_node_state(new_state, node_id)

    # 3. 执行异步节点执行器
    executed_node_state = _run_async(async_node_executor(node_run_state))

    # 4. 转换 NodeRunState → PipelineState
    new_state = _convert_node_to_pipeline_state(executed_node_state, new_state)

    # 5. 第二层保存 (如果成功)
    if status in ("completed", "approved"):
        _run_async(_save_deliverable_async(...))

    # 6. 增加迭代计数 + 加入 completed_nodes
    new_state["node_iterations"][node_id] = current_iteration + 1
    new_state["completed_nodes"] = [..., node_id]

    return new_state
```

### 8.4 CheckpointManager

[checkpoints.py](autoBMAD/docuswarm/storage/checkpoints.py:13-79):

```python
class CheckpointManager:
    async def initialize(self):
        aconn = await aiosqlite.connect(self.db_path)
        cursor = await aconn.execute("PRAGMA journal_mode=WAL")  # WAL 模式
        cursor = await aconn.execute("PRAGMA synchronous=NORMAL")
        self._checkpointer = AsyncSqliteSaver(conn=aconn)
```

**设计特征**：

- **WAL 模式**：Write-Ahead Logging，允许并发读写
- **NORMAL 同步**：平衡性能和持久性
- **is_alive 补丁**：为 `aiosqlite` 添加 `is_alive()` 方法以兼容 LangGraph
- **线程 ID 隔离**：每个 pipeline 使用唯一 `thread_id = {pipeline_id}_{uuid8}`

### 8.5 检查点数据结构

```python
checkpoint = {
    "checkpoint_id": str,           # 唯一标识
    "thread_id": str,               # pipeline 线程 ID
    "pipeline_id": str,             # 管道 ID
    "state": {                      # channel_values (序列化的 PipelineState)
        "pipeline_id": "...",
        "deliverables": {...},      # 所有节点的交付物
        "completed_nodes": [...],
        "node_iterations": {...},
        ...
    },
    "timestamp": str,               # ISO 时间戳
}
```

---

## 9. 状态转换：PipelineState ↔ NodeRunState

### 9.1 Pipeline → Node 转换

[graph.py](autoBMAD/docuswarm/pipeline/graph.py:162-224):

```python
def _convert_pipeline_to_node_state(state, node_id):
    # 1. 从 subject_context 生成 context_hash (MD5)
    context_hash = hashlib.md5(json.dumps(subject_context).encode()).hexdigest()

    # 2. 序列化累积上下文为 context_file
    accumulated = accumulate_context(subject_context, deliverables, node_id)
    context_file = json.dumps(accumulated)

    # 3. 构建 chained_context（前序节点的交付物 + 迭代数）
    chained_context = {}
    for prev_node_id in PIPELINE_NODES:
        if prev_node_id == node_id: break
        if prev_node_id in deliverables:
            chained_context[prev_node_id] = {
                "deliverable": deliverables[prev_node_id],
                "iteration": node_iterations[prev_node_id],
            }

    return NodeRunState(
        run_id=pipeline_id, node_id=node_id,
        context_hash=context_hash, context_file=context_file,
        iteration=iteration, chained_context=chained_context,
        status="pending", ...
    )
```

### 9.2 Node → Pipeline 转换

[graph.py](autoBMAD/docuswarm/pipeline/graph.py:227-290):

```python
def _convert_node_to_pipeline_state(node_state, original_state):
    new_state = copy.deepcopy(original_state)
    node_id = node_state["node_id"]

    # 更新交付物
    if node_state.get("deliverable") is not None:
        new_state["deliverables"][node_id] = node_state["deliverable"]

    # 更新问题、评估、迭代计数
    if node_state.get("questions"): new_state["questions"][node_id] = ...
    if node_state.get("evaluation"): new_state["evaluations"][node_id] = ...
    new_state["node_iterations"][node_id] = node_state.get("iteration", 1)

    # 加入 completed_nodes
    if node_id not in new_state["completed_nodes"]:
        new_state["completed_nodes"] = [..., node_id]

    return new_state
```

---

## 10. 错误处理与容错设计

### 10.1 各层错误处理策略

| 层级 | 错误处理策略 | 影响范围 |
|------|-------------|---------|
| **create_deliverable 工具** | 返回 `ToolResult(success=False, error=...)` | LLM 收到错误信息，可能重试 |
| **IndependentAgent** | 抛出 `ResponseParseAgentError` → `IndependentExecutionError` | DualAgentNode 捕获，终止迭代 |
| **DualAgentNode** | 抛出 `IndependentExecutionError` / `EvaluatorExecutionError` | NodeExecutor 捕获 |
| **NodeExecutor (executor.py)** | 设置 `status = FAILED` | PipelineGraph 捕获 |
| **PipelineGraph (graph.py)** | 回退到空交付物 `deliverables[node_id] = {}` | 管道继续执行 |
| **FileStorage (第二层保存)** | `logger.warning` 但不中断管道 | 不影响管道状态 |
| **CheckpointManager** | 由 LangGraph 框架自动处理 | 可能丢失最近状态 |

### 10.2 LLM 调用容错

[independent.py](autoBMAD/docuswarm/agents/independent.py:306-329):

```python
# StepLimitExceeded: 返回部分消息而非失败
except StepLimitExceeded as e:
    if messages:
        return self._convert_messages_to_dicts(messages)
    raise LLMCallError(...)

# SessionCancelled: 返回部分消息而非失败
except SessionCancelled as e:
    if messages:
        return self._convert_messages_to_dicts(messages)
    raise LLMCallError(...)
```

**设计决策**：当 LLM 超出步骤限制或会话被取消时，如果已有部分消息（可能包含 tool_use 调用），仍然返回这些消息而非直接失败。这意味着即使 LLM 的最终 JSON 响应未完成，交付物可能已通过工具保存到磁盘。

### 10.3 迭代回退

[graph.py](autoBMAD/docuswarm/pipeline/graph.py:406-413):

```python
except Exception as e:
    logger.error("integrated_executor_error", ...)
    # 回退到空交付物
    new_state["deliverables"][node_id] = {}
```

**设计意图**：节点执行失败时，管道不会中断。空交付物 `{}` 会传递给下游节点的 `accumulate_context()`，下游节点将看不到该节点的输出，但仍可基于更早的上下文继续工作。

---

## 11. 外部依赖验证

### 11.1 代码路径审计

对交付物保存流程涉及的所有文件进行 `_bmad` 引用审计：

| 文件 | `_bmad` 引用 | 状态 |
|------|-------------|------|
| `tools/create_deliverable.py` | 无 | 安全 |
| `agents/independent.py` | 无 | 安全 |
| `tools/tool_result_extractor.py` | 无 | 安全 |
| `nodes/dual_agent.py` | 无 | 安全 |
| `node_execution/executor.py` | 无 | 安全 |
| `pipeline/graph.py` | 无 | 安全 |
| `storage/files.py` | 无 | 安全 |
| `storage/checkpoints.py` | 无 | 安全 |
| `pipeline/state.py` | 无 | 安全 |

### 11.2 结论

**交付物保存流程的全部代码路径无任何 `_bmad` 外部依赖。** 所有配置加载（persona.json, node.yaml, evaluator.yaml）均来自 `autoBMAD/nodes/` 目录，所有文件写入均指向 `output/{pipeline_id}/` 目录。

---

## 12. 关键设计模式总结

### 12.1 工作目录隔离模式

```
每次 IndependentAgent.execute() 创建独立的 KimiSessionManager
    → work_dir = output/{pipeline_id}/
    → SDK tools 在此目录下执行
    → 执行完毕后恢复原始 session_manager
```

**优势**：确保不同管道执行之间的文件输出完全隔离，避免覆盖。

### 12.2 双层保存冗余模式

```
第一层: LLM → create_deliverable tool → 直接写入 (即时性)
第二层: Pipeline → FileStorage → 原子写入 (可靠性)
```

**优势**：即使 Pipeline 框架的第二层保存失败，LLM 已通过工具将完整内容写入磁盘。

### 12.3 上下文累积模式

```
节点 N 的上下文 = subject_context + Σ(deliverable[i]) for i < N
```

**优势**：每个后续节点都能看到前序节点的完整输出，实现知识的链式传递。

### 12.4 深拷贝不可变模式

```python
new_state = copy.deepcopy(state)  # 每个节点执行器都深拷贝状态
```

**优势**：满足 LangGraph 的不可变状态要求，避免并发修改问题。

### 12.5 优雅降级模式

```
节点执行失败 → deliverables[node_id] = {} → 下游节点继续
第二层保存失败 → logger.warning → 管道不中断
```

**优势**：单个节点的失败不会导致整个管道崩溃。

---

## 13. 与 BMM 重构的关系

### 13.1 保存流程不受重构影响

交付物保存流程的核心代码路径（create_deliverable → FileStorage → Checkpoints）**不受 BMM NodeExecutor 重构的影响**。重构仅影响：

- `persona.json` 内容增强（加入 BMM 角色上下文）
- `node.yaml` 结构扩展（加入 task 描述和 deliverable 定义）
- `evaluator.yaml` 评估标准微调

这些变更仅影响 LLM 的 system prompt 和评估标准，不影响保存机制本身。

### 13.2 重构后的交付物流转

重构后，交付物的内容质量将因 BMM 角色上下文的注入而提升，但保存流程保持不变：

```
[重构前] 通用 persona → LLM → create_deliverable → FileStorage
[重构后] BMM persona → LLM → create_deliverable → FileStorage (完全相同)
```

---

## 14. 建议与改进方向

### 14.1 P2 - 内容一致性问题

**问题**：第二层保存从 `deliverable` dict 提取内容时，可能只获取到 `content_summary`（500 字符摘要）而非完整内容。

**建议**：在 `_save_deliverable_async` 中，优先尝试从第一层保存的文件直接读取完整内容，或在 `IndependentOutput` 中保留完整内容的文件路径引用。

### 14.2 P3 - 双重文件清理

**问题**：第一层和第二层保存可能在同一目录产生两个不同名称的文件（例如 `project-analysis-report.md` 和 `analyst-report.md`）。

**建议**：在第二层保存成功后，清理第一层保存的 slugified 文件；或统一使用 FILENAME_MAP 中的规范文件名作为 `create_deliverable` 工具的默认文件名。

### 14.3 P3 - 第一层保存原子性

**问题**：`create_deliverable` 工具使用直接 `open + write`，无原子写入保护。

**建议**：考虑在工具层也使用 temp + rename 模式，与 FileStorage 保持一致。

---

## 附录 A: 完整调用链索引

| 步骤 | 函数/方法 | 文件:行号 |
|------|----------|----------|
| 1 | `create_pipeline_graph()` | `pipeline/graph.py:492` |
| 2 | `_create_integrated_node_executor()` | `pipeline/graph.py:293` |
| 3 | `create_node_executor()` | `node_execution/executor.py:34` |
| 4 | `_execute_node()` | `node_execution/executor.py:75` |
| 5 | `NodeLoader.load()` | `nodes/loader.py` |
| 6 | `create_dual_agent_node()` | `nodes/dual_agent.py:778` |
| 7 | `DualAgentNode.execute()` | `nodes/dual_agent.py:251` |
| 8 | `IndependentAgent.execute()` | `agents/independent.py:428` |
| 9 | `KimiSessionManager` work_dir 设置 | `agents/independent.py:509-539` |
| 10 | `_call_llm_via_session()` | `agents/independent.py:237` |
| 11 | SDK `session.prompt()` → LLM 执行 | `agents/independent.py:283` |
| 12 | `create_deliverable()` (工具) | `tools/create_deliverable.py:59` |
| 13 | `_slugify_filename()` | `tools/create_deliverable.py:37` |
| 14 | `aiofiles.open()` 写入 | `tools/create_deliverable.py:76` |
| 15 | `_parse_response()` | `agents/independent.py:377` |
| 16 | `ToolResultExtractor.extract_from_dicts()` | `tools/tool_result_extractor.py:158` |
| 17 | `DeliverableMetadata` 构建 | `tools/tool_result_extractor.py:357` |
| 18 | `validate_independent_output()` | `llm/response.py` |
| 19 | `ContextFilter.filter_for_evaluator()` | `context/filter.py` |
| 20 | `EvaluatorAgent.execute()` | `agents/evaluator.py` |
| 21 | `_convert_node_to_pipeline_state()` | `pipeline/graph.py:227` |
| 22 | `_save_deliverable_async()` | `pipeline/graph.py:428` |
| 23 | `FileStorage.save_deliverable()` | `storage/files.py:107` |
| 24 | 原子写入 (temp + rename) | `storage/files.py:160-167` |
| 25 | LangGraph checkpointer | `storage/checkpoints.py` |

---

## 附录 B: 数据格式参考

### IndependentOutput

```json
{
  "deliverable": {
    "title": "Project Analysis Report",
    "content": "Created comprehensive analysis... (summary)",
    "metadata": {}
  },
  "questions": [
    {
      "question": "Should we include performance benchmarks?",
      "priority": "clarifying",
      "context": "To provide quantitative data"
    }
  ],
  "action": "create_deliverable"
}
```

### NodeResult (DualAgentNode)

```python
NodeResult(
    deliverable={"title": "...", "content": "...", "metadata": {}},
    questions=[{"question": "...", "priority": "...", "context": "..."}],
    evaluation={"verdict": "APPROVED", "alignment_score": 0.85, "issues_found": [], "suggestions": []},
    iteration=2,
    timestamp=datetime(2026, 3, 2, ...),
    force_completion=None,
)
```

### PipelineState.deliverables

```json
{
  "analyst": {"title": "Analysis Report", "content": "...", "metadata": {}},
  "pm": {"title": "PRD", "content": "...", "metadata": {}},
  "ux": {"title": "UX Design", "content": "...", "metadata": {}},
  "architect": {"title": "Architecture", "content": "...", "metadata": {}},
  "po": {"title": "Epics & Stories", "content": "...", "metadata": {}}
}
```

### ToolResult (create_deliverable)

```json
{
  "success": true,
  "output": "Deliverable 'Project Analysis Report' saved to /output/abc123/project-analysis-report.md",
  "error": null,
  "metadata": {
    "file_path": "/output/abc123/project-analysis-report.md",
    "title": "Project Analysis Report"
  }
}
```


---

## 7. 解决方案文档

本文档的研究结果（交付物双层保存、Filename管理）已转化为测试驱动的实施方案：

| 方案文档 | 内容 | 位置 |
|----------|------|------|
| **TDD-BMM-01** | NodeLoader 配置加载系统重构 (含 deliverable.output_filename) | [`docs/solution/TDD-BMM-01-NodeLoader-Config-Refactor.md`](../solution/TDD-BMM-01-NodeLoader-Config-Refactor.md) |
| **TDD-BMM-04** | 双代理流程集成与端到端测试 | [`docs/solution/TDD-BMM-04-DualAgent-Integration-E2E.md`](../solution/TDD-BMM-04-DualAgent-Integration-E2E.md) |
| **TDD-BMM-05** | BMM NodeExecutor 重构主实施指南 | [`docs/solution/TDD-BMM-05-Master-Implementation-Guide.md`](../solution/TDD-BMM-05-Master-Implementation-Guide.md) |

**关键配置字段**:
```yaml
# node.yaml.deliverable
deliverable:
  type: product-brief
  template_title: "Product Brief: {project_name}"      # 用于LLM Tool
  output_filename: "product-brief-{project_name}.md"   # 用于FileStorage
```

**架构文档更新**:
- [`docs/architecture/03_PIPELINE_ARCHITECTURE.md`](../architecture/03_PIPELINE_ARCHITECTURE.md) - 节点执行架构 (v2.3)

---

**文档结束**
