"""Fuzz testing for bubble sort module.

This test file uses fuzz testing to find edge cases and potential bugs
in the bubble sort implementation by testing with randomized data.
"""

import random
from collections import Counter

import pytest


class TestBubbleSortFuzz:
    """Fuzz test cases for bubble sort algorithm."""

    @pytest.mark.parametrize("seed", range(10))
    def test_fuzz_random_small_lists(self, seed):
        """Test sorting with random small lists using different seeds."""
        from src.bubble_sort import bubble_sort

        random.seed(seed)
        test_data = [
            random.randint(-100, 100) for _ in range(random.randint(0, 20))
        ]

        result = bubble_sort(test_data.copy())
        expected = sorted(test_data)

        assert result == expected, (
            f"Failed for seed {seed} with data {test_data}. "
            f"Expected {expected}, got {result}"
        )

    @pytest.mark.parametrize("size", [10, 20, 30, 50, 100])
    def test_fuzz_random_medium_lists(self, size):
        """Test sorting with random medium-sized lists."""
        from src.bubble_sort import bubble_sort

        random.seed(42)
        test_data = [random.randint(-1000, 1000) for _ in range(size)]

        result = bubble_sort(test_data.copy())
        expected = sorted(test_data)

        assert result == expected, (
            f"Failed for size {size}. " f"Expected {expected}, got {result}"
        )

    def test_fuzz_large_dataset(self):
        """Test sorting with a large randomized dataset."""
        from src.bubble_sort import bubble_sort

        random.seed(123)
        # Generate a large dataset with various characteristics
        test_data = [random.randint(-(10**6), 10**6) for _ in range(1000)]

        result = bubble_sort(test_data.copy())
        expected = sorted(test_data)

        assert result == expected
        assert len(result) == len(test_data)
        assert Counter(result) == Counter(test_data)

    def test_fuzz_with_duplicates(self):
        """Test sorting with heavy duplicates."""
        from src.bubble_sort import bubble_sort

        random.seed(456)
        # Create data with many duplicates
        test_data = [
            random.choice([1, 2, 3, 5, 7, 11, 13, 17, 19]) for _ in range(200)
        ]

        result = bubble_sort(test_data.copy())
        expected = sorted(test_data)

        assert result == expected
        assert Counter(result) == Counter(test_data)

    def test_fuzz_negative_numbers(self):
        """Test sorting with heavy negative numbers."""
        from src.bubble_sort import bubble_sort

        random.seed(789)
        # Create data with mostly negative numbers
        test_data = [random.randint(-1000, -1) for _ in range(100)]

        result = bubble_sort(test_data.copy())
        expected = sorted(test_data)

        assert result == expected

    def test_fuzz_mixed_range(self):
        """Test sorting with a wide range of numbers."""
        from src.bubble_sort import bubble_sort

        random.seed(101112)
        # Create data with extreme values
        test_data = [
            -(10**9),
            -1000,
            -1,
            0,
            1,
            1000,
            10**9,
        ]
        # Add some random values in between
        test_data.extend([random.randint(-(10**6), 10**6) for _ in range(20)])

        result = bubble_sort(test_data)
        expected = sorted(test_data)

        assert result == expected

    def test_fuzz_strings_and_numbers(self):
        """Test sorting with mixed strings and numbers (lexicographic)."""
        from src.bubble_sort import bubble_sort

        random.seed(131415)
        # Create mixed data
        test_data = ["apple", "banana", "cherry", "date", "elderberry"]
        test_data.extend([str(random.randint(1, 100)) for _ in range(10)])

        result = bubble_sort(test_data.copy())
        expected = sorted(test_data)

        assert result == expected

    def test_fuzz_float_precision(self):
        """Test sorting with floating point numbers."""
        from src.bubble_sort import bubble_sort

        random.seed(161718)
        # Create float data with potential precision issues
        test_data = [random.uniform(-1000, 1000) for _ in range(50)]

        result = bubble_sort(test_data.copy())
        expected = sorted(test_data)

        assert result == expected

    def test_fuzz_extreme_values(self):
        """Test sorting with extreme edge values."""
        from src.bubble_sort import bubble_sort

        # Include various extreme values
        test_data = [
            float("inf"),
            float("-inf"),
            0,
            -0.0,
            1,
            -1,
            2**31 - 1,
            -(2**31),
            2**63 - 1,
            -(2**63),
        ]

        result = bubble_sort(test_data.copy())

        # Note: sorting with inf values has special behavior
        # We just verify the result is in non-decreasing order
        for i in range(len(result) - 1):
            assert (
                result[i] <= result[i + 1]
            ), f"Result not sorted: {result[i]} > {result[i + 1]}"

    @pytest.mark.parametrize(
        "pattern",
        [
            "alternating",
            "alternating_large",
            "random_blocks",
            "valley",
            "mountain",
            "sawtooth",
        ],
    )
    def test_fuzz_patterns(self, pattern):
        """Test sorting with various data patterns."""
        from src.bubble_sort import bubble_sort

        patterns = {
            "alternating": [i if i % 2 == 0 else -i for i in range(50)],
            "alternating_large": [
                i if i % 2 == 0 else 10**6 - i for i in range(50)
            ],
            "random_blocks": [i // 5 for i in range(50)],
            "valley": [abs(i - 25) for i in range(50)],
            "mountain": [50 - abs(i - 25) for i in range(50)],
            "sawtooth": [i % 10 for i in range(50)],
        }

        test_data = patterns[pattern]
        result = bubble_sort(test_data.copy())
        expected = sorted(test_data)

        assert result == expected, (
            f"Failed for pattern '{pattern}'. "
            f"Expected {expected}, got {result}"
        )

    def test_fuzz_biased_distribution(self):
        """Test sorting with biased distributions."""
        from src.bubble_sort import bubble_sort

        random.seed(192021)
        # Create biased distributions
        for _ in range(5):
            # Mostly small values with occasional large ones
            test_data = [random.randint(1, 10) for _ in range(50)]
            test_data.extend([random.randint(100, 1000) for _ in range(10)])

            result = bubble_sort(test_data.copy())
            expected = sorted(test_data)

            assert result == expected

    def test_fuzz_zero_heavy(self):
        """Test sorting with many zeros."""
        from src.bubble_sort import bubble_sort

        random.seed(222324)
        # Create data with many zeros
        test_data = [0] * 50
        test_data.extend([random.randint(-100, 100) for _ in range(50)])

        result = bubble_sort(test_data.copy())
        expected = sorted(test_data)

        assert result == expected
        assert result.count(0) == 50
