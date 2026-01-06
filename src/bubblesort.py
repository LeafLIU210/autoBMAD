"""Bubble Sort Algorithm Implementation.

This module provides a pure implementation of the bubble sort algorithm,
which repeatedly steps through the list, compares adjacent elements and
swaps them if they are in the wrong order. The pass through the list is
repeated until the list is sorted.

The algorithm has O(n²) time complexity, making it inefficient for large
datasets, but it's simple to understand and implement, making it suitable
for educational purposes and small datasets.
"""

from typing import List, Iterable, Union


def bubble_sort(numbers: Iterable[Union[int, float]]) -> List[Union[int, float]]:
    """Sort a list of numbers using the bubble sort algorithm.

    This function implements the bubble sort algorithm, which works by
    repeatedly swapping adjacent elements if they are in the wrong order.
    The algorithm continues until no more swaps are needed, indicating
    that the list is sorted.

    Args:
        numbers: An iterable of numbers (int or float) to be sorted.
                 Cannot be None.

    Returns:
        A new sorted list containing the same elements as the input.

    Raises:
        TypeError: If the input is None or not iterable.

    Examples:
        >>> bubble_sort([5, 1, 4, 2, 8])
        [1, 2, 4, 5, 8]

        >>> bubble_sort([3, 2, 1])
        [1, 2, 3]

        >>> bubble_sort([1, 2, 3, 4, 5])
        [1, 2, 3, 4, 5]

        >>> bubble_sort([])
        []

        >>> bubble_sort([5])
        [5]
    """
    # Validate input is not None
    if numbers is None:
        raise TypeError("Input cannot be None")

    # Convert to list and handle edge cases
    nums_list = list(numbers)

    # Handle empty list and single element (already sorted)
    if len(nums_list) <= 1:
        return nums_list

    # Create a copy to maintain pure function behavior
    result = nums_list.copy()

    # Bubble sort implementation
    n = len(result)
    for i in range(n):
        # Flag to optimize: if no swaps occur, list is sorted
        swapped = False
        # Last i elements are already in place
        for j in range(0, n - i - 1):
            # Compare adjacent elements
            if result[j] > result[j + 1]:
                # Swap if they are in wrong order
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True

        # If no swapping occurred, list is sorted
        if not swapped:
            break

    return result
