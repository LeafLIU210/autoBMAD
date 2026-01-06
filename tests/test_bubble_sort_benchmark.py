"""Benchmark tests for bubble sort module.

This test file contains benchmark tests to track performance characteristics
of the bubble sort implementation over time and ensure no performance regressions.
"""

import random
import time


class TestBubbleSortBenchmark:
    """Benchmark test cases for bubble sort algorithm."""

    def test_benchmark_small_list(self):
        """Benchmark sorting a small list (10 elements)."""
        from src.bubble_sort import bubble_sort

        random.seed(42)
        test_data = [random.randint(1, 100) for _ in range(10)]

        start = time.perf_counter()
        result = bubble_sort(test_data.copy())
        end = time.perf_counter()

        elapsed = end - start

        # Small list should sort very quickly (under 1ms)
        assert (
            elapsed < 0.001
        ), f"Sorting small list took {elapsed:.6f} seconds"
        assert result == sorted(test_data)

    def test_benchmark_medium_list(self):
        """Benchmark sorting a medium list (100 elements)."""
        from src.bubble_sort import bubble_sort

        random.seed(42)
        test_data = [random.randint(1, 1000) for _ in range(100)]

        start = time.perf_counter()
        result = bubble_sort(test_data.copy())
        end = time.perf_counter()

        elapsed = end - start

        # Medium list should still be reasonable (under 10ms)
        assert (
            elapsed < 0.01
        ), f"Sorting medium list took {elapsed:.6f} seconds"
        assert result == sorted(test_data)

    def test_benchmark_large_list(self):
        """Benchmark sorting a large list (1000 elements)."""
        from src.bubble_sort import bubble_sort

        random.seed(42)
        test_data = [random.randint(1, 10000) for _ in range(1000)]

        start = time.perf_counter()
        result = bubble_sort(test_data.copy())
        end = time.perf_counter()

        elapsed = end - start

        # Large list might take longer but should still complete (under 1 second)
        assert elapsed < 1.0, f"Sorting large list took {elapsed:.6f} seconds"
        assert result == sorted(test_data)

    def test_benchmark_worst_case_reverse_sorted(self):
        """Benchmark worst-case scenario: reverse sorted list."""
        from src.bubble_sort import bubble_sort

        test_data = list(range(1000, 0, -1))

        start = time.perf_counter()
        result = bubble_sort(test_data.copy())
        end = time.perf_counter()

        elapsed = end - start

        # Worst case should still complete (under 2 seconds)
        assert elapsed < 2.0, f"Worst case sorting took {elapsed:.6f} seconds"
        assert result == list(range(1, 1001))

    def test_benchmark_best_case_already_sorted(self):
        """Benchmark best-case scenario: already sorted list."""
        from src.bubble_sort import bubble_sort

        test_data = list(range(1, 1001))

        start = time.perf_counter()
        result = bubble_sort(test_data.copy())
        end = time.perf_counter()

        elapsed = end - start

        # Best case should be very fast due to optimization (under 1ms)
        assert elapsed < 0.001, f"Best case sorting took {elapsed:.6f} seconds"
        assert result == list(range(1, 1001))

    def test_benchmark_comparison_different_sizes(self):
        """Compare performance across different list sizes."""
        from src.bubble_sort import bubble_sort

        sizes = [10, 50, 100, 200, 500, 1000]
        times = []

        for size in sizes:
            random.seed(42)
            test_data = [random.randint(1, size * 10) for _ in range(size)]

            start = time.perf_counter()
            result = bubble_sort(test_data.copy())
            end = time.perf_counter()

            elapsed = end - start
            times.append(elapsed)

            assert result == sorted(test_data)

        # Verify performance scales appropriately
        # Time should roughly increase quadratically with size
        for i in range(1, len(sizes)):
            size_ratio = sizes[i] / sizes[i - 1]
            time_ratio = times[i] / times[i - 1] if times[i - 1] > 0 else 0

            # For bubble sort, time should increase roughly with square of size
            # So if size doubles, time should roughly quadruple
            assert time_ratio > size_ratio, (
                f"Performance anomaly: size {sizes[i-1]}->{sizes[i]} "
                f"(ratio {size_ratio:.2f}), "
                f"time ratio {time_ratio:.2f}"
            )

    def test_benchmark_stability_with_timing(self):
        """Verify stability while benchmarking."""
        from src.bubble_sort import bubble_sort

        # Create list with duplicates to test stability
        test_data = [(i % 100, i) for i in range(1000)]

        start = time.perf_counter()
        result = bubble_sort(test_data.copy())
        end = time.perf_counter()

        elapsed = end - start

        # Should complete in reasonable time
        assert elapsed < 1.0, f"Stability test took {elapsed:.6f} seconds"

        # Verify stability
        for i in range(len(result) - 1):
            assert result[i][0] <= result[i + 1][0]

        # Verify that elements with equal keys maintain relative order
        for value in range(100):
            indices = [i for i, x in enumerate(test_data) if x[0] == value]
            result_indices = [i for i, x in enumerate(result) if x[0] == value]

            original_order = [test_data[i][1] for i in indices]
            result_order = [result[i][1] for i in result_indices]

            assert (
                original_order == result_order
            ), f"Stability broken for value {value}"

    def test_benchmark_memory_efficiency(self):
        """Benchmark to verify memory efficiency (in-place sorting)."""
        import sys

        from src.bubble_sort import bubble_sort

        random.seed(42)
        test_data = [random.randint(1, 1000) for _ in range(1000)]
        test_data_copy = test_data.copy()

        # Get initial memory (approximate)
        initial_size = sys.getsizeof(test_data)

        result = bubble_sort(test_data)

        # Should create a new list (pure function)
        assert id(result) != id(test_data)

        # Memory usage should be proportional to input size
        # (We're creating a new list)
        final_size = sys.getsizeof(result)
        # Allow some variation due to list growth
        assert final_size >= initial_size * 0.8

        # Input should not be modified
        assert test_data == test_data_copy

    def test_benchmark_multiple_runs_consistency(self):
        """Test that multiple runs produce consistent results."""
        from src.bubble_sort import bubble_sort

        random.seed(42)
        test_data = [random.randint(1, 100) for _ in range(100)]

        results = []
        for _ in range(10):
            result = bubble_sort(test_data.copy())
            results.append(result)

        # All runs should produce the same result
        expected = sorted(test_data)
        for result in results:
            assert result == expected

    def test_benchmark_pure_function_timing(self):
        """Benchmark pure function vs creating new list."""
        from src.bubble_sort import bubble_sort

        test_data = [random.randint(1, 1000) for _ in range(500)]
        test_data_copy = test_data.copy()

        # Time the pure function
        start = time.perf_counter()
        result = bubble_sort(test_data)
        end = time.perf_counter()

        pure_time = end - start

        # Should be fast (creating a copy and sorting)
        assert (
            pure_time < 0.1
        ), f"Pure function took {pure_time:.6f} seconds"
        assert id(result) != id(test_data)  # Should be different object
        assert test_data == test_data_copy  # Input should not be modified

    def test_benchmark_comparison_with_sorted(self):
        """Compare bubble sort timing with Python's built-in sorted()."""
        from src.bubble_sort import bubble_sort

        random.seed(42)
        test_data = [random.randint(1, 1000) for _ in range(500)]

        # Time bubble sort
        start = time.perf_counter()
        bubble_result = bubble_sort(test_data.copy())
        end = time.perf_counter()
        bubble_time = end - start

        # Time built-in sorted
        start = time.perf_counter()
        sorted_result = sorted(test_data.copy())
        end = time.perf_counter()
        sorted_time = end - start

        # Both should produce same result
        assert bubble_result == sorted_result

        # Bubble sort will be slower (it's O(n²) vs O(n log n))
        # But it should still complete in reasonable time
        assert bubble_time < 1.0, f"Bubble sort took {bubble_time:.6f} seconds"
        assert sorted_time < 0.01, f"sorted() took {sorted_time:.6f} seconds"

    def test_benchmark_optimization_effectiveness(self):
        """Benchmark the effectiveness of the swapped flag optimization."""
        from src.bubble_sort import bubble_sort

        # Best case: already sorted
        best_case = list(range(1, 1001))
        start = time.perf_counter()
        bubble_sort(best_case)
        end = time.perf_counter()
        best_case_time = end - start

        # Worst case: reverse sorted
        worst_case = list(range(1000, 0, -1))
        start = time.perf_counter()
        bubble_sort(worst_case)
        end = time.perf_counter()
        worst_case_time = end - start

        # Best case should be significantly faster due to optimization
        assert best_case_time < worst_case_time, (
            f"Optimization not working: best case {best_case_time:.6f}s, "
            f"worst case {worst_case_time:.6f}s"
        )

        # Best case should be at least 10x faster
        speedup = worst_case_time / best_case_time if best_case_time > 0 else 0
        assert (
            speedup > 10
        ), f"Optimization not effective enough: {speedup:.2f}x speedup"

    def test_benchmark_various_data_patterns(self):
        """Benchmark sorting various data patterns."""
        from src.bubble_sort import bubble_sort

        patterns = {
            "random": lambda n: [random.randint(1, n) for _ in range(n)],
            "already_sorted": lambda n: list(range(n)),
            "reverse_sorted": lambda n: list(range(n, 0, -1)),
            "few_unique": lambda n: [i % 10 for i in range(n)],
        }

        n = 500
        times = {}

        for pattern_name, pattern_func in patterns.items():
            test_data = pattern_func(n)

            start = time.perf_counter()
            result = bubble_sort(test_data.copy())
            end = time.perf_counter()

            times[pattern_name] = end - start
            assert result == sorted(test_data)

        # Verify that patterns with optimization potential are faster
        # (already_sorted should be fastest due to early termination)
        assert (
            times["already_sorted"] < times["random"]
        ), "Optimization not working: already_sorted should be fastest"
