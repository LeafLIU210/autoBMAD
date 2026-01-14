"""Comprehensive test suite for bubble_sort module using parameterized tests."""

import pytest

from src.bubblesort.bubble_sort import bubble_sort


class TestBubbleSortBasicScenarios:
    """Test basic sorting scenarios using parameterized tests."""

    @pytest.mark.parametrize(
        "input_data,expected",
        [
            ([], []),  # Empty list
            ([1], [1]),  # Single element - int
            ([5.5], [5.5]),  # Single element - float
        ],
    )
    def test_basic_cases(self, input_data, expected):
        """Test basic sorting scenarios."""
        assert bubble_sort(input_data) == expected

    @pytest.mark.parametrize(
        "input_data,expected",
        [
            ([1, 2], [1, 2]),  # Two elements already sorted
            ([1.5, 3.2], [1.5, 3.2]),  # Two elements already sorted - floats
            ([2, 1], [1, 2]),  # Two elements unsorted
            ([3.2, 1.5], [1.5, 3.2]),  # Two elements unsorted - floats
        ],
    )
    def test_two_element_cases(self, input_data, expected):
        """Test two-element list sorting scenarios."""
        assert bubble_sort(input_data) == expected


class TestBubbleSortOrdering:
    """Test various ordering scenarios using parameterized tests."""

    @pytest.mark.parametrize(
        "input_data,expected",
        [
            ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),  # Already sorted
            ([1.1, 2.2, 3.3, 4.4], [1.1, 2.2, 3.3, 4.4]),  # Already sorted - floats
            ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),  # Reverse sorted
            ([4.4, 3.3, 2.2, 1.1], [1.1, 2.2, 3.3, 4.4]),  # Reverse sorted - floats
            ([3, 1, 4, 1, 5, 9, 2, 6], [1, 1, 2, 3, 4, 5, 6, 9]),  # Random order
            ([2.7, 1.5, 3.3, 0.9], [0.9, 1.5, 2.7, 3.3]),  # Random order - floats
            ([1, 2, 3, 5, 4, 6, 7, 8], [1, 2, 3, 4, 5, 6, 7, 8]),  # Nearly sorted
        ],
    )
    def test_ordering_scenarios(self, input_data, expected):
        """Test various ordering scenarios."""
        assert bubble_sort(input_data) == expected


class TestBubbleSortDataTypes:
    """Test sorting with different numeric data types."""

    @pytest.mark.parametrize(
        "input_data,expected",
        [
            ([-1, -2, -3, -4], [-4, -3, -2, -1]),  # All negative
            ([0, -1, 1, -2, 2], [-2, -1, 0, 1, 2]),  # Mixed pos/neg
            ([3, -1, 0, 2, -3], [-3, -1, 0, 2, 3]),  # Mixed pos/neg/zero
            ([1.1, 1.11, 1.111], [1.1, 1.11, 1.111]),  # Float precision
            ([1, 2.5, 3, 1.5], [1, 1.5, 2.5, 3]),  # Mixed int/float
        ],
    )
    def test_numeric_types(self, input_data, expected):
        """Test sorting with different numeric types."""
        assert bubble_sort(input_data) == expected


class TestBubbleSortDuplicates:
    """Test sorting with duplicate elements."""

    @pytest.mark.parametrize(
        "input_data,expected",
        [
            ([2, 2, 2], [2, 2, 2]),  # All duplicates
            ([3, 1, 3, 1, 3], [1, 1, 3, 3, 3]),  # Multiple duplicates
            ([5, 5, 5, 5], [5, 5, 5, 5]),  # All same
        ],
    )
    def test_duplicate_handling(self, input_data, expected):
        """Test sorting lists with duplicate elements."""
        assert bubble_sort(input_data) == expected


class TestBubbleSortIterableTypes:
    """Test sorting different iterable types."""

    @pytest.mark.parametrize(
        "iterable_type,input_data,expected",
        [
            ("list", [3, 1, 2], [1, 2, 3]),  # List input
            ("tuple", (3, 1, 2), [1, 2, 3]),  # Tuple input
            ("generator", (x for x in [3, 1, 2]), [1, 2, 3]),  # Generator input
            ("range", range(5, 0, -1), [1, 2, 3, 4, 5]),  # Range input
        ],
    )
    def test_different_iterables(self, iterable_type, input_data, expected):
        """Test sorting different iterable types."""
        result = bubble_sort(input_data)
        assert result == expected
        assert isinstance(result, list)


class TestBubbleSortPerformance:
    """Test performance and optimization features."""

    @pytest.mark.parametrize(
        "input_data,expected",
        [
            # Large list
            (list(range(100, 0, -1)), list(range(1, 101))),
            # Already sorted - tests early optimization
            ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
        ],
    )
    def test_performance_scenarios(self, input_data, expected):
        """Test performance-related scenarios."""
        assert bubble_sort(input_data) == expected


class TestBubbleSortErrorHandling:
    """Test error handling for invalid inputs."""

    @pytest.mark.parametrize(
        "invalid_input,error_type,error_message",
        [
            (None, TypeError, "Input cannot be None"),
            (123, TypeError, "Input must be iterable"),
        ],
    )
    def test_invalid_inputs(self, invalid_input, error_type, error_message):
        """Test that invalid inputs raise appropriate errors."""
        with pytest.raises(error_type, match=error_message):
            bubble_sort(invalid_input)


class TestBubbleSortImmutability:
    """Test that the function maintains immutability of input."""

    @pytest.mark.parametrize(
        "input_data",
        [
            [3, 1, 2],
            [5, 4, 3, 2, 1],
            [1.5, 3.2, 0.5],
        ],
    )
    def test_input_immutability(self, input_data):
        """Test that the original input list is not modified."""
        original = input_data[:]  # Create a copy to verify
        result = bubble_sort(input_data)

        # Verify result is correct
        assert result == sorted(original)

        # Verify original is unchanged
        assert input_data == original


class TestBubbleSortReturnType:
    """Test that the function returns the correct type."""

    @pytest.mark.parametrize(
        "input_data",
        [
            [3, 1, 2],
            [5, 4, 3, 2, 1],
            [1.5, 3.2, 0.5],
        ],
    )
    def test_returns_list(self, input_data):
        """Test that the function returns a list."""
        result = bubble_sort(input_data)
        assert isinstance(result, list)


class TestBubbleSortCorrectness:
    """Additional correctness tests for verification."""

    @pytest.mark.parametrize(
        "input_data,expected",
        [
            # Edge cases
            ([1], [1]),  # Single element
            ([2, 1], [1, 2]),  # Two elements
            # Complex cases
            ([3, 1, 4, 1, 5, 9, 2, 6], [1, 1, 2, 3, 4, 5, 6, 9]),  # Pi-like sequence
            ([-5, -10, -3, 0, 5, 10], [-10, -5, -3, 0, 5, 10]),  # Range with zero
        ],
    )
    def test_correctness(self, input_data, expected):
        """Test correctness of sorting algorithm."""
        assert bubble_sort(input_data) == expected
