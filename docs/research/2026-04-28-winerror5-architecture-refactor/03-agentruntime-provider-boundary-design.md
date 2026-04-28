# 研究报告 03：AgentRuntime / Provider 边界重构设计研究

**日期**: 2026-04-28  
**研究对象**: `autoBMAD/docuswarm/llm/session_manager.py`, 节点执行层  
**关联问题**: LLM transport 与业务主路径耦合过深（R1）  
**研究工具**: `tools/winerror5_architecture_research_tool.py --mode provider-coupling`

---

## 执行摘要

当前 `SessionManager` 同时承担 SDK options 构造、MCP server 创建、allowed_tools 生成、session 生命周期管理、transport 监控、异常映射等 **7+ 项职责**。这种耦合导致：

1. **WinError 5 直接穿透到每个业务节点**（analyst、pm 等五个节点逐一失败）。
2. **单元测试困难**：无法在不启动真实 SDK 的情况下测试节点执行逻辑。
3. **扩展成本高**：添加新 provider（如 OpenAI、本地模型）需要重写大量业务代码。

本报告提出 **AgentRuntime / LLMProvider 边界重构方案**，目标是将 DocuSwarm 业务节点与 Claude SDK transport 细节隔离，形成可测试、可替换、可诊断的 provider 层。

**核心原则**：
- 不承诺立即支持多模型。
- 首先隔离 blast radius，使 transport 问题不会污染业务图。

---

## 1. 当前耦合分析

### 1.1 SessionManager 职责清单

通过静态代码审计，`session_manager.py`（~1000 行）承担以下职责：

| 职责 | 代码位置 | 耦合度 |
|------|----------|--------|
| 构造 `ClaudeAgentOptions` | `_create_options()` | 🔴 深度耦合 SDK |
| 注入 Skills `setting_sources` | `_create_options()` ~line 328 | 🔴 深度耦合 SDK |
| 创建 MCP servers | `_create_options()` ~line 354 | 🔴 深度耦合 SDK + NodeToolFilter |
| 生成 `allowed_tools` | `_build_allowed_tools()` | 🟡 耦合业务逻辑 |
| 启动 `ClaudeSDKClient` | `create_session()` ~line 513 | 🔴 深度耦合 SDK |
| 管理 session wrapper | `_active_clients`, `_active_wrappers` | 🟡 生命周期管理 |
| prompt timeout / idle watchdog | （历史修复痕迹） | 🟡 transport 监控 |
| stderr callback | `_stderr_callback()` | 🟡 transport 监控 |
| process fallback (kill) | `_close_client_with_process_fallback()` | 🔴 深度耦合 SDK 内部结构 |
| SDK 异常 → `LLMError` 映射 | `create_session()`, `single_prompt()` | 🟡 异常转换 |

### 1.2 节点层对 SessionManager 的直接依赖

```text
autoBMAD/docuswarm/node_execution/executor.py
  → from autoBMAD.docuswarm.llm.session_manager import SessionManager
  → create_dual_agent_node(config, session_manager, node_id, ...)

autoBMAD/docuswarm/agents/independent.py
  → 通过 SessionManager 创建 session

autoBMAD/docuswarm/agents/summary.py
  → 通过 SessionManager 调用 single_prompt()
```

**问题**: 如果 `SessionManager` 因 `WinError 5` 无法创建 session，所有节点直接失败。没有中间层可以进行 fail-fast 或 fallback。

### 1.3 直接 SDK 引用扩散

除 `session_manager.py` 外，以下文件也直接引用 `claude_agent_sdk`：

- `autoBMAD/docuswarm/agents/independent.py`（通过 SessionManager 间接）
- `autoBMAD/docuswarm/agents/summary.py`（`query()` 直接调用）
- `autoBMAD/docuswarm/agents/evaluator.py`（可能通过独立 agent）

虽然没有在 `pipeline/graph.py` 或 `node_execution/executor.py` 中发现直接的 `claude_agent_sdk` import，但 `SessionManager` 作为参数传入，实际上形成了**隐式深度耦合**。

---

## 2. 目标架构：AgentRuntime / Provider 边界

### 2.1 建议目录结构

```text
autoBMAD/docuswarm/
  llm/
    __init__.py
    provider.py                 # Protocols: AgentRuntime, AgentSession
    runtime_preflight.py         # Windows/CLI/AnyIO/SDK capability checks
    claude_sdk_provider.py       # Claude Agent SDK implementation
    claude_options.py            # options/MCP/Skills construction
    transport_monitor.py         # timeout, stderr, process close fallback
    session_manager.py           # Compatibility facade (gradually thinned)
  pipeline/
    graph.py                     # Pure graph flow, no duplicated completion policy
    state.py                     # Deterministic state transitions
    status_projection.py         # checkpoint -> DB/CLI projection
    orchestrator.py              # Orchestration, not transport diagnosis owner
```

### 2.2 核心 Protocol

```python
# autoBMAD/docuswarm/llm/provider.py
from typing import Protocol, AsyncIterator, TypedDict, Any
from dataclasses import dataclass
from pathlib import Path

class RuntimePreflightResult(TypedDict):
    success: bool
    category: str
    error: str
    diagnostics: dict[str, Any]

class AgentSession(Protocol):
    """Per-session abstraction."""

    @property
    def session_id(self) -> str: ...

    async def prompt(self, message: str, timeout: int | None = None) -> AsyncIterator[Any]: ...
    async def close(self) -> None: ...

class AgentRuntime(Protocol):
    """Provider-level abstraction."""

    async def preflight(self) -> RuntimePreflightResult:
        """Runtime capability check before any node execution."""
        ...

    async def create_session(
        self,
        node_id: str,
        mode: str = "agent",
        system_prompt: str | None = None,
        output_format: dict[str, Any] | None = None,
    ) -> AgentSession:
        """Create a new session for a specific node."""
        ...

    async def close_all(self) -> None:
        """Close all active sessions."""
        ...

    def get_capabilities(self) -> dict[str, Any]:
        """Return provider capabilities (MCP, Skills, etc.)."""
        ...
```

### 2.3 Claude Agent SDK 实现

```python
# autoBMAD/docuswarm/llm/claude_sdk_provider.py
from autoBMAD.docuswarm.llm.provider import AgentRuntime, AgentSession, RuntimePreflightResult
from autoBMAD.docuswarm.llm.claude_options import ClaudeOptionsFactory
from autoBMAD.docuswarm.llm.transport_monitor import TransportMonitor

class ClaudeAgentSDKProvider:
    """Claude Agent SDK implementation of AgentRuntime."""

    def __init__(
        self,
        cwd: Path,
        output_dir: Path,
        config: Any | None = None,
    ) -> None:
        self._cwd = cwd
        self._output_dir = output_dir
        self._config = config
        self._options_factory = ClaudeOptionsFactory(cwd=cwd, output_dir=output_dir)
        self._monitor = TransportMonitor()
        self._active_sessions: dict[str, ClaudeSDKSession] = {}

    async def preflight(self) -> RuntimePreflightResult:
        from autoBMAD.docuswarm.llm.runtime_preflight import TransportPreflight
        return await TransportPreflight().check(cwd=self._cwd)

    async def create_session(
        self,
        node_id: str,
        mode: str = "agent",
        system_prompt: str | None = None,
        output_format: dict[str, Any] | None = None,
    ) -> AgentSession:
        # 1. Build options via factory
        options = self._options_factory.build(
            node_id=node_id,
            mode=mode,
            system_prompt=system_prompt,
            output_format=output_format,
        )

        # 2. Create SDK client
        from claude_agent_sdk import ClaudeSDKClient
        client = ClaudeSDKClient(options=options)

        # 3. Connect with monitor
        await self._monitor.connect(client)

        # 4. Wrap
        session = ClaudeSDKSession(
            client=client,
            session_id=f"session_{uuid.uuid4().hex[:12]}",
            monitor=self._monitor,
        )
        self._active_sessions[session.session_id] = session
        return session

    async def close_all(self) -> None:
        for session in list(self._active_sessions.values()):
            await session.close()
        self._active_sessions.clear()

    def get_capabilities(self) -> dict[str, Any]:
        return {
            "provider": "claude_agent_sdk",
            "supports_mcp": True,
            "supports_skills": True,
            "supports_structured_output": True,
        }


class ClaudeSDKSession:
    """SDK-specific session wrapper."""

    def __init__(self, client: Any, session_id: str, monitor: TransportMonitor) -> None:
        self._client = client
        self._session_id = session_id
        self._monitor = monitor

    @property
    def session_id(self) -> str:
        return self._session_id

    async def prompt(self, message: str, timeout: int | None = None) -> AsyncIterator[Any]:
        # Delegate to SDK with monitor wrapping
        async for msg in self._monitor.prompt(self._client, message, timeout):
            yield msg

    async def close(self) -> None:
        await self._monitor.disconnect(self._client)
```

### 2.4 职责拆分：从 SessionManager 到新模块

| 原 SessionManager 职责 | 新归属 | 说明 |
|------------------------|--------|------|
| `_create_options()` | `claude_options.ClaudeOptionsFactory` | 纯构造逻辑，无状态 |
| `_build_allowed_tools()` | `claude_options.ClaudeOptionsFactory` | 工具列表生成 |
| MCP server 创建 | `claude_options.ClaudeOptionsFactory` | 调用 `NodeToolFilter` |
| `create_session()` | `claude_sdk_provider.ClaudeAgentSDKProvider` | provider 实现 |
| `_close_client_with_process_fallback()` | `transport_monitor.TransportMonitor` | 关闭/兜底 |
| `_stderr_callback()` | `transport_monitor.TransportMonitor` | stderr 观察 |
| `single_prompt()` | `ClaudeSDKSession.prompt()` | session 方法 |
| `resume_session()` | `ClaudeSDKProvider` / `ClaudeSDKSession` | 恢复逻辑 |

---

## 3. 集成路径

### 3.1 Orchestrator 集成

```python
# orchestrator.py
class HybridOrchestrator:
    def __init__(
        self,
        db_path: str | None = None,
        runtime: AgentRuntime | None = None,  # 替代 session_manager
        ...
    ) -> None:
        self._runtime = runtime

    async def start_pipeline(self, subject_context, pipeline_id=None):
        # 1. Preflight
        if self._runtime:
            preflight = await self._runtime.preflight()
            if not preflight["success"]:
                raise OrchestratorError(f"Preflight failed: {preflight['error']}")

        # 2. Create graph (runtime is passed, not session_manager)
        graph = create_pipeline_graph(runtime=self._runtime)
        ...
```

### 3.2 Graph / Executor 集成

```python
# graph.py
def _create_integrated_node_executor(node_id: str, runtime: AgentRuntime):
    async def executor(state: dict[str, Any]) -> dict[str, Any]:
        # Create session via runtime abstraction
        session = await runtime.create_session(node_id=node_id, mode="agent")
        try:
            # Execute node with session
            ...
        finally:
            await session.close()
        ...
    return executor
```

### 3.3 向后兼容

`session_manager.py` 保留为 **compatibility facade**：

```python
class SessionManager:
    """Deprecated compatibility facade. Delegates to AgentRuntime."""

    def __init__(self, ...):
        self._provider = ClaudeAgentSDKProvider(...)

    async def create_session(self, ...):
        return await self._provider.create_session(...)

    async def single_prompt(self, ...):
        session = await self._provider.create_session(...)
        messages = []
        async for msg in session.prompt(prompt):
            messages.append(msg)
        await session.close()
        return messages
```

---

## 4. 收益分析

### 4.1 可测试性

| 场景 | 重构前 | 重构后 |
|------|--------|--------|
| 测试 graph 流程 | 必须 mock 整个 SessionManager | mock `AgentRuntime` protocol |
| 测试 preflight 失败 | 无法单独测试 | `MockRuntime(preflight_ok=False)` |
| 测试节点完成语义 | 需要真实 SDK | `MockSession` 返回固定结果 |

### 4.2 可诊断性

| 场景 | 重构前 | 重构后 |
|------|--------|--------|
| WinError 5 定位 | 5 个节点重复失败 | preflight 单点失败 |
| transport 问题排查 | 深入 SessionManager 内部 | 查看 `runtime_preflight` 诊断 |
| stderr 分析 | 分散在 SessionManager | 集中在 `TransportMonitor` |

### 4.3 可扩展性

虽然本重构**不承诺**立即支持多模型，但边界为未来替换 provider 打下基础：

```python
# 未来可能的 DiagnosticOnlyProvider
class DiagnosticOnlyProvider:
    """仅用于环境诊断，不用于生产交付物生成。"""
    async def preflight(self): ...
    async def create_session(self, ...):
        raise NotImplementedError("DiagnosticOnlyProvider does not support session creation")
```

---

## 5. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 重构引入新的 async 边界错误 | HIGH | 保持所有接口 async；增加 contract tests |
| SessionManager facade 与 provider 行为不一致 | MEDIUM | facade 直接委托，不重新实现逻辑 |
| MCP/Skills 配置在新 options factory 中出错 | HIGH | 快照测试：对比新旧 options 输出 |
| 性能退化（增加抽象层） | LOW | protocol 调用无运行时开销 |

---

## 6. 实施路线图

### P1-1: 新建 provider.py protocol（1 天）
- 定义 `AgentRuntime`, `AgentSession`, `RuntimePreflightResult`
- 无实现，仅接口

### P1-2: 拆分 ClaudeOptionsFactory（2 天）
- 从 `SessionManager._create_options()` 提取逻辑
- 保持行为一致，增加单元测试

### P1-3: 拆分 TransportMonitor（2 天）
- 从 `SessionManager` 提取 stderr、kill fallback、timeout 逻辑
- 保持行为一致

### P1-4: 实现 ClaudeAgentSDKProvider（2 天）
- 实现 `AgentRuntime` protocol
- 集成 `ClaudeOptionsFactory` + `TransportMonitor`

### P1-5: SessionManager facade（1 天）
- 使 `SessionManager` 委托给 `ClaudeAgentSDKProvider`
- 验证所有现有测试通过

### P1-6: Orchestrator / Graph 接入（2 天）
- `start_pipeline()` 调用 `runtime.preflight()`
- `create_pipeline_graph()` 接受 `runtime` 参数

---

## 7. 结论

`SessionManager` 的职责膨胀是 `WinError 5` 问题被放大的关键架构因素。通过引入 `AgentRuntime` / `LLMProvider` 边界，可以将 transport 问题关进可测、可诊断、可隔离的边界内，使业务节点不再直接承受 SDK transport 的启动失败。

这不是全量重写，而是**边界型重构**：保留 Claude SDK 投资，收紧耦合度。

---

## 参考资料

- `autoBMAD/docuswarm/llm/session_manager.py`
- `autoBMAD/docuswarm/node_execution/executor.py`
- `autoBMAD/docuswarm/pipeline/graph.py`
- `autoBMAD/docuswarm/pipeline/orchestrator.py`
- `tools/winerror5_architecture_research_tool.py`
