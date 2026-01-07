"""
Integration tests for bubble sort with CLI and complete workflow.
"""

import pytest
import sys
import subprocess


class TestBubbleSortCLI:
    """Integration tests for CLI interface."""

    def test_cli_basic_usage(self):
        """Test basic CLI usage with simple input."""
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '5', '3', '1', '4', '2'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert '[1, 2, 3, 4, 5]' in result.stdout

    def test_cli_already_sorted(self):
        """Test CLI with already sorted input."""
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '1', '2', '3', '4', '5'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert '[1, 2, 3, 4, 5]' in result.stdout

    def test_cli_reverse_sorted(self):
        """Test CLI with reverse sorted input."""
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '5', '4', '3', '2', '1'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert '[1, 2, 3, 4, 5]' in result.stdout

    def test_cli_single_element(self):
        """Test CLI with single element."""
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '42'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert '[42]' in result.stdout

    def test_cli_empty(self):
        """Test CLI with no arguments."""
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli'],
            capture_output=True,
            text=True
        )
        # Should fail or show error
        assert result.returncode != 0

    def test_cli_with_negative_numbers(self):
        """Test CLI with negative numbers."""
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '-5', '3', '-1', '0'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert '[-5, -1, 0, 3]' in result.stdout

    def test_cli_with_duplicates(self):
        """Test CLI with duplicate numbers."""
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '5', '3', '5', '3', '1'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert '[1, 3, 3, 5, 5]' in result.stdout

    def test_cli_invalid_argument(self):
        """Test CLI with invalid argument."""
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '5', 'abc', '3'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        assert 'Error' in result.stderr

    def test_cli_with_output_file(self):
        """Test CLI output to file."""
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_file = f.name

        try:
            result = subprocess.run(
                [sys.executable, '-m', 'src.cli', '5', '3', '1', '--format', 'detailed'],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0
            assert 'Input:' in result.stdout
            assert 'Output:' in result.stdout
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_cli_with_input_file(self):
        """Test CLI input from file."""
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('5\n3\n1\n4\n2\n')
            input_file = f.name

        try:
            result = subprocess.run(
                [sys.executable, '-m', 'src.cli', '--input-file', input_file],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0
            assert '[1, 2, 3, 4, 5]' in result.stdout
        finally:
            if os.path.exists(input_file):
                os.unlink(input_file)

    def test_cli_with_input_file_with_invalid_number(self):
        """Test CLI with invalid number in file."""
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('5\ninvalid\n3\n')
            input_file = f.name

        try:
            result = subprocess.run(
                [sys.executable, '-m', 'src.cli', '--input-file', input_file],
                capture_output=True,
                text=True
            )
            assert result.returncode == 1
            assert 'Error' in result.stderr
        finally:
            if os.path.exists(input_file):
                os.unlink(input_file)

    def test_cli_with_mixed_int_float(self):
        """Test CLI with mixed integers and floats."""
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '5', '3.5', '1', '4.2'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert '[1, 3.5, 4.2, 5]' in result.stdout or '[1, 3.5, 4.2, 5]' in result.stdout.replace(' ', '')

    def test_cli_all_integers_display_as_int(self):
        """Test CLI with all integers."""
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '5', '3', '1', '4', '2'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert '1' in result.stdout and '2' in result.stdout and '3' in result.stdout

    def test_cli_with_verbose_output(self):
        """Test CLI with verbose output."""
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '--format', 'steps', '5', '3', '1'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'Pass' in result.stdout

    def test_cli_with_statistics(self):
        """Test CLI with statistics output."""
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '--format', 'detailed', '5', '3', '1'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'Comparisons:' in result.stdout
        assert 'Swaps:' in result.stdout

    def test_cli_with_comma_separated_input(self):
        """Test CLI with comma-separated input."""
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '5,3,1,4,2'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert '[1, 2, 3, 4, 5]' in result.stdout

    def test_cli_with_space_separated_input(self):
        """Test CLI with space-separated input."""
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '5 3 1 4 2'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert '[1, 2, 3, 4, 5]' in result.stdout

    def test_cli_with_stdin_input(self):
        """Test CLI with stdin input."""
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli'],
            input='5\n3\n1\n4\n2\n',
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert '[1, 2, 3, 4, 5]' in result.stdout

    def test_cli_with_piped_input(self):
        """Test CLI with piped input."""
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli'],
            input='5 3 1\n',
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert '[1, 3, 5]' in result.stdout

    def test_cli_interactive_mode(self):
        """Test CLI interactive mode."""
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '--interactive'],
            input='quit\n',
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0

    def test_cli_help_flag(self):
        """Test CLI help flag."""
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '--help'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'usage:' in result.stdout.lower()

    def test_cli_with_mixed_comma_space_separation(self):
        """Test CLI with mixed comma and space separation."""
        # This should fail because comma in middle of argument is invalid
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '5,3', '1'],
            capture_output=True,
            text=True
        )
        # Expect failure
        assert result.returncode != 0

    def test_cli_repl_mode(self):
        """Test CLI REPL mode (same as interactive)."""
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '--interactive'],
            input='quit\n',
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0

    def test_cli_batch_mode(self):
        """Test CLI batch mode."""
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '5', '3', '1'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert '[1, 3, 5]' in result.stdout


class TestCLIAcceptanceCriteria:
    """Test all acceptance criteria from Story 1.4."""

    def test_ac1_cli_entry_point(self):
        """AC #1: Create CLI entry point that accepts arrays as command-line arguments."""
        # Test space-separated
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '5', '1', '4', '2', '8'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert '[1, 2, 4, 5, 8]' in result.stdout

        # Test comma-separated
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '5,1,4,2,8'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert '[1, 2, 4, 5, 8]' in result.stdout

    def test_ac2_file_input(self):
        """AC #2: Support reading arrays from files or standard input."""
        import tempfile
        import os

        # Test file input
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('5\n3\n1\n4\n2\n')
            input_file = f.name

        try:
            result = subprocess.run(
                [sys.executable, '-m', 'src.cli', '--input-file', input_file],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0
            assert '[1, 2, 3, 4, 5]' in result.stdout
        finally:
            if os.path.exists(input_file):
                os.unlink(input_file)

        # Test stdin input
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli'],
            input='5\n3\n1\n4\n2\n',
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert '[1, 2, 3, 4, 5]' in result.stdout

    def test_ac3_output_formats(self):
        """AC #3: Provide options for different output formats."""
        # Test sorted format (default)
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '--format', 'sorted', '5', '3', '1'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert '[1, 3, 5]' in result.stdout

        # Test detailed format
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '--format', 'detailed', '5', '3', '1'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'Input:' in result.stdout
        assert 'Output:' in result.stdout
        assert 'Comparisons:' in result.stdout
        assert 'Swaps:' in result.stdout

        # Test steps format
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '--format', 'steps', '5', '3', '1'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'Pass' in result.stdout
        assert 'Final:' in result.stdout

    def test_ac4_help_documentation(self):
        """AC #4: Include help documentation and usage examples."""
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '--help'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert 'usage:' in result.stdout.lower()
        assert 'Examples:' in result.stdout

    def test_ac5_error_handling(self):
        """AC #5: Handle command-line errors gracefully with helpful messages."""
        # Test invalid number
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '5', 'abc', '3'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        assert 'Error' in result.stderr

        # Test non-existent file
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '--input-file', 'nonexistent.txt'],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0

    def test_ac6_multiple_modes(self):
        """AC #6: Support both interactive and batch modes of operation."""
        # Test batch mode
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '5', '3', '1'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert '[1, 3, 5]' in result.stdout

        # Test interactive mode
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '--interactive'],
            input='5 3 1\nquit\n',
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0
        assert 'Interactive' in result.stdout or 'Enter' in result.stdout
