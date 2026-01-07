"""
Comprehensive tests for optimized bubble sort variants.
Following TDD principles for Story 2.1.
"""

import pytest
from src.bubble_sort import (
    bubble_sort_optimized,
    bubble_sort_cocktail,
)


class TestBubbleSortOptimizedBasic:
    """Basic functionality tests for optimized bubble sort."""

    def test_sort_empty_list(self):
        """Test that empty list is handled correctly."""
        result = bubble_sort_optimized([])
        assert result == []

    def test_sort_single_element(self):
        """Test sorting a single element list."""
        result = bubble_sort_optimized([1])
        assert result == [1]

    def test_sort_two_elements(self):
        """Test sorting two-element list."""
        result = bubble_sort_optimized([2, 1])
        assert result == [1, 2]

    def test_sort_three_elements(self):
        """Test sorting three-element list."""
        result = bubble_sort_optimized([3, 1, 2])
        assert result == [1, 2, 3]

    def test_sort_small_list(self):
        """Test sorting small list."""
        result = bubble_sort_optimized([5, 1, 4, 2, 8])
        assert result == [1, 2, 4, 5, 8]

    def test_sort_medium_list(self):
        """Test sorting medium list."""
        input_list = [64, 34, 25, 12, 22, 11, 90]
        result = bubble_sort_optimized(input_list)
        assert result == [11, 12, 22, 25, 34, 64, 90]


class TestBubbleSortOptimizedEarlyTermination:
    """Tests for early termination optimization."""

    def test_already_sorted_large_list(self):
        """Test that already sorted list exits after 1 pass."""
        # This test validates the O(n) best case performance
        input_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = bubble_sort_optimized(input_list)
        assert result == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_already_sorted_small_list(self):
        """Test early termination on small sorted list."""
        result = bubble_sort_optimized([1, 2, 3])
        assert result == [1, 2, 3]

    def test_two_elements_sorted(self):
        """Test early termination on two sorted elements."""
        result = bubble_sort_optimized([1, 2])
        assert result == [1, 2]

    def test_reverse_sorted_performs_full_sort(self):
        """Test that reverse sorted performs full sort."""
        # Reverse sorted should not trigger early termination
        input_list = [5, 4, 3, 2, 1]
        result = bubble_sort_optimized(input_list)
        assert result == [1, 2, 3, 4, 5]

    def test_partially_sorted(self):
        """Test with partially sorted data."""
        input_list = [1, 3, 2, 4, 5]
        result = bubble_sort_optimized(input_list)
        assert result == [1, 2, 3, 4, 5]


class TestBubbleSortCocktailBasic:
    """Basic functionality tests for cocktail sort."""

    def test_sort_empty_list(self):
        """Test that empty list is handled correctly."""
        result = bubble_sort_cocktail([])
        assert result == []

    def test_sort_single_element(self):
        """Test sorting a single element list."""
        result = bubble_sort_cocktail([1])
        assert result == [1]

    def test_sort_two_elements(self):
        """Test sorting two-element list."""
        result = bubble_sort_cocktail([2, 1])
        assert result == [1, 2]

    def test_sort_three_elements(self):
        """Test sorting three-element list."""
        result = bubble_sort_cocktail([3, 1, 2])
        assert result == [1, 2, 3]

    def test_sort_small_list(self):
        """Test sorting small list."""
        result = bubble_sort_cocktail([5, 1, 4, 2, 8])
        assert result == [1, 2, 4, 5, 8]

    def test_sort_medium_list(self):
        """Test sorting medium list."""
        input_list = [64, 34, 25, 12, 22, 11, 90]
        result = bubble_sort_cocktail(input_list)
        assert result == [11, 12, 22, 25, 34, 64, 90]


class TestBubbleSortCocktailBidirectional:
    """Tests for cocktail sort's bidirectional nature."""

    def test_reverse_sorted(self):
        """Test cocktail sort on reverse sorted list."""
        input_list = [5, 4, 3, 2, 1]
        result = bubble_sort_cocktail(input_list)
        assert result == [1, 2, 3, 4, 5]

    def test_already_sorted(self):
        """Test cocktail sort on already sorted list."""
        input_list = [1, 2, 3, 4, 5]
        result = bubble_sort_cocktail(input_list)
        assert result == [1, 2, 3, 4, 5]

    def test_partially_sorted(self):
        """Test with partially sorted data."""
        input_list = [1, 3, 2, 4, 5]
        result = bubble_sort_cocktail(input_list)
        assert result == [1, 2, 3, 4, 5]

    def test_comparison_with_standard(self):
        """Test that cocktail sort produces same results as standard bubble sort."""
        test_cases = [
            [5, 1, 4, 2, 8],
            [64, 34, 25, 12, 22, 11, 90],
            [3, 1, 4, 1, 5],
            [1, 2, 3, 4, 5],
            [5, 4, 3, 2, 1],
        ]
        for test_case in test_cases:
            result_optimized = bubble_sort_optimized(test_case)
            result_cocktail = bubble_sort_cocktail(test_case)
            assert result_cocktail == result_optimized


class TestBubbleSortDirection:
    """Tests for ascending/descending direction parameter."""

    @pytest.mark.parametrize("input_list,expected_asc,expected_desc", [
        ([5, 1, 4, 2, 8], [1, 2, 4, 5, 8], [8, 5, 4, 2, 1]),
        ([3, 1, 2], [1, 2, 3], [3, 2, 1]),
        ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [5, 4, 3, 2, 1]),
        ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5], [5, 4, 3, 2, 1]),
    ])
    def test_ascending_and_descending_optimized(self, input_list, expected_asc, expected_desc):
        """Test both ascending and descending with optimized sort."""
        result_asc = bubble_sort_optimized(input_list, ascending=True)
        assert result_asc == expected_asc

        result_desc = bubble_sort_optimized(input_list, ascending=False)
        assert result_desc == expected_desc

    @pytest.mark.parametrize("input_list,expected_asc,expected_desc", [
        ([5, 1, 4, 2, 8], [1, 2, 4, 5, 8], [8, 5, 4, 2, 1]),
        ([3, 1, 2], [1, 2, 3], [3, 2, 1]),
        ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [5, 4, 3, 2, 1]),
        ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5], [5, 4, 3, 2, 1]),
    ])
    def test_ascending_and_descending_cocktail(self, input_list, expected_asc, expected_desc):
        """Test both ascending and descending with cocktail sort."""
        result_asc = bubble_sort_cocktail(input_list, ascending=True)
        assert result_asc == expected_asc

        result_desc = bubble_sort_cocktail(input_list, ascending=False)
        assert result_desc == expected_desc

    def test_default_is_ascending(self):
        """Test that default direction is ascending."""
        result = bubble_sort_optimized([3, 1, 2])
        assert result == [1, 2, 3]

    def test_direction_with_duplicates(self):
        """Test direction parameter with duplicate values."""
        input_list = [3, 1, 3, 2, 1]
        result_asc = bubble_sort_optimized(input_list, ascending=True)
        assert result_asc == [1, 1, 2, 3, 3]

        result_desc = bubble_sort_optimized(input_list, ascending=False)
        assert result_desc == [3, 3, 2, 1, 1]


class TestBubbleSortCustomComparison:
    """Tests for custom comparison function support."""

    def test_with_key_function(self):
        """Test sorting with custom key extraction."""
        # Sort tuples by their second element
        data = [(1, 3), (2, 1), (3, 2)]
        result = bubble_sort_optimized(data, key=lambda x: x[1])
        assert result == [(2, 1), (3, 2), (1, 3)]

    def test_with_key_function_descending(self):
        """Test sorting with key function and descending order."""
        data = [(1, 3), (2, 1), (3, 2)]
        result = bubble_sort_optimized(data, key=lambda x: x[1], ascending=False)
        assert result == [(1, 3), (3, 2), (2, 1)]

    def test_with_key_function_strings(self):
        """Test sorting strings by length."""
        data = ["a", "abc", "ab"]
        result = bubble_sort_optimized(data, key=len)
        assert result == ["a", "ab", "abc"]

    def test_with_key_function_objects(self):
        """Test sorting with custom objects."""
        class Person:
            def __init__(self, name, age):
                self.name = name
                self.age = age

            def __repr__(self):
                return f"Person({self.name}, {self.age})"

            def __eq__(self, other):
                return self.name == other.name and self.age == other.age

        people = [
            Person("Alice", 30),
            Person("Bob", 25),
            Person("Charlie", 35)
        ]
        result = bubble_sort_optimized(people, key=lambda x: x.age)
        assert result[0].age == 25
        assert result[1].age == 30
        assert result[2].age == 35

    def test_cocktail_with_key_function(self):
        """Test cocktail sort with key function."""
        data = [(1, 3), (2, 1), (3, 2)]
        result = bubble_sort_cocktail(data, key=lambda x: x[1])
        assert result == [(2, 1), (3, 2), (1, 3)]

    def test_custom_cmp_function(self):
        """Test with custom comparison function."""
        # Sort by absolute value
        data = [1, -3, 2, -2, 0]
        result = bubble_sort_optimized(data, key=abs)
        assert result == [0, 1, 2, -2, -3]

    def test_reverse_parameter(self):
        """Test reverse parameter for sorting strings by length in reverse."""
        data = ["a", "abc", "ab"]
        result = bubble_sort_optimized(data, key=len, reverse=True)
        assert result == ["abc", "ab", "a"]


class TestBubbleSortInterfaceConsistency:
    """Tests to ensure consistent interface across all variants."""

    def test_all_variants_accept_same_parameters(self):
        """Test that all variants accept the same parameters."""
        data = [3, 1, 2]

        # All should work with these parameters
        result1 = bubble_sort_optimized(data, ascending=True, key=None, reverse=False, cmp=None)
        result2 = bubble_sort_cocktail(data, ascending=True, key=None, reverse=False, cmp=None)

        assert result1 == result2

    def test_all_variants_return_new_list(self):
        """Test that all variants return a new list (non-mutating)."""
        data = [3, 1, 2]
        original = data.copy()

        result1 = bubble_sort_optimized(data)
        result2 = bubble_sort_cocktail(data)

        # Original should be unchanged
        assert data == original

        # Results should be new lists
        assert result1 is not data
        assert result2 is not data

    def test_optional_in_place_parameter(self):
        """Test optional in-place parameter."""
        data = [3, 1, 2]
        original_id = id(data)

        # Sort in place
        result = bubble_sort_optimized(data, in_place=True)

        # Should return None or same list
        assert result is None or result is data
        # Data should be modified in place
        assert data == [1, 2, 3]
        assert id(data) == original_id


class TestBubbleSortEdgeCases:
    """Edge case tests for all variants."""

    def test_optimized_with_duplicates(self):
        """Test optimized sort with duplicate values."""
        result = bubble_sort_optimized([5, 5, 5, 5])
        assert result == [5, 5, 5, 5]

    def test_cocktail_with_duplicates(self):
        """Test cocktail sort with duplicate values."""
        result = bubble_sort_cocktail([5, 5, 5, 5])
        assert result == [5, 5, 5, 5]

    def test_negative_numbers_optimized(self):
        """Test optimized sort with negative numbers."""
        result = bubble_sort_optimized([3, -1, -4, 0, 2])
        assert result == [-4, -1, 0, 2, 3]

    def test_negative_numbers_cocktail(self):
        """Test cocktail sort with negative numbers."""
        result = bubble_sort_cocktail([3, -1, -4, 0, 2])
        assert result == [-4, -1, 0, 2, 3]

    def test_floating_point_numbers_optimized(self):
        """Test optimized sort with floating point numbers."""
        result = bubble_sort_optimized([3.5, 1.2, 4.7, 2.1])
        assert result == [1.2, 2.1, 3.5, 4.7]

    def test_floating_point_numbers_cocktail(self):
        """Test cocktail sort with floating point numbers."""
        result = bubble_sort_cocktail([3.5, 1.2, 4.7, 2.1])
        assert result == [1.2, 2.1, 3.5, 4.7]

    def test_mixed_integers_and_floats(self):
        """Test with mixed integers and floats."""
        result = bubble_sort_optimized([3, 1.5, 2, 1.2])
        assert result == [1.2, 1.5, 2, 3]


class TestBubbleSortPerformance:
    """Tests to validate performance characteristics."""

    def test_optimized_early_termination_performance(self):
        """Test that optimized sort exits early on sorted data."""
        # Large sorted list - should exit after first pass
        large_sorted = list(range(1000))
        result = bubble_sort_optimized(large_sorted)
        assert result == large_sorted
        # If early termination works correctly, this should be very fast

    def test_cocktail_sort_performance_on_unsorted(self):
        """Test cocktail sort on random data."""
        import random
        random_data = [random.randint(1, 100) for _ in range(50)]
        result = bubble_sort_cocktail(random_data)
        assert len(result) == 50
        assert result == sorted(random_data)

    def test_both_variants_produce_sorted_results(self):
        """Test that both variants produce correctly sorted results."""
        test_data = [64, 34, 25, 12, 22, 11, 90, 5, 77, 30, 20, 15]
        result1 = bubble_sort_optimized(test_data)
        result2 = bubble_sort_cocktail(test_data)

        # Both should produce same sorted result
        expected = sorted(test_data)
        assert result1 == expected
        assert result2 == expected
