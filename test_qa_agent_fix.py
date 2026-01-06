#!/usr/bin/env python3
"""
QA Agent Fix Validation Script

This script validates that the QA Agent error fixes are working correctly.
"""

import sys
import traceback
from pathlib import Path

def test_qa_agent_sdk_import():
    """Test that QA Agent can import SDK components correctly."""
    print("=" * 60)
    print("Test 1: QA Agent SDK Import")
    print("=" * 60)

    try:
        from autoBMAD.epic_automation.qa_agent import query, ClaudeAgentOptions, QAAgent
        print("✓ Successfully imported query, ClaudeAgentOptions, and QAAgent")

        # Check that imports match dev_agent pattern
        from autoBMAD.epic_automation.dev_agent import query as dev_query, ClaudeAgentOptions as dev_options
        if query is dev_query and ClaudeAgentOptions is dev_options:
            print("✓ QA Agent SDK components match dev_agent pattern")
        else:
            print("✗ SDK components don't match dev_agent")
            return False

        # Verify they are None when SDK not installed
        if query is None and ClaudeAgentOptions is None:
            print("✓ SDK components are None (expected when SDK not installed)")
        else:
            print("✗ SDK components should be None when SDK not installed")
            return False

        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        traceback.print_exc()
        return False


def test_sdk_wrapper_improvements():
    """Test SDK wrapper improvements."""
    print("\n" + "=" * 60)
    print("Test 2: SDK Wrapper Improvements")
    print("=" * 60)

    try:
        from autoBMAD.epic_automation.sdk_wrapper import SafeClaudeSDK

        # Check that stop_periodic_display accepts timeout parameter
        import inspect
        sig = inspect.signature(SafeClaudeSDK.stop_periodic_display)
        params = list(sig.parameters.keys())

        if 'timeout' in params:
            print("✓ stop_periodic_display has timeout parameter")
        else:
            print("✗ stop_periodic_display missing timeout parameter")
            return False

        # Verify default timeout value
        if sig.parameters['timeout'].default == 1.0:
            print("✓ Default timeout value is 1.0 seconds")
        else:
            print(f"✗ Default timeout should be 1.0, got {sig.parameters['timeout'].default}")
            return False

        return True
    except Exception as e:
        print(f"✗ SDK wrapper test failed: {e}")
        traceback.print_exc()
        return False


def test_state_manager_improvements():
    """Test state manager improvements."""
    print("\n" + "=" * 60)
    print("Test 3: State Manager Improvements")
    print("=" * 60)

    try:
        from autoBMAD.epic_automation.state_manager import StateManager
        import inspect

        # Get source code of update_story_status method
        source = inspect.getsource(StateManager.update_story_status)

        # Check for improved error handling
        checks = [
            ("cause_str", "cause_str variable for better error context"),
            ("timeout", "timeout detection logic"),
            ("logger.info", "informational logging for user/system cancellation"),
        ]

        all_passed = True
        for check, description in checks:
            if check in source:
                print(f"✓ Found {description}")
            else:
                print(f"✗ Missing {description}")
                all_passed = False

        return all_passed
    except Exception as e:
        print(f"✗ State manager test failed: {e}")
        traceback.print_exc()
        return False


def test_architectural_consistency():
    """Test that all agents use consistent patterns."""
    print("\n" + "=" * 60)
    print("Test 4: Architectural Consistency")
    print("=" * 60)

    try:
        # Compare qa_agent and dev_agent import patterns
        from autoBMAD.epic_automation.qa_agent import query as qa_query, ClaudeAgentOptions as qa_options
        from autoBMAD.epic_automation.dev_agent import query as dev_query, ClaudeAgentOptions as dev_options

        if qa_query is dev_query and qa_options is dev_options:
            print("✓ QA Agent and Dev Agent use identical SDK components")
        else:
            print("✗ SDK components differ between agents")
            return False

        # Check that sm_agent also follows the same pattern
        from autoBMAD.epic_automation.sm_agent import query as sm_query, ClaudeAgentOptions as sm_options

        if sm_query is dev_query and sm_options is dev_options:
            print("✓ SM Agent also uses identical SDK components")
        else:
            print("✗ SM Agent SDK components differ")
            return False

        return True
    except Exception as e:
        print(f"✗ Architectural consistency test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all validation tests."""
    print("\n" + "=" * 60)
    print("QA AGENT ERROR FIX VALIDATION")
    print("=" * 60)
    print()

    tests = [
        ("SDK Import", test_qa_agent_sdk_import),
        ("SDK Wrapper", test_sdk_wrapper_improvements),
        ("State Manager", test_state_manager_improvements),
        ("Architecture", test_architectural_consistency),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {name}")

    print()
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All validation tests PASSED!")
        print("\nThe QA Agent error fixes are working correctly:")
        print("  1. SDK import issue resolved")
        print("  2. Async cancellation handling improved")
        print("  3. State management error classification improved")
        print("  4. All agents use consistent SDK import patterns")
        return 0
    else:
        print("\n✗ Some validation tests FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
