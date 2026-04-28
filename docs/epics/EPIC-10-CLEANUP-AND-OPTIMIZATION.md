> **⚠️ 已更新**: 本 Epic 已更新为使用 claude-agent-sdk + Kimi Code API 方案。详见 [EPIC-16-SDK-WRAPPER.md](EPIC-16-SDK-WRAPPER.md)。

# Epic 10: Cleanup & Optimization

**Epic ID**: EPIC-10  
**Version**: 1.1  
**Date**: 2026-03-01  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Phase**: Phase 4 (Cleanup & Optimization)

---

## 1. Epic Overview

### 1.1 Summary

Remove all legacy KimiClient code and related modules, evaluate and decide on TokenBucketRateLimiter and RetryHandler retention, update `pyproject.toml` dependencies, migrate all tests to SDK-based patterns, and perform final documentation updates. This epic concludes the claude-agent-sdk transformation with a clean, fully-migrated codebase.

### 1.2 Business Value

- **Clean Codebase**: No dead code or dual-path confusion
- **Reduced Dependencies**: Remove httpx and langchain-openai if no longer needed
- **Test Reliability**: All tests use SDK mocking patterns
- **Documentation Accuracy**: All docs reflect final SDK architecture
- **Maintenance Efficiency**: Single LLM integration path to maintain

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| Legacy removal | Zero references to KimiClient in production code |
| Dependency cleanup | httpx removed if only used by KimiClient |
| Test migration | All tests use SDK types and mocking |
| Documentation | All architecture docs reflect SDK integration |
| Full pipeline | Complete 5-node BMAD pipeline passes end-to-end |

### 1.4 Dependencies

- **Requires**: Epic 7 (Core Layer), Epic 8 (Tools), Epic 9 (Session & Cancel), Epic 16 (SDK Wrapper) all completed
- **Blocks**: None (final migration epic)

### 1.5 Source Reference

Based on: `docs/solution/TDD-05-SDKWrapper-Refactor.md`

---

## 2. Architecture Context

### 2.1 Final Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                DocuSwarm Application (Post-Migration)            │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                     │
│  │ Analyst  │  │   PM     │  │   UX     │ ...  ← BMAD Nodes   │
│  │  Node    │  │  Node    │  │  Node    │                     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                     │
│       │              │              │                           │
│  ┌────▼──────────────▼──────────────▼─────┐                     │
│  │         DualAgentNode                  │  ← Dual-Agent       │
│  │  ┌─────────────┐  ┌─────────────┐     │                     │
│  │  │Independent  │  │ Evaluator   │     │                     │
│  │  │   Agent     │  │   Agent     │     │                     │
│  │  └──────┬──────┘  └──────┬──────┘     │                     │
│  └─────────┼────────────────┼────────────┘                     │
│            │                │                                   │
│  ┌─────────▼────────────────▼────────────┐                     │
│  │      SessionManager                   │  ← SDK Adapter      │
│  │  ┌────────────┐  ┌────────────────┐   │                     │
│  │  │  Claude    │  │   single_prompt│   │                     │
│  │  │SDKWrapper  │  │  (single-shot) │   │                     │
│  │  └────────────┘  └────────────────┘   │                     │
│  │  ┌────────────┐  ┌────────────────┐   │                     │
│  │  │  execute   │  │   execute_with │   │                     │
│  │  │  method    │  │   tools        │   │                     │
│  │  └────────────┘  └────────────────┘   │                     │
│  └───────────────────────────────────────┘                     │
│                      │                                          │
└──────────────────────┼──────────────────────────────────────────┘
                       │
              ┌────────▼────────┐
              │ claude-agent-sdk│
              │  (query/Wire)   │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │  Kimi Code API  │
              │ (OpenAI-compat) │
              └─────────────────┘
```

### 2.2 Files to Remove

| File | Reason |
|------|--------|
| `docuswarm/llm/client.py` | KimiClient replaced by SessionManager |
| `docuswarm/llm/tools.py` | JSON Schema tools replaced by claude-agent-sdk Tool Use Block |
| `docuswarm/llm/kimi_session_manager.py` | Replaced by claude-agent-sdk based SessionManager |

### 2.3 Files to Evaluate

| File | Decision Criteria |
|------|-------------------|
| `docuswarm/llm/rate_limit.py` | Remove - claude-agent-sdk handles rate limiting internally |
| `docuswarm/llm/retry.py` | Remove - claude-agent-sdk handles retries internally |

---

## 3. User Stories

### Story 10.1: Remove KimiClient Module

**ID**: US-10.1  
**As a** developer  
**I want to** remove the KimiClient module and all references  
**So that** there is a single LLM integration path through the SDK

**Acceptance Criteria**:
- [ ] `docuswarm/llm/client.py` deleted
- [ ] All imports of `KimiClient` removed from codebase
- [ ] All instantiations of `KimiClient` removed
- [ ] No production code references `KimiClient` or `client.py`
- [ ] `ChatResponse` data class removed or migrated

**Technical Tasks**:
1. Search for all `KimiClient` references: `grep -r "KimiClient" docuswarm/`
2. Search for all `client.py` imports: `grep -r "from docuswarm.llm.client" docuswarm/`
3. Remove `docuswarm/llm/client.py`
4. Remove `ChatResponse` class (or migrate if used elsewhere)
5. Update `docuswarm/llm/__init__.py` exports
6. Run type checking and fix all errors

**Definition of Done**:
- `grep -r "KimiClient" docuswarm/` returns no results
- `grep -r "ChatResponse" docuswarm/` returns no production code results
- Type checking passes
- All tests pass

---

### Story 10.2: Remove Legacy Session Manager

**ID**: US-10.2  
**As a** developer  
**I want to** remove the legacy KimiSessionManager  
**So that** only the claude-agent-sdk based SessionManager remains

**Acceptance Criteria**:
- [ ] `docuswarm/llm/kimi_session_manager.py` deleted (if exists)
- [ ] All imports of `KimiSessionManager` removed from codebase
- [ ] All references updated to use new `SessionManager` from Epic 16
- [ ] No dual-path confusion in codebase

**Technical Tasks**:
1. Search for all `KimiSessionManager` references: `grep -r "KimiSessionManager" docuswarm/`
2. Remove `docuswarm/llm/kimi_session_manager.py` (if exists)
3. Update all imports to use new `SessionManager`
4. Verify `SessionManager` from Epic 16 is the only implementation

**Definition of Done**:
- `grep -r "KimiSessionManager" docuswarm/` returns no results
- Only `SessionManager` from Epic 16 is used
- All tests pass

---

### Story 10.3: Remove Rate Limiter and Retry Handler

**ID**: US-10.3  
**As a** developer  
**I want to** remove the custom rate limiter and retry handler  
**So that** rate limiting and retries are handled by claude-agent-sdk

**Acceptance Criteria**:
- [ ] `docuswarm/llm/rate_limit.py` deleted
- [ ] `docuswarm/llm/retry.py` deleted
- [ ] All references cleaned up
- [ ] claude-agent-sdk internal handling verified

**Technical Tasks**:
1. Verify claude-agent-sdk handles rate limiting internally
2. Verify claude-agent-sdk handles retries internally
3. Delete `docuswarm/llm/rate_limit.py`
4. Delete `docuswarm/llm/retry.py`
5. Clean up all references

**Definition of Done**:
- Rate limiter and retry handler files removed
- No conflicting rate limiting or retry behavior
- System works correctly with SDK internal handling

---

### Story 10.4: Update pyproject.toml Dependencies

**ID**: US-10.4  
**As a** developer  
**I want to** clean up project dependencies to reflect the SDK migration  
**So that** only necessary packages are installed

**Acceptance Criteria**:
- [ ] `claude-agent-sdk` is primary LLM dependency
- [x] `kimi-agent-sdk` **completely removed** (zero backward compatibility)
- [ ] `httpx` removed if only used by KimiClient
- [ ] `langchain-openai` removed if no longer needed
- [ ] All retained dependencies have correct version pins
- [ ] `pip install -e .` succeeds with clean environment

**Technical Tasks**:
1. Audit all imports to identify unused dependencies
2. **Completely remove** `kimi-agent-sdk` (no compatibility layer)
3. Remove `httpx` if only used by `client.py`
4. Evaluate `langchain-openai` usage (LangGraph may still need it)
5. Update version pins for retained dependencies
6. Test clean install in fresh virtual environment

**Final Dependencies**:
```toml
[project.dependencies]
# Core
claude-agent-sdk = ">=0.1.0"
langgraph = ">=0.2.0"
langchain-core = ">=0.2.0"

# Data
pydantic = ">=2.0.0"

# CLI
click = ">=8.1.0"
rich = ">=13.0.0"

# Config
python-dotenv = ">=1.0.0"
pyyaml = ">=6.0.0"

# Logging
structlog = ">=24.0.0"

# Async
aiofiles = ">=23.0.0"

# Removed:
# kimi-agent-sdk = ">=0.0.5"   → ✅ Completely removed, replaced by claude-agent-sdk
# httpx = ">=0.27.0"          → Remove if only KimiClient used it
# langchain-openai = ">=0.1.0" → Remove if LangGraph doesn't need it
```

**Environment Variables**:
```bash
# claude-agent-sdk + Kimi Code API configuration
ANTHROPIC_BASE_URL=https://api.kimi.com/coding/
ANTHROPIC_API_KEY=<your-kimi-api-key>
```

**Definition of Done**:
- `pip install -e .` succeeds in fresh venv
- No unused dependencies remain
- Application fully functional with updated deps

---

### Story 10.5: Migrate All Tests to SDK Patterns

**ID**: US-10.5  
**As a** developer  
**I want to** update all tests to use SDK types and mocking  
**So that** the test suite validates the actual production code paths

**Acceptance Criteria**:
- [ ] All `mock_llm_client` fixtures replaced with `mock_session_manager`
- [ ] Test assertions use SDK types instead of `ChatResponse`
- [ ] SDK exceptions used in error path tests
- [ ] Integration tests use real SDK (with API key)
- [ ] Unit tests use mocked SDK (no API key needed)
- [ ] Test coverage ≥80% for all SDK-related modules

**Technical Tasks**:
1. Audit all test files for `KimiClient` / `ChatResponse` references
2. Replace `mock_llm_client` fixtures with `mock_session_manager`
3. Update assertion types from `ChatResponse` to `SDKResult`
4. Update error tests to use SDK exceptions
5. Verify all tests pass
6. Run coverage report

**Mock Pattern Update**:
```python
# Before
@pytest.fixture
def mock_llm_client():
    client = AsyncMock(spec=KimiClient)
    client.chat.return_value = ChatResponse(content="test", ...)
    return client

# After
@pytest.fixture
def mock_session_manager():
    manager = AsyncMock(spec=SessionManager)
    manager.single_prompt.return_value = SDKResult(
        success=True,
        content="test",
        error=None,
        duration=1.0,
        messages=[],
        tool_calls=[]
    )
    manager.execute_with_tools.return_value = SDKResult(...)
    return manager
```

**Definition of Done**:
- `pytest -v --tb=short` — all tests pass
- `pytest --cov=docuswarm` — coverage ≥80%
- No references to `KimiClient` or `ChatResponse` in test code
- Mock patterns use SDK types

---

### Story 10.6: Full Pipeline End-to-End Validation

**ID**: US-10.6  
**As a** developer  
**I want to** run a complete 5-node BMAD pipeline through the SDK  
**So that** I can verify the entire system works end-to-end post-migration

**Acceptance Criteria**:
- [ ] All 5 BMAD nodes (analyst, pm, ux, architect, po) execute via SDK
- [ ] Each node creates deliverable and receives evaluation
- [ ] Context chaining works across nodes
- [ ] Pipeline state persisted to SQLite
- [ ] LangGraph orchestration functions correctly
- [ ] No KimiClient code paths executed

**Technical Tasks**:
1. Create full pipeline integration test
2. Execute all 5 nodes sequentially
3. Verify deliverables created for each node
4. Verify evaluations returned for each node
5. Verify context chaining across nodes
6. Verify state persistence and recovery

**Definition of Done**:
- Complete pipeline execution succeeds
- All 5 node deliverables present and valid
- All evaluations scored and consistent
- State fully persisted and recoverable
- Zero legacy code paths executed

---

### Story 10.7: Final Documentation Update

**ID**: US-10.7  
**As a** developer  
**I want to** ensure all documentation reflects the final SDK architecture  
**So that** new developers understand the current system correctly

**Acceptance Criteria**:
- [ ] `docs/architecture/` documents accurate for claude-agent-sdk architecture
- [ ] `docs/analyst/` documents reflect SDK terminology
- [ ] `CLAUDE.md` technology stack section updated if needed
- [ ] Code comments in SDK modules are accurate
- [ ] Inline references to KimiClient/KimiSessionManager removed from all docs
- [ ] References to EPIC-16 for SDK details added

**Technical Tasks**:
1. Grep all docs for remaining `KimiClient` / `KimiSessionManager` / `kimi-agent-sdk` references
2. Update any remaining references to SDK equivalents
3. Verify architecture diagrams in docs match implementation
4. Update CLAUDE.md if technology stack changed
5. Add references to EPIC-16 for SDK implementation details
6. Final documentation review

**Definition of Done**:
- `grep -r "KimiClient" docs/` returns no results (except historical references)
- `grep -r "kimi-agent-sdk" docs/` returns no results (except historical references)
- All architecture diagrams match implementation
- Documentation reviewed and accurate

---

## 4. Technical Specifications

### 4.1 Removed Modules

| Module | Location | Replacement |
|--------|----------|-------------|
| `KimiClient` | `docuswarm/llm/client.py` | `SessionManager` (from Epic 16) |
| `ChatResponse` | `docuswarm/llm/client.py` | `SDKResult` type |
| `KimiSessionManager` | `docuswarm/llm/kimi_session_manager.py` | ✅ **Completely removed** |
| JSON Schema tools | `docuswarm/llm/tools.py` | claude-agent-sdk Tool Use Block |
| `TokenBucketRateLimiter` | `docuswarm/llm/rate_limit.py` | claude-agent-sdk internal handling |
| `RetryHandler` | `docuswarm/llm/retry.py` | claude-agent-sdk internal handling |

### 4.2 New/Updated Modules (from Epic 16)

| Module | Location | Purpose |
|--------|----------|---------|
| `ClaudeSDKWrapper` | `llm/claude_sdk_wrapper.py` | claude-agent-sdk wrapper |
| `SessionManager` | `llm/session_manager.py` | Compatible session manager |
| `SDKResult` | `llm/claude_sdk_wrapper.py` | Standardized result type |

### 4.3 Quality Gates

| Check | Command | Threshold |
|-------|---------|-----------|
| Type checking | `basedpyright docuswarm/` | Zero errors |
| Linting | `ruff check docuswarm/` | Zero errors |
| Unit tests | `pytest tests/unit/` | 100% pass |
| Coverage | `pytest --cov=docuswarm` | ≥80% |
| Integration | `pytest tests/integration/` | Full pipeline pass |
| Legacy check | `grep -r "KimiClient" docuswarm/` | No matches |
| SDK check | `grep -r "kimi-agent-sdk" docuswarm/` | No matches (except imports) |

---

## 5. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| SDK compatibility issues | Low | High | Epic 16 provides compatible wrapper layer |
| Environment variable configuration | Medium | High | Clear documentation of ANTHROPIC_* variables |
| Removing rate limiter causes issues | Low | Medium | claude-agent-sdk handles internally |
| httpx used by other modules besides KimiClient | Low | Low | Thorough import audit before removal |
| Test migration introduces coverage gaps | Medium | Medium | Run coverage report, fill gaps |
| Full pipeline test reveals edge cases | Medium | High | Run against multiple context inputs |

---

## 6. Definition of Done (Epic Level)

- [ ] All 7 stories completed and tested
- [ ] `KimiClient`, `KimiSessionManager` and all legacy LLM code removed
- [ ] Rate limiter and retry handler removed (SDK handles internally)
- [x] `pyproject.toml` dependencies cleaned up (**kimi-agent-sdk completely removed**)
- [ ] All tests migrated to claude-agent-sdk patterns
- [ ] Full 5-node pipeline passes end-to-end
- [ ] Documentation fully updated
- [ ] Type checking passes
- [ ] Linting passes
- [ ] Test coverage ≥80%
- [ ] **claude-agent-sdk + Kimi Code API migration complete**

---

## 7. References

| Document | Location |
|----------|----------|
| SDK Wrapper Epic | `docs/epics/EPIC-16-SDK-WRAPPER.md` |
| SDK Wrapper TDD | `docs/solution/TDD-05-SDKWrapper-Refactor.md` |
| System Architecture | `docs/architecture/01_SYSTEM_ARCHITECTURE.md` |

---

**Epic End**
