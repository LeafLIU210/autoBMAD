"""Property-based tests for bubble sort using hypothesis.

This module implements property-based testing to verify bubble sort behavior
across a wide range of inputs, ensuring robustness and catching edge cases
that traditional example-based tests might miss.
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from typing import List, Union


class TestBubbleSortProperties:
    """Property-based tests for bubble sort algorithm."""

    @given(st.lists(st.integers()))
    @settings(max_examples=100)
    def test_sorting_result_is_sorted(self, lst):
        """Property: The result of sorting must be in ascending order."""
        from src.bubblesort import bubble_sort

        result = bubble_sort(lst)
        # Check that result is sorted
        for i in range(len(result) - 1):
            assert result[i] <= result[i + 1], f"List not sorted at index {i}: {result}"

    @given(st.lists(st.integers()))
    @settings(max_examples=100)
    def test_sorting_result_is_permutation(self, lst):
        """Property: The result must contain the same elements as input (permutation)."""
        from src.bubblesort import bubble_sort

        result = bubble_sort(lst)
        # Check that result is a permutation of input
        assert sorted(lst) == sorted(result), "Result is not a permutation of input"

    @given(st.lists(st.integers()))
    @settings(max_examples=100)
    def test_sorting_result_has_same_length(self, lst):
        """Property: The result must have the same length as input."""
        from src.bubblesort import bubble_sort

        result = bubble_sort(lst)
        assert len(result) == len(lst), "Result has different length than input"

    @given(st.lists(st.integers()))
    @settings(max_examples=100)
    def test_idempotence(self, lst):
        """Property: Sorting an already sorted list should return the same result."""
        from src.bubblesort import bubble_sort

        result1 = bubble_sort(lst)
        result2 = bubble_sort(result1)
        assert result1 == result2, "Sorting is not idempotent"

    @given(st.lists(st.integers()))
    @settings(max_examples=100)
    def test_stability_preserved(self, lst):
        """Property: The sort should be stable (equal elements maintain relative order)."""
        from src.bubblesort import bubble_sort

        # Create list with equal elements
        indexed_list = [(x, i) for i, x in enumerate(lst)]
        result = bubble_sort(indexed_list)

        # Check stability: equal elements should maintain original order
        for i in range(len(result) - 1):
            if result[i][0] == result[i + 1][0]:
                assert result[i][1] < result[i + 1][1], "Sort is not stable"

    @given(st.lists(st.floats(allow_nan=False, allow_infinity=False)))
    @settings(max_examples=50)
    def test_float_sorting_properties(self, lst):
        """Property: Sorting floats should satisfy the same properties."""
        from src.bubblesort import bubble_sort

        result = bubble_sort(lst)

        # Result is sorted
        for i in range(len(result) - 1):
            assert result[i] <= result[i + 1], "Float list not sorted"

        # Result is permutation
        assert sorted(lst) == sorted(result), "Float result is not a permutation"

    @given(st.lists(st.integers(min_value=-1000, max_value=1000)))
    @settings(max_examples=100)
    def test_sorting_preserves_min_max(self, lst):
        """Property: Sorting preserves minimum and maximum values."""
        from src.bubblesort import bubble_sort

        if len(lst) > 0:
            result = bubble_sort(lst)
            assert min(result) == min(lst), "Minimum value not preserved"
            assert max(result) == max(lst), "Maximum value not preserved"

    @given(st.lists(st.integers()))
    @settings(max_examples=100)
    def test_original_list_not_modified(self, lst):
        """Property: The original list should never be modified."""
        from src.bubblesort import bubble_sort

        original = lst.copy()
        result = bubble_sort(lst)

        # Original list should be unchanged
        assert lst == original, "Original list was modified"
        # Result should be a different list instance
        assert result is not lst, "Result is the same list instance"

    @given(st.lists(st.tuples(st.integers(), st.integers())))
    @settings(max_examples=50)
    def test_tuple_sorting(self, lst):
        """Property: Sorting tuples works correctly."""
        from src.bubblesort import bubble_sort

        result = bubble_sort(lst)

        # Result is sorted
        for i in range(len(result) - 1):
            assert result[i] <= result[i + 1], "Tuple list not sorted"

        # Result is permutation
        assert sorted(lst) == sorted(result), "Tuple result is not a permutation"

    @given(st.lists(st.integers(min_value=-100, max_value=100)))
    @settings(max_examples=100)
    def test_symmetry(self, lst):
        """Property: Sorting reversed list should give same result as sorting original."""
        from src.bubblesort import bubble_sort

        reversed_lst = list(reversed(lst))
        result1 = bubble_sort(lst)
        result2 = bubble_sort(reversed_lst)

        assert result1 == result2, "Sorting is not symmetric"


class TestBubbleSortContract:
    """Contract tests to verify bubble sort meets its specification."""

    def test_returns_list_for_all_iterable_types(self):
        """Contract: Function must return a list for any iterable input."""
        from src.bubblesort import bubble_sort

        test_inputs = [
            [3, 2, 1],  # list
            (3, 2, 1),  # tuple
            range(3, 0, -1),  # range
            {3, 2, 1},  # set
            iter([3, 2, 1]),  # iterator
        ]

        for input_val in test_inputs:
            result = bubble_sort(input_val)
            assert isinstance(result, list), f"Failed for input type: {type(input_val)}"

    def test_handles_duplicate_elements_correctly(self):
        """Contract: Duplicate elements should appear correct number of times."""
        from src.bubblesort import bubble_sort

        input_list = [3, 1, 3, 2, 1, 3]
        result = bubble_sort(input_list)

        # Count occurrences
        input_counts = {x: input_list.count(x) for x in set(input_list)}
        result_counts = {x: result.count(x) for x in set(result)}

        assert input_counts == result_counts, "Duplicate counts don't match"

    def test_handles_empty_and_single_element(self):
        """Contract: Must handle empty and single-element lists correctly."""
        from src.bubblesort import bubble_sort

        # Empty list
        assert bubble_sort([]) == []

        # Single element
        assert bubble_sort([42]) == [42]
        assert bubble_sort([0]) == [0]
        assert bubble_sort([-5]) == [-5]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
