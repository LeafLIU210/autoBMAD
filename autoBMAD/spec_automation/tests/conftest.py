"""Shared pytest fixtures for spec automation tests."""

import asyncio
import tempfile
from pathlib import Path
from typing import Any, AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import anyio


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    import tempfile
    import shutil

    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_task_group():
    """Create a mock TaskGroup for testing."""
    task_group = MagicMock()
    task_group.start = AsyncMock()
    return task_group


@pytest.fixture
def mock_sdk_result():
    """Create a mock SDKResult for testing."""
    from autoBMAD.epic_automation.core.sdk_result import SDKResult, SDKErrorType

    return SDKResult(
        has_target_result=True,
        cleanup_completed=True,
        duration_seconds=1.0,
        session_id="test-session",
        agent_name="TestAgent",
        messages=[],
        error_type=SDKErrorType.SUCCESS,
        errors=[],
    )


@pytest.fixture
def mock_cancellation_manager():
    """Create a mock CancellationManager for testing."""
    from autoBMAD.epic_automation.core.cancellation_manager import CancellationManager

    return CancellationManager()


@pytest.fixture
def mock_sdk_executor():
    """Create a mock SDKExecutor for testing."""
    from autoBMAD.epic_automation.core.sdk_executor import SDKExecutor

    executor = MagicMock(spec=SDKExecutor)
    executor.cancel_manager = MagicMock()
    executor.cancel_manager.get_active_calls_count.return_value = 0
    return executor


@pytest.fixture
def sample_story_content():
    """Sample story markdown content for testing."""
    return """# Story 1.1: Test Story

## Status
Status: Draft

## Acceptance Criteria
- [ ] Criteria 1
- [ ] Criteria 2

## Dev Agent Record
Tasks:
- [ ] Task 1
- [ ] Task 2
"""


@pytest.fixture
async def mock_state_manager(temp_dir):
    """Create a StateManager with temporary database."""
    from autoBMAD.epic_automation.state_manager import StateManager

    db_path = temp_dir / "test.db"
    manager = StateManager(db_path=str(db_path), use_connection_pool=False)
    yield manager


@pytest.fixture
def mock_agent():
    """Create a mock agent for testing."""
    class MockAgent:
        def __init__(self, name="MockAgent"):
            self.name = name
            self.executed = False
            self.execution_args = None
            self.execution_kwargs = None

        async def execute(self, *args, **kwargs):
            self.executed = True
            self.execution_args = args
            self.execution_kwargs = kwargs
            return {"status": "success", "agent": self.name}

    return MockAgent


@pytest.fixture
async def async_generator_fixture():
    """Create an async generator for testing."""
    async def async_generator():
        for i in range(3):
            yield {"value": i, "type": "data"}

    return async_generator()


@pytest.fixture
def mock_sdk_helper():
    """Create a mock SDK helper for testing."""
    with patch("autoBMAD.epic_automation.agents.sdk_helper.execute_sdk_call") as mock:
        yield mock


@pytest.fixture
def mock_log_manager():
    """Create a mock log manager for testing."""
    log_manager = MagicMock()
    log_manager.log = MagicMock()
    return log_manager


@pytest.fixture
def concrete_agent_class():
    """Return the ConcreteAgent class for testing."""
    from autoBMAD.spec_automation.tests.test_base_agent import ConcreteAgent
    return ConcreteAgent


@pytest.fixture(params=["asyncio", "anyio"])
def anyio_backend(request):
    """Parametrized fixture for anyio backends."""
    return request.param
