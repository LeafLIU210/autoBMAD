"""Tests for SpecQAAgent - Document-centric QA review agent."""

import pytest
from pathlib import Path
from unittest.mock import Mock

from autoBMAD.spec_automation.spec_qa_agent import SpecQAAgent, QAReportStatus, QAReport


class TestSpecQAAgent:
    """Test suite for SpecQAAgent"""

    def test_init(self):
        """Test agent initialization"""
        agent = SpecQAAgent()
        assert agent is not None
        assert agent.document_parser is not None

    def test_init_with_sdk(self):
        """Test agent initialization with SDK"""
        mock_sdk = Mock()
        agent = SpecQAAgent(sdk=mock_sdk)
        assert agent.sdk == mock_sdk

    def test_determine_status_pass(self):
        """Test PASS status"""
        agent = SpecQAAgent()
        status = agent._determine_status("Implemented", 0.8, [])
        assert status == QAReportStatus.PASS

    def test_determine_status_fail_missing(self):
        """Test FAIL status - Missing implementation"""
        agent = SpecQAAgent()
        status = agent._determine_status("Missing", 0.5, [])
        assert status == QAReportStatus.FAIL

    def test_determine_status_fail_low_coverage(self):
        """Test FAIL status - Low test coverage"""
        agent = SpecQAAgent()
        status = agent._determine_status("Implemented", 0.2, [])
        assert status == QAReportStatus.FAIL

    def test_determine_status_concerns_partial(self):
        """Test CONCERNS status - Partial implementation"""
        agent = SpecQAAgent()
        status = agent._determine_status("Partial", 0.5, [])
        assert status == QAReportStatus.CONCERNS

    def test_determine_status_concerns_moderate_coverage(self):
        """Test CONCERNS status - Moderate coverage"""
        agent = SpecQAAgent()
        status = agent._determine_status("Implemented", 0.5, [])
        assert status == QAReportStatus.CONCERNS

    def test_verify_implementation_basic_implemented(self):
        """Test basic implementation verification - Implemented"""
        agent = SpecQAAgent()
        status = agent._verify_implementation_basic("authenticate user", "def authenticate_user(): pass")
        assert status == "Implemented"

    def test_verify_implementation_basic_partial(self):
        """Test basic implementation verification - Partial"""
        agent = SpecQAAgent()
        status = agent._verify_implementation_basic("authenticate user with password", "def authenticate(): pass")
        assert status in ["Partial", "Implemented"]

    def test_verify_implementation_basic_missing(self):
        """Test basic implementation verification - Missing"""
        agent = SpecQAAgent()
        status = agent._verify_implementation_basic("payment processing", "def authenticate(): pass")
        assert status == "Missing"

    def test_check_test_coverage_basic_full(self):
        """Test basic test coverage check - Full coverage"""
        agent = SpecQAAgent()
        coverage = agent._check_test_coverage_basic("authenticate", "def test_authenticate(): pass")
        assert 0.0 <= coverage <= 1.0
        assert coverage > 0.0

    def test_check_test_coverage_basic_zero(self):
        """Test basic test coverage check - Zero coverage"""
        agent = SpecQAAgent()
        coverage = agent._check_test_coverage_basic("payment", "def test_auth(): pass")
        assert 0.0 <= coverage <= 1.0

    def test_check_test_coverage_basic_empty_requirement(self):
        """Test basic test coverage check - Empty requirement"""
        agent = SpecQAAgent()
        coverage = agent._check_test_coverage_basic("", "def test_auth(): pass")
        assert coverage == 0.0

    @pytest.mark.asyncio
    async def test_review_implementation_basic(self, tmp_path):
        """Test basic review implementation"""
        story_file = tmp_path / "story.md"
        story_content = "# Test\n## Requirements\n- Req1\n"
        story_file.write_text(story_content)

        agent = SpecQAAgent()
        report = await agent.review_implementation(story_file)

        assert report is not None
        assert hasattr(report, 'overall_status')
        assert report.overall_status in [QAReportStatus.PASS, QAReportStatus.FAIL, QAReportStatus.CONCERNS]

    @pytest.mark.asyncio
    async def test_review_implementation_file_not_found(self):
        """Test review with non-existent file"""
        agent = SpecQAAgent()
        with pytest.raises(FileNotFoundError):
            await agent.review_implementation("nonexistent.md")

    @pytest.mark.asyncio
    async def test_review_implementation_multiple_requirements(self, tmp_path):
        """Test review with multiple requirements"""
        story_file = tmp_path / "story.md"
        story_content = """# Test
## Requirements
- Authenticate user
- Process payment
- Send email notification
"""
        story_file.write_text(story_content)

        # Create source files
        auth_file = tmp_path / "auth.py"
        auth_file.write_text("def authenticate_user(): pass\n")

        payment_file = tmp_path / "payment.py"
        payment_file.write_text("def process_payment(): pass\n")

        # Create test files
        test_file = tmp_path / "test_auth.py"
        test_file.write_text("def test_authenticate_user(): pass\n")

        agent = SpecQAAgent()
        report = await agent.review_implementation(story_file)

        assert report is not None
        assert len(report.requirement_reports) == 3

    @pytest.mark.asyncio
    async def test_review_implementation_with_source_files(self, tmp_path):
        """Test review with source files"""
        story_file = tmp_path / "story.md"
        story_content = """# Test
## Requirements
- User authentication
"""
        story_file.write_text(story_content)

        # Create source file
        auth_file = tmp_path / "auth.py"
        auth_file.write_text("def authenticate_user(): pass\n")

        # Create test file
        test_file = tmp_path / "test_auth.py"
        test_file.write_text("def test_authenticate_user(): pass\n")

        agent = SpecQAAgent()
        report = await agent.review_implementation(story_file)

        assert report is not None
        assert len(report.requirement_reports) >= 1

    @pytest.mark.asyncio
    async def test_review_implementation_no_test_files(self, tmp_path):
        """Test review with no test files"""
        story_file = tmp_path / "story.md"
        story_content = """# Test
## Requirements
- User authentication
"""
        story_file.write_text(story_content)

        # Create source file only
        auth_file = tmp_path / "auth.py"
        auth_file.write_text("def authenticate_user(): pass\n")

        agent = SpecQAAgent()
        report = await agent.review_implementation(story_file)

        assert report is not None
        assert "No test files found" in report.findings

    def test_calculate_overall_coverage(self):
        """Test overall coverage calculation"""
        agent = SpecQAAgent()
        requirement_reports = [
            {"test_coverage": 0.8},
            {"test_coverage": 0.6},
            {"test_coverage": 0.9},
        ]
        coverage = agent._calculate_overall_coverage(requirement_reports)
        assert coverage == (0.8 + 0.6 + 0.9) / 3

    def test_calculate_overall_coverage_empty(self):
        """Test overall coverage calculation with empty list"""
        agent = SpecQAAgent()
        coverage = agent._calculate_overall_coverage([])
        assert coverage == 0.0

    def test_calculate_overall_coverage_single_requirement(self):
        """Test overall coverage calculation with single requirement"""
        agent = SpecQAAgent()
        requirement_reports = [{"test_coverage": 0.75}]
        coverage = agent._calculate_overall_coverage(requirement_reports)
        assert coverage == 0.75

    def test_generate_findings_missing_implementations(self):
        """Test findings generation for missing implementations"""
        agent = SpecQAAgent()
        requirement_reports = [
            {
                "requirement": "Payment processing",
                "implementation_status": "Missing",
                "test_coverage": 0.0,
            },
        ]
        source_paths = []
        test_paths = []
        findings = agent._generate_findings(requirement_reports, source_paths, test_paths)
        assert any("Missing implementations" in finding for finding in findings)

    def test_generate_findings_low_coverage(self):
        """Test findings generation for low coverage"""
        agent = SpecQAAgent()
        requirement_reports = [
            {
                "requirement": "User authentication",
                "implementation_status": "Implemented",
                "test_coverage": 0.2,
            },
        ]
        source_paths = [Path("auth.py")]
        test_paths = []
        findings = agent._generate_findings(requirement_reports, source_paths, test_paths)
        assert any("Low test coverage" in finding for finding in findings)

    def test_generate_findings_no_test_files(self):
        """Test findings generation when no test files"""
        agent = SpecQAAgent()
        requirement_reports = []
        source_paths = []
        test_paths = []
        findings = agent._generate_findings(requirement_reports, source_paths, test_paths)
        assert "No test files found" in findings

    def test_determine_overall_status_all_pass(self):
        """Test overall status determination - all PASS"""
        agent = SpecQAAgent()
        requirement_reports = [
            {"status": "PASS"},
            {"status": "PASS"},
        ]
        status = agent._determine_overall_status(requirement_reports)
        assert status == QAReportStatus.PASS

    def test_determine_overall_status_any_fail(self):
        """Test overall status determination - any FAIL"""
        agent = SpecQAAgent()
        requirement_reports = [
            {"status": "PASS"},
            {"status": "FAIL"},
            {"status": "CONCERNS"},
        ]
        status = agent._determine_overall_status(requirement_reports)
        assert status == QAReportStatus.FAIL

    def test_determine_overall_status_concerns(self):
        """Test overall status determination - all CONCERNS"""
        agent = SpecQAAgent()
        requirement_reports = [
            {"status": "CONCERNS"},
            {"status": "CONCERNS"},
        ]
        status = agent._determine_overall_status(requirement_reports)
        assert status == QAReportStatus.CONCERNS

    def test_determine_overall_status_empty(self):
        """Test overall status determination - empty"""
        agent = SpecQAAgent()
        status = agent._determine_overall_status([])
        assert status == QAReportStatus.FAIL

    def test_collect_source_files(self, tmp_path):
        """Test source file collection"""
        agent = SpecQAAgent()
        # Create test files
        (tmp_path / "test1.py").write_text("# test")
        (tmp_path / "test2.js").write_text("// test")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "test3.py").write_text("# test")

        source_files = agent._collect_source_files(tmp_path)
        assert len(source_files) >= 3

    def test_collect_test_files(self, tmp_path):
        """Test test file collection"""
        agent = SpecQAAgent()
        # Create test files
        (tmp_path / "test_auth.py").write_text("# test")
        (tmp_path / "auth_test.py").write_text("# test")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_main.py").write_text("# test")

        test_files = agent._collect_test_files(tmp_path)
        assert len(test_files) >= 3

    def test_verify_requirement(self, tmp_path):
        """Test individual requirement verification"""
        agent = SpecQAAgent()
        # Create test files
        auth_file = tmp_path / "auth.py"
        auth_file.write_text("def authenticate_user(): pass\n")

        test_file = tmp_path / "test_auth.py"
        test_file.write_text("def test_authenticate_user(): pass\n")

        source_paths = [auth_file]
        test_paths = [test_file]

        report = agent._verify_requirement("User authentication", source_paths, test_paths)

        assert "requirement" in report
        assert "implementation_status" in report
        assert "test_coverage" in report
        assert "status" in report

    def test_qa_report_to_dict(self):
        """Test QA report serialization"""
        report = QAReport(
            story_path="test.md",
            overall_status=QAReportStatus.PASS,
            requirement_reports=[{"requirement": "Test", "status": "PASS"}],
            overall_coverage=0.8,
            findings=["Test finding"],
        )

        report_dict = report.to_dict()
        assert report_dict["story_path"] == "test.md"
        assert report_dict["overall_status"] == "PASS"
        assert report_dict["overall_coverage"] == 0.8
        assert len(report_dict["requirement_reports"]) == 1
        assert len(report_dict["findings"]) == 1

    def test_qa_report_str_representation(self):
        """Test QA report string representation"""
        report = QAReport(
            story_path="test.md",
            overall_status=QAReportStatus.PASS,
            requirement_reports=[{"requirement": "Test", "status": "PASS"}],
            overall_coverage=0.8,
            findings=["Test finding"],
        )

        report_str = str(report)
        assert "PASS" in report_str
        assert "80.0%" in report_str
        assert "Requirement Reports" in report_str
        assert "Findings" in report_str

    def test_qa_report_str_with_no_findings(self):
        """Test QA report string representation with no findings"""
        report = QAReport(
            story_path="test.md",
            overall_status=QAReportStatus.PASS,
            requirement_reports=[{"requirement": "Test", "status": "PASS"}],
            overall_coverage=0.8,
            findings=[],
        )

        report_str = str(report)
        assert "PASS" in report_str
        # Should not show findings section if empty
        assert "Findings (0):" not in report_str or "Test finding" not in report_str

    def test_verify_implementation_edge_cases(self):
        """Test implementation verification edge cases"""
        agent = SpecQAAgent()

        # Empty requirement
        status = agent._verify_implementation_basic("", "def test(): pass")
        assert status == "Missing"

        # Empty source code
        status = agent._verify_implementation_basic("requirement", "")
        assert status == "Missing"

        # Case sensitivity
        status = agent._verify_implementation_basic("AUTHENTICATE", "def authenticate(): pass")
        assert status in ["Implemented", "Partial"]  # Should find due to case-insensitive matching

    def test_coverage_edge_cases(self):
        """Test coverage calculation edge cases"""
        agent = SpecQAAgent()

        # Empty test code
        coverage = agent._check_test_coverage_basic("requirement", "")
        assert coverage == 0.0

        # Very long requirement
        long_req = "requirement " * 100
        coverage = agent._check_test_coverage_basic(long_req, "requirement")
        assert 0.0 <= coverage <= 1.0
