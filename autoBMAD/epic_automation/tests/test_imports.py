"""Tests for epic_automation module."""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestImports:
    """Test that all modules can be imported."""

    def test_import_agents(self):
        """Test importing agents."""
        from autoBMAD.epic_automation.agents.dev_agent import DevAgent
        from autoBMAD.epic_automation.agents.qa_agent import QAAgent
        from autoBMAD.epic_automation.agents.sm_agent import SMAgent

        assert DevAgent is not None
        assert QAAgent is not None
        assert SMAgent is not None

    def test_import_controllers(self):
        """Test importing controllers."""
        from autoBMAD.epic_automation.controllers.devqa_controller import DevQaController
        from autoBMAD.epic_automation.controllers.sm_controller import SMController

        assert DevQaController is not None
        assert SMController is not None

    def test_import_core(self):
        """Test importing core modules."""
        from autoBMAD.epic_automation.core.cancellation_manager import CancellationManager
        from autoBMAD.epic_automation.core.sdk_executor import SDKExecutor
        from autoBMAD.epic_automation.core.sdk_result import SDKErrorType, SDKResult

        assert SDKExecutor is not None
        assert CancellationManager is not None
        assert SDKResult is not None
        assert SDKErrorType is not None


class TestSDKResult:
    """Test SDKResult class."""

    def test_sdk_result_creation(self):
        """Test SDKResult can be created."""
        from autoBMAD.epic_automation.core.sdk_result import SDKResult

        result = SDKResult(
            has_target_result=True,
            cleanup_completed=True,
            duration_seconds=1.5,
            session_id="test-session",
            agent_name="test-agent",
        )

        assert result.has_target_result is True
        assert result.duration_seconds == 1.5

    def test_sdk_result_is_success(self):
        """Test SDKResult.is_success()."""
        from autoBMAD.epic_automation.core.sdk_result import SDKResult

        result = SDKResult(
            has_target_result=True,
            cleanup_completed=True,
            duration_seconds=1.5,
            session_id="test-session",
            agent_name="test-agent",
        )

        assert result.is_success() is True


class TestStateManager:
    """Test StateManager class."""

    def test_state_manager_import(self):
        """Test StateManager can be imported."""
        from autoBMAD.epic_automation.state_manager import StateManager

        assert StateManager is not None


class TestLogManager:
    """Test LogManager class."""

    def test_log_manager_import(self):
        """Test LogManager can be imported."""
        from autoBMAD.epic_automation.log_manager import LogManager

        assert LogManager is not None
