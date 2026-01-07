"""Bubble Sort Algorithm Implementation and Optimized Variants.

This module provides implementations of bubble sort algorithm and its optimized
variants for educational and practical sorting of small lists.

Variants:
- bubble_sort: Basic implementation with early termination
- bubble_sort_optimized: Enhanced version with custom comparison support
- bubble_sort_cocktail: Bidirectional bubble sort variant

All variants maintain the same interface with support for:
- Ascending/descending order
- Custom key extraction
- Custom comparison functions
- In-place sorting option
"""

from typing import List, Iterable, Union, Callable, Optional, Any


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


def bubble_sort_optimized(
    data: Iterable[Any],
    ascending: bool = True,
    key: Optional[Callable[[Any], Any]] = None,
    reverse: bool = False,
    cmp: Optional[Callable[[Any, Any], int]] = None,
    in_place: bool = False
) -> List[Any]:
    """Sort a list using optimized bubble sort with early termination.

    This function implements an optimized bubble sort algorithm with the following
    features:
    - Early termination when no swaps occur (best case O(n) for sorted data)
    - Support for ascending/descending order
    - Custom key extraction function
    - Custom comparison function
    - Optional in-place sorting

    Time Complexity: O(n²) average and worst case
                     O(n) best case (already sorted)
    Space Complexity: O(1) if in_place=True, O(n) otherwise

    Performance Characteristics:
    - Best for: Small datasets (n < 50), partially sorted data
    - Early termination makes it efficient for nearly sorted lists
    - Simple implementation with predictable performance

    Args:
        data: An iterable of comparable elements to be sorted.
        ascending: If True, sort in ascending order; if False, descending.
                   Default is True. Note: when both ascending and reverse are
                   specified, they are combined (e.g., ascending=False, reverse=True
                   produces ascending order).
        key: Optional function to extract comparison key from elements.
             Similar to Python's sorted() key parameter.
        reverse: If True, reverse the sort order. Combined with ascending parameter.
        cmp: Optional custom comparison function taking two arguments (a, b)
             and returning negative if a < b, zero if a == b, positive if a > b.
             If provided, overrides the default comparison.
        in_place: If True, sort the list in place and return None.
                  Default is False (returns new sorted list).

    Returns:
        A new sorted list (if in_place=False) or None (if in_place=True).

    Raises:
        TypeError: If input is None or not iterable.
        ValueError: If custom comparison function is invalid.

    Examples:
        >>> bubble_sort_optimized([5, 1, 4, 2, 8])
        [1, 2, 4, 5, 8]

        >>> bubble_sort_optimized([5, 1, 4, 2, 8], ascending=False)
        [8, 5, 4, 2, 1]

        >>> bubble_sort_optimized([(1, 3), (2, 1), (3, 2)], key=lambda x: x[1])
        [(2, 1), (3, 2), (1, 3)]

        >>> bubble_sort_optimized(["a", "abc", "ab"], key=len)
        ['a', 'ab', 'abc']
    """
    if data is None:
        raise TypeError("Input cannot be None")

    # Handle in-place sorting
    if in_place:
        # For in-place sorting, data must be a list
        try:
            sorted_list = data  # type: ignore
            # Verify it's actually a list and mutable
            if not hasattr(sorted_list, '__setitem__'):
                raise TypeError("For in_place=True, data must be a mutable sequence (list)")
        except TypeError:
            raise TypeError("Input must be an iterable")
    else:
        # Create a copy for non-in-place sorting
        try:
            sorted_list = list(data)
        except TypeError:
            raise TypeError("Input must be an iterable")

    n = len(sorted_list)
    if n <= 1:
        return sorted_list if not in_place else None

    final_reverse = ascending ^ reverse

    if cmp is not None:
        def compare(a: Any, b: Any) -> bool:
            result = cmp(a, b)
            if final_reverse:
                return result > 0
            return result < 0
    else:
        if key is not None:
            # Stable comparison: compare by key, then by original element for stability
            def compare(a: Any, b: Any) -> bool:
                a_key = key(a)
                b_key = key(b)
                if a_key == b_key:
                    # Keys are equal, use original comparison for stability
                    # Only swap if elements are in wrong order (to maintain stability)
                    if final_reverse:
                        return a < b
                    else:
                        return a > b
                # Keys differ, compare by key
                if final_reverse:
                    return a_key > b_key
                return a_key < b_key
        else:
            if final_reverse:
                def compare(a: Any, b: Any) -> bool:
                    return a > b
            else:
                def compare(a: Any, b: Any) -> bool:
                    return a < b

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if compare(sorted_list[j], sorted_list[j + 1]):
                sorted_list[j], sorted_list[j + 1] = sorted_list[j + 1], sorted_list[j]
                swapped = True
        if not swapped:
            break

    return sorted_list if not in_place else None


def bubble_sort_cocktail(
    data: Iterable[Any],
    ascending: bool = True,
    key: Optional[Callable[[Any], Any]] = None,
    reverse: bool = False,
    cmp: Optional[Callable[[Any, Any], int]] = None,
    in_place: bool = False
) -> List[Any]:
    """Sort a list using cocktail shaker sort (bidirectional bubble sort).

    This function implements cocktail shaker sort, a bidirectional variant of
    bubble sort that sorts in both directions each pass. This can be more
    efficient than standard bubble sort for some patterns.

    Time Complexity: O(n²) average and worst case
                     O(n) best case (already sorted)
    Space Complexity: O(1) if in_place=True, O(n) otherwise

    Performance Characteristics:
    - Best for: Small datasets where small elements are at the end
    - Bidirectional passes can bring small elements to front faster
    - Still has same worst-case complexity as standard bubble sort

    Args:
        data: An iterable of comparable elements to be sorted.
        ascending: If True, sort in ascending order; if False, descending.
                   Default is True. Note: when both ascending and reverse are
                   specified, they are combined (e.g., ascending=False, reverse=True
                   produces ascending order).
        key: Optional function to extract comparison key from elements.
             Similar to Python's sorted() key parameter.
        reverse: If True, reverse the sort order. Combined with ascending parameter.
        cmp: Optional custom comparison function taking two arguments (a, b)
             and returning negative if a < b, zero if a == b, positive if a > b.
             If provided, overrides the default comparison.
        in_place: If True, sort the list in place and return None.
                  Default is False (returns new sorted list).

    Returns:
        A new sorted list (if in_place=False) or None (if in_place=True).

    Raises:
        TypeError: If input is None or not iterable.

    Examples:
        >>> bubble_sort_cocktail([5, 1, 4, 2, 8])
        [1, 2, 4, 5, 8]

        >>> bubble_sort_cocktail([5, 1, 4, 2, 8], ascending=False)
        [8, 5, 4, 2, 1]

        >>> bubble_sort_cocktail([(1, 3), (2, 1), (3, 2)], key=lambda x: x[1])
        [(2, 1), (3, 2), (1, 3)]
    """
    if data is None:
        raise TypeError("Input cannot be None")

    # Handle in-place sorting
    if in_place:
        # For in-place sorting, data must be a list
        try:
            sorted_list = data  # type: ignore
            # Verify it's actually a list and mutable
            if not hasattr(sorted_list, '__setitem__'):
                raise TypeError("For in_place=True, data must be a mutable sequence (list)")
        except TypeError:
            raise TypeError("Input must be an iterable")
    else:
        # Create a copy for non-in-place sorting
        try:
            sorted_list = list(data)
        except TypeError:
            raise TypeError("Input must be an iterable")

    n = len(sorted_list)
    if n <= 1:
        return sorted_list if not in_place else None

    final_reverse = ascending ^ reverse

    if cmp is not None:
        def compare(a: Any, b: Any) -> bool:
            result = cmp(a, b)
            if final_reverse:
                return result > 0
            return result < 0
    else:
        if key is not None:
            # Stable comparison: compare by key, then by original element for stability
            def compare(a: Any, b: Any) -> bool:
                a_key = key(a)
                b_key = key(b)
                if a_key == b_key:
                    # Keys are equal, use original comparison for stability
                    # Only swap if elements are in wrong order (to maintain stability)
                    if final_reverse:
                        return a < b
                    else:
                        return a > b
                # Keys differ, compare by key
                if final_reverse:
                    return a_key > b_key
                return a_key < b_key
        else:
            if final_reverse:
                def compare(a: Any, b: Any) -> bool:
                    return a > b
            else:
                def compare(a: Any, b: Any) -> bool:
                    return a < b

    start = 0
    end = n - 1
    swapped = True

    while swapped:
        swapped = False
        for i in range(start, end):
            if compare(sorted_list[i], sorted_list[i + 1]):
                sorted_list[i], sorted_list[i + 1] = sorted_list[i + 1], sorted_list[i]
                swapped = True

        if not swapped:
            break

        swapped = False
        end -= 1
        for i in range(end - 1, start - 1, -1):
            if compare(sorted_list[i], sorted_list[i + 1]):
                sorted_list[i], sorted_list[i + 1] = sorted_list[i + 1], sorted_list[i]
                swapped = True
        start += 1

    return sorted_list if not in_place else None
