# DocuSwarm Technology Stack

**Version**: 5.1 (TDD SDK Migration - Fixing Dependency Drift)  
**Date**: 2026-03-25  
**Status**: In Progress  
**Author**: Solution Architect  

> **重要提示**: 当前正在进行 [TDD SDK Migration](../solution/TDD-SDK-Migration-2026-03-25.md) 以修复依赖漂移。详见 [Dependency Drift Research](../research/dependency-drift-2026-03-25/README.md)。
> 
> **依赖漂移状态**: Drift Score 85/100 (CRITICAL) - 7个文件使用 kimi-agent-sdk，3个文件使用 kaos.path
>
> **迁移研究报告**: [完全移除 kimi-agent-sdk](../research/migration/README.md)  

---

## 1. Overview

This document provides a comprehensive specification of the technology stack used in DocuSwarm, including core technologies, dependencies, version requirements, and architectural rationale.

### 1.1 Technology Selection Principles

| Principle | Description | Application |
|-----------|-------------|-------------|
| **Occam's Razor** | Choose the simplest solution | Single LLM provider, SQLite over PostgreSQL |
| **Battle-Tested** | Prefer mature, stable technologies | LangGraph, SQLite, Python |
| **Native Integration** | Minimize adapter layers | LangGraph SqliteSaver for checkpointing |
| **Cost Efficiency** | Optimize operational costs | Kimi K2.5 with context caching |

### 1.2 Stack Summary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DocuSwarm Technology Stack                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Application Layer                                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  Python 3.14+    │  LangGraph 0.2+    │  Click (CLI)                 │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  Integration Layer                                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  claude-agent-sdk │  langgraph         │  pydantic 2.0+              │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  LLM Provider                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  Kimi K2.5 (256K context) │  Kimi Code API (OpenAI-compatible)      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  Persistence Layer                                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  SQLite 3.35+    │  WAL Mode          │  LangGraph SqliteSaver       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  Development Tools                                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  pytest          │  Black             │  Ruff      │  Basedpyright   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Technologies

### 2.1 Programming Language

#### Python 3.14+

| Attribute | Specification |
|-----------|---------------|
| **Version** | 3.14+ (required: 3.14) |
| **Rationale** | LangGraph native support, mature async ecosystem |
| **Key Features** | Pattern matching, improved type hints, asyncio |

**Why Python 3.14+:****
- Native support for `TypedDict`, `Literal`, and advanced type hints
- LangGraph and LangChain ecosystem is Python-first
- Mature async/await support for concurrent API calls
- Rich ecosystem of AI/ML libraries

**Alternatives Considered:**
| Alternative | Rejected Reason |
|-------------|-----------------|
| TypeScript | LangGraph.js is less mature than Python version |
| Go | Lack of LangGraph equivalent, limited AI tooling |
| Rust | Steep learning curve, no LangGraph support |

### 2.2 Multi-Agent Framework

#### LangGraph 0.2+

| Attribute | Specification |
|-----------|---------------|
| **Version** | >=0.2.0 |
| **Package** | `langgraph` |
| **Documentation** | https://langchain-ai.github.io/langgraph/ |

**Core Features Used:**
```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

# Key LangGraph components
- StateGraph          # Node execution graph definition
- SqliteSaver         # Checkpoint persistence
- thread_config       # Concurrent node run isolation
- Conditional edges   # Dynamic routing (Phase 2)
```

**Why LangGraph:**
- **Time Savings**: 8-12 weeks vs custom NodeExecutor
- **Battle-Tested**: Production-ready state management
- **Native Checkpointing**: SqliteSaver for resume capability
- **Thread Isolation**: Concurrent node run support out-of-box

**Alternatives Considered:**
| Alternative | Rejected Reason |
|-------------|-----------------|
| Custom NodeExecutor | 8-12 weeks additional development |
| CrewAI | Less flexible state management |
| AutoGen | Heavier, more complex for our use case |
| Haystack | Focused on RAG, not multi-agent workflows |

### 2.3 LLM Provider

#### Kimi K2.5

| Attribute | Specification |
|-----------|---------------|
| **Provider** | Moonshot AI |
| **Integration** | claude-agent-sdk (Python SDK) |
| **Protocol** | HTTP/REST (OpenAI-compatible) |
| **Context Window** | 256K tokens |
| **API Compatibility** | SDK 原生 (非 HTTP 直连) |

**Mode Specifications (SDK 参数映射):**

| Mode | Use Case | SDK Params | Response Time |
|------|----------|-----------|---------------|
| **Instant** | Context Validator | model="kimi", thinking=False, max_steps=5 | 3-8 seconds |
| **Thinking** | Evaluator | model="kimi", thinking=True, max_steps=10 | 10-30 seconds |
| **Agent** | Independent | model="kimi", thinking=False, max_steps=50 | 30-120 seconds |

**Rate Limits (Tier 3):**
| Limit Type | Value |
|------------|-------|
| Concurrent Requests | 20 |
| Requests per Minute | 200 |
| Tokens per Minute | 5,000,000 |

**Pricing:**
| Type | Price (per 1M tokens) |
|------|----------------------|
| Input (Cache Miss) | $0.60 |
| Input (Cache Hit) | $0.10 |
| Output | $2.50 |

**Why Kimi K2.5:**
- **Large Context**: 256K tokens eliminates need for RAG in MVP
- **Cost Effective**: Competitive pricing with caching
- **Multi-Mode**: Different modes optimized for different tasks
- **claude-agent-sdk**: 原生 Python SDK 提供 query() API、标准工具系统、ResultMessage 响应格式

**Alternatives Considered:**
| Alternative | Rejected Reason |
|-------------|-----------------|
| GPT-4 Turbo | Higher cost, 128K context |
| Claude 3 | Higher cost, 200K context |
| Gemini Pro | Less mature API, variable quality |
| Local LLMs | Insufficient capability for complex tasks |

### 2.4 Database

#### SQLite with WAL Mode

| Attribute | Specification |
|-----------|---------------|
| **Version** | 3.35+ (for JSON functions) |
| **Mode** | WAL (Write-Ahead Logging) |
| **Location** | `docuswarm.db` (local file) |

**Configuration:**
```python
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;
PRAGMA foreign_keys = ON;
PRAGMA synchronous = NORMAL;
```

**Database Schema:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Database Tables                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  node_runs                                                                   │
│  ├── run_id (PK)                                                            │
│  ├── node_id                                                                │
│  ├── context_hash                                                           │
│  ├── status (pending/running/completed/failed)                              │
│  ├── iteration                                                              │
│  ├── deliverable (JSON)                                                     │
│  ├── questions (JSON)                                                       │
│  ├── evaluation (JSON)                                                      │
│  ├── created_at                                                             │
│  └── updated_at                                                             │
│                                                                             │
│  subject_context                                                             │
│  ├── context_hash (PK)                                                      │
│  ├── context_data (JSON)                                                    │
│  └── updated_at                                                             │
│                                                                             │
│  checkpoints (LangGraph managed)                                             │
│  └── [LangGraph internal schema]                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Why SQLite:**
- **Simplicity**: Zero configuration, file-based
- **ACID**: Full transaction support with WAL
- **Native Integration**: LangGraph SqliteSaver support
- **Portability**: Single file, easy backup/migration

**Alternatives Considered:**
| Alternative | Rejected Reason |
|-------------|-----------------|
| PostgreSQL | Overkill for MVP, requires server setup |
| Redis | No ACID, transient storage |
| MongoDB | Schema-less adds complexity |
| DuckDB | Less mature, limited tooling |

---

## 3. Dependency Drift Status (Current Issue)

> **重要提示**: 当前技术栈存在严重的依赖漂移问题。
> 
> **TDD 迁移方案**: [TDD-SDK-Migration-2026-03-25](../solution/TDD-SDK-Migration-2026-03-25.md)  
> **详细研究**: [Dependency Drift Research](../research/dependency-drift-2026-03-25/README.md)

### 3.1 Drift Summary

| 指标 | 数值 | 严重程度 |
|------|------|----------|
| **Drift Score** | 85/100 | CRITICAL |
| **声明依赖** | claude-agent-sdk | ✅ 正确 |
| **实际使用** | kimi-agent-sdk + kaos.path | ❌ 错误 |
| **受影响文件** | 7个文件 + 3个 kaos 文件 | 必须修复 |
| **迁移进度** | 0% | 刚开始 |

### 3.2 Affected Files

**kimi-agent-sdk 依赖 (7个文件)**:
| 文件 | 导入内容 | 迁移策略 |
|------|----------|----------|
| `llm/session_manager.py` | Session, Config, Message, WireMessage, MessageAggregator | 使用 claude-agent-sdk.query() |
| `agents/independent.py` | Message, MessageAggregator | 使用 dict[str, Any] |
| `agents/evaluator.py` | Message | 使用 dict[str, Any] |
| `llm/approval.py` | ApprovalRequest | 使用 dict[str, Any] |
| `pipeline/orchestrator.py` | Message | 使用 dict[str, Any] |
| `tools/callable_tool_wrapper.py` | CallableTool2 | 使用纯函数 |
| `tools/sdk_adapter.py` | ToolOk, ToolError | 使用 dict 格式 |

**kaos.path 依赖 (3个文件)**:
| 文件 | 替换为 |
|------|--------|
| `llm/session_manager.py` | `pathlib.Path` |
| `agents/independent.py` | `pathlib.Path` |
| `pipeline/orchestrator.py` | `pathlib.Path` |

### 3.3 Migration Plan

使用 [TDD (Test-Driven Development)](../solution/TDD-SDK-Migration-2026-03-25.md) 方法:

| 阶段 | 内容 | 测试文件 |
|------|------|----------|
| Phase 1 | 基础设施 | `tests/conftest.py` |
| Phase 2 | SessionManager | `tests/llm/test_session_manager_tdd.py` |
| Phase 3 | 工具系统 | `tests/tools/test_sdk_adapter_tdd.py` |
| Phase 4 | Agent 层 | `tests/agents/test_independent_agent_tdd.py` |
| Phase 5 | 集成验证 | `tests/cli/test_cli_integration_tdd.py` |

---

## 4. Dependencies

### 4.1 Core Dependencies

```toml
[project]
requires-python = ">=3.14"

[project.dependencies]
# Multi-agent framework
langgraph = ">=0.2.0"
langchain-core = ">=0.2.0"

# LLM Integration (claude-agent-sdk)
claude-agent-sdk = ">=0.1.0"

# Data validation
pydantic = ">=2.0.0"

# Async support
aiofiles = ">=23.0.0"

# CLI interface
click = ">=8.1.0"
rich = ">=13.0.0"

# Configuration
python-dotenv = ">=1.0.0"
pyyaml = ">=6.0.0"

# Utilities
structlog = ">=24.0.0"
```

### 4.2 Development Dependencies

```toml
[project.optional-dependencies]
dev = [
    # Testing
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.0.0",
    "pytest-mock>=3.12.0",
    
    # Type checking
    "basedpyright>=1.10.0",
    
    # Linting and formatting
    "ruff>=0.3.0",
    "black>=24.0.0",
    
    # Pre-commit
    "pre-commit>=3.6.0",
]
```

### 4.3 Dependency Graph

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Dependency Relationships                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  docuswarm                                                                   │
│  │                                                                          │
│  ├── langgraph                                                              │
│  │   ├── langchain-core                                                     │
│  │   └── [internal deps]                                                    │
│  │                                                                          │
│  ├── claude-agent-sdk ───────────── Kimi K2.5 (Kimi Code API)              │
│  │   └── pydantic (工具参数验证)                                            │
│  │                                                                          │
│  ├── pydantic ──────────────────────── Data validation                     │
│  │                                                                          │
│  ├── click + rich ──────────────────── CLI interface                       │
│  │                                                                          │
│  └── structlog ─────────────────────── Structured logging                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Development Tools

### 4.1 Type Checking

#### Basedpyright

| Attribute | Specification |
|-----------|---------------|
| **Package** | `basedpyright` |
| **Version** | >=1.10.0 |
| **Mode** | Strict |

**Configuration (pyproject.toml):**
```toml
[tool.basedpyright]
pythonVersion = "3.14"
typeCheckingMode = "strict"
reportMissingTypeStubs = false
reportUnknownMemberType = false
reportUnknownArgumentType = false
```

### 4.2 Linting

#### Ruff

| Attribute | Specification |
|-----------|---------------|
| **Package** | `ruff` |
| **Version** | >=0.3.0 |
| **Rules** | E, F, W, I, N, UP, ANN, B, C4, DTZ, PIE, PT, RET, SIM, TCH |

**Configuration (pyproject.toml):**
```toml
[tool.ruff]
target-version = "py314"
line-length = 100

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "F",      # pyflakes
    "W",      # pycodestyle warnings
    "I",      # isort
    "N",      # pep8-naming
    "UP",     # pyupgrade
    "ANN",    # flake8-annotations
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "DTZ",    # flake8-datetimez
    "PIE",    # flake8-pie
    "PT",     # flake8-pytest-style
    "RET",    # flake8-return
    "SIM",    # flake8-simplify
    "TCH",    # flake8-type-checking
]
ignore = ["ANN101", "ANN102"]  # self, cls
```

### 4.3 Formatting

#### Black

| Attribute | Specification |
|-----------|---------------|
| **Package** | `black` |
| **Version** | >=24.0.0 |
| **Line Length** | 100 |

**Configuration (pyproject.toml):**
```toml
[tool.black]
line-length = 100
target-version = ["py314"]
```

### 4.4 Testing

#### pytest

| Attribute | Specification |
|-----------|---------------|
| **Package** | `pytest` |
| **Version** | >=8.0.0 |
| **Coverage Target** | >=80% |

**Configuration (pyproject.toml):**
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "-v --tb=short"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "slow: Slow-running tests",
]

[tool.coverage.run]
source = ["docuswarm"]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
```

### 4.5 Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/psf/black
    rev: 24.2.0
    hooks:
      - id: black

  - repo: local
    hooks:
      - id: basedpyright
        name: basedpyright
        entry: basedpyright
        language: system
        types: [python]
        pass_filenames: false
```

---

## 5. Integration Architecture

### 5.1 LLM Integration

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LLM Integration Flow                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DocuSwarm                                                                   │
│  │                                                                          │
│  ├── SessionManager (SDK 适配层)                                            │
│  │   └── single_prompt()  ── All Agents (stateless query)                   │
│  │                                                                          │
│  └── Request Flow (SDK-managed):                                            │
│      │                                                                      │
│      ├── 1. SDK query() call                                               │
│      ├── 2. AsyncGenerator response                                        │
│      ├── 3. ResultMessage extraction                                       │
│      ├── 4. ToolUseBlock handling (standard tool system)                   │
│      └── 5. SafeAsyncGenerator wrapper for cancellation                    │
│                                                                             │
│                         │                                                   │
│                         ▼                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         claude-agent-sdk → Kimi Code API                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 State Management Integration

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      State Management Integration                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LangGraph StateGraph                                                        │
│  │                                                                          │
│  ├── NodeRunState (TypedDict)                                               │
│  │   ├── run_id: str                                                        │
│  │   ├── node_id: str                                                       │
│  │   ├── context_hash: str                                                  │
│  │   ├── current_node: Optional[str]                                        │
│  │   ├── completed_nodes: List[str]                                         │
│  │   ├── deliverables: Dict[str, dict]                                      │
│  │   ├── questions: Dict[str, List[dict]]                                   │
│  │   └── evaluations: Dict[str, dict]                                       │
│  │                                                                          │
│  └── SqliteSaver                                                            │
│      │                                                                      │
│      ├── Checkpoint Storage                                                 │
│      │   ├── Automatic state serialization                                  │
│      │   ├── Thread-based isolation                                         │
│      │   └── Resume capability                                              │
│      │                                                                      │
│      └── Integration:                                                       │
│          checkpointer = SqliteSaver.from_conn_string("docuswarm.db")       │
│          graph = graph.compile(checkpointer=checkpointer)                  │
│                                                                             │
│  Custom State Manager                                                        │
│  │                                                                          │
│  ├── Node run metadata                                                      │
│  ├── Node results                                                           │
│  └── Subject context updates                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Runtime Environment

### 6.1 Environment Configuration

> **P1-2 Config Semantics Note**: 项目已完成配置命名统一（Phase 10）。**仅支持 `ANTHROPIC_*` 环境变量**。
> - `ANTHROPIC_API_KEY` 和 `ANTHROPIC_BASE_URL` 是唯一支持的配置
> - `KIMI_API_KEY`、`CLAUDE_API_KEY` 等旧命名已彻底移除，无兼容层
> 详见 [P1-2 Deep Research](../research/2026-04-03-p1-2-config-semantics-analysis-report.md)。

```bash
# .env - 唯一支持的配置
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_BASE_URL=https://api.kimi.com/coding/
DOCUSWARM_DB_PATH=docuswarm.db
DOCUSWARM_OUTPUT_DIR=output
DOCUSWARM_LOG_LEVEL=INFO
```

> **2026-04-05 Update**: `ANTHROPIC_MODEL_NAME` 环境变量已移除。模型选择由 Kimi Code API 网关统一管理，客户端无需也不应指定模型。详见 [Session Execution Failure Solution](../research/session-execution-failure-solution.md)。

**环境变量映射 (P1-2 Final)**:

| 旧配置 (Removed) | 新配置 (Required) | 处理方式 |
|-----------------|-------------------|----------|
| `KIMI_API_KEY` | `ANTHROPIC_API_KEY` | **直接替换，无兼容** |
| `KIMI_BASE_URL` | `ANTHROPIC_BASE_URL` | **直接替换，无兼容** |
| `CLAUDE_API_KEY` | `ANTHROPIC_API_KEY` | **直接替换，无兼容** |
| `CLAUDE_BASE_URL` | `ANTHROPIC_BASE_URL` | **直接替换，无兼容** |
| `CLAUDE_MODEL_NAME` | *(已移除)* | 模型由 API 网关统一管理 |

### 6.2 System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **Python** | 3.14 | 3.14 |
| **RAM** | 4GB | 8GB |
| **Storage** | 1GB | 10GB |
| **Network** | Internet access | Stable connection |

### 6.3 Platform Support

| Platform | Status | Notes |
|----------|--------|-------|
| **Linux** | Supported | Primary development platform |
| **macOS** | Supported | Tested on Apple Silicon |
| **Windows** | Supported | WSL2 recommended |

---

## 7. Version Compatibility Matrix

### 7.1 Core Components

| Component | MVP Version | Minimum | Maximum |
|-----------|-------------|---------|---------|  
| Python | 3.14 | 3.14 | 3.14 |
| LangGraph | 0.2.x | 0.2.0 | <0.3.0 |
| claude-agent-sdk | 0.1.x | 0.1.0 | <1.0.0 |
| pydantic | 2.x | 2.0.0 | <3.0.0 |
| SQLite | 3.35+ | 3.35 | latest |

### 7.2 Breaking Change Policy

| Change Type | Handling |
|-------------|----------|
| LangGraph minor version | Test before upgrade |
| LangGraph major version | Requires migration plan |
| claude-agent-sdk minor version | Test before upgrade |
| Pydantic major version | Requires model updates |
| Python minor version | Generally compatible |

---

## 8. Security Considerations

### 8.1 API Key Management

```python
# Secure API key handling
import os
from pathlib import Path

def get_api_key() -> str:
    """Get API key from environment."""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError("ANTHROPIC_API_KEY not set")
    return key

# NEVER:
# - Commit API keys to version control
# - Log API keys
# - Store API keys in code
```

### 8.2 Dependency Security

| Practice | Implementation |
|----------|----------------|
| **Pin versions** | Use exact versions in requirements |
| **Regular updates** | Monthly dependency audit |
| **Vulnerability scanning** | pip-audit, safety |
| **License compliance** | pip-licenses check |

---

## 9. Performance Characteristics

### 9.1 Expected Performance

| Metric | Target | Typical |
|--------|--------|---------|
| **Node execution** | <2 min | 30-90 sec |
| **Full 5-node run** | <15 min | 8-12 min |
| **Checkpoint save** | <1 sec | 50-200 ms |
| **State query** | <100 ms | 10-50 ms |

### 9.2 Resource Usage

| Resource | Idle | Active (1 node run) | Peak (5 concurrent) |
|----------|------|---------------------|-------------------|
| **CPU** | <1% | 5-15% | 20-40% |
| **RAM** | 200MB | 500MB | 1.5GB |
| **Disk I/O** | Minimal | Low | Moderate |
| **Network** | None | 1-5 MB/min | 5-25 MB/min |

---

## 10. Phase 2 Technology Additions

### 10.1 Planned Additions

| Technology | Purpose | Timeline |
|------------|---------|----------|
| **Redis** | Rate limiting, caching | Phase 2 |
| **PostgreSQL** | Scalable persistence (optional) | Phase 2 |
| **FastAPI** | Web API (if web UI added) | Phase 3 |

> **Note**: MCP Protocol 已实现 SDK MCP 格式迁移。FastMCP 格式导致 `TypeError: Object of type FastMCP is not JSON serializable`，现已迁移到 SDK MCP 格式，完全兼容 claude-agent-sdk。详见 [FastMCP SDK 兼容性研究报告](../research/fastmcp-sdk-compatibility-issue.md) 和 [Test-Driven SDK MCP Migration](../solution/test-driven-sdk-mcp-migration-plan.md)。

### 10.2 Deferred Technologies

| Technology | Reason for Deferral |
|------------|---------------------|
| **Vector Database** | 256K context sufficient for MVP |
| **Multi-provider LLM** | claude-agent-sdk 绑定 Kimi K2.5，单 provider 简化调试 |
| **Kubernetes** | MVP runs single instance |
| **Message Queue** | Node-centric execution doesn't require |

---

## 11. References

### Related Documents

| Document | Location |
|----------|----------|
| System Architecture | `01_SYSTEM_ARCHITECTURE.md` |
| LLM Integration | `05_LLM_INTEGRATION.md` |
| Coding Standards | `coding-standards.md` |
| Project Structure | `project-structure.md` |

### External References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [claude-agent-sdk Python SDK](https://github.com/anthropics/claude-agent-sdk)
- [Kimi K2.5 API](https://platform.moonshot.cn/docs)
- [SQLite WAL Mode](https://sqlite.org/wal.html)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/)
- [Ruff Linter](https://docs.astral.sh/ruff/)

---

**Document End**
> **2026-03-13 Alignment Notice**: 技术栈文档中的“已完全移除 kimi-agent-sdk”目前与代码不符。涉及实际改造优先级时，请按 `../research/2026-03-13-docuswarm-context-refactor-overview.md` 的顺序执行，而不要以本文默认状态为前提。


## 11. P0-2/P0-3 架构约束 (2026-04-03)

### 11.1 单执行主干 (P0-2)

**核心原则**: 系统内只允许存在 **一套** 执行主干。

| 组件 | 唯一实现位置 | 状态 |
|------|-------------|------|
| `create_node_executor` | `node_execution/executor.py` | ✅ 活跃 |
| 图工厂 | `pipeline/graph.py:create_pipeline_graph` | ✅ 活跃 |

**已删除组件**:
- `nodes/dual_agent.py:create_node_executor` → 物理删除
- `node_execution/graph.py` → 物理删除
- `node_execution/flow.py` → 物理删除

**架构守护测试**:
```python
# tests/architecture/test_p0_2_execution_trunk_retirement.py
def test_exactly_one_create_node_executor_implementation():
    """全代码库中只允许存在 node_execution/executor.py 中的实现。"""
    ...
```

### 11.2 同步/异步契约 (P0-3)

**StateManager 同步契约**:
```python
# ✅ StateManager 提供同步接口
class StateManager:
    def get_latest_successful_run(...): ...  # def, not async def
    def save_node_result(...): ...

# ❌ 禁止: await 同步方法
run_result = await state_manager.get_latest_successful_run(...)  # TypeError!

# ✅ 上层 async 代码使用 asyncio.to_thread()
run_result = await asyncio.to_thread(
    state_manager.get_latest_successful_run, pred_id, context_hash
)
```

**pipeline/graph.py 约束**:
```python
# ❌ 禁止: run_until_complete 自举
checkpointer = loop.run_until_complete(create_async_checkpointer())  # RuntimeError!

# ✅ 必须: 预创建 checkpointer 传入
if checkpointer is None and db_path is not None:
    raise ValueError(
        "create_pipeline_graph does not support self-bootstrapping a checkpointer."
    )
```

**禁止 _run_async 桥接**:
```python
# ❌ 禁止: ThreadPoolExecutor + asyncio.run 桥接
def _run_async(coro):
    with ThreadPoolExecutor() as pool:
        future = pool.submit(asyncio.run, coro)
        return future.result()
```

### 11.3 参考文档

| 文档 | 说明 |
|------|------|
| [Test-Driven Retirement Plan](../solution/2026-04-03-p0-2-p0-3-test-driven-retirement-plan.md) | 测试驱动退役方案 |
| [Deep Research Report](../research/2026-04-03-p0-2-p0-3-deep-research-report.md) | 问题深度研究 |

---

**Document End**
> **2026-03-13 Alignment Notice**: 技术栈文档中的"已完全移除 kimi-agent-sdk"目前与代码不符。涉及实际改造优先级时，请按 `../research/2026-03-13-docuswarm-context-refactor-overview.md` 的顺序执行，而不要以本文默认状态为前提。
> 
> **2026-04-03 P0-2/P0-3 Update**: 新增单执行主干和同步/异步契约约束。详见第11节。
