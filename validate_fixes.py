#!/usr/bin/env python3
"""
验证BMAD史诗自动化系统修复的脚本
"""
import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from autoBMAD.epic_automation.qa_agent import QAAgent
from autoBMAD.epic_automation.state_manager import StateManager


async def test_qa_agent_imports():
    """Test QA Agent import and basic functionality"""
    print("[1/4] Testing QA Agent import...")
    try:
        agent = QAAgent()
        print("  [PASS] QA Agent imported successfully")
        return True
    except Exception as e:
        print(f"  [FAIL] QA Agent import failed: {e}")
        return False


async def test_state_manager_imports():
    """Test State Manager import and basic functionality"""
    print("\n[2/4] Testing State Manager import...")
    try:
        manager = StateManager(db_path=":memory:")
        print("  [PASS] State Manager imported successfully")
        return True
    except Exception as e:
        print(f"  [FAIL] State Manager import failed: {e}")
        return False


async def test_qa_gate_paths():
    """Test QA gate file path functionality"""
    print("\n[3/4] Testing QA gate file paths...")
    try:
        agent = QAAgent()
        # Test empty path (should generate fallback)
        paths = await agent._collect_qa_gate_paths()
        if isinstance(paths, list):
            print(f"  [PASS] QA gate paths collected successfully, {len(paths)} paths returned")
            return True
        else:
            print(f"  [FAIL] QA gate paths returned wrong type: {type(paths)}")
            return False
    except Exception as e:
        print(f"  [FAIL] QA gate paths test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_state_manager_lock():
    """Test State Manager lock management"""
    print("\n[4/4] Testing State Manager lock management...")
    try:
        manager = StateManager(db_path=":memory:")

        # Test managed_operation context manager
        async with manager.managed_operation():
            if manager._lock.locked():
                print("  [PASS] Lock correctly acquired in context")
            else:
                print("  [FAIL] Lock not acquired in context")
                return False

        if not manager._lock.locked():
            print("  [PASS] Lock correctly released after context exit")
            return True
        else:
            print("  [FAIL] Lock not released after context exit")
            return False
    except Exception as e:
        print(f"  [FAIL] State Manager lock test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all validation tests"""
    print("=" * 60)
    print("BMAD Epic Automation System Fix Validation")
    print("=" * 60)

    tests = [
        ("QA Agent Import", test_qa_agent_imports),
        ("State Manager Import", test_state_manager_imports),
        ("QA Gate File Paths", test_qa_gate_paths),
        ("State Manager Lock", test_state_manager_lock)
    ]

    results = []
    for test_name, test_func in tests:
        result = await test_func()
        results.append((test_name, result))

    print("\n" + "=" * 60)
    print("Validation Results Summary")
    print("=" * 60)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name}: {status}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All fix validations passed!")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
