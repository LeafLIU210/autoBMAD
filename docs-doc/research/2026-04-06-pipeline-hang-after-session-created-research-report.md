# DocuSwarm Pipeline Hang After `session_created` 深度研究报告

**日期**: 2026-04-06  
**触发日志**: `logs/docuswarm-2026-04-06.log`  
**Pipeline ID**: `pipeline-1775436143731-75fea5a4`  
**研究范围**: `autoBMAD/docuswarm/` 全链路  

---

## 一、问题概述

本次 pipeline 在日志第 45 行 (`session_created`) 后**完全静默**，进程既未输出任何后续日志，也未记录任何错误。整个 `analyst` 节点未完成执行，pipeline 状态未知。

### 日志时间线（完整）

| 时间戳 (UTC) | 级别 | 消息 |
|---|---|---|
| 00:42:16.512 | info | `hybrid_orchestrator_initialized` |
| 00:42:16.512 | info | `starting_pipeline` |
| 00:42:16.512 | info | `single_prompt_start` ← **LLM 上下文验证开始** |
| 00:42:23.698 | info | `single_prompt_result` ← 耗时 7.2 秒 |
| 00:42:23.729 | info | `single_prompt_complete` |
| 00:42:23.729 | **debug** | `extract_text_debug` |
| 00:42:23.729 | **debug** | `no_text_extracted` ← **⚠ 关键警告** |
| 00:42:23.735 | info | `pipeline_work_dir_created` |
| 00:42:23.740 | info | `using_integrated_node_executor` |
| 00:42:23.766 | info | `analyst` - `node_execution_started` |
| 00:42:23.782 | debug | `execution_context_built` |
| 00:42:23.788 | info | `Loaded persona file` |
| 00:42:23.789 | debug | `Persona cached` |
| 00:42:23.795 | info | `starting_dual_agent_execution_with_context` |
| 00:42:23.795 | info | `iteration_start` (iteration=1) |
| 00:42:23.795 | debug | `context_build` |
| 00:42:23.797 | info | `executing_independent_agent_with_input` |
| 00:42:23.797 | debug | `Using cached persona` |
| 00:42:23.801 | info | `creating_session` |
| 00:42:23.801 | debug | `configuring_mcp_servers` |
| 00:42:23.802 | debug | `mcp_servers_created` |
| 00:42:23.802 | debug | `allowed_tools_configured` |
| 00:42:24.149 | info | `session_created` ← **最后一条日志** |
| **此后静默** | — | 进程无响应 |

---

## 二、发现的问题

### BUG-1（CRITICAL）：`ClaudeSessionWrapper.prompt()` 实现机制缺陷导致挂起

**文件**: [`session_manager.py` L659-L672](file:///d:/GITHUB/DocuSwarm/autoBMAD/docuswarm/llm/session_manager.py)

**问题代码**:
```python
async def prompt(self, message: str) -> AsyncIterator[Any]:
    await self._client.query(message)          # 行 668：发送消息

    # Stream messages using receive_messages API
    async for msg in self._client.receive_messages():  # 行 671：接收流
        yield msg
```

**根因分析**:

`ClaudeSDKClient` 的 `query()` 与 `receive_messages()` 是两个独立的异步操作。问题在于：

1. `await self._client.query(message)` — 发出请求后返回（可能只是"发送成功"，非完整响应）
2. `async for msg in self._client.receive_messages()` — 试图从消息流中读取

如果 `receive_messages()` 返回的是一个**无限等待的异步生成器**（例如等待 WebSocket 消息或 SSE 流），且 SDK 内部没有设置超时，则这里会**永远阻塞**。

日志中 `session_created` 之后立即调用 `session.prompt(user_prompt)` （在 `independent.py` L325），进入 `async for msg in session.prompt(user_prompt)` 循环后，由于 `receive_messages()` 永远不返回，导致进程挂起且**无任何错误日志**（异常从未被抛出）。

**证据**:
- `session_created` 日志存在（`create_session()` 已成功完成）
- 之后应该出现的 `llm_tool_call`、`session_creation_failed`、`llm_call_error` 等日志**全部缺失**
- 进程没有崩溃（否则会有 OS 级别信号），而是静默挂起

---

### BUG-2（CRITICAL）：`no_text_extracted` —— LLM 上下文验证阶段返回空响应

**文件**: [`response.py` L149-L263](file:///d:/GITHUB/DocuSwarm/autoBMAD/docuswarm/llm/response.py)，[`validator.py` L1244-L1248](file:///d:/GITHUB/DocuSwarm/autoBMAD/docuswarm/context/validator.py)

**触发路径**:
```
orchestrator.start_pipeline()
  → context_validator.validate_context_with_llm()
    → LLMContextValidationStrategy.validate()
      → session_manager.single_prompt()
        → extract_text_from_messages(messages)  ← 返回 ""
          → logger.debug("no_text_extracted")   ← 日志第13行
```

**问题分析**:

`extract_text_from_messages()` 在 `response.py` L262 记录 `no_text_extracted` 并返回空字符串，当且仅当**所有消息均不满足提取条件**时触发。

可能原因：
1. `single_prompt()` 通过 `async for msg in query(prompt=prompt, options=options)` 收集消息，但 `_message_to_dict()` 对 `ResultMessage` 返回 `None`（L529），过滤掉了它；
2. 其他消息可能 `role != "assistant"`（被 L190 跳过）；
3. SDK 返回的消息类型不包含 `text` 内容块（例如只有 `tool_use` 块无 `text`）。

**后果**:
- `_parse_validation_response()` 在 L1250 检测到空 content，抛出 `ValueError("Empty response from LLM")`；
- 但 `LLMContextValidationStrategy.validate()` 捕获此异常并**fail-open**（L1222-L1230），返回 `ValidationResult(valid=True)`；
- 因此 pipeline 继续执行，**不因此中止**。

这表明 BUG-2 是**已知的 fail-open 行为**，不是直接致命原因，但说明 LLM SDK 的消息格式在验证阶段已出现解析异常。

---

### BUG-3（HIGH）：`receive_messages()` 缺乏超时保护

**文件**: [`session_manager.py` L668-L672](file:///d:/GITHUB/DocuSwarm/autoBMAD/docuswarm/llm/session_manager.py)

`ClaudeSessionWrapper.prompt()` 调用 `receive_messages()` 时没有任何超时机制：

```python
async def prompt(self, message: str) -> AsyncIterator[Any]:
    await self._client.query(message)
    async for msg in self._client.receive_messages():  # ← 无 timeout
        yield msg
```

标准做法应当包裹 `asyncio.timeout()` 或 `asyncio.wait_for()`：
```python
async with asyncio.timeout(300):  # 5 分钟超时
    async for msg in self._client.receive_messages():
        yield msg
```

若 SDK 连接已建立但响应迟迟不来（网络抖动、API 限流、模型响应慢），整个调用栈会无限挂起，且不会写入任何日志。

---

### BUG-4（HIGH）：`create_session()` 与 `prompt()` 的语义二义性

**文件**: [`session_manager.py` L242-L336](file:///d:/GITHUB/DocuSwarm/autoBMAD/docuswarm/llm/session_manager.py)，[`independent.py` L316-L325](file:///d:/GITHUB/DocuSwarm/autoBMAD/docuswarm/agents/independent.py)

**调用链**:
```python
# independent.py L316-L325
session = await sm.create_session(
    mode="agent",
    yolo=True,
    agent_file=self._agent_file,
    system_prompt=system_prompt_append,
)

async for msg in session.prompt(user_prompt):   # ← 进入挂起
    ...
```

`create_session()` 在 L306 执行 `await client.connect()`，随后封装为 `ClaudeSessionWrapper`。`session_created` 日志证明 `connect()` 成功。

但 `ClaudeSessionWrapper.prompt()` 内的 `client.query()` + `client.receive_messages()` 是一个**有状态的流式 API**，其行为依赖 SDK 内部实现：

- 若 `query()` 只是发送请求但不等待响应，`receive_messages()` 才是真正阻塞点
- 若 `receive_messages()` 是"持续监听"模式而非"一次响应"模式，则永远不会 StopIteration

这种设计在 SDK 文档不完整时**极易产生死锁**。

---

### BUG-5（MEDIUM）：`single_prompt()` 与 `prompt()` 使用不同 API 路径，一致性存疑

**文件**: [`session_manager.py` L425-L509](file:///d:/GITHUB/DocuSwarm/autoBMAD/docuswarm/llm/session_manager.py)

`single_prompt()` 使用顶层 `query()` 函数：
```python
async for msg in query(prompt=prompt, options=options):   # SDK 顶层函数
    ...
```

`ClaudeSessionWrapper.prompt()` 使用客户端实例方法：
```python
await self._client.query(message)
async for msg in self._client.receive_messages():
```

这两条路径的行为和可靠性存在潜在差异：
- `single_prompt()` 已被验证能收到 `ResultMessage`（日志显示 `single_prompt_result` 存在）
- `ClaudeSessionWrapper.prompt()` 的路径从未有成功的日志输出，是**本次挂起的直接现场**

---

## 三、执行链路追踪图

```
CLI start
  │
  ▼
pipeline_service.py
  │  构建 subject_context
  ▼
HybridOrchestrator.start_pipeline()
  │
  ├─→ [验证] LLMContextValidationStrategy.validate()
  │     └─→ single_prompt()  ← 使用顶层 query()，成功但 no_text_extracted
  │         └─→ fail-open，继续执行
  │
  ├─→ StateManager.create_pipeline()  ← 写入 DB
  │
  ├─→ create_pipeline_graph()
  │
  └─→ graph.ainvoke(initial_state, config)
        │
        ▼
      NodeExecutor._execute_node(state, "analyst", ...)
        │
        ├─→ context_builder.build()
        ├─→ create_dual_agent_node()
        └─→ DualAgentNode.execute_with_context()
              │
              ├─→ ContextManager.build_independent_input()
              └─→ IndependentAgent.execute_with_input()
                    │
                    ├─→ SessionManager(...).create_session()  ← session_created 成功
                    └─→ session.prompt(user_prompt)
                          │
                          ├─→ client.query(message)
                          └─→ async for msg in client.receive_messages()
                                │
                                ▼
                              ⚠ 永久阻塞 ⚠  （最后日志位置）
```

---

## 四、现有调试工具评估

`tools/` 目录中已有以下相关工具：

| 工具文件 | 功能 | 本次适用性 |
|---|---|---|
| `docuswarm_debugger.py` | 离线诊断：DB 快照 + 日志分析 + 工具注册检查 | **部分适用**：缺少 async 挂起检测 |
| `p0_runtime_consumption_debugger.py` | 运行时 API 消耗分析 | 适用于 SDK API 调用分析 |
| `docuswarm_priority_issues_debugger.py` | 优先级问题专项调试 | 不直接适用 |
| `p0_async_sync_contract_analyzer.py` | 异步/同步边界分析 | **高度适用**：可分析 `prompt()` 边界 |

**现有工具的盲区**：
1. 无法检测"进程存活但无响应"的挂起场景
2. 缺少针对 `ClaudeSDKClient` API 调用序列的正确性验证
3. 无超时配置建议模块

---

## 五、根因汇总

| 编号 | 严重度 | 位置 | 根因 |
|---|---|---|---|
| BUG-1 | CRITICAL | `session_manager.py:668-672` | `ClaudeSessionWrapper.prompt()` 调用 `receive_messages()` 永久阻塞，无超时保护 |
| BUG-2 | MEDIUM | `response.py:262` / `validator.py:1222` | LLM 上下文验证阶段消息文本提取失败（no_text_extracted），fail-open 掩盖了早期 SDK 异常信号 |
| BUG-3 | HIGH | `session_manager.py:671` | `async for msg in receive_messages()` 缺乏 `asyncio.timeout()` 保护 |
| BUG-4 | HIGH | `session_manager.py:668` / `independent.py:325` | `query()` + `receive_messages()` 语义模型不明，与 `single_prompt()` 使用的顶层 `query()` 函数行为不一致 |
| BUG-5 | MEDIUM | `session_manager.py:458` vs `668` | 两条 LLM 调用路径（`single_prompt` vs `prompt`）使用不同 API，一致性未经验证 |

---

## 六、建议修复方向

### Fix-1：为 `ClaudeSessionWrapper.prompt()` 添加超时保护

```python
import asyncio

async def prompt(self, message: str) -> AsyncIterator[Any]:
    await self._client.query(message)
    try:
        async with asyncio.timeout(1200):  # 20 分钟超时
            async for msg in self._client.receive_messages():
                yield msg
    except TimeoutError:
        raise LLMError("Session prompt timed out after 1200 seconds")
```

### Fix-2：统一 LLM 调用路径

考虑将 `ClaudeSessionWrapper.prompt()` 改为使用顶层 `query()` 函数，与 `single_prompt()` 一致：

```python
from claude_agent_sdk import query

async def prompt(self, message: str) -> AsyncIterator[Any]:
    async for msg in query(prompt=message, options=self._options):
        yield msg
```

这需要在 `create_session()` 时保存 `options` 引用。

### Fix-3：增强日志覆盖

在 `_call_llm_with_prompts()` 的 `async for msg in session.prompt(user_prompt)` 前后各增加一条 info 日志，确保挂起位置可见：

```python
self.logger.info("llm_prompt_start", user_prompt_length=len(user_prompt))
async for msg in session.prompt(user_prompt):
    self.logger.debug("llm_message_received", msg_type=type(msg).__name__)
    ...
self.logger.info("llm_prompt_complete", message_count=len(messages))
```

### Fix-4：no_text_extracted 应升级为 warning 而非 debug

`response.py` L262 的 `no_text_extracted` 目前是 `debug` 级别，应改为 `warning`，并包含更多上下文（消息数量、消息角色列表），便于快速定位。

---

## 七、结论

本次 pipeline `pipeline-1775436143731-75fea5a4` 的中断是由 **`ClaudeSessionWrapper.prompt()` 中 `receive_messages()` 无限阻塞**导致的。

核心设计缺陷是：`single_prompt()` 与 `create_session()+prompt()` 使用了两套不同的 SDK API，前者经过验证可正常返回，后者从未有成功执行的证据，且在本次执行中进入了无返回状态。

`no_text_extracted` 是早期预警信号——表明 SDK 的消息格式在验证阶段已出现异常——但 fail-open 策略掩盖了此问题，让 pipeline 继续推进到更深的挂起点。

**最高优先级行动**：为 `ClaudeSessionWrapper.prompt()` 内的 `receive_messages()` 调用添加超时机制，并统一两条 LLM 调用路径的 SDK API 使用方式。
