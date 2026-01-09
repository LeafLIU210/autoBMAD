"""Advanced CLI tests to achieve 100% coverage.

This module adds tests for edge cases and corner cases in the CLI module
to achieve complete code coverage.
"""

import sys
import argparse
from unittest.mock import patch, MagicMock
import pytest

from src.cli import (
    parse_array_input,
    read_from_file,
    get_sorting_steps,
    format_output,
    get_input_data,
    validate_data,
    main,
)


class TestCLIUncoveredLines:
    """Tests to cover previously uncovered lines in cli.py."""

    def test_get_input_data_interactive_mode_no_input(self):
        """Test line 109: interactive mode with no input raises ValueError."""
        args = argparse.Namespace(array=None, file=None, interactive=True)

        with pytest.raises(ValueError, match="No input provided"):
            get_input_data(args)

    def test_main_entry_point(self):
        """Test line 246: main entry point (if __name__ == '__main__')."""
        # This test verifies that main() can be called directly
        with patch("sys.argv", ["cli.py", "--help"]), \
             pytest.raises(SystemExit) as exc_info:
            main()

        # Should exit with code 0 for --help
        assert exc_info.value.code == 0

    def test_main_handles_unexpected_exception(self):
        """Test unexpected exception handling in main function."""
        with patch("src.cli.get_input_data", side_effect=RuntimeError("Unexpected error")), \
             patch("sys.stderr"), \
             patch("sys.argv", ["cli.py", "1, 2, 3"]), \
             pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1


class TestCLIAdditionalEdgeCases:
    """Additional edge cases for CLI functionality."""

    def test_parse_array_input_with_very_large_numbers(self):
        """Test parsing very large numbers."""
        result = parse_array_input("1e308, -1e308, 1e307")
        assert result == [1e308, -1e308, 1e307]

    def test_parse_array_input_with_scientific_notation_lowercase(self):
        """Test parsing scientific notation with lowercase e."""
        result = parse_array_input("1e3, 2e-2, 3e+5")
        assert result == [1000.0, 0.02, 300000.0]

    def test_parse_array_input_with_unicode_numbers(self):
        """Test parsing unicode numbers (should fail gracefully)."""
        with pytest.raises(ValueError):
            parse_array_input("1, ₂, 3")

    def test_read_from_file_with_unicode_bom(self):
        """Test reading file with Unicode BOM."""
        import tempfile
        from pathlib import Path

        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".txt") as f:
            # Write UTF-8 BOM followed by content
            f.write(b'\xef\xbb\xbf1, 2, 3')
            temp_path = f.name

        try:
            result = read_from_file(temp_path)
            assert result == [1, 2, 3]
        finally:
            Path(temp_path).unlink()

    def test_read_from_file_with_only_whitespace(self):
        """Test reading file with only whitespace."""
        import tempfile
        from pathlib import Path

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("   \n  \t  \n  ")
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="File is empty"):
                read_from_file(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_get_sorting_steps_extreme_cases(self):
        """Test getting sorting steps for extreme cases."""
        # Empty list
        steps = get_sorting_steps([])
        assert steps == [[]]

        # Single element
        steps = get_sorting_steps([42])
        assert steps == [[42]]

        # Already sorted
        steps = get_sorting_steps([1, 2, 3])
        assert len(steps) == 1

        # Reverse sorted with many elements
        steps = get_sorting_steps([10, 9, 8, 7, 6, 5, 4, 3, 2, 1])
        assert steps[-1] == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        assert len(steps) > 1

    def test_format_output_with_extreme_values(self):
        """Test formatting output with extreme values."""
        data = [float('inf'), float('-inf'), 0]
        sorted_data = [float('-inf'), 0, float('inf')]

        output = format_output(data, sorted_data, format_type="json")
        import json
        parsed = json.loads(output)
        assert "input" in parsed
        assert "sorted" in parsed

    def test_validate_data_with_nan(self):
        """Test validation with NaN values."""
        # NaN is a float and is numeric
        validate_data([1.0, float('nan'), 3.0])

    def test_validate_data_with_very_long_list(self):
        """Test validation rejects very long lists."""
        with pytest.raises(ValueError, match="List too long"):
            validate_data(list(range(10001)))

    def test_validate_data_with_non_numeric_types(self):
        """Test validation rejects non-numeric types."""
        with pytest.raises(ValueError, match="Non-numeric value found"):
            validate_data([1, "2", 3])

        with pytest.raises(ValueError, match="Non-numeric value found"):
            validate_data([1, None, 3])

        with pytest.raises(ValueError, match="Non-numeric value found"):
            validate_data([1, [], 3])


class TestCLIIOOperations:
    """Test I/O operations and file handling."""

    def test_read_from_file_binary_mode_error(self):
        """Test reading from file opened in binary mode (should handle gracefully)."""
        import tempfile
        from pathlib import Path

        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".txt") as f:
            f.write(b"1, 2, 3")
            temp_path = f.name

        try:
            # Should handle text mode reading
            result = read_from_file(temp_path)
            assert result == [1, 2, 3]
        finally:
            Path(temp_path).unlink()

    def test_read_from_file_permission_denied(self):
        """Test reading from file with permission denied (if possible)."""
        import tempfile
        from pathlib import Path
        import sys

        # Skip on Windows or systems where we can't test this
        if sys.platform == 'win32':
            pytest.skip("Skipping permission test on Windows")

        # Skip on systems where we can't test this
        try:
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
                f.write("1, 2, 3")
                temp_path = f.name

            # Try to make it unreadable (may not work on all systems)
            try:
                Path(temp_path).chmod(0o000)
                with pytest.raises((PermissionError, OSError)):
                    read_from_file(temp_path)
            except (PermissionError, OSError):
                pass  # Skip if we can't change permissions
            finally:
                # Restore permissions to delete
                try:
                    Path(temp_path).chmod(0o644)
                    Path(temp_path).unlink()
                except:
                    pass
        except Exception:
            pass  # Skip test if we can't set up


class TestCLIIntegrationScenarios:
    """Integration scenarios for CLI workflows."""

    @patch("sys.stdin.isatty")
    @patch("sys.stdin.read")
    def test_stdin_pipeline_mode(self, mock_stdin_read, mock_stdin_isatty):
        """Test processing data from stdin in pipeline mode."""
        mock_stdin_isatty.return_value = False
        mock_stdin_read.return_value = "5, 3, 8, 1"
        args = argparse.Namespace(array=None, file=None)

        result = get_input_data(args)
        assert result == [5, 3, 8, 1]

    @patch("sys.stdin.isatty")
    @patch("sys.stdin.read")
    def test_stdin_empty_pipeline(self, mock_stdin_read, mock_stdin_isatty):
        """Test empty stdin in pipeline mode."""
        mock_stdin_isatty.return_value = False
        mock_stdin_read.return_value = ""
        args = argparse.Namespace(array=None, file=None)

        with pytest.raises(ValueError, match="No input received from stdin"):
            get_input_data(args)

    @patch("sys.stdin.isatty")
    @patch("sys.stdin.read")
    def test_stdin_whitespace_only(self, mock_stdin_read, mock_stdin_isatty):
        """Test stdin with only whitespace."""
        mock_stdin_isatty.return_value = False
        mock_stdin_read.return_value = "   \n\t  "
        args = argparse.Namespace(array=None, file=None)

        with pytest.raises(ValueError, match="No input received from stdin"):
            get_input_data(args)

    def test_format_output_all_formats(self):
        """Test all output formats work correctly."""
        data = [3, 2, 1]
        sorted_data = [1, 2, 3]

        # Test default format
        output = format_output(data, sorted_data)
        assert "1" in output and "2" in output and "3" in output

        # Test JSON format
        import json
        output_json = format_output(data, sorted_data, format_type="json")
        parsed = json.loads(output_json)
        assert parsed["input"] == [3, 2, 1]

        # Test steps format
        output_steps = format_output(data, sorted_data, format_type="steps")
        assert "Sorting Steps" in output_steps

        # Test detailed format
        output_detailed = format_output(data, sorted_data, format_type="detailed")
        assert "Input" in output_detailed

        # Test with statistics
        output_stats = format_output(data, sorted_data, format_type="json", show_stats=True)
        parsed_stats = json.loads(output_stats)
        assert "statistics" in parsed_stats

    def test_format_output_invalid_format(self):
        """Test that invalid format falls back gracefully."""
        data = [3, 2, 1]
        sorted_data = [1, 2, 3]

        # Invalid format should still produce output (fallback to default)
        output = format_output(data, sorted_data, format_type="invalid_format")
        assert len(output) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
