#!/usr/bin/env python3
"""
Test script for max_iterations removal verification
"""

import sys
from pathlib import Path

# Add project path to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test imports"""
    try:
        from autoBMAD.epic_automation.epic_driver import EpicDriver, StoryProgressTracker, STORY_TIME_BUDGET, CYCLE_TIME_BUDGET
        print("PASS: Import test successful")
        return True
    except ImportError as e:
        print(f"FAIL: Import test failed: {e}")
        return False

def test_progress_tracker():
    """Test progress tracker functionality"""
    try:
        from autoBMAD.epic_automation.epic_driver import StoryProgressTracker
        import logging

        # Create test logger
        logger = logging.getLogger(__name__)

        # Create progress tracker
        tracker = StoryProgressTracker("test_story.md", logger)

        # Test record cycle start
        tracker.record_cycle_start()
        print(f"  Cycle count: {tracker.cycle_count}")

        # Test record dev phase
        tracker.record_dev_phase(10.5, True)
        print(f"  Dev phase times: {tracker.dev_phase_times}")

        # Test record qa phase
        tracker.record_qa_phase(5.2, True, "In Progress")
        print(f"  QA phase times: {tracker.qa_phase_times}")
        print(f"  Status history: {tracker.status_history}")

        # Test get summary
        summary = tracker.get_summary()
        print(f"  Progress summary: {summary}")

        print("PASS: Progress tracker test successful")
        return True
    except Exception as e:
        print(f"FAIL: Progress tracker test failed: {e}")
        return False

def test_epic_driver_init():
    """Test EpicDriver initialization"""
    try:
        from autoBMAD.epic_automation.epic_driver import EpicDriver

        # Try to create EpicDriver instance (without max_iterations)
        driver = EpicDriver(
            epic_path="test.md",
            retry_failed=False,
            verbose=True
        )

        # Check if max_iterations attribute exists
        if hasattr(driver, 'max_iterations'):
            print("FAIL: max_iterations attribute still exists")
            return False
        else:
            print("PASS: max_iterations attribute removed")

        print("PASS: EpicDriver initialization test successful")
        return True
    except Exception as e:
        print(f"FAIL: EpicDriver initialization test failed: {e}")
        return False

def test_constants():
    """Test time budget constants"""
    try:
        from autoBMAD.epic_automation.epic_driver import STORY_TIME_BUDGET, CYCLE_TIME_BUDGET

        print(f"  STORY_TIME_BUDGET: {STORY_TIME_BUDGET} seconds ({STORY_TIME_BUDGET/60} minutes)")
        print(f"  CYCLE_TIME_BUDGET: {CYCLE_TIME_BUDGET} seconds ({CYCLE_TIME_BUDGET/60} minutes)")

        print("PASS: Constants test successful")
        return True
    except Exception as e:
        print(f"FAIL: Constants test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting max_iterations removal verification...")
    print("=" * 50)

    tests = [
        ("Import Test", test_imports),
        ("Progress Tracker Test", test_progress_tracker),
        ("EpicDriver Init Test", test_epic_driver_init),
        ("Time Budget Constants Test", test_constants)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        if test_func():
            passed += 1

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} passed")

    if passed == total:
        print("All tests passed! max_iterations removal successful!")
        return 0
    else:
        print("Some tests failed, please check the code")
        return 1

if __name__ == "__main__":
    sys.exit(main())
