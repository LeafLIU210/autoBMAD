"""
Test bubble sort implementation.

This module contains comprehensive unit tests for the bubble sort algorithm
implementation, covering edge cases, various input types, and functional behavior.
"""

import pytest

from src.bubblesort.bubble_sort import bubble_sort


class TestBubbleSort:
    """Test suite for bubble sort algorithm."""

    def test_empty_list(self) -> None:
        """Test that bubble sort handles empty list correctly."""
        input_list = []
        result = bubble_sort(input_list)
        assert result == [], "Empty list should return empty list"
        # Should not modify the original
        assert input_list == [], "Original list should remain unchanged"

    def test_single_element(self) -> None:
        """Test that bubble sort handles single element correctly."""
        input_list = [5]
        result = bubble_sort(input_list)
        assert result == [5], "Single element list should remain unchanged"
        assert input_list == [5], "Original list should remain unchanged"

    def test_two_elements_sorted(self) -> None:
        """Test that bubble sort handles already sorted two-element list."""
        input_list = [1, 2]
        result = bubble_sort(input_list)
        assert result == [1, 2], "Sorted list should remain sorted"
        assert input_list == [1, 2], "Original list should remain unchanged"

    def test_two_elements_unsorted(self) -> None:
        """Test that bubble sort sorts two-element unsorted list."""
        input_list = [2, 1]
        result = bubble_sort(input_list)
        assert result == [1, 2], "Unsorted list should be sorted"
        assert input_list == [2, 1], "Original list should remain unchanged"

    def test_three_elements_sorted(self) -> None:
        """Test that bubble sort handles already sorted three-element list."""
        input_list = [1, 2, 3]
        result = bubble_sort(input_list)
        assert result == [1, 2, 3], "Sorted list should remain sorted"

    def test_three_elements_reverse_sorted(self) -> None:
        """Test that bubble sort sorts reverse-sorted three-element list."""
        input_list = [3, 2, 1]
        result = bubble_sort(input_list)
        assert result == [1, 2, 3], "Reverse-sorted list should be sorted"

    def test_three_elements_random_order(self) -> None:
        """Test that bubble sort sorts three-element random order list."""
        test_cases = [
            ([2, 3, 1], [1, 2, 3]),
            ([3, 1, 2], [1, 2, 3]),
            ([2, 1, 3], [1, 2, 3]),
        ]

        for input_list, expected in test_cases:
            result = bubble_sort(input_list.copy())
            assert result == expected, f"{input_list} should sort to {expected}"

    def test_five_elements(self) -> None:
        """Test that bubble sort handles five-element list."""
        input_list = [5, 2, 4, 1, 3]
        result = bubble_sort(input_list)
        assert result == [1, 2, 3, 4, 5], "Five-element list should be sorted"

    def test_larger_list(self) -> None:
        """Test that bubble sort handles larger lists."""
        input_list = [64, 34, 25, 12, 22, 11, 90]
        result = bubble_sort(input_list)
        assert result == [11, 12, 22, 25, 34, 64, 90], \
            "Larger list should be properly sorted"

    def test_list_with_duplicates(self) -> None:
        """Test that bubble sort handles list with duplicate values."""
        input_list = [3, 1, 4, 1, 5, 9, 2, 6]
        result = bubble_sort(input_list)
        assert result == [1, 1, 2, 3, 4, 5, 6, 9], \
            "List with duplicates should be sorted"

    def test_list_with_all_duplicates(self) -> None:
        """Test that bubble sort handles list where all elements are identical."""
        input_list = [5, 5, 5, 5, 5]
        result = bubble_sort(input_list)
        assert result == [5, 5, 5, 5, 5], \
            "List with all duplicates should remain unchanged"

    def test_negative_numbers(self) -> None:
        """Test that bubble sort handles negative numbers."""
        input_list = [3, -1, -4, 0, 2]
        result = bubble_sort(input_list)
        assert result == [-4, -1, 0, 2, 3], \
            "List with negative numbers should be sorted"

    def test_all_negative_numbers(self) -> None:
        """Test that bubble sort handles list with all negative numbers."""
        input_list = [-3, -1, -4, -2]
        result = bubble_sort(input_list)
        assert result == [-4, -3, -2, -1], \
            "List with all negative numbers should be sorted"

    def test_large_numbers(self) -> None:
        """Test that bubble sort handles large numbers."""
        input_list = [1000000, 500000, 999999, 1]
        result = bubble_sort(input_list)
        assert result == [1, 500000, 999999, 1000000], \
            "List with large numbers should be sorted"

    def test_float_numbers(self) -> None:
        """Test that bubble sort handles floating-point numbers."""
        input_list = [3.14, 2.71, 1.41, 0.5]
        result = bubble_sort(input_list)
        assert result == [0.5, 1.41, 2.71, 3.14], \
            "List with floats should be sorted"

    def test_mixed_integers_and_floats(self) -> None:
        """Test that bubble sort handles mixed integers and floats."""
        input_list = [3, 2.5, 4, 1.5]
        result = bubble_sort(input_list)
        assert result == [1.5, 2.5, 3, 4], \
            "List with mixed ints and floats should be sorted"

    def test_returns_new_list(self) -> None:
        """Test that bubble sort returns a new list, not modify original."""
        original = [5, 3, 2, 4, 1]
        original_copy = original.copy()
        result = bubble_sort(original)

        # Original should not be modified
        assert original == original_copy, "Original list should not be modified"
        # Result should be different object
        assert result is not original, "Result should be a new list object"

    def test_sorted_list_returns_new_list(self) -> None:
        """Test that even sorted input returns a new list."""
        original = [1, 2, 3, 4, 5]
        result = bubble_sort(original)

        assert result is not original, "Result should be a new list object"
        assert result == original, "Result should have same content"

    def test_stability_with_tuples(self) -> None:
        """Test that bubble sort maintains stability with complex objects."""
        # Using tuples to test stability
        items = [(2, 'a'), (1, 'b'), (2, 'c'), (1, 'a')]
        # Extract first elements for sorting
        result = bubble_sort(items)
        # Check that items with same first element maintain relative order
        first_elements = [item[0] for item in result]
        assert first_elements == [1, 1, 2, 2], "First elements should be sorted"

    def test_type_consistency(self) -> None:
        """Test that output type matches input type."""
        # Test with list
        assert isinstance(bubble_sort([]), list), "Result should be a list"
        assert isinstance(bubble_sort([1]), list), "Result should be a list"

    def test_algorithm_sorts_correctly(self) -> None:
        """
        Comprehensive test to verify the algorithm actually sorts.

        This test validates that the bubble sort implementation correctly
        sorts lists of various sizes and compositions.
        """
        test_cases = [
            ([], []),
            ([1], [1]),
            ([2, 1], [1, 2]),
            ([1, 2, 3], [1, 2, 3]),
            ([3, 2, 1], [1, 2, 3]),
            ([5, 1, 4, 2, 8], [1, 2, 4, 5, 8]),
            ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
            ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
            ([1, 3, 2, 5, 4], [1, 2, 3, 4, 5]),
        ]

        for input_list, expected in test_cases:
            result = bubble_sort(input_list)
            assert result == expected, \
                f"bubble_sort({input_list}) should return {expected}, got {result}"

    def test_large_random_list(self) -> None:
        """Test bubble sort with a larger random-like list."""
        input_list = [64, 34, 25, 12, 22, 11, 90, 5, 77, 30]
        result = bubble_sort(input_list)
        expected = [5, 11, 12, 22, 25, 30, 34, 64, 77, 90]
        assert result == expected, "Large list should be correctly sorted"


class TestBubbleSortErrorHandling:
    """Test suite for bubble sort error handling."""

    def test_none_input_raises_typeerror(self) -> None:
        """Test that None input raises TypeError."""
        with pytest.raises(TypeError, match="Input cannot be None"):
            bubble_sort(None)

    def test_non_iterable_input_raises_typeerror(self) -> None:
        """Test that non-iterable input raises TypeError."""
        with pytest.raises(TypeError, match="Input must be iterable"):
            bubble_sort(42)

    def test_non_comparable_elements_raises_typeerror(self) -> None:
        """Test that list with non-comparable elements raises TypeError."""
        # Comparing int with string raises TypeError
        with pytest.raises(TypeError):
            bubble_sort([1, "two", 3])


class TestBubbleSortParameterized:
    """Parameterized test suite for bubble sort algorithm."""

    @pytest.mark.parametrize("input_list,expected", [
        # Edge cases
        ([], []),
        ([1], [1]),
        ([1, 1], [1, 1]),

        # Already sorted
        ([1, 2, 3], [1, 2, 3]),
        ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),

        # Reverse sorted
        ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
        ([3, 2, 1], [1, 2, 3]),

        # Random order
        ([2, 1, 3], [1, 2, 3]),
        ([3, 1, 2], [1, 2, 3]),
        ([2, 3, 1], [1, 2, 3]),
        ([5, 2, 4, 1, 3], [1, 2, 3, 4, 5]),
        ([64, 34, 25, 12, 22, 11, 90], [11, 12, 22, 25, 34, 64, 90]),
    ])
    def test_sorting_behavior(self, input_list, expected) -> None:
        """Test that bubble sort correctly sorts various input patterns."""
        result = bubble_sort(input_list)
        assert result == expected, f"bubble_sort({input_list}) should return {expected}, got {result}"

    @pytest.mark.parametrize("negative_list,expected", [
        ([-1, -2, -3], [-3, -2, -1]),
        ([3, -1, -4, 0, 2], [-4, -1, 0, 2, 3]),
        ([-3, -1, -4, -2], [-4, -3, -2, -1]),
        ([0, -1, 1], [-1, 0, 1]),
    ])
    def test_negative_numbers(self, negative_list, expected) -> None:
        """Test bubble sort with negative numbers."""
        result = bubble_sort(negative_list)
        assert result == expected, f"bubble_sort({negative_list}) should return {expected}"

    @pytest.mark.parametrize("float_list,expected", [
        ([3.14, 2.71, 1.41], [1.41, 2.71, 3.14]),
        ([1.5, 3.2, 0.5], [0.5, 1.5, 3.2]),
        ([2.5, 1.5, 3.5, 0.5], [0.5, 1.5, 2.5, 3.5]),
    ])
    def test_float_numbers(self, float_list, expected) -> None:
        """Test bubble sort with floating point numbers."""
        result = bubble_sort(float_list)
        assert result == expected, f"bubble_sort({float_list}) should return {expected}"

    @pytest.mark.parametrize("mixed_list,expected", [
        ([3, 2.5, 4, 1.5], [1.5, 2.5, 3, 4]),
        ([1, 2.5, 3, 0.5], [0.5, 1, 2.5, 3]),
        ([5.5, 5, 4.5, 4], [4, 4.5, 5, 5.5]),
    ])
    def test_mixed_int_float(self, mixed_list, expected) -> None:
        """Test bubble sort with mixed integers and floats."""
        result = bubble_sort(mixed_list)
        assert result == expected, f"bubble_sort({mixed_list}) should return {expected}"

    @pytest.mark.parametrize("input_value", [
        None,
        42,
        3.14,
    ])
    def test_error_handling_parametrized(self, input_value) -> None:
        """Test error handling for invalid inputs."""
        if input_value is None:
            with pytest.raises(TypeError, match="Input cannot be None"):
                bubble_sort(input_value)
        else:
            with pytest.raises(TypeError, match="Input must be iterable"):
                bubble_sort(input_value)


class TestBubbleSortImmutability:
    """Test suite for bubble sort immutability (pure function behavior)."""

    def test_empty_list_not_modified(self) -> None:
        """Test that empty list is not modified."""
        original = []
        result = bubble_sort(original)
        assert result == [], "Should return empty list"
        assert original == [], "Original should remain empty"

    def test_single_element_not_modified(self) -> None:
        """Test that single element list is not modified."""
        original = [5]
        result = bubble_sort(original)
        assert result == [5], "Should return same element"
        assert original == [5], "Original should remain unchanged"
        assert result is not original, "Should return new list instance"

    def test_multiple_elements_not_modified(self) -> None:
        """Test that multiple element list is not modified."""
        original = [5, 3, 2, 4, 1]
        original_copy = original.copy()
        result = bubble_sort(original)

        assert result == [1, 2, 3, 4, 5], "Should return sorted list"
        assert original == original_copy, "Original list should not be modified"
        assert result is not original, "Should return new list instance"

    def test_sorted_input_returns_new_list(self) -> None:
        """Test that sorted input returns a new list."""
        original = [1, 2, 3, 4, 5]
        result = bubble_sort(original)

        assert result is not original, "Should return new list instance"
        assert result == original, "Should have same content"
        assert id(result) != id(original), "Should have different memory addresses"

    def test_reverse_sorted_not_modified(self) -> None:
        """Test that reverse sorted input is not modified."""
        original = [5, 4, 3, 2, 1]
        original_copy = original.copy()
        result = bubble_sort(original)

        assert result == [1, 2, 3, 4, 5], "Should return sorted list"
        assert original == original_copy, "Original should remain [5, 4, 3, 2, 1]"


class TestBubbleSortPerformanceAndCorrectness:
    """Test suite for performance and correctness validation."""

    def test_correctness_vs_builtin_sorted(self) -> None:
        """Test that bubble sort produces same results as Python's sorted()."""
        test_cases = [
            [],
            [1],
            [2, 1],
            [1, 2, 3],
            [3, 2, 1],
            [5, 1, 4, 2, 8],
            [1, 3, 2, 5, 4, 7, 6],
            [64, 34, 25, 12, 22, 11, 90, 5, 77, 30],
            [3, -1, -4, 0, 2],
            [3.14, 2.71, 1.41, 0.5],
            [3, 2.5, 4, 1.5],
            [1, 1, 2, 2, 3, 3],
        ]

        for test_case in test_cases:
            result = bubble_sort(test_case)
            expected = sorted(test_case)
            assert result == expected, \
                f"bubble_sort({test_case}) should match sorted({test_case})"

    def test_large_list_100_elements(self) -> None:
        """Test bubble sort with list of 100 elements."""
        import random
        random.seed(42)  # For reproducible tests

        input_list = list(range(100))
        random.shuffle(input_list)

        result = bubble_sort(input_list)
        expected = list(range(100))

        assert result == expected, "Should correctly sort 100 elements"
        assert result is not input_list, "Should return new list"

    def test_large_list_1000_elements(self) -> None:
        """Test bubble sort with list of 1000 elements."""
        import random
        random.seed(42)  # For reproducible tests

        input_list = list(range(1000))
        random.shuffle(input_list)

        result = bubble_sort(input_list)
        expected = list(range(1000))

        assert result == expected, "Should correctly sort 1000 elements"
        assert result is not input_list, "Should return new list"

    def test_correctness_large_list_vs_sorted(self) -> None:
        """Test correctness with large list comparing to sorted()."""
        import random
        random.seed(123)

        input_list = [random.randint(-1000, 1000) for _ in range(500)]
        result = bubble_sort(input_list)
        expected = sorted(input_list)

        assert result == expected, "Should match Python's sorted() for 500 elements"

    def test_performance_already_sorted(self) -> None:
        """Test that bubble sort efficiently handles already sorted list."""
        # Should exit early with optimization
        input_list = list(range(100))
        result = bubble_sort(input_list)
        expected = list(range(100))

        assert result == expected, "Should handle already sorted list"
        assert result is not input_list, "Should return new list"

    def test_performance_reverse_sorted(self) -> None:
        """Test bubble sort with reverse sorted list."""
        input_list = list(range(100, 0, -1))
        result = bubble_sort(input_list)
        expected = list(range(1, 101))

        assert result == expected, "Should sort reverse ordered list"
