"""
Test Automation Agent - Integrates pytest test execution with debugpy for persistent failure diagnosis.

Orchestrates test automation after code quality validation without external workflow dependencies.
"""

import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import sys

from autoBMAD.epic_automation.state_manager import StateManager

# Import for testing/mocking
try:
    from fixtest_workflow.test_automation_workflow import run_pytest_execution
    from fixtest_workflow.debugpy_integration import (
        start_debugpy_listener,
        attach_debugpy,
        collect_debug_info
    )
except ImportError:
    # For testing purposes
    run_pytest_execution = None
    start_debugpy_listener = None
    attach_debugpy = None
    collect_debug_info = None

# Import for Claude SDK
try:
    from claude_agent_sdk import Claude
except ImportError:
    Claude = None


class TestAutomationAgent:
    """Orchestrates pytest test execution and debugging."""

    def __init__(
        self,
        state_manager: StateManager,
        epic_id: str,
        skip_tests: bool = False
    ):
        """
        Initialize with state manager and epic tracking.

        Args:
            state_manager: StateManager instance for progress tracking
            epic_id: Epic identifier for tracking
            skip_tests: Skip test automation (default: False)
        """
        self.state_manager = state_manager
        self.epic_id = epic_id
        self.max_retry_attempts = 5
        self.debugpy_timeout = 300  # 5 minutes
        self.skip_tests = skip_tests
        self.logger = logging.getLogger(__name__)

    async def run_test_automation(
        self,
        test_dir: str = "tests",
        skip_tests: bool = False
    ) -> Dict[str, Any]:
        """
        Execute complete test automation workflow.

        Args:
            test_dir: Directory containing tests to execute
            skip_tests: If True, bypass test automation

        Returns:
            Dict with test automation results and status
        """
        if skip_tests or self.skip_tests:
            self.logger.info("Skipping test automation due to --skip-tests flag")
            return {
                "status": "skipped",
                "message": "Test automation bypassed via CLI flag"
            }

        self.logger.info(f"Starting test automation for epic: {self.epic_id}")
        self.logger.info(f"Test directory: {test_dir}")

        results = {
            "status": "in_progress",
            "epic_id": self.epic_id,
            "test_dir": test_dir,
            "pytest": {},
            "iterations": 0,
            "retry_attempts": 0,
            "debugpy_sessions": [],
            "errors": []
        }

        # Validate test directory
        test_path = Path(test_dir)
        if not test_path.exists():
            error_msg = f"Test directory not found: {test_dir}"
            self.logger.error(error_msg)
            results["status"] = "failed"
            results["errors"].append(error_msg)
            return results

        # Find all test files
        test_files = list(test_path.rglob("test_*.py")) + list(test_path.rglob("*_test.py"))
        results["test_file_count"] = len(test_files)

        if len(test_files) == 0:
            self.logger.warning(f"No test files found in {test_dir}")
            results["status"] = "completed"
            results["message"] = "No test files to execute"
            results["summary"] = {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "error": 0,
                "skipped": 0
            }
            return results

        self.logger.info(f"Found {len(test_files)} test files")

        # Run initial pytest execution
        results = await self._run_initial_tests(test_dir, results)

        # If tests pass, we're done
        if results["pytest"].get("summary", {}).get("failed", 0) == 0:
            self.logger.info("All tests passed on first attempt")
            results["status"] = "completed"
            return results

        # Retry loop for failed tests
        results = await self._retry_failed_tests(test_dir, results)

        # Generate final report
        report_path = self.generate_test_report(
            results,
            results.get("failed_tests", [])
        )
        results["report_path"] = report_path

        self.logger.info(f"Test automation completed. Report: {report_path}")
        return results

    async def _run_initial_tests(
        self,
        test_dir: str,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run initial pytest execution."""
        try:
            self.logger.info("Running initial pytest execution")
            json_report_path = "test_results.json"

            pytest_result = await self.run_pytest_execution(
                test_dir=test_dir,
                json_report_path=json_report_path
            )

            results["pytest"] = pytest_result

            # Collect failures
            failures = await self.collect_failures(json_report_path)
            results["failed_tests"] = failures

            # Add test phase records for each failed test file
            for failure in failures:
                test_file = failure.get("test_file", "")
                if test_file:
                    await self.state_manager.add_test_phase_record(
                        epic_id=self.epic_id,
                        test_file_path=test_file,
                        failure_count=1,
                        debug_info=json.dumps(failure)
                    )

            self.logger.info(
                f"Initial test run: {pytest_result.get('summary', {})}"
            )

        except Exception as e:
            self.logger.error(f"Failed to run initial tests: {e}")
            results["status"] = "failed"
            results["errors"].append(str(e))

        return results

    async def _retry_failed_tests(
        self,
        test_dir: str,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Retry failed tests with automated fixes."""
        max_attempts = self.max_retry_attempts
        results.setdefault("retry_history", [])

        for attempt in range(1, max_attempts + 1):
            self.logger.info(f"Retry attempt {attempt}/{max_attempts}")

            failures = results.get("failed_tests", [])
            if not failures:
                self.logger.info("No more failures to fix")
                break

            # Try to fix tests with Claude agents
            fix_success = await self.fix_tests(failures)

            # Track retry history
            retry_entry = {
                "attempt": attempt,
                "timestamp": datetime.now().isoformat(),
                "failures_count": len(failures),
                "fixes_applied": len(failures) if fix_success else 0,
                "fixes_successful": len(failures) if fix_success else 0,
                "fix_success": fix_success
            }

            if fix_success:
                # Re-run tests
                results["iterations"] += 1
                results["retry_attempts"] = attempt

                json_report_path = f"test_results_attempt_{attempt}.json"
                pytest_result = await self.run_pytest_execution(
                    test_dir=test_dir,
                    json_report_path=json_report_path
                )

                # Collect new failures
                new_failures = await self.collect_failures(json_report_path)
                results["pytest"] = pytest_result
                results["failed_tests"] = new_failures

                # Update retry entry with test results
                retry_entry["tests_passed"] = pytest_result.get("summary", {}).get("passed", 0)
                retry_entry["tests_failed"] = pytest_result.get("summary", {}).get("failed", 0)
                retry_entry["tests_error"] = pytest_result.get("summary", {}).get("error", 0)

                # Check if all tests pass now
                if pytest_result.get("summary", {}).get("failed", 0) == 0:
                    self.logger.info(f"All tests passed after {attempt} retry attempts")
                    results["status"] = "completed"
                    results["retry_history"].append(retry_entry)
                    break

                # If still failing and this is the 5th attempt, use debugpy
                if attempt == max_attempts:
                    self.logger.info("Max retry attempts reached, invoking debugpy")
                    results = await self._invoke_debugpy_for_persistent_failures(
                        test_dir,
                        results
                    )
                    results["status"] = "completed_with_debugpy"
            else:
                self.logger.warning("Fix attempt failed")
                retry_entry["fixes_successful"] = 0
                if attempt == max_attempts:
                    results = await self._invoke_debugpy_for_persistent_failures(
                        test_dir,
                        results
                    )
                    results["status"] = "completed_with_debugpy"

            results["retry_history"].append(retry_entry)

        return results

    async def _invoke_debugpy_for_persistent_failures(
        self,
        test_dir: str,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Invoke debugpy for persistent test failures."""
        try:
            self.logger.info("Starting debugpy for persistent failures")

            # Start debugpy listener
            await start_debugpy_listener(port=5678)

            # Attach debugpy
            attach_success = await attach_debugpy(timeout=self.debugpy_timeout)

            if attach_success:
                # Collect debug info for each failed test
                failures = results.get("failed_tests", [])
                for failure in failures:
                    test_file = failure.get("test_file", "")
                    if test_file:
                        debug_info = collect_debug_info(test_file, failure)

                        # Update state manager
                        await self.state_manager.add_test_phase_record(
                            epic_id=self.epic_id,
                            test_file_path=test_file,
                            failure_count=1,
                            debug_info=json.dumps(debug_info),
                            fix_status="debugpy_invoked"
                        )

                        results["debugpy_sessions"].append({
                            "test_file": test_file,
                            "debug_info": debug_info
                        })

                self.logger.info(f"Debugpy invoked for {len(failures)} test files")
            else:
                self.logger.error("Failed to attach debugpy")
                results["errors"].append("Debugpy attach failed")

        except Exception as e:
            self.logger.error(f"Debugpy invocation failed: {e}")
            results["errors"].append(str(e))

        return results

    async def run_pytest_execution(
        self,
        test_dir: str,
        json_report_path: str = "test_results.json"
    ) -> Dict[str, Any]:
        """Execute pytest with JSON report generation."""
        if run_pytest_execution is None:
            # Fallback to direct pytest execution
            try:
                cmd = [sys.executable, "-m", "pytest", test_dir, "--json-report", f"--json-report-file={json_report_path}", "-v"]
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()

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
                    return {
                        "success": process.returncode == 0,
                        "summary": {"passed": 0, "failed": 0, "error": 0},
                        "json_report_path": json_report_path,
                        "execution_time": 0.0
                    }
            except Exception as e:
                self.logger.error(f"Pytest execution failed: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "summary": {"passed": 0, "failed": 0, "error": 0}
                }

        return await run_pytest_execution(
            test_dir=test_dir,
            json_report_file=json_report_path
        )

    async def collect_failures(
        self,
        json_report_path: str
    ) -> List[Dict[str, Any]]:
        """Collect failed/errored tests from JSON report."""
        try:
            if not Path(json_report_path).exists():
                return []

            with open(json_report_path) as f:
                report = json.load(f)

            failures = []
            tests = report.get("tests", [])

            for test in tests:
                outcome = test.get("outcome", "")
                if outcome in ["failed", "error"]:
                    failures.append({
                        "test_file": test.get("nodeid", "").split("::")[0],
                        "test_name": test.get("nodeid", "").split("::")[1] if "::" in test.get("nodeid", "") else "",
                        "failure_type": outcome,
                        "error_message": str(test.get("longrepr", "")),
                        "traceback": test.get("traceback", []),
                        "duration": test.get("duration", 0),
                        "fix_attempts": 0,
                        "debugpy_invoked": False
                    })

            return failures

        except Exception as e:
            self.logger.error(f"Failed to collect failures: {e}")
            return []

    async def fix_tests(self, failures: List[Dict[str, Any]]) -> bool:
        """Invoke Claude agents to fix test issues."""
        try:
            self.logger.info(f"Attempting to fix {len(failures)} test failures")

            if not failures:
                self.logger.info("No failures to fix")
                return True

            # Import Claude SDK
            try:
                from claude_agent_sdk import Claude
            except ImportError:
                self.logger.error("claude_agent_sdk not installed")
                return False

            # Get API key from environment
            api_key = None
            import os
            for env_var in ["ANTHROPIC_API_KEY", "CLAUDE_API_KEY"]:
                api_key = os.environ.get(env_var)
                if api_key:
                    break

            if not api_key:
                self.logger.error("No API key found for Claude")
                return False

            # Initialize Claude client
            claude = Claude(api_key=api_key)

            # Read prompt template
            prompt_path = Path(__file__).parent.parent.parent / "fixtest_workflow" / "prompts" / "prompt-test-fix.md"
            if not prompt_path.exists():
                self.logger.error(f"Prompt template not found at {prompt_path}")
                return False

            prompt_template = prompt_path.read_text()

            # Format failures for the prompt
            failed_tests_info = []
            for failure in failures:
                failed_tests_info.append(f"""
Test: {failure.get('test_name', 'Unknown')}
File: {failure.get('test_file', 'Unknown')}
Error Type: {failure.get('failure_type', 'Unknown')}
Error Message: {failure.get('error_message', 'No message')}
Traceback: {failure.get('traceback', 'No traceback')}
""")

            failed_tests_text = "\n".join(failed_tests_info)

            # Create the prompt with failure information
            prompt = prompt_template.replace("{{FAILED_TESTS}}", failed_tests_text)

            self.logger.info("Sending test failures to Claude for analysis and fixing...")

            # Send to Claude
            response = await claude(prompt)

            if not response or not response.content:
                self.logger.error("No response from Claude")
                return False

            # Parse response for file changes
            response_text = response.content[0].text if isinstance(response.content, list) else str(response.content)

            self.logger.info("Claude response received, applying fixes...")

            # Apply fixes (simple implementation - look for file change blocks)
            fixed_count = 0
            lines = response_text.split('\n')
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line.startswith("# File:"):
                    # Extract file path
                    file_path = line.replace("# File:", "").strip()
                    i += 1

                    # Skip to "Fixed code:"
                    while i < len(lines) and "Fixed code:" not in lines[i]:
                        i += 1

                    if i >= len(lines):
                        break

                    i += 1  # Skip "Fixed code:" line

                    # Collect fixed code
                    fixed_code_lines = []
                    while i < len(lines) and not lines[i].strip().startswith("```"):
                        fixed_code_lines.append(lines[i])
                        i += 1

                    # Write fixed code to file
                    try:
                        if os.path.exists(file_path):
                            Path(file_path).write_text('\n'.join(fixed_code_lines))
                            self.logger.info(f"Applied fix to {file_path}")
                            fixed_count += 1
                    except Exception as e:
                        self.logger.error(f"Failed to write fix to {file_path}: {e}")
                else:
                    i += 1

            if fixed_count > 0:
                self.logger.info(f"Successfully applied {fixed_count} fixes")
                return True
            else:
                self.logger.warning("No fixes were applied")
                return False

        except Exception as e:
            self.logger.error(f"Failed to fix tests: {e}")
            return False

    async def invoke_debugpy(
        self,
        test_file: str,
        error_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Invoke debugpy for persistent test failures."""
        try:
            self.logger.info(f"Invoking debugpy for {test_file}")

            debug_info = collect_debug_info(test_file, error_details)

            await self.state_manager.add_test_phase_record(
                epic_id=self.epic_id,
                test_file_path=test_file,
                failure_count=1,
                debug_info=json.dumps(debug_info),
                fix_status="debugpy_invoked"
            )

            return debug_info

        except Exception as e:
            self.logger.error(f"Debugpy invocation failed: {e}")
            return {}

    def generate_test_report(
        self,
        results: Dict[str, Any],
        failures: List[Dict[str, Any]]
    ) -> str:
        """Generate JSON test automation report."""
        report = {
            "test_automation_id": f"test-auto-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "epic_id": self.epic_id,
            "timestamp": datetime.now().isoformat(),
            "summary": results.get("pytest", {}).get("summary", {}),
            "failed_tests": failures,
            "retry_history": results.get("retry_history", []),
            "debugpy_sessions": results.get("debugpy_sessions", []),
            "status": results.get("status", "unknown"),
            "iterations": results.get("iterations", 0),
            "errors": results.get("errors", [])
        }

        report_path = "test_automation_report.json"
        try:
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)
            self.logger.info(f"Generated test automation report: {report_path}")
            return report_path
        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            return ""
