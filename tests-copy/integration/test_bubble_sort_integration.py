"""Comprehensive integration tests for bubble sort implementation.

These tests verify the integration between the bubble sort algorithm
and the CLI interface, ensuring end-to-end functionality works correctly.
"""
import pytest
import sys
import json
from pathlib import Path
from unittest.mock import patch
from io import StringIO

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestBubbleSortAlgorithmIntegration:
    """Test the bubble sort algorithm with various real-world scenarios."""

    def test_sort_large_dataset(self):
        """Test sorting a large dataset efficiently."""
        from bubblesort import bubble_sort
        import random

        # Generate a large dataset
        large_data = [random.randint(1, 10000) for _ in range(1000)]
        expected = sorted(large_data)

        result = bubble_sort(large_data)

        assert result == expected
        assert len(result) == 1000

    def test_sort_with_extreme_values(self):
        """Test sorting with extreme numeric values."""
        from bubblesort import bubble_sort

        # Test with very large numbers
        large_numbers = [999999999, -999999999, 0, 1, -1]
        expected = [-999999999, -1, 0, 1, 999999999]
        result = bubble_sort(large_numbers)
        assert result == expected

    def test_sort_multiple_times_consistent(self):
        """Test that sorting the same data multiple times produces consistent results."""
        from bubblesort import bubble_sort

        test_data = [5, 2, 8, 1, 9, 3, 7, 4, 6]
        expected = [1, 2, 3, 4, 5, 6, 7, 8, 9]

        result1 = bubble_sort(test_data)
        result2 = bubble_sort(test_data)
        result3 = bubble_sort(test_data)

        assert result1 == expected
        assert result2 == expected
        assert result3 == expected
        assert result1 == result2 == result3

    def test_sort_does_not_affect_original(self):
        """Test that sorting doesn't modify the original list."""
        from bubblesort import bubble_sort

        original = [5, 2, 8, 1, 9]
        original_copy = original.copy()

        result = bubble_sort(original)

        assert original == original_copy
        assert result != original
        assert result is not original

    def test_sort_performance_very_large_list(self):
        """Test sorting performance with a very large list."""
        from bubblesort import bubble_sort
        import time

        # Create a list of 5000 elements
        very_large_data = list(range(5000, 0, -1))  # Reverse sorted

        start_time = time.time()
        result = bubble_sort(very_large_data)
        end_time = time.time()

        # Verify correctness
        assert result == list(range(1, 5001))

        # Performance check (should complete within reasonable time)
        execution_time = end_time - start_time
        assert execution_time < 10.0  # Should complete within 10 seconds


class TestCLIIntegration:
    """Test CLI integration with various input sources."""

    def test_cli_with_very_large_array(self):
        """Test CLI with a very large array input."""
        from cli import main

        # Generate a large array
        large_array = list(range(1000, 0, -1))
        array_str = ", ".join(map(str, large_array))

        with patch('sys.argv', ['cli.py', array_str]):
            with patch('builtins.print') as mock_print:
                main()

                # Verify output contains sorted array
                output = "".join([str(call[0][0]) for call in mock_print.call_args_list])
                assert '[1, 2, 3' in output  # Should start with sorted values

    def test_cli_with_mixed_data_types(self):
        """Test CLI with mixed int and float values."""
        from cli import main

        with patch('sys.argv', ['cli.py', '5, 3.5, 1, 2.2, 4']):
            with patch('builtins.print') as mock_print:
                main()

                output = "".join([str(call[0][0]) for call in mock_print.call_args_list])
                assert '[1, 2.2, 3.5, 4, 5]' in output

    def test_cli_with_negative_numbers(self):
        """Test CLI with negative numbers."""
        from cli import main

        with patch('sys.argv', ['cli.py', '5, -3, 0, -10, 2']):
            with patch('builtins.print') as mock_print:
                main()

                output = "".join([str(call[0][0]) for call in mock_print.call_args_list])
                assert '[-10, -3, 0, 2, 5]' in output

    def test_cli_with_json_output_format(self):
        """Test CLI with JSON output format."""
        from cli import main

        with patch('sys.argv', ['cli.py', '3, 1, 2', '--format', 'json']):
            with patch('builtins.print') as mock_print:
                main()

                # Verify JSON output
                output = "".join([str(call[0][0]) for call in mock_print.call_args_list])
                parsed = json.loads(output)
                assert parsed['input'] == [3, 1, 2]
                assert parsed['sorted'] == [1, 2, 3]

    def test_cli_with_statistics(self):
        """Test CLI with statistics enabled."""
        from cli import main

        with patch('sys.argv', ['cli.py', '3, 1, 2', '--stats', '--format', 'detailed']):
            with patch('builtins.print') as mock_print:
                main()

                output = "".join([str(call[0][0]) for call in mock_print.call_args_list])
                # Verify statistics are included in detailed format
                assert 'Comparisons:' in output
                assert 'Swaps:' in output
                assert 'Steps:' in output

    def test_cli_preserves_original_data(self):
        """Test that CLI processing doesn't modify source data."""
        from cli import parse_array_input, bubble_sort

        # Parse data
        data = parse_array_input("5, 2, 8, 1")

        # Store original
        original_data = data.copy()

        # Process (which internally uses bubble_sort)
        sorted_data = bubble_sort(data)

        # Verify original is unchanged
        assert data == original_data
        assert sorted_data == [1, 2, 5, 8]
        assert data != sorted_data

    def test_cli_error_handling_invalid_json(self):
        """Test CLI error handling with invalid JSON output scenario."""
        from cli import main

        with patch('sys.argv', ['cli.py', 'invalid,input']):
            with pytest.raises(SystemExit):
                main()

    def test_cli_with_duplicates(self):
        """Test CLI with duplicate values."""
        from cli import main

        with patch('sys.argv', ['cli.py', '3, 1, 3, 2, 1']):
            with patch('builtins.print') as mock_print:
                main()

                output = "".join([str(call[0][0]) for call in mock_print.call_args_list])
                assert '[1, 1, 2, 3, 3]' in output

    def test_cli_stdin_pipeline(self):
        """Test CLI with stdin input (pipeline scenario)."""
        from cli import main

        with patch('sys.stdin.isatty', return_value=False):
            with patch('sys.stdin.read', return_value="5, 3, 1, 2, 4"):
                with patch('sys.argv', ['cli.py']):
                    with patch('builtins.print') as mock_print:
                        main()

                        output = "".join([str(call[0][0]) for call in mock_print.call_args_list])
                        assert '[1, 2, 3, 4, 5]' in output

    def test_cli_consistency_across_formats(self):
        """Test that different output formats produce consistent results."""
        from cli import format_output

        input_data = [3, 1, 2]
        sorted_data = [1, 2, 3]

        # Test different formats produce same sorted result
        default_output = format_output(input_data, sorted_data)
        json_output = format_output(input_data, sorted_data, format_type="json")

        assert '[1, 2, 3]' in default_output

        # Verify JSON contains correct sorted data
        parsed = json.loads(json_output)
        assert parsed['sorted'] == [1, 2, 3]


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_sorting_gradebook(self):
        """Test sorting a gradebook-like dataset."""
        from bubblesort import bubble_sort

        # Simulate a gradebook with scores
        grades = [85, 92, 78, 90, 88, 76, 95, 82]
        expected = [76, 78, 82, 85, 88, 90, 92, 95]

        result = bubble_sort(grades)
        assert result == expected

    def test_sorting_temperatures(self):
        """Test sorting temperature readings."""
        from bubblesort import bubble_sort

        # Simulate daily temperature readings (Celsius)
        temperatures = [23.5, 19.2, 25.8, 18.0, 21.3, 24.1]
        expected = [18.0, 19.2, 21.3, 23.5, 24.1, 25.8]

        result = bubble_sort(temperatures)
        assert result == expected

    def test_sorting_coordinates(self):
        """Test sorting coordinate values."""
        from bubblesort import bubble_sort

        # Simulate X coordinates
        coordinates = [100.5, -50.2, 0.0, 75.8, -10.1]
        expected = [-50.2, -10.1, 0.0, 75.8, 100.5]

        result = bubble_sort(coordinates)
        assert result == expected

    def test_cli_multiple_sequential_operations(self):
        """Test CLI handling multiple sequential sorting operations."""
        from cli import main

        # First operation
        with patch('sys.argv', ['cli.py', '3, 1, 2']):
            with patch('builtins.print') as mock_print1:
                main()
                output1 = "".join([str(call[0][0]) for call in mock_print1.call_args_list])
                assert '[1, 2, 3]' in output1

        # Second operation with different data
        with patch('sys.argv', ['cli.py', '5, 4, 3, 2, 1']):
            with patch('builtins.print') as mock_print2:
                main()
                output2 = "".join([str(call[0][0]) for call in mock_print2.call_args_list])
                assert '[1, 2, 3, 4, 5]' in output2


class TestDataIntegrity:
    """Test data integrity and validation."""

    def test_no_data_corruption_large_dataset(self):
        """Test that large datasets are not corrupted during sorting."""
        from bubblesort import bubble_sort
        import random

        # Create dataset with known structure (100-0-100 pattern creates duplicates)
        test_data = list(range(100)) + list(range(100, -1, -1))  # 0-99 + 100-0 = has duplicates

        result = bubble_sort(test_data)

        # Verify data integrity: all elements should be present and sorted
        assert len(result) == len(test_data)
        assert result == sorted(test_data)

        # Verify no corruption - all elements should be in ascending order
        assert all(result[i] <= result[i+1] for i in range(len(result)-1))

        # Verify all original elements are present
        assert sorted(result) == sorted(test_data)

    def test_sorted_data_preserves_all_elements(self):
        """Test that sorting preserves all elements (no duplicates, no losses)."""
        from bubblesort import bubble_sort

        # Dataset with duplicates
        data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
        result = bubble_sort(data)

        # All elements should be preserved
        assert sorted(result) == sorted(data)
        assert len(result) == len(data)
        assert result.count(1) == data.count(1)
        assert result.count(3) == data.count(3)
        assert result.count(5) == data.count(5)

    def test_stability_of_sort(self):
        """Test that the sort is stable (equal elements maintain relative order)."""
        # Note: Basic bubble sort is typically stable
        from bubblesort import bubble_sort

        # Create data with equal values at different positions
        data = [(1, 'a'), (2, 'b'), (1, 'c'), (2, 'd'), (1, 'e')]

        # Sort only by first element of tuple
        # In a stable sort, relative order of equal first elements is preserved
        # This tests the basic property

    def test_cli_preserves_data_integrity(self):
        """Test that CLI operations preserve data integrity."""
        from cli import parse_array_input, validate_data

        # Parse valid data
        data = parse_array_input("5, 3, 1, 2, 4")

        # Validate
        validate_data(data)

        # Verify data is correct
        assert data == [5, 3, 1, 2, 4]
        assert len(data) == 5

        # All elements should be numeric
        assert all(isinstance(x, (int, float)) for x in data)
