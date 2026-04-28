# DocuSwarm WinError 5 与架构重构评估报告

**日期**: 2026-04-28  
**评估对象**: `autoBMAD/docuswarm`  
**触发问题**: `python -m autoBMAD.docuswarm start --context docs/calc-one-plus-one/calc-context.md` 在 Windows 环境中所有节点创建 Claude SDK session 失败，真实日志出现 `[WinError 5] 拒绝访问`。  
**评估问题**: 是否应当对 `autoBMAD/docuswarm` 进行架构重构？

## 结论摘要

应当进行架构重构，但不是全量重写。

最小充分的判断是：`WinError 5` 的直接触发点在 Claude Agent SDK 通过 `anyio.open_process()` 启动 `claude.exe` 的异步子进程路径；它不是缺少 `claude.exe`、不是单个业务节点失败，也不是 LangGraph 本身的根因。直接迁移到 TypeScript、替换 LangGraph、或者自研完整 agent loop，都超过了当前证据所要求的改动范围。

但是，当前 `docuswarm` 把 SDK transport、MCP/Skills 配置、session 生命周期、节点执行、LangGraph 状态、数据库状态混在主路径上，导致一个底层启动能力故障被放大为五个节点全部失败，并在图结果中出现 `completed_nodes` 与 `failed_nodes` 同时包含全部节点、`status=completed` 与 `error` 并存的矛盾状态。因此建议做**边界型、测试驱动的架构重构**：

1. P0：增加运行时能力预检和 fail-fast 诊断，专门识别 Windows 下 `anyio.open_process`/SDK transport 无法启动的情况。
2. P0：修正 LangGraph 节点完成语义，禁止失败节点进入 `completed_nodes`，禁止 finalizer 盲目标记完成。
3. P1：引入 `AgentRuntime`/`LLMProvider` 边界，把 Claude Agent SDK 作为默认 provider，而不是让业务节点直接依赖 SDK transport 细节。
4. P1：收敛 LangGraph checkpoint 与 `StateManager`/SQLite 状态的所有权，形成单一状态真相。
5. P2：补齐 Windows transport、provider contract、LangGraph failure propagation、MCP/Skills capability 的回归测试。

## 证据链

### 1. 真实日志证据

真实日志路径：`logs/docuswarm-2026-04-28.log`。

关键事实：

- `single_prompt_sdk_error` 首先失败：`Failed to start Claude Code: [WinError 5] 拒绝访问。`
- `analyst`、`pm`、`ux`、`architect`、`po` 五个节点都在 `session_creation_failed` 处失败。
- 每个节点失败前已经完成 MCP/Skills 配置：
  - `setting_sources_enabled`
  - `configuring_mcp_servers`
  - `mcp_servers_created`
  - `sdk_native_skills_enabled`
  - `allowed_tools_configured`
- 日志还显示：`agent_file_skipped_for_tools reason=kimi-agent-sdk format not compatible with claude-agent-sdk`。这说明旧 Kimi agent YAML 不再作为 SDK tools 入口使用，当前主路径已经切到 Claude SDK MCP server。
- 最终 `pipeline_started` 日志中的 `result` 同时出现：
  - `completed_nodes=['analyst','pm','ux','architect','po']`
  - `failed_nodes=['analyst','pm','ux','architect','po']`
  - `status='completed'`
  - `error={'node_id':'analyst','status':'failed',...}`
  - `deliverables={}`

这组结果说明：底层 LLM session 创建失败已经被识别，但图状态仍存在完成语义污染。

### 2. 本机复现实验

在当前工作区和 `venv` 中执行最小诊断：

```text
claude --version
2.1.92 (Claude Code)
```

`claude.exe` 可以直接执行，且 PATH 指向：

```text
C:\Users\Administrator\.local\bin\claude.exe
```

同一环境中，Python 直接 `subprocess.Popen(['claude', '--version'], stdin=PIPE, stdout=PIPE, stderr=PIPE)` 成功返回：

```text
returncode 0
stdout 2.1.92 (Claude Code)
```

但 `anyio.open_process(['claude', '--version'], stdin=PIPE, stdout=PIPE, stderr=PIPE)` 失败：

```text
PermissionError [WinError 5] 拒绝访问。
```

因此当前 `WinError 5` 更像是 Windows 环境对 Python/AnyIO 异步子进程 pipe transport 的拒绝，而不是 CLI 不存在、Claude Code 未安装、或者 `docs/calc-one-plus-one/calc-context.md` 任务内容错误。

### 3. SDK transport 证据

当前虚拟环境：

```text
Python 3.12.10
claude_agent_sdk 0.1.68
claude.exe 2.1.92
```

`venv/Lib/site-packages/claude_agent_sdk/_internal/transport/subprocess_cli.py` 中，SDK 连接路径会构造：

```text
[claude.exe, --output-format, stream-json, --verbose, ...]
```

并通过：

```python
self._process = await anyio.open_process(
    cmd,
    stdin=PIPE,
    stdout=PIPE,
    stderr=stderr_dest,
    cwd=self._cwd,
    env=process_env,
    user=self._options.user,
)
```

启动子进程。任何异常会被包装为：

```python
CLIConnectionError(f"Failed to start Claude Code: {e}")
```

这与日志中的 `Failed to start Claude Code: [WinError 5] 拒绝访问。` 完全吻合。

### 4. 既有文档证据

`docs-doc/evaluation/2026-04-27-claude-agent-sdk-subprocess-transport-architecture-evaluation.md` 的核心结论是：不应放弃 Claude Agent SDK 的 subprocess+stdio 架构，应做 transport 加固和 provider 抽象。该结论仍成立，但需要补充当前新的启动阶段 `WinError 5` 证据。

`docs-doc/evaluation/2026-04-27-transport-hardening-scheme-a-code-review.md` 指出，已有 A-1 idle watchdog、A-3 stderr callback、A-4 日志增强、A-2 关闭兜底的实现痕迹，但真实 SDK close 行为、异常路径清理和日志字段仍存在不足。

`docs-doc/evaluation/2026-04-27-docuswarm-deep-tech-debt-review.md` 的总体判断是“不建议重写整个 DocuSwarm”，问题集中在运行时合同和边界层。当前 WinError 5 进一步验证了这个判断：需要收紧边界，而不是推翻全部。

`docs-doc/solution/TDD-Solution-DocuSwarm-Start-Command.md` 曾把历史 P0-1 定义为 Kimi 会话目录权限错误，并提出 P0-3 防止失败节点被错误加入 `completed_nodes`。当前问题不是同一个 Kimi 会话目录错误，但“失败传播和完成状态污染”仍然复现。

### 5. Claude Agent SDK 文档约束

`autoBMAD/agentdocs/05_python.md` 表明 Python SDK 的正确模式是：

- 一次性调用可用 `query()`
- 多轮会话使用 `ClaudeSDKClient`
- 多轮会话接口包括 `query()`、`receive_messages()`、`receive_response()`、`interrupt()`、`disconnect()`
- `ClaudeAgentOptions` 承载 `allowed_tools`、`mcp_servers`、`permission_mode`、`resume`、`cwd`、`env`、`setting_sources`、`enable_file_checkpointing`

`autoBMAD/agentdocs/15_hosting.md` 明确说明 Claude Agent SDK 不是传统无状态 LLM API，而是在持久环境中维护状态并执行命令；运行时依赖 Python/Node.js/Claude Code CLI。

`autoBMAD/agentdocs/18_mcp.md`、`19_custom_tools.md`、`22_skills.md` 说明 MCP、SDK in-process custom tools、Skills 都是 SDK 正式能力：

- MCP server 可作为本地进程、HTTP/SSE、或 SDK in-process server。
- SDK 自定义工具需要 `create_sdk_mcp_server`/`tool`。
- MCP 工具名遵循 `mcp__server__tool`。
- Skills 需要 `setting_sources` 和 `allowed_tools` 中的 `Skill`。

这说明 DocuSwarm 当前的 MCP/Skills 方向是与 SDK 契约一致的，不应因为 `WinError 5` 直接回退到旧 Kimi YAML 或自研工具协议。

### 6. LangGraph 相关约束

当前代码已经使用：

- `autoBMAD/docuswarm/pipeline/graph.py` 的 `StateGraph(PipelineState)`
- `autoBMAD/docuswarm/pipeline/orchestrator.py` 的 `graph.ainvoke(...)`
- `langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver`
- `create_checkpoint_config(thread_id)`

LangGraph 官方文档将 persistence/checkpointing 作为 durable execution、resume 和 thread state 的核心能力。对于 DocuSwarm 这种长时间、多节点、可恢复的文档流水线，LangGraph 的定位是匹配的。

问题不在于“用了 LangGraph”，而在于当前图节点和状态适配器之间没有形成单一完成语义。

## 当前架构问题定位

### R1：LLM transport 与业务主路径耦合过深

`SessionManager` 同时承担以下职责：

- 构造 Claude SDK options。
- 注入 Skills 的 `setting_sources`。
- 构造 MCP servers。
- 生成 allowed tools。
- 启动 `ClaudeSDKClient`。
- 管理 session wrapper。
- 做 prompt timeout、idle watchdog、stderr callback、process fallback。
- 把 SDK 异常转换为 `LLMError`。

这使一个底层 transport 能力问题直接穿透到每个业务节点。当前日志中五个节点逐一创建 session 并逐一失败，就是缺少统一运行时能力预检的结果。

### R2：失败节点仍被图执行器加入 `completed_nodes`

`PipelineAdapter.convert_node_to_pipeline_state()` 已经有 P0-F1 逻辑：只有 `node_status == COMPLETED` 才加入 `completed_nodes`，否则加入 `failed_nodes`。

但 `autoBMAD/docuswarm/pipeline/graph.py` 在 adapter 转换之后仍执行：

```python
current_iteration = result_state["node_iterations"].get(node_id, 0)
result_state["node_iterations"][node_id] = current_iteration + 1

if node_id not in result_state["completed_nodes"]:
    result_state["completed_nodes"] = result_state["completed_nodes"] + [node_id]
```

这会覆盖 adapter 的失败语义，导致失败节点仍进入 `completed_nodes`。真实日志中的矛盾结果正是这个问题的运行时证据。

### R3：finalizer 盲目标记完成

`autoBMAD/docuswarm/pipeline/state.py` 的 `finalize_pipeline_state()` 无条件执行：

```python
result["status"] = COMPLETED
```

虽然 `HybridOrchestrator._determine_final_status()` 会根据 `failed_nodes` 或 `error` 把数据库最终状态修正为 `failed`，但 LangGraph 返回结果、日志、checkpoint 中仍会保留 `status=completed` 的矛盾状态。

这不是单纯日志问题。恢复、重跑、导出和状态排障都会依赖这些状态字段。

### R4：LangGraph checkpoint 与数据库状态存在双重真相

既有文档已经多次指出 `state_json`、顶层 `pipelines.status/current_node`、LangGraph checkpoint 之间存在语义漂移。当前日志再次暴露：

- 图状态认为 `status=completed`
- 失败字段认为所有节点失败
- orchestrator 再另行计算最终 status

这是状态所有权不清晰，而不是某个 if 条件缺失。

### R5：Windows transport 能力缺少可测试契约

当前已有 transport hardening 测试关注 idle、关闭、stderr、日志字段，但缺少一个最关键的 Windows capability contract：

- 直接 `claude --version` 成功不代表 SDK transport 可用。
- `subprocess.Popen` 成功不代表 `anyio.open_process` 可用。
- `ClaudeSDKClient.connect()` 失败应在流水线启动前被诊断出来，而不是让五个节点重复失败。

## 是否应当重构

### 应当重构的部分

#### 1. Agent Runtime / LLM Provider 边界

应新建 provider 边界，例如：

```text
autoBMAD/docuswarm/llm/provider.py
autoBMAD/docuswarm/llm/runtime.py
```

建议接口：

```python
class AgentRuntime(Protocol):
    async def preflight(self) -> RuntimePreflightResult: ...
    async def create_session(self, request: SessionRequest) -> AgentSession: ...
    async def close_all(self) -> None: ...

class AgentSession(Protocol):
    async def prompt(self, message: str, timeout: int | None = None) -> AsyncIterator[Any]: ...
    async def close(self) -> None: ...
```

默认实现仍然是：

```text
ClaudeAgentSDKProvider
```

这个边界不应马上承诺多模型能力。它首先是为了把“DocuSwarm 的业务节点”从“Claude SDK transport 的启动机制”中隔离出来。

#### 2. Transport capability preflight

在 pipeline 创建之前执行一次预检：

1. 定位 `claude.exe`。
2. 执行 `claude --version`。
3. 执行与 SDK 等价的 `anyio.open_process(..., stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=repo_root)` 最小探针。
4. 可选：执行 `ClaudeSDKClient.connect()` 的最小连接探针，但必须设置短 timeout。
5. 失败时输出结构化诊断：
   - `category=transport_permission_denied`
   - `platform=Windows`
   - `cli_path=...`
   - `direct_cli_ok=true`
   - `subprocess_popen_ok=true`
   - `anyio_open_process_ok=false`
   - `error=[WinError 5] 拒绝访问`

这样可以把当前“五个节点都失败”的行为压缩成“一次 preflight 失败”，更符合奥卡姆剃刀原则。

#### 3. LangGraph failure gate

应把“节点是否完成”的判断收敛到一处。

推荐规则：

- 只有 `NodeStatus.COMPLETED` 或明确的 `FORCE_APPROVED` 可进入 `completed_nodes`。
- `FAILED`、`BLOCKED`、`PENDING`、空状态都必须进入 `failed_nodes` 或保持未完成，不得进入 `completed_nodes`。
- `finalize_pipeline_state()` 必须检查：
  - 是否存在 `failed_nodes`
  - 是否存在 `error`
  - 是否所有 `PIPELINE_NODES` 都在 `completed_nodes`
  - 是否每个节点都有对应 deliverable 或明确的跳过原因
- `graph.py` 不应在 adapter 后再次无条件追加 `completed_nodes`。

#### 4. State ownership refactor

建议建立状态所有权规则：

- LangGraph checkpoint 是执行中恢复的事实来源。
- `StateManager`/SQLite 顶层字段是索引和查询投影。
- 更新状态时通过一个 mapper 从 checkpoint state 派生投影字段，而不是让 graph、orchestrator、state manager 分别写自己的 status。
- `status/list/export/resume/restart/cancel` 必须通过同一状态读取服务访问。

#### 5. Runtime test matrix

至少补齐以下测试：

- `test_transport_preflight_distinguishes_direct_cli_from_anyio_spawn`
- `test_preflight_failure_prevents_node_execution`
- `test_failed_node_never_enters_completed_nodes_after_adapter`
- `test_finalize_failed_when_failed_nodes_present`
- `test_graph_result_status_matches_orchestrator_final_status`
- `test_provider_contract_for_claude_agent_sdk`
- `test_mcp_allowed_tools_match_registered_servers`
- `test_skills_require_setting_sources_and_skill_tool`

### 不应当重构的部分

#### 不应放弃 Claude Agent SDK

理由：

- SDK 是当前 Skills、MCP、session resume、file checkpointing、Claude Code 权限控制的正式入口。
- 直接 HTTP API 需要自研 agent loop、工具调用、文件权限、MCP 协议、Claude Code 行为兼容，复杂度远大于当前问题。
- 当前失败根因是 Windows/AnyIO transport 启动能力问题，不是 SDK 抽象模型错误。

#### 不应为了此问题迁移到 TypeScript

迁移语言不能证明能消除 Windows 权限策略。即便 TypeScript SDK 避开 Python AnyIO，也会引入：

- Python DocuSwarm 主体重写成本。
- LangGraph Python 工作流迁移成本。
- 现有测试和文档体系重建成本。
- 与现有 BMAD/DocuSwarm 模块的大量接口漂移。

#### 不应移除 LangGraph

LangGraph 的 StateGraph、checkpoint、thread/resume 能力与 DocuSwarm 的多节点长流程匹配。当前问题是状态适配和完成语义污染，不是 LangGraph 不适合。

#### 不应把 mock/fallback 文档生成当作生产成功

在 WinError 5 发生时，可以提供诊断和失败报告，但不能用本地模板假装 analyst/pm/ux/architect/po 已完成。否则会继续污染 `completed_nodes`、交付物和用户信任。

## 方案比较

| 方案 | 能否解决 WinError 5 | 能否减少状态污染 | 成本 | 风险 | 结论 |
|---|---:|---:|---:|---:|---|
| 不重构，只调环境 | 部分 | 否 | 低 | 高 | 不足。下次环境变化还会重复失败 |
| P0 transport preflight + failure gate | 是 | 是 | 低到中 | 低 | 必做 |
| P1 AgentRuntime/Provider 边界 | 间接 | 是 | 中 | 中 | 推荐。本质上是隔离 blast radius |
| 全量替换 Claude SDK 为 HTTP direct | 不确定 | 可重做 | 极高 | 极高 | 不建议 |
| 迁移 TypeScript | 不确定 | 可重做 | 极高 | 高 | 不建议 |
| 移除 LangGraph | 否 | 可重做 | 高 | 高 | 不建议 |

## 推荐重构路线

### P0：立即修正

目标：当前错误要快速、清楚、单点失败，不再污染五个节点和最终状态。

开发要求：

1. 新增 runtime preflight。
2. `start_pipeline()` 在 preflight 失败时直接创建失败状态，不进入五节点 graph。
3. 删除或改造 `graph.py` 中 adapter 后无条件追加 `completed_nodes` 的逻辑。
4. `finalize_pipeline_state()` 根据 `failed_nodes/error/completed_nodes` 决定状态。
5. 日志新增结构化字段，明确 `direct_cli_ok`、`anyio_open_process_ok`。

验证要求：

- Windows 下 anyio spawn 失败时，只有一次 preflight error。
- `completed_nodes=[]`。
- `failed_nodes` 不应包含五个业务节点，除非节点真的被执行过。
- pipeline status 为 `failed`。
- 错误消息包含 `[WinError 5] 拒绝访问` 和诊断建议。

### P1：边界重构

目标：让 `docuswarm` 的业务层不直接知道 Claude SDK transport 细节。

开发要求：

1. 新建 `AgentRuntime`/`LLMProvider` protocol。
2. 移动 SDK options 构建到 `ClaudeAgentSDKProvider`。
3. `SessionManager` 降级为 provider 的一个实现细节，或拆分为：
   - `ClaudeOptionsFactory`
   - `ClaudeSessionFactory`
   - `ClaudeTransportMonitor`
4. 节点执行器只依赖 provider/session 抽象。
5. MCP/Skills capability 作为 provider capabilities 暴露。

验证要求：

- provider contract tests 不启动真实 Claude 也能验证状态映射。
- transport integration test 可以在具备权限的环境中启用。
- MCP server 和 `allowed_tools` 快照保持一致。

### P1/P2：状态所有权收敛

目标：checkpoint、DB、CLI 查询说同一种状态语言。

开发要求：

1. 定义 `PipelineExecutionState` 到 `PipelineStatusProjection` 的单一 mapper。
2. `status/list/export/resume/restart/cancel` 统一通过状态访问层读取。
3. `orchestrator` 不再局部修正 graph 的矛盾状态，而是从统一 mapper 派生最终状态。
4. 增加迁移兼容逻辑读取旧 checkpoint。

验证要求：

- `graph.ainvoke()` 返回状态、checkpoint 状态、DB 顶层 status 三者一致。
- 失败节点不会被恢复流程当作已完成节点跳过。
- `export` 不会导出空 deliverables 却标记 completed。

### P2：运行时弹性增强

目标：提升跨平台诊断和恢复能力。

候选项：

- 对 `claude_agent_sdk` 私有 `_transport._process` 访问保留兼容兜底，但集中在 provider 层。
- 建立上游 SDK 变更监控，尤其是 `SubprocessCLITransport`、`stderr` callback、`skills`、`session_store`。
- 可选实现一个非常窄的 `DiagnosticOnlyProvider`，只用于环境诊断，不用于生产交付物生成。

## 架构边界建议

建议目标结构：

```text
autoBMAD/docuswarm/
  llm/
    provider.py                 # Protocols: AgentRuntime, AgentSession
    runtime_preflight.py         # Windows/CLI/AnyIO/SDK capability checks
    claude_sdk_provider.py       # Claude Agent SDK implementation
    claude_options.py            # options/MCP/Skills construction
    transport_monitor.py         # timeout, stderr, process close fallback
    session_manager.py           # compatibility facade, gradually thinned
  pipeline/
    graph.py                     # pure graph flow, no duplicated completion policy
    state.py                     # deterministic state transitions
    status_projection.py         # checkpoint -> DB/CLI projection
    orchestrator.py              # orchestration, not transport diagnosis owner
```

该结构保留现有 LangGraph 和 Claude SDK 投资，同时把最容易受环境影响的 transport 层关进一个可测边界里。

## 根因判断

本次 `WinError 5` 的直接根因：

```text
Claude Agent SDK -> SubprocessCLITransport.connect()
-> anyio.open_process(... stdin/stdout/stderr PIPE ...)
-> Windows PermissionError [WinError 5] 拒绝访问
```

架构层根因：

```text
缺少 transport capability preflight
+ LLM transport 与业务节点强耦合
+ LangGraph completion policy 被多处重复实现
+ checkpoint/DB/log result 状态所有权不一致
```

因此，奥卡姆剃刀下的最小解释是：不是五个节点都坏了，也不是文档任务坏了，而是共享的 Claude SDK transport 启动能力坏了；架构缺陷在于没有在共享边界 fail fast，并且失败状态被后续 graph/finalizer 污染。

## 最终建议

建议执行“P0/P1 边界重构”，不要执行“全量替换/重写”。

具体决策：

- **保留** Claude Agent SDK。
- **保留** LangGraph。
- **新增** AgentRuntime/Provider 边界。
- **新增** Windows transport preflight。
- **修复** graph/finalizer 完成语义。
- **收敛** checkpoint 与 DB 状态所有权。
- **补齐** 能证明 WinError 5 不再污染流水线状态的测试。

完成这些之后，`WinError 5` 即便仍由宿主环境触发，也会成为一个清晰、可定位、不会误报业务完成的启动前失败，而不是一个拖垮整条文档流水线的架构性故障。

## 参考资料

- `logs/docuswarm-2026-04-28.log`
- `docs-doc/evaluation/2026-04-27-claude-agent-sdk-subprocess-transport-architecture-evaluation.md`
- `docs-doc/evaluation/2026-04-27-transport-hardening-scheme-a-code-review.md`
- `docs-doc/evaluation/2026-04-27-docuswarm-deep-tech-debt-review.md`
- `docs-doc/solution/TDD-Solution-DocuSwarm-Start-Command.md`
- `docs-doc/research/2026-04-27-transport-hardening-scheme-a-research.md`
- `autoBMAD/agentdocs/05_python.md`
- `autoBMAD/agentdocs/12_sessions.md`
- `autoBMAD/agentdocs/13_file_checkpointing.md`
- `autoBMAD/agentdocs/15_hosting.md`
- `autoBMAD/agentdocs/18_mcp.md`
- `autoBMAD/agentdocs/19_custom_tools.md`
- `autoBMAD/agentdocs/22_skills.md`
- LangGraph 官方文档：`https://docs.langchain.com/oss/python/langgraph/persistence`
- LangGraph 官方文档：`https://docs.langchain.com/oss/python/langgraph/durable-execution`
- `venv/Lib/site-packages/claude_agent_sdk/_internal/transport/subprocess_cli.py`
- `autoBMAD/docuswarm/llm/session_manager.py`
- `autoBMAD/docuswarm/pipeline/graph.py`
- `autoBMAD/docuswarm/pipeline/state.py`
- `autoBMAD/docuswarm/pipeline/orchestrator.py`
- `autoBMAD/docuswarm/node_execution/pipeline_adapter.py`
