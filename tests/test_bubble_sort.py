"""
Comprehensive unit tests for bubble sort algorithm implementation.
Following TDD principles with complete coverage.
"""

import pytest
from src.bubble_sort import bubble_sort


class TestBubbleSortBasic:
    """Basic functionality tests for bubble sort."""

    def test_sort_empty_list(self):
        """Test that empty list is handled correctly."""
        result = bubble_sort([])
        assert result == []

    def test_sort_single_element(self):
        """Test sorting a single element list."""
        result = bubble_sort([1])
        assert result == [1]

    def test_sort_two_elements_sorted(self):
        """Test sorting already sorted two-element list."""
        result = bubble_sort([1, 2])
        assert result == [1, 2]

    def test_sort_two_elements_unsorted(self):
        """Test sorting unsorted two-element list."""
        result = bubble_sort([2, 1])
        assert result == [1, 2]

    def test_sort_three_elements_random(self):
        """Test sorting three-element list with random order."""
        result = bubble_sort([3, 1, 2])
        assert result == [1, 2, 3]

    def test_sort_three_elements_reverse(self):
        """Test sorting three-element list in reverse order."""
        result = bubble_sort([3, 2, 1])
        assert result == [1, 2, 3]

    def test_sort_small_list(self):
        """Test sorting small list with multiple elements."""
        result = bubble_sort([5, 1, 4, 2, 8])
        assert result == [1, 2, 4, 5, 8]

    def test_sort_medium_list(self):
        """Test sorting medium-sized list."""
        input_list = [64, 34, 25, 12, 22, 11, 90]
        result = bubble_sort(input_list)
        assert result == [11, 12, 22, 25, 34, 64, 90]

    def test_sort_large_list(self):
        """Test sorting larger list."""
        input_list = [5, 1, 4, 2, 8, 0, 2, 6, 9, 1]
        result = bubble_sort(input_list)
        assert result == [0, 1, 1, 2, 2, 4, 5, 6, 8, 9]


class TestBubbleSortWithDuplicates:
    """Tests for handling duplicate values."""

    def test_all_duplicates(self):
        """Test sorting list with all identical elements."""
        result = bubble_sort([5, 5, 5, 5])
        assert result == [5, 5, 5, 5]

    def test_multiple_duplicates(self):
        """Test sorting list with multiple duplicate values."""
        result = bubble_sort([3, 1, 3, 2, 1, 3])
        assert result == [1, 1, 2, 3, 3, 3]

    def test_consecutive_duplicates(self):
        """Test sorting list with consecutive duplicate values."""
        result = bubble_sort([2, 2, 1, 1])
        assert result == [1, 1, 2, 2]


class TestBubbleSortEdgeCases:
    """Edge case tests."""

    def test_negative_numbers(self):
        """Test sorting list with negative numbers."""
        result = bubble_sort([3, -1, -4, 0, 2])
        assert result == [-4, -1, 0, 2, 3]

    def test_all_negative(self):
        """Test sorting list with all negative numbers."""
        result = bubble_sort([-3, -1, -4, -2])
        assert result == [-4, -3, -2, -1]

    def test_floating_point_numbers(self):
        """Test sorting list with floating point numbers."""
        result = bubble_sort([3.5, 1.2, 4.7, 2.1])
        assert result == [1.2, 2.1, 3.5, 4.7]

    def test_mixed_integers_and_floats(self):
        """Test sorting list with mixed integers and floats."""
        result = bubble_sort([3, 1.5, 2, 1.2])
        assert result == [1.2, 1.5, 2, 3]

    def test_already_sorted(self):
        """Test that already sorted list remains unchanged."""
        input_list = [1, 2, 3, 4, 5]
        result = bubble_sort(input_list)
        assert result == [1, 2, 3, 4, 5]

    def test_reverse_sorted(self):
        """Test sorting reverse-ordered list."""
        input_list = [5, 4, 3, 2, 1]
        result = bubble_sort(input_list)
        assert result == [1, 2, 3, 4, 5]


class TestBubbleSortImmutability:
    """Test that original list is not modified."""

    def test_original_list_unchanged(self):
        """Verify original list is not modified during sorting."""
        original = [3, 1, 2]
        original_copy = original.copy()
        bubble_sort(original)
        assert original == original_copy

    def test_returns_new_list(self):
        """Verify function returns a new list, not modifies input."""
        original = [3, 1, 2]
        result = bubble_sort(original)
        assert result is not original
        assert result != original


class TestBubbleSortTypeSafety:
    """Type safety and error handling tests."""

    def test_with_none_raises_error(self):
        """Test that passing None raises appropriate error."""
        with pytest.raises(TypeError, match="Input cannot be None"):
            bubble_sort(None)

    def test_with_integer_raises_error(self):
        """Test that passing non-iterable (integer) raises TypeError."""
        with pytest.raises(TypeError, match="Input must be an iterable"):
            bubble_sort(42)

    def test_with_string_raises_error(self):
        """Test that passing string (iterable but non-numeric) raises ValueError."""
        # String is iterable (contains characters) but not numeric
        with pytest.raises(ValueError, match="All elements must be numeric"):
            bubble_sort("abc")

    def test_with_mixed_types_raises_error(self):
        """Test that mixed types raise appropriate error."""
        with pytest.raises(ValueError, match="All elements must be numeric"):
            bubble_sort([1, "2", 3])


class TestBubbleSortParameterized:
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
        result = bubble_sort(input_data)
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
            bubble_sort(input_data)


class TestBubbleSortComplexity:
    """Tests related to algorithm complexity."""

    def test_compares_elements_correctly(self):
        """Test that bubble sort performs correct comparisons."""
        # This is a basic test to ensure algorithm correctness
        test_cases = [
            ([5, 1, 4, 2, 8], [1, 2, 4, 5, 8]),
            ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
            ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
        ]
        for input_list, expected in test_cases:
            result = bubble_sort(input_list.copy())
            assert result == expected


class TestBubbleSortParameterized:
    """Parameterized tests for multiple input scenarios using pytest.mark.parametrize."""

    @pytest.mark.parametrize("input_list,expected", [
        # Basic scenarios
        ([], []),
        ([1], [1]),
        ([2, 1], [1, 2]),
        ([1, 2], [1, 2]),
        ([3, 2, 1], [1, 2, 3]),
        ([2, 3, 1], [1, 2, 3]),
        ([1, 3, 2], [1, 2, 3]),
        # Multiple elements
        ([5, 1, 4, 2, 8], [1, 2, 4, 5, 8]),
        ([64, 34, 25, 12, 22, 11, 90], [11, 12, 22, 25, 34, 64, 90]),
        ([5, 1, 4, 2, 8, 0, 2, 6, 9, 1], [0, 1, 1, 2, 2, 4, 5, 6, 8, 9]),
    ])
    def test_basic_sorting_parametrized(self, input_list, expected):
        """Test basic sorting scenarios using parameterized tests."""
        result = bubble_sort(input_list)
        assert result == expected

    @pytest.mark.parametrize("input_list,expected", [
        # Already sorted
        ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
        ([1, 2, 3], [1, 2, 3]),
        # Reverse sorted
        ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
        ([3, 2, 1], [1, 2, 3]),
        # Random order
        ([3, 1, 2], [1, 2, 3]),
        ([5, 2, 8, 1, 9], [1, 2, 5, 8, 9]),
    ])
    def test_sorting_order_parametrized(self, input_list, expected):
        """Test different sorting orders using parameterized tests."""
        result = bubble_sort(input_list)
        assert result == expected

    @pytest.mark.parametrize("input_list,expected", [
        # Negative numbers
        ([3, -1, -4, 0, 2], [-4, -1, 0, 2, 3]),
        ([-3, -1, -4, -2], [-4, -3, -2, -1]),
        # Floating point numbers
        ([3.5, 1.2, 4.7, 2.1], [1.2, 2.1, 3.5, 4.7]),
        ([2.5, 1.5, 3.5], [1.5, 2.5, 3.5]),
        # Mixed integers and floats
        ([3, 1.5, 2, 1.2], [1.2, 1.5, 2, 3]),
        ([5, 2.5, 7, 1.1], [1.1, 2.5, 5, 7]),
    ])
    def test_numeric_types_parametrized(self, input_list, expected):
        """Test different numeric types using parameterized tests."""
        result = bubble_sort(input_list)
        assert result == expected

    @pytest.mark.parametrize("input_list,expected", [
        # Duplicate elements
        ([5, 5, 5, 5], [5, 5, 5, 5]),
        ([3, 1, 3, 2, 1, 3], [1, 1, 2, 3, 3, 3]),
        ([2, 2, 1, 1], [1, 1, 2, 2]),
        ([1, 2, 2, 1], [1, 1, 2, 2]),
        ([4, 1, 4, 2, 4], [1, 2, 4, 4, 4]),
    ])
    def test_duplicates_parametrized(self, input_list, expected):
        """Test handling of duplicate values using parameterized tests."""
        result = bubble_sort(input_list)
        assert result == expected

    @pytest.mark.parametrize("input_data,expected_error,error_match", [
        (None, TypeError, "Input cannot be None"),
        (42, TypeError, "Input must be an iterable"),
        ("abc", ValueError, "All elements must be numeric"),
        ([1, "2", 3], ValueError, "All elements must be numeric"),
        ([1.5, "text", 2], ValueError, "All elements must be numeric"),
    ])
    def test_error_handling_parametrized(self, input_data, expected_error, error_match):
        """Test error handling for invalid inputs using parameterized tests."""
        with pytest.raises(expected_error, match=error_match):
            bubble_sort(input_data)

    @pytest.mark.parametrize("input_list", [
        [3, 1, 2],
        [5, 4, 3, 2, 1],
        [1, 2, 3, 4, 5],
        [10, -5, 3.14, 0, -2.5],
    ])
    def test_immutability_parametrized(self, input_list):
        """Test that original list is not modified using parameterized tests."""
        original = input_list.copy()
        result = bubble_sort(input_list)
        # Verify input list is unchanged
        assert input_list == original
        # Verify function returns a new list
        assert result is not input_list
