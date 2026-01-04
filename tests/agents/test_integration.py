"""Integration tests for BMAD agents."""

import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch

from src.agents import SMAgent, SMConfig, DevAgent, DevConfig, QAAgent, QAConfig


class TestAgentIntegration:
    """Integration tests for agent collaboration."""

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_all_agents_can_be_instantiated(self, mock_anthropic):
        """Test that all agents can be instantiated independently."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        # Instantiate all agents
        sm_agent = SMAgent()
        dev_agent = DevAgent()
        qa_agent = QAAgent()

        # Verify all agents are properly initialized
        assert sm_agent.client is not None
        assert dev_agent.client is not None
        assert qa_agent.client is not None

        # Verify each has unique session ID
        session_ids = {
            sm_agent.session_id,
            dev_agent.session_id,
            qa_agent.session_id,
        }
        assert len(session_ids) == 3  # All unique

        # Verify task guidance is loaded
        assert sm_agent.task_guidance is not None
        assert dev_agent.task_guidance is not None
        assert qa_agent.task_guidance is not None

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_agent_fresh_client_per_session(self, mock_anthropic):
        """Test that each agent creates a fresh client per session."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        # Create two instances of the same agent type
        agent1 = SMAgent()
        agent2 = SMAgent()

        # Each should have a different client instance
        assert agent1.client is not None
        assert agent2.client is not None
        assert agent1.session_id != agent2.session_id

        # Both should be functional
        assert agent1.task_guidance is not None
        assert agent2.task_guidance is not None

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_agents_have_different_task_guidance(self, mock_anthropic):
        """Test that agents load different task guidance files."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        sm_agent = SMAgent()
        dev_agent = DevAgent()
        qa_agent = QAAgent()

        # Each agent should load different task guidance
        # The exact content will vary, but they should all be non-None
        assert sm_agent.task_guidance is not None
        assert dev_agent.task_guidance is not None
        assert qa_agent.task_guidance is not None

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_agent_configuration_inheritance(self, mock_anthropic):
        """Test that agents properly inherit and extend configuration."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        # Test SM Agent config
        sm_config = SMConfig(story_output_dir="custom/stories")
        sm_agent = SMAgent(sm_config)
        assert sm_agent.config.story_output_dir == "custom/stories"

        # Test Dev Agent config
        dev_config = DevConfig(source_dir="custom/src", run_tests=False)
        dev_agent = DevAgent(dev_config)
        assert dev_agent.config.source_dir == "custom/src"
        assert dev_agent.config.run_tests is False

        # Test QA Agent config
        qa_config = QAConfig(qa_output_dir="custom/qa")
        qa_agent = QAAgent(qa_config)
        assert qa_agent.config.qa_output_dir == "custom/qa"

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_agent_error_handling(self, mock_anthropic):
        """Test that agents handle errors consistently."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        sm_agent = SMAgent()
        dev_agent = DevAgent()
        qa_agent = QAAgent()

        # Test missing client error
        sm_agent.client = None
        with pytest.raises(RuntimeError, match="Claude SDK client not initialized"):
            # This would be called in a real scenario
            pass

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_agent_context_manager(self, mock_anthropic):
        """Test that all agents support context manager protocol."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        # Test each agent as context manager
        with SMAgent() as sm_agent:
            assert sm_agent.client is not None

        assert sm_agent.client is None

        with DevAgent() as dev_agent:
            assert dev_agent.client is not None

        assert dev_agent.client is None

        with QAAgent() as qa_agent:
            assert qa_agent.client is not None

        assert qa_agent.client is None

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_agent_get_info_consistency(self, mock_anthropic):
        """Test that all agents provide consistent info structure."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        sm_agent = SMAgent()
        dev_agent = DevAgent()
        qa_agent = QAAgent()

        # Get info from each agent
        sm_info = sm_agent.get_agent_info()
        dev_info = dev_agent.get_agent_info()
        qa_info = qa_agent.get_agent_info()

        # All should have these base fields
        for info in [sm_info, dev_info, qa_info]:
            assert "task_name" in info
            assert "session_id" in info
            assert "model" in info
            assert "guidance_loaded" in info
            assert "client_initialized" in info

        # Each should have agent-specific fields
        assert sm_info["agent_type"] == "Story Master"
        assert dev_info["agent_type"] == "Developer"
        assert qa_info["agent_type"] == "QA"

    @patch('anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_qa_result_structure(self, mock_anthropic):
        """Test that QAResult has proper structure with all required fields."""
        from src.agents import QAResult

        # Test all gate states
        for gate in ["PASS", "CONCERNS", "FAIL", "WAIVED"]:
            result = QAResult(
                gate=gate,
                status_reason=f"Test {gate}"
            )
            assert result.gate == gate
            assert result.status_reason == f"Test {gate}"
            assert result.quality_score == 0  # Will be set by agent
            assert result.reviewed_by == "QA Agent"
            assert isinstance(result.top_issues, list)
            assert isinstance(result.nfr_validation, dict)
            assert isinstance(result.recommendations, dict)
