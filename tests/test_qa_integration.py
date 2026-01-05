"""
Tests for QA Tools Integration Module

Tests the integration of BasedPyright-Workflow and Fixtest-Workflow
into the BMAD workflow system.

Author: BMAD Development Team
Version: 1.0.0
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch
import sys

# Add the bmad-workflow module to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "bmad-workflow"))

from qa.qa_tools_integration import (
    QAStatus,
    QAViolation,
    QAResult,
    QAAggregateResult,
    BasedPyrightIntegration,
    FixtestIntegration,
    QAToolsOrchestrator
)


class TestQAViolation:
    """Test QAViolation dataclass"""

    def test_qa_violation_creation(self):
        """Test creating a QA violation"""
        violation = QAViolation(
            tool="basedpyright",
            file="src/test.py",
            line=10,
            column=5,
            rule="reportOptionalMemberAccess",
            message="Object is possibly undefined",
            severity="warning"
        )

        assert violation.tool == "basedpyright"
        assert violation.file == "src/test.py"
        assert violation.line == 10
        assert violation.column == 5
        assert violation.rule == "reportOptionalMemberAccess"
        assert violation.message == "Object is possibly undefined"
        assert violation.severity == "warning"
        assert violation.type == ""  # Default value


class TestQAResult:
    """Test QAResult dataclass"""

    def test_qa_result_creation(self):
        """Test creating a QA result"""
        start_time = datetime.now()
        end_time = datetime.now()
        violations = []

        result = QAResult(
            tool="basedpyright",
            status=QAStatus.PASS,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=5.0,
            violations=violations
        )

        assert result.tool == "basedpyright"
        assert result.status == QAStatus.PASS
        assert result.start_time == start_time
        assert result.end_time == end_time
        assert result.duration_seconds == 5.0
        assert result.violations == violations
        assert result.metrics is not None


class TestQAAggregateResult:
    """Test QAAggregateResult dataclass"""

    def test_qa_aggregate_result_creation(self):
        """Test creating an aggregate result"""
        bp_result = QAResult(
            tool="basedpyright",
            status=QAStatus.PASS,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_seconds=5.0,
            violations=[]
        )

        ft_result = QAResult(
            tool="fixtest",
            status=QAStatus.PASS,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_seconds=3.0,
            violations=[]
        )

        aggregate = QAAggregateResult(
            overall_status=QAStatus.PASS,
            basedpyright_result=bp_result,
            fixtest_result=ft_result,
            retry_count=0
        )

        assert aggregate.overall_status == QAStatus.PASS
        assert aggregate.basedpyright_result == bp_result
        assert aggregate.fixtest_result == ft_result
        assert aggregate.timestamp is not None


class TestBasedPyrightIntegration:
    """Test BasedPyrightIntegration class"""

    @pytest.fixture
    def project_root(self, tmp_path):
        """Create a temporary project root"""
        return tmp_path

    @pytest.fixture
    def basedpyright_integration(self, project_root):
        """Create a BasedPyrightIntegration instance"""
        # Create necessary directories
        (project_root / "basedpyright-workflow").mkdir(parents=True)
        (project_root / "basedpyright-workflow" / "results").mkdir(parents=True)
        return BasedPyrightIntegration(str(project_root))

    def test_initialization(self, basedpyright_integration, project_root):
        """Test initialization"""
        assert basedpyright_integration.project_root == project_root
        assert "basedpyright-workflow" in str(basedpyright_integration.workflow_dir)
        assert "results" in str(basedpyright_integration.results_dir)

    @patch('subprocess.run')
    def test_run_check_success(self, mock_run, basedpyright_integration):
        """Test successful run check"""
        # Mock successful subprocess call
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "BasedPyright check completed"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        # Create a mock JSON result file
        json_file = basedpyright_integration.results_dir / "basedpyright_check_result_20260104_120000.json"
        json_file.write_text(json.dumps({
            "diagnostics": [],
            "summary": {"total_errors": 0}
        }))

        result = basedpyright_integration.run_check(max_retries=0)

        assert result.tool == "basedpyright"
        assert result.status == QAStatus.PASS
        assert result.violations == []
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_run_check_with_violations(self, mock_run, basedpyright_integration):
        """Test run check with violations"""
        # Mock subprocess call with output
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "BasedPyright completed with issues"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        # Create a mock JSON result file with violations
        json_file = basedpyright_integration.results_dir / "basedpyright_check_result_20260104_120000.json"
        json_file.write_text(json.dumps({
            "diagnostics": [
                {
                    "file": "src/test.py",
                    "line": 10,
                    "column": 5,
                    "rule": "reportOptionalMemberAccess",
                    "message": "Object is possibly undefined",
                    "severity": "warning"
                }
            ]
        }))

        result = basedpyright_integration.run_check(max_retries=0)

        assert result.status == QAStatus.CONCERNS
        assert len(result.violations) == 1
        assert result.violations[0].file == "src/test.py"

    @patch('subprocess.run')
    def test_run_check_failure(self, mock_run, basedpyright_integration):
        """Test failed run check"""
        # Mock failed subprocess call
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "BasedPyright failed"
        mock_run.return_value = mock_result

        result = basedpyright_integration.run_check(max_retries=0)

        assert result.status == QAStatus.FAIL
        assert result.error_message is not None

    @patch('subprocess.run')
    def test_run_check_retry(self, mock_run, basedpyright_integration):
        """Test retry mechanism"""
        # Mock first call fails, second succeeds
        mock_fail = Mock()
        mock_fail.returncode = 1
        mock_fail.stderr = "Failed"

        mock_success = Mock()
        mock_success.returncode = 0
        mock_success.stdout = "Success"

        mock_run.side_effect = [mock_fail, mock_success]

        result = basedpyright_integration.run_check(max_retries=1)

        assert result.retry_count == 1
        assert result.status == QAStatus.PASS
        assert mock_run.call_count == 2

    def test_find_latest_result_files(self, basedpyright_integration):
        """Test finding latest result files"""
        # Create mock result files
        json_file = basedpyright_integration.results_dir / "basedpyright_check_result_20260104_120000.json"
        txt_file = basedpyright_integration.results_dir / "basedpyright_check_result_20260104_120000.txt"
        json_file.touch()
        txt_file.touch()

        json_path, txt_path = basedpyright_integration._find_latest_result_files()

        assert json_path == json_file
        assert txt_path == txt_file

    def test_parse_json_results(self, basedpyright_integration):
        """Test parsing JSON results"""
        # Create test JSON data
        json_data = {
            "diagnostics": [
                {
                    "file": "src/test.py",
                    "line": 10,
                    "column": 5,
                    "rule": "reportOptionalMemberAccess",
                    "message": "Object is possibly undefined",
                    "severity": "warning"
                },
                {
                    "file": "src/test2.py",
                    "line": 20,
                    "rule": "reportOptionalMemberAccess",
                    "message": "Another error",
                    "severity": "error"
                }
            ]
        }

        json_file = basedpyright_integration.results_dir / "test.json"
        json_file.write_text(json.dumps(json_data))

        violations = basedpyright_integration._parse_json_results(json_file)

        assert len(violations) == 2
        assert violations[0].file == "src/test.py"
        assert violations[0].line == 10
        assert violations[0].column == 5
        assert violations[1].file == "src/test2.py"
        assert violations[1].line == 20

    def test_parse_text_output(self, basedpyright_integration):
        """Test parsing text output"""
        output = """
src/test.py:10:5: warning: Object is possibly undefined
src/test2.py:20: error: Missing type annotation
"""

        violations = basedpyright_integration._parse_text_output(output)

        # Should find at least one violation
        assert len(violations) > 0

    def test_calculate_metrics(self, basedpyright_integration):
        """Test calculating metrics"""
        violations = [
            QAViolation(tool="bp", file="f1.py", severity="error"),
            QAViolation(tool="bp", file="f1.py", severity="error"),
            QAViolation(tool="bp", file="f2.py", severity="warning"),
            QAViolation(tool="bp", file="f3.py", severity="info"),
        ]

        metrics = basedpyright_integration._calculate_metrics(violations)

        assert metrics["total_violations"] == 4
        assert metrics["errors"] == 2
        assert metrics["warnings"] == 1
        assert metrics["infos"] == 1
        assert metrics["files_affected"] == 3


class TestFixtestIntegration:
    """Test FixtestIntegration class"""

    @pytest.fixture
    def project_root(self, tmp_path):
        """Create a temporary project root"""
        return tmp_path

    @pytest.fixture
    def fixtest_integration(self, project_root):
        """Create a FixtestIntegration instance"""
        # Create necessary directories
        (project_root / "fixtest-workflow").mkdir(parents=True)
        (project_root / "fixtest-workflow" / "fileslist").mkdir(parents=True)
        (project_root / "fixtest-workflow" / "summaries").mkdir(parents=True)
        return FixtestIntegration(str(project_root))

    def test_initialization(self, fixtest_integration, project_root):
        """Test initialization"""
        assert fixtest_integration.project_root == project_root
        assert "fixtest-workflow" in str(fixtest_integration.workflow_dir)
        assert "summaries" in str(fixtest_integration.summaries_dir)

    @patch('subprocess.run')
    def test_run_check_success(self, mock_run, fixtest_integration):
        """Test successful run check"""
        # Mock successful subprocess calls
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "All tests passed"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        # Create a mock summary file
        summary_file = fixtest_integration.summaries_dir / "test_results_summary_20260104_120000.json"
        summary_file.write_text(json.dumps({
            "files_with_errors": [],
            "errors": [],
            "failures": []
        }))

        result = fixtest_integration.run_check(max_retries=0)

        assert result.tool == "fixtest"
        assert result.status == QAStatus.PASS
        assert len(result.violations) == 0

    @patch('subprocess.run')
    def test_run_check_with_failures(self, mock_run, fixtest_integration):
        """Test run check with test failures"""
        # Mock subprocess call
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Some tests failed"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        # Create a mock summary file with failures
        summary_file = fixtest_integration.summaries_dir / "test_results_summary_20260104_120000.json"
        summary_file.write_text(json.dumps({
            "files_with_errors": ["test_fail.py"],
            "errors": [
                {
                    "file": "test_fail.py",
                    "message": "ERROR: test failed"
                }
            ],
            "failures": [
                {
                    "file": "test_fail.py",
                    "message": "FAILED: assertion error"
                }
            ]
        }))

        result = fixtest_integration.run_check(max_retries=0)

        assert result.status == QAStatus.FAIL
        assert len(result.violations) > 0

    def test_find_latest_summary_file(self, fixtest_integration):
        """Test finding latest summary file"""
        # Create mock summary files
        summary_file1 = fixtest_integration.summaries_dir / "test_results_summary_20260104_120000.json"
        summary_file2 = fixtest_integration.summaries_dir / "test_results_summary_20260104_130000.json"
        summary_file1.touch()
        summary_file2.touch()

        latest = fixtest_integration._find_latest_summary_file()

        assert latest == summary_file2

    def test_parse_summary_results(self, fixtest_integration):
        """Test parsing summary results"""
        # Create test summary data
        summary_data = {
            "files_with_errors": ["test_fail.py", "test_error.py"],
            "errors": [
                {
                    "file": "test_fail.py",
                    "message": "ERROR: test failed"
                }
            ],
            "failures": [
                {
                    "file": "test_error.py",
                    "message": "FAILED: assertion error"
                }
            ]
        }

        summary_file = fixtest_integration.summaries_dir / "test.json"
        summary_file.write_text(json.dumps(summary_data))

        violations = fixtest_integration._parse_summary_results(summary_file)

        assert len(violations) == 2
        assert violations[0].type == "test_error"
        assert violations[1].type == "test_failure"


class TestQAToolsOrchestrator:
    """Test QAToolsOrchestrator class"""

    @pytest.fixture
    def project_root(self, tmp_path):
        """Create a temporary project root"""
        return tmp_path

    @pytest.fixture
    def orchestrator(self, project_root):
        """Create a QAToolsOrchestrator instance"""
        # Create necessary directories
        (project_root / "basedpyright-workflow").mkdir(parents=True)
        (project_root / "basedpyright-workflow" / "results").mkdir(parents=True)
        (project_root / "fixtest-workflow").mkdir(parents=True)
        (project_root / "fixtest-workflow" / "summaries").mkdir(parents=True)
        return QAToolsOrchestrator(str(project_root))

    @patch.object(BasedPyrightIntegration, 'run_check')
    @patch.object(FixtestIntegration, 'run_check')
    def test_run_qa_checks_both_pass(self, mock_ft_run, mock_bp_run, orchestrator):
        """Test QA checks when both tools pass"""
        # Mock both tools to pass
        bp_result = QAResult(
            tool="basedpyright",
            status=QAStatus.PASS,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_seconds=5.0,
            violations=[]
        )
        ft_result = QAResult(
            tool="fixtest",
            status=QAStatus.PASS,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_seconds=3.0,
            violations=[]
        )
        mock_bp_run.return_value = bp_result
        mock_ft_run.return_value = ft_result

        result = orchestrator.run_qa_checks(max_retries=0)

        assert result.overall_status == QAStatus.PASS
        assert result.basedpyright_result.status == QAStatus.PASS
        assert result.fixtest_result.status == QAStatus.PASS

    @patch.object(BasedPyrightIntegration, 'run_check')
    @patch.object(FixtestIntegration, 'run_check')
    def test_run_qa_checks_one_fail(self, mock_ft_run, mock_bp_run, orchestrator):
        """Test QA checks when one tool fails"""
        # Mock one tool to fail
        bp_result = QAResult(
            tool="basedpyright",
            status=QAStatus.PASS,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_seconds=5.0,
            violations=[]
        )
        ft_result = QAResult(
            tool="fixtest",
            status=QAStatus.FAIL,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_seconds=3.0,
            violations=[QAViolation(tool="fixtest", file="test.py", severity="error")]
        )
        mock_bp_run.return_value = bp_result
        mock_ft_run.return_value = ft_result

        result = orchestrator.run_qa_checks(max_retries=0)

        assert result.overall_status == QAStatus.FAIL
        assert result.basedpyright_result.status == QAStatus.PASS
        assert result.fixtest_result.status == QAStatus.FAIL

    @patch.object(BasedPyrightIntegration, 'run_check')
    @patch.object(FixtestIntegration, 'run_check')
    def test_run_qa_checks_concerns(self, mock_ft_run, mock_bp_run, orchestrator):
        """Test QA checks when tools have concerns"""
        # Mock tools to have concerns
        bp_result = QAResult(
            tool="basedpyright",
            status=QAStatus.CONCERNS,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_seconds=5.0,
            violations=[QAViolation(tool="basedpyright", file="test.py", severity="warning")]
        )
        ft_result = QAResult(
            tool="fixtest",
            status=QAStatus.PASS,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_seconds=3.0,
            violations=[]
        )
        mock_bp_run.return_value = bp_result
        mock_ft_run.return_value = ft_result

        result = orchestrator.run_qa_checks(max_retries=0)

        assert result.overall_status == QAStatus.CONCERNS

    def test_save_results(self, orchestrator, tmp_path):
        """Test saving results to file"""
        # Create test result
        bp_result = QAResult(
            tool="basedpyright",
            status=QAStatus.PASS,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_seconds=5.0,
            violations=[]
        )
        ft_result = QAResult(
            tool="fixtest",
            status=QAStatus.PASS,
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_seconds=3.0,
            violations=[]
        )

        aggregate = QAAggregateResult(
            overall_status=QAStatus.PASS,
            basedpyright_result=bp_result,
            fixtest_result=ft_result
        )

        # Save results
        orchestrator.save_results(aggregate, tmp_path)

        # Check file was created
        json_files = list(tmp_path.glob("qa_results_*.json"))
        assert len(json_files) == 1

        # Verify file content
        with open(json_files[0], 'r') as f:
            data = json.load(f)

        assert data["overall_status"] == "PASS"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
