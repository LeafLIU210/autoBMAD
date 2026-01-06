"""
Tests for SMAgent class.

This module contains unit tests for the Story Master (SM) Agent which
specializes in story creation and preparation.
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
    from bmad_agents.sm_agent import SMAgent


class TestSMAgent:
    """Test cases for SMAgent class."""

    def test_init(self):
        """Test SM Agent initialization."""
        with patch('bmad_agents.sm_agent.SMAgent._load_task_guidance'), \
             patch('bmad_agents.sm_agent.SMAgent._init_client'):
            agent = SMAgent()

            assert agent.agent_name == "sm"
            assert agent.task_file == "create-next-story.md"

    def test_identify_next_story_no_directory(self):
        """Test identifying next story when directory doesn't exist."""
        with patch('bmad_agents.sm_agent.SMAgent._load_task_guidance'), \
             patch('bmad_agents.sm_agent.SMAgent._init_client'):
            agent = SMAgent()

            result = agent.identify_next_story("/nonexistent/path")

            assert result["success"] is False
            assert "Story directory not found" in result["error"]

    def test_identify_next_story_no_files(self):
        """Test identifying next story when no story files exist."""
        with patch('bmad_agents.sm_agent.SMAgent._load_task_guidance'), \
             patch('bmad_agents.sm_agent.SMAgent._init_client'), \
             patch('pathlib.Path') as mock_path:
            agent = SMAgent()

            # Mock directory and no files
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.glob.return_value = []

            result = agent.identify_next_story("/test/path")

            assert result["success"] is True
            assert result["epic"] == 1
            assert result["story"] == 1
            assert result["is_first"] is True

    def test_identify_next_story_existing_files(self):
        """Test identifying next story when story files exist."""
        with patch('bmad_agents.sm_agent.SMAgent._load_task_guidance'), \
             patch('bmad_agents.sm_agent.SMAgent._init_client'), \
             patch('pathlib.Path') as mock_path_class:
            agent = SMAgent()

            # Mock directory with files
            mock_path = mock_path_class.return_value
            mock_path.exists.return_value = True

            # Mock file list with stories 1.1, 1.2, 1.3
            mock_file1 = Mock()
            mock_file1.stem = "1.1.story"
            mock_file2 = Mock()
            mock_file2.stem = "1.2.story"
            mock_file3 = Mock()
            mock_file3.stem = "1.3.story"

            mock_path.glob.return_value = [mock_file1, mock_file2, mock_file3]

            result = agent.identify_next_story("/test/path")

            assert result["success"] is True
            assert result["epic"] == 1
            assert result["story"] == 4
            assert result["is_first"] is False

    def test_identify_next_story_multiple_epics(self):
        """Test identifying next story across multiple epics."""
        with patch('bmad_agents.sm_agent.SMAgent._load_task_guidance'), \
             patch('bmad_agents.sm_agent.SMAgent._init_client'), \
             patch('pathlib.Path') as mock_path_class:
            agent = SMAgent()

            # Mock directory with files from multiple epics
            mock_path = mock_path_class.return_value
            mock_path.exists.return_value = True

            # Mock file list: 1.1, 1.2, 2.1, 2.2, 2.3
            for i in [1, 2]:
                for j in [1, 2, 3]:
                    if i == 1 and j > 2:
                        continue
                    if i == 2 and j > 3:
                        continue
                    mock_file = Mock()
                    mock_file.stem = f"{i}.{j}.story"
                    mock_path.glob.return_value.append(mock_file)

            mock_path.glob.return_value = [
                Mock(stem="1.1.story"),
                Mock(stem="1.2.story"),
                Mock(stem="2.1.story"),
                Mock(stem="2.2.story"),
                Mock(stem="2.3.story"),
            ]

            result = agent.identify_next_story("/test/path")

            assert result["success"] is True
            assert result["epic"] == 2
            assert result["story"] == 4

    def test_create_story_document_success(self):
        """Test successful story document creation."""
        with patch('bmad_agents.sm_agent.SMAgent._load_task_guidance'), \
             patch('bmad_agents.sm_agent.SMAgent._init_client'), \
             patch('pathlib.Path') as mock_path_class:
            agent = SMAgent()

            # Mock path operations
            mock_path = mock_path_class.return_value
            mock_path.parent.mkdir = Mock()
            mock_open_file = mock_open()

            with patch('builtins.open', mock_open_file):
                result = agent.create_story_document(
                    epic_number=1,
                    story_number=1,
                    story_title="Test Story",
                    story_description="Test description",
                    acceptance_criteria=["Criterion 1", "Criterion 2"],
                    output_path="/test/output"
                )

            assert result["success"] is True
            assert "file_path" in result
            assert result["story_id"] == "1.1"
            assert result["story_slug"] == "test-story"

    def test_create_story_document_error(self):
        """Test story document creation with error."""
        with patch('bmad_agents.sm_agent.SMAgent._load_task_guidance'), \
             patch('bmad_agents.sm_agent.SMAgent._init_client'), \
             patch('pathlib.Path', side_effect=Exception("Path error")):
            agent = SMAgent()

            result = agent.create_story_document(
                epic_number=1,
                story_number=1,
                story_title="Test Story",
                story_description="Test description",
                acceptance_criteria=[],
                output_path="/test/output"
            )

            assert result["success"] is False
            assert "error" in result

    def test_format_acceptance_criteria(self):
        """Test acceptance criteria formatting."""
        with patch('bmad_agents.sm_agent.SMAgent._load_task_guidance'), \
             patch('bmad_agents.sm_agent.SMAgent._init_client'):
            agent = SMAgent()

            criteria = ["Criterion 1", "Criterion 2", "Criterion 3"]
            result = agent._format_acceptance_criteria(criteria)

            assert "- [ ] Criterion 1" in result
            assert "- [ ] Criterion 2" in result
            assert "- [ ] Criterion 3" in result

    def test_format_acceptance_criteria_empty(self):
        """Test acceptance criteria formatting with empty list."""
        with patch('bmad_agents.sm_agent.SMAgent._load_task_guidance'), \
             patch('bmad_agents.sm_agent.SMAgent._init_client'):
            agent = SMAgent()

            result = agent._format_acceptance_criteria([])

            assert result == "- [ ] [Acceptance criteria]"

    @pytest.mark.asyncio
    async def test_prepare_story_with_claude_success(self):
        """Test successful story preparation with Claude."""
        with patch('bmad_agents.sm_agent.SMAgent._load_task_guidance'), \
             patch('bmad_agents.sm_agent.SMAgent._init_client') as mock_init:
            agent = SMAgent()

            # Mock the execute_with_claude method
            with patch.object(agent, 'execute_with_claude') as mock_execute:
                mock_execute.return_value = {
                    "success": True,
                    "content": "Prepared story content"
                }

                result = await agent.prepare_story_with_claude(
                    epic_context="Epic context",
                    requirements="Requirements",
                    additional_context="Additional context"
                )

                assert result["success"] is True
                assert result["content"] == "Prepared story content"

    @pytest.mark.asyncio
    async def test_prepare_story_with_claude_error(self):
        """Test story preparation with Claude when error occurs."""
        with patch('bmad_agents.sm_agent.SMAgent._load_task_guidance'), \
             patch('bmad_agents.sm_agent.SMAgent._init_client'):
            agent = SMAgent()

            # Mock the execute_with_claude method to return error
            with patch.object(agent, 'execute_with_claude') as mock_execute:
                mock_execute.return_value = {
                    "success": False,
                    "error": "API error"
                }

                result = await agent.prepare_story_with_claude(
                    epic_context="Epic context",
                    requirements="Requirements"
                )

                assert result["success"] is False
                assert "error" in result

    def test_repr(self):
        """Test string representation."""
        with patch('bmad_agents.sm_agent.SMAgent._load_task_guidance'), \
             patch('bmad_agents.sm_agent.SMAgent._init_client'):
            agent = SMAgent()

            assert repr(agent) == "SMAgent()"
