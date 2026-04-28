# DocuSwarm 异常处理完全移除报告

> **奥卡姆剃刀原则**: 如无必要，勿增实体  
> **决策**: 完全移除 kimi-agent-sdk 异常，使用统一异常体系  
> **研究日期**: 2026-03-02  
> **主题**: 从 kimi-agent-sdk 异常体系迁移到统一异常处理

---

## 目录

1. [执行摘要](#1-执行摘要)
2. [当前异常体系分析](#2-当前异常体系分析)
3. [目标异常体系](#3-目标异常体系)
4. [完全移除方案](#4-完全移除方案)
5. [代码迁移示例](#5-代码迁移示例)
6. [文件修改清单](#6-文件修改清单)
7. [风险评估](#7-风险评估)
8. [测试策略](#8-测试策略)
9. [结论](#9-结论)

---

## 1. 执行摘要

### 1.1 目标

完全移除 DocuSwarm 项目中 `kimi-agent-sdk` 的异常体系依赖。

### 1.2 关键发现

| 维度 | 评估 |
|-----|------|
| **异常类型数** | Kimi SDK: 8+ 个 |
| **代码影响** | 15+ 个文件有显式异常处理 |
| **处理复杂度** | 🟡 中 |
| **策略** | **完全移除，无兼容层** |

### 1.3 决策

**不使用兼容层，完全移除**:
- ❌ 不保留 Kimi SDK 异常类作为别名
- ❌ 不使用异常映射层
- ❌ 不提供废弃警告
- ✅ 直接替换为统一异常
- ✅ 所有代码使用新异常

---

## 2. 当前异常体系分析

### 2.1 Kimi SDK 异常类（将被移除）

```python
# 将被完全移除的异常类

from kimi_agent_sdk import (
    KimiSDKError,           # 基础异常
    ConfigError,            # 配置错误
    ChatProviderError,      # API 提供程序错误
    RunCancelled,           # 运行被取消
    MaxStepsReached,        # 达到最大步数
    InvalidToolError,       # 无效工具
    MessageAggregatorError, # 消息聚合错误
    WireError,              # Wire 协议错误
)
```

### 2.2 代码中的异常处理（需要修改）

```python
# llm/session_manager.py (将被移除的部分)

from kimi_agent_sdk import (
    ChatProviderError,
    ConfigError,
    RunCancelled,
    MaxStepsReached,
    InvalidToolError,
)

async def single_prompt(self, prompt: str, ...) -> list[Message]:
    try:
        async for wire_msg in session.prompt(prompt):
            ...
    except MaxStepsReached:
        # 将被替换
        self._logger.warning("single_prompt_max_steps")
        return aggregator.flush()
    except RunCancelled:
        # 将被替换
        self._logger.info("single_prompt_cancelled")
        return []
    except ChatProviderError as e:
        # 将被替换
        raise LLMError(...) from e
    except ConfigError as e:
        # 将被替换
        raise ConfigurationError(...) from e
```

```python
# agents/independent.py (将被移除的部分)

async def _call_llm_via_session(self, user_message: str) -> list[Message]:
    try:
        async for wire_msg in session.prompt(full_prompt):
            ...
    except MaxStepsReached as e:
        # 将被替换
        self.logger.warning("max_steps_reached", error=str(e))
        if messages:
            return messages
        raise LLMCallError(f"Max steps reached: {e}") from e
    except RunCancelled as e:
        # 将被替换
        self.logger.info("run_cancelled", error=str(e))
        if messages:
            return messages
        raise LLMCallError(f"Run cancelled: {e}") from e
```

---

## 3. 目标异常体系

### 3.1 统一异常层次结构（新）

```python
# exceptions.py (新方案)

"""DocuSwarm 统一异常层次结构 - 无 SDK 依赖"""

from typing import Any


# ============ 基础层 ============

class DocuSwarmError(Exception):
    """DocuSwarm 基础异常"""
    
    def __init__(self, message: str, *, error_code: str | None = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


# ============ SDK 层 ============

class SDKError(DocuSwarmError):
    """SDK 错误基类"""
    
    def __init__(
        self,
        message: str,
        *,
        sdk_type: str | None = None,
        original_error: Exception | None = None
    ):
        self.sdk_type = sdk_type
        self.original_error = original_error
        super().__init__(message)


class ConfigurationError(SDKError):
    """配置错误"""
    
    def __init__(
        self,
        message: str,
        *,
        config_source: str | None = None,
        **kwargs
    ):
        self.config_source = config_source
        super().__init__(message, **kwargs)


class ConnectionError(SDKError):
    """连接错误 - API 调用失败"""
    
    def __init__(
        self,
        message: str,
        *,
        endpoint: str | None = None,
        status_code: int | None = None,
        **kwargs
    ):
        self.endpoint = endpoint
        self.status_code = status_code
        super().__init__(message, **kwargs)


class SessionError(SDKError):
    """Session 错误基类"""
    pass


class SessionCancelled(SessionError):
    """Session 被取消"""
    
    def __init__(self, message: str = "Session was cancelled", **kwargs):
        super().__init__(message, **kwargs)


class StepLimitExceeded(SessionError):
    """超出步数限制"""
    
    def __init__(
        self,
        max_steps: int | None = None,
        message: str | None = None,
        **kwargs
    ):
        self.max_steps = max_steps
        if message is None:
            message = f"Maximum steps ({max_steps}) reached" if max_steps else "Maximum steps reached"
        super().__init__(message, **kwargs)


class ToolExecutionError(SDKError):
    """工具执行错误"""
    
    def __init__(
        self,
        message: str,
        *,
        tool_name: str | None = None,
        tool_input: dict[str, Any] | None = None,
        **kwargs
    ):
        self.tool_name = tool_name
        self.tool_input = tool_input
        super().__init__(message, **kwargs)


# ============ 业务层 ============

class AgentError(DocuSwarmError):
    """Agent 错误基类"""
    pass


class LLMCallError(AgentError):
    """LLM 调用错误"""
    
    def __init__(
        self,
        message: str,
        *,
        prompt_preview: str | None = None,
        **kwargs
    ):
        self.prompt_preview = prompt_preview
        super().__init__(message, **kwargs)


class ResponseParseError(AgentError):
    """响应解析错误"""
    
    def __init__(
        self,
        message: str,
        *,
        raw_content: str | None = None,
        **kwargs
    ):
        self.raw_content = raw_content
        super().__init__(message, **kwargs)
```

### 3.2 异常映射（直接替换，无适配层）

| Kimi SDK 异常 (移除) | 新异常 | 说明 |
|---------------------|--------|------|
| `ChatProviderError` | `ConnectionError` | 直接替换 |
| `ConfigError` | `ConfigurationError` | 直接替换 |
| `RunCancelled` | `SessionCancelled` | 直接替换 |
| `MaxStepsReached` | `StepLimitExceeded` | 直接替换 |
| `InvalidToolError` | `ToolExecutionError` | 直接替换 |
| `MessageAggregatorError` | `SDKError` | 使用基类 |
| `WireError` | `SDKError` | 使用基类 |

---

## 4. 完全移除方案

### 4.1 移除内容清单

**完全移除（直接替换）**:
- `kimi_agent_sdk.ChatProviderError` → 使用 `ConnectionError`
- `kimi_agent_sdk.ConfigError` → 使用 `ConfigurationError`
- `kimi_agent_sdk.RunCancelled` → 使用 `SessionCancelled`
- `kimi_agent_sdk.MaxStepsReached` → 使用 `StepLimitExceeded`
- `kimi_agent_sdk.InvalidToolError` → 使用 `ToolExecutionError`
- `kimi_agent_sdk.MessageAggregatorError` → 使用 `SDKError`
- `kimi_agent_sdk.WireError` → 使用 `SDKError`

**不保留**:
- 兼容层
- 异常映射器
- 废弃警告
- 别名

---

## 5. 代码迁移示例

### 5.1 SessionManager 异常处理迁移

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
    except InvalidToolError as e:
        raise LLMError(...) from e
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

### 5.2 IndependentAgent 异常处理迁移

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

---

## 6. 文件修改清单

| 文件 | 修改内容 | 优先级 |
|-----|---------|--------|
| `exceptions.py` | 重写统一异常 | 🔴 高 |
| `llm/session_manager.py` | 更新异常导入和处理 | 🔴 高 |
| `agents/independent.py` | 更新异常导入和处理 | 🔴 高 |
| `agents/evaluator.py` | 更新异常导入和处理 | 🔴 高 |
| `tools/*.py` | 更新异常处理 | 🟡 中 |
| `pipeline/*.py` | 更新异常处理 | 🟡 中 |
| `tests/` | 更新测试异常断言 | 🔴 高 |

---

## 7. 风险评估

### 7.1 技术风险矩阵

| 风险项 | 概率 | 影响 | 等级 | 缓解措施 |
|-------|------|------|------|---------|
| 异常类型不匹配 | 低 | 高 | 🟡 中 | 代码审查 |
| 异常信息丢失 | 低 | 中 | 🟢 低 | 保留原始异常链 |
| 测试失败 | 中 | 中 | 🟡 中 | 更新测试断言 |

### 7.2 关键风险点

**风险: 异常捕获失效**

原有的 `except MaxStepsReached:` 需要改为 `except StepLimitExceeded:`。

**缓解**: 全局搜索替换所有异常导入和捕获。

---

## 8. 测试策略

### 8.1 异常测试

```python
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
    """异常类测试"""
    
    def test_step_limit_exceeded(self):
        """测试步数限制异常"""
        exc = StepLimitExceeded(max_steps=10)
        
        assert exc.max_steps == 10
        assert "10" in str(exc)
    
    def test_connection_error(self):
        """测试连接错误"""
        exc = ConnectionError(
            message="Connection failed",
            endpoint="api.example.com",
            status_code=500
        )
        
        assert exc.endpoint == "api.example.com"
        assert exc.status_code == 500
    
    def test_tool_execution_error(self):
        """测试工具执行错误"""
        exc = ToolExecutionError(
            message="Tool failed",
            tool_name="create_deliverable",
            tool_input={"title": "Test"}
        )
        
        assert exc.tool_name == "create_deliverable"
        assert exc.tool_input == {"title": "Test"}
```

### 8.2 异常处理测试

```python
# tests/unit/test_session_manager_exceptions.py

import pytest
from autoBMAD.docuswarm.exceptions import (
    StepLimitExceeded,
    SessionCancelled,
    ConnectionError,
)


class TestSessionManagerExceptions:
    """SessionManager 异常处理测试"""
    
    @pytest.mark.asyncio
    async def test_step_limit_handling(self, mock_sdk_wrapper):
        """测试步数限制处理"""
        mock_sdk_wrapper.execute.side_effect = StepLimitExceeded(max_steps=10)
        
        manager = SessionManager(work_dir="/tmp/test")
        manager._sdk_wrapper = mock_sdk_wrapper
        
        result = await manager.single_prompt("test")
        
        # 应该返回空列表而非抛出
        assert result == []
    
    @pytest.mark.asyncio
    async def test_connection_error_handling(self, mock_sdk_wrapper):
        """测试连接错误处理"""
        mock_sdk_wrapper.execute.side_effect = ConnectionError(
            message="Connection failed"
        )
        
        manager = SessionManager(work_dir="/tmp/test")
        manager._sdk_wrapper = mock_sdk_wrapper
        
        with pytest.raises(LLMCallError):
            await manager.single_prompt("test")
```

---

## 9. 结论

### 9.1 结论

1. **异常体系需要完全替换**：Kimi SDK 异常与统一异常语义基本一致，可以直接替换。

2. **完全移除是最佳方案**：避免维护映射层的复杂性。

3. **迁移需要 1-2 周**：主要是全局搜索替换和测试更新。

4. **风险较低**：异常语义清晰，替换简单。

### 9.2 建议

**立即执行**:
1. 重写 `exceptions.py` 定义统一异常
2. 全局搜索替换异常导入
3. 更新所有测试断言
4. 运行完整测试套件

**监控指标**:
- 异常处理测试通过率
- 代码覆盖率
- 运行时异常发生率

---

*报告完成日期: 2026-03-02*  
*文档版本: 2.0 (完全移除版)*
