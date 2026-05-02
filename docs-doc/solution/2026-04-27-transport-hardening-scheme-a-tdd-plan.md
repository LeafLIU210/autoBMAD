# 方案A Transport 加固 TDD 执行方案

**日期**: 2026-04-27
**来源**: [深度研究报告](../research/2026-04-27-transport-hardening-scheme-a-research.md)
**目标**: 通过测试驱动开发（TDD）实施方案A的四个子任务

---

## 总体策略

采用 **Red-Green-Refactor** 循环：
1. **Red**: 写 failing test，验证当前行为确实缺失/错误
2. **Green**: 写最小实现，使 test 通过
3. **Refactor**: 清理代码，保持测试通过

---

## 子任务 A-1: Idle Watchdog（核心修复）

### 问题定义
`ClaudeSessionWrapper.prompt()` 仅依赖 `asyncio.timeout(effective_timeout)`，当子进程 stdout 永久静默时，若 effective_timeout 被污染为 7200s，将挂起 2 小时。

### TDD 步骤

#### Test 1: 验证当前无 idle watchdog（Red）
- **测试文件**: `tests/docuswarm/llm/test_transport_hardening_scheme_a.py`
- **测试名**: `test_prompt_should_raise_on_idle_timeout`
- **行为**: Mock `receive_messages()` 为永不产出的 async generator，调用 `prompt()` 并设置短 idle timeout，期望在 idle timeout 后抛出 `LLMError`
- **预期初始状态**: FAIL（当前无 idle watchdog）

#### Test 2: 验证正常消息流不触发 watchdog（Green）
- **测试名**: `test_prompt_should_not_raise_when_messages_keep_coming`
- **行为**: Mock `receive_messages()` 每 0.1s 产出一条消息，共 10 条，idle timeout=1s，总 timeout=5s
- **预期**: 正常完成，不抛异常

#### Test 3: 验证 thinking 模式可配置更长 idle timeout
- **测试名**: `test_prompt_should_use_configurable_idle_timeout`
- **行为**: 设置 IDLE_TIMEOUT=60s，mock 消息间隔 0.5s，不应触发

### 实现要点
- 在 `ClaudeSessionWrapper.__init__` 中增加 `_prompt_lock`（防并发重入）
- 在 `prompt()` 中增加 idle watchdog task
- `IDLE_TIMEOUT` 作为类常量或构造参数，默认 300s
- 使用 `asyncio.get_event_loop().time()` 单调时钟
- 异常类型: `LLMError(f"Transport idle: no message for {idle:.1f}s ...")`
- `try/finally` 确保 watchdog.cancel()

---

## 子任务 A-2: 子进程硬杀兜底

### 问题定义
`ClaudeSessionWrapper.close()` 仅调用 `disconnect()`，当 asyncio cancel 后子进程可能残留。

### TDD 步骤

#### Test 4: 验证 close() 在 disconnect 后检查并硬杀子进程
- **测试名**: `test_close_should_force_kill_orphan_subprocess`
- **行为**: Mock `_client.disconnect()` + mock `_client._transport._process` with `returncode=None`，调用 `close()`，验证 `process.kill()` 被调用
- **预期初始状态**: FAIL

#### Test 5: 验证已完成子进程不被重复 kill
- **测试名**: `test_close_should_not_kill_already_terminated_process`
- **行为**: Mock process with `returncode=0`，调用 `close()`，验证 `kill()` 未被调用

### 实现要点
- `ClaudeSessionWrapper.close()` 中 `await self._client.disconnect()` 后:
  ```python
  transport = getattr(self._client, "_transport", None)
  process = getattr(transport, "_process", None) if transport else None
  if process and process.returncode is None:
      process.kill()
      try:
          await asyncio.wait_for(process.wait(), timeout=5)
      except asyncio.TimeoutError:
          pass
  ```

---

## 子任务 A-3: stderr 透传

### 问题定义
DocuSwarm 未配置 SDK 的 stderr callback，子进程 Node.js 端错误/警告不可见。

### TDD 步骤

#### Test 6: 验证 _create_options 包含 stderr callback
- **测试名**: `test_create_options_should_include_stderr_callback`
- **行为**: 创建 SessionManager，调用 `_create_options()`，验证 options 有 `stderr` 字段且为 callable
- **预期初始状态**: FAIL

#### Test 7: 验证 stderr callback 记录日志
- **测试名**: `test_stderr_callback_logs_to_structlog`
- **行为**: 调用 stderr callback，验证 logger 输出包含 `cli_subprocess_stderr`

### 实现要点
- `SessionManager.__init__` 中创建 `_stderr_callback` 方法
- `_create_options()` 中增加 `options_dict["stderr"] = self._stderr_callback`
- callback 内使用 `self._logger.debug/info/error("cli_subprocess_stderr", line_preview=..., line_length=...)`

---

## 子任务 A-4: 日志字段落地

### 问题定义
`llm_message_received` 等事件的 `msg_type` / `message_index` 等 kwargs 未出现在文本日志中。

### TDD 步骤

#### Test 8: 验证 prompt() 日志包含消息元数据
- **测试名**: `test_prompt_logs_contain_message_metadata`
- **行为**: Mock receive_messages 产出消息，捕获 logger 调用，验证包含 `msg_type` / `message_index`

### 实现要点
- 在 `prompt()` 的 `receive_messages` 循环中，增加日志:
  ```python
  self._logger.info(
      "llm_message_received",
      msg_type=type(msg).__name__,
      message_index=messages_received,
      has_role=getattr(msg, "role", None) is not None,
  )
  ```
- 或在 `_message_to_dict` 调用处记录

---

## 执行计划

| 阶段 | 内容 | 预计时间 |
|---|---|---|
| 1 | 创建测试文件 + Test 1 (A-1 Red) | 10 min |
| 2 | 实现 A-1 idle watchdog + Test 1 Green | 20 min |
| 3 | Test 2, 3 (A-1 边界条件) + 验证 | 15 min |
| 4 | Test 4 (A-2 Red) + 实现 A-2 + Test 4,5 Green | 20 min |
| 5 | Test 6 (A-3 Red) + 实现 A-3 + Test 6,7 Green | 15 min |
| 6 | Test 8 (A-4 Red) + 实现 A-4 + Test 8 Green | 15 min |
| 7 | 运行全部现有测试，修复回归 | 20 min |
| 8 | 代码清理与文档更新 | 10 min |

---

## 回归测试要求

执行 `python -m pytest tests/docuswarm/llm/ -v` 确保：
1. 新测试全部通过
2. 现有 `test_sdk_skills_discovery.py` 测试通过
3. 现有 `test_update_context_server_creation.py` 测试通过
