# DocuSwarm Session 执行失败解决方案报告

**基于分析报告**: `session-execution-failure-analysis.md`  
**方案日期**: 2026-04-05  
**覆盖文件**: `session_manager.py` / `independent.py`  
**优先级**: P0（阻断性，立即修复）

---

## 1. 方案概述

本报告基于 `session-execution-failure-analysis.md` 中确认的 3 个问题，提供完整的代码修复方案。核心目标：

1. **Fix-1**：修复 `ClaudeSessionWrapper.prompt()` 调用了不存在的 SDK 方法（BUG-1）
2. **Fix-2**：修复 `independent.py` 错误地对异步生成器使用 `await`（BUG-2）
3. **Fix-3**：移除 `session_manager.py` 中 `ANTHROPIC_MODEL_NAME` 环境变量及其 `model` 字段整体逻辑

修复后，第二次运行中所有节点的 `llm_call_error` → `independent_agent_failed` → `node_execution_failed` 失败链将被彻底消除。

---

## 2. Fix-1 — 重写 `ClaudeSessionWrapper.prompt()`

### 问题定位

**文件**: `autoBMAD/docuswarm/llm/session_manager.py`  
**类**: `ClaudeSessionWrapper`（第 642 行起）  
**方法**: `prompt()`（第 667–681 行）

`ClaudeSDKClient` 在 v0.1.68 中不存在 `send_message()` 和 `messages()` 方法，正确的 API 为 `query()` + `receive_messages()`。

### 修改前

```python
async def prompt(self, message: str) -> Any:
    """Send a prompt and get streaming responses."""
    await self._client.send_message(message)      # AttributeError: 方法不存在

    # Collect all messages until we get a result
    async for msg in self._client.messages():     # AttributeError: 方法不存在
        yield msg
```

### 修改后

```python
async def prompt(self, message: str) -> Any:
    """Send a prompt and yield streaming responses via SDK query API.

    Uses client.query() to send the message and client.receive_messages()
    to stream back all response messages.

    Args:
        message: The message string to send.

    Yields:
        Message objects from the SDK response stream.
    """
    await self._client.query(message)
    async for msg in self._client.receive_messages():
        yield msg
```

---

## 3. Fix-2 — 修正 `independent.py` 的 await 模式

### 问题定位

**文件**: `autoBMAD/docuswarm/agents/independent.py`  
**方法**: `_call_llm_with_prompts()`（第 277 行起）  
**问题行**: 第 325 行

`session.prompt()` 是 `async generator` 函数，调用后返回 `async_generator` 对象，不能用 `await` 修饰。

### 修改前

```python
# Note: session.prompt() returns an async iterator, use async for directly
async for msg in await session.prompt(user_prompt):    # TypeError: 对 async_generator 执行 await
    if isinstance(msg, dict):
        messages.append(msg)
    else:
        msg_dict = {
            "role": getattr(msg, "role", "unknown"),
            "content": getattr(msg, "content", []),
        }
        messages.append(msg_dict)
```

### 修改后

```python
# session.prompt() is an async generator, iterate directly without await
async for msg in session.prompt(user_prompt):
    if isinstance(msg, dict):
        messages.append(msg)
    else:
        msg_dict = {
            "role": getattr(msg, "role", "unknown"),
            "content": getattr(msg, "content", []),
        }
        messages.append(msg_dict)
```

---

## 4. Fix-3 — 移除 `ANTHROPIC_MODEL_NAME` 及 `model` 字段

### 背景说明

`ANTHROPIC_MODEL_NAME` 环境变量及 `model` 字段在本项目中**禁止使用**：

- `session_manager._create_options()` 中通过 `os.environ.get("ANTHROPIC_MODEL_NAME", "claude-3-opus-20240229")` 读取模型名，默认值 `claude-3-opus-20240229` 为过时标识符
- `Config` 类无 `model` 字段，`hasattr(self._config, "model")` 永远为 `False`，导致每次均落入 `os.environ.get` 分支
- 项目统一使用 Kimi Code API（`ANTHROPIC_BASE_URL` 已指向 Kimi 端点），模型选择由 API 网关侧管理，客户端无需也不应指定 model

### 4.1 修改 `session_manager._create_options()`

**文件**: `autoBMAD/docuswarm/llm/session_manager.py`

#### 修改前

```python
def _create_options(self, mode: str = "agent", yolo: bool = True) -> ClaudeAgentOptions:
    """Create ClaudeAgentOptions from configuration."""
    # Get model from config or environment, use default
    if self._config and hasattr(self._config, "model"):
        model = self._config.model
    else:
        model = os.environ.get("ANTHROPIC_MODEL_NAME", "claude-3-opus-20240229")

    # Determine permission mode based on yolo
    permission_mode = "bypassPermissions" if yolo else "default"

    options_dict: dict[str, Any] = {
        "cwd": self._work_dir,
        "model": model,
        "permission_mode": permission_mode,
    }
```

#### 修改后

```python
def _create_options(self, mode: str = "agent", yolo: bool = True) -> ClaudeAgentOptions:
    """Create ClaudeAgentOptions from configuration."""
    # Determine permission mode based on yolo
    permission_mode = "bypassPermissions" if yolo else "default"

    options_dict: dict[str, Any] = {
        "cwd": self._work_dir,
        "permission_mode": permission_mode,
    }
```

**变更说明**：
- 删除整个 model 读取逻辑（`if self._config and hasattr(...)` 分支及 `os.environ.get("ANTHROPIC_MODEL_NAME", ...)` 行）
- 从 `options_dict` 中移除 `"model": model` 键
- `ClaudeAgentOptions.model` 默认值为 `None`，SDK 会使用 API 网关的默认模型，无需客户端指定

### 4.2 移除 `os` 模块导入（如仅被 model 逻辑使用）

检查 `session_manager.py` 中 `os` 的其他使用场景：

```python
# 第 19 行
import os
```

`os` 模块在 `_create_options()` 中仅用于 `os.environ.get("ANTHROPIC_MODEL_NAME", ...)`，移除 model 逻辑后，需确认 `os` 是否还有其他引用。若无其他使用则一并移除该 import；若有其他引用（如路径操作等）则保留。

> **注意**：根据代码全文检查，`os` 在 `session_manager.py` 中**仅用于**第 146 行的 `os.environ.get`，Fix-3 实施后需同步移除 `import os`。

---

## 5. 完整代码变更清单

### 5.1 `autoBMAD/docuswarm/llm/session_manager.py`

| 行号 | 变更类型 | 说明 |
|------|----------|------|
| 19 | 删除 | `import os` — Fix-3 后不再使用 |
| 142–146 | 删除 | model 读取逻辑（`if self._config...` 块及 `os.environ.get` 行） |
| 153 | 删除 | `"model": model,` 键 |
| 667–681 | 修改 | `ClaudeSessionWrapper.prompt()` — 用 `query()` + `receive_messages()` 替换 `send_message()` + `messages()` |

### 5.2 `autoBMAD/docuswarm/agents/independent.py`

| 行号 | 变更类型 | 说明 |
|------|----------|------|
| 325 | 修改 | `async for msg in await session.prompt(...)` → `async for msg in session.prompt(...)` |

---

## 6. 应用修复的完整 diff

### `session_manager.py` — `_create_options()` 方法

```diff
-import os
 import asyncio
 import types
 from pathlib import Path

 ...

     def _create_options(self, mode: str = "agent", yolo: bool = True) -> ClaudeAgentOptions:
         """Create ClaudeAgentOptions from configuration."""
-        # Get model from config or environment, use default
-        if self._config and hasattr(self._config, "model"):
-            model = self._config.model
-        else:
-            model = os.environ.get("ANTHROPIC_MODEL_NAME", "claude-3-opus-20240229")
-
         # Determine permission mode based on yolo
         permission_mode = "bypassPermissions" if yolo else "default"

         options_dict: dict[str, Any] = {
             "cwd": self._work_dir,
-            "model": model,
             "permission_mode": permission_mode,
         }
```

### `session_manager.py` — `ClaudeSessionWrapper.prompt()` 方法

```diff
     async def prompt(self, message: str) -> Any:
-        """Send a prompt and get streaming responses."""
-        await self._client.send_message(message)
-
-        # Collect all messages until we get a result
-        async for msg in self._client.messages():
+        """Send a prompt and yield streaming responses via SDK query API.
+
+        Args:
+            message: The message string to send.
+
+        Yields:
+            Message objects from the SDK response stream.
+        """
+        await self._client.query(message)
+        async for msg in self._client.receive_messages():
             yield msg
```

### `independent.py` — `_call_llm_with_prompts()` 方法

```diff
-            # Note: session.prompt() returns an async iterator, use async for directly
-            async for msg in await session.prompt(user_prompt):
+            # session.prompt() is an async generator, iterate directly without await
+            async for msg in session.prompt(user_prompt):
                 if isinstance(msg, dict):
```

---

## 7. 验证方案

### 7.1 单元验证（无需 API 调用）

```python
import inspect
import asyncio
from pathlib import Path

async def verify_fixes():
    from autoBMAD.docuswarm.llm.session_manager import SessionManager

    # 验证 Fix-3：_create_options 不包含 model 字段
    sm = SessionManager(work_dir=Path('.'))
    opts = sm._create_options()
    assert opts.model is None, f"model should be None, got {opts.model}"
    print("✅ Fix-3: model 字段已移除，opts.model is None")

    # 验证 Fix-1：prompt() 是 async generator
    from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper
    from claude_agent_sdk import ClaudeSDKClient
    from claude_agent_sdk.types import ClaudeAgentOptions
    client = ClaudeSDKClient(options=ClaudeAgentOptions(cwd='.'))
    wrapper = ClaudeSessionWrapper(client=client, session_id='test', work_dir=Path('.'))
    gen = wrapper.prompt("test")
    assert inspect.isasyncgen(gen), "prompt() must be async generator"
    print("✅ Fix-1: prompt() 正确返回 async_generator")

asyncio.run(verify_fixes())
```

### 7.2 集成验证

```bash
# 启动一次 pipeline，确认日志中不再出现以下错误序列：
# llm_call_error -> independent_agent_failed -> node_execution_failed
python -m autoBMAD.docuswarm start --context docs/bubble-sort/bubble-sort-context.md
```

**预期日志变化**：

| 日志消息 | 修复前 | 修复后 |
|---------|--------|--------|
| `llm_call_error` | ✅ 出现（WARNING） | ❌ 不再出现 |
| `independent_agent_failed` | ✅ 出现（ERROR） | ❌ 不再出现 |
| `node_execution_failed` | ✅ 出现（ERROR） | ❌ 不再出现 |
| `session_created` | ✅ 出现 | ✅ 继续出现 |

---

## 8. 修复影响范围评估

| 组件 | 影响 | 说明 |
|------|------|------|
| `SessionManager._create_options()` | 直接修改 | 移除 model 逻辑，`ClaudeAgentOptions` 不再携带 model 字段 |
| `ClaudeSessionWrapper.prompt()` | 直接修改 | API 调用从 send_message/messages 改为 query/receive_messages |
| `IndependentAgent._call_llm_with_prompts()` | 直接修改 | 移除 `await` 前缀 |
| `Config` 类 | 无需修改 | 本无 model 字段 |
| `.env` / `docuswarm.yaml` | 无需修改 | 均未配置 `ANTHROPIC_MODEL_NAME` |
| 所有节点（analyst/pm/ux/architect/po） | 间接受益 | 通过 `IndependentAgent` 路径修复，所有节点统一生效 |
| 测试文件 | 需关注 | 若测试中有 mock `send_message`/`messages` 的用例需同步更新 |

---

## 9. 结论

三处修复相互独立，均为外科式精准修改，无架构风险：

- **Fix-1 + Fix-2** 消除了第二次运行中所有节点的 `llm_call_error` 失败链（确定性复现 Bug）
- **Fix-3** 移除了项目禁止使用的 `ANTHROPIC_MODEL_NAME` 环境变量读取及 `model` 字段，使 `ClaudeAgentOptions` 不再携带模型标识符，由 API 网关统一管理模型选择

建议按 Fix-3 → Fix-1 → Fix-2 的顺序提交，每步独立验证。
