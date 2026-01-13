"""Comprehensive test suite for CLI bubble sort interface.

This test suite provides thorough coverage of the CLI interface for the bubble sort
application, testing argument parsing, input handling, output formatting, and error handling.
"""
import pytest
import sys
import json
from pathlib import Path
from unittest.mock import patch, mock_open
from io import StringIO

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestParseArrayInput:
    """Test the parse_array_input function."""

    def test_parse_simple_comma_separated(self):
        """Test parsing simple comma-separated numbers."""
        from cli import parse_array_input
        result = parse_array_input("1, 2, 3")
        assert result == [1, 2, 3]

    def test_parse_space_separated(self):
        """Test parsing space-separated numbers."""
        from cli import parse_array_input
        result = parse_array_input("1 2 3")
        assert result == [1, 2, 3]

    def test_parse_bracketed_input(self):
        """Test parsing bracketed input."""
        from cli import parse_array_input
        result = parse_array_input("[1, 2, 3]")
        assert result == [1, 2, 3]

    def test_parse_mixed_int_float(self):
        """Test parsing mixed integers and floats."""
        from cli import parse_array_input
        result = parse_array_input("1, 2.5, 3")
        assert result == [1, 2.5, 3]

    def test_parse_negative_numbers(self):
        """Test parsing negative numbers."""
        from cli import parse_array_input
        result = parse_array_input("-1, -2, -3")
        assert result == [-1, -2, -3]

    def test_empty_input_raises_error(self):
        """Test that empty input raises ValueError."""
        from cli import parse_array_input
        with pytest.raises(ValueError, match="Empty input"):
            parse_array_input("")

    def test_whitespace_only_raises_error(self):
        """Test that whitespace-only input raises ValueError."""
        from cli import parse_array_input
        with pytest.raises(ValueError, match="Empty input"):
            parse_array_input("   ")

    def test_invalid_number_raises_error(self):
        """Test that invalid numbers raise ValueError."""
        from cli import parse_array_input
        with pytest.raises(ValueError, match="Invalid number"):
            parse_array_input("1, abc, 3")

    def test_parse_empty_after_strip(self):
        """Test that input that becomes empty after stripping raises ValueError."""
        from cli import parse_array_input
        with pytest.raises(ValueError, match="Empty input"):
            parse_array_input(", , ,")


class TestReadFromFile:
    """Test the read_from_file function."""

    def test_read_valid_file(self, tmp_path):
        """Test reading a valid file."""
        from cli import read_from_file
        test_file = tmp_path / "test.txt"
        test_file.write_text("1, 2, 3")

        result = read_from_file(str(test_file))
        assert result == [1, 2, 3]

    def test_read_empty_file_raises_error(self, tmp_path):
        """Test reading an empty file raises ValueError."""
        from cli import read_from_file
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")

        with pytest.raises(ValueError, match="File is empty"):
            read_from_file(str(test_file))

    def test_read_nonexistent_file_raises_error(self):
        """Test reading a nonexistent file raises ValueError."""
        from cli import read_from_file
        with pytest.raises(ValueError, match="Error reading file"):
            read_from_file("/nonexistent/file.txt")


class TestGetSortingSteps:
    """Test the get_sorting_steps function."""

    def test_single_element(self):
        """Test steps for single element."""
        from cli import get_sorting_steps
        result = get_sorting_steps([5])
        assert result == [[5]]

    def test_two_elements(self):
        """Test steps for two elements."""
        from cli import get_sorting_steps
        result = get_sorting_steps([2, 1])
        assert result == [[2, 1], [1, 2]]

    def test_already_sorted(self):
        """Test steps for already sorted list."""
        from cli import get_sorting_steps
        result = get_sorting_steps([1, 2, 3])
        assert result == [[1, 2, 3]]


class TestFormatOutput:
    """Test the format_output function."""

    def test_default_format(self):
        """Test default output format."""
        from cli import format_output
        result = format_output([3, 1, 2], [1, 2, 3])
        assert result == "[1, 2, 3]"

    def test_json_format(self):
        """Test JSON output format."""
        from cli import format_output
        result = format_output([3, 1, 2], [1, 2, 3], format_type="json")
        parsed = json.loads(result)
        assert parsed == {"input": [3, 1, 2], "sorted": [1, 2, 3]}

    def test_steps_format(self):
        """Test steps output format."""
        from cli import format_output
        result = format_output([2, 1], [1, 2], format_type="steps")
        assert "Step 0:" in result
        assert "Step 1:" in result

    def test_detailed_format(self):
        """Test detailed output format."""
        from cli import format_output
        result = format_output([3, 1, 2], [1, 2, 3], format_type="detailed")
        assert "Input:" in result
        assert "Sorted:" in result

    def test_json_with_stats(self):
        """Test JSON output with statistics."""
        from cli import format_output
        result = format_output([3, 1, 2], [1, 2, 3], format_type="json", show_stats=True)
        parsed = json.loads(result)
        assert "statistics" in parsed
        assert "comparisons" in parsed["statistics"]


class TestValidateData:
    """Test the validate_data function."""

    def test_valid_data_passes(self):
        """Test that valid data passes validation."""
        from cli import validate_data
        validate_data([1, 2, 3])  # Should not raise

    def test_empty_data_raises_error(self):
        """Test that empty data raises ValueError."""
        from cli import validate_data
        with pytest.raises(ValueError, match="No data to sort"):
            validate_data([])

    def test_too_many_elements_raises_error(self):
        """Test that too many elements raises ValueError."""
        from cli import validate_data
        with pytest.raises(ValueError, match="List too long"):
            validate_data(list(range(10001)))

    def test_non_numeric_raises_error(self):
        """Test that non-numeric values raise ValueError."""
        from cli import validate_data
        with pytest.raises(ValueError, match="Non-numeric value"):
            validate_data([1, "a", 3])


class TestGetInputData:
    """Test the get_input_data function."""

    def test_get_input_from_array_arg(self):
        """Test getting input from array argument."""
        from cli import get_input_data
        from argparse import Namespace

        args = Namespace(array="1, 2, 3", file=None, interactive=False)
        result = get_input_data(args)
        assert result == [1, 2, 3]

    def test_get_input_from_file_arg(self, tmp_path):
        """Test getting input from file argument."""
        from cli import get_input_data
        from argparse import Namespace

        test_file = tmp_path / "test.txt"
        test_file.write_text("1, 2, 3")

        args = Namespace(array=None, file=str(test_file), interactive=False)
        result = get_input_data(args)
        assert result == [1, 2, 3]

    @patch('sys.stdin.isatty', return_value=True)
    def test_no_input_raises_error(self, mock_isatty):
        """Test that no input raises ValueError."""
        from cli import get_input_data
        from argparse import Namespace

        args = Namespace(array=None, file=None, interactive=False)
        with pytest.raises(ValueError, match="No input provided"):
            get_input_data(args)

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdin.read')
    def test_stdin_input(self, mock_stdin_read, mock_isatty):
        """Test getting input from stdin."""
        from cli import get_input_data
        from argparse import Namespace

        mock_stdin_read.return_value = "1, 2, 3"

        args = Namespace(array=None, file=None, interactive=False)
        result = get_input_data(args)
        assert result == [1, 2, 3]

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdin.read')
    def test_stdin_empty_input_raises_error(self, mock_stdin_read, mock_isatty):
        """Test that empty stdin input raises ValueError."""
        from cli import get_input_data
        from argparse import Namespace

        mock_stdin_read.return_value = ""

        args = Namespace(array=None, file=None, interactive=False)
        with pytest.raises(ValueError, match="No input received from stdin"):
            get_input_data(args)

    def test_get_input_from_interactive_flag(self):
        """Test getting input when interactive flag is set."""
        from cli import get_input_data
        from argparse import Namespace

        args = Namespace(array=None, file=None, interactive=True)
        result = get_input_data(args)
        assert result == []


class TestMainFunction:
    """Test the main function with various scenarios."""

    @patch('sys.argv')
    @patch('builtins.print')
    def test_main_simple_array(self, mock_print, mock_argv):
        """Test main function with simple array input."""
        from cli import main

        mock_argv.__getitem__.side_effect = lambda i: ['cli.py', '3, 1, 2'][i]
        mock_argv.__len__.return_value = 2

        main()

        # Check that sorted output was printed
        assert mock_print.called
        output = "".join([str(call[0][0]) for call in mock_print.call_args_list])
        assert '[1, 2, 3]' in output

    @patch('sys.argv')
    @patch('builtins.print')
    def test_main_with_format_json(self, mock_print, mock_argv):
        """Test main function with JSON output format."""
        from cli import main

        mock_argv.__getitem__.side_effect = lambda i: ['cli.py', '3, 1, 2', '--format', 'json'][i]
        mock_argv.__len__.return_value = 4

        main()

        # Verify JSON output
        output = "".join([str(call[0][0]) for call in mock_print.call_args_list])
        parsed = json.loads(output)
        assert parsed == {"input": [3, 1, 2], "sorted": [1, 2, 3]}

    @patch('sys.argv')
    @patch('builtins.print')
    def test_main_with_stats(self, mock_print, mock_argv):
        """Test main function with statistics."""
        from cli import main

        mock_argv.__getitem__.side_effect = lambda i: ['cli.py', '3, 1, 2', '--stats', '--format', 'detailed'][i]
        mock_argv.__len__.return_value = 5

        main()

        # Verify statistics are included
        output = "".join([str(call[0][0]) for call in mock_print.call_args_list])
        assert 'Comparisons' in output and 'Swaps' in output and 'Steps' in output

    @patch('sys.argv')
    def test_main_invalid_input(self, mock_argv):
        """Test main function with invalid input."""
        from cli import main

        mock_argv.__getitem__.side_effect = lambda i: ['cli.py', 'invalid'][i]
        mock_argv.__len__.return_value = 2

        with pytest.raises(SystemExit):
            main()

    @patch('sys.argv')
    def test_main_help(self, mock_argv):
        """Test main function with --help."""
        from cli import main

        mock_argv.__getitem__.side_effect = lambda i: ['cli.py', '--help'][i]
        mock_argv.__len__.return_value = 2

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0

    @patch('sys.argv')
    @patch('builtins.print')
    def test_main_file_input(self, mock_print, mock_argv, tmp_path):
        """Test main function with file input."""
        from cli import main

        test_file = tmp_path / "test.txt"
        test_file.write_text("3, 1, 2")

        mock_argv.__getitem__.side_effect = lambda i: ['cli.py', '-f', str(test_file)][i]
        mock_argv.__len__.return_value = 3

        main()

        # Verify sorted output was printed
        output = "".join([str(call[0][0]) for call in mock_print.call_args_list])
        assert '[1, 2, 3]' in output

    @patch('sys.argv')
    @patch('builtins.print')
    @patch('cli.interactive_mode')
    def test_main_interactive_mode(self, mock_interactive, mock_print, mock_argv):
        """Test main function with --interactive flag."""
        from cli import main

        mock_argv.__getitem__.side_effect = lambda i: ['cli.py', '--interactive'][i]
        mock_argv.__len__.return_value = 2

        main()

        # Verify interactive_mode was called
        mock_interactive.assert_called_once()

    @patch('sys.argv')
    @patch('builtins.print')
    @patch('cli.batch_mode')
    def test_main_batch_mode(self, mock_batch, mock_print, mock_argv):
        """Test main function with --batch flag."""
        from cli import main

        mock_argv.__getitem__.side_effect = lambda i: ['cli.py', '--batch'][i]
        mock_argv.__len__.return_value = 2

        main()

        # Verify batch_mode was called
        mock_batch.assert_called_once()

    @patch('sys.argv')
    @patch('sys.stderr')
    def test_main_file_not_found(self, mock_stderr, mock_argv):
        """Test main function handles FileNotFoundError."""
        from cli import main

        mock_argv.__getitem__.side_effect = lambda i: ['cli.py', '-f', '/nonexistent.txt'][i]
        mock_argv.__len__.return_value = 3

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        # Verify error was printed to stderr
        assert mock_stderr.write.called

    @patch('sys.argv')
    @patch('sys.stderr')
    def test_main_keyboard_interrupt(self, mock_stderr, mock_argv):
        """Test main function handles KeyboardInterrupt."""
        from cli import main
        from unittest.mock import patch

        mock_argv.__getitem__.side_effect = lambda i: ['cli.py', '1, 2, 3'][i]
        mock_argv.__len__.return_value = 2

        with patch('cli.get_input_data', side_effect=KeyboardInterrupt()):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 130
        # Verify interrupt message was printed to stderr
        assert mock_stderr.write.called

    @patch('sys.argv')
    @patch('sys.stderr')
    def test_main_generic_exception(self, mock_stderr, mock_argv):
        """Test main function handles generic exceptions."""
        from cli import main

        mock_argv.__getitem__.side_effect = lambda i: ['cli.py', '1, 2, 3'][i]
        mock_argv.__len__.return_value = 2

        with patch('cli.get_input_data', side_effect=RuntimeError("Unexpected error")):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 1
        # Verify unexpected error message was printed to stderr
        assert mock_stderr.write.called

    @patch('sys.argv')
    @patch('sys.stderr')
    def test_main_value_error_exception(self, mock_stderr, mock_argv):
        """Test main function handles ValueError exceptions."""
        from cli import main

        mock_argv.__getitem__.side_effect = lambda i: ['cli.py', '1, 2, 3'][i]
        mock_argv.__len__.return_value = 2

        with patch('cli.get_input_data', side_effect=ValueError("Invalid input")):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 1
        # Verify error message was printed to stderr
        assert mock_stderr.write.called

    @patch('sys.argv')
    @patch('sys.stderr')
    def test_main_file_not_found_error(self, mock_stderr, mock_argv):
        """Test main function handles FileNotFoundError exceptions."""
        from cli import main

        mock_argv.__getitem__.side_effect = lambda i: ['cli.py', '1, 2, 3'][i]
        mock_argv.__len__.return_value = 2

        with patch('cli.get_input_data', side_effect=FileNotFoundError("File not found")):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 1
        # Verify error message was printed to stderr
        assert mock_stderr.write.called


class TestInteractiveMode:
    """Test the interactive_mode function."""

    @patch('builtins.input')
    @patch('builtins.print')
    def test_interactive_quit(self, mock_print, mock_input):
        """Test interactive mode quits on 'quit' command."""
        from cli import interactive_mode

        mock_input.side_effect = ['quit', KeyboardInterrupt()]
        interactive_mode()

        # Verify quit message was printed
        assert any('Goodbye!' in str(call[0][0]) for call in mock_print.call_args_list)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_interactive_single_input(self, mock_print, mock_input):
        """Test interactive mode processes single input."""
        from cli import interactive_mode

        inputs = ['1, 2, 3', 'quit']
        mock_input.side_effect = inputs

        interactive_mode()

        # Verify sorted output was printed
        assert any('[1, 2, 3]' in str(call[0][0]) for call in mock_print.call_args_list)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_interactive_invalid_input(self, mock_print, mock_input):
        """Test interactive mode handles invalid input."""
        from cli import interactive_mode

        inputs = ['invalid', '1, 2, 3', 'quit']
        mock_input.side_effect = inputs

        interactive_mode()

        # Verify error message was printed
        assert any('Error:' in str(call[0][0]) for call in mock_print.call_args_list)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_interactive_empty_input(self, mock_print, mock_input):
        """Test interactive mode handles empty input gracefully."""
        from cli import interactive_mode

        inputs = ['', '1, 2, 3', 'quit']
        mock_input.side_effect = inputs

        interactive_mode()

        # Should not crash on empty input, should continue loop
        assert mock_input.call_count >= 3

    @patch('builtins.input')
    @patch('builtins.print')
    def test_interactive_keyboard_interrupt(self, mock_print, mock_input):
        """Test interactive mode handles KeyboardInterrupt."""
        from cli import interactive_mode

        mock_input.side_effect = KeyboardInterrupt()

        interactive_mode()

        # Verify goodbye message was printed
        assert any('Goodbye!' in str(call[0][0]) for call in mock_print.call_args_list)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_interactive_eof_error(self, mock_print, mock_input):
        """Test interactive mode handles EOFError."""
        from cli import interactive_mode

        mock_input.side_effect = EOFError()

        interactive_mode()

        # Verify goodbye message was printed
        assert any('Goodbye!' in str(call[0][0]) for call in mock_print.call_args_list)


class TestBatchMode:
    """Test the batch_mode function."""

    @patch('builtins.input')
    @patch('builtins.print')
    def test_batch_quit(self, mock_print, mock_input):
        """Test batch mode quits on 'quit' command."""
        from cli import batch_mode

        mock_input.side_effect = ['quit', KeyboardInterrupt()]
        batch_mode()

        # Verify quit message was printed
        assert any('Goodbye!' in str(call[0][0]) for call in mock_print.call_args_list)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_batch_single_file(self, mock_print, mock_input, tmp_path):
        """Test batch mode processes single file."""
        from cli import batch_mode

        test_file = tmp_path / "test.txt"
        test_file.write_text("3, 1, 2")

        inputs = [str(test_file), 'quit']
        mock_input.side_effect = inputs

        batch_mode()

        # Verify sorted output was printed
        assert any('[1, 2, 3]' in str(call[0][0]) for call in mock_print.call_args_list)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_batch_invalid_file(self, mock_print, mock_input):
        """Test batch mode handles invalid file."""
        from cli import batch_mode

        inputs = ['/nonexistent/file.txt', 'quit']
        mock_input.side_effect = inputs

        batch_mode()

        # Verify error message was printed
        assert any('Error:' in str(call[0][0]) for call in mock_print.call_args_list)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_batch_empty_file_path(self, mock_print, mock_input):
        """Test batch mode handles empty file path gracefully."""
        from cli import batch_mode

        inputs = ['', str(Path('/tmp/test.txt')), 'quit']
        mock_input.side_effect = inputs

        batch_mode()

        # Should not crash on empty file path, should continue loop
        assert mock_input.call_count >= 3

    @patch('builtins.input')
    @patch('builtins.print')
    def test_batch_keyboard_interrupt(self, mock_print, mock_input):
        """Test batch mode handles KeyboardInterrupt."""
        from cli import batch_mode

        mock_input.side_effect = KeyboardInterrupt()

        batch_mode()

        # Verify goodbye message was printed
        assert any('Goodbye!' in str(call[0][0]) for call in mock_print.call_args_list)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_batch_eof_error(self, mock_print, mock_input):
        """Test batch mode handles EOFError."""
        from cli import batch_mode

        mock_input.side_effect = EOFError()

        batch_mode()

        # Verify goodbye message was printed
        assert any('Goodbye!' in str(call[0][0]) for call in mock_print.call_args_list)
