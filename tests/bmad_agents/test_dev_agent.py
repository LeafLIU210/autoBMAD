"""
Tests for DevAgent class.

This module contains unit tests for the Developer (Dev) Agent which
specializes in story development and code implementation.
"""

import pytest
import sys
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Check if bmad_agents module exists
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
bmad_agents_path = src_path / "bmad_agents"
HAS_BMAD_AGENTS = bmad_agents_path.exists()

# Skip all tests if bmad_agents doesn't exist
pytestmark = pytest.mark.skipif(
    not HAS_BMAD_AGENTS,
    reason="bmad_agents module not found - skipping tests"
)

sys.path.insert(0, str(src_path))

if HAS_BMAD_AGENTS:
    from bmad_agents.dev_agent import DevAgent


class TestDevAgent:
    """Test cases for DevAgent class."""

    def test_init(self):
        """Test Dev Agent initialization."""
        with patch('bmad_agents.dev_agent.DevAgent._load_task_guidance'), \
             patch('bmad_agents.dev_agent.DevAgent._init_client'):
            agent = DevAgent()

            assert agent.agent_name == "dev"
            assert agent.task_file == "develop-story.md"

    def test_read_story_file_success(self):
        """Test successful story file reading."""
        with patch('bmad_agents.dev_agent.DevAgent._load_task_guidance'), \
             patch('bmad_agents.dev_agent.DevAgent._init_client'), \
             patch('builtins.open', mock_open(read_data="# Story 1.1: Test Story\n\nContent")):
            agent = DevAgent()

            result = agent.read_story_file("/test/story.md")

            assert result["success"] is True
            assert "file_path" in result
            assert "content" in result

    def test_read_story_file_not_found(self):
        """Test reading story file when it doesn't exist."""
        with patch('bmad_agents.dev_agent.DevAgent._load_task_guidance'), \
             patch('bmad_agents.dev_agent.DevAgent._init_client'), \
             patch('pathlib.Path.exists', return_value=False):
            agent = DevAgent()

            result = agent.read_story_file("/nonexistent/story.md")

            assert result["success"] is False
            assert "Story file not found" in result["error"]

    def test_analyze_tasks_success(self):
        """Test successful task analysis."""
        with patch('bmad_agents.dev_agent.DevAgent._load_task_guidance'), \
             patch('bmad_agents.dev_agent.DevAgent._init_client'):
            agent = DevAgent()

            story_content = """
            - [ ] Task 1: First Task
              - [ ] Subtask 1.1: First subtask
              - [ ] Subtask 1.2: Second subtask
            - [ ] Task 2: Second Task
              - [ ] Subtask 2.1: Third subtask
            """

            result = agent.analyze_tasks(story_content)

            assert result["success"] is True
            assert result["task_count"] == 2
            assert result["total_subtasks"] == 3

    def test_analyze_tasks_no_tasks(self):
        """Test task analysis with no tasks."""
        with patch('bmad_agents.dev_agent.DevAgent._load_task_guidance'), \
             patch('bmad_agents.dev_agent.DevAgent._init_client'):
            agent = DevAgent()

            story_content = "No tasks here"

            result = agent.analyze_tasks(story_content)

            assert result["success"] is True
            assert result["task_count"] == 0
            assert result["total_subtasks"] == 0

    def test_create_source_file_success(self):
        """Test successful source file creation."""
        with patch('bmad_agents.dev_agent.DevAgent._load_task_guidance'), \
             patch('bmad_agents.dev_agent.DevAgent._init_client'), \
             patch('pathlib.Path') as mock_path_class:
            agent = DevAgent()

            # Mock path operations
            mock_path = mock_path_class.return_value
            mock_path.parent.mkdir = Mock()
            mock_open_file = mock_open()

            with patch('builtins.open', mock_open_file):
                result = agent.create_source_file(
                    file_path="test.py",
                    content="# Test content",
                    directory="/test"
                )

            assert result["success"] is True
            assert "file_path" in result

    def test_modify_source_file_success(self):
        """Test successful source file modification."""
        with patch('bmad_agents.dev_agent.DevAgent._load_task_guidance'), \
             patch('bmad_agents.dev_agent.DevAgent._init_client'), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data="Old content")):
            agent = DevAgent()

            result = agent.modify_source_file(
                file_path="/test/file.py",
                old_string="Old content",
                new_string="New content"
            )

            assert result["success"] is True

    def test_modify_source_file_not_found(self):
        """Test modifying file when it doesn't exist."""
        with patch('bmad_agents.dev_agent.DevAgent._load_task_guidance'), \
             patch('bmad_agents.dev_agent.DevAgent._init_client'), \
             patch('pathlib.Path.exists', return_value=False):
            agent = DevAgent()

            result = agent.modify_source_file(
                file_path="/nonexistent/file.py",
                old_string="Old",
                new_string="New"
            )

            assert result["success"] is False
            assert "File not found" in result["error"]

    def test_modify_source_file_string_not_found(self):
        """Test modifying file when old string is not found."""
        with patch('bmad_agents.dev_agent.DevAgent._load_task_guidance'), \
             patch('bmad_agents.dev_agent.DevAgent._init_client'), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data="Different content")):
            agent = DevAgent()

            result = agent.modify_source_file(
                file_path="/test/file.py",
                old_string="Not in file",
                new_string="New"
            )

            assert result["success"] is False
            assert "Old string not found in file" in result["error"]

    def test_create_test_file(self):
        """Test test file creation."""
        with patch('bmad_agents.dev_agent.DevAgent._load_task_guidance'), \
             patch('bmad_agents.dev_agent.DevAgent._init_client'), \
             patch.object(DevAgent, 'create_source_file') as mock_create:
            agent = DevAgent()

            agent.create_test_file("test_example.py", "Test content")

            mock_create.assert_called_once_with(
                file_path="test_example.py",
                content="Test content",
                directory="tests"
            )

    @patch('subprocess.run')
    def test_run_tests_success(self, mock_run):
        """Test successful test execution."""
        with patch('bmad_agents.dev_agent.DevAgent._load_task_guidance'), \
             patch('bmad_agents.dev_agent.DevAgent._init_client'), \
             patch('pathlib.Path.cwd', return_value=Path("/test")):
            agent = DevAgent()

            # Mock successful test run
            mock_run.return_value = Mock(returncode=0, stdout="All tests passed", stderr="")

            result = agent.run_tests()

            assert result["success"] is True
            assert result["passed"] is True

    @patch('subprocess.run')
    def test_run_tests_failure(self, mock_run):
        """Test failed test execution."""
        with patch('bmad_agents.dev_agent.DevAgent._load_task_guidance'), \
             patch('bmad_agents.dev_agent.DevAgent._init_client'), \
             patch('pathlib.Path.cwd', return_value=Path("/test")):
            agent = DevAgent()

            # Mock failed test run
            mock_run.return_value = Mock(returncode=1, stdout="", stderr="Test failed")

            result = agent.run_tests()

            assert result["success"] is True  # Subprocess ran successfully
            assert result["passed"] is False

    @patch('subprocess.run')
    def test_run_type_check_success(self, mock_run):
        """Test successful type check."""
        with patch('bmad_agents.dev_agent.DevAgent._load_task_guidance'), \
             patch('bmad_agents.dev_agent.DevAgent._init_client'), \
             patch('pathlib.Path.cwd', return_value=Path("/test")):
            agent = DevAgent()

            # Mock successful type check
            mock_run.return_value = Mock(returncode=0, stdout="No errors", stderr="")

            result = agent.run_type_check()

            assert result["success"] is True
            assert result["passed"] is True

    @patch('subprocess.run')
    def test_run_type_check_failure(self, mock_run):
        """Test failed type check."""
        with patch('bmad_agents.dev_agent.DevAgent._load_task_guidance'), \
             patch('bmad_agents.dev_agent.DevAgent._init_client'), \
             patch('pathlib.Path.cwd', return_value=Path("/test")):
            agent = DevAgent()

            # Mock failed type check
            mock_run.return_value = Mock(returncode=1, stdout="", stderr="Type error")

            result = agent.run_type_check()

            assert result["success"] is True
            assert result["passed"] is False

    def test_track_file_changes(self):
        """Test file change tracking."""
        with patch('bmad_agents.dev_agent.DevAgent._load_task_guidance'), \
             patch('bmad_agents.dev_agent.DevAgent._init_client'):
            agent = DevAgent()

            result = agent.track_file_changes(
                files_created=["file1.py", "file2.py"],
                files_modified=["file3.py"],
                files_deleted=["file4.py"]
            )

            assert result["success"] is True
            assert len(result["created"]) == 2
            assert len(result["modified"]) == 1
            assert len(result["deleted"]) == 1
            assert result["total_changes"] == 4

    def test_track_file_changes_empty(self):
        """Test file change tracking with no changes."""
        with patch('bmad_agents.dev_agent.DevAgent._load_task_guidance'), \
             patch('bmad_agents.dev_agent.DevAgent._init_client'):
            agent = DevAgent()

            result = agent.track_file_changes()

            assert result["success"] is True
            assert result["total_changes"] == 0

    @pytest.mark.asyncio
    async def test_develop_with_claude_success(self):
        """Test successful development with Claude."""
        with patch('bmad_agents.dev_agent.DevAgent._load_task_guidance'), \
             patch('bmad_agents.dev_agent.DevAgent._init_client'):
            agent = DevAgent()

            # Mock the execute_with_claude method
            with patch.object(agent, 'execute_with_claude') as mock_execute:
                mock_execute.return_value = {
                    "success": True,
                    "content": "Developed code"
                }

                result = await agent.develop_with_claude(
                    story_content="Story content",
                    implementation_notes="Implementation notes"
                )

                assert result["success"] is True
                assert result["content"] == "Developed code"

    def test_repr(self):
        """Test string representation."""
        with patch('bmad_agents.dev_agent.DevAgent._load_task_guidance'), \
             patch('bmad_agents.dev_agent.DevAgent._init_client'):
            agent = DevAgent()

            assert repr(agent) == "DevAgent()"
