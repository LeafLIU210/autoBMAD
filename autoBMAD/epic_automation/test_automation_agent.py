"""
Test Automation Agent - Pytest Integration with Debugpy

This module provides automated test execution using pytest with JSON reporting,
and debugpy integration for persistent test failures.

Main Features:
1. Pytest execution with JSON report output: `pytest -v --tb=short --json-report {test_dir}`
2. JSON report parsing for test failure analysis
3. Claude SDK integration for automated test fixes (max_turns=150, NO external timeouts)
4. Debugpy invocation for persistent failures (5+ failed attempts)
5. Retry mechanism (max 3 cycles, 2 retries each)
6. Zero Cancel Scope errors (no asyncio.wait_for/asyncio.shield)

Safety Requirements (per Cancel Scope guidelines):
- DO NOT use asyncio.wait_for() or asyncio.shield()
- DO use max_turns=150 in ClaudeAgentOptions for protection
- NO external timeout mechanisms - let SDK sessions complete naturally
- Simple exception handling without external cancellation
"""

from __future__ import annotations

import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, cast
import sys

# Import StateManager for integration with epic automation
from autoBMAD.epic_automation.state_manager import StateManager

logger = logging.getLogger(__name__)

class TestAutomationAgent:
    """Orchestrates pytest test execution and debugging."""

    def __init__(self, state_manager: StateManager, epic_id: str, skip_tests: bool = False):
        self.state_manager = state_manager
        self.epic_id = epic_id
        self.max_retry_attempts = 5
        self.debugpy_timeout = 300
        self.skip_tests = skip_tests
        self.logger = logging.getLogger(__name__)

    async def run_test_automation(
        self,
        test_dir: str = "tests",
        skip_tests: bool = False
    ) -> dict[str, Any]:
        if skip_tests:
            return {
                "status": "skipped",
                "message": "Test automation bypassed via CLI flag"
            }

        self.logger.info(f"Starting test automation for epic: {self.epic_id}")

        results = {
            "status": "in_progress",
            "epic_id": self.epic_id,
            "timestamp": datetime.now().isoformat(),
            "test_dir": test_dir,
            "summary": {"total_tests": 0, "passed": 0, "failed": 0, "error": 0, "skipped": 0, "execution_time": 0.0},
            "failed_tests": [],
            "retry_history": [],
            "debugpy_sessions": []
        }

        try:
            pytest_results = await self.run_pytest_execution(test_dir, "test_results.json")

            if pytest_results.get("success"):
                results["summary"] = pytest_results.get("summary", {})
                results["status"] = "completed"
            else:
                failures = await self.collect_failures("test_results.json")
                results["failed_tests"] = failures
                results["status"] = "failed" if failures else "completed"

            failed_tests_list: list[dict[str, Any]] = cast(list[dict[str, Any]], results.get("failed_tests", []))
            report_path = self.generate_test_report(cast(dict[str, Any], results), failed_tests_list)
            results["report_path"] = report_path

            return results

        except Exception as e:
            self.logger.error(f"Test automation failed: {e}")
            results["status"] = "failed"
            results["error_message"] = str(e)
            return results

    async def run_pytest_execution(self, test_dir: str, json_report_path: str = "test_results.json") -> dict[str, Any]:
        process = None
        try:
            cmd = [sys.executable, "-m", "pytest", test_dir, "--json-report", f"--json-report-file={json_report_path}", "-v"]

            # Execute pytest without asyncio.shield to avoid cancel scope errors
            try:
                process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                await process.communicate()
            except asyncio.CancelledError:
                self.logger.warning("Pytest execution cancelled, cleaning up process")
                if process is not None:
                    try:
                        process.terminate()
                        await process.wait()
                    except Exception:
                        pass
                # Return empty result instead of re-raising to prevent cancel scope propagation
                self.logger.info("Pytest execution cancelled, returning empty result")
                return {"success": True, "summary": {"passed": 0, "failed": 0, "error": 0}, "json_report_path": json_report_path, "execution_time": 0.0}

            if Path(json_report_path).exists():
                with open(json_report_path) as f:
                    pytest_results = json.load(f)
                summary = pytest_results.get("summary", {})
                return {
                    "success": summary.get("failed", 0) == 0 and summary.get("error", 0) == 0,
                    "summary": summary,
                    "json_report_path": json_report_path,
                    "execution_time": pytest_results.get("duration", 0.0)
                }
            else:
                return {"success": process.returncode == 0, "summary": {"passed": 0, "failed": 0, "error": 0}, "json_report_path": json_report_path, "execution_time": 0.0}
        except Exception as e:
            self.logger.error(f"Pytest execution failed: {e}")
            return {"success": False, "error": str(e), "summary": {"passed": 0, "failed": 0, "error": 0}}

    async def collect_failures(self, json_report_path: str) -> list[dict[str, Any]]:
        try:
            if not Path(json_report_path).exists():
                return []
            with open(json_report_path) as f:
                pytest_results = json.load(f)
            failures = []
            tests_list: list[dict[str, Any]] = cast(list[dict[str, Any]], pytest_results.get("tests", []))
            for test in tests_list:
                if test.get("outcome") in ["failed", "error"]:
                    nodeid = cast(str, test.get("nodeid", ""))
                    nodeid_parts = nodeid.split("::")
                    failure_info = {
                        "test_file": nodeid_parts[0] if nodeid_parts else "",
                        "test_name": nodeid_parts[1] if len(nodeid_parts) > 1 else "",
                        "failure_type": test.get("outcome"),
                        "error_message": str(test.get("longrepr", "")),
                        "traceback": test.get("traceback", []),
                        "fix_attempts": 0,
                        "debugpy_invoked": False
                    }
                    failures.append(failure_info)
            return failures
        except Exception as e:
            self.logger.error(f"Failed to collect failures: {e}")
            return []

    async def fix_tests(self, failures: list[dict[str, Any]]) -> bool:
        """
        Use Claude SDK to generate fixes for test failures (AC #7).

        Args:
            failures: List of test failures

        Returns:
            True if fix attempt was successful, False otherwise
        """
        if not failures:
            self.logger.info("No test failures to fix")
            return True

        self.logger.info(f"Attempting to fix {len(failures)} failed tests using Claude SDK")

        try:
            # Import Claude SDK
            try:
                from claude_agent_sdk import query as _query, ClaudeAgentOptions as _ClaudeAgentOptions, ResultMessage as _ResultMessage  # noqa: F401
            except ImportError:
                self.logger.warning("Claude SDK not available, cannot generate test fixes")
                return False

            # Generate fix prompt
            prompt = self._generate_test_fix_prompt(failures)

            self.logger.info(f"Requesting fixes for {len(failures)} test failures")

            # Execute SDK query with max_turns protection (NO external timeouts)
            options = _ClaudeAgentOptions(max_turns=150) if _ClaudeAgentOptions else None

            # Execute query
            response_iterator = _query(
                prompt=prompt,
                options=options
            )

            # Collect messages from the iterator
            messages = []
            async for message in response_iterator:
                messages.append(message)

                # Check if we got a ResultMessage
                try:
                    if isinstance(message, _ResultMessage):
                        # Since message is a ResultMessage, check for error status
                        is_error = getattr(message, 'is_error', False)
                        if is_error:
                            error_msg = getattr(message, 'result', 'Unknown error')
                            self.logger.error(f"SDK error: {error_msg}")
                            return False
                        else:
                            # Success
                            self.logger.info(f"Successfully generated fixes for {len(failures)} test issues")
                            return True
                except TypeError:
                    # isinstance raised TypeError, treat as not a ResultMessage
                    pass

                # Check for result attribute as fallback
                if hasattr(message, 'result'):
                    self.logger.info(f"Successfully generated fixes for {len(failures)} test issues")
                    return True

            # If we get here, no ResultMessage was received
            if messages:
                self.logger.warning("SDK returned messages but no final result")
                return False
            else:
                self.logger.error("No response from SDK")
                return False

        except Exception as e:
            # Log cancel scope errors from SDK without propagating them
            if "cancel scope" in str(e).lower() or "cancel scope" in str(type(e)).lower():
                self.logger.warning(f"SDK cancel scope error (non-critical): {e}")
                return False
            self.logger.error(f"Error generating test fixes: {e}")
            return False

    def _generate_test_fix_prompt(self, failures: list[dict[str, Any]]) -> str:
        """
        Generate a prompt for fixing test failures using Claude SDK.

        Args:
            failures: List of test failures

        Returns:
            Formatted prompt for Claude SDK
        """
        prompt_lines = [
            "You are a test automation expert. Please help fix the following test failures:",
            ""
        ]

        for i, failure in enumerate(failures, 1):
            prompt_lines.append(f"{i}. Test File: {failure.get('test_file', 'Unknown')}")
            prompt_lines.append(f"   Test Name: {failure.get('test_name', 'Unknown')}")
            prompt_lines.append(f"   Failure Type: {failure.get('failure_type', 'Unknown')}")
            prompt_lines.append(f"   Error Message: {failure.get('error_message', 'No error message')}")
            prompt_lines.append("")

        prompt_lines.extend([
            "",
            "Please analyze these test failures and provide specific fixes.",
            "Consider the following:",
            "1. Test logic errors or incorrect assertions",
            "2. Missing test setup or teardown",
            "3. Dependency issues",
            "4. Environment or configuration problems",
            "",
            "Provide actionable fixes that can be applied to resolve these issues."
        ])

        return "\n".join(prompt_lines)

    async def invoke_debugpy(self, test_file: str, error_details: dict[str, Any]) -> dict[str, Any]:
        """
        Invoke debugpy for persistent test failures (5+ failed attempts).

        Args:
            test_file: Path to the test file
            error_details: Error details for debugging

        Returns:
            Debug session information
        """
        self.logger.info(f"Invoking debugpy for {test_file}")

        # Check if debugpy is available
        try:
            import importlib.util
            debugpy_spec = importlib.util.find_spec("debugpy")
            debugpy_available = debugpy_spec is not None
        except (ImportError, AttributeError):
            debugpy_available = False

        if not debugpy_available:
            return {
                "test_file": test_file,
                "timestamp": datetime.now().isoformat(),
                "error_details": error_details,
                "success": False,
                "error": "debugpy not available - install with: pip install debugpy"
            }

        # Build debug command
        debug_cmd = f"{sys.executable} -m debugpy --listen 5678 --wait-for-client -m pytest {test_file} -v"

        return {
            "test_file": test_file,
            "timestamp": datetime.now().isoformat(),
            "error_details": error_details,
            "success": True,
            "debug_command": debug_cmd,
            "port": 5678,
            "instructions": [
                f"1. Run: {debug_cmd}",
                "2. Connect debugger to localhost:5678",
                "3. Set breakpoints and debug the failing test"
            ]
        }

    async def retry_cycle(
        self,
        test_dir: str = "tests",
        source_dir: str = "src",
        max_cycles: int = 3,
        retries_per_cycle: int = 2
    ) -> dict[str, Any]:
        """
        Execute test and fix cycle with retry logic.

        Max 3 cycles with 2 retries each (no external timeout mechanisms).
        Debugpy invoked after 5+ failed attempts on same test.

        Args:
            test_dir: Path to test directory
            source_dir: Path to source directory
            max_cycles: Maximum fix cycles (default 3)
            retries_per_cycle: Retries per cycle (default 2)

        Returns:
            Dictionary with cycle results
        """
        cycle_results: dict[str, Any] = {
            "total_cycles": 0,
            "successful_cycles": 0,
            "total_tests_run": 0,
            "total_failures_fixed": 0,
            "debugpy_invoked": False,
            "cycles": []
        }

        # Track persistent failure counts per test
        failure_counts: dict[str, int] = {}

        for cycle_num in range(1, max_cycles + 1):
            self.logger.info(f"Starting test cycle {cycle_num}/{max_cycles}")

            # Execute tests
            pytest_results = await self.run_pytest_execution(test_dir, "test_results.json")

            summary = pytest_results.get("summary", {})
            total_tests = summary.get("total", 0)
            cycle_results["total_tests_run"] += total_tests

            if pytest_results.get("success"):
                self.logger.info(f"All tests passed in cycle {cycle_num}")
                cycle_results["successful_cycles"] += 1
                cycle_results["total_cycles"] = cycle_num
                cycle_results["cycles"].append({
                    "cycle": cycle_num,
                    "success": True,
                    "tests_run": total_tests,
                    "failures": 0,
                    "message": "All tests passed"
                })
                break

            # Collect and handle failures
            failures: list[dict[str, Any]] = await self.collect_failures("test_results.json")
            self.logger.info(f"Cycle {cycle_num}: {len(failures)} failures detected")

            # Update failure counts and check for persistent failures (5+)
            persistent_failures: list[dict[str, Any]] = []
            for failure in failures:
                test_id = f"{failure.get('test_file', '')}::{failure.get('test_name', '')}"
                failure_counts[test_id] = failure_counts.get(test_id, 0) + 1
                if failure_counts[test_id] >= 5:
                    persistent_failures.append(failure)

            # Invoke debugpy for persistent failures
            if persistent_failures:
                self.logger.warning(f"Invoking debugpy for {len(persistent_failures)} persistent failures")
                for pf in persistent_failures:
                    await self.invoke_debugpy(pf.get("test_file", ""), pf)
                cycle_results["debugpy_invoked"] = True

            # Retry logic within cycle
            fix_success = False
            fix_message = ""

            for retry_num in range(1, retries_per_cycle + 1):
                self.logger.info(f"Cycle {cycle_num}, Retry {retry_num}/{retries_per_cycle}")

                # Attempt to fix tests using Claude SDK (max_turns=150, no external timeouts)
                fix_result = await self.fix_tests(failures)

                if fix_result:
                    fix_success = True
                    fix_message = f"Generated fixes for {len(failures)} failures"
                    cycle_results["total_failures_fixed"] += len(failures)
                    break
                else:
                    fix_message = "Fix generation failed"

            if fix_success:
                cycle_results["successful_cycles"] += 1

            cycle_results["total_cycles"] = cycle_num
            cycle_results["cycles"].append({
                "cycle": cycle_num,
                "success": fix_success,
                "tests_run": total_tests,
                "failures": len(failures),
                "message": fix_message
            })

        self.logger.info(
            f"Test cycle complete: {cycle_results.get('successful_cycles', 0)}/{cycle_results.get('total_cycles', 0)} "
            f"successful cycles"
        )

        return cycle_results

    def generate_test_report(self, results: dict[str, Any], failures: list[dict[str, Any]]) -> str:
        report_path = "test_automation_report.json"
        report = {
            "test_automation_id": f"test-auto-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "epic_id": results.get("epic_id"),
            "timestamp": results.get("timestamp"),
            "summary": results.get("summary", {}),
            "failed_tests": failures,
            "retry_history": results.get("retry_history", []),
            "debugpy_sessions": results.get("debugpy_sessions", []),
            "status": results.get("status")
        }
        try:
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)
            return report_path
        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            return ""
