"""Tests for QAAgent class."""

import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from src.agents import QAAgent, QAConfig, QAResult


class TestQAResult:
    """Test suite for QAResult dataclass."""

    def test_qa_result_default(self):
        """Test QAResult with default values."""
        result = QAResult(
            gate="PASS",
            status_reason="All requirements met"
        )
        assert result.gate == "PASS"
        assert result.status_reason == "All requirements met"
        assert result.quality_score == 0
        assert result.reviewed_by == "QA Agent"
        assert result.top_issues == []
        assert result.nfr_validation == {}
        assert result.recommendations == {"immediate": [], "future": []}

    def test_qa_result_custom(self):
        """Test QAResult with custom values."""
        result = QAResult(
            gate="CONCERNS",
            status_reason="Minor issues found",
            quality_score=75,
            reviewed_by="Custom Reviewer",
            top_issues=[{"severity": "medium", "description": "Issue 1"}],
            nfr_validation={"security": "PASS"},
            recommendations={"immediate": ["Fix X"], "future": ["Improve Y"]}
        )
        assert result.gate == "CONCERNS"
        assert result.status_reason == "Minor issues found"
        assert result.quality_score == 75
        assert result.reviewed_by == "Custom Reviewer"
        assert len(result.top_issues) == 1
        assert result.nfr_validation == {"security": "PASS"}
        assert result.recommendations == {"immediate": ["Fix X"], "future": ["Improve Y"]}

    def test_qa_result_post_init(self):
        """Test QAResult initializes empty collections properly."""
        result = QAResult(gate="PASS", status_reason="Test")
        assert result.top_issues is not None
        assert isinstance(result.top_issues, list)
        assert result.nfr_validation is not None
        assert isinstance(result.nfr_validation, dict)
        assert result.recommendations is not None
        assert isinstance(result.recommendations, dict)


class TestQAAgent:
    """Test suite for QAAgent class."""

    def test_qa_config_default(self):
        """Test QAConfig with default values."""
        config = QAConfig()
        assert config.task_name == "review-story"
        assert config.qa_output_dir == "qa"
        assert config.gates_dir == "gates"
        assert config.assessments_dir == "assessments"

    def test_qa_config_custom(self):
        """Test QAConfig with custom values."""
        config = QAConfig(
            qa_output_dir="custom/qa",
            gates_dir="custom/gates"
        )
        assert config.qa_output_dir == "custom/qa"
        assert config.gates_dir == "custom/gates"

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_qa_agent_initialization(self, mock_anthropic):
        """Test QAAgent initialization."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        agent = QAAgent()

        assert agent.config.task_name == "review-story"
        assert agent.config.qa_output_dir == "qa"
        assert agent.client == mock_client
        assert agent.task_guidance is not None

    @patch('anthropic.Anthropic')
    @patch('builtins.open', mock_open(read_data="# Story Content"))
    @patch('pathlib.Path.exists', return_value=True)
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_review_story_success(self, mock_file, mock_anthropic):
        """Test successful story review."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Gate: PASS\nStatus reason: All requirements met")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        with tempfile.TemporaryDirectory() as tmpdir:
            story_path = Path(tmpdir) / "test-story.md"
            story_path.write_text("# Story Content")

            agent = QAAgent()

            with patch.object(agent, 'task_guidance', "test guidance"):
                result = agent.review_story(
                    story_path=str(story_path),
                    file_list=["src/test.py"],
                    test_files=["tests/test_test.py"]
                )

            assert result.gate in ["PASS", "CONCERNS", "FAIL", "WAIVED"]
            assert isinstance(result.status_reason, str)

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_review_story_no_client(self, mock_anthropic):
        """Test review_story raises error when client not initialized."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        agent = QAAgent()
        agent.client = None

        with pytest.raises(RuntimeError, match="Claude SDK client not initialized"):
            agent.review_story("story.md", ["file.py"])

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_review_story_file_not_found(self, mock_anthropic):
        """Test review_story raises error when file not found."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        agent = QAAgent()

        with pytest.raises(FileNotFoundError):
            agent.review_story("nonexistent.md", ["file.py"])

    def test_parse_qa_response_pass(self):
        """Test parsing PASS response."""
        response = "Gate: PASS\nStatus reason: All requirements met"
        result = QAAgent()._parse_qa_response(response)

        assert result.gate == "PASS"
        assert result.status_reason == "All requirements met"

    def test_parse_qa_response_concerns(self):
        """Test parsing CONCERNS response."""
        response = "Gate: CONCERNS\nStatus reason: Minor issues found"
        result = QAAgent()._parse_qa_response(response)

        assert result.gate == "CONCERNS"
        assert result.status_reason == "Minor issues found"

    def test_parse_qa_response_fail(self):
        """Test parsing FAIL response."""
        response = "Gate: FAIL\nStatus reason: Critical issues"
        result = QAAgent()._parse_qa_response(response)

        assert result.gate == "FAIL"
        assert result.status_reason == "Critical issues"

    def test_parse_qa_response_waived(self):
        """Test parsing WAIVED response."""
        response = "Gate: WAIVED\nStatus reason: Issues accepted"
        result = QAAgent()._parse_qa_response(response)

        assert result.gate == "WAIVED"
        assert result.status_reason == "Issues accepted"

    def test_parse_qa_response_invalid(self):
        """Test parsing invalid response returns default."""
        response = "Invalid response format"
        result = QAAgent()._parse_qa_response(response)

        assert result.gate == "CONCERNS"
        assert "Failed to parse" in result.status_reason

    def test_calculate_quality_score(self):
        """Test quality score calculation."""
        agent = QAAgent()

        assert agent._calculate_quality_score("PASS") == 100
        assert agent._calculate_quality_score("CONCERNS") == 75
        assert agent._calculate_quality_score("FAIL") == 50
        assert agent._calculate_quality_score("WAIVED") == 85
        assert agent._calculate_quality_score("UNKNOWN") == 0

    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', mock_open())
    @patch('yaml.dump')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_create_gate_file_success(self, mock_yaml, mock_file, mock_mkdir, mock_anthropic):
        """Test successful gate file creation."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        qa_result = QAResult(gate="PASS", status_reason="All good")

        with tempfile.TemporaryDirectory() as tmpdir:
            config = QAConfig(qa_output_dir=tmpdir)
            agent = QAAgent(config)

            result = agent.create_gate_file(
                qa_result=qa_result,
                epic="1",
                story="1",
                story_title="Test Story",
                story_slug="test-story"
            )

            assert result["status"] == "success"
            assert "gate_file" in result
            assert result["gate"] == "PASS"
            assert result["quality_score"] == 100

    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', side_effect=IOError("Write error"))
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_create_gate_file_io_error(self, mock_file, mock_mkdir, mock_anthropic):
        """Test create_gate_file raises error on IO failure."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        qa_result = QAResult(gate="PASS", status_reason="All good")

        with tempfile.TemporaryDirectory() as tmpdir:
            config = QAConfig(qa_output_dir=tmpdir)
            agent = QAAgent(config)

            with pytest.raises(IOError):
                agent.create_gate_file(qa_result, "1", "1", "Test", "test")

    @patch('anthropic.Anthropic')
    @patch('builtins.open', mock_open(read_data="# Story Content"))
    @patch('builtins.open', mock_open(read_data="# Updated Story"), create=True)
    @patch('pathlib.Path.exists', return_value=True)
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_update_story_qa_section_success(
        self, mock_file, mock_file2, mock_exists, mock_anthropic
    ):
        """Test successful story QA section update."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="# Updated Story Content")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        with tempfile.TemporaryDirectory() as tmpdir:
            story_path = Path(tmpdir) / "test-story.md"
            story_path.write_text("# Story Content")

            agent = QAAgent()

            with patch.object(agent, 'task_guidance', "test guidance"):
                result = agent.update_story_qa_section(
                    story_path=str(story_path),
                    qa_result=QAResult(gate="PASS", status_reason="All good"),
                    refactoring_performed=["Refactored X"]
                )

            assert result["status"] == "success"
            assert result["story_path"] == str(story_path)
            assert result["gate"] == "PASS"

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_update_story_qa_section_file_not_found(self, mock_anthropic):
        """Test update_story_qa_section raises error when file not found."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        agent = QAAgent()

        with pytest.raises(FileNotFoundError):
            agent.update_story_qa_section(
                "nonexistent.md",
                QAResult(gate="PASS", status_reason="All good")
            )

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_get_agent_info(self, mock_anthropic):
        """Test get_agent_info returns correct information."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        agent = QAAgent()

        info = agent.get_agent_info()

        assert info["agent_type"] == "QA"
        assert info["specialization"] == "Test architecture review and quality gates"
        assert info["qa_output_directory"] == "qa"
        assert info["gate_states"] == ["PASS", "CONCERNS", "FAIL", "WAIVED"]
        assert info["task_name"] == "review-story"
        assert info["guidance_loaded"] is True
