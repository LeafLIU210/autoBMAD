"""
Unit tests for pytest workflow module.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
import json

from fixtest_workflow.test_automation_workflow import (
    run_pytest_execution,
    parse_pytest_json,
    extract_failed_tests
)


class TestPytestWorkflow:
    """Test cases for pytest workflow module."""

    @pytest.mark.asyncio
    async def test_run_pytest_execution_success(self):
        """Test successful pytest execution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "tests"
            test_dir.mkdir()

            # Create a simple test file
            test_file = test_dir / "test_example.py"
            test_file.write_text("""
def test_pass():
    assert True
""")

            json_report = {
                "summary": {
                    "total": 1,
                    "passed": 1,
                    "failed": 0,
                    "error": 0,
                    "skipped": 0
                },
                "tests": []
            }

            with patch('builtins.open', mock_open(read_data=json.dumps(json_report))):
                with patch('pathlib.Path.exists', return_value=True):
                    result = await run_pytest_execution(
                        test_dir=str(test_dir),
                        json_report_file="test_results.json"
                    )

                    assert result["success"] is True
                    assert result["summary"]["total"] == 1
                    assert result["summary"]["passed"] == 1
                    assert result["summary"]["failed"] == 0
                    assert result["json_report_path"] == "test_results.json"

    @pytest.mark.asyncio
    async def test_run_pytest_execution_with_failures(self):
        """Test pytest execution with test failures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "tests"
            test_dir.mkdir()

            json_report = {
                "summary": {
                    "total": 2,
                    "passed": 1,
                    "failed": 1,
                    "error": 0,
                    "skipped": 0
                },
                "tests": [
                    {
                        "nodeid": "tests/test_example.py::test_pass",
                        "outcome": "passed"
                    },
                    {
                        "nodeid": "tests/test_example.py::test_fail",
                        "outcome": "failed"
                    }
                ]
            }

            with patch('builtins.open', mock_open(read_data=json.dumps(json_report))):
                with patch('pathlib.Path.exists', return_value=True):
                    result = await run_pytest_execution(
                        test_dir=str(test_dir),
                        json_report_file="test_results.json"
                    )

                    assert result["success"] is False
                    assert result["summary"]["total"] == 2
                    assert result["summary"]["passed"] == 1
                    assert result["summary"]["failed"] == 1

    @pytest.mark.asyncio
    async def test_run_pytest_execution_nonexistent_dir(self):
        """Test pytest execution with non-existent directory."""
        result = await run_pytest_execution(
            test_dir="nonexistent",
            json_report_file="test_results.json"
        )

        assert result["success"] is False
        assert "does not exist" in result["error"]

    def test_parse_pytest_json(self):
        """Test parsing pytest JSON report."""
        mock_report = {
            "summary": {
                "total": 5,
                "passed": 4,
                "failed": 1
            },
            "tests": [
                {
                    "nodeid": "tests/test_example.py::test_func",
                    "outcome": "failed"
                }
            ]
        }

        with patch('builtins.open', mock_open(read_data=json.dumps(mock_report))):
            result = parse_pytest_json("test_results.json")

            assert result["summary"]["total"] == 5
            assert result["summary"]["passed"] == 4
            assert len(result["tests"]) == 1

    def test_extract_failed_tests(self):
        """Test extraction of failed tests from pytest results."""
        pytest_results = {
            "tests": [
                {
                    "nodeid": "tests/test_example.py::test_pass",
                    "outcome": "passed",
                    "longrepr": ""
                },
                {
                    "nodeid": "tests/test_example.py::test_fail",
                    "outcome": "failed",
                    "longrepr": "AssertionError",
                    "traceback": ["test_example.py:45"]
                },
                {
                    "nodeid": "tests/test_example.py::test_error",
                    "outcome": "error",
                    "longrepr": "ValueError",
                    "traceback": ["test_example.py:50"]
                }
            ]
        }

        failures = extract_failed_tests(pytest_results)

        assert len(failures) == 2
        assert failures[0]["outcome"] == "failed"
        assert failures[1]["outcome"] == "error"
        assert "traceback" in failures[0]

    def test_extract_failed_tests_all_passed(self):
        """Test extraction when all tests pass."""
        pytest_results = {
            "tests": [
                {
                    "nodeid": "tests/test_example.py::test_pass",
                    "outcome": "passed"
                },
                {
                    "nodeid": "tests/test_example.py::test_another_pass",
                    "outcome": "passed"
                }
            ]
        }

        failures = extract_failed_tests(pytest_results)

        assert len(failures) == 0
