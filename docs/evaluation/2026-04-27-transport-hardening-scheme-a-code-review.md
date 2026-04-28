# Transport Hardening Scheme A 代码审查报告

**审查日期**: 2026-04-27  
**审查对象**: `autoBMAD/docuswarm`  
**参考研究**: `docs-doc/research/2026-04-27-transport-hardening-scheme-a-research.md`  
**重点文件**:

- `autoBMAD/docuswarm/llm/session_manager.py`
- `autoBMAD/docuswarm/utils/logging.py`
- `tests/docuswarm/llm/test_transport_hardening_scheme_a.py`
- 已安装 `claude_agent_sdk` 0.1.44 的 `client.py`、`_internal/query.py`、`_internal/transport/subprocess_cli.py`

## 执行摘要

当前代码已经出现了方案 A 的落地痕迹，尤其是 A-1 idle watchdog、A-3 stderr callback、A-4 消息元数据日志和 A-2 close 后 force kill 兜底。但审查结果显示：实现并未完全达到研究报告的防护目标。

最关键的问题是 A-2。`ClaudeSessionWrapper.close()` 在 `await self._client.disconnect()` 之后才读取 `_transport._process`，而当前安装的 `claude_agent_sdk` 0.1.44 在 `ClaudeSDKClient.disconnect()` 结束时会执行 `self._transport = None`。因此真实 SDK 路径上，DocuSwarm 的 force-kill fallback 很可能拿不到进程句柄。更糟的是，如果 SDK 的 `transport.close()` 自身卡在 `await process.wait()`，DocuSwarm 的 fallback 代码根本没有机会执行。

另外，A-4 的文件日志字段丢失仍然存在。虽然 `session_manager.py` 和 `independent.py` 已经在 logger 调用中传入 `msg_type`、`message_index`、`has_role`，但 `utils/logging.py` 的非 JSON 文件落盘格式只写 `timestamp/level/run_id/node_id/message`，丢弃了额外字段。实际 `logs/docuswarm-2026-04-27.log` 中仍可看到大量 `message="llm_message_received"`，没有消息类型和序号。

## 审查结论总览

| 项 | 研究目标 | 当前状态 | 结论 |
|---|---|---|---|
| A-1 | prompt idle watchdog | 已实现 | 基本可用，但未配置化，异常后不主动清理 session/process |
| A-2 | 子进程硬杀兜底 | 部分实现 | 真实 SDK 路径大概率失效，且 `close_all()` 绕过 wrapper |
| A-3 | CLI stderr 捕获 | 已实现 | 基本可用，但敏感信息过滤只按字段名，不会过滤 `line_preview` 内容 |
| A-4 | 日志关键字段落地 | 部分实现 | logger 调用已传字段，默认文件日志仍丢字段 |

## 主要发现

### HIGH: A-2 force-kill fallback 在真实 SDK 路径上失效

**位置**:

- `autoBMAD/docuswarm/llm/session_manager.py:1146-1167`
- `claude_agent_sdk/client.py:399-404`
- `claude_agent_sdk/_internal/query.py:615-623`
- `claude_agent_sdk/_internal/transport/subprocess_cli.py:466-475`

**现象**:

`ClaudeSessionWrapper.close()` 当前顺序如下：

1. `await self._client.disconnect()`
2. `transport = getattr(self._client, "_transport", None)`
3. `process = getattr(transport, "_process", None)`
4. 如果 `process.returncode is None`，再 `process.kill()`

但已安装 SDK 0.1.44 的 `ClaudeSDKClient.disconnect()` 逻辑是：

1. 如果 `_query` 存在，执行 `await self._query.close()`
2. `_query.close()` 执行 `await self.transport.close()`
3. SDK transport close 中对进程执行 `terminate()` 后 `await self._process.wait()`
4. `disconnect()` 最后设置 `self._transport = None`

因此在 `disconnect()` 正常返回后，DocuSwarm 再取 `self._client._transport` 已经是 `None`，force-kill fallback 不会运行。若 `transport.close()` 卡在 `await self._process.wait()`，`disconnect()` 甚至不会返回，fallback 代码同样不会运行。

**影响**:

- 研究报告要求的“硬杀兜底”没有覆盖真实失败路径。
- idle timeout 或 total timeout 后如果后续清理依赖 wrapper close，仍可能残留 CLI 子进程。
- 当前单测无法暴露该问题，因为测试里的 `mock_sdk_client.disconnect` 不会模拟 SDK 把 `_transport` 清空，也不会模拟 `disconnect()` 内部卡住。

**建议修复**:

- 在调用 `disconnect()` 前先捕获 `transport` 和 `process` 引用。
- 对 `disconnect()` 本身加 `asyncio.wait_for()`，例如 5 到 10 秒。
- 如果 `disconnect()` 超时或返回后进程仍存活，使用预先捕获的 `process.kill()` 并等待 `process.wait()`。
- 将清理逻辑封装成一个 helper，避免 `close()` 和 `close_all()` 出现两套行为。

### HIGH: `SessionManager.close_all()` 绕过 `ClaudeSessionWrapper.close()`

**位置**: `autoBMAD/docuswarm/llm/session_manager.py:943-965`

**现象**:

`SessionManager` 当前只在 `_active_clients` 中保存 `ClaudeSDKClient`，`close_all()` 直接调用：

```python
await client.disconnect()
```

这会完全绕过 `ClaudeSessionWrapper.close()` 中的 A-2 fallback。即使修好 wrapper close，批量关闭和上下文管理器退出路径仍然无法获得 DocuSwarm 自己的硬杀兜底。

**影响**:

- `async with SessionManager(...)` 退出时不会走 wrapper 的增强清理。
- pipeline 收尾时如果调用 `close_all()`，A-2 防护不生效。
- 这会让“单个 wrapper close 已测试通过”与“生产生命周期安全”之间出现偏差。

**建议修复**:

- `_active_clients` 改为保存 wrapper，或增加 `SessionManager._close_client_with_process_fallback(client, session_id)`。
- `ClaudeSessionWrapper.close()` 和 `SessionManager.close_all()` 共享同一个 close helper。
- 增加覆盖 `close_all()` 的单测，模拟真实 SDK 的 `_transport = None` 行为和 `disconnect()` 超时行为。

### HIGH: prompt idle/total timeout 后没有主动清理 SDK session

**位置**: `autoBMAD/docuswarm/llm/session_manager.py:1093-1144`

**现象**:

`prompt()` 中 idle watchdog 触发后会抛出 `LLMError`，`finally` 里只取消 watchdog task：

```python
finally:
    watchdog.cancel()
    with suppress(asyncio.CancelledError):
        await watchdog
```

没有对当前 `ClaudeSDKClient` 执行 disconnect，也没有标记 session 不可复用。`TimeoutError` 路径同样只是记录 `prompt_timeout` 后抛出 `LLMError`。

**影响**:

- 触发 idle watchdog 的场景本身就意味着 transport 可能已经异常静默。此时只停止 Python 层的 prompt 迭代，不等于停止 CLI 子进程。
- 上游如果捕获异常后继续运行，后台 SDK read task 或 CLI 子进程可能仍然存在，直到更外层 `close_all()` 被调用。而 `close_all()` 当前又绕过 wrapper fallback。
- 同一个 wrapper 的 `_prompt_lock` 会释放，调用方理论上可以再次 prompt 到一个已经处于未知状态的 SDK session。

**建议修复**:

- 在 idle timeout 和 total timeout 路径上触发 session close 或标记 wrapper 为 closed/unusable。
- 关闭逻辑必须使用修复后的 process fallback，而不是裸 `client.disconnect()`。
- 为 `prompt_idle_exceeded` 增加测试，断言触发后会调用清理逻辑，且清理逻辑能处理 `disconnect()` 超时。

### MEDIUM: A-1 idle timeout 没有运行时配置入口

**位置**: `autoBMAD/docuswarm/llm/session_manager.py:996-999`

**现象**:

`ClaudeSessionWrapper.IDLE_TIMEOUT` 是类常量，当前值为 300 秒。测试通过 monkey patch 验证“可改”，但生产配置中没有 `DOCUSWARM_IDLE_TIMEOUT`、yaml 字段或按 mode 调整的入口。

研究报告建议 idle timeout 可配置，并在 thinking 场景延长。当前 `_create_options(mode="thinking")` 会开启 thinking，但 `ClaudeSessionWrapper` 没有接收 mode，也不会据此调整 idle timeout。

**影响**:

- 300 秒比研究建议的 120 到 180 秒更保守，能降低误杀，但也会把静默 transport 的发现时间拉长到 5 分钟以上。
- 如果未来需要在 CI、长推理、交互式调试中调参，只能改代码或 monkey patch。

**建议修复**:

- 在配置中增加 `transport_idle_timeout_seconds`。
- `create_session()` 创建 wrapper 时传入 mode 和 idle timeout。
- 对 thinking 模式使用显式策略，例如默认 300 秒，agent 模式 120 到 180 秒，允许配置覆盖。

### MEDIUM: A-4 默认文件日志仍丢弃关键字段

**位置**:

- `autoBMAD/docuswarm/utils/logging.py:111-157`
- `autoBMAD/docuswarm/llm/session_manager.py:1118-1124`
- `autoBMAD/docuswarm/agents/independent.py:437-444`
- `logs/docuswarm-2026-04-27.log`

**现象**:

代码已经在 `llm_message_received` 事件里传入：

- `msg_type`
- `message_index`
- `has_role`

但 `_write_to_file()` 在非 JSON 模式下只写：

```text
timestamp [level] run_id=... node_id=... message="..."
```

实际日志样本仍然是：

```text
2026-04-27T12:58:17.251964+08:00 [debug] run_id=... node_id=analyst message="llm_message_received"
```

没有 `msg_type`、`message_index`、`has_role`，也没有 `messages_received_before_timeout` 等 timeout 诊断字段。

**影响**:

- A-4 在 logger 调用层“看起来修了”，但默认文件日志仍不可诊断。
- 研究报告中的实际问题仍然存在：排查 hang 时无法从日志判断最后一条消息类型、序号和状态。
- 当前 A-4 单测只 patch 了 logger 调用参数，没有验证文件落盘结果，因此无法发现该问题。

**建议修复**:

- 非 JSON 文件日志也应渲染额外字段，例如追加 `key=value`。
- 或默认启用 JSON 文件日志，保留所有 event_dict 字段。
- 增加日志落盘测试：调用 `configure_logging(json_format=False)` 后写入 `llm_message_received`，断言文件中包含 `msg_type` 和 `message_index`。

### MEDIUM: stderr callback 内容可能绕过敏感信息过滤

**位置**:

- `autoBMAD/docuswarm/llm/session_manager.py:129-150`
- `autoBMAD/docuswarm/utils/logging.py:84-99`

**现象**:

`_stderr_callback()` 将 stderr 行放到 `line_preview` 字段中。敏感信息过滤器 `_redact_sensitive_fields()` 只按字段名判断，例如 `api_key`、`token`、`authorization`。由于字段名是 `line_preview`，如果 stderr 内容本身包含 token 或 URL query secret，当前过滤器不会处理字符串内容。

**影响**:

- CLI stderr 通常不应打印密钥，但 debug/error 输出无法完全信任。
- A-3 提升了可观测性，也扩大了日志泄漏面。

**建议修复**:

- 对 `line_preview` 做内容级脱敏，至少覆盖常见 `sk-...`、`Bearer ...`、`ANTHROPIC_API_KEY=...`、`api_key=...`。
- 保留 `line_length`，必要时限制 `line_preview` 到更短长度。

### LOW: `llm_message_received` 事件可能重复计数

**位置**:

- `autoBMAD/docuswarm/llm/session_manager.py:1118-1124`
- `autoBMAD/docuswarm/agents/independent.py:437-444`

**现象**:

wrapper 层和 IndependentAgent 层都记录 `llm_message_received`。字段名类似，但含义不完全一样：wrapper 记录原始 SDK 消息流，IndependentAgent 记录业务消费消息。

**影响**:

- 如果后续用日志做指标统计，可能重复计数。
- 两层日志没有 `source` 或 `component` 字段落到默认文件日志中，进一步增加混淆。

**建议修复**:

- 将事件名区分为 `sdk_message_received` 和 `agent_message_received`，或添加 `message_source` 字段。
- 修复 A-4 文件字段落盘后，此问题会更容易观察和处理。

## 测试评估

执行命令：

```powershell
pytest -q tests\docuswarm\llm\test_transport_hardening_scheme_a.py
```

结果：

- 11 个测试通过。
- 有 pytest cache 写入权限 warning，不影响该测试文件的执行结果。

但这些测试存在明显盲区：

- A-2 测试使用 `MagicMock`，没有模拟真实 SDK `disconnect()` 后 `_transport = None`。
- 没有模拟 `disconnect()` 卡住，因此无法证明 fallback 能在 SDK close hang 时执行。
- 没有覆盖 `SessionManager.close_all()`，生产收尾路径绕过了 wrapper close。
- A-4 测试只验证 logger 调用参数，没有验证默认文件日志是否包含字段。
- A-1 测试验证 idle 会抛错，但没有验证抛错后是否清理 SDK session 和 CLI 子进程。

## 建议修复优先级

1. **P0: 重写 A-2 清理顺序**  
   在 `disconnect()` 前捕获 process，给 `disconnect()` 加 timeout，超时或进程未退出时执行 kill。`close()` 和 `close_all()` 共享同一逻辑。

2. **P0: prompt timeout 后主动清理 session**  
   idle timeout 和 total timeout 触发后，关闭或废弃当前 session，避免异常 transport 继续存在。

3. **P1: 修复文件日志字段落盘**  
   默认非 JSON 日志必须输出 event_dict 额外字段，或者默认使用 JSON 文件日志。

4. **P1: 增加真实 SDK 行为单测**  
   模拟 `ClaudeSDKClient.disconnect()` 清空 `_transport`，模拟 `disconnect()` 永不返回，覆盖 `close_all()`。

5. **P2: 配置化 idle timeout 和 stderr 脱敏**  
   让 idle timeout 可通过配置和 mode 策略调整，对 stderr 内容做基本脱敏。

## 总体判断

方案 A 的方向正确，当前代码也已经完成了一部分实现。但从“能否在真实 transport hang 场景中可靠止损”的角度看，A-2 仍未达标，A-1 的错误路径也缺少主动清理。A-4 的日志字段修复停留在 logger 调用层，默认文件日志仍然丢失诊断字段。

建议先修 A-2 和 timeout 后清理，再补强测试。否则现在的绿灯测试会给出过强的安全感，而生产路径仍可能在 SDK close 或子进程退出上卡住。
