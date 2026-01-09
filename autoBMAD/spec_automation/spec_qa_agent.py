"""
Spec QA Agent

Document-centric QA review agent for spec automation.
Verifies implementation against all extracted requirements and generates detailed reports.
"""

import json
import logging
from enum import Enum
from typing import Any, Dict, List, Optional
from pathlib import Path

from autoBMAD.spec_automation.doc_parser import DocumentParser
from autoBMAD.spec_automation.spec_state_manager import SpecStateManager
from autoBMAD.spec_automation.prompts import PromptSystem

logger = logging.getLogger(__name__)


class QAReportStatus(Enum):
    """QA report status enumeration."""
    PASS = "PASS"
    FAIL = "FAIL"
    CONCERNS = "CONCERNS"


class QAReport:
    """QA review report with detailed findings."""

    def __init__(
        self,
        story_path: str,
        overall_status: QAReportStatus,
        requirement_reports: List[Dict[str, Any]],
        overall_coverage: float,
        findings: List[str],
    ):
        """
        Initialize QA report.

        Args:
            story_path: Path to the story file
            overall_status: Overall PASS/FAIL/CONCERNS status
            requirement_reports: List of requirement-specific reports
            overall_coverage: Overall test coverage percentage
            findings: List of overall findings
        """
        self.story_path = story_path
        self.overall_status = overall_status
        self.requirement_reports = requirement_reports
        self.overall_coverage = overall_coverage
        self.findings = findings

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "story_path": self.story_path,
            "overall_status": self.overall_status.value,
            "requirement_reports": self.requirement_reports,
            "overall_coverage": self.overall_coverage,
            "findings": self.findings,
        }

    def __str__(self) -> str:
        """String representation of the report."""
        status_emoji = {
            QAReportStatus.PASS: "✅",
            QAReportStatus.FAIL: "❌",
            QAReportStatus.CONCERNS: "⚠️",
        }

        result = "QA Review Report\n"
        result += f"{status_emoji[self.overall_status]} Overall Status: {self.overall_status.value}\n"
        result += f"Coverage: {self.overall_coverage:.1%}\n\n"

        result += f"Requirement Reports ({len(self.requirement_reports)}):\n"
        for req_report in self.requirement_reports:
            result += f"  - {req_report['requirement']}: {req_report['status']}\n"

        if self.findings:
            result += f"\nFindings ({len(self.findings)}):\n"
            for finding in self.findings:
                result += f"  - {finding}\n"

        return result


class SpecQAAgent:
    """Document-centric QA agent for spec automation."""

    def __init__(self, sdk: Optional[Any] = None, db_path: Optional[Path] = None):
        """
        Initialize the spec QA agent.

        Args:
            sdk: Claude SDK instance (optional for testing)
            db_path: Path to SQLite database for state tracking
        """
        self.sdk = sdk
        self.document_parser = DocumentParser()
        self.prompts = PromptSystem()
        self.db_path = db_path or Path("spec_progress.db")
        self.state_manager = SpecStateManager(self.db_path)
        logger.info("SpecQAAgent initialized")

    def _determine_status(
        self, implementation_status: str, test_coverage: float, findings: List[str]
    ) -> QAReportStatus:
        """
        Determine PASS/FAIL/CONCERNS status based on metrics.

        Args:
            implementation_status: Implementation status (Implemented/Partial/Missing)
            test_coverage: Test coverage percentage (0.0-1.0)
            findings: List of findings

        Returns:
            QAReportStatus enum value
        """
        # FAIL: Missing implementation OR very low test coverage (<30%)
        if implementation_status == "Missing" or test_coverage < 0.3:
            return QAReportStatus.FAIL

        # PASS: Fully implemented with good test coverage (>70%)
        if implementation_status == "Implemented" and test_coverage >= 0.7:
            return QAReportStatus.PASS

        # CONCERNS: Partial implementation OR moderate test coverage (30-70%)
        return QAReportStatus.CONCERNS

    def _verify_implementation_basic(
        self, requirement: str, source_code: str
    ) -> str:
        """
        Basic implementation verification without SDK.

        Args:
            requirement: Requirement text
            source_code: Source code to analyze

        Returns:
            Implementation status: "Implemented", "Partial", "Missing", or "Unknown"
        """
        # Simple keyword-based verification for basic cases
        req_lower = requirement.lower()
        code_lower = source_code.lower()

        # Check for key terms in requirement
        req_words = set(req_lower.split())

        # Count matching words
        matches = sum(1 for word in req_words if word in code_lower)

        # Determine status based on match ratio
        if matches == 0:
            return "Missing"
        elif matches < len(req_words) * 0.5:
            return "Partial"
        else:
            return "Implemented"

    def _check_test_coverage_basic(
        self, requirement: str, test_code: str
    ) -> float:
        """
        Basic test coverage assessment without SDK.

        Args:
            requirement: Requirement text
            test_code: Test code to analyze

        Returns:
            Coverage percentage (0.0-1.0)
        """
        # Simple heuristic: check if test code contains requirement keywords
        req_lower = requirement.lower()
        test_lower = test_code.lower()

        req_words = set(req_lower.split())
        test_matches = sum(1 for word in req_words if word in test_lower)

        if len(req_words) == 0:
            return 0.0

        coverage = test_matches / len(req_words)

        # Cap at 1.0
        return min(coverage, 1.0)

    async def review_implementation(self, story_path: str) -> QAReport:
        """
        Review implementation against requirements from document.

        Args:
            story_path: Path to the story file

        Returns:
            QAReport with detailed findings
        """
        logger.info(f"Starting review for {story_path}")

        try:
            # Parse the story document
            story_file = Path(story_path)
            if not story_file.exists():
                raise FileNotFoundError(f"Story file not found: {story_path}")

            parsed_doc = self.document_parser.parse_document(story_file)
            logger.info(f"Parsed document: {parsed_doc.get('title', 'Untitled')}")

            # Extract requirements
            requirements = parsed_doc.get("requirements", [])

            # Collect source code files
            source_paths = self._collect_source_files(story_file.parent)
            test_paths = self._collect_test_files(story_file.parent)

            # Verify each requirement
            requirement_reports = []
            for requirement in requirements:
                req_report = self._verify_requirement(
                    requirement, source_paths, test_paths
                )
                requirement_reports.append(req_report)

            # Calculate overall coverage
            overall_coverage = self._calculate_overall_coverage(requirement_reports)

            # Generate findings
            findings = self._generate_findings(
                requirement_reports, source_paths, test_paths
            )

            # Determine overall status
            overall_status = self._determine_overall_status(requirement_reports)

            # Create report
            report = QAReport(
                story_path=str(story_path),
                overall_status=overall_status,
                requirement_reports=requirement_reports,
                overall_coverage=overall_coverage,
                findings=findings,
            )

            # Save report to database
            self._save_report(report)

            # Update story status
            self.state_manager.update_story_status(
                story_path=str(story_path),
                status=overall_status.value,
                phase="QA Review Complete",
            )

            logger.info(f"Review complete. Status: {overall_status.value}")
            return report

        except Exception as e:
            logger.error(f"Error during review: {e}", exc_info=True)
            raise

    def _verify_requirement(
        self, requirement: str, source_paths: List[Path], test_paths: List[Path]
    ) -> Dict[str, Any]:
        """
        Verify a single requirement against source code and tests.

        Args:
            requirement: Requirement text
            source_paths: List of source file paths
            test_paths: List of test file paths

        Returns:
            Requirement verification report
        """
        # Read source code
        source_code = ""
        for path in source_paths:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    source_code += f.read() + "\n"
            except Exception as e:
                logger.warning(f"Could not read {path}: {e}")

        # Verify implementation
        implementation_status = self._verify_implementation_basic(
            requirement, source_code
        )

        # Read test code
        test_code = ""
        for path in test_paths:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    test_code += f.read() + "\n"
            except Exception as e:
                logger.warning(f"Could not read {path}: {e}")

        # Check test coverage
        test_coverage = self._check_test_coverage_basic(requirement, test_code)

        # Determine status
        status = self._determine_status(
            implementation_status, test_coverage, []
        )

        return {
            "requirement": requirement,
            "implementation_status": implementation_status,
            "test_coverage": test_coverage,
            "status": status.value,
            "findings": [],  # TODO: Populate with detailed findings
        }

    def _collect_source_files(self, project_root: Path) -> List[Path]:
        """
        Collect source code files from project.

        Args:
            project_root: Project root directory

        Returns:
            List of source file paths
        """
        source_files = []
        for ext in ["*.py", "*.js", "*.ts", "*.java", "*.cpp", "*.c"]:
            source_files.extend(project_root.rglob(ext))
        return source_files

    def _collect_test_files(self, project_root: Path) -> List[Path]:
        """
        Collect test files from project.

        Args:
            project_root: Project root directory

        Returns:
            List of test file paths
        """
        test_files = []
        for pattern in ["test_*.py", "*_test.py", "tests/*.py"]:
            test_files.extend(project_root.rglob(pattern))
        return test_files

    def _calculate_overall_coverage(
        self, requirement_reports: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate overall test coverage.

        Args:
            requirement_reports: List of requirement reports

        Returns:
            Overall coverage percentage (0.0-1.0)
        """
        if not requirement_reports:
            return 0.0

        total_coverage = sum(
            req.get("test_coverage", 0.0) for req in requirement_reports
        )
        return total_coverage / len(requirement_reports)

    def _generate_findings(
        self,
        requirement_reports: List[Dict[str, Any]],
        source_paths: List[Path],
        test_paths: List[Path],
    ) -> List[str]:
        """
        Generate findings from verification results.

        Args:
            requirement_reports: List of requirement reports
            source_paths: Source file paths
            test_paths: Test file paths

        Returns:
            List of findings
        """
        findings = []

        # Check for missing implementations
        missing_reqs = [
            req["requirement"]
            for req in requirement_reports
            if req["implementation_status"] == "Missing"
        ]
        if missing_reqs:
            findings.append(
                f"Missing implementations for {len(missing_reqs)} requirements"
            )

        # Check for low test coverage
        low_coverage_reqs = [
            req["requirement"]
            for req in requirement_reports
            if req["test_coverage"] < 0.5
        ]
        if low_coverage_reqs:
            findings.append(
                f"Low test coverage for {len(low_coverage_reqs)} requirements"
            )

        # Check for insufficient test files
        if len(test_paths) == 0:
            findings.append("No test files found")

        return findings

    def _determine_overall_status(
        self, requirement_reports: List[Dict[str, Any]]
    ) -> QAReportStatus:
        """
        Determine overall status from requirement reports.

        Args:
            requirement_reports: List of requirement reports

        Returns:
            Overall QAReportStatus
        """
        if not requirement_reports:
            return QAReportStatus.FAIL

        # Count statuses
        statuses = [req["status"] for req in requirement_reports]

        if all(status == "PASS" for status in statuses):
            return QAReportStatus.PASS

        if any(status == "FAIL" for status in statuses):
            return QAReportStatus.FAIL

        return QAReportStatus.CONCERNS

    def _save_report(self, report: QAReport) -> None:
        """
        Save report to database.

        Args:
            report: QA report to save
        """
        try:
            self.state_manager.save_review_report(
                story_path=report.story_path,
                report_json=json.dumps(report.to_dict()),
                overall_status=report.overall_status.value,
            )

            # Save individual QA results
            for req_report in report.requirement_reports:
                self.state_manager.save_qa_result(
                    story_path=report.story_path,
                    requirement=req_report["requirement"],
                    status=req_report["status"],
                    findings=req_report.get("findings", []),
                    test_coverage=req_report.get("test_coverage", 0.0),
                )

            logger.debug(f"Report saved to database for {report.story_path}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}", exc_info=True)
