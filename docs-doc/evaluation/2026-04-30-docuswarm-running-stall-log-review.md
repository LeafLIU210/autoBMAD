# 2026-04-30 DocuSwarm 运行中断与 stale-running 状态审查报告

审查对象: `autoBMAD/docuswarm`  
触发日志: `logs/docuswarm-2026-04-30.log`  
关联 pipeline: `pipeline-1777548246143-43a13bf8`  
输出目录: `output/pipeline-1777548246143-43a13bf8`  
报告目录: `docs-doc/evaluation`  
审查方法: `systematic-debugging` 根因追踪 + 日志/状态/代码交叉验证  
审查时间: 2026-04-30 CST

## 结论摘要

本次日志没有记录到传统意义上的 Python traceback、`pipeline_execution_error`、`prompt_timeout`、`prompt_idle_exceeded` 或节点失败事件。可以确认的是:

1. context validation 成功。
2. SummaryAgent 第一次 LLM 调用被取消并被上层表现为 `Empty response from LLM`，第二次重试成功。
3. pipeline 进入 `analyst` 节点，创建了 Claude SDK session，并收到 5 条 SDK 消息。
4. 日志在 `2026-04-30T19:25:12.241100+08:00` 后停止，没有 `llm_prompt_complete`、`independent_agent_completed`、`node_execution_completed` 或 `pipeline_started`。
5. 当前没有仍在运行的 DocuSwarm/Claude 子进程。
6. DB 中该 pipeline 仍是 `status=running, current_node=analyst`，没有 node result，没有交付物，输出目录为空。

因此，本次可证明的核心故障不是“SummaryAgent 失败”，也不是“某个节点显式失败”。更准确的结论是:

**pipeline 在 analyst 节点进行中的 SDK 消息流阶段被外部中断或进程提前结束；DocuSwarm 缺少 in-flight 节点状态、session、heartbeat 和中断 finalization 的持久化机制，导致进程已经不存在但 DB 仍永久显示 running。**

这是一类状态一致性/可恢复性问题。它会让 CLI/status/resume 看到一个“看起来仍在运行、实际上无人持有”的 pipeline，并且由于没有持久化当前 session id 与节点运行记录，恢复只能从 checkpoint 重跑，无法解释上一次为何停住。

## 运行时间线

### 1. Context validation 成功

日志行 1 到 21:

- `hybrid_orchestrator_initialized`: `db_path=docuswarm.db`, `work_dir=/home/leafliu/autoBMAD/output`
- `starting_pipeline`: 输入是 `docs/calc-one-plus-one/calc-context.md`
- `single_prompt_result`: context validator 返回 `{"valid": true, ...}`
- `single_prompt_complete`: `message_count=2`, `tool_calls=0`

结论: 输入上下文是有效的，API 凭证至少能完成一次 LLM 调用。

### 2. SummaryAgent 第一次尝试被取消，第二次重试成功

日志行 23 到 88:

- `pipeline_work_dir_created`: 创建 `output/pipeline-1777548246143-43a13bf8`
- `starting_summary_generation`: 处理 1 个文件
- `processing_document`: `docs/calc-one-plus-one/calc-context.md`, `size_bytes=1796`
- 第一次 `single_prompt_start` 后约 33.7 秒出现 `single_prompt_cancelled`
- 紧接着 `llm_call_failed`: `error=Empty response from LLM`, `error_type=LLMSummaryError`, `attempt=1`
- 第二次重试在约 18.1 秒后成功返回 JSON summary
- `summary_generation_complete`: `success_count=1`, `failure_count=0`
- `documents_summarized`: `count=1`

结论: SummaryAgent 有一次 transient failure，但不是最终阻断点。它被 retry 恢复，pipeline 继续进入节点执行。

需要注意的是，`single_prompt_cancelled` 由 `SessionManager.single_prompt()` 捕获 `asyncio.CancelledError` 后返回空列表造成。上层只能看到空响应，丢失了“调用被取消”的真实语义。

### 3. Analyst 节点开始执行，SDK session 创建成功

日志行 90 到 134:

- `using_integrated_node_executor`
- `node_execution_started`: `node_id=analyst`, `iteration=1`
- `using_cached_docs_summary`: `count=1`
- `starting_dual_agent_execution_with_context`
- `iteration_start`: `iteration=1`, `max_iterations=3`
- `executing_independent_agent_with_input`
- `llm_prompt_start`: `user_prompt_length=1989`, `system_prompt_length=4216`
- `creating_session`: `cwd=/home/leafliu`, `output_dir=/home/leafliu/autoBMAD/output/pipeline-1777548246143-43a13bf8`
- `mcp_servers_created`: `server_keys=['docuswarm-deliverable-analyst']`
- `allowed_tools_configured`: `create_deliverable` 与 `submit_execution_report` 已允许
- `session_created`: `session_id=session_5d79b774cc4f`
- `tools_configured`: MCP server 与 allowed tools 均已配置

结论: 节点执行没有卡在配置加载、persona 加载、MCP server 创建或 session 创建阶段。

### 4. SDK 消息流收到消息后日志停止

日志行 136 到 154:

- message 1: `SystemMessage`
- message 2: `AssistantMessage`
- message 3: `AssistantMessage`
- message 4: `UserMessage`
- message 5: `AssistantMessage`

缺失的预期后续日志:

- 没有 `llm_tool_call`
- 没有 `llm_prompt_complete`
- 没有 `independent_agent_completed`
- 没有 `response_validation_failed`
- 没有 `evaluator_agent_failed`
- 没有 `node_execution_failed`
- 没有 `node_execution_completed`
- 没有 `pipeline_execution_error`
- 没有 `pipeline_started`
- 没有 `prompt_timeout`
- 没有 `prompt_idle_exceeded`

结论: 日志不是“正常失败后结束”，而是在 analyst session 的 receive loop 中途停止。

### 5. 文件系统与 DB 状态

输出目录:

```text
output/pipeline-1777548246143-43a13bf8
```

目录存在但无文件。说明 analyst 没有成功调用 `create_deliverable`，也没有生成任何交付物。

DB `pipelines` 表:

```text
pipeline_id: pipeline-1777548246143-43a13bf8
status: running
current_node: analyst
completed_nodes: []
failed_nodes: []
deliverables: {}
questions: {}
evaluations: {}
node_iterations: {}
current_node_session_id: null
error: null
docs_context_summary: []
```

DB `node_results`、`node_runs`、`node_run_metrics`、`shared_context_history` 均无该 pipeline 记录。

LangGraph checkpoint 有该 pipeline 的两条 checkpoint，并且 writes 只到 `start:analyst`。这说明 graph 已经准备进入 analyst，但没有完成 analyst 节点，也没有走到 finalizer。

当前进程列表没有 DocuSwarm/Claude 相关执行进程。说明 DB 的 `running` 不代表真实运行中。

## Systematic Debugging 过程

### Phase 1: Root Cause Investigation

#### 读取错误与告警

本日志中的唯一 warning 是:

```text
llm_call_failed agent=SummaryAgent attempt=1 max_retries=2 error=Empty response from LLM error_type=LLMSummaryError
```

但随后 SummaryAgent 第二次成功，并记录:

```text
summary_generation_complete success_count=1 failure_count=0
documents_summarized count=1
```

所以不能把 SummaryAgent warning 当作本次 pipeline 的最终根因。

真正的异常信号是“应该出现的完成/失败日志完全缺失”。这类问题需要沿组件边界看状态:

- CLI/Service: 是否返回最终 result? 日志没有。
- Orchestrator: 是否执行到 `graph.ainvoke()` 后? 没有 `pipeline_started`。
- Graph/Node executor: 是否执行完 analyst? 没有 `node_execution_completed`。
- IndependentAgent: 是否收完 session prompt? 没有 `llm_prompt_complete`。
- Session wrapper: 是否 timeout/idle? 没有 `prompt_timeout`/`prompt_idle_exceeded`。
- DB: 是否标记失败或取消? 没有，仍 running。

#### 复现边界

本次没有直接重跑真实 LLM，因为审查目标是根据给定日志做评估，并且网络/API 行为不可稳定复现。改用日志、DB、输出目录和代码路径做一致性复核:

- `logs/docuswarm-2026-04-30.log` 只有 155 行，末尾停在 SDK message 5。
- `output/pipeline-1777548246143-43a13bf8` 为空。
- DB 中 pipeline 仍 running。
- 当前系统进程中没有该 pipeline 对应的运行进程。

这足以证明“运行状态已失真”，但不足以证明是用户 Ctrl+C、进程被杀、宿主环境中断、SDK 子进程退出未回传，还是其他外部停止。报告后续只把这些作为候选，不把它们写成已证实根因。

#### 最近代码路径

关键路径:

1. `PipelineService.start()` 创建全局 `SessionManager`，调用 `orchestrator.start_pipeline()`，finally 中只关闭这个全局 manager。
2. `HybridOrchestrator.start_pipeline()` 先写入 `status=running,current_node=analyst`，然后生成 summary，再 `await graph.ainvoke(...)`。
3. `_create_integrated_node_executor()` 调用 node executor。
4. `_execute_node()` 调用 `DualAgentNode.execute_with_context()`。
5. `DualAgentNode.execute_with_context()` 调用 `IndependentAgent.execute_with_input()`。
6. `IndependentAgent.execute_with_input()` 创建节点专用 `pipeline_session_manager`，调用 `_call_llm_with_prompts()`。
7. `_call_llm_with_prompts()` 创建 session，然后 `async for msg in session.prompt(...)` 收消息。
8. `ClaudeSessionWrapper.prompt()` 负责 total timeout 与 idle watchdog。

日志停止点位于第 7 到第 8 步之间。

### Phase 2: Pattern Analysis

#### 工作路径应该出现的日志

若 analyst 正常完成，后续至少应出现:

- `llm_prompt_complete`
- `parse_response_using_submit_report` 或 fallback 解析日志
- `independent_agent_completed`
- `evaluation_complete`
- `dual_agent_execution_complete`
- `node_execution_completed`
- 后续节点开始，或 finalizer

若 analyst 内部失败，后续至少应出现:

- `llm_call_error` 或 `receive_messages_error`
- `independent_agent_failed`
- `node_execution_failed`
- `integrated_executor_error` 或 failed node 状态
- `pipeline_started` 返回 failed result，或 `pipeline_execution_error`

若 SDK idle/total timeout，后续至少应出现:

- `prompt_idle_exceeded` 或 `prompt_timeout`
- `llm_call_error`
- `node_execution_failed`

这些日志均不存在。

#### 4 月 29 日同类报告的差异

`docs-doc/evaluation/2026-04-29-docuswarm-summary-json-failure-evaluation.md` 中的失败是 SummaryAgent JSON 解析失败，发生在 graph 节点执行前。而本次 4 月 30 日:

- SummaryAgent 第二次重试成功。
- 已进入 integrated node executor。
- 已创建 analyst session。
- 停止点在 SDK streaming 阶段。

因此不能复用 4 月 29 日的根因结论。

#### 状态持久化模式的薄弱点

`HybridOrchestrator.start_pipeline()` 在 graph 前只持久化 running 状态，graph 返回后才持久化完整 result。若 graph 执行期间发生 `KeyboardInterrupt`、`asyncio.CancelledError`、进程被杀或宿主环境中断，`pipelines.state_json` 不会记录正在执行的节点、session、最后消息、已缓存 summary 或中断原因。

`StateManager.update_pipeline_state()` 可以同步顶层 `status/current_node` 和 `state_json`，但它只在调用方显式调用时生效。当前节点内部并未在 session 创建、节点开始、节点消息阶段持续写入状态。

### Phase 3: Hypothesis and Testing

#### 已确认假设

**H1: pipeline 并非 SummaryAgent 阶段失败。**

证据:

- 日志有 `summary_generation_complete success_count=1 failure_count=0`。
- 日志有 `documents_summarized count=1`。
- 后续有 `node_execution_started analyst`。

结论: 成立。

**H2: pipeline 停在 analyst IndependentAgent 的 SDK session 消息流阶段。**

证据:

- 有 `session_created session_5d79b774cc4f`。
- 有 SDK `llm_message_received` 到 message 5。
- 无 `llm_prompt_complete`。
- 无工具调用、交付物、节点完成。

结论: 成立。

**H3: DB 的 running 状态已失真。**

证据:

- DB `status=running,current_node=analyst`。
- 输出目录为空，node_results 为空。
- 当前进程列表没有对应运行进程。

结论: 成立。

#### 未能确认的候选原因

以下候选都可能导致日志中途停止，但当前证据不足以单独确认:

- 用户手动中断 CLI。
- 外部 supervisor/IDE/容器杀死进程。
- Claude SDK/CLI 子进程异常退出但没有被父进程记录到日志。
- Python 进程收到 `KeyboardInterrupt` 或 `CancelledError`，绕过 `except Exception`。
- 宿主环境收集日志不完整。

本报告不把这些候选写成根因。真正可行动的根因是: **系统没有为这些中断路径建立可观测、可恢复、可最终化的状态机制。**

### Phase 4: Implementation Guidance

本次任务是创建审查报告，未直接修改业务代码。若进入修复，应先写失败测试:

1. graph 执行中抛出 `asyncio.CancelledError` 时，pipeline 不应永久保持 running。
2. CLI 收到 `KeyboardInterrupt` 时，应把 pipeline 标记为 `cancelled` 或 `failed/interrupted`，并记录 `error_type`。
3. session 创建后，`current_node_session_id` 与 `session_ids[node_id]` 应写入 StateManager。
4. per-node `pipeline_session_manager` 在成功、失败、取消路径都应 `close_all()`。
5. stale-running 检测应能发现“updated_at 超过阈值且无 owner/heartbeat”的 pipeline。
6. `single_prompt()` 被取消时，应保留 cancellation 语义，而不是返回空列表。

## 关键问题清单

### P0-1: graph 执行中断会留下永久 running 的 pipeline

严重性: Critical  
影响范围: CLI status/list/resume、用户判断、自动化调度、后续清理  
证据:

- `logs/docuswarm-2026-04-30.log` 没有任何 terminal event。
- DB 中 `pipeline-1777548246143-43a13bf8` 仍为 `running/analyst`。
- 当前无对应运行进程。
- 输出目录为空，node_results 为空。

相关代码:

- `autoBMAD/docuswarm/pipeline/orchestrator.py:433-437` 在 graph 前写入 running。
- `autoBMAD/docuswarm/pipeline/orchestrator.py:482-494` 只有 `graph.ainvoke()` 正常返回后才写完整 result。
- `autoBMAD/docuswarm/pipeline/orchestrator.py:512-525` 只捕获 `Exception`，无法覆盖 `KeyboardInterrupt`，且在现代 Python 中也不能可靠覆盖 `asyncio.CancelledError`。
- `autoBMAD/docuswarm/cli/commands/start.py:28-45` CLI 同样只捕获 `Exception` 类错误。

根因判断:

系统把 pipeline 的“开始运行”和“最终结果”持久化了，但没有持久化“运行租约/心跳/中断 finalization”。任何中途退出都会留下假 running。

建议:

- 在 orchestrator 中显式处理 `asyncio.CancelledError`，持久化 `status=cancelled` 或 `failed`，记录 `error_type=CancelledError` 后再 re-raise。
- 在 CLI 层处理 `KeyboardInterrupt`，调用 StateManager 将当前 pipeline 标记为 `cancelled/interrupted`。
- 增加 pipeline lease 字段: `owner_pid`, `host`, `started_at`, `last_heartbeat_at`, `last_event`.
- 在 `status/list/resume` 中加入 stale-running 检测: running 且 heartbeat 超阈值、owner 不存在时标记 `stale` 或提示 `resume --force`。
- 在 graph/node/session 关键边界写入 last event，至少包括 `node_started`, `session_created`, `message_received`, `tool_call_started`, `node_completed`.

### P0-2: in-flight session 未持久化，resume 无法恢复当前节点会话

严重性: High  
证据:

- 日志记录 `session_created session_5d79b774cc4f`。
- DB 中 `current_node_session_id=null`。
- DB `state_json.session_ids` 未体现当前 analyst session。

相关代码:

- `SessionManager.create_session()` 只在内存 `_active_clients/_active_wrappers` 中记录 session。
- `IndependentAgent.execute_with_input()` 创建 pipeline-scoped SessionManager，但没有把 session id 回写 pipeline state。
- `HybridOrchestrator.resume_pipeline()` 期望从 checkpoint state 读取 `current_node_session_id`，但本次状态中没有。

影响:

所谓 session-aware resume 在真实中断场景无法发挥作用。即使日志里有 SDK session id，系统持久化状态不知道它，恢复只能重跑 analyst。

建议:

- 在 session 创建成功后，通过回调或事件总线写入:

```json
{
  "current_node_session_id": "session_...",
  "session_ids": {"analyst": "session_..."},
  "session_metadata": {
    "analyst": {
      "created_at": "...",
      "cwd": "...",
      "output_dir": "...",
      "allowed_tools": [...]
    }
  }
}
```

- 把 session 创建事件与 node run 记录放入同一个状态更新事务，避免日志有 session 但 DB 无 session。

### P0-3: 节点专用 SessionManager 没有在 finally 中关闭

严重性: High  
证据:

- `IndependentAgent.execute_with_input()` 创建 `pipeline_session_manager`。
- finally 中只恢复 `self.session_manager = original_session_manager`。
- 没有 `await pipeline_session_manager.close_all()`。

相关代码:

- `autoBMAD/docuswarm/agents/independent.py:1035-1047` 创建并替换 session manager。
- `autoBMAD/docuswarm/agents/independent.py:1049-1059` finally 只恢复原 manager。
- `PipelineService.start()` finally 只关闭外层全局 `session_manager`，关闭不到节点内部创建的 manager。

影响:

正常路径可能残留 SDK client/CLI subprocess；异常/取消路径更容易残留。虽然本次审查时未发现仍存活的进程，但这是一个结构性资源生命周期缺口。

建议:

```python
pipeline_session_manager = self._create_pipeline_session_manager(...)
original_session_manager = self.session_manager
self.session_manager = pipeline_session_manager
try:
    response = await self._call_llm_with_prompts(...)
finally:
    self.session_manager = original_session_manager
    await pipeline_session_manager.close_all()
```

同时增加测试，断言成功、LLMError、CancelledError 三条路径都会调用 `close_all()`。

### P1-1: `single_prompt()` 吞掉 cancellation，导致真实取消被误报为空响应

严重性: Medium-High  
证据:

- 日志中先出现 `single_prompt_cancelled`，随后 SummaryAgent 报 `Empty response from LLM`。

相关代码:

- `autoBMAD/docuswarm/llm/session_manager.py:824-826`

当前逻辑:

```python
except asyncio.CancelledError:
    self._logger.info("single_prompt_cancelled")
    return []
```

影响:

调用方无法区分“模型空响应”和“调用被取消/超时传播”。这会误导 root cause 分析，也可能触发无意义重试。

建议:

- 默认重新抛出 `CancelledError`，或包装成 `LLMError(api_error_type="CancelledError")`。
- 如果确实需要 fail-open，必须显式命名，例如 `return_empty_on_cancel=True`，并在日志中记录 caller、timeout、attempt。
- SummaryAgent 应分别处理 timeout、cancelled、empty text，错误类型不能混同。

### P1-2: SummaryAgent 每文档 30 秒 timeout 偏紧，且取消语义与空响应耦合

严重性: Medium  
证据:

- 第一次 SummaryAgent 调用从 `19:24:06.152849` 到 `19:24:39.856415` 被取消，约 33.7 秒。
- 配置 `timeout_per_document_seconds=30`, `max_retries=2`。
- 第二次同一文档调用 18.1 秒成功。

相关代码:

- `autoBMAD/docuswarm/config/summary_agent.yaml:48-50`
- `autoBMAD/docuswarm/agents/summary.py:451-465`

影响:

对 1796 bytes 的文件，首次调用超过 30 秒就被取消并重试。虽然本次恢复成功，但它放大了耗时和不稳定性。如果多个文档并发处理，会引入更多 retry 噪声。

建议:

- 把 SummaryAgent timeout 提升到 60-120 秒，或按内容长度动态计算。
- 使用 SDK `output_format` 或项目已有 `extract_json()`，减少重试来自格式问题的概率。
- 对 timeout/cancelled/empty response 分开计数和告警。

### P1-3: docs_context_summary 没有在 graph 前同步到 StateManager

严重性: Medium  
证据:

- 日志显示 `documents_summarized count=1`。
- LangGraph writes 中存在 `docs_context_summary`。
- `pipelines.state_json.docs_context_summary` 仍是 `[]`。

相关代码:

- `HybridOrchestrator.start_pipeline()` 在 `create_initial_state(... docs_context_summary=docs_context_summary)` 中把 summary 放入 graph state。
- 但 StateManager 只在 graph 完成后持久化完整 result。

影响:

当 graph 中途停止时，DB status 看不到已成功生成的 summary。后续 resume/status/debug 都丢失这部分上下文，只能依赖 LangGraph checkpoint。

建议:

在 `documents_summarized` 后立即更新 StateManager:

```python
await self._state_manager.update_pipeline_state(
    final_pipeline_id,
    {"docs_context_summary": docs_context_summary}
)
```

这不是替代 checkpoint，而是让用户可见状态与实际进度一致。

### P2-1: `node_results` 与 `node_runs` 未被当前执行链路使用

严重性: Medium  
证据:

- DB 表存在 `node_results`, `node_runs`, `node_run_metrics`。
- 本次 pipeline 没有任何 node run 记录。
- `_execute_node()` 直接在内存 state 中更新，不调用 `StateManager.save_node_result()` 或 node run tracker。

影响:

节点级状态只能在 graph 返回后间接进入 pipeline state。节点中途失败、取消或卡住时，DB 缺少“正在运行哪个节点、哪次迭代、开始时间、session id、最后事件”的事实记录。

建议:

- node executor 进入节点时创建 `node_runs` 记录。
- session 创建后更新 `node_runs.session_id` 或 metadata。
- 每次 node 完成/失败/取消都更新 `node_runs.status/end_time/error`。
- `node_results` 只记录完成结果，`node_runs` 记录生命周期，两者职责分离。

## 风险评估

### 用户可见风险

- `docuswarm list --status running` 会展示已经没有进程持有的 pipeline。
- `docuswarm resume` 可能提示 pipeline already running，需要用户 `--force`，但用户无法判断它是否真的还在运行。
- 输出目录为空但 DB 显示 running，容易误判为“仍在生成”。
- 一旦多个 stale running 累积，后续清理和调度会变得混乱。

### 工程风险

- 资源泄漏: 节点专用 SessionManager 未关闭。
- 可恢复性不足: session id 未持久化。
- 可观测性不足: 消息流中断没有 last event/heartbeat。
- 错误分类不足: cancellation 被包装成 empty response。
- 状态双轨: LangGraph checkpoint 有部分事实，StateManager state_json 没同步。

## 推荐修复顺序

### 第一优先级: 防止假 running

1. 为 orchestrator graph 执行添加 `CancelledError`/中断 finalization。
2. CLI 捕获 `KeyboardInterrupt` 并标记 pipeline interrupted/cancelled。
3. 加入 heartbeat/lease 与 stale-running 检测。
4. 在 status/list 中展示 stale 标记，而不是单纯 running。

验收标准:

- 人为取消运行后，DB 不再永久 running。
- 无进程持有且 heartbeat 过期时，status 明确提示 stale。
- stale pipeline 可被安全 `resume --force` 或 cancel。

### 第二优先级: 持久化 in-flight 节点与 session

1. `node_execution_started` 时创建/更新 `node_runs`。
2. `session_created` 后写入 `current_node_session_id` 与 `session_ids[node]`。
3. 每次 SDK message 更新 `last_event_at` 或轻量 heartbeat。

验收标准:

- DB 可回答: 当前哪个节点、哪次迭代、哪个 session、最后收到什么事件。
- resume 可以知道是否存在可恢复 session，不能恢复时也能说明原因。

### 第三优先级: 清理资源生命周期

1. `IndependentAgent.execute_with_input()` finally 中关闭节点专用 SessionManager。
2. 为 success/error/cancel 三种路径加单元测试。
3. 日志中记录 `session_closed` 与是否 force-kill。

验收标准:

- 单次节点执行结束后没有遗留 Claude subprocess。
- 测试能证明异常路径也清理。

### 第四优先级: 错误语义与 SummaryAgent 稳定性

1. `single_prompt()` 不再默认吞掉 cancellation。
2. SummaryAgent 区分 timeout/cancelled/empty response。
3. SummaryAgent timeout 放宽或动态化。
4. SummaryAgent 使用 `output_format` 或 `extract_json()`。

验收标准:

- 日志能区分 `CancelledError`、timeout、空响应、JSON 解析失败。
- transient LLM latency 不会轻易产生误导性 Empty response。

## 建议测试清单

### T1: graph cancellation finalizes pipeline

模拟 `graph.ainvoke()` 抛出 `asyncio.CancelledError`。

期望:

- StateManager 被更新为 `cancelled` 或 `failed/interrupted`。
- `error.type == "CancelledError"`。
- 不留下普通 running 状态。

### T2: CLI KeyboardInterrupt finalizes pipeline

模拟用户 Ctrl+C。

期望:

- CLI 输出明确的 interrupted/cancelled。
- DB 状态不是 running。
- session cleanup 被调用。

### T3: stale-running detection

构造 running pipeline，`last_heartbeat_at` 超过阈值，owner pid 不存在。

期望:

- status 返回 `stale=true`。
- list 显示 stale 标记。
- resume 不误报“already running”，或提示 `--force` 的原因。

### T4: session id persistence

mock `SessionManager.create_session()` 返回固定 session id。

期望:

- `current_node_session_id` 写入 DB。
- `session_ids[analyst]` 写入 DB。
- `session_metadata[analyst]` 包含 cwd/output_dir/allowed_tools。

### T5: per-node SessionManager closes on all paths

分别模拟:

- prompt 成功。
- prompt 抛 `LLMError`。
- prompt 抛 `asyncio.CancelledError`。

期望:

- `pipeline_session_manager.close_all()` 都被调用一次。
- original session_manager 总能恢复。

### T6: cancellation is not empty response

mock `query()` 抛 `asyncio.CancelledError`。

期望:

- `single_prompt()` 不返回 `[]`。
- 上层日志保留 cancellation 类型。
- SummaryAgent 不把它记录成 `Empty response from LLM`。

## 最终判断

本次日志暴露的是 DocuSwarm 的运行时韧性问题，而不是单个 agent 输出质量问题。

可以证明的根因链是:

```text
analyst session 进行中
→ 进程/执行流在 message 5 后停止
→ 没有 terminal exception/finalizer/heartbeat
→ StateManager 仍保留 graph 前写入的 running 状态
→ output/node_results/current_node_session_id 均为空
→ 用户看到一个假 running pipeline
```

优先修复应放在“中断路径状态最终化 + in-flight session 持久化 + stale-running 检测”，而不是继续围绕 SummaryAgent warning 做局部补丁。SummaryAgent 的取消/空响应分类仍需修，但它在本次运行中不是最终阻断点。

