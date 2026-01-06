"""Bubble sort algorithm implementation."""

from typing import List, Iterable, Any


def bubble_sort(arr: List[Any]) -> List[Any]:
    """
    Sort a list using the bubble sort algorithm.

    Bubble sort works by repeatedly stepping through the list,
    comparing adjacent elements and swapping them if in the wrong order.

    Args:
        arr: A list of comparable elements to sort

    Returns:
        The sorted list (same object, modified in place)

    Raises:
        TypeError: If arr is None or not iterable

    Time Complexity: O(n^2) in worst and average case
    Space Complexity: O(1) - sorts in place

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

    if len(arr) <= 1:
        return arr

    n = len(arr)
    # Perform n-1 passes through the array
    for i in range(n):
        # Flag to optimize: if no swapping occurs, array is sorted
        swapped = False
        # Last i elements are already in place
        for j in range(0, n - i - 1):
            # Compare adjacent elements
            if arr[j] > arr[j + 1]:
                # Swap if they are in wrong order
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True

        # If no two elements were swapped, array is sorted
        if not swapped:
            break

    return arr
