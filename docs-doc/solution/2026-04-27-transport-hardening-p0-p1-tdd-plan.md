# Transport Hardening Scheme A — P0/P1 测试驱动修复方案

**日期**: 2026-04-27  
**审查来源**: `docs/evaluation/2026-04-27-transport-hardening-scheme-a-code-review.md`  
**目标模块**: `autoBMAD/docuswarm`  
**执行环境**: `venv` (Python 3.12.10)

---

## 1. 目标概述

根据代码审查报告的 P0/P1 修复优先级，本方案采用**测试驱动开发（TDD）**方式，先写失败测试，再修复源码，最后迭代至全部通过。

### 修复范围

| 优先级 | 项 | 目标 | 对应测试文件 |
|---|---|---|---|
| P0 | A-2 清理顺序重写 | disconnect() 前捕获 process，加 timeout，close() 与 close_all() 共享逻辑 | `tests/docuswarm/llm/test_transport_hardening_scheme_a.py` |
| P0 | timeout 后主动清理 | idle/total timeout 后关闭/标记 session，防止异常 transport 残留 | 同上 |
| P1 | A-4 文件日志字段落盘 | 非 JSON 文件日志也输出 event_dict 额外字段（msg_type, message_index 等） | `tests/docuswarm/utils/test_logging_fields.py` |
| P1 | 真实 SDK 行为单测 | 模拟 disconnect() 清空 _transport、disconnect() 永不返回、覆盖 close_all() | `tests/docuswarm/llm/test_transport_hardening_scheme_a.py` |
| P2 | stderr 内容脱敏 | 对 line_preview 做内容级脱敏 | `tests/docuswarm/utils/test_logging_redaction.py` |

---

## 2. 现有状态基线

- 现有测试文件：`tests/docuswarm/llm/test_transport_hardening_scheme_a.py`
- 现有测试数：**11 个全部通过**
- 已知盲区：
  - A-2 测试使用 MagicMock，未模拟真实 SDK `disconnect()` 后 `_transport = None`
  - 未模拟 `disconnect()` 卡住
  - 未覆盖 `SessionManager.close_all()`
  - A-4 测试只验证 logger 调用参数，未验证文件落盘结果
  - A-1 测试验证 idle 会抛错，但未验证抛错后是否清理 session/子进程

---

## 3. 实施步骤

### Phase 1: P0 — A-2 清理顺序重写

#### 3.1.1 设计新 helper

在 `session_manager.py` 中引入**模块级**或 `SessionManager` 级别的异步 helper：

```python
async def _close_client_with_process_fallback(
    client: ClaudeSDKClient,
    logger: structlog.BoundLogger,
    disconnect_timeout: float = 10.0,
    kill_wait_timeout: float = 5.0,
) -> None:
    """Close a client with process fallback.

    1. 在 disconnect() 前预先捕获 _transport._process。
    2. 给 disconnect() 加 asyncio.wait_for() timeout。
    3. 如果 disconnect() 超时或返回后进程仍存活，执行 kill() 并等待。
    """
```

#### 3.1.2 先写测试（红）

新增测试类 `TestRealSDKCloseBehavior`：

1. `test_close_should_pre_capture_process_before_disconnect`  
   模拟 `_transport` 在 `disconnect()` 后被设为 `None`。断言 `kill()` 仍然被调用（因为 pre-captured）。

2. `test_close_should_force_kill_when_disconnect_hangs`  
   模拟 `disconnect()` 永不返回（`AsyncMock(side_effect=asyncio.sleep(3600))`）。断言 `process.kill()` 在 timeout 后被调用。

3. `test_close_all_should_use_fallback_not_bare_disconnect`  
   `SessionManager` 创建 wrapper，调用 `close_all()`。模拟 SDK 清空 `_transport`。断言 fallback kill 发生。

4. `test_close_should_not_crash_when_no_process_attr`  
   transport 没有 `_process` 属性，正常完成。

#### 3.1.3 修改源码（绿）

- `ClaudeSessionWrapper.close()`：
  - disconnect 前 `transport = getattr(self._client, "_transport", None)`
  - `process = getattr(transport, "_process", None)`
  - `await asyncio.wait_for(self._client.disconnect(), timeout=10)`
  - 超时或返回后检查 `process` 存活则 kill
- `SessionManager.close_all()`：
  - 改为保存 wrapper 而非裸 client，或使用同一 helper 关闭 client。
  - 由于 `_active_clients` 当前保存 `ClaudeSDKClient`，引入 `_close_client_with_process_fallback` helper 供 `close_all()` 循环调用。

#### 3.1.4 运行并验证

```powershell
pytest -q tests\docuswarm\llm\test_transport_hardening_scheme_a.py
```

---

### Phase 2: P0 — prompt timeout 后主动清理 session

#### 3.2.1 先写测试（红）

1. `test_prompt_idle_timeout_should_close_session`  
   idle watchdog 触发后，断言 `session_wrapper.close()` 被调用（或 session 被标记 closed）。

2. `test_prompt_total_timeout_should_close_session`  
   `asyncio.timeout` 触发后，断言 session 被关闭/标记。

3. `test_prompt_after_idle_timeout_should_raise_not_reusable`  
   第一次 idle timeout 后，再次调用 `prompt()` 应直接抛 `LLMError`（session 已 unusable）。

#### 3.2.2 修改源码（绿）

- `ClaudeSessionWrapper.__init__`：增加 `_closed = False` 状态。
- `prompt()`：
  - 入口检查 `if self._closed: raise LLMError("Session is closed/unusable")`
  - `except LLMError`（idle）和 `except TimeoutError`（total）后调用 `await self.close()` 并设置 `self._closed = True`
- `close()`：设置 `self._closed = True`

#### 3.2.3 运行并验证

同上。

---

### Phase 3: P1 — A-4 文件日志字段落盘

#### 3.3.1 先写测试（红）

新建 `tests/docuswarm/utils/test_logging_fields.py`：

1. `test_non_json_file_log_should_include_extra_fields`  
   - `configure_logging(json_format=False)`
   - `logger.info("llm_message_received", msg_type="text", message_index=1)`
   - 读取日志文件，断言包含 `msg_type=text` 和 `message_index=1`

2. `test_json_file_log_should_include_extra_fields`  
   - `configure_logging(json_format=True)`
   - 同上，断言 JSON 中包含对应字段

#### 3.3.2 修改源码（绿）

`utils/logging.py` 的 `_write_to_file()`：

非 JSON 模式下，从 `event_dict` 中提取除基础字段外的所有额外字段，追加 `key=value`：

```python
else:
    extra_parts = []
    for key, value in event_dict.items():
        key_str = str(key)
        if key_str not in ["event", "level", "run_id", "node_id", "timestamp", "message"]:
            extra_parts.append(f"{key_str}={value}")
    extra = " ".join(extra_parts)
    line = f'{timestamp} [{level}] run_id={run_id} node_id={node_id} message="{message}" {extra}\n'
```

同时确保 `reset_logging()` 在测试中可清理状态。

#### 3.3.3 运行并验证

```powershell
pytest -q tests\docuswarm\utils\test_logging_fields.py
```

---

### Phase 4: P1 — stderr 内容脱敏（P2 提升）

#### 3.4.1 先写测试（红）

新建 `tests/docuswarm/utils/test_logging_redaction.py`：

1. `test_line_preview_should_redact_sk_token`  
   `line_preview` 包含 `sk-ant-api03-...`，断言被替换为 `[REDACTED]`。

2. `test_line_preview_should_redact_bearer_token`  
   `line_preview` 包含 `Bearer abc123`，断言被替换。

3. `test_line_preview_should_redact_api_key_assignment`  
   `ANTHROPIC_API_KEY=secret`，断言被替换。

#### 3.4.2 修改源码（绿）

`utils/logging.py` 的 `_redact_sensitive_fields()`：

增加对 `line_preview` 值的内容级正则匹配：

```python
# Content-level redaction for line_preview
line_preview = redacted.get("line_preview")
if isinstance(line_preview, str):
    redacted["line_preview"] = _redact_line_content(line_preview)
```

引入 helper `_redact_line_content()` 覆盖常见模式：
- `sk-[a-zA-Z0-9_-]+`
- `Bearer\s+\S+`
- `(?i)(api_key|token|secret)\s*=\s*\S+`

#### 3.4.3 运行并验证

```powershell
pytest -q tests\docuswarm\utils\test_logging_redaction.py
```

---

## 4. 回归测试策略

每完成一个 Phase，执行：

```powershell
pytest -q tests\docuswarm\llm\test_transport_hardening_scheme_a.py
pytest -q tests\docuswarm\utils\test_logging_fields.py
pytest -q tests\docuswarm\utils\test_logging_redaction.py
```

全部完成后执行 broader regression：

```powershell
pytest -q tests\docuswarm\ --tb=short
```

---

## 5. 文件修改清单

| 文件 | 动作 | 说明 |
|---|---|---|
| `autoBMAD/docuswarm/llm/session_manager.py` | 修改 | A-2 helper、close()、close_all()、prompt() 清理 |
| `autoBMAD/docuswarm/utils/logging.py` | 修改 | 文件字段落盘、line_preview 脱敏 |
| `tests/docuswarm/llm/test_transport_hardening_scheme_a.py` | 修改/追加 | 真实 SDK 行为测试、timeout 后清理测试 |
| `tests/docuswarm/utils/test_logging_fields.py` | 新建 | 日志字段落盘测试 |
| `tests/docuswarm/utils/test_logging_redaction.py` | 新建 | stderr 内容脱敏测试 |

---

## 6. 验收标准

- [ ] 所有原有 11 个测试继续通过
- [ ] 新增 A-2 真实 SDK 行为测试 ≥ 4 个，全部通过
- [ ] 新增 timeout 后清理测试 ≥ 3 个，全部通过
- [ ] 新增日志字段落盘测试 ≥ 2 个，全部通过
- [ ] 新增 stderr 脱敏测试 ≥ 3 个，全部通过
- [ ] `pytest -q tests\docuswarm\` 无回归失败
