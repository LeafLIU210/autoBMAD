"""
Comprehensive test suite for bubble sort implementation.

This test suite provides thorough coverage of the bubble sort algorithm,
testing all edge cases, input types, and error conditions as specified in
the acceptance criteria for Story 1.3.
"""


import pytest


class TestBubbleSortExistence:
    """Test that bubble_sort function exists and is importable."""

    def test_bubble_sort_exists(self):
        """Test that bubble_sort function exists and is importable."""
        from src.bubblesort import bubble_sort

        assert callable(bubble_sort)


class TestBasicFunctionality:
    """Test basic functionality scenarios (AC: #1)."""

    @pytest.mark.parametrize(
        "input_list,expected",
        [
            ([], []),
            ([5], [5]),
            ([1], [1]),
            ([0], [0]),
            ([-1], [-1]),
            ([100], [100]),
        ],
    )
    def test_empty_and_single_element(self, input_list, expected):
        """Test empty list and single element scenarios."""
        from src.bubblesort import bubble_sort

        result = bubble_sort(input_list)
        assert result == expected
        assert isinstance(result, list)

    @pytest.mark.parametrize(
        "input_list,expected",
        [
            ([1, 2], [1, 2]),
            ([2, 1], [1, 2]),
            ([5, 1, 4, 2, 8], [1, 2, 4, 5, 8]),
            ([10, -5, 3, 0, 7], [-5, 0, 3, 7, 10]),
            ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
            ([3, 7, 2, 9, 1], [1, 2, 3, 7, 9]),
        ],
    )
    def test_multiple_elements(self, input_list, expected):
        """Test multiple element scenarios with 2, 5, and 10+ elements."""
        from src.bubblesort import bubble_sort

        result = bubble_sort(input_list)
        assert result == expected


class TestInputOrderings:
    """Test various input orderings (AC: #2)."""

    @pytest.mark.parametrize(
        "input_list,expected",
        [
            ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
            ([1, 2, 3], [1, 2, 3]),
            ([0, 1, 2], [0, 1, 2]),
            ([100, 200, 300], [100, 200, 300]),
        ],
    )
    def test_already_sorted(self, input_list, expected):
        """Test already sorted input."""
        from src.bubblesort import bubble_sort

        result = bubble_sort(input_list)
        assert result == expected

    @pytest.mark.parametrize(
        "input_list,expected",
        [
            ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
            ([3, 2, 1], [1, 2, 3]),
            ([10, 5, 0], [0, 5, 10]),
            ([100, 50, 0], [0, 50, 100]),
        ],
    )
    def test_reverse_sorted(self, input_list, expected):
        """Test reverse sorted input."""
        from src.bubblesort import bubble_sort

        result = bubble_sort(input_list)
        assert result == expected

    @pytest.mark.parametrize(
        "input_list,expected",
        [
            ([3, 1, 4, 1, 5, 9, 2, 6], [1, 1, 2, 3, 4, 5, 6, 9]),
            ([5, 3, 8, 4, 2, 7, 1, 6], [1, 2, 3, 4, 5, 6, 7, 8]),
            ([9, 1, 8, 2, 7, 3, 6, 4, 5], [1, 2, 3, 4, 5, 6, 7, 8, 9]),
            ([7, 3, 9, 2, 5, 1, 8, 4, 6], [1, 2, 3, 4, 5, 6, 7, 8, 9]),
        ],
    )
    def test_random_order(self, input_list, expected):
        """Test random order input."""
        from src.bubblesort import bubble_sort

        result = bubble_sort(input_list)
        assert result == expected

    @pytest.mark.parametrize(
        "input_list,expected",
        [
            ([3, 1, 2, 3, 1], [1, 1, 2, 3, 3]),
            ([5, 5, 5, 5], [5, 5, 5, 5]),
            ([1, 2, 1, 2, 1], [1, 1, 1, 2, 2]),
            ([4, 4, 1, 1, 2, 2], [1, 1, 2, 2, 4, 4]),
            ([2, 2, 2, 1, 1, 1], [1, 1, 1, 2, 2, 2]),
        ],
    )
    def test_duplicate_elements(self, input_list, expected):
        """Test with duplicate elements."""
        from src.bubblesort import bubble_sort

        result = bubble_sort(input_list)
        assert result == expected

    @pytest.mark.parametrize(
        "input_list,expected",
        [
            ([1, 2, 5, 3, 4, 6, 7, 8], [1, 2, 3, 4, 5, 6, 7, 8]),
            ([1, 3, 2, 4, 5], [1, 2, 3, 4, 5]),
            ([2, 1, 3, 4, 5], [1, 2, 3, 4, 5]),
        ],
    )
    def test_partially_sorted(self, input_list, expected):
        """Test partially sorted input."""
        from src.bubblesort import bubble_sort

        result = bubble_sort(input_list)
        assert result == expected


class TestNumericTypes:
    """Test different numeric types (AC: #3)."""

    @pytest.mark.parametrize(
        "input_list,expected",
        [
            ([5, -3, 0, -10, 2], [-10, -3, 0, 2, 5]),
            ([-1, -2, -3, -4, -5], [-5, -4, -3, -2, -1]),
            ([0, -1, 1, -2, 2], [-2, -1, 0, 1, 2]),
            ([100, -100, 50, -50, 0], [-100, -50, 0, 50, 100]),
        ],
    )
    def test_negative_numbers(self, input_list, expected):
        """Test with negative numbers."""
        from src.bubblesort import bubble_sort

        result = bubble_sort(input_list)
        assert result == expected

    @pytest.mark.parametrize(
        "input_list,expected",
        [
            ([3.5, 1.2, 2.8, 0.5], [0.5, 1.2, 2.8, 3.5]),
            ([1.1, 2.2, 3.3, 4.4], [1.1, 2.2, 3.3, 4.4]),
            ([9.9, 1.1, 5.5, 3.3], [1.1, 3.3, 5.5, 9.9]),
            ([0.1, 0.2, 0.3], [0.1, 0.2, 0.3]),
        ],
    )
    def test_floats(self, input_list, expected):
        """Test with floats."""
        from src.bubblesort import bubble_sort

        result = bubble_sort(input_list)
        assert result == expected

    @pytest.mark.parametrize(
        "input_list,expected",
        [
            ([5, 1.5, 3, 2.7, 4], [1.5, 2.7, 3, 4, 5]),
            ([10, 5.5, 0, 2.2, 7], [0, 2.2, 5.5, 7, 10]),
            ([1, 2.5, 3, 4.5, 5], [1, 2.5, 3, 4.5, 5]),
            ([3.14, 1, 2.71, 0], [0, 1, 2.71, 3.14]),
        ],
    )
    def test_mixed_int_float(self, input_list, expected):
        """Test with mixed int and float."""
        from src.bubblesort import bubble_sort

        result = bubble_sort(input_list)
        assert result == expected

    @pytest.mark.parametrize(
        "input_list,expected",
        [
            ([0, 0, 0, 0], [0, 0, 0, 0]),
            ([1, 0, -1, 2, -2], [-2, -1, 0, 1, 2]),
            ([0.0, 1.0, -1.0], [-1.0, 0.0, 1.0]),
        ],
    )
    def test_zero_values(self, input_list, expected):
        """Test with zero values."""
        from src.bubblesort import bubble_sort

        result = bubble_sort(input_list)
        assert result == expected

    @pytest.mark.parametrize(
        "input_list,expected",
        [
            ([1000000, 1000, 100], [100, 1000, 1000000]),
            ([0.001, 0.01, 0.1], [0.001, 0.01, 0.1]),
            ([999999, 1, 100000], [1, 100000, 999999]),
        ],
    )
    def test_large_numbers(self, input_list, expected):
        """Test with large numbers."""
        from src.bubblesort import bubble_sort

        result = bubble_sort(input_list)
        assert result == expected


class TestErrorHandling:
    """Test error handling (AC: #4)."""

    def test_none_input_raises_type_error(self):
        """Test None input handling."""
        from src.bubblesort import bubble_sort

        with pytest.raises(TypeError, match="Input cannot be None"):
            bubble_sort(None)

    @pytest.mark.parametrize(
        "non_iterable",
        [
            123,
            45.67,
            True,
            None,
        ],
    )
    def test_non_iterable_input_raises_type_error(self, non_iterable):
        """Test non-iterable input handling."""
        from src.bubblesort import bubble_sort

        with pytest.raises(TypeError):
            bubble_sort(non_iterable)


class TestPureFunctionBehavior:
    """Test pure function behavior (AC: #5)."""

    @pytest.mark.parametrize(
        "original",
        [
            [5, 1, 4, 2, 8],
            [3, 1, 2],
            [10, 9, 8, 7],
            [1, 2, 3, 4, 5],
            [5],
            [],
            [1.5, 0.5, 2.5],
        ],
    )
    def test_original_list_not_modified(self, original):
        """Verify original list is not modified."""
        from src.bubblesort import bubble_sort

        original_copy = original.copy()
        result = bubble_sort(original)
        assert original == original_copy
        assert result is not original

    @pytest.mark.parametrize(
        "original",
        [
            [5, 1, 4, 2, 8],
            [3, 1, 2],
            [10, 9, 8, 7],
            [1, 2, 3, 4, 5],
            [5],
            [],
        ],
    )
    def test_returns_new_list_instance(self, original):
        """Verify function returns a new list instance."""
        from src.bubblesort import bubble_sort

        result = bubble_sort(original)
        assert result is not original
        assert isinstance(result, list)


class TestDocumentation:
    """Test that implementation has proper documentation."""

    def test_bubble_sort_has_docstring(self):
        """Test that bubble_sort has a docstring."""
        from src.bubblesort import bubble_sort

        assert bubble_sort.__doc__ is not None
        assert len(bubble_sort.__doc__.strip()) > 0

    def test_bubble_sort_docstring_contains_info(self):
        """Test that docstring contains algorithm information."""
        from src.bubblesort import bubble_sort

        docstring = bubble_sort.__doc__.lower()
        assert "bubble" in docstring or "sort" in docstring

    def test_bubble_sort_has_type_hints(self):
        """Test that bubble_sort has type hints."""
        import inspect

        from src.bubblesort import bubble_sort

        sig = inspect.signature(bubble_sort)
        sig_str = str(sig).lower()
        assert "list" in sig_str or "typing" in sig_str


class TestCoverageEdgeCases:
    """Additional edge cases for comprehensive coverage."""

    @pytest.mark.parametrize(
        "input_list,expected",
        [
            ([-100, 100, -50, 50, 0], [-100, -50, 0, 50, 100]),
            ([1.1, 1.0, 1.2, 0.9], [0.9, 1.0, 1.1, 1.2]),
            ([1000, 100, 10, 1], [1, 10, 100, 1000]),
            ([0.001, 0.01, 0.1], [0.001, 0.01, 0.1]),
        ],
    )
    def test_additional_edge_cases(self, input_list, expected):
        """Test additional edge cases for comprehensive coverage."""
        from src.bubblesort import bubble_sort

        result = bubble_sort(input_list)
        assert result == expected

    def test_with_generator_input(self):
        """Test that function works with generator input."""
        from src.bubblesort import bubble_sort

        generator = (x for x in [5, 3, 1, 4, 2])
        result = bubble_sort(generator)
        assert result == [1, 2, 3, 4, 5]
        assert isinstance(result, list)

    def test_with_tuple_input(self):
        """Test that function works with tuple input."""
        from src.bubblesort import bubble_sort

        result = bubble_sort((5, 3, 1, 4, 2))
        assert result == [1, 2, 3, 4, 5]
        assert isinstance(result, list)
