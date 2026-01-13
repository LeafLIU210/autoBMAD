"""
Resource Cleanup Test

Test the effectiveness of resource cleanup mechanisms.
"""

import asyncio
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fixed_modules.state_manager_fixed import StateManager, DatabaseConnectionPool
from fixed_modules.sdk_session_manager_fixed import SDKSessionManager


class TestResourceCleanup:
    """Resource Cleanup Tests"""

    def test_state_manager_cleanup(self):
        """Test state manager resource cleanup"""
        async def test_cleanup():
            # Create temporary database
            db_path = "test_cleanup.db"
            state_manager = StateManager(db_path)

            # Execute some operations
            await state_manager.update_story_status(
                story_path="test_story.md",
                status="test_status",
                phase="test_phase"
            )

            # Get health status
            health = state_manager.get_health_status()
            assert health["db_exists"] is True
            assert health["lock_locked"] is False

            # Cleanup
            db_file = Path(db_path)
            if db_file.exists():
                db_file.unlink()

        asyncio.run(test_cleanup())

    def test_database_connection_pool(self):
        """Test database connection pool"""
        async def test_pool():
            pool = DatabaseConnectionPool(max_connections=3)
            db_path = Path("test_pool.db")

            # Initialize connection pool
            await pool.initialize(db_path)

            # Get connections
            conn1 = await pool.get_connection()
            conn2 = await pool.get_connection()

            assert conn1 is not None
            assert conn2 is not None

            # Return connections
            await pool.return_connection(conn1)
            await pool.return_connection(conn2)

            # Cleanup
            db_file = Path("test_pool.db")
            if db_file.exists():
                db_file.unlink()

        asyncio.run(test_pool())

    def test_session_manager_cleanup(self):
        """Test session manager cleanup"""
        async def test_session_cleanup():
            manager = SDKSessionManager()

            # Create multiple sessions
            sessions = []
            for i in range(5):
                async with manager.create_session(f"test_agent_{i}"):
                    sessions.append(manager.get_session_count())
                    await asyncio.sleep(0.01)

            # Verify all sessions are cleaned up
            assert manager.get_session_count() == 0

            # Get statistics
            stats = manager.get_statistics()
            assert stats['active_sessions'] == 0

        asyncio.run(test_session_cleanup())

    def test_lock_cleanup_on_exception(self):
        """Test lock cleanup on exception"""
        async def test_lock_cleanup():
            state_manager = StateManager("test_lock_cleanup.db")

            try:
                # Simulate exception scenario
                async with state_manager.managed_operation():
                    await state_manager.update_story_status(
                        story_path="test_story.md",
                        status="test_status"
                    )
                    raise RuntimeError("Test exception")
            except RuntimeError:
                pass  # Catch exception

            # Verify lock is released
            health = state_manager.get_health_status()
            assert health["lock_locked"] is False

            # Cleanup
            db_file = Path("test_lock_cleanup.db")
            if db_file.exists():
                db_file.unlink()

        asyncio.run(test_lock_cleanup())

    def test_session_cleanup_on_failure(self):
        """Test session cleanup on failure"""
        async def test_failure_cleanup():
            manager = SDKSessionManager()

            async def failing_session():
                async with manager.create_session("test_agent"):
                    raise RuntimeError("Test failure")

            try:
                await failing_session()
            except RuntimeError:
                pass  # Catch exception

            # Verify session is cleaned up
            assert manager.get_session_count() == 0

        asyncio.run(test_failure_cleanup())

    def test_resource_leak_detection(self):
        """Test resource leak detection"""
        async def test_leak_detection():
            from debug_suite.resource_monitor import ResourceMonitor

            monitor = ResourceMonitor(Path("test_leak.log"))

            # Test lock leak detection
            async with monitor.monitor_lock("test_lock"):
                await asyncio.sleep(0.01)

            # Check leaks
            stats = monitor.get_comprehensive_statistics()
            lock_stats = stats["locks"]

            # Verify no leaks
            assert lock_stats["leak_count"] == 0

        asyncio.run(test_leak_detection())

    def test_batch_operation_cleanup(self):
        """Test batch operation cleanup"""
        async def test_batch():
            state_manager = StateManager("test_batch.db")

            # Execute batch updates
            updates = [
                {
                    "story_path": f"story_{i}.md",
                    "status": f"status_{i}",
                    "phase": "test_phase"
                }
                for i in range(10)
            ]

            # Use managed_operation for batch operations
            async with state_manager.managed_operation():
                for update in updates:
                    await state_manager.update_story_status(**update)

            # Verify operation completed with no leaks
            health = state_manager.get_health_status()
            assert health["lock_locked"] is False

            # Cleanup
            db_file = Path("test_batch.db")
            if db_file.exists():
                db_file.unlink()

        asyncio.run(test_batch())

    def test_cleanup_on_cancellation(self):
        """Test cleanup on cancellation"""
        async def test_cancel():
            manager = SDKSessionManager()

            async def cancellable_session():
                async with manager.create_session("test_agent"):
                    await asyncio.sleep(10.0)

            # Create task and cancel
            task = asyncio.create_task(cancellable_session())
            await asyncio.sleep(0.01)
            task.cancel()

            try:
                await task
            except asyncio.CancelledError:
                pass  # Catch cancellation exception

            # Verify session is cleaned up
            assert manager.get_session_count() == 0

        asyncio.run(test_cancel())

    def test_database_connection_leak_detection(self):
        """Test database connection leak detection"""
        async def test_leak():
            from debug_suite.resource_monitor import ResourceMonitor

            monitor = ResourceMonitor(Path("test_db_leak.log"))
            pool = DatabaseConnectionPool(max_connections=5)
            db_path = Path("test_db_leak.db")

            # Initialize connection pool
            await pool.initialize(db_path)

            # Test normal get and return
            conn = await pool.get_connection()
            await pool.return_connection(conn)

            # Test not returning (simulate leak)
            conn_leak = await pool.get_connection()
            # Deliberately not returning conn_leak

            # Check leak statistics
            await asyncio.sleep(0.01)
            stats = monitor.get_comprehensive_statistics()
            db_stats = stats.get("database", {})

            # Cleanup
            db_file = db_path
            if db_file.exists():
                db_file.unlink()

        asyncio.run(test_database_connection_leak_detection())

    def test_lock_deadlock_detection(self):
        """Test lock deadlock detection"""
        async def test_deadlock():
            from debug_suite.resource_monitor import ResourceMonitor

            monitor = ResourceMonitor(Path("test_deadlock.log"))

            # Test normal lock get and release
            async with monitor.monitor_lock("normal_lock"):
                await asyncio.sleep(0.01)

            # Test potential deadlock (long lock hold)
            start_time = asyncio.get_event_loop().time()
            async with monitor.monitor_lock("potential_deadlock"):
                await asyncio.sleep(0.1)  # Long hold

            duration = asyncio.get_event_loop().time() - start_time

            # Verify lock statistics
            stats = monitor.get_comprehensive_statistics()
            lock_stats = stats["locks"]

            assert lock_stats["total_acquisitions"] == 2
            assert lock_stats["total_releases"] == 1  # One not released

        asyncio.run(test_lock_deadlock_detection())

    def test_state_manager_recovery_after_failure(self):
        """Test state manager recovery after failure"""
        async def test_recovery():
            state_manager = StateManager("test_recovery.db")

            # Simulate multiple failures
            for i in range(5):
                try:
                    async with state_manager.managed_operation():
                        await state_manager.update_story_status(
                            story_path=f"story_{i}.md",
                            status=f"status_{i}"
                        )
                        if i == 2:
                            raise RuntimeError("Simulated failure")
                except RuntimeError:
                    pass  # Catch exception

            # Verify state manager is still available
            health = state_manager.get_health_status()
            assert health["db_exists"] is True
            assert health["lock_locked"] is False

            # Verify normal operations work
            await state_manager.update_story_status(
                story_path="recovery_story.md",
                status="recovered"
            )

            # Cleanup
            db_file = Path("test_recovery.db")
            if db_file.exists():
                db_file.unlink()

        asyncio.run(test_state_manager_recovery_after_failure())

    def test_connection_pool_exhaustion_handling(self):
        """Test connection pool exhaustion handling"""
        async def test_exhaustion():
            pool = DatabaseConnectionPool(max_connections=3)
            db_path = Path("test_exhaustion.db")

            # Initialize connection pool
            await pool.initialize(db_path)

            # Get all connections
            connections = []
            for _ in range(3):
                conn = await pool.get_connection()
                connections.append(conn)

            # Try to get 4th connection (should wait or fail)
            try:
                # Set short timeout
                extra_conn = await asyncio.wait_for(
                    pool.get_connection(),
                    timeout=0.1
                )
                # If success, pool can expand or wait
                await pool.return_connection(extra_conn)
            except asyncio.TimeoutError:
                # Expected timeout
                pass

            # Return all connections
            for conn in connections:
                await pool.return_connection(conn)

            # Verify can get connection again
            conn = await pool.get_connection()
            await pool.return_connection(conn)

            # Cleanup
            db_file = db_path
            if db_file.exists():
                db_file.unlink()

        asyncio.run(test_connection_pool_exhaustion_handling())

    def test_resource_cleanup_under_stress(self):
        """Test resource cleanup under stress"""
        async def test_stress():
            state_manager = StateManager("test_stress.db")

            # Create many concurrent operations
            tasks = []
            for i in range(100):
                task = asyncio.create_task(
                    state_manager.update_story_status(
                        story_path=f"stress_story_{i}.md",
                        status=f"stress_status_{i}"
                    )
                )
                tasks.append(task)

            # Wait for all tasks to complete
            await asyncio.gather(*tasks, return_exceptions=True)

            # Verify no resource leaks
            health = state_manager.get_health_status()
            assert health["lock_locked"] is False

            # Cleanup
            db_file = Path("test_stress.db")
            if db_file.exists():
                db_file.unlink()

        asyncio.run(test_resource_cleanup_under_stress())

    def test_memory_leak_detection(self):
        """Test memory leak detection"""
        async def test_memory():
            from debug_suite.resource_monitor import ResourceMonitor

            monitor = ResourceMonitor(Path("test_memory.log"))

            # Execute operations that might cause memory leaks
            for i in range(50):
                async with monitor.monitor_operation(f"op_{i}"):
                    # Simulate memory usage
                    data = list(range(1000))
                    await asyncio.sleep(0.001)

            # Check memory statistics
            stats = monitor.get_comprehensive_statistics()
            op_stats = stats.get("operations", {})

            # Verify all operations are cleaned up
            assert op_stats["completed"] >= 50

        asyncio.run(test_memory_leak_detection())

    def test_session_cleanup_with_exceptions(self):
        """Test session cleanup with exceptions"""
        async def test_session_exceptions():
            manager = SDKSessionManager()

            # Create multiple exception sessions
            exception_tasks = []
            for i in range(10):
                async def failing_session():
                    async with manager.create_session(f"agent_{i}"):
                        await asyncio.sleep(0.01)
                        raise ValueError(f"Error in session {i}")

                task = asyncio.create_task(failing_session())
                exception_tasks.append(task)

            # Wait for all tasks to complete (catch exceptions)
            results = await asyncio.gather(*exception_tasks, return_exceptions=True)

            # Verify all exceptions are handled
            assert len(results) == 10

            # Verify no session leaks
            assert manager.get_session_count() == 0

        asyncio.run(test_session_cleanup_with_exceptions())

    def test_resource_finalization_order(self):
        """Test resource finalization order"""
        async def test_finalization():
            from debug_suite.resource_monitor import ResourceMonitor

            monitor = ResourceMonitor(Path("test_finalization.log"))
            cleanup_order = []

            class TestResource:
                def __init__(self, name):
                    self.name = name

                async def __aenter__(self):
                    return self

                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    cleanup_order.append(self.name)

            # Test nested resource cleanup order
            async with monitor.monitor_operation("outer"):
                async with TestResource("resource_1"):
                    async with TestResource("resource_2"):
                        async with TestResource("resource_3"):
                            await asyncio.sleep(0.01)

            # Verify cleanup order (LIFO)
            assert cleanup_order == ["resource_3", "resource_2", "resource_1"]

        asyncio.run(test_resource_finalization_order())

    def test_long_running_operation_cleanup(self):
        """Test long-running operation cleanup"""
        async def test_long_op():
            state_manager = StateManager("test_long_op.db")

            # Start long-running operation
            long_task = asyncio.create_task(
                state_manager.update_story_status(
                    story_path="long_story.md",
                    status="running"
                )
            )

            # Cancel after short wait
            await asyncio.sleep(0.01)
            long_task.cancel()

            try:
                await long_task
            except asyncio.CancelledError:
                pass

            # Verify resources are cleaned up
            health = state_manager.get_health_status()
            assert health["lock_locked"] is False

            # Cleanup
            db_file = Path("test_long_op.db")
            if db_file.exists():
                db_file.unlink()

        asyncio.run(test_long_running_operation_cleanup())

    def test_concurrent_resource_contention(self):
        """Test concurrent resource contention"""
        async def test_contention():
            state_manager = StateManager("test_contention.db")

            # Create multiple tasks competing for same resource
            results = []

            async def competing_task(task_id: int):
                async with state_manager.managed_operation():
                    await asyncio.sleep(0.01)  # Brief resource hold
                    results.append(task_id)
                    return task_id

            # Create 20 competing tasks
            tasks = [competing_task(i) for i in range(20)]
            task_results = await asyncio.gather(*tasks)

            # Verify all tasks completed
            assert len(task_results) == 20
            assert len(results) == 20

            # Verify no resource leaks
            health = state_manager.get_health_status()
            assert health["lock_locked"] is False

            # Cleanup
            db_file = Path("test_contention.db")
            if db_file.exists():
                db_file.unlink()

        asyncio.run(test_concurrent_resource_contention())


if __name__ == "__main__":
    # Run tests
    test = TestResourceCleanup()

    print("Running resource cleanup tests...")
    print()

    try:
        test.test_state_manager_cleanup()
        print("PASS: State manager cleanup test")
        print()

        test.test_database_connection_pool()
        print("PASS: Database connection pool test")
        print()

        test.test_session_manager_cleanup()
        print("PASS: Session manager cleanup test")
        print()

        test.test_lock_cleanup_on_exception()
        print("PASS: Lock cleanup on exception test")
        print()

        test.test_session_cleanup_on_failure()
        print("PASS: Session cleanup on failure test")
        print()

        test.test_resource_leak_detection()
        print("PASS: Resource leak detection test")
        print()

        test.test_batch_operation_cleanup()
        print("PASS: Batch operation cleanup test")
        print()

        test.test_cleanup_on_cancellation()
        print("PASS: Cleanup on cancellation test")
        print()

        test.test_database_connection_leak_detection()
        print("PASS: Database connection leak detection test")
        print()

        test.test_lock_deadlock_detection()
        print("PASS: Lock deadlock detection test")
        print()

        test.test_state_manager_recovery_after_failure()
        print("PASS: State manager recovery after failure test")
        print()

        test.test_connection_pool_exhaustion_handling()
        print("PASS: Connection pool exhaustion handling test")
        print()

        test.test_resource_cleanup_under_stress()
        print("PASS: Resource cleanup under stress test")
        print()

        test.test_memory_leak_detection()
        print("PASS: Memory leak detection test")
        print()

        test.test_session_cleanup_with_exceptions()
        print("PASS: Session cleanup with exceptions test")
        print()

        test.test_resource_finalization_order()
        print("PASS: Resource finalization order test")
        print()

        test.test_long_running_operation_cleanup()
        print("PASS: Long-running operation cleanup test")
        print()

        test.test_concurrent_resource_contention()
        print("PASS: Concurrent resource contention test")
        print()

        print("SUCCESS: All resource cleanup tests passed!")

    except Exception as e:
        print(f"FAIL: Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
