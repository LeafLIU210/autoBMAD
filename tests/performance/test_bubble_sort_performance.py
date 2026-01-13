"""Performance tests for bubble sort algorithm."""

import time
import pytest

from src.bubblesort import bubble_sort


class TestBubbleSortPerformance:
    """Performance benchmarks for bubble sort."""

    def test_small_array_performance(self):
        """Test performance with small array (10 elements)."""
        data = list(range(10, 0, -1))  # Reverse sorted

        start_time = time.perf_counter()
        result = bubble_sort(data)
        end_time = time.perf_counter()

        assert result == list(range(1, 11))
        # Should complete in well under 1 second for small array
        assert (end_time - start_time) < 0.1

    def test_medium_array_performance(self):
        """Test performance with medium array (100 elements)."""
        data = list(range(100, 0, -1))  # Reverse sorted

        start_time = time.perf_counter()
        result = bubble_sort(data)
        end_time = time.perf_counter()

        assert result == list(range(1, 101))
        # Should complete in reasonable time
        assert (end_time - start_time) < 1.0

    def test_large_array_performance(self):
        """Test performance with large array (1000 elements)."""
        data = list(range(1000, 0, -1))  # Reverse sorted

        start_time = time.perf_counter()
        result = bubble_sort(data)
        end_time = time.perf_counter()

        assert result == list(range(1, 1001))
        # Should complete within reasonable time (<5 seconds)
        assert (end_time - start_time) < 5.0

    def test_already_sorted_optimization(self):
        """Test that already-sorted array is optimized."""
        data = list(range(1, 1001))  # Already sorted

        start_time = time.perf_counter()
        result = bubble_sort(data)
        end_time = time.perf_counter()

        assert result == data
        # Should be much faster than reverse sorted due to optimization
        elapsed = end_time - start_time

        # Now test reverse sorted for comparison
        reverse_data = list(range(1000, 0, -1))
        start_time2 = time.perf_counter()
        bubble_sort(reverse_data)
        end_time2 = time.perf_counter()
        reverse_elapsed = end_time2 - start_time2

        # Already sorted should be significantly faster
        assert elapsed < reverse_elapsed
        # Should be very fast (optimization kicks in immediately)
        assert elapsed < 0.01

    def test_partially_sorted_performance(self):
        """Test performance with partially sorted array."""
        # 90% sorted, 10% random
        data = list(range(1, 901)) + list(range(1000, 900, -1))

        start_time = time.perf_counter()
        result = bubble_sort(data)
        end_time = time.perf_counter()

        assert result == list(range(1, 1001))
        elapsed = end_time - start_time
        # Should be faster than reverse sorted
        assert elapsed < 5.0

    def test_duplicate_values_performance(self):
        """Test performance with many duplicate values."""
        # Many duplicates can reduce the number of swaps needed
        data = [5] * 200 + [3] * 200 + [1] * 200

        start_time = time.perf_counter()
        result = bubble_sort(data)
        end_time = time.perf_counter()

        assert result == [1] * 200 + [3] * 200 + [5] * 200
        # Should complete reasonably fast
        assert (end_time - start_time) < 5.0

    def test_negative_numbers_performance(self):
        """Test performance with negative numbers."""
        data = list(range(-500, 500))  # -500 to 499

        start_time = time.perf_counter()
        result = bubble_sort(data)
        end_time = time.perf_counter()

        assert result == list(range(-500, 500))
        # Should complete in reasonable time
        assert (end_time - start_time) < 5.0

    def test_float_numbers_performance(self):
        """Test performance with float numbers."""
        data = [i / 10.0 for i in range(1000, 0, -1)]

        start_time = time.perf_counter()
        result = bubble_sort(data)
        end_time = time.perf_counter()

        assert result == [i / 10.0 for i in range(1, 1001)]
        # Should complete in reasonable time
        assert (end_time - start_time) < 5.0

    def test_mixed_int_float_performance(self):
        """Test performance with mixed int and float types."""
        data = [i + (0.5 if i % 2 else 0.0) for i in range(1000, 0, -1)]

        start_time = time.perf_counter()
        result = bubble_sort(data)
        end_time = time.perf_counter()

        # Verify sorted correctly
        for i in range(len(result) - 1):
            assert result[i] <= result[i + 1]

        # Should complete in reasonable time
        assert (end_time - start_time) < 5.0

    def test_consistent_performance(self):
        """Test that performance is consistent across multiple runs."""
        data = list(range(500, 0, -1))

        times = []
        for _ in range(5):
            start_time = time.perf_counter()
            bubble_sort(data.copy())
            end_time = time.perf_counter()
            times.append(end_time - start_time)

        # All runs should complete within reasonable time
        for t in times:
            assert t < 1.0

        # Times should be somewhat consistent (within 2x of each other)
        max_time = max(times)
        min_time = min(times)
        assert max_time / min_time < 2.0

    @pytest.mark.parametrize("size", [10, 50, 100, 500, 1000])
    def test_various_sizes_performance(self, size):
        """Test performance across various array sizes."""
        data = list(range(size, 0, -1))

        start_time = time.perf_counter()
        result = bubble_sort(data)
        end_time = time.perf_counter()

        assert result == list(range(1, size + 1))

        elapsed = end_time - start_time
        # Performance should scale reasonably (O(n^2) is expected for bubble sort)
        # For bubble sort, time should be roughly proportional to n^2
        # We'll just verify it's not unreasonably slow
        assert elapsed < size * size / 100000  # Reasonable upper bound

    def test_max_size_performance(self):
        """Test performance at maximum supported size (10000 elements)."""
        # This is the maximum size allowed by validate_data
        data = list(range(10000, 0, -1))

        start_time = time.perf_counter()
        result = bubble_sort(data)
        end_time = time.perf_counter()

        assert result == list(range(1, 10001))

        elapsed = end_time - start_time
        # Should complete but may take a few seconds (bubble sort is O(n^2))
        # 10000^2 operations / 1000000 ops per second ≈ 1 second
        assert elapsed < 10.0  # Reasonable upper bound

    def test_early_exit_optimization(self):
        """Test that early exit optimization works correctly."""
        # Create array that becomes sorted after a few passes
        data = [1, 2, 3, 5, 4, 6, 7, 8, 9, 10]  # Only needs a few swaps

        start_time = time.perf_counter()
        result = bubble_sort(data)
        end_time = time.perf_counter()

        assert result == list(range(1, 11))
        # Should be very fast due to early exit
        assert (end_time - start_time) < 0.01


class TestBubbleSortCorrectnessUnderLoad:
    """Test correctness of bubble sort under various conditions."""

    def test_random_order_correctness(self):
        """Test that bubble sort correctly handles random order."""
        import random

        # Test multiple random arrays
        for _ in range(10):
            size = random.randint(1, 100)
            data = [random.randint(-1000, 1000) for _ in range(size)]

            result = bubble_sort(data)

            # Verify it's sorted
            for i in range(len(result) - 1):
                assert result[i] <= result[i + 1], f"Array not sorted: {result}"

            # Verify all elements are preserved
            assert sorted(data) == result

    def test_extreme_values_correctness(self):
        """Test with extreme numeric values."""
        # Mix of very large and very small numbers
        data = [1e10, -1e10, 1e-10, -1e-10, 0, 1, -1]

        result = bubble_sort(data)

        # Verify sorted
        for i in range(len(result) - 1):
            assert result[i] <= result[i + 1]

    def test_single_element_performance(self):
        """Test performance with single element."""
        data = [42]

        start_time = time.perf_counter()
        result = bubble_sort(data)
        end_time = time.perf_counter()

        assert result == [42]
        # Should be instantaneous
        assert (end_time - start_time) < 0.001

    def test_two_elements_performance(self):
        """Test performance with two elements."""
        data = [2, 1]

        start_time = time.perf_counter()
        result = bubble_sort(data)
        end_time = time.perf_counter()

        assert result == [1, 2]
        # Should be very fast
        assert (end_time - start_time) < 0.001

    def test_three_elements_performance(self):
        """Test performance with three elements."""
        data = [3, 1, 2]

        start_time = time.perf_counter()
        result = bubble_sort(data)
        end_time = time.perf_counter()

        assert result == [1, 2, 3]
        # Should be very fast
        assert (end_time - start_time) < 0.001


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
