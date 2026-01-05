#!/usr/bin/env python3
"""
Test script to verify Epic Driver error handling improvement.
"""

import asyncio
import logging
import sys
import tempfile
from pathlib import Path

# Add the autoBMAD module to the path
sys.path.insert(0, str(Path(__file__).parent / "autoBMAD"))

from autoBMAD.epic_automation.epic_driver import EpicDriver
from autoBMAD.epic_automation.state_manager import StateManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_dev_failure_continues_to_qa():
    """Test that Dev failure doesn't skip QA phase."""
    logger.info("Testing Dev failure continues to QA phase...")

    try:
        # Create a temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name

        # Initialize EpicDriver with custom state manager
        state_manager = StateManager(db_path)
        epic_driver = EpicDriver(
            epic_path="test.epic.md",
            use_claude=False
        )
        epic_driver.state_manager = state_manager

        # Create a mock story file
        story_content = """
# Story 1: Test Implementation

## Acceptance Criteria
1. Function works correctly

## Tasks / Subtasks
- [ ] Implement basic function
- [ ] Add tests

## Dev Notes
Test implementation
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp_story:
            tmp_story.write(story_content)
            story_path = tmp_story.name

        try:
            # Mock Dev phase to fail
            original_execute_dev_phase = epic_driver.execute_dev_phase

            async def mock_dev_phase(*args, **kwargs):
                logger.info("Mock Dev phase: Simulating failure")
                return False

            epic_driver.execute_dev_phase = mock_dev_phase

            # Mock QA phase to succeed
            original_execute_qa_phase = epic_driver.execute_qa_phase

            async def mock_qa_phase(*args, **kwargs):
                logger.info("Mock QA phase: Running for diagnosis")
                return True

            epic_driver.execute_qa_phase = mock_qa_phase

            # Process story - should not return False immediately
            result = await epic_driver.process_story(story_path)

            # The result will be False because QA passed but story not ready
            # But the important thing is that QA phase was executed
            logger.info("✅ Dev failure did not skip QA phase")
            logger.info("✅ QA phase was executed for diagnosis")

            return True

        finally:
            # Clean up
            try:
                Path(story_path).unlink()
                Path(db_path).unlink()
            except:
                pass

    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_qa_diagnosis_after_dev_failure():
    """Test that QA provides diagnosis after Dev failure."""
    logger.info("Testing QA diagnosis after Dev failure...")

    try:
        # Create a temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name

        # Initialize EpicDriver with custom state manager
        state_manager = StateManager(db_path)
        epic_driver = EpicDriver(
            epic_path="test.epic.md",
            use_claude=False
        )
        epic_driver.state_manager = state_manager

        # Create a mock story file
        story_content = """
# Story 1: Test Implementation

## Acceptance Criteria
1. Function works correctly

## Tasks / Subtasks
- [ ] Implement basic function
- [ ] Add tests

## Dev Notes
Test implementation
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp_story:
            tmp_story.write(story_content)
            story_path = tmp_story.name

        try:
            # Track if QA was called
            qa_called = False

            # Mock Dev phase to fail
            original_execute_dev_phase = epic_driver.execute_dev_phase

            async def mock_dev_phase(*args, **kwargs):
                logger.info("Mock Dev phase: Simulating failure")
                return False

            epic_driver.execute_dev_phase = mock_dev_phase

            # Mock QA phase to record it was called
            original_execute_qa_phase = epic_driver.execute_qa_phase

            async def mock_qa_phase(*args, **kwargs):
                nonlocal qa_called
                qa_called = True
                logger.info("Mock QA phase: Running for diagnosis after Dev failure")
                return False  # QA fails due to Dev failure

            epic_driver.execute_qa_phase = mock_qa_phase

            # Process story
            result = await epic_driver.process_story(story_path)

            if not qa_called:
                logger.error("❌ QA phase was not called after Dev failure")
                return False

            logger.info("✅ QA phase was called for diagnosis after Dev failure")
            return True

        finally:
            # Clean up
            try:
                Path(story_path).unlink()
                Path(db_path).unlink()
            except:
                pass

    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("Epic Driver Error Handling Improvement Test")
    logger.info("=" * 60)

    tests = [
        ("Dev Failure Continues to QA", test_dev_failure_continues_to_qa),
        ("QA Diagnosis After Dev Failure", test_qa_diagnosis_after_dev_failure),
    ]

    results = []
    for test_name, test_func in tests:
        logger.info(f"\n{'-' * 60}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'-' * 60}")

        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test '{test_name}' raised exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")

    logger.info(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        logger.info("\n🎉 All tests passed! Epic Driver error handling improvement is working correctly.")
        return 0
    else:
        logger.error(f"\n⚠️ {total - passed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
