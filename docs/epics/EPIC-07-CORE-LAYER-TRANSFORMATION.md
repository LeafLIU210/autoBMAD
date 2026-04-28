# Epic 7: Core Layer Transformation

> **⚠️ 已更新**: 本 Epic 已更新为**完全移除** `kimi-agent-sdk`，使用 `claude-agent-sdk` + Kimi Code API 方案。零向后兼容。详见 [迁移研究报告](../research/migration/README.md)。

**Epic ID**: EPIC-07  
**Version**: 3.0 (完全移除版)  
**Date**: 2026-03-02  
**Status**: Completed  
**Owner**: Tech Lead  
**Phase**: Phase 1 (Core Layer Transformation)

---

## 1. Epic Overview

### 1.1 Summary

**完全移除** `kimi-agent-sdk`，将核心 LLM 交互层从 KimiClient (httpx direct REST) 迁移到基于 `claude-agent-sdk` 的 SessionManager。包括创建 SessionManager 作为 SDK 适配层（由 ClaudeSDKWrapper 支持），并适配 BaseAgent、IndependentAgent 和 EvaluatorAgent 使用新的 SDK API。这是迁移中影响最大的阶段。

> **关键决策**: 完全移除 kimi-agent-sdk，不保留任何兼容层。详见 [迁移研究报告](../research/migration/README.md)。

### 1.2 Business Value

- **完全移除 kimi-agent-sdk**: 零向后兼容，完全移除所有 kimi-agent-sdk 依赖
- **Unified SDK**: Uses claude-agent-sdk with Kimi Code API's OpenAI-compatible interface
- **Architecture Alignment**: Consistent with epic_automation SDK usage
- **Simplified Tool Handling**: 纯函数工具替代 CallableTool2，标准 Tool Use Block 模式
- **Typed Exceptions**: 统一异常体系替代 SDK 特定异常

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| SessionManager operational | single_prompt/execute_with_tools cycle works |
| IndependentAgent adapted | Agent mode with tools via SDK |
| EvaluatorAgent adapted | Thinking mode via single_prompt() API |
| Single node execution | One BMAD node completes end-to-end via SDK |

### 1.4 Dependencies

- **Requires**: Epic 6 (SDK Preparation) completed
- **Blocks**: Epic 8 (Tool Migration), Epic 9 (Session & Cancellation)

### 1.5 Source Reference

Based on: `docs/epics/EPIC-16-SDK-WRAPPER.md`

---

## 2. Architecture Context

### 2.1 Transformation Overview

```
Before (v3.1):
  Agent → KimiClient (httpx) → Kimi REST API
         ↑ Manual: message formatting, tool schema, rate limiting,
           retry, response parsing

Before (v4.0 - 迁移中):
  Agent → SessionManager → ClaudeSDKWrapper → query() → Kimi Code API
         ↑ SDK manages: session lifecycle, tool execution,
           response aggregation via ResultMessage

After (v5.0 - 完全移除):
  Agent → SessionManager → ClaudeSDKWrapper → query() → Kimi Code API
         ↑ 完全移除 kimi-agent-sdk，使用纯函数工具
           统一异常体系，无兼容层
```

### 2.2 Layer Design

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: SDK Adapter Layer (NEW)                           │
│  ┌─────────────────────┐  ┌──────────────────────┐         │
│  │  SessionManager     │  │  ClaudeSDKWrapper    │         │
│  │  - single_prompt()   │  │  - execute()          │         │
│  │  - execute_with_tools│  │  - query() wrapper    │         │
│  │  - close()           │  │  - ResultMessage      │         │
│  └─────────────────────┘  └──────────────────────┘         │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Agent Adaptation Layer (MODIFIED)                 │
│  ┌──────────┐  ┌─────────────────┐  ┌───────────────────┐  │
│  │ BaseAgent│  │IndependentAgent │  │ EvaluatorAgent    │  │
│  │ (inject  │  │(SDK query API)  │  │ (single_prompt    │  │
│  │  manager)│  │                 │  │  + thinking mode) │  │
│  └──────────┘  └─────────────────┘  └───────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Key Files

| File | Operation | Purpose |
|------|-----------|---------|
| `docuswarm/llm/session_manager.py` | **NEW** | SessionManager - SDK adapter compatible layer |
| `docuswarm/llm/claude_sdk_wrapper.py` | **NEW** | ClaudeSDKWrapper - query() API wrapper |
| `docuswarm/agents/base.py` | **MODIFY** | Inject SessionManager |
| `docuswarm/agents/independent.py` | **MODIFY** | SDK query() API integration |
| `docuswarm/agents/evaluator.py` | **MODIFY** | single_prompt() API + thinking mode |
| `docuswarm/llm/client.py` | **REMOVE** | KimiClient 已完全移除 |

---

## 3. User Stories

### Story 7.1: SessionManager Implementation

**ID**: US-7.1  
**As a** developer  
**I want to** have a SessionManager that wraps the claude-agent-sdk  
**So that** agents can interact with Kimi K2.5 through the SDK

**Acceptance Criteria**:
- [ ] `SessionManager` class created in `docuswarm/llm/session_manager.py`
- [ ] `single_prompt()` provides one-shot prompt API (for EvaluatorAgent)
- [ ] `execute_with_tools()` provides tool-enabled execution API
- [ ] `close()` cleans up resources
- [ ] Async context manager support
- [ ] `work_dir` and `config` properties for compatibility

**Technical Tasks**:
1. Create `docuswarm/llm/session_manager.py`
2. Implement `single_prompt()` using `ClaudeSDKWrapper.execute()`
3. Implement `execute_with_tools()` with tool description injection
4. Implement resource cleanup
5. Add structured logging with `structlog`
6. Write unit tests with mocked SDK

**API Design**:

```python
class SessionManager:
    def __init__(
        self,
        work_dir: Path | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
    ) -> None: ...

    @property
    def work_dir(self) -> Path: ...

    @property
    def config(self) -> dict[str, Any]: ...

    async def single_prompt(
        self,
        prompt: str,
        mode: str = "agent",
        yolo: bool = True,
        agent_name: str = "docuswarm",
        timeout: float | None = 1800.0,
    ) -> SDKResult: ...

    async def execute_with_tools(
        self,
        prompt: str,
        tools: list[Any] | None = None,
        agent_name: str = "docuswarm",
        timeout: float | None = 1800.0,
    ) -> SDKResult: ...

    async def close(self) -> None: ...
```

**Definition of Done**:
- All methods tested with mocked SDK
- Integration test passes with real Kimi Code API
- Structured logging for all session lifecycle events
- Clean resource cleanup on `close()`

---

### Story 7.2: ClaudeSDKWrapper Implementation

**ID**: US-7.2  
**As a** developer  
**I want to** have a ClaudeSDKWrapper that encapsulates query() API  
**So that** SessionManager can use claude-agent-sdk with Kimi Code API

**Acceptance Criteria**:
- [ ] `ClaudeSDKWrapper` class created in `docuswarm/llm/claude_sdk_wrapper.py`
- [ ] `execute()` method wraps `query()` AsyncGenerator
- [ ] `ResultMessage` extraction for final results
- [ ] Environment variables `ANTHROPIC_BASE_URL` and `ANTHROPIC_API_KEY` supported
- [ ] Error handling for `ResultMessage.is_error`

**Technical Tasks**:
1. Create `docuswarm/llm/claude_sdk_wrapper.py`
2. Define `SDKResult` dataclass
3. Implement `ClaudeSDKWrapper.__init__()` with environment variable support
4. Implement `execute()` with query() integration
5. Implement cancellation and exception handling
6. Write unit tests

**API Design**:

```python
@dataclass
class SDKResult:
    success: bool
    content: str | None
    error: str | None
    duration: float
    messages: list[Any] = field(default_factory=list)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)

class ClaudeSDKWrapper:
    DEFAULT_BASE_URL = "https://api.kimi.com/coding/"
    
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        permission_mode: str = "bypassPermissions",
    ) -> None: ...

    async def execute(
        self,
        prompt: str,
        agent_name: str = "docuswarm",
        timeout: float | None = None,
        cwd: str | Path | None = None,
    ) -> SDKResult: ...
```

**Definition of Done**:
- Wrapper tested with mocked query()
- Environment variable configuration works
- Error cases handled correctly
- Integration test passes with real API

---

### Story 7.3: BaseAgent Adaptation

**ID**: US-7.3  
**As a** developer  
**I want to** update BaseAgent to accept SessionManager  
**So that** all agents use the SDK instead of KimiClient

**Acceptance Criteria**:
- [ ] Constructor accepts `session_manager: SessionManager` parameter
- [ ] `self.session_manager` replaces `self.llm`
- [ ] `execute()` abstract method signature unchanged
- [ ] Structured logging preserved with `structlog`
- [ ] Backward compatibility considered (dual support during transition)

**Technical Tasks**:
1. Modify `docuswarm/agents/base.py` constructor
2. Replace `llm: KimiClient` with `session_manager: SessionManager`
3. Update all property references from `self.llm` to `self.session_manager`
4. Update type hints and imports
5. Update unit tests

**Before/After**:

```python
# Before
class BaseAgent(ABC):
    def __init__(self, config: AgentConfig, llm: KimiClient) -> None:
        self.llm = llm

# After
class BaseAgent(ABC):
    def __init__(self, config: AgentConfig, session_manager: SessionManager) -> None:
        self.session_manager = session_manager
```

**Definition of Done**:
- BaseAgent constructor uses SessionManager
- All subclass instantiation updated
- Type checking passes
- Existing tests updated

---

### Story 7.4: IndependentAgent Adaptation

**ID**: US-7.4  
**As a** developer  
**I want to** update IndependentAgent to use SDK query() API  
**So that** it can leverage automatic tool dispatch via claude-agent-sdk

**Acceptance Criteria**:
- [ ] `_call_llm()` uses `session_manager.execute_with_tools()`
- [ ] Tool descriptions injected into prompt
- [ ] `SDKResult` processed for response content
- [ ] Tool calls extracted from `SDKResult.tool_calls`
- [ ] Exception handling for SDK errors

**Technical Tasks**:
1. Modify `docuswarm/agents/independent.py` `_call_llm()` method
2. Use `session_manager.execute_with_tools()` with tool descriptions
3. Process `SDKResult` for response content
4. Add SDK exception handling
5. Remove manual tool_calls parsing logic
6. Update unit tests

**Implementation Example**:

```python
async def _call_llm(self, prompt: str, tools: list[Any] | None = None) -> str:
    result = await self.session_manager.execute_with_tools(
        prompt=prompt,
        tools=tools,
        agent_name=self.name,
        timeout=1800.0,
    )
    
    if not result.success:
        raise LLMError(f"SDK execution failed: {result.error}")
    
    # Process tool calls if present
    for tool_call in result.tool_calls:
        await self._handle_tool_call(tool_call)
    
    return result.content or ""
```

**Definition of Done**:
- IndependentAgent completes full execution cycle via SDK
- Tools dispatched via SDK
- Exception handling covers SDK exception types
- Integration test passes with real Kimi Code API

---

### Story 7.5: EvaluatorAgent Adaptation

**ID**: US-7.5  
**As a** developer  
**I want to** update EvaluatorAgent to use `single_prompt()` API with thinking mode  
**So that** evaluations leverage SDK's simplified single-shot API

**Acceptance Criteria**:
- [ ] `_call_llm()` uses `session_manager.single_prompt()`
- [ ] Context isolation checks preserved (ContextFilter)
- [ ] Evaluation prompt formatting unchanged
- [ ] Response parsing adapted to SDK `SDKResult` type
- [ ] No tool calling (evaluator is read-only)

**Technical Tasks**:
1. Modify `docuswarm/agents/evaluator.py` `_call_llm()` method
2. Use `session_manager.single_prompt()` instead of `KimiClient.chat()`
3. Adapt response parsing from `ChatResponse` to `SDKResult`
4. Preserve context isolation validation
5. Update unit tests

**Before/After**:

```python
# Before
response = await self.llm.chat(
    messages=eval_messages,
    mode=ChatMode.THINKING,
)
return self._parse_evaluation(response)

# After
result = await self.session_manager.single_prompt(
    prompt=eval_prompt,
    mode="thinking",
    yolo=True,
    agent_name=self.name,
)
if not result.success:
    raise LLMError(f"Evaluation failed: {result.error}")
return self._parse_evaluation(result.content)
```

**Definition of Done**:
- EvaluatorAgent completes evaluation cycle via SDK
- Context isolation fully preserved
- Thinking mode activated correctly
- Response parsing handles SDKResult structure
- Integration test passes

---

### Story 7.6: SDK Exception Handling Integration

**ID**: US-7.6  
**As a** developer  
**I want to** map SDK exceptions to DocuSwarm exception handling  
**So that** errors are handled consistently across the application

**Acceptance Criteria**:
- [ ] SDK exceptions caught in ClaudeSDKWrapper
- [ ] `SDKResult` with `success=False` mapped to `LLMError`
- [ ] `asyncio.CancelledError` handled gracefully
- [ ] Other exceptions caught and wrapped in `SDKResult`
- [ ] Structured logging for all error cases

**Technical Tasks**:
1. Create exception handling in `ClaudeSDKWrapper.execute()`
2. Map SDK result errors to existing DocuSwarm exceptions
3. Implement try/except blocks for all SDK calls
4. Add structured logging for all caught exceptions
5. Write unit tests for exception scenarios

**Exception Mapping**:

```python
try:
    async for message in query(prompt=prompt, options=options):
        messages.append(message)
        if isinstance(message, ResultMessage):
            if message.is_error:
                return SDKResult(
                    success=False,
                    content=None,
                    error=str(message.result),
                    duration=time.time() - start_time,
                    messages=messages,
                )
            else:
                result_content = str(message.result)
                break
except asyncio.CancelledError:
    logger.warning("sdk_execute_cancelled")
    return SDKResult(
        success=False,
        content=None,
        error="Execution cancelled",
        duration=time.time() - start_time,
    )
except Exception as e:
    logger.error("sdk_execute_error", error=str(e))
    return SDKResult(
        success=False,
        content=None,
        error=str(e),
        duration=time.time() - start_time,
    )
```

**Definition of Done**:
- All SDK exceptions mapped to appropriate DocuSwarm exceptions
- No unhandled SDK exceptions can propagate to application level
- Error messages include sufficient context for debugging
- Tests verify all exception paths

---

### Story 7.7: End-to-End Single Node Test

**ID**: US-7.7  
**As a** developer  
**I want to** verify a complete single-node execution through the SDK  
**So that** I have confidence the core transformation works correctly

**Acceptance Criteria**:
- [ ] One BMAD node (e.g., analyst) completes full cycle
- [ ] IndependentAgent creates deliverable via SDK
- [ ] EvaluatorAgent evaluates deliverable via SDK
- [ ] DualAgentNode orchestration works with SDK-adapted agents
- [ ] Results saved to state manager
- [ ] Entire flow logged with structured logging

**Technical Tasks**:
1. Create integration test for single node execution
2. Wire up SessionManager → BaseAgent → IndependentAgent → EvaluatorAgent
3. Execute through DualAgentNode
4. Verify deliverable creation and evaluation
5. Verify state persistence

**Definition of Done**:
- Complete analyst node execution passes end-to-end
- Deliverable created with valid content
- Evaluation returned with score and verdict
- State persisted to SQLite
- No KimiClient code invoked (pure SDK path)

---

## 4. Technical Specifications

### 4.1 New Modules

| Module | Location | Purpose |
|--------|----------|---------|
| `SessionManager` | `docuswarm/llm/session_manager.py` | SDK adapter compatibility layer |
| `ClaudeSDKWrapper` | `docuswarm/llm/claude_sdk_wrapper.py` | query() API wrapper |
| `SDKResult` | `docuswarm/llm/claude_sdk_wrapper.py` | Standardized result dataclass |

### 4.2 Modified Modules

| Module | Location | Changes |
|--------|----------|---------|
| `BaseAgent` | `docuswarm/agents/base.py` | `llm` → `session_manager` injection |
| `IndependentAgent` | `docuswarm/agents/independent.py` | SDK query() API integration |
| `EvaluatorAgent` | `docuswarm/agents/evaluator.py` | `single_prompt()` API + thinking mode |

### 4.3 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_BASE_URL` | `https://api.kimi.com/coding/` | Kimi Code API base URL |
| `ANTHROPIC_API_KEY` | `""` | API key for Kimi Code API |

### 4.4 Quality Gates

| Check | Command | Threshold |
|-------|---------|-----------|
| Type checking | `basedpyright docuswarm/` | Zero errors |
| Linting | `ruff check docuswarm/` | Zero errors |
| Unit tests | `pytest tests/unit/` | 100% pass |
| Integration test | `pytest tests/integration/ -m sdk` | Single node passes |

---

## 5. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| SDK API changes | Medium | High | Pin SDK version, monitor changelog |
| ResultMessage format changes | Low | Medium | Thorough testing with real API responses |
| Session state conflicts with LangGraph checkpoints | Low | Medium | Clear separation of concerns |
| Performance regression | Medium | Low | Benchmark and optimize if needed |
| SDK 完全移除兼容性 | N/A | N/A | 完全移除，无兼容层 |
| Environment variable configuration errors | Medium | High | Clear documentation and validation |

---

## 6. Definition of Done (Epic Level)

- [ ] All 7 stories completed and tested
- [ ] SessionManager fully functional
- [ ] ClaudeSDKWrapper fully functional
- [ ] BaseAgent uses SessionManager
- [ ] IndependentAgent uses SDK query() API
- [ ] EvaluatorAgent uses single_prompt() with thinking mode
- [ ] SDK exceptions mapped to DocuSwarm exceptions
- [ ] Single node end-to-end execution passes
- [ ] Type checking passes
- [ ] Linting passes
- [ ] Unit test coverage ≥80% for new code
- [ ] Environment variables `ANTHROPIC_BASE_URL` and `ANTHROPIC_API_KEY` documented

---

## 7. References

| Document | Location |
|----------|----------|
| SDK Wrapper Epic | `docs/epics/EPIC-16-SDK-WRAPPER.md` |
| SDK Wrapper TDD | `docs/solution/TDD-05-SDKWrapper-Refactor.md` |
| Agent Architecture | `docs/architecture/02_AGENT_ARCHITECTURE.md` |
| LLM Integration | `docs/architecture/05_LLM_INTEGRATION.md` |

---

**Epic End**
