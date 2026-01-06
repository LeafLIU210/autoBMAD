"""Concurrency and thread safety tests for bubble sort module.

This test file verifies that bubble sort handles concurrent access correctly
and maintains thread safety in multi-threaded environments.
"""

import concurrent.futures
import threading
from threading import Lock


class TestBubbleSortConcurrency:
    """Concurrency test cases for bubble sort algorithm."""

    def test_concurrent_sorting_different_lists(self):
        """Test that sorting different lists concurrently works correctly."""
        from src.bubble_sort import bubble_sort

        lists_to_sort = [
            [5, 3, 8, 1, 9],
            [10, 7, 8, 9, 3],
            [15, 11, 6, 13, 2],
            [20, 4, 17, 1, 14],
        ]

        def sort_list(lst):
            return bubble_sort(lst)

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(sort_list, lst.copy()) for lst in lists_to_sort]
            results = [future.result() for future in futures]

        expected_results = [sorted(lst) for lst in lists_to_sort]

        assert results == expected_results

    def test_concurrent_access_with_lock(self):
        """Test concurrent access to bubble sort with thread synchronization."""
        from src.bubble_sort import bubble_sort

        results = []
        lock = Lock()

        def sort_with_lock(lst, index):
            with lock:
                result = bubble_sort(lst)
                results.append((index, result))

        lists = [[i, i + 10, i + 5] for i in range(10)]

        threads = [
            threading.Thread(target=sort_with_lock, args=(lst.copy(), i))
            for i, lst in enumerate(lists)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        assert len(results) == 10
        for _, result in results:
            assert result == sorted(result)

    def test_multiple_threads_same_list(self):
        """Test that multiple threads can safely work with the same list."""
        from src.bubble_sort import bubble_sort

        # Each thread should work with its own copy
        original = [5, 3, 8, 1, 9, 2, 7, 4, 6]
        num_threads = 5
        results = []

        def sort_and_store(lst):
            result = bubble_sort(lst)
            results.append(result)

        threads = [
            threading.Thread(target=sort_and_store, args=(original.copy(),))
            for _ in range(num_threads)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        expected = sorted(original)
        assert len(results) == num_threads
        for result in results:
            assert result == expected

    def test_concurrent_modification_doesnt_crash(self):
        """Test that concurrent operations don't cause crashes."""
        from src.bubble_sort import bubble_sort

        success_count = [0]
        lock = Lock()

        def safe_sort(lst):
            try:
                result = bubble_sort(lst)
                with lock:
                    success_count[0] += 1
                return result
            except Exception:
                pass

        lists = [[i, i % 10, (i + 5) % 10] for i in range(50)]

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(safe_sort, lst.copy()) for lst in lists]
            concurrent.futures.wait(futures)

        assert success_count[0] == 50

    def test_thread_pool_stress_test(self):
        """Stress test with many concurrent sorting operations."""
        from src.bubble_sort import bubble_sort

        import random

        random.seed(42)
        test_lists = [
            [random.randint(-1000, 1000) for _ in range(50)]
            for _ in range(20)
        ]

        def sort_and_verify(lst):
            result = bubble_sort(lst)
            assert result == sorted(lst)
            assert len(result) == len(lst)
            return True

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = [
                executor.submit(sort_and_verify, lst.copy())
                for lst in test_lists
            ]
            results = [future.result() for future in futures]

        assert all(results)
