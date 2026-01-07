"""Insertion Sort Algorithm Implementation.

This module provides a clean implementation of the insertion sort algorithm
for educational and practical sorting of small to medium lists.
"""

from typing import List, Iterable, Union


def insertion_sort(data: Iterable[Union[int, float]]) -> List[Union[int, float]]:
    """Sort a list of numbers using the insertion sort algorithm.

    This function implements the insertion sort algorithm, which builds
    the final sorted list one item at a time by comparing and inserting
    each element into its correct position.

    Algorithm Steps:
    1. Start with the second element (assume first element is sorted)
    2. Compare the current element with the elements in the sorted portion
    3. Shift all greater elements one position to the right
    4. Insert the current element in its correct position
    5. Repeat for all elements in the list

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
        >>> insertion_sort([5, 1, 4, 2, 8])
        [1, 2, 4, 5, 8]

        >>> insertion_sort([3.14, 2.71, 1.41])
        [1.41, 2.71, 3.14]

        >>> insertion_sort([])
        []

        >>> insertion_sort([42])
        [42]

        >>> insertion_sort([8, 5, 3, 1])
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

    # Insertion sort implementation
    # Start with the second element (index 1)
    for i in range(1, n):
        # Store the current element to be inserted
        key = sorted_list[i]
        j = i - 1

        # Move elements greater than 'key' one position ahead
        while j >= 0 and sorted_list[j] > key:
            sorted_list[j + 1] = sorted_list[j]
            j -= 1

        # Insert the key at its correct position
        sorted_list[j + 1] = key

    return sorted_list
