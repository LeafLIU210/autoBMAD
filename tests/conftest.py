"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture
def empty_list():
    """Return an empty list."""
    return []


@pytest.fixture
def single_element_list():
    """Return a list with one element."""
    return [42]


@pytest.fixture
def sorted_list():
    """Return a sorted list of integers."""
    return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


@pytest.fixture
def reverse_sorted_list():
    """Return a reverse-sorted list of integers."""
    return [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]


@pytest.fixture
def random_list():
    """Return a randomly ordered list of integers."""
    return [5, 2, 8, 1, 9, 3, 7, 4, 6]


@pytest.fixture
def list_with_duplicates():
    """Return a list with duplicate elements."""
    return [3, 1, 2, 3, 1, 2, 3]


@pytest.fixture
def list_with_negatives():
    """Return a list with negative numbers."""
    return [-5, -2, -8, -1, 0, 3, -3, 1]


@pytest.fixture
def list_with_floats():
    """Return a list with floating-point numbers."""
    return [3.14, 1.5, 2.7, 0.5, 4.2, 1.1]


@pytest.fixture
def list_with_strings():
    """Return a list with strings."""
    return ["zebra", "apple", "banana", "cherry", "apricot"]


@pytest.fixture
def large_list():
    """Return a large list for performance testing."""
    import random

    random.seed(42)
    return [random.randint(1, 1000) for _ in range(100)]


@pytest.fixture
def very_large_list():
    """Return a very large list for stress testing."""
    import random

    random.seed(123)
    return [random.randint(-10000, 10000) for _ in range(1000)]


@pytest.fixture
def list_with_extreme_values():
    """Return a list with extreme numerical values."""
    return [
        float("inf"),
        -(float("inf")),
        10**308,
        -(10**308),
        1e-308,
        -1e-308,
        0,
    ]


@pytest.fixture
def list_with_nan():
    """Return a list with NaN values (note: NaN comparisons are unusual)."""
    import math

    return [1.0, 2.0, math.nan, 3.0, 0.0]


@pytest.fixture
def palindrome_list():
    """Return a palindrome list."""
    return [1, 2, 3, 2, 1]


@pytest.fixture
def already_sorted_list():
    """Return an already sorted list for best-case testing."""
    return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]


@pytest.fixture
def worst_case_list():
    """Return a reverse-sorted list (worst case for bubble sort)."""
    return [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]


@pytest.fixture
def nearly_sorted_list():
    """Return a nearly sorted list (few elements out of place)."""
    return [1, 2, 3, 5, 4, 6, 7, 9, 8, 10]


@pytest.fixture
def all_same_elements():
    """Return a list with all identical elements."""
    return [42] * 20


@pytest.fixture
def alternating_pattern():
    """Return a list with alternating high/low pattern."""
    return [1, 100, 2, 99, 3, 98, 4, 97, 5, 96]


@pytest.fixture
def mountain_pattern():
    """Return a list with mountain-like pattern."""
    return [1, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2, 1]


@pytest.fixture
def valley_pattern():
    """Return a list with valley-like pattern."""
    return [10, 9, 8, 7, 6, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


@pytest.fixture
def random_binary_values():
    """Return a list with random binary values (0s and 1s)."""
    import random

    random.seed(999)
    return [random.randint(0, 1) for _ in range(50)]


@pytest.fixture
def list_of_tuples():
    """Return a list of tuples for comparison testing."""
    return [(3, "c"), (1, "a"), (2, "b"), (1, "d")]


@pytest.fixture
def list_of_lists():
    """Return a list of lists for nested comparison testing."""
    return [[3, 5], [1, 2], [2, 8], [1, 1], [3, 3]]


@pytest.fixture
def mixed_positive_negative():
    """Return a list with mixed positive and negative numbers."""
    return [-50, 30, -20, 40, -10, 50, 0, 10, -30, 20]


@pytest.fixture
def scientific_notation():
    """Return a list with numbers in scientific notation."""
    return [
        1e-10,
        1e10,
        -1e10,
        1e-5,
        1e5,
        -1e-5,
        -1e5,
        0,
    ]


@pytest.fixture
def very_small_numbers():
    """Return a list with very small positive numbers."""
    return [
        1e-100,
        1e-99,
        1e-98,
        1e-97,
        1e-96,
    ]


@pytest.fixture
def very_large_numbers():
    """Return a list with very large positive numbers."""
    return [
        10**50,
        10**51,
        10**52,
        10**53,
        10**54,
    ]


@pytest.fixture
def alternating_extremes():
    """Return a list alternating between min and max values."""
    import sys

    return [sys.maxsize, -(sys.maxsize)] * 10


@pytest.fixture
def duplicate_heavy():
    """Return a list with heavy duplication (90% duplicates)."""
    return [5] * 90 + [3] * 5 + [7] * 5


@pytest.fixture
def seeded_random_list():
    """Return a list with seeded random values for reproducibility."""
    import random

    random.seed(777)
    return [random.randint(-1000, 1000) for _ in range(50)]


@pytest.fixture
def consecutive_numbers():
    """Return a list of consecutive numbers."""
    return list(range(1, 21))


@pytest.fixture
def consecutive_numbers_reversed():
    """Return a reversed list of consecutive numbers."""
    return list(range(20, 0, -1))


@pytest.fixture
def list_with_zeros():
    """Return a list with many zeros."""
    return [0, 1, 0, 2, 0, 3, 0, 4, 0, 5]


@pytest.fixture
def primes_list():
    """Return a list of prime numbers."""
    return [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]


@pytest.fixture
def fibonacci_sequence():
    """Return a list of Fibonacci numbers (unsorted)."""
    return [34, 1, 55, 3, 21, 8, 13, 2, 5, 144, 89]


@pytest.fixture
def custom_comparable_objects():
    """Return a list of custom objects with comparison operators."""

    class Item:
        """Custom comparable item."""

        def __init__(self, value, priority):
            self.value = value
            self.priority = priority

        def __lt__(self, other):
            return self.priority < other.priority

        def __eq__(self, other):
            return self.priority == other.priority

        def __le__(self, other):
            return self.priority <= other.priority

        def __gt__(self, other):
            return self.priority > other.priority

        def __ge__(self, other):
            return self.priority >= other.priority

        def __ne__(self, other):
            return self.priority != other.priority

        def __repr__(self):
            return f"Item({self.value}, {self.priority})"

    return [
        Item("a", 3),
        Item("b", 1),
        Item("c", 4),
        Item("d", 1),
        Item("e", 5),
    ]


@pytest.fixture
def datetime_list():
    """Return a list of datetime objects for comparison testing."""
    from datetime import datetime, timedelta

    base = datetime(2024, 1, 1)
    return [
        base + timedelta(days=5),
        base,
        base + timedelta(days=3),
        base + timedelta(days=7),
        base + timedelta(days=1),
    ]


@pytest.fixture
def complex_number_list():
    """Return a list of complex numbers for comparison."""
    return [3 + 2j, 1 + 1j, 2 + 3j, 1 + 2j]
