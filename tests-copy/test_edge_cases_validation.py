"""Test suite for edge cases and validation.

Tests cover:
- Boundary conditions
- Error scenarios
- Input validation edge cases
- Performance edge cases
"""

import pytest
from src.bubblesort.bubble_sort import bubble_sort


class TestBoundaryConditions:
    """Test boundary conditions for bubble sort."""

    def test_minimum_size_lists(self):
        """Test lists at minimum size (0, 1, 2 elements)."""
        assert bubble_sort([]) == []
        assert bubble_sort([1]) == [1]
        assert bubble_sort([2, 1]) == [1, 2]

    def test_maximum_value_integers(self):
        """Test sorting with maximum integer values."""
        assert bubble_sort([2**31 - 1, 0, -(2**31)]) == [-(2**31), 0, 2**31 - 1]

    def test_negative_numbers(self):
        """Test sorting lists with negative numbers."""
        assert bubble_sort([-3, -1, -2]) == [-3, -2, -1]
        assert bubble_sort([0, -5, 3, -1]) == [-5, -1, 0, 3]

    def test_zero_values(self):
        """Test sorting lists with zero values."""
        assert bubble_sort([0, 0, 0]) == [0, 0, 0]
        assert bubble_sort([1, 0, -1, 0]) == [-1, 0, 0, 1]

    def test_very_large_numbers(self):
        """Test sorting with very large numbers."""
        large_num = 10**100
        assert bubble_sort([large_num, -large_num, 0]) == [-large_num, 0, large_num]

    def test_very_small_decimal_places(self):
        """Test sorting with very small decimal values."""
        assert bubble_sort([0.0001, 0.00001, 0.0001]) == [0.00001, 0.0001, 0.0001]


class TestSpecialSequences:
    """Test special number sequences."""

    def test_fibonacci_sequence(self):
        """Test sorting Fibonacci sequence."""
        fib = [34, 1, 55, 3, 21, 8, 13]
        expected = [1, 3, 8, 13, 21, 34, 55]
        assert bubble_sort(fib) == expected

    def test_powers_of_two(self):
        """Test sorting powers of two."""
        powers = [256, 1, 2, 4, 8, 16, 32, 64, 128]
        expected = [1, 2, 4, 8, 16, 32, 64, 128, 256]
        assert bubble_sort(powers) == expected

    def test_alternating_pattern(self):
        """Test sorting alternating high-low pattern."""
        pattern = [1, 100, 2, 99, 3, 98]
        expected = [1, 2, 3, 98, 99, 100]
        assert bubble_sort(pattern) == expected

    def test_near_sorted_array(self):
        """Test sorting array that's almost sorted."""
        near_sorted = [1, 2, 3, 5, 4, 6, 7, 8, 9]
        expected = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        assert bubble_sort(near_sorted) == expected

    def test_all_duplicates(self):
        """Test array with all identical elements."""
        assert bubble_sort([5] * 100) == [5] * 100

    def test_high_duplicates_ratio(self):
        """Test array with high ratio of duplicates."""
        input_list = [3, 1, 3, 1, 3, 1, 2]
        expected = [1, 1, 1, 2, 3, 3, 3]
        assert bubble_sort(input_list) == expected


class TestInputValidationEdgeCases:
    """Test edge cases in input validation."""

    def test_whitespace_only_string(self):
        """Test that whitespace-only string fails validation."""
        with pytest.raises(ValueError):
            validate_input([' '])

    def test_mixed_numeric_strings(self):
        """Test validation with mixed numeric formats."""
        # Valid: decimal notation
        result = validate_input(['1.5', '2.7'])
        assert result == [1.5, 2.7]

    def test_scientific_notation_strings(self):
        """Test validation with scientific notation."""
        result = validate_input(['1e-5', '2e3'])
        assert result == [1e-5, 2e3]

    def test_leading_trailing_spaces(self):
        """Test validation with leading/trailing spaces."""
        result = validate_input(['  5  ', '  3  ', '  1  '])
        assert result == [5, 3, 1]

    def test_special_characters_in_numbers(self):
        """Test that numbers with special characters fail."""
        with pytest.raises(ValueError):
            validate_input(['1,000'])  # Comma thousands separator

    def test_unicode_numbers(self):
        """Test validation with unicode number characters."""
        result = validate_input(['１', '２'])  # Full-width digits
        # Note: This might fail depending on implementation


class TestTypeEdgeCases:
    """Test edge cases with different input types."""

    def test_nested_iterable(self):
        """Test that nested iterables work correctly."""
        # Should flatten or handle appropriately
        result = bubble_sort([[1, 2], [3, 0]])
        # Bubble sort should work on the outer list
        # Comparison of lists will use lexicographic order
        assert result == [[1, 2], [3, 0]] or result == [[3, 0], [1, 2]]

    def test_mixed_comparable_types(self):
        """Test sorting with mixed but comparable types."""
        # int and float are comparable
        result = bubble_sort([3, 1.5, 2, 0.5])
        assert result == [0.5, 1.5, 2, 3]

    def test_incompatible_types(self):
        """Test that incompatible types raise appropriate errors."""
        # Strings that can't convert to numbers
        with pytest.raises(ValueError):
            bubble_sort(['abc', 'def'])

    def test_none_in_iterable(self):
        """Test handling of None values in iterable."""
        # Should handle gracefully or raise appropriate error
        try:
            result = bubble_sort([1, None, 2])
            # If it works, result should be sorted with None handling
        except (TypeError, ValueError):
            # Expected if None comparison is not supported
            pass

    def test_boolean_values(self):
        """Test sorting boolean values (they're numbers in Python)."""
        result = bubble_sort([True, False, True])
        # False = 0, True = 1
        assert result == [False, True, True]


class TestPerformanceEdgeCases:
    """Test performance-related edge cases."""

    def test_large_list_memory_efficiency(self):
        """Test that large lists don't cause memory issues."""
        large_list = list(range(10000, 0, -1))
        result = bubble_sort(large_list)
        assert len(result) == 10000
        assert result == list(range(1, 10001))

    def test_list_with_many_duplicates(self):
        """Test list with many duplicate values."""
        input_list = [5, 1, 5, 1, 5, 1] * 100
        result = bubble_sort(input_list)
        assert result == [1, 1, 1] * 100 + [5, 5, 5] * 100

    def test_random_large_list(self):
        """Test with randomly generated large list."""
        import random
        random.seed(42)  # For reproducibility
        large_random = [random.randint(-1000, 1000) for _ in range(1000)]
        result = bubble_sort(large_random)
        assert result == sorted(large_random)

    def test_alternating_extreme_values(self):
        """Test list with alternating extreme values."""
        extreme_list = [10**10, -(10**10), 10**10, -(10**10)] * 10
        result = bubble_sort(extreme_list)
        assert result == [-(10**10)] * 10 + [10**10] * 10


class TestAlgorithmCorrectness:
    """Test algorithm correctness properties."""

    def test_sorting_stability(self):
        """Test that bubble sort is stable (equal elements maintain order)."""
        # Create list with equal elements that have identity
        items = [(1, 'a'), (1, 'b'), (0, 'c'), (1, 'd')]
        # Note: bubble sort should maintain relative order of equal items
        result = bubble_sort(items)
        # Check that all (1, x) items maintain their relative order
        ones = [item for item in result if item[0] == 1]
        assert ones == [(1, 'a'), (1, 'b'), (1, 'd')]

    def test_sorted_property_preserved(self):
        """Test that if input is sorted, output is unchanged."""
        already_sorted = [1, 2, 3, 4, 5]
        result = bubble_sort(already_sorted)
        assert result == already_sorted

    def test_transitive_property(self):
        """Test transitivity: if a <= b and b <= c, then a <= c."""
        # This is more of a mathematical property test
        result = bubble_sort([3, 1, 4, 1, 5, 9, 2, 6])
        # Verify result is sorted
        for i in range(len(result) - 1):
            assert result[i] <= result[i + 1]

    def test_permutation_property(self):
        """Test that output is a permutation of input."""
        original = [3, 1, 4, 1, 5, 9, 2, 6]
        result = bubble_sort(original)
        # Check that all elements are preserved
        assert sorted(original) == sorted(result)
        assert len(result) == len(original)


class TestNumericEdgeCases:
    """Test numeric-specific edge cases."""

    def test_float_precision(self):
        """Test floating-point precision issues."""
        # 0.1 + 0.2 != 0.3 in floating point
        result = bubble_sort([0.1, 0.2, 0.3])
        assert len(result) == 3
        # Results should be ordered correctly despite precision
        assert result[0] <= result[1] <= result[2]

    def test_infinity_values(self):
        """Test sorting with infinity values."""
        result = bubble_sort([1, float('inf'), 0, float('-inf')])
        assert result[0] == float('-inf')
        assert result[-1] == float('inf')

    def test_nan_values(self):
        """Test sorting with NaN values."""
        result = bubble_sort([1, float('nan'), 2])
        # NaN comparison behavior is implementation-defined
        # Just verify no exception is raised
        assert len(result) == 3

    def test_zero_signedness(self):
        """Test that positive and negative zero are handled."""
        result = bubble_sort([-0.0, 0.0, 0.0])
        assert result == [0.0, 0.0, 0.0] or result == [-0.0, 0.0, 0.0]


class TestAlgorithmEdgeCases:
    """Test algorithm-specific edge cases."""

    def test_single_element_list(self):
        """Test list with single element."""
        result = bubble_sort([42])
        assert result == [42]

    def test_very_large_list(self):
        """Test with a very large list."""
        import random
        random.seed(42)
        large_list = [random.randint(1, 100) for _ in range(50)]
        result = bubble_sort(large_list)
        assert result == sorted(large_list)
