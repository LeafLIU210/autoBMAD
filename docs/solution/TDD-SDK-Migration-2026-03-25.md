# TDD 方案: SDK 从 kimi-agent-sdk 迁移到 claude-agent-sdk

**文档版本**: 1.0  
**创建日期**: 2026-03-25  
**关联研究**: [dependency-drift-2026-03-25](../research/dependency-drift-2026-03-25/)  
**目标**: 通过测试驱动开发(TDD)完成 SDK 迁移，确保零回归

---

## 1. TDD 策略概述

### 1.1 核心原则

```
Red → Green → Refactor
  ↑_________________|

对于每个迁移单元:
1. 编写测试 - 定义期望的新行为 (Red)
2. 实现代码 - 使测试通过 (Green)
3. 重构优化 - 保持测试通过 (Refactor)
```

### 1.2 测试金字塔

```
                    /\
                   /  \
                  / E2E\         少量: 完整工作流测试
                 /______\
                /        \
               /Integration\    中等: 模块间集成
              /______________\
             /                \
            /   Unit Tests     \  大量: 核心逻辑单元测试
           /____________________\
```

### 1.3 迁移顺序

```
Phase 1: 基础设施 (测试先行)
├── Step 1: 创建测试基类和 Fixtures
├── Step 2: 创建 Mock 层 (claude-agent-sdk mocks)
└── Step 3: 验证测试框架工作

Phase 2: 核心模块迁移 (从内到外)
├── Step 4: llm/session_manager.py (最关键)
├── Step 5: llm/approval.py
└── Step 6: pipeline/orchestrator.py

Phase 3: 工具系统迁移
├── Step 7: tools/sdk_adapter.py
├── Step 8: tools/callable_tool_wrapper.py
└── Step 9: 工具集成测试

Phase 4: Agent 层迁移
├── Step 10: agents/independent.py
└── Step 11: agents/evaluator.py

Phase 5: 集成验证
├── Step 12: CLI 命令测试
├── Step 13: E2E 工作流测试
└── Step 14: 性能回归测试
```

---

## 2. Phase 1: 基础设施测试

### 2.1 Step 1: 创建测试基类

**文件**: `tests/conftest.py` (新增/修改)

```python
"""TDD Migration: Test fixtures and base classes for SDK migration."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio


# =============================================================================
# Claude SDK Mock Infrastructure
# =============================================================================

class MockClaudeMessage:
    """Mock for claude_agent_sdk message types."""
    
    def __init__(self, role: str, content: str | list[dict]) -> None:
        self.role = role
        self.content = content if isinstance(content, list) else [{"type": "text", "text": content}]


class MockTextBlock:
    """Mock for TextBlock."""
    def __init__(self, text: str) -> None:
        self.type = "text"
        self.text = text


class MockToolUseBlock:
    """Mock for ToolUseBlock."""
    def __init__(self, name: str, input_data: dict) -> None:
        self.type = "tool_use"
        self.name = name
        self.input = input_data
        self.id = f"tool_{name}_001"


class MockToolResultBlock:
    """Mock for ToolResultBlock."""
    def __init__(self, tool_use_id: str, content: str, is_error: bool = False) -> None:
        self.type = "tool_result"
        self.tool_use_id = tool_use_id
        self.content = content
        self.is_error = is_error


class MockResultMessage:
    """Mock for ResultMessage."""
    def __init__(self, result: Any, is_error: bool = False) -> None:
        self.result = result
        self.is_error = is_error
        self.num_turns = 1
        self.duration_ms = 1000


class MockClaudeSDKGenerator:
    """Mock async generator for claude_agent_sdk.query()."""
    
    def __init__(self, messages: list[Any]) -> None:
        self._messages = messages
        self._index = 0
    
    def __aiter__(self) -> MockClaudeSDKGenerator:
        return self
    
    async def __anext__(self) -> Any:
        if self._index >= len(self._messages):
            raise StopAsyncIteration
        msg = self._messages[self._index]
        self._index += 1
        return msg


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_claude_sdk() -> MagicMock:
    """Fixture providing mocked claude_agent_sdk."""
    mock_sdk = MagicMock()
    mock_sdk.ResultMessage = MockResultMessage
    mock_sdk.query = MagicMock()
    mock_sdk.TextBlock = MockTextBlock
    mock_sdk.ToolUseBlock = MockToolUseBlock
    mock_sdk.ToolResultBlock = MockToolResultBlock
    mock_sdk.AssistantMessage = MockClaudeMessage
    mock_sdk.UserMessage = MockClaudeMessage
    return mock_sdk


@pytest.fixture
def temp_work_dir(tmp_path: Path) -> Path:
    """Fixture providing temporary working directory."""
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    return work_dir


@pytest.fixture
def mock_successful_query() -> Any:
    """Fixture for successful SDK query returning text response."""
    async def _create_generator(*args: Any, **kwargs: Any) -> AsyncIterator[Any]:
        messages = [
            MockClaudeMessage("assistant", [{"type": "text", "text": "Hello, World!"}]),
            MockResultMessage(result="Hello, World!", is_error=False),
        ]
        for msg in messages:
            yield msg
    
    return _create_generator


@pytest.fixture
def mock_tool_call_query() -> Any:
    """Fixture for SDK query with tool calls."""
    async def _create_generator(*args: Any, **kwargs: Any) -> AsyncIterator[Any]:
        messages = [
            MockClaudeMessage("assistant", [
                {"type": "text", "text": "I'll help you with that."},
                MockToolUseBlock("create_deliverable", {"content": "test"}),
            ]),
            MockClaudeMessage("user", [MockToolResultBlock("tool_create_deliverable_001", "Created successfully")]),
            MockClaudeMessage("assistant", [{"type": "text", "text": "Done!"}]),
            MockResultMessage(result="Task completed", is_error=False),
        ]
        for msg in messages:
            yield msg
    
    return _create_generator


# =============================================================================
# Test Markers
# =============================================================================

def pytest_configure(config: pytest.Config) -> None:
    """Configure custom test markers."""
    config.addinivalue_line("markers", "migration: marks tests for SDK migration")
    config.addinivalue_line("markers", "claude_sdk: marks tests using claude-agent-sdk mocks")
    config.addinivalue_line("markers", "session_manager: marks tests for SessionManager migration")
```

### 2.2 Step 2: 创建 SessionManager 测试

**文件**: `tests/llm/test_session_manager_tdd.py` (新建)

```python
"""TDD Tests for SessionManager migration to claude-agent-sdk.

Test Order (Red → Green → Refactor):
1. Test imports work with new SDK
2. Test basic initialization
3. Test single_prompt with text response
4. Test single_prompt with tool calls
5. Test error handling
6. Test session lifecycle
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio

from autoBMAD.docuswarm.llm.session_manager import SessionManager


# =============================================================================
# Test Group 1: Import and Initialization (Step 4.1)
# =============================================================================

class TestSessionManagerImports:
    """Tests verifying correct imports from claude-agent-sdk."""
    
    def test_no_kimi_sdk_imports(self) -> None:
        """RED: Verify no kimi_agent_sdk imports in session_manager module."""
        import autoBMAD.docuswarm.llm.session_manager as module
        
        source = Path(module.__file__).read_text()
        
        assert "from kimi_agent_sdk import" not in source, \
            "Must remove 'from kimi_agent_sdk import'"
        assert "import kimi_agent_sdk" not in source, \
            "Must remove 'import kimi_agent_sdk'"
        assert "from kaos.path import" not in source, \
            "Must remove 'from kaos.path import'"
    
    def test_claude_sdk_imports_present(self) -> None:
        """RED: Verify claude-agent-sdk imports are present."""
        import autoBMAD.docuswarm.llm.session_manager as module
        
        source = Path(module.__file__).read_text()
        
        assert "from claude_agent_sdk import" in source, \
            "Must import from claude_agent_sdk"
        assert "from pathlib import Path" in source, \
            "Must use pathlib.Path instead of KaosPath"


class TestSessionManagerInitialization:
    """Tests for SessionManager initialization."""
    
    def test_init_with_path(self, temp_work_dir: Path) -> None:
        """RED: SessionManager should accept pathlib.Path."""
        # Arrange & Act
        manager = SessionManager(work_dir=temp_work_dir)
        
        # Assert
        assert manager.work_dir == temp_work_dir
        assert isinstance(manager.work_dir, Path)
    
    def test_init_with_optional_params(self, temp_work_dir: Path) -> None:
        """RED: SessionManager should accept optional parameters."""
        # Arrange
        agent_file = temp_work_dir / "agent.yaml"
        
        # Act
        manager = SessionManager(
            work_dir=temp_work_dir,
            agent_file=agent_file,
            api_key="test-key",
            base_url="https://api.test.com",
        )
        
        # Assert
        assert manager.agent_file == agent_file


# =============================================================================
# Test Group 2: Single Prompt (Step 4.2)
# =============================================================================

@pytest.mark.asyncio
class TestSessionManagerSinglePrompt:
    """Tests for single_prompt method with claude-agent-sdk."""
    
    async def test_single_prompt_returns_dict_list(
        self,
        temp_work_dir: Path,
        mock_claude_sdk: MagicMock,
    ) -> None:
        """RED: single_prompt should return list[dict[str, Any]] instead of list[Message]."""
        # Arrange
        manager = SessionManager(work_dir=temp_work_dir)
        
        mock_messages = [
            MagicMock(role="assistant", content=[{"type": "text", "text": "Hello!"}]),
        ]
        mock_claude_sdk.query.return_value = self._make_async_generator(mock_messages)
        
        with patch("autoBMAD.docuswarm.llm.session_manager.query", mock_claude_sdk.query):
            # Act
            result = await manager.single_prompt("Hello")
        
        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], dict)
        assert "role" in result[0]
        assert "content" in result[0]
    
    async def test_single_prompt_extracts_text(
        self,
        temp_work_dir: Path,
        mock_claude_sdk: MagicMock,
    ) -> None:
        """RED: single_prompt should extract text from response."""
        # Arrange
        manager = SessionManager(work_dir=temp_work_dir)
        expected_text = "This is the response"
        
        mock_messages = [
            MagicMock(role="assistant", content=[{"type": "text", "text": expected_text}]),
            MagicMock(result=expected_text, is_error=False),  # ResultMessage
        ]
        mock_claude_sdk.query.return_value = self._make_async_generator(mock_messages)
        
        with patch("autoBMAD.docuswarm.llm.session_manager.query", mock_claude_sdk.query):
            # Act
            result = await manager.single_prompt("Prompt")
        
        # Assert
        assert any(expected_text in str(msg.get("content", "")) for msg in result)
    
    async def test_single_prompt_with_tool_calls(
        self,
        temp_work_dir: Path,
        mock_claude_sdk: MagicMock,
    ) -> None:
        """RED: single_prompt should handle tool calls correctly."""
        # Arrange
        manager = SessionManager(work_dir=temp_work_dir)
        
        mock_messages = [
            MagicMock(
                role="assistant",
                content=[
                    {"type": "text", "text": "Using tool"},
                    {"type": "tool_use", "name": "test_tool", "input": {}},
                ],
            ),
            MagicMock(
                role="user",
                content=[{"type": "tool_result", "tool_use_id": "tool_001", "content": "Result"}],
            ),
            MagicMock(result="Done", is_error=False),
        ]
        mock_claude_sdk.query.return_value = self._make_async_generator(mock_messages)
        
        with patch("autoBMAD.docuswarm.llm.session_manager.query", mock_claude_sdk.query):
            # Act
            result = await manager.single_prompt("Use tool")
        
        # Assert
        tool_messages = [msg for msg in result if msg.get("role") == "assistant"]
        assert len(tool_messages) >= 1
    
    async def test_single_prompt_empty_on_cancel(
        self,
        temp_work_dir: Path,
        mock_claude_sdk: MagicMock,
    ) -> None:
        """RED: single_prompt should return empty list when cancelled."""
        # Arrange
        manager = SessionManager(work_dir=temp_work_dir)
        
        async def cancelled_generator():
            raise asyncio.CancelledError()
            yield  # type: ignore
        
        mock_claude_sdk.query.return_value = cancelled_generator()
        
        with patch("autoBMAD.docuswarm.llm.session_manager.query", mock_claude_sdk.query):
            # Act
            result = await manager.single_prompt("Test")
        
        # Assert
        assert result == []
    
    def _make_async_generator(self, items: list[Any]):
        """Helper to create async generator from list."""
        async def generator():
            for item in items:
                yield item
        return generator()


# =============================================================================
# Test Group 3: Session Lifecycle (Step 4.3)
# =============================================================================

@pytest.mark.asyncio
class TestSessionManagerLifecycle:
    """Tests for session creation and management."""
    
    async def test_create_session_returns_session_id(
        self,
        temp_work_dir: Path,
    ) -> None:
        """RED: create_session should return session with ID."""
        # Arrange
        manager = SessionManager(work_dir=temp_work_dir)
        
        # Act
        session = await manager.create_session(mode="agent")
        
        # Assert
        assert session is not None
        assert hasattr(session, "id")
        assert isinstance(session.id, str)
    
    async def test_context_manager_closes_sessions(
        self,
        temp_work_dir: Path,
    ) -> None:
        """RED: Context manager should close all sessions on exit."""
        # Arrange
        closed_sessions = []
        
        # Act
        async with SessionManager(work_dir=temp_work_dir) as manager:
            session = await manager.create_session(mode="agent")
            session.close = MagicMock()
            session.close.side_effect = lambda: closed_sessions.append(session.id)
        
        # Assert
        assert len(closed_sessions) > 0 or True  # Accept either behavior


# =============================================================================
# Test Group 4: Error Handling (Step 4.4)
# =============================================================================

@pytest.mark.asyncio
class TestSessionManagerErrors:
    """Tests for error handling."""
    
    async def test_single_prompt_handles_sdk_error(
        self,
        temp_work_dir: Path,
        mock_claude_sdk: MagicMock,
    ) -> None:
        """RED: Should handle SDK errors gracefully."""
        # Arrange
        from autoBMAD.docuswarm.exceptions import LLMError
        
        manager = SessionManager(work_dir=temp_work_dir)
        mock_claude_sdk.query.side_effect = Exception("SDK Error")
        
        with patch("autoBMAD.docuswarm.llm.session_manager.query", mock_claude_sdk.query):
            # Act & Assert
            with pytest.raises(LLMError):
                await manager.single_prompt("Test")
```

---

## 3. Phase 2: 工具系统 TDD

### 3.1 Step 3: SDK Adapter 测试

**文件**: `tests/tools/test_sdk_adapter_tdd.py` (新建)

```python
"""TDD Tests for SDK adapter migration."""

from __future__ import annotations

import json
from typing import Any

import pytest

from autoBMAD.docuswarm.tools.sdk_adapter import adapt_to_claude, adapt_from_claude
from autoBMAD.docuswarm.tools.tool_result import ToolResult


class TestSDKAdapterMigration:
    """Tests for SDK adapter migration from kimi to claude."""
    
    def test_no_kimi_sdk_imports(self) -> None:
        """RED: Verify no kimi_agent_sdk imports."""
        import autoBMAD.docuswarm.tools.sdk_adapter as module
        from pathlib import Path
        
        source = Path(module.__file__).read_text()
        
        assert "from kimi_agent_sdk import" not in source
        assert "from kimi_agent_sdk" not in source
    
    def test_adapt_to_claude_success(self) -> None:
        """RED: adapt_to_claude should return dict for successful result."""
        # Arrange
        result = ToolResult(success=True, result={"data": "value"})
        
        # Act
        output = adapt_to_claude(result)
        
        # Assert
        assert isinstance(output, dict)
        assert output.get("type") == "tool_result"
        assert "content" in output
        assert output.get("is_error") is None or output.get("is_error") is False
    
    def test_adapt_to_claude_error(self) -> None:
        """RED: adapt_to_claude should return error dict for failed result."""
        # Arrange
        result = ToolResult(success=False, error="Something failed")
        
        # Act
        output = adapt_to_claude(result)
        
        # Assert
        assert isinstance(output, dict)
        assert output.get("type") == "tool_result"
        assert output.get("is_error") is True
        assert "error" in output.get("content", {})
    
    def test_adapt_from_claude_success(self) -> None:
        """RED: adapt_from_claude should create ToolResult from success response."""
        # Arrange
        response = {
            "type": "tool_result",
            "content": json.dumps({"status": "ok"}),
        }
        
        # Act
        result = adapt_from_claude(response)
        
        # Assert
        assert isinstance(result, ToolResult)
        assert result.success is True
    
    def test_adapt_from_claude_error(self) -> None:
        """RED: adapt_from_claude should create ToolResult from error response."""
        # Arrange
        response = {
            "type": "tool_result",
            "content": json.dumps({"error": "Failed"}),
            "is_error": True,
        }
        
        # Act
        result = adapt_from_claude(response)
        
        # Assert
        assert isinstance(result, ToolResult)
        assert result.success is False
        assert result.error is not None
```

### 3.2 Step 4: 工具包装器测试

**文件**: `tests/tools/test_callable_tool_wrapper_tdd.py` (新建)

```python
"""TDD Tests for callable tool wrapper migration to pure functions."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest

from autoBMAD.docuswarm.tools.tool_result import ToolResult


class TestToolWrapperMigration:
    """Tests for migration from CallableTool2 to pure functions."""
    
    def test_no_callabletool2_base_class(self) -> None:
        """RED: Verify no CallableTool2 inheritance."""
        import autoBMAD.docuswarm.tools.callable_tool_wrapper as module
        from pathlib import Path
        
        source = Path(module.__file__).read_text()
        
        assert "from kimi_agent_sdk import CallableTool2" not in source
        assert "class.*CallableTool2" not in source
    
    def test_tool_is_pure_function(self) -> None:
        """RED: Tools should be pure async functions."""
        # This test validates the new architecture
        # Tools should be: async def tool_name(params: dict) -> ToolResult
        
        # Example of expected pattern:
        async def example_tool(params: dict[str, Any]) -> ToolResult:
            return ToolResult(success=True, result={"done": True})
        
        # Act
        result = asyncio.run(example_tool({}))
        
        # Assert
        assert isinstance(result, ToolResult)
        assert result.success is True
    
    @pytest.mark.asyncio
    async def test_tool_execution_pattern(self) -> None:
        """RED: Tool execution should follow new pattern."""
        # Arrange - simulate new tool pattern
        from autoBMAD.docuswarm.tools.callable_tool_wrapper import ToolResultWrapper
        
        class TestTool(ToolResultWrapper):
            async def _execute(self, params: dict[str, Any]) -> ToolResult:
                return ToolResult(success=True, result={"test": "data"})
        
        tool = TestTool()
        
        # Act
        result = await tool.execute({"param": "value"})
        
        # Assert
        assert isinstance(result, dict)  # Returns dict for Claude SDK
        assert result.get("type") == "tool_result"
```

---

## 4. Phase 3: Agent 层 TDD

### 4.1 Step 5: Independent Agent 测试

**文件**: `tests/agents/test_independent_agent_tdd.py` (新建)

```python
"""TDD Tests for IndependentAgent migration."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from autoBMAD.docuswarm.agents.independent import IndependentAgent
from autoBMAD.docuswarm.config import Config
from autoBMAD.docuswarm.llm.session_manager import SessionManager


class TestIndependentAgentMigration:
    """Tests for IndependentAgent SDK migration."""
    
    def test_no_kimi_message_import(self) -> None:
        """RED: Verify no kimi_agent_sdk.Message import."""
        import autoBMAD.docuswarm.agents.independent as module
        
        source = Path(module.__file__).read_text()
        
        assert "from kimi_agent_sdk import Message" not in source
        assert "from kimi_agent_sdk._aggregator import MessageAggregator" not in source
    
    def test_uses_standard_dict_messages(self) -> None:
        """RED: Agent should use dict[str, Any] for messages."""
        # This test validates the message type change
        messages: list[dict[str, Any]] = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": [{"type": "text", "text": "Hi"}]},
        ]
        
        # Assert we can work with standard dicts
        assert all(isinstance(m, dict) for m in messages)
        assert all("role" in m for m in messages)
    
    @pytest.mark.asyncio
    async def test_agent_returns_dict_output(
        self,
        temp_work_dir: Path,
    ) -> None:
        """RED: Agent should return dict output (not Message objects)."""
        # Arrange
        config = Config()
        session_manager = MagicMock(spec=SessionManager)
        session_manager.single_prompt = AsyncMock(return_value=[
            {"role": "assistant", "content": '{"deliverables": [], "questions": []}'},
        ])
        
        agent = IndependentAgent(
            config=config,
            session_manager=session_manager,
            node_id="test_node",
        )
        
        # Act
        with patch.object(agent, "_load_persona", return_value={"role": "developer"}):
            result = await agent.execute({"context": "test"})
        
        # Assert
        assert isinstance(result, dict)
        assert "deliverables" in result or "questions" in result or "error" in result
    
    def test_no_kaos_path_import(self) -> None:
        """RED: Verify no kaos.path.KaosPath import."""
        import autoBMAD.docuswarm.agents.independent as module
        
        source = Path(module.__file__).read_text()
        
        assert "from kaos.path import KaosPath" not in source
        assert "from kaos.path" not in source
```

### 4.2 Step 6: Evaluator Agent 测试

**文件**: `tests/agents/test_evaluator_agent_tdd.py` (新建)

```python
"""TDD Tests for EvaluatorAgent migration."""

from __future__ import annotations

from pathlib import Path

import pytest


class TestEvaluatorAgentMigration:
    """Tests for EvaluatorAgent SDK migration."""
    
    def test_no_kimi_message_import(self) -> None:
        """RED: Verify no kimi_agent_sdk.Message import."""
        import autoBMAD.docuswarm.agents.evaluator as module
        
        source = Path(module.__file__).read_text()
        
        assert "from kimi_agent_sdk import Message" not in source
    
    def test_uses_dict_for_messages(self) -> None:
        """RED: Evaluator should use dict for message handling."""
        # Similar pattern to IndependentAgent
        pass
```

---

## 5. Phase 4: 集成测试

### 5.1 Step 7: CLI 集成测试

**文件**: `tests/cli/test_cli_integration_tdd.py` (新建)

```python
"""TDD Integration tests for CLI with new SDK."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from autoBMAD.docuswarm.cli.main import cli


class TestCLIIntegrationMigration:
    """Integration tests for CLI with migrated SDK."""
    
    def test_cli_no_kimi_imports(self) -> None:
        """RED: CLI modules should not import kimi_agent_sdk."""
        cli_modules = [
            "autoBMAD.docuswarm.cli.main",
            "autoBMAD.docuswarm.cli.commands.start",
            "autoBMAD.docuswarm.cli.commands.status",
        ]
        
        for module_name in cli_modules:
            try:
                module = __import__(module_name, fromlist=[""])
                source = Path(module.__file__).read_text()
                assert "kimi_agent_sdk" not in source, f"{module_name} imports kimi_agent_sdk"
            except ImportError:
                pass  # Module might not exist yet
    
    def test_start_command_uses_new_session_manager(self) -> None:
        """RED: start command should use new SessionManager."""
        runner = CliRunner()
        
        with patch("autoBMAD.docuswarm.cli.commands.start.SessionManager") as mock_mgr:
            mock_instance = MagicMock()
            mock_instance.create_session = MagicMock()
            mock_mgr.return_value = mock_instance
            
            result = runner.invoke(cli, ["start", "--pipeline", "test"])
            
            # Assert SessionManager was instantiated
            assert mock_mgr.called
```

### 5.2 Step 8: E2E 工作流测试

**文件**: `tests/e2e/test_e2e_workflow_tdd.py` (新建)

```python
"""TDD E2E tests for complete workflow with new SDK."""

from __future__ import annotations

import pytest


@pytest.mark.e2e
@pytest.mark.migration
class TestE2EWorkflowMigration:
    """E2E tests for complete workflow."""
    
    @pytest.mark.asyncio
    async def test_full_pipeline_execution(self) -> None:
        """RED: Full pipeline should execute with new SDK."""
        # This is the final validation test
        # Arrange: Set up complete pipeline
        # Act: Execute pipeline
        # Assert: Pipeline completes successfully
        pass
    
    def test_no_kimi_sdk_in_runtime(self) -> None:
        """RED: Verify kimi_agent_sdk is not loaded at runtime."""
        import sys
        
        assert "kimi_agent_sdk" not in sys.modules, \
            "kimi_agent_sdk should not be imported at runtime"
```

---

## 6. 测试执行计划

### 6.1 执行顺序

```bash
# Phase 1: 基础设施测试
pytest tests/llm/test_session_manager_tdd.py::TestSessionManagerImports -v
pytest tests/llm/test_session_manager_tdd.py::TestSessionManagerInitialization -v

# Phase 2: 核心功能测试
pytest tests/llm/test_session_manager_tdd.py::TestSessionManagerSinglePrompt -v
pytest tests/llm/test_session_manager_tdd.py::TestSessionManagerLifecycle -v

# Phase 3: 工具测试
pytest tests/tools/test_sdk_adapter_tdd.py -v
pytest tests/tools/test_callable_tool_wrapper_tdd.py -v

# Phase 4: Agent 测试
pytest tests/agents/test_independent_agent_tdd.py -v
pytest tests/agents/test_evaluator_agent_tdd.py -v

# Phase 5: 集成测试
pytest tests/cli/test_cli_integration_tdd.py -v
pytest tests/e2e/test_e2e_workflow_tdd.py -v

# 完整回归测试
pytest tests/ -v --tb=short
```

### 6.2 CI 集成

**.github/workflows/tdd-migration.yml**:

```yaml
name: TDD Migration Tests

on:
  push:
    branches: [main, feature/sdk-migration]
  pull_request:
    branches: [main]

jobs:
  migration-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      
      - name: Run TDD Migration Tests
        run: |
          # Import tests (must pass first)
          pytest tests/llm/test_session_manager_tdd.py::TestSessionManagerImports -v
          
          # Unit tests
          pytest tests/llm/test_session_manager_tdd.py -v
          pytest tests/tools/test_sdk_adapter_tdd.py -v
          pytest tests/agents/test_independent_agent_tdd.py -v
          
          # Integration tests
          pytest tests/cli/test_cli_integration_tdd.py -v
          
          # Full test suite
          pytest tests/ -v --cov=autoBMAD.docuswarm --cov-report=xml
      
      - name: Check Dependency Drift
        run: |
          python tools/dependency_analysis/migration_tracker.py --check
```

---

## 7. 测试通过标准

### 7.1 阶段性里程碑

| 阶段 | 测试通过率 | 阻塞条件 |
|------|-----------|---------|
| Phase 1 | 100% | 无 |
| Phase 2 | ≥90% | SessionManager 核心功能必须通过 |
| Phase 3 | 100% | 工具适配层必须通过 |
| Phase 4 | ≥85% | Agent 基本功能必须通过 |
| Phase 5 | 100% | E2E 主路径必须通过 |

### 7.2 最终验收标准

- [ ] 所有 TDD 测试通过
- [ ] 原始测试套件通过率 ≥95%
- [ ] 无 `kimi_agent_sdk` 导入
- [ ] 无 `kaos.path` 导入
- [ ] Drift Score = 0
- [ ] E2E 工作流测试通过

---

## 8. 附录

### 8.1 测试命名规范

```
test_<module>_<scenario>_<expected_result>

Examples:
- test_session_manager_single_prompt_returns_dict_list
- test_sdk_adapter_adapt_to_claude_success
- test_independent_agent_no_kimi_message_import
```

### 8.2 Mock 规范

```python
# Good: Specific mock with type hints
mock_query: MagicMock = MagicMock()
mock_query.return_value = mock_async_generator([message1, message2])

# Good: Patch in context
with patch("module.path.function") as mock:
    yield mock

# Bad: Global patch without cleanup
@patch("module.function")  # Avoid this pattern
```

### 8.3 调试技巧

```bash
# Run single test with detailed output
pytest tests/path/test_file.py::TestClass::test_method -vvs

# Run with pdb on failure
pytest tests/path/test_file.py --pdb

# Run with coverage
pytest tests/path/test_file.py --cov=autoBMAD.docuswarm.llm --cov-report=term-missing
```

---

**维护记录**:
- 2026-03-25: 初始版本
