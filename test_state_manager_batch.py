#!/usr/bin/env python3
"""
Test script to verify State Manager batch transaction fix.
"""

import asyncio
import logging
import sys
import tempfile
from pathlib import Path

# Add the autoBMAD module to the path
sys.path.insert(0, str(Path(__file__).parent / "autoBMAD"))

from autoBMAD.epic_automation.state_manager import StateManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_batch_update():
    """Test batch update of multiple stories."""
    logger.info("Testing batch update of multiple stories...")

    # Create a temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        state_manager = StateManager(db_path)

        # Test data: 4 stories
        stories = [
            {
                'story_path': 'docs/stories/1.1.project-setup.md',
                'status': 'sm_completed',
                'phase': 'sm',
                'iteration': 1,
                'epic_path': 'docs/epics/epic-1-core-algorithm-foundation.md'
            },
            {
                'story_path': 'docs/stories/1.2.bubble-sort-implementation.md',
                'status': 'sm_completed',
                'phase': 'sm',
                'iteration': 1,
                'epic_path': 'docs/epics/epic-1-core-algorithm-foundation.md'
            },
            {
                'story_path': 'docs/stories/1.3.testing-suite.md',
                'status': 'sm_completed',
                'phase': 'sm',
                'iteration': 1,
                'epic_path': 'docs/epics/epic-1-core-algorithm-foundation.md'
            },
            {
                'story_path': 'docs/stories/1.4.command-line-interface.md',
                'status': 'sm_completed',
                'phase': 'sm',
                'iteration': 1,
                'epic_path': 'docs/epics/epic-1-core-algorithm-foundation.md'
            }
        ]

        # Perform batch update
        result = await state_manager.update_stories_status_batch(stories)

        if not result:
            logger.error("❌ Batch update failed")
            return False

        logger.info("✅ Batch update succeeded")

        # Verify all stories were inserted
        all_stories = await state_manager.get_all_stories()

        if len(all_stories) != 4:
            logger.error(f"❌ Expected 4 stories, got {len(all_stories)}")
            return False

        logger.info(f"✅ All 4 stories were inserted into database")

        # Verify each story
        expected_paths = {s['story_path'] for s in stories}
        actual_paths = {s['story_path'] for s in all_stories}

        if expected_paths != actual_paths:
            logger.error(f"❌ Story paths don't match. Expected: {expected_paths}, Got: {actual_paths}")
            return False

        logger.info("✅ All story paths match expected values")

        # Verify iteration update works correctly (COALESCE fix)
        for story in all_stories:
            if story['iteration'] != 1:
                logger.error(f"❌ Iteration not updated correctly for {story['story_path']}: {story['iteration']}")
                return False

        logger.info("✅ Iteration updates work correctly (COALESCE fix verified)")

        return True

    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        try:
            Path(db_path).unlink()
        except:
            pass


async def test_batch_update_with_iteration_zero():
    """Test that iteration=0 is properly handled (not ignored by COALESCE)."""
    logger.info("Testing batch update with iteration=0...")

    # Create a temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        state_manager = StateManager(db_path)

        # First insert a story with iteration=5
        await state_manager.update_story_status(
            story_path='test-story.md',
            status='sm_completed',
            iteration=5
        )

        # Then update with iteration=0 using batch update
        stories = [
            {
                'story_path': 'test-story.md',
                'status': 'dev_completed',
                'iteration': 0,  # This should be 0, not ignored
                'phase': 'dev'
            }
        ]

        result = await state_manager.update_stories_status_batch(stories)

        if not result:
            logger.error("❌ Batch update with iteration=0 failed")
            return False

        # Verify iteration was set to 0
        story = await state_manager.get_story_status('test-story.md')

        if story['iteration'] != 0:
            logger.error(f"❌ Iteration should be 0, but got {story['iteration']}")
            return False

        logger.info("✅ Iteration=0 is properly handled (COALESCE fix verified)")
        return True

    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        try:
            Path(db_path).unlink()
        except:
            pass


async def test_batch_transaction_rollback():
    """Test that batch update rolls back on error."""
    logger.info("Testing batch transaction rollback...")

    # Create a temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        state_manager = StateManager(db_path)

        # First insert a story
        await state_manager.update_story_status(
            story_path='test-story-1.md',
            status='sm_completed',
            iteration=1
        )

        # Try batch update with one valid and one invalid (missing required field)
        stories = [
            {
                'story_path': 'test-story-2.md',
                'status': 'sm_completed',
                'iteration': 1
            },
            {
                # Missing 'status' - should cause error
                'story_path': 'test-story-3.md',
                'iteration': 1
            }
        ]

        result = await state_manager.update_stories_status_batch(stories)

        if result:
            logger.error("❌ Batch update should have failed but succeeded")
            return False

        # Verify that test-story-2 was not inserted (rollback worked)
        story2 = await state_manager.get_story_status('test-story-2.md')
        story1 = await state_manager.get_story_status('test-story-1.md')

        if story2 is not None:
            logger.error("❌ Rollback failed - test-story-2 was inserted")
            return False

        if story1 is None:
            logger.error("❌ Rollback affected existing story")
            return False

        logger.info("✅ Batch transaction rollback works correctly")
        return True

    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        try:
            Path(db_path).unlink()
        except:
            pass


async def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("State Manager Batch Transaction Fix Test")
    logger.info("=" * 60)

    tests = [
        ("Batch Update 4 Stories", test_batch_update),
        ("Iteration=0 Handling", test_batch_update_with_iteration_zero),
        ("Transaction Rollback", test_batch_transaction_rollback),
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
        logger.info("\n🎉 All tests passed! State Manager batch transaction fix is working correctly.")
        return 0
    else:
        logger.error(f"\n⚠️ {total - passed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
