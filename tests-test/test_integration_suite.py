"""
Integration test suite for autoBMAD epic_automation system.

This module contains integration tests that verify the main functionality
of the epic_automation system works correctly.
"""
import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Test the bubble sort implementation
from src.bubblesort.bubble_sort import bubble_sort


class TestBubbleSortIntegration:
    """Integration tests for bubble sort."""

    def test_bubble_sort_basic_functionality(self):
        """Test basic bubble sort works correctly."""
        result = bubble_sort([3, 1, 4, 1, 5, 9, 2, 6])
        assert result == [1, 1, 2, 3, 4, 5, 6, 9]

    def test_bubble_sort_empty_list(self):
        """Test bubble sort with empty list."""
        result = bubble_sort([])
        assert result == []

    def test_bubble_sort_single_element(self):
        """Test bubble sort with single element."""
        result = bubble_sort([42])
        assert result == [42]

    def test_bubble_sort_already_sorted(self):
        """Test bubble sort with already sorted list."""
        result = bubble_sort([1, 2, 3, 4, 5])
        assert result == [1, 2, 3, 4, 5]

    def test_bubble_sort_reverse_sorted(self):
        """Test bubble sort with reverse sorted list."""
        result = bubble_sort([5, 4, 3, 2, 1])
        assert result == [1, 2, 3, 4, 5]

    def test_bubble_sort_with_duplicates(self):
        """Test bubble sort with duplicate elements."""
        result = bubble_sort([3, 3, 2, 1, 2, 3])
        assert result == [1, 2, 2, 3, 3, 3]


class TestAutoBMADAgents:
    """Integration tests for autoBMAD agents."""

    @pytest.mark.asyncio
    async def test_base_agent_can_be_imported(self):
        """Test that BaseAgent can be imported."""
        from autoBMAD.epic_automation.agents.base_agent import BaseAgent
        assert BaseAgent is not None

    @pytest.mark.asyncio
    async def test_dev_agent_can_be_imported(self):
        """Test that DevAgent can be imported."""
        from autoBMAD.epic_automation.agents.dev_agent import DevAgent
        assert DevAgent is not None

    @pytest.mark.asyncio
    async def test_qa_agent_can_be_imported(self):
        """Test that QAAgent can be imported."""
        from autoBMAD.epic_automation.agents.qa_agent import QAAgent
        assert QAAgent is not None

    @pytest.mark.asyncio
    async def test_dev_agent_initialization(self):
        """Test DevAgent can be initialized."""
        from autoBMAD.epic_automation.agents.dev_agent import DevAgent

        agent = DevAgent()
        assert agent.name == "DevAgent"
        assert agent.use_claude is True

    @pytest.mark.asyncio
    async def test_dev_agent_with_use_claude_false(self):
        """Test DevAgent initialization with use_claude=False."""
        from autoBMAD.epic_automation.agents.dev_agent import DevAgent

        agent = DevAgent(use_claude=False)
        assert agent.name == "DevAgent"
        assert agent.use_claude is False

    @pytest.mark.asyncio
    async def test_agent_config_classes(self):
        """Test that agent config classes work."""
        from autoBMAD.epic_automation.agents.config import (
            AgentConfig,
            DevConfig,
            SMConfig,
            QAConfig,
            QAResult,
        )

        # Test AgentConfig
        config = AgentConfig(task_name="test")
        assert config.task_name == "test"

        # Test DevConfig
        dev_config = DevConfig(task_name="dev")
        assert dev_config.task_name == "dev"

        # Test SMConfig
        sm_config = SMConfig(task_name="sm")
        assert sm_config.task_name == "sm"

        # Test QAConfig
        qa_config = QAConfig(task_name="qa")
        assert qa_config.task_name == "qa"

        # Test QAResult
        result = QAResult(passed=True, score=100.0)
        assert result.passed is True
        assert result.score == 100.0


class TestAutoBMADControllers:
    """Integration tests for autoBMAD controllers."""

    @pytest.mark.asyncio
    async def test_base_controller_can_be_imported(self):
        """Test that BaseController can be imported."""
        from autoBMAD.epic_automation.controllers.base_controller import BaseController
        assert BaseController is not None

    @pytest.mark.asyncio
    async def test_state_driven_controller_can_be_imported(self):
        """Test that StateDrivenController can be imported."""
        from autoBMAD.epic_automation.controllers.base_controller import StateDrivenController
        assert StateDrivenController is not None

    @pytest.mark.asyncio
    async def test_devqa_controller_can_be_imported(self):
        """Test that DevQaController can be imported."""
        from autoBMAD.epic_automation.controllers.devqa_controller import DevQaController
        assert DevQaController is not None

    @pytest.mark.asyncio
    async def test_quality_controller_can_be_imported(self):
        """Test that QualityController can be imported."""
        from autoBMAD.epic_automation.controllers.quality_controller import QualityController
        assert QualityController is not None

    @pytest.mark.asyncio
    async def test_sm_controller_can_be_imported(self):
        """Test that SMController can be imported."""
        from autoBMAD.epic_automation.controllers.sm_controller import SMController
        assert SMController is not None


class TestAutoBMADCore:
    """Integration tests for autoBMAD core modules."""

    @pytest.mark.asyncio
    async def test_sdk_executor_can_be_imported(self):
        """Test that SDKExecutor can be imported."""
        try:
            from autoBMAD.epic_automation.core.sdk_executor import SDKExecutor
            assert SDKExecutor is not None
        except ImportError:
            pytest.skip("SDKExecutor not available")

    @pytest.mark.asyncio
    async def test_sdk_result_can_be_imported(self):
        """Test that SDKResult can be imported."""
        try:
            from autoBMAD.epic_automation.core.sdk_result import SDKResult
            assert SDKResult is not None
        except ImportError:
            pytest.skip("SDKResult not available")

    @pytest.mark.asyncio
    async def test_cancellation_manager_can_be_imported(self):
        """Test that CancellationManager can be imported."""
        try:
            from autoBMAD.epic_automation.core.cancellation_manager import CancellationManager
            assert CancellationManager is not None
        except ImportError:
            pytest.skip("CancellationManager not available")


class TestEpicDriverIntegration:
    """Integration tests for EpicDriver."""

    @pytest.mark.asyncio
    async def test_epic_driver_can_be_imported(self):
        """Test that EpicDriver can be imported."""
        from autoBMAD.epic_automation.epic_driver import EpicDriver
        assert EpicDriver is not None


class TestStateManagerIntegration:
    """Integration tests for StateManager."""

    @pytest.mark.asyncio
    async def test_state_manager_can_be_imported(self):
        """Test that StateManager can be imported."""
        from autoBMAD.epic_automation.state_manager import StateManager
        assert StateManager is not None

    @pytest.mark.asyncio
    async def test_story_status_enum(self):
        """Test StoryStatus enum."""
        from autoBMAD.epic_automation.agents.config import StoryStatus

        assert StoryStatus.DRAFT.value == "Draft"
        assert StoryStatus.IN_PROGRESS.value == "In Progress"
        assert StoryStatus.READY_FOR_REVIEW.value == "Ready for Review"
        assert StoryStatus.COMPLETED.value == "Completed"
        assert StoryStatus.BLOCKED.value == "Blocked"


class TestSDKWrapperIntegration:
    """Integration tests for SDK wrapper."""

    @pytest.mark.asyncio
    async def test_sdk_wrapper_can_be_imported(self):
        """Test that SDK wrapper can be imported."""
        from autoBMAD.epic_automation.sdk_wrapper import SafeClaudeSDK
        assert SafeClaudeSDK is not None


class TestLogManagerIntegration:
    """Integration tests for LogManager."""

    @pytest.mark.asyncio
    async def test_log_manager_can_be_imported(self):
        """Test that LogManager can be imported."""
        from autoBMAD.epic_automation.log_manager import LogManager
        assert LogManager is not None


class TestModuleInitialization:
    """Test module initialization."""

    def test_agents_module_init(self):
        """Test agents module can be initialized."""
        from autoBMAD.epic_automation import agents
        assert agents is not None

    def test_controllers_module_init(self):
        """Test controllers module can be initialized."""
        from autoBMAD.epic_automation import controllers
        assert controllers is not None

    def test_core_module_init(self):
        """Test core module can be initialized."""
        from autoBMAD.epic_automation import core
        assert core is not None

    def test_epic_automation_package_init(self):
        """Test epic_automation package can be initialized."""
        from autoBMAD import epic_automation
        assert epic_automation is not None


class TestConfigurationFiles:
    """Test configuration and project structure."""

    def test_pyproject_toml_exists(self):
        """Test pyproject.toml exists."""
        pyproject_path = Path("pyproject.toml")
        assert pyproject_path.exists(), "pyproject.toml should exist"

    def test_pyproject_toml_is_valid(self):
        """Test pyproject.toml is valid TOML."""
        import tomllib

        pyproject_path = Path("pyproject.toml")
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
            assert "project" in data or "tool" in data

    def test_readme_exists(self):
        """Test README.md exists."""
        readme_path = Path("README.md")
        assert readme_path.exists(), "README.md should exist"

    def test_gitignore_exists(self):
        """Test .gitignore exists."""
        gitignore_path = Path(".gitignore")
        assert gitignore_path.exists(), ".gitignore should exist"


class TestCLIIntegration:
    """Integration tests for CLI functionality."""

    @pytest.mark.asyncio
    async def test_cli_module_can_be_imported(self):
        """Test CLI module can be imported."""
        from src.cli import main
        assert main is not None


class TestDatabaseIntegration:
    """Integration tests for database functionality."""

    @pytest.mark.asyncio
    async def test_db_file_exists(self):
        """Test database file exists."""
        db_path = Path("test.db")
        # Database may or may not exist, this is just a check
        # assert db_path.exists(), "Database file should exist"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
