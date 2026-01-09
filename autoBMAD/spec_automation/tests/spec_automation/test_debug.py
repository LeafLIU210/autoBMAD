"""Debug test to check SpecDevAgent attributes."""

import pytest
from unittest.mock import Mock, AsyncMock
from spec_automation.spec_dev_agent import SpecDevAgent


@pytest.fixture
def mock_sdk():
    """Create a mock SDK instance."""
    sdk = Mock()
    sdk.query = AsyncMock()
    return sdk


def test_debug_agent_attributes(mock_sdk):
    """Debug test to check agent attributes."""
    agent = SpecDevAgent(sdk=mock_sdk)
    print(f"\nAgent type: {type(agent)}")
    print(f"Agent attributes: {[a for a in dir(agent) if not a.startswith('_')]}")
    print(f"Has tdd_engine: {hasattr(agent, 'tdd_engine')}")
    print(f"Has prompts: {hasattr(agent, 'prompts')}")
    print(f"Has state_manager: {hasattr(agent, 'state_manager')}")

    # Try to access the attributes
    try:
        print(f"tdd_engine: {agent.tdd_engine}")
    except Exception as e:
        print(f"Error accessing tdd_engine: {e}")

    try:
        print(f"prompts: {agent.prompts}")
    except Exception as e:
        print(f"Error accessing prompts: {e}")

    try:
        print(f"state_manager: {agent.state_manager}")
    except Exception as e:
        print(f"Error accessing state_manager: {e}")
