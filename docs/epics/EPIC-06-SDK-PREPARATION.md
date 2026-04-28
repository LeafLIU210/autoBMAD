> **⚠️ 已废弃**: 本 Epic 已被 [EPIC-16-SDK-WRAPPER.md](EPIC-16-SDK-WRAPPER.md) 替代。项目统一使用 claude-agent-sdk + Kimi Code API 方案。

# Epic 6: Claude SDK Preparation & Environment Setup

**Epic ID**: EPIC-06  
**Version**: 1.0  
**Date**: 2026-02-20  
**Status**: Deprecated (被 EPIC-16 替代)  
**Owner**: Tech Lead  
**Phase**: Phase 0 (Preparation)

---

## 1. Epic Overview

### 1.1 Summary

准备 claude-agent-sdk 环境，通过 Kimi Code API 的 OpenAI 兼容接口工作。安装 SDK 及其依赖，验证 API 连通性，创建集成冒烟测试，并备份现有 KimiClient 代码。本 Epic 在实施 EPIC-16 前建立 SDK 基础。

**关键配置**:
- `ANTHROPIC_BASE_URL=https://api.kimi.com/coding/`
- `ANTHROPIC_API_KEY=<your-kimi-api-key>`

### 1.2 Business Value

- **Risk Reduction**: Validates SDK compatibility before committing to migration
- **Environment Readiness**: Ensures all developers have working SDK setup
- **Rollback Safety**: Backup of existing code enables safe migration
- **Fast Feedback**: Smoke tests catch SDK issues early

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| SDK installed | `import claude_agent_sdk` succeeds |
| API connectivity | Connection to Kimi Code API verified |
| Smoke test passes | `query()` returns ResultMessage |
| Backup created | KimiClient code branch preserved |

### 1.4 Dependencies

- **Requires**: Epic 1 (Core Infrastructure) completed
- **Requires**: Python 3.12+ (currently 3.14+, satisfied)
- **Blocks**: Epic 7 (Core Layer Transformation)

### 1.5 Source Reference

基于 EPIC-16 方案：`docs/epics/EPIC-16-SDK-WRAPPER.md`

---

## 2. Architecture Context

### 2.1 SDK Dependency Chain

```
claude-agent-sdk
├── OpenAI 兼容 API                  # Kimi Code API
└── 标准 Tool Use Block              # 工具调用格式
```

### 2.2 API Architecture

```
┌──────────────────┐     ┌──────────────────────┐     ┌──────────────┐
│  claude-agent-   │────>│  ANTHROPIC_BASE_URL  │────>│  Kimi Code   │
│  sdk             │     │  (OpenAI 兼容接口)    │     │  API Backend │
│  (Python SDK)    │<────│  Kimi Code API       │<────│              │
└──────────────────┘     └──────────────────────┘     └──────────────┘
     query() API          OpenAI Compatible API        Kimi K2.5
```

### 2.3 Key Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Add claude-agent-sdk dependency |
| `tests/integration/test_sdk_smoke.py` | SDK connectivity smoke test |
| `docuswarm/llm/client.py` | Existing KimiClient (to be backed up) |

---

## 3. User Stories

### Story 6.1: Install claude-agent-sdk Dependencies

**ID**: US-6.1  
**As a** developer  
**I want to** have claude-agent-sdk and its dependencies installed  
**So that** I can use the SDK's query API in the project

**Acceptance Criteria**:
- [ ] `claude-agent-sdk` added to `pyproject.toml` dependencies
- [ ] `import claude_agent_sdk` succeeds in Python REPL
- [ ] Version pins: `claude-agent-sdk>=0.1.0`
- [ ] `httpx` dependency retained (may still be needed for non-SDK calls)

**Technical Tasks**:
1. Add `claude-agent-sdk>=0.1.0` to `pyproject.toml` `[project.dependencies]`
2. Run `pip install -e .` to install SDK and deps
3. Update `requirements.txt` if applicable

**pyproject.toml Changes**:
```toml
[project.dependencies]
# New
claude-agent-sdk = ">=0.1.0"

# Retained
langgraph = ">=0.2.0"
pydantic = ">=2.0.0"
structlog = ">=24.0.0"

# Evaluate for removal in Phase 4
# httpx = ">=0.27.0"
# langchain-openai = ">=0.1.0"
```

**Definition of Done**:
- All SDK imports resolve without errors
- `from claude_agent_sdk import query, ClaudeAgentOptions` succeeds
- Development environment fully functional

---

### Story 6.2: Verify API Connectivity

**ID**: US-6.2  
**As a** developer  
**I want to** verify Kimi Code API connectivity works in the project environment  
**So that** I know the SDK can communicate with Kimi backend

**Acceptance Criteria**:
- [ ] API connection test succeeds
- [ ] OpenAI compatible endpoint responds correctly
- [ ] No firewall or proxy issues blocking API communication
- [ ] Environment variables (`ANTHROPIC_API_KEY`) are accessible

**Technical Tasks**:
1. Set `ANTHROPIC_BASE_URL=https://api.kimi.com/coding/`
2. Set `ANTHROPIC_API_KEY` environment variable
3. Test basic API connectivity with simple prompt
4. Document any environment-specific configuration needs

**Definition of Done**:
- API connection verified with Kimi Code API backend
- Query messages flow correctly between SDK and API
- No connectivity errors in test environment

---

### Story 6.3: Create SDK Integration Smoke Test

**ID**: US-6.3  
**As a** developer  
**I want to** have a smoke test that verifies basic SDK functionality  
**So that** I can quickly validate SDK setup on any environment

**Acceptance Criteria**:
- [ ] Smoke test uses `query()` high-level API
- [ ] Test sends "Hello" and verifies ResultMessage response
- [ ] Test validates ResultMessage structure (result, is_error)
- [ ] Test runs with `pytest -m smoke` marker
- [ ] Test uses `permission_mode="bypassPermissions"` for automatic approval

**Technical Tasks**:
1. Create `tests/integration/test_sdk_smoke.py`
2. Implement basic `query()` test
3. Implement `ClaudeAgentOptions` configuration test
4. Add `@pytest.mark.smoke` marker
5. Add `@pytest.mark.integration` marker (requires API key)

**Smoke Test Design**:
```python
import pytest
import os
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

@pytest.mark.smoke
@pytest.mark.integration
async def test_query_basic():
    """Verify basic query() API returns ResultMessage."""
    os.environ["ANTHROPIC_BASE_URL"] = "https://api.kimi.com/coding/"
    os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY", "")
    
    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        cwd=str(Path.cwd()),
    )
    
    messages = []
    async for msg in query("Say hello in one word", options=options):
        messages.append(msg)
        if isinstance(msg, ResultMessage):
            assert not msg.is_error
            assert msg.result is not None
    
    assert len(messages) > 0
    assert any(isinstance(m, ResultMessage) for m in messages)

@pytest.mark.smoke
@pytest.mark.integration
async def test_query_lifecycle():
    """Verify query lifecycle with ResultMessage extraction."""
    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        cwd=str(Path.cwd()),
    )
    
    result_content = None
    async for message in query("What is 1+1?", options=options):
        if isinstance(message, ResultMessage):
            if not message.is_error:
                result_content = str(message.result)
            break
    
    assert result_content is not None
```

**Definition of Done**:
- `pytest tests/integration/test_sdk_smoke.py -m smoke` passes
- Test clearly reports SDK version in output
- Test fails gracefully with clear message if API key missing

---

### Story 6.4: Backup Existing KimiClient Code

**ID**: US-6.4  
**As a** developer  
**I want to** have the existing KimiClient code preserved  
**So that** I can rollback if the SDK migration encounters issues

**Acceptance Criteria**:
- [ ] Git branch `backup/pre-sdk-migration` created
- [ ] All `docuswarm/llm/` files preserved in backup
- [ ] Backup includes `docuswarm/agents/` files
- [ ] Backup tag created for easy reference

**Technical Tasks**:
1. Create git branch `backup/pre-sdk-migration` from current state
2. Tag the branch as `v-pre-sdk-migration`
3. Document backup location in migration notes
4. Verify backup branch contains all relevant files

**Definition of Done**:
- Git branch exists with pre-migration code
- Tag is accessible via `git checkout v-pre-sdk-migration`
- All team members aware of backup location

---

### Story 6.5: SDK Type System Exploration

**ID**: US-6.5  
**As a** developer  
**I want to** understand the SDK's type system (ResultMessage, ClaudeAgentOptions)  
**So that** I can design the adapter layer correctly in Phase 1

**Acceptance Criteria**:
- [ ] SDK type hierarchy documented
- [ ] Mapping between existing `ChatResponse` and SDK types identified
- [ ] `ResultMessage` structure (result, is_error) understood
- [ ] Tool Use Block pattern documented
- [ ] SDK exception hierarchy mapped to existing exceptions

**Technical Tasks**:
1. Explore `claude_agent_sdk` package structure and exports
2. Document `ResultMessage` fields and methods
3. Document `ClaudeAgentOptions` configuration options
4. Map `ChatResponse` fields to SDK equivalents
5. Document SDK exception hierarchy

**Type Mapping**:
```
Existing ChatResponse           →  SDK ResultMessage
  .content                      →  .result (str)
  .usage.total_tokens          →  (API-level metadata)
  .model                        →  (Config-level)
  .finish_reason                →  (消息类型区分)

Existing Exception              →  SDK Exception
  HTTP 429                      →  APIStatusError
  HTTP timeout                  →  APITimeoutError
  HTTP 5xx                      →  APIStatusError
  Connection error              →  APIConnectionError
  Empty response                →  APIEmptyResponseError
  (new) Cancel                  →  RunCancelled
  (new) Step limit              →  MaxStepsReached
  (new) Config error            →  ConfigError
  (new) Tool error              →  InvalidToolError
```

**Definition of Done**:
- Type mapping document available for Phase 1 development
- All SDK public types documented with usage examples
- Exception mapping complete

---

## 4. Technical Specifications

### 4.1 Dependency Changes

```toml
# pyproject.toml additions
[project.dependencies]
claude-agent-sdk = ">=0.1.0"
```

### 4.2 Environment Requirements

| Requirement | Value |
|-------------|-------|
| Python | >=3.12 (project uses 3.14+) |
| claude-agent-sdk | >=0.1.0 |
| API Base URL | `ANTHROPIC_BASE_URL=https://api.kimi.com/coding/` |
| API Key | `ANTHROPIC_API_KEY` environment variable |

### 4.3 Quality Gates

| Check | Command | Threshold |
|-------|---------|-----------|
| SDK Import | `python -c "import claude_agent_sdk"` | Success |
| Smoke Test | `pytest tests/integration/test_sdk_smoke.py -m smoke` | 100% pass |
| Type checking | `basedpyright docuswarm/` | Zero new errors |

---

## 5. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| SDK not available on all platforms | Low | High | Test on all target platforms first |
| SDK version instability | Medium | Medium | Pin exact version range |
| API key configuration | Low | Medium | Verify env var availability |
| Network/firewall blocking API | Low | High | Document proxy configuration |

---

## 6. Definition of Done (Epic Level)

- [ ] All 5 stories completed and tested
- [ ] `claude-agent-sdk` installed and importable
- [ ] Kimi Code API connectivity verified operational
- [ ] Smoke test passes with Kimi K2.5 backend
- [ ] Existing code backed up in git branch
- [ ] SDK type system documented
- [ ] No existing tests broken by dependency addition
- [ ] Type checking passes

---

## 7. References

| Document | Location |
|----------|----------|
| EPIC-16 SDK Wrapper | `docs/epics/EPIC-16-SDK-WRAPPER.md` |
| SDK Capability Matrix | EPIC-16 Section 2.1 |
| LLM Integration Architecture | `docs/architecture/05_LLM_INTEGRATION.md` |
| Tech Stack | `docs/architecture/tech-stack.md` |

---

**Epic End**
