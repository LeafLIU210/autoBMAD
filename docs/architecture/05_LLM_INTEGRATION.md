# DocuSwarm LLM Integration Architecture

**Version**: 5.1 (BMM NodeExecutor Refactor)  
**Date**: 2026-03-02  
**Status**: Completed  
**Author**: Solution Architect

> **Migration Plan**: [TDD-05: Claude SDK Wrapper](../solution/TDD-05-SDKWrapper-Refactor.md)  
> **TDD SDK Migration**: [TDD-SDK-Migration-2026-03-25](../solution/TDD-SDK-Migration-2026-03-25.md) - Test-driven migration addressing dependency drift  
> **Dependency Drift Research**: [Dependency Drift Report](../research/dependency-drift-2026-03-25/README.md)  
> **迁移研究报告**: [完全移除 kimi-agent-sdk](../research/migration/README.md)  
> **BMM Refactor**: [TDD-BMM-02: Persona & System Prompt](../solution/TDD-BMM-02-Persona-SystemPrompt-Refactor.md)  
> **P1-2 Config Semantics**: [P1-2 Test-Driven Plan](../solution/2026-04-03-p1-2-config-semantics-test-driven-plan.md) - 配置语义统一 (Kimi/Claude 命名债清理)  
> **Previous Version**: 4.0 (claude-agent-sdk migration) - see bottom of document for archived content  

---

## 1. Overview

This document describes the LLM integration architecture migration from **kimi-agent-sdk** to **claude-agent-sdk** via Kimi Code API OpenAI-compatible interface.

### 1.1 Architecture Evolution

| Version | SDK | API | Status |
|---------|-----|-----|--------|
| 2.1 | httpx / ChatOpenAI | Direct REST | Deprecated |
| 3.1 | kimi-agent-sdk | Wire Protocol | Deprecated |
| 4.0 | claude-agent-sdk | Kimi Code API | Deprecated |
| 5.0 | claude-agent-sdk (声明依赖) | Kimi Code API | Deprecated |
| 5.1 | claude-agent-sdk (TDD Migration) | Kimi Code API | **Current** |

### 1.1 Design Principles

| Principle | Description |
|-----------|-------------|
| **Single Provider** | Kimi K2.5 only for MVP simplicity |
| **SDK-Native** | 使用 claude-agent-sdk 的 query() API，而非直接 HTTP 调用 |
| **Mode Optimization** | Different modes for different agent types via SDK 参数映射 |
| **Stateless Query** | 无 Session 状态，每次调用独立 |
| **Native Tool System** | 标准 Tool Use Block + 纯函数工具替代 CallableTool2 |

### 1.2 Current Migration Status (v5.1)

> **重要提示**: 当前正在进行 [TDD SDK Migration](../solution/TDD-SDK-Migration-2026-03-25.md) 以修复依赖漂移问题。详见 [Dependency Drift Research](../research/dependency-drift-2026-03-25/README.md)。

**依赖漂移现状**:
| 指标 | 数值 | 严重程度 |
|------|------|----------|
| Drift Score | 85/100 | CRITICAL |
| kimi-agent-sdk 文件 | 7 | 必须修复 |
| kaos.path 文件 | 3 | 必须修复 |
| 迁移进度 | 0% | 刚开始 |

**迁移计划**:
1. **Phase 1**: 基础设施 (测试先行) - 使用 [TDD-SDK-Migration](../solution/TDD-SDK-Migration-2026-03-25.md)
2. **Phase 2**: 核心模块迁移 - SessionManager
3. **Phase 3**: 工具系统迁移
4. **Phase 4**: Agent 层迁移
5. **Phase 5**: 集成验证

### 1.3 Target Architecture (v5.1 - Post-Migration)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  DocuSwarm v4.0 LLM Architecture                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DocuSwarm                                                                  │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                         SessionManager                                │ │
│  │                    (Unified API - Compatibility Removed)              │ │
│  │  ┌───────────────────────────────────────────────────────────────┐   │ │
│  │  │  single_prompt() → ClaudeSDKWrapper.execute()                │   │ │
│  │  │  create_session() → Not needed (stateless query)             │   │ │
│  │  │  resume_session() → Not needed                               │   │ │
│  │  └───────────────────────────────────────────────────────────────┘   │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                        │
│                                    ▼                                        │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                      ClaudeSDKWrapper                                 │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │ │
│  │  │  Environment:                                                   │ │ │
│  │  │  • ANTHROPIC_BASE_URL=https://api.kimi.com/coding/             │ │ │
│  │  │  • ANTHROPIC_API_KEY=xxx                                       │ │ │
│  │  └─────────────────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │ │
│  │  │  query() → AsyncGenerator[Message]                              │ │ │
│  │  │  ResultMessage (terminal)                                       │ │ │
│  │  │  ToolUseBlock (tool calls)                                      │ │ │
│  │  └─────────────────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                        │
│                                    ▼                                        │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    claude-agent-sdk                                   │ │
│  │                    (via Kimi Code API)                                │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 LLM Usage Summary (v4.0)

| Agent Type | API | Timeout | Purpose |
|------------|-----|---------|---------|
| **Context Validator** | `single_prompt()` | 60s | Context validation, completeness check |
| **Independent** | `single_prompt()` | 1800s | Deliverable creation |
| **Evaluator** | `single_prompt()` | 600s | Document quality evaluation |
| **Summarizer** | `single_prompt(mode="instant")` | 120s | Document summary (TDD-04) |

### 1.4 Architecture Change Summary (v3.1 → v4.0)

| 维度 | v3.1 (Current) | v4.0 (Target) |
|------|----------------|---------------|
| **SDK** | kimi-agent-sdk | claude-agent-sdk |
| **API** | Kimi Wire Protocol | Kimi Code API (OpenAI-compatible) |
| **Environment** | `KIMI_API_KEY` | `ANTHROPIC_BASE_URL`, `ANTHROPIC_API_KEY` |
| **工具系统** | CallableTool2[P] (已移除) | 纯函数工具 + ToolRegistry |
| **消息格式** | WireMessage + MessageAggregator (已移除) | ResultMessage + ToolUseBlock |
| **会话管理** | Session.create() / resume() (已移除) | Stateless query() (per-call) |
| **取消机制** | session.cancel() | SafeAsyncGenerator wrapper |
| **SDK Wrapper** | None (direct SDK use) | ClaudeSDKWrapper (TDD-05) |

### 1.5 Environment Variables (v4.0)

```bash
# Required
ANTHROPIC_BASE_URL=https://api.kimi.com/coding/
ANTHROPIC_API_KEY=your-kimi-api-key

# Optional
SDK_TIMEOUT=1800                          # Default timeout in seconds
```

> **2026-04-05 Update**: `ANTHROPIC_MODEL_NAME` 已移除。模型选择由 API 网关统一管理，客户端不再指定。详见 [Session Execution Failure Solution](../research/session-execution-failure-solution.md)。

> **P1-2 Config Semantics Note**: 项目已完成配置命名统一（Phase 10）。**仅支持 `ANTHROPIC_*` 环境变量**。
> - `ANTHROPIC_API_KEY` 和 `ANTHROPIC_BASE_URL` 是唯一支持的配置
> - `KIMI_API_KEY`、`CLAUDE_API_KEY` 等旧命名已彻底移除，无兼容层
> 详见 [P1-2 Deep Research](../research/2026-04-03-p1-2-config-semantics-analysis-report.md)。

**Configuration Loading Priority**:
1. System environment variables (if set)
2. `.env` file (project root)
3. `.env` file (`autoBMAD/docuswarm/`)
4. Code defaults

**Environment Variable Mapping (P1-2 Final)**:

| 旧配置 (Removed) | 新配置 (Required) | 状态 |
|-----------------|-------------------|------|
| `KIMI_API_KEY` | `ANTHROPIC_API_KEY` | 已移除，无兼容 |
| `KIMI_BASE_URL` | `ANTHROPIC_BASE_URL` | 已移除，无兼容 |
| `CLAUDE_API_KEY` | `ANTHROPIC_API_KEY` | 已移除，无兼容 |
| `CLAUDE_BASE_URL` | `ANTHROPIC_BASE_URL` | 已移除，无兼容 |
| `CLAUDE_MODEL_NAME` | *(已移除)* | 模型由 API 网关统一管理 |

---

## 2. Claude SDK Wrapper Architecture (TDD-05)

### 2.1 Overview

The `ClaudeSDKWrapper` provides a unified interface for SDK calls, compatible with `epic_automation` patterns, working through Kimi Code API.

```python
# llm/claude_sdk_wrapper.py
class ClaudeSDKWrapper:
    """Claude SDK wrapper compatible with epic_automation patterns.
    
    Uses Kimi Code API through OpenAI-compatible interface.
    
    Example:
        >>> wrapper = ClaudeSDKWrapper()
        >>> result = await wrapper.execute(
        ...     prompt="Create a document",
        ...     agent_name="independent",
        ...     timeout=1800.0,
        ... )
        >>> if result.is_success():
        ...     print(result.content)
    """
    
    DEFAULT_BASE_URL = "https://api.kimi.com/coding/"
    DEFAULT_TIMEOUT = 1800.0
    
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        permission_mode: str = "bypassPermissions",
    ) -> None:
        self.base_url = base_url or os.getenv("ANTHROPIC_BASE_URL", self.DEFAULT_BASE_URL)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.permission_mode = permission_mode
    
    async def execute(
        self,
        prompt: str,
        agent_name: str = "docuswarm",
        timeout: float | None = None,
        cwd: str | Path | None = None,
    ) -> SDKResult:
        """Execute SDK query.
        
        Returns:
            SDKResult with success, content, error, duration, messages
        """
```

### 2.2 SessionManager Architecture

```python
# llm/session_manager.py
class SessionManager:
    """Session manager using Claude SDK via Kimi Code API.
    
    Unified interface for LLM session management.
    Internally uses ClaudeSDKWrapper.
    
    Ref: TDD-05 + P0 Runtime Consumption Fix (2026-04-03) + P1-2 Config Semantics (2026-04-03)
    
    Note: KimiSessionManager alias has been removed per P1-2 cleanup.
    """
    
    def __init__(
        self,
        work_dir: Path | None = None,
        config: Config | None = None,  # P1-2: Unified config source
        node_id: str | None = None,  # Added for MCP tool isolation
        file_dirs: list[str] | None = None,  # File permissions
        search_dirs: list[str] | None = None,  # Search permissions
        tool_permissions: Any | None = None,  # P0 Fix: Complete NodeToolPermissions
    ) -> None:
        self._work_dir = work_dir or Path.cwd()
        self._config = config  # P1-2: Config is the single source
        self._node_id = node_id
        self._file_dirs = file_dirs or []
        self._search_dirs = search_dirs or []
        self._tool_permissions = tool_permissions  # P0 Fix: Store complete permissions
        # P1-2: SDK wrapper gets credentials from Config, not direct env var access
        self._sdk = ClaudeSDKWrapper(
            base_url=config.base_url if config else None,
            api_key=config.api_key if config else None,
        )
    
    async def single_prompt(
        self,
        prompt: str,
        mode: str = "agent",
        yolo: bool = True,
        agent_name: str = "docuswarm",
        timeout: float | None = 1800.0,
    ) -> SDKResult:
        """Single prompt API."""
        return await self._sdk.execute(
            prompt=prompt,
            agent_name=agent_name,
            timeout=timeout,
            cwd=self._work_dir,
        )
    
    async def create_session(
        self,
        mode: str = "agent",
        yolo: bool = True,
        system_prompt: str | dict[str, Any] | None = None,  # Supports preset/append
    ) -> ClaudeSessionWrapper:
        """Create session with Four-Layer Architecture support.
        
        Args:
            system_prompt: String or dict with preset/append structure.
                          Dict format: {"type": "preset", "preset": "claude_code", "append": ...}
        """
        # Implementation handles both string and dict formats
        # String is auto-wrapped to preset/append structure
    
    def _create_options(self) -> ClaudeAgentOptions:
        """Create ClaudeAgentOptions with MCP servers and tool permissions.
        
        **SDK MCP Format**: Returns dict-compatible server config for JSON serialization.
        
        **Migration Note**: FastMCP format caused `TypeError: Object of type FastMCP is not JSON 
        serializable`. Migrated to SDK MCP format per [Test-Driven SDK MCP Migration](../solution/test-driven-sdk-mcp-migration-plan.md).
        
        P0 Fix: MCP server keys use consistent naming with NodeToolFilter
        to avoid conflicts between file and search servers.
        """
        from autoBMAD.docuswarm.llm.tool_filter import (
            FILE_SERVER_NAME_FORMAT,
            SEARCH_SERVER_NAME_FORMAT,
        )
        
        # Use complete tool_permissions
        if self._tool_permissions is not None:
            tool_permissions = self._tool_permissions
        else:
            # Build from file_dirs/search_dirs
            tool_permissions = NodeToolPermissions(
                file_permissions=NodeFilePermissions(allowed_read_dirs=self._file_dirs),
                search_permissions=NodeSearchPermissions(search_dirs=self._search_dirs),
            )
        
        # Create NodeToolFilter for allowed_tools generation
        node_filter = NodeToolFilter(
            node_id=self._node_id,
            tool_permissions=tool_permissions,
        )
        
        # SDK MCP Format: create_mcp_servers() returns dict[str, Any] (not list[FastMCP])
        # - File server: docuswarm-files-{node_id}
        # - Search server: docuswarm-search-{node_id}
        mcp_servers_dict = node_filter.create_mcp_servers()  # Returns {server_name: sdk_mcp_server}
        options_dict = {}
        options_dict["mcp_servers"] = mcp_servers_dict  # Direct assignment, no iteration needed
        
        # Get allowed_tools including builtin tools (Read, Glob) and MCP tools
        options_dict["allowed_tools"] = node_filter.get_allowed_tools()
        
        return ClaudeAgentOptions(**options_dict)
```

**P0 Fix: MCP Server Key Naming**:

| Server Type | Key Format | Example (analyst node) |
|-------------|------------|------------------------|
| File Server | `docuswarm-files-{node_id}` | `docuswarm-files-analyst` |
| Search Server | `docuswarm-search-{node_id}` | `docuswarm-search-analyst` |

**Tool Name Format in allowed_tools**:
- Builtin: `Read`, `Glob`
- MCP File: `mcp__docuswarm-files-{node_id}__read_document`
- MCP Search: `mcp__docuswarm-search-{node_id}__grep_search`

This ensures consistency between `SessionManager._create_options()` and `NodeToolFilter.get_allowed_tools()`.

**SDK MCP Migration (Phase 14)**:

| Aspect | FastMCP (Before) | SDK MCP (After) |
|--------|-----------------|-----------------|
| **Return Type** | `list[FastMCP]` | `dict[str, Any]` |
| **Serialization** | ❌ Not JSON serializable | ✅ JSON serializable |
| **Server Name** | `mcp__docuswarm-files-{node_id}` | `docuswarm-files-{node_id}` |
| **Tool Name** | `mcp__docuswarm-files-{node_id}__read_document` | `read_document` (SDK adds prefix) |
| **MCP Tool Full Name** | `mcp__mcp__...` (duplicated) | `mcp__docuswarm-files-{node_id}__read_document` |
| **Implementation** | `@server.tool()` | `@tool()` + `create_sdk_mcp_server()` |

**SDK MCP Server Structure**:
```python
{
    'type': 'sdk',
    'name': 'docuswarm-files-analyst',
    'instance': <Server object>
}
```

**References**:
- [FastMCP SDK Compatibility Issue](../research/fastmcp-sdk-compatibility-issue.md)
- [SDK MCP Migration Plan A](../research/sdk-mcp-migration-plan-a.md)
- [Test-Driven SDK MCP Migration](../solution/test-driven-sdk-mcp-migration-plan.md)

### 2.3 Four-Layer System Prompt Architecture

**Layer Structure**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Four-Layer System Prompt Architecture                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Layer 1: Preset (claude_code)                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  • SDK built-in tool definitions                                      │ │
│  │  • Safety instructions                                                │ │
│  │  • Code style guidelines                                              │ │
│  │  ~2000 tokens                                                         │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Layer 2: Persona (from persona.json)                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  • Role identity                                                      │ │
│  │  • Expertise areas                                                    │ │
│  │  • Communication style                                                │ │
│  │  ~500 tokens                                                          │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Layer 3: Task Context (from node.yaml)                                    │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  • Task name and description                                          │ │
│  │  • Deliverable requirements                                           │ │
│  │  • Required sections                                                  │ │
│  │  ~300 tokens                                                          │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Layer 4: Skills (from .claude/skills/)                                    │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  • BMAD command descriptions                                          │ │
│  │  • Node-specific skill injection                                      │ │
│  │  ~400 tokens                                                          │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Total: ~3200 tokens (1.25% of 256K context)                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**SDK Configuration**:
```python
# Four-Layer Architecture with preset/append
options = ClaudeAgentOptions(
    system_prompt={
        "type": "preset",
        "preset": "claude_code",  # Layer 1
        "append": layer_2_3_4_content  # Layers 2+3+4 combined
    },
    mcp_servers=mcp_servers,  # Node-specific file/search tools
    allowed_tools=allowed_tools,
)
```

**Reference**: [2026-03-28 Implementation Requirements](../research/refactor-2026-03-28-implementation-requirements.md#1-claude-agent-sdk-system_prompt-presetappend-高级结构)

## 3. Archived: v3.1 kimi-agent-sdk Architecture

> **Note**: The following sections describe the current (v3.1) architecture using kimi-agent-sdk.
> This will be replaced by v4.0 (claude-agent-sdk) per TDD-05.

### 3.1 Provider Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   Kimi K2.5 Integration (kimi-agent-sdk)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DocuSwarm                                                                  │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                                                                        │ │
│  │  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐              │ │
│  │  │  Context     │   │ Independent  │   │  Evaluator   │              │ │
│  │  │  Validator   │   │   Agent      │   │   Agent      │              │ │
│  │  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘              │ │
│  │         │                  │                   │                      │ │
│  │         ▼                  ▼                   ▼                      │ │
│  │  ┌───────────────────────────────────────────────────────────────┐   │ │
│  │  │              KimiSessionManager (SDK 适配层)                   │   │ │
│  │  │  ┌─────────────────────────────────────────────────────────┐  │   │ │
│  │  │  │  API Selection:                                         │  │   │ │
│  │  │  │  • Context Validator → prompt() (单次, instant)         │  │   │ │
│  │  │  │  • Independent → Session.prompt() (多轮, agent)         │  │   │ │
│  │  │  │  • Evaluator → prompt() (单次, thinking)                │  │   │ │
│  │  │  └─────────────────────────────────────────────────────────┘  │   │ │
│  │  │  ┌─────────────────────────────────────────────────────────┐  │   │ │
│  │  │  │  SDK Capabilities:                                      │  │   │ │
│  │  │  │  • Session 生命周期管理 (create/resume/close)            │  │   │ │
│  │  │  │  • CallableTool2 工具自动调度                            │  │   │ │
│  │  │  │  • ApprovalRequest 审批处理                              │  │   │ │
│  │  │  │  • Wire 流式消息 + MessageAggregator                    │  │   │ │
│  │  │  │  • session.cancel() 原生取消                             │  │   │ │
│  │  │  └─────────────────────────────────────────────────────────┘  │   │ │
│  │  └───────────────────────────────────────────────────────────────┘   │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                 │                                          │
│                                 ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                      kimi-agent-sdk                                    │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │ │
│  │  │  Session → KimiCLI (--wire mode) → Kimi K2.5 API              │ │ │
│  │  │                                                                  │ │ │
│  │  │  Features:                                                       │ │ │
│  │  │  • Wire 协议通信 (非 HTTP 直连)                                 │ │ │
│  │  │  • 256K Context Window                                          │ │ │
│  │  │  • Multiple Modes (Instant, Thinking, Agent)                   │ │ │
│  │  │  • Context Caching                                              │ │ │
│  │  │  • SDK 内置连接管理/重试/消息序列化                              │ │ │
│  │  └─────────────────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Mode Specifications (SDK 参数映射)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Kimi K2.5 Modes (SDK Mapping)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  INSTANT MODE (Context Validator)                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  SDK Params: model="kimi", thinking=False, max_steps_per_turn=5     │ │
│  │  API: prompt() (单次高级 API)                                        │ │
│  │  Use Cases: Intent classification, context validation               │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  THINKING MODE (Evaluator)                                                  │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  SDK Params: model="kimi", thinking=True, max_steps_per_turn=10     │ │
│  │  API: prompt() (单次高级 API)                                        │ │
│  │  Use Cases: Document quality evaluation, criterion scoring          │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  AGENT MODE (Independent Agent)                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  SDK Params: model="kimi", thinking=False, max_steps_per_turn=50    │ │
│  │  API: Session.create() + Session.prompt() (多轮持久会话)             │ │
│  │  Tools: CallableTool2 via agent_file.yaml                           │ │
│  │  Use Cases: Deliverable creation, question generation               │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. KimiSessionManager Implementation

### 3.1 Session Manager Architecture

```python
from kimi_agent_sdk import Session, prompt, Config, MessageAggregator, Message
from kimi_agent_sdk.types import ApprovalRequest, WireMessage
from kimi_agent_sdk.exceptions import RunCancelled, MaxStepsReached, ChatProviderError
from pathlib import Path
from typing import Any

class KimiSessionManager:
    """
    基于 kimi-agent-sdk 的会话管理器。
    替代原有的 KimiClient，提供 Session 生命周期管理。
    """

    def __init__(
        self,
        work_dir: Path | None = None,
        agent_file: Path | None = None,
        config: Config | Path | None = None,
    ) -> None:
        self._work_dir = work_dir or Path.cwd()
        self._agent_file = agent_file
        self._config = config
        self._active_sessions: dict[str, Session] = {}

    async def create_session(
        self,
        session_id: str | None = None,
        mode: str = "agent",
        yolo: bool = False,
        max_steps: int | None = None,
    ) -> Session:
        """创建新 Session（对应原 KimiClient.chat 的初始化）"""
        mode_params = MODE_MAP[mode]
        session = await Session.create(
            work_dir=self._work_dir,
            session_id=session_id,
            config=self._config,
            model=mode_params.model,
            thinking=mode_params.thinking,
            yolo=yolo,
            agent_file=self._agent_file,
            max_steps_per_turn=max_steps or mode_params.max_steps_per_turn,
        )
        if session_id:
            self._active_sessions[session_id] = session
        return session

    async def resume_session(self, session_id: str) -> Session | None:
        """恢复已有 Session"""
        return await Session.resume(
            work_dir=self._work_dir,
            session_id=session_id,
            config=self._config,
            agent_file=self._agent_file,
        )

    async def single_prompt(
        self,
        user_input: str,
        mode: str = "instant",
        yolo: bool = True,
        approval_handler=None,
    ) -> list[Message]:
        """单次调用（对应原 KimiClient.chat）"""
        mode_params = MODE_MAP[mode]
        messages = []
        async for msg in prompt(
            user_input,
            work_dir=self._work_dir,
            config=self._config,
            model=mode_params.model,
            thinking=mode_params.thinking,
            yolo=yolo,
            approval_handler_fn=approval_handler,
            agent_file=self._agent_file,
        ):
            messages.append(msg)
        return messages

    def get_active(self, session_id: str) -> Session | None:
        return self._active_sessions.get(session_id)

    async def close_all(self) -> None:
        """关闭所有活跃 Session"""
        for session in self._active_sessions.values():
            await session.close()
        self._active_sessions.clear()
```

### 3.2 Mode Mapper

```python
from dataclasses import dataclass

@dataclass
class SDKModeParams:
    """SDK 模式参数"""
    model: str
    thinking: bool
    max_steps_per_turn: int | None

MODE_MAP = {
    "instant": SDKModeParams(model="kimi", thinking=False, max_steps_per_turn=5),
    "thinking": SDKModeParams(model="kimi", thinking=True, max_steps_per_turn=10),
    "agent": SDKModeParams(model="kimi", thinking=False, max_steps_per_turn=50),
}
```

### 3.3 Wire Message Processing

```python
async def process_wire_stream(
    session: Session,
    user_input: str,
    on_message=None,
) -> list[Message]:
    """处理 Wire 流式消息，转换为高级 Message 对象"""
    aggregator = MessageAggregator()
    messages: list[Message] = []

    async for wire_msg in session.prompt(user_input):
        if isinstance(wire_msg, ApprovalRequest):
            wire_msg.resolve("approve")
            continue

        for message in aggregator.feed(wire_msg):
            messages.append(message)
            if on_message:
                on_message(message)

    # flush 最终消息
    for message in aggregator.flush():
        messages.append(message)
        if on_message:
            on_message(message)

    return messages
```

---

## 4. Tool System (v4.0)

### 4.1 Tool Result Extractor (TDD-03)

As part of the pure tool output mode (12-Factor Factor 4), the `ToolResultExtractor` provides deterministic metadata extraction from tool calls.

```python
# tools/tool_result_extractor.py
@dataclass(frozen=True)
class DeliverableMetadata:
    """Standardized deliverable metadata."""
    title: str
    content: str
    content_summary: str  # Truncated for state storage
    file_path: str
    metadata: dict[str, Any]
    tool_name: str  # "create_deliverable" | "create_document_set"

class ToolResultExtractor:
    """Extract deliverable metadata from SDK tool call records.
    
    Implements 12-Factor Agents Factor 4: Tools Are Just Structured Outputs.
    Supports both kimi-agent-sdk and claude-agent-sdk message formats.
    
    Ref: TDD-03
    """
    
    SUPPORTED_TOOLS = {"create_deliverable", "create_document_set"}
    
    def extract_from_messages(self, messages: list[Any]) -> list[DeliverableMetadata]:
        """Extract all deliverable metadata from message list."""
        
    def extract_single_deliverable(self, messages: list[Any]) -> DeliverableMetadata | None:
        """Extract first deliverable (convenience method)."""
```

### 4.2 Tool System Changes (v3.1 → v4.0)

| Aspect | v3.1 (kimi-agent-sdk) | v4.0 (claude-agent-sdk) |
|--------|----------------------|------------------------|
| Tool Definition | `CallableTool2[Pydantic]` | Standard async functions |
| Registration | `agent_file.yaml` | Agent configuration file |
| Dispatch | SDK automatic | SDK automatic |
| Result Extraction | JSON parsing from LLM text | `ToolResultExtractor` from tool calls |

### 4.3 Archived: v3.1 Tool Calling (CallableTool2 + Pydantic)

> **Note**: The following describes the current v3.1 tool system. See TDD-03 for migration plan.

#### 4.3.1 Tool Definitions

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Tool Definitions (kimi-agent-sdk)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  TOOL 1: CreateDeliverableTool(CallableTool2)                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Purpose: Create node deliverable document                            │ │
│  │  Params: Pydantic BaseModel (CreateDeliverableParams)                │ │
│  │  ├── title (str, required)                                           │ │
│  │  ├── content (str, required) - Markdown content                      │ │
│  │  └── metadata (dict, optional) - Version, status                     │ │
│  │  Returns: ToolOk / ToolError                                         │ │
│  │  Dispatch: SDK 自动调度，无需手动解析 tool_calls                       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  TOOL 2: UpdateContextTool(CallableTool2)                                  │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  Purpose: Update shared subject context                               │ │
│  │  Params: Pydantic BaseModel (UpdateContextParams)                    │ │
│  │  ├── key (str, required) - Context key                               │ │
│  │  ├── value (dict, required) - Value to store                         │ │
│  │  └── operation (Literal["set","append","remove"], optional)          │ │
│  │  Returns: ToolOk / ToolError                                         │ │
│  │  Dispatch: SDK 自动调度，无需手动解析 tool_calls                       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Tool Registration: agent_file.yaml (非代码内嵌)                            │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  version: 1                                                           │ │
│  │  agent:                                                               │ │
│  │    extend: default                                                    │ │
│  │    tools:                                                             │ │
│  │      - "docuswarm.tools.create_deliverable:CreateDeliverableTool"   │ │
│  │      - "docuswarm.tools.update_context:UpdateContextTool"           │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Tool Implementation (CallableTool2)

```python
from pydantic import BaseModel, Field
from kimi_agent_sdk import CallableTool2, ToolOk, ToolError, ToolReturnValue
from typing import Literal


class CreateDeliverableParams(BaseModel):
    """可交付物创建参数"""
    title: str = Field(description="Document title")
    content: str = Field(description="Document content in Markdown format")
    metadata: dict = Field(default_factory=dict, description="Optional metadata")


class CreateDeliverableTool(CallableTool2):
    """创建节点可交付物文档"""
    name: str = "create_deliverable"
    description: str = "Create the node's deliverable document"
    params: type[CreateDeliverableParams] = CreateDeliverableParams

    def __init__(self, output_handler):
        super().__init__()
        self._output_handler = output_handler

    async def __call__(self, params: CreateDeliverableParams) -> ToolReturnValue:
        try:
            self._output_handler.save_deliverable(
                title=params.title,
                content=params.content,
                metadata=params.metadata,
            )
            return ToolOk(output=f"Deliverable '{params.title}' created successfully")
        except Exception as exc:
            return ToolError(output="", message=str(exc), brief="Failed to create deliverable")


class UpdateContextParams(BaseModel):
    """上下文更新参数"""
    key: str = Field(description="Context key to update")
    value: dict = Field(description="Value to store")
    operation: Literal["set", "append", "remove"] = Field(
        default="set", description="Update operation"
    )


class UpdateContextTool(CallableTool2):
    """更新共享 subject_context"""
    name: str = "update_context"
    description: str = "Update the shared subject context"
    params: type[UpdateContextParams] = UpdateContextParams

    def __init__(self, context_store):
        super().__init__()
        self._context_store = context_store

    async def __call__(self, params: UpdateContextParams) -> ToolReturnValue:
        try:
            self._context_store.update(
                key=params.key, value=params.value, operation=params.operation
            )
            return ToolOk(output=f"Context '{params.key}' updated ({params.operation})")
        except Exception as exc:
            return ToolError(output="", message=str(exc), brief="Context update failed")
```

### 4.3 Tool Registration Flow

```
改造前 (v2.1):
  Agent 手动定义 JSON Schema → 传入 KimiClient.chat(tools=[...])
  Agent 手动解析 tool_calls → 手动执行工具 → 手动构造返回消息

改造后 (v3.0):
  CallableTool2 定义 → agent_file.yaml 注册 → SDK 自动调度
  SDK 接收 ToolCall → 自动反序列化参数（Pydantic） → 调用 __call__ → 自动返回 ToolResult
```

### 4.4 Tool Integration Status and Required Fix

> **Reference**: `docs/research/DocuSwarm架构缺失与节点执行器集成问题深度研究报告.md`

**Current Status**: The tool definitions (Section 4.2) and registration configuration (Section 4.1) are correctly implemented but **never activated at runtime**:

| Component | Implementation | Runtime Status |
|-----------|---------------|----------------|
| `CreateDeliverableTool` class | Complete | Never instantiated |
| `UpdateContextTool` class | Complete | Never instantiated |
| `independent_agent.yaml` | Complete | Never loaded by Session |
| `KimiSessionManager.create_session()` | `agent_file` param supported | Never passed `agent_file` for Independent Agent |

**Root Cause**: When `IndependentAgent` creates a Session, it does not pass `agent_file` or `work_dir` parameters. Without `agent_file`, the SDK does not register any tools, so the LLM has no tools available to call.

**Fix (方案C)**: When creating the Independent Agent Session:
1. Pass `agent_file=Path("agents/configs/independent_agent.yaml")`
2. Pass `work_dir=Path(f"output/{pipeline_id}/")`
3. Set `yolo=True` to auto-approve file operations
4. Modify the prompt to instruct the LLM to use `create_deliverable` tool (remove JSON-only output requirement)

---

## 5. Rate Limiting and Retry

### 5.1 SDK Internal Handling

kimi-agent-sdk 通过 kimi-cli 子进程管理底层通信，SDK 内部已处理：
- 连接管理
- 消息序列化/反序列化
- 基础重试逻辑

### 5.2 外层防护（保留评估）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Rate Limiting Strategy (v3.0)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Kimi K2.5 Tier 3 Limits:                                                   │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  • Concurrent Requests: 20                                            │ │
│  │  • Requests per Minute (RPM): 200                                     │ │
│  │  • Tokens per Minute (TPM): 5,000,000                                 │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Strategy:                                                                  │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  • SDK 内部: 连接管理、消息序列化、基础重试                            │ │
│  │  • 外层可选: TokenBucketRateLimiter 作为并发防护                       │ │
│  │    - 如 SDK 自身限流足够 → Phase 4 移除外层                           │ │
│  │    - 如 SDK 无并发控制 → 保留外层信号量                                │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.3 SDK 异常体系 (替代手动 HTTP 错误处理)

```python
from kimi_agent_sdk.exceptions import (
    ChatProviderError,     # API 错误 (429/5xx)
    APITimeoutError,       # 超时
    APIConnectionError,    # 连接错误
    APIEmptyResponseError, # 空响应
    RunCancelled,          # 取消
    MaxStepsReached,       # 步骤上限
    ConfigError,           # 配置错误
    InvalidToolError,      # 工具错误
    SessionStateError,     # 会话状态错误
    PromptValidationError, # 提示验证错误
)

# 异常映射 (旧 → 新)
# HTTP 429        → ChatProviderError (APIStatusError)
# HTTP timeout    → APITimeoutError
# HTTP 5xx        → ChatProviderError (APIStatusError)
# 连接错误        → APIConnectionError
# 空响应          → APIEmptyResponseError
# 取消（新增）    → RunCancelled
# 步骤超限（新增）→ MaxStepsReached
```

---

## 6. Cost Optimization

### 6.1 Context Caching

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Context Caching Strategy                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Kimi K2.5 Context Caching Pricing:                                         │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  • Cache Miss: $0.60 / 1M tokens                                      │ │
│  │  • Cache Hit: $0.10 / 1M tokens                                       │ │
│  │  • Savings: 83% on cached content                                    │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  SDK Session 优势:                                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  • Session.create() 保持对话上下文 → 自动利用 context caching         │ │
│  │  • 多轮对话中 system prompt 和历史消息自动缓存                         │ │
│  │  • 比旧架构每次独立 HTTP 请求更高效                                    │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Session Management

### 7.1 Session Persistence Strategy

```
Session ID 命名规范:

Pipeline 级别:
  pipeline_session_id = f"docuswarm-{pipeline_id}"

节点级别:
  node_session_id = f"docuswarm-{pipeline_id}-{node_id}"

迭代级别（Independent Agent 多轮）:
  iteration_session_id = f"docuswarm-{pipeline_id}-{node_id}-iter{n}"
```

### 7.2 Session 与 LangGraph Checkpoint 关系

```
LangGraph Checkpoint (SQLite):
  ├── 管理 Pipeline 全局状态 (PipelineState)
  ├── 管理节点间数据传递 (deliverables, questions, evaluations)
  └── 管理 DAG 执行进度

kimi-agent-sdk Session:
  ├── 管理 Agent 与 LLM 的对话历史
  ├── 管理工具调用上下文
  └── 管理迭代反馈状态

两者互补，不冲突:
  LangGraph → 宏观编排状态
  SDK Session → 微观对话状态
```

---

## 8. Cancellation and Approval

### 8.1 Cancellation Mechanism

```python
# Session 级别取消
session = await Session.create(...)

# 在另一个协程中取消
session.cancel()  # 设置内部 asyncio.Event

# prompt() 协程收到取消信号后抛出 RunCancelled
try:
    async for wire_msg in session.prompt(user_input):
        ...
except RunCancelled:
    logger.info("Agent execution cancelled")
```

### 8.2 Approval Handler

```python
from kimi_agent_sdk import ApprovalRequest

class DocuSwarmApprovalHandler:
    """DocuSwarm 审批策略"""

    AUTO_APPROVE_ACTIONS = {"create_deliverable", "update_context", "read_file"}
    REJECT_ACTIONS = {"write_file", "execute_command", "delete_file"}

    def __init__(self, auto_approve_all: bool = False):
        self._auto_approve_all = auto_approve_all

    def handle(self, request: ApprovalRequest) -> None:
        if self._auto_approve_all:
            request.resolve("approve")
            return

        action = request.action
        if action in self.AUTO_APPROVE_ACTIONS:
            request.resolve("approve")
        elif action in self.REJECT_ACTIONS:
            request.resolve("reject")
        else:
            request.resolve("approve")  # 未知操作，保守批准单次
```

---

## 9. Unified LLM Service (SDK-Based)

### 9.1 Service Architecture

```python
class LLMService:
    """基于 claude-agent-sdk 的统一 LLM 服务"""

    def __init__(self, work_dir: Path, config: Config | None = None):
        # P1-2: Use SessionManager (KimiSessionManager alias removed)
        self.session_manager = SessionManager(
            work_dir=work_dir,
            config=config,
        )
        self.approval_handler = DocuSwarmApprovalHandler()

    async def execute_context_validator(self, subject_context: dict) -> dict:
        """使用 prompt() 单次 API 执行上下文验证"""
        messages = await self.session_manager.single_prompt(
            user_input=json.dumps(subject_context),
            mode="instant",
            yolo=True,
        )
        return self._extract_content(messages)

    async def execute_independent(
        self,
        node_id: str,
        system_prompt: str,
        context: dict,
        session_id: str | None = None,
    ) -> dict:
        """使用 Session 多轮 API 执行 Independent Agent"""
        session = await self.session_manager.create_session(
            session_id=session_id or f"docuswarm-{node_id}",
            mode="agent",
            yolo=True,
            max_steps=50,
        )

        try:
            async with session:
                messages = await process_wire_stream(
                    session, json.dumps(context)
                )
                return self._extract_content(messages)
        except MaxStepsReached:
            return {"warning": "max_steps_reached"}
        except RunCancelled:
            return {"cancelled": True}

    async def execute_evaluator(
        self,
        system_prompt: str,
        subject_context: dict,
        deliverable: dict,
    ) -> dict:
        """使用 prompt() 单次 API + thinking 模式执行 Evaluator"""
        user_message = json.dumps({
            "subject_context": subject_context,
            "deliverable": deliverable,
            # NOTE: NO private_reasoning - context isolation
        })

        messages = await self.session_manager.single_prompt(
            user_input=user_message,
            mode="thinking",
            yolo=True,
        )
        return self._extract_content(messages)

    def _extract_content(self, messages: list[Message]) -> dict:
        """从 SDK Message 列表提取内容"""
        for msg in reversed(messages):
            if msg.content:
                return {"content": msg.content}
        return {}
```

---

## 10. SDK Message Type Handling Best Practices

> **Critical**: `claude_agent_sdk v0.1.68` message types do NOT have `role` or `type` attributes.  
> **Reference**: [Root Cause Analysis](../../research/2026-04-06-kimi-no-text-extracted-root-cause-analysis.md) | [TDD Fix Plan](../../solution/2026-04-06-kimi-message-extraction-tdd-plan.md)

### 10.1 Message Type Identification (Use `isinstance()`)

**❌ WRONG: Using `getattr()` with `role` attribute**
```python
# This will FAIL because AssistantMessage has no 'role' attribute
msg_role = getattr(msg, "role", "")
if msg_role == "assistant":  # Always False for AssistantMessage
    ...
```

**✅ CORRECT: Using `isinstance()` type checking**
```python
from claude_agent_sdk.types import AssistantMessage, UserMessage, SystemMessage

if isinstance(msg, AssistantMessage):
    role = "assistant"
elif isinstance(msg, UserMessage):
    role = "user"
elif isinstance(msg, SystemMessage):
    return None  # Skip system messages
```

### 10.2 Content Block Type Identification

**❌ WRONG: Using `getattr()` with `type` attribute**
```python
# This will FAIL because TextBlock has no 'type' attribute
item_type = getattr(item, "type", "")
if item_type == "text":  # Never matches TextBlock
    ...
```

**✅ CORRECT: Using `isinstance()` for ContentBlock types**
```python
from claude_agent_sdk.types import TextBlock, ThinkingBlock, ToolUseBlock, ToolResultBlock

if isinstance(item, TextBlock):
    converted_content.append({"type": "text", "text": item.text})
elif isinstance(item, ThinkingBlock):
    # ThinkingBlock has 'thinking' and 'signature' fields, no 'text'
    pass  # Skip or handle separately
elif isinstance(item, ToolUseBlock):
    converted_content.append({
        "type": "tool_use",
        "name": item.name,
        "input": item.input,
        "id": item.id,
    })
elif isinstance(item, ToolResultBlock):
    converted_content.append({
        "type": "tool_result",
        "tool_use_id": item.tool_use_id,
        "content": item.content,
    })
```

### 10.3 SDK Message Types Reference

```python
# Message Types (NO 'role' attribute!)
@dataclass
class AssistantMessage:
    content: list[ContentBlock]
    model: str
    parent_tool_use_id: str | None = None
    error: AssistantMessageError | None = None

@dataclass
class UserMessage:
    content: str | list[ContentBlock]

@dataclass
class SystemMessage:
    subtype: str  # e.g., 'init'
    data: dict = field(default_factory=dict)

@dataclass
class ResultMessage:
    result: str
    is_error: bool
    duration_ms: int
    num_turns: int
    session_id: str

# Content Block Types (NO 'type' attribute!)
@dataclass
class TextBlock:
    text: str

@dataclass
class ThinkingBlock:
    thinking: str
    signature: str

@dataclass
class ToolUseBlock:
    name: str
    input: dict
    id: str

@dataclass
class ToolResultBlock:
    tool_use_id: str
    content: str | list[dict]
    is_error: bool = False
```

### 10.4 Implementation Checklist

When implementing message handling code:

- [ ] Import SDK types: `from claude_agent_sdk.types import AssistantMessage, TextBlock, ...`
- [ ] Use `isinstance(msg, AssistantMessage)` instead of `getattr(msg, "role", "")`
- [ ] Use `isinstance(item, TextBlock)` instead of `getattr(item, "type", "")`
- [ ] Handle `SystemMessage` and `ResultMessage` appropriately (usually skip)
- [ ] Provide fallback for legacy dict-format messages (backward compatibility)
- [ ] Add unit tests with mock SDK message objects (no `role`/`type` attributes)

### 10.5 Testing with Mock SDK Objects

```python
# tests/conftest.py
@dataclass
class MockAssistantMessage:
    """Mock SDK AssistantMessage - NO role attribute!"""
    content: list[Any]
    model: str = "kimi"
    # Note: NO role field

@dataclass
class MockTextBlock:
    """Mock SDK TextBlock - NO type attribute!"""
    text: str
    # Note: NO type field

# Usage in tests
def test_extract_text_from_sdk_messages():
    msg = MockAssistantMessage(
        content=[MockTextBlock(text="Hello")]
    )
    result = extract_text_from_messages([msg])
    assert result == "Hello"
```

---

## 11. File Structure

```
docuswarm/llm/
├── __init__.py
├── session_manager.py    # SessionManager (P1-2: KimiSessionManager alias removed)
│                         # F9: _message_to_dict() uses isinstance() for type checking
├── response.py           # extract_text_from_messages() - F9: uses isinstance() 
├── claude_sdk_wrapper.py # ClaudeSDKWrapper (TDD-05)
├── mode_mapper.py        # SDKModeParams + MODE_MAP
├── approval.py           # DocuSwarmApprovalHandler
├── config.py             # SDK Config 适配
├── rate_limit.py         # 外层限流 (评估是否保留)
└── service.py            # LLMService 统一服务

docuswarm/tools/
├── __init__.py
├── create_deliverable.py # CreateDeliverableTool
└── update_context.py     # UpdateContextTool

docuswarm/agents/configs/
└── independent_agent.yaml  # Agent 工具配置

docuswarm/agents/
├── independent.py        # F9: Uses SessionManager._message_to_dict() for conversion
└── evaluator.py
```

---

## 12. References

### Related Documents

| Document | Location |
|----------|----------|
| System Architecture | `01_SYSTEM_ARCHITECTURE.md` |
| Agent Architecture | `02_AGENT_ARCHITECTURE.md` |
| Context Isolation | `06_CONTEXT_ISOLATION.md` |
| Transformation Plan | `docs/research/kimi-agent-sdk-transformation-plan.md` |
| **F9: Message Extraction Fix** | `docs/solution/2026-04-06-kimi-message-extraction-tdd-plan.md` |
| **F9: Root Cause Analysis** | `docs/research/2026-04-06-kimi-no-text-extracted-root-cause-analysis.md` |

### External References

- [kimi-agent-sdk Python SDK](https://github.com/anthropics/kimi-agent-sdk)
- [Kimi K2.5 API Documentation](https://platform.moonshot.cn/docs)
- [claude-agent-sdk Types Reference](../../autoBMAD/agentdocs/05_python.md) - Official SDK type definitions

---

**Document End**
> **2026-03-13 Alignment Notice**: 当前运行时代码仍广泛依赖 `kimi_agent_sdk`、`CallableTool2` 与 `KimiSessionManager`。因此，本文件中的 SDK 迁移描述应被视为目标态，而非现状。与当前可实施重构有关的部分，请优先参考 `../research/2026-03-13-docuswarm-context-refactor-overview.md`。
