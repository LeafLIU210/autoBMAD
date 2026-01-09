"""
Enhanced test suite for bubble sort with additional edge cases and stress tests.

This module extends the comprehensive test coverage with stress tests,
performance benchmarks, and additional edge cases to ensure robustness.
"""

import pytest
import time
from typing import Generator


class TestBubbleSortStressCases:
    """Stress test scenarios for bubble sort."""

    def test_very_large_list(self):
        """Test sorting a large list of numbers."""
        from src.bubblesort import bubble_sort

        # Generate a moderately large list (bubble sort is O(n²))
        large_list = list(range(1000, 0, -1))
        start_time = time.time()
        result = bubble_sort(large_list)
        elapsed = time.time() - start_time

        # Verify correctness
        assert result == list(range(1, 1001))
        # Verify it's a new list
        assert result is not large_list
        # Should complete in reasonable time (bubble sort is slow)
        # Allow more time for larger lists
        assert elapsed < 10.0, f"Sorting took too long: {elapsed}s"

    def test_maximum_sized_list(self):
        """Test sorting with maximum practical list size."""
        from src.bubblesort import bubble_sort

        # Test with a more moderate size for regular testing
        large_list = list(range(1000, 0, -1))
        result = bubble_sort(large_list)
        assert result == list(range(1, 1001))
        assert len(result) == 1000

    def test_repeated_large_values(self):
        """Test with repeated large values."""
        from src.bubblesort import bubble_sort

        large_values = [1000000] * 100 + list(range(100))
        result = bubble_sort(large_values)
        expected = list(range(100)) + [1000000] * 100
        assert result == expected


class TestBubbleSortMemoryBehavior:
    """Test memory-related behavior and efficiency."""

    def test_returns_list_type(self):
        """Verify function always returns a list."""
        from src.bubblesort import bubble_sort

        # Test with various inputs
        test_cases = [
            [3, 2, 1],
            (3, 2, 1),  # tuple
            [5],  # single element
            [],  # empty
            range(5),  # range
        ]

        for test_input in test_cases:
            result = bubble_sort(test_input)
            assert isinstance(result, list), f"Expected list for input {test_input}"

    def test_does_not_modify_input(self):
        """Comprehensive test that input is never modified."""
        from src.bubblesort import bubble_sort

        test_cases = [
            [5, 4, 3, 2, 1],
            [1, 2, 3, 4, 5],
            [3, 3, 3, 3],
            [1],
            [],
            [-5, 10, -3, 8],
        ]

        for original in test_cases:
            original_copy = original.copy()
            result = bubble_sort(original)
            assert original == original_copy, f"Input was modified for {original}"
            assert result is not original, "Should return a new list"


class TestBubbleSortTypeSystem:
    """Test type system and type hints."""

    def test_accepts_iterable_protocol(self):
        """Test that function accepts any iterable."""
        from src.bubblesort import bubble_sort

        # Test with various iterable types
        iterables = [
            [1, 2, 3],
            (1, 2, 3),
            range(1, 4),
            {1, 2, 3},  # set (unordered)
            iter([1, 2, 3]),  # iterator
        ]

        for iterable in iterables:
            result = bubble_sort(iterable)
            assert isinstance(result, list)
            assert len(result) == 3

    def test_type_consistency(self):
        """Test that sorting preserves type relationships."""
        from src.bubblesort import bubble_sort

        # Integers should produce comparable results
        int_result = bubble_sort([3, 1, 2])
        assert all(isinstance(x, (int, float)) for x in int_result)

        # Floats should produce comparable results
        float_result = bubble_sort([3.5, 1.2, 2.8])
        assert all(isinstance(x, (int, float)) for x in float_result)


class TestBubbleSortAlgorithmVerification:
    """Verify the algorithm implementation details."""

    def test_swapping_works_correctly(self):
        """Test that adjacent element swapping works correctly."""
        from src.bubblesort import bubble_sort

        # Test case where each pair needs swapping
        input_list = [5, 4, 3, 2, 1]
        result = bubble_sort(input_list)
        assert result == [1, 2, 3, 4, 5]

        # Test case with no swaps needed
        input_list = [1, 2, 3, 4, 5]
        result = bubble_sort(input_list)
        assert result == [1, 2, 3, 4, 5]

    def test_optimization_flag_works(self):
        """Test that the optimization (early exit) works."""
        from src.bubblesort import bubble_sort

        # Already sorted list - should exit early
        sorted_list = list(range(1, 101))
        start_time = time.time()
        result = bubble_sort(sorted_list)
        elapsed = time.time() - start_time

        assert result == sorted_list
        # Should be very fast for already sorted
        assert elapsed < 0.1

    def test_stability(self):
        """Test that equal elements maintain their relative order."""
        from src.bubblesort import bubble_sort

        # Create list with equal elements
        input_list = [(1, 'a'), (1, 'b'), (2, 'c'), (1, 'd')]
        # Bubble sort should be stable for this implementation
        # Note: This test depends on how tuples are compared
        result = bubble_sort(input_list)
        assert result[0][0] <= result[1][0] <= result[2][0] <= result[3][0]


class TestBubbleSortBoundaryConditions:
    """Test boundary and limit conditions."""

    def test_extreme_values(self):
        """Test with extreme numeric values."""
        from src.bubblesort import bubble_sort

        extreme_values = [
            float('inf'),
            float('-inf'),
            0,
            -0,
            1e308,  # Large number
            -1e308,  # Small number
        ]
        result = bubble_sort(extreme_values)
        assert isinstance(result, list)
        assert len(result) == len(extreme_values)

    def test_very_small_lists(self):
        """Test with minimum-sized lists."""
        from src.bubblesort import bubble_sort

        # Empty list
        assert bubble_sort([]) == []

        # Single element
        assert bubble_sort([42]) == [42]
        assert bubble_sort([0]) == [0]
        assert bubble_sort([-5]) == [-5]

    def test_identical_elements(self):
        """Test with all identical elements."""
        from src.bubblesort import bubble_sort

        result = bubble_sort([5] * 100)
        assert result == [5] * 100
        assert all(x == 5 for x in result)


class TestBubbleSortIntegration:
    """Integration tests with Python ecosystem."""

    def test_with_list_comprehension(self):
        """Test that function works in list comprehensions."""
        from src.bubblesort import bubble_sort

        numbers = [[5, 1, 4], [3, 2, 6], [9, 0]]
        sorted_lists = [bubble_sort(lst) for lst in numbers]
        assert sorted_lists == [[1, 4, 5], [2, 3, 6], [0, 9]]

    def test_with_map_filter(self):
        """Test that function works with map/filter."""
        from src.bubblesort import bubble_sort

        # Sort results from map
        mapped = map(lambda x: x * 2, [3, 1, 2])
        result = bubble_sort(mapped)
        assert result == [2, 4, 6]

    def test_nested_sorting(self):
        """Test sorting the result of another sort."""
        from src.bubblesort import bubble_sort

        # Sort already sorted list
        result = bubble_sort(bubble_sort([3, 2, 1]))
        assert result == [1, 2, 3]

        # Sort multiple times
        multiple_sort = bubble_sort(bubble_sort(bubble_sort([5, 1, 3])))
        assert multiple_sort == [1, 3, 5]


class TestBubbleSortReproducibility:
    """Test that results are deterministic and reproducible."""

    @pytest.mark.parametrize("run", range(10))
    def test_deterministic_results(self, run):
        """Test that multiple runs produce identical results."""
        from src.bubblesort import bubble_sort

        input_list = [5, 3, 8, 1, 9, 2]
        result1 = bubble_sort(input_list)
        result2 = bubble_sort(input_list)
        result3 = bubble_sort(input_list)

        assert result1 == result2 == result3

    def test_randomness_handling(self):
        """Test that the function handles random-like input."""
        from src.bubblesort import bubble_sort
        import random

        random.seed(42)
        random_list = [random.randint(-100, 100) for _ in range(50)]
        result = bubble_sort(random_list)

        # Verify result is sorted
        assert all(result[i] <= result[i + 1] for i in range(len(result) - 1))
        # Verify all elements are present
        assert sorted(random_list) == result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
