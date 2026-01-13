"""
SDK Sessions Test

Test the effectiveness of SDK session management fixes.
"""

import asyncio
import pytest
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from fixed_modules.sdk_session_manager_fixed import (
    SDKSessionManager,
    SDKErrorType,
    SDKExecutionResult,
    SessionHealthChecker
)


class TestSDKSessionManager:
    """SDK Session Manager Tests"""

    def test_session_creation_and_cleanup(self):
        """Test session creation and cleanup"""
        async def test_sessions():
            manager = SDKSessionManager()

            # Test session creation
            async with manager.create_session("test_agent"):
                assert manager.get_session_count() == 1
                active_sessions = manager.get_active_sessions()
                assert len(active_sessions) == 1

            # Verify session is cleaned up
            assert manager.get_session_count() == 0

        asyncio.run(test_sessions())

    def test_multiple_concurrent_sessions(self):
        """Test multiple concurrent sessions"""
        async def test_concurrent():
            manager = SDKSessionManager()

            results = []

            async def session_task(task_id: int):
                async with manager.create_session(f"agent_{task_id}"):
                    await asyncio.sleep(0.01)
                    return f"Task {task_id} completed"

            # Create concurrent tasks
            tasks = [session_task(i) for i in range(5)]
            results = await asyncio.gather(*tasks)

            # Verify all tasks completed
            assert len(results) == 5
            assert all(f"Task {i} completed" in results[i] for i in range(5))

            # Verify no active sessions
            assert manager.get_session_count() == 0

        asyncio.run(test_concurrent())

    def test_session_isolation(self):
        """Test session isolation"""
        async def test_isolation():
            manager = SDKSessionManager()

            session_ids = []

            # Create multiple sessions
            for i in range(3):
                async with manager.create_session(f"agent_{i}") as context:
                    session_ids.append(context.session_id)
                    # Verify each session has unique ID
                    assert len(context.session_id) > 0
                    await asyncio.sleep(0.01)

            # Verify all session IDs are unique
            assert len(session_ids) == len(set(session_ids))

        asyncio.run(test_isolation())

    def test_execution_result_structure(self):
        """Test execution result structure"""
        # Create test result
        result = SDKExecutionResult(
            success=True,
            error_type=SDKErrorType.SUCCESS,
            error_message=None,
            duration_seconds=1.5,
            session_id="test_session_123",
            retry_count=0
        )

        # Verify result attributes
        assert result.success is True
        assert result.error_type == SDKErrorType.SUCCESS
        assert result.duration_seconds == 1.5
        assert result.session_id == "test_session_123"
        assert result.retry_count == 0
        assert result.is_cancelled() is False
        assert result.is_timeout() is False
        assert result.is_retryable_error() is False

    def test_error_types(self):
        """Test error types"""
        # Test different error types
        timeout_result = SDKExecutionResult(
            success=False,
            error_type=SDKErrorType.TIMEOUT
        )
        assert timeout_result.is_timeout() is True
        assert timeout_result.is_retryable_error() is True

        cancelled_result = SDKExecutionResult(
            success=False,
            error_type=SDKErrorType.CANCELLED
        )
        assert cancelled_result.is_cancelled() is True
        assert cancelled_result.is_retryable_error() is False

    def test_successful_execution(self):
        """Test successful execution"""
        async def test_success():
            manager = SDKSessionManager()

            # Create successful SDK function
            async def successful_func():
                await asyncio.sleep(0.01)
                return True

            result = await manager.execute_isolated(
                agent_name="test_agent",
                sdk_func=successful_func,
                timeout=5.0
            )

            # Verify result
            assert result.success is True
            assert result.error_type == SDKErrorType.SUCCESS
            assert result.duration_seconds > 0
            assert result.session_id != ""

        asyncio.run(test_success())

    def test_failed_execution(self):
        """Test failed execution"""
        async def test_failure():
            manager = SDKSessionManager()

            # Create failing SDK function
            async def failing_func():
                await asyncio.sleep(0.01)
                return False

            result = await manager.execute_isolated(
                agent_name="test_agent",
                sdk_func=failing_func,
                timeout=5.0
            )

            # Verify result
            assert result.success is False
            assert result.error_type == SDKErrorType.SDK_ERROR

        asyncio.run(test_failure())

    def test_timeout_execution(self):
        """Test timeout execution"""
        async def test_timeout():
            manager = SDKSessionManager()

            # Create timeout SDK function
            async def slow_func():
                await asyncio.sleep(0.1)  # 100ms
                return True

            result = await manager.execute_isolated(
                agent_name="test_agent",
                sdk_func=slow_func,
                timeout=0.05  # 50ms timeout
            )

            # Verify result
            assert result.success is False
            assert result.error_type == SDKErrorType.TIMEOUT

        asyncio.run(test_timeout())

    def test_cancelled_execution(self):
        """Test cancelled execution"""
        async def test_cancellation():
            manager = SDKSessionManager()

            # Create cancellable SDK function
            async def cancellable_func():
                await asyncio.sleep(10.0)  # Long wait
                return True

            # Create task and cancel immediately
            task = asyncio.create_task(
                manager.execute_isolated(
                    agent_name="test_agent",
                    sdk_func=cancellable_func,
                    timeout=5.0
                )
            )

            await asyncio.sleep(0.01)  # Brief wait
            task.cancel()

            try:
                result = await task
                # If cancellation is handled correctly, result should indicate cancellation
                assert result.success is False
                assert result.error_type == SDKErrorType.CANCELLED
            except asyncio.CancelledError:
                # Cancel exception being thrown is also acceptable
                pass

        asyncio.run(test_cancellation())

    def test_statistics(self):
        """Test statistics"""
        async def test_stats():
            manager = SDKSessionManager()

            # Execute some operations
            async def success_func():
                await asyncio.sleep(0.01)
                return True

            async def failure_func():
                await asyncio.sleep(0.01)
                return False

            # Successful execution
            await manager.execute_isolated("agent_success", success_func)

            # Failed execution
            await manager.execute_isolated("agent_failure", failure_func)

            # Get statistics
            stats = manager.get_statistics()

            # Verify statistics
            assert stats['total_sessions'] >= 2
            assert stats['successful_sessions'] >= 1
            assert stats['failed_sessions'] >= 1
            assert stats['active_sessions'] == 0  # All sessions should be completed
            assert stats['success_rate'] >= 0  # Between 0-100
            assert 0 <= stats['failure_rate'] <= 100

        asyncio.run(test_stats())

    def test_session_health_checker(self):
        """Test session health checker"""
        async def test_health():
            checker = SessionHealthChecker()
            session_id = "test_session_123"

            # Initial health status
            assert await checker.check_session_health(session_id) is True

            # Record health checks
            checker.record_health_check(session_id, True, {"test": "ok"})
            checker.record_health_check(session_id, True, {"test": "ok"})
            checker.record_health_check(session_id, True, {"test": "ok"})

            # Still healthy
            assert await checker.check_session_health(session_id) is True

            # Record failures
            checker.record_health_check(session_id, False, {"error": "test"})
            checker.record_health_check(session_id, False, {"error": "test"})
            checker.record_health_check(session_id, False, {"error": "test"})

            # Consecutive failures reach threshold, should be unhealthy
            assert await checker.check_session_health(session_id) is False

            # Record some successes, should be recovering
            checker.record_health_check(session_id, True, {"test": "ok"})
            assert checker.is_session_recovering(session_id) is True

            # Enough successes, should recover
            checker.record_health_check(session_id, True, {"test": "ok"})
            assert await checker.check_session_health(session_id) is True

        asyncio.run(test_health())

    def test_session_retry_mechanism(self):
        """Test session retry mechanism"""
        async def test_retry():
            manager = SDKSessionManager()

            attempt_count = 0

            async def flaky_func():
                nonlocal attempt_count
                attempt_count += 1
                if attempt_count < 3:
                    raise RuntimeError("Temporary failure")
                return "Success after retry"

            result = await manager.execute_isolated(
                agent_name="test_agent",
                sdk_func=flaky_func,
                timeout=5.0,
                max_retries=3
            )

            # Verify retry success
            assert result.success is True
            assert result.retry_count > 0
            assert result.duration_seconds > 0

        asyncio.run(test_session_retry_mechanism())

    def test_session_concurrent_load(self):
        """Test session concurrent load"""
        async def test_load():
            manager = SDKSessionManager()

            async def load_task(task_id: int):
                async def load_func():
                    await asyncio.sleep(0.01)
                    return {"task_id": task_id, "status": "ok"}

                result = await manager.execute_isolated(
                    agent_name=f"load_agent_{task_id}",
                    sdk_func=load_func,
                    timeout=5.0
                )
                return result.success

            # Create 100 concurrent tasks
            tasks = [load_task(i) for i in range(100)]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Verify all tasks completed
            successful = sum(1 for r in results if r is True)
            assert successful >= 95  # At least 95% success rate

            # Verify no active session leaks
            assert manager.get_session_count() == 0

        asyncio.run(test_session_concurrent_load())

    def test_session_error_recovery(self):
        """Test session error recovery"""
        async def test_recovery():
            manager = SDKSessionManager()

            # Simulate consecutive errors
            error_count = 0

            async def error_func():
                nonlocal error_count
                error_count += 1
                if error_count <= 2:
                    raise ConnectionError("Network error")
                return "Recovered"

            result = await manager.execute_isolated(
                agent_name="test_agent",
                sdk_func=error_func,
                timeout=5.0,
                max_retries=5
            )

            # Verify recovery success
            assert result.success is True
            assert result.retry_count >= 2

        asyncio.run(test_session_error_recovery())

    def test_session_performance_metrics(self):
        """Test session performance metrics"""
        async def test_metrics():
            manager = SDKSessionManager()

            # Execute multiple operations
            async def quick_func():
                await asyncio.sleep(0.01)
                return True

            async def slow_func():
                await asyncio.sleep(0.1)
                return True

            # Quick operations
            for _ in range(5):
                await manager.execute_isolated("quick_agent", quick_func)

            # Slow operations
            for _ in range(3):
                await manager.execute_isolated("slow_agent", slow_func)

            # Get statistics
            stats = manager.get_statistics()

            # Verify performance metrics
            assert stats['total_sessions'] >= 8
            assert stats['average_duration'] > 0
            assert stats['min_duration'] > 0
            assert stats['max_duration'] >= 0.1  # Includes slow operations

        asyncio.run(test_session_performance_metrics())

    def test_session_isolation_stress(self):
        """Test session isolation stress test"""
        async def test_isolation_stress():
            manager = SDKSessionManager()

            shared_data = {"counter": 0}

            async def isolated_task(task_id: int):
                # Each task should have its own session
                async with manager.create_session(f"agent_{task_id}") as session:
                    # Modify shared data (simulate incorrect usage)
                    shared_data["counter"] += 1
                    await asyncio.sleep(0.001)

                    # Verify session isolation
                    assert session.session_id is not None
                    return {
                        "task_id": task_id,
                        "session_id": session.session_id,
                        "counter": shared_data["counter"]
                    }

            # Create 50 concurrent tasks
            tasks = [isolated_task(i) for i in range(50)]
            results = await asyncio.gather(*tasks)

            # Verify all sessions have unique IDs
            session_ids = [r["session_id"] for r in results]
            assert len(session_ids) == len(set(session_ids))

            # Verify concurrent modification of shared data
            assert shared_data["counter"] == 50

        asyncio.run(test_session_isolation_stress())

    def test_session_timeout_handling(self):
        """Test session timeout handling"""
        async def test_timeout():
            manager = SDKSessionManager()

            async def slow_func():
                await asyncio.sleep(0.5)
                return True

            result = await manager.execute_isolated(
                agent_name="test_agent",
                sdk_func=slow_func,
                timeout=0.1
            )

            # Verify timeout handling
            assert result.success is False
            assert result.is_timeout() is True
            assert result.error_type == SDKErrorType.TIMEOUT

        asyncio.run(test_session_timeout_handling())

    def test_session_concurrent_execution_order(self):
        """Test session concurrent execution order"""
        async def test_order():
            manager = SDKSessionManager()
            execution_order = []

            async def ordered_func(order_id: int):
                await asyncio.sleep(0.001 * (10 - order_id))  # Reverse delay
                execution_order.append(order_id)
                return order_id

            # Create multiple tasks
            tasks = [
                manager.execute_isolated(f"agent_{i}", ordered_func, timeout=5.0)
                for i in range(10)
            ]

            results = await asyncio.gather(*tasks)

            # Verify all tasks completed
            assert len(results) == 10
            assert all(r.success for r in results)

            # Verify execution order (slower ones complete first)
            assert execution_order == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        asyncio.run(test_session_concurrent_execution_order())

    def test_session_cleanup_on_garbage_collection(self):
        """Test session cleanup on garbage collection"""
        import gc

        async def test_gc():
            manager = SDKSessionManager()

            async def session_func():
                await asyncio.sleep(0.01)
                return True

            # Create session but don't explicitly close
            task = asyncio.create_task(
                manager.execute_isolated("test_agent", session_func)
            )

            await task
            await asyncio.sleep(0.01)

            # Force garbage collection
            gc.collect()

            # Verify no session leaks
            assert manager.get_session_count() == 0

        asyncio.run(test_session_cleanup_on_garbage_collection())


if __name__ == "__main__":
    # Run tests
    test = TestSDKSessionManager()

    print("Running SDK Sessions tests...")
    print()

    try:
        test.test_session_creation_and_cleanup()
        print("PASS: Session creation and cleanup test")
        print()

        test.test_multiple_concurrent_sessions()
        print("PASS: Multiple concurrent sessions test")
        print()

        test.test_session_isolation()
        print("PASS: Session isolation test")
        print()

        test.test_execution_result_structure()
        print("PASS: Execution result structure test")
        print()

        test.test_error_types()
        print("PASS: Error types test")
        print()

        test.test_successful_execution()
        print("PASS: Successful execution test")
        print()

        test.test_failed_execution()
        print("PASS: Failed execution test")
        print()

        test.test_timeout_execution()
        print("PASS: Timeout execution test")
        print()

        test.test_cancelled_execution()
        print("PASS: Cancelled execution test")
        print()

        test.test_statistics()
        print("PASS: Statistics test")
        print()

        test.test_session_health_checker()
        print("PASS: Session health checker test")
        print()

        test.test_session_retry_mechanism()
        print("PASS: Session retry mechanism test")
        print()

        test.test_session_concurrent_load()
        print("PASS: Session concurrent load test")
        print()

        test.test_session_error_recovery()
        print("PASS: Session error recovery test")
        print()

        test.test_session_performance_metrics()
        print("PASS: Session performance metrics test")
        print()

        test.test_session_isolation_stress()
        print("PASS: Session isolation stress test")
        print()

        test.test_session_timeout_handling()
        print("PASS: Session timeout handling test")
        print()

        test.test_session_concurrent_execution_order()
        print("PASS: Session concurrent execution order test")
        print()

        test.test_session_cleanup_on_garbage_collection()
        print("PASS: Session cleanup on garbage collection test")
        print()

        print("SUCCESS: All SDK Sessions tests passed!")

    except Exception as e:
        print(f"FAIL: Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
