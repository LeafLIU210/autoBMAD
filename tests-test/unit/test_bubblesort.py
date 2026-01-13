"""Comprehensive test suite for bubblesort module using TDD approach."""

import pytest
import random
import time
from src.bubblesort import bubble_sort


class TestBubbleSortBasic:
    def test_empty_list(self):
        assert bubble_sort([]) == []

    def test_single_element(self):
        assert bubble_sort([1]) == [1]

    def test_three_elements_unsorted(self):
        assert bubble_sort([3, 1, 2]) == [1, 2, 3]


class TestBubbleSortWithFloats:
    def test_floats_unsorted(self):
        assert bubble_sort([3.5, 1.2, 2.8]) == [1.2, 2.8, 3.5]


class TestBubbleSortLargeDatasets:
    def test_large_list_100_elements(self):
        data = list(range(100))
        random.shuffle(data)
        result = bubble_sort(data)
        assert result == list(range(100))

    def test_performance_large_list(self):
        data = list(range(100))
        random.shuffle(data)
        start = time.time()
        result = bubble_sort(data)
        elapsed = time.time() - start
        assert result == list(range(100))
        assert elapsed < 1.0


class TestBubbleSortErrorHandling:
    def test_none_input(self):
        with pytest.raises(TypeError, match="Input cannot be None"):
            bubble_sort(None)

    def test_non_iterable_input(self):
        with pytest.raises(TypeError, match="Input must be iterable"):
            bubble_sort(42)

    def test_nested_list(self):
        result = bubble_sort([[2, 3], [1, 2], [3, 4]])
        assert result == [[1, 2], [2, 3], [3, 4]]


class TestBubbleSortOptimization:
    def test_early_exit_optimization(self):
        sorted_data = list(range(100))
        start = time.time()
        result = bubble_sort(sorted_data)
        elapsed = time.time() - start
        assert result == sorted_data
        assert elapsed < 0.01


class TestBubbleSortInvariants:
    def test_commutativity_with_sort(self):
        for _ in range(10):
            data = [random.randint(-100, 100) for _ in range(20)]
            assert bubble_sort(data) == sorted(data)


class TestBubbleSortDocstringExamples:
    def test_docstring_example_1(self):
        assert bubble_sort([3, 1, 2]) == [1, 2, 3]
    
    def test_docstring_example_2(self):
        assert bubble_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]
    
    def test_docstring_example_3(self):
        assert bubble_sort([1.5, 3.2, 0.5]) == [0.5, 1.5, 3.2]
