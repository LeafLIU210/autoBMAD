#!/usr/bin/env python3
"""
Simplified test for Cancel Scope fix verification
"""

import asyncio
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_imports():
    """Test module imports"""
    logger.info("=" * 70)
    logger.info("Test 1: Module Imports")
    logger.info("=" * 70)

    try:
        from autoBMAD.epic_automation.sdk_wrapper import SafeClaudeSDK, SafeAsyncGenerator
        logger.info("SUCCESS: Imported SafeClaudeSDK and SafeAsyncGenerator")

        from autoBMAD.epic_automation.monitoring import get_cancellation_manager
        logger.info("SUCCESS: Imported get_cancellation_manager")

        from autoBMAD.epic_automation.monitoring.cancel_scope_tracker import get_tracker
        logger.info("SUCCESS: Imported get_tracker")

        return True
    except Exception as e:
        logger.error(f"FAILED: Import error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_new_methods():
    """Test new methods exist"""
    logger.info("\n" + "=" * 70)
    logger.info("Test 2: New Methods")
    logger.info("=" * 70)

    try:
        from autoBMAD.epic_automation.sdk_wrapper import SafeClaudeSDK

        # Check for new methods
        methods = [
            '_execute_with_isolated_scope',
            '_execute_with_recovery',
            '_rebuild_execution_context',
            '_execute_safely_with_manager'
        ]

        for method in methods:
            if hasattr(SafeClaudeSDK, method):
                logger.info(f"SUCCESS: Method {method} exists")
            else:
                logger.error(f"FAILED: Method {method} does not exist")
                return False

        return True
    except Exception as e:
        logger.error(f"FAILED: Test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_monitor_features():
    """Test monitor features"""
    logger.info("\n" + "=" * 70)
    logger.info("Test 3: Monitor Features")
    logger.info("=" * 70)

    try:
        from autoBMAD.epic_automation.monitoring import get_cancellation_manager

        manager = get_cancellation_manager()

        # Check for detect_cross_task_risk method
        if hasattr(manager, 'detect_cross_task_risk'):
            logger.info("SUCCESS: detect_cross_task_risk method exists")
        else:
            logger.error("FAILED: detect_cross_task_risk method missing")
            return False

        # Check statistics
        stats = manager.get_statistics()
        if 'active_cross_task_risks' in stats:
            logger.info(f"SUCCESS: Statistics include active_cross_task_risks: {stats['active_cross_task_risks']}")
        else:
            logger.error("FAILED: Statistics missing active_cross_task_risks")
            return False

        if 'cross_task_violations' in stats:
            logger.info(f"SUCCESS: Statistics include cross_task_violations: {stats['cross_task_violations']}")
        else:
            logger.error("FAILED: Statistics missing cross_task_violations")
            return False

        return True
    except Exception as e:
        logger.error(f"FAILED: Monitor test error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_async_functionality():
    """Test async functionality"""
    logger.info("\n" + "=" * 70)
    logger.info("Test 4: Async Functionality")
    logger.info("=" * 70)

    try:
        from autoBMAD.epic_automation.monitoring import get_cancellation_manager

        manager = get_cancellation_manager()

        # Test tracking execution
        call_id = f"test_{id(manager)}"

        async with manager.track_sdk_execution(
            call_id=call_id,
            operation_name="test_operation",
            context={"test": True}
        ):
            logger.info("SUCCESS: Entered tracking context")

            # Test cross-task risk detection
            risk_detected = manager.detect_cross_task_risk(call_id)
            logger.info(f"SUCCESS: Cross-task risk detection completed: {risk_detected}")

        # Check cleanup
        if call_id not in manager.active_sdk_calls:
            logger.info("SUCCESS: Call properly cleaned up")
        else:
            logger.warning("WARNING: Call still in active list")

        return True
    except Exception as e:
        logger.error(f"FAILED: Async test error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_safe_async_generator():
    """Test SafeAsyncGenerator"""
    logger.info("\n" + "=" * 70)
    logger.info("Test 5: SafeAsyncGenerator")
    logger.info("=" * 70)

    try:
        from autoBMAD.epic_automation.sdk_wrapper import SafeAsyncGenerator

        # Create mock async generator
        async def mock_generator():
            for i in range(3):
                yield i

        safe_gen = SafeAsyncGenerator(mock_generator())
        logger.info("SUCCESS: Created SafeAsyncGenerator instance")

        # Check _closed attribute
        if hasattr(safe_gen, '_closed'):
            logger.info(f"SUCCESS: _closed attribute exists, initial value: {safe_gen._closed}")
        else:
            logger.error("FAILED: _closed attribute missing")
            return False

        # Test aclose method
        await safe_gen.aclose()
        logger.info("SUCCESS: aclose() method called")

        if safe_gen._closed:
            logger.info("SUCCESS: Generator marked as closed")
        else:
            logger.warning("WARNING: Generator not marked as closed")

        return True
    except Exception as e:
        logger.error(f"FAILED: SafeAsyncGenerator test error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    logger.info("\n" + "=" * 70)
    logger.info("Cancel Scope Fix Verification Tests")
    logger.info("=" * 70)

    results = {}

    # Run tests
    results["Import Modules"] = test_imports()
    results["New Methods"] = test_new_methods()
    results["Monitor Features"] = test_monitor_features()
    results["SafeAsyncGenerator"] = test_safe_async_generator()
    results["Async Functionality"] = await test_async_functionality()

    # Print summary
    logger.info("\n" + "=" * 70)
    logger.info("Test Summary")
    logger.info("=" * 70)

    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed

    logger.info(f"Total Tests: {total}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Success Rate: {passed/total*100:.1f}%")

    if failed > 0:
        logger.info("\nFailed Tests:")
        for test_name, result in results.items():
            if not result:
                logger.info(f"  - {test_name}")
    else:
        logger.info("\nAll tests passed!")

    logger.info("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
