# DocuSwarm 流水线 Current Node 显示 unknown 的问题分析与操作指引

## 一、问题背景

在使用 DocuSwarm 的 CLI 命令检查流水线状态时，出现如下状态信息：

- **Status**: `running`
- **Current Node**: `unknown`

按文档说明，流水线应当按顺序执行节点：`analyst → pm → ux → architect → po`，因此期望在 `Current Node` 一列看到具体节点名称，而不是 `unknown`。

本报告基于代码与文档的对比分析，给出：

- **根因说明**：为什么会出现 `Current Node = unknown`
- **设计预期行为**：流水线是如何“按顺序执行节点”的
- **正确的操作路径**：如何让流水线真实从 `analyst` 节点开始执行

---

## 二、现象复盘

命令示例（用户实际执行）：

```bash
python -m autoBMAD.docuswarm status pipeline-1771817617511-a6eea25d
```

得到的状态类似：

```text
Pipeline Status: pipeline-1771817617511-a6eea25d
│ Status       │ running
│ Current Node │ unknown
```

同时，文档中示例输出为：

```text
│ Status       │ running
│ Current Node │ pm
```

两者差异点在于：**Current Node 一个是具体节点 pm，一个是 unknown**。

---

## 三、根因分析

### 3.1 Current Node 的真实来源

在 CLI 中，`status` 命令的实现位于 `autoBMAD/docuswarm/main.py`：

```python
pipeline: dict[str, Any] | None = state_manager.get_pipeline(pipeline_id)
...
table.add_row("Current Node", str(cast(str, pipeline.get("current_node")) or "N/A"))
```

可以确认：

- **Current Node** 的值来自数据库中 `pipelines` 表的 `current_node` 字段；
- 只有当这个字段为 `NULL`/空值时，才会显示为 `"N/A"`；
- 你看到的是字面值 `unknown`，说明数据库中这一条记录的 `current_node` 字段，就是字符串 `"unknown"`。

`current_node` 字段由 `StateManager.update_pipeline_status` 写入，代码在 `autoBMAD/docuswarm/storage/state_manager.py`：

```python
def update_pipeline_status(
    self,
    pipeline_id: str,
    status: str,
    current_node: str | None = None,
) -> bool:
    ...
    with self._db.acquire() as conn:
        if current_node is not None:
            conn.execute(
                "UPDATE pipelines SET status = ?, current_node = ?, "
                + "updated_at = CURRENT_TIMESTAMP WHERE pipeline_id = ?",
                (status, current_node, pipeline_id),
            )
        else:
            conn.execute(
                "UPDATE pipelines SET status = ?, "
                + "updated_at = CURRENT_TIMESTAMP WHERE pipeline_id = ?",
                (status, pipeline_id),
            )
```

结论：

- `unknown` 不是渲染层随便显示的占位，而是 **已经被当成字符串写进了数据库**。

### 3.2 是谁把 "unknown" 写进了 current_node

在 CLI 的 `resume` 命令中，有如下逻辑（同样在 `main.py`）：

```python
pipeline: dict[str, Any] | None = state_manager.get_pipeline(pipeline_id)
...
current_node: str = str(cast(str, pipeline.get("current_node")) or "unknown")
...
state_manager.update_pipeline_status(
    pipeline_id=pipeline_id,
    status="running",
    current_node=current_node,
)
```

分析：

1. 如果数据库中这条流水线的 `current_node` 还没有被设置（`NULL`/空）：
   - `pipeline.get("current_node")` 为 `None`；
   - `str(... or "unknown")` 会得到字符串 `"unknown"`；
2. 然后 `update_pipeline_status` 被调用，带着 `current_node="unknown"`，于是：
   - `pipelines.current_node` 字段被更新为 `"unknown"`；
3. 后续无论是 CLI `status`，还是 `list-pipelines`，都会直接展示这个值。

因此：

> **`Current Node = unknown` = 这条流水线在没有真正执行任何节点的前提下，先被 `resume` 之类的操作写入了占位字符串 `"unknown"` 作为当前节点。**

### 3.3 这条流水线并没有真正跑过 analyst

真正负责“从 analyst 开始顺序执行五个节点”的，是 `HybridOrchestrator.start_pipeline`，位于 `autoBMAD/docuswarm/pipeline/orchestrator.py`：

```python
# 1. LLM 校验上下文
validation_result = await self._validate_context(subject_context)
...
# 2. 创建流水线记录
subject = subject_context.get("subject", "Untitled")
db_pipeline_id = self._state_manager.create_pipeline(
    subject=subject,
    subject_context=subject_context,
)

# 3. 更新状态为 running，并设置 current_node 为第一个节点
final_pipeline_id = pipeline_id or db_pipeline_id
self._state_manager.update_pipeline_status(
    final_pipeline_id,
    status=RUNNING,
    current_node=PIPELINE_NODES[0],  # 即 "analyst"
)

# 4. 构建并执行 LangGraph
graph = create_pipeline_graph(...)
result = await graph.ainvoke(initial_state, config)

# 5. 执行完成后更新为 completed
self._state_manager.update_pipeline_status(
    final_pipeline_id,
    status="completed",
)
```

几点关键事实：

- `PIPELINE_NODES = ["analyst", "pm", "ux", "architect", "po"]` 定义于 `pipeline/state.py`；
- `start_pipeline` **明确在第 3 步将 `current_node` 设为 `PIPELINE_NODES[0]`，即 `"analyst"`**；
- 随后通过 LangGraph 的 `create_pipeline_graph` 实现顺序执行这五个节点。

而你当前这条 `pipeline-1771817617511-a6eea25d`：

- 是通过 CLI 的 `start` 命令，用 `StateManager.create_pipeline` 直接在数据库创建的记录；
- **并没有经过 `HybridOrchestrator.start_pipeline` 这个入口**；
- 因此：
  - 没有 LangGraph 实际跑节点；
  - 没有任何地方把 `current_node` 设置为 `"analyst"`；
  - 如果之后调用了 `resume`，会把空的 `current_node` 填成 `"unknown"` 并写回数据库。

这解释了为什么：

> 文档说“流水线会自动按顺序执行节点”，是指通过 `HybridOrchestrator` 启动的流水线；
> 你当前这条仅由 CLI `start` 创建的流水线，只是一个“元数据壳子”，**并没有真正启动 LangGraph 图执行**。

---

## 四、设计预期：流水线是如何顺序执行 analyst → pm → ux → architect → po 的

### 4.1 节点顺序定义

在 `autoBMAD/docuswarm/pipeline/state.py` 中：

```python
# Pipeline node order - must execute in sequence
PIPELINE_NODES: list[str] = ["analyst", "pm", "ux", "architect", "po"]
```

这是流水线节点的唯一顺序定义，所有依赖、上下文累积等逻辑都围绕这个列表展开。

### 4.2 LangGraph 图结构

`autoBMAD/docuswarm/pipeline/graph.py` 中的 `create_pipeline_graph` 定义了状态机：

```python
# 将五个节点都加入图
for node_id in PIPELINE_NODES:
    node_executor = _create_default_node_executor(node_id)
    graph.add_node(node_id, node_executor)

# 起点连接到 analyst
graph.add_edge("__start__", "analyst")

# 依次连接 analyst → pm → ux → architect → po
for i in range(len(PIPELINE_NODES) - 1):
    current_node = PIPELINE_NODES[i]
    next_node = PIPELINE_NODES[i + 1]
    graph.add_edge(current_node, next_node)

# 最后 po → __finalize__ → END
graph.add_edge("po", "__finalize__")
graph.add_edge("__finalize__", END)
```

因此：

- 一旦通过 `start_pipeline` 触发 graph 执行，**第一个执行节点一定是 `analyst`**；
- 后续节点严格按上述顺序流转；
- 最终进入 `__finalize__` 节点并结束。

### 4.3 current_node 的预期变化

结合 Orchestrator、StateManager 与 LangGraph 的设计意图：

1. `start_pipeline` 将 `current_node` 置为 `analyst`，`status` 置为 `running`；
2. 随着 LangGraph 执行到每个节点，对应的 `current_node` 会被更新（以及 `node_results` 写入）；
3. 流水线完成后：
   - `status` 更新为 `completed`；
   - 最后一个 `current_node` 保留为最后执行的节点，用于调试和审计。

这就是 README 示例中显示 `Current Node = pm` 的来源（展示的是“当前/最近的执行节点”）。

---

## 五、正确的操作路径：如何让它真正从 analyst 开始执行

### 5.1 必要前置条件

1. **环境变量配置**（`.env`）：

   ```env
   KIMI_API_KEY=你的_kimi_key
   DOCUSWARM_DB_PATH=docuswarm.db      # 可选，默认即为该值
   DOCUSWARM_OUTPUT_DIR=output        # 可选
   ```

2. **上下文文件准备**：

   - 按 README 建议，准备一个 `docs/epics/EPIC-01.md` 或 `docs/proposal.md` 之类的输入文档；
   - 该文档内容会作为 `subject_context` 的一部分，供各节点 Agent 使用。

### 5.2 推荐的启动方式：通过 HybridOrchestrator 启动全流水线

由于当前 CLI 的 `start` 命令只创建数据库记录，并没有调用 `HybridOrchestrator.start_pipeline`，因此要真正执行流水线，建议：

1. **编写一个简单的运行脚本（示例）**：

   ```python
   # 示例：run_docuswarm_pipeline.py

   import asyncio
   from pathlib import Path

   from autoBMAD.docuswarm.pipeline import HybridOrchestrator


   async def main() -> None:
       # 1. 读取上下文文件
       ctx_path = Path("docs/proposal.md")  # 根据实际路径调整
       content = ctx_path.read_text(encoding="utf-8")

       # 2. 构建 subject_context
       subject_context = {
           "subject": ctx_path.stem,              # 如 "proposal"
           "context_file": str(ctx_path),
           "content": content,
       }

       # 3. 创建 Orchestrator（会使用 .env / config 中的配置）
       orchestrator = HybridOrchestrator()

       # 4. 启动流水线
       pipeline_id = await orchestrator.start_pipeline(subject_context)

       print("pipeline_id =", pipeline_id)


   if __name__ == "__main__":
       asyncio.run(main())
   ```

2. **在虚拟环境中执行脚本**：

   ```bash
   (venv) PS D:\GITHUB\pptx-video> python run_docuswarm_pipeline.py
   ```

3. **使用 CLI 查看状态**：

   运行结束后，脚本会输出一个新的 `pipeline_id`，例如：

   ```text
   pipeline_id = pipeline-1771817617511-a6eea25d
   ```

   然后使用 CLI 查看状态：

   ```bash
   python -m autoBMAD.docuswarm status pipeline-1771817617511-a6eea25d
   ```

   这时：

   - 如果流水线正在执行中：
     - `Status` 应为 `running`；
     - `Current Node` 会是当前正在运行或最近运行完的真实节点名（`analyst` / `pm` 等），而不是 `unknown`；
   - 如果执行已完成：
     - `Status` 为 `completed`；
     - `Current Node` 会停留在最后一个节点（`po`）。

### 5.3 现有“只创建不执行”的 pipeline 的处理建议

对于类似 `pipeline-1771817617511-a6eea25d` 这种：

- 仅通过 CLI `start` 创建、没有真正执行的流水线；
- 或者已经被 `resume` 写入 `current_node = "unknown"`；

建议的处理方式：

1. **作为历史记录保留**（调试用途）：
   - 无需强制删除，只要知道它从未实际跑过即可；
   - 使用 `list-pipelines` 时，可通过状态 / 创建时间进行过滤；

2. **如果影响观感，可用 clean 命令清理**：
   - 如需要定期清理无效流水线，可用：

   ```bash
   python -m autoBMAD.docuswarm clean --status pending --confirm
   ```

   或按 README 提供的定期清理策略，针对 `failed` / `cancelled` / 过旧的 `completed` 做归档和删除。

3. **不建议对 `current_node = "unknown"` 做手工更新**：
   - 这个字段是协同多个组件（Orchestrator / StateManager / LangGraph）共同管理的；
   - 手工更新容易和实际执行状态不一致，除非是一次性数据修复脚本，并有充分审计。

---

## 六、结论与后续建议

1. **`Current Node = unknown` 的本质含义**：
   - 该流水线记录从未通过 `HybridOrchestrator.start_pipeline` 启动过；
   - 后续某次 `resume` 调用将空的 `current_node` 替换成占位字符串 `"unknown"` 并写入数据库；
   - 因此，这不是在执行某个叫 `unknown` 的节点，而是“无真实当前节点”的一种编码方式。

2. **要让流水线真正从 `analyst` 开始顺序执行**：
   - 必须通过 **`HybridOrchestrator.start_pipeline(subject_context)`** 来启动；
   - CLI 的 `start` 目前只是“创建流水线元数据”，不负责触发 LangGraph 执行。

3. **操作层面的推荐实践**：
   - 开发 /测试环境中：
     - 使用一个专用的 Python 脚本调用 Orchestrator 来启动完整流水线；
     - 使用 CLI `status` / `list-pipelines` 做只读观察与调试；
   - 将来如有需要，可以考虑：
     - 在 CLI 中新增一个显式命令（例如 `run`），包装对 `HybridOrchestrator.start_pipeline` 的调用，实现“一条命令完成创建 + 执行”。

本报告可作为后续调试 DocuSwarm 流水线状态问题（尤其是 `Current Node` 异常值）时的参考基线文档。