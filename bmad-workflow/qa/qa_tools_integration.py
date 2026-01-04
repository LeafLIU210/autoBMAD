"""
QA Tools Integration Module

This module provides integration for BasedPyright-Workflow and Fixtest-Workflow
into the BMAD workflow system. It handles subprocess calls, output parsing,
retry mechanisms, and result aggregation.

Author: BMAD Development Team
Version: 1.0.0
"""

import json
import subprocess
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum


class QAStatus(Enum):
    """QA status enumeration matching BMAD quality gate states"""
    PASS = "PASS"
    CONCERNS = "CONCERNS"
    FAIL = "FAIL"
    WAIVED = "WAIVED"


class QAToolType(Enum):
    """QA tool types"""
    BASEDPYRIGHT = "basedpyright"
    FIXTEST = "fixtest"


@dataclass
class QAViolation:
    """Represents a single QA violation"""
    tool: str
    file: str
    line: Optional[int] = None
    column: Optional[int] = None
    rule: Optional[str] = None
    message: str = ""
    severity: str = "error"  # error, warning, info
    type: str = ""  # type error, test failure, etc.


@dataclass
class QAResult:
    """Represents the result of a QA tool execution"""
    tool: str
    status: QAStatus
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    violations: List[QAViolation]
    output_file: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    metrics: Dict[str, Any] = None

    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}


@dataclass
class QAAggregateResult:
    """Aggregated result from all QA tools"""
    overall_status: QAStatus
    basedpyright_result: Optional[QAResult] = None
    fixtest_result: Optional[QAResult] = None
    timestamp: datetime = None
    retry_count: int = 0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class BasedPyrightIntegration:
    """Integration wrapper for BasedPyright-Workflow"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.workflow_dir = self.project_root / "basedpyright-workflow"
        self.results_dir = self.workflow_dir / "results"
        self.reports_dir = self.workflow_dir / "reports"

    def run_check(self, max_retries: int = 2) -> QAResult:
        """
        Run BasedPyright check via subprocess

        Args:
            max_retries: Maximum number of retry attempts

        Returns:
            QAResult object with parsed results
        """
        start_time = datetime.now()

        # Ensure results directory exists
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Prepare command
        cmd = [
            "python", "-m", "basedpyright_workflow", "check",
            "--output-dir", str(self.results_dir)
        ]

        # Run with retries
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                WriteWorkflowLog(
                    f"Running BasedPyright check (attempt {attempt + 1}/{max_retries + 1})",
                    "Info"
                )

                result = subprocess.run(
                    cmd,
                    cwd=str(self.project_root),
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )

                if result.returncode == 0:
                    # Success - parse results
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()

                    # Find latest result files
                    json_file, txt_file = self._find_latest_result_files()

                    if json_file:
                        violations = self._parse_json_results(json_file)
                    else:
                        violations = self._parse_text_output(result.stdout)

                    metrics = self._calculate_metrics(violations)

                    return QAResult(
                        tool="basedpyright",
                        status=QAStatus.PASS if not violations else QAStatus.CONCERNS,
                        start_time=start_time,
                        end_time=end_time,
                        duration_seconds=duration,
                        violations=violations,
                        output_file=str(json_file) if json_file else None,
                        retry_count=attempt
                    )
                else:
                    # Error occurred
                    last_error = result.stderr or result.stdout
                    WriteWorkflowLog(
                        f"BasedPyright check failed (attempt {attempt + 1}): {last_error}",
                        "Warning"
                    )

            except subprocess.TimeoutExpired:
                last_error = "BasedPyright check timed out after 5 minutes"
                WriteWorkflowLog(last_error, "Warning")
            except Exception as e:
                last_error = str(e)
                WriteWorkflowLog(
                    f"BasedPyright check failed with exception: {last_error}",
                    "Error"
                )

        # All retries failed
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        return QAResult(
            tool="basedpyright",
            status=QAStatus.FAIL,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            violations=[],
            error_message=last_error,
            retry_count=max_retries
        )

    def _find_latest_result_files(self) -> Tuple[Optional[Path], Optional[Path]]:
        """Find the latest BasedPyright result files"""
        if not self.results_dir.exists():
            return None, None

        json_files = list(self.results_dir.glob("basedpyright_check_result_*.json"))
        txt_files = list(self.results_dir.glob("basedpyright_check_result_*.txt"))

        if not json_files or not txt_files:
            return None, None

        latest_json = max(json_files, key=lambda f: f.stat().st_mtime)
        latest_txt = max(txt_files, key=lambda f: f.stat().st_mtime)

        return latest_json, latest_txt

    def _parse_json_results(self, json_file: Path) -> List[QAViolation]:
        """Parse BasedPyright JSON result file"""
        violations = []

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # BasedPyright JSON structure may vary, handle common patterns
            diagnostics = data.get('diagnostics', data.get('errors', []))

            for diag in diagnostics:
                # Extract information based on common BasedPyright output format
                file_path = diag.get('file', diag.get('path', ''))
                line = diag.get('line', diag.get('start', {}).get('line'))
                column = diag.get('column', diag.get('start', {}).get('character'))
                rule = diag.get('rule', diag.get('ruleId', diag.get('code')))
                message = diag.get('message', diag.get('description', ''))
                severity = diag.get('severity', 'error').lower()

                violation = QAViolation(
                    tool="basedpyright",
                    file=file_path,
                    line=line,
                    column=column,
                    rule=rule,
                    message=message,
                    severity=severity,
                    type="type_error"
                )

                violations.append(violation)

        except Exception as e:
            WriteWorkflowLog(
                f"Failed to parse BasedPyright JSON results: {e}",
                "Warning"
            )

        return violations

    def _parse_text_output(self, output: str) -> List[QAViolation]:
        """Parse BasedPyright text output"""
        violations = []

        # Simple regex patterns for common BasedPyright text output formats
        patterns = [
            r'(.+?):(\d+):(\d+):\s+(error|warning|info):\s+(.+?)(?:\s+\(.*\))?$',
            r'(.+?):(\d+):\s+(error|warning|info):\s+(.+?)$',
        ]

        for line in output.split('\n'):
            for pattern in patterns:
                match = re.match(pattern, line.strip())
                if match:
                    groups = match.groups()
                    if len(groups) == 5:
                        file_path, line_num, column, severity, message = groups
                    elif len(groups) == 4:
                        file_path, line_num, severity, message = groups
                        column = None
                    else:
                        continue

                    violation = QAViolation(
                        tool="basedpyright",
                        file=file_path,
                        line=int(line_num) if line_num else None,
                        column=int(column) if column else None,
                        message=message,
                        severity=severity.lower(),
                        type="type_error"
                    )

                    violations.append(violation)
                    break

        return violations

    def _calculate_metrics(self, violations: List[QAViolation]) -> Dict[str, Any]:
        """Calculate metrics from violations"""
        metrics = {
            "total_violations": len(violations),
            "errors": sum(1 for v in violations if v.severity == "error"),
            "warnings": sum(1 for v in violations if v.severity == "warning"),
            "infos": sum(1 for v in violations if v.severity == "info"),
            "files_affected": len(set(v.file for v in violations)),
            "rules": list(set(v.rule for v in violations if v.rule))
        }

        return metrics


class FixtestIntegration:
    """Integration wrapper for Fixtest-Workflow"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.workflow_dir = self.project_root / "fixtest-workflow"
        self.fileslist_dir = self.workflow_dir / "fileslist"
        self.summaries_dir = self.workflow_dir / "summaries"

    def run_check(self, max_retries: int = 2) -> QAResult:
        """
        Run Fixtest check via subprocess

        Args:
            max_retries: Maximum number of retry attempts

        Returns:
            QAResult object with parsed results
        """
        start_time = datetime.now()

        # Ensure directories exist
        self.fileslist_dir.mkdir(parents=True, exist_ok=True)
        self.summaries_dir.mkdir(parents=True, exist_ok=True)

        last_error = None

        for attempt in range(max_retries + 1):
            try:
                WriteWorkflowLog(
                    f"Running Fixtest check (attempt {attempt + 1}/{max_retries + 1})",
                    "Info"
                )

                # Step 1: Scan test files
                scan_result = subprocess.run(
                    ["python", "scan_test_files.py"],
                    cwd=str(self.workflow_dir),
                    capture_output=True,
                    text=True,
                    timeout=120
                )

                if scan_result.returncode != 0:
                    last_error = f"Scan failed: {scan_result.stderr}"
                    continue

                # Step 2: Run tests
                test_result = subprocess.run(
                    ["python", "run_tests.py"],
                    cwd=str(self.workflow_dir),
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minute timeout
                )

                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                if test_result.returncode == 0 or "passed" in test_result.stdout.lower():
                    # Parse results
                    summary_file = self._find_latest_summary_file()

                    if summary_file:
                        violations = self._parse_summary_results(summary_file)
                    else:
                        # Fallback: parse stdout
                        violations = self._parse_test_output(test_result.stdout)

                    metrics = self._calculate_test_metrics(violations)

                    # Determine status based on violations
                    if not violations:
                        status = QAStatus.PASS
                    elif any(v.severity == "error" for v in violations):
                        status = QAStatus.FAIL
                    else:
                        status = QAStatus.CONCERNS

                    return QAResult(
                        tool="fixtest",
                        status=status,
                        start_time=start_time,
                        end_time=end_time,
                        duration_seconds=duration,
                        violations=violations,
                        output_file=str(summary_file) if summary_file else None,
                        retry_count=attempt,
                        metrics=metrics
                    )
                else:
                    last_error = test_result.stderr or test_result.stdout
                    WriteWorkflowLog(
                        f"Fixtest check failed (attempt {attempt + 1}): {last_error}",
                        "Warning"
                    )

            except subprocess.TimeoutExpired:
                last_error = "Fixtest check timed out"
                WriteWorkflowLog(last_error, "Warning")
            except Exception as e:
                last_error = str(e)
                WriteWorkflowLog(
                    f"Fixtest check failed with exception: {last_error}",
                    "Error"
                )

        # All retries failed
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        return QAResult(
            tool="fixtest",
            status=QAStatus.FAIL,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            violations=[],
            error_message=last_error,
            retry_count=max_retries
        )

    def _find_latest_summary_file(self) -> Optional[Path]:
        """Find the latest test summary file"""
        if not self.summaries_dir.exists():
            return None

        summary_files = list(self.summaries_dir.glob("test_results_summary_*.json"))

        if not summary_files:
            return None

        return max(summary_files, key=lambda f: f.stat().st_mtime)

    def _parse_summary_results(self, summary_file: Path) -> List[QAViolation]:
        """Parse test summary JSON file"""
        violations = []

        try:
            with open(summary_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Parse errors and failures
            files_with_errors = data.get('files_with_errors', [])
            errors = data.get('errors', [])
            failures = data.get('failures', [])

            # Convert to violations
            for error in errors:
                violation = QAViolation(
                    tool="fixtest",
                    file=error.get('file', ''),
                    message=error.get('message', ''),
                    severity="error",
                    type="test_error"
                )
                violations.append(violation)

            for failure in failures:
                violation = QAViolation(
                    tool="fixtest",
                    file=failure.get('file', ''),
                    message=failure.get('message', ''),
                    severity="error",
                    type="test_failure"
                )
                violations.append(violation)

        except Exception as e:
            WriteWorkflowLog(
                f"Failed to parse test summary results: {e}",
                "Warning"
            )

        return violations

    def _parse_test_output(self, output: str) -> List[QAViolation]:
        """Parse test execution output"""
        violations = []

        # Look for ERROR and FAILED patterns
        for line in output.split('\n'):
            if 'ERROR:' in line or 'FAILED' in line:
                violation = QAViolation(
                    tool="fixtest",
                    file="",  # Will need more sophisticated parsing
                    message=line.strip(),
                    severity="error",
                    type="test_error"
                )
                violations.append(violation)

        return violations

    def _calculate_test_metrics(self, violations: List[QAViolation]) -> Dict[str, Any]:
        """Calculate test metrics from violations"""
        metrics = {
            "total_violations": len(violations),
            "errors": sum(1 for v in violations if v.severity == "error"),
            "failures": sum(1 for v in violations if v.type == "test_failure"),
            "files_affected": len(set(v.file for v in violations)),
            "error_rate": len(violations)  # Simplified metric
        }

        return metrics


class QAToolsOrchestrator:
    """Main orchestrator for QA tools integration"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.basedpyright = BasedPyrightIntegration(project_root)
        self.fixtest = FixtestIntegration(project_root)

    def run_qa_checks(self, max_retries: int = 2) -> QAAggregateResult:
        """
        Run all QA checks in sequence

        Args:
            max_retries: Maximum retry attempts per tool

        Returns:
            QAAggregateResult with combined results
        """
        WriteWorkflowLog("Starting QA checks", "Info")

        # Run BasedPyright check
        WriteWorkflowLog("Running BasedPyright check", "Info")
        basedpyright_result = self.basedpyright.run_check(max_retries)

        # Run Fixtest check
        WriteWorkflowLog("Running Fixtest check", "Info")
        fixtest_result = self.fixtest.run_check(max_retries)

        # Aggregate results
        aggregate = self._aggregate_results(basedpyright_result, fixtest_result)

        # Log final status
        WriteWorkflowLog(
            f"QA checks completed with status: {aggregate.overall_status.value}",
            "Info" if aggregate.overall_status == QAStatus.PASS else "Warning"
        )

        return aggregate

    def _aggregate_results(self, bp_result: QAResult, ft_result: QAResult) -> QAAggregateResult:
        """Aggregate results from both QA tools"""
        # Determine overall status
        if bp_result.status == QAStatus.FAIL or ft_result.status == QAStatus.FAIL:
            overall_status = QAStatus.FAIL
        elif bp_result.status == QAStatus.CONCERNS or ft_result.status == QAStatus.CONCERNS:
            overall_status = QAStatus.CONCERNS
        elif bp_result.status == QAStatus.PASS and ft_result.status == QAStatus.PASS:
            overall_status = QAStatus.PASS
        else:
            overall_status = QAStatus.CONCERNS

        return QAAggregateResult(
            overall_status=overall_status,
            basedpyright_result=bp_result,
            fixtest_result=ft_result,
            retry_count=max(bp_result.retry_count, ft_result.retry_count)
        )

    def save_results(self, result: QAAggregateResult, output_dir: Path) -> None:
        """Save QA results to file"""
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"qa_results_{timestamp}.json"

        # Convert to dict for JSON serialization
        result_dict = asdict(result)

        # Convert datetime objects to strings in the dict
        for tool_key in ['basedpyright_result', 'fixtest_result']:
            tool_result = result_dict.get(tool_key)
            if tool_result:
                tool_result['start_time'] = tool_result['start_time'].isoformat()
                tool_result['end_time'] = tool_result['end_time'].isoformat()
                # Convert QAStatus enum to string
                if 'status' in tool_result and hasattr(tool_result['status'], 'value'):
                    tool_result['status'] = tool_result['status'].value

        result_dict['timestamp'] = result.timestamp.isoformat()
        # Convert overall status enum to string
        if 'overall_status' in result_dict and hasattr(result_dict['overall_status'], 'value'):
            result_dict['overall_status'] = result_dict['overall_status'].value

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, indent=2, ensure_ascii=False)


# Internal logging function for Python module
def WriteWorkflowLog(Message, Level):
    """Internal logging function - will be connected to PowerShell logging"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{Level}] {Message}")
