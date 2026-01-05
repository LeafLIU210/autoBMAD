"""
Unit tests for CodeQualityAgent.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
import json

from autoBMAD.epic_automation.code_quality_agent import CodeQualityAgent


@pytest.fixture
def mock_state_manager():
    """Create a mock StateManager."""
    return Mock()


@pytest.fixture
def quality_agent(mock_state_manager):
    """Create CodeQualityAgent for testing."""
    return CodeQualityAgent(mock_state_manager, "test-epic-001", skip_quality=False)


class TestCodeQualityAgent:
    """Test cases for CodeQualityAgent."""

    @pytest.mark.asyncio
    async def test_init(self, quality_agent):
        """Test CodeQualityAgent initialization."""
        assert quality_agent.state_manager is not None
        assert quality_agent.epic_id == "test-epic-001"
        assert quality_agent.max_iterations == 3
        assert quality_agent.skip_quality is False

    @pytest.mark.asyncio
    async def test_run_quality_gates_skip_quality(self, quality_agent):
        """Test quality gates bypass when skip_quality is True."""
        result = await quality_agent.run_quality_gates(
            source_dir="src",
            skip_quality=True
        )

        assert result["status"] == "skipped"
        assert "bypassed" in result["message"]

    @pytest.mark.asyncio
    async def test_run_quality_gates_no_source_dir(self, quality_agent):
        """Test quality gates with non-existent source directory."""
        result = await quality_agent.run_quality_gates(
            source_dir="nonexistent",
            skip_quality=False
        )

        assert result["status"] == "failed"
        assert "not found" in result["errors"][0]

    @pytest.mark.asyncio
    async def test_run_basedpyright_check_success(self, quality_agent):
        """Test basedpyright check execution with success."""
        with patch('basedpyright_workflow.run_basedpyright_check') as mock_check:
            mock_check.return_value = {
                'success': True,
                'errors': {},
                'file_count': 5,
                'error_count': 0,
                'json_output': {}
            }

            # Create a temporary directory with Python files
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                # Create test Python file
                test_file = Path(tmpdir) / "test.py"
                test_file.write_text("def hello():\n    return 'world'\n")

                result = await quality_agent.run_basedpyright_check(tmpdir)

                assert result['success'] is True
                assert result['error_count'] == 0

    @pytest.mark.asyncio
    async def test_run_basedpyright_check_with_errors(self, quality_agent):
        """Test basedpyright check execution with errors."""
        with patch('basedpyright_workflow.run_basedpyright_check') as mock_check:
            mock_check.return_value = {
                'success': False,
                'errors': {
                    '/test/file.py': [
                        {
                            'file': '/test/file.py',
                            'message': 'Argument missing type annotation',
                            'range': {
                                'start': {'line': 1, 'character': 0},
                                'end': {'line': 1, 'character': 5}
                            }
                        }
                    ]
                },
                'file_count': 1,
                'error_count': 1,
                'json_output': {}
            }

            # Create a temporary directory with Python files
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                # Create test Python file
                test_file = Path(tmpdir) / "test.py"
                test_file.write_text("def hello(name):\n    return f'Hello {name}'\n")

                result = await quality_agent.run_basedpyright_check(tmpdir)

                assert result['success'] is False
                assert result['error_count'] == 1

    @pytest.mark.asyncio
    async def test_run_ruff_check_success(self, quality_agent):
        """Test ruff check execution with success."""
        with patch('basedpyright_workflow.run_ruff_check') as mock_check:
            mock_check.return_value = {
                'success': True,
                'errors': {},
                'file_count': 5,
                'error_count': 0,
                'fixed_count': 0,
                'json_output': []
            }

            # Create a temporary directory with Python files
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                # Create test Python file
                test_file = Path(tmpdir) / "test.py"
                test_file.write_text("def hello():\n    return 'world'\n")

                result = await quality_agent.run_ruff_check(tmpdir)

                assert result['success'] is True
                assert result['error_count'] == 0

    @pytest.mark.asyncio
    async def test_run_ruff_check_with_errors(self, quality_agent):
        """Test ruff check execution with errors."""
        with patch('basedpyright_workflow.run_ruff_check') as mock_check:
            mock_check.return_value = {
                'success': False,
                'errors': {
                    '/test/file.py': [
                        {
                            'filename': '/test/file.py',
                            'text': 'Unused import: os',
                            'fix': None
                        }
                    ]
                },
                'file_count': 1,
                'error_count': 1,
                'fixed_count': 0,
                'json_output': []
            }

            # Create a temporary directory with Python files
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                # Create test Python file
                test_file = Path(tmpdir) / "test.py"
                test_file.write_text("import os\ndef hello():\n    return 'world'\n")

                result = await quality_agent.run_ruff_check(tmpdir)

                assert result['success'] is False
                assert result['error_count'] == 1

    @pytest.mark.asyncio
    async def test_fix_issues_no_api_key(self, quality_agent):
        """Test fix_issues without API key."""
        with patch.dict('os.environ', {}, clear=True):
            result = await quality_agent.fix_issues({})

            assert result is False

    @pytest.mark.asyncio
    async def test_fix_issues_with_api_key(self, quality_agent):
        """Test fix_issues with API key (mocked)."""
        with patch('os.environ.get') as mock_get, \
             patch('claude_agent_sdk.Claude') as mock_claude:

            # Mock API key
            mock_get.side_effect = lambda x: "test-api-key" if x == "ANTHROPIC_API_KEY" else None

            # Mock Claude client
            mock_client = AsyncMock()
            mock_claude.return_value = mock_client
            mock_client.messages.create.return_value = Mock(
                content=[Mock(text="Fixed all issues")]
            )

            errors = {
                "basedpyright": {
                    "errors": {}
                },
                "ruff": {
                    "errors": {}
                }
            }

            result = await quality_agent.fix_issues(errors)

            # Should return True since we mocked the Claude client
            assert result is True

    def test_create_fix_prompt(self, quality_agent):
        """Test _create_fix_prompt method."""
        errors = [
            {
                "file": "/test/file1.py",
                "tool": "basedpyright",
                "errors": [
                    {
                        "message": "Missing type annotation",
                        "range": {"start": {"line": 1}}
                    }
                ]
            },
            {
                "file": "/test/file2.py",
                "tool": "ruff",
                "errors": [
                    {"text": "Unused import"}
                ]
            }
        ]

        prompt = quality_agent._create_fix_prompt(errors)

        assert "file1.py" in prompt
        assert "basedpyright" in prompt
        assert "file2.py" in prompt
        assert "ruff" in prompt

    def test_generate_quality_report(self, quality_agent):
        """Test generate_quality_report method."""
        results = {
            "status": "completed",
            "message": "All checks passed",
            "iterations": 1,
            "file_count": 5,
            "basedpyright": {
                "success": True,
                "error_count": 0,
                "file_count": 5
            },
            "ruff": {
                "success": True,
                "error_count": 0,
                "file_count": 5,
                "fixed_count": 0
            }
        }

        report = quality_agent.generate_quality_report(results)

        # Verify report is valid JSON
        report_data = json.loads(report)

        assert report_data["status"] == "completed"
        assert report_data["epic_id"] == "test-epic-001"
        assert report_data["basedpyright"]["error_count"] == 0
        assert report_data["ruff"]["error_count"] == 0
