"""
Unit tests for basedpyright_workflow module.
"""

import pytest
import asyncio
import json
from unittest.mock import patch, AsyncMock
from pathlib import Path

# Check if basedpyright_workflow module exists
try:
    from basedpyright_workflow.basedpyright_workflow import (
        run_basedpyright_check,
        parse_basedpyright_json
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

# Skip all tests in this module if basedpyright_workflow doesn't exist
pytestmark = pytest.mark.skipif(
    not HAS_MODULE,
    reason="basedpyright_workflow module not found - tests will be implemented when module is ready"
)


@pytest.fixture
def sample_basedpyright_output():
    """Sample basedpyright JSON output."""
    return {
        "version": "1.1.0",
        "time": "2026-01-05T10:00:00Z",
        "generalDiagnostics": [
            {
                "file": "/test/file1.py",
                "severity": "error",
                "message": "Argument missing type annotation",
                "range": {
                    "start": {"line": 10, "character": 5},
                    "end": {"line": 10, "character": 15}
                },
                "rule": "reportGeneralTypeIssues"
            },
            {
                "file": "/test/file1.py",
                "severity": "warning",
                "message": "Optional member access",
                "range": {
                    "start": {"line": 15, "character": 10},
                    "end": {"line": 15, "character": 20}
                },
                "rule": "reportOptionalMemberAccess"
            },
            {
                "file": "/test/file2.py",
                "severity": "error",
                "message": "Missing return type annotation",
                "range": {
                    "start": {"line": 5, "character": 0},
                    "end": {"line": 5, "character": 10}
                },
                "rule": "reportGeneralTypeIssues"
            }
        ],
        "summary": {
            "errorCount": 2,
            "warningCount": 1,
            "informationCount": 0
        }
    }


class TestBasedpyrightWorkflow:
    """Test cases for basedpyright_workflow."""

    @pytest.mark.asyncio
    async def test_run_basedpyright_check_tool_not_found(self):
        """Test basedpyright check when tool is not found."""
        with patch('shutil.which', return_value=None):
            result = await run_basedpyright_check("/test/src")

            assert result['success'] is False
            assert result['error_count'] == 0
            assert "not installed" in result['message']

    @pytest.mark.asyncio
    async def test_run_basedpyright_check_directory_not_found(self):
        """Test basedpyright check with non-existent directory."""
        with patch('shutil.which', return_value="/usr/bin/basedpyright"):
            result = await run_basedpyright_check("/nonexistent")

            assert result['success'] is False
            assert result['error_count'] == 0
            assert "not found" in result['message']

    @pytest.mark.asyncio
    async def test_run_basedpyright_check_success(self, sample_basedpyright_output):
        """Test basedpyright check with successful execution."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test Python file
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def hello():\n    return 'world'\n")

            with patch('shutil.which', return_value="/usr/bin/basedpyright"), \
                 patch('asyncio.create_subprocess_exec') as mock_process:

                # Mock successful process execution
                mock_proc = AsyncMock()
                mock_proc.communicate.return_value = (
                    json.dumps(sample_basedpyright_output).encode('utf-8'),
                    b''
                )
                mock_process.return_value = mock_proc

                result = await run_basedpyright_check(tmpdir)

                assert result['success'] is False  # Has errors
                assert result['error_count'] == 3  # 2 errors + 1 warning
                assert result['file_count'] == 2
                assert '/test/file1.py' in result['errors']
                assert '/test/file2.py' in result['errors']

    @pytest.mark.asyncio
    async def test_run_basedpyright_check_no_errors(self):
        """Test basedpyright check with no errors."""
        no_errors_output = {
            "version": "1.1.0",
            "generalDiagnostics": [],
            "summary": {
                "errorCount": 0,
                "warningCount": 0,
                "informationCount": 0
            }
        }

        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def hello() -> str:\n    return 'world'\n")

            with patch('shutil.which', return_value="/usr/bin/basedpyright"), \
                 patch('asyncio.create_subprocess_exec') as mock_process:

                mock_proc = AsyncMock()
                mock_proc.communicate.return_value = (
                    json.dumps(no_errors_output).encode('utf-8'),
                    b''
                )
                mock_process.return_value = mock_proc

                result = await run_basedpyright_check(tmpdir)

                assert result['success'] is True
                assert result['error_count'] == 0
                assert result['file_count'] == 0

    @pytest.mark.asyncio
    async def test_run_basedpyright_check_invalid_json(self):
        """Test basedpyright check with invalid JSON output."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def hello():\n    return 'world'\n")

            with patch('shutil.which', return_value="/usr/bin/basedpyright"), \
                 patch('asyncio.create_subprocess_exec') as mock_process:

                mock_proc = AsyncMock()
                mock_proc.communicate.return_value = (
                    b'invalid json output',
                    b''
                )
                mock_process.return_value = mock_proc

                result = await run_basedpyright_check(tmpdir)

                assert result['success'] is False
                assert "JSON parse error" in result['message']

    @pytest.mark.asyncio
    async def test_run_basedpyright_check_timeout(self):
        """Test basedpyright check with timeout."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def hello():\n    return 'world'\n")

            with patch('shutil.which', return_value="/usr/bin/basedpyright"), \
                 patch('asyncio.create_subprocess_exec') as mock_process:

                mock_process.side_effect = asyncio.TimeoutError()

                result = await run_basedpyright_check(tmpdir)

                assert result['success'] is False
                assert "timed out" in result['message']

    @pytest.mark.asyncio
    async def test_run_basedpyright_check_with_config(self, sample_basedpyright_output):
        """Test basedpyright check with custom config path."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "pyproject.toml"
            config_file.write_text("[tool.basedpyright]\n")

            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def hello():\n    return 'world'\n")

            with patch('shutil.which', return_value="/usr/bin/basedpyright"), \
                 patch('asyncio.create_subprocess_exec') as mock_process:

                mock_proc = AsyncMock()
                mock_proc.communicate.return_value = (
                    json.dumps(sample_basedpyright_output).encode('utf-8'),
                    b''
                )
                mock_process.return_value = mock_proc

                result = await run_basedpyright_check(tmpdir, config_path=str(config_file))

                assert result['success'] is False

    def test_parse_basedpyright_json_valid(self, sample_basedpyright_output):
        """Test parsing valid basedpyright JSON."""
        json_str = json.dumps(sample_basedpyright_output)
        parsed = parse_basedpyright_json(json_str)

        assert len(parsed) == 3
        assert parsed[0]['file'] == '/test/file1.py'
        assert parsed[0]['severity'] == 'error'
        assert 'Missing type annotation' in parsed[0]['message']

    def test_parse_basedpyright_json_invalid(self):
        """Test parsing invalid basedpyright JSON."""
        parsed = parse_basedpyright_json("invalid json")

        assert parsed == []

    def test_parse_basedpyright_json_empty(self):
        """Test parsing empty basedpyright JSON."""
        json_str = json.dumps({"generalDiagnostics": []})
        parsed = parse_basedpyright_json(json_str)

        assert parsed == []
