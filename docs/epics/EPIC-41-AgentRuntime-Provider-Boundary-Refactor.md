# EPIC-41: AgentRuntime / Provider 边界重构

**Epic ID**: EPIC-41  
**Epic 名称**: AgentRuntime / Provider 边界重构  
**优先级**: P1（HIGH）  
**状态**: ❌ READY FOR IMPLEMENTATION（未实现 / 0% complete as of 2026-04-28）  
**创建日期**: 2026-04-28  
**研究来源**: `docs/research/2026-04-28-winerror5-architecture-refactor/03-agentruntime-provider-boundary-design.md`  
**预估工作量**: ~5 days

---

## Epic 概述

当前 `SessionManager` 同时承担 SDK options 构造、MCP server 创建、allowed_tools 生成、session 生命周期管理、transport 监控、异常映射等 **7+ 项职责**。这种耦合导致 WinError 5 直接穿透到每个业务节点，单元测试困难，扩展成本高。

**核心问题**：
- `SessionManager` 职责膨胀，深度耦合 `claude_agent_sdk`
- 节点层直接依赖 `SessionManager`，没有中间层可以 fail-fast 或 fallback
- 无法在不启动真实 SDK 的情况下测试节点执行逻辑

**推荐方案**：引入 `AgentRuntime` / `LLMProvider` 边界，将 DocuSwarm 业务节点与 Claude SDK transport 细节隔离，形成可测试、可替换、可诊断的 provider 层。

**核心原则**：
- 不承诺立即支持多模型
- 首先隔离 blast radius，使 transport 问题不会污染业务图

---

## 背景与技术分析

### SessionManager 职责清单

| 职责 | 代码位置 | 耦合度 |
|------|----------|--------|
| 构造 `ClaudeAgentOptions` | `_create_options()` | 🔴 深度耦合 SDK |
| 注入 Skills `setting_sources` | `_create_options()` ~line 328 | 🔴 深度耦合 SDK |
| 创建 MCP servers | `_create_options()` ~line 354 | 🔴 深度耦合 SDK + NodeToolFilter |
| 生成 `allowed_tools` | `_build_allowed_tools()` | 🟡 耦合业务逻辑 |
| 启动 `ClaudeSDKClient` | `create_session()` ~line 513 | 🔴 深度耦合 SDK |
| 管理 session wrapper | `_active_clients`, `_active_wrappers` | 🟡 生命周期管理 |
| stderr callback | `_stderr_callback()` | 🟡 transport 监控 |
| process fallback (kill) | `_close_client_with_process_fallback()` | 🔴 深度耦合 SDK 内部结构 |
| SDK 异常 → `LLMError` 映射 | `create_session()`, `single_prompt()` | 🟡 异常转换 |

### 目标目录结构

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
```

---

## Stories

### Story 41.1: 定义 AgentRuntime / AgentSession Protocol

**目标**：新建 `provider.py`，定义 `AgentRuntime`、`AgentSession`、`RuntimePreflightResult` 核心协议。

**涉及文件**：1 个（新建 `autoBMAD/docuswarm/llm/provider.py`）

#### 验收标准

- [ ] 定义 `RuntimePreflightResult` TypedDict
- [ ] 定义 `AgentSession` Protocol，包含 `session_id` property、`prompt()`、`close()`
- [ ] 定义 `AgentRuntime` Protocol，包含 `preflight()`、`create_session()`、`close_all()`、`get_capabilities()`
- [ ] 所有接口使用 `async` 定义
- [ ] `create_session` 接受 `node_id`, `mode`, `system_prompt`, `output_format` 参数
- [ ] 协议定义不包含任何 SDK 特定类型

#### 技术规格

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
    @property
    def session_id(self) -> str: ...
    async def prompt(self, message: str, timeout: int | None = None) -> AsyncIterator[Any]: ...
    async def close(self) -> None: ...

class AgentRuntime(Protocol):
    async def preflight(self) -> RuntimePreflightResult: ...
    async def create_session(
        self, node_id: str, mode: str = "agent",
        system_prompt: str | None = None,
        output_format: dict[str, Any] | None = None,
    ) -> AgentSession: ...
    async def close_all(self) -> None: ...
    def get_capabilities(self) -> dict[str, Any]: ...
```

#### 测试要求

- 单元测试：`tests/test_llm/test_provider_protocol.py`
  - 测试 `ClaudeAgentSDKProvider` 满足 `AgentRuntime` protocol（使用 `typing.runtime_checkable`）
  - 测试 `ClaudeSDKSession` 满足 `AgentSession` protocol

---

### Story 41.2: 拆分 ClaudeOptionsFactory

**目标**：从 `SessionManager._create_options()` 提取逻辑到新建的 `claude_options.py`。

**涉及文件**：1 个（新建 `autoBMAD/docuswarm/llm/claude_options.py`）

#### 验收标准

- [ ] 新建 `ClaudeOptionsFactory` 类，包含 `build(node_id, mode, system_prompt, output_format)` 方法
- [ ]  factory 处理 `allowed_tools` 生成
- [ ] factory 处理 MCP server 创建（调用 `NodeToolFilter`）
- [ ] factory 处理 Skills `setting_sources` 注入
- [ ] factory 返回 `ClaudeAgentOptions` 实例（SDK 类型，但仅在 provider 层使用）
- [ ] 增加快照测试：对比新旧 options 输出，确保行为一致

#### 技术规格

```python
# autoBMAD/docuswarm/llm/claude_options.py
class ClaudeOptionsFactory:
    def __init__(self, cwd: Path, output_dir: Path, config: Any | None = None) -> None:
        self._cwd = cwd
        self._output_dir = output_dir
        self._config = config

    def build(
        self,
        node_id: str,
        mode: str = "agent",
        system_prompt: str | None = None,
        output_format: dict[str, Any] | None = None,
    ) -> ClaudeAgentOptions:
        # 1. Build allowed_tools
        # 2. Create MCP servers
        # 3. Inject setting_sources for skills
        # 4. Apply system_prompt and output_format
        ...
```

#### 测试要求

- 单元测试：`tests/test_llm/test_claude_options_factory.py`
  - 快照测试：对比 `ClaudeOptionsFactory.build()` 与旧 `SessionManager._create_options()` 输出
  - 测试 MCP server 注册的工具名与 `allowed_tools` 一致
  - 测试 Skills 启用时 `setting_sources` 和 `Skill` 工具同时存在

---

### Story 41.3: 拆分 TransportMonitor

**目标**：从 `SessionManager` 提取 stderr、kill fallback、timeout 逻辑到新建的 `transport_monitor.py`。

**涉及文件**：1 个（新建 `autoBMAD/docuswarm/llm/transport_monitor.py`）

#### 验收标准

- [ ] 新建 `TransportMonitor` 类
- [ ] 包含 `connect(client)` 方法：包装 SDK client connect，附加 stderr 观察
- [ ] 包含 `disconnect(client)` 方法：优雅关闭，带 process fallback kill
- [ ] 包含 `prompt(client, message, timeout)` 方法：包装 SDK prompt，带 timeout 监控
- [ ] 保留原有 stderr callback 行为
- [ ] 保留原有 process fallback (kill) 行为

#### 技术规格

```python
# autoBMAD/docuswarm/llm/transport_monitor.py
class TransportMonitor:
    async def connect(self, client: ClaudeSDKClient) -> None:
        """Connect with stderr observation."""
        ...

    async def disconnect(self, client: ClaudeSDKClient) -> None:
        """Graceful disconnect with process fallback."""
        ...

    async def prompt(
        self, client: ClaudeSDKClient, message: str, timeout: int | None = None
    ) -> AsyncIterator[Any]:
        """Prompt with timeout monitoring."""
        ...
```

#### 测试要求

- 单元测试：`tests/test_llm/test_transport_monitor.py`
  - 测试 connect/disconnect 生命周期
  - 测试 timeout 触发行为
  - 测试 process fallback kill 在 disconnect 失败时触发

---

### Story 41.4: 实现 ClaudeAgentSDKProvider

**目标**：实现 `AgentRuntime` protocol 的 Claude Agent SDK 具体实现。

**涉及文件**：1 个（新建 `autoBMAD/docuswarm/llm/claude_sdk_provider.py`）

#### 验收标准

- [ ] 新建 `ClaudeAgentSDKProvider` 类，实现 `AgentRuntime` protocol
- [ ] 集成 `ClaudeOptionsFactory` + `TransportMonitor`
- [ ] `create_session()` 返回 `ClaudeSDKSession` 实例
- [ ] `preflight()` 委托给 `TransportPreflight().check()`
- [ ] `close_all()` 关闭所有活跃 session
- [ ] `get_capabilities()` 返回 provider 能力（MCP, Skills, structured_output）
- [ ] 内部使用 `_active_sessions: dict[str, ClaudeSDKSession]` 管理生命周期

#### 技术规格

```python
# autoBMAD/docuswarm/llm/claude_sdk_provider.py
class ClaudeAgentSDKProvider:
    def __init__(self, cwd: Path, output_dir: Path, config: Any | None = None) -> None:
        self._cwd = cwd
        self._output_dir = output_dir
        self._config = config
        self._options_factory = ClaudeOptionsFactory(cwd=cwd, output_dir=output_dir)
        self._monitor = TransportMonitor()
        self._active_sessions: dict[str, ClaudeSDKSession] = {}

    async def preflight(self) -> RuntimePreflightResult:
        from autoBMAD.docuswarm.llm.runtime_preflight import TransportPreflight
        return await TransportPreflight().check(cwd=self._cwd)

    async def create_session(self, node_id: str, mode: str = "agent",
                             system_prompt: str | None = None,
                             output_format: dict[str, Any] | None = None) -> ClaudeSDKSession:
        options = self._options_factory.build(...)
        client = ClaudeSDKClient(options=options)
        await self._monitor.connect(client)
        session = ClaudeSDKSession(client=client, session_id=f"session_{uuid.uuid4().hex[:12]}", monitor=self._monitor)
        self._active_sessions[session.session_id] = session
        return session

class ClaudeSDKSession:
    def __init__(self, client: Any, session_id: str, monitor: TransportMonitor) -> None:
        self._client = client
        self._session_id = session_id
        self._monitor = monitor

    @property
    def session_id(self) -> str:
        return self._session_id

    async def prompt(self, message: str, timeout: int | None = None) -> AsyncIterator[Any]:
        async for msg in self._monitor.prompt(self._client, message, timeout):
            yield msg

    async def close(self) -> None:
        await self._monitor.disconnect(self._client)
```

#### 测试要求

- 单元测试：`tests/test_llm/test_claude_sdk_provider.py`
  - 测试 provider 实现 `AgentRuntime` protocol
  - 测试 session 实现 `AgentSession` protocol
  - 测试 `create_session` 生命周期（创建 → prompt → 关闭）
  - 测试 `close_all` 关闭所有活跃 session

---

### Story 41.5: SessionManager 兼容性 Facade

**目标**：使现有 `SessionManager` 委托给 `ClaudeAgentSDKProvider`，保持向后兼容。

**涉及文件**：1 个（`autoBMAD/docuswarm/llm/session_manager.py`）

#### 验收标准

- [ ] `SessionManager` 内部创建 `ClaudeAgentSDKProvider` 实例
- [ ] `SessionManager.create_session()` 委托给 `provider.create_session()`
- [ ] `SessionManager.single_prompt()` 委托给 provider（创建 session → prompt → 关闭）
- [ ] `SessionManager.resume_session()` 委托给 provider
- [ ] facade 不重新实现逻辑，直接委托
- [ ] 所有现有测试无需修改即可通过

#### 技术规格

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

#### 测试要求

- 回归测试：所有现有 `test_session_manager*.py` 测试无需修改即可通过
- 契约测试：`test_session_manager_facade_delegation.py` 验证 facade 正确委托

---

### Story 41.6: Orchestrator / Graph 接入 AgentRuntime

**目标**：`HybridOrchestrator` 和 `create_pipeline_graph()` 接受 `AgentRuntime` 参数替代 `SessionManager`。

**涉及文件**：2 个（`autoBMAD/docuswarm/pipeline/orchestrator.py` + `autoBMAD/docuswarm/pipeline/graph.py`）

#### 验收标准

- [ ] `HybridOrchestrator.__init__()` 接受 `runtime: AgentRuntime | None = None` 参数
- [ ] `start_pipeline()` 调用 `runtime.preflight()`（如果 runtime 存在）
- [ ] `create_pipeline_graph()` 接受 `runtime: AgentRuntime` 参数
- [ ] `_create_integrated_node_executor()` 使用 `runtime.create_session()` 创建 session
- [ ] 向后兼容：`runtime=None` 时使用现有 `SessionManager` 路径

#### 技术规格

```python
# orchestrator.py
class HybridOrchestrator:
    def __init__(self, ..., runtime: AgentRuntime | None = None):
        self._runtime = runtime

    async def start_pipeline(self, subject_context, pipeline_id=None):
        if self._runtime:
            preflight = await self._runtime.preflight()
            if not preflight["success"]:
                raise OrchestratorError(f"Preflight failed: {preflight['error']}")
        graph = create_pipeline_graph(runtime=self._runtime)
        ...

# graph.py
def _create_integrated_node_executor(node_id: str, runtime: AgentRuntime):
    async def executor(state: dict[str, Any]) -> dict[str, Any]:
        session = await runtime.create_session(node_id=node_id, mode="agent")
        try:
            ...
        finally:
            await session.close()
        ...
    return executor
```

#### 测试要求

- 单元测试：`tests/test_pipeline/test_runtime_integration.py`
  - 测试使用 `MockRuntime` 时 pipeline 可正常执行（脱离真实 SDK）
  - 测试 preflight 失败时 graph 不被调用

---

## 依赖关系

```
Story 41.1 → Story 41.4  (Protocol 先定义，再实现)
Story 41.2 → Story 41.4  (OptionsFactory 先拆分，再集成到 Provider)
Story 41.3 → Story 41.4  (TransportMonitor 先拆分，再集成到 Provider)
Story 41.4 → Story 41.5  (Provider 实现后，Facade 才能委托)
Story 41.4 → Story 41.6  (Provider 实现后，Orchestrator/Graph 才能接入)
Story 41.5 → Story 41.6  (Facade 稳定后，Orchestrator 才能安全切换)
```

**并行路径**：
- Story 41.1、41.2、41.3 可并行实施（三者相互独立）
- Story 41.5 和 41.6 可并行实施（两者都依赖 41.4，但相互独立）

---

## 实施阶段划分

### 阶段 1（协议与拆分）

- **Story 41.1**：定义 AgentRuntime / AgentSession Protocol
- **Story 41.2**：拆分 ClaudeOptionsFactory
- **Story 41.3**：拆分 TransportMonitor

### 阶段 2（实现与集成）

- **Story 41.4**：实现 ClaudeAgentSDKProvider
- **Story 41.5**：SessionManager 兼容性 Facade
- **Story 41.6**：Orchestrator / Graph 接入 AgentRuntime

---

## 收益分析

### 可测试性

| 场景 | 重构前 | 重构后 |
|------|--------|--------|
| 测试 graph 流程 | 必须 mock 整个 SessionManager | mock `AgentRuntime` protocol |
| 测试 preflight 失败 | 无法单独测试 | `MockRuntime(preflight_ok=False)` |
| 测试节点完成语义 | 需要真实 SDK | `MockSession` 返回固定结果 |

### 可诊断性

| 场景 | 重构前 | 重构后 |
|------|--------|--------|
| WinError 5 定位 | 5 个节点重复失败 | preflight 单点失败 |
| transport 问题排查 | 深入 SessionManager 内部 | 查看 `runtime_preflight` 诊断 |
| stderr 分析 | 分散在 SessionManager | 集中在 `TransportMonitor` |

---

## 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 重构引入新的 async 边界错误 | HIGH | 保持所有接口 async；增加 contract tests |
| SessionManager facade 与 provider 行为不一致 | MEDIUM | facade 直接委托，不重新实现逻辑 |
| MCP/Skills 配置在新 options factory 中出错 | HIGH | 快照测试：对比新旧 options 输出 |
| 性能退化（增加抽象层） | LOW | protocol 调用无运行时开销 |

---

## 相关文件

| 文件 | 角色 |
|------|------|
| `autoBMAD/docuswarm/llm/provider.py` | Story 41.1 新建（Protocol 定义） |
| `autoBMAD/docuswarm/llm/claude_options.py` | Story 41.2 新建（OptionsFactory） |
| `autoBMAD/docuswarm/llm/transport_monitor.py` | Story 41.3 新建（TransportMonitor） |
| `autoBMAD/docuswarm/llm/claude_sdk_provider.py` | Story 41.4 新建（Provider 实现） |
| `autoBMAD/docuswarm/llm/session_manager.py` | Story 41.5 改造（Facade） |
| `autoBMAD/docuswarm/pipeline/orchestrator.py` | Story 41.6 接入点 |
| `autoBMAD/docuswarm/pipeline/graph.py` | Story 41.6 接入点 |
