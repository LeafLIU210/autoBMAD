"""Bubble sort algorithm implementation."""

from typing import List, Iterable, Any


def bubble_sort(arr: List[Any]) -> List[Any]:
    """
    Sort a list using the bubble sort algorithm.

    Bubble sort works by repeatedly stepping through the list,
    comparing adjacent elements and swapping them if in the wrong order.
    This implementation is pure and does not modify the input list.

    Args:
        arr: A list of comparable elements to sort

    Returns:
        A new sorted list (does not modify the input)

    Raises:
        TypeError: If arr is None or not iterable

    Time Complexity: O(n^2) in worst and average case
    Space Complexity: O(n) - creates a new list

    Examples:
        >>> bubble_sort([3, 1, 2])
        [1, 2, 3]

        >>> bubble_sort([5, 4, 3, 2, 1])
        [1, 2, 3, 4, 5]

        >>> bubble_sort([1, 2, 3, 4, 5])
        [1, 2, 3, 4, 5]

        >>> bubble_sort([])
        []

        >>> bubble_sort([1])
        [1]

        >>> bubble_sort([2, 2, 2, 2])
        [2, 2, 2, 2]

        >>> bubble_sort([-1, -3, -2, 0, 2])
        [-3, -2, -1, 0, 2]
    """
    # Input validation
    if arr is None:
        raise TypeError("Input cannot be None")
    try:
        # Check if iterable by attempting to iterate
        iter(arr)
    except TypeError:
        raise TypeError("Input must be iterable")

    # Create a copy to maintain purity
    result = list(arr)

    if len(result) <= 1:
        return result

    n = len(result)
    # Perform n-1 passes through the array
    for i in range(n):
        # Flag to optimize: if no swapping occurs, array is sorted
        swapped = False
        # Last i elements are already in place
        for j in range(0, n - i - 1):
            # Compare adjacent elements
            if result[j] > result[j + 1]:
                # Swap if they are in wrong order
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True

        # If no two elements were swapped, array is sorted
        if not swapped:
            break

    return result
