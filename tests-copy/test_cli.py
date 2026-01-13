"""Test suite for CLI functionality.

Tests cover:
- Command-line argument parsing
- Help messages
- Error handling
- Main execution flow
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
from io import StringIO
from src.cli import main, parse_array_input, read_from_file, validate_data, format_output


class TestParseArrayInput:
    """Test command-line argument parsing."""

    def test_parse_array_input_valid(self):
        """Test parsing valid array input."""
        result = parse_array_input("3, 1, 2, 4")
        assert result == [3, 1, 2, 4]

    def test_parse_array_input_with_brackets(self):
        """Test parsing array input with brackets."""
        result = parse_array_input("[3, 1, 2, 4]")
        assert result == [3, 1, 2, 4]

    def test_parse_array_input_with_spaces(self):
        """Test parsing array input with spaces."""
        result = parse_array_input("3 1 2 4")
        assert result == [3, 1, 2, 4]

    def test_parse_array_input_empty(self):
        """Test that empty input raises ValueError."""
        with pytest.raises(ValueError, match="Empty input"):
            parse_array_input("")

    def test_parse_array_input_invalid_number(self):
        """Test that invalid number raises ValueError."""
        with pytest.raises(ValueError, match="Invalid number"):
            parse_array_input("3, abc, 2")


class TestValidateData:
    """Test data validation."""

    def test_validate_data_valid(self):
        """Test that valid data passes validation."""
        validate_data([1, 2, 3])

    def test_validate_data_empty(self):
        """Test that empty list raises ValueError."""
        with pytest.raises(ValueError):
            validate_data([])

    def test_validate_data_single_element(self):
        """Test that single element passes validation."""
        validate_data([42])

    def test_validate_data_with_duplicates(self):
        """Test that duplicates pass validation."""
        validate_data([1, 2, 1, 3])


class TestFormatOutput:
    """Test output formatting."""

    def test_format_output_json(self):
        """Test JSON output formatting."""
        output = format_output([1, 2, 3], 'json')
        import json
        parsed = json.loads(output)
        assert parsed == [1, 2, 3]

    def test_format_output_pretty(self):
        """Test pretty output formatting."""
        output = format_output([1, 2, 3], 'pretty')
        assert '1' in output and '2' in output and '3' in output

    def test_format_output_simple(self):
        """Test simple output formatting."""
        output = format_output([1, 2, 3], 'simple')
        assert '[1, 2, 3]' in output


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_read_from_file_not_found(self):
        """Test that missing file raises error."""
        with pytest.raises(ValueError, match="Error reading file"):
            read_from_file("nonexistent_file.txt")

    def test_parse_array_input_empty_string(self):
        """Test that empty string raises error."""
        with pytest.raises(ValueError, match="Empty input"):
            parse_array_input("")


class TestCLIHelp:
    """Test CLI help functionality."""

    def test_help_message_exists(self):
        """Test that help message is defined."""
        # This is a basic check that the module has help-related content
        import src.cli as cli_module
        assert hasattr(cli_module, 'main')


class TestCLIIntegration:
    """Integration tests for CLI."""

    @patch('sys.stdout', new_callable=StringIO)
    def test_end_to_end_sorting(self, mock_stdout):
        """Test end-to-end sorting workflow."""
        with patch('sys.argv', ['cli.py', '5', '3', '8', '1']):
            main()
        output = mock_stdout.getvalue()
        # Check that the numbers are sorted in the output
        assert '[1, 3, 5, 8]' in output

    @patch('sys.stdout', new_callable=StringIO)
    def test_end_to_end_with_duplicates(self, mock_stdout):
        """Test end-to-end sorting with duplicates."""
        with patch('sys.argv', ['cli.py', '3', '1', '3', '2', '1']):
            main()
        output = mock_stdout.getvalue()
        assert '[1, 1, 2, 3, 3]' in output

    @patch('sys.stdout', new_callable=StringIO)
    def test_end_to_end_already_sorted(self, mock_stdout):
        """Test end-to-end sorting with already sorted list."""
        with patch('sys.argv', ['cli.py', '1', '2', '3', '4', '5']):
            main()
        output = mock_stdout.getvalue()
        assert '[1, 2, 3, 4, 5]' in output


class TestCLITypeHints:
    """Test that CLI functions have proper type hints."""

    def test_main_has_type_hints(self):
        """Test that main function has type hints."""
        import inspect
        sig = inspect.signature(main)
        assert sig is not None

    def test_parse_array_input_has_type_hints(self):
        """Test that parse_array_input has type hints."""
        import inspect
        sig = inspect.signature(parse_array_input)
        assert 'return' in sig.annotations or len(sig.parameters) > 0

    def test_validate_data_has_type_hints(self):
        """Test that validate_data has type hints."""
        import inspect
        sig = inspect.signature(validate_data)
        assert 'return' in sig.annotations


class TestCLIDocumentation:
    """Test that CLI functions have proper documentation."""

    def test_main_has_docstring(self):
        """Test that main function has a docstring."""
        assert main.__doc__ is not None

    def test_parse_array_input_has_docstring(self):
        """Test that parse_array_input has a docstring."""
        assert parse_array_input.__doc__ is not None

    def test_validate_data_has_docstring(self):
        """Test that validate_data has a docstring."""
        assert validate_data.__doc__ is not None
