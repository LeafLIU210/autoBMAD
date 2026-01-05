"""
Tests for CLI interface of epic_driver.py
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch

# Add the epic_automation directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "autoBMAD" / "epic_automation"))

from epic_driver import parse_arguments, EpicDriver


class TestCLIInterface:
    """Test CLI argument parsing and functionality."""

    def test_parse_arguments_basic(self):
        """Test basic argument parsing with positional argument."""
        with patch('sys.argv', ['epic_driver.py', 'docs/epics/my-epic.md']):
            args = parse_arguments()
            assert args.epic_path == 'docs/epics/my-epic.md'
            assert args.max_iterations == 3  # default value
            assert args.retry_failed == False  # default value
            assert args.verbose == False  # default value
            assert args.concurrent == False  # default value

    def test_parse_arguments_max_iterations(self):
        """Test --max-iterations option."""
        with patch('sys.argv', ['epic_driver.py', 'docs/epics/my-epic.md', '--max-iterations', '5']):
            args = parse_arguments()
            assert args.max_iterations == 5

    def test_parse_arguments_retry_failed(self):
        """Test --retry-failed option."""
        with patch('sys.argv', ['epic_driver.py', 'docs/epics/my-epic.md', '--retry-failed']):
            args = parse_arguments()
            assert args.retry_failed == True

    def test_parse_arguments_verbose(self):
        """Test --verbose option."""
        with patch('sys.argv', ['epic_driver.py', 'docs/epics/my-epic.md', '--verbose']):
            args = parse_arguments()
            assert args.verbose == True

    def test_parse_arguments_concurrent(self):
        """Test --concurrent option."""
        with patch('sys.argv', ['epic_driver.py', 'docs/epics/my-epic.md', '--concurrent']):
            args = parse_arguments()
            assert args.concurrent == True

    def test_parse_arguments_all_options(self):
        """Test all CLI options together."""
        with patch('sys.argv', [
            'epic_driver.py',
            'docs/epics/my-epic.md',
            '--max-iterations', '10',
            '--retry-failed',
            '--verbose',
            '--concurrent'
        ]):
            args = parse_arguments()
            assert args.epic_path == 'docs/epics/my-epic.md'
            assert args.max_iterations == 10
            assert args.retry_failed == True
            assert args.verbose == True
            assert args.concurrent == True

    def test_help_message(self):
        """Test that help message is displayed with --help."""
        with pytest.raises(SystemExit) as exc_info:
            with patch('sys.argv', ['epic_driver.py', '--help']):
                parse_arguments()
        assert exc_info.value.code == 0

    def test_epic_driver_initialization(self):
        """Test EpicDriver initialization with CLI options."""
        driver = EpicDriver(
            epic_path='docs/epics/my-epic.md',
            max_iterations=5,
            retry_failed=True,
            verbose=True,
            concurrent=False
        )
        assert driver.epic_path == Path('docs/epics/my-epic.md')
        assert driver.max_iterations == 5
        assert driver.retry_failed == True
        assert driver.verbose == True
        assert driver.concurrent == False

    def test_epic_driver_default_initialization(self):
        """Test EpicDriver initialization with default values."""
        driver = EpicDriver(epic_path='docs/epics/my-epic.md')
        assert driver.epic_path == Path('docs/epics/my-epic.md')
        assert driver.max_iterations == 3  # default
        assert driver.retry_failed == False  # default
        assert driver.verbose == False  # default
        assert driver.concurrent == False  # default

    @pytest.mark.parametrize("invalid_path", [
        "nonexistent/file.md",
        "docs/epics/missing.md",
        "/tmp/fake-epic.md"
    ])
    def test_nonexistent_epic_file(self, invalid_path):
        """Test handling of nonexistent epic files."""
        # This test would need to be run in main() context
        # For now, we verify the argparse validation works
        with patch('sys.argv', ['epic_driver.py', invalid_path]):
            # The file doesn't exist, but argparse won't catch this
            # The check happens in main() after parsing
            args = parse_arguments()
            assert args.epic_path == invalid_path

    def test_argument_validation(self):
        """Test that invalid arguments are rejected."""
        # Test invalid max-iterations (negative number)
        with pytest.raises(SystemExit):
            with patch('sys.argv', ['epic_driver.py', 'docs/epics/my-epic.md', '--max-iterations', '-1']):
                parse_arguments()

    def test_missing_required_argument(self):
        """Test that missing epic_path raises error."""
        with pytest.raises(SystemExit):
            with patch('sys.argv', ['epic_driver.py']):
                parse_arguments()
