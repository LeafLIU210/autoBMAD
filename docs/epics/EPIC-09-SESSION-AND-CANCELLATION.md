> **⚠️ 已更新**: 本 Epic 已更新为使用 claude-agent-sdk + Kimi Code API 方案。详见 [EPIC-16-SDK-WRAPPER.md](EPIC-16-SDK-WRAPPER.md)。
> 
> **2026-04-05 Session 执行失败修复**: 修复了 `ClaudeSessionWrapper.prompt()` 使用错误 SDK API 的问题，以及 `independent.py` 中 `await session.prompt()` 的语法错误。详见 [Session Execution Failure Solution](../research/session-execution-failure-solution.md) 和 [TDD Plan](../solution/2026-04-05-session-execution-failure-tdd-plan.md)。

# Epic 9: Session Management & Cancellation

**Epic ID**: EPIC-09  
**Version**: 1.1  
**Date**: 2026-03-01  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Phase**: Phase 3 (Session & Cancellation)

---

## 1. Epic Overview

### 1.1 Summary

Implement advanced session management features including Session persistence, hierarchical session tracking, LangGraph checkpoint integration, cancellation via `asyncio.CancelledError`, and the DocuSwarmApprovalHandler for controlled tool approval. This epic leverages claude-agent-sdk's `query()` API and `SafeAsyncGenerator` pattern to enable pipeline interruption, resumption, and graceful cancellation.

### 1.2 Business Value

- **Resilience**: Pipeline can resume after interruption without restarting from scratch
- **User Control**: Native cancellation allows stopping long-running agent execution
- **Security**: Approval handler controls which tool actions are permitted
- **State Coherence**: Dual-layer state management (LangGraph macro + SDK micro) provides complete recovery

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| Session persistence | Session tracking and recovery cycle works |
| Session ID naming | Hierarchical IDs follow naming convention |
| Cancellation | `asyncio.CancelledError` stops execution within 5s |
| Approval handler | Auto-approve safe tools, reject dangerous ones |
| Pipeline resume | Interrupted pipeline resumes from last node |

### 1.4 Dependencies

- **Requires**: Epic 7 (Core Layer Transformation) completed
- **Requires**: Epic 8 (Tool Migration) completed
- **Requires**: Epic 16 (Claude SDK Wrapper) completed
- **Blocks**: Epic 10 (Cleanup & Optimization)

### 1.5 Source Reference

Based on: `docs/solution/TDD-05-SDKWrapper-Refactor.md`

---

## 2. Architecture Context

### 2.1 Dual-Layer State Management

```
┌─────────────────────────────────────────────────────────────────┐
│  LangGraph Checkpoint (SQLite) — Macro State                    │
│  ├── Pipeline global state (PipelineState)                      │
│  ├── Inter-node data (deliverables, questions, evaluations)     │
│  └── DAG execution progress                                     │
├─────────────────────────────────────────────────────────────────┤
│  claude-agent-sdk Session — Micro State                         │
│  ├── Agent ↔ LLM conversation history (via messages)            │
│  ├── Tool call context                                          │
│  └── SafeAsyncGenerator state management                        │
├─────────────────────────────────────────────────────────────────┤
│  Complementary, Not Conflicting:                                │
│    LangGraph → Macro orchestration state                        │
│    SDK query() → Micro conversation state                       │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Session ID Hierarchy

```
Pipeline level:
  pipeline_session_id = "docuswarm-{pipeline_id}"

Node level:
  node_session_id = "docuswarm-{pipeline_id}-{node_id}"

Iteration level (IndependentAgent multi-turn):
  iteration_session_id = "docuswarm-{pipeline_id}-{node_id}-iter{n}"
```

### 2.3 Cancellation Flow

```
External cancel request
  → Cancel task via asyncio
    → SafeAsyncGenerator detects cancellation
      → asyncio.CancelledError raised
        → ClaudeSDKWrapper catches and returns error result
          → Resource cleanup via aclose()
```

### 2.4 Key Files

| File | Operation | Purpose |
|------|-----------|---------|
| `docuswarm/llm/session_manager.py` | **MODIFY** | Session tracking and management |
| `docuswarm/llm/claude_sdk_wrapper.py` | **NEW** | ClaudeSDKWrapper with cancellation support |
| `docuswarm/llm/approval.py` | **NEW** | DocuSwarmApprovalHandler |
| `docuswarm/pipeline/orchestrator.py` | **MODIFY** | Pipeline cancel/resume integration |
| `docuswarm/agents/independent.py` | **MODIFY** | Session ID injection, cancel handling |

---

## 3. User Stories

### Story 9.1: Session Persistence Strategy

**ID**: US-9.1  
**As a** developer  
**I want to** implement hierarchical session ID naming  
**So that** sessions can be uniquely identified and tracked at any level

**Acceptance Criteria**:
- [ ] Session ID generator follows naming convention: `docuswarm-{pipeline_id}-{node_id}[-iter{n}]`
- [ ] Pipeline-level session ID for orchestrator
- [ ] Node-level session ID for each DualAgentNode
- [ ] Iteration-level session ID for IndependentAgent multi-turn
- [ ] Session IDs stored in pipeline state for recovery

**Technical Tasks**:
1. Create session ID generation utility
2. Implement pipeline-level ID: `docuswarm-{pipeline_id}`
3. Implement node-level ID: `docuswarm-{pipeline_id}-{node_id}`
4. Implement iteration-level ID: `docuswarm-{pipeline_id}-{node_id}-iter{n}`
5. Store session IDs in LangGraph PipelineState
6. Write unit tests for ID generation

**Session ID Format**:
```python
def generate_session_id(
    pipeline_id: str,
    node_id: str | None = None,
    iteration: int | None = None,
) -> str:
    parts = [f"docuswarm-{pipeline_id}"]
    if node_id:
        parts.append(node_id)
    if iteration is not None:
        parts.append(f"iter{iteration}")
    return "-".join(parts)
```

**Definition of Done**:
- Session IDs unique and deterministic
- All three levels generate correct format
- IDs stored in pipeline state
- Unit tests pass

---

### Story 9.2: Session State Tracking

**ID**: US-9.2  
**As a** developer  
**I want to** track session state via messages and metadata  
**So that** execution context can be recovered after interruption

**Acceptance Criteria**:
- [ ] `SessionManager` tracks execution via `SDKResult` messages
- [ ] Messages stored for potential recovery
- [ ] Session metadata includes tool call context
- [ ] Failed execution triggers graceful fallback

**Technical Tasks**:
1. Implement message tracking in `SessionManager`
2. Add session metadata storage
3. Implement fallback on execution failure
4. Store execution context for recovery
5. Write integration test for execution cycle

**Execution Flow**:
```python
async def execute_with_tracking(
    self, session_id: str, prompt: str, **kwargs
) -> SDKResult:
    self._logger.info("session_execute_start", session_id=session_id)
    
    result = await self._sdk.execute(
        prompt=prompt,
        agent_name=session_id,
        **kwargs
    )
    
    # Store messages for potential recovery
    self._store_messages(session_id, result.messages)
    
    if not result.success:
        self._logger.warning("session_execute_failed", 
                            session_id=session_id, 
                            error=result.error)
    
    return result
```

**Definition of Done**:
- Session state tracked correctly
- Messages stored for recovery
- Graceful fallback on failure
- Integration test verifies full lifecycle
- Structured logging for all session events

---

### Story 9.3: Pipeline Resume with Session Recovery

**ID**: US-9.3  
**As a** developer  
**I want to** resume an interrupted pipeline from its last node  
**So that** users don't lose progress on long-running orchestrations

**Acceptance Criteria**:
- [ ] Pipeline orchestrator stores current node's session_id in state
- [ ] On resume, retrieves last node from LangGraph checkpoint
- [ ] Attempts session recovery using stored messages
- [ ] Falls back to node restart if recovery not possible
- [ ] Pipeline continues from the interrupted node forward

**Technical Tasks**:
1. Add session_id tracking to PipelineState
2. Implement `resume_pipeline()` in PipelineOrchestrator
3. Integrate LangGraph checkpoint with session recovery
4. Implement node restart fallback
5. Write integration test for pipeline interrupt/resume

**Resume Flow**:
```python
async def resume_pipeline(self, pipeline_id: str) -> None:
    # 1. Get pipeline state from LangGraph checkpoint
    pipeline_state = await self.state_manager.get_pipeline(pipeline_id)
    last_node = pipeline_state["current_node"]

    # 2. Try session recovery with stored messages
    session_id = f"docuswarm-{pipeline_id}-{last_node}"
    messages = self._get_stored_messages(session_id)

    if messages:
        # 3a. Messages exist → continue with context
        result = await self._continue_with_context(session_id, messages, pipeline_state)
    else:
        # 3b. No context → restart node
        result = await self._restart_node(pipeline_id, last_node)
```

**Definition of Done**:
- Pipeline resumes from correct node
- Session recovery preferred over restart
- Fallback to restart works correctly
- State consistency maintained across resume

---

### Story 9.4: Native Cancellation Integration

**ID**: US-9.4  
**As a** developer  
**I want to** cancel running agent execution via asyncio  
**So that** users can stop long-running operations gracefully

**Acceptance Criteria**:
- [ ] `asyncio.CancelledError` properly propagated through SafeAsyncGenerator
- [ ] Cancellation caught in agent execution
- [ ] Cancellation triggers clean resource cleanup via `aclose()`
- [ ] Pipeline state updated to reflect cancellation
- [ ] Partial results preserved where possible

**Technical Tasks**:
1. Implement `cancel_current_node()` in PipelineOrchestrator
2. Track active tasks for cancellation access
3. Handle `asyncio.CancelledError` in IndependentAgent and EvaluatorAgent
4. Update pipeline state on cancellation
5. Write test for cancellation flow

**Cancellation API**:
```python
class PipelineOrchestrator:
    def __init__(self):
        self._active_tasks: dict[str, asyncio.Task] = {}
    
    async def cancel_current_node(self, pipeline_id: str) -> None:
        task = self._active_tasks.get(pipeline_id)
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
```

**Agent-side handling**:
```python
async def execute_with_cancel_handling(
    self, prompt: str, session_id: str
) -> SDKResult:
    try:
        result = await self._sdk.execute(
            prompt=prompt,
            agent_name=session_id,
        )
        return result
    except asyncio.CancelledError:
        self._logger.info("execution_cancelled", session_id=session_id)
        # Ensure generator cleanup
        await self._sdk.aclose()
        return SDKResult(
            success=False,
            content=None,
            error="Execution cancelled",
            duration=0.0,
        )
```

**Definition of Done**:
- Cancellation stops execution within reasonable time
- Resources cleaned up properly via SafeAsyncGenerator
- Pipeline state reflects cancellation
- No orphaned processes

---

### Story 9.5: SafeAsyncGenerator Implementation

**ID**: US-9.5  
**As a** developer  
**I want to** wrap query() AsyncGenerator with SafeAsyncGenerator  
**So that** cancellation and resource cleanup work reliably

**Acceptance Criteria**:
- [ ] `SafeAsyncGenerator` class wraps AsyncIterator from `query()`
- [ ] Proper handling of `StopAsyncIteration`
- [ ] `aclose()` method for resource cleanup
- [ ] Prevention of double-close issues
- [ ] Integration with cancellation flow

**Technical Tasks**:
1. Create `SafeAsyncGenerator` class
2. Implement `__aiter__` and `__anext__` methods
3. Implement `aclose()` for cleanup
4. Integrate with ClaudeSDKWrapper
5. Write tests for generator lifecycle

**Implementation**:
```python
class SafeAsyncGenerator:
    """Wrapper for query() AsyncGenerator to handle cancellation safely."""
    
    def __init__(self, generator: AsyncIterator[Any]) -> None:
        self._generator = generator
        self._closed = False
        self._logger = logger.bind(component="SafeAsyncGenerator")
    
    def __aiter__(self) -> SafeAsyncGenerator:
        return self
    
    async def __anext__(self) -> Any:
        if self._closed:
            raise StopAsyncIteration
        try:
            return await self._generator.__anext__()
        except StopAsyncIteration:
            self._closed = True
            raise
    
    async def aclose(self) -> None:
        """Close the generator and cleanup resources."""
        if not self._closed:
            self._closed = True
            try:
                await self._generator.aclose()
            except Exception as e:
                self._logger.warning("generator_close_error", error=str(e))


# Usage in ClaudeSDKWrapper
async def execute(self, prompt: str, **kwargs) -> SDKResult:
    start_time = time.time()
    
    try:
        # Wrap query() in SafeAsyncGenerator
        raw_generator = query(prompt=prompt, options=options)
        safe_gen = SafeAsyncGenerator(raw_generator)
        
        messages: list[Any] = []
        result_content: str | None = None
        
        async for message in safe_gen:
            messages.append(message)
            if isinstance(message, ResultMessage):
                result_content = str(message.result)
                break
        
        await safe_gen.aclose()
        
        return SDKResult(
            success=result_content is not None,
            content=result_content,
            error=None if result_content else "No result received",
            duration=time.time() - start_time,
            messages=messages,
        )
        
    except asyncio.CancelledError:
        await safe_gen.aclose()
        raise
```

**Definition of Done**:
- SafeAsyncGenerator correctly wraps query()
- Cancellation handled properly
- Resources cleaned up on close
- Double-close prevented
- Tests cover all lifecycle scenarios

---

### Story 9.6: DocuSwarmApprovalHandler

**ID**: US-9.6  
**As a** developer  
**I want to** have a configurable approval handler for SDK tool calls  
**So that** dangerous operations are blocked while safe operations proceed automatically

**Acceptance Criteria**:
- [ ] `DocuSwarmApprovalHandler` class in `docuswarm/llm/approval.py`
- [ ] Auto-approve list: `create_deliverable`, `update_context`, `read_file`
- [ ] Reject list: `write_file`, `execute_command`, `delete_file`
- [ ] Unknown actions: approve single (conservative policy)
- [ ] `auto_approve_all` flag for yolo mode
- [ ] Handler integrated with ClaudeSDKWrapper via permission_mode

**Technical Tasks**:
1. Create `docuswarm/llm/approval.py`
2. Implement `DocuSwarmApprovalHandler` with action lists
3. Implement approval callback method
4. Register handler with SessionManager
5. Write unit tests for all approval paths

**Implementation**:
```python
class DocuSwarmApprovalHandler:
    AUTO_APPROVE_ACTIONS = {"create_deliverable", "update_context", "read_file"}
    REJECT_ACTIONS = {"write_file", "execute_command", "delete_file"}

    def __init__(self, auto_approve_all: bool = False):
        self._auto_approve_all = auto_approve_all

    def should_approve(self, action: str, **kwargs) -> bool:
        """Determine if action should be approved."""
        if self._auto_approve_all:
            return True
        
        if action in self.AUTO_APPROVE_ACTIONS:
            return True
        elif action in self.REJECT_ACTIONS:
            return False
        else:
            return True  # Unknown → approve single (conservative)
    
    def get_permission_mode(self) -> str:
        """Return permission mode for SDK."""
        return "bypassPermissions" if self._auto_approve_all else "promptForPermissions"
```

**Definition of Done**:
- Approval handler correctly routes all known actions
- Safe actions auto-approved
- Dangerous actions rejected
- Unknown actions handled with conservative policy
- Unit tests cover all branches

---

### Story 9.7: Session & Cancellation Integration Test

**ID**: US-9.7  
**As a** developer  
**I want to** verify the complete session lifecycle and cancellation flow  
**So that** I have confidence in production readiness

**Acceptance Criteria**:
- [ ] Test: Session tracking during execute cycle
- [ ] Test: Cancellation during active query()
- [ ] Test: SafeAsyncGenerator cleanup on cancel
- [ ] Test: Pipeline resume after interruption
- [ ] Test: Approval handler blocks dangerous operations
- [ ] All tests pass with real Kimi Code API

**Technical Tasks**:
1. Create `tests/integration/test_session_lifecycle.py`
2. Implement session tracking test
3. Implement cancellation test (async cancel during query)
4. Implement SafeAsyncGenerator cleanup test
5. Implement pipeline resume test
6. Implement approval handler integration test

**Definition of Done**:
- All integration tests pass
- Session tracking verified end-to-end
- Cancellation works reliably with SafeAsyncGenerator
- Pipeline resume produces correct results
- Approval handler integrated with real SDK

---

## 4. Technical Specifications

### 4.1 New Modules

| Module | Location | Purpose |
|--------|----------|---------|
| `ClaudeSDKWrapper` | `docuswarm/llm/claude_sdk_wrapper.py` | SDK wrapper with cancellation |
| `SafeAsyncGenerator` | `docuswarm/llm/claude_sdk_wrapper.py` | Safe generator wrapper |
| `DocuSwarmApprovalHandler` | `docuswarm/llm/approval.py` | Tool approval strategy |
| Session ID utility | `docuswarm/utils/session_ids.py` | Hierarchical ID generation |

### 4.2 Modified Modules

| Module | Location | Changes |
|--------|----------|---------|
| `SessionManager` | `docuswarm/llm/session_manager.py` | Use ClaudeSDKWrapper, tracking |
| `PipelineOrchestrator` | `docuswarm/pipeline/orchestrator.py` | Cancel, resume pipeline |
| `IndependentAgent` | `docuswarm/agents/independent.py` | Session ID injection, cancel handling |

### 4.3 API Changes

#### From kimi-agent-sdk to claude-agent-sdk

| Original | New | Notes |
|----------|-----|-------|
| `Session.create()` | `query()` | Function-based API |
| `Session.resume()` | Message replay | Via stored messages |
| `session.cancel()` | `asyncio.CancelledError` | Standard Python cancellation |
| `session.prompt()` | `query()` + SafeAsyncGenerator | AsyncGenerator pattern |
| Wire Protocol | Direct message handling | Simplified architecture |
| `MessageAggregator` | `ResultMessage` extraction | Direct result handling |

### 4.4 Quality Gates

| Check | Command | Threshold |
|-------|---------|-----------|
| Type checking | `basedpyright docuswarm/` | Zero errors |
| Linting | `ruff check docuswarm/` | Zero errors |
| Unit tests | `pytest tests/unit/` | 100% pass |
| Integration | `pytest tests/integration/test_session_lifecycle.py` | Pass |

---

## 5. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| SDK message storage conflicts with project work_dir | Low | Medium | Configure isolated work_dir |
| Session recovery loses tool context | Medium | High | Verify tool state in messages |
| Cancellation leaves process orphaned | Low | Medium | SafeAsyncGenerator aclose() |
| LangGraph + SDK dual checkpoint complexity | Medium | Medium | Clear separation of concerns |
| Approval handler too restrictive | Low | Low | Configurable action lists |

---

## 6. Definition of Done (Epic Level)

- [ ] All 7 stories completed and tested
- [ ] Session tracking fully functional
- [ ] SafeAsyncGenerator implemented and tested
- [ ] Hierarchical session ID naming working
- [ ] Pipeline can resume after interruption
- [ ] `asyncio.CancelledError` stops execution cleanly
- [ ] DocuSwarmApprovalHandler controls tool access
- [ ] Integration tests pass end-to-end
- [ ] Type checking passes
- [ ] Linting passes

---

## 7. References

| Document | Location |
|----------|----------|
| SDK Wrapper TDD | `docs/solution/TDD-05-SDKWrapper-Refactor.md` |
| Epic 16 | `docs/epics/EPIC-16-SDK-WRAPPER.md` |
| Pipeline Architecture | `docs/architecture/03_PIPELINE_ARCHITECTURE.md` |

---

**Epic End**
