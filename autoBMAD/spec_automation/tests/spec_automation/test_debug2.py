"""Debug test to check SpecDevAgent initialization."""

import pytest
from unittest.mock import Mock, AsyncMock
from spec_automation.spec_dev_agent import SpecDevAgent


@pytest.fixture
def mock_sdk():
    """Create a mock SDK instance."""
    sdk = Mock()
    sdk.query = AsyncMock()
    return sdk


def test_debug_agent_init_with_exception_handling(mock_sdk):
    """Debug test with exception handling."""
    print("\n=== Starting SpecDevAgent initialization ===")

    try:
        print("Creating agent...")
        agent = SpecDevAgent(sdk=mock_sdk)
        print(f"Agent created: {agent}")

        print(f"\nAgent has __init__ completed: {hasattr(agent, 'sdk')}")
        print(f"Agent.sdk: {agent.sdk}")

        print("\nChecking attributes...")
        print(f"Has state_manager: {hasattr(agent, 'state_manager')}")
        print(f"Has doc_parser: {hasattr(agent, 'doc_parser')}")
        print(f"Has prompts: {hasattr(agent, 'prompts')}")
        print(f"Has tdd_engine: {hasattr(agent, 'tdd_engine')}")
        print(f"Has test_verifier: {hasattr(agent, 'test_verifier')}")
        print(f"Has quality_gate_runner: {hasattr(agent, 'quality_gate_runner')}")

        print(f"\nAll attributes: {[a for a in dir(agent) if not a.startswith('_')]}")

    except Exception as e:
        print("\n!!! Exception during initialization !!!")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {e}")
        import traceback
        traceback.print_exc()
        raise
