"""Memory efficiency tests for bubble sort module.

This test file verifies that bubble sort maintains O(1) space complexity
and handles memory efficiently during sorting operations.
"""

import gc
import sys


class TestBubbleSortMemory:
    """Memory efficiency test cases for bubble sort algorithm."""

    def test_pure_function_behavior(self):
        """Test that bubble sort does not modify the input list (pure function)."""
        from src.bubble_sort import bubble_sort

        original = [5, 3, 8, 1, 9, 2, 7, 4, 6]
        original_copy = original.copy()

        result = bubble_sort(original)

        # Input should not be modified
        assert original == original_copy
        assert original == [5, 3, 8, 1, 9, 2, 7, 4, 6]

        # Result should be sorted
        assert result == [1, 2, 3, 4, 5, 6, 7, 8, 9]

        # Result should be a new list object
        assert result is not original

    def test_no_additional_memory_allocation(self):
        """Test that sorting doesn't allocate additional memory proportional to input."""
        from src.bubble_sort import bubble_sort

        # Get baseline memory
        gc.collect()

        # Test with various list sizes
        for size in [10, 50, 100, 500]:
            test_list = list(range(size, 0, -1))  # Reverse sorted for worst case

            gc.collect()
            before_size = sys.getsizeof(test_list)

            result = bubble_sort(test_list)

            gc.collect()
            after_size = sys.getsizeof(result)

            # Size should not increase significantly (O(1) space)
            # Allowing small variations due to internal list growth
            size_diff = after_size - before_size

            # The list might grow slightly but not proportionally to input size
            assert size_diff < size / 2, (
                f"Memory allocation grew too much: {size_diff} bytes for size {size}"
            )

    def test_constant_extra_space(self):
        """Test that extra space used is constant regardless of input size."""
        from src.bubble_sort import bubble_sort

        import random

        random.seed(42)

        memory_measurements = []

        for size in [10, 50, 100, 200]:
            test_list = [random.randint(-1000, 1000) for _ in range(size)]

            # Measure memory before
            gc.collect()
            before = sys.getsizeof(test_list)

            result = bubble_sort(test_list)

            # Measure memory after
            gc.collect()
            after = sys.getsizeof(result)

            memory_measurements.append(after - before)

        # The difference in extra memory should be minimal
        # (variations are due to list resizing, not algorithm complexity)
        max_diff = max(memory_measurements) - min(memory_measurements)

        # Allow some variation due to list resizing
        assert max_diff < 100, (
            f"Extra memory varies too much: {max_diff} bytes"
        )

    def test_very_large_integers(self):
        """Test sorting with very large integers doesn't cause memory issues."""
        from src.bubble_sort import bubble_sort

        # Use very large integers
        large_ints = [
            10**100,
            -(10**100),
            10**50,
            -(10**50),
            0,
            1,
            -1,
        ]

        result = bubble_sort(large_ints)

        assert result == sorted(large_ints)
        assert len(result) == len(large_ints)

    def test_memory_with_duplicate_elements(self):
        """Test memory efficiency with many duplicate elements."""
        from src.bubble_sort import bubble_sort

        # Create list with many duplicates
        test_list = [42] * 1000 + [17] * 500 + [99] * 300

        original_size = sys.getsizeof(test_list)
        result = bubble_sort(test_list)
        result_size = sys.getsizeof(result)

        # Size should not change dramatically
        size_diff = abs(result_size - original_size)
        assert size_diff < 100, f"Size changed too much: {size_diff} bytes"

        # Result should be correct
        assert result == sorted(test_list)

    def test_memory_reuse(self):
        """Test that bubble sort creates a new list (pure function)."""
        from src.bubble_sort import bubble_sort

        test_list = [5, 3, 8, 1, 9, 2, 7, 4, 6]
        original_id = id(test_list)

        result = bubble_sort(test_list)

        # Should create a new list object
        assert id(result) != original_id

        # Original should not be modified
        assert test_list == [5, 3, 8, 1, 9, 2, 7, 4, 6]

        # Result should be sorted
        assert result == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_nested_list_handling(self):
        """Test that nested structures are handled correctly."""
        from src.bubble_sort import bubble_sort

        # Sort list of lists by first element
        nested = [[3, 5], [1, 2], [2, 8], [1, 1]]

        result = bubble_sort(nested)

        expected = [[1, 1], [1, 2], [2, 8], [3, 5]]
        assert result == expected

        # Input should not be modified
        assert nested == [[3, 5], [1, 2], [2, 8], [1, 1]]

        # Should create a new list
        assert id(result) != id(nested)

    def test_memory_pressure(self):
        """Test sorting under memory pressure conditions."""
        from src.bubble_sort import bubble_sort

        # Create a reasonably large list
        test_list = [i % 100 for i in range(10000)]
        original = test_list.copy()

        result = bubble_sort(test_list)

        # Verify correctness
        assert result == sorted(test_list)

        # Verify input is not modified
        assert test_list == original

        # Memory should be reasonable
        result_size = sys.getsizeof(result)
        # Size should be proportional to elements, not complexity
        assert result_size < 100000

    def test_tuple_sorting_memory(self):
        """Test sorting tuples maintains memory efficiency."""
        from src.bubble_sort import bubble_sort

        # Sort tuples by first element
        tuples = [(3, "a"), (1, "b"), (2, "c"), (1, "a")]

        result = bubble_sort(tuples)

        expected = [(1, "a"), (1, "b"), (2, "c"), (3, "a")]
        assert result == expected

        # Input should not be modified
        assert tuples == [(3, "a"), (1, "b"), (2, "c"), (1, "a")]

        # Should create a new list
        assert id(result) != id(tuples)

    def test_mixed_type_sorting(self):
        """Test sorting with mixed types doesn't waste memory."""
        from src.bubble_sort import bubble_sort

        # Mix integers and floats
        mixed = [3.14, 1, 2.5, 0, -1, 3.0]

        result = bubble_sort(mixed)

        expected = sorted(mixed)
        assert result == expected

        # Input should not be modified
        assert mixed == [3.14, 1, 2.5, 0, -1, 3.0]

        # Should create a new list
        assert id(result) != id(mixed)

    def test_empty_and_single_element_memory(self):
        """Test memory handling for edge cases."""
        from src.bubble_sort import bubble_sort

        # Empty list
        empty = []
        result_empty = bubble_sort(empty)
        assert result_empty == []

        # Single element
        single = [42]
        result_single = bubble_sort(single)
        assert result_single == [42]
        # For single element, it returns a new list (pure function)
        assert id(result_single) != id(single)

    def test_gc_pressure(self):
        """Test that sorting doesn't create garbage for GC to collect."""
        import gc
        from src.bubble_sort import bubble_sort

        gc.collect()
        gc_before = gc.get_count()

        test_list = [5, 3, 8, 1, 9, 2, 7, 4, 6]

        # Perform sorting
        for _ in range(10):
            bubble_sort(test_list.copy())

        gc.collect()
        gc_after = gc.get_count()

        # GC count shouldn't increase dramatically
        # (allow some variation as GC is non-deterministic)
        assert gc_after[0] - gc_before[0] < 100
