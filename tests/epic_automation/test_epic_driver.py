"""
Test Epic Driver - Quality Gates Integration

Tests for the epic driver with quality gates orchestration.
Tests quality gates integration after Dev-QA cycle.
"""

import asyncio
import json
import logging
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, Mock
import sys

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from autoBMAD.epic_automation.epic_driver import (
    EpicDriver,
    QualityGateOrchestrator,
)


class TestQualityGateOrchestrator:
    """Test quality gate orchestrator functionality."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        with tempfile.TemporaryDirectory() as source_dir, \
             tempfile.TemporaryDirectory() as test_dir:
            yield Path(source_dir), Path(test_dir)

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, temp_dirs):
        """Test quality gate orchestrator initialization."""
        source_dir, test_dir = temp_dirs

        orchestrator = QualityGateOrchestrator(
            source_dir=str(source_dir),
            test_dir=str(test_dir),
            skip_quality=False,
            skip_tests=False
        )

        assert orchestrator.source_dir == str(source_dir)
        assert orchestrator.test_dir == str(test_dir)
        assert orchestrator.skip_quality is False
        assert orchestrator.skip_tests is False
        assert orchestrator.results["success"] is True
        assert orchestrator.results["errors"] == []

    @pytest.mark.asyncio
    async def test_orchestrator_initialization_with_skip_flags(self, temp_dirs):
        """Test quality gate orchestrator initialization with skip flags."""
        source_dir, test_dir = temp_dirs

        orchestrator = QualityGateOrchestrator(
            source_dir=str(source_dir),
            test_dir=str(test_dir),
            skip_quality=True,
            skip_tests=True
        )

        assert orchestrator.skip_quality is True
        assert orchestrator.skip_tests is True

    @pytest.mark.asyncio
    async def test_execute_quality_gates_skip_quality(self, temp_dirs):
        """Test quality gates with skip_quality flag."""
        source_dir, test_dir = temp_dirs

        orchestrator = QualityGateOrchestrator(
            source_dir=str(source_dir),
            test_dir=str(test_dir),
            skip_quality=True,
            skip_tests=False
        )

        # Mock the pytest agent
        with patch('autoBMAD.epic_automation.test_automation_agent.TestAutomationAgent') as mock_agent:
            mock_instance = AsyncMock()
            mock_instance.run_test_automation.return_value = {
                "status": "completed",
                "summary": {"passed": 10, "failed": 0}
            }
            mock_agent.return_value = mock_instance

            results = await orchestrator.execute_quality_gates("test_epic")

            assert results["success"] is True
            assert results["ruff"] is None
            assert results["basedpyright"] is None
            assert results["pytest"]["success"] is True

    @pytest.mark.asyncio
    async def test_execute_quality_gates_skip_tests(self, temp_dirs):
        """Test quality gates with skip_tests flag."""
        source_dir, test_dir = temp_dirs

        orchestrator = QualityGateOrchestrator(
            source_dir=str(source_dir),
            test_dir=str(test_dir),
            skip_quality=False,
            skip_tests=True
        )

        # Mock Ruff and Basedpyright agents
        with patch('autoBMAD.epic_automation.quality_agents.RuffAgent') as mock_ruff, \
             patch('autoBMAD.epic_automation.quality_agents.BasedpyrightAgent') as mock_basedpyright:

            mock_ruff_instance = AsyncMock()
            mock_ruff_instance.retry_cycle.return_value = {
                "successful_cycles": 1,
                "total_cycles": 1,
                "total_issues_found": 0
            }
            mock_ruff.return_value = mock_ruff_instance

            mock_basedpyright_instance = AsyncMock()
            mock_basedpyright_instance.retry_cycle.return_value = {
                "successful_cycles": 1,
                "total_cycles": 1,
                "total_issues_found": 0
            }
            mock_basedpyright.return_value = mock_basedpyright_instance

            results = await orchestrator.execute_quality_gates("test_epic")

            assert results["success"] is True
            assert results["ruff"]["success"] is True
            assert results["basedpyright"]["success"] is True
            assert results["pytest"] is None

    @pytest.mark.asyncio
    async def test_execute_quality_gates_all_phases(self, temp_dirs):
        """Test quality gates with all phases enabled."""
        source_dir, test_dir = temp_dirs

        orchestrator = QualityGateOrchestrator(
            source_dir=str(source_dir),
            test_dir=str(test_dir),
            skip_quality=False,
            skip_tests=False
        )

        # Mock all agents
        with patch('autoBMAD.epic_automation.quality_agents.RuffAgent') as mock_ruff, \
             patch('autoBMAD.epic_automation.quality_agents.BasedpyrightAgent') as mock_basedpyright, \
             patch('autoBMAD.epic_automation.test_automation_agent.TestAutomationAgent') as mock_pytest:

            # Setup Ruff mock
            mock_ruff_instance = AsyncMock()
            mock_ruff_instance.retry_cycle.return_value = {
                "successful_cycles": 1,
                "total_cycles": 1,
                "total_issues_found": 0
            }
            mock_ruff.return_value = mock_ruff_instance

            # Setup Basedpyright mock
            mock_basedpyright_instance = AsyncMock()
            mock_basedpyright_instance.retry_cycle.return_value = {
                "successful_cycles": 1,
                "total_cycles": 1,
                "total_issues_found": 0
            }
            mock_basedpyright.return_value = mock_basedpyright_instance

            # Setup Pytest mock
            mock_pytest_instance = AsyncMock()
            mock_pytest_instance.run_test_automation.return_value = {
                "status": "completed",
                "summary": {"passed": 10, "failed": 0}
            }
            mock_pytest.return_value = mock_pytest_instance

            results = await orchestrator.execute_quality_gates("test_epic")

            assert results["success"] is True
            assert results["ruff"]["success"] is True
            assert results["basedpyright"]["success"] is True
            assert results["pytest"]["success"] is True
            assert "total_duration" in results

    @pytest.mark.asyncio
    async def test_execute_quality_gates_ruff_failure(self, temp_dirs):
        """Test quality gates with Ruff failure."""
        source_dir, test_dir = temp_dirs

        orchestrator = QualityGateOrchestrator(
            source_dir=str(source_dir),
            test_dir=str(test_dir),
            skip_quality=False,
            skip_tests=False
        )

        # Mock Ruff to fail
        with patch('autoBMAD.epic_automation.quality_agents.RuffAgent') as mock_ruff:
            mock_ruff_instance = AsyncMock()
            mock_ruff_instance.retry_cycle.return_value = {
                "successful_cycles": 0,
                "total_cycles": 3,
                "total_issues_found": 5
            }
            mock_ruff.return_value = mock_ruff_instance

            results = await orchestrator.execute_quality_gates("test_epic")

            assert results["success"] is False
            assert results["ruff"]["success"] is False
            assert len(results["errors"]) > 0

    @pytest.mark.asyncio
    async def test_execute_quality_gates_basedpyright_failure(self, temp_dirs):
        """Test quality gates with Basedpyright failure."""
        source_dir, test_dir = temp_dirs

        orchestrator = QualityGateOrchestrator(
            source_dir=str(source_dir),
            test_dir=str(test_dir),
            skip_quality=False,
            skip_tests=False
        )

        # Mock Ruff to succeed, Basedpyright to fail
        with patch('autoBMAD.epic_automation.quality_agents.RuffAgent') as mock_ruff, \
             patch('autoBMAD.epic_automation.quality_agents.BasedpyrightAgent') as mock_basedpyright:

            # Ruff succeeds
            mock_ruff_instance = AsyncMock()
            mock_ruff_instance.retry_cycle.return_value = {
                "successful_cycles": 1,
                "total_cycles": 1,
                "total_issues_found": 0
            }
            mock_ruff.return_value = mock_ruff_instance

            # Basedpyright fails
            mock_basedpyright_instance = AsyncMock()
            mock_basedpyright_instance.retry_cycle.return_value = {
                "successful_cycles": 0,
                "total_cycles": 3,
                "total_issues_found": 10
            }
            mock_basedpyright.return_value = mock_basedpyright_instance

            results = await orchestrator.execute_quality_gates("test_epic")

            assert results["success"] is False
            assert results["ruff"]["success"] is True
            assert results["basedpyright"]["success"] is False
            assert len(results["errors"]) > 0

    @pytest.mark.asyncio
    async def test_execute_quality_gates_pytest_failure(self, temp_dirs):
        """Test quality gates with Pytest failure."""
        source_dir, test_dir = temp_dirs

        orchestrator = QualityGateOrchestrator(
            source_dir=str(source_dir),
            test_dir=str(test_dir),
            skip_quality=False,
            skip_tests=False
        )

        # Mock all agents
        with patch('autoBMAD.epic_automation.quality_agents.RuffAgent') as mock_ruff, \
             patch('autoBMAD.epic_automation.quality_agents.BasedpyrightAgent') as mock_basedpyright, \
             patch('autoBMAD.epic_automation.test_automation_agent.TestAutomationAgent') as mock_pytest:

            # Ruff succeeds
            mock_ruff_instance = AsyncMock()
            mock_ruff_instance.retry_cycle.return_value = {
                "successful_cycles": 1,
                "total_cycles": 1,
                "total_issues_found": 0
            }
            mock_ruff.return_value = mock_ruff_instance

            # Basedpyright succeeds
            mock_basedpyright_instance = AsyncMock()
            mock_basedpyright_instance.retry_cycle.return_value = {
                "successful_cycles": 1,
                "total_cycles": 1,
                "total_issues_found": 0
            }
            mock_basedpyright.return_value = mock_basedpyright_instance

            # Pytest fails
            mock_pytest_instance = AsyncMock()
            mock_pytest_instance.run_test_automation.return_value = {
                "status": "failed",
                "summary": {"passed": 5, "failed": 5}
            }
            mock_pytest.return_value = mock_pytest_instance

            results = await orchestrator.execute_quality_gates("test_epic")

            # Pytest failure doesn't halt the pipeline but marks success as False
            assert results["success"] is False
            assert results["ruff"]["success"] is True
            assert results["basedpyright"]["success"] is True
            assert results["pytest"]["success"] is False
            assert len(results["errors"]) > 0

    @pytest.mark.asyncio
    async def test_progress_tracking(self, temp_dirs):
        """Test progress tracking through quality gates."""
        source_dir, test_dir = temp_dirs

        orchestrator = QualityGateOrchestrator(
            source_dir=str(source_dir),
            test_dir=str(test_dir),
            skip_quality=False,
            skip_tests=False
        )

        # Mock all agents
        with patch('autoBMAD.epic_automation.quality_agents.RuffAgent') as mock_ruff, \
             patch('autoBMAD.epic_automation.quality_agents.BasedpyrightAgent') as mock_basedpyright, \
             patch('autoBMAD.epic_automation.test_automation_agent.TestAutomationAgent') as mock_pytest:

            # Setup mocks
            for mock_agent in [mock_ruff, mock_basedpyright]:
                mock_instance = AsyncMock()
                mock_instance.retry_cycle.return_value = {
                    "successful_cycles": 1,
                    "total_cycles": 1,
                    "total_issues_found": 0
                }
                mock_agent.return_value = mock_instance

            mock_pytest_instance = AsyncMock()
            mock_pytest_instance.run_test_automation.return_value = {
                "status": "completed",
                "summary": {"passed": 10, "failed": 0}
            }
            mock_pytest.return_value = mock_pytest_instance

            results = await orchestrator.execute_quality_gates("test_epic")

            # Check progress tracking
            assert "progress" in results
            assert "current_phase" in results["progress"]
            assert "phase_1_ruff" in results["progress"]
            assert "phase_2_basedpyright" in results["progress"]
            assert "phase_3_pytest" in results["progress"]

            # All phases should be completed
            assert results["progress"]["phase_1_ruff"]["status"] == "completed"
            assert results["progress"]["phase_2_basedpyright"]["status"] == "completed"
            assert results["progress"]["phase_3_pytest"]["status"] == "completed"


class TestEpicDriverIntegration:
    """Test Epic Driver integration with quality gates."""

    @pytest.fixture
    def epic_driver(self):
        """Create an EpicDriver instance for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            epic_path = Path(temp_dir) / "test_epic.md"
            epic_path.write_text("# Test Epic\n\n## Stories\n- Story 1: Test Story\n")

            # Mock StateManager to avoid async initialization issues in tests
            with patch('autoBMAD.epic_automation.epic_driver.StateManager'):
                driver = EpicDriver(
                    epic_path=str(epic_path),
                    source_dir=temp_dir,
                    test_dir=temp_dir,
                    skip_quality=True,
                    skip_tests=True
                )

                yield driver

    @pytest.mark.asyncio
    async def test_epic_driver_initialization_with_quality_flags(self):
        """Test EpicDriver initialization with quality gate flags."""
        with tempfile.TemporaryDirectory() as temp_dir:
            epic_path = Path(temp_dir) / "test_epic.md"
            epic_path.write_text("# Test Epic\n\n## Stories\n- Story 1: Test Story\n")

            with patch('autoBMAD.epic_automation.state_manager.StateManager'):
                driver = EpicDriver(
                    epic_path=str(epic_path),
                    source_dir=temp_dir,
                    test_dir=temp_dir,
                    skip_quality=True,
                    skip_tests=True
                )

                assert driver.skip_quality is True
                assert driver.skip_tests is True

    @pytest.mark.asyncio
    async def test_epic_driver_initialization_default_flags(self):
        """Test EpicDriver initialization with default quality gate flags."""
        with tempfile.TemporaryDirectory() as temp_dir:
            epic_path = Path(temp_dir) / "test_epic.md"
            epic_path.write_text("# Test Epic\n\n")

            with patch('autoBMAD.epic_automation.state_manager.StateManager'):
                driver = EpicDriver(
                    epic_path=str(epic_path),
                    source_dir=temp_dir,
                    test_dir=temp_dir
                )

                assert driver.skip_quality is False
                assert driver.skip_tests is False

    @pytest.mark.asyncio
    async def test_run_with_quality_gates(self):
        """Test EpicDriver run with quality gates enabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            epic_path = Path(temp_dir) / "test_epic.md"
            epic_path.write_text("# Test Epic\n\n")

            with patch('autoBMAD.epic_automation.state_manager.StateManager'):
                driver = EpicDriver(
                    epic_path=str(epic_path),
                    source_dir=temp_dir,
                    test_dir=temp_dir,
                    skip_quality=True,
                    skip_tests=True
                )

                # Mock the parse_epic to return empty stories
                driver.parse_epic = AsyncMock(return_value=[])

                # Run the epic driver
                result = await driver.run()

                # Should return False because no stories were found
                assert result is False

    @pytest.mark.asyncio
    async def test_run_with_quality_gates_disabled(self):
        """Test EpicDriver run with quality gates disabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            epic_path = Path(temp_dir) / "test_epic.md"
            epic_path.write_text("# Test Epic\n\n")

            with patch('autoBMAD.epic_automation.state_manager.StateManager'):
                driver = EpicDriver(
                    epic_path=str(epic_path),
                    source_dir=temp_dir,
                    test_dir=temp_dir,
                    skip_quality=True,
                    skip_tests=True
                )

                # Mock the parse_epic to return empty stories
                driver.parse_epic = AsyncMock(return_value=[])

                # Run the epic driver
                result = await driver.run()

                # Should return False because no stories were found
                assert result is False

    def test_cli_argument_parsing(self):
        """Test CLI argument parsing for quality gate flags."""
        import sys
        from unittest.mock import patch

        # Test --skip-quality flag
        with patch.object(sys, 'argv', ['epic_driver.py', 'test.md', '--skip-quality']):
            from autoBMAD.epic_automation.epic_driver import parse_arguments
            args = parse_arguments()
            assert args.skip_quality is True
            assert args.skip_tests is False

        # Test --skip-tests flag
        with patch.object(sys, 'argv', ['epic_driver.py', 'test.md', '--skip-tests']):
            args = parse_arguments()
            assert args.skip_quality is False
            assert args.skip_tests is True

        # Test both flags
        with patch.object(sys, 'argv', ['epic_driver.py', 'test.md', '--skip-quality', '--skip-tests']):
            args = parse_arguments()
            assert args.skip_quality is True
            assert args.skip_tests is True

        # Test no flags (default)
        with patch.object(sys, 'argv', ['epic_driver.py', 'test.md']):
            args = parse_arguments()
            assert args.skip_quality is False
            assert args.skip_tests is False


class TestQualityGateErrorHandling:
    """Test error handling in quality gates."""

    @pytest.mark.asyncio
    async def test_exception_handling_in_quality_gates(self):
        """Test exception handling in quality gates pipeline."""
        with tempfile.TemporaryDirectory() as source_dir, \
             tempfile.TemporaryDirectory() as test_dir:

            orchestrator = QualityGateOrchestrator(
                source_dir=source_dir,
                test_dir=test_dir,
                skip_quality=False,
                skip_tests=False
            )

            # Mock an agent to raise an exception
            with patch('autoBMAD.epic_automation.quality_agents.RuffAgent') as mock_ruff:
                mock_ruff_instance = AsyncMock()
                mock_ruff_instance.retry_cycle.side_effect = Exception("Test exception")
                mock_ruff.return_value = mock_ruff_instance

                results = await orchestrator.execute_quality_gates("test_epic")

                assert results["success"] is False
                assert len(results["errors"]) > 0
                assert "Test exception" in results["errors"][0]

    @pytest.mark.asyncio
    async def test_max_turns_configuration(self):
        """Test that max_turns is properly configured."""
        with tempfile.TemporaryDirectory() as source_dir, \
             tempfile.TemporaryDirectory() as test_dir:

            orchestrator = QualityGateOrchestrator(
                source_dir=source_dir,
                test_dir=test_dir,
                skip_quality=False,
                skip_tests=False
            )

            # Mock the Ruff agent
            with patch('autoBMAD.epic_automation.quality_agents.RuffAgent') as mock_ruff:
                mock_instance = AsyncMock()
                mock_instance.retry_cycle.return_value = {
                    "successful_cycles": 1,
                    "total_cycles": 1
                }
                mock_ruff.return_value = mock_instance

                results = await orchestrator.execute_quality_gates("test_epic")

                # Verify retry_cycle was called
                mock_instance.retry_cycle.assert_called_once()
                call_kwargs = mock_instance.retry_cycle.call_args[1]
                assert "max_cycles" in call_kwargs
                assert call_kwargs["max_cycles"] == 3


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
