"""
Test Automation Workflow - Pytest integration for test automation.

Executes pytest with JSON report generation for automated test processing.
"""

import json
import asyncio
import sys
import time
from pathlib import Path
from typing import Dict, Any, List


async def run_pytest_execution(
    test_dir: str,
    json_report_file: str = "test_results.json",
    max_failures: int = None
) -> Dict[str, Any]:
    """
    Execute pytest on test directory with JSON reporting.

    Args:
        test_dir: Directory containing tests
        json_report_file: Path for JSON report output
        max_failures: Stop after N failures

    Returns:
        Dict containing:
            - success: Boolean indicating if all tests passed
            - summary: Test execution summary
            - json_report_path: Path to generated JSON report
            - execution_time: Total execution time
    """
    start_time = time.time()

    try:
        # Validate test directory
        test_path = Path(test_dir)
        if not test_path.exists() or not test_path.is_dir():
            return {
                "success": False,
                "error": f"Test directory does not exist: {test_dir}",
                "summary": {"total": 0, "passed": 0, "failed": 0, "error": 0, "skipped": 0},
                "json_report_path": json_report_file,
                "execution_time": 0.0
            }

        # Build pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_path),
            "--json-report",
            f"--json-report-file={json_report_file}",
            "-v"
        ]

        if max_failures:
            cmd.append(f"--maxfail={max_failures}")

        # Execute pytest
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        execution_time = time.time() - start_time

        # Parse results
        if Path(json_report_file).exists():
            try:
                with open(json_report_file) as f:
                    pytest_results = json.load(f)

                summary = pytest_results.get("summary", {})
                total = summary.get("total", 0)
                passed = summary.get("passed", 0)
                failed = summary.get("failed", 0)
                error = summary.get("error", 0)
                skipped = summary.get("skipped", 0)

                return {
                    "success": failed == 0 and error == 0,
                    "summary": {
                        "total": total,
                        "passed": passed,
                        "failed": failed,
                        "error": error,
                        "skipped": skipped
                    },
                    "json_report_path": json_report_file,
                    "execution_time": execution_time,
                    "return_code": process.returncode
                }

            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Failed to parse JSON report: {e}",
                    "summary": {"total": 0, "passed": 0, "failed": 0, "error": 0, "skipped": 0},
                    "json_report_path": json_report_file,
                    "execution_time": execution_time
                }
        else:
            # No JSON report generated
            return {
                "success": process.returncode == 0,
                "error": "JSON report was not generated",
                "summary": {"total": 0, "passed": 0, "failed": 0, "error": 0, "skipped": 0},
                "json_report_path": json_report_file,
                "execution_time": execution_time,
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else ""
            }

    except Exception as e:
        execution_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "summary": {"total": 0, "passed": 0, "failed": 0, "error": 0, "skipped": 0},
            "json_report_path": json_report_file,
            "execution_time": execution_time
        }


def parse_pytest_json(json_report_path: str) -> Dict[str, Any]:
    """
    Parse pytest JSON report into structured data.

    Args:
        json_report_path: Path to pytest JSON report

    Returns:
        Dict containing parsed test results
    """
    try:
        if not Path(json_report_path).exists():
            return {
                "error": f"JSON report not found: {json_report_path}",
                "tests": [],
                "summary": {"total": 0, "passed": 0, "failed": 0, "error": 0, "skipped": 0}
            }

        with open(json_report_path) as f:
            results = json.load(f)

        return results

    except Exception as e:
        return {
            "error": f"Failed to parse JSON report: {e}",
            "tests": [],
            "summary": {"total": 0, "passed": 0, "failed": 0, "error": 0, "skipped": 0}
        }


def extract_failed_tests(pytest_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract only failed/errored tests from pytest results.

    Args:
        pytest_results: Parsed pytest JSON results

    Returns:
        List of failed test information
    """
    failed_tests = []

    try:
        tests = pytest_results.get("tests", [])

        for test in tests:
            outcome = test.get("outcome", "")

            if outcome in ["failed", "error"]:
                # Extract test file and name from nodeid
                nodeid = test.get("nodeid", "")
                parts = nodeid.split("::")

                test_file = parts[0] if len(parts) > 0 else ""
                test_name = parts[1] if len(parts) > 1 else ""

                failed_test = {
                    "nodeid": nodeid,
                    "test_file": test_file,
                    "test_name": test_name,
                    "outcome": outcome,
                    "when": test.get("when", ""),
                    "duration": test.get("duration", 0.0),
                    "longrepr": test.get("longrepr", ""),
                    "traceback": test.get("traceback", []),
                    "caplog": test.get("caplog", ""),
                    "user_properties": test.get("user_properties", [])
                }

                failed_tests.append(failed_test)

        return failed_tests

    except Exception:
        return []


def get_test_summary(pytest_results: Dict[str, Any]) -> Dict[str, int]:
    """
    Get test execution summary from pytest results.

    Args:
        pytest_results: Parsed pytest JSON results

    Returns:
        Dict with test counts
    """
    try:
        return pytest_results.get("summary", {})
    except Exception:
        return {"total": 0, "passed": 0, "failed": 0, "error": 0, "skipped": 0}
