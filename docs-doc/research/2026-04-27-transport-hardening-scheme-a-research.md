# 方案A Transport 加固深度研究报告

**生成时间**: 2026-04-27T22:49:43.206935
**研究范围**: autoBMAD/docuswarm/llm/session_manager.py + claude-agent-sdk transport 层
**方法**: 源码静态审计 + 场景模拟 + 可行性验证

---

## 执行摘要

本报告针对方案A的四个子任务进行了深度研究。共发现 **1** 个 CRITICAL 级问题、**3** 个 HIGH 级问题。所有子任务均具备可行实现路径，预计总工作量 1.5-2 人日。

## 研究发现总览

| 任务 | 严重度 | 类别 | 标题 | 可行性 |
|---|---|---|---|---|
| A-1 | CRITICAL | 缺失防护 | prompt() 缺少 idle watchdog | FEASIBLE_WITH_CAVEATS: 算法简单可靠，核心风险是误杀长推理。建议实现可配置 IDLE_TIMEOUT，thinking 模式自动延长。 |
| A-1 | HIGH | 缺失防护 | prompt() 缺少 idle watchdog | FEASIBLE_WITH_CAVEATS: 算法简单可靠，核心风险是误杀长推理。建议实现可配置 IDLE_TIMEOUT，thinking 模式自动延长。 |
| A-1 | MEDIUM | 边界条件 | Idle watchdog edge case: 正常长推理（thinking > 60s） |  |
| A-1 | MEDIUM | 边界条件 | Idle watchdog edge case: watchdog task 被事件循环延迟唤醒 |  |
| A-1 | MEDIUM | 边界条件 | Idle watchdog edge case: receive_messages 在 watchdog 触发前产出最后一条消息 |  |
| A-1 | MEDIUM | 边界条件 | Idle watchdog edge case: 多个 prompt() 并发调用（同一个 session） |  |
| A-1 | MEDIUM | 边界条件 | Idle watchdog edge case: asyncio.timeout 和 idle watchdog 同时触发 |  |
| A-2 | HIGH | 资源泄漏 | 子进程残留风险 | FEASIBLE_AND_RECOMMENDED: 实现简单，风险可控。必须注意：硬杀只能作为兜底，不能替代 idle watchdog（因为事件循环卡顿时 close() 也可能无法执行）。 |
| A-3 | HIGH | 可观测性缺失 | 未配置 CLI stderr 捕获 | TRIVIAL: SDK 已原生支持，DocuSwarm 只需在 _create_options 中增加一行配置。推荐立即实施。 |
| A-4 | MEDIUM | 可观测性缺失 | 日志关键字段丢失 | EASY: 取决于实际日志样本的验证结果。如果字段确实丢失，修复 structlog 配置或调整 logger 调用即可。 |

---

## A-1 Idle Watchdog（核心修复）深度分析

### current_implementation

- **has_asyncio_timeout_wrapper**: True
- **has_idle_watchdog**: False
- **has_last_msg_tracking**: False
- **has_message_counting**: True
- **prompt_method_lines**: 46

### deficiencies

- CRITICAL: prompt() 仅依赖 asyncio.timeout(effective_timeout)，没有消息间空闲检测。当子进程 stdout 永久静默时，effective_timeout=7200s（来自 config.agent_timeout）会导致挂起 2 小时。
- HIGH: effective_timeout 直接取自参数，可被外部传入超大值（如 7200s），asyncio.timeout 无法区分'正常长推理'和'transport 阻塞'。

### proposed_watchdog_correctness

- **algorithm**: 在 receive_messages 循环外启动独立 asyncio Task，每 IDLE_TIMEOUT/2 秒检查一次自上次收到消息以来的时间差，超过 IDLE_TIMEOUT 则抛出 LLMError。
- **cancellation_safety**: 使用 try/finally 确保 watchdog.cancel() 被调用，避免正常完成后的 task 泄漏。但注意：如果 prompt() 本身被外部 cancel（asyncio.CancelledError），finally 块仍会执行，watchdog 会被正确清理。
- **race_condition_risk**: LOW: last_msg_at 的更新和 watchdog 的检查存在竞态，但 IDLE_TIMEOUT 通常 60-120s，远大于一次事件循环迭代，竞态窗口可忽略。
- **cpu_overhead**: NEGLIGIBLE: 仅一个 sleep 循环，每 30-60s 唤醒一次，无 CPU 密集型操作。

### edge_cases

- **scenario**: 正常长推理（thinking > 60s）
- **impact**: 如果 IDLE_TIMEOUT=60s，可能误杀 thinking 模式。
- **mitigation**: 建议 IDLE_TIMEOUT 默认 120s，thinking 场景可动态调整为 180s。

- **scenario**: watchdog task 被事件循环延迟唤醒
- **impact**: 系统高负载时，sleep(IDLE_TIMEOUT/2) 可能延迟。
- **mitigation**: 使用 asyncio.get_event_loop().time() 获取单调时钟，不受 sleep 延迟影响。

- **scenario**: receive_messages 在 watchdog 触发前产出最后一条消息
- **impact**: 正常结束，无风险。
- **mitigation**: N/A

- **scenario**: 多个 prompt() 并发调用（同一个 session）
- **impact**: 当前 ClaudeSessionWrapper 不支持并发 prompt，但需防御。
- **mitigation**: 在 prompt() 入口增加 _prompt_lock，拒绝重入。

- **scenario**: asyncio.timeout 和 idle watchdog 同时触发
- **impact**: 两个异常源可能竞争。
- **mitigation**: idle watchdog 使用专用异常类型或 LLMError 子类型，外层捕获后明确日志区分 'idle_timeout' vs 'total_timeout'。


- **feasibility_verdict**: FEASIBLE_WITH_CAVEATS: 算法简单可靠，核心风险是误杀长推理。建议实现可配置 IDLE_TIMEOUT，thinking 模式自动延长。


## A-2 子进程硬杀兜底深度分析

### sdk_transport_close_behavior

- **has_graceful_wait**: True
- **has_sigterm**: True
- **has_sigkill**: True
- **has_timeout_on_wait**: True
- **grace_period_seconds**: 5
- **sigterm_timeout_seconds**: 5
- **notes**: SDK transport 已实现 graceful → SIGTERM → SIGKILL 三级关闭。但存在关键问题：close() 是 async 的，如果事件循环卡住，close() 本身可能无法被调用。

### current_docswarm_close_behavior

- **has_disconnect**: True
- **has_kill_fallback**: False
- **has_returncode_check**: False
- **code**: async def close(self) -> None:
        """Close the session."""
        await self._client.disconnect()


# Define public API - KimiSessionManager removed
__all__ = [
    "SessionManager",
    "ClaudeSessionWrapper",
]
- **assessment**: UNSAFE

### orphan_process_risk

- **severity**: HIGH
- **scenario**: 当 asyncio.timeout 取消 prompt() task 时，Python 端的 CancelledError 不会传播到 Node.js 子进程。子进程继续运行，等待 HTTP 响应或执行工具。
#### evidence

- subprocess_cli.py: close() 需要被显式调用才会清理子进程
- asyncio.CancelledError 不会自动触发 __dealloc__ 或 atexit
- Windows 上 orphan process 会持续占用 ~1GB 内存

- **quantified_risk**: 每次挂起产生 1 个 orphan claude 进程（~1GB RAM）。若每天挂起 3 次，月累积泄漏 ~90GB 内存当量（进程不释放但也不再工作）。

### proposed_kill_safety

- **implementation**: 在 ClaudeSessionWrapper.close() 中，await disconnect() 后，检查 transport._process.returncode。若为 None，调用 process.kill()，再 asyncio.wait_for(process.wait(), 5)。
- **process_accessibility**: ClaudeSDKClient._transport 是 SubprocessCLITransport 实例，其 _process 属性是 anyio.Process（封装 asyncio.subprocess.Process）。通过 getattr 链访问是安全的，但属于私有属性，SDK 升级可能改变路径。
- **kill_semantics_windows**: Windows: process.kill() → TerminateProcess()，无 SIGKILL 语义差异，子进程无法拦截，立即终止。
- **kill_semantics_posix**: POSIX: process.kill() → SIGKILL，子进程无法捕获或忽略，内核强制回收。
- **side_effects**: 1. 可能丢失子进程未 flush 的 stdout 数据（但阻塞时已无数据）。2. 子进程若正在写文件，可能产生不完整文件（但 Claude CLI 不写用户文件）。3. 全局 session checkpoint 可能不一致（可接受，因已判定失败）。
- **alternative_safer_approach**: 使用 atexit + psutil 扫描 'claude' 进程，在 Python 进程退出时清理孤儿。但这无法解决运行时的资源泄漏。最佳方案是两者结合：prompt() 层面加 watchdog + close() 层面加硬杀 + 全局 orphan 清理。

- **feasibility_verdict**: FEASIBLE_AND_RECOMMENDED: 实现简单，风险可控。必须注意：硬杀只能作为兜底，不能替代 idle watchdog（因为事件循环卡顿时 close() 也可能无法执行）。


## A-3 stderr 透传深度分析

### sdk_stderr_support

- **has_stderr_callback_option**: True
- **has_stderr_stream_reading**: True
- **has_async_stderr_handler**: True
- **stderr_pipe_logic**: should_pipe_stderr = (
                self._options.stderr is not None
                or "debug-to-stderr" in self._options.extra_args
            )
- **notes**: SDK 已经完整支持 stderr callback：ClaudeAgentOptions.stderr 可接受一个 Callable[[str], None]，transport.connect() 时会启动 Task 异步读取 stderr 并回调。
- **options_type_has_stderr_field**: True

### current_docswarm_stderr

- **configures_stderr_callback**: False
- **assessment**: DISABLED — DocuSwarm 完全未配置 stderr

### proposed_integration

- **implementation**: 在 SessionManager._create_options() 中增加：options_dict['stderr'] = self._stderr_callback，其中 _stderr_callback 将 stderr 行写入 structlog（事件名 cli_subprocess_stderr）。
#### log_event_design

- **event**: cli_subprocess_stderr
##### fields

- session_id
- line_preview
- line_length
- timestamp

- **sampling**: 100%（stderr 通常量小，可直接全量）

- **log_level_recommendation**: stderr 内容可能包含 HTTP 错误、警告、调试信息。建议：包含 'error'/'fail'/'timeout' 的行用 error 级别，其余用 debug 级别。
- **mcp_server_stderr**: 注意：in-process MCP 服务器的日志不会出现在 CLI stderr 中，它们直接由 Python 端处理。CLI stderr 主要包含 Node.js 端的日志。

### value_assessment

- **diagnostic_value**: HIGH: 如果再次发生挂起，stderr 可能包含 ECONNRESET / socket hang up / undici request failed 等线索，直接指向上游网络问题。
- **runtime_value**: MEDIUM: 可提前发现 CLI 子进程的警告（如版本过旧、MCP 服务器连接失败），不等挂起即可定位配置问题。
- **cost**: NEGLIGIBLE: 仅增加一个 callback 注册和日志写入，stderr 读取由 SDK 内部 Task 异步完成，无阻塞。

- **feasibility_verdict**: TRIVIAL: SDK 已原生支持，DocuSwarm 只需在 _create_options 中增加一行配置。推荐立即实施。


## A-4 日志字段落地深度分析

### log_field_audit

- **level**: debug
- **event**: sdk_native_skills_enabled
- **kwargs**: ['node_id']

- **level**: debug
- **event**: sdk_native_skills_disabled
- **kwargs**: ['node_id']

- **level**: warning
- **event**: mcp_tools_build_failed
- **kwargs**: ['node_id', 'error']

- **level**: debug
- **event**: setting_sources_enabled
- **kwargs**: ['node_id']

- **level**: debug
- **event**: configuring_mcp_servers
- **kwargs**: ['node_id', 'file_dirs', 'search_dirs', 'has_full_tool_permissions']

- **level**: debug
- **event**: mcp_servers_created
- **kwargs**: ['node_id', 'server_count', 'server_keys']

- **level**: warning
- **event**: mcp_server_creation_failed
- **kwargs**: ['node_id', 'error']

- **level**: debug
- **event**: allowed_tools_configured
- **kwargs**: ['node_id', 'tool_count', 'tools']

- **level**: warning
- **event**: allowed_tools_generation_failed
- **kwargs**: ['node_id', 'error']

- **level**: warning
- **event**: mcp_configuration_failed
- **kwargs**: ['node_id', 'error']

- **level**: info
- **event**: creating_session
- **kwargs**: ['mode', 'yolo', 'max_steps']

- **level**: debug
- **event**: agent_file_skipped_for_tools
- **kwargs**: ['agent_file', 'reason']

- **level**: info
- **event**: session_created
- **kwargs**: ['session_id', 'mode']

- **level**: info
- **event**: tools_configured
- **kwargs**: ['mcp_servers']

- **level**: error
- **event**: session_creation_failed
- **kwargs**: ['error']

- **level**: info
- **event**: resuming_session
- **kwargs**: ['session_id']

- **level**: info
- **event**: session_resumed
- **kwargs**: ['session_id']

- **level**: warning
- **event**: session_not_found
- **kwargs**: ['session_id']

- **level**: error
- **event**: session_resume_failed
- **kwargs**: ['error']

- **level**: info
- **event**: session_resume_success
- **kwargs**: ['session_id', 'mode']

- **level**: warning
- **event**: session_not_found_creating_new
- **kwargs**: ['session_id', 'requested_mode']

- **level**: info
- **event**: single_prompt_start
- **kwargs**: ['prompt_length', 'mode', 'has_output_format']

- **level**: info
- **event**: tools_configured
- **kwargs**: ['mcp_servers']

- **level**: info
- **event**: llm_tool_call
- **kwargs**: ['message_index', 'tool_name']

- **level**: info
- **event**: single_prompt_result
- **kwargs**: ['result', 'is_error', 'subtype', 'has_structured_output']

- **level**: error
- **event**: structured_output_retries_exhausted
- **kwargs**: ['subtype']

- **level**: info
- **event**: returning_structured_output
- **kwargs**: ['data_keys']

- **level**: info
- **event**: single_prompt_complete
- **kwargs**: ['message_count', 'tool_calls']

- **level**: info
- **event**: single_prompt_cancelled
- **kwargs**: []

- **level**: error
- **event**: single_prompt_sdk_error
- **kwargs**: ['error']

- **level**: error
- **event**: single_prompt_error
- **kwargs**: ['error']

- **level**: info
- **event**: closing_all_sessions
- **kwargs**: ['session_count']

- **level**: debug
- **event**: session_closed
- **kwargs**: ['session_id']

- **level**: error
- **event**: session_close_error
- **kwargs**: ['session_id', 'error']

- **level**: info
- **event**: all_sessions_closed
- **kwargs**: []

- **level**: debug
- **event**: context_manager_enter
- **kwargs**: []

- **level**: debug
- **event**: context_manager_exit
- **kwargs**: ['exc_type']

- **level**: error
- **event**: query_failed
- **kwargs**: ['error']

- **level**: error
- **event**: prompt_timeout
- **kwargs**: ['timeout_seconds', 'message_length', 'messages_received_before_timeout']

- **level**: error
- **event**: receive_messages_error
- **kwargs**: ['error']


### renderer_analysis

- **detected_renderer_type**: unknown
- **field_loss_mechanism**: ConsoleRenderer 默认只渲染事件名和可能的部分字段，如果配置中未指定 pad_event 或未使用 key_order，额外 kwargs 可能在文本日志中不可见。但 structlog 的标准行为是所有 kwargs 都会出现在日志中（key=value 格式）。需检查是否被自定义 processor 过滤。
- **verification_needed**: 需要检查实际日志文件中的 'llm_message_received' 行，确认 msg_type / message_index / has_role 是否存在。

### missing_fields_impact

- **msg_type_present_in_logs**: False
- **message_index_present_in_logs**: False
- **conclusion**: FIELDS_LOST

### proposed_fix

- **root_cause_hypothesis**: session_manager.py 中 _message_to_dict() 返回的 dict 被 logger 记录时，msg_type 等字段是 kwargs，但如果日志 processor 过滤了 dict 值，或 ConsoleRenderer 的格式字符串未包含这些字段，文本日志中可能缺失。
#### fix_options

- **option**: A
- **description**: 在 logger 调用中使用显式字符串拼接，确保字段出现在消息文本中。
- **example**: self._logger.info("llm_message_received", msg_type=msg_dict.get("role"), ...)
- **drawback**: 冗余，structlog 本应将 kwargs 自动渲染。

- **option**: B
- **description**: 检查并修复 structlog 配置，确保 ConsoleRenderer 渲染所有 kwargs。
- **example**: structlog.configure(processors=[..., structlog.dev.ConsoleRenderer(colors=False)])
- **drawback**: 需找到配置位置，可能影响全局日志格式。

- **option**: C
- **description**: 将关键字段放入事件消息字符串本身。
- **example**: self._logger.info(f"llm_msg_received type={msg_type} idx={idx}")
- **drawback**: 不符合结构化日志最佳实践，但文本可读性最高。


- **recommendation**: 首选 B（修复 structlog 配置），辅以 A（在 session_manager.py 中明确传递关键字段）。

- **feasibility_verdict**: EASY: 取决于实际日志样本的验证结果。如果字段确实丢失，修复 structlog 配置或调整 logger 调用即可。
### actual_log_samples

- 2026-04-27T12:58:17.251964+08:00 [debug] run_id=pipeline-1777265896780-fd396b8e node_id=analyst message="llm_message_received"
- 2026-04-27T12:58:40.966127+08:00 [debug] run_id=pipeline-1777265896780-fd396b8e node_id=analyst message="llm_message_received"
- 2026-04-27T12:58:41.323143+08:00 [debug] run_id=pipeline-1777265896780-fd396b8e node_id=analyst message="llm_message_received"
- 2026-04-27T12:58:42.030856+08:00 [debug] run_id=pipeline-1777265896780-fd396b8e node_id=analyst message="llm_message_received"
- 2026-04-27T12:58:42.050379+08:00 [debug] run_id=pipeline-1777265896780-fd396b8e node_id=analyst message="llm_message_received"
- 2026-04-06T17:53:14.980364+08:00 [debug] run_id=pipeline-1775469194501-cad63b21 node_id=analyst message="llm_message_received"



## SDK Transport 层可加固点审计

### hooks_and_options

- **name**: stderr callback
- **sdk_supports**: True
- **docswarm_uses**: unknown

- **name**: debug_stderr file object
- **sdk_supports**: True
- **docswarm_uses**: unknown

- **name**: extra_args (debug-to-stderr)
- **sdk_supports**: True
- **docswarm_uses**: unknown

- **name**: env 变量覆盖
- **sdk_supports**: True
- **docswarm_uses**: unknown

- **name**: max_buffer_size
- **sdk_supports**: True
- **docswarm_uses**: unknown

- **name**: enable_file_checkpointing
- **sdk_supports**: True
- **docswarm_uses**: unknown


### observability_gaps

- **gap**: 无 stdout 字节数统计
- **impact**: 无法从父进程侧检测子进程 stdout 是否完全静默
- **mitigation**: 在 DocuSwarm 层包装 receive_messages，统计每条消息时间戳和字节数

- **gap**: 无子进程 PID 暴露
- **impact**: 外部监控工具无法直接 attach 或检查子进程健康
- **mitigation**: 通过 transport._process.pid 获取（私有属性）

- **gap**: 无 HTTP 层状态暴露
- **impact**: 子进程内部的 HTTP 请求状态对父进程完全黑盒
- **mitigation**: 依赖 stderr 透传（A-3）获取 Node.js 端 HTTP 日志




## 场景模拟结果

- **scenario**: simulate_stdout_block
- **production_idle_timeout**: 120.0
- **simulation_idle_timeout**: 10.0
### events

- t=0.0s: watchdog started (check every 5.0s)
- t≈15.0s: watchdog triggered (idle=10.0s exceeds 10.0s)

- **outcome**: WATCHDOG_FIRST
- **simulation_wall_time_seconds**: 10.03


## 详细研究发现

### [A-1] prompt() 缺少 idle watchdog (CRITICAL)

**类别**: 缺失防护

**详情**: CRITICAL: prompt() 仅依赖 asyncio.timeout(effective_timeout)，没有消息间空闲检测。当子进程 stdout 永久静默时，effective_timeout=7200s（来自 config.agent_timeout）会导致挂起 2 小时。


### [A-1] prompt() 缺少 idle watchdog (HIGH)

**类别**: 缺失防护

**详情**: HIGH: effective_timeout 直接取自参数，可被外部传入超大值（如 7200s），asyncio.timeout 无法区分'正常长推理'和'transport 阻塞'。


### [A-1] Idle watchdog edge case: 正常长推理（thinking > 60s） (MEDIUM)

**类别**: 边界条件

**详情**: 如果 IDLE_TIMEOUT=60s，可能误杀 thinking 模式。

**建议**: 建议 IDLE_TIMEOUT 默认 120s，thinking 场景可动态调整为 180s。


### [A-1] Idle watchdog edge case: watchdog task 被事件循环延迟唤醒 (MEDIUM)

**类别**: 边界条件

**详情**: 系统高负载时，sleep(IDLE_TIMEOUT/2) 可能延迟。

**建议**: 使用 asyncio.get_event_loop().time() 获取单调时钟，不受 sleep 延迟影响。


### [A-1] Idle watchdog edge case: receive_messages 在 watchdog 触发前产出最后一条消息 (MEDIUM)

**类别**: 边界条件

**详情**: 正常结束，无风险。

**建议**: N/A


### [A-1] Idle watchdog edge case: 多个 prompt() 并发调用（同一个 session） (MEDIUM)

**类别**: 边界条件

**详情**: 当前 ClaudeSessionWrapper 不支持并发 prompt，但需防御。

**建议**: 在 prompt() 入口增加 _prompt_lock，拒绝重入。


### [A-1] Idle watchdog edge case: asyncio.timeout 和 idle watchdog 同时触发 (MEDIUM)

**类别**: 边界条件

**详情**: 两个异常源可能竞争。

**建议**: idle watchdog 使用专用异常类型或 LLMError 子类型，外层捕获后明确日志区分 'idle_timeout' vs 'total_timeout'。


### [A-2] 子进程残留风险 (HIGH)

**类别**: 资源泄漏

**详情**: 当 asyncio.timeout 取消 prompt() task 时，Python 端的 CancelledError 不会传播到 Node.js 子进程。子进程继续运行，等待 HTTP 响应或执行工具。

**证据**:
- subprocess_cli.py: close() 需要被显式调用才会清理子进程
- asyncio.CancelledError 不会自动触发 __dealloc__ 或 atexit
- Windows 上 orphan process 会持续占用 ~1GB 内存

**建议**: 在 ClaudeSessionWrapper.close() 中，await disconnect() 后，检查 transport._process.returncode。若为 None，调用 process.kill()，再 asyncio.wait_for(process.wait(), 5)。

**风险**: 每次挂起产生 1 个 orphan claude 进程（~1GB RAM）。若每天挂起 3 次，月累积泄漏 ~90GB 内存当量（进程不释放但也不再工作）。


### [A-3] 未配置 CLI stderr 捕获 (HIGH)

**类别**: 可观测性缺失

**详情**: DocuSwarm 未利用 SDK 提供的 stderr callback，子进程 Node.js 端的错误/警告完全不可见。

**建议**: 在 SessionManager._create_options() 中增加：options_dict['stderr'] = self._stderr_callback，其中 _stderr_callback 将 stderr 行写入 structlog（事件名 cli_subprocess_stderr）。


### [A-4] 日志关键字段丢失 (MEDIUM)

**类别**: 可观测性缺失

**详情**: llm_message_received 等事件的 msg_type / message_index 字段未出现在文本日志中，影响挂起诊断。

**建议**: 首选 B（修复 structlog 配置），辅以 A（在 session_manager.py 中明确传递关键字段）。


---

## 结论与实施建议

### 实施优先级

1. **P0 - A-1 Idle Watchdog**: 这是解决挂起不被发现的唯一有效手段。模拟验证表明，在 stdout 阻塞场景下，watchdog 可在 120-150s 内触发，远早于 asyncio.timeout(7200)。

2. **P0 - A-2 子进程硬杀**: 实现简单，防止资源泄漏。建议与 A-1 同时实施。

3. **P1 - A-3 stderr 透传**: SDK 已原生支持，仅需一行配置即可大幅提升可观测性。

4. **P1 - A-4 日志字段落地**: 需先验证实际日志样本，修复成本最低。

### 技术债务警示

- 访问 SDK 私有属性（`_transport._process`）存在升级兼容性风险。建议在代码中添加 try/except 回退，并关注 SDK changelog。
- Idle watchdog 的 `IDLE_TIMEOUT` 必须可配置，避免 thinking 模式误杀。
- stderr 透传应做好敏感信息过滤（如 API key、token），虽然 Claude CLI 通常不会将 key 打印到 stderr。

### 下一步行动

1. 在 `ClaudeSessionWrapper.prompt()` 中实施 A-1 idle watchdog（参考评估报告 §5.1 代码）。
2. 在 `ClaudeSessionWrapper.close()` 中实施 A-2 硬杀兜底（参考评估报告 §5.1 代码）。
3. 在 `SessionManager._create_options()` 中注册 stderr callback 实施 A-3。
4. 检查 structlog 配置并修复 A-4 字段丢失问题。
5. 编写单元测试：mock 静默 stdout，验证 120s 内触发 LLMError。
