"""Regression tests for bubble sort module.

This test file contains regression tests to ensure that previously identified bugs
and edge cases don't reappear in future changes to the bubble sort implementation.
"""


class TestBubbleSortRegression:
    """Regression test cases for bubble sort algorithm.

    These tests capture specific bugs and edge cases that were identified
    during development and testing to prevent regressions.
    """

    def test_regression_empty_list_handling(self):
        """Regression: Ensure empty list is handled correctly.

        Bug: Some implementations might crash or return None for empty lists.
        Fix: Bubble sort should return empty list immediately.
        """
        from src.bubble_sort import bubble_sort

        result = bubble_sort([])
        assert result == []
        assert isinstance(result, list)

    def test_regression_single_element_list(self):
        """Regression: Ensure single-element list returns correctly.

        Bug: Some implementations might attempt to modify single-element lists.
        Fix: Single-element lists should be returned as-is.
        """
        from src.bubble_sort import bubble_sort

        result = bubble_sort([42])
        assert result == [42]
        assert len(result) == 1

    def test_regression_already_sorted_list(self):
        """Regression: Already sorted list should be handled efficiently.

        Bug: Some implementations might unnecessarily continue sorting.
        Fix: Use swapped flag to detect already sorted list and break early.
        """
        from src.bubble_sort import bubble_sort

        sorted_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = bubble_sort(sorted_list)

        assert result == sorted_list
        # Input should not be modified
        assert sorted_list == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        # Result should be a new list
        assert id(result) != id(sorted_list)

    def test_regression_reverse_sorted_list(self):
        """Regression: Reverse sorted list should be sorted correctly.

        Bug: Some implementations might not handle worst-case scenario correctly.
        Fix: Should complete successfully for reverse-sorted lists.
        """
        from src.bubble_sort import bubble_sort

        reverse_sorted = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        result = bubble_sort(reverse_sorted)

        assert result == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_regression_all_identical_elements(self):
        """Regression: List with all identical elements.

        Bug: Some implementations might enter infinite loop or fail comparison.
        Fix: Should handle identical elements correctly.
        """
        from src.bubble_sort import bubble_sort

        identical = [5, 5, 5, 5, 5, 5, 5]
        result = bubble_sort(identical)

        assert result == [5, 5, 5, 5, 5, 5, 5]
        # With optimization, should detect no swaps and break early

    def test_regression_two_element_list(self):
        """Regression: Two-element list sorting.

        Bug: Some implementations might have off-by-one errors with n=2.
        Fix: Should correctly sort two-element lists.
        """
        from src.bubble_sort import bubble_sort

        # Already sorted
        assert bubble_sort([1, 2]) == [1, 2]

        # Needs sorting
        assert bubble_sort([2, 1]) == [1, 2]

    def test_regression_negative_numbers(self):
        """Regression: Negative numbers should be sorted correctly.

        Bug: Some implementations might mishandle negative number comparisons.
        Fix: Should handle negative numbers in sort order.
        """
        from src.bubble_sort import bubble_sort

        with_negatives = [-5, -2, -8, -1, 0, 3, -3, 1]
        result = bubble_sort(with_negatives)

        expected = sorted(with_negatives)
        assert result == expected

    def test_regression_zero_in_list(self):
        """Regression: Zero should be sorted correctly with other numbers.

        Bug: Some implementations might treat zero specially.
        Fix: Zero should be sorted like any other number.
        """
        from src.bubble_sort import bubble_sort

        with_zeros = [5, 0, 3, 0, 1, -1]
        result = bubble_sort(with_zeros)

        expected = sorted(with_zeros)
        assert result == expected

    def test_regression_floating_point_precision(self):
        """Regression: Floating point numbers should maintain precision.

        Bug: Some implementations might lose precision or fail on floats.
        Fix: Should handle floating point numbers correctly.
        """
        from src.bubble_sort import bubble_sort

        floats = [3.14, 1.5, 2.7, 0.5, 4.2, 1.1]
        result = bubble_sort(floats)

        expected = sorted(floats)
        assert result == expected

    def test_regression_string_sorting(self):
        """Regression: String sorting should work correctly.

        Bug: Some implementations might not handle string comparisons.
        Fix: Should sort strings lexicographically.
        """
        from src.bubble_sort import bubble_sort

        strings = ["zebra", "apple", "banana", "cherry", "apricot"]
        result = bubble_sort(strings)

        expected = sorted(strings)
        assert result == expected

    def test_regression_large_gaps_in_values(self):
        """Regression: Large gaps between values should be handled.

        Bug: Some implementations might overflow or mishandle large numbers.
        Fix: Should handle large numerical ranges.
        """
        from src.bubble_sort import bubble_sort

        large_gaps = [10**15, -(10**15), 10**10, -(10**10), 0, 1, -1]
        result = bubble_sort(large_gaps)

        expected = sorted(large_gaps)
        assert result == expected

    def test_regression_mixed_positive_negative(self):
        """Regression: Mix of positive, negative, and zero.

        Bug: Some implementations might have comparison issues.
        Fix: Should correctly order negative, zero, and positive.
        """
        from src.bubble_sort import bubble_sort

        mixed = [-5, 5, -3, 3, -1, 1, 0, 0]
        result = bubble_sort(mixed)

        expected = sorted(mixed)
        assert result == expected

    def test_regression_duplicates_scattered(self):
        """Regression: Duplicates should maintain stability.

        Bug: Some implementations might lose stability with duplicates.
        Fix: Bubble sort is stable, should preserve relative order.
        """
        from src.bubble_sort import bubble_sort

        # Use tuples to test stability
        duplicates = [(1, "a"), (2, "b"), (1, "c"), (2, "d"), (1, "e")]
        result = bubble_sort(duplicates)

        # Should be sorted by first element
        assert result[0][0] == 1
        assert result[1][0] == 1
        assert result[2][0] == 1
        assert result[3][0] == 2
        assert result[4][0] == 2

    def test_regression_pure_function_behavior(self):
        """Regression: Function should be pure and not modify input.

        Bug: Some implementations might modify the input list.
        Fix: Should create a new list without modifying the input.
        """
        from src.bubble_sort import bubble_sort

        original = [3, 1, 2]
        original_id = id(original)

        result = bubble_sort(original)

        # Should return a new object
        assert id(result) != original_id
        # Input should not be modified
        assert original == [3, 1, 2]
        # Result should be sorted
        assert result == [1, 2, 3]

    def test_regression_nearly_sorted_list(self):
        """Regression: Nearly sorted list should be handled efficiently.

        Bug: Some implementations might do unnecessary work on nearly sorted lists.
        Fix: With swap detection, should handle nearly sorted lists efficiently.
        """
        from src.bubble_sort import bubble_sort

        nearly_sorted = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = bubble_sort(nearly_sorted)

        assert result == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        # Input should not be modified
        assert nearly_sorted == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        # Should create a new list
        assert id(result) != id(nearly_sorted)

    def test_regression_swap_optimization(self):
        """Regression: Swap detection optimization should work.

        Bug: Without optimization, bubble sort does unnecessary passes.
        Fix: Early termination when no swaps occur.
        """
        from src.bubble_sort import bubble_sort

        # Already sorted - should detect no swaps
        sorted_list = [1, 2, 3, 4, 5]
        result = bubble_sort(sorted_list)

        assert result == [1, 2, 3, 4, 5]
        # With optimization, should do minimal passes

    def test_regression_early_termination(self):
        """Regression: Early termination should work correctly.

        Bug: Some implementations might not break when array is sorted.
        Fix: Should break out of outer loop when no swaps occur.
        """
        from src.bubble_sort import bubble_sort

        # Test with a list that becomes sorted before all passes complete
        nearly_sorted = [1, 3, 2, 4, 5, 6, 7, 8, 9, 10]
        result = bubble_sort(nearly_sorted)

        assert result == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_regression_boundary_n_equals_1(self):
        """Regression: n=1 (smallest non-empty list).

        Bug: Some implementations might have special case issues.
        Fix: Should handle n=1 correctly.
        """
        from src.bubble_sort import bubble_sort

        assert bubble_sort([1]) == [1]

    def test_regression_boundary_n_equals_2(self):
        """Regression: n=2 (smallest list that needs sorting).

        Bug: Some implementations might have off-by-one errors.
        Fix: Should handle n=2 correctly.
        """
        from src.bubble_sort import bubble_sort

        assert bubble_sort([2, 1]) == [1, 2]
        assert bubble_sort([1, 2]) == [1, 2]

    def test_regression_boundary_n_equals_3(self):
        """Regression: n=3 (smallest interesting case).

        Bug: Some implementations might have issues with 3 elements.
        Fix: Should handle n=3 correctly.
        """
        from src.bubble_sort import bubble_sort

        assert bubble_sort([3, 2, 1]) == [1, 2, 3]
        assert bubble_sort([1, 3, 2]) == [1, 2, 3]
        assert bubble_sort([2, 1, 3]) == [1, 2, 3]
        assert bubble_sort([2, 3, 1]) == [1, 2, 3]
        assert bubble_sort([3, 1, 2]) == [1, 2, 3]

    def test_regression_tuples_with_same_first_element(self):
        """Regression: Tuples with same first element should be sorted correctly.

        When tuples have the same first element, Python compares the second elements.
        This test verifies correct sorting behavior.
        """
        from src.bubble_sort import bubble_sort

        # Use tuples where first elements are equal - they will be sorted by second element
        tuples_test = [(1, "d"), (1, "a"), (1, "c"), (1, "b")]
        result = bubble_sort(tuples_test)

        # All should have first element 1
        assert all(t[0] == 1 for t in result)
        # Should be sorted by second element alphabetically
        assert result[0][1] == "a"
        assert result[1][1] == "b"
        assert result[2][1] == "c"
        assert result[3][1] == "d"

    def test_regression_consecutive_duplicate_values(self):
        """Regression: Consecutive duplicate values.

        Bug: Some implementations might have issues with consecutive duplicates.
        Fix: Should handle consecutive duplicates correctly.
        """
        from src.bubble_sort import bubble_sort

        consecutive_dups = [1, 1, 1, 2, 2, 2, 3, 3, 3]
        result = bubble_sort(consecutive_dups)

        assert result == [1, 1, 1, 2, 2, 2, 3, 3, 3]

    def test_regression_single_swap_needed(self):
        """Regression: Lists requiring only one swap.

        Bug: Some implementations might do unnecessary work.
        Fix: Should handle single-swap cases efficiently.
        """
        from src.bubble_sort import bubble_sort

        single_swap = [1, 3, 2, 4, 5, 6, 7, 8, 9, 10]
        result = bubble_sort(single_swap)

        assert result == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_regression_at_beginning_and_end(self):
        """Regression: Elements out of place at beginning and end.

        Bug: Some implementations might not handle this correctly.
        Fix: Should correctly place elements at both ends.
        """
        from src.bubble_sort import bubble_sort

        misplaced = [10, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        result = bubble_sort(misplaced)

        assert result == list(range(1, 11))

    def test_regression_palindrome_like_pattern(self):
        """Regression: Palindrome-like pattern.

        Bug: Some implementations might have issues with symmetric patterns.
        Fix: Should handle palindrome-like patterns.
        """
        from src.bubble_sort import bubble_sort

        palindrome_pattern = [1, 2, 3, 2, 1]
        result = bubble_sort(palindrome_pattern)

        assert result == [1, 1, 2, 2, 3]

    def test_regression_very_long_sequence_of_same_value(self):
        """Regression: Very long sequence of identical values.

        Bug: Some implementations might have performance issues.
        Fix: Should handle long sequences efficiently with optimization.
        """
        from src.bubble_sort import bubble_sort

        long_sequence = [42] * 1000
        result = bubble_sort(long_sequence)

        assert result == [42] * 1000
        # With optimization, should detect no swaps early

    def test_regression_alternating_extreme_values(self):
        """Regression: Alternating extreme positive and negative.

        Bug: Some implementations might overflow or have comparison issues.
        Fix: Should handle alternating extremes correctly.
        """
        from src.bubble_sort import bubble_sort

        alternating = [10**18, -(10**18), 10**18, -(10**18)]
        result = bubble_sort(alternating)

        expected = sorted(alternating)
        assert result == expected
