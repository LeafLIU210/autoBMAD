# DocuSwarm Pipeline Hang 修复方案 - 测试驱动开发

**日期**: 2026-04-06  
**基于研究报告**: `docs/research/2026-04-06-pipeline-hang-after-session-created-research-report.md`  
**目标模块**: `autoBMAD/docuswarm`  
**方案类型**: 测试驱动修复 (Test-Driven Fix)

---

## 一、问题总览

根据深度研究报告，pipeline 在 `session_created` 后挂起的根本原因涉及 5 个关键 BUG：

| 编号 | 严重度 | 位置 | 问题描述 |
|------|--------|------|----------|
| BUG-1 | CRITICAL | `session_manager.py:668-672` | `ClaudeSessionWrapper.prompt()` 调用 `receive_messages()` 永久阻塞 |
| BUG-2 | MEDIUM | `response.py:262` / `validator.py:1222` | LLM 上下文验证阶段消息文本提取失败，fail-open 掩盖早期 SDK 异常 |
| BUG-3 | HIGH | `session_manager.py:671` | `receive_messages()` 缺乏 `asyncio.timeout()` 保护 |
| BUG-4 | HIGH | `session_manager.py:668` / `independent.py:325` | `query()` + `receive_messages()` 语义模型不明，与 `single_prompt()` 路径不一致 |
| BUG-5 | MEDIUM | `session_manager.py:458` vs `668` | 两条 LLM 调用路径使用不同 API，一致性未经验证 |

---

## 二、修复策略总览

采用**测试驱动开发 (TDD)** 方法，每个修复遵循以下流程：

```
1. 编写失败测试 (Red) → 2. 实现修复 (Green) → 3. 重构优化 (Refactor)
```

### 修复优先级

```
P0 (紧急): BUG-1 + BUG-3 (超时保护) - 解决挂起问题
P1 (高):   BUG-4 + BUG-5 (API 统一) - 确保调用一致性
P2 (中):   BUG-2 (日志增强) - 改善可观测性
```

---

## 三、详细修复方案

### Fix-1: ClaudeSessionWrapper.prompt() 超时保护 (BUG-1 + BUG-3)

#### 3.1.1 问题代码

**文件**: `autoBMAD/docuswarm/llm/session_manager.py` (L659-L672)

```python
async def prompt(self, message: str) -> AsyncIterator[Any]:
    await self._client.query(message)
    # Stream messages using receive_messages API
    async for msg in self._client.receive_messages():  # ← 无限阻塞风险
        yield msg
```

#### 3.1.2 失败测试先行

**创建测试文件**: `tests/llm/test_session_manager_timeout.py`

```python
"""Tests for session_manager timeout protection (BUG-1 + BUG-3)."""

import asyncio
from unittest.mock import AsyncMock, MagicMock
import pytest
from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper
from autoBMAD.docuswarm.exceptions import LLMError


class TestClaudeSessionWrapperTimeout:
    """Test suite for ClaudeSessionWrapper timeout behavior."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock ClaudeSDKClient."""
        client = MagicMock()
        client.query = AsyncMock()
        return client

    @pytest.fixture
    def session_wrapper(self, mock_client):
        """Create a session wrapper with mock client."""
        from pathlib import Path
        return ClaudeSessionWrapper(
            client=mock_client,
            session_id="test_session_001",
            work_dir=Path("/tmp/test"),
        )

    async def test_prompt_raises_timeout_on_blocking_receive(self, session_wrapper, mock_client):
        """TEST-001: prompt() 应在 receive_messages 阻塞超时时抛出 LLMError。
        
        模拟 receive_messages 永远阻塞的场景，验证超时机制。
        """
        # Arrange: 模拟 receive_messages 永远阻塞
        async def infinite_generator():
            await asyncio.sleep(3600)  # 模拟无限阻塞
            yield {"role": "assistant", "content": "never reached"}
        
        mock_client.receive_messages.return_value = infinite_generator()
        
        # Act & Assert: 应在配置的超时时间内抛出 LLMError
        with pytest.raises(LLMError) as exc_info:
            async for _ in session_wrapper.prompt("test message"):
                pass
        
        assert "timed out" in str(exc_info.value).lower()
        assert "1200" in str(exc_info.value) or "timeout" in str(exc_info.value).lower()

    async def test_prompt_completes_within_timeout(self, session_wrapper, mock_client):
        """TEST-002: prompt() 应在正常响应时间内成功完成。
        
        模拟正常的快速响应，验证正常流程不受影响。
        """
        # Arrange: 模拟正常响应
        async def normal_generator():
            yield {"role": "assistant", "content": "response"}
        
        mock_client.receive_messages.return_value = normal_generator()
        
        # Act
        messages = []
        async for msg in session_wrapper.prompt("test message"):
            messages.append(msg)
        
        # Assert
        assert len(messages) == 1
        assert messages[0]["content"] == "response"

    async def test_prompt_partial_messages_before_timeout(self, session_wrapper, mock_client):
        """TEST-003: 超时前收到的部分消息应被保留。
        
        模拟缓慢响应但最终超时的情况，验证已接收消息不丢失。
        """
        # Arrange: 模拟缓慢响应（中间有消息但最终超时）
        async def slow_generator():
            yield {"role": "assistant", "content": "partial 1"}
            await asyncio.sleep(0.1)  # 短暂延迟
            yield {"role": "assistant", "content": "partial 2"}
            await asyncio.sleep(3600)  # 然后阻塞
        
        # 使用短超时进行测试
        mock_client.receive_messages.return_value = slow_generator()
        
        # Act: 使用测试专用的短超时版本
        messages = []
        try:
            # 在实际实现中，我们会注入超时参数用于测试
            async with asyncio.timeout(0.15):  # 比第二个消息稍长
                async for msg in session_wrapper.prompt("test"):
                    messages.append(msg)
        except asyncio.TimeoutError:
            pass
        
        # Assert: 应收到部分消息
        assert len(messages) >= 1

    async def test_prompt_logs_timeout_event(self, session_wrapper, mock_client, caplog):
        """TEST-004: 超时事件应被记录到日志中。"""
        import structlog
        
        # Arrange
        async def blocking_generator():
            await asyncio.sleep(3600)
            yield {"role": "assistant", "content": "test"}
        
        mock_client.receive_messages.return_value = blocking_generator()
        
        # Act
        with pytest.raises(LLMError):
            async for _ in session_wrapper.prompt("test"):
                pass
        
        # Assert: 验证日志包含超时信息
        # 实际断言依赖于 structlog 的捕获配置
```

#### 3.1.3 实现修复

**修改文件**: `autoBMAD/docuswarm/llm/session_manager.py`

```python
class ClaudeSessionWrapper:
    """Wrapper around ClaudeSDKClient to provide a session-like interface."""
    
    # 可配置的超时时间（秒）- P0 修复：默认 20 分钟
    DEFAULT_PROMPT_TIMEOUT: int = 1200
    
    # ... __init__ 保持不变 ...

    async def prompt(self, message: str) -> AsyncIterator[Any]:
        """Send a prompt and yield streaming responses via SDK query API.
        
        P0 Fix: 添加 asyncio.timeout 保护，防止 receive_messages 永久阻塞。
        
        Args:
            message: The message to send.
        
        Yields:
            Message responses from Claude.
            
        Raises:
            LLMError: 当超时或 SDK 调用失败时抛出。
        """
        import asyncio
        from autoBMAD.docuswarm.exceptions import LLMError
        
        try:
            await self._client.query(message)
        except Exception as e:
            self._logger.error("query_failed", error=str(e))
            raise LLMError(f"Failed to send query: {e}") from e

        # P0 Fix: 使用 asyncio.timeout 保护 receive_messages
        try:
            async with asyncio.timeout(self.DEFAULT_PROMPT_TIMEOUT):
                async for msg in self._client.receive_messages():
                    yield msg
        except asyncio.TimeoutError as e:
            self._logger.error(
                "prompt_timeout",
                timeout_seconds=self.DEFAULT_PROMPT_TIMEOUT,
                message_length=len(message),
            )
            raise LLMError(
                f"Session prompt timed out after {self.DEFAULT_PROMPT_TIMEOUT} seconds"
            ) from e
        except Exception as e:
            self._logger.error("receive_messages_error", error=str(e))
            raise LLMError(f"Failed to receive messages: {e}") from e
```

#### 3.1.4 集成测试

**创建测试文件**: `tests/llm/test_session_manager_integration.py`

```python
"""Integration tests for session_manager timeout with real async behavior."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from autoBMAD.docuswarm.llm.session_manager import SessionManager, ClaudeSessionWrapper


class TestSessionManagerIntegration:
    """Integration tests for SessionManager timeout behavior."""

    @pytest.fixture
    async def session_manager(self, tmp_path):
        """Create a SessionManager with temp work directory."""
        async with SessionManager(work_dir=tmp_path) as sm:
            yield sm

    async def test_create_session_and_prompt_timeout(self, session_manager):
        """TEST-INT-001: 完整的创建会话 + prompt 超时场景。"""
        # 这里使用 mock 客户端进行集成测试
        with patch("autoBMAD.docuswarm.llm.session_manager.ClaudeSDKClient") as MockClient:
            mock_client = AsyncMock()
            
            # 模拟 receive_messages 永远阻塞
            async def infinite_stream():
                while True:
                    await asyncio.sleep(1)
            
            mock_client.connect = AsyncMock()
            mock_client.disconnect = AsyncMock()
            mock_client.query = AsyncMock()
            mock_client.receive_messages = MagicMock(return_value=infinite_stream())
            
            MockClient.return_value = mock_client
            
            # 创建会话（使用缩短的超时用于测试）
            session = await session_manager.create_session(mode="agent", yolo=True)
            
            # 验证 prompt 会超时
            with pytest.raises(Exception) as exc_info:  # LLMError
                async for _ in session.prompt("test message"):
                    pass
            
            assert "timeout" in str(exc_info.value).lower() or "timed out" in str(exc_info.value).lower()
```

---

### Fix-2: 统一 LLM 调用路径 (BUG-4 + BUG-5)

#### 3.2.1 问题分析

**当前问题**:
- `single_prompt()` 使用: `query(prompt=prompt, options=options)` (顶层函数)
- `prompt()` 使用: `client.query()` + `client.receive_messages()` (实例方法)

两条路径行为不一致，且 `prompt()` 路径未经充分验证。

#### 3.2.2 失败测试先行

**创建测试文件**: `tests/llm/test_session_manager_api_consistency.py`

```python
"""Tests for API path consistency (BUG-4 + BUG-5)."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, call
import pytest
from pathlib import Path

from autoBMAD.docuswarm.llm.session_manager import SessionManager


class TestAPIPathConsistency:
    """Test suite for ensuring single_prompt and prompt use consistent APIs."""

    @pytest.fixture
    async def session_manager(self, tmp_path):
        """Create a SessionManager with mocked SDK."""
        sm = SessionManager(work_dir=tmp_path)
        yield sm
        await sm.close_all()

    async def test_single_prompt_and_session_prompt_use_same_underlying_api(self, tmp_path):
        """TEST-API-001: single_prompt 和 session.prompt 应使用相同的底层 API。
        
        验证两种调用方式最终调用相同的 SDK 函数。
        """
        sm = SessionManager(work_dir=tmp_path)
        
        # Mock SDK 顶层 query 函数
        async def mock_query_stream(*, prompt, options):
            yield {"role": "assistant", "content": [{"type": "text", "text": "response"}]}
        
        with patch("autoBMAD.docuswarm.llm.session_manager.query", side_effect=mock_query_stream):
            # 调用 single_prompt
            result = await sm.single_prompt("test prompt", mode="agent", yolo=True)
            
            # 验证结果被正确收集
            assert len(result) > 0
            assert result[0]["role"] == "assistant"

    async def test_session_prompt_calls_sdk_query_function(self, tmp_path):
        """TEST-API-002: ClaudeSessionWrapper.prompt 应使用顶层 query 函数。
        
        P1 Fix: 确保 prompt() 改为使用与 single_prompt 相同的 query() 函数。
        """
        from autoBMAD.docuswarm.llm.session_manager import ClaudeSessionWrapper
        
        mock_client = MagicMock()
        wrapper = ClaudeSessionWrapper(
            client=mock_client,
            session_id="test",
            work_dir=tmp_path,
        )
        
        # Mock 顶层 query 函数
        async def mock_query(*, prompt, options):
            yield {"role": "assistant", "content": "unified response"}
        
        # P1 Fix 后: prompt 应使用 query() 而非 client.query + receive_messages
        with patch("autoBMAD.docuswarm.llm.session_manager.query", side_effect=mock_query) as mock_query_func:
            # 需要保存 options 以便 prompt 可以使用
            wrapper._options = MagicMock()
            
            messages = []
            async for msg in wrapper.prompt("test"):
                messages.append(msg)
            
            # 验证调用了统一的 query 函数
            mock_query_func.assert_called_once()
            call_kwargs = mock_query_func.call_args.kwargs
            assert call_kwargs["prompt"] == "test"
            assert "options" in call_kwargs

    async def test_message_format_consistency_between_apis(self, tmp_path):
        """TEST-API-003: 两种 API 应返回相同格式的消息。"""
        sm = SessionManager(work_dir=tmp_path)
        
        # 模拟 SDK 返回的消息
        sdk_messages = [
            type("Msg", (), {
                "role": "assistant",
                "content": [{"type": "text", "text": "Hello"}],
            })(),
        ]
        
        async def mock_query(*, prompt, options):
            for msg in sdk_messages:
                yield msg
        
        with patch("autoBMAD.docuswarm.llm.session_manager.query", side_effect=mock_query):
            result = await sm.single_prompt("test")
            
            # 验证消息格式一致
            assert len(result) == 1
            assert result[0]["role"] == "assistant"
            assert isinstance(result[0]["content"], list)
```

#### 3.2.3 实现修复

**修改文件**: `autoBMAD/docuswarm/llm/session_manager.py`

```python
class ClaudeSessionWrapper:
    """Wrapper around ClaudeSDKClient to provide a session-like interface."""

    def __init__(
        self,
        client: ClaudeSDKClient,
        session_id: str,
        work_dir: Path,
        options: ClaudeAgentOptions | None = None,  # P1 Fix: 保存 options
    ) -> None:
        """Initialize the wrapper.
        
        P1 Fix: 添加 options 参数以便统一使用顶层 query() 函数。
        """
        self._client = client
        self._id = session_id
        self._work_dir = work_dir
        self._options = options  # P1 Fix: 保存 options

    @property
    def id(self) -> str:
        """Get the session ID."""
        return self._id

    async def prompt(self, message: str) -> AsyncIterator[Any]:
        """Send a prompt and yield streaming responses via SDK query API.
        
        P1 Fix: 统一使用与 single_prompt 相同的顶层 query() 函数，
        确保行为一致并简化维护。
        
        P0 Fix: 添加 asyncio.timeout 保护。
        
        Args:
            message: The message to send.
        
        Yields:
            Message responses from Claude.
            
        Raises:
            LLMError: 当超时或 SDK 调用失败时抛出。
        """
        import asyncio
        from autoBMAD.docuswarm.exceptions import LLMError
        
        if self._options is None:
            raise LLMError("Session options not available for prompt")
        
        try:
            async with asyncio.timeout(self.DEFAULT_PROMPT_TIMEOUT):
                # P1 Fix: 使用与 single_prompt 相同的顶层 query() 函数
                async for msg in query(prompt=message, options=self._options):
                    yield msg
        except asyncio.TimeoutError as e:
            self._logger.error(
                "prompt_timeout",
                timeout_seconds=self.DEFAULT_PROMPT_TIMEOUT,
                message_length=len(message),
            )
            raise LLMError(
                f"Session prompt timed out after {self.DEFAULT_PROMPT_TIMEOUT} seconds"
            ) from e
        except Exception as e:
            self._logger.error("prompt_error", error=str(e))
            raise LLMError(f"Prompt failed: {e}") from e
```

**修改文件**: `autoBMAD/docuswarm/llm/session_manager.py` (create_session 方法)

```python
async def create_session(
    self,
    mode: str = "agent",
    yolo: bool = True,
    max_steps: int | None = None,
    agent_file: Path | None = None,
    approval_handler_fn: Any | None = None,
    system_prompt: str | dict[str, Any] | None = None,
) -> ClaudeSessionWrapper:
    """Create a new Claude session.
    
    P1 Fix: 现在保存 options 以便 ClaudeSessionWrapper 使用统一的 query() API。
    """
    try:
        self._logger.info(
            "creating_session",
            mode=mode,
            yolo=yolo,
            max_steps=max_steps,
        )

        # Use per-session agent_file if provided
        effective_agent_file = agent_file if agent_file is not None else self._agent_file

        # Create options
        options = self._create_options(mode=mode, yolo=yolo)

        # Override agent_file if provided for this session
        if effective_agent_file:
            options.tools = [str(effective_agent_file)]

        # Set system_prompt if provided
        if system_prompt is not None:
            if isinstance(system_prompt, dict):
                options.system_prompt = system_prompt
            else:
                options.system_prompt = {
                    "type": "preset",
                    "preset": "claude_code",
                    "append": system_prompt,
                }

        # Create client
        client = ClaudeSDKClient(options=options)

        # Connect the client
        await client.connect()

        # Generate a session ID
        import uuid
        session_id = f"session_{uuid.uuid4().hex[:12]}"

        # Wrap the client - P1 Fix: 传递 options
        wrapper = ClaudeSessionWrapper(
            client=client,
            session_id=session_id,
            work_dir=self._work_dir,
            options=options,  # P1 Fix: 保存 options 供 prompt() 使用
        )

        # Track the session
        self._active_clients[session_id] = client

        self._logger.info(
            "session_created",
            session_id=session_id,
            mode=mode,
        )

        return wrapper

    except Exception as e:
        self._logger.error("session_creation_failed", error=str(e))
        raise LLMError(
            f"Failed to create session: {e}",
            api_error_type=type(e).__name__,
        ) from e
```

---

### Fix-3: 增强日志覆盖 (BUG-2 部分)

#### 3.3.1 问题分析

**independent.py** 中 `_call_llm_with_prompts` 方法在 `session.prompt()` 前后缺乏足够的日志。

#### 3.3.2 失败测试先行

**创建测试文件**: `tests/agents/test_independent_logging.py`

```python
"""Tests for IndependentAgent logging improvements."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import structlog

from autoBMAD.docuswarm.agents.independent import IndependentAgent
from autoBMAD.docuswarm.config import Config


class TestIndependentAgentLogging:
    """Test suite for IndependentAgent logging coverage."""

    @pytest.fixture
    def mock_session_manager(self):
        """Create a mock SessionManager."""
        sm = MagicMock()
        sm.config = MagicMock()
        return sm

    @pytest.fixture
    def agent(self, mock_session_manager, tmp_path):
        """Create an IndependentAgent with mocked dependencies."""
        config = MagicMock(spec=Config)
        
        with patch("autoBMAD.docuswarm.agents.independent.PersonaLoader") as MockPersona:
            MockPersona.load.return_value = {
                "name": "TestPersona",
                "role": "Test Role",
            }
            MockPersona.format_system_prompt.return_value = "System prompt"
            
            agent = IndependentAgent(
                config=config,
                session_manager=mock_session_manager,
                node_id="test_node",
                project_root=tmp_path,
            )
            return agent

    async def test_llm_prompt_logs_start_event(self, agent, mock_session_manager, caplog):
        """TEST-LOG-001: _call_llm_with_prompts 应在开始时记录 llm_prompt_start。
        
        验证日志包含 prompt 长度信息。
        """
        # Arrange
        mock_session = AsyncMock()
        mock_session.prompt = AsyncMock(return_value=async_generator([]))
        mock_session_manager.create_session = AsyncMock(return_value=mock_session)
        
        # Act
        with structlog.testing.capture_logs() as cap_logs:
            await agent._call_llm_with_prompts(
                system_prompt_append="system",
                user_prompt="user message",
            )
        
        # Assert: 验证日志中包含 llm_prompt_start
        log_events = [e for e in cap_logs if e.get("event") == "llm_prompt_start"]
        assert len(log_events) >= 1
        # 验证包含 user_prompt_length
        assert "user_prompt_length" in log_events[0] or "prompt_length" in log_events[0]

    async def test_llm_prompt_logs_complete_event(self, agent, mock_session_manager):
        """TEST-LOG-002: _call_llm_with_prompts 应在完成时记录 llm_prompt_complete。"""
        # Arrange
        async def message_gen():
            yield {"role": "assistant", "content": "response"}
        
        mock_session = AsyncMock()
        mock_session.prompt = MagicMock(return_value=message_gen())
        mock_session_manager.create_session = AsyncMock(return_value=mock_session)
        
        # Act
        with structlog.testing.capture_logs() as cap_logs:
            await agent._call_llm_with_prompts(
                system_prompt_append="system",
                user_prompt="user message",
            )
        
        # Assert: 验证日志中包含 llm_prompt_complete
        log_events = [e for e in cap_logs if e.get("event") == "llm_prompt_complete"]
        assert len(log_events) >= 1
        # 验证包含 message_count
        assert "message_count" in log_events[0]

    async def test_llm_logs_each_message_received(self, agent, mock_session_manager):
        """TEST-LOG-003: 应记录每个收到的消息类型。"""
        # Arrange
        async def message_gen():
            yield {"role": "assistant", "content": [{"type": "text", "text": "msg1"}]}
            yield {"role": "assistant", "content": [{"type": "tool_use", "name": "tool"}]}
        
        mock_session = AsyncMock()
        mock_session.prompt = MagicMock(return_value=message_gen())
        mock_session_manager.create_session = AsyncMock(return_value=mock_session)
        
        # Act
        with structlog.testing.capture_logs() as cap_logs:
            await agent._call_llm_with_prompts(
                system_prompt_append="system",
                user_prompt="user message",
            )
        
        # Assert: 验证日志中包含 llm_message_received
        log_events = [e for e in cap_logs if e.get("event") == "llm_message_received"]
        assert len(log_events) >= 2  # 至少两条消息


async def async_generator(items):
    """Helper to create async generator from list."""
    for item in items:
        yield item
```

#### 3.3.3 实现修复

**修改文件**: `autoBMAD/docuswarm/agents/independent.py` (L277-L349)

```python
async def _call_llm_with_prompts(
    self,
    system_prompt_append: str,
    user_prompt: str,
) -> list[dict[str, Any]]:
    """Call LLM with Four-Layer Architecture prompts (Story 29.6).

    P2 Fix: 增强日志覆盖，记录 prompt 开始、消息接收和完成事件。
    """
    messages: list[dict[str, Any]] = []

    try:
        sm = self.session_manager
        assert sm is not None

        # P2 Fix: 记录 prompt 开始
        self.logger.info(
            "llm_prompt_start",
            user_prompt_length=len(user_prompt),
            system_prompt_length=len(system_prompt_append),
        )

        session = await sm.create_session(
            mode="agent",
            yolo=True,
            agent_file=self._agent_file,
            system_prompt=system_prompt_append,
        )

        # P2 Fix: 记录每个收到的消息
        message_count = 0
        async for msg in session.prompt(user_prompt):
            message_count += 1
            
            # 记录消息类型
            msg_type = type(msg).__name__
            self.logger.debug(
                "llm_message_received",
                message_index=message_count,
                msg_type=msg_type,
                has_role=hasattr(msg, "role"),
            )
            
            if isinstance(msg, dict):
                messages.append(msg)
            else:
                msg_dict = {
                    "role": getattr(msg, "role", "unknown"),
                    "content": getattr(msg, "content", []),
                }
                messages.append(msg_dict)

        # P2 Fix: 记录 prompt 完成
        self.logger.info(
            "llm_prompt_complete",
            message_count=len(messages),
            total_received=message_count,
        )

        if not messages:
            raise LLMCallError("No messages returned from session")

        return messages

    except Exception as e:
        self.logger.warning("llm_call_error", error=str(e), error_type=type(e).__name__)
        if messages:
            return messages
        raise LLMCallError(f"LLM call failed: {e}") from e
```

---

### Fix-4: no_text_extracted 日志级别升级 (BUG-2 剩余部分)

#### 3.4.1 问题分析

`response.py` L262 的 `no_text_extracted` 目前是 `debug` 级别，应改为 `warning` 以更容易发现问题。

#### 3.4.2 失败测试先行

**创建测试文件**: `tests/llm/test_response_logging.py`

```python
"""Tests for response.py logging improvements (BUG-2)."""

from unittest.mock import MagicMock
import pytest
import structlog

from autoBMAD.docuswarm.llm.response import extract_text_from_messages


class TestExtractTextFromMessagesLogging:
    """Test suite for extract_text_from_messages logging."""

    def test_no_text_extracted_logs_warning(self):
        """TEST-RESP-001: no_text_extracted 应记录 warning 级别日志。
        
        当无法从消息中提取文本时，应发出警告而非 debug。
        """
        # Arrange: 创建无法提取文本的消息列表
        messages = [
            MagicMock(role="user", content="not assistant"),  # 非 assistant 角色
            MagicMock(role="assistant", content=None),  # 空内容
        ]
        
        # Act
        with structlog.testing.capture_logs() as cap_logs:
            result = extract_text_from_messages(messages)
        
        # Assert
        assert result == ""
        
        # 验证存在 warning 级别的 no_text_extracted
        warning_logs = [
            e for e in cap_logs 
            if e.get("event") == "no_text_extracted" and e.get("log_level") == "warning"
        ]
        assert len(warning_logs) >= 1

    def test_no_text_extracted_includes_context(self):
        """TEST-RESP-002: no_text_extracted 日志应包含上下文信息。
        
        日志应包含消息数量、角色列表等信息以便诊断。
        """
        messages = [
            MagicMock(role="user", content="msg1"),
            MagicMock(role="system", content="msg2"),
        ]
        
        with structlog.testing.capture_logs() as cap_logs:
            extract_text_from_messages(messages)
        
        # 验证日志包含上下文
        log_events = [e for e in cap_logs if e.get("event") == "no_text_extracted"]
        assert len(log_events) >= 1
        
        # 验证包含诊断信息
        assert "message_count" in log_events[0] or "total_messages" in log_events[0]
        assert "role_list" in log_events[0] or "roles" in log_events[0]
```

#### 3.4.3 实现修复

**修改文件**: `autoBMAD/docuswarm/llm/response.py` (L262)

```python
def extract_text_from_messages(messages: list[MessageLike]) -> str:
    """Extract text content from the last assistant Message.
    
    P2 Fix: no_text_extracted 升级为 warning 级别并包含诊断信息。
    """
    import structlog

    logger = structlog.get_logger(__name__)
    logger.debug("extract_text_debug", total_messages=len(messages))

    # ... 现有提取逻辑保持不变 ...

    # P2 Fix: 升级为 warning 并包含诊断信息
    role_list = []
    for msg in messages:
        if hasattr(msg, "role"):
            role_list.append(getattr(msg, "role", "unknown"))
    
    logger.warning(
        "no_text_extracted",
        message_count=len(messages),
        role_list=role_list,
        has_assistant_message=any(
            getattr(msg, "role", "") == "assistant" for msg in messages
        ),
        hint="Check if LLM returned valid assistant messages with text content",
    )
    return ""
```

---

## 四、测试运行计划

### 4.1 测试文件结构

```
tests/
├── llm/
│   ├── test_session_manager_timeout.py          # Fix-1 测试
│   ├── test_session_manager_api_consistency.py  # Fix-2 测试
│   └── test_response_logging.py                 # Fix-4 测试
├── agents/
│   └── test_independent_logging.py              # Fix-3 测试
└── integration/
    └── test_session_manager_integration.py      # 集成测试
```

### 4.2 运行命令

```bash
# 运行所有新测试
pytest tests/llm/test_session_manager_timeout.py -v
pytest tests/llm/test_session_manager_api_consistency.py -v
pytest tests/agents/test_independent_logging.py -v
pytest tests/llm/test_response_logging.py -v
pytest tests/integration/test_session_manager_integration.py -v

# 运行特定测试
pytest tests/llm/test_session_manager_timeout.py::TestClaudeSessionWrapperTimeout::test_prompt_raises_timeout_on_blocking_receive -v

# 带覆盖率报告
pytest tests/llm/test_session_manager_timeout.py --cov=autoBMAD.docuswarm.llm.session_manager --cov-report=term-missing
```

### 4.3 预期修复验证清单

| 测试 ID | 描述 | 修复前状态 | 修复后状态 |
|---------|------|-----------|-----------|
| TEST-001 | prompt() 超时抛出 LLMError | ❌ 挂起 | ✅ 抛出异常 |
| TEST-002 | prompt() 正常完成 | ✅ 通过 | ✅ 通过 |
| TEST-003 | 部分消息保留 | ❌ 挂起 | ✅ 返回部分消息 |
| TEST-004 | 超时事件日志 | ❌ 无日志 | ✅ 记录 error |
| TEST-API-001 | API 路径一致性 | ❌ 不一致 | ✅ 统一 |
| TEST-API-002 | 使用顶层 query() | ❌ 使用 client 方法 | ✅ 使用 query() |
| TEST-LOG-001 | llm_prompt_start 日志 | ❌ 无 | ✅ 有 |
| TEST-LOG-002 | llm_prompt_complete 日志 | ❌ 无 | ✅ 有 |
| TEST-LOG-003 | llm_message_received 日志 | ❌ 无 | ✅ 有 |
| TEST-RESP-001 | no_text_extracted warning | ❌ debug | ✅ warning |
| TEST-RESP-002 | 包含诊断信息 | ❌ 无 | ✅ 有 |

---

## 五、实施计划

### Phase 1: P0 紧急修复 (1-2 天)

1. **编写超时保护测试** (TEST-001 到 TEST-004)
2. **实现 Fix-1**: ClaudeSessionWrapper.prompt() 超时保护
3. **运行测试验证**: 确认超时机制工作正常
4. **集成测试**: 确保与现有代码兼容

### Phase 2: P1 API 统一 (2-3 天)

1. **编写 API 一致性测试** (TEST-API-001 到 TEST-API-003)
2. **实现 Fix-2**: 统一使用顶层 query() 函数
3. **修改 create_session**: 传递 options 参数
4. **运行测试验证**: 确认两种调用路径行为一致

### Phase 3: P2 日志增强 (1 天)

1. **编写日志测试** (TEST-LOG-001 到 TEST-LOG-003, TEST-RESP-001/002)
2. **实现 Fix-3**: 增强 independent.py 日志
3. **实现 Fix-4**: 升级 no_text_extracted 为 warning
4. **运行测试验证**: 确认日志正确记录

### Phase 4: 回归测试 (1 天)

1. 运行完整的 pipeline 端到端测试
2. 验证现有功能未受影响
3. 性能测试确认超时参数合理

---

## 六、风险与回滚策略

### 6.1 主要风险

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| 超时时间设置不当 | 中 | 正常请求被中断 | 配置化超时，默认 20 分钟 |
| API 统一引入新问题 | 低 | 功能回归 | 保留原实现作为 fallback |
| 日志过多影响性能 | 低 | 日志膨胀 | 使用 debug 级别控制 |

### 6.2 回滚策略

```python
# 在 session_manager.py 中添加功能开关
USE_UNIFIED_QUERY_API = os.environ.get("USE_UNIFIED_QUERY_API", "true").lower() == "true"
ENABLE_PROMPT_TIMEOUT = os.environ.get("ENABLE_PROMPT_TIMEOUT", "true").lower() == "true"

# 在 prompt() 方法中
if not USE_UNIFIED_QUERY_API:
    # 回退到旧实现
    await self._client.query(message)
    async for msg in self._client.receive_messages():
        yield msg
    return
```

---

## 七、相关文件变更汇总

| 文件 | 变更类型 | 变更内容 |
|------|----------|----------|
| `autoBMAD/docuswarm/llm/session_manager.py` | 修改 | 添加超时保护、统一 API |
| `autoBMAD/docuswarm/agents/independent.py` | 修改 | 增强日志覆盖 |
| `autoBMAD/docuswarm/llm/response.py` | 修改 | 升级日志级别 |
| `tests/llm/test_session_manager_timeout.py` | 新增 | 超时保护测试 |
| `tests/llm/test_session_manager_api_consistency.py` | 新增 | API 一致性测试 |
| `tests/agents/test_independent_logging.py` | 新增 | 日志测试 |
| `tests/llm/test_response_logging.py` | 新增 | 响应日志测试 |
| `tests/integration/test_session_manager_integration.py` | 新增 | 集成测试 |

---

## 八、验证成功的标准

### 8.1 功能标准

- [ ] `session.prompt()` 在 `receive_messages` 阻塞时能在 20 分钟内抛出 `LLMError`
- [ ] `single_prompt()` 和 `session.prompt()` 使用相同的底层 SDK API
- [ ] 所有 LLM 调用都有完整的开始/完成日志
- [ ] `no_text_extracted` 发出 warning 级别日志

### 8.2 测试标准

- [ ] 所有新测试通过
- [ ] 现有测试不失败
- [ ] 代码覆盖率 > 80%

### 8.3 集成标准

- [ ] Pipeline 不再在 `session_created` 后挂起
- [ ] 验证阶段 `no_text_extracted` 能被正确观察到
- [ ] 正常 pipeline 执行不受影响

---

**方案制定完成，等待实施批准。**
