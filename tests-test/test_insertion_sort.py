"""
Comprehensive unit tests for insertion sort algorithm implementation.
Following TDD principles with complete coverage.
"""

import pytest
from src.insertion_sort import insertion_sort


class TestInsertionSortBasic:
    """Basic functionality tests for insertion sort."""

    def test_sort_empty_list(self):
        """Test that empty list is handled correctly."""
        result = insertion_sort([])
        assert result == []

    def test_sort_single_element(self):
        """Test sorting a single element list."""
        result = insertion_sort([1])
        assert result == [1]

    def test_sort_two_elements_sorted(self):
        """Test sorting already sorted two-element list."""
        result = insertion_sort([1, 2])
        assert result == [1, 2]

    def test_sort_two_elements_unsorted(self):
        """Test sorting unsorted two-element list."""
        result = insertion_sort([2, 1])
        assert result == [1, 2]

    def test_sort_three_elements_random(self):
        """Test sorting three-element list with random order."""
        result = insertion_sort([3, 1, 2])
        assert result == [1, 2, 3]

    def test_sort_three_elements_reverse(self):
        """Test sorting three-element list in reverse order."""
        result = insertion_sort([3, 2, 1])
        assert result == [1, 2, 3]

    def test_sort_small_list(self):
        """Test sorting small list with multiple elements."""
        result = insertion_sort([5, 1, 4, 2, 8])
        assert result == [1, 2, 4, 5, 8]

    def test_sort_medium_list(self):
        """Test sorting medium-sized list."""
        input_list = [64, 34, 25, 12, 22, 11, 90]
        result = insertion_sort(input_list)
        assert result == [11, 12, 22, 25, 34, 64, 90]

    def test_sort_large_list(self):
        """Test sorting larger list."""
        input_list = [5, 1, 4, 2, 8, 0, 2, 6, 9, 1]
        result = insertion_sort(input_list)
        assert result == [0, 1, 1, 2, 2, 4, 5, 6, 8, 9]


class TestInsertionSortWithDuplicates:
    """Tests for handling duplicate values."""

    def test_all_duplicates(self):
        """Test sorting list with all identical elements."""
        result = insertion_sort([5, 5, 5, 5])
        assert result == [5, 5, 5, 5]

    def test_multiple_duplicates(self):
        """Test sorting list with multiple duplicate values."""
        result = insertion_sort([3, 1, 3, 2, 1, 3])
        assert result == [1, 1, 2, 3, 3, 3]

    def test_consecutive_duplicates(self):
        """Test sorting list with consecutive duplicate values."""
        result = insertion_sort([2, 2, 1, 1])
        assert result == [1, 1, 2, 2]


class TestInsertionSortEdgeCases:
    """Edge case tests."""

    def test_negative_numbers(self):
        """Test sorting list with negative numbers."""
        result = insertion_sort([3, -1, -4, 0, 2])
        assert result == [-4, -1, 0, 2, 3]

    def test_all_negative(self):
        """Test sorting list with all negative numbers."""
        result = insertion_sort([-3, -1, -4, -2])
        assert result == [-4, -3, -2, -1]

    def test_floating_point_numbers(self):
        """Test sorting list with floating point numbers."""
        result = insertion_sort([3.5, 1.2, 4.7, 2.1])
        assert result == [1.2, 2.1, 3.5, 4.7]

    def test_mixed_integers_and_floats(self):
        """Test sorting list with mixed integers and floats."""
        result = insertion_sort([3, 1.5, 2, 1.2])
        assert result == [1.2, 1.5, 2, 3]

    def test_already_sorted(self):
        """Test that already sorted list remains unchanged."""
        input_list = [1, 2, 3, 4, 5]
        result = insertion_sort(input_list)
        assert result == [1, 2, 3, 4, 5]

    def test_reverse_sorted(self):
        """Test sorting reverse-ordered list."""
        input_list = [5, 4, 3, 2, 1]
        result = insertion_sort(input_list)
        assert result == [1, 2, 3, 4, 5]


class TestInsertionSortImmutability:
    """Test that original list is not modified."""

    def test_original_list_unchanged(self):
        """Verify original list is not modified during sorting."""
        original = [3, 1, 2]
        original_copy = original.copy()
        insertion_sort(original)
        assert original == original_copy

    def test_returns_new_list(self):
        """Verify function returns a new list, not modifies input."""
        original = [3, 1, 2]
        result = insertion_sort(original)
        assert result is not original
        assert result != original


class TestInsertionSortTypeSafety:
    """Type safety and error handling tests."""

    def test_with_none_raises_error(self):
        """Test that passing None raises appropriate error."""
        with pytest.raises(TypeError, match="Input cannot be None"):
            insertion_sort(None)

    def test_with_integer_raises_error(self):
        """Test that passing non-iterable (integer) raises TypeError."""
        with pytest.raises(TypeError, match="Input must be an iterable"):
            insertion_sort(42)

    def test_with_string_raises_error(self):
        """Test that passing string (iterable but non-numeric) raises ValueError."""
        # String is iterable (contains characters) but not numeric
        with pytest.raises(ValueError, match="All elements must be numeric"):
            insertion_sort("abc")

    def test_with_mixed_types_raises_error(self):
        """Test that mixed types raise appropriate error."""
        with pytest.raises(ValueError, match="All elements must be numeric"):
            insertion_sort([1, "2", 3])


class TestInsertionSortParameterized:
    """Parameterized tests for comprehensive coverage."""

    @pytest.mark.parametrize("input_data,expected", [
        # Basic scenarios
        ([], []),
        ([1], [1]),
        ([2, 1], [1, 2]),
        ([1, 2], [1, 2]),
        # Already sorted
        ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
        # Reverse sorted
        ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
        # Random order
        ([3, 1, 4, 1, 5], [1, 1, 3, 4, 5]),
        ([5, 1, 4, 2, 8], [1, 2, 4, 5, 8]),
        # Duplicates
        ([5, 5, 5, 5], [5, 5, 5, 5]),
        ([3, 1, 3, 2, 1, 3], [1, 1, 2, 3, 3, 3]),
        ([2, 2, 1, 1], [1, 1, 2, 2]),
        # Negative numbers
        ([3, -1, -4, 0, 2], [-4, -1, 0, 2, 3]),
        ([-3, -1, -4, -2], [-4, -3, -2, -1]),
        # Floats
        ([3.5, 1.2, 4.7, 2.1], [1.2, 2.1, 3.5, 4.7]),
        # Mixed integers and floats
        ([3, 1.5, 2, 1.2], [1.2, 1.5, 2, 3]),
        # Very large numbers
        ([1e10, -1e10, 5e9, -5e9], [-1e10, -5e9, 5e9, 1e10]),
        # Medium sized list
        ([64, 34, 25, 12, 22, 11, 90], [11, 12, 22, 25, 34, 64, 90]),
    ])
    def test_sorting_scenarios(self, input_data, expected):
        """Test various sorting scenarios using parameterized tests."""
        result = insertion_sort(input_data)
        assert result == expected

    @pytest.mark.parametrize("input_data,error_type,error_match", [
        (None, TypeError, "Input cannot be None"),
        (42, TypeError, "Input must be an iterable"),
        ("abc", ValueError, "All elements must be numeric"),
        ([1, "2", 3], ValueError, "All elements must be numeric"),
        ([1, None, 3], ValueError, "All elements must be numeric"),
    ])
    def test_error_handling(self, input_data, error_type, error_match):
        """Test error handling for invalid inputs using parameterized tests."""
        with pytest.raises(error_type, match=error_match):
            insertion_sort(input_data)


class TestInsertionSortComplexity:
    """Tests related to algorithm complexity."""

    def test_compares_elements_correctly(self):
        """Test that insertion sort performs correct comparisons."""
        # This is a basic test to ensure algorithm correctness
        test_cases = [
            ([5, 1, 4, 2, 8], [1, 2, 4, 5, 8]),
            ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
            ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
        ]
        for input_list, expected in test_cases:
            result = insertion_sort(input_list.copy())
            assert result == expected

    def test_best_case_already_sorted(self):
        """Test best case - insertion sort is efficient on already sorted lists."""
        input_list = list(range(100))
        result = insertion_sort(input_list)
        assert result == input_list
        # Insertion sort performs O(n) comparisons in best case (already sorted)

    def test_worst_case_reverse_sorted(self):
        """Test worst case - reverse sorted takes O(n²)."""
        input_list = list(range(100, 0, -1))
        result = insertion_sort(input_list)
        assert result == list(range(1, 101))
        # Insertion sort performs O(n²) comparisons in worst case (reverse sorted)


class TestInsertionSortInterface:
    """Test interface consistency with bubble sort."""

    def test_interface_matches_bubble_sort(self):
        """Verify insertion sort has same interface as bubble sort."""
        from src.bubble_sort import bubble_sort

        # Both should accept same inputs
        test_data = [5, 1, 4, 2, 8]
        bubble_result = bubble_sort(test_data)
        insertion_result = insertion_sort(test_data)

        # Both should produce same output
        assert bubble_result == insertion_result

    def test_both_alter_return_new_lists(self):
        """Verify both algorithms return new lists."""
        from src.bubble_sort import bubble_sort

        test_data = [3, 1, 2]
        original = test_data.copy()

        bubble_result = bubble_sort(test_data)
        insertion_result = insertion_sort(test_data)

        # Original should be unchanged
        assert test_data == original

        # Both should return new lists
        assert bubble_result is not test_data
        assert insertion_result is not test_data
