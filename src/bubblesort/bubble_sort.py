"""Bubble sort algorithm implementation.

This module provides a pure implementation of the bubble sort algorithm
with comprehensive error handling and support for various numeric types.
"""

from collections.abc import Iterable


def bubble_sort(data: Iterable[int | float]) -> list[int | float]:
    """Sort a list of numbers using the bubble sort algorithm.

    This function implements the bubble sort algorithm with optimization for
    already-sorted lists (early exit when no swaps occur).

    Args:
        data: An iterable of numbers (int or float) to be sorted

    Returns:
        A new sorted list containing all elements from the input

    Raises:
        TypeError: If input is None or not iterable

    Examples:
        >>> bubble_sort([3, 1, 2])
        [1, 2, 3]
        >>> bubble_sort([5, 4, 3, 2, 1])
        [1, 2, 3, 4, 5]
        >>> bubble_sort([1.5, 3.2, 0.5])
        [0.5, 1.5, 3.2]
    """
    if data is None:
        raise TypeError("Input cannot be None")

    # Convert to list and validate
    try:
        result = list(data)
    except TypeError as err:
        raise TypeError("Input must be iterable") from err

    # Bubble sort implementation with optimization
    n = len(result)
    if n <= 1:
        return result

    # Track if any swap occurred
    swapped = True
    # We can stop early if no swaps in a complete pass
    for i in range(n):
        swapped = False
        # Last i elements are already in place
        for j in range(0, n - i - 1):
            if result[j] > result[j + 1]:
                # Swap elements
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True

        # If no swap occurred, array is sorted
        if not swapped:
            break

    return result
