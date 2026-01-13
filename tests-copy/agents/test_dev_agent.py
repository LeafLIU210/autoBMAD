"""Tests for DevAgent class."""

import pytest
import os
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from autoBMAD.epic_automation.agents import DevAgent, DevConfig


class TestDevAgent:
    """Test suite for DevAgent class."""

    def test_dev_config_default(self):
        """Test DevConfig with default values."""
        config = DevConfig()
        assert config.task_name == "develop-story"
        assert config.source_dir == "src"
        assert config.test_dir == "tests"
        assert config.test_framework == "pytest"
        assert config.run_tests is True

    def test_dev_config_custom(self):
        """Test DevConfig with custom values."""
        config = DevConfig(
            source_dir="custom/src",
            test_dir="custom/tests",
            run_tests=False
        )
        assert config.source_dir == "custom/src"
        assert config.test_dir == "custom/tests"
        assert config.run_tests is False

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_dev_agent_initialization(self, mock_anthropic):
        """Test DevAgent initialization."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        agent = DevAgent()

        assert agent.config.task_name == "develop-story"
        assert agent.config.source_dir == "src"
        assert agent.client == mock_client
        assert agent.task_guidance is not None

    @patch('anthropic.Anthropic')
    @patch('builtins.open', mock_open(read_data="# Story Content"))
    @patch('pathlib.Path.exists', return_value=True)
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_implement_story_success(self, mock_file, mock_anthropic):
        """Test successful story implementation."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Implementation code")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        with tempfile.TemporaryDirectory() as tmpdir:
            story_path = Path(tmpdir) / "test-story.md"
            story_path.write_text("# Story Content")

            agent = DevAgent()

            with patch.object(agent, 'task_guidance', "test guidance"):
                result = agent.implement_story(
                    story_path=str(story_path),
                    tasks=["Task 1", "Task 2"],
                    acceptance_criteria=["AC1", "AC2"]
                )

            assert result["status"] == "success"
            assert result["story_path"] == str(story_path)
            assert result["tasks_completed"] == ["Task 1", "Task 2"]
            assert "implementation" in result

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_implement_story_no_client(self, mock_anthropic):
        """Test implement_story raises error when client not initialized."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        agent = DevAgent()
        agent.client = None

        with pytest.raises(RuntimeError, match="Claude SDK client not initialized"):
            agent.implement_story("story.md", ["Task 1"], ["AC1"])

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_write_tests_success(self, mock_anthropic):
        """Test successful test writing."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Test code")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        agent = DevAgent()

        with patch.object(agent, 'task_guidance', "test guidance"):
            result = agent.write_tests(
                test_specs=[{"name": "test_func", "input": "value"}],
                test_type="unit"
            )

        assert result["status"] == "success"
        assert result["test_type"] == "unit"
        assert result["specs_count"] == 1
        assert "tests" in result

    @patch('subprocess.run')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_execute_validations_success(self, mock_run, mock_anthropic):
        """Test successful validation execution."""
        # Mock successful type check
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Type check passed",
            stderr=""
        )

        agent = DevAgent()

        result = agent.execute_validations(
            source_files=["src/test.py"],
            test_files=["tests/test_test.py"]
        )

        assert result["status"] == "success"
        assert "results" in result
        assert result["results"]["source_files"] == ["src/test.py"]
        assert len(result["results"]["validations"]) > 0

    @patch('subprocess.run')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_execute_validations_with_timeout(self, mock_run, mock_anthropic):
        """Test execute_validations handles timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 30)

        agent = DevAgent()

        result = agent.execute_validations(source_files=["src/test.py"])

        assert result["status"] == "success"
        assert len(result["results"]["validations"]) > 0

    @patch('anthropic.Anthropic')
    @patch('builtins.open', mock_open(read_data="# Story Content"))
    @patch('pathlib.Path.exists', return_value=True)
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_update_story_status_success(self, mock_file, mock_anthropic):
        """Test successful story status update."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="# Updated Story Content")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        with tempfile.TemporaryDirectory() as tmpdir:
            story_path = Path(tmpdir) / "test-story.md"
            story_path.write_text("# Story Content")

            agent = DevAgent()

            with patch.object(agent, 'task_guidance', "test guidance"):
                result = agent.update_story_status(
                    story_path=str(story_path),
                    completed_tasks=["Task 1", "Task 2"],
                    file_list=["src/test.py"]
                )

            assert result["status"] == "success"
            assert result["story_path"] == str(story_path)
            assert result["completed_tasks"] == ["Task 1", "Task 2"]
            assert result["file_list"] == ["src/test.py"]

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_update_story_status_file_not_found(self, mock_anthropic):
        """Test update_story_status raises error when file not found."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        agent = DevAgent()

        with pytest.raises(FileNotFoundError):
            agent.update_story_status("nonexistent.md", ["Task 1"], ["file.py"])

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_get_agent_info(self, mock_anthropic):
        """Test get_agent_info returns correct information."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        agent = DevAgent()

        info = agent.get_agent_info()

        assert info["agent_type"] == "Developer"
        assert info["specialization"] == "Story implementation and TDD"
        assert info["source_directory"] == "src"
        assert info["test_directory"] == "tests"
        assert info["test_framework"] == "pytest"
        assert info["task_name"] == "develop-story"
        assert info["guidance_loaded"] is True
