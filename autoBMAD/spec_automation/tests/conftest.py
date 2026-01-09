"""Shared test fixtures for bubble sort tests."""


import pytest


@pytest.fixture
def empty_list() -> list:
    """Return an empty list."""
    return []


@pytest.fixture
def single_element_list() -> list[int]:
    """Return a single element list."""
    return [42]


@pytest.fixture
def already_sorted_list() -> list[int]:
    """Return an already sorted list."""
    return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


@pytest.fixture
def reverse_sorted_list() -> list[int]:
    """Return a reverse sorted list."""
    return [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]


@pytest.fixture
def random_order_list() -> list[int]:
    """Return a random order list."""
    return [5, 3, 8, 4, 2, 7, 1, 6, 9, 10]


@pytest.fixture
def negative_numbers_list() -> list[int]:
    """Return a list with negative numbers."""
    return [5, -3, 0, -10, 2, 7, -5]


@pytest.fixture
def floats_list() -> list[float]:
    """Return a list with float numbers."""
    return [3.5, 1.2, 2.8, 0.5, 4.1, 2.3]


@pytest.fixture
def mixed_int_float_list() -> list:
    """Return a list with mixed int and float."""
    return [5, 1.5, 3, 2.7, 4, 0.5]


@pytest.fixture
def duplicate_elements_list() -> list[int]:
    """Return a list with duplicate elements."""
    return [3, 1, 2, 3, 1, 5, 2, 1]


@pytest.fixture
def all_same_elements_list() -> list[int]:
    """Return a list with all same elements."""
    return [5, 5, 5, 5, 5]


@pytest.fixture
def large_numbers_list() -> list[int]:
    """Return a list with large numbers."""
    return [1000, 5000, 100, 500, 10000, 50]


@pytest.fixture
def partially_sorted_list() -> list[int]:
    """Return a partially sorted list."""
    return [1, 2, 5, 3, 4, 6, 7, 8]
