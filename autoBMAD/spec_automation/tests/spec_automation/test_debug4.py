"""Debug test to check spec_dev_agent import."""

from unittest.mock import AsyncMock


def test_debug_spec_dev_agent_import():
    """Debug test to check spec_dev_agent import."""
    print("\n=== Testing spec_dev_agent import ===")

    try:
        print("Importing spec_dev_agent...")
        from spec_automation import spec_dev_agent
        print(f"✓ spec_dev_agent module: {spec_dev_agent}")

        print("\nAccessing SpecDevAgent class...")
        spec_dev_class = spec_dev_agent.SpecDevAgent
        print(f"✓ SpecDevAgent class: {spec_dev_class}")

        print("\nCreating mock SDK...")
        from unittest.mock import Mock
        mock_sdk = Mock()
        mock_sdk.query = AsyncMock()
        print(f"✓ Mock SDK: {mock_sdk}")

        print("\nCreating SpecDevAgent...")
        agent = spec_dev_class(sdk=mock_sdk)
        print(f"✓ Agent created: {agent}")
        print(f"Agent attributes: {[a for a in dir(agent) if not a.startswith('_')]}")

    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
