# Transport Hardening Scheme A — P0/P1 测试驱动执行方案

**日期**: 2026-04-27
**目标模块**: `autoBMAD/docuswarm`
**范围**: `llm/session_manager.py`, `utils/logging.py`
**执行环境**: `venv` (Python 3.12.10)

---

## 1. 目标与范围

根据代码评审报告 `docs-doc/evaluation/2026-04-27-transport-hardening-scheme-a-code-review.md` 中的 P0/P1 修复优先级，以**测试驱动开发（TDD）**方式验证并完善以下修复项：

| 优先级 | 项 | 目标文件 | 当前状态 |
|---|---|---|---|
| P0 | A-2 关闭顺序重写 | `llm/session_manager.py` | 已实现 `_close_client_with_process_fallback`，需补充边界测试 |
| P0 | prompt timeout 清理 session | `llm/session_manager.py` | 已实现 idle/total timeout 后 close，但 `except Exception` 路径遗漏 cleanup |
| P1 | A-4 文件日志字段缺失 | `utils/logging.py` | 已修复非 JSON/JSON 字段落地，测试已覆盖 |
| P1 | 补充真实 SDK 行为模拟 | `tests/docuswarm/llm/test_transport_hardening_scheme_a.py` | 已有测试，需补充 `close_all()` wrapper 状态一致性测试 |
| P2 | stderr 脱敏 | `utils/logging.py` | 已实现 `_LINE_REDACTION_PATTERNS`，测试已覆盖 |

---

## 2. 当前问题诊断

### 2.1 P0-A: `prompt()` 异常路径未关闭 session

`ClaudeSessionWrapper.prompt()` 的异常处理：

```python
except LLMError:
    self._closed = True
    await self.close()
    raise
except TimeoutError as e:
    self._closed = True
    await self.close()
    raise LLMError(...) from e
except Exception as e:          # ← 遗漏 cleanup
    self._logger.error("receive_messages_error", error=str(e))
    raise LLMError(...) from e
```

当 `receive_messages()` 抛出非 timeout/idle 异常（如 SDK 内部崩溃）时，session 不会被关闭，异常 transport 可能残留。

**修复**: 在 `except Exception` 中添加 `self._closed = True; await self.close()`。

### 2.2 P0-B: `SessionManager.close_all()` 不更新 wrapper 状态

`SessionManager._active_clients` 只存储 `ClaudeSDKClient`，不存储 `ClaudeSessionWrapper`。因此 `close_all()` 虽然能断开 client，但 wrapper 的 `_closed` 状态仍为 `False`。调用者复用 wrapper 时不会收到 "session closed" 提示，而是遇到底层断开错误。

**修复**: `SessionManager` 增加 `_active_wrappers` 字典，在 `create_session()` / `resume_session()` 中注册 wrapper；`close_all()` 通过 wrapper.close() 关闭，确保状态同步。

### 2.3 P1-A: `_close_client_with_process_fallback` 边界场景

- `disconnect()` 抛出非 `TimeoutError` 异常时，仍需尝试 kill
- `process.wait()` 超时（kill 后子进程仍不退出）时，需记录 `force_kill_wait_timeout`
- transport 存在但无 `_process` 属性时，需优雅处理

这些场景代码已处理，但测试覆盖不足。

---

## 3. TDD 测试矩阵

### Phase 1 — P0 核心修复验证

| # | 测试名 | 测试类 | 目的 |
|---|---|---|---|
| 1.1 | `test_prompt_exception_should_close_session` | `TestPromptTimeoutCleanup` | `receive_messages` 抛异常后 `_closed=True` |
| 1.2 | `test_prompt_normal_completion_should_not_close_session` | `TestPromptTimeoutCleanup` | 正常完成后 `_closed=False` |
| 1.3 | `test_close_all_should_update_wrapper_closed_state` | `TestRealSDKCloseBehavior` | `close_all()` 后 wrapper 不可用 |
| 1.4 | `test_context_manager_exit_should_close_wrappers` | `TestRealSDKCloseBehavior` | `async with` 退出后 wrapper 被关闭 |
| 1.5 | `test_close_should_handle_disconnect_exception` | `TestRealSDKCloseBehavior` | `disconnect()` 抛异常仍尝试 kill |
| 1.6 | `test_close_should_handle_kill_wait_timeout` | `TestRealSDKCloseBehavior` | `process.wait()` 超时记录 error |

### Phase 2 — P1 日志与 SDK 行为

| # | 测试名 | 测试类 | 目的 |
|---|---|---|---|
| 2.1 | `test_non_json_file_log_should_include_extra_fields` | `TestNonJsonFileLogFields` | 非 JSON 文件日志包含 `msg_type` 等（已有） |
| 2.2 | `test_json_file_log_should_include_extra_fields` | `TestJsonFileLogFields` | JSON 文件日志包含额外字段（已有） |
| 2.3 | `test_line_preview_should_redact_sk_token` | `TestLinePreviewRedaction` | `sk-...` 被脱敏（已有） |
| 2.4 | `test_line_preview_should_redact_bearer_token` | `TestLinePreviewRedaction` | `Bearer ...` 被脱敏（已有） |
| 2.5 | `test_close_should_pre_capture_process_before_disconnect` | `TestRealSDKCloseBehavior` | 预捕获 process（已有） |
| 2.6 | `test_close_should_force_kill_when_disconnect_hangs` | `TestRealSDKCloseBehavior` | disconnect hang 时 fallback（已有） |

---

## 4. 执行步骤

### Step 1 — Red: 编写失败测试

1. 在 `tests/docuswarm/llm/test_transport_hardening_scheme_a.py` 中补充 Phase 1 的 1.1–1.6 测试。
2. 运行测试，预期 1.1、1.3、1.4 失败（因为代码尚未修复 `except Exception` 路径和 `close_all()` wrapper 状态同步）。

### Step 2 — Green: 最小代码修改

1. 修改 `session_manager.py`:
   - `except Exception` 中添加 `self._closed = True; await self.close()`
   - `SessionManager.__init__` 添加 `self._active_wrappers: dict[str, ClaudeSessionWrapper] = {}`
   - `create_session()` 中 `self._active_wrappers[session_id] = wrapper`
   - `resume_session()` 中 `self._active_wrappers[session_id] = wrapper`
   - `close_all()` 改为遍历 `_active_wrappers` 调用 `await wrapper.close()`，然后清空两个字典
2. 运行测试，预期全部通过。

### Step 3 — Refactor: 回归验证

1. 运行全部 docuswarm 测试：`pytest tests/docuswarm -v`
2. 运行全部项目测试（如果时间允许）。
3. 检查覆盖率变化。

### Step 4 — 文档归档

1. 更新本文档，标记各测试通过状态。
2. 记录发现的边界问题与修复决策。

---

## 5. 执行命令

```powershell
# 运行 transport hardening 专项测试
pytest -q tests\docuswarm\llm\test_transport_hardening_scheme_a.py

# 运行日志字段测试
pytest -q tests\docuswarm\utils\test_logging_fields.py

# 运行日志脱敏测试
pytest -q tests\docuswarm\utils\test_logging_redaction.py

# 运行全部 docuswarm 测试
pytest -q tests\docuswarm
```

---

## 6. 执行结果

### 6.1 测试统计

| 测试文件 | 测试数 | 结果 |
|---|---|---|
| `tests/docuswarm/llm/test_transport_hardening_scheme_a.py` | 24 | **24 passed** |
| `tests/docuswarm/utils/test_logging_fields.py` | 3 | **3 passed** |
| `tests/docuswarm/utils/test_logging_redaction.py` | 4 | **4 passed** |
| `tests/docuswarm (全部)` | 83 | **83 passed** |

### 6.2 代码修改摘要

**`autoBMAD/docuswarm/llm/session_manager.py`**:
1. `SessionManager.__init__`：新增 `self._active_wrappers: dict[str, ClaudeSessionWrapper] = {}`
2. `SessionManager.create_session()`：创建 wrapper 后同步注册到 `_active_wrappers`
3. `SessionManager.resume_session()`：恢复 wrapper 后同步注册到 `_active_wrappers`
4. `SessionManager.close_all()`：先关闭所有 tracked wrappers（同步 `_closed` 状态），再对仅存在于 `_active_clients` 的 client 执行 fallback 关闭，最后清空两个字典
5. `ClaudeSessionWrapper.prompt()`：`except Exception` 路径新增 `self._closed = True; await self.close()`，确保任何 `receive_messages` 异常后 transport 被清理

**`tests/docuswarm/llm/test_transport_hardening_scheme_a.py`**:
新增 6 个边界测试：
- `test_prompt_exception_should_close_session` — 验证异常路径关闭 session
- `test_prompt_normal_completion_should_not_close_session` — 验证正常路径不关闭 session
- `test_close_all_should_update_wrapper_closed_state` — 验证 `close_all()` 同步 wrapper 状态
- `test_context_manager_exit_should_close_wrappers` — 验证 `async with` 退出后 wrapper 被关闭
- `test_close_should_handle_disconnect_exception` — 验证 `disconnect()` 抛异常仍尝试 kill
- `test_close_should_handle_kill_wait_timeout` — 验证 `process.wait()` 超时不会导致崩溃

### 6.3 发现与修复的问题

| 问题 | 严重程度 | 状态 |
|---|---|---|
| `prompt()` 的 `except Exception` 路径未关闭 session，可能导致异常 transport 残留 | P0 | **已修复** |
| `SessionManager.close_all()` 不更新 wrapper `_closed` 状态，导致 wrapper 复用时行为不可预期 | P0 | **已修复** |
| `AsyncMock(side_effect=coroutine)` 在 `asyncio.wait_for` 取消时可能导致 Windows 事件循环关闭卡住 | 测试技术债 | **已规避**（改用纯 async function） |

---

## 7. 验收标准

- [x] P0: `disconnect()` 前 pre-capture process，超时后 force-kill fallback
- [x] P0: `close()` 与 `close_all()` 复用同一 helper
- [x] P0: idle/total timeout 后主动关闭 session，并标记 unusable
- [x] P0: 所有异常路径（包括 `receive_messages` 抛错）均关闭 session
- [x] P0: `SessionManager` 退出后，其创建的 wrapper 被标记为 closed
- [x] P1: 非 JSON 文件日志包含 `msg_type`、`message_index` 等额外字段
- [x] P1: JSON 文件日志包含额外字段
- [x] P1: 测试模拟真实 SDK `disconnect()` 后 `_transport=None`
- [x] P1: 测试模拟 `disconnect()` 阻塞/超时
- [x] P2: `line_preview` 内容级脱敏覆盖 `sk-...`、`Bearer ...`、`api_key=...`
