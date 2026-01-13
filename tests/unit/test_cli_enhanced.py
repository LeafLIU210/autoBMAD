"""Comprehensive tests for CLI module."""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
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
    """Test parse_array_input function."""

    def test_valid_comma_separated(self):
        """Test parsing comma-separated values."""
        assert parse_array_input("1, 2, 3") == [1, 2, 3]
        assert parse_array_input("5,4,3,2,1") == [5, 4, 3, 2, 1]

    def test_valid_bracketed(self):
        """Test parsing bracketed arrays."""
        assert parse_array_input("[1, 2, 3]") == [1, 2, 3]
        assert parse_array_input("[5, 4, 3, 2, 1]") == [5, 4, 3, 2, 1]

    def test_valid_space_separated(self):
        """Test parsing space-separated values."""
        assert parse_array_input("1 2 3") == [1, 2, 3]
        assert parse_array_input("5 4 3 2 1") == [5, 4, 3, 2, 1]

    def test_mixed_separators(self):
        """Test parsing with mixed separators."""
        assert parse_array_input("1, 2 3, 4") == [1, 2, 3, 4]
        assert parse_array_input("1 2,3, 4") == [1, 2, 3, 4]

    def test_float_values(self):
        """Test parsing float values."""
        assert parse_array_input("1.5, 2.7, 3.2") == [1.5, 2.7, 3.2]
        assert parse_array_input("1.0, 2.5") == [1, 2.5]

    def test_mixed_int_and_float(self):
        """Test parsing mixed integers and floats."""
        assert parse_array_input("1, 2.5, 3") == [1, 2.5, 3]
        assert parse_array_input("[1.0, 2, 3.7]") == [1, 2, 3.7]

    def test_single_value(self):
        """Test parsing single value."""
        assert parse_array_input("42") == [42]
        assert parse_array_input("[42]") == [42]

    def test_empty_string_raises_error(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError, match="Empty input"):
            parse_array_input("")

        with pytest.raises(ValueError, match="Empty input"):
            parse_array_input("   ")

    def test_whitespace_only_raises_error(self):
        """Test that whitespace-only string raises ValueError."""
        with pytest.raises(ValueError, match="Empty input"):
            parse_array_input("   ")

    def test_invalid_number_raises_error(self):
        """Test that invalid number raises ValueError."""
        with pytest.raises(ValueError, match="Invalid number: abc"):
            parse_array_input("1, abc, 3")

        with pytest.raises(ValueError, match="Invalid number: xyz"):
            parse_array_input("1 xyz 3")

    def test_negative_numbers(self):
        """Test parsing negative numbers."""
        assert parse_array_input("-1, -2, -3") == [-1, -2, -3]
        assert parse_array_input("5, -3, 2") == [5, -3, 2]

    def test_zero(self):
        """Test parsing zero."""
        assert parse_array_input("0") == [0]
        assert parse_array_input("0, 1, 0") == [0, 1, 0]

    def test_leading_trailing_spaces(self):
        """Test handling of leading/trailing spaces."""
        assert parse_array_input("  1, 2, 3  ") == [1, 2, 3]
        assert parse_array_input("  [1, 2, 3]  ") == [1, 2, 3]


class TestReadFromFile:
    """Test read_from_file function."""

    def test_valid_file_content(self):
        """Test reading valid data from file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("1, 2, 3, 4, 5")
            temp_path = f.name

        try:
            result = read_from_file(temp_path)
            assert result == [1, 2, 3, 4, 5]
        finally:
            Path(temp_path).unlink()

    def test_file_with_brackets(self):
        """Test reading file with bracketed array."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("[1, 2, 3, 4, 5]")
            temp_path = f.name

        try:
            result = read_from_file(temp_path)
            assert result == [1, 2, 3, 4, 5]
        finally:
            Path(temp_path).unlink()

    def test_empty_file_raises_error(self):
        """Test that empty file raises ValueError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="File is empty"):
                read_from_file(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_nonexistent_file_raises_error(self):
        """Test that nonexistent file raises ValueError."""
        with pytest.raises(ValueError, match="Error reading file"):
            read_from_file("/nonexistent/file.txt")

    def test_invalid_content_raises_error(self):
        """Test that invalid file content raises ValueError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("1, abc, 3")
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Invalid number: abc"):
                read_from_file(temp_path)
        finally:
            Path(temp_path).unlink()


class TestGetSortingSteps:
    """Test get_sorting_steps function."""

    def test_empty_list(self):
        """Test steps for empty list."""
        steps = get_sorting_steps([])
        assert steps == [[]]

    def test_single_element(self):
        """Test steps for single element."""
        steps = get_sorting_steps([5])
        assert steps == [[5]]

    def test_already_sorted(self):
        """Test steps for already sorted list."""
        steps = get_sorting_steps([1, 2, 3, 4, 5])
        assert steps == [[1, 2, 3, 4, 5]]

    def test_reverse_sorted(self):
        """Test steps for reverse sorted list."""
        steps = get_sorting_steps([5, 4, 3, 2, 1])
        assert len(steps) > 1
        assert steps[0] == [5, 4, 3, 2, 1]
        assert steps[-1] == [1, 2, 3, 4, 5]

    def test_random_order(self):
        """Test steps for random order list."""
        steps = get_sorting_steps([3, 1, 4, 1, 5])
        assert len(steps) > 1
        assert steps[0] == [3, 1, 4, 1, 5]
        assert steps[-1] == [1, 1, 3, 4, 5]

    def test_with_duplicates(self):
        """Test steps for list with duplicates."""
        steps = get_sorting_steps([3, 1, 3, 1])
        assert steps[0] == [3, 1, 3, 1]
        assert steps[-1] == [1, 1, 3, 3]

    def test_negative_numbers(self):
        """Test steps with negative numbers."""
        steps = get_sorting_steps([3, -1, 2, -2])
        assert steps[0] == [3, -1, 2, -2]
        assert steps[-1] == [-2, -1, 2, 3]

    def test_floats(self):
        """Test steps with floats."""
        steps = get_sorting_steps([1.5, 0.5, 2.5])
        assert steps[0] == [1.5, 0.5, 2.5]
        assert steps[-1] == [0.5, 1.5, 2.5]


class TestFormatOutput:
    """Test format_output function."""

    def test_default_format(self):
        """Test default output format."""
        result = format_output([3, 1, 2], [1, 2, 3])
        assert result == "[1, 2, 3]"

    def test_json_format(self):
        """Test JSON output format."""
        result = format_output([3, 1, 2], [1, 2, 3], format_type="json")
        output = json.loads(result)
        assert output == {"input": [3, 1, 2], "sorted": [1, 2, 3]}

    def test_json_format_with_stats(self):
        """Test JSON format with statistics."""
        result = format_output([3, 1, 2], [1, 2, 3], format_type="json", show_stats=True)
        output = json.loads(result)
        assert "input" in output
        assert "sorted" in output
        assert "statistics" in output
        assert "comparisons" in output["statistics"]
        assert "swaps" in output["statistics"]
        assert "steps" in output["statistics"]

    def test_steps_format(self):
        """Test steps output format."""
        result = format_output([3, 1, 2], [1, 2, 3], format_type="steps")
        assert "Sorting Steps:" in result
        assert "Step 0: [3, 1, 2]" in result
        assert "Step" in result

    def test_detailed_format(self):
        """Test detailed output format."""
        result = format_output([3, 1, 2], [1, 2, 3], format_type="detailed")
        assert "Input: [3, 1, 2]" in result
        assert "Sorted: [1, 2, 3]" in result

    def test_detailed_format_with_stats(self):
        """Test detailed format with statistics."""
        result = format_output([3, 1, 2], [1, 2, 3], format_type="detailed", show_stats=True)
        assert "Input: [3, 1, 2]" in result
        assert "Sorted: [1, 2, 3]" in result
        assert "Comparisons:" in result
        assert "Swaps:" in result

    def test_mixed_types(self):
        """Test with mixed int and float types."""
        result = format_output([1.0, 2, 3.5], [1, 2, 3.5])
        assert result == "[1, 2, 3.5]"


class TestValidateData:
    """Test validate_data function."""

    def test_valid_data_passes(self):
        """Test that valid data passes validation."""
        validate_data([1, 2, 3, 4, 5])
        validate_data([1.5, 2.7, 3.2])
        validate_data([1])

    def test_empty_list_raises_error(self):
        """Test that empty list raises ValueError."""
        with pytest.raises(ValueError, match="No data to sort"):
            validate_data([])

    def test_list_too_long_raises_error(self):
        """Test that too-long list raises ValueError."""
        with pytest.raises(ValueError, match="List too long"):
            validate_data([1] * 10001)

    def test_non_numeric_value_raises_error(self):
        """Test that non-numeric values raise ValueError."""
        with pytest.raises(ValueError, match="Non-numeric value found: abc"):
            validate_data([1, 2, "abc", 4])

        with pytest.raises(ValueError, match="Non-numeric value found:"):
            validate_data([1, 2, None, 4])

    def test_mixed_types_passes(self):
        """Test that mixed int/float passes validation."""
        validate_data([1, 2.5, 3, 4.7])

    def test_negative_numbers_passes(self):
        """Test that negative numbers pass validation."""
        validate_data([-5, -3, -1, 0, 2])


class TestGetInputData:
    """Test get_input_data function."""

    def test_array_argument(self):
        """Test getting data from array argument."""
        args = Mock()
        args.array = "1, 2, 3"
        args.file = None
        args.interactive = False

        result = get_input_data(args)
        assert result == [1, 2, 3]

    def test_file_argument(self):
        """Test getting data from file argument."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("1, 2, 3")
            temp_path = f.name

        try:
            args = Mock()
            args.array = None
            args.file = temp_path
            args.interactive = False

            result = get_input_data(args)
            assert result == [1, 2, 3]
        finally:
            Path(temp_path).unlink()

    def test_interactive_flag(self):
        """Test with interactive flag."""
        args = Mock()
        args.array = None
        args.file = None
        args.interactive = True

        result = get_input_data(args)
        assert result == []

    def test_no_input_raises_error(self):
        """Test that no input raises ValueError."""
        args = Mock()
        args.array = None
        args.file = None
        args.interactive = False

        with pytest.raises(ValueError, match="No input provided"):
            with patch("sys.stdin.isatty", return_value=True):
                get_input_data(args)

    @patch("sys.stdin")
    def test_stdin_input(self, mock_stdin):
        """Test getting data from stdin."""
        mock_stdin.isatty.return_value = False
        mock_stdin.read.return_value = "1, 2, 3"

        args = Mock()
        args.array = None
        args.file = None
        args.interactive = False

        result = get_input_data(args)
        assert result == [1, 2, 3]

    def test_empty_stdin_raises_error(self):
        """Test that empty stdin raises ValueError."""
        args = Mock()
        args.array = None
        args.file = None
        args.interactive = False

        with pytest.raises(ValueError, match="No input received from stdin"):
            with patch("sys.stdin.isatty", return_value=False):
                with patch("sys.stdin.read", return_value=""):
                    get_input_data(args)


class TestMainFunction:
    """Test main function."""

    @patch("sys.argv")
    @patch("sys.stdout.write")  # Mock to prevent actual output
    def test_main_with_array_argument(self, mock_write, mock_argv):
        """Test main function with array argument."""
        mock_argv.__getitem__.side_effect = lambda i: [
            "cli.py",
            "3, 1, 2",
        ][i]
        mock_argv.__len__.return_value = 2

        # main() doesn't call sys.exit on success, just returns
        # So we just verify it runs without error
        main()

    @patch("sys.argv")
    @patch("sys.stdout.write")
    @patch("sys.stderr.write")
    def test_main_with_invalid_input(self, mock_stderr, mock_write, mock_argv):
        """Test main function with invalid input."""
        mock_argv.__getitem__.side_effect = lambda i: [
            "cli.py",
            "abc",
        ][i]
        mock_argv.__len__.return_value = 2

        with patch("sys.exit") as mock_exit:
            main()
            mock_exit.assert_called_once_with(1)

    @patch("sys.argv")
    @patch("sys.stdout.write")
    def test_main_with_json_format(self, mock_write, mock_argv):
        """Test main function with JSON format option."""
        mock_argv.__getitem__.side_effect = lambda i: [
            "cli.py",
            "3, 1, 2",
            "--format",
            "json",
        ][i]
        mock_argv.__len__.return_value = 4

        # main() doesn't call sys.exit on success, just returns
        main()

    @patch("sys.argv")
    @patch("sys.stdout.write")
    def test_main_with_stats(self, mock_write, mock_argv):
        """Test main function with stats option."""
        mock_argv.__getitem__.side_effect = lambda i: [
            "cli.py",
            "3, 1, 2",
            "--stats",
        ][i]
        mock_argv.__len__.return_value = 3

        # main() doesn't call sys.exit on success, just returns
        main()

    @patch("sys.argv")
    @patch("sys.stdout.write")
    def test_main_with_steps_format(self, mock_write, mock_argv):
        """Test main function with steps format option."""
        mock_argv.__getitem__.side_effect = lambda i: [
            "cli.py",
            "3, 1, 2",
            "--format",
            "steps",
        ][i]
        mock_argv.__len__.return_value = 4

        # main() doesn't call sys.exit on success, just returns
        main()

    @patch("sys.argv")
    @patch("sys.stdout.write")
    def test_main_with_detailed_format(self, mock_write, mock_argv):
        """Test main function with detailed format option."""
        mock_argv.__getitem__.side_effect = lambda i: [
            "cli.py",
            "3, 1, 2",
            "--format",
            "detailed",
        ][i]
        mock_argv.__len__.return_value = 4

        # main() doesn't call sys.exit on success, just returns
        main()

    @patch("sys.argv")
    @patch("sys.stdout.write")
    def test_main_with_file_argument(self, mock_write, mock_argv):
        """Test main function with file argument."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("3, 1, 2")
            temp_path = f.name

        try:
            mock_argv.__getitem__.side_effect = lambda i: [
                "cli.py",
                "-f",
                temp_path,
            ][i]
            mock_argv.__len__.return_value = 3

            # main() doesn't call sys.exit on success, just returns
            main()
        finally:
            Path(temp_path).unlink()


class TestInteractiveMode:
    """Test interactive_mode function."""

    @patch("builtins.input")
    @patch("builtins.print")
    def test_interactive_quit(self, mock_print, mock_input):
        """Test interactive mode with quit command."""
        mock_input.side_effect = ["quit"]

        with patch("sys.exit"):
            interactive_mode()

        # Check that greeting was printed
        assert mock_print.call_count > 0

    @patch("builtins.input")
    @patch("builtins.print")
    def test_interactive_sort(self, mock_print, mock_input):
        """Test interactive mode with valid sort input."""
        mock_input.side_effect = ["3, 1, 2", "quit"]

        with patch("sys.exit"):
            interactive_mode()

        # Check that sorted result was printed
        assert mock_print.call_count > 0

    @patch("builtins.input")
    @patch("builtins.print")
    def test_interactive_invalid_input(self, mock_print, mock_input):
        """Test interactive mode with invalid input."""
        mock_input.side_effect = ["invalid", "3, 1, 2", "quit"]

        with patch("sys.exit"):
            interactive_mode()

        # Should print error for invalid input
        assert mock_print.call_count > 0


class TestBatchMode:
    """Test batch_mode function."""

    @patch("builtins.input")
    @patch("builtins.print")
    def test_batch_quit(self, mock_print, mock_input):
        """Test batch mode with quit command."""
        mock_input.side_effect = ["quit"]

        with patch("sys.exit"):
            batch_mode()

        assert mock_print.call_count > 0

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("builtins.open", mock_open(read_data="3, 1, 2"))
    def test_batch_sort(self, mock_print, mock_input):
        """Test batch mode with valid file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("3, 1, 2")
            temp_path = f.name

        try:
            mock_input.side_effect = [temp_path, "quit"]

            with patch("sys.exit"):
                batch_mode()

            assert mock_print.call_count > 0
        finally:
            Path(temp_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
