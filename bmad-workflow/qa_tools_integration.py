#!/usr/bin/env python3
"""
QA Tools Integration Module

This module provides automated integration with BasedPyright-Workflow and Fixtest-Workflow
as part of the BMAD QA automation process.

Features:
- BasedPyright-Workflow integration via subprocess calls
- Fixtest-Workflow integration via subprocess calls
- Automatic QA trigger after Dev phase
- Retry mechanism for QA failures
- Output parsing for pass/fail decisions
- State management integration with progress.db
"""

import subprocess
import json
import re
import sys
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import sqlite3
from dataclasses import dataclass, asdict
from enum import Enum


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QAStatus(Enum):
    """QA execution status enumeration"""
    PASS = "PASS"
    CONCERNS = "CONCERNS"
    FAIL = "FAIL"
    WAIVED = "WAIVED"


@dataclass
class BasedPyrightResult:
    """Result object for BasedPyright-Workflow execution"""
    success: bool
    exit_code: int
    output: str
    error_count: int
    warning_count: int
    type_errors: List[str]
    style_violations: List[str]
    import_issues: List[str]
    undefined_variables: List[str]
    report_path: Optional[str] = None


@dataclass
class FixtestResult:
    """Result object for Fixtest-Workflow execution"""
    success: bool
    exit_code: int
    output: str
    tests_passed: int
    tests_failed: int
    tests_skipped: int
    coverage_percentage: float
    failing_test_cases: List[str]
    auto_fixed_tests: List[str]
    summary_path: Optional[str] = None


@dataclass
class QAResult:
    """Comprehensive QA result aggregating all tools"""
    overall_status: QAStatus
    basedpyright_result: Optional[BasedPyrightResult]
    fixtest_result: Optional[FixtestResult]
    timestamp: str
    retry_count: int
    errors: List[str]
    warnings: List[str]


class BasedPyrightIntegrator:
    """Handles BasedPyright-Workflow integration"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.workflow_dir = self.project_root / "basedpyright-workflow"

    def run_basedpyright_check(self, max_retries: int = 3) -> BasedPyrightResult:
        """
        Execute BasedPyright-Workflow check via subprocess

        Args:
            max_retries: Maximum number of retry attempts

        Returns:
            BasedPyrightResult object with execution details
        """
        logger.info("Starting BasedPyright-Workflow check")

        last_error = None
        for attempt in range(max_retries):
            try:
                logger.info(f"BasedPyright check attempt {attempt + 1}/{max_retries}")

                # Change to workflow directory and execute command
                cmd = [sys.executable, "-m", "basedpyright_workflow", "check"]

                result = subprocess.run(
                    cmd,
                    cwd=self.workflow_dir,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )

                output = result.stdout + "\n" + result.stderr

                # Parse output for results
                parsed_result = self._parse_basedpyright_output(output, result.returncode)

                if parsed_result.success or attempt == max_retries - 1:
                    logger.info(f"BasedPyright check completed with exit code: {result.returncode}")
                    return parsed_result

                last_error = output
                logger.warning(f"BasedPyright check failed, retrying... (attempt {attempt + 1})")
                logger.warning(f"Error output: {output[:500]}...")

            except subprocess.TimeoutExpired as e:
                last_error = f"Timeout: {str(e)}"
                logger.error(f"BasedPyright check timed out on attempt {attempt + 1}")
            except Exception as e:
                last_error = str(e)
                logger.error(f"BasedPyright check failed on attempt {attempt + 1}: {e}")

        # If all retries failed, return failure result
        logger.error("BasedPyright check failed after all retries")
        return BasedPyrightResult(
            success=False,
            exit_code=-1,
            output=last_error or "Unknown error",
            error_count=0,
            warning_count=0,
            type_errors=[],
            style_violations=[],
            import_issues=[],
            undefined_variables=[]
        )

    def _parse_basedpyright_output(self, output: str, exit_code: int) -> BasedPyrightResult:
        """
        Parse BasedPyright output to extract metrics and violations

        Args:
            output: Raw output from BasedPyright execution
            exit_code: Process exit code

        Returns:
            Parsed BasedPyrightResult
        """
        # Count errors and warnings
        error_pattern = re.compile(r"error\d*:", re.IGNORECASE)
        warning_pattern = re.compile(r"warning\d*:", re.IGNORECASE)

        errors = error_pattern.findall(output)
        warnings = warning_pattern.findall(output)

        # Extract specific issue types
        type_errors = re.findall(r"(?:error|Error).*?(?=\n|$)", output, re.MULTILINE)
        style_violations = re.findall(r"(?:style|Style).*?(?=\n|$)", output, re.MULTILINE)
        import_issues = re.findall(r"(?:import|Import).*?(?=\n|$)", output, re.MULTILINE)
        undefined_vars = re.findall(r"(?:undefined|Unresolved).*?(?=\n|$)", output, re.MULTILINE)

        # Determine success based on exit code and errors
        success = exit_code == 0 or len(errors) == 0

        # Find report path if it exists
        report_path = None
        report_match = re.search(r"Report saved to:\s*(.+)", output)
        if report_match:
            report_path = report_match.group(1).strip()

        return BasedPyrightResult(
            success=success,
            exit_code=exit_code,
            output=output,
            error_count=len(errors),
            warning_count=len(warnings),
            type_errors=type_errors[:50],  # Limit to first 50
            style_violations=style_violations[:50],
            import_issues=import_issues[:50],
            undefined_variables=undefined_vars[:50],
            report_path=report_path
        )


class FixtestIntegrator:
    """Handles Fixtest-Workflow integration"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.workflow_dir = self.project_root / "fixtest-workflow"

    def run_fixtest_check(self, max_retries: int = 3) -> FixtestResult:
        """
        Execute Fixtest-Workflow check via subprocess

        Args:
            max_retries: Maximum number of retry attempts

        Returns:
            FixtestResult object with execution details
        """
        logger.info("Starting Fixtest-Workflow check")

        last_error = None
        for attempt in range(max_retries):
            try:
                logger.info(f"Fixtest check attempt {attempt + 1}/{max_retries}")

                # First run scan_test_files.py
                scan_cmd = [sys.executable, "scan_test_files.py"]
                scan_result = subprocess.run(
                    scan_cmd,
                    cwd=self.workflow_dir,
                    capture_output=True,
                    text=True,
                    timeout=120  # 2 minute timeout
                )

                # Then run run_tests.py
                test_cmd = [sys.executable, "run_tests.py"]
                test_result = subprocess.run(
                    test_cmd,
                    cwd=self.workflow_dir,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )

                output = scan_result.stdout + "\n" + scan_result.stderr + "\n" + test_result.stdout + "\n" + test_result.stderr
                exit_code = test_result.returncode

                # Parse output for results
                parsed_result = self._parse_fixtest_output(output, exit_code)

                if parsed_result.success or attempt == max_retries - 1:
                    logger.info(f"Fixtest check completed with exit code: {exit_code}")
                    return parsed_result

                last_error = output
                logger.warning(f"Fixtest check failed, retrying... (attempt {attempt + 1})")
                logger.warning(f"Error output: {output[:500]}...")

            except subprocess.TimeoutExpired as e:
                last_error = f"Timeout: {str(e)}"
                logger.error(f"Fixtest check timed out on attempt {attempt + 1}")
            except Exception as e:
                last_error = str(e)
                logger.error(f"Fixtest check failed on attempt {attempt + 1}: {e}")

        # If all retries failed, return failure result
        logger.error("Fixtest check failed after all retries")
        return FixtestResult(
            success=False,
            exit_code=-1,
            output=last_error or "Unknown error",
            tests_passed=0,
            tests_failed=0,
            tests_skipped=0,
            coverage_percentage=0.0,
            failing_test_cases=[],
            auto_fixed_tests=[]
        )

    def _parse_fixtest_output(self, output: str, exit_code: int) -> FixtestResult:
        """
        Parse Fixtest output to extract test results

        Args:
            output: Raw output from Fixtest execution
            exit_code: Process exit code

        Returns:
            Parsed FixtestResult
        """
        # Extract test counts
        passed_match = re.search(r"(\d+)\s+passed", output, re.IGNORECASE)
        failed_match = re.search(r"(\d+)\s+failed", output, re.IGNORECASE)
        skipped_match = re.search(r"(\d+)\s+skipped", output, re.IGNORECASE)
        coverage_match = re.search(r"(\d+\.?\d*)%\s*coverage", output, re.IGNORECASE)

        tests_passed = int(passed_match.group(1)) if passed_match else 0
        tests_failed = int(failed_match.group(1)) if failed_match else 0
        tests_skipped = int(skipped_match.group(1)) if skipped_match else 0
        coverage_percentage = float(coverage_match.group(1)) if coverage_match else 0.0

        # Extract failing test cases
        failing_tests = re.findall(r"FAILED\s+([\w\.]+::[\w\.]+)", output)
        auto_fixed = re.findall(r"(?:auto-?fixed|fixed)\s+([\w\.]+)", output, re.IGNORECASE)

        # Determine success based on exit code and failures
        success = exit_code == 0 or tests_failed == 0

        # Find summary path if it exists
        summary_path = None
        summary_match = re.search(r"Summary saved to:\s*(.+)", output)
        if summary_match:
            summary_path = summary_match.group(1).strip()

        return FixtestResult(
            success=success,
            exit_code=exit_code,
            output=output,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            tests_skipped=tests_skipped,
            coverage_percentage=coverage_percentage,
            failing_test_cases=failing_tests[:50],  # Limit to first 50
            auto_fixed_tests=auto_fixed[:50],
            summary_path=summary_path
        )


class QAWorkflowAutomation:
    """Main QA automation workflow orchestrator"""

    def __init__(self, project_root: str, progress_db_path: str):
        self.project_root = Path(project_root)
        self.progress_db_path = progress_db_path
        self.basedpyright = BasedPyrightIntegrator(str(self.project_root))
        self.fixtest = FixtestIntegrator(str(self.project_root))

    def run_qa_checks(self, story_path: str, max_retries: int = 3) -> QAResult:
        """
        Run comprehensive QA checks for a story

        Args:
            story_path: Path to the story file
            max_retries: Maximum retry attempts for each tool

        Returns:
            QAResult with aggregated results from all tools
        """
        logger.info(f"Starting QA checks for story: {story_path}")

        errors = []
        warnings = []
        basedpyright_result = None
        fixtest_result = None
        retry_count = 0

        try:
            # Run BasedPyright-Workflow
            logger.info("Running BasedPyright-Workflow check...")
            basedpyright_result = self.basedpyright.run_basedpyright_check(max_retries)

            if not basedpyright_result.success:
                errors.append(f"BasedPyright check failed with {basedpyright_result.error_count} errors")
                warnings.extend(basedpyright_result.type_errors[:5])  # Add first 5 errors as warnings

            # Run Fixtest-Workflow
            logger.info("Running Fixtest-Workflow check...")
            fixtest_result = self.fixtest.run_fixtest_check(max_retries)

            if not fixtest_result.success:
                errors.append(f"Fixtest check failed with {fixtest_result.tests_failed} test failures")
                if fixtest_result.failing_test_cases:
                    warnings.extend(fixtest_result.failing_test_cases[:5])  # Add first 5 failures

            # Determine overall status
            overall_status = self._determine_overall_status(basedpyright_result, fixtest_result, errors)

            # Create result object
            qa_result = QAResult(
                overall_status=overall_status,
                basedpyright_result=basedpyright_result,
                fixtest_result=fixtest_result,
                timestamp=datetime.now().isoformat(),
                retry_count=retry_count,
                errors=errors,
                warnings=warnings
            )

            # Update state in progress.db
            self._update_progress_db(story_path, qa_result)

            logger.info(f"QA checks completed with status: {overall_status.value}")
            return qa_result

        except Exception as e:
            logger.error(f"QA workflow failed with exception: {e}", exc_info=True)
            error_msg = f"QA workflow exception: {str(e)}"
            errors.append(error_msg)

            return QAResult(
                overall_status=QAStatus.FAIL,
                basedpyright_result=basedpyright_result,
                fixtest_result=fixtest_result,
                timestamp=datetime.now().isoformat(),
                retry_count=retry_count,
                errors=errors,
                warnings=warnings
            )

    def _determine_overall_status(
        self,
        basedpyright_result: Optional[BasedPyrightResult],
        fixtest_result: Optional[FixtestResult],
        errors: List[str]
    ) -> QAStatus:
        """
        Determine overall QA status based on all tool results

        Args:
            basedpyright_result: BasedPyright execution result
            fixtest_result: Fixtest execution result
            errors: List of errors encountered

        Returns:
            Overall QA status
        """
        # Critical failures: Either tool has critical issues
        if not basedpyright_result or not fixtest_result:
            return QAStatus.FAIL

        if errors:
            return QAStatus.FAIL

        # PASS: Both tools succeeded with no issues
        if basedpyright_result.success and fixtest_result.success:
            # Check for warnings
            total_warnings = basedpyright_result.warning_count + (100 - fixtest_result.coverage_percentage)
            if total_warnings > 0 and total_warnings < 10:
                return QAStatus.CONCERNS
            return QAStatus.PASS

        # CONCERNS: Non-blocking issues
        if basedpyright_result.success and fixtest_result.tests_failed <= 2:
            return QAStatus.CONCERNS

        if fixtest_result.success and basedpyright_result.error_count <= 3:
            return QAStatus.CONCERNS

        # FAIL: Critical issues
        return QAStatus.FAIL

    def _update_progress_db(self, story_path: str, qa_result: QAResult) -> None:
        """
        Update progress.db with QA results

        Args:
            story_path: Path to the story file
            qa_result: QA result to store
        """
        try:
            with sqlite3.connect(self.progress_db_path) as conn:
                cursor = conn.cursor()

                # Create table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS qa_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        story_path TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        status TEXT NOT NULL,
                        basedpyright_success INTEGER,
                        fixtest_success INTEGER,
                        error_count INTEGER,
                        warning_count INTEGER,
                        retry_count INTEGER,
                        details TEXT
                    )
                """)

                # Insert QA result
                cursor.execute("""
                    INSERT INTO qa_results (
                        story_path, timestamp, status, basedpyright_success,
                        fixtest_success, error_count, warning_count,
                        retry_count, details
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    story_path,
                    qa_result.timestamp,
                    qa_result.overall_status.value,
                    1 if qa_result.basedpyright_result and qa_result.basedpyright_result.success else 0,
                    1 if qa_result.fixtest_result and qa_result.fixtest_result.success else 0,
                    len(qa_result.errors),
                    len(qa_result.warnings),
                    qa_result.retry_count,
                    json.dumps(asdict(qa_result))
                ))

                conn.commit()
                logger.info(f"QA results updated in progress.db for story: {story_path}")

        except Exception as e:
            logger.error(f"Failed to update progress.db: {e}", exc_info=True)

    def generate_qa_report(self, qa_result: QAResult) -> str:
        """
        Generate a comprehensive QA report

        Args:
            qa_result: QA result to report on

        Returns:
            Formatted QA report as string
        """
        report = []
        report.append("=" * 80)
        report.append("QA AUTOMATION REPORT")
        report.append("=" * 80)
        report.append(f"Timestamp: {qa_result.timestamp}")
        report.append(f"Overall Status: {qa_result.overall_status.value}")
        report.append(f"Retry Count: {qa_result.retry_count}")
        report.append("")

        # BasedPyright results
        if qa_result.basedpyright_result:
            bp = qa_result.basedpyright_result
            report.append("-" * 80)
            report.append("BASEDPYRIGHT-WORKFLOW RESULTS")
            report.append("-" * 80)
            report.append(f"Success: {bp.success}")
            report.append(f"Exit Code: {bp.exit_code}")
            report.append(f"Errors: {bp.error_count}")
            report.append(f"Warnings: {bp.warning_count}")
            report.append(f"Type Errors: {len(bp.type_errors)}")
            report.append(f"Style Violations: {len(bp.style_violations)}")
            report.append(f"Import Issues: {len(bp.import_issues)}")
            report.append(f"Undefined Variables: {len(bp.undefined_variables)}")
            if bp.report_path:
                report.append(f"Report Path: {bp.report_path}")
            report.append("")

        # Fixtest results
        if qa_result.fixtest_result:
            ft = qa_result.fixtest_result
            report.append("-" * 80)
            report.append("FIXTEST-WORKFLOW RESULTS")
            report.append("-" * 80)
            report.append(f"Success: {ft.success}")
            report.append(f"Exit Code: {ft.exit_code}")
            report.append(f"Tests Passed: {ft.tests_passed}")
            report.append(f"Tests Failed: {ft.tests_failed}")
            report.append(f"Tests Skipped: {ft.tests_skipped}")
            report.append(f"Coverage: {ft.coverage_percentage}%")
            report.append(f"Failing Test Cases: {len(ft.failing_test_cases)}")
            report.append(f"Auto-Fixed Tests: {len(ft.auto_fixed_tests)}")
            if ft.summary_path:
                report.append(f"Summary Path: {ft.summary_path}")
            report.append("")

        # Errors and warnings
        if qa_result.errors:
            report.append("-" * 80)
            report.append("ERRORS")
            report.append("-" * 80)
            for error in qa_result.errors:
                report.append(f"• {error}")
            report.append("")

        if qa_result.warnings:
            report.append("-" * 80)
            report.append("WARNINGS")
            report.append("-" * 80)
            for warning in qa_result.warnings[:10]:  # Limit to 10 warnings
                report.append(f"• {warning}")
            if len(qa_result.warnings) > 10:
                report.append(f"... and {len(qa_result.warnings) - 10} more warnings")
            report.append("")

        report.append("=" * 80)

        return "\n".join(report)


def main():
    """Main entry point for QA automation"""
    import argparse

    parser = argparse.ArgumentParser(description="QA Tools Integration Automation")
    parser.add_argument("--story-path", required=True, help="Path to the story file")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--progress-db", default="progress.db", help="Path to progress database")
    parser.add_argument("--max-retries", type=int, default=3, help="Maximum retry attempts")
    parser.add_argument("--output-format", choices=["json", "text"], default="text", help="Output format")

    args = parser.parse_args()

    # Initialize QA automation
    qa_workflow = QAWorkflowAutomation(args.project_root, args.progress_db)

    # Run QA checks
    result = qa_workflow.run_qa_checks(args.story_path, args.max_retries)

    # Generate and print report
    if args.output_format == "json":
        print(json.dumps(asdict(result), indent=2))
    else:
        report = qa_workflow.generate_qa_report(result)
        print(report)

    # Exit with appropriate code
    if result.overall_status == QAStatus.PASS:
        sys.exit(0)
    elif result.overall_status == QAStatus.CONCERNS:
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
