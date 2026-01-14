"""Test suite for bubble sort algorithm implementation.

Tests cover:
- Basic sorting functionality
- Edge cases (empty lists, single elements, duplicates)
- Type validation
- Performance characteristics
"""

import pytest
from src.bubblesort.bubble_sort import bubble_sort


class TestBubbleSortBasic:
    """Test basic bubble sort functionality."""

    def test_sort_integers_ascending(self):
        """Test sorting integers in ascending order."""
        assert bubble_sort([3, 1, 2]) == [1, 2, 3]
        assert bubble_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]
        assert bubble_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

    def test_sort_floats(self):
        """Test sorting floats."""
        assert bubble_sort([3.5, 1.2, 2.8]) == [1.2, 2.8, 3.5]
        assert bubble_sort([1.1, 3.3, 2.2]) == [1.1, 2.2, 3.3]

    def test_sort_mixed_ints_and_floats(self):
        """Test sorting mixed integers and floats."""
        result = bubble_sort([3, 1.5, 2, 0.5])
        assert result == [0.5, 1.5, 2, 3]

    def test_sort_reverse_order(self):
        """Test sorting reverse-ordered list."""
        assert bubble_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]
        assert bubble_sort([10, 8, 6, 4, 2]) == [2, 4, 6, 8, 10]


class TestBubbleSortEdgeCases:
    """Test edge cases for bubble sort."""

    def test_empty_list(self):
        """Test sorting empty list."""
        assert bubble_sort([]) == []

    def test_single_element(self):
        """Test sorting list with single element."""
        assert bubble_sort([42]) == [42]
        assert bubble_sort([3.14]) == [3.14]

    def test_two_elements(self):
        """Test sorting list with two elements."""
        assert bubble_sort([2, 1]) == [1, 2]
        assert bubble_sort([1, 2]) == [1, 2]

    def test_all_same_elements(self):
        """Test sorting list with all identical elements."""
        assert bubble_sort([1, 1, 1, 1]) == [1, 1, 1, 1]
        assert bubble_sort([2.5, 2.5, 2.5]) == [2.5, 2.5, 2.5]

    def test_duplicates(self):
        """Test sorting list with duplicate values."""
        assert bubble_sort([3, 1, 2, 1, 3]) == [1, 1, 2, 3, 3]
        assert bubble_sort([5, 5, 1, 5, 1, 1]) == [1, 1, 1, 5, 5, 5]

    def test_already_sorted(self):
        """Test that already sorted list remains sorted."""
        assert bubble_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]
        assert bubble_sort([1, 1, 2, 2, 3, 3]) == [1, 1, 2, 2, 3, 3]


class TestBubbleSortInputValidation:
    """Test input validation for bubble sort."""

    def test_none_input_raises_type_error(self):
        """Test that None input raises TypeError."""
        with pytest.raises(TypeError, match="Input cannot be None"):
            bubble_sort(None)

    def test_non_iterable_raises_type_error(self):
        """Test that non-iterable input raises TypeError."""
        with pytest.raises(TypeError, match="Input must be iterable"):
            bubble_sort(42)
        with pytest.raises(TypeError, match="Input must be iterable"):
            bubble_sort(3.14)

    def test_generator_input(self):
        """Test that generator input works correctly."""
        result = bubble_sort(x for x in [3, 1, 2])
        assert result == [1, 2, 3]

    def test_tuple_input(self):
        """Test that tuple input works correctly."""
        assert bubble_sort((3, 1, 2)) == [1, 2, 3]
        assert bubble_sort((5, 4, 3)) == [3, 4, 5]

    def test_range_input(self):
        """Test that range input works correctly."""
        result = bubble_sort(range(5, 0, -1))
        assert result == [1, 2, 3, 4, 5]


class TestBubbleSortReturnType:
    """Test return type of bubble sort."""

    def test_returns_list(self):
        """Test that bubble sort returns a list."""
        result = bubble_sort([3, 1, 2])
        assert isinstance(result, list)

    def test_returns_new_list(self):
        """Test that bubble sort returns a new list (doesn't modify input)."""
        input_list = [3, 1, 2]
        original = input_list.copy()
        result = bubble_sort(input_list)
        assert input_list == original
        assert result != input_list


class TestBubbleSortLargeLists:
    """Test bubble sort with larger lists."""

    def test_large_list(self):
        """Test sorting a large list."""
        import random
        large_list = [random.randint(1, 1000) for _ in range(100)]
        sorted_list = bubble_sort(large_list)
        assert sorted_list == sorted(large_list)

    def test_worst_case_reverse_sorted(self):
        """Test worst case scenario (reverse sorted list)."""
        reverse_list = list(range(100, 0, -1))
        sorted_list = bubble_sort(reverse_list)
        assert sorted_list == list(range(1, 101))


class TestBubbleSortTypeHints:
    """Test that bubble sort has proper type hints."""

    def test_function_has_type_hints(self):
        """Test that bubble_sort function has type hints."""
        import inspect
        sig = inspect.signature(bubble_sort)
        assert sig.return_annotation is not None
        assert 'data' in sig.parameters
        assert sig.parameters['data'].annotation != inspect.Parameter.empty


class TestBubbleSortDocstring:
    """Test that bubble sort has proper documentation."""

    def test_function_has_docstring(self):
        """Test that bubble_sort function has a docstring."""
        assert bubble_sort.__doc__ is not None
        assert "bubble sort" in bubble_sort.__doc__.lower()
        assert "Args:" in bubble_sort.__doc__
        assert "Returns:" in bubble_sort.__doc__
        assert "Examples:" in bubble_sort.__doc__
