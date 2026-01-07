"""Comprehensive test suite for the bubble sort CLI."""

import json
import os
import sys
import tempfile
from io import StringIO
from typing import List
from unittest.mock import patch, MagicMock

import pytest

from src.cli import (
    main,
    create_parser,
    parse_input_value,
    parse_array_string,
    read_from_file,
    read_from_stdin,
    process_and_format,
    format_output_sorted,
    format_output_detailed,
    format_output_steps,
    bubble_sort_detailed,
    bubble_sort_steps,
    run_interactive_mode,
)


class TestParseInputValue:
    """Tests for parse_input_value function."""

    def test_parse_integer(self):
        """Test parsing integer values."""
        assert parse_input_value("5") == 5
        assert parse_input_value("0") == 0
        assert parse_input_value("-5") == -5

    def test_parse_float(self):
        """Test parsing float values."""
        assert parse_input_value("3.14") == 3.14
        assert parse_input_value("-2.5") == -2.5
        assert parse_input_value("0.0") == 0.0

    def test_parse_with_whitespace(self):
        """Test parsing values with surrounding whitespace."""
        assert parse_input_value("  5  ") == 5
        assert parse_input_value("\t3.14\n") == 3.14

    def test_parse_invalid_value(self):
        """Test parsing invalid values raises ValueError."""
        with pytest.raises(ValueError, match="Invalid number 'abc'"):
            parse_input_value("abc")

    def test_parse_empty_value(self):
        """Test parsing empty value raises ValueError."""
        with pytest.raises(ValueError, match="Empty value"):
            parse_input_value("")
        with pytest.raises(ValueError, match="Empty value"):
            parse_input_value("   ")


class TestParseArrayString:
    """Tests for parse_array_string function."""

    def test_parse_space_separated(self):
        """Test parsing space-separated numbers."""
        assert parse_array_string("5 3 1 4 2") == [5, 3, 1, 4, 2]
        assert parse_array_string("1") == [1]

    def test_parse_comma_separated(self):
        """Test parsing comma-separated numbers."""
        assert parse_array_string("5,3,1,4,2") == [5, 3, 1, 4, 2]
        assert parse_array_string("5, 3, 1, 4, 2") == [5, 3, 1, 4, 2]

    def test_parse_json_array(self):
        """Test parsing JSON array format."""
        assert parse_array_string("[5, 3, 1, 4, 2]") == [5, 3, 1, 4, 2]
        assert parse_array_string("[1]") == [1]
        assert parse_array_string("[]") == []

    def test_parse_mixed_integers_floats(self):
        """Test parsing mixed integer and float values."""
        assert parse_array_string("1.5 2 3.7") == [1.5, 2, 3.7]

    def test_parse_negative_numbers(self):
        """Test parsing negative numbers."""
        assert parse_array_string("-1 -2 -3") == [-1, -2, -3]
        assert parse_array_string("[-1, -2, -3]") == [-1, -2, -3]

    def test_parse_empty_input(self):
        """Test parsing empty input raises ValueError."""
        with pytest.raises(ValueError, match="No input provided"):
            parse_array_string("")
        with pytest.raises(ValueError, match="No input provided"):
            parse_array_string("   ")

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON raises ValueError."""
        with pytest.raises(ValueError, match="Invalid JSON format"):
            parse_array_string("[1, 2, 3")

    def test_parse_invalid_number_in_list(self):
        """Test parsing invalid number in list raises ValueError."""
        with pytest.raises(ValueError, match="Invalid number 'abc' at position 2"):
            parse_array_string("1 abc 3")

    def test_parse_json_non_array(self):
        """Test parsing JSON non-array raises ValueError."""
        with pytest.raises(ValueError, match="Invalid JSON format: expected array"):
            parse_array_string('{"key": "value"}')

    def test_parse_json_with_non_numbers(self):
        """Test parsing JSON with non-numbers raises ValueError."""
        with pytest.raises(ValueError, match="Invalid number at position 2"):
            parse_array_string('[1, "two", 3]')


class TestBubbleSortDetailed:
    """Tests for bubble_sort_detailed function."""

    def test_basic_sort(self):
        """Test basic sorting with statistics."""
        result, comparisons, swaps = bubble_sort_detailed([3, 1, 2])
        assert result == [1, 2, 3]
        assert comparisons >= 0
        assert swaps >= 0

    def test_already_sorted(self):
        """Test already sorted array."""
        result, comparisons, swaps = bubble_sort_detailed([1, 2, 3, 4, 5])
        assert result == [1, 2, 3, 4, 5]
        assert swaps == 0

    def test_reverse_sorted(self):
        """Test reverse sorted array."""
        result, comparisons, swaps = bubble_sort_detailed([5, 4, 3, 2, 1])
        assert result == [1, 2, 3, 4, 5]
        assert swaps > 0

    def test_empty_array(self):
        """Test empty array."""
        result, comparisons, swaps = bubble_sort_detailed([])
        assert result == []
        assert comparisons == 0
        assert swaps == 0

    def test_single_element(self):
        """Test single element array."""
        result, comparisons, swaps = bubble_sort_detailed([1])
        assert result == [1]
        assert comparisons == 0
        assert swaps == 0

    def test_none_input(self):
        """Test None input raises TypeError."""
        with pytest.raises(TypeError, match="Input cannot be None"):
            bubble_sort_detailed(None)


class TestBubbleSortSteps:
    """Tests for bubble_sort_steps function."""

    def test_basic_sort(self):
        """Test basic sorting with steps."""
        result, steps = bubble_sort_steps([3, 1, 2])
        assert result == [1, 2, 3]
        assert len(steps) > 0

    def test_already_sorted(self):
        """Test already sorted array returns minimal steps."""
        result, steps = bubble_sort_steps([1, 2, 3])
        assert result == [1, 2, 3]
        # Should stop early due to optimization

    def test_empty_array(self):
        """Test empty array."""
        result, steps = bubble_sort_steps([])
        assert result == []
        assert steps == []

    def test_single_element(self):
        """Test single element array."""
        result, steps = bubble_sort_steps([1])
        assert result == [1]
        assert steps == []

    def test_none_input(self):
        """Test None input raises TypeError."""
        with pytest.raises(TypeError, match="Input cannot be None"):
            bubble_sort_steps(None)


class TestFormatOutput:
    """Tests for output formatting functions."""

    def test_format_sorted(self):
        """Test sorted format output."""
        output = format_output_sorted([1, 2, 3, 4, 5])
        assert output == "[1, 2, 3, 4, 5]"

    def test_format_detailed(self):
        """Test detailed format output."""
        output = format_output_detailed([3, 1, 2], [1, 2, 3], 3, 2)
        assert "Input: [3, 1, 2]" in output
        assert "Output: [1, 2, 3]" in output
        assert "Comparisons: 3" in output
        assert "Swaps: 2" in output

    def test_format_steps(self):
        """Test steps format output."""
        steps = [(1, [1, 3, 2]), (2, [1, 2, 3])]
        output = format_output_steps([3, 1, 2], [1, 2, 3], steps)
        assert "Input: [3, 1, 2]" in output
        assert "Pass 1:" in output
        assert "Pass 2:" in output
        assert "Final: [1, 2, 3]" in output


class TestProcessAndFormat:
    """Tests for process_and_format function."""

    def test_sorted_format(self):
        """Test processing with sorted format."""
        output = process_and_format([3, 1, 2], 'sorted')
        assert output == "[1, 2, 3]"

    def test_detailed_format(self):
        """Test processing with detailed format."""
        output = process_and_format([3, 1, 2], 'detailed')
        assert "Input:" in output
        assert "Output:" in output
        assert "Comparisons:" in output
        assert "Swaps:" in output

    def test_steps_format(self):
        """Test processing with steps format."""
        output = process_and_format([3, 1, 2], 'steps')
        assert "Input:" in output
        assert "Pass" in output
        assert "Final:" in output


class TestReadFromFile:
    """Tests for read_from_file function."""

    def test_read_space_separated(self):
        """Test reading space-separated numbers from file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("5 3 1 4 2")
            f.flush()
            temp_path = f.name

        try:
            result = read_from_file(temp_path)
            assert result == [5, 3, 1, 4, 2]
        finally:
            os.unlink(temp_path)

    def test_read_comma_separated(self):
        """Test reading comma-separated numbers from file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("5,3,1,4,2")
            f.flush()
            temp_path = f.name

        try:
            result = read_from_file(temp_path)
            assert result == [5, 3, 1, 4, 2]
        finally:
            os.unlink(temp_path)

    def test_read_json_file(self):
        """Test reading JSON array from file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([5, 3, 1, 4, 2], f)
            f.flush()
            temp_path = f.name

        try:
            result = read_from_file(temp_path)
            assert result == [5, 3, 1, 4, 2]
        finally:
            os.unlink(temp_path)

    def test_read_one_per_line(self):
        """Test reading numbers one per line."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("5\n3\n1\n4\n2")
            f.flush()
            temp_path = f.name

        try:
            result = read_from_file(temp_path)
            assert result == [5, 3, 1, 4, 2]
        finally:
            os.unlink(temp_path)

    def test_file_not_found(self):
        """Test file not found error."""
        with pytest.raises(FileNotFoundError, match="not found"):
            read_from_file("nonexistent_file.txt")

    def test_empty_file(self):
        """Test empty file raises ValueError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("")
            f.flush()
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="File is empty"):
                read_from_file(temp_path)
        finally:
            os.unlink(temp_path)


class TestReadFromStdin:
    """Tests for read_from_stdin function."""

    def test_read_valid_input(self):
        """Test reading valid input from stdin."""
        with patch('sys.stdin', StringIO("5 3 1 4 2")):
            with patch('sys.stdin.isatty', return_value=False):
                result = read_from_stdin()
                assert result == [5, 3, 1, 4, 2]

    def test_empty_stdin(self):
        """Test empty stdin raises ValueError."""
        with patch('sys.stdin', StringIO("")):
            with patch('sys.stdin.isatty', return_value=False):
                with pytest.raises(ValueError, match="No input provided"):
                    read_from_stdin()

    def test_tty_stdin(self):
        """Test TTY stdin raises ValueError."""
        with patch('sys.stdin.isatty', return_value=True):
            with pytest.raises(ValueError, match="No input provided via stdin"):
                read_from_stdin()


class TestCreateParser:
    """Tests for create_parser function."""

    def test_parser_creation(self):
        """Test parser is created correctly."""
        parser = create_parser()
        assert parser is not None
        assert parser.prog == 'bubble-sort'

    def test_parse_numbers(self):
        """Test parsing number arguments."""
        parser = create_parser()
        args = parser.parse_args(['5', '3', '1', '4', '2'])
        assert args.numbers == ['5', '3', '1', '4', '2']

    def test_parse_format_option(self):
        """Test parsing format option."""
        parser = create_parser()
        args = parser.parse_args(['--format', 'detailed', '5', '3'])
        assert args.format == 'detailed'

    def test_parse_input_file_option(self):
        """Test parsing input-file option."""
        parser = create_parser()
        args = parser.parse_args(['--input-file', 'test.txt'])
        assert args.input_file == 'test.txt'

    def test_parse_interactive_option(self):
        """Test parsing interactive option."""
        parser = create_parser()
        args = parser.parse_args(['--interactive'])
        assert args.interactive is True

    def test_default_format(self):
        """Test default format is sorted."""
        parser = create_parser()
        args = parser.parse_args(['1', '2', '3'])
        assert args.format == 'sorted'


class TestMainFunction:
    """Tests for main CLI entry point."""

    def test_basic_sorting(self):
        """Test basic sorting with command line args."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            exit_code = main(['5', '3', '1', '4', '2'])
            assert exit_code == 0
            assert '[1, 2, 3, 4, 5]' in mock_stdout.getvalue()

    def test_comma_separated_input(self):
        """Test comma-separated input."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            exit_code = main(['5,3,1,4,2'])
            assert exit_code == 0
            assert '[1, 2, 3, 4, 5]' in mock_stdout.getvalue()

    def test_detailed_format(self):
        """Test detailed output format."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            exit_code = main(['--format', 'detailed', '3', '1', '2'])
            assert exit_code == 0
            output = mock_stdout.getvalue()
            assert 'Input:' in output
            assert 'Output:' in output
            assert 'Comparisons:' in output
            assert 'Swaps:' in output

    def test_steps_format(self):
        """Test steps output format."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            exit_code = main(['--format', 'steps', '3', '1', '2'])
            assert exit_code == 0
            output = mock_stdout.getvalue()
            assert 'Input:' in output
            assert 'Pass' in output
            assert 'Final:' in output

    def test_file_input(self):
        """Test file input."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("5 3 1 4 2")
            f.flush()
            temp_path = f.name

        try:
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                exit_code = main(['--input-file', temp_path])
                assert exit_code == 0
                assert '[1, 2, 3, 4, 5]' in mock_stdout.getvalue()
        finally:
            os.unlink(temp_path)

    def test_file_not_found_error(self):
        """Test file not found error handling."""
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            exit_code = main(['--input-file', 'nonexistent.txt'])
            assert exit_code == 1
            assert 'not found' in mock_stderr.getvalue()

    def test_no_input_error(self):
        """Test no input error handling."""
        with patch('sys.stdin.isatty', return_value=True):
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                exit_code = main([])
                assert exit_code == 1
                assert 'No input provided' in mock_stderr.getvalue()

    def test_invalid_number_error(self):
        """Test invalid number error handling."""
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            exit_code = main(['1', 'abc', '3'])
            assert exit_code == 1
            assert 'Invalid number' in mock_stderr.getvalue()

    def test_single_element(self):
        """Test single element input."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            exit_code = main(['42'])
            assert exit_code == 0
            assert '[42]' in mock_stdout.getvalue()

    def test_negative_numbers(self):
        """Test negative numbers."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            exit_code = main(['-3', '-1', '-2'])
            assert exit_code == 0
            assert '[-3, -2, -1]' in mock_stdout.getvalue()

    def test_floating_point_numbers(self):
        """Test floating point numbers."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            exit_code = main(['3.5', '1.2', '2.8'])
            assert exit_code == 0
            assert '[1.2, 2.8, 3.5]' in mock_stdout.getvalue()

    def test_already_sorted(self):
        """Test already sorted array."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            exit_code = main(['1', '2', '3', '4', '5'])
            assert exit_code == 0
            assert '[1, 2, 3, 4, 5]' in mock_stdout.getvalue()

    def test_reverse_sorted(self):
        """Test reverse sorted array."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            exit_code = main(['5', '4', '3', '2', '1'])
            assert exit_code == 0
            assert '[1, 2, 3, 4, 5]' in mock_stdout.getvalue()

    def test_duplicates(self):
        """Test array with duplicates."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            exit_code = main(['3', '1', '3', '2', '1'])
            assert exit_code == 0
            assert '[1, 1, 2, 3, 3]' in mock_stdout.getvalue()

    def test_json_input(self):
        """Test JSON array input from file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([5, 3, 1, 4, 2], f)
            f.flush()
            temp_path = f.name

        try:
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                exit_code = main(['--input-file', temp_path])
                assert exit_code == 0
                assert '[1, 2, 3, 4, 5]' in mock_stdout.getvalue()
        finally:
            os.unlink(temp_path)


class TestInteractiveMode:
    """Tests for interactive mode."""

    def test_interactive_quit(self):
        """Test interactive mode quit command."""
        with patch('builtins.input', side_effect=['quit']):
            with patch('sys.stdout', new_callable=StringIO):
                run_interactive_mode('sorted')

    def test_interactive_exit(self):
        """Test interactive mode exit command."""
        with patch('builtins.input', side_effect=['exit']):
            with patch('sys.stdout', new_callable=StringIO):
                run_interactive_mode('sorted')

    def test_interactive_valid_input(self):
        """Test interactive mode with valid input."""
        with patch('builtins.input', side_effect=['3 1 2', 'quit']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                run_interactive_mode('sorted')
                output = mock_stdout.getvalue()
                assert '[1, 2, 3]' in output

    def test_interactive_invalid_input(self):
        """Test interactive mode with invalid input."""
        with patch('builtins.input', side_effect=['abc', 'quit']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                run_interactive_mode('sorted')
                output = mock_stdout.getvalue()
                assert 'Error' in output

    def test_interactive_empty_input(self):
        """Test interactive mode with empty input."""
        with patch('builtins.input', side_effect=['', 'quit']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                run_interactive_mode('sorted')
                output = mock_stdout.getvalue()
                assert 'Error' in output or 'No input' in output

    def test_interactive_keyboard_interrupt(self):
        """Test interactive mode with keyboard interrupt."""
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                run_interactive_mode('sorted')
                output = mock_stdout.getvalue()
                assert 'Exiting' in output

    def test_interactive_eof(self):
        """Test interactive mode with EOF."""
        with patch('builtins.input', side_effect=EOFError):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                run_interactive_mode('sorted')
                output = mock_stdout.getvalue()
                assert 'Exiting' in output

    def test_interactive_detailed_format(self):
        """Test interactive mode with detailed format."""
        with patch('builtins.input', side_effect=['3 1 2', 'quit']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                run_interactive_mode('detailed')
                output = mock_stdout.getvalue()
                assert 'Comparisons' in output


class TestMainInteractiveMode:
    """Tests for main function with interactive flag."""

    def test_main_interactive_flag(self):
        """Test main with interactive flag."""
        with patch('builtins.input', side_effect=['quit']):
            with patch('sys.stdout', new_callable=StringIO):
                exit_code = main(['--interactive'])
                assert exit_code == 0

    def test_main_interactive_with_format(self):
        """Test main with interactive flag and format."""
        with patch('builtins.input', side_effect=['3 1 2', 'quit']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                exit_code = main(['--interactive', '--format', 'detailed'])
                assert exit_code == 0
                output = mock_stdout.getvalue()
                assert 'Comparisons' in output


class TestStdinInput:
    """Tests for stdin input handling."""

    def test_stdin_input(self):
        """Test reading from stdin when piped."""
        with patch('sys.stdin', StringIO("5 3 1 4 2")):
            with patch('sys.stdin.isatty', return_value=False):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    exit_code = main([])
                    assert exit_code == 0
                    assert '[1, 2, 3, 4, 5]' in mock_stdout.getvalue()


class TestEdgeCases:
    """Tests for edge cases."""

    def test_very_large_array(self):
        """Test with a large array."""
        large_array = list(range(100, 0, -1))  # [100, 99, ..., 1]
        args = [str(x) for x in large_array]
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            exit_code = main(args)
            assert exit_code == 0
            output = mock_stdout.getvalue()
            # Check it's sorted correctly
            assert '1,' in output

    def test_all_same_values(self):
        """Test with all same values."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            exit_code = main(['5', '5', '5', '5', '5'])
            assert exit_code == 0
            assert '[5, 5, 5, 5, 5]' in mock_stdout.getvalue()

    def test_two_elements(self):
        """Test with two elements."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            exit_code = main(['2', '1'])
            assert exit_code == 0
            assert '[1, 2]' in mock_stdout.getvalue()

    def test_mixed_formats_in_args(self):
        """Test mixed formats in command line args - comma parsing takes precedence."""
        # When args are joined, "5,3 1 4 2" has a comma, so it's parsed as comma-separated
        # This means "5,3 1 4 2" becomes ["5", "3 1 4 2"] which is invalid
        # This is expected behavior - user should use consistent formatting
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            exit_code = main(['5,3', '1', '4', '2'])
            assert exit_code == 1  # Should fail due to inconsistent format


class TestHelpAndVersion:
    """Tests for help and version options."""

    def test_help_option(self):
        """Test --help option."""
        with pytest.raises(SystemExit) as exc_info:
            main(['--help'])
        assert exc_info.value.code == 0

    def test_version_option(self):
        """Test --version option."""
        with pytest.raises(SystemExit) as exc_info:
            main(['--version'])
        assert exc_info.value.code == 0


class TestShortOptions:
    """Tests for short option flags."""

    def test_short_input_file_option(self):
        """Test -i option for input file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("5 3 1 4 2")
            f.flush()
            temp_path = f.name

        try:
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                exit_code = main(['-i', temp_path])
                assert exit_code == 0
                assert '[1, 2, 3, 4, 5]' in mock_stdout.getvalue()
        finally:
            os.unlink(temp_path)

    def test_short_format_option(self):
        """Test -f option for format."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            exit_code = main(['-f', 'detailed', '3', '1', '2'])
            assert exit_code == 0
            assert 'Comparisons' in mock_stdout.getvalue()


class TestBatchMode:
    """Tests for batch mode (default non-interactive mode)."""

    def test_batch_single_array(self):
        """Test batch mode with single array."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            exit_code = main(['5', '3', '1', '4', '2'])
            assert exit_code == 0
            assert '[1, 2, 3, 4, 5]' in mock_stdout.getvalue()

    def test_batch_file_input(self):
        """Test batch mode with file input."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("5 3 1 4 2")
            f.flush()
            temp_path = f.name

        try:
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                exit_code = main(['-i', temp_path])
                assert exit_code == 0
                assert '[1, 2, 3, 4, 5]' in mock_stdout.getvalue()
        finally:
            os.unlink(temp_path)


class TestModuleExecution:
    """Tests for running as a module."""

    def test_main_module_import(self):
        """Test that __main__.py can import main."""
        from src.__main__ import main as module_main
        assert module_main is main


class TestErrorMessages:
    """Tests for error message quality."""

    def test_file_not_found_message(self):
        """Test file not found error message is helpful."""
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            exit_code = main(['--input-file', 'nonexistent_file.txt'])
            assert exit_code == 1
            error = mock_stderr.getvalue()
            assert 'nonexistent_file.txt' in error
            assert 'not found' in error

    def test_invalid_number_message(self):
        """Test invalid number error message is helpful."""
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            exit_code = main(['1', '2', 'xyz', '4'])
            assert exit_code == 1
            error = mock_stderr.getvalue()
            assert 'xyz' in error
            assert 'Invalid number' in error

    def test_no_input_message(self):
        """Test no input error message is helpful."""
        with patch('sys.stdin.isatty', return_value=True):
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                exit_code = main([])
                assert exit_code == 1
                error = mock_stderr.getvalue()
                assert 'No input provided' in error
                assert '--help' in error
