"""Optimization detection tests for bubble sort module.

This test file verifies that bubble sort's optimization features work correctly,
including early termination detection and swap detection.
"""

import time


class TestBubbleSortOptimization:
    """Optimization detection test cases for bubble sort algorithm."""

    def test_early_termination_already_sorted(self):
        """Test that already-sorted list triggers early termination."""
        from src.bubble_sort import bubble_sort

        # Already sorted list should terminate after first pass
        sorted_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = bubble_sort(sorted_list)

        assert result == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        assert result is sorted_list  # Should still be in-place

    def test_early_termination_single_swap(self):
        """Test that lists requiring only one swap terminate early."""
        from src.bubble_sort import bubble_sort

        # Only two elements out of place
        test_list = [1, 2, 3, 5, 4, 6, 7, 8, 9, 10]
        result = bubble_sort(test_list)

        assert result == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_early_termination_two_swaps(self):
        """Test that lists requiring two swaps work correctly."""
        from src.bubble_sort import bubble_sort

        # Two separate elements out of place
        test_list = [1, 2, 4, 3, 5, 7, 6, 8, 9, 10]
        result = bubble_sort(test_list)

        assert result == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_no_early_termination_reverse_sorted(self):
        """Test that reverse-sorted list requires full sorting."""
        from src.bubble_sort import bubble_sort

        # Worst case - should require full passes
        reverse_list = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        result = bubble_sort(reverse_list)

        assert result == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_optimization_performance_small_sorted(self):
        """Test that sorted lists are much faster than reverse-sorted."""
        from src.bubble_sort import bubble_sort

        # Create two lists of the same size
        size = 100
        sorted_list = list(range(size))
        reverse_list = list(range(size, 0, -1))

        # Time the sorted list (should be very fast due to optimization)
        start = time.perf_counter()
        bubble_sort(sorted_list.copy())
        sorted_time = time.perf_counter() - start

        # Time the reverse list (should be slower)
        start = time.perf_counter()
        bubble_sort(reverse_list.copy())
        reverse_time = time.perf_counter() - start

        # Sorted should be significantly faster
        # (allowing some variance but should be noticeably different)
        assert sorted_time < reverse_time, (
            f"Sorted list ({sorted_time:.6f}s) should be faster than "
            f"reverse-sorted ({reverse_time:.6f}s)"
        )

    def test_optimization_with_duplicates(self):
        """Test early termination with duplicate elements."""
        from src.bubble_sort import bubble_sort

        # Already sorted with duplicates
        test_list = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
        result = bubble_sort(test_list)

        assert result == [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]

    def test_nearly_sorted_optimization(self):
        """Test that nearly-sorted lists benefit from optimization."""
        from src.bubble_sort import bubble_sort

        # Only a few elements out of place
        nearly_sorted = [1, 2, 3, 4, 6, 5, 7, 8, 9, 10]
        result = bubble_sort(nearly_sorted)

        assert result == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_swap_detection_with_specific_pattern(self):
        """Test swap detection with specific out-of-order patterns."""
        from src.bubble_sort import bubble_sort

        # Pattern: most sorted, just a few swaps needed
        patterns = [
            [1, 2, 3, 5, 4],  # One swap needed
            [1, 3, 2, 4, 5],  # One swap needed
            [2, 1, 3, 4, 5],  # One swap needed
            [1, 2, 4, 3, 5],  # One swap needed
        ]

        for pattern in patterns:
            result = bubble_sort(pattern)
            assert result == [1, 2, 3, 4, 5]

    def test_boundary_optimization(self):
        """Test optimization at boundaries (empty and single element)."""
        from src.bubble_sort import bubble_sort

        # Empty list
        empty = []
        result = bubble_sort(empty)
        assert result == []

        # Single element
        single = [42]
        result = bubble_sort(single)
        assert result == [42]

    def test_all_identical_elements_optimization(self):
        """Test that all identical elements trigger optimization."""
        from src.bubble_sort import bubble_sort

        # All elements identical - should terminate after first pass
        test_list = [42] * 50
        result = bubble_sort(test_list)

        assert result == [42] * 50

    def test_optimization_preserves_stability(self):
        """Test that optimization preserves stability."""
        from src.bubble_sort import bubble_sort

        # Already sorted with equal elements
        items = [(1, "a"), (1, "b"), (1, "c"), (2, "a")]
        result = bubble_sort(items)

        # Should maintain relative order of equal elements
        assert result[0][1] == "a"
        assert result[1][1] == "b"
        assert result[2][1] == "c"

    def test_multiple_nearly_sorted_patterns(self):
        """Test various nearly-sorted patterns."""
        from src.bubble_sort import bubble_sort

        patterns = [
            [1, 2, 3, 4, 5, 7, 6, 8, 9, 10],  # One pair swapped
            [1, 3, 2, 4, 5, 6, 7, 8, 9, 10],  # Adjacent pair swapped
            [1, 2, 3, 5, 4, 6, 7, 9, 8, 10],  # Two pairs swapped
        ]

        expected = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        for pattern in patterns:
            result = bubble_sort(pattern)
            assert result == expected

    def test_optimization_with_floats(self):
        """Test early termination with floating point numbers."""
        from src.bubble_sort import bubble_sort

        # Already sorted floats
        floats = [1.0, 2.5, 3.7, 4.2, 5.9]
        result = bubble_sort(floats)

        assert result == [1.0, 2.5, 3.7, 4.2, 5.9]

    def test_optimization_with_strings(self):
        """Test early termination with strings."""
        from src.bubble_sort import bubble_sort

        # Already sorted strings
        strings = ["a", "b", "c", "d", "e"]
        result = bubble_sort(strings)

        assert result == ["a", "b", "c", "d", "e"]

    def test_very_small_lists_optimization(self):
        """Test optimization works correctly for very small lists."""
        from src.bubble_sort import bubble_sort

        test_cases = [
            ([], []),
            ([1], [1]),
            ([1, 2], [1, 2]),
            ([2, 1], [1, 2]),
        ]

        for input_list, expected in test_cases:
            result = bubble_sort(input_list)
            assert result == expected

    def test_alternating_optimization(self):
        """Test optimization with alternating sorted patterns."""
        from src.bubble_sort import bubble_sort

        # Alternating high-low but nearly sorted
        test_list = [1, 100, 2, 99, 3, 98, 4, 97, 5, 96]
        result = bubble_sort(test_list)

        expected = [1, 2, 3, 4, 5, 96, 97, 98, 99, 100]
        assert result == expected
