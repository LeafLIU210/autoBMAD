"""Edge case tests for bubble sort module."""

import time


class TestBubbleSortEdgeCases:
    """Edge case test cases for bubble sort algorithm."""

    def test_very_large_numbers(self):
        """Test sorting with very large numbers."""
        from src.bubble_sort import bubble_sort

        original = [10**18, -(10**18), 10**15, -(10**15), 0]
        sorted_list = bubble_sort(original)

        expected = sorted(original)
        assert sorted_list == expected

    def test_all_same_elements(self):
        """Test sorting when all elements are identical."""
        from src.bubble_sort import bubble_sort

        original = [5, 5, 5, 5, 5]
        sorted_list = bubble_sort(original)

        assert sorted_list == [5, 5, 5, 5, 5]
        assert all(x == 5 for x in sorted_list)

    def test_alternating_elements(self):
        """Test sorting with alternating high and low values."""
        from src.bubble_sort import bubble_sort

        original = [1, 100, 2, 99, 3, 98, 4, 97]
        sorted_list = bubble_sort(original)

        expected = sorted(original)
        assert sorted_list == expected

    def test_already_sorted_with_duplicates(self):
        """Test sorting an already sorted list with duplicates."""
        from src.bubble_sort import bubble_sort

        original = [1, 1, 2, 2, 3, 3, 4, 4]
        sorted_list = bubble_sort(original)

        assert sorted_list == original

    def test_single_swap_needed(self):
        """Test when only one swap is needed."""
        from src.bubble_sort import bubble_sort

        original = [1, 3, 2, 4, 5]
        sorted_list = bubble_sort(original)

        expected = [1, 2, 3, 4, 5]
        assert sorted_list == expected

    def test_zeros_and_negatives(self):
        """Test sorting with zeros and negative numbers."""
        from src.bubble_sort import bubble_sort

        original = [0, -1, 0, -2, 1, -3]
        sorted_list = bubble_sort(original)

        expected = [-3, -2, -1, 0, 0, 1]
        assert sorted_list == expected

    def test_very_small_list(self):
        """Test with the smallest possible lists."""
        from src.bubble_sort import bubble_sort

        # Empty list
        assert bubble_sort([]) == []

        # Single element
        assert bubble_sort([1]) == [1]

        # Two elements
        assert bubble_sort([2, 1]) == [1, 2]
        assert bubble_sort([1, 2]) == [1, 2]

    def test_performance_with_large_list(self):
        """Test that bubble sort handles reasonably sized lists."""
        # 100 elements should still be manageable
        import random

        from src.bubble_sort import bubble_sort

        random.seed(42)
        original = [random.randint(1, 1000) for _ in range(100)]
        sorted_list = bubble_sort(original.copy())

        assert sorted_list == sorted(original)

    def test_tuple_sorting(self):
        """Test sorting tuples (should sort by first element)."""
        from src.bubble_sort import bubble_sort

        original = [(2, "b"), (1, "a"), (3, "c")]
        sorted_list = bubble_sort(original)

        expected = [(1, "a"), (2, "b"), (3, "c")]
        assert sorted_list == expected

    def test_mixed_types_that_compare(self):
        """Test sorting with mixed numeric types."""
        from src.bubble_sort import bubble_sort

        original = [3, 1.5, 2, 4.2, 1]
        sorted_list = bubble_sort(original)

        expected = sorted(original)
        assert sorted_list == expected

    def test_long_sequences(self):
        """Test with long sequences of repeated values."""
        from src.bubble_sort import bubble_sort

        original = [5] * 50 + [3] * 50 + [7] * 50
        sorted_list = bubble_sort(original)

        # All 3s should come before all 5s, which come before all 7s
        assert sorted_list[:50] == [3] * 50
        assert sorted_list[50:100] == [5] * 50
        assert sorted_list[100:] == [7] * 50

    def test_performance_small_list(self):
        """Test performance of sorting a small list (10 elements)."""
        from src.bubble_sort import bubble_sort

        test_data = [5, 2, 8, 1, 9, 3, 7, 4, 6, 0]
        result = bubble_sort(test_data)

        assert result == sorted(test_data)

    def test_performance_medium_list(self):
        """Test performance of sorting a medium list (50 elements)."""
        import random

        from src.bubble_sort import bubble_sort

        random.seed(42)
        test_data = [random.randint(1, 1000) for _ in range(50)]
        result = bubble_sort(test_data)

        assert result == sorted(test_data)

    def test_performance_large_list(self):
        """Test performance of sorting a large list (100 elements)."""
        import random

        from src.bubble_sort import bubble_sort

        random.seed(42)
        test_data = [random.randint(1, 1000) for _ in range(100)]
        result = bubble_sort(test_data)

        assert result == sorted(test_data)

    def test_time_complexity(self):
        """Verify that bubble sort has O(n^2) time complexity."""
        import random

        from src.bubble_sort import bubble_sort

        # Test with different list sizes and measure time
        sizes = [10, 20, 30, 40, 50]
        times = []

        for size in sizes:
            random.seed(42)
            test_data = [random.randint(1, 1000) for _ in range(size)]

            start = time.perf_counter()
            bubble_sort(test_data)
            end = time.perf_counter()

            times.append(end - start)

        # For bubble sort (O(n^2)), time should roughly increase by factor of 4 when size doubles
        # This is a rough check - we're looking for quadratic growth
        for i in range(1, len(times)):
            size_ratio = sizes[i] / sizes[i - 1]
            time_ratio = times[i] / times[i - 1] if times[i - 1] > 0 else 0

            # Time ratio should be roughly proportional to square of size ratio
            # For example, if size doubles (ratio=2), time should roughly quadruple (ratio≈4)
            # Relaxed assertion to account for timing variability
            assert time_ratio > size_ratio * 0.5, (
                f"Time complexity appears much better than O(n^2): "
                f"size {sizes[i-1]}->{sizes[i]} (ratio {size_ratio:.2f}), "
                f"time ratio {time_ratio:.2f}"
            )


class CustomObject:
    """Custom class for testing bubble sort with custom objects."""

    def __init__(self, value, name):
        self.value = value
        self.name = name

    def __lt__(self, other):
        return self.value < other.value

    def __eq__(self, other):
        return self.value == other.value

    def __le__(self, other):
        return self.value <= other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __ne__(self, other):
        return self.value != other.value

    def __repr__(self):
        return f"CustomObject({self.value}, '{self.name}')"


class TestBubbleSortCustomObjects:
    """Test cases for bubble sort with custom objects."""

    def test_custom_objects_sorting(self):
        """Test sorting with custom objects that implement comparison operators."""
        from src.bubble_sort import bubble_sort

        objects = [
            CustomObject(3, "third"),
            CustomObject(1, "first"),
            CustomObject(2, "second"),
        ]
        sorted_objects = bubble_sort(objects)

        assert sorted_objects[0].value == 1
        assert sorted_objects[1].value == 2
        assert sorted_objects[2].value == 3

    def test_custom_objects_stability(self):
        """Test that bubble sort maintains stability with custom objects."""
        from src.bubble_sort import bubble_sort

        objects = [
            CustomObject(1, "first"),
            CustomObject(2, "a"),
            CustomObject(1, "second"),
            CustomObject(2, "b"),
        ]
        sorted_objects = bubble_sort(objects)

        # First object with value 1 should come before second object with value 1
        assert sorted_objects[0].name == "first"
        assert sorted_objects[1].name == "second"

        # First object with value 2 should come before second object with value 2
        assert sorted_objects[2].name == "a"
        assert sorted_objects[3].name == "b"

    def test_custom_objects_duplicate_values(self):
        """Test sorting with custom objects having duplicate values."""
        from src.bubble_sort import bubble_sort

        objects = [
            CustomObject(5, "a"),
            CustomObject(3, "b"),
            CustomObject(5, "c"),
            CustomObject(3, "d"),
            CustomObject(5, "e"),
        ]
        sorted_objects = bubble_sort(objects)

        # All 3s should come before all 5s
        assert sorted_objects[0].value == 3
        assert sorted_objects[1].value == 3
        assert sorted_objects[2].value == 5
        assert sorted_objects[3].value == 5
        assert sorted_objects[4].value == 5

        # Within same value groups, order should be preserved
        assert sorted_objects[0].name == "b"
        assert sorted_objects[1].name == "d"
        assert sorted_objects[2].name == "a"
        assert sorted_objects[3].name == "c"
        assert sorted_objects[4].name == "e"
