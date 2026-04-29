# 2026-04-29 DocuSwarm 深度代码审查与运行时评估报告

审查对象：`autoBMAD/docuswarm`  
目标目录：`docs-doc/evaluation`  
审查日期：2026-04-29 CST（工作区本地时间）  
审查方法：`code-review-pro` 安全/性能/维护性审查 + `systematic-debugging` 失败复现与根因定位  
基准说明：当前工作区存在大量未提交迁移和文档搬迁改动。本报告只评价当前可见工作区状态，不假设这些改动已经进入稳定主干。

## 结论摘要

`autoBMAD/docuswarm` 的功能骨架已经很完整：CLI、LangGraph pipeline、节点执行器、Claude Agent SDK session、MCP 工具、SQLite 状态和共享上下文都有实现。但当前最主要风险不是“缺少功能”，而是运行时合同没有闭环：图执行、节点状态、SQLite `state_json`、数据库顶层字段、CLI 状态展示、MCP shared_context 写入链路之间存在多处断裂。

本次审查的总体健康评分：**34 / 100**。

优先级判断：

- P0：修复 graph 运行时超时、节点工具权限 schema 断裂、状态持久化单一事实源断裂、非 completed 节点被错误完成的问题。
- P1：修复 shared_context MCP 写错数据库/无法刷新、CLI list/status 读取陈旧字段、交付物文件覆盖和元数据丢失。
- P2：清理类型错误、lint 债务、重复 SDK/legacy 工具实现、巨型模块和薄弱测试。

最小可执行判断：**不建议重写 DocuSwarm，但当前不应宣称主 pipeline 可可靠运行。** 应当先做一轮运行时合同修复和回归测试加固，再继续扩展 Agent 能力。

## 验证结果

### 已执行命令

```text
.venv/bin/python -m compileall -q autoBMAD/docuswarm
结果：通过

.venv/bin/ruff check autoBMAD/docuswarm tests/test_docuswarm_*.py tests/test_node_config_tool_permissions.py --statistics
结果：失败，77 个 lint violations

.venv/bin/basedpyright autoBMAD/docuswarm
结果：失败，32 errors, 227 warnings

.venv/bin/python -m pytest tests/test_docuswarm_p1_runtime_contract.py::TestGraphExecutionWithFakeAgents::test_graph_execution_with_fake_agents --no-cov --tb=short -q --timeout=20
结果：失败，20 秒超时
```

前序批量验证同样显示 `tests/test_docuswarm_p1_runtime_contract.py` 中两个 fake-agent graph 测试超时；其余被选中的 DocuSwarm 测试大多通过，但无法覆盖当前 P0 问题。

### Ruff 统计

```text
30 F401  unused-import
19 E402  module-import-not-at-top-of-file
15 I001  unsorted-imports
 6 W293  blank-line-with-whitespace
 3 F811  redefined-while-unused
 2 W291  trailing-whitespace
 2 UP041 timeout-error-alias
```

这批问题大多是机械清理，但它们说明近期迁移代码还没有经过稳定的质量门禁。

### Basedpyright 高信号错误

主要错误集中在：

- `autoBMAD/docuswarm/agents/independent.py:384`、`:1010`、`:1013`：`node_config.tool_permissions` 可能为 `None`。
- `autoBMAD/docuswarm/context/isolation.py:170` 到 `:172`、`:233` 到 `:234`：`task` 可能为 `None`。
- `autoBMAD/docuswarm/prompts/contract_builder.py:166`、`:189` 到 `:191`、`:744`、`:770` 到 `:771`：prompt contract 假设 optional 字段一定存在。
- `autoBMAD/docuswarm/cli/main.py:77` 到 `:89`：Click 装饰器后的类型推断与真实调用边界不匹配。
- `autoBMAD/docuswarm/tools/create_deliverable_sdk.py:171`：`metadata` 参数未使用，和多文档 MCP handler 的设计意图冲突。

## 代码规模与风险轮廓

`autoBMAD/docuswarm` 当前 Python 代码约 **27,863 行**。最大热点文件：

| 文件 | 行数 | 风险判断 |
| --- | ---: | --- |
| `context/validator.py` | 1,960 | 规则、策略、格式校验集中，回归面大 |
| `storage/state_manager.py` | 1,309 | pipeline、node result、shared_context、history 混合 |
| `llm/session_manager.py` | 1,255 | SDK options、MCP、allowed_tools、session lifecycle 混合 |
| `agents/independent.py` | 1,198 | prompt、skills、tool permissions、session 切换、解析混合 |
| `pipeline/orchestrator.py` | 1,119 | start/resume/restart/cancel/checkpoint/state update 混合 |
| `prompts/contract_builder.py` | 920 | schema 映射、模板、fallback 混合 |
| `nodes/dual_agent.py` | 899 | 双 agent loop 和终止语义复杂 |

这些文件不只是“大”，而是承担了跨层合同，导致一个字段或状态语义变更会同时影响 CLI、Graph、DB、Agent 和测试。

## Critical Issues

### C1. Graph fake-agent 回归测试稳定超时，失败点定位到 LangGraph conditional branch

严重性：Critical  
影响范围：核心 pipeline 可运行性、CI、无 LLM 回归测试、故障定位  

证据：

- 复现命令：`pytest tests/test_docuswarm_p1_runtime_contract.py::TestGraphExecutionWithFakeAgents::test_graph_execution_with_fake_agents --timeout=20`
- 测试卡在 `graph.ainvoke(...)`：`tests/test_docuswarm_p1_runtime_contract.py:52`
- timeout stack 显示挂在 LangGraph `Branch._aroute`，随后等待 `langchain_core.runnables.config.run_in_executor`。
- graph conditional edge 定义在 `autoBMAD/docuswarm/pipeline/graph.py:240` 到 `:253`。
- stdout 只显示 `using_integrated_node_executor`，fake 全流程没有完成。

根因定位：

这不是 Claude SDK、API key 或真实 LLM 问题；fake executor 已经绕开 LLM。问题发生在 LangGraph 节点执行后的 conditional branch 路由阶段。当前 `_route_after_node` 是同步函数，LangGraph 在 async graph 中通过 executor 运行它；测试销毁时仍有 pending `Branch._aroute`/`run_in_executor` task。

影响：

- 不能用 fake agents 验证五节点主链路。
- `pytest` 默认 timeout 是 300 秒，真实 CI 会长时间挂起。
- 这会掩盖节点状态、deliverables、failed_nodes 等合同错误，因为 graph 根本没有稳定返回。

建议：

1. 先用最小 LangGraph micrograph 复现“async node + sync conditional route”的行为，确认是当前 LangGraph 版本交互问题还是 DocuSwarm state schema 触发。
2. 在修复前，把 runtime contract 测试 timeout 降到 20-30 秒，避免 CI 长挂。
3. 若 micrograph 证实同步 router 是触发点，改成 LangGraph 当前版本推荐的 async route 或替代控制流；修复后保留 fake-agent 全图测试作为 P0 gate。

### C2. `NodeToolPermissions` schema 与 `NodeToolFilter` 消费者断裂，工具 allowlist 分支会抛 `AttributeError`

严重性：Critical  
影响范围：MCP server 创建、allowed_tools、shared_context、Agent 工具权限  

证据：

- `NodeToolPermissions` 只定义了 `allowed_builtin_tools`、`file_permissions`、`search_permissions`、`skills`：`autoBMAD/nodes/loader.py:87` 到 `:93`。
- `NodeToolFilter.get_allowed_tools()` 直接访问 `self.tool_permissions.shared_context.enabled`：`autoBMAD/docuswarm/llm/tool_filter.py:170` 到 `:175`。
- `NodeToolFilter.create_mcp_servers()` 也直接访问 `shared_context.operations` 和 `shared_context.allowed_keys`：`autoBMAD/docuswarm/llm/tool_filter.py:259` 到 `:267`。
- 当前 node yaml 中没有 `tools:` 段；`NodeLoader` 会构造默认 `NodeToolPermissions`：`autoBMAD/nodes/loader.py:342` 到 `:360`。

最小复现：

```text
from autoBMAD.nodes.loader import NodeLoader
from autoBMAD.docuswarm.llm.tool_filter import NodeToolFilter

c = NodeLoader.load("analyst")
hasattr(c.tool_permissions, "shared_context")  # False
NodeToolFilter.from_node_config(c).get_allowed_tools()
# AttributeError: 'NodeToolPermissions' object has no attribute 'shared_context'
```

影响：

- 工具权限快照不是“缺少配置时禁用 shared_context”，而是运行时异常。
- `SessionManager._build_allowed_tools()` 会 catch 异常后退回已收集的 builtin tools：`autoBMAD/docuswarm/llm/session_manager.py:275` 到 `:300`，容易形成静默降级。
- shared_context MCP server 当前没有稳定启用路径。
- 现有 `tests/test_node_config_tool_permissions.py` 只断言 `NodeToolFilter` 对象存在，没有调用 `get_allowed_tools()`，所以测试没有覆盖断点。

建议：

1. 给 `NodeToolPermissions` 增加明确的 `shared_context` dataclass，默认 `enabled=False`、`operations=[]`、`allowed_keys=[]`。
2. `NodeToolFilter` 访问前使用 typed default，而不是 `hasattr` 式容错。
3. 增加测试：`NodeToolFilter.from_node_config(NodeLoader.load("analyst")).get_allowed_tools()` 必须不抛异常，且输出等于配置展开结果。

### C3. StateManager 的单一事实源没有闭合，`state_json`、顶层字段、CLI list/status 互相冲突

严重性：Critical  
影响范围：start/status/list/resume/restart/cancel、用户可见状态、恢复能力  

证据：

- `create_pipeline()` 生成数据库 ID 并写入 `state_json`：`autoBMAD/docuswarm/storage/state_manager.py:155` 到 `:166`。
- `update_pipeline_state()` 只更新 `state_json` 和 `updated_at`，不更新顶层 `pipelines.status/current_node`：`autoBMAD/docuswarm/storage/state_manager.py:845` 到 `:851`。
- `list_pipelines()` 查询和过滤的是顶层 `pipelines.status/current_node`：`autoBMAD/docuswarm/storage/state_manager.py:420` 到 `:443`。
- `get_pipeline()` 解析 `state_json` 后把字段 flatten 到顶层，但没有返回 `state` key：`autoBMAD/docuswarm/storage/state_manager.py:369` 到 `:393`。
- CLI status 读取 `pipeline.get("state", {})`，所以节点表永远拿不到 `completed_nodes/node_iterations`：`autoBMAD/docuswarm/cli/commands/status.py:41` 到 `:45`。
- Orchestrator resume/restart/cancel 同样读取 `pipeline.get("state", {})`：`autoBMAD/docuswarm/pipeline/orchestrator.py:546`、`:704`、`:1004`。

最小复现：

```text
create_pipeline -> update_pipeline_state({"status": "running", "current_node": "analyst"})
get_pipeline: running analyst
list_all: pending None
list_running: 0
```

影响：

- `docuswarm list --status running` 会漏掉真实 running pipeline。
- `docuswarm status` 的节点进度会错误显示 pending。
- resume/restart/cancel 会从空 state 推导当前节点和 session，导致恢复与取消不可用。
- 用户可能看到同一个 pipeline 在不同 CLI 命令中状态不一致。

建议：

1. 明确单一事实源：要么所有读取都从 `state_json` 派生，要么 `update_pipeline_state()` 同步维护顶层 columns。
2. `get_pipeline()` 应保留 `"state": state`，同时可继续提供 flattened fields。
3. `list_pipelines(status=...)` 若保留顶层字段，需要在每次状态更新时同步顶层 `status/current_node`；否则改为读取 `json_extract(state_json, '$.status')`。
4. 增加端到端测试：create -> update running -> list running -> status node table -> resume/cancel 都必须读到同一状态。

### C4. `start_pipeline(pipeline_id=...)` 会更新未创建的 ID

严重性：Critical  
影响范围：外部调用方、测试、自定义 pipeline ID、幂等启动  

证据：

- `start_pipeline()` 先调用 `create_pipeline()` 创建 `db_pipeline_id`：`autoBMAD/docuswarm/pipeline/orchestrator.py:414` 到 `:417`。
- 然后 `final_pipeline_id = pipeline_id or db_pipeline_id`：`autoBMAD/docuswarm/pipeline/orchestrator.py:420`。
- 随后用 `final_pipeline_id` 调 `update_pipeline_state()`：`autoBMAD/docuswarm/pipeline/orchestrator.py:423` 到 `:425`。
- 如果调用者传入 `pipeline_id`，数据库中实际只有 `db_pipeline_id`，`update_pipeline_state(final_pipeline_id)` 会报 pipeline not found。

影响：

- API 表面支持外部传入 pipeline ID，但实现路径不可用。
- 这会破坏外部系统追踪、自定义 ID、测试固定 ID 等场景。

建议：

1. `StateManager.create_pipeline()` 接收可选 `pipeline_id` 并以同一个 ID 创建 row。
2. 或者 `start_pipeline()` 不暴露 `pipeline_id` 参数。
3. 增加测试：传入固定 `pipeline_id` 后 DB row、LangGraph thread_id、output dir 和返回值必须一致。

### C5. 非 `failed` 节点会被 graph executor 加入 `completed_nodes`，与 adapter/finalizer 语义冲突

严重性：Critical  
影响范围：质量门禁、BLOCKED/NEEDS_REVISION、状态不变量、finalizer  

证据：

- `NodeExecutor` 对 `BLOCKED` 设置 `status = BLOCKED`：`autoBMAD/docuswarm/node_execution/executor.py:176` 到 `:183`。
- 对 `NEEDS_REVISION` 或 unknown verdict 保持 `status = RUNNING`：`autoBMAD/docuswarm/node_execution/executor.py:193` 到 `:202`。
- `PipelineAdapter.convert_node_to_pipeline_state()` 只有 `status == COMPLETED` 才加入 completed，否则加入 failed_nodes：`autoBMAD/docuswarm/node_execution/pipeline_adapter.py:322` 到 `:337`。
- 但 `pipeline/graph.py` 在 adapter 之后又用 `node_status != "failed"` 判断完成：`autoBMAD/docuswarm/pipeline/graph.py:149` 到 `:158`。

影响：

- `blocked` 或 `running` 会同时进入 `failed_nodes` 和 `completed_nodes`。
- `finalize_pipeline_state()` 明确禁止 failed/completed 交集：`autoBMAD/docuswarm/pipeline/state.py:325` 到 `:330`，因此真实 graph 可能在 finalizer 阶段抛 invariant error。
- 质量未达标节点可能污染为“已完成”，下游节点拿到不可信上下文。

建议：

1. 删除 `pipeline/graph.py:149` 到 `:158` 的第二套 completed_nodes 维护，让 `PipelineAdapter` 成为唯一状态转换点。
2. 如果要保留 graph 层维护，则必须使用 `node_status == COMPLETED`，并与 adapter 共享同一个常量。
3. 增加参数化测试：`completed/failed/blocked/running/needs_revision` 五类状态分别断言 `completed_nodes`、`failed_nodes`、`status`。

## High Priority Issues

### H1. Shared context MCP 写入默认数据库，节点执行后也无法从真实 session manager 刷新

严重性：High  
影响范围：跨节点记忆、上下文协作、审计历史、测试隔离  

证据：

- `create_update_context_server()` 在 tool handler 内部创建 `StateManager()`，没有接收 orchestrator 的 `db_path` 或当前 `StateManager`：`autoBMAD/docuswarm/tools/update_context_sdk.py:91` 到 `:101`。
- `StateManager()` 默认写 `docuswarm.db`：`autoBMAD/docuswarm/storage/state_manager.py:58` 到 `:67`。
- `_refresh_shared_context_from_db()` 试图从 `session_manager` 上 duck typing 找 state manager：`autoBMAD/docuswarm/node_execution/executor.py:382` 到 `:391`。
- 真实 `SessionManager` 没有稳定暴露 `_state_manager/storage/state_manager`：`autoBMAD/docuswarm/node_execution/executor.py:432` 到 `:472`。
- `IndependentAgent._create_pipeline_session_manager()` 只传 `pipeline_id`，不传 `db_path` 或 `state_manager`：`autoBMAD/docuswarm/agents/independent.py:1088` 到 `:1099`。

影响：

- 即使 C2 修复后启用了 shared_context，Agent 工具也可能写到 cwd 下的 `docuswarm.db`，而不是 CLI 配置或测试传入的数据库。
- 下游节点刷新不到刚写入的 shared_context。
- `shared_context_history` 表有审计能力，但 node_id 当前仍写 `None`：`autoBMAD/docuswarm/storage/state_manager.py:745` 到 `:750`。

建议：

1. `SessionManager` 显式接收 `state_manager` 或 `db_path`。
2. `NodeToolFilter.create_mcp_servers()` 把同一个 state manager/db path 传给 `create_update_context_server()`。
3. `UpdateContextTool` 增加 `node_id`，写 history 时记录真实节点。
4. 增加 E2E 测试：analyst 调 `update_context` 写事实，pm 输入必须读取到该事实，并且 history.node_id 为 `analyst`。

### H2. Graph 完成后只持久化 status/current_node，deliverables/evaluations/docs summary 没进入 StateManager

严重性：High  
影响范围：CLI status、resume/restart、事后审计、产物追踪  

证据：

- graph 返回完整 `result`：`autoBMAD/docuswarm/pipeline/orchestrator.py:472`。
- 但持久化时只更新 `status` 和 `current_node`：`autoBMAD/docuswarm/pipeline/orchestrator.py:477` 到 `:480`。
- 返回给调用方时才包含 `failed_nodes`、`completed_nodes`、`deliverables`：`autoBMAD/docuswarm/pipeline/orchestrator.py:488` 到 `:496`。
- `StateManager.get_pipeline()` 读取的是 `state_json`，不是 LangGraph checkpoint：`autoBMAD/docuswarm/storage/state_manager.py:312` 到 `:393`。

影响：

- CLI 后续查询看不到真实产物和评估。
- resume/restart 依赖旧 state_json，可能从空状态或半状态恢复。
- LangGraph checkpoint 与 SQLite pipeline row 形成两个状态源。

建议：

1. graph 完成或节点结束时，把完整 PipelineState 写回 `StateManager.update_pipeline_state()`。
2. 明确 checkpoint 的职责是 LangGraph durable execution，SQLite `pipelines.state_json` 是用户/CLI 查询源；两者需要同步点。
3. 增加测试：start_pipeline 返回的 `completed_nodes/deliverables/evaluations/docs_context_summary` 必须能从 `StateManager.get_pipeline()` 读回。

### H3. StateManager 本地 initial state schema 落后于 `pipeline.state.create_initial_state`

严重性：High  
影响范围：状态兼容、failed_nodes、docs_context_summary、恢复语义  

证据：

- `pipeline.state.create_initial_state()` 包含 `failed_nodes` 和 `docs_context_summary`：`autoBMAD/docuswarm/pipeline/state.py:108` 到 `:125`。
- `StateManager._create_initial_state()` 缺少这些字段：`autoBMAD/docuswarm/storage/state_manager.py:107` 到 `:136`。

影响：

- 数据库创建的初始 state 与 graph 创建的初始 state 不一致。
- 后续 merge 可能靠默认值“碰巧工作”，但 resume/restart/status 读取会出现字段缺失分支。

建议：

1. 删除 StateManager 的本地 copy，直接复用 `pipeline.state.create_initial_state()`，或建立共享 schema factory。
2. 增加 schema parity 测试：StateManager 初始 state keys 必须等于 PipelineState 初始 keys。

### H4. `create_deliverable()` 丢弃 metadata，且同名 title 会静默覆盖文件

严重性：High  
影响范围：多文档输出、hash 追踪、迭代产物、审计  

证据：

- `create_deliverable()` 接收 `metadata`：`autoBMAD/docuswarm/tools/create_deliverable_sdk.py:167` 到 `:172`。
- `metadata` 没有进入 `result_metadata`：`autoBMAD/docuswarm/tools/create_deliverable_sdk.py:198` 到 `:205`。
- MCP handler 把 `document_index/document_total/document_type` 合并进 metadata：`autoBMAD/docuswarm/tools/create_deliverable_sdk.py:332` 到 `:340`，但底层函数丢弃它。
- 文件名由 title slug 生成，`file_path.write_text()` 直接覆盖：`autoBMAD/docuswarm/tools/create_deliverable_sdk.py:184` 到 `:191`。
- `_slugify_filename()` 对全中文或全符号标题可能生成 `.md`：`autoBMAD/docuswarm/tools/create_deliverable_sdk.py:134` 到 `:148`。

影响：

- 多文档 workflow 返回值缺少文档序号/类型，总结和验证链路难以判断集合完整性。
- 同标题多次迭代会覆盖历史文件。
- 空 slug 会把多个标题都写到 `.md`。

建议：

1. 将安全过滤后的 `metadata` 合入返回值。
2. slug 为空时使用 node_id、document_type 或 hash fallback。
3. 文件存在时生成唯一后缀，或显式返回冲突错误。
4. 增加测试：metadata round-trip、中文标题、同标题二次写入。

### H5. SQLite 同步 I/O 被包装成 async 方法，主事件循环可能被阻塞

严重性：High  
影响范围：并发 pipeline、长运行 Agent、CLI 响应、测试超时  

证据：

- 文件头明确说明 `StateManager` 是同步存储操作，async 调用方应使用 `asyncio.to_thread()`：`autoBMAD/docuswarm/storage/state_manager.py:3` 到 `:6`。
- 但 `update_pipeline_state()` 是 `async def`，内部直接执行同步 SQLite 操作：`autoBMAD/docuswarm/storage/state_manager.py:793` 到 `:851`。
- `update_shared_context()` 同样是 async 外壳包同步 DB 操作：`autoBMAD/docuswarm/storage/state_manager.py:560` 到 `:760`。
- Orchestrator 直接 `await self._state_manager.update_pipeline_state(...)`：`autoBMAD/docuswarm/pipeline/orchestrator.py:423`、`:477`、`:1057`。

影响：

- async 调用语义误导，调用方以为不会阻塞事件循环。
- DB busy timeout 或磁盘慢时会卡住 Agent pipeline。

建议：

1. 选择一种模型：要么改回同步 API，由调用方显式 `to_thread`；要么内部 `await asyncio.to_thread(...)`。
2. 对 shared_context 更新增加并发写测试，验证 WAL/busy timeout 下不会阻塞 graph。

## Medium Priority Issues

### M1. Approval handler 默认 approve unknown action，不符合最小权限原则

严重性：Medium  
影响范围：Claude SDK 工具授权、安全审计  

证据：

- 默认 `unknown_action_policy="approve"`：`autoBMAD/docuswarm/llm/approval.py:69` 到 `:75`。
- 未知 action 最终直接 `request.resolve(self._unknown_action_policy)`：`autoBMAD/docuswarm/llm/approval.py:171` 到 `:178`。
- `auto_approve_all=True` 时无条件 approve：`autoBMAD/docuswarm/llm/approval.py:138` 到 `:147`。

影响：

- 新增 SDK action 或工具名变化时，默认会放行而不是失败关闭。
- 如果 allowed_tools 配置又发生 C2/H1 的静默降级，安全边界更不清晰。

建议：

1. unknown action 默认 reject。
2. 仅在明确开发模式下允许 approve unknown。
3. 对 Bash/Edit/写文件类 action 增加单独 allowlist 和审计日志。

### M2. `.env` 加载使用 `override=True`，可能覆盖进程环境

严重性：Medium  
影响范围：部署、安全配置、CI  

证据：

- `load_dotenv()` 显式 override 现有环境变量：`autoBMAD/docuswarm/config.py:46` 到 `:49`。

影响：

- CI/CD 或 shell 已注入的 `ANTHROPIC_API_KEY`、base URL 等可能被本地 `.env` 覆盖。
- 在多环境部署时容易误用旧凭证或测试配置。

建议：

1. 默认 `override=False`。
2. 如确需本地覆盖，提供显式 CLI/env 开关，例如 `DOCUSWARM_DOTENV_OVERRIDE=1`。
3. 在日志中记录 dotenv path，但不要记录敏感值。

### M3. 测试存在“文档式断言”，不能真正防回归

严重性：Medium  
影响范围：P0 状态机质量门禁  

证据：

- `tests/test_docuswarm_p0_state_invariants.py` 中 `assert "analyst" not in state["completed_nodes"] or True` 永远通过。
- `tests/test_node_config_tool_permissions.py` 只检查对象存在，没有调用 `get_allowed_tools()`。
- `tests/test_docuswarm_p1_cli_status.py` 大量 mock orchestrator，不验证真实 StateManager/CLI 读取一致性。

影响：

- 看起来有测试覆盖 P0 状态机和工具权限，但生产断点仍然存在。

建议：

1. 移除 `or True` 式断言。
2. 所有 schema consumer contract 测试必须调用真实 consumer 方法，而不仅检查 dataclass 字段。
3. 增加一个无 LLM、无 SDK 的完整 pipeline fake-agent 测试，并作为 CI 必跑。

### M4. 依赖与安全扫描不完整

严重性：Medium  
影响范围：供应链、可复现构建  

证据：

- `requirements*.txt` 是范围约束，没有 lockfile。
- 当前环境没有 `pip-audit` 可用；网络受限，未完成依赖漏洞扫描。
- `.venv` 中依赖版本满足范围，但无法证明可复现。

建议：

1. 生成并提交 lockfile，或使用 `uv.lock`/`requirements.lock`。
2. 在 CI 增加 `pip-audit` 或等价扫描。
3. 对 Claude SDK/LangGraph 这类运行时关键依赖设置兼容性 smoke test。

## Strengths

- `pipeline.state.finalize_pipeline_state()` 已经加入不变量校验，方向正确：`autoBMAD/docuswarm/pipeline/state.py:291` 到 `:352`。
- `DatabaseManager.get_instance()` 已按 resolved path 缓存，避免旧式全局单例污染：`autoBMAD/docuswarm/storage/database.py:64` 到 `:82`。
- SessionManager 对 Claude SDK subprocess close 有超时和 kill fallback：`autoBMAD/docuswarm/llm/session_manager.py:41` 到 `:79`。
- 文件/搜索工具整体有路径边界意识，使用专门 SDK MCP server 工厂，不是把任意文件系统能力裸露给 Agent。
- 结构化日志已经贯穿 orchestrator、node execution、session manager，利于后续做运行时诊断。

## 修复路线图

### P0：恢复主链路可信度

1. 修复 C1：用 micrograph 定位 LangGraph branch 超时，恢复 fake-agent 全图测试。
2. 修复 C2：补齐 `NodeToolPermissions.shared_context` schema，并让 `NodeToolFilter.get_allowed_tools()` 成为必跑测试。
3. 修复 C3/C4/H2/H3：统一 PipelineState 创建、读取、写回和 list/status 语义。
4. 修复 C5：删除 graph 层第二套 completed_nodes 维护，统一由 `PipelineAdapter` 做状态转换。

完成标准：

- `pytest tests/test_docuswarm_p1_runtime_contract.py --no-cov --timeout=30` 全通过。
- create/update/list/status/resume/cancel 对同一个 pipeline 读到一致状态。
- `StateManager` 初始 state keys 与 `create_initial_state()` 一致。

### P1：让 shared_context 和交付物闭环

1. `SessionManager` 接收并传递 `state_manager` 或 `db_path`。
2. `create_update_context_server()` 不再自行 `StateManager()`。
3. `update_shared_context()` 记录真实 `node_id`。
4. `create_deliverable()` 保留 metadata，避免同名覆盖和空 slug。

完成标准：

- analyst 写 shared_context，pm 能读到。
- history 表包含 pipeline_id、node_id、key、version。
- 多文档 tool result 包含 document metadata，且同 title 不覆盖。

### P2：质量门禁与债务压缩

1. 清零 `basedpyright` errors，至少先解决 optional member access 和 schema drift。
2. 清理 ruff 的 import/style 债务，避免迁移噪音继续堆积。
3. 拆分 `StateManager`、`SessionManager`、`IndependentAgent`、`ContextValidator` 的职责边界。
4. 收敛 legacy 和 SDK 双工具实现，保留一套 canonical contract。

## 建议的新增回归测试清单

```text
test_graph_fake_agents_full_pipeline_completes_without_llm
test_graph_blocked_node_is_failed_not_completed
test_node_tool_filter_default_permissions_do_not_raise
test_shared_context_mcp_writes_to_configured_db
test_shared_context_written_by_analyst_visible_to_pm
test_state_manager_get_and_list_status_are_consistent
test_get_pipeline_returns_flattened_fields_and_state_snapshot
test_start_pipeline_with_explicit_pipeline_id_creates_same_id
test_deliverable_metadata_round_trip
test_deliverable_filename_collision_does_not_overwrite
```

## 最终判断

当前 DocuSwarm 不缺少“架构方向”，缺的是运行时合同收敛。最值得保留的是 LangGraph pipeline、StateManager、SessionManager、MCP tool factory、PipelineAdapter 这些边界；最需要立即修的是这些边界之间的字段和状态语义。

只要先把 P0 的图执行、工具权限 schema、状态持久化和完成语义修掉，系统可以继续增量演进。若跳过这些问题继续做功能扩展，后续每个 Agent 能力都会建立在不可信的 pipeline 状态上，调试成本会持续放大。
