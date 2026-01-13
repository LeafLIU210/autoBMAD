"""
Performance Tests

Test performance metrics of the system after fixes.
"""

import asyncio
import time
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fixed_modules.sdk_session_manager_fixed import SDKSessionManager
from fixed_modules.state_manager_fixed import StateManager
from fixed_modules.sdk_wrapper_fixed import SafeAsyncGenerator


class TestPerformanceBenchmarks:
    """Performance Benchmark Tests"""

    def test_session_creation_performance(self):
        """Test session creation performance"""
        async def test_creation():
            manager = SDKSessionManager()

            # Test 1000 session creations
            start_time = time.time()
            creation_times = []

            for _ in range(1000):
                task_start = time.time()
                async with manager.create_session("test_agent"):
                    pass
                task_time = time.time() - task_start
                creation_times.append(task_time)

            total_time = time.time() - start_time
            avg_time = sum(creation_times) / len(creation_times)
            min_time = min(creation_times)
            max_time = max(creation_times)

            print(f"\nSession Creation Performance:")
            print(f"  Total time: {total_time:.3f}s")
            print(f"  Average time: {avg_time*1000:.3f}ms")
            print(f"  Min time: {min_time*1000:.3f}ms")
            print(f"  Max time: {max_time*1000:.3f}ms")
            print(f"  Creations per second: {1000/total_time:.1f}")

            # Performance assertions
            assert avg_time < 0.01  # Average less than 10ms
            assert max_time < 0.1   # Max less than 100ms
            assert total_time < 10  # Total less than 10 seconds

        asyncio.run(test_creation())

    def test_concurrent_session_performance(self):
        """Test concurrent session performance"""
        async def test_concurrent():
            manager = SDKSessionManager()

            # Test 100 concurrent sessions
            async def session_task(task_id: int):
                async with manager.create_session(f"agent_{task_id}"):
                    await asyncio.sleep(0.01)
                return task_id

            start_time = time.time()
            tasks = [session_task(i) for i in range(100)]
            results = await asyncio.gather(*tasks)
            total_time = time.time() - start_time

            print(f"\nConcurrent Session Performance:")
            print(f"  Concurrency: 100")
            print(f"  Total time: {total_time:.3f}s")
            print(f"  Average per session: {total_time*10:.3f}ms")
            print(f"  Sessions per second: {100/total_time:.1f}")

            # Verify all tasks completed
            assert len(results) == 100
            assert all(isinstance(r, int) for r in results)

            # Performance assertions
            assert total_time < 2  # Less than 2 seconds

        asyncio.run(test_concurrent())

    def test_state_manager_performance(self):
        """Test state manager performance"""
        async def test_state():
            state_manager = StateManager("perf_state.db")

            # Test 1000 state updates
            start_time = time.time()

            for i in range(1000):
                await state_manager.update_story_status(
                    story_path=f"perf_story_{i}.md",
                    status="test_status",
                    phase="perf_phase"
                )

            total_time = time.time() - start_time
            avg_time = total_time / 1000

            print(f"\nState Manager Performance:")
            print(f"  Update count: 1000")
            print(f"  Total time: {total_time:.3f}s")
            print(f"  Average time: {avg_time*1000:.3f}ms")
            print(f"  Updates per second: {1000/total_time:.1f}")

            # Cleanup
            db_file = Path("perf_state.db")
            if db_file.exists():
                db_file.unlink()

            # Performance assertions
            assert avg_time < 0.005  # Average less than 5ms
            assert total_time < 5    # Total less than 5 seconds

        asyncio.run(test_state_performance())

    def test_safe_async_generator_performance(self):
        """Test SafeAsyncGenerator performance"""
        async def test_gen():
            # Test large data generator performance
            async def large_gen():
                for i in range(10000):
                    yield i

            safe_gen = SafeAsyncGenerator(large_gen())

            start_time = time.time()
            count = 0
            async for value in safe_gen:
                count += 1
                if count >= 10000:
                    break

            total_time = time.time() - start_time

            print(f"\nSafeAsyncGenerator Performance:")
            print(f"  Items processed: 10000")
            print(f"  Total time: {total_time:.3f}s")
            print(f"  Average per item: {total_time/10000*1000000:.2f}μs")
            print(f"  Items per second: {10000/total_time:.1f}")

            # Performance assertions
            assert count == 10000
            assert total_time < 1  # Less than 1 second

        asyncio.run(test_safe_async_generator_performance())

    def test_memory_usage_performance(self):
        """Test memory usage performance"""
        async def test_memory():
            import gc

            # Force garbage collection
            gc.collect()

            # Create many objects
            async def memory_task(task_id: int):
                async with SDKSessionManager().create_session(f"agent_{task_id}"):
                    # Create some data
                    data = [{"id": i, "value": f"data_{i}"} for i in range(100)]
                    await asyncio.sleep(0.001)
                    return len(data)

            # Execute 100 tasks
            tasks = [memory_task(i) for i in range(100)]
            results = await asyncio.gather(*tasks)

            # Force garbage collection again
            gc.collect()

            print(f"\nMemory Usage Performance:")
            print(f"  Task count: 100")
            print(f"  Data per task: 100")
            print(f"  Total data: 10000")

            # Verify
            assert len(results) == 100
            assert all(r == 100 for r in results)

        asyncio.run(test_memory_usage_performance())

    def test_throughput_benchmark(self):
        """Test throughput benchmark"""
        async def test_throughput():
            manager = SDKSessionManager()

            # Test high throughput scenario
            async def throughput_task(task_id: int):
                async def quick_func():
                    await asyncio.sleep(0.001)
                    return task_id

                result = await manager.execute_isolated(
                    agent_name=f"throughput_{task_id}",
                    sdk_func=quick_func,
                    timeout=5.0
                )
                return result.success

            # Execute 1000 quick tasks
            start_time = time.time()
            tasks = [throughput_task(i) for i in range(1000)]
            results = await asyncio.gather(*tasks)
            total_time = time.time() - start_time

            # Count successes
            success_count = sum(1 for r in results if r)

            print(f"\nThroughput Benchmark:")
            print(f"  Task count: 1000")
            print(f"  Success count: {success_count}")
            print(f"  Success rate: {success_count/1000*100:.1f}%")
            print(f"  Total time: {total_time:.3f}s")
            print(f"  Throughput: {1000/total_time:.1f} ops/s")

            # Performance assertions
            assert success_count >= 950  # At least 95% success rate
            assert total_time < 5  # Less than 5 seconds
            assert 1000/total_time > 200  # At least 200 ops per second

        asyncio.run(test_throughput_benchmark())

    def test_latency_performance(self):
        """Test latency performance"""
        async def test_latency():
            manager = SDKSessionManager()

            # Test latency of operations with different sizes
            sizes = [1, 10, 100, 1000]
            latency_results = {}

            for size in sizes:
                latencies = []

                for _ in range(50):
                    async def size_func():
                        data = list(range(size))
                        await asyncio.sleep(0.0001)
                        return len(data)

                    start = time.time()
                    result = await manager.execute_isolated(
                        agent_name=f"latency_{size}",
                        sdk_func=size_func,
                        timeout=5.0
                    )
                    latency = (time.time() - start) * 1000  # Convert to ms
                    latencies.append(latency)

                latency_results[size] = {
                    "min": min(latencies),
                    "max": max(latencies),
                    "avg": sum(latencies) / len(latencies),
                    "p95": sorted(latencies)[int(len(latencies) * 0.95)]
                }

            print(f"\nLatency Performance (ms):")
            for size, stats in latency_results.items():
                print(f"  Size {size:4d}: avg={stats['avg']:6.2f}, p95={stats['p95']:6.2f}, min={stats['min']:6.2f}, max={stats['max']:6.2f}")

            # Performance assertions
            for size, stats in latency_results.items():
                assert stats['avg'] < 100  # Average latency less than 100ms
                assert stats['p95'] < 200  # 95% latency less than 200ms

        asyncio.run(test_latency_performance())

    def test_scalability_benchmark(self):
        """Test scalability benchmark"""
        async def test_scalability():
            manager = SDKSessionManager()

            # Test performance at different concurrency levels
            concurrency_levels = [10, 50, 100, 200]
            scalability_results = {}

            for level in concurrency_levels:
                async def scalable_task(task_id: int):
                    async with manager.create_session(f"agent_{task_id}"):
                        await asyncio.sleep(0.01)
                    return task_id

                start = time.time()
                tasks = [scalable_task(i) for i in range(level)]
                results = await asyncio.gather(*tasks)
                duration = time.time() - start

                scalability_results[level] = {
                    "duration": duration,
                    "throughput": level / duration,
                    "success_count": len(results)
                }

            print(f"\nScalability Benchmark:")
            for level, stats in scalability_results.items():
                print(f"  Concurrency {level:3d}: {stats['duration']:6.3f}s, {stats['throughput']:6.1f} ops/s")

            # Verify scalability
            # As concurrency increases, throughput should increase or stay stable
            throughputs = [stats['throughput'] for stats in scalability_results.values()]
            assert throughputs[0] > 0  # First throughput should be > 0
            assert max(throughputs) > min(throughputs) * 0.5  # Max throughput should not be too small

        asyncio.run(test_scalability_benchmark())

    def test_resource_efficiency(self):
        """Test resource efficiency"""
        async def test_efficiency():
            session_manager = SDKSessionManager()
            state_manager = StateManager("efficiency.db")

            # Test resource usage efficiency
            async def efficiency_task(task_id: int):
                async with session_manager.create_session(f"efficiency_{task_id}"):
                    await state_manager.update_story_status(
                        story_path=f"efficiency_story_{task_id}.md",
                        status="efficiency_test",
                        phase="efficiency_phase"
                    )
                    await asyncio.sleep(0.001)

            # Execute 500 tasks
            start = time.time()
            tasks = [efficiency_task(i) for i in range(500)]
            results = await asyncio.gather(*tasks)
            total_time = time.time() - start

            # Verify resource cleanup
            session_count = session_manager.get_session_count()
            health = state_manager.get_health_status()

            print(f"\nResource Efficiency:")
            print(f"  Task count: 500")
            print(f"  Total time: {total_time:.3f}s")
            print(f"  Remaining sessions: {session_count}")
            print(f"  Lock status: {'locked' if health['lock_locked'] else 'unlocked'}")

            # Efficiency assertions
            assert session_count == 0  # No remaining sessions
            assert not health['lock_locked']  # Lock released
            assert total_time < 5  # Reasonable total time

            # Cleanup
            db_file = Path("efficiency.db")
            if db_file.exists():
                db_file.unlink()

        asyncio.run(test_resource_efficiency())

    def test_stress_performance(self):
        """Test stress performance"""
        async def test_stress():
            manager = SDKSessionManager()

            # Stress test: create many concurrent tasks
            async def stress_task(task_id: int):
                try:
                    async with manager.create_session(f"stress_agent_{task_id}"):
                        await asyncio.sleep(0.005)  # Brief work
                    return True
                except Exception:
                    return False

            # Execute 500 high-concurrency tasks
            start = time.time()
            tasks = [stress_task(i) for i in range(500)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start

            success_count = sum(1 for r in results if r is True)

            print(f"\nStress Performance:")
            print(f"  Task count: 500")
            print(f"  Success count: {success_count}")
            print(f"  Failure count: {500 - success_count}")
            print(f"  Success rate: {success_count/500*100:.1f}%")
            print(f"  Total time: {total_time:.3f}s")
            print(f"  Throughput: {500/total_time:.1f} ops/s")

            # Stress test assertions
            assert success_count >= 450  # At least 90% success rate
            assert total_time < 10  # Total time less than 10 seconds

        asyncio.run(test_stress_performance())


if __name__ == "__main__":
    # Run performance tests
    test = TestPerformanceBenchmarks()

    print("=" * 60)
    print("Performance Benchmark Tests")
    print("=" * 60)

    try:
        test.test_session_creation_performance()
        print()

        test.test_concurrent_session_performance()
        print()

        test.test_state_manager_performance()
        print()

        test.test_safe_async_generator_performance()
        print()

        test.test_memory_usage_performance()
        print()

        test.test_throughput_benchmark()
        print()

        test.test_latency_performance()
        print()

        test.test_scalability_benchmark()
        print()

        test.test_resource_efficiency()
        print()

        test.test_stress_performance()
        print()

        print("=" * 60)
        print("SUCCESS: All performance tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"\nFAIL: Performance test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
