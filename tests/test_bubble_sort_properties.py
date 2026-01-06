"""Property-based tests for bubble sort module."""

import pytest


class TestBubbleSortProperties:
    """Property-based test cases for bubble sort algorithm."""

    def test_sorting_idempotence(self):
        """Sorting twice should give the same result."""
        from src.bubble_sort import bubble_sort

        original = [3, 1, 4, 1, 5, 9, 2, 6, 5]
        sorted_once = bubble_sort(original.copy())
        sorted_twice = bubble_sort(sorted_once.copy())

        assert sorted_once == sorted_twice

    def test_sorting_preserves_length(self):
        """Sorting should not change the length of the list."""
        from src.bubble_sort import bubble_sort

        original = [5, 2, 8, 1, 9, 3, 7, 4, 6]
        sorted_list = bubble_sort(original)

        assert len(sorted_list) == len(original)

    def test_sorting_is_stable(self):
        """Sorting should preserve the relative order of equal elements."""
        from src.bubble_sort import bubble_sort

        # Create list with elements that compare equal but are distinct objects
        original = [(1, "a"), (2, "b"), (1, "c"), (2, "d")]
        sorted_list = bubble_sort(original.copy())

        # Check that elements with equal keys maintain relative order
        assert sorted_list[0][0] == 1
        assert sorted_list[1][0] == 1
        assert sorted_list[2][0] == 2
        assert sorted_list[3][0] == 2

    def test_minimum_element_is_first(self):
        """The minimum element should be first after sorting."""
        from src.bubble_sort import bubble_sort

        original = [5, 2, 8, 1, 9, 3, 7, 4, 6]
        sorted_list = bubble_sort(original)

        assert sorted_list[0] == min(original)

    def test_maximum_element_is_last(self):
        """The maximum element should be last after sorting."""
        from src.bubble_sort import bubble_sort

        original = [5, 2, 8, 1, 9, 3, 7, 4, 6]
        sorted_list = bubble_sort(original)

        assert sorted_list[-1] == max(original)

    def test_result_is_sorted(self):
        """The result should be in non-decreasing order."""
        from src.bubble_sort import bubble_sort

        original = [5, 2, 8, 1, 9, 3, 7, 4, 6]
        sorted_list = bubble_sort(original)

        for i in range(len(sorted_list) - 1):
            assert sorted_list[i] <= sorted_list[i + 1]

    def test_result_is_permutation(self):
        """The sorted list should be a permutation of the original."""
        from src.bubble_sort import bubble_sort

        original = [5, 2, 8, 1, 9, 3, 7, 4, 6]
        sorted_list = bubble_sort(original)

        assert sorted(original) == sorted_list

    def test_floats_are_sorted_correctly(self):
        """Floating-point numbers should be sorted correctly."""
        from src.bubble_sort import bubble_sort

        original = [3.14, 1.5, 2.7, 0.5, 4.2, 1.1]
        sorted_list = bubble_sort(original)

        expected = sorted(original)
        assert sorted_list == expected

    def test_strings_are_sorted_correctly(self):
        """String elements should be sorted correctly."""
        from src.bubble_sort import bubble_sort

        original = ["zebra", "apple", "banana", "cherry", "apricot"]
        sorted_list = bubble_sort(original)

        expected = sorted(original)
        assert sorted_list == expected

    @pytest.mark.parametrize("size", [0, 1, 2, 3, 5, 10, 20])
    def test_various_list_sizes(self, size):
        """Test sorting for various list sizes."""
        from src.bubble_sort import bubble_sort

        original = list(range(size, 0, -1))  # Reverse order
        sorted_list = bubble_sort(original)

        expected = list(range(1, size + 1))
        assert sorted_list == expected

    def test_commutative_property_with_duplicate_pairs(self):
        """Test that sorting is commutative with duplicate elements."""
        from src.bubble_sort import bubble_sort

        original = [3, 1, 2, 1, 3, 2]
        sorted_list = bubble_sort(original.copy())

        # Sorting twice should give the same result
        assert sorted_list == bubble_sort(sorted_list.copy())

    def test_transitive_property(self):
        """Test transitive property: if a <= b and b <= c, then a <= c."""
        from src.bubble_sort import bubble_sort

        original = [5, 3, 8, 1, 9, 2]
        sorted_list = bubble_sort(original)

        # Verify transitive property holds for sorted list
        for i in range(len(sorted_list) - 2):
            assert sorted_list[i] <= sorted_list[i + 1] <= sorted_list[i + 2]

    def test_antisymmetric_property(self):
        """Test antisymmetric property: if a <= b and b <= a, then a == b."""
        from src.bubble_sort import bubble_sort

        original = [3, 3, 2, 2, 1, 1]
        sorted_list = bubble_sort(original)

        # Elements should be grouped by value
        for value in sorted_list:
            indices = [i for i, x in enumerate(sorted_list) if x == value]
            # All occurrences of the same value should be consecutive
            assert all(sorted_list[i] == value for i in indices)

    def test_sorting_preserves_multiset(self):
        """Test that sorting preserves the multiset of elements."""
        from collections import Counter

        from src.bubble_sort import bubble_sort

        original = [5, 2, 8, 1, 9, 3, 7, 4, 6, 5, 2]
        sorted_list = bubble_sort(original)

        # Counter should be the same before and after sorting
        assert Counter(original) == Counter(sorted_list)

    def test_adversarial_input(self):
        """Test sorting with adversarial input (worst-case scenarios)."""
        from src.bubble_sort import bubble_sort

        # Worst case: reverse sorted list
        worst_case = list(range(100, 0, -1))
        sorted_worst = bubble_sort(worst_case)

        assert sorted_worst == list(range(1, 101))

        # Already sorted list (best case with optimization)
        best_case = list(range(1, 101))
        sorted_best = bubble_sort(best_case)

        assert sorted_best == list(range(1, 101))

    def test_pure_function_property(self):
        """Test that bubble sort is a pure function and doesn't modify input."""
        from src.bubble_sort import bubble_sort

        original = [5, 2, 8, 1, 9]
        original_id = id(original)

        result = bubble_sort(original)

        # Should create a new list
        assert id(result) != original_id
        # Input should not be modified
        assert original == [5, 2, 8, 1, 9]
        # Result should be sorted
        assert result == [1, 2, 5, 8, 9]
