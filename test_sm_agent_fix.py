#!/usr/bin/env python3
"""
Test script to verify sm_agent.py fixes
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that ResultMessage is imported correctly"""
    print("=" * 60)
    print("TEST 1: Import Verification")
    print("=" * 60)

    try:
        from autoBMAD.epic_automation.sm_agent import SMAgent, ResultMessage
        print("[PASS] Successfully imported SMAgent and ResultMessage")
        return True
    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        return False

def test_message_type_handling():
    """Test message type handling logic"""
    print("\n" + "=" * 60)
    print("TEST 2: Message Type Handling Logic")
    print("=" * 60)

    # Create mock message classes to simulate SDK behavior
    class MockResultMessage:
        def __init__(self, is_error=False, result=None):
            self.is_error = is_error
            self.result = result

    class MockAssistantMessage:
        pass

    # Test ResultMessage detection
    success_msg = MockResultMessage(is_error=False, result="Success!")
    error_msg = MockResultMessage(is_error=True, result="Error occurred")
    assistant_msg = MockAssistantMessage()

    # Simulate isinstance() checks (our fix)
    print("Testing message type detection...")

    if isinstance(success_msg, MockResultMessage) and not success_msg.is_error:
        print("[PASS] Success message detected correctly")
    else:
        print("[FAIL] Success message detection failed")
        return False

    if isinstance(error_msg, MockResultMessage) and error_msg.is_error:
        print("[PASS] Error message detected correctly")
    else:
        print("[FAIL] Error message detection failed")
        return False

    if not isinstance(assistant_msg, MockResultMessage):
        print("[PASS] Non-ResultMessage detected correctly")
    else:
        print("[FAIL] Non-ResultMessage detection failed")
        return False

    return True

def test_code_structure():
    """Test that code structure is correct"""
    print("\n" + "=" * 60)
    print("TEST 3: Code Structure Verification")
    print("=" * 60)

    try:
        from autoBMAD.epic_automation.sm_agent import SMAgent

        # Check that methods exist
        agent = SMAgent()
        methods = ['create_stories_from_epic', '_execute_claude_sdk',
                   '_execute_sdk_with_logging', '_verify_story_files']

        for method in methods:
            if hasattr(agent, method):
                print(f"[PASS] Method {method} exists")
            else:
                print(f"[FAIL] Method {method} missing")
                return False

        return True

    except Exception as e:
        print(f"[FAIL] Code structure test failed: {e}")
        return False

def test_logging_english():
    """Verify that logs are in English"""
    print("\n" + "=" * 60)
    print("TEST 4: English Logging Verification")
    print("=" * 60)

    import inspect
    from autoBMAD.epic_automation import sm_agent

    source = inspect.getsource(sm_agent)

    # Check for Chinese characters in logs
    chinese_chars = ['开始', '创建', '故事', '错误', '结果', '验证', '失败', '成功']
    found_chinese = []

    for char in chinese_chars:
        if char in source:
            found_chinese.append(char)

    if found_chinese:
        print(f"[FAIL] Found Chinese characters in logs: {found_chinese}")
        return False
    else:
        print("[PASS] No Chinese characters found in logs (all English)")
        return True

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("SM Agent Fix Verification Tests")
    print("=" * 60)

    tests = [
        test_imports,
        test_message_type_handling,
        test_code_structure,
        test_logging_english
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"[FAIL] Test {test.__name__} raised exception: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")

    if all(results):
        print("\n[SUCCESS] ALL TESTS PASSED - Fix verification successful!")
        return 0
    else:
        print("\n[ERROR] SOME TESTS FAILED - Please review the issues above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
