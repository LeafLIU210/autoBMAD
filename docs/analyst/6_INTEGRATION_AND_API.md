# DocuSwarm Integration & API Analysis

**Version**: 3.0 (kimi-agent-sdk)  
**Date**: 2026-02-20  
**Category**: Integration & API  
**Topics Covered**: 6.1 - 6.6  
**Status**: Analysis Complete - Simplified

---

## Executive Summary

This analysis covers 6 topics related to external integrations and API design in DocuSwarm. The focus is on LLM integration, simplified rate limiting, and deferred features.

**Key Simplifications from Occam's Razor Analysis**:
- Dual-agent mode mapping (no Questioner mode)
- Simple rate limiting (SDK 内部处理基础连接管理，外层可选)
- Manual failover (no automatic circuit breaker for MVP)
- CallableTool2 工具定义 (kimi-agent-sdk 原生，替代 OpenAI Functions)
- RAG deferred to Phase 2
- WebSocket streaming deferred to Phase 2

**Key Findings**:
- Kimi K2.5 mode assignment: Instant for Orchestrator, Agent for Independent, Thinking for Evaluator
- Simple request counting sufficient for MVP single-user scenario
- Manual provider switching sufficient for MVP reliability

**Critical Dependencies**: Technology Stack decisions (Section 4) must be finalized first.

**Development Time Savings**: ~3-4 weeks compared to full integration implementation.

---

## Topic 6.1: Kimi K2.5 Mode Selection (Dual-Agent, kimi-agent-sdk)

### Context

Kimi K2.5 通过 kimi-agent-sdk 提供接入。DocuSwarm MVP uses dual-agent pattern:
- **Context Validator**: Intent classification and routing
- **Independent Agent**: Deliverable creation + question generation
- **Evaluator Agent**: Quality review (context-isolated)

### Research Findings

**Mode Characteristics (SDK 参数映射)**:

| Mode | SDK Params | Response Time | Tool Calls | Cost |
|------|-----------|---------------|------------|------|
| **Instant** | model="kimi", thinking=False, max_steps=5 | 3-8s | N/A | Lowest |
| **Thinking** | model="kimi", thinking=True, max_steps=10 | Variable | N/A | Medium |
| **Agent** | model="kimi", thinking=False, max_steps=50 | Variable | SDK 自动调度 | Good |

**Dual-Agent Mode Assignment (SDK API)**:

| DocuSwarm Agent | SDK API | SDK Mode Params | Rationale |
|-----------------|---------|----------------|-----------|
| Context Validator | `prompt()` 单次 | instant | Fast intent classification |
| Independent | `Session.prompt()` 多轮 | agent | Tool calling + multi-turn |
| Evaluator | `prompt()` 单次 | thinking | Detailed quality reasoning |

### Implementation Guidance

**Mode Configuration (kimi-agent-sdk)**:

```python
# config/llm_modes.py
from dataclasses import dataclass

@dataclass
class SDKModeParams:
    model: str
    thinking: bool
    max_steps_per_turn: int | None

MODE_MAP = {
    "context_validator": SDKModeParams(
        model="kimi", thinking=False, max_steps_per_turn=5
    ),
    "independent": SDKModeParams(
        model="kimi", thinking=False, max_steps_per_turn=50
    ),
    "evaluator": SDKModeParams(
        model="kimi", thinking=True, max_steps_per_turn=10
    ),
}

def get_mode_params(agent_type: str) -> SDKModeParams:
    """Get SDK mode params for agent type."""
    return MODE_MAP.get(agent_type, MODE_MAP["independent"])
```

### Recommendation

**Dual-Agent Mode Assignment (kimi-agent-sdk)**:

| Agent | SDK API | Mode | Temperature |
|-------|---------|------|-------------|
| Context Validator | prompt() | instant | 0.3 |
| Independent | Session.prompt() | agent | 0.7 |
| Evaluator | prompt() | thinking | 0.5 |

Benefits:
- Cost-optimized (instant 最低开销用于路由)
- Quality-optimized (thinking 用于评估)
- Session 持久化 (Independent Agent 多轮)
- Simplified (no Questioner mode needed)

---

## Topic 6.2: API Rate Limiting (SDK Internal + Optional External)

### Context

**kimi-agent-sdk 改造**: SDK 通过 kimi-cli 子进程管理底层连接，内部已包含基础重试/连接管理。外层限流作为可选防护层。

Kimi K2.5 Tier 3 limits:
- 20 concurrent requests
- 200 RPM
- 5M TPM

### Implementation Guidance

**策略**: SDK 内部处理基础连接管理，外层保留简单信号量作为并发防护（评估是否必需）。

```python
import asyncio
from typing import Optional

class OptionalRateLimiter:
    """可选外层并发限制 (如 SDK 自身限流足够，Phase 4 可移除)"""

    def __init__(self, max_concurrent: int = 20):
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def __aenter__(self):
        await self._semaphore.acquire()
        return self

    async def __aexit__(self, *args):
        self._semaphore.release()

# Usage:
# async with rate_limiter:
#     messages = await session_manager.single_prompt(...)
```

### Recommendation

**Simple request counting + SDK 内部管理** for MVP.

Configuration:
- SDK 内部: 连接管理、消息序列化、基础重试
- 外层可选: asyncio.Semaphore (max_concurrent=20)
- 如 SDK 自身限流足够 → Phase 4 移除外层

Phase 2 Enhancement:
- Token bucket with burst control
- TPM tracking
- Per-model limits

---

## Topic 6.3: Multi-Provider Fallback (Simplified)

### Context

**Occam's Razor Decision**: Manual provider switching for MVP. Automatic circuit breaker deferred to Phase 2.

### Implementation Guidance

**Simple Fallback Client (MVP, kimi-agent-sdk 场景)**:

> **Note**: kimi-agent-sdk 绑定 Kimi K2.5，不支持多 provider 切换。
> 如需 fallback，需在 SDK 层之上做 provider 选择逻辑。
> MVP 阶段使用单一 provider，fallback 延迟到 Phase 2。

```python
# MVP: 单一 provider (kimi-agent-sdk)
# 如 SDK 调用失败，记录错误并返回，不尝试切换 provider

from kimi_agent_sdk.exceptions import ChatProviderError, APIConnectionError

class SimpleFallbackHandler:
    """MVP: 记录错误，不切换 provider。"""

    async def execute_with_logging(self, operation, *args, **kwargs):
        try:
            return await operation(*args, **kwargs)
        except (ChatProviderError, APIConnectionError) as e:
            import structlog
            logger = structlog.get_logger()
            logger.error("kimi_sdk_error", error=str(e))
            raise
```

### Recommendation

**Simple fallback with error logging** for MVP.

MVP Behavior:
- kimi-agent-sdk 绑定 Kimi K2.5 (单一 provider)
- SDK 内部处理基础重试
- 外层记录错误日志
- 不尝试切换 provider

Phase 2 Enhancement:
- Automatic circuit breaker
- Health monitoring
- Automatic recovery

---

## Topic 6.4: Tool Definition Standard (CallableTool2 via kimi-agent-sdk)

### Context

**kimi-agent-sdk 改造**: 使用 SDK 原生 CallableTool2 + Pydantic 替代 OpenAI Functions JSON Schema。MCP 迁移不再需要。

### Implementation Guidance

**CallableTool2 工具定义**:

```python
from pydantic import BaseModel, Field
from kimi_agent_sdk import CallableTool2, ToolOk, ToolError, ToolReturnValue

class CreateDeliverableParams(BaseModel):
    title: str = Field(description="Document title")
    content: str = Field(description="Document content in Markdown")

class CreateDeliverableTool(CallableTool2):
    name: str = "create_deliverable"
    description: str = "Create the deliverable document"
    params: type[CreateDeliverableParams] = CreateDeliverableParams

    async def __call__(self, params: CreateDeliverableParams) -> ToolReturnValue:
        # ... save deliverable
        return ToolOk(output=f"Deliverable '{params.title}' created")

class UpdateContextParams(BaseModel):
    key: str = Field(description="Context key")
    value: dict = Field(description="Value to store")

class UpdateContextTool(CallableTool2):
    name: str = "update_context"
    description: str = "Update shared subject context"
    params: type[UpdateContextParams] = UpdateContextParams

    async def __call__(self, params: UpdateContextParams) -> ToolReturnValue:
        # ... update context
        return ToolOk(output=f"Context '{params.key}' updated")
```

**agent_file.yaml 注册**:

```yaml
version: 1
agent:
  extend: default
  tools:
    - "docuswarm.tools.create_deliverable:CreateDeliverableTool"
    - "docuswarm.tools.update_context:UpdateContextTool"
```

### Recommendation

**CallableTool2 + agent_file.yaml** — SDK 原生工具体系。

Tools:
1. `create_deliverable` - CallableTool2 (Pydantic 参数)
2. `update_context` - CallableTool2 (Pydantic 参数)

优势:
- SDK 自动调度 (无需手动解析 tool_calls)
- Pydantic 类型安全
- 声明式注册 (YAML)
- MCP 迁移不再需要

---

## Topic 6.5: RAG Query Optimization (Deferred)

### Context

**Occam's Razor Decision**: RAG is deferred to Phase 2. MVP uses direct context passing.

### MVP Approach

```python
class DirectContextManager:
    """MVP: Direct context passing without RAG."""
    
    def __init__(self, state_manager):
        self.state_manager = state_manager
    
    def build_node_context(self, pipeline_id: str, node_id: str) -> dict:
        """Build context from pipeline state."""
        state = self.state_manager.get_pipeline(pipeline_id)
        
        return {
            "subject_context": state["subject_context"],
            "previous_deliverables": {
                nid: node["deliverable"]
                for nid, node in state.get("nodes", {}).items()
                if node.get("status") == "completed"
            }
        }
```

### Recommendation

**Defer RAG to Phase 2** - direct context passing is sufficient for MVP.

---

## Topic 6.6: WebSocket Real-Time Updates (Deferred)

### Context

**Occam's Razor Decision**: WebSocket streaming is deferred to Phase 2. MVP uses simple console output.

### MVP Approach

```python
class ConsoleProgressReporter:
    """MVP: Simple console progress reporting."""
    
    def __init__(self, pipeline_id: str):
        self.pipeline_id = pipeline_id
    
    def report_pipeline_started(self):
        print(f"[{self.pipeline_id}] Pipeline started")
    
    def report_node_started(self, node_id: str):
        print(f"[{self.pipeline_id}] Node {node_id} started")
    
    def report_node_completed(self, node_id: str, score: float, verdict: str):
        print(f"[{self.pipeline_id}] Node {node_id} completed: {verdict} (score: {score:.2f})")
    
    def report_pipeline_completed(self):
        print(f"[{self.pipeline_id}] Pipeline completed")
```

### Recommendation

**Defer WebSocket to Phase 2** - console output sufficient for MVP.

---

## Cross-Topic Dependencies (Updated)

```
6.1 Kimi Mode Selection
 └─→ 1.1 Dual-Agent Pattern
 └─→ kimi-agent-sdk SDK 参数映射

6.2 API Rate Limiting
 └─→ SDK 内部连接管理
 └─→ 外层可选并发信号量

6.3 Multi-Provider Fallback
 └─→ kimi-agent-sdk 绑定 Kimi K2.5
 └─→ Phase 2: 外层 provider 选择

6.4 Tool Definition Standard
 └─→ CallableTool2 (SDK 原生)
 └─→ agent_file.yaml 声明式注册

6.5 RAG Query Optimization
 └─→ Deferred to Phase 2
 └─→ MVP: Direct context passing

6.6 WebSocket Real-Time Updates
 └─→ Deferred to Phase 2
 └─→ MVP: Console output
```

---

## Summary of Occam's Razor Simplifications

| Topic | Original Design | Simplified Design | Savings |
|-------|----------------|-------------------|---------|
| 6.1 Mode Selection | 4 agent types | 3 agent types (SDK 参数映射) | Simpler mapping |
| 6.2 Rate Limiting | Token bucket + backpressure | SDK 内部 + 可选信号量 | ~1 week |
| 6.3 Fallback | Circuit breaker + auto-recovery | 单 provider (SDK 绑定) | ~1 week |
| 6.4 Tools | 4 tools + MCP abstraction | 2 CallableTool2 (SDK 原生) | ~1 week |
| 6.5 RAG | Full optimization | Deferred | ~2 weeks |
| 6.6 WebSocket | Full streaming | Deferred | ~1 week |

**Total Estimated Savings**: ~3-4 weeks development time

---

## References

### Research Sources
- Kimi K2.5 API Documentation (platform.moonshot.ai)
- OpenAI Function Calling Specification

### Related Analysis Documents
- [4_TECHNOLOGY_STACK.md](4_TECHNOLOGY_STACK.md) - Provider selection
- [2_AGENT_SYSTEM_DESIGN.md](2_AGENT_SYSTEM_DESIGN.md) - Dual-agent pattern

---

**Document Status**: Version 3.0 - kimi-agent-sdk  
**Key Change**: SDK 原生接入替代 HTTP 直连; CallableTool2 替代 OpenAI Functions  
**Development Time Savings**: ~3-4 weeks compared to full integration
