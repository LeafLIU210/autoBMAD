"""
Comprehensive test suite for bubble_sort function.

Tests all acceptance criteria including edge cases, error conditions,
and function purity.
"""

import pytest

from src.bubblesort import bubble_sort


class TestBubbleSortBasic:
    """Test basic sorting functionality."""

    def test_empty_list(self):
        """Empty list returns empty list."""
        assert bubble_sort([]) == []

    def test_single_element(self):
        """Single element list returns same list."""
        assert bubble_sort([42]) == [42]
        assert bubble_sort([-5]) == [-5]
        assert bubble_sort([0]) == [0]

    def test_two_elements_sorted(self):
        """Two element list sorted correctly."""
        assert bubble_sort([2, 1]) == [1, 2]
        assert bubble_sort([1, 2]) == [1, 2]

    def test_multiple_elements(self):
        """Multiple elements sorted in ascending order."""
        assert bubble_sort([5, 1, 4, 2, 8]) == [1, 2, 4, 5, 8]
        assert bubble_sort([10, 7, 8, 9, 1, 5]) == [1, 5, 7, 8, 9, 10]
        assert bubble_sort([3, 3, 2, 1, 2]) == [1, 2, 2, 3, 3]


class TestBubbleSortEdgeCases:
    """Test edge cases and special scenarios."""

    def test_already_sorted(self):
        """Already sorted list remains sorted."""
        assert bubble_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]
        assert bubble_sort([1, 1, 1]) == [1, 1, 1]

    def test_reverse_sorted(self):
        """Reverse sorted list becomes sorted."""
        assert bubble_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]
        assert bubble_sort([10, 9, 8, 7]) == [7, 8, 9, 10]

    def test_with_duplicates(self):
        """List with duplicates sorted correctly."""
        assert bubble_sort([5, 1, 5, 1, 5]) == [1, 1, 5, 5, 5]
        assert bubble_sort([3, 3, 3]) == [3, 3, 3]

    def test_with_negatives(self):
        """List with negative numbers sorted correctly."""
        assert bubble_sort([5, -1, 3, -10]) == [-10, -1, 3, 5]
        assert bubble_sort([-5, -1, -3]) == [-5, -3, -1]

    def test_with_floats(self):
        """List with floats sorted correctly."""
        assert bubble_sort([3.5, 2.1, 4.8]) == [2.1, 3.5, 4.8]
        assert bubble_sort([1.1, 1.0, 2.9]) == [1.0, 1.1, 2.9]
        assert bubble_sort([5.5, 5.0, 6.0]) == [5.0, 5.5, 6.0]

    def test_mixed_ints_and_floats(self):
        """List with mixed integers and floats sorted correctly."""
        assert bubble_sort([5, 2.5, 3, 1.1]) == [1.1, 2.5, 3, 5]


class TestBubbleSortErrorHandling:
    """Test error handling and validation."""

    def test_none_input(self):
        """None input raises TypeError."""
        with pytest.raises(TypeError, match="Input cannot be None"):
            bubble_sort(None)

    def test_non_iterable_input(self):
        """Non-iterable input raises TypeError."""
        with pytest.raises(TypeError, match="Input must be iterable"):
            bubble_sort(123)

        with pytest.raises(TypeError, match="Input must be iterable"):
            bubble_sort(45.67)


class TestBubbleSortFunctionPurity:
    """Test that function is pure (no side effects)."""

    def test_original_not_modified(self):
        """Original input list is not modified."""
        original = [5, 2, 8, 1]
        result = bubble_sort(original)

        # Original should be unchanged
        assert original == [5, 2, 8, 1]
        assert result == [1, 2, 5, 8]

    def test_returns_new_list(self):
        """Function returns a new list instance."""
        input_list = [3, 1, 2]
        result = bubble_sort(input_list)

        # Should be a different list object
        assert result is not input_list
        assert result == [1, 2, 3]

    def test_multiple_calls_independent(self):
        """Multiple calls with same input are independent."""
        input_list = [2, 1, 3]
        result1 = bubble_sort(input_list)
        result2 = bubble_sort(input_list)

        # Both should be equal but different instances
        assert result1 == result2 == [1, 2, 3]
        assert result1 is not result2
        assert result1 is not input_list
        assert result2 is not input_list


class TestBubbleSortComplex:
    """Test more complex scenarios."""

    def test_large_list(self):
        """Handle large lists efficiently."""
        large_list = list(range(100, 0, -1))
        sorted_list = bubble_sort(large_list)
        assert sorted_list == list(range(1, 101))

    def test_all_same_elements(self):
        """List with all identical elements."""
        assert bubble_sort([7] * 10) == [7] * 10

    def test_very_small_numbers(self):
        """List with very small numbers."""
        assert bubble_sort([0.0001, 0.00001, 0.001]) == [0.00001, 0.0001, 0.001]

    def test_large_magnitude_numbers(self):
        """List with large magnitude numbers."""
        assert bubble_sort([1e10, 1e5, 1e15]) == [1e5, 1e10, 1e15]
