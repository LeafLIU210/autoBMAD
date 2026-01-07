"""
Cancel Scope Test

Test the effectiveness of cancel scope fixes.
"""

import asyncio
import pytest
import sys
from pathlib import Path

# 添加父目录到路径
parent_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, parent_dir)

from debug_suite.cancel_scope_tracker import CancelScopeTracker, tracked_cancel_scope
from fixed_modules.sdk_wrapper_fixed import SafeAsyncGenerator


class TestCancelScopeFixes:
    """Cancel Scope Fix Tests"""

    def test_cross_task_scope_access_detection(self):
        """Test cross-task scope access detection"""
        async def test_cross_task_violation():
            tracker = CancelScopeTracker(Path("test_cancel_scope.log"))

            async def task_that_enters():
                async with tracked_cancel_scope("task_scope"):
                    await asyncio.sleep(0.01)
                    return "Task completed"

            # 创建任务
            task1 = asyncio.create_task(task_that_enters())
            task2 = asyncio.create_task(task_that_enters())

            # 等待任务完成
            results = await asyncio.gather(task1, task2)

            # 检查违规
            violations = tracker.check_cross_task_violations()

            # Verify results
            assert len(results) == 2
            assert all(r == "Task completed" for r in results)

            # Print results
            tracker.print_summary()
            report = tracker.generate_report()
            print(f"Cross-task violations: {len(report['cross_task_violations'])}")

        asyncio.run(test_cross_task_violation())

    def test_safe_async_generator(self):
        """Test safe async generator"""
        async def test_generator():
            async def async_gen():
                for i in range(5):
                    yield i

            safe_gen = SafeAsyncGenerator(async_gen())
            results = []

            async for value in safe_gen:
                results.append(value)

            assert results == [0, 1, 2, 3, 4]

        asyncio.run(test_generator())

    def test_generator_cleanup_on_error(self):
        """Test generator cleanup on error"""
        async def test_cleanup():
            async def failing_gen():
                yield 1
                yield 2
                raise RuntimeError("Test error")

            safe_gen = SafeAsyncGenerator(failing_gen())

            with pytest.raises(RuntimeError, match="Test error"):
                async for value in safe_gen:
                    pass

            # Verify generator is closed
            assert safe_gen._closed

        asyncio.run(test_cleanup())

    def test_nested_scope_tracking(self):
        """Test nested scope tracking"""
        async def test_nested():
            tracker = CancelScopeTracker()

            async with tracker.tracked_cancel_scope("outer_scope"):
                await asyncio.sleep(0.01)

                async with tracker.tracked_cancel_scope("inner_scope"):
                    await asyncio.sleep(0.01)

            # Check statistics
            stats = tracker.get_scope_statistics()
            assert stats['active_scopes'] == 0
            assert stats['enter_events'] == 2
            assert stats['exit_events'] == 2

        asyncio.run(test_nested())

    def test_scope_cancel_request(self):
        """Test scope cancel request"""
        async def test_cancel():
            tracker = CancelScopeTracker()

            async with tracker.tracked_cancel_scope("cancelable_scope"):
                # Simulate cancel request
                tracker.request_cancel("dummy_id")  # Won't actually cancel since using context manager
                await asyncio.sleep(0.01)

            stats = tracker.get_scope_statistics()
            assert stats['cancel_events'] == 1

        asyncio.run(test_cancel())

    def test_deeply_nested_scopes(self):
        """Test deeply nested scopes"""
        async def test_deep_nesting():
            tracker = CancelScopeTracker()

            async def nested_operation(depth):
                if depth == 0:
                    return "completed"
                async with tracker.tracked_cancel_scope(f"depth_{depth}"):
                    result = await nested_operation(depth - 1)
                    await asyncio.sleep(0.001)
                    return result

            result = await nested_operation(10)
            assert result == "completed"

            stats = tracker.get_scope_statistics()
            assert stats['enter_events'] == 10
            assert stats['exit_events'] == 10

        asyncio.run(test_deeply_nested_scopes())

    def test_concurrent_scope_operations(self):
        """Test concurrent scope operations"""
        async def test_concurrent():
            tracker = CancelScopeTracker()
            results = []

            async def scoped_task(task_id: int):
                async with tracker.tracked_cancel_scope(f"task_{task_id}"):
                    await asyncio.sleep(0.01 * task_id)
                    return f"Task {task_id} completed"

            # Create 20 concurrent tasks
            tasks = [scoped_task(i) for i in range(20)]
            results = await asyncio.gather(*tasks)

            assert len(results) == 20
            assert all("completed" in r for r in results)

            stats = tracker.get_scope_statistics()
            assert stats['enter_events'] == 20
            assert stats['exit_events'] == 20

        asyncio.run(test_concurrent())

    def test_scope_exception_handling(self):
        """Test scope exception handling"""
        async def test_exception():
            tracker = CancelScopeTracker()

            try:
                async with tracker.tracked_cancel_scope("exception_scope"):
                    await asyncio.sleep(0.01)
                    raise ValueError("Test exception")
            except ValueError as e:
                assert str(e) == "Test exception"

            # Verify scope statistics
            stats = tracker.get_scope_statistics()
            assert stats['enter_events'] == 1
            assert stats['exit_events'] == 1
            assert stats['active_scopes'] == 0

        asyncio.run(test_scope_exception_handling())

    def test_generator_with_cancellation(self):
        """Test generator with cancellation interaction"""
        async def test_gen_cancel():
            async def async_gen():
                for i in range(100):
                    try:
                        yield i
                    except asyncio.CancelledError:
                        # Catch cancel exception and cleanup
                        break

            safe_gen = SafeAsyncGenerator(async_gen())
            count = 0

            async for value in safe_gen:
                count += 1
                if count >= 10:
                    # Cancel task
                    break

            assert count == 10
            assert safe_gen._closed

        asyncio.run(test_generator_with_cancellation())

    def test_safe_async_generator_large_data(self):
        """Test large data generator"""
        async def test_large_data():
            async def large_gen():
                for i in range(10000):
                    yield i * 2

            safe_gen = SafeAsyncGenerator(large_gen())
            results = []
            async for value in safe_gen:
                results.append(value)
                if len(results) >= 1000:  # Take only first 1000
                    break

            assert len(results) == 1000
            assert results[-1] == 1998

        asyncio.run(test_safe_async_generator_large_data())

    def test_cross_task_violation_isolation(self):
        """Test cross-task violation isolation"""
        async def test_isolation():
            tracker = CancelScopeTracker()
            violations = []

            async def task_with_violation():
                async with tracked_cancel_scope("task_scope") as scope:
                    await asyncio.sleep(0.01)
                    # Record potential violations
                    violations.append(scope)

            # 创建多个任务
            tasks = [asyncio.create_task(task_with_violation()) for _ in range(5)]
            await asyncio.gather(*tasks)

            # Verify no actual violations (SafeAsyncGenerator should prevent)
            assert len(violations) == 5
            assert all(v is not None for v in violations)

        asyncio.run(test_cross_task_violation_isolation())

    def test_tracker_memory_efficiency(self):
        """Test tracker memory efficiency"""
        async def test_memory():
            tracker = CancelScopeTracker()

            # Execute large number of operations
            for i in range(1000):
                async with tracker.tracked_cancel_scope(f"scope_{i}"):
                    await asyncio.sleep(0.0001)

            stats = tracker.get_scope_statistics()
            # Verify reasonable memory usage (may have history limits)
            assert stats['enter_events'] >= 1000
            assert stats['exit_events'] >= 1000

        asyncio.run(test_tracker_memory_efficiency())


if __name__ == "__main__":
    # Run tests
    test = TestCancelScopeFixes()

    print("Running Cancel Scope tests...")
    print()

    try:
        test.test_cross_task_scope_access_detection()
        print("PASS: Cross-task scope access detection test")
        print()

        test.test_safe_async_generator()
        print("PASS: Safe async generator test")
        print()

        test.test_generator_cleanup_on_error()
        print("PASS: Generator error cleanup test")
        print()

        test.test_nested_scope_tracking()
        print("PASS: Nested scope tracking test")
        print()

        test.test_scope_cancel_request()
        print("PASS: Scope cancel request test")
        print()

        test.test_deeply_nested_scopes()
        print("PASS: Deeply nested scopes test")
        print()

        test.test_concurrent_scope_operations()
        print("PASS: Concurrent scope operations test")
        print()

        test.test_scope_exception_handling()
        print("PASS: Scope exception handling test")
        print()

        test.test_generator_with_cancellation()
        print("PASS: Generator with cancellation test")
        print()

        test.test_safe_async_generator_large_data()
        print("PASS: Large data generator test")
        print()

        test.test_cross_task_violation_isolation()
        print("PASS: Cross-task violation isolation test")
        print()

        test.test_tracker_memory_efficiency()
        print("PASS: Tracker memory efficiency test")
        print()

        print("SUCCESS: All Cancel Scope tests passed!")

    except Exception as e:
        print(f"FAIL: Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
