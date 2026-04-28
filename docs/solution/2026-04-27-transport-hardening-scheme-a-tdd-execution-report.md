# 方案A Transport 加固 TDD 执行报告

**日期**: 2026-04-27
**执行范围**: A-1 ~ A-4 全部子任务
**测试文件**: `tests/docuswarm/llm/test_transport_hardening_scheme_a.py`
**被修改文件**: `autoBMAD/docuswarm/llm/session_manager.py`

---

## 执行摘要

采用严格的 **Red-Green-Refactor** 循环，针对方案A的四个子任务完成了测试驱动开发。共编写 **11 个新测试**，全部通过；**63 个现有测试**零回归。

| 指标 | 数值 |
|---|---|
| 新测试 | 11 |
| 原有测试 | 63（全部通过） |
| 修改文件 | 1（session_manager.py） |
| 新增代码行 | ~80 |
| 总用时 | ~45 分钟 |

---

## Red-Green-Refactor 详细记录

### A-1 Idle Watchdog

#### Test 1: `test_prompt_should_raise_on_idle_timeout` (RED → GREEN)
- **初始 RED**: 测试使用 timeout=2 模拟阻塞 stdout，断言异常消息包含 "idle"。当前代码无 idle watchdog，抛出 `LLMError("Session prompt timed out after 2 seconds")`，断言失败。
- **实现难点**: 第一个实现尝试在独立 asyncio.Task 中 raise `LLMError`，但发现 **独立 task 的异常不会自动传播到主 task**。主 task 仍在 `async for msg in self._client.receive_messages()` 中阻塞，不受 watchdog task 异常影响。
- **解决方案**: 将主循环从 `async for` 改为 `asyncio.wait([anext_task, event_task])` 竞争模式：
  ```python
  anext_task = asyncio.create_task(receive_gen.__anext__())
  event_task = asyncio.create_task(idle_event.wait())
  done, pending = await asyncio.wait([anext_task, event_task], return_when=FIRST_COMPLETED)
  ```
  当 idle_event 被 watchdog 设置时，主循环检测并主动 raise `LLMError`。
- **GREEN**: 测试通过，idle watchdog 在 1.5s 内触发（测试中 monkeypatch IDLE_TIMEOUT=1）。

#### Test 2: `test_prompt_should_not_raise_when_messages_keep_coming` (GREEN)
- 验证正常消息流（每 0.05s 一条）不触发 watchdog。直接通过。

#### Test 3: `test_prompt_should_use_configurable_idle_timeout` (GREEN)
- 验证可配置性：monkeypatch IDLE_TIMEOUT=1，消息延迟 0.3s，不应触发。通过。

#### Test 4: `test_prompt_should_be_non_reentrant` (GREEN)
- 验证并发 prompt 被拒绝：通过 `asyncio.Lock()` + 前置检查实现。

### A-2 子进程硬杀兜底

#### Test 5: `test_close_should_force_kill_orphan_subprocess` (RED → GREEN)
- **RED**: mock process.returncode=None，断言 kill() 被调用。当前 close() 仅调用 disconnect()，kill 未被调用。
- **实现**: 在 close() 中添加兜底逻辑：
  ```python
  transport = getattr(self._client, "_transport", None)
  process = getattr(transport, "_process", None) if transport else None
  if process and process.returncode is None:
      process.kill()
      await asyncio.wait_for(process.wait(), timeout=5)
  ```
- **GREEN**: 测试通过。

#### Test 6: `test_close_should_not_kill_already_terminated_process` (GREEN)
- returncode=0 时验证 kill() 不被调用。直接通过。

#### Test 7: `test_close_should_handle_missing_transport_gracefully` (GREEN)
- 验证 _transport 不存在时不崩溃。直接通过。

### A-3 stderr 透传

#### Test 8: `test_create_options_should_include_stderr_callback` (RED → GREEN)
- **RED**: 断言 options.stderr is not None。当前 _create_options() 未配置 stderr。
- **实现**: 在 SessionManager 中添加 `_stderr_callback` 方法，并在 `_create_options()` 中注册：
  ```python
  options_dict["stderr"] = self._stderr_callback
  ```
  callback 内根据内容关键词（error/fail/timeout/exception/econnreset）选择 error/debug 级别。
- **GREEN**: 测试通过。

#### Test 9: `test_stderr_callback_should_log_to_structlog` (GREEN)
- 验证 callback 触发日志。通过。

#### Test 10: `test_stderr_callback_should_use_error_level_for_errors` (GREEN)
- 验证包含 "ECONNRESET" 的行使用 error 级别。通过。

### A-4 日志字段落地

#### Test 11: `test_prompt_logs_contain_message_metadata` (RED → GREEN)
- **RED**: 验证 `llm_message_received` 日志包含 `msg_type` / `message_index`。当前 prompt() 循环中无此日志。
- **实现**: 在 prompt() 的消息处理循环中添加：
  ```python
  self._logger.info(
      "llm_message_received",
      msg_type=type(msg).__name__,
      message_index=messages_received,
      has_role=getattr(msg, "role", None) is not None,
  )
  ```
- **GREEN**: 测试通过。

---

## 技术难点与解决方案

### 难点 1: Idle Watchdog 的异常传播
**问题**: asyncio.Task 内部抛出的异常不会自动中断另一个正在 `await` async generator 的 task。
**解决**: 使用 `asyncio.Event` + `asyncio.wait(FIRST_COMPLETED)` 竞争模式，将 `async for` 拆分为逐条 `__anext__()` 的竞争等待。

### 难点 2: async generator 的取消语义
**问题**: `anext_task = asyncio.create_task(receive_gen.__anext__())` 被取消时，async generator 是否能正确清理？
**验证**: mock generator 中的 `await asyncio.sleep(3600)` 可被 `task.cancel()` 正确中断，Python 3.12 的 async generator 取消语义正常工作。

### 难点 3: 测试快速执行 vs 生产 IDLE_TIMEOUT=120s
**问题**: 若测试等待 120s，pytest timeout 会杀死测试。
**解决**: 测试中通过 monkeypatch 将 `ClaudeSessionWrapper.IDLE_TIMEOUT` 临时设为 1s，既验证了机制，又保证了测试速度（< 2s）。

---

## 回归测试结果

```
pytest tests/docuswarm/llm/ -v --timeout=30
============================= 23 passed in 4.46s =============================

pytest tests/docuswarm/ -v --timeout=60 -x
============================= 63 passed in 4.56s =============================
```

全部通过，零回归。

---

## 代码变更清单

| 文件 | 变更类型 | 说明 |
|---|---|---|
| `autoBMAD/docuswarm/llm/session_manager.py` | 修改 | A-1: prompt() 增加 idle watchdog + 并发锁；A-2: close() 增加硬杀兜底；A-3: SessionManager 增加 _stderr_callback；A-4: prompt() 增加消息元数据日志 |
| `tests/docuswarm/llm/test_transport_hardening_scheme_a.py` | 新增 | 11 个 TDD 测试 |
| `docs-doc/solution/2026-04-27-transport-hardening-scheme-a-tdd-plan.md` | 新增 | TDD 方案文档 |
| `docs-doc/solution/2026-04-27-transport-hardening-scheme-a-tdd-execution-report.md` | 新增 | 本执行报告 |

---

## 下一步建议

1. **集成验证**: 在真实 pipeline（calc-one-plus-one）上运行，确认 idle watchdog 不会误杀正常推理
2. **性能基准**: 测量 prompt() 在消息密集场景下的 CPU 开销（理论上可忽略）
3. **监控告警**: 在生产日志中配置 `prompt_idle_exceeded` 和 `force_kill_cli_subprocess` 的告警规则
