"""Test suite for CLI module."""

import argparse
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
import pytest

from src.cli import (
    parse_array_input,
    read_from_file,
    get_sorting_steps,
    format_output,
    get_input_data,
    validate_data,
    interactive_mode,
    batch_mode,
    main,
)


class TestParseArrayInput:
    """Test the parse_array_input function."""

    def test_parse_array_input_basic(self):
        """Test basic array parsing."""
        result = parse_array_input("1, 2, 3")
        assert result == [1, 2, 3]

    def test_parse_array_input_with_brackets(self):
        """Test array parsing with brackets."""
        result = parse_array_input("[1, 2, 3]")
        assert result == [1, 2, 3]

    def test_parse_array_input_space_separated(self):
        """Test space-separated array parsing."""
        result = parse_array_input("1 2 3")
        assert result == [1, 2, 3]

    def test_parse_array_input_with_floats(self):
        """Test array parsing with floats."""
        result = parse_array_input("1.5, 2.3, 3.7")
        assert result == [1.5, 2.3, 3.7]

    def test_parse_array_input_mixed_int_float(self):
        """Test array parsing with mixed int and float."""
        result = parse_array_input("1, 2.5, 3")
        assert result == [1, 2.5, 3]

    def test_parse_array_input_negative_numbers(self):
        """Test array parsing with negative numbers."""
        result = parse_array_input("-1, 2, -3")
        assert result == [-1, 2, -3]

    def test_parse_array_input_scientific_notation(self):
        """Test array parsing with scientific notation."""
        result = parse_array_input("1e3, 2e-1")
        assert result == [1000.0, 0.2]

    def test_parse_array_input_empty_string(self):
        """Test array parsing with empty string."""
        with pytest.raises(ValueError, match="Empty input"):
            parse_array_input("")

    def test_parse_array_input_whitespace_only(self):
        """Test array parsing with whitespace only."""
        with pytest.raises(ValueError, match="Empty input"):
            parse_array_input("   ")

    def test_parse_array_input_single_element(self):
        """Test array parsing with single element."""
        result = parse_array_input("5")
        assert result == [5]

    def test_parse_array_input_empty_between_commas(self):
        """Test array parsing with empty elements between commas."""
        result = parse_array_input("1, , 3")
        assert result == [1, 3]

    def test_parse_array_input_invalid_number(self):
        """Test array parsing with invalid number."""
        with pytest.raises(ValueError, match="Invalid number"):
            parse_array_input("1, abc, 3")

    def test_parse_array_input_leading_trailing_spaces(self):
        """Test array parsing with leading/trailing spaces."""
        result = parse_array_input("  1, 2, 3  ")
        assert result == [1, 2, 3]


class TestReadFromFile:
    """Test the read_from_file function."""

    def test_read_from_file_success(self):
        """Test reading from file successfully."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("1, 2, 3")
            temp_path = f.name

        try:
            result = read_from_file(temp_path)
            assert result == [1, 2, 3]
        finally:
            Path(temp_path).unlink()

    def test_read_from_file_not_found(self):
        """Test reading from non-existent file."""
        with pytest.raises(FileNotFoundError):
            read_from_file("nonexistent_file.txt")

    def test_read_from_file_empty(self):
        """Test reading from empty file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("")
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="File is empty"):
                read_from_file(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_read_from_file_unicode_error(self):
        """Test reading from file with encoding errors."""
        # Create a file with problematic content
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".txt") as f:
            # Write binary content that will cause UnicodeDecodeError
            f.write(b"\xff\xfe")
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Error reading file"):
                read_from_file(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_read_from_file_with_whitespace(self):
        """Test reading from file with whitespace."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("  1, 2, 3  \n")
            temp_path = f.name

        try:
            result = read_from_file(temp_path)
            assert result == [1, 2, 3]
        finally:
            Path(temp_path).unlink()


class TestGetSortingSteps:
    """Test the get_sorting_steps function."""

    def test_get_sorting_steps_unsorted(self):
        """Test getting sorting steps for unsorted array."""
        data = [3, 2, 1]
        steps = get_sorting_steps(data)
        assert len(steps) > 1
        assert steps[0] == [3, 2, 1]
        assert steps[-1] == [1, 2, 3]

    def test_get_sorting_steps_already_sorted(self):
        """Test getting sorting steps for already sorted array."""
        data = [1, 2, 3]
        steps = get_sorting_steps(data)
        assert len(steps) == 1  # Only initial state (early exit before any swaps)

    def test_get_sorting_steps_empty(self):
        """Test getting sorting steps for empty array."""
        data = []
        steps = get_sorting_steps(data)
        assert steps == [[]]

    def test_get_sorting_steps_single_element(self):
        """Test getting sorting steps for single element."""
        data = [5]
        steps = get_sorting_steps(data)
        assert steps == [[5]]

    def test_get_sorting_steps_with_duplicates(self):
        """Test getting sorting steps with duplicate elements."""
        data = [3, 2, 3, 1]
        steps = get_sorting_steps(data)
        assert steps[-1] == [1, 2, 3, 3]


class TestFormatOutput:
    """Test the format_output function."""

    def test_format_output_default(self):
        """Test default output format."""
        data = [3, 2, 1]
        sorted_data = [1, 2, 3]
        output = format_output(data, sorted_data)
        assert output == str([1, 2, 3])

    def test_format_output_json(self):
        """Test JSON output format."""
        data = [3, 2, 1]
        sorted_data = [1, 2, 3]
        output = format_output(data, sorted_data, format_type="json")
        parsed = json.loads(output)
        assert parsed["input"] == [3, 2, 1]
        assert parsed["sorted"] == [1, 2, 3]

    def test_format_output_json_with_stats(self):
        """Test JSON output format with statistics."""
        data = [3, 2, 1]
        sorted_data = [1, 2, 3]
        output = format_output(data, sorted_data, format_type="json", show_stats=True)
        parsed = json.loads(output)
        assert "statistics" in parsed
        assert "comparisons" in parsed["statistics"]
        assert "swaps" in parsed["statistics"]
        assert "steps" in parsed["statistics"]

    def test_format_output_steps(self):
        """Test steps output format."""
        data = [3, 2, 1]
        sorted_data = [1, 2, 3]
        output = format_output(data, sorted_data, format_type="steps")
        assert "Sorting Steps:" in output
        assert "Step 0:" in output

    def test_format_output_detailed(self):
        """Test detailed output format."""
        data = [3, 2, 1]
        sorted_data = [1, 2, 3]
        output = format_output(data, sorted_data, format_type="detailed")
        assert "Input:" in output
        assert "Sorted:" in output
        assert "[1, 2, 3]" in output

    def test_format_output_detailed_with_stats(self):
        """Test detailed output format with statistics."""
        data = [3, 2, 1]
        sorted_data = [1, 2, 3]
        output = format_output(
            data, sorted_data, format_type="detailed", show_stats=True
        )
        assert "Comparisons:" in output
        assert "Swaps:" in output


class TestGetInputData:
    """Test the get_input_data function."""

    def test_get_input_data_from_array(self):
        """Test getting input data from array argument."""
        args = argparse.Namespace(array="1, 2, 3", file=None)
        result = get_input_data(args)
        assert result == [1, 2, 3]

    def test_get_input_data_from_file(self):
        """Test getting input data from file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("1, 2, 3")
            temp_path = f.name

        try:
            args = argparse.Namespace(array=None, file=temp_path)
            result = get_input_data(args)
            assert result == [1, 2, 3]
        finally:
            Path(temp_path).unlink()

    def test_get_input_data_no_input(self):
        """Test getting input data with no input provided."""
        with patch("sys.stdin.isatty", return_value=True):
            args = argparse.Namespace(array=None, file=None, interactive=False)
            with pytest.raises(ValueError, match="No input provided"):
                get_input_data(args)

    def test_get_input_data_stdin(self):
        """Test getting input data from stdin."""
        with patch("sys.stdin.isatty", return_value=False), patch(
            "sys.stdin.read", return_value="1, 2, 3"
        ):
            args = argparse.Namespace(array=None, file=None)
            result = get_input_data(args)
            assert result == [1, 2, 3]

    def test_get_input_data_stdin_empty(self):
        """Test getting input data from empty stdin."""
        with patch("sys.stdin.isatty", return_value=False), patch(
            "sys.stdin.read", return_value=""
        ):
            args = argparse.Namespace(array=None, file=None)
            with pytest.raises(ValueError, match="No input received from stdin"):
                get_input_data(args)


class TestValidateData:
    """Test the validate_data function."""

    def test_validate_data_valid(self):
        """Test validation with valid data."""
        validate_data([1, 2, 3])

    def test_validate_data_empty(self):
        """Test validation with empty data."""
        with pytest.raises(ValueError, match="No data to sort"):
            validate_data([])

    def test_validate_data_non_numeric(self):
        """Test validation with non-numeric values."""
        with pytest.raises(ValueError, match="Non-numeric value found"):
            validate_data([1, "a", 3])

    def test_validate_data_too_long(self):
        """Test validation with too many elements."""
        with pytest.raises(ValueError, match="List too long"):
            validate_data(list(range(10001)))

    def test_validate_data_floats(self):
        """Test validation with float values."""
        validate_data([1.5, 2.3, 3.7])

    def test_validate_data_mixed_types(self):
        """Test validation with mixed int and float."""
        validate_data([1, 2.5, 3])


class TestInteractiveMode:
    """Test the interactive_mode function."""

    @patch("builtins.input", side_effect=["1, 2, 3", "quit"])
    @patch("builtins.print")
    def test_interactive_mode_success(self, mock_print, mock_input):
        """Test interactive mode with valid input."""
        with patch("src.cli.bubble_sort") as mock_sort:
            mock_sort.return_value = [1, 2, 3]
            interactive_mode()
            # Check that sorted result was printed
            assert any("Sorted: [1, 2, 3]" in str(call) for call in mock_print.call_args_list)

    @patch("builtins.input", side_effect=["quit"])
    def test_interactive_mode_quit(self, mock_input):
        """Test interactive mode quits on quit command."""
        with patch("builtins.print") as mock_print:
            interactive_mode()
            assert any("Goodbye!" in str(call) for call in mock_print.call_args_list)

    @patch("builtins.input", side_effect=["", "1, 2, 3", "quit"])
    def test_interactive_mode_empty_input(self, mock_input):
        """Test interactive mode ignores empty input."""
        with patch("src.cli.bubble_sort") as mock_sort:
            mock_sort.return_value = [1, 2, 3]
            interactive_mode()

    @patch("builtins.input", side_effect=["abc", "1, 2, 3", "quit"])
    @patch("builtins.print")
    def test_interactive_mode_invalid_input(self, mock_print, mock_input):
        """Test interactive mode handles invalid input."""
        with patch("src.cli.bubble_sort") as mock_sort:
            mock_sort.return_value = [1, 2, 3]
            interactive_mode()
            # Check that error was printed
            assert any("Error:" in str(call) for call in mock_print.call_args_list)

    @patch("builtins.input", side_effect=KeyboardInterrupt)
    def test_interactive_mode_keyboard_interrupt(self, mock_input):
        """Test interactive mode handles keyboard interrupt."""
        with patch("builtins.print") as mock_print:
            interactive_mode()
            assert any("Goodbye!" in str(call) for call in mock_print.call_args_list)

    @patch("builtins.input", side_effect=EOFError)
    def test_interactive_mode_eof(self, mock_input):
        """Test interactive mode handles EOF."""
        with patch("builtins.print") as mock_print:
            interactive_mode()
            assert any("Goodbye!" in str(call) for call in mock_print.call_args_list)


class TestBatchMode:
    """Test the batch_mode function."""

    def test_batch_mode_quit(self):
        """Test batch mode quits on quit command."""
        with patch("builtins.input", return_value="quit"), patch(
            "builtins.print"
        ) as mock_print:
            batch_mode()
            assert any("Goodbye!" in str(call) for call in mock_print.call_args_list)

    def test_batch_mode_keyboard_interrupt(self):
        """Test batch mode handles keyboard interrupt."""
        with patch("builtins.input", side_effect=KeyboardInterrupt), patch(
            "builtins.print"
        ) as mock_print:
            batch_mode()
            assert any("Goodbye!" in str(call) for call in mock_print.call_args_list)

    def test_batch_mode_eof(self):
        """Test batch mode handles EOF."""
        with patch("builtins.input", side_effect=EOFError), patch(
            "builtins.print"
        ) as mock_print:
            batch_mode()
            assert any("Goodbye!" in str(call) for call in mock_print.call_args_list)

    @patch("builtins.input", side_effect=["", "1, 2, 3", "quit"])
    def test_batch_mode_empty_input(self, mock_input):
        """Test batch mode ignores empty input."""
        with patch("src.cli.read_from_file") as mock_read, patch(
            "src.cli.validate_data"
        ), patch("src.cli.bubble_sort") as mock_sort:
            mock_read.return_value = [3, 2, 1]
            mock_sort.return_value = [1, 2, 3]
            with patch("builtins.print"):
                batch_mode()
            # Should have been called at least once
            assert mock_read.call_count >= 1

    @patch("builtins.input", side_effect=["nonexistent.txt", "quit"])
    def test_batch_mode_file_not_found(self, mock_input):
        """Test batch mode handles file not found error."""
        with patch("builtins.print") as mock_print:
            batch_mode()
            assert any(
                "Error:" in str(call) and "nonexistent.txt" in str(call)
                for call in mock_print.call_args_list
            )

    @patch("builtins.input", side_effect=["test.txt", "quit"])
    def test_batch_mode_success(self, mock_input):
        """Test batch mode with successful file processing."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("3, 2, 1")
            temp_path = f.name

        try:
            with patch("builtins.print") as mock_print:
                # Patch read_from_file to return test data
                with patch("src.cli.read_from_file", return_value=[3, 2, 1]), patch(
                    "src.cli.bubble_sort", return_value=[1, 2, 3]
                ):
                    batch_mode()
                    # Check that output was printed
                    assert any("Sorted:" in str(call) for call in mock_print.call_args_list)
        finally:
            Path(temp_path).unlink()


class TestMain:
    """Test the main function."""

    @patch("src.cli.get_input_data")
    @patch("src.cli.validate_data")
    @patch("src.cli.bubble_sort")
    @patch("src.cli.format_output")
    @patch("builtins.print")
    def test_main_success(self, mock_print, mock_format, mock_sort, mock_validate, mock_get_input):
        """Test main function with successful execution."""
        mock_get_input.return_value = [3, 2, 1]
        mock_sort.return_value = [1, 2, 3]
        mock_format.return_value = "[1, 2, 3]"

        with patch("sys.argv", ["cli.py", "1, 2, 3"]):
            main()

        mock_get_input.assert_called_once()
        mock_validate.assert_called_once()
        mock_sort.assert_called_once()
        mock_format.assert_called_once()

    @patch("sys.stderr")
    @patch("src.cli.get_input_data")
    def test_main_file_not_found(self, mock_get_input, mock_stderr):
        """Test main function handles file not found error."""
        mock_get_input.side_effect = FileNotFoundError("File not found")

        with patch("sys.argv", ["cli.py", "--file", "nonexistent.txt"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 1

    @patch("sys.stderr")
    @patch("src.cli.get_input_data")
    def test_main_keyboard_interrupt(self, mock_get_input, mock_stderr):
        """Test main function handles keyboard interrupt."""
        mock_get_input.side_effect = KeyboardInterrupt()

        with patch("sys.argv", ["cli.py", "1, 2, 3"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 130

    @patch("sys.stderr")
    @patch("src.cli.get_input_data")
    def test_main_unexpected_error(self, mock_get_input, mock_stderr):
        """Test main function handles unexpected errors."""
        mock_get_input.side_effect = RuntimeError("Unexpected error")

        with patch("sys.argv", ["cli.py", "1, 2, 3"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 1

    @patch("src.cli.interactive_mode")
    def test_main_interactive_mode(self, mock_interactive):
        """Test main function runs interactive mode."""
        with patch("sys.argv", ["cli.py", "--interactive"]):
            main()
        mock_interactive.assert_called_once()

    @patch("src.cli.batch_mode")
    def test_main_batch_mode(self, mock_batch):
        """Test main function runs batch mode."""
        with patch("sys.argv", ["cli.py", "--batch"]):
            main()
        mock_batch.assert_called_once()

    @patch("src.cli.get_input_data")
    @patch("src.cli.validate_data")
    @patch("src.cli.bubble_sort")
    @patch("src.cli.format_output")
    @patch("builtins.print")
    def test_main_with_stats(self, mock_print, mock_format, mock_sort, mock_validate, mock_get_input):
        """Test main function with statistics."""
        mock_get_input.return_value = [3, 2, 1]
        mock_sort.return_value = [1, 2, 3]
        mock_format.return_value = '{"input": [3, 2, 1], "sorted": [1, 2, 3], "statistics": {...}}'

        with patch("sys.argv", ["cli.py", "--stats", "1, 2, 3"]):
            main()

        mock_format.assert_called_once()
        assert mock_format.call_args[1]["show_stats"] is True

    @patch("src.cli.get_input_data")
    @patch("src.cli.validate_data")
    @patch("src.cli.bubble_sort")
    @patch("src.cli.format_output")
    @patch("builtins.print")
    def test_main_json_format(self, mock_print, mock_format, mock_sort, mock_validate, mock_get_input):
        """Test main function with JSON format."""
        mock_get_input.return_value = [3, 2, 1]
        mock_sort.return_value = [1, 2, 3]
        mock_format.return_value = '{"input": [3, 2, 1], "sorted": [1, 2, 3]}'

        with patch("sys.argv", ["cli.py", "--format", "json", "1, 2, 3"]):
            main()

        mock_format.assert_called_once()
        assert mock_format.call_args[1]["format_type"] == "json"

    @patch("src.cli.get_input_data")
    @patch("src.cli.validate_data")
    @patch("src.cli.bubble_sort")
    @patch("src.cli.format_output")
    @patch("builtins.print")
    def test_main_steps_format(self, mock_print, mock_format, mock_sort, mock_validate, mock_get_input):
        """Test main function with steps format."""
        mock_get_input.return_value = [3, 2, 1]
        mock_sort.return_value = [1, 2, 3]
        mock_format.return_value = "Sorting Steps:\nStep 0: [3, 2, 1]\nStep 1: [1, 2, 3]"

        with patch("sys.argv", ["cli.py", "--format", "steps", "1, 2, 3"]):
            main()

        mock_format.assert_called_once()
        assert mock_format.call_args[1]["format_type"] == "steps"

    @patch("src.cli.get_input_data")
    @patch("src.cli.validate_data")
    @patch("src.cli.bubble_sort")
    @patch("src.cli.format_output")
    @patch("builtins.print")
    def test_main_detailed_format(self, mock_print, mock_format, mock_sort, mock_validate, mock_get_input):
        """Test main function with detailed format."""
        mock_get_input.return_value = [3, 2, 1]
        mock_sort.return_value = [1, 2, 3]
        mock_format.return_value = "Input: [3, 2, 1]\nSorted: [1, 2, 3]"

        with patch("sys.argv", ["cli.py", "--format", "detailed", "1, 2, 3"]):
            main()

        mock_format.assert_called_once()
        assert mock_format.call_args[1]["format_type"] == "detailed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
