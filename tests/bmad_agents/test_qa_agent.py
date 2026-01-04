"""
Tests for QAAgent class.

This module contains unit tests for the Quality Assurance (QA) Agent which
specializes in story review and quality gate decisions.
"""

import pytest
import sys
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from bmad_agents.qa_agent import QAAgent, QAResult


class TestQAAgent:
    """Test cases for QAAgent class."""

    def test_init(self):
        """Test QA Agent initialization."""
        with patch('bmad_agents.qa_agent.QAAgent._load_task_guidance'), \
             patch('bmad_agents.qa_agent.QAAgent._init_client'):
            agent = QAAgent()

            assert agent.agent_name == "qa"
            assert agent.task_file == "review-story.md"

    def test_read_story_file_success(self):
        """Test successful story file reading."""
        with patch('bmad_agents.qa_agent.QAAgent._load_task_guidance'), \
             patch('bmad_agents.qa_agent.QAAgent._init_client'), \
             patch('builtins.open', mock_open(read_data="# Story 1.1: Test Story\n\nContent")):
            agent = QAAgent()

            result = agent.read_story_file("/test/story.md")

            assert result["success"] is True
            assert "file_path" in result
            assert "content" in result

    def test_check_test_coverage_success(self):
        """Test successful test coverage check."""
        with patch('bmad_agents.qa_agent.QAAgent._load_task_guidance'), \
             patch('bmad_agents.qa_agent.QAAgent._init_client'), \
             patch('pathlib.Path') as mock_path_class:
            agent = QAAgent()

            # Mock tests directory with files
            mock_path = mock_path_class.return_value
            mock_path.exists.return_value = True
            mock_path.glob.return_value = [Mock(), Mock(), Mock()]  # 3 test files

            story_content = """
            ## Testing
            This story includes testing.
            We use pytest and unit tests.
            """

            result = agent.check_test_coverage(story_content)

            assert result["success"] is True
            assert result["score"] > 0
            assert result["has_testing_section"] is True

    def test_check_test_coverage_no_tests(self):
        """Test test coverage check with no tests."""
        with patch('bmad_agents.qa_agent.QAAgent._load_task_guidance'), \
             patch('bmad_agents.qa_agent.QAAgent._init_client'), \
             patch('pathlib.Path') as mock_path_class:
            agent = QAAgent()

            # Mock tests directory doesn't exist
            mock_path = mock_path_class.return_value
            mock_path.exists.return_value = False

            story_content = "No testing mentioned"

            result = agent.check_test_coverage(story_content)

            assert result["success"] is True
            assert result["adequate"] is False

    def test_run_qa_tests_success(self):
        """Test successful QA test execution."""
        with patch('bmad_agents.qa_agent.QAAgent._load_task_guidance'), \
             patch('bmad_agents.qa_agent.QAAgent._init_client'), \
             patch('pathlib.Path.cwd', return_value=Path("/test")), \
             patch('subprocess.run') as mock_run:
            agent = QAAgent()

            # Mock successful test runs
            mock_run.return_value = Mock(returncode=0, stdout="Success", stderr="")

            result = agent.run_qa_tests()

            assert result["success"] is True
            assert result["all_passed"] is True

    def test_run_qa_tests_failure(self):
        """Test failed QA test execution."""
        with patch('bmad_agents.qa_agent.QAAgent._load_task_guidance'), \
             patch('bmad_agents.qa_agent.QAAgent._init_client'), \
             patch('pathlib.Path.cwd', return_value=Path("/test")), \
             patch('subprocess.run') as mock_run:
            agent = QAAgent()

            # Mock failed test runs
            mock_run.return_value = Mock(returncode=1, stdout="", stderr="Error")

            result = agent.run_qa_tests()

            assert result["success"] is True
            assert result["all_passed"] is False

    def test_assess_code_quality_success(self):
        """Test successful code quality assessment."""
        with patch('bmad_agents.qa_agent.QAAgent._load_task_guidance'), \
             patch('bmad_agents.qa_agent.QAAgent._init_client'):
            agent = QAAgent()

            story_content = """
            ## Testing
            ## Dev Notes
            ## Change Log
            ### File List
            - file1.py
            - file2.py
            """

            result = agent.assess_code_quality(story_content)

            assert result["success"] is True
            assert result["score"] > 0
            assert result["adequate"] is True

    def test_assess_code_quality_poor(self):
        """Test code quality assessment with poor quality."""
        with patch('bmad_agents.qa_agent.QAAgent._load_task_guidance'), \
             patch('bmad_agents.qa_agent.QAAgent._init_client'):
            agent = QAAgent()

            story_content = "Just some basic content without sections"

            result = agent.assess_code_quality(story_content)

            assert result["success"] is True
            assert result["adequate"] is False

    def test_make_qa_decision_pass(self):
        """Test making QA decision with PASS result."""
        with patch('bmad_agents.qa_agent.QAAgent._load_task_guidance'), \
             patch('bmad_agents.qa_agent.QAAgent._init_client'):
            agent = QAAgent()

            test_coverage = {"success": True, "adequate": True, "score": 80}
            qa_tests = {"success": True, "all_passed": True}
            code_quality = {"success": True, "adequate": True, "score": 85}

            result = agent.make_qa_decision(test_coverage, qa_tests, code_quality)

            assert result["success"] is True
            assert result["decision"] == "PASS"

    def test_make_qa_decision_concerns(self):
        """Test making QA decision with CONCERNS result."""
        with patch('bmad_agents.qa_agent.QAAgent._load_task_guidance'), \
             patch('bmad_agents.qa_agent.QAAgent._init_client'):
            agent = QAAgent()

            test_coverage = {"success": True, "adequate": False, "score": 40}
            qa_tests = {"success": True, "all_passed": True}
            code_quality = {"success": True, "adequate": True, "score": 85}

            result = agent.make_qa_decision(test_coverage, qa_tests, code_quality)

            assert result["success"] is True
            assert result["decision"] == "CONCERNS"

    def test_make_qa_decision_fail(self):
        """Test making QA decision with FAIL result."""
        with patch('bmad_agents.qa_agent.QAAgent._load_task_guidance'), \
             patch('bmad_agents.qa_agent.QAAgent._init_client'):
            agent = QAAgent()

            test_coverage = {"success": True, "adequate": True, "score": 80}
            qa_tests = {"success": True, "all_passed": False}
            code_quality = {"success": True, "adequate": True, "score": 85}

            result = agent.make_qa_decision(test_coverage, qa_tests, code_quality)

            assert result["success"] is True
            assert result["decision"] == "FAIL"

    def test_make_qa_decision_waived(self):
        """Test making QA decision with WAIVED result."""
        with patch('bmad_agents.qa_agent.QAAgent._load_task_guidance'), \
             patch('bmad_agents.qa_agent.QAAgent._init_client'):
            agent = QAAgent()

            test_coverage = {"success": True, "adequate": False, "score": 40}
            qa_tests = {"success": True, "all_passed": True}
            code_quality = {"success": True, "adequate": True, "score": 85}

            result = agent.make_qa_decision(
                test_coverage,
                qa_tests,
                code_quality,
                waiver_reason="Accepting risk due to time constraints"
            )

            assert result["success"] is True
            assert result["decision"] == "WAIVED"
            assert result["waiver_reason"] == "Accepting risk due to time constraints"

    def test_generate_qa_report(self):
        """Test QA report generation."""
        with patch('bmad_agents.qa_agent.QAAgent._load_task_guidance'), \
             patch('bmad_agents.qa_agent.QAAgent._init_client'), \
             patch('pathlib.Path') as mock_path_class:
            agent = QAAgent()

            # Mock path
            mock_path = mock_path_class.return_value
            mock_path.name = "test-story.md"

            qa_decision = {
                "decision": "PASS",
                "test_coverage": 85,
                "code_quality": 90,
                "tests_passed": True,
                "reasons": ["All checks passed"]
            }

            result = agent.generate_qa_report("/test/story.md", qa_decision)

            assert result["success"] is True
            assert "report" in result
            assert "PASS" in result["report"]

    def test_extract_file_list(self):
        """Test file list extraction from story content."""
        with patch('bmad_agents.qa_agent.QAAgent._load_task_guidance'), \
             patch('bmad_agents.qa_agent.QAAgent._init_client'):
            agent = QAAgent()

            story_content = """
            ### File List
            - file1.py
            - file2.py
            - file3.py

            ## QA Results
            """

            result = agent._extract_file_list(story_content)

            assert result is not None
            assert len(result) == 3

    def test_extract_file_list_no_section(self):
        """Test file list extraction when no File List section exists."""
        with patch('bmad_agents.qa_agent.QAAgent._load_task_guidance'), \
             patch('bmad_agents.qa_agent.QAAgent._init_client'):
            agent = QAAgent()

            story_content = "No file list section here"

            result = agent._extract_file_list(story_content)

            assert result is None

    @pytest.mark.asyncio
    async def test_review_with_claude_success(self):
        """Test successful review with Claude."""
        with patch('bmad_agents.qa_agent.QAAgent._load_task_guidance'), \
             patch('bmad_agents.qa_agent.QAAgent._init_client'):
            agent = QAAgent()

            # Mock the execute_with_claude method
            with patch.object(agent, 'execute_with_claude') as mock_execute:
                mock_execute.return_value = {
                    "success": True,
                    "content": "QA Review: PASS"
                }

                result = await agent.review_with_claude(
                    story_content="Story content",
                    file_list=["file1.py", "file2.py"]
                )

                assert result["success"] is True
                assert result["content"] == "QA Review: PASS"

    def test_repr(self):
        """Test string representation."""
        with patch('bmad_agents.qa_agent.QAAgent._load_task_guidance'), \
             patch('bmad_agents.qa_agent.QAAgent._init_client'):
            agent = QAAgent()

            assert repr(agent) == "QAAgent()"


class TestQAResult:
    """Test cases for QAResult enum."""

    def test_qa_result_values(self):
        """Test QAResult enum values."""
        assert QAResult.PASS.value == "PASS"
        assert QAResult.CONCERNS.value == "CONCERNS"
        assert QAResult.FAIL.value == "FAIL"
        assert QAResult.WAIVED.value == "WAIVED"

    def test_qa_result_members(self):
        """Test QAResult enum members."""
        assert QAResult.PASS == QAResult.PASS
        assert QAResult.CONCERNS != QAResult.PASS
        assert QAResult.FAIL != QAResult.PASS
        assert QAResult.WAIVED != QAResult.PASS
