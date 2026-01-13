"""
Verification tests for TaskGroup.start() return value fix

This test verifies that _execute_within_taskgroup() correctly returns
the result of the coroutine instead of None. This is a fix for the
anyio TaskGroup.start() API misunderstanding bug.
"""
import pytest
import anyio
from autoBMAD.epic_automation.agents.state_agent import StateAgent
from autoBMAD.epic_automation.controllers.devqa_controller import DevQaController
from autoBMAD.epic_automation.controllers.base_controller import BaseController


class SimpleTestAgent(BaseController):
    """Simple controller for testing"""

    def __init__(self, task_group):
        super().__init__(task_group)

    async def execute(self, *args, **kwargs):
        return True


@pytest.mark.anyio
async def test_base_agent_execute_within_taskgroup_returns_value():
    """Verify BaseAgent._execute_within_taskgroup returns coroutine result"""

    async def sample_coro():
        return "expected_result"

    async with anyio.create_task_group() as tg:
        agent = StateAgent(task_group=tg)
        result = await agent._execute_within_taskgroup(sample_coro)

    assert result == "expected_result", f"Expected 'expected_result', got {result}"
    print("[PASS] BaseAgent._execute_within_taskgroup return value test")


@pytest.mark.anyio
async def test_base_controller_execute_within_taskgroup_returns_value():
    """Verify BaseController._execute_within_taskgroup returns coroutine result"""

    async def sample_coro():
        return "controller_result"

    async with anyio.create_task_group() as tg:
        controller = SimpleTestAgent(tg)
        result = await controller._execute_within_taskgroup(sample_coro)

    assert result == "controller_result", f"Expected 'controller_result', got {result}"
    print("[PASS] BaseController._execute_within_taskgroup return value test")


@pytest.mark.anyio
async def test_state_agent_execute_scenario():
    """Test StateAgent execute with actual file parsing"""

    import tempfile
    import os

    status_content = """# Story Status

## Current Status
Status: Ready for Development

## Progress
- [x] Requirement analysis
- [ ] Implement core algorithm
- [ ] Unit tests
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(status_content)
        temp_file = f.name

    try:
        async with anyio.create_task_group() as tg:
            agent = StateAgent(task_group=tg)

            # Test with _execute_within_taskgroup
            result = await agent._execute_within_taskgroup(
                lambda: agent.execute(temp_file)
            )

        assert result is not None, "StateAgent execute result should not be None"
        assert isinstance(result, str), f"Result should be a string, got {type(result)}"

        print(f"[PASS] StateAgent execute test - result: {result}")

    finally:
        os.unlink(temp_file)


@pytest.mark.anyio
async def test_taskgroup_started_with_various_types():
    """Test that various types of return values are correctly passed"""

    test_cases = [
        ("string", "test_string"),
        ("integer", 42),
        ("boolean", True),
        ("list", [1, 2, 3]),
        ("dict", {"key": "value"}),
        ("none", None),
    ]

    async with anyio.create_task_group() as tg:
        agent = StateAgent(task_group=tg)

        for test_name, expected_value in test_cases:
            async def sample_coro():
                return expected_value

            result = await agent._execute_within_taskgroup(sample_coro)

            assert result == expected_value, \
                f"Test {test_name} failed: expected {expected_value}, got {result}"
            print(f"  [PASS] Type {test_name}: {expected_value}")


if __name__ == "__main__":
    print("=" * 60)
    print("TaskGroup.start() Return Value Fix Verification")
    print("=" * 60)

    # Run tests
    pytest.main([__file__, "-v", "-s"])
