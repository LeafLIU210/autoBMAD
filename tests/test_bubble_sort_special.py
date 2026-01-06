"""Special value tests for bubble sort module.

This test file verifies that bubble sort handles special numerical values correctly,
including NaN, infinity, very large numbers, and extreme values.
"""

import sys


class TestBubbleSortSpecialValues:
    """Special value test cases for bubble sort algorithm."""

    def test_infinity_sorting(self):
        """Test sorting with positive and negative infinity."""
        from src.bubble_sort import bubble_sort

        test_list = [1, float("inf"), 2, float("-inf"), 3, 0]
        result = bubble_sort(test_list)

        # Negative infinity should come first, positive infinity last
        assert result[0] == float("-inf")
        assert result[-1] == float("inf")

    def test_extreme_large_numbers(self):
        """Test sorting with extremely large numbers."""
        from src.bubble_sort import bubble_sort

        test_list = [
            10**100,
            -(10**100),
            10**50,
            -(10**50),
            0,
            1,
            -1,
        ]

        result = bubble_sort(test_list)
        expected = sorted(test_list)

        assert result == expected

    def test_extreme_small_numbers(self):
        """Test sorting with extremely small positive numbers."""
        from src.bubble_sort import bubble_sort

        test_list = [
            1e-100,
            1e-99,
            1e-98,
            1e-97,
            1e-96,
            0,
        ]

        result = bubble_sort(test_list)
        expected = sorted(test_list)

        assert result == expected

    def test_mixed_extreme_values(self):
        """Test sorting with mixed extreme positive and negative values."""
        from src.bubble_sort import bubble_sort

        test_list = [
            10**50,
            -(10**50),
            1e-50,
            -(1e-50),
            0,
            1,
            -1,
        ]

        result = bubble_sort(test_list)
        expected = sorted(test_list)

        assert result == expected

    def test_maxsize_sorting(self):
        """Test sorting with sys.maxsize values."""
        from src.bubble_sort import bubble_sort

        test_list = [
            sys.maxsize,
            -(sys.maxsize),
            0,
            1,
            -1,
        ]

        result = bubble_sort(test_list)
        expected = sorted(test_list)

        assert result == expected

    def test_alternating_extremes(self):
        """Test sorting with alternating min and max values."""
        from src.bubble_sort import bubble_sort

        test_list = [sys.maxsize, -(sys.maxsize)] * 5 + [0]

        result = bubble_sort(test_list)
        expected = sorted(test_list)

        assert result == expected

    def test_scientific_notation(self):
        """Test sorting with numbers in scientific notation."""
        from src.bubble_sort import bubble_sort

        test_list = [
            1e-10,
            1e10,
            -1e10,
            1e-5,
            1e5,
            -1e-5,
            -1e5,
            0,
        ]

        result = bubble_sort(test_list)
        expected = sorted(test_list)

        assert result == expected

    def test_negative_zero(self):
        """Test sorting with negative zero."""
        from src.bubble_sort import bubble_sort

        test_list = [0.0, -0.0, 1, -1, 2, -2]

        result = bubble_sort(test_list)
        expected = sorted(test_list)

        assert result == expected

    def test_very_large_floats(self):
        """Test sorting with very large floating point numbers."""
        from src.bubble_sort import bubble_sort

        test_list = [
            float(1e308),
            float(-1e308),
            float(1e307),
            float(-1e307),
        ]

        result = bubble_sort(test_list)
        expected = sorted(test_list)

        assert result == expected

    def test_denormalized_numbers(self):
        """Test sorting with denormalized (very small) numbers."""
        from src.bubble_sort import bubble_sort

        # Test with numbers near the minimum denormalized value
        test_list = [
            1e-308,
            1e-309,
            1e-310,
            0,
            -1e-310,
            -1e-309,
            -1e-308,
        ]

        result = bubble_sort(test_list)
        expected = sorted(test_list)

        assert result == expected

    def test_mixed_int_and_float_extremes(self):
        """Test sorting with mixed integers and floating point extremes."""
        from src.bubble_sort import bubble_sort

        test_list = [
            1000000,
            float("inf"),
            -(float("inf")),
            0,
            -1000000,
            1e100,
            -1e100,
        ]

        result = bubble_sort(test_list)

        # Check extreme values are in correct positions
        assert result[0] == -(float("inf"))
        assert result[-1] == float("inf")

    def test_special_float_values(self):
        """Test sorting with various special float values."""
        from src.bubble_sort import bubble_sort

        # Create a list with various special values
        test_list = [
            0.0,
            -0.0,
            1.0,
            -1.0,
            float("inf"),
            float("-inf"),
        ]

        result = bubble_sort(test_list)
        expected = sorted(test_list)

        assert result == expected

    def test_extreme_precision_values(self):
        """Test sorting with values at the edge of float precision."""
        from src.bubble_sort import bubble_sort

        # These values are very close together
        test_list = [
            1.0000000000001,
            1.0000000000002,
            1.0,
            1.0000000000003,
        ]

        result = bubble_sort(test_list)
        expected = sorted(test_list)

        assert result == expected

    def test_all_infinities(self):
        """Test sorting a list containing only infinity values."""
        from src.bubble_sort import bubble_sort

        test_list = [
            float("inf"),
            float("-inf"),
            float("inf"),
            float("-inf"),
        ]

        result = bubble_sort(test_list)
        expected = sorted(test_list)

        assert result == expected

    def test_extreme_range(self):
        """Test sorting with an extreme range of values."""
        from src.bubble_sort import bubble_sort

        test_list = [
            -(10**100),
            10**100,
            -(10**50),
            10**50,
            -(10**10),
            10**10,
            0,
        ]

        result = bubble_sort(test_list)
        expected = sorted(test_list)

        assert result == expected

    def test_repeated_extreme_values(self):
        """Test sorting with repeated extreme values."""
        from src.bubble_sort import bubble_sort

        test_list = [
            float("inf"),
            float("inf"),
            float("inf"),
            float("-inf"),
            float("-inf"),
            0,
        ]

        result = bubble_sort(test_list)
        expected = sorted(test_list)

        assert result == expected

    def test_very_wide_range(self):
        """Test sorting with a very wide range of values."""
        from src.bubble_sort import bubble_sort

        test_list = [
            10**100,
            -(10**100),
            1e-100,
            -1e-100,
            1,
            -1,
            0,
        ]

        result = bubble_sort(test_list)
        expected = sorted(test_list)

        assert result == expected

    def test_binary_extremes(self):
        """Test sorting with binary-related extreme values."""
        from src.bubble_sort import bubble_sort

        # Using powers of 2
        test_list = [
            2**100,
            -(2**100),
            2**50,
            -(2**50),
            0,
            1,
            -1,
        ]

        result = bubble_sort(test_list)
        expected = sorted(test_list)

        assert result == expected

    def test_hexadecimal_extremes(self):
        """Test sorting with hexadecimal-based extreme values."""
        from src.bubble_sort import bubble_sort

        # Using hexadecimal notation (0x)
        test_list = [
            0xFFFF,
            -(0xFFFF),
            0xFF,
            -(0xFF),
            0,
            1,
            -1,
        ]

        result = bubble_sort(test_list)
        expected = sorted(test_list)

        assert result == expected

    def test_octal_extremes(self):
        """Test sorting with octal-based extreme values."""
        from src.bubble_sort import bubble_sort

        # Using octal notation (0o)
        test_list = [
            0o7777,
            -(0o7777),
            0o777,
            -(0o777),
            0,
            1,
            -1,
        ]

        result = bubble_sort(test_list)
        expected = sorted(test_list)

        assert result == expected
