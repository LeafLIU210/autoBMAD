"""Stress testing for bubble sort module.

This test file contains stress tests to verify that the bubble sort implementation
can handle very large datasets and extreme conditions.
"""

import random
import time
from collections import Counter


class TestBubbleSortStress:
    """Stress test cases for bubble sort algorithm."""

    def test_stress_very_large_dataset(self):
        """Test sorting with a very large dataset (10,000 elements)."""
        from src.bubble_sort import bubble_sort

        random.seed(42)
        test_data = [random.randint(1, 100000) for _ in range(10000)]

        result = bubble_sort(test_data.copy())

        assert result == sorted(test_data)
        assert len(result) == 10000

    def test_stress_maximum_size_list(self):
        """Test sorting with a list at the upper limit of reasonable size (5,000 elements)."""
        from src.bubble_sort import bubble_sort

        random.seed(123)
        test_data = [random.randint(1, 100000) for _ in range(5000)]

        start = time.perf_counter()
        result = bubble_sort(test_data.copy())
        end = time.perf_counter()

        assert result == sorted(test_data)
        assert len(result) == 5000
        # Verify it completes within reasonable time (should be under 10 seconds)
        assert end - start < 10, f"Sorting took {end - start:.2f} seconds"

    def test_stress_repeated_sorting(self):
        """Test that repeated sorting of the same data produces consistent results."""
        from src.bubble_sort import bubble_sort

        random.seed(456)
        original = [random.randint(1, 1000) for _ in range(1000)]

        result1 = bubble_sort(original.copy())
        result2 = bubble_sort(result1.copy())
        result3 = bubble_sort(result2.copy())

        assert result1 == result2 == result3
        assert result1 == sorted(original)

    def test_stress_memory_pressure(self):
        """Test sorting under memory pressure conditions."""
        from src.bubble_sort import bubble_sort

        # Create multiple large lists to stress memory
        random.seed(789)
        lists = [
            [random.randint(1, 10000) for _ in range(5000)],
            [random.randint(1, 10000) for _ in range(5000)],
            [random.randint(1, 10000) for _ in range(5000)],
        ]

        results = []
        for lst in lists:
            result = bubble_sort(lst.copy())
            results.append(result)
            assert result == sorted(lst)

        # Verify all results are correct
        for i, (original, result) in enumerate(zip(lists, results)):
            assert result == sorted(original), f"List {i} failed sorting"

    def test_stress_extreme_duplicates(self):
        """Test sorting with extreme duplicate values."""
        from src.bubble_sort import bubble_sort

        # Create list with 90% duplicates
        random.seed(101112)
        test_data = []
        for _ in range(1000):
            test_data.extend([5] * 9 + [random.randint(1, 100)])

        result = bubble_sort(test_data.copy())

        assert result == sorted(test_data)
        assert Counter(result) == Counter(test_data)

    def test_stress_alternating_extreme_values(self):
        """Test sorting with alternating extreme positive and negative values."""
        from src.bubble_sort import bubble_sort

        # Create alternating extreme values
        test_data = []
        for i in range(2000):
            test_data.append(10**18 if i % 2 == 0 else -(10**18))

        random.shuffle(test_data)
        result = bubble_sort(test_data.copy())

        expected = sorted(test_data)
        assert result == expected

    def test_stress_concurrent_operations(self):
        """Test that sorting doesn't interfere with other list operations."""
        from src.bubble_sort import bubble_sort

        random.seed(131415)
        test_data = [random.randint(1, 1000) for _ in range(2000)]

        # Create copies for different operations
        sorted_copy = test_data.copy()
        bubble_sort(sorted_copy)

        # Verify other list operations still work
        assert len(sorted_copy) == 2000
        assert sorted_copy[0] <= sorted_copy[-1]
        assert Counter(sorted_copy) == Counter(test_data)

    def test_stress_regression_prevention(self):
        """Test known problematic patterns to prevent regressions."""
        from src.bubble_sort import bubble_sort

        # Pattern 1: Many small out-of-order segments
        pattern1 = [i + 1 if i % 3 != 0 else i - 1 for i in range(1, 1001)]
        result1 = bubble_sort(pattern1.copy())
        assert result1 == sorted(pattern1)

        # Pattern 2: Worst-case reverse sorted
        pattern2 = list(range(1000, 0, -1))
        result2 = bubble_sort(pattern2.copy())
        assert result2 == list(range(1, 1001))

        # Pattern 3: Sawtooth pattern
        pattern3 = [i % 100 for i in range(1000)]
        result3 = bubble_sort(pattern3.copy())
        assert result3 == sorted(pattern3)

    def test_stress_stability_preservation(self):
        """Test that stability is preserved even under stress."""
        from src.bubble_sort import bubble_sort

        # Create list with many equal values that need to maintain relative order
        random.seed(161718)
        test_data = [(i % 100, i) for i in range(2000)]

        result = bubble_sort(test_data.copy())

        # Verify sorting by first element
        for i in range(len(result) - 1):
            assert result[i][0] <= result[i + 1][0]

        # Verify stability: for equal first elements, order should be preserved
        for value in range(100):
            indices = [i for i, x in enumerate(test_data) if x[0] == value]
            result_indices = [i for i, x in enumerate(result) if x[0] == value]

            # The relative order should be preserved
            original_order = [test_data[i][1] for i in indices]
            result_order = [result[i][1] for i in result_indices]

            assert (
                original_order == result_order
            ), f"Stability broken for value {value}"

    def test_stress_boundary_conditions(self):
        """Test boundary conditions that might cause issues."""
        from src.bubble_sort import bubble_sort

        # Test with list at typical maximum for bubble sort
        # (beyond this, performance becomes prohibitive)
        random.seed(192021)
        test_data = [random.randint(1, 100000) for _ in range(10000)]

        result = bubble_sort(test_data.copy())

        # Verify basic properties
        assert len(result) == len(test_data)
        assert result == sorted(test_data)
        assert Counter(result) == Counter(test_data)

        # Verify it's actually sorted
        for i in range(len(result) - 1):
            assert result[i] <= result[i + 1]
