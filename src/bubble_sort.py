"""Bubble Sort Algorithm Implementation.

This module provides a clean implementation of the bubble sort algorithm
for educational and practical sorting of small lists.
"""

from typing import List, Iterable, Union


def bubble_sort(data: Iterable[Union[int, float]]) -> List[Union[int, float]]:
    """Sort a list of numbers using the bubble sort algorithm.

    This function implements the bubble sort algorithm, which repeatedly
    steps through the list, compares adjacent elements and swaps them
    if they are in the wrong order. The pass through the list is
    repeated until the list is sorted.

    Algorithm Steps:
    1. Start with the first element and compare it with the next element
    2. If the current element is greater than the next element, swap them
    3. Move to the next element and repeat steps 1-2
    4. After each full pass, the largest unsorted element "bubbles up"
       to its correct position at the end of the list
    5. Repeat until no swaps are needed (list is sorted)

    Time Complexity: O(n²) in the average and worst case
                     O(n) in the best case (already sorted)
    Space Complexity: O(1) - sorts in place

    Args:
        data: An iterable of numbers (int or float) to be sorted.
              The input list is not modified.

    Returns:
        A new sorted list containing all elements from the input.

    Raises:
        TypeError: If input is None or not iterable.
        ValueError: If input contains non-numeric elements.

    Examples:
        >>> bubble_sort([5, 1, 4, 2, 8])
        [1, 2, 4, 5, 8]

        >>> bubble_sort([3.14, 2.71, 1.41])
        [1.41, 2.71, 3.14]

        >>> bubble_sort([])
        []

        >>> bubble_sort([42])
        [42]

        >>> bubble_sort([8, 5, 3, 1])
        [1, 3, 5, 8]
    """
    # Validate input is not None
    if data is None:
        raise TypeError("Input cannot be None")

    # Convert to list and validate it's iterable
    try:
        input_list = list(data)
    except TypeError:
        raise TypeError("Input must be an iterable of numbers")

    # Validate all elements are numeric
    for i, item in enumerate(input_list):
        if not isinstance(item, (int, float)):
            raise ValueError(
                f"All elements must be numeric (int or float), "
                f"but element at index {i} is {type(item).__name__}"
            )

    # Handle edge cases: empty list or single element
    n = len(input_list)
    if n <= 1:
        return input_list

    # Create a copy to avoid modifying the original list
    sorted_list = input_list[:]

    # Bubble sort implementation with early termination
    # Outer loop: controls how many passes through the list
    for i in range(n):
        # Flag to optimize: if no swaps occur, list is sorted
        swapped = False

        # Inner loop: compare adjacent elements
        # After i passes, the last i elements are already in place
        for j in range(0, n - i - 1):
            # Compare adjacent elements and swap if out of order
            if sorted_list[j] > sorted_list[j + 1]:
                # Swap elements
                sorted_list[j], sorted_list[j + 1] = sorted_list[j + 1], sorted_list[j]
                swapped = True

        # Early termination: if no swaps occurred, list is sorted
        if not swapped:
            break

    return sorted_list
