"""Integration test suite for complete workflows.

Tests cover:
- End-to-end workflows
- Multi-module integration
- CLI integration with core functionality
- Real-world usage scenarios
"""

import pytest
from pathlib import Path
import sys
import subprocess
from unittest.mock import patch
from io import StringIO


class TestEndToEndSorting:
    """Test end-to-end sorting workflows."""

    def test_complete_sorting_workflow(self):
        """Test complete sorting from CLI input to output."""
        # Add src to path
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))

        from src.bubblesort.bubble_sort import bubble_sort
        from src.cli import main, parse_args, validate_input

        # Test the full workflow: validate -> sort -> output
        input_numbers = ['5', '3', '8', '1', '4']
        validated = validate_input(input_numbers)
        sorted_result = bubble_sort(validated)

        assert sorted_result == [1, 3, 4, 5, 8]

    def test_cli_to_sorting_pipeline(self):
        """Test CLI parsing to sorting pipeline."""
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))

        from src.cli import parse_args, validate_input
        from src.bubblesort.bubble_sort import bubble_sort

        args = parse_args(['10', '2', '7', '1', '5'])
        numbers = validate_input(args.numbers)
        result = bubble_sort(numbers)

        assert result == [1, 2, 5, 7, 10]

    def test_edge_case_through_pipeline(self):
        """Test edge cases through the full pipeline."""
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))

        from src.bubblesort.bubble_sort import bubble_sort
        from src.cli import validate_input

        # Test empty list
        validated = validate_input([])
        result = bubble_sort(validated)
        assert result == []

        # Test single element
        validated = validate_input(['42'])
        result = bubble_sort(validated)
        assert result == [42]

        # Test duplicates
        validated = validate_input(['5', '1', '5', '3', '1'])
        result = bubble_sort(validated)
        assert result == [1, 1, 3, 5, 5]


class TestCLIModuleIntegration:
    """Test CLI module integration with core functionality."""

    @patch('sys.stdout', new_callable=StringIO)
    def test_main_function_integration(self, mock_stdout):
        """Test that main function integrates all components."""
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))

        from src.cli import main

        with patch('sys.argv', ['cli.py', '4', '2', '6', '1']):
            main()

        output = mock_stdout.getvalue()
        assert '[1, 2, 4, 6]' in output

    def test_module_imports_work_together(self):
        """Test that modules can be imported and used together."""
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))

        # Import both modules
        from src.bubblesort.bubble_sort import bubble_sort
        from src.cli import parse_args, validate_input

        # Use them together
        args = parse_args(['9', '1', '6', '3'])
        numbers = validate_input(args.numbers)
        result = bubble_sort(numbers)

        assert result == [1, 3, 6, 9]

    def test_function_call_chain(self):
        """Test function call chain from CLI to sorting."""
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))

        from src.cli import parse_args, validate_input
        from src.bubblesort.bubble_sort import bubble_sort

        # Chain: parse_args -> validate_input -> bubble_sort
        args = parse_args(['8', '5', '12', '3'])
        validated = validate_input(args.numbers)
        sorted_data = bubble_sort(validated)

        assert sorted_data == [3, 5, 8, 12]


class TestPackageIntegration:
    """Test package-level integration."""

    def test_package_import_integration(self):
        """Test that packages can be imported and work together."""
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))

        # Import subpackage
        import src.bubblesort as bs
        from src import cli

        # Use both
        result = bs.bubble_sort.bubble_sort([3, 1, 2])
        assert result == [1, 2, 3]

        # Check CLI is accessible
        assert hasattr(cli, 'main')
        assert hasattr(cli, 'parse_args')

    def test_bubblesort_package_structure(self):
        """Test bubblesort package structure integration."""
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))

        import src.bubblesort

        # Package should have the module
        assert hasattr(src.bubblesort, 'bubble_sort')

        # Module should have the function
        from src.bubblesort.bubble_sort import bubble_sort

        # Function should work
        result = bubble_sort([5, 2, 8, 1])
        assert result == [1, 2, 5, 8]


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_user_sorting_numbers(self):
        """Test scenario: user wants to sort a list of numbers."""
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))

        from src.bubblesort.bubble_sort import bubble_sort

        # User has a list of test scores
        scores = [85, 92, 78, 96, 88, 73, 91]
        sorted_scores = bubble_sort(scores)

        assert sorted_scores == [73, 78, 85, 88, 91, 92, 96]

    def test_user_processing_data_from_cli(self):
        """Test scenario: user processes data via CLI."""
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))

        from src.cli import parse_args, validate_input
        from src.bubblesort.bubble_sort import bubble_sort

        # User provides temperatures: 72, 68, 71, 70, 69
        args = parse_args(['72', '68', '71', '70', '69'])
        temps = validate_input(args.numbers)
        sorted_temps = bubble_sort(temps)

        assert sorted_temps == [68, 69, 70, 71, 72]

    def test_batch_processing(self):
        """Test scenario: batch processing multiple lists."""
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))

        from src.bubblesort.bubble_sort import bubble_sort

        # Multiple lists to sort
        lists = [
            [3, 1, 2],
            [9, 5, 7],
            [6, 4, 8, 2]
        ]

        # Sort each list
        sorted_lists = [bubble_sort(lst) for lst in lists]

        assert sorted_lists == [
            [1, 2, 3],
            [5, 7, 9],
            [2, 4, 6, 8]
        ]

    def test_data_analysis_workflow(self):
        """Test scenario: simple data analysis workflow."""
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))

        from src.bubblesort.bubble_sort import bubble_sort

        # Data: response times in milliseconds
        response_times = [45, 123, 67, 234, 89, 12, 156]

        # Sort for analysis
        sorted_times = bubble_sort(response_times)

        # Calculate statistics
        min_time = sorted_times[0]
        max_time = sorted_times[-1]
        median = sorted_times[len(sorted_times) // 2]

        assert min_time == 12
        assert max_time == 234
        assert median == 89


class TestWorkflowValidation:
    """Test workflow validation and error handling."""

    def test_error_propagation(self):
        """Test that errors propagate correctly through the workflow."""
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))

        from src.bubblesort.bubble_sort import bubble_sort

        # Invalid input should raise error
        with pytest.raises(TypeError):
            bubble_sort(None)

    def test_validation_before_processing(self):
        """Test that validation happens before processing."""
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))

        from src.cli import validate_input

        # Valid input should work
        result = validate_input(['1', '2', '3'])
        assert result == [1, 2, 3]

        # Invalid input should raise error
        with pytest.raises(ValueError):
            validate_input(['not_a_number'])

    def test_cli_error_handling(self):
        """Test that CLI errors are handled gracefully."""
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))

        from src.cli import parse_args

        # No arguments should fail
        with pytest.raises(SystemExit):
            parse_args([])


class TestCrossModuleConsistency:
    """Test consistency across modules."""

    def test_sorting_algorithm_consistency(self):
        """Test that sorting produces consistent results."""
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))

        from src.bubblesort.bubble_sort import bubble_sort

        test_data = [5, 1, 4, 2, 8, 3, 7]

        # Sort multiple times, should be consistent
        result1 = bubble_sort(test_data.copy())
        result2 = bubble_sort(test_data.copy())
        result3 = bubble_sort(test_data.copy())

        assert result1 == result2 == result3 == [1, 2, 3, 4, 5, 7, 8]

    def test_algorithm_properties(self):
        """Test that algorithm maintains mathematical properties."""
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))

        from src.bubblesort.bubble_sort import bubble_sort

        # Property 1: Sorting twice should give same result
        data = [3, 1, 4, 1, 5, 9, 2, 6]
        result1 = bubble_sort(data)
        result2 = bubble_sort(result1)

        assert result1 == result2

        # Property 2: Output is sorted
        assert result1 == sorted(result1)

        # Property 3: All elements preserved
        assert sorted(result1) == sorted(data)

    def test_cli_and_direct_consistency(self):
        """Test that CLI and direct function calls give same results."""
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))

        from src.bubblesort.bubble_sort import bubble_sort
        from src.cli import validate_input

        test_input = ['10', '5', '20', '15', '2']

        # Method 1: Direct function call
        direct_result = bubble_sort([10, 5, 20, 15, 2])

        # Method 2: Via CLI validation
        cli_result = bubble_sort(validate_input(test_input))

        assert direct_result == cli_result == [2, 5, 10, 15, 20]


class TestPerformanceIntegration:
    """Test performance-related integration."""

    def test_large_dataset_integration(self):
        """Test integration with larger datasets."""
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))

        from src.bubblesort.bubble_sort import bubble_sort

        # Create a large sorted list
        import random
        random.seed(42)
        large_data = [random.randint(1, 1000) for _ in range(100)]

        result = bubble_sort(large_data)

        # Verify it's sorted
        assert result == sorted(large_data)

    def test_memory_efficiency(self):
        """Test that sorting doesn't modify input."""
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))

        from src.bubblesort.bubble_sort import bubble_sort

        # Original data
        original = [5, 2, 8, 1, 9]
        original_copy = original.copy()

        # Sort
        result = bubble_sort(original)

        # Original should be unchanged
        assert original == original_copy

        # Result should be different
        assert result != original

        # Result should be sorted
        assert result == [1, 2, 5, 8, 9]


class TestWorkflowCompleteness:
    """Test that workflows are complete and functional."""

    def test_user_can_complete_task(self):
        """Test that a user can complete the sorting task end-to-end."""
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))

        from src.bubblesort.bubble_sort import bubble_sort

        # User task: Sort student grades
        grades = [87, 92, 78, 95, 83, 89, 91, 76, 88, 94]

        # User action: Sort grades
        sorted_grades = bubble_sort(grades)

        # Verify task completed successfully
        assert sorted_grades == [76, 78, 83, 87, 88, 89, 91, 92, 94, 95]

    def test_developer_can_import_and_use(self):
        """Test that developer can import and use the package."""
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))

        # Developer imports
        from src.bubblesort.bubble_sort import bubble_sort
        from src.cli import main

        # Developer uses bubble_sort
        numbers = [4, 2, 7, 1, 5]
        result = bubble_sort(numbers)
        assert result == [1, 2, 4, 5, 7]

    def test_all_entry_points_work(self):
        """Test that all entry points are functional."""
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))

        # Test direct import
        from src.bubblesort.bubble_sort import bubble_sort

        # Test package import
        import src.bubblesort.bubble_sort as bs_module

        # Both should work
        result1 = bubble_sort([3, 1, 2])
        result2 = bs_module.bubble_sort([3, 1, 2])

        assert result1 == result2 == [1, 2, 3]
