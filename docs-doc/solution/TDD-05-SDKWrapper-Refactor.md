# TDD 重构方案: Claude SDK Wrapper（SDK 替换）

> **关联研究报告**: [DocuSwarm-重构详细研究报告-Part3.md](../research/DocuSwarm-重构详细研究报告-Part3.md)  
> **优先级**: P1 - 重要  
> **预估工期**: 2-3 天  
> **影响范围**: `llm/claude_sdk_wrapper.py` (新增), `llm/session_manager.py` (重写)

---

## 1. 问题分析

### 1.1 当前架构问题

采用 `claude-agent-sdk` + Kimi Code API 的 OpenAI 兼容接口：
- 与 `epic_automation` 使用的 SDK 一致
- 统一的 Tool Use Block 模式
- 简化 MessageAggregator 逻辑

### 1.2 目标架构

```
目标 (claude-agent-sdk + Kimi Code API)
────────────────────────────────────────
query() 函数式 API
返回 AsyncGenerator
ResultMessage (终结)
标准 Tool Use Block
标准 Path
环境变量: ANTHROPIC_BASE_URL, ANTHROPIC_API_KEY
```

### 1.3 兼容性策略

通过 **Kimi Code API 的 OpenAI 兼容接口** 使用 Claude SDK：

```python
# 环境变量配置
ANTHROPIC_BASE_URL="https://api.kimi.com/coding/"
ANTHROPIC_API_KEY="your-kimi-api-key"
```

---

## 2. 目标设计

### 2.1 SDKResult 数据类

```python
@dataclass
class SDKResult:
    """SDK 执行结果（与 epic_automation 兼容）。"""
    success: bool
    content: str | None
    error: str | None
    duration: float
    messages: list[Any] = field(default_factory=list)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    
    def is_success(self) -> bool:
        return self.success and self.content is not None
```

### 2.2 ClaudeSDKWrapper API

```python
class ClaudeSDKWrapper:
    """Claude SDK 封装层 - 统一的 SDK 调用接口。
    
    借鉴 epic_automation/sdk_wrapper.py 的成熟模式，
    通过 Kimi Code API 的 OpenAI 兼容接口工作。
    """
    
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        permission_mode: str = "bypassPermissions",
    ) -> None:
        """初始化 SDK 封装。
        
        Args:
            base_url: Kimi Code API base URL
            api_key: API key
            permission_mode: 权限模式
        """
    
    async def execute(
        self,
        prompt: str,
        agent_name: str = "docuswarm",
        timeout: float | None = 1800.0,
        cwd: str | Path | None = None,
    ) -> SDKResult:
        """执行 SDK 调用。
        
        Args:
            prompt: 提示词
            agent_name: Agent 名称（用于日志）
            timeout: 超时时间（秒）
            cwd: 工作目录
            
        Returns:
            SDKResult: 执行结果
        """
```

### 2.3 SessionManager 兼容层

```python
class SessionManager:
    """会话管理器 - 基于 Claude SDK（兼容原 KimiSessionManager 接口）。
    
    提供与原 KimiSessionManager 兼容的接口，内部使用 ClaudeSDKWrapper。
    """
    
    async def single_prompt(
        self,
        prompt: str,
        mode: str = "agent",
        yolo: bool = True,
        agent_name: str = "docuswarm",
        timeout: float | None = 1800.0,
    ) -> SDKResult:
        """执行单次提示（兼容原 single_prompt 接口）。"""
```

---

## 3. 测试驱动开发计划

### Phase 1: ClaudeSDKWrapper 测试

```python
# tests/unit/test_claude_sdk_wrapper.py

import pytest
from unittest.mock import AsyncMock, Mock, patch
from autoBMAD.docuswarm.llm.claude_sdk_wrapper import (
    ClaudeSDKWrapper,
    SDKResult,
    SDKError,
)


class TestClaudeSDKWrapperInit:
    """Test initialization."""
    
    def test_init_with_explicit_params(self):
        """Test initialization with explicit parameters."""
        wrapper = ClaudeSDKWrapper(
            base_url="https://api.kimi.com/coding/",
            api_key="test-key",
            permission_mode="confirmPermissions",
        )
        
        assert wrapper.base_url == "https://api.kimi.com/coding/"
        assert wrapper.api_key == "test-key"
        assert wrapper.permission_mode == "confirmPermissions"
    
    def test_init_reads_from_env(self, monkeypatch):
        """Test initialization reads from environment variables."""
        monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://custom.api.com/")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "env-key")
        
        wrapper = ClaudeSDKWrapper()
        
        assert wrapper.base_url == "https://custom.api.com/"
        assert wrapper.api_key == "env-key"
    
    def test_init_uses_defaults(self):
        """Test initialization uses defaults when no env vars."""
        wrapper = ClaudeSDKWrapper()
        
        assert wrapper.base_url == "https://api.kimi.com/coding/"
        assert wrapper.api_key == ""  # Empty default


class TestClaudeSDKWrapperExecute:
    """Test execute method."""
    
    @pytest.mark.asyncio
    @patch("autoBMAD.docuswarm.llm.claude_sdk_wrapper.query")
    async def test_execute_success(self, mock_query):
        """Test successful execution."""
        # Arrange
        from claude_agent_sdk import ResultMessage
        
        mock_query.return_value = AsyncMock()
        mock_query.return_value.__aiter__ = AsyncMock(
            return_value=iter([ResultMessage(result="Success output", is_error=False)])
        )
        
        wrapper = ClaudeSDKWrapper(api_key="test-key")
        
        # Act
        result = await wrapper.execute("Test prompt")
        
        # Assert
        assert isinstance(result, SDKResult)
        assert result.success is True
        assert result.content == "Success output"
        assert result.error is None
    
    @pytest.mark.asyncio
    @patch("autoBMAD.docuswarm.llm.claude_sdk_wrapper.query")
    async def test_execute_error_result(self, mock_query):
        """Test handling of error ResultMessage."""
        from claude_agent_sdk import ResultMessage
        
        mock_query.return_value = AsyncMock()
        mock_query.return_value.__aiter__ = AsyncMock(
            return_value=iter([ResultMessage(result="Error occurred", is_error=True)])
        )
        
        wrapper = ClaudeSDKWrapper(api_key="test-key")
        result = await wrapper.execute("Test prompt")
        
        assert result.success is False
        assert "Error occurred" in result.error
    
    @pytest.mark.asyncio
    @patch("autoBMAD.docuswarm.llm.claude_sdk_wrapper.query")
    async def test_execute_no_result_message(self, mock_query):
        """Test when no ResultMessage is received."""
        from claude_agent_sdk import AssistantMessage
        
        mock_query.return_value = AsyncMock()
        mock_query.return_value.__aiter__ = AsyncMock(
            return_value=iter([AssistantMessage(content="Just text")])
        )
        
        wrapper = ClaudeSDKWrapper(api_key="test-key")
        result = await wrapper.execute("Test prompt")
        
        assert result.success is False
        assert "No ResultMessage received" in result.error
    
    @pytest.mark.asyncio
    @patch("autoBMAD.docuswarm.llm.claude_sdk_wrapper.query")
    async def test_execute_exception(self, mock_query):
        """Test handling of exceptions."""
        mock_query.side_effect = Exception("SDK error")
        
        wrapper = ClaudeSDKWrapper(api_key="test-key")
        result = await wrapper.execute("Test prompt")
        
        assert result.success is False
        assert "SDK error" in result.error
    
    @pytest.mark.asyncio
    @patch("autoBMAD.docuswarm.llm.claude_sdk_wrapper.query")
    async def test_execute_cancellation(self, mock_query):
        """Test handling of CancelledError."""
        import asyncio
        mock_query.side_effect = asyncio.CancelledError()
        
        wrapper = ClaudeSDKWrapper(api_key="test-key")
        result = await wrapper.execute("Test prompt")
        
        assert result.success is False
        assert "cancelled" in result.error.lower()


class TestClaudeSDKWrapperEnvironment:
    """Test environment variable setup."""
    
    @pytest.mark.asyncio
    @patch("autoBMAD.docuswarm.llm.claude_sdk_wrapper.query")
    async def test_sets_environment_before_query(self, mock_query):
        """Test that ANTHROPIC_* env vars are set before calling query."""
        import os
        from claude_agent_sdk import ResultMessage
        
        mock_query.return_value = AsyncMock()
        mock_query.return_value.__aiter__ = AsyncMock(
            return_value=iter([ResultMessage(result="OK", is_error=False)])
        )
        
        wrapper = ClaudeSDKWrapper(
            base_url="https://custom.url/",
            api_key="custom-key",
        )
        
        await wrapper.execute("Test")
        
        assert os.environ.get("ANTHROPIC_BASE_URL") == "https://custom.url/"
        assert os.environ.get("ANTHROPIC_API_KEY") == "custom-key"
```

### Phase 2: SessionManager 兼容层测试

```python
# tests/unit/test_session_manager.py

import pytest
from unittest.mock import AsyncMock, Mock, patch
from pathlib import Path
from autoBMAD.docuswarm.llm.session_manager import SessionManager


class TestSessionManagerInit:
    """Test SessionManager initialization."""
    
    def test_init_with_work_dir(self):
        """Test initialization with work directory."""
        manager = SessionManager(work_dir=Path("/test/work"))
        
        assert manager.work_dir == Path("/test/work")
    
    def test_init_uses_cwd_default(self):
        """Test initialization defaults to cwd."""
        manager = SessionManager()
        
        assert manager.work_dir == Path.cwd()


class TestSessionManagerSinglePrompt:
    """Test single_prompt method (兼容接口)."""
    
    @pytest.mark.asyncio
    @patch("autoBMAD.docuswarm.llm.session_manager.ClaudeSDKWrapper")
    async def test_single_prompt_success(self, mock_wrapper_class):
        """Test successful single prompt."""
        # Arrange
        mock_wrapper = Mock()
        mock_wrapper.execute = AsyncMock(return_value=Mock(
            success=True,
            content="Response content",
            error=None,
            duration=1.5,
            messages=[],
        ))
        mock_wrapper_class.return_value = mock_wrapper
        
        manager = SessionManager()
        
        # Act
        result = await manager.single_prompt(
            prompt="Hello",
            mode="agent",
            agent_name="test-agent",
        )
        
        # Assert
        assert result.content == "Response content"
        mock_wrapper.execute.assert_called_once()
        call_kwargs = mock_wrapper.execute.call_args.kwargs
        assert call_kwargs["prompt"] == "Hello"
        assert call_kwargs["agent_name"] == "test-agent"
    
    @pytest.mark.asyncio
    @patch("autoBMAD.docuswarm.llm.session_manager.ClaudeSDKWrapper")
    async def test_single_prompt_with_timeout(self, mock_wrapper_class):
        """Test timeout parameter is passed through."""
        mock_wrapper = Mock()
        mock_wrapper.execute = AsyncMock(return_value=Mock(
            success=True,
            content="OK",
            error=None,
            duration=1.0,
            messages=[],
        ))
        mock_wrapper_class.return_value = mock_wrapper
        
        manager = SessionManager()
        await manager.single_prompt("Test", timeout=600.0)
        
        call_kwargs = mock_wrapper.execute.call_args.kwargs
        assert call_kwargs["timeout"] == 600.0
    
    @pytest.mark.asyncio
    @patch("autoBMAD.docuswarm.llm.session_manager.ClaudeSDKWrapper")
    async def test_single_prompt_propagates_error(self, mock_wrapper_class):
        """Test error is propagated in result."""
        mock_wrapper = Mock()
        mock_wrapper.execute = AsyncMock(return_value=Mock(
            success=False,
            content=None,
            error="LLM failed",
            duration=0.5,
            messages=[],
        ))
        mock_wrapper_class.return_value = mock_wrapper
        
        manager = SessionManager()
        result = await manager.single_prompt("Test")
        
        assert result.success is False
        assert result.error == "LLM failed"


class TestSessionManagerExecuteWithTools:
    """Test execute_with_tools method."""
    
    @pytest.mark.asyncio
    @patch("autoBMAD.docuswarm.llm.session_manager.ClaudeSDKWrapper")
    async def test_execute_with_tools_includes_tool_descriptions(self, mock_wrapper_class):
        """Test tool descriptions are included in prompt."""
        mock_wrapper = Mock()
        mock_wrapper.execute = AsyncMock(return_value=Mock(
            success=True,
            content="Tool result",
            error=None,
            duration=1.0,
            messages=[],
        ))
        mock_wrapper_class.return_value = mock_wrapper
        
        manager = SessionManager()
        
        # Mock tools
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        mock_tool.description = "A test tool"
        
        await manager.execute_with_tools(
            prompt="Use the tool",
            tools=[mock_tool],
        )
        
        call_kwargs = mock_wrapper.execute.call_args.kwargs
        prompt = call_kwargs["prompt"]
        assert "Available tools:" in prompt
        assert "test_tool" in prompt
        assert "A test tool" in prompt
        assert "Use the tool" in prompt
```

### Phase 3: 实现代码

```python
# llm/claude_sdk_wrapper.py
"""Claude SDK Wrapper - Unified SDK calling interface.

Provides compatibility with epic_automation SDK patterns,
working through Kimi Code API OpenAI-compatible interface.
"""

from __future__ import annotations

import asyncio
import os
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class SDKResult:
    """SDK execution result.
    
    Compatible with epic_automation result patterns.
    """
    success: bool
    content: str | None
    error: str | None
    duration: float
    messages: list[Any] = field(default_factory=list)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    
    def is_success(self) -> bool:
        """Check if execution was successful."""
        return self.success and self.content is not None


class SDKError(Exception):
    """SDK execution error."""
    pass


class SDKNotAvailableError(SDKError):
    """SDK not available."""
    pass


# Try import claude_agent_sdk
try:
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        ToolUseBlock,
        query,
    )
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    query = None
    ResultMessage = None
    ClaudeAgentOptions = None


class SafeAsyncGenerator:
    """Safe async generator wrapper to prevent cancel scope issues."""
    
    def __init__(self, generator: AsyncIterator[Any]) -> None:
        self.generator = generator
        self._closed = False
    
    def __aiter__(self) -> SafeAsyncGenerator:
        return self
    
    async def __anext__(self) -> Any:
        if self._closed:
            raise StopAsyncIteration
        try:
            return await self.generator.__anext__()
        except StopAsyncIteration:
            self._closed = True
            raise
    
    async def aclose(self) -> None:
        if not self._closed:
            self._closed = True


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
        """Initialize wrapper.
        
        Args:
            base_url: API base URL (default: Kimi Code API)
            api_key: API key (reads from ANTHROPIC_API_KEY env var)
            permission_mode: Permission handling mode
        """
        self.base_url = base_url or os.getenv(
            "ANTHROPIC_BASE_URL",
            self.DEFAULT_BASE_URL
        )
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.permission_mode = permission_mode
        
        self._logger = logger.bind(
            component="ClaudeSDKWrapper",
            base_url=self.base_url,
        )
    
    async def execute(
        self,
        prompt: str,
        agent_name: str = "docuswarm",
        timeout: float | None = None,
        cwd: str | Path | None = None,
    ) -> SDKResult:
        """Execute SDK query.
        
        Args:
            prompt: Prompt text
            agent_name: Agent name for logging
            timeout: Timeout in seconds
            cwd: Working directory
            
        Returns:
            SDKResult with execution outcome
        """
        if not SDK_AVAILABLE or query is None:
            return SDKResult(
                success=False,
                content=None,
                error="Claude Agent SDK not available",
                duration=0.0,
            )
        
        timeout = timeout or self.DEFAULT_TIMEOUT
        start_time = time.time()
        
        self._logger.info(
            "sdk_execute_start",
            agent_name=agent_name,
            prompt_length=len(prompt),
        )
        
        try:
            # Set environment for SDK
            os.environ["ANTHROPIC_BASE_URL"] = self.base_url
            os.environ["ANTHROPIC_API_KEY"] = self.api_key
            
            # Create options
            options = ClaudeAgentOptions(
                permission_mode=self.permission_mode,
                cwd=str(cwd or Path.cwd()),
            )
            
            # Execute query
            messages: list[Any] = []
            result_content: str | None = None
            
            generator = query(prompt=prompt, options=options)
            safe_gen = SafeAsyncGenerator(generator)
            
            try:
                async for message in safe_gen:
                    messages.append(message)
                    
                    # Check for result
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
            finally:
                await safe_gen.aclose()
            
            duration = time.time() - start_time
            
            if result_content is not None:
                self._logger.info(
                    "sdk_execute_success",
                    agent_name=agent_name,
                    duration=duration,
                )
                return SDKResult(
                    success=True,
                    content=result_content,
                    error=None,
                    duration=duration,
                    messages=messages,
                )
            else:
                self._logger.warning(
                    "sdk_execute_no_result",
                    agent_name=agent_name,
                )
                return SDKResult(
                    success=False,
                    content=None,
                    error="No ResultMessage received",
                    duration=duration,
                    messages=messages,
                )
        
        except asyncio.CancelledError:
            self._logger.warning("sdk_execute_cancelled", agent_name=agent_name)
            return SDKResult(
                success=False,
                content=None,
                error="Execution cancelled",
                duration=time.time() - start_time,
            )
        except Exception as e:
            self._logger.error(
                "sdk_execute_error",
                agent_name=agent_name,
                error=str(e),
            )
            return SDKResult(
                success=False,
                content=None,
                error=str(e),
                duration=time.time() - start_time,
            )
```

```python
# llm/session_manager.py
"""Session Manager - Claude SDK based session management.

Replaces KimiSessionManager with ClaudeSDKWrapper.
Maintains backward-compatible interface.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import structlog

from autoBMAD.docuswarm.llm.claude_sdk_wrapper import (
    ClaudeSDKWrapper,
    SDKResult,
)

logger = structlog.get_logger(__name__)


class SessionManager:
    """Session manager using Claude SDK.
    
    Compatible with original KimiSessionManager interface.
    
    Example:
        >>> manager = SessionManager(work_dir=Path.cwd())
        >>> result = await manager.single_prompt("Hello!")
        >>> print(result.content)
    """
    
    def __init__(
        self,
        work_dir: Path | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
    ) -> None:
        """Initialize session manager.
        
        Args:
            work_dir: Working directory
            base_url: API base URL
            api_key: API key
        """
        self._work_dir = work_dir or Path.cwd()
        self._sdk = ClaudeSDKWrapper(
            base_url=base_url,
            api_key=api_key,
        )
        self._logger = logger.bind(
            component="SessionManager",
            work_dir=str(self._work_dir),
        )
    
    @property
    def work_dir(self) -> Path:
        """Get working directory."""
        return self._work_dir
    
    @property
    def config(self) -> dict[str, Any]:
        """Get configuration (compatibility)."""
        return {
            "base_url": self._sdk.base_url,
            "work_dir": str(self._work_dir),
        }
    
    async def single_prompt(
        self,
        prompt: str,
        mode: str = "agent",
        yolo: bool = True,
        agent_name: str = "docuswarm",
        timeout: float | None = 1800.0,
    ) -> SDKResult:
        """Execute single prompt.
        
        Args:
            prompt: Prompt text
            mode: Mode (compatibility, ignored)
            yolo: Auto-approve (compatibility, ignored)
            agent_name: Agent name
            timeout: Timeout
            
        Returns:
            SDKResult
        """
        self._logger.info(
            "single_prompt_start",
            prompt_length=len(prompt),
            agent_name=agent_name,
        )
        
        result = await self._sdk.execute(
            prompt=prompt,
            agent_name=agent_name,
            timeout=timeout,
            cwd=self._work_dir,
        )
        
        self._logger.info(
            "single_prompt_complete",
            success=result.success,
            duration=result.duration,
        )
        
        return result
    
    async def execute_with_tools(
        self,
        prompt: str,
        tools: list[Any] | None = None,
        agent_name: str = "docuswarm",
        timeout: float | None = 1800.0,
    ) -> SDKResult:
        """Execute with tool descriptions.
        
        Args:
            prompt: Base prompt
            tools: Tools to describe
            agent_name: Agent name
            timeout: Timeout
            
        Returns:
            SDKResult
        """
        if tools:
            tool_desc = "\n".join(
                f"- {t.name}: {t.description}"
                for t in tools
                if hasattr(t, "name") and hasattr(t, "description")
            )
            full_prompt = f"""Available tools:
{tool_desc}

{prompt}"""
        else:
            full_prompt = prompt
        
        return await self.single_prompt(
            prompt=full_prompt,
            agent_name=agent_name,
            timeout=timeout,
        )
    
    async def close(self) -> None:
        """Close session manager (compatibility)."""
        self._logger.debug("session_manager_closed")
    
    async def __aenter__(self) -> SessionManager:
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        await self.close()
```

---

## 4. 验收标准

| 检查项 | 标准 |
|--------|------|
| 单元测试 | `pytest tests/unit/test_claude_sdk_wrapper.py` 100% 通过 |
| 集成测试 | `pytest tests/integration/` 100% 通过 |
| 类型检查 | `basedpyright` 0 错误 |
| 代码风格 | `ruff check` 0 违反 |
| 向后兼容 | 原 `KimiSessionManager` 调用点无需修改 |
| 环境变量 | 支持 `ANTHROPIC_BASE_URL` 和 `ANTHROPIC_API_KEY` |
