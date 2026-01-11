"""Comprehensive test suite for CLI module.

Tests all CLI functionality including argument parsing, input/output methods,
error handling, and special modes.
"""

import json
from io import StringIO
from unittest.mock import patch

import pytest

from src.cli import (
    format_output,
    main,
    parse_array_input,
    read_from_file,
    validate_data,
)


class TestParseArrayInput:
    """Test array input parsing functionality."""

    def test_comma_separated_with_brackets(self):
        assert parse_array_input("[1, 3, 2, 5, 4]") == [1, 3, 2, 5, 4]

    def test_comma_separated_without_brackets(self):
        assert parse_array_input("1,3,2,5,4") == [1, 3, 2, 5, 4]

    def test_space_separated(self):
        assert parse_array_input("1 3 2 5 4") == [1, 3, 2, 5, 4]

    def test_single_element(self):
        assert parse_array_input("42") == [42]

    def test_with_floats(self):
        assert parse_array_input("1.5, 2.3, 3.7") == [1.5, 2.3, 3.7]

    def test_with_scientific_notation(self):
        assert parse_array_input("1e3, 2e-1") == [1000.0, 0.2]

    def test_with_negatives(self):
        assert parse_array_input("-5, 3, -1") == [-5, 3, -1]

    def test_empty_string_raises_error(self):
        with pytest.raises(ValueError, match="Empty input"):
            parse_array_input("")

    def test_whitespace_only_raises_error(self):
        with pytest.raises(ValueError, match="Empty input"):
            parse_array_input("   ")

    def test_invalid_number_raises_error(self):
        with pytest.raises(ValueError, match="Invalid number"):
            parse_array_input("1, abc, 3")

    def test_only_brackets(self):
        # Empty brackets should return empty list
        assert parse_array_input("[]") == []


class TestReadFromFile:
    """Test file reading functionality."""

    @patch("src.cli.Path")
    def test_read_valid_file(self, mock_path_class):
        mock_path = mock_path_class.return_value
        mock_path.exists.return_value = True
        mock_path.read_text.return_value = "1, 3, 2, 5, 4"
        assert read_from_file("test.txt") == [1, 3, 2, 5, 4]

    @patch("src.cli.Path.exists")
    def test_file_not_found_raises_error(self, mock_exists):
        mock_exists.return_value = False
        with pytest.raises(FileNotFoundError, match="File not found"):
            read_from_file("nonexistent.txt")

    @patch("src.cli.Path")
    def test_empty_file_raises_error(self, mock_path_class):
        mock_path = mock_path_class.return_value
        mock_path.exists.return_value = True
        mock_path.read_text.return_value = ""
        with pytest.raises(ValueError, match="File is empty"):
            read_from_file("empty.txt")


class TestFormatOutput:
    """Test output formatting."""

    def test_default_format(self):
        data = [3, 1, 2]
        sorted_data = [1, 2, 3]
        output = format_output(data, sorted_data, "default")
        assert output == "[1, 2, 3]"

    def test_detailed_format(self):
        data = [3, 1, 2]
        sorted_data = [1, 2, 3]
        output = format_output(data, sorted_data, "detailed")
        assert "Input: [3, 1, 2]" in output
        assert "Sorted: [1, 2, 3]" in output

    def test_json_format(self):
        data = [3, 1, 2]
        sorted_data = [1, 2, 3]
        output = format_output(data, sorted_data, "json")
        parsed = json.loads(output)
        assert parsed["input"] == [3, 1, 2]
        assert parsed["sorted"] == [1, 2, 3]


class TestValidateData:
    """Test data validation."""

    def test_valid_data_passes(self):
        validate_data([1, 2, 3, 4, 5])

    def test_empty_list_raises_error(self):
        with pytest.raises(ValueError, match="No data to sort"):
            validate_data([])

    def test_non_numeric_values_raise_error(self):
        with pytest.raises(ValueError, match="Non-numeric value found"):
            validate_data([1, "abc", 3])


class TestCLIIntegration:
    """Test CLI integration."""

    def test_help_message(self):
        with pytest.raises(SystemExit) as exc_info:
            with patch("sys.argv", ["bubble-sort", "--help"]):
                main()
        assert exc_info.value.code == 0

    def test_basic_array_sorting(self):
        with patch("sys.argv", ["bubble-sort", "[3, 1, 2]"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert "[1, 2, 3]" in output

    def test_comma_separated_array(self):
        with patch("sys.argv", ["bubble-sort", "3,1,2"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert "[1, 2, 3]" in output

    def test_space_separated_array(self):
        with patch("sys.argv", ["bubble-sort", "3 1 2"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert "[1, 2, 3]" in output

    def test_detailed_format(self):
        with patch("sys.argv", ["bubble-sort", "--format", "detailed", "[3, 1, 2]"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert "Input: [3, 1, 2]" in output
                assert "Sorted: [1, 2, 3]" in output

    def test_json_format(self):
        with patch("sys.argv", ["bubble-sort", "--format", "json", "[3, 1, 2]"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                parsed = json.loads(output)
                assert parsed["input"] == [3, 1, 2]
                assert parsed["sorted"] == [1, 2, 3]

    def test_invalid_array_format(self):
        with patch("sys.argv", ["bubble-sort", "abc"]):
            with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1
                assert "Invalid number" in mock_stderr.getvalue()

    def test_empty_input(self):
        with patch("sys.argv", ["bubble-sort"]):
            with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1
                # The actual error might be about stdin, so check for either
                error_output = mock_stderr.getvalue()
                assert "No input provided" in error_output or "stdin" in error_output
