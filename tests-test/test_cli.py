"""Tests for CLI module."""

import argparse
import json
import os
import sys
import tempfile
from unittest import mock

import pytest

from src.bubblesort.cli import (
    batch_mode,
    format_output,
    get_input_data,
    get_sorting_steps,
    interactive_mode,
    main,
    parse_array_input,
    read_from_file,
    validate_data,
)


class TestParseArrayInput:
    """Test suite for parse_array_input function."""

    def test_valid_comma_separated(self):
        """Test parsing comma-separated values."""
        assert parse_array_input("1, 2, 3") == [1, 2, 3]
        assert parse_array_input("1,2,3") == [1, 2, 3]

    def test_valid_space_separated(self):
        """Test parsing space-separated values."""
        assert parse_array_input("1 2 3") == [1, 2, 3]

    def test_bracketed_input(self):
        """Test parsing bracketed input."""
        assert parse_array_input("[1, 2, 3]") == [1, 2, 3]

    def test_mixed_separators(self):
        """Test parsing with mixed separators."""
        assert parse_array_input("1,2 3,4") == [1, 2, 3, 4]

    def test_float_values(self):
        """Test parsing float values."""
        assert parse_array_input("1.5, 2.3, 3.7") == [1.5, 2.3, 3.7]

    def test_mixed_int_float(self):
        """Test parsing mixed integers and floats."""
        assert parse_array_input("1, 2.5, 3") == [1, 2.5, 3]

    def test_negative_numbers(self):
        """Test parsing negative numbers."""
        assert parse_array_input("-1, -2, -3") == [-1, -2, -3]
        assert parse_array_input("1, -2, 3") == [1, -2, 3]

    def test_empty_input_raises_error(self):
        """Test that empty input raises ValueError."""
        with pytest.raises(ValueError, match="Empty input"):
            parse_array_input("")

    def test_whitespace_only_raises_error(self):
        """Test that whitespace-only input raises ValueError."""
        with pytest.raises(ValueError, match="Empty input"):
            parse_array_input("   ")

    def test_invalid_number_raises_error(self):
        """Test that invalid numbers raise ValueError."""
        with pytest.raises(ValueError, match="Invalid number"):
            parse_array_input("1, abc, 3")

    def test_only_commas_raises_error(self):
        """Test that only commas raises ValueError."""
        with pytest.raises(ValueError, match="Empty input"):
            parse_array_input(",,,")

    def test_single_number(self):
        """Test parsing a single number."""
        assert parse_array_input("42") == [42]

    def test_zero(self):
        """Test parsing zero."""
        assert parse_array_input("0") == [0]
        assert parse_array_input("0.0") == [0.0]

    def test_large_numbers(self):
        """Test parsing large numbers."""
        assert parse_array_input("1000000, 2000000, 3000000") == [
            1000000,
            2000000,
            3000000,
        ]

    def test_scientific_notation(self):
        """Test parsing numbers in scientific notation."""
        result = parse_array_input("1e3, 2e3")
        assert result == [1000.0, 2000.0]


class TestReadFromFile:
    """Test suite for read_from_file function."""

    def test_read_valid_file(self):
        """Test reading a valid file with numbers."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("1, 2, 3")
            temp_path = f.name

        try:
            result = read_from_file(temp_path)
            assert result == [1, 2, 3]
        finally:
            os.unlink(temp_path)

    def test_read_file_with_brackets(self):
        """Test reading a file with bracketed numbers."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("[1, 2, 3]")
            temp_path = f.name

        try:
            result = read_from_file(temp_path)
            assert result == [1, 2, 3]
        finally:
            os.unlink(temp_path)

    def test_read_empty_file_raises_error(self):
        """Test that reading an empty file raises ValueError."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="File is empty"):
                read_from_file(temp_path)
        finally:
            os.unlink(temp_path)

    def test_read_nonexistent_file_raises_error(self):
        """Test that reading a nonexistent file raises ValueError."""
        with pytest.raises(ValueError, match="Error reading file"):
            read_from_file("/nonexistent/file.txt")

    def test_read_file_with_multiple_lines(self):
        """Test reading from file with multiple lines."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("1, 2, 3\n4, 5, 6")
            temp_path = f.name

        try:
            result = read_from_file(temp_path)
            assert result == [1, 2, 3, 4, 5, 6]
        finally:
            os.unlink(temp_path)


class TestGetSortingSteps:
    """Test suite for get_sorting_steps function."""

    def test_empty_list(self):
        """Test getting steps for empty list."""
        assert get_sorting_steps([]) == [[]]

    def test_single_element(self):
        """Test getting steps for single element."""
        assert get_sorting_steps([1]) == [[1]]

    def test_already_sorted(self):
        """Test getting steps for already sorted list."""
        steps = get_sorting_steps([1, 2, 3])
        assert steps[0] == [1, 2, 3]
        assert len(steps) == 1  # No swaps needed

    def test_reverse_sorted(self):
        """Test getting steps for reverse sorted list."""
        steps = get_sorting_steps([3, 2, 1])
        assert steps[0] == [3, 2, 1]
        assert steps[-1] == [1, 2, 3]
        # Should have multiple steps
        assert len(steps) > 1

    def test_two_elements_unsorted(self):
        """Test getting steps for two unsorted elements."""
        steps = get_sorting_steps([2, 1])
        assert steps[0] == [2, 1]
        assert steps[-1] == [1, 2]

    def test_duplicate_elements(self):
        """Test getting steps for list with duplicates."""
        steps = get_sorting_steps([2, 1, 2])
        assert steps[0] == [2, 1, 2]
        assert steps[-1] == [1, 2, 2]

    def test_large_list(self):
        """Test getting steps for a larger list."""
        data = [5, 1, 4, 2, 8]
        steps = get_sorting_steps(data)
        assert len(steps) > 1
        assert steps[0] == [5, 1, 4, 2, 8]
        assert steps[-1] == [1, 2, 4, 5, 8]


class TestFormatOutput:
    """Test suite for format_output function."""

    def test_default_format(self):
        """Test default output format."""
        output = format_output([3, 1, 2], [1, 2, 3])
        assert output == "[1, 2, 3]"

    def test_json_format(self):
        """Test JSON output format."""
        output = format_output([3, 1, 2], [1, 2, 3], format_type="json")
        result = json.loads(output)
        assert result["input"] == [3, 1, 2]
        assert result["sorted"] == [1, 2, 3]

    def test_json_format_with_stats(self):
        """Test JSON output format with statistics."""
        output = format_output(
            [3, 1, 2], [1, 2, 3], format_type="json", show_stats=True
        )
        result = json.loads(output)
        assert "input" in result
        assert "sorted" in result
        assert "statistics" in result

    def test_steps_format(self):
        """Test steps output format."""
        output = format_output([3, 1, 2], [1, 2, 3], format_type="steps")
        assert "Sorting Steps:" in output
        assert "Step 0: [3, 1, 2]" in output

    def test_detailed_format(self):
        """Test detailed output format."""
        output = format_output([3, 1, 2], [1, 2, 3], format_type="detailed")
        assert "Input: [3, 1, 2]" in output
        assert "Sorted: [1, 2, 3]" in output

    def test_detailed_format_with_stats(self):
        """Test detailed output format with statistics."""
        output = format_output(
            [3, 1, 2], [1, 2, 3], format_type="detailed", show_stats=True
        )
        assert "Input: [3, 1, 2]" in output
        assert "Sorted: [1, 2, 3]" in output
        assert "Comparisons:" in output
        assert "Steps:" in output

    def test_json_format_all_numeric_types(self):
        """Test JSON format with mixed numeric types."""
        output = format_output([1, 2.5, -3], [1, 2.5, -3], format_type="json")
        result = json.loads(output)
        assert result["input"] == [1, 2.5, -3]
        assert result["sorted"] == [1, 2.5, -3]


class TestValidateData:
    """Test suite for validate_data function."""

    def test_valid_data_passes(self):
        """Test that valid data passes validation."""
        validate_data([1, 2, 3])  # Should not raise

    def test_empty_list_raises_error(self):
        """Test that empty list raises ValueError."""
        with pytest.raises(ValueError, match="No data to sort"):
            validate_data([])

    def test_oversized_list_raises_error(self):
        """Test that oversized list raises ValueError."""
        large_list = list(range(10001))
        with pytest.raises(ValueError, match="List too long"):
            validate_data(large_list)

    def test_non_numeric_value_raises_error(self):
        """Test that non-numeric value raises ValueError."""
        with pytest.raises(ValueError, match="Non-numeric value found"):
            validate_data([1, 2, "three"])

    def test_mixed_types_valid(self):
        """Test that mixed int/float types are valid."""
        validate_data([1, 2.5, 3])  # Should not raise

    def test_negative_numbers_valid(self):
        """Test that negative numbers are valid."""
        validate_data([-1, -2, -3])  # Should not raise

    def test_zero_is_valid(self):
        """Test that zero is valid."""
        validate_data([0, 0, 0])  # Should not raise


class TestGetInputData:
    """Test suite for get_input_data function."""

    def test_get_input_from_array_arg(self):
        """Test getting input from command line array argument."""
        mock_args = mock.MagicMock()
        mock_args.array = "1, 2, 3"
        mock_args.file = None
        mock_args.interactive = False

        result = get_input_data(mock_args)
        assert result == [1, 2, 3]

    def test_get_input_from_file(self):
        """Test getting input from file argument."""
        mock_args = mock.MagicMock()
        mock_args.array = None
        mock_args.file = "test.txt"
        mock_args.interactive = False

        with mock.patch("src.bubblesort.cli.read_from_file", return_value=[4, 5, 6]):
            result = get_input_data(mock_args)
            assert result == [4, 5, 6]

    def test_get_input_from_interactive(self):
        """Test getting input from interactive mode."""
        mock_args = mock.MagicMock()
        mock_args.array = None
        mock_args.file = None
        mock_args.interactive = True

        result = get_input_data(mock_args)
        assert result == []

    def test_get_input_from_stdin(self):
        """Test getting input from stdin."""
        mock_args = mock.MagicMock()
        mock_args.array = None
        mock_args.file = None
        mock_args.interactive = False

        with mock.patch("src.bubblesort.cli.sys.stdin.isatty", return_value=False):
            with mock.patch("src.bubblesort.cli.sys.stdin.read", return_value="7, 8, 9"):
                result = get_input_data(mock_args)
                assert result == [7, 8, 9]

    def test_get_input_no_input_raises_error(self):
        """Test that no input raises ValueError."""
        mock_args = mock.MagicMock()
        mock_args.array = None
        mock_args.file = None
        mock_args.interactive = False

        with mock.patch("src.bubblesort.cli.sys.stdin.isatty", return_value=True):
            with pytest.raises(ValueError, match="No input provided"):
                get_input_data(mock_args)

    def test_get_input_stdin_empty_raises_error(self):
        """Test that empty stdin raises ValueError."""
        mock_args = mock.MagicMock()
        mock_args.array = None
        mock_args.file = None
        mock_args.interactive = False

        with mock.patch("src.bubblesort.cli.sys.stdin.isatty", return_value=False):
            with mock.patch("src.bubblesort.cli.sys.stdin.read", return_value=""):
                with pytest.raises(ValueError, match="No input received from stdin"):
                    get_input_data(mock_args)


class TestInteractiveMode:
    """Test suite for interactive_mode function."""

    @pytest.mark.parametrize("exit_command", ["quit", "exit", "q"])
    def test_interactive_quit_commands(self, exit_command):
        """Test interactive mode exits with quit commands."""
        with mock.patch("builtins.input", side_effect=[exit_command]):
            with mock.patch("src.bubblesort.cli.print"):
                try:
                    interactive_mode()
                except SystemExit:
                    pass

    def test_interactive_process_valid_input(self):
        """Test interactive mode processes valid input."""
        with mock.patch("builtins.input", side_effect=["1, 2, 3", "quit"]):
            with mock.patch("src.bubblesort.cli.print"):
                with mock.patch("src.bubblesort.cli.parse_array_input", return_value=[1, 2, 3]):
                    with mock.patch("src.bubblesort.cli.validate_data"):
                        with mock.patch("src.bubblesort.cli.bubble_sort", return_value=[1, 2, 3]):
                            try:
                                interactive_mode()
                            except SystemExit:
                                pass

    def test_interactive_handles_invalid_input(self):
        """Test interactive mode handles invalid input."""
        with mock.patch("builtins.input", side_effect=["invalid", "quit"]):
            with mock.patch("src.bubblesort.cli.print"):
                with mock.patch(
                    "src.bubblesort.cli.parse_array_input",
                    side_effect=ValueError("Invalid number"),
                ):
                    try:
                        interactive_mode()
                    except SystemExit:
                        pass

    def test_interactive_keyboard_interrupt(self):
        """Test interactive mode handles keyboard interrupt."""
        with mock.patch("builtins.input", side_effect=KeyboardInterrupt()):
            with mock.patch("src.bubblesort.cli.print") as mock_print:
                interactive_mode()
                mock_print.assert_called_with("\nGoodbye!")


class TestBatchMode:
    """Test suite for batch_mode function."""

    @pytest.mark.parametrize("exit_command", ["quit", "exit", "q"])
    def test_batch_quit_commands(self, exit_command):
        """Test batch mode exits with quit commands."""
        with mock.patch("builtins.input", side_effect=[exit_command]):
            with mock.patch("src.bubblesort.cli.print"):
                try:
                    batch_mode()
                except SystemExit:
                    pass

    def test_batch_process_valid_file(self):
        """Test batch mode processes valid file."""
        with mock.patch("builtins.input", side_effect=["test.txt", "quit"]):
            with mock.patch("src.bubblesort.cli.print"):
                with mock.patch("src.bubblesort.cli.read_from_file", return_value=[1, 2, 3]):
                    with mock.patch("src.bubblesort.cli.validate_data"):
                        with mock.patch("src.bubblesort.cli.bubble_sort", return_value=[1, 2, 3]):
                            try:
                                batch_mode()
                            except SystemExit:
                                pass

    def test_batch_handles_file_error(self):
        """Test batch mode handles file errors."""
        with mock.patch("builtins.input", side_effect=["nonexistent.txt", "quit"]):
            with mock.patch("src.bubblesort.cli.print"):
                with mock.patch(
                    "src.bubblesort.cli.read_from_file",
                    side_effect=FileNotFoundError("File not found"),
                ):
                    try:
                        batch_mode()
                    except SystemExit:
                        pass

    def test_batch_keyboard_interrupt(self):
        """Test batch mode handles keyboard interrupt."""
        with mock.patch("builtins.input", side_effect=KeyboardInterrupt()):
            with mock.patch("src.bubblesort.cli.print") as mock_print:
                batch_mode()
                mock_print.assert_called_with("\nGoodbye!")


class TestMainFunction:
    """Test suite for main function."""

    def test_main_with_array_arg(self):
        """Test main function with array argument."""
        with mock.patch(
            "argparse.ArgumentParser.parse_args",
            return_value=mock.MagicMock(
                array="1, 2, 3",
                file=None,
                interactive=False,
                batch=False,
                format="default",
                stats=False,
            ),
        ):
            with mock.patch("src.bubblesort.cli.get_input_data", return_value=[1, 2, 3]):
                with mock.patch("src.bubblesort.cli.validate_data"):
                    with mock.patch("src.bubblesort.cli.bubble_sort", return_value=[1, 2, 3]):
                        with mock.patch(
                            "src.bubblesort.cli.format_output", return_value="[1, 2, 3]"
                        ):
                            with mock.patch("src.bubblesort.cli.print"):
                                main()

    def test_main_with_interactive_flag(self):
        """Test main function with interactive flag."""
        with mock.patch(
            "argparse.ArgumentParser.parse_args",
            return_value=mock.MagicMock(
                array=None,
                file=None,
                interactive=True,
                batch=False,
                format="default",
                stats=False,
            ),
        ):
            with mock.patch("src.bubblesort.cli.interactive_mode"):
                main()

    def test_main_with_batch_flag(self):
        """Test main function with batch flag."""
        with mock.patch(
            "argparse.ArgumentParser.parse_args",
            return_value=mock.MagicMock(
                array=None,
                file=None,
                interactive=False,
                batch=True,
                format="default",
                stats=False,
            ),
        ):
            with mock.patch("src.bubblesort.cli.batch_mode"):
                main()

    def test_main_handles_file_not_found(self):
        """Test main function handles file not found error."""
        with mock.patch(
            "argparse.ArgumentParser.parse_args",
            return_value=mock.MagicMock(
                array="1, 2, 3",
                file=None,
                interactive=False,
                batch=False,
                format="default",
                stats=False,
            ),
        ):
            with mock.patch(
                "src.bubblesort.cli.get_input_data",
                side_effect=FileNotFoundError("File not found"),
            ):
                with mock.patch("src.bubblesort.cli.sys.exit") as mock_exit:
                    main()
                    mock_exit.assert_called_with(1)

    def test_main_handles_value_error(self):
        """Test main function handles value error."""
        with mock.patch(
            "argparse.ArgumentParser.parse_args",
            return_value=mock.MagicMock(
                array="1, 2, 3",
                file=None,
                interactive=False,
                batch=False,
                format="default",
                stats=False,
            ),
        ):
            with mock.patch(
                "src.bubblesort.cli.get_input_data",
                side_effect=ValueError("Invalid input"),
            ):
                with mock.patch("src.bubblesort.cli.sys.exit") as mock_exit:
                    main()
                    mock_exit.assert_called_with(1)

    def test_main_handles_keyboard_interrupt(self):
        """Test main function handles keyboard interrupt."""
        with mock.patch(
            "argparse.ArgumentParser.parse_args",
            return_value=mock.MagicMock(
                array="1, 2, 3",
                file=None,
                interactive=False,
                batch=False,
                format="default",
                stats=False,
            ),
        ):
            with mock.patch(
                "src.bubblesort.cli.get_input_data",
                side_effect=KeyboardInterrupt(),
            ):
                with mock.patch("src.bubblesort.cli.sys.exit") as mock_exit:
                    main()
                    mock_exit.assert_called_with(130)

    def test_main_handles_unexpected_error(self):
        """Test main function handles unexpected errors."""
        with mock.patch(
            "argparse.ArgumentParser.parse_args",
            return_value=mock.MagicMock(
                array="1, 2, 3",
                file=None,
                interactive=False,
                batch=False,
                format="default",
                stats=False,
            ),
        ):
            with mock.patch(
                "src.bubblesort.cli.get_input_data",
                side_effect=RuntimeError("Unexpected error"),
            ):
                with mock.patch("src.bubblesort.cli.sys.exit") as mock_exit:
                    main()
                    mock_exit.assert_called_with(1)
