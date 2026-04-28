# Epic 20: Exception Handling Migration

> **⚠️ 完全移除**: 本 Epic 完全移除 `kimi-agent-sdk` 异常，使用统一异常体系  
> **决策**: 零向后兼容，完全移除 Kimi SDK 异常，使用 DocuSwarm 统一异常  
> **参考**: [异常处理迁移研究报告](../research/migration/04-exception-handling-migration-report.md)

**Epic ID**: EPIC-20  
**Version**: 1.0 (完全移除版)  
**Date**: 2026-03-02  
**Status**: Ready for Development  
**Owner**: Tech Lead  
**Phase**: Phase 2 (Kimi SDK Removal)

---

## 1. Epic Overview

### 1.1 Summary

**完全移除** `kimi-agent-sdk` 的异常体系，将 DocuSwarm 项目中的 Kimi SDK 异常（如 `MaxStepsReached`, `RunCancelled`, `ChatProviderError` 等）迁移到 DocuSwarm 统一异常。这是 Kimi SDK 完全移除的最后一步。

### 1.2 Business Value

- **完全移除 Kimi SDK**: 消除对所有 Kimi SDK 异常的依赖
- **统一异常体系**: 使用单一的异常层次结构
- **清晰的错误处理**: 统一的异常类型便于错误处理
- **可维护性**: 减少外部依赖，提高代码稳定性

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| Kimi 异常移除 | 项目中无 `kimi_agent_sdk.*` 异常导入 |
| 异常替换 | 所有 Kimi 异常替换为统一异常 |
| 异常捕获 | 所有 `except` 子句更新 |
| 测试通过 | 所有异常相关测试通过 |

### 1.4 Dependencies

- **Requires**: Epic 17, 18, 19 completed
- **Blocks**: Final integration and cleanup

---

## 2. Architecture Context

### 2.1 Migration Overview

```
Before (v4.x - 迁移中):
  ┌─────────────────────────────────────────────────────────────┐
  │  Kimi SDK 异常                                              │
  │  ┌─────────────────────────────────────────────────────┐   │
  │  │ from kimi_agent_sdk import (                       │   │
  │  │     MaxStepsReached,        # 达到最大步数         │   │
  │  │     RunCancelled,           # 运行被取消           │   │
  │  │     ChatProviderError,      # API 提供程序错误     │   │
  │  │     ConfigError,            # 配置错误             │   │
  │  │     InvalidToolError,       # 无效工具             │   │
  │  │     ...                                             │   │
  │  │ )                                                   │   │
  │  └─────────────────────────────────────────────────────┘   │
  │                                                             │
  │  try:                                                       │
  │      await session.prompt(prompt)                          │
  │  except MaxStepsReached:                                   │
  │      handle_max_steps()                                    │
  │  except RunCancelled:                                      │
  │      handle_cancelled()                                    │
  └─────────────────────────────────────────────────────────────┘

After (v5.0 - 完全移除):
  ┌─────────────────────────────────────────────────────────────┐
  │  DocuSwarm 统一异常                                         │
  │  ┌─────────────────────────────────────────────────────┐   │
  │  │ from autoBMAD.docuswarm.exceptions import (        │   │
  │  │     StepLimitExceeded,      # 替代 MaxStepsReached │   │
  │  │     SessionCancelled,       # 替代 RunCancelled    │   │
  │  │     ConnectionError,        # 替代 ChatProviderError│   │
  │  │     ConfigurationError,     # 替代 ConfigError     │   │
  │  │     ToolExecutionError,     # 替代 InvalidToolError│   │
  │  │     ...                                             │   │
  │  │ )                                                   │   │
  │  └─────────────────────────────────────────────────────┘   │
  │                                                             │
  │  try:                                                       │
  │      await sdk_wrapper.execute(prompt)                     │
  │  except StepLimitExceeded:                                 │
  │      handle_max_steps()                                    │
  │  except SessionCancelled:                                  │
  │      handle_cancelled()                                    │
  └─────────────────────────────────────────────────────────────┘
```

### 2.2 Exception Mapping

| Kimi SDK 异常 (移除) | DocuSwarm 异常 (新) | 说明 |
|---------------------|---------------------|------|
| `MaxStepsReached` | `StepLimitExceeded` | 达到步数限制 |
| `RunCancelled` | `SessionCancelled` | Session 被取消 |
| `ChatProviderError` | `ConnectionError` | API 连接错误 |
| `ConfigError` | `ConfigurationError` | 配置错误 |
| `InvalidToolError` | `ToolExecutionError` | 工具执行错误 |
| `MessageAggregatorError` | `SDKError` | 使用基类 |
| `WireError` | `SDKError` | 使用基类 |

### 2.3 Key Files

| 文件 | 修改内容 | 优先级 |
|-----|---------|--------|
| `exceptions.py` | 扩展统一异常 | 🔴 高 |
| `llm/session_manager.py` | 更新异常导入和处理 | 🔴 高 |
| `agents/independent.py` | 更新异常导入和处理 | 🔴 高 |
| `agents/evaluator.py` | 更新异常导入和处理 | 🔴 高 |
| `llm/claude_sdk_wrapper.py` | 更新异常处理 | 🟡 中 |
| `tools/*.py` | 更新异常处理 | 🟡 中 |
| `tests/` | 更新测试异常断言 | 🔴 高 |

---

## 3. User Stories

### Story 20.1: Unified Exception Hierarchy Extension

**ID**: US-20.1  
**As a** developer  
**I want to** extend the exception hierarchy with SDK-specific exceptions  
**So that** all Kimi SDK exceptions have DocuSwarm equivalents

**Acceptance Criteria**:
- [ ] 扩展 `exceptions.py` 添加 SDK 层异常
- [ ] 创建 `SDKError` 基类
- [ ] 创建 `StepLimitExceeded` 异常
- [ ] 创建 `SessionCancelled` 异常
- [ ] 创建 `ConnectionError` 异常
- [ ] 创建 `ToolExecutionError` 异常
- [ ] 所有异常支持上下文信息

**Technical Tasks**:
1. 修改 `docuswarm/exceptions.py`
2. 添加 SDK 异常基类
3. 添加具体异常类
4. 更新 `__all__` 导出
5. 编写单元测试

**Implementation**:

```python
# docuswarm/exceptions.py (扩展)

# ============ SDK 层 ============

class SDKError(DocuSwarmError):
    """SDK 错误基类。
    
    所有 SDK 相关错误的基类。
    """
    
    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
        *,
        sdk_type: str | None = None,
        original_error: Exception | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        self.sdk_type = sdk_type
        self.original_error = original_error
        super().__init__(message, context, **kwargs)
        if sdk_type is not None:
            self._context["sdk_type"] = sdk_type
        if original_error is not None:
            self._context["original_error"] = str(original_error)


class StepLimitExceeded(SDKError):
    """超出步数限制。
    
    当 Agent 执行超过最大步数时抛出。
    替代 Kimi SDK 的 MaxStepsReached。
    """
    
    def __init__(
        self,
        message: str | None = None,
        context: dict[str, Any] | None = None,
        *,
        max_steps: int | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        self.max_steps = max_steps
        if message is None:
            message = f"Maximum steps ({max_steps}) reached" if max_steps else "Maximum steps reached"
        super().__init__(message, context, **kwargs)
        if max_steps is not None:
            self._context["max_steps"] = max_steps


class SessionCancelled(SDKError):
    """Session 被取消。
    
    当 Session 执行被用户或系统取消时抛出。
    替代 Kimi SDK 的 RunCancelled。
    """
    
    def __init__(
        self,
        message: str = "Session was cancelled",
        context: dict[str, Any] | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        super().__init__(message, context, **kwargs)


class ConnectionError(SDKError):
    """连接错误 - API 调用失败。
    
    当与 LLM API 的连接失败时抛出。
    替代 Kimi SDK 的 ChatProviderError。
    """
    
    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
        *,
        endpoint: str | None = None,
        status_code: int | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        self.endpoint = endpoint
        self.status_code = status_code
        super().__init__(message, context, **kwargs)
        if endpoint is not None:
            self._context["endpoint"] = endpoint
        if status_code is not None:
            self._context["status_code"] = status_code


class ToolExecutionError(SDKError):
    """工具执行错误。
    
    当工具执行失败时抛出。
    替代 Kimi SDK 的 InvalidToolError。
    """
    
    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
        *,
        tool_name: str | None = None,
        tool_input: dict[str, Any] | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        self.tool_name = tool_name
        self.tool_input = tool_input
        super().__init__(message, context, **kwargs)
        if tool_name is not None:
            self._context["tool_name"] = tool_name
        if tool_input is not None:
            self._context["tool_input"] = tool_input


# 更新 __all__
__all__ = [
    # ... 现有导出
    "SDKError",
    "StepLimitExceeded",
    "SessionCancelled",
    "ConnectionError",
    "ToolExecutionError",
]
```

**Definition of Done**:
- 所有新异常类创建完成
- 所有异常支持上下文信息
- 单元测试通过

---

### Story 20.2: SessionManager Exception Migration

**ID**: US-20.2  
**As a** developer  
**I want to** update SessionManager to use unified exceptions  
**So that** it doesn't depend on Kimi SDK exceptions

**Acceptance Criteria**:
- [ ] 移除 Kimi SDK 异常导入
- [ ] 更新异常捕获为统一异常
- [ ] `MaxStepsReached` → `StepLimitExceeded`
- [ ] `RunCancelled` → `SessionCancelled`
- [ ] `ChatProviderError` → `ConnectionError`

**Technical Tasks**:
1. 修改 `docuswarm/llm/session_manager.py`
2. 更新所有异常导入
3. 更新异常捕获逻辑
4. 更新单元测试

**Before/After**:

```python
# BEFORE: 完全移除

from kimi_agent_sdk import (
    ChatProviderError,
    ConfigError,
    RunCancelled,
    MaxStepsReached,
    InvalidToolError,
)
from autoBMAD.docuswarm.exceptions import ConfigurationError, LLMError

async def single_prompt(self, prompt: str, ...) -> list[Message]:
    try:
        async for wire_msg in session.prompt(prompt):
            ...
    except MaxStepsReached:
        self._logger.warning("single_prompt_max_steps")
        return aggregator.flush()
    except RunCancelled:
        self._logger.info("single_prompt_cancelled")
        return []
    except ChatProviderError as e:
        raise LLMError(...) from e
    except ConfigError as e:
        raise ConfigurationError(...) from e
```

```python
# AFTER: 新实现

from autoBMAD.docuswarm.exceptions import (
    ConnectionError,
    ConfigurationError,
    SessionCancelled,
    StepLimitExceeded,
    ToolExecutionError,
    LLMCallError,
)

async def single_prompt(self, prompt: str, ...) -> list[dict[str, Any]]:
    try:
        result = await self._sdk_wrapper.execute(prompt)
        ...
    except StepLimitExceeded:
        self._logger.warning("single_prompt_max_steps")
        return []
    except SessionCancelled:
        self._logger.info("single_prompt_cancelled")
        return []
    except ConnectionError as e:
        self._logger.error("single_prompt_connection_error", error=str(e))
        raise LLMCallError(f"Connection error: {e}") from e
    except ConfigurationError as e:
        self._logger.error("single_prompt_config_error", error=str(e))
        raise
    except ToolExecutionError as e:
        self._logger.error("single_prompt_tool_error", tool=e.tool_name)
        raise
```

**Definition of Done**:
- SessionManager 无 Kimi SDK 异常导入
- 所有异常捕获更新
- 单元测试通过

---

### Story 20.3: IndependentAgent Exception Migration

**ID**: US-20.3  
**As a** developer  
**I want to** update IndependentAgent to use unified exceptions  
**So that** it doesn't depend on Kimi SDK exceptions

**Acceptance Criteria**:
- [ ] 移除 Kimi SDK 异常导入
- [ ] 更新异常捕获为统一异常
- [ ] 更新异常抛出为统一异常
- [ ] 保留原始异常链

**Technical Tasks**:
1. 修改 `docuswarm/agents/independent.py`
2. 更新所有异常导入
3. 更新异常捕获逻辑
4. 更新单元测试

**Before/After**:

```python
# BEFORE: 完全移除

async def _call_llm_via_session(self, user_message: str) -> list[Message]:
    try:
        async for wire_msg in session.prompt(full_prompt):
            ...
    except MaxStepsReached as e:
        self.logger.warning("max_steps_reached", error=str(e))
        if messages:
            return messages
        raise LLMCallError(f"Max steps reached: {e}") from e
    except RunCancelled as e:
        self.logger.info("run_cancelled", error=str(e))
        if messages:
            return messages
        raise LLMCallError(f"Run cancelled: {e}") from e
    except LLMError:
        raise
    except Exception as e:
        self.logger.error("session_call_failed", error=str(e))
        raise SessionError(f"Session call failed: {e}") from e
```

```python
# AFTER: 新实现

from autoBMAD.docuswarm.exceptions import (
    LLMCallError,
    SessionError,
    SessionCancelled,
    StepLimitExceeded,
)

async def _call_llm_via_session(self, user_message: str) -> list[dict[str, Any]]:
    try:
        result = await self._session_manager.execute(prompt=full_prompt)
        return result.messages
    except StepLimitExceeded as e:
        self.logger.warning("max_steps_reached", max_steps=e.max_steps)
        if result.messages:
            return result.messages
        raise LLMCallError(
            f"Maximum steps ({e.max_steps}) reached",
            prompt_preview=user_message[:100]
        ) from e
    except SessionCancelled as e:
        self.logger.info("run_cancelled")
        if result.messages:
            return result.messages
        raise LLMCallError("Session was cancelled") from e
    except LLMCallError:
        raise
    except Exception as e:
        self.logger.error("session_call_failed", error=str(e))
        raise SessionError(f"Session call failed: {e}") from e
```

**Definition of Done**:
- IndependentAgent 无 Kimi SDK 异常导入
- 所有异常捕获更新
- 单元测试通过

---

### Story 20.4: EvaluatorAgent Exception Migration

**ID**: US-20.4  
**As a** developer  
**I want to** update EvaluatorAgent to use unified exceptions  
**So that** it doesn't depend on Kimi SDK exceptions

**Acceptance Criteria**:
- [ ] 移除 Kimi SDK 异常导入
- [ ] 更新异常处理为统一异常
- [ ] 更新类型提示

**Technical Tasks**:
1. 修改 `docuswarm/agents/evaluator.py`
2. 更新所有异常导入
3. 更新异常处理逻辑
4. 更新单元测试

**Definition of Done**:
- EvaluatorAgent 无 Kimi SDK 异常导入
- 所有异常处理更新
- 单元测试通过

---

### Story 20.5: Test Exception Assertions Update

**ID**: US-20.5  
**As a** developer  
**I want to** update test exception assertions  
**So that** they use unified exceptions

**Acceptance Criteria**:
- [ ] 更新 `pytest.raises()` 调用
- [ ] 更新异常导入
- [ ] 验证异常上下文信息

**Technical Tasks**:
1. 更新所有测试文件中的异常断言
2. 更新异常导入
3. 运行测试验证

**Implementation**:

```python
# tests/unit/test_session_manager_exceptions.py

import pytest
from autoBMAD.docuswarm.exceptions import (
    StepLimitExceeded,
    SessionCancelled,
    ConnectionError,
)


class TestSessionManagerExceptions:
    """SessionManager 异常处理测试。"""
    
    @pytest.mark.asyncio
    async def test_step_limit_handling(self, mock_sdk_wrapper):
        """测试步数限制处理。"""
        mock_sdk_wrapper.execute.side_effect = StepLimitExceeded(max_steps=10)
        
        manager = SessionManager(work_dir="/tmp/test")
        manager._sdk_wrapper = mock_sdk_wrapper
        
        result = await manager.single_prompt("test")
        
        # 应该返回空列表而非抛出
        assert result == []
    
    @pytest.mark.asyncio
    async def test_connection_error_handling(self, mock_sdk_wrapper):
        """测试连接错误处理。"""
        mock_sdk_wrapper.execute.side_effect = ConnectionError(
            message="Connection failed"
        )
        
        manager = SessionManager(work_dir="/tmp/test")
        manager._sdk_wrapper = mock_sdk_wrapper
        
        with pytest.raises(LLMCallError):
            await manager.single_prompt("test")


# tests/unit/test_exceptions.py

import pytest
from autoBMAD.docuswarm.exceptions import (
    ConnectionError,
    ConfigurationError,
    SessionCancelled,
    StepLimitExceeded,
    ToolExecutionError,
)


class TestExceptions:
    """异常类测试。"""
    
    def test_step_limit_exceeded(self):
        """测试步数限制异常。"""
        exc = StepLimitExceeded(max_steps=10)
        
        assert exc.max_steps == 10
        assert "10" in str(exc)
    
    def test_connection_error(self):
        """测试连接错误。"""
        exc = ConnectionError(
            message="Connection failed",
            endpoint="api.example.com",
            status_code=500
        )
        
        assert exc.endpoint == "api.example.com"
        assert exc.status_code == 500
    
    def test_tool_execution_error(self):
        """测试工具执行错误。"""
        exc = ToolExecutionError(
            message="Tool failed",
            tool_name="create_deliverable",
            tool_input={"title": "Test"}
        )
        
        assert exc.tool_name == "create_deliverable"
        assert exc.tool_input == {"title": "Test"}
```

**Definition of Done**:
- 所有测试异常断言更新
- 所有测试通过

---

## 4. Technical Specifications

### 4.1 Modified Modules

| Module | Location | Changes |
|--------|----------|---------|
| `exceptions.py` | `docuswarm/exceptions.py` | 扩展统一异常 |
| `SessionManager` | `docuswarm/llm/session_manager.py` | 更新异常处理 |
| `IndependentAgent` | `docuswarm/agents/independent.py` | 更新异常处理 |
| `EvaluatorAgent` | `docuswarm/agents/evaluator.py` | 更新异常处理 |
| `ClaudeSDKWrapper` | `docuswarm/llm/claude_sdk_wrapper.py` | 更新异常处理 |

### 4.2 Exception Mapping Summary

| 原异常 | 新异常 | 状态 |
|--------|--------|------|
| `kimi_agent_sdk.MaxStepsReached` | `StepLimitExceeded` | 替换 |
| `kimi_agent_sdk.RunCancelled` | `SessionCancelled` | 替换 |
| `kimi_agent_sdk.ChatProviderError` | `ConnectionError` | 替换 |
| `kimi_agent_sdk.ConfigError` | `ConfigurationError` | 替换 |
| `kimi_agent_sdk.InvalidToolError` | `ToolExecutionError` | 替换 |

### 4.3 Quality Gates

| Check | Command | Threshold |
|-------|---------|-----------|
| Type checking | `basedpyright docuswarm/` | Zero errors |
| Linting | `ruff check docuswarm/` | Zero errors |
| Unit tests | `pytest tests/unit/test_exceptions.py` | 100% pass |
| Integration tests | `pytest tests/integration/` | Pass |

---

## 5. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| 异常类型不匹配 | 低 | 高 | 代码审查 |
| 异常信息丢失 | 低 | 中 | 保留原始异常链 |
| 测试失败 | 中 | 中 | 更新测试断言 |
| 异常捕获失效 | 中 | 高 | 全局搜索替换 |

---

## 6. Definition of Done (Epic Level)

- [ ] 所有 Story 完成并测试通过
- [ ] `exceptions.py` 扩展完成，包含所有新异常
- [ ] 项目中无 `kimi_agent_sdk.*` 异常导入
- [ ] SessionManager 使用统一异常
- [ ] IndependentAgent 使用统一异常
- [ ] EvaluatorAgent 使用统一异常
- [ ] 所有异常捕获更新
- [ ] 所有测试异常断言更新
- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 类型检查通过
- [ ] Linting 通过

---

## 7. References

| Document | Location |
|----------|----------|
| 异常处理迁移报告 | `docs/research/migration/04-exception-handling-migration-report.md` |
| Epic 17 Message 迁移 | `docs/epics/EPIC-17-MESSAGE-FORMAT-MIGRATION.md` |
| Epic 18 Tool 迁移 | `docs/epics/EPIC-18-TOOL-CALLING-MIGRATION.md` |
| Epic 19 测试迁移 | `docs/epics/EPIC-19-TEST-MIGRATION.md` |

---

**Epic End**
