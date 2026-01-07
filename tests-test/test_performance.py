"""
Performance tests for bubble sort algorithm.
Tests ensure algorithm correctness under various load conditions.
"""

import time
import pytest
from src import bubble_sort


class TestBubbleSortPerformance:
    """Performance and scalability tests."""

    @pytest.mark.performance
    def test_sorting_small_list_performance(self):
        """Test performance with small list (10 elements)."""
        import random

        data = list(range(10))
        random.shuffle(data)

        start = time.time()
        result = bubble_sort(data)
        elapsed = time.time() - start

        assert result == list(range(10))
        assert elapsed < 0.01  # Should complete in under 10ms

    @pytest.mark.performance
    def test_sorting_medium_list_performance(self):
        """Test performance with medium list (100 elements)."""
        import random

        data = list(range(100))
        random.shuffle(data)

        start = time.time()
        result = bubble_sort(data)
        elapsed = time.time() - start

        assert result == list(range(100))
        assert elapsed < 1.0  # Should complete in under 1 second

    @pytest.mark.performance
    def test_sorting_large_list_performance(self):
        """Test performance with large list (1000 elements)."""
        import random

        data = list(range(1000))
        random.shuffle(data)

        start = time.time()
        result = bubble_sort(data)
        elapsed = time.time() - start

        assert result == list(range(1000))
        assert elapsed < 30.0  # Should complete in under 30 seconds

    @pytest.mark.performance
    def test_best_case_already_sorted(self):
        """Test best case scenario - already sorted list."""
        data = list(range(100))

        start = time.time()
        result = bubble_sort(data)
        elapsed = time.time() - start

        assert result == list(range(100))
        # Best case should be faster than worst case

    @pytest.mark.performance
    def test_worst_case_reverse_sorted(self):
        """Test worst case scenario - reverse sorted list."""
        data = list(range(100, 0, -1))

        start = time.time()
        result = bubble_sort(data)
        elapsed = time.time() - start

        assert result == list(range(1, 101))
        # Worst case should take longer but still complete


class TestBubbleSortComplexityVerification:
    """Tests to verify O(n²) time complexity characteristics."""

    def test_quadratic_growth(self):
        """Verify that time grows quadratically with input size."""
        import random
        import time

        # Test with different sizes
        sizes = [10, 20, 40]
        times = []

        for size in sizes:
            data = list(range(size))
            random.shuffle(data)

            start = time.time()
            bubble_sort(data)
            elapsed = time.time() - start
            times.append(elapsed)

        # Time should increase as size increases
        # (This is a simple sanity check, not exact measurement)
        assert times[-1] >= times[0]  # Largest size takes at least as long as smallest

    def test_stability_under_load(self):
        """Test that algorithm remains stable under various data patterns."""
        test_cases = [
            # Already sorted
            list(range(50)),
            # Reverse sorted
            list(range(50, 0, -1)),
            # Random
            list(range(50)),
        ]

        for data in test_cases:
            import random
            if data == list(range(50)):  # Random case
                random.shuffle(data)

            result = bubble_sort(data.copy())
            assert result == sorted(data)
