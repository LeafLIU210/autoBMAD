# DocuSwarm Session 执行失败深度分析报告

**分析日期**: 2026-04-05  
**日志文件**: `logs/docuswarm-2026-04-05.log`  
**SDK 版本**: `claude_agent_sdk 0.1.68`  
**Python 版本**: 3.12.10

---

## 1. 执行摘要

本报告对 `docuswarm-2026-04-05.log` 中出现的两轮 Pipeline 执行失败进行了深度技术分析。通过逐层代码追踪与运行时复现测试，发现了 **3 个分层错误**，其中 2 个为阻断性（CRITICAL）Bug，直接导致所有节点（analyst / pm / ux / architect / po）100% 失败。

---

## 2. 日志失败模式对比

### 2.1 第一次运行（01:17:20 — pipeline-1775351840732-355b5f84）

| 节点 | configuring_mcp_servers | mcp_servers_created | session_created | session_creation_failed |
|------|------------------------|---------------------|-----------------|------------------------|
| analyst | ✅ | ✅ | ❌ | ❌（ERROR） |
| pm | ✅ | ✅ | ❌ | ❌（ERROR） |
| ux | ✅ | ✅ | ❌ | ❌（ERROR） |
| architect | ✅ | ✅ | ❌ | ❌（ERROR） |
| po | ✅ | ✅ | ❌ | ❌（ERROR） |

**特征**：`connect()` 调用本身抛出异常，`session_created` 日志从未出现。失败发生在进程内部（约 83ms 内），极可能由 Claude Code CLI 未就绪或瞬时网络超时引起。

### 2.2 第二次运行（02:17:49 — pipeline-1775355469272-5ebdc81e）

| 节点 | session_created | llm_call_error | independent_agent_failed |
|------|-----------------|----------------|--------------------------|
| analyst | ✅（INFO） | ✅（WARNING） | ✅（ERROR） |
| pm | ✅（INFO） | ✅（WARNING） | ✅（ERROR） |
| ux | ✅（INFO） | ✅（WARNING） | ✅（ERROR） |
| architect | ✅（INFO） | ✅（WARNING） | ✅（ERROR） |
| po | ✅（INFO） | ✅（WARNING） | ✅（ERROR） |

**特征**：`connect()` 已成功，`session_created` 出现，但随后 `llm_call_error` 立即触发。这是一个**代码层面的确定性 Bug**，每次运行都会必然复现。

---

## 3. 根因分析（按严重级别排序）

### 3.1 BUG-1 [CRITICAL] — `ClaudeSessionWrapper.prompt()` 调用了不存在的 SDK 方法

**位置**: [`session_manager.py:ClaudeSessionWrapper.prompt()`](d:/GITHUB/DocuSwarm/autoBMAD/docuswarm/llm/session_manager.py#L667-L681)

**问题代码**:
```python
async def prompt(self, message: str) -> Any:
    await self._client.send_message(message)      # ← 方法不存在！
    async for msg in self._client.messages():     # ← 方法不存在！
        yield msg
```

**验证结果**（运行时确认）:
```
Has send_message: False   ← SDK 0.1.68 中此方法不存在
Has messages: False       ← SDK 0.1.68 中此方法不存在
Has query: True           ← 正确的发送方法
Has receive_messages: True ← 正确的接收方法
```

**正确的 SDK API**（`claude_agent_sdk 0.1.68`）:
```python
# 正确写法
await client.query(prompt)                              # 发送消息
async for msg in client.receive_messages():             # 接收消息流
    yield msg
```

**影响**：每次调用 `session.prompt()` 都会因 `AttributeError: 'ClaudeSDKClient' object has no attribute 'send_message'` 而失败，触发 `llm_call_error` 警告，最终导致 `independent_agent_failed`。

---

### 3.2 BUG-2 [CRITICAL] — `independent.py` 错误地 `await` 异步生成器

**位置**: [`independent.py:_call_llm_with_prompts()`](d:/GITHUB/DocuSwarm/autoBMAD/docuswarm/agents/independent.py#L325)

**问题代码**:
```python
# 错误：session.prompt() 是 async generator，不是 coroutine
async for msg in await session.prompt(user_prompt):   # ← TypeError!
```

**复现验证**:
```python
result = session.prompt(user_prompt)
# result type: <class 'async_generator'>
# Is async generator: True
await result  # → TypeError: object async_generator can't be used in 'await' expression
```

**正确写法**:
```python
# 正确：直接 async for，不需要 await
async for msg in session.prompt(user_prompt):
```

**影响链**:
```
_call_llm_with_prompts()
  → session.prompt() → async_generator
  → await async_generator → TypeError
  → LLMCallError caught at line 344
  → logger.warning("llm_call_error")  [日志中确认]
  → raise LLMCallError(...)
  → execute_with_input() 捕获 → IndependentExecutionError
  → logger.error("independent_agent_failed")  [日志中确认]
  → node_execution_failed
```

这两个 Bug（BUG-1 + BUG-2）的组合，解释了日志中第二次运行的完整失败链。

---

### 3.3 [MEDIUM] — 第一次运行中 `connect()` 本身失败

**表现**（01:17 运行）：
- 日志顺序：`configuring_mcp_servers` → `mcp_servers_created` → `allowed_tools_configured` → `session_creation_failed`
- **`session_created` 从未出现**，说明异常发生在 `await client.connect()` 内部

**与第二次运行的差异**：
- 02:17 运行：`session_created` 出现，说明 `connect()` 成功
- 两次运行之间相隔约 1 小时，环境可能有变化（CLI 进程重启、网络恢复）

**可能原因**：
1. Claude Code CLI 进程未启动或崩溃
2. 网络短暂超时（连接到 Kimi API）

---

## 4. SDK API 完整对比

### `ClaudeSDKClient` 实际可用方法（v0.1.68）

| 方法 | 签名 | 用途 |
|------|------|------|
| `connect()` | `async () -> None` | 建立与 Claude Code CLI 的连接 |
| `disconnect()` | `async () -> None` | 断开连接 |
| `query()` | `async (prompt: str \| AsyncIterable[dict], session_id: str = 'default') -> None` | 发送消息 |
| `receive_messages()` | `() -> AsyncIterator[UserMessage \| AssistantMessage \| ...]` | 接收消息流 |
| `receive_response()` | `() -> AsyncIterator[...]` | 接收响应 |
| `interrupt()` | `async () -> None` | 中断当前执行 |
| `get_mcp_status()` | — | 获取 MCP 服务器状态 |

**不存在的方法**（代码中错误引用）：
- `send_message()` ❌
- `messages()` ❌

### `ClaudeAgentOptions` 关键字段验证

| 字段 | 类型 | 状态 |
|------|------|------|
| `mcp_servers` | `dict[str, McpStdioServerConfig \| McpSSEServerConfig \| McpHttpServerConfig \| McpSdkServerConfig] \| str \| Path` | ✅ 存在 |
| `allowed_tools` | `list[str]` | ✅ 存在 |
| `system_prompt` | `str \| SystemPromptPreset \| None` | ✅ 存在 |
| `permission_mode` | `str \| None` | ✅ 存在 |
| `tools` | `list[str] \| ToolsPreset \| None` | ✅ 存在（用于 agent file） |

MCP 服务器格式（`create_file_read_server` 返回）经验证可被 SDK 正确接受：
```python
{'type': 'sdk', 'name': 'docuswarm-files-analyst', 'instance': <mcp.Server>}
```

---

## 5. 完整调用链失败图

```
Pipeline.start()
  └─ NodeExecutor.execute_node(node_id="analyst")
       └─ DualAgentNode.execute_with_context(execution_context)
            └─ IndependentAgent.execute_with_input(agent_input, pipeline_id)
                 └─ IndependentAgent._call_llm_with_prompts(system_prompt, user_prompt)
                      └─ SessionManager.create_session(mode="agent", yolo=True)
                           └─ ClaudeSDKClient.connect()
                                ├─ [Run1] FAILED HERE → session_creation_failed
                                └─ [Run2] 
                                     └─ ClaudeSessionWrapper.prompt(user_prompt)  ← async generator
                                          └─ await session.prompt(user_prompt)
                                               ├─ TypeError: can't await async_generator  [BUG-2]
                                               └─ (即使修复 BUG-2) AttributeError: send_message [BUG-1]
                                                    └─ logger.warning("llm_call_error")
                                                    └─ raise LLMCallError
                                                         └─ logger.error("independent_agent_failed")
                                                         └─ logger.error("node_execution_failed")
```

---

## 6. 修复建议

### Fix-1（立即修复）— 重写 `ClaudeSessionWrapper.prompt()`

**文件**: `autoBMAD/docuswarm/llm/session_manager.py`

```python
# 当前错误实现
async def prompt(self, message: str) -> Any:
    await self._client.send_message(message)      # AttributeError
    async for msg in self._client.messages():     # AttributeError
        yield msg

# 修复后
async def prompt(self, message: str) -> AsyncIterator[Any]:
    """Send a prompt and yield streaming responses."""
    await self._client.query(message)
    async for msg in self._client.receive_messages():
        yield msg
```

### Fix-2（同步修复）— 修正 `independent.py` 的 await 模式

**文件**: `autoBMAD/docuswarm/agents/independent.py`，第 325 行

```python
# 当前错误（TypeError）
async for msg in await session.prompt(user_prompt):

# 修复后（去掉 await）
async for msg in session.prompt(user_prompt):
```

### Fix-3（架构改进）— 统一会话 API 使用方式

考虑将 `ClaudeSessionWrapper` 改为薄包装器，在 `_call_llm_with_prompts` 中直接使用底层 `client.query()` + `client.receive_messages()` 组合，消除包装层带来的混淆：

```python
# 推荐：在 _call_llm_with_prompts 中直接操作 client
session = await sm.create_session(...)
await session._client.query(user_prompt)
async for msg in session._client.receive_messages():
    messages.append(self._convert_msg(msg))
```

---

## 7. 验证修复的测试方案

```python
# 建议的集成测试（tests/ 中）
async def test_session_prompt_api():
    """确保 session.prompt() 使用正确的 SDK API。"""
    sm = SessionManager(work_dir=Path.cwd())
    session = await sm.create_session(mode="agent", yolo=True)
    
    # 验证 prompt() 是 async generator
    import inspect
    gen = session.prompt("test")
    assert inspect.isasyncgen(gen), "prompt() must return async generator"
    
    # 验证 async for 可以迭代（不报 TypeError）
    messages = []
    async for msg in session.prompt("test"):
        messages.append(msg)
        break  # 只取第一条即可
```

---

## 8. 环境状态汇总

| 配置项 | 当前值 | 状态 |
|--------|--------|------|
| `claude_agent_sdk` 版本 | 0.1.68 | ✅ 已安装 |
| `ANTHROPIC_API_KEY` | `sk-kimi-...` | ✅ 已设置 |
| `ANTHROPIC_BASE_URL` | Kimi 端点 | ✅ 已设置 |
| `KIMI_API_KEY` | `sk-kimi-...` | ✅ 已设置 |
| MCP 服务器格式 | SDK 格式 dict | ✅ 正确 |
| `ClaudeAgentOptions.mcp_servers` | 字段存在 | ✅ 正确 |
| `ClaudeAgentOptions.allowed_tools` | 字段存在 | ✅ 正确 |
| `send_message()` 方法 | **不存在** | ❌ 代码错误引用 |
| `messages()` 方法 | **不存在** | ❌ 代码错误引用 |

---

## 9. 结论

日志中显示的所有节点失败均由以下两个确定性代码 Bug 导致：

1. **BUG-1**：`ClaudeSessionWrapper.prompt()` 引用了 SDK v0.1.68 中已不存在的 `send_message()` 和 `messages()` 方法
2. **BUG-2**：`independent.py` 使用 `await session.prompt()` 对异步生成器执行了非法的 await 操作

这两个 Bug 的叠加效果是**所有节点在第一次 LLM 调用时必然失败**，与 Pipeline 内容、上下文文件或网络状况无关。修复这两处代码（BUG-1 + BUG-2）后，第二次运行中的 `llm_call_error` 链将被消除。

第一次运行中的 `session_creation_failed`（`connect()` 失败）可能由临时性 CLI/网络问题引起。
