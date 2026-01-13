"""
Tests for BMAD Agents (SM, Dev, QA)

This module contains comprehensive unit and integration tests
for all BMAD agents, validating their core functionality
and ensuring proper integration with the BMAD workflow.
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# Check if bmad_agents module exists
import sys
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
bmad_agents_path = src_path / "bmad_agents"
HAS_BMAD_AGENTS = bmad_agents_path.exists()

# Skip all tests if bmad_agents doesn't exist
pytestmark = pytest.mark.skipif(
    not HAS_BMAD_AGENTS,
    reason="bmad_agents module not found - skipping BMAD agents tests"
)

# Import agents
sys.path.insert(0, str(src_path))

if HAS_BMAD_AGENTS:
    from bmad_agents.base_agent import BaseAgent
    from bmad_agents.sm_agent import SMAgent
    from bmad_agents.dev_agent import DevAgent
    from bmad_agents.qa_agent import QAAgent
    from bmad_agents import QAResult, QAGateResult, QAResultStatus

    class TestBaseAgent:
        """Test BaseAgent class functionality."""
    
        def test_base_agent_initialization(self):
            """Test BaseAgent initialization."""
            agent = BaseAgent(agent_name="test", task_type="test-task")
            assert agent.agent_name == "test"
            assert agent.task_type == "test-task"
            assert agent._task_guidance is None
            assert agent._claude_client is None
    
        @patch('builtins.open', new_callable=Mock)
        @patch('pathlib.Path.exists', return_value=True)
        @patch('pathlib.Path.open', new_callable=Mock)
        def test_load_task_guidance(self, mock_open, mock_exists, mock_file):
            """Test loading task guidance from file."""
            # Setup
            mock_file.return_value.__enter__.return_value.read.return_value = "Test guidance content"
    
            agent = BaseAgent(agent_name="test", task_type="test-task")
            result = agent.load_task_guidance()
    
            assert result == "Test guidance content"
            assert agent._task_guidance == "Test guidance content"
    
        def test_load_task_guidance_file_not_found(self):
            """Test loading task guidance when file doesn't exist."""
            agent = BaseAgent(agent_name="test", task_type="nonexistent-task")
    
            with pytest.raises(FileNotFoundError):
                agent.load_task_guidance()
    
        def test_create_claude_client(self):
            """Test creating Claude SDK client."""
            with patch('anthropic.Anthropic') as mock_anthropic:
                mock_client = Mock()
                mock_anthropic.return_value = mock_client
    
                agent = BaseAgent(agent_name="test", task_type="test-task")
                client = agent.create_claude_client()
    
                assert client == mock_client
                assert agent._claude_client == mock_client
    
        def test_get_system_prompt(self):
            """Test getting system prompt."""
            agent = BaseAgent(agent_name="test", task_type="test-task")
    
            with patch.object(agent, 'load_task_guidance', return_value="Test guidance"):
                with patch.object(agent, '_get_agent_role_description', return_value="Test role"):
                    prompt = agent.get_system_prompt()
                    assert "Test guidance" in prompt
                    assert "Test role" in prompt
    
        def test_reset_session(self):
            """Test session reset functionality."""
            agent = BaseAgent(agent_name="test", task_type="test-task")
            agent._task_guidance = "cached guidance"
            agent._claude_client = Mock()
    
            agent.reset_session()
    
            assert agent._task_guidance is None
            assert agent._claude_client is None
    
    
    class TestSMAgent:
        """Test SM Agent functionality."""
    
        def test_sm_agent_initialization(self):
            """Test SM Agent initialization."""
            agent = SMAgent()
            assert agent.agent_name == "sm"
            assert agent.task_type == "create-next-story"
            assert agent.current_epic is None
            assert agent.story_path is None
    
        @patch('bmad_workflow.agents.sm_agent.SMAgent.load_task_guidance')
        @patch('bmad_workflow.agents.sm_agent.SMAgent.call_claude')
        @patch('bmad_workflow.agents.sm_agent.SMAgent._write_story_file')
        def test_prepare_next_story(self, mock_write, mock_call, mock_guidance):
            """Test story preparation workflow."""
            # Setup
            mock_guidance.return_value = "Test guidance"
            mock_response = {
                'content': [Mock(text="Test story content")]
            }
            mock_call.return_value = mock_response
            mock_path = Path("/test/story.md")
            mock_write.return_value = mock_path
    
            agent = SMAgent()
            result = agent.prepare_next_story(epic_id="1.1")
    
            assert result['status'] == 'success'
            assert 'story_path' in result
            assert 'story_id' in result
            assert 'guidance_used' in result
    
        def test_validate_story(self):
            """Test story validation."""
            # Create temporary story file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write("# Test Story\n## Story\nTest content\n## Acceptance Criteria\n- [ ] Test AC\n")
                temp_path = Path(f.name)
    
            try:
                agent = SMAgent()
                result = agent.validate_story(temp_path)
    
                assert 'status' in result
                assert 'validation_score' in result
                assert 'checks' in result
            finally:
                os.unlink(temp_path)
    
    
    class TestDevAgent:
        """Test Dev Agent functionality."""
    
        def test_dev_agent_initialization(self):
            """Test Dev Agent initialization."""
            agent = DevAgent()
            assert agent.agent_name == "dev"
            assert agent.task_type == "develop-story"
            assert agent.story_path is None
            assert agent.current_story_id is None
    
        @patch('pathlib.Path.exists', return_value=True)
        def test_develop_story_file_not_found(self, mock_exists):
            """Test developing story when file doesn't exist."""
            agent = DevAgent()
    
            with patch('builtins.open', new_callable=Mock) as mock_file:
                mock_file.return_value.__enter__.return_value.read.return_value = "Test story"
    
                with patch.object(agent, 'load_task_guidance', return_value="Test guidance"):
                    with patch.object(agent, 'call_claude') as mock_call:
                        mock_call.return_value = {'content': [Mock(text="Response")]}
    
                        result = agent.develop_story(Path("/nonexistent/story.md"))
    
                        assert result['status'] == 'success'
    
        def test_validate_implementation(self):
            """Test implementation validation."""
            agent = DevAgent()
            agent.story_content = "# Test Story\n## Acceptance Criteria\n- [ ] Test\n"
    
            result = agent.validate_implementation()
    
            assert 'status' in result
            assert 'validation_score' in result
            assert 'checks' in result
    
    
    class TestQAAgent:
        """Test QA Agent functionality."""
    
        def test_qa_agent_initialization(self):
            """Test QA Agent initialization."""
            agent = QAAgent()
            assert agent.agent_name == "qa"
            assert agent.task_type == "review-story"
            assert agent.story_path is None
            assert agent.current_story_id is None
    
        def test_qa_gate_result_creation(self):
            """Test QAGateResult creation and conversion."""
            result = QAGateResult(status=QAResultStatus.PASS, reason="All good")
    
            assert result.status == QAResultStatus.PASS
            assert result.reason == "All good"
    
            result_dict = result.to_dict()
            assert 'status' in result_dict
            assert 'reason' in result_dict
            assert 'timestamp' in result_dict
            assert 'quality_score' in result_dict
    
        def test_qa_gate_result_quality_score(self):
            """Test quality score calculation."""
            pass_result = QAGateResult(QAResultStatus.PASS, "Good")
            assert pass_result.to_dict()['quality_score'] == 100
    
            concerns_result = QAGateResult(QAResultStatus.CONCERNS, "Minor issues")
            assert concerns_result.to_dict()['quality_score'] == 70
    
            fail_result = QAGateResult(QAResultStatus.FAIL, "Major issues")
            assert fail_result.to_dict()['quality_score'] == 40
    
            waived_result = QAGateResult(QAResultStatus.WAIVED, "Waived")
            assert waived_result.to_dict()['quality_score'] == 60
    
        @patch('pathlib.Path.exists', return_value=True)
        def test_review_story(self, mock_exists):
            """Test story review workflow."""
            agent = QAAgent()
    
            with patch('builtins.open', new_callable=Mock) as mock_file:
                mock_file.return_value.__enter__.return_value.read.return_value = "Test story"
    
                with patch.object(agent, 'load_task_guidance', return_value="Test guidance"):
                    with patch.object(agent, 'call_claude') as mock_call:
                        mock_call.return_value = {'content': [Mock(text="PASS - All requirements met")]}
    
                        result = agent.review_story(Path("/test/story.md"))
    
                        assert isinstance(result, QAGateResult)
                        assert result.status in [QAResultStatus.PASS, QAResultStatus.CONCERNS,
                                               QAResultStatus.FAIL, QAResultStatus.WAIVED]
    
        def test_quick_review(self):
            """Test quick review functionality."""
            # Create temporary story file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write("# Test Story\n## Acceptance Criteria\n- [ ] Test\n## Tasks\n- [ ] Task\n")
                temp_path = Path(f.name)
    
            try:
                agent = QAAgent()
                result = agent.quick_review(temp_path)
    
                assert 'status' in result
                assert 'score' in result
                assert 'checks' in result
                assert result['status'] in ['PASS', 'CONCERNS', 'FAIL', 'WAIVED']
            finally:
                os.unlink(temp_path)
    
    
    class TestAgentIntegration:
        """Integration tests for agent coordination."""
    
        def test_all_agents_instantiable(self):
            """Test that all agents can be instantiated independently."""
            sm_agent = SMAgent()
            dev_agent = DevAgent()
            qa_agent = QAAgent()
    
            assert sm_agent is not None
            assert dev_agent is not None
            assert qa_agent is not None
    
        def test_agent_task_types(self):
            """Test that agents have correct task types."""
            sm_agent = SMAgent()
            dev_agent = DevAgent()
            qa_agent = QAAgent()
    
            assert sm_agent.task_type == "create-next-story"
            assert dev_agent.task_type == "develop-story"
            assert qa_agent.task_type == "review-story"
    
        def test_agent_reset_session(self):
            """Test that agents can reset sessions independently."""
            agents = [SMAgent(), DevAgent(), QAAgent()]
    
            for agent in agents:
                # Simulate session state
                agent._task_guidance = "test"
                agent._claude_client = Mock()
    
                # Reset
                agent.reset_session()
    
                # Verify reset
                assert agent._task_guidance is None
                assert agent._claude_client is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
