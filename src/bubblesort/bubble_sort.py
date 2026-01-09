"""
Bubble Sort Algorithm Implementation

This module provides a pure implementation of the bubble sort algorithm
for sorting lists of comparable elements (numbers).
"""

from collections.abc import Iterable
from typing import TypeVar

T = TypeVar("T", int, float)


def bubble_sort[T: (int, float)](data: Iterable[T]) -> list[T]:
    """
    Sort a list of numbers using the bubble sort algorithm.

    Bubble sort works by repeatedly stepping through the list, comparing
    adjacent elements and swapping them if they are in the wrong order.
    The pass through the list is repeated until the list is sorted.

    Args:
        data: An iterable of comparable elements (int or float)

    Returns:
        A new sorted list containing all elements from the input

    Raises:
        TypeError: If input is None or not iterable

    Examples:
        >>> bubble_sort([5, 1, 4, 2, 8])
        [1, 2, 4, 5, 8]

        >>> bubble_sort([3.5, 2.1, 4.8])
        [2.1, 3.5, 4.8]

        >>> bubble_sort([])  # Empty list
        []

        >>> bubble_sort([42])  # Single element
        [42]

    Time Complexity:
        - Worst Case: O(n²) - when list is in reverse order
        - Best Case: O(n) - when list is already sorted
        - Average Case: O(n²) - random order

    Space Complexity:
        O(n) - Creates a new list to store the sorted result
        (pure function - does not modify the original input)
    """
    # Input validation
    if data is None:
        raise TypeError("Input cannot be None")

    try:
        # Convert to list to ensure we can iterate and index
        result = list(data)
    except TypeError:
        raise TypeError("Input must be iterable")

    # Edge cases: empty list or single element
    n = len(result)
    if n <= 1:
        return result

    # Bubble sort implementation
    # Outer loop: n-1 passes through the list
    for i in range(n - 1):
        # Track if any swaps occurred in this pass
        swapped = False

        # Inner loop: compare adjacent elements
        # Each pass bubbles the largest element to the end
        for j in range(0, n - i - 1):
            if result[j] > result[j + 1]:
                # Swap adjacent elements
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True

        # Optimization: if no swaps occurred, list is sorted
        if not swapped:
            break

    return result
