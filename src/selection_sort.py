"""Selection Sort Algorithm Implementation.

This module provides a clean implementation of the selection sort algorithm
for educational and practical sorting of small lists.
"""

from typing import List, Iterable, Union


def selection_sort(data: Iterable[Union[int, float]]) -> List[Union[int, float]]:
    """Sort a list of numbers using the selection sort algorithm.

    This function implements the selection sort algorithm, which repeatedly
    finds the minimum element from the unsorted portion and puts it at the
    beginning of the sorted portion.

    Algorithm Steps:
    1. Start with the first element as the minimum
    2. Scan through the remaining elements to find the actual minimum
    3. Swap the found minimum with the first element
    4. Move to the next position in the sorted portion
    5. Repeat until the entire list is sorted

    Time Complexity: O(n²) in all cases (best, average, and worst)
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
        >>> selection_sort([5, 1, 4, 2, 8])
        [1, 2, 4, 5, 8]

        >>> selection_sort([3.14, 2.71, 1.41])
        [1.41, 2.71, 3.14]

        >>> selection_sort([])
        []

        >>> selection_sort([42])
        [42]

        >>> selection_sort([8, 5, 3, 1])
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

    # Selection sort implementation
    # Traverse through all array elements
    for i in range(n):
        # Find the minimum element in the remaining unsorted array
        min_idx = i
        for j in range(i + 1, n):
            if sorted_list[j] < sorted_list[min_idx]:
                min_idx = j

        # Swap the found minimum element with the first element
        # (only swap if the minimum is at a different position)
        if min_idx != i:
            sorted_list[i], sorted_list[min_idx] = sorted_list[min_idx], sorted_list[i]

    return sorted_list
