"""Test suite for bubble sort module."""

import pytest


class TestBubbleSort:
    """Test cases for bubble sort algorithm."""

    @pytest.mark.parametrize(
        "input_list,expected",
        [
            ([], []),
            ([1], [1]),
            ([1, 2], [1, 2]),
            ([2, 1], [1, 2]),
            ([1, 2, 3], [1, 2, 3]),
            ([3, 1, 2], [1, 2, 3]),
            ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
            (
                [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5],
                [1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9],
            ),
            ([2, 2, 2, 2], [2, 2, 2, 2]),
            ([-1, -3, -2, 0, 2], [-3, -2, -1, 0, 2]),
            ([3, -1, 0, -5, 2], [-5, -1, 0, 2, 3]),
        ],
    )
    def test_parametrized_basic_cases(self, input_list, expected):
        """Test sorting for various basic cases using parametrization."""
        from src.bubble_sort import bubble_sort

        assert bubble_sort(input_list) == expected

    def test_in_place_modification(self):
        """Test that bubble sort modifies the list in place."""
        from src.bubble_sort import bubble_sort

        original = [3, 1, 2]
        result = bubble_sort(original)
        assert result == [1, 2, 3]
        assert result is original  # Should return the same list object

    def test_preserves_original_values(self):
        """Test that bubble sort preserves all original values."""
        from src.bubble_sort import bubble_sort

        original = [5, 1, 4, 2, 8]
        sorted_list = bubble_sort(original)
        assert sorted(original) == sorted_list

    @pytest.mark.parametrize(
        "input_list,expected",
        [
            (
                [10**18, -(10**18), 10**15, -(10**15), 0],
                [-(10**18), -(10**15), 0, 10**15, 10**18],
            ),
            (
                [1, 100, 2, 99, 3, 98, 4, 97],
                [1, 2, 3, 4, 97, 98, 99, 100],
            ),
            ([1, 1, 2, 2, 3, 3, 4, 4], [1, 1, 2, 2, 3, 3, 4, 4]),
            ([1, 3, 2, 4, 5], [1, 2, 3, 4, 5]),
            ([0, -1, 0, -2, 1, -3], [-3, -2, -1, 0, 0, 1]),
            ([(2, "b"), (1, "a"), (3, "c")], [(1, "a"), (2, "b"), (3, "c")]),
            ([3, 1.5, 2, 4.2, 1], [1, 1.5, 2, 3, 4.2]),
            ([5] * 50 + [3] * 50 + [7] * 50, [3] * 50 + [5] * 50 + [7] * 50),
        ],
    )
    def test_parametrized_edge_cases(self, input_list, expected):
        """Test sorting for various edge cases using parametrization."""
        from src.bubble_sort import bubble_sort

        assert bubble_sort(input_list) == expected
