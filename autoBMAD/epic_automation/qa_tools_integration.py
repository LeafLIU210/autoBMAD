"""
QA Tools Integration Module

Integrates BasedPyright-Workflow and Fixtest-Workflow into the BMAD automation system.
Provides automated quality assurance checks with quality gate decisions.
"""

import asyncio
import logging
import subprocess
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

logger = logging.getLogger(__name__)


class QAStatus(Enum):
    """QA tool execution status."""
    PASS = "PASS"
    CONCERNS = "CONCERNS"
    FAIL = "FAIL"
    WAIVED = "WAIVED"


class QAError(Exception):
    """QA tool execution error."""
    pass


class BasedPyrightWorkflowRunner:
    """Runner for BasedPyright-Workflow integration."""

    def __init__(self, workflow_dir: str = "basedpyright-workflow", timeout: int = 300):
        """
        Initialize BasedPyright runner.

        Args:
            workflow_dir: Directory containing BasedPyright-Workflow
            timeout: Timeout in seconds for tool execution
        """
        self.workflow_dir = Path(workflow_dir)
        self.timeout = timeout
        self.available = self._check_availability()

    def _check_availability(self) -> bool:
        """Check if BasedPyright-Workflow is available."""
        if not self.workflow_dir.exists():
            logger.warning(f"BasedPyright-Workflow directory not found: {self.workflow_dir}")
            return False

        # Check for required scripts
        required_files = ["fix_basedpyright_errors_new.ps1"]
        for file in required_files:
            if not (self.workflow_dir / file).exists():
                logger.warning(f"BasedPyright-Workflow missing required file: {file}")
                return False

        logger.info("BasedPyright-Workflow is available")
        return True

    async def run_check(self, source_dir: str = "src", max_retries: int = 2) -> Dict[str, Any]:
        """
        Run BasedPyright check.

        Args:
            source_dir: Directory to check
            max_retries: Maximum retry attempts

        Returns:
            Dictionary with check results
        """
        if not self.available:
            return self._create_unavailable_result()

        result: Dict[str, Any] = {
            "status": QAStatus.PASS,
            "tool": "BasedPyright-Workflow",
            "timestamp": datetime.now().isoformat(),
            "source_dir": source_dir,
            "errors": 0,
            "warnings": 0,
            "details": [],
            "auto_fixable": 0,
            "retry_count": 0
        }

        try:
            # Step 1: Run initial check
            logger.info("Running BasedPyright check...")
            stdout, stderr, returncode = await self._run_basedpyright_check(source_dir)
            result["retry_count"] = result["retry_count"] + 1  # type: ignore[operator]

            # Parse results
            errors_found, warnings_found, auto_fixable = self._parse_basedpyright_output(stdout, stderr, returncode)

            result["errors"] = errors_found
            result["warnings"] = warnings_found
            result["auto_fixable"] = auto_fixable

            if errors_found > 0 or warnings_found > 0:
                logger.warning(f"BasedPyright found {errors_found} errors, {warnings_found} warnings")

                # Try auto-fix if configured
                if auto_fixable > 0 and result["retry_count"] < max_retries:
                    logger.info(f"Attempting auto-fix of {auto_fixable} issues...")
                    await self._run_auto_fix()
                    result["retry_count"] = result["retry_count"] + 1  # type: ignore[operator]

                    # Re-check after auto-fix
                    logger.info("Re-running check after auto-fix...")
                    stdout, stderr, returncode = await self._run_basedpyright_check(source_dir)
                    errors_found, warnings_found, _ = self._parse_basedpyright_output(stdout, stderr, returncode)

                    result["errors"] = errors_found
                    result["warnings"] = warnings_found

            # Determine status
            if result["errors"] == 0:
                result["status"] = QAStatus.PASS
            elif result["auto_fixable"] > 0:
                result["status"] = QAStatus.CONCERNS
            else:
                result["status"] = QAStatus.FAIL

            logger.info(f"BasedPyright check complete: {result['status'].value}")

        except subprocess.TimeoutExpired:
            logger.error(f"BasedPyright check timed out after {self.timeout}s")
            result["status"] = QAStatus.FAIL
            result["details"].append(f"Check timed out after {self.timeout} seconds")  # type: ignore[union-attr]
        except Exception as e:
            logger.error(f"BasedPyright check failed: {e}")
            result["status"] = QAStatus.FAIL
            result["details"].append(f"Execution error: {str(e)}")  # type: ignore[union-attr]

        return result

    async def _run_basedpyright_check(self, source_dir: str) -> Tuple[str, str, Optional[int]]:
        """Run BasedPyright check command."""
        # Calculate relative path from basedpyright-workflow directory
        # source_dir is relative to project root, need to convert to relative to workflow dir
        workflow_to_project = Path("..")  # basedpyright-workflow is at project root level
        relative_path = workflow_to_project / source_dir
        cmd = [sys.executable, "-m", "basedpyright_workflow", "check", "--path", str(relative_path)]

        logger.debug(f"Executing: {' '.join(cmd)} in {self.workflow_dir}")

        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=self.workflow_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout
            )
            # Handle encoding errors gracefully
            def safe_decode(data: bytes) -> str:
                try:
                    return data.decode('utf-8')
                except UnicodeDecodeError:
                    # Try latin-1 as fallback (accepts any byte sequence)
                    return data.decode('latin-1')

            stdout_str = safe_decode(stdout)
            stderr_str = safe_decode(stderr)
            return stdout_str, stderr_str, process.returncode
        except asyncio.TimeoutError:
            process.kill()
            raise subprocess.TimeoutExpired(cmd, self.timeout)

    async def _run_auto_fix(self) -> None:
        """Run BasedPyright auto-fix PowerShell script."""
        ps_script = self.workflow_dir / "fix_basedpyright_errors_new.ps1"

        if not ps_script.exists():
            logger.warning(f"Auto-fix script not found: {ps_script}")
            return

        cmd = ["powershell", "-File", str(ps_script)]

        logger.debug(f"Executing: {' '.join(cmd)}")

        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=self.workflow_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            _stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout
            )

            if process.returncode != 0:
                logger.warning(f"Auto-fix completed with warnings: {stderr.decode('utf-8')}")
            else:
                logger.info("Auto-fix completed successfully")

        except asyncio.TimeoutError:
            process.kill()
            logger.warning("Auto-fix timed out")

    def _parse_basedpyright_output(self, stdout: str, stderr: str, returncode: Optional[int]) -> Tuple[int, int, int]:
        """Parse BasedPyright output to extract error counts."""
        errors = 0
        warnings = 0
        auto_fixable = 0

        # Look for error summary in output
        # BasedPyright typically outputs a summary at the end
        lines = stdout.split('\n')
        for line in lines:
            line = line.strip()

            # Count errors and warnings
            if "error" in line.lower() and ":" in line:
                if "0 errors" not in line.lower():
                    # Try to extract number from line
                    try:
                        parts = line.split()
                        for part in parts:
                            if part.isdigit():
                                errors += int(part)
                                break
                    except Exception:
                        errors += 1

            if "warning" in line.lower() and ":" in line:
                if "0 warnings" not in line.lower():
                    try:
                        parts = line.split()
                        for part in parts:
                            if part.isdigit():
                                warnings += int(part)
                                break
                    except Exception:
                        warnings += 1

        # Simple heuristic: assume simple errors are auto-fixable
        auto_fixable = min(errors, 10)  # Cap at 10 for safety

        logger.debug(f"Parsed output: {errors} errors, {warnings} warnings, {auto_fixable} auto-fixable")

        return errors, warnings, auto_fixable

    def _create_unavailable_result(self) -> Dict[str, Any]:
        """Create result for when tool is unavailable."""
        return {
            "status": QAStatus.WAIVED,
            "tool": "BasedPyright-Workflow",
            "timestamp": datetime.now().isoformat(),
            "errors": 0,
            "warnings": 0,
            "details": [f"Tool not available at {self.workflow_dir}"],
            "auto_fixable": 0,
            "retry_count": 0
        }


class FixtestWorkflowRunner:
    """Runner for Fixtest-Workflow integration."""

    def __init__(self, workflow_dir: str = "fixtest-workflow", timeout: int = 120):
        """
        Initialize Fixtest runner.

        Args:
            workflow_dir: Directory containing Fixtest-Workflow
            timeout: Timeout in seconds for tool execution
        """
        self.workflow_dir = Path(workflow_dir)
        self.timeout = timeout
        self.available = self._check_availability()

    def _check_availability(self) -> bool:
        """Check if Fixtest-Workflow is available."""
        if not self.workflow_dir.exists():
            logger.warning(f"Fixtest-Workflow directory not found: {self.workflow_dir}")
            return False

        # Check for required scripts
        required_files = [
            "scan_test_files.py",
            "run_tests.py",
            "fix_tests.ps1"
        ]
        for file in required_files:
            if not (self.workflow_dir / file).exists():
                logger.warning(f"Fixtest-Workflow missing required file: {file}")
                return False

        logger.info("Fixtest-Workflow is available")
        return True

    async def run_check(self, source_dir: str = "tests", max_retries: int = 2) -> Dict[str, Any]:
        """
        Run Fixtest check.

        Args:
            source_dir: Directory containing tests
            max_retries: Maximum retry attempts

        Returns:
            Dictionary with check results
        """
        if not self.available:
            return self._create_unavailable_result()

        result: Dict[str, Any] = {
            "status": QAStatus.PASS,
            "tool": "Fixtest-Workflow",
            "timestamp": datetime.now().isoformat(),
            "source_dir": source_dir,
            "tests_passed": 0,
            "tests_failed": 0,
            "tests_errors": 0,
            "details": [],
            "retry_count": 0
        }

        try:
            # Step 1: Scan test files
            logger.info("Scanning test files...")
            test_files = await self._scan_test_files()
            result["total_tests"] = len(test_files)

            if len(test_files) == 0:
                logger.warning("No test files found")
                result["status"] = QAStatus.CONCERNS
                result["details"].append("No test files found in test directory")  # type: ignore[union-attr]
                return result

            # Step 2: Run tests
            logger.info(f"Running tests from {len(test_files)} files...")
            stdout, stderr, returncode = await self._run_tests()
            result["retry_count"] = result["retry_count"] + 1  # type: ignore[operator]

            # Parse test results
            passed, failed, errors = self._parse_test_output(stdout, stderr, returncode)

            result["tests_passed"] = passed
            result["tests_failed"] = failed
            result["tests_errors"] = errors

            # Determine status
            if passed > 0 and failed == 0 and errors == 0:
                result["status"] = QAStatus.PASS
            elif failed > 0 or errors > 0:
                result["status"] = QAStatus.CONCERNS
            else:
                result["status"] = QAStatus.FAIL

            logger.info(f"Fixtest check complete: {result['status'].value}")
            logger.info(f"Tests: {passed} passed, {failed} failed, {errors} errors")

        except subprocess.TimeoutExpired:
            logger.error(f"Fixtest check timed out after {self.timeout}s")
            result["status"] = QAStatus.FAIL
            result["details"].append(f"Check timed out after {self.timeout} seconds")  # type: ignore[union-attr]
        except Exception as e:
            logger.error(f"Fixtest check failed: {e}")
            result["status"] = QAStatus.FAIL
            result["details"].append(f"Execution error: {str(e)}")  # type: ignore[union-attr]

        return result

    async def _scan_test_files(self) -> List[str]:
        """Scan for test files."""
        cmd = [sys.executable, "scan_test_files.py"]

        logger.debug(f"Executing: {' '.join(cmd)} in {self.workflow_dir}")

        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=self.workflow_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=120  # 2 minute timeout for scanning
            )

            if process.returncode != 0:
                logger.warning(f"Test scan completed with warnings: {stderr.decode('utf-8')}")

            # Parse scan output to get test file count
            output = stdout.decode('utf-8')
            test_files: List[str] = []

            # Look for JSON output or file list
            for line in output.split('\n'):
                if 'test' in line.lower() and '.py' in line:
                    test_files.append(line.strip())

            return test_files

        except asyncio.TimeoutError:
            process.kill()
            logger.warning("Test scan timed out")
            return []

    async def _run_tests(self) -> Tuple[str, str, Optional[int]]:
        """Run pytest tests."""
        cmd = [sys.executable, "run_tests.py"]

        logger.debug(f"Executing: {' '.join(cmd)} in {self.workflow_dir}")

        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=self.workflow_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout
            )
            # Handle encoding errors gracefully
            def safe_decode(data: bytes) -> str:
                try:
                    return data.decode('utf-8')
                except UnicodeDecodeError:
                    # Try latin-1 as fallback (accepts any byte sequence)
                    return data.decode('latin-1')

            stdout_str = safe_decode(stdout)
            stderr_str = safe_decode(stderr)
            return stdout_str, stderr_str, process.returncode
        except asyncio.TimeoutError:
            process.kill()
            raise subprocess.TimeoutExpired(cmd, self.timeout)

    def _parse_test_output(self, stdout: str, stderr: str, returncode: Optional[int]) -> Tuple[int, int, int]:
        """Parse test output to extract test counts."""
        passed = 0
        failed = 0
        errors = 0

        # Look for test summary in output
        lines = stdout.split('\n') + stderr.split('\n')

        for line in lines:
            line = line.strip()

            # Parse pytest summary format
            # Example: "5 passed, 2 failed, 1 error in 10.50s"
            if "passed" in line.lower() and ("failed" in line.lower() or "error" in line.lower()):
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.isdigit():
                        count = int(part)
                        if i > 0 and "passed" in parts[i-1].lower():
                            passed = count
                        elif i > 0 and "failed" in parts[i-1].lower():
                            failed = count
                        elif i > 0 and "error" in parts[i-1].lower():
                            errors = count

        logger.debug(f"Parsed test output: {passed} passed, {failed} failed, {errors} errors")

        return passed, failed, errors

    def _create_unavailable_result(self) -> Dict[str, Any]:
        """Create result for when tool is unavailable."""
        return {
            "status": QAStatus.WAIVED,
            "tool": "Fixtest-Workflow",
            "timestamp": datetime.now().isoformat(),
            "tests_passed": 0,
            "tests_failed": 0,
            "tests_errors": 0,
            "details": [f"Tool not available at {self.workflow_dir}"],
            "retry_count": 0
        }


class QAAutomationWorkflow:
    """Main QA automation workflow orchestrator."""

    def __init__(self,
                 basedpyright_dir: str = "basedpyright-workflow",
                 fixtest_dir: str = "fixtest-workflow",
                 timeout: int = 120,
                 max_retries: int = 2):
        """
        Initialize QA workflow.

        Args:
            basedpyright_dir: BasedPyright-Workflow directory
            fixtest_dir: Fixtest-Workflow directory
            timeout: Default timeout for tool execution
            max_retries: Default max retry attempts
        """
        self.basedpyright_runner = BasedPyrightWorkflowRunner(basedpyright_dir, timeout)
        self.fixtest_runner = FixtestWorkflowRunner(fixtest_dir, timeout)
        self.max_retries = max_retries
        logger.info("QA Automation Workflow initialized")

    async def run_qa_checks(self,
                           source_dir: str = "src",
                           test_dir: str = "tests") -> Dict[str, Any]:
        """
        Run complete QA checks using both tools.

        Args:
            source_dir: Source code directory for BasedPyright
            test_dir: Test directory for Fixtest

        Returns:
            Dictionary with comprehensive QA results
        """
        logger.info("Starting QA checks with Both Tools")

        # Track all tasks to prevent task leaks
        tasks: List[asyncio.Task[Dict[str, Any]]] = []

        # Run both checks in parallel
        basedpyright_task = asyncio.create_task(
            self.basedpyright_runner.run_check(source_dir, self.max_retries)
        )
        tasks.append(basedpyright_task)

        fixtest_task = asyncio.create_task(
            self.fixtest_runner.run_check(test_dir, self.max_retries)
        )
        tasks.append(fixtest_task)

        basedpyright_result, fixtest_result = await asyncio.gather(
            basedpyright_task,
            fixtest_task
        )

        # Ensure all tasks are completed
        for task in tasks:
            if not task.done():
                await task

        # Determine overall status
        overall_status = self._determine_overall_status(basedpyright_result, fixtest_result)

        # Compile comprehensive results
        results = {
            "timestamp": datetime.now().isoformat(),
            "basedpyright": basedpyright_result,
            "fixtest": fixtest_result,
            "overall_status": overall_status.value,
            "summary": self._generate_summary(basedpyright_result, fixtest_result, overall_status)
        }

        logger.info(f"QA checks complete: Overall status = {overall_status.value}")

        return results

    def _determine_overall_status(self,
                                  bp_result: Dict[str, Any],
                                  ft_result: Dict[str, Any]) -> QAStatus:
        """
        Determine overall QA status from individual tool results.

        Args:
            bp_result: BasedPyright result
            ft_result: Fixtest result

        Returns:
            Overall QA status
        """
        bp_status = QAStatus(bp_result["status"])
        ft_status = QAStatus(ft_result["status"])

        # If either tool has WAIVED status, propagate it
        if bp_status == QAStatus.WAIVED or ft_status == QAStatus.WAIVED:
            return QAStatus.WAIVED

        # If both tools PASS, overall is PASS
        if bp_status == QAStatus.PASS and ft_status == QAStatus.PASS:
            return QAStatus.PASS

        # If either tool FAIL, overall is FAIL
        if bp_status == QAStatus.FAIL or ft_status == QAStatus.FAIL:
            return QAStatus.FAIL

        # Otherwise, overall is CONCERNS
        return QAStatus.CONCERNS

    def _generate_summary(self,
                         bp_result: Dict[str, Any],
                         ft_result: Dict[str, Any],
                         overall_status: QAStatus) -> Dict[str, Any]:
        """Generate human-readable summary of QA results."""
        summary: Dict[str, Any] = {
            "overall_status": overall_status.value,
            "tools_status": {
                "BasedPyright": bp_result["status"],
                "Fixtest": ft_result["status"]
            },
            "metrics": {
                "basedpyright_errors": bp_result.get("errors", 0),
                "basedpyright_warnings": bp_result.get("warnings", 0),
                "fixtest_passed": ft_result.get("tests_passed", 0),
                "fixtest_failed": ft_result.get("tests_failed", 0),
                "fixtest_errors": ft_result.get("tests_errors", 0)
            },
            "recommendations": []
        }

        # Add recommendations based on results
        if bp_result.get("errors", 0) > 0:
            summary["recommendations"].append(  # type: ignore[union-attr]
                f"Fix {bp_result['errors']} BasedPyright errors before proceeding"
            )

        if ft_result.get("tests_failed", 0) > 0:
            summary["recommendations"].append(  # type: ignore[union-attr]
                f"Address {ft_result['tests_failed']} failed tests"
            )

        if ft_result.get("tests_errors", 0) > 0:
            summary["recommendations"].append(  # type: ignore[union-attr]
                f"Resolve {ft_result['tests_errors']} test execution errors"
            )

        if overall_status == QAStatus.PASS:
            summary["recommendations"].append("All QA checks passed - ready for production")  # type: ignore[union-attr]

        return summary
