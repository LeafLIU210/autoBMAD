"""
Integration Tests

Test integration between system components after fixes.
"""

import asyncio
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fixed_modules.sdk_wrapper_fixed import SafeAsyncGenerator
from fixed_modules.sdk_session_manager_fixed import SDKSessionManager
from fixed_modules.state_manager_fixed import StateManager


class TestIntegrationScenarios:
    """Integration Scenario Tests"""

    def test_sdk_session_with_state_manager(self):
        """Test SDK session with state manager integration"""
        async def test_integration():
            # Initialize components
            session_manager = SDKSessionManager()
            state_manager = StateManager("integration_test.db")

            # Execute session operations requiring state management
            async def session_with_state():
                async with session_manager.create_session("test_agent") as session:
                    # Update state
                    await state_manager.update_story_status(
                        story_path="integration_story.md",
                        status="processing",
                        phase="session_phase"
                    )

                    # Simulate some work
                    await asyncio.sleep(0.01)

                    # Update state again
                    await state_manager.update_story_status(
                        story_path="integration_story.md",
                        status="completed",
                        phase="session_phase"
                    )

                    return session.session_id

            # Execute integration operation
            session_id = await session_with_state()

            # Verify
            assert session_id is not None
            health = state_manager.get_health_status()
            assert health["db_exists"] is True

            # Cleanup
            db_file = Path("integration_test.db")
            if db_file.exists():
                db_file.unlink()

        asyncio.run(test_sdk_session_with_state_manager())

    def test_qa_agent_with_session_manager(self):
        """Test QA agent with session manager integration"""
        async def test_qa_integration():
            session_manager = SDKSessionManager()

            # Create a mock QA session operation
            async with session_manager.create_session("qa_agent") as session:
                # Execute mock QA operation
                result = await session_manager.execute_isolated(
                    agent_name="qa_agent",
                    sdk_func=lambda: {"status": "completed", "session_id": session.session_id},
                    timeout=5.0
                )

                # Verify
                assert result is not None
                assert result.success is True

        asyncio.run(test_qa_integration())

    def test_end_to_end_workflow(self):
        """Test end-to-end workflow"""
        async def test_e2e():
            # Initialize all components
            session_manager = SDKSessionManager()
            state_manager = StateManager("e2e_test.db")

            workflow_results = []

            # Execute complete workflow
            async def e2e_task(task_id: int):
                # 1. Create session
                async with session_manager.create_session(f"agent_{task_id}") as session:
                    # 2. Update state
                    await state_manager.update_story_status(
                        story_path=f"story_{task_id}.md",
                        status="started",
                        phase="e2e_phase"
                    )

                    # 3. Simulate processing
                    await asyncio.sleep(0.01)

                    # 4. Update state
                    await state_manager.update_story_status(
                        story_path=f"story_{task_id}.md",
                        status="completed",
                        phase="e2e_phase"
                    )

                    workflow_results.append({
                        "task_id": task_id,
                        "session_id": session.session_id,
                        "status": "completed"
                    })

                    return session.session_id

            # Execute multiple concurrent tasks
            tasks = [e2e_task(i) for i in range(10)]
            session_ids = await asyncio.gather(*tasks)

            # Verify
            assert len(session_ids) == 10
            assert len(workflow_results) == 10
            assert all(r["status"] == "completed" for r in workflow_results)

            # Verify all session IDs are unique
            assert len(session_ids) == len(set(session_ids))

            # Cleanup
            db_file = Path("e2e_test.db")
            if db_file.exists():
                db_file.unlink()

        asyncio.run(test_end_to_end_workflow())

    def test_cancellation_with_integration(self):
        """Test cancellation in integration scenarios"""
        async def test_cancel_integration():
            session_manager = SDKSessionManager()
            state_manager = StateManager("cancel_integration.db")

            # Create task that will be cancelled
            async def cancellable_task():
                async with session_manager.create_session("test_agent"):
                    # Update state
                    await state_manager.update_story_status(
                        story_path="cancel_story.md",
                        status="cancelled",
                        phase="cancel_phase"
                    )

                    # Long wait
                    await asyncio.sleep(10.0)

                    return "should not reach here"

            # Create task and cancel
            task = asyncio.create_task(cancellable_task())
            await asyncio.sleep(0.01)
            task.cancel()

            try:
                await task
            except asyncio.CancelledError:
                pass

            # Verify resource cleanup
            assert session_manager.get_session_count() == 0
            health = state_manager.get_health_status()
            assert health["lock_locked"] is False

            # Cleanup
            db_file = Path("cancel_integration.db")
            if db_file.exists():
                db_file.unlink()

        asyncio.run(test_cancellation_with_integration())

    def test_timeout_with_state_management(self):
        """Test timeout with state management integration"""
        async def test_timeout_state():
            session_manager = SDKSessionManager()
            state_manager = StateManager("timeout_state.db")

            async def slow_operation():
                async with session_manager.create_session("test_agent"):
                    # Update state
                    await state_manager.update_story_status(
                        story_path="timeout_story.md",
                        status="timeout_test",
                        phase="timeout_phase"
                    )

                    # Long wait
                    await asyncio.sleep(1.0)

                    return "completed"

            # Execute operation with timeout
            result = await session_manager.execute_isolated(
                agent_name="test_agent",
                sdk_func=slow_operation,
                timeout=0.1
            )

            # Verify timeout
            assert result.is_timeout() is True

            # Verify state manager is still available
            health = state_manager.get_health_status()
            assert health["db_exists"] is True
            assert health["lock_locked"] is False

            # Cleanup
            db_file = Path("timeout_state.db")
            if db_file.exists():
                db_file.unlink()

        asyncio.run(test_timeout_with_state_management())

    def test_error_recovery_integration(self):
        """Test error recovery in integration scenarios"""
        async def test_recovery():
            session_manager = SDKSessionManager()
            state_manager = StateManager("recovery_integration.db")

            recovery_count = 0

            async def recoverable_operation():
                nonlocal recovery_count
                recovery_count += 1

                if recovery_count <= 3:
                    # First 3 attempts fail
                    await state_manager.update_story_status(
                        story_path="recovery_story.md",
                        status=f"failed_attempt_{recovery_count}",
                        phase="recovery_phase"
                    )
                    raise RuntimeError("Temporary failure")
                else:
                    # 4th attempt succeeds
                    await state_manager.update_story_status(
                        story_path="recovery_story.md",
                        status="recovered",
                        phase="recovery_phase"
                    )
                    return "recovered"

            # Execute recovery operation
            result = await session_manager.execute_isolated(
                agent_name="test_agent",
                sdk_func=recoverable_operation,
                timeout=5.0,
                max_retries=5
            )

            # Verify recovery
            assert result.success is True
            assert result.retry_count >= 3

            # Cleanup
            db_file = Path("recovery_integration.db")
            if db_file.exists():
                db_file.unlink()

        asyncio.run(test_error_recovery_integration())

    def test_concurrent_integration_scenarios(self):
        """Test concurrent integration scenarios"""
        async def test_concurrent_integration():
            session_manager = SDKSessionManager()
            state_manager = StateManager("concurrent_integration.db")

            async def integration_task(task_id: int):
                # Each task has its own session and state operations
                async with session_manager.create_session(f"agent_{task_id}"):
                    # Update state
                    await state_manager.update_story_status(
                        story_path=f"concurrent_story_{task_id}.md",
                        status=f"processing_{task_id}",
                        phase="concurrent_phase"
                    )

                    # Simulate work
                    await asyncio.sleep(0.01)

                    # Update state again
                    await state_manager.update_story_status(
                        story_path=f"concurrent_story_{task_id}.md",
                        status=f"completed_{task_id}",
                        phase="concurrent_phase"
                    )

                    return task_id

            # Create 50 concurrent tasks
            tasks = [integration_task(i) for i in range(50)]
            results = await asyncio.gather(*tasks)

            # Verify
            assert len(results) == 50
            assert all(isinstance(r, int) for r in results)

            # Verify no resource leaks
            assert session_manager.get_session_count() == 0
            health = state_manager.get_health_status()
            assert health["lock_locked"] is False

            # Cleanup
            db_file = Path("concurrent_integration.db")
            if db_file.exists():
                db_file.unlink()

        asyncio.run(test_concurrent_integration_scenarios())

    def test_resource_contention_integration(self):
        """Test resource contention in integration scenarios"""
        async def test_contention():
            session_manager = SDKSessionManager()
            state_manager = StateManager("contention_integration.db")

            # Shared state updates
            async def state_update_task(task_id: int):
                async with session_manager.create_session(f"agent_{task_id}"):
                    # Compete for same state resource
                    async with state_manager.managed_operation():
                        current_status = "task_" + str(task_id)
                        await state_manager.update_story_status(
                            story_path="shared_story.md",
                            status=current_status,
                            phase="contention_phase"
                        )
                        await asyncio.sleep(0.01)  # Brief hold

                    return task_id

            # Create 30 competing tasks
            tasks = [state_update_task(i) for i in range(30)]
            results = await asyncio.gather(*tasks)

            # Verify all tasks completed
            assert len(results) == 30

            # Verify no resource leaks
            assert session_manager.get_session_count() == 0
            health = state_manager.get_health_status()
            assert health["lock_locked"] is False

            # Cleanup
            db_file = Path("contention_integration.db")
            if db_file.exists():
                db_file.unlink()

        asyncio.run(test_resource_contention_integration())

    def test_safe_async_generator_integration(self):
        """Test SafeAsyncGenerator with integration scenarios"""
        async def test_gen_integration():
            session_manager = SDKSessionManager()

            async def generator_task(task_id: int):
                async def data_generator():
                    for i in range(10):
                        await asyncio.sleep(0.001)
                        yield {"task_id": task_id, "data": i}

                safe_gen = SafeAsyncGenerator(data_generator())

                results = []
                async for item in safe_gen:
                    results.append(item)
                    if len(results) >= 5:  # Take only first 5
                        break

                return {
                    "task_id": task_id,
                    "results_count": len(results),
                    "generator_closed": safe_gen._closed
                }

            # Create 20 tasks using generators
            tasks = [generator_task(i) for i in range(20)]
            results = await asyncio.gather(*tasks)

            # Verify
            assert len(results) == 20
            assert all(r["results_count"] == 5 for r in results)
            assert all(r["generator_closed"] is True for r in results)

        asyncio.run(test_safe_async_generator_integration())

    def test_complex_workflow_integration(self):
        """Test complex workflow integration"""
        async def test_complex():
            session_manager = SDKSessionManager()
            state_manager = StateManager("complex_integration.db")

            async def complex_workflow(workflow_id: int):
                workflow_results = []

                # Phase 1: Create session and initialize state
                async with session_manager.create_session(f"workflow_agent_{workflow_id}"):
                    await state_manager.update_story_status(
                        story_path=f"complex_story_{workflow_id}.md",
                        status="initialized",
                        phase="phase_1"
                    )
                    workflow_results.append("initialized")

                    # Phase 2: Concurrent subtasks
                    sub_results = []

                    async def sub_task(sub_id: int):
                        async with session_manager.create_session(f"sub_agent_{workflow_id}_{sub_id}"):
                            await asyncio.sleep(0.001)
                            return f"subtask_{sub_id}"

                    sub_tasks = [sub_task(i) for i in range(5)]
                    sub_results = await asyncio.gather(*sub_tasks)
                    workflow_results.extend(sub_results)

                    # Phase 3: Update state
                    await state_manager.update_story_status(
                        story_path=f"complex_story_{workflow_id}.md",
                        status="processing",
                        phase="phase_3"
                    )
                    workflow_results.append("processing")

                    # Phase 4: Complete
                    await state_manager.update_story_status(
                        story_path=f"complex_story_{workflow_id}.md",
                        status="completed",
                        phase="phase_4"
                    )
                    workflow_results.append("completed")

                return {
                    "workflow_id": workflow_id,
                    "phases": workflow_results,
                    "sub_results": sub_results
                }

            # Execute 5 complex workflows
            tasks = [complex_workflow(i) for i in range(5)]
            results = await asyncio.gather(*tasks)

            # Verify
            assert len(results) == 5
            for r in results:
                assert len(r["phases"]) == 3  # initialized, processing, completed
                assert len(r["sub_results"]) == 5  # 5 subtasks
                assert r["sub_results"] == [f"subtask_{i}" for i in range(5)]

            # Verify no resource leaks
            assert session_manager.get_session_count() == 0
            health = state_manager.get_health_status()
            assert health["lock_locked"] is False

            # Cleanup
            db_file = Path("complex_integration.db")
            if db_file.exists():
                db_file.unlink()

        asyncio.run(test_complex_workflow_integration())


if __name__ == "__main__":
    # Run tests
    test = TestIntegrationScenarios()

    print("Running integration tests...")
    print()

    try:
        test.test_sdk_session_with_state_manager()
        print("PASS: SDK session with state manager integration test")
        print()

        test.test_qa_agent_with_session_manager()
        print("PASS: QA agent with session manager integration test")
        print()

        test.test_end_to_end_workflow()
        print("PASS: End-to-end workflow test")
        print()

        test.test_cancellation_with_integration()
        print("PASS: Cancellation in integration scenarios test")
        print()

        test.test_timeout_with_state_management()
        print("PASS: Timeout with state management integration test")
        print()

        test.test_error_recovery_integration()
        print("PASS: Error recovery in integration scenarios test")
        print()

        test.test_concurrent_integration_scenarios()
        print("PASS: Concurrent integration scenarios test")
        print()

        test.test_resource_contention_integration()
        print("PASS: Resource contention in integration scenarios test")
        print()

        test.test_safe_async_generator_integration()
        print("PASS: SafeAsyncGenerator integration test")
        print()

        test.test_complex_workflow_integration()
        print("PASS: Complex workflow integration test")
        print()

        print("SUCCESS: All integration tests passed!")

    except Exception as e:
        print(f"FAIL: Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
