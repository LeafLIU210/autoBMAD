# DocuSwarm P0/P1 测试驱动修复总方案

**依据**: `docs-doc/research/2026-04-29-docuswarm-p0-p1-deep-research-report.md`  
**目标**: 通过 TDD 方式修复 C1-C5 (Critical)、H1-H5 (High)、M1 (Medium) 全部问题  
**执行环境**: `.venv`  
**基准测试**: `tests/test_docuswarm_*.py` (当前 49 tests 全通过)

---

## 一、P0 — Critical 修复（恢复主链路可信度）

### C1: `_route_after_node` 同步路由 → async

**问题**: `graph.py:240` `_route_after_node` 是 `def` 而非 `async def`，在 async LangGraph 中通过 `run_in_executor` 调度，存在死锁风险。

**TDD 步骤**:
1. 修改 `graph.py`: 将 `_route_after_node` 改为 `async def`
2. 运行 `tests/test_docuswarm_p1_runtime_contract.py` 验证 fake-agent graph 仍通过
3. 运行全部 DocuSwarm 测试回归

### C2: `NodeToolPermissions` 补全 `shared_context` schema

**问题**: `nodes/loader.py:87` `NodeToolPermissions` 缺少 `shared_context` 字段，`tool_filter.py:171` 访问时抛 `AttributeError`。

**TDD 步骤**:
1. 在 `nodes/loader.py` 添加 `NodeSharedContextPermissions` dataclass
2. 在 `NodeToolPermissions` 添加 `shared_context` 字段（默认 disabled）
3. 在 `NodeLoader._build_node_config` 中解析 `tools.shared_context`
4. 新增测试 `test_node_tool_filter_default_permissions_do_not_raise`
5. 运行全部相关测试

### C3: StateManager 单一事实源闭合

**问题**: `update_pipeline_state` 只写 `state_json`，不更新顶层 `status/current_node`；`get_pipeline` 不返回 `state` key；`list_pipelines` 读取陈旧顶层字段。

**TDD 步骤**:
1. 修改 `StateManager.update_pipeline_state`: 同步更新顶层 `status`、`current_node`
2. 修改 `StateManager.get_pipeline`: 返回中保留 `"state": state`
3. 修改 `StateManager.list_pipelines`: 若按 status 过滤，使用 `json_extract(state_json, '$.status')` 或依赖同步后的顶层字段
4. 新增测试 `test_state_manager_get_and_list_status_are_consistent`
5. 新增测试 `test_get_pipeline_returns_flattened_fields_and_state_snapshot`

### C4: `start_pipeline` 自定义 pipeline_id

**问题**: `orchestrator.py:420` `final_pipeline_id = pipeline_id or db_pipeline_id`，但 DB row 用的是 `db_pipeline_id`，后续 `update_pipeline_state(final_pipeline_id)` 可能找不到。

**TDD 步骤**:
1. 修改 `StateManager.create_pipeline`: 接受可选 `pipeline_id` 参数，若提供则以此为主键
2. 运行现有测试验证不破坏默认行为
3. 新增测试 `test_start_pipeline_with_explicit_pipeline_id_creates_same_id`

### C5: graph.py 第二层 completed_nodes 维护删除

**问题**: `graph.py:149-158` 使用 `node_status != "failed"` 将非 failed 节点加入 `completed_nodes`，与 `PipelineAdapter` 的 `node_status == COMPLETED` 语义冲突。

**TDD 步骤**:
1. 删除 `graph.py:149-158` 的 completed_nodes 维护块（Adapter 已正确处理）
2. 新增测试 `test_graph_blocked_node_is_failed_not_completed`
3. 运行全部 graph 相关测试

---

## 二、P1 — High 修复（shared_context & 交付物闭环）

### H1: shared_context MCP 写入配置的数据库

**问题**: `update_context_sdk.py:99` `StateManager()` 无参实例化，写入默认 `docuswarm.db`。

**TDD 步骤**:
1. 修改 `create_update_context_server`: 接收 `db_path` 或 `state_manager` 参数
2. 修改 `NodeToolFilter.create_mcp_servers`: 传递 `db_path`
3. 修改 `UpdateContextTool`: 记录真实 `node_id` 到 history
4. 新增测试 `test_shared_context_mcp_writes_to_configured_db`

### H2: Graph 完成后完整状态写回 StateManager

**问题**: `orchestrator.py:477-480` 只持久化 `status`/`current_node`，遗漏 `completed_nodes`/`failed_nodes`/`deliverables`/`evaluations`/`docs_context_summary`。

**TDD 步骤**:
1. 修改 `orchestrator.start_pipeline`: graph 完成后将完整 `result` 写回 `update_pipeline_state`
2. 新增测试 `test_graph_result_persisted_to_state_manager`

### H3: StateManager 初始 state schema 统一

**问题**: `StateManager._create_initial_state()` 缺少 `failed_nodes` 和 `docs_context_summary`。

**TDD 步骤**:
1. 修改 `StateManager._create_initial_state`: 复用 `pipeline.state.create_initial_state()` 或补全缺失字段
2. 新增测试 `test_state_manager_initial_state_matches_pipeline_state`

### H4: `create_deliverable` 保留 metadata + 防覆盖

**问题**: `metadata` 参数未使用；同名 title 静默覆盖；中文 title 生成空 slug → `.md`。

**TDD 步骤**:
1. 修改 `create_deliverable`: 将 `metadata` 合入 `result_metadata`
2. 修改 `_slugify_filename`: 空 slug 时 fallback 到 `node_id` + hash
3. 修改 `create_deliverable`: 文件存在时生成唯一后缀
4. 新增测试 `test_deliverable_metadata_round_trip`
5. 新增测试 `test_deliverable_filename_collision_does_not_overwrite`

### H5: SQLite sync I/O async 语义统一

**问题**: `StateManager.update_pipeline_state` / `update_shared_context` 是 `async def` 但内部直接执行同步 SQLite。

**TDD 步骤**:
1. 修改 `StateManager`: 在 async 方法内部用 `asyncio.to_thread()` 包装同步 DB 操作
2. 运行全部测试验证无行为变化

---

## 三、P2 — Medium 修复（质量门禁）

### M1: Approval handler 默认 reject unknown

**问题**: `approval.py:74` `unknown_action_policy="approve"` 不符合最小权限。

**TDD 步骤**:
1. 修改 `DocuSwarmApprovalHandler.__init__`: 默认 `unknown_action_policy="reject"`
2. 新增测试 `test_approval_handler_rejects_unknown_action_by_default`
3. 运行全部测试

---

## 四、新增回归测试清单

```text
test_graph_fake_agents_full_pipeline_completes_without_llm   (C1)
test_graph_blocked_node_is_failed_not_completed               (C5)
test_node_tool_filter_default_permissions_do_not_raise        (C2)
test_shared_context_mcp_writes_to_configured_db               (H1)
test_shared_context_written_by_analyst_visible_to_pm          (H1)
test_state_manager_get_and_list_status_are_consistent         (C3)
test_get_pipeline_returns_flattened_fields_and_state_snapshot (C3)
test_start_pipeline_with_explicit_pipeline_id_creates_same_id (C4)
test_deliverable_metadata_round_trip                          (H4)
test_deliverable_filename_collision_does_not_overwrite        (H4)
```

---

## 五、执行顺序

1. **阶段 1**: C2 (schema 补全) → H3 (初始 state 统一) — 无依赖，先做
2. **阶段 2**: C5 (删除 graph 层重复逻辑) → C1 (async router) — graph 层
3. **阶段 3**: C3 (StateManager 一致性) → C4 (pipeline_id) — 存储层
4. **阶段 4**: H2 (完整状态写回) → H1 (shared_context DB) — 闭环层
5. **阶段 5**: H4 (deliverable) → H5 (async I/O) → M1 (approval) — 工具层
6. **阶段 6**: 全部测试回归 + ruff/basedpyright 清理

---

## 六、完成标准

- [ ] `pytest tests/test_docuswarm_*.py --no-cov --timeout=30` 全通过（含新增测试）
- [ ] `ruff check autoBMAD/docuswarm tests/test_docuswarm_*.py` 无 violations
- [ ] `basedpyright autoBMAD/docuswarm` errors 清零（至少 optional access 和 schema drift）
- [ ] 新增 10+ 个回归测试全部通过
