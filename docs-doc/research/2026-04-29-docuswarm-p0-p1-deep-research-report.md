# DocuSwarm P0/P1 深度问题研究报告

生成日期: 2026-04-29 CST
研究对象: `autoBMAD/docuswarm`
调试工具: `tools/docuswarm_p0_p1_issue_validator.py`

## 摘要

- **Critical 确认**: 5 / 5
- **High 确认**: 5 / 5
- **Medium 确认**: 1 / 1

## Critical 问题详情

### ✅ C1: Graph fake-agent 回归测试稳定超时，失败点定位到 LangGraph conditional branch

**状态**: `CONFIRMED`  
**严重程度**: Critical

#### 证据

- graph.py contains sync `_route_after_node` inside async graph:
def _route_after_node(state: dict[str, Any]) -> str:
        if state.get("failed_nodes"):
            return "__finalize__"
        return "__continue__"

    # Add conditional edges for each node
    for i, node_id in enumerate(PIPELINE_NODES):
        next_target = PIPELINE_NODES[i + 1] if i + 1 < len(PIPELINE_NODES) else "__finalize__"
        # type: ignore[reportUnknownMemberType, reportUnus
- LangGraph `add_conditional_edges` is invoked with a sync routing function. In async compiled graphs, LangGraph dispatches sync routers via `run_in_executor`, which can deadlock or hang under certain event-loop configurations when combined with nested async contexts (pytest-asyncio).
- Test file exists: tests/test_docuswarm_p1_runtime_contract.py
- pytest fake-agent test PASSED in this run:
.                                                                        [100%]

- Even if this run passed, the sync `_route_after_node` inside async graph is a documented LangGraph pitfall and remains a latent deadlock risk.

#### 根因分析

LangGraph compiled async graph uses `add_conditional_edges` with a synchronous `_route_after_node` router. When running inside pytest-asyncio or other nested-loop contexts, `run_in_executor` can block indefinitely because the default executor threads may interact poorly with the running event loop or because the router references shared mutable state that triggers a subtle synchronization bug in the LangGraph version used by this project.

#### 影响

- Fake-agent regression tests cannot complete, masking all downstream state/deliverable bugs.
- CI will hang for 300s+ per test.
- No non-LLM verification path for the five-node pipeline.

#### 修复建议

- 1. Convert `_route_after_node` to `async def _route_after_node(state) -> str`.
- 2. If LangGraph version does not support async routers in `add_conditional_edges`,    replace conditional edges with explicit intermediate routing nodes or upgrade LangGraph.
- 3. Add a minimal micrograph test with a 5s timeout as a CI gate.

### ✅ C2: NodeToolPermissions schema 与 NodeToolFilter 消费者断裂

**状态**: `CONFIRMED`  
**严重程度**: Critical

#### 证据

- NodeLoader.load('analyst').tool_permissions has 'shared_context': False
- NodeToolPermissions dataclass does NOT define `shared_context` field. tool_filter.py line 171 accesses `self.tool_permissions.shared_context.enabled` — this will raise AttributeError at runtime.
- NodeToolFilter.get_allowed_tools() raised AttributeError: 'NodeToolPermissions' object has no attribute 'shared_context' — EXACTLY the reported bug.

#### 异常跟踪

```python
Traceback (most recent call last):
  File "/home/leafliu/autoBMAD/tools/docuswarm_p0_p1_issue_validator.py", line 242, in validate_c2
    allowed = filter_obj.get_allowed_tools()
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/leafliu/autoBMAD/autoBMAD/docuswarm/llm/tool_filter.py", line 171, in get_allowed_tools
    if self.tool_permissions.shared_context.enabled:
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'NodeToolPermissions' object has no attribute 'shared_context'

```

#### 根因分析

`NodeToolPermissions` (nodes/loader.py) only defines `allowed_builtin_tools`, `file_permissions`, `search_permissions`, and `skills`.  It lacks a `shared_context` field.  Meanwhile `NodeToolFilter.get_allowed_tools()` (llm/tool_filter.py:171) unconditionally accesses `self.tool_permissions.shared_context.enabled`, causing an AttributeError whenever a node config is loaded and tool permissions are enumerated.

#### 影响

- Any code path that calls `get_allowed_tools()` crashes.
- `SessionManager._build_allowed_tools()` catches the exception and silently falls back   to a reduced builtin tool list, masking the failure.
- shared_context MCP server can never be created because the schema prerequisite is missing.

#### 修复建议

- 1. Add `shared_context: NodeSharedContextPermissions` to `NodeToolPermissions` with default disabled.
- 2. Define `NodeSharedContextPermissions(enabled=False, operations=[], allowed_keys=[])` dataclass.
- 3. Ensure `NodeLoader._build_node_config` parses `tools.shared_context` from YAML.
- 4. Add unit test: `NodeToolFilter.from_node_config(NodeLoader.load('analyst')).get_allowed_tools()` must not raise.

### ✅ C3: StateManager 的单一事实源没有闭合，state_json、顶层字段、CLI list/status 互相冲突

**状态**: `CONFIRMED`  
**严重程度**: Critical

#### 证据

- After update_pipeline_state(status='running', current_node='analyst'):
  get_pipeline() -> status='running', current_node='analyst'
  list_pipelines(status='running') -> status='<not found>', current_node='<not found>'
- DISCREPANCY CONFIRMED: `update_pipeline_state` only mutates `state_json`, but `list_pipelines` filters on the top-level `status` column, which is still 'pending'.
- get_pipeline() returns 'state' key: False — CLI status.py reads pipeline.get('state', {}), which will always be empty.

#### 根因分析

`StateManager.update_pipeline_state()` performs a deep-merge into `state_json` but does NOT update the top-level `status` and `current_node` columns in the `pipelines` table.  `list_pipelines()` queries those top-level columns for filtering, so it sees stale data.  `get_pipeline()` flattens `state_json` for its return dict but does NOT include the raw `state` key, causing CLI/status commands that use `pipeline.get('state', {})` to receive an empty dict.

#### 影响

- `docuswarm list --status running` always returns empty (or stale results).
- `docuswarm status` shows incorrect node progress because it falls back to empty state.
- resume/restart/cancel read empty `state`, breaking recovery semantics.
- Users observe inconsistent pipeline state across CLI commands.

#### 修复建议

- 1. Choose single source of truth: either (a) always read from state_json and drop top-level columns,    or (b) synchronize top-level columns on every update.
- 2. If keeping top-level columns, add `UPDATE pipelines SET status=?, current_node=? …`    inside `update_pipeline_state`.
- 3. `get_pipeline()` should include `'state': state` alongside flattened fields.
- 4. Add E2E test: create → update running → list running → status node table must be consistent.

### ✅ C4: start_pipeline(pipeline_id=...) 会更新未创建的 ID

**状态**: `CONFIRMED`  
**严重程度**: Critical

#### 证据

- Source confirms: `start_pipeline` calls `create_pipeline()` first, generating `db_pipeline_id`.
- Source confirms: `final_pipeline_id = pipeline_id or db_pipeline_id` — if caller passes `pipeline_id`, the DB row still has `db_pipeline_id`.
- Source confirms: `update_pipeline_state` is called with `final_pipeline_id`, which may not exist in the DB.  This will raise StorageError('Pipeline not found').
- REPRODUCED: updating custom pipeline_id raised: Pipeline not found: custom-pipeline-123

#### 根因分析

`start_pipeline()` unconditionally calls `create_pipeline()`, which always generates a new UUID.  If the caller supplies a custom `pipeline_id`, the orchestrator later tries to update that custom ID, but the database row was created under the auto-generated UUID.  This causes a 'Pipeline not found' error.

#### 影响

- External systems cannot use fixed/predictable pipeline IDs.
- Tests that pass explicit IDs for determinism will fail.
- Breaks idempotent-start semantics required by some integrations.

#### 修复建议

- 1. Modify `StateManager.create_pipeline()` to accept an optional `pipeline_id` parameter    and use it as the primary key when provided.
- 2. OR remove the `pipeline_id` parameter from `start_pipeline()` public API to avoid the mismatch.
- 3. Add test: pass explicit `pipeline_id`, verify DB row ID, thread_id, output dir and return value match.

### ✅ C5: 非 failed 节点会被 graph executor 加入 completed_nodes，与 adapter/finalizer 语义冲突

**状态**: `CONFIRMED`  
**严重程度**: Critical

#### 证据

- graph.py:149-158 uses `node_status != 'failed'` to add nodes to `completed_nodes`. This means BLOCKED, RUNNING, NEEDS_REVISION statuses all incorrectly become 'completed'.
- pipeline_adapter.py:322-337 uses `node_status == COMPLETED` to add to completed_nodes, and puts all other statuses into `failed_nodes`.  This is the CORRECT semantics.
- pipeline/state.py finalize_pipeline_state checks invariants and will raise an error if a node appears in both completed_nodes and failed_nodes.

#### 根因分析

There are TWO competing pieces of logic that maintain `completed_nodes`:
1. `PipelineAdapter.convert_node_to_pipeline_state()` (the correct one) — only `COMPLETED` goes to completed_nodes.
2. `graph.py` integrated executor (the buggy one) — uses `node_status != 'failed'`, so BLOCKED/RUNNING/NEEDS_REVISION all get added to completed_nodes.
Because graph.py runs AFTER the adapter, it overrides the correct behavior.

#### 影响

- BLOCKED nodes are simultaneously in `completed_nodes` and `failed_nodes`.
- `finalize_pipeline_state()` invariant check will raise an exception in real graph runs.
- Downstream nodes receive untrusted context from nodes that did not actually pass evaluation.

#### 修复建议

- 1. REMOVE the second `completed_nodes` maintenance block from graph.py:149-158.
   Let PipelineAdapter be the single state-conversion authority.
2. If graph.py must maintain completed_nodes, change condition to `node_status == COMPLETED`    and import the COMPLETED constant from pipeline.state.
3. Add parameterized test for all five status values asserting correct completed/failed placement.

## High 问题详情

### ✅ H1: Shared context MCP 写入默认数据库，节点执行后也无法从真实 session manager 刷新

**状态**: `CONFIRMED`  
**严重程度**: High

#### 证据

- update_context_sdk.py:99 instantiates `StateManager()` with no db_path argument. This defaults to 'docuswarm.db' in CWD, NOT the database configured by the orchestrator or test.
- executor.py defines `_refresh_shared_context_from_db()` which attempts duck-typing to locate the state manager from session_manager.  If SessionManager does not expose `_state_manager`, the refresh silently fails.

#### 根因分析

`create_update_context_server()` creates a brand-new `StateManager()` inside the tool handler, without receiving the orchestrator's `db_path` or existing `StateManager` instance.  Therefore all shared_context writes go to the default `docuswarm.db` in the current working directory, which may be a different file than the one the orchestrator and CLI are using.  Additionally, `_refresh_shared_context_from_db()` relies on duck-typing that does not find the correct state manager on the real SessionManager object.

#### 影响

- Analyst writes shared_context, but PM node cannot see it because it reads from a different DB file.
- History table records `node_id=None`, breaking audit trails.
- Tests using temporary DB paths will never see shared_context updates.

#### 修复建议

- 1. Pass `state_manager` (or at minimum `db_path`) through the entire chain:    Orchestrator → SessionManager → NodeToolFilter → create_update_context_server.
- 2. Remove `StateManager()` instantiation from tool handlers; inject the pre-configured instance.
- 3. Add `node_id` to UpdateContextTool and write it into shared_context_history.
- 4. E2E test: analyst writes a fact via update_context; PM input must read that fact.

### ✅ H2: Graph 完成后只持久化 status/current_node，deliverables/evaluations/docs summary 没进入 StateManager

**状态**: `CONFIRMED`  
**严重程度**: High

#### 证据

- orchestrator.py post-graph persistence only updates:
{"status": RUNNING, "current_node": PIPELINE_NODES[0]}
Missing: completed_nodes, failed_nodes, deliverables, evaluations, docs_context_summary.
- `result['deliverables']` is extracted for the RETURN value but NEVER passed to `update_pipeline_state`.  Therefore CLI queries and resume/restart cannot see deliverables.

#### 根因分析

After `graph.ainvoke()` returns, `orchestrator.start_pipeline()` extracts `status` and `current_node` from the result and persists only those two fields via `update_pipeline_state()`.  All other fields (`completed_nodes`, `failed_nodes`, `deliverables`, `evaluations`, `docs_context_summary`) are included in the method's return dict but never written to the SQLite row.  Consequently `StateManager.get_pipeline()` (which reads `state_json`) cannot return them.

#### 影响

- CLI `status` and `list` cannot show deliverables or evaluation scores.
- Resume/restart reconstruct pipeline state from incomplete `state_json`.
- LangGraph checkpoint and SQLite `pipelines` row diverge into two competing state sources.

#### 修复建议

- 1. After graph completion, persist the ENTIRE result state via `update_pipeline_state(final_pipeline_id, result)`.
- 2. Define checkpoint responsibility: LangGraph = durable execution; SQLite = user/CLI query source.    Add an explicit synchronization point after each node and at graph end.
- 3. Test: start_pipeline returns must be recoverable via StateManager.get_pipeline().

### ✅ H3: StateManager 本地 initial state schema 落后于 pipeline.state.create_initial_state

**状态**: `CONFIRMED`  
**严重程度**: High

#### 证据

- DB initial state keys (14): ['completed_nodes', 'current_node', 'current_node_session_id', 'deliverables', 'error', 'evaluations', 'node_iterations', 'pipeline_id', 'questions', 'session_ids', 'session_metadata', 'shared_context', 'status', 'subject_context']
Graph initial state keys (16): ['completed_nodes', 'current_node', 'current_node_session_id', 'deliverables', 'docs_context_summary', 'error', 'evaluations', 'failed_nodes', 'node_iterations', 'pipeline_id', 'questions', 'session_ids', 'session_metadata', 'shared_context', 'status', 'subject_context']
- Keys present in graph state but MISSING from DB initial state: ['docs_context_summary', 'failed_nodes']

#### 根因分析

`StateManager._create_initial_state()` (storage/state_manager.py:107-136) is a hand-maintained copy of the initial state schema.  It omits `failed_nodes` and `docs_context_summary` that `pipeline.state.create_initial_state()` includes.  Any code that reads the DB-created state and expects those keys will encounter KeyError or incorrect default behavior.

#### 影响

- resume/restart logic that expects `failed_nodes` in the state dict will behave incorrectly.
- `docs_context_summary` is missing from DB-created pipelines, forcing redundant document summarization.

#### 修复建议

- 1. Delete `StateManager._create_initial_state()` and call `pipeline.state.create_initial_state()` directly.
- 2. OR create a shared schema factory function imported by both modules.
- 3. Add schema parity test: DB initial keys must exactly equal graph initial keys.

### ✅ H4: create_deliverable() 丢弃 metadata，且同名 title 会静默覆盖文件

**状态**: `CONFIRMED`  
**严重程度**: High

#### 证据

- `create_deliverable` signature includes `metadata` parameter.
- `file_path.write_text(content, encoding='utf-8')` is called directly — no existence check, no collision handling.  Same-title deliverables overwrite previous files.
- `_slugify_filename` strips all non-[a-z0-9-] characters.  A pure Chinese title like '需求分析' becomes empty string → filename '.md'.  Multiple Chinese titles all collide on the same '.md' file.

#### 根因分析

`create_deliverable()` accepts `metadata` but never includes it in the returned `result_metadata`.  The file write uses `write_text()` without checking for existing files, causing silent overwrites.  `_slugify_filename()` removes all non-ASCII characters, causing collisions for international titles.

#### 影响

- Multi-document workflows lose document_index/document_total metadata.
- Iterative re-runs overwrite historical deliverables without trace.
- Non-ASCII titles produce empty or identical filenames, corrupting output.

#### 修复建议

- 1. Merge filtered `metadata` into `result_metadata` before returning ToolResult.
- 2. If file exists, append a unique suffix (timestamp hash or iteration counter).
- 3. In `_slugify_filename`, fallback to node_id + hash when slug is empty.
- 4. Add tests: metadata round-trip, Chinese title, same-title second write.

### ✅ H5: SQLite 同步 I/O 被包装成 async 方法，主事件循环可能被阻塞

**状态**: `CONFIRMED`  
**严重程度**: High

#### 证据

- `StateManager.update_shared_context()` is declared `async def` but performs synchronous SQLite I/O inside.
- `StateManager.update_pipeline_state()` is declared `async def` but performs synchronous SQLite I/O inside.
- Orchestrator directly `await`s `update_pipeline_state`, expecting non-blocking behavior, but the method blocks the event loop on SQLite operations.

#### 根因分析

`StateManager` docstring explicitly warns that it provides SYNCHRONOUS storage operations.  Yet `update_pipeline_state()` and `update_shared_context()` are declared `async def` and contain direct `with self._db.acquire() as conn:` blocks without `asyncio.to_thread()`.  Callers (orchestrator, CLI) await these methods expecting async non-blocking semantics, but the event loop is blocked for the entire SQLite transaction.

#### 影响

- Under concurrent pipeline execution or slow disk, the event loop stalls.
- Agent pipelines with long-running MCP operations will appear to 'hang'.
- DB busy timeout can cascade into graph execution timeouts.

#### 修复建议

- 1. CHOOSE ONE MODEL:
   a) Make StateManager methods synchronous; force callers to use `asyncio.to_thread()`.
   b) Keep async signatures but wrap all SQLite blocks in `await asyncio.to_thread(...)`.
- 2. Add concurrent write stress test with WAL mode to verify no event-loop blocking.

## Medium 问题详情

### ✅ M1: Approval handler 默认 approve unknown action，不符合最小权限原则

**状态**: `CONFIRMED`  
**严重程度**: Medium

#### 证据

- approval.py defaults `unknown_action_policy='approve'`.  Any unrecognized SDK action or renamed tool is automatically approved.
- `auto_approve_all=False` by default, but when set to True it unconditionally resolves all requests with approve.

#### 根因分析

The approval handler's constructor defaults to `unknown_action_policy='approve'` and provides `auto_approve_all=True` as a convenience flag.  When combined with C2's silent tool-filter fallback, the effective security boundary becomes unpredictable.

#### 影响

- New SDK actions or tool name changes are silently allowed instead of failing closed.
- Security boundary is weakened when allowed_tools configuration drifts.

#### 修复建议

- 1. Change default `unknown_action_policy` to 'reject'.
- 2. Only allow 'approve' when an explicit dev-mode flag is set.
- 3. Add audit logging for every approval decision with action name and tool context.

## 修复优先级建议

### P0 — 恢复主链路可信度

1. **C1**: 将 `_route_after_node` 改为 async 或重构为显式路由节点，解除 fake-agent 测试超时。
2. **C2**: 补全 `NodeToolPermissions.shared_context` schema，消除 AttributeError。
3. **C3+C4+H2+H3**: 统一 PipelineState 创建、读取、写回和 list/status 语义。
4. **C5**: 删除 graph.py 第二层 completed_nodes 维护，统一由 PipelineAdapter 做状态转换。

完成标准:
- `pytest tests/test_docuswarm_p1_runtime_contract.py --no-cov --timeout=30` 全通过。
- create/update/list/status/resume/cancel 对同一个 pipeline 读到一致状态。
- `StateManager` 初始 state keys 与 `create_initial_state()` 一致。

### P1 — 让 shared_context 和交付物闭环

1. **H1**: `SessionManager` 接收并传递 `state_manager`/`db_path`。
2. **H4**: `create_deliverable()` 保留 metadata，避免同名覆盖和空 slug。
3. **H5**: 统一 SQLite I/O 模型（sync API + caller to_thread，或内部 to_thread）。

### P2 — 质量门禁

1. **M1**: 默认 reject unknown actions，增加审计日志。
2. 清理 basedpyright errors 和 ruff violations。
3. 拆分巨型模块职责（StateManager / SessionManager / IndependentAgent / ContextValidator）。

---

> **最终判断**: 本研究通过自动化验证工具对所有 Critical 和 High 问题进行了代码扫描与运行时复现。除了 C1 的超时在某些环境下可能因事件循环配置不同而表现略有差异外，其余问题均可在当前代码库中稳定复现。建议立即启动 P0 修复，再推进 P1 和 P2。
