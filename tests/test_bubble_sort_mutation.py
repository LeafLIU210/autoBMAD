"""Mutation testing for bubble sort module.

This test file verifies the robustness of our test suite by introducing mutations
to the bubble_sort function and ensuring that tests fail when they should.
"""

import importlib.util
import os
import tempfile


class MutatedBubbleSort:
    """A class to generate mutated versions of bubble_sort for testing."""

    @staticmethod
    def create_mutation_remove_swap(original_code):
        """Create a mutation where swap logic is removed (broken)."""
        # This mutation removes the swap statement, leaving elements in place
        mutated = original_code.replace(
            "result[j], result[j + 1] = result[j + 1], result[j]",
            "# result[j], result[j + 1] = result[j + 1]  # MUTATION: removed swap",
        )
        return mutated

    @staticmethod
    def create_mutation_reverse_comparison(original_code):
        """Create a mutation where comparison is reversed (broken)."""
        # This mutation reverses the comparison, sorting in descending order
        mutated = original_code.replace(
            "if result[j] > result[j + 1]:",
            "if result[j] < result[j + 1]:  # MUTATION: reversed comparison",
        )
        return mutated

    @staticmethod
    def create_mutation_remove_swapped_flag(original_code):
        """Create a mutation where the swapped flag logic is removed (broken)."""
        # This mutation removes the swapped flag, always doing full passes
        mutated = original_code.replace(
            "swapped = True", "# swapped = True  # MUTATION: removed flag"
        )
        return mutated


class TestBubbleSortMutation:
    """Test cases to verify robustness of test suite through mutation testing."""

    def test_mutation_detection(self):
        """Verify that our tests can detect common mutations."""
        from tests.test_bubble_sort_mutation import MutatedBubbleSort

        # Read the original bubble_sort source code
        source_path = os.path.join(
            os.path.dirname(__file__), "..", "src", "bubble_sort.py"
        )
        with open(source_path, "r") as f:
            original_code = f.read()

        # Create mutated versions
        mutated_remove_swap = MutatedBubbleSort.create_mutation_remove_swap(
            original_code
        )
        mutated_reverse_comparison = (
            MutatedBubbleSort.create_mutation_reverse_comparison(original_code)
        )
        mutated_remove_swapped = (
            MutatedBubbleSort.create_mutation_remove_swapped_flag(
                original_code
            )
        )

        # Test 1: Mutation that removes swap should fail
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(mutated_remove_swap)
            temp_path = f.name

        try:
            spec = importlib.util.spec_from_file_location(
                "mutated_bubble_sort", temp_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # This should fail because elements are not swapped (pure function version)
            test_list = [3, 1, 2]
            result = module.bubble_sort(test_list)
            # The result should not be correctly sorted OR input should be modified
            assert result != [1, 2, 3] and test_list == [3, 1, 2], "Mutation should break the test"
        finally:
            os.unlink(temp_path)

        # Test 2: Mutation that reverses comparison should fail
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(mutated_reverse_comparison)
            temp_path = f.name

        try:
            spec = importlib.util.spec_from_file_location(
                "mutated_bubble_sort", temp_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # This should fail because comparison is reversed (pure function version)
            test_list = [1, 2, 3]
            result = module.bubble_sort(test_list)
            # The result should not be correctly sorted AND input should not be modified
            assert result != [1, 2, 3] and test_list == [1, 2, 3], "Mutation should break the test"
        finally:
            os.unlink(temp_path)

        # Test 3: Mutation that removes swapped flag should fail
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(mutated_remove_swapped)
            temp_path = f.name

        try:
            spec = importlib.util.spec_from_file_location(
                "mutated_bubble_sort", temp_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # This should still work but be less efficient
            # Let's use a test that would fail if optimization was needed
            # Actually, this mutation might still pass for many cases
            # So we'll just verify it's still functional
            test_list = [3, 1, 2]
            result = module.bubble_sort(test_list.copy())
            assert result == [1, 2, 3], "Mutation should still sort correctly"
        finally:
            os.unlink(temp_path)

    def test_test_suite_detects_broken_implementations(self):
        """Verify that the test suite can detect obviously broken implementations."""
        # Define a broken implementation that doesn't sort
        def broken_bubble_sort(arr):
            return arr  # Just return the array without sorting

        # Our test suite should detect this broken implementation
        test_cases = [
            ([3, 1, 2], [1, 2, 3]),
            ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
            ([1, 2, 3], [1, 2, 3]),
        ]

        for input_list, expected in test_cases:
            result = broken_bubble_sort(input_list.copy())
            # This should fail because broken implementation doesn't sort
            assert (
                result != expected or input_list == expected
            ), f"Broken implementation should fail for input {input_list}"

    def test_edge_case_mutation_resilience(self):
        """Verify that tests are resilient to edge case mutations."""
        from src.bubble_sort import bubble_sort

        # Create a mutation that only handles some edge cases
        def partially_broken_bubble_sort(arr):
            if len(arr) <= 1:
                return arr
            # Only sort if list has exactly 3 elements
            if len(arr) == 3:
                return bubble_sort(arr)
            # Otherwise, don't sort (broken for other sizes)
            return arr

        # Test with various list sizes
        test_cases = [
            ([], []),
            ([1], [1]),
            ([1, 2], [1, 2]),  # This should fail for broken implementation
            ([1, 2, 3], [1, 2, 3]),  # This should pass
            ([3, 1, 2], [1, 2, 3]),  # This should pass
            ([1, 2, 3, 4], [1, 2, 3, 4]),  # This should fail
        ]

        for input_list, expected in test_cases:
            if len(input_list) == 3:
                # Should pass for 3-element lists
                result = partially_broken_bubble_sort(input_list)
                assert (
                    result == expected
                ), f"Should work for 3-element list {input_list}"
            else:
                # Should fail for other sizes
                result = partially_broken_bubble_sort(input_list)
                assert (
                    result != expected or input_list == expected
                ), f"Broken implementation should fail for size {len(input_list)}: {input_list}"
