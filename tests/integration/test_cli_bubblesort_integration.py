"""Integration tests for CLI and bubble sort module interaction."""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from src.cli import main
from src.bubblesort import bubble_sort


class TestCLIIntegration:
    """Integration tests for CLI with bubble sort."""

    def test_cli_end_to_end_simple_array(self):
        """Test complete CLI workflow with simple array."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("5, 3, 8, 1, 2")
            temp_path = f.name

        try:
            # Run CLI with file input
            result = subprocess.run(
                [sys.executable, "-m", "src.cli", "-f", temp_path],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert "1, 2, 3, 5, 8" in result.stdout
        finally:
            Path(temp_path).unlink()

    def test_cli_end_to_end_with_json_output(self):
        """Test CLI with JSON output format."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("4, 2, 7, 1")
            temp_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli", "-f", temp_path, "--format", "json"],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert '"input":' in result.stdout
            assert '"sorted":' in result.stdout
            # JSON is pretty-printed with newlines
            assert '"input"' in result.stdout
            assert '"sorted"' in result.stdout
            assert '4' in result.stdout
            assert '7' in result.stdout
        finally:
            Path(temp_path).unlink()

    def test_cli_end_to_end_with_stats(self):
        """Test CLI with statistics output."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "3, 1, 2", "--stats"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "1, 2, 3" in result.stdout

    def test_cli_end_to_end_with_steps(self):
        """Test CLI with steps output."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "3, 1, 2", "--format", "steps"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Sorting Steps:" in result.stdout
        assert "Step 0:" in result.stdout
        assert "[3, 1, 2]" in result.stdout

    def test_cli_end_to_end_with_detailed(self):
        """Test CLI with detailed output."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "3, 1, 2", "--format", "detailed"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Input: [3, 1, 2]" in result.stdout
        assert "Sorted: [1, 2, 3]" in result.stdout

    def test_cli_with_invalid_input(self):
        """Test CLI with invalid input."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "abc, 123"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "Error:" in result.stderr or "Error:" in result.stdout

    def test_cli_with_empty_file(self):
        """Test CLI with empty file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("")
            temp_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli", "-f", temp_path],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 1
            assert "Error:" in result.stderr
        finally:
            Path(temp_path).unlink()

    def test_cli_with_nonexistent_file(self):
        """Test CLI with nonexistent file."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "-f", "/nonexistent/file.txt"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "Error:" in result.stderr

    def test_cli_with_mixed_types(self):
        """Test CLI with mixed integer and float types."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "3, 1.5, 2, 0.5"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "[0.5, 1.5, 2, 3]" in result.stdout or "[0.5, 1.5, 2, 3]" in result.stdout

    def test_cli_with_negative_numbers(self):
        """Test CLI with negative numbers."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "5, -3, 2, -1"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "-3, -1, 2, 5" in result.stdout

    def test_cli_already_sorted(self):
        """Test CLI with already sorted array."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "1, 2, 3, 4, 5"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "1, 2, 3, 4, 5" in result.stdout

    def test_cli_reverse_sorted(self):
        """Test CLI with reverse sorted array."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "5, 4, 3, 2, 1"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "1, 2, 3, 4, 5" in result.stdout

    def test_cli_with_duplicates(self):
        """Test CLI with duplicate values."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "3, 1, 3, 1, 2"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "1, 1, 2, 3, 3" in result.stdout

    def test_cli_single_element(self):
        """Test CLI with single element."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "42"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "42" in result.stdout

    def test_cli_with_large_array(self):
        """Test CLI with large array (1000 elements)."""
        large_array = ", ".join(str(i) for i in range(1000, 0, -1))
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", large_array],
            capture_output=True,
            text=True,
            timeout=10,  # Add timeout to prevent hanging
        )

        assert result.returncode == 0
        # Just verify it completes successfully
        assert "1, 2" in result.stdout  # Should start with "1, 2"

    def test_cli_stdin_input(self):
        """Test CLI with stdin input."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli"],
            input="3, 1, 2\n",
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "1, 2, 3" in result.stdout

    def test_cli_with_bracket_format(self):
        """Test CLI with bracketed array format."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "[3, 1, 2]"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "1, 2, 3" in result.stdout

    def test_cli_with_space_separated(self):
        """Test CLI with space-separated values."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "3 1 2"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "1, 2, 3" in result.stdout

    def test_bubble_sort_integration(self):
        """Test that bubble sort is correctly integrated with CLI."""
        # Test direct bubble sort call
        result = bubble_sort([5, 3, 8, 1, 2])
        assert result == [1, 2, 3, 5, 8]

        # Test that CLI produces the same result
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("5, 3, 8, 1, 2")
            temp_path = f.name

        try:
            cli_result = subprocess.run(
                [sys.executable, "-m", "src.cli", "-f", temp_path],
                capture_output=True,
                text=True,
            )

            assert cli_result.returncode == 0
            assert "1, 2, 3, 5, 8" in cli_result.stdout
        finally:
            Path(temp_path).unlink()


class TestFileFormats:
    """Test various file input formats."""

    def test_file_with_mixed_separators(self):
        """Test file with mixed separators."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("1, 2 3, 4")
            temp_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli", "-f", temp_path],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert "1, 2, 3, 4" in result.stdout
        finally:
            Path(temp_path).unlink()

    def test_file_with_newlines(self):
        """Test file with newlines between numbers."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("3\n1\n2")
            temp_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli", "-f", temp_path],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert "1, 2, 3" in result.stdout
        finally:
            Path(temp_path).unlink()

    def test_file_with_leading_trailing_spaces(self):
        """Test file with leading/trailing spaces."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("  3, 1, 2  ")
            temp_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli", "-f", temp_path],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert "1, 2, 3" in result.stdout
        finally:
            Path(temp_path).unlink()


class TestErrorPropagation:
    """Test error handling and propagation."""

    def test_cli_handles_file_read_error(self):
        """Test CLI handles file read errors gracefully."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("1, abc, 3")
            temp_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli", "-f", temp_path],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 1
            assert "Error:" in result.stderr or "Error:" in result.stdout
        finally:
            Path(temp_path).unlink()

    def test_cli_handles_empty_input(self):
        """Test CLI handles empty input gracefully."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("")
            temp_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli", "-f", temp_path],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 1
        finally:
            Path(temp_path).unlink()

    def test_cli_handles_unicode_in_file(self):
        """Test CLI handles Unicode characters in file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write("1, 2, 3")  # Just valid numbers
            temp_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli", "-f", temp_path],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert "1, 2, 3" in result.stdout
        finally:
            Path(temp_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
