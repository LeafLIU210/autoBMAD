"""
Unit tests for ruff_workflow module.
"""

import pytest
import asyncio
import json
from unittest.mock import patch, AsyncMock
from pathlib import Path

# Check if basedpyright_workflow module exists
try:
    from basedpyright_workflow.ruff_workflow import (
        run_ruff_check,
        parse_ruff_json
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

# Skip all tests in this module if basedpyright_workflow doesn't exist
pytestmark = pytest.mark.skipif(
    not HAS_MODULE,
    reason="basedpyright_workflow.ruff_workflow module not found - tests will be implemented when module is ready"
)


@pytest.fixture
def sample_ruff_output():
    """Sample ruff JSON output."""
    return [
        {
            "filename": "/test/file1.py",
            "source": "import os",
            "text": "Line is too long (85 > 88 characters)",
            "fix": {
                "message": "Delete items",
                "content_edits": [
                    {
                        "range": {
                            "start": {"row": 0, "column": 0},
                            "end": {"row": 0, "column": 85}
                        },
                        "replacement": "import os"
                    }
                ]
            }
        },
        {
            "filename": "/test/file1.py",
            "source": "import sys",
            "text": "Unused import: sys",
            "fix": {
                "message": "Delete items",
                "content_edits": []
            }
        },
        {
            "filename": "/test/file2.py",
            "source": "x=1+2",
            "text": "Missing whitespace around operator",
            "fix": {
                "message": "Insert whitespace",
                "content_edits": [
                    {
                        "range": {
                            "start": {"row": 0, "column": 1},
                            "end": {"row": 0, "column": 4}
                        },
                        "replacement": "x = 1 + 2"
                    }
                ]
            }
        }
    ]


class TestRuffWorkflow:
    """Test cases for ruff_workflow."""

    @pytest.mark.asyncio
    async def test_run_ruff_check_tool_not_found(self):
        """Test ruff check when tool is not found."""
        with patch('shutil.which', return_value=None):
            result = await run_ruff_check("/test/src")

            assert result['success'] is False
            assert result['error_count'] == 0
            assert "not installed" in result['message']

    @pytest.mark.asyncio
    async def test_run_ruff_check_directory_not_found(self):
        """Test ruff check with non-existent directory."""
        with patch('shutil.which', return_value="/usr/bin/ruff"):
            result = await run_ruff_check("/nonexistent")

            assert result['success'] is False
            assert result['error_count'] == 0
            assert "not found" in result['message']

    @pytest.mark.asyncio
    async def test_run_ruff_check_success(self, sample_ruff_output):
        """Test ruff check with successful execution."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test Python file
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("import os\ndef hello():\n    return 'world'\n")

            with patch('shutil.which', return_value="/usr/bin/ruff"), \
                 patch('asyncio.create_subprocess_exec') as mock_process:

                # Mock successful process execution
                mock_proc = AsyncMock()
                mock_proc.communicate.return_value = (
                    json.dumps(sample_ruff_output).encode('utf-8'),
                    b''
                )
                mock_process.return_value = mock_proc

                result = await run_ruff_check(tmpdir, auto_fix=True)

                assert result['success'] is False  # Has errors
                assert result['error_count'] == 3
                assert result['file_count'] == 2
                assert result['fixed_count'] == 3
                assert '/test/file1.py' in result['errors']
                assert '/test/file2.py' in result['errors']

    @pytest.mark.asyncio
    async def test_run_ruff_check_no_errors(self):
        """Test ruff check with no errors."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def hello() -> str:\n    return 'world'\n")

            with patch('shutil.which', return_value="/usr/bin/ruff"), \
                 patch('asyncio.create_subprocess_exec') as mock_process:

                mock_proc = AsyncMock()
                mock_proc.communicate.return_value = (
                    json.dumps([]).encode('utf-8'),
                    b''
                )
                mock_process.return_value = mock_proc

                result = await run_ruff_check(tmpdir)

                assert result['success'] is True
                assert result['error_count'] == 0
                assert result['file_count'] == 0
                assert result['fixed_count'] == 0

    @pytest.mark.asyncio
    async def test_run_ruff_check_invalid_json(self):
        """Test ruff check with invalid JSON output."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def hello():\n    return 'world'\n")

            with patch('shutil.which', return_value="/usr/bin/ruff"), \
                 patch('asyncio.create_subprocess_exec') as mock_process:

                mock_proc = AsyncMock()
                mock_proc.communicate.return_value = (
                    b'invalid json output',
                    b''
                )
                mock_process.return_value = mock_proc

                result = await run_ruff_check(tmpdir)

                assert result['success'] is False
                assert "JSON parse error" in result['message']

    @pytest.mark.asyncio
    async def test_run_ruff_check_timeout(self):
        """Test ruff check with timeout."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def hello():\n    return 'world'\n")

            with patch('shutil.which', return_value="/usr/bin/ruff"), \
                 patch('asyncio.create_subprocess_exec') as mock_process:

                mock_process.side_effect = asyncio.TimeoutError()

                result = await run_ruff_check(tmpdir)

                assert result['success'] is False
                assert "timed out" in result['message']

    @pytest.mark.asyncio
    async def test_run_ruff_check_with_config(self, sample_ruff_output):
        """Test ruff check with custom config path."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "pyproject.toml"
            config_file.write_text("[tool.ruff]\n")

            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("import os\ndef hello():\n    return 'world'\n")

            with patch('shutil.which', return_value="/usr/bin/ruff"), \
                 patch('asyncio.create_subprocess_exec') as mock_process:

                mock_proc = AsyncMock()
                mock_proc.communicate.return_value = (
                    json.dumps(sample_ruff_output).encode('utf-8'),
                    b''
                )
                mock_process.return_value = mock_proc

                result = await run_ruff_check(tmpdir, auto_fix=True, config_path=str(config_file))

                assert result['success'] is False

    @pytest.mark.asyncio
    async def test_run_ruff_check_no_auto_fix(self, sample_ruff_output):
        """Test ruff check without auto-fix."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("import os\ndef hello():\n    return 'world'\n")

            with patch('shutil.which', return_value="/usr/bin/ruff"), \
                 patch('asyncio.create_subprocess_exec') as mock_process:

                mock_proc = AsyncMock()
                mock_proc.communicate.return_value = (
                    json.dumps(sample_ruff_output).encode('utf-8'),
                    b''
                )
                mock_process.return_value = mock_proc

                result = await run_ruff_check(tmpdir, auto_fix=False)

                assert result['success'] is False
                assert result['error_count'] == 3

    def test_parse_ruff_json_list_format(self, sample_ruff_output):
        """Test parsing ruff JSON in list format."""
        json_str = json.dumps(sample_ruff_output)
        parsed = parse_ruff_json(json_str)

        assert len(parsed) == 3
        assert parsed[0]['filename'] == '/test/file1.py'
        assert 'Line is too long' in parsed[0]['text']

    def test_parse_ruff_json_dict_format(self):
        """Test parsing ruff JSON in dict format."""
        dict_format = {
            "results": [
                {
                    "filename": "/test/file.py",
                    "text": "Unused import"
                }
            ]
        }

        json_str = json.dumps(dict_format)
        parsed = parse_ruff_json(json_str)

        assert len(parsed) == 1
        assert parsed[0]['filename'] == '/test/file.py'

    def test_parse_ruff_json_invalid(self):
        """Test parsing invalid ruff JSON."""
        parsed = parse_ruff_json("invalid json")

        assert parsed == []

    def test_parse_ruff_json_empty(self):
        """Test parsing empty ruff JSON."""
        json_str = json.dumps([])
        parsed = parse_ruff_json(json_str)

        assert parsed == []

    def test_parse_ruff_json_unexpected_format(self):
        """Test parsing JSON with unexpected format."""
        json_str = json.dumps({"unexpected": "format"})
        parsed = parse_ruff_json(json_str)

        assert parsed == []
