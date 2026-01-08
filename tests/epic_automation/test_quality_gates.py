"""
Unit tests for Quality Gate Orchestration feature (Story 003.4).

Tests cover:
- QualityGateOrchestrator class
- EpicDriver integration with quality gates
- CLI flag handling (--skip-quality, --skip-tests)
- Sequential execution workflow (Ruff → BasedPyright → Pytest)
- Error handling without external timeouts
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from autoBMAD.epic_automation.epic_driver import (
    EpicDriver,
    QualityGateOrchestrator,
    parse_arguments
)


class TestQualityGateOrchestrator:
    """Test suite for QualityGateOrchestrator class."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests"
        )
        assert orchestrator.source_dir == "src"
        assert orchestrator.test_dir == "tests"
        assert orchestrator.skip_quality is False
        assert orchestrator.skip_tests is False

    def test_init_with_skip_flags(self):
        """Test initialization with skip flags."""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests",
            skip_quality=True,
            skip_tests=True
        )
        assert orchestrator.skip_quality is True
        assert orchestrator.skip_tests is True

    @pytest.mark.asyncio
    async def test_execute_ruff_agent_success(self):
        """Test successful Ruff execution."""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests"
        )

        # Mock RuffAgent
        with patch('autoBMAD.epic_automation.quality_agents.RuffAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.retry_cycle = AsyncMock(return_value={
                "successful_cycles": 1,
                "total_cycles": 1
            })
            mock_agent_class.return_value = mock_agent

            result = await orchestrator.execute_ruff_agent("src")

            assert result["success"] is True
            assert "duration" in result

    @pytest.mark.asyncio
    async def test_execute_ruff_agent_skipped(self):
        """Test Ruff execution skipped when skip_quality is True."""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests",
            skip_quality=True
        )

        result = await orchestrator.execute_ruff_agent("src")

        assert result["success"] is True
        assert result["skipped"] is True
        assert "message" in result

    @pytest.mark.asyncio
    async def test_execute_basedpyright_agent_success(self):
        """Test successful Basedpyright execution."""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests"
        )

        # Mock BasedpyrightAgent
        with patch('autoBMAD.epic_automation.quality_agents.BasedpyrightAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.retry_cycle = AsyncMock(return_value={
                "successful_cycles": 1,
                "total_cycles": 1
            })
            mock_agent_class.return_value = mock_agent

            result = await orchestrator.execute_basedpyright_agent("src")

            assert result["success"] is True
            assert "duration" in result

    @pytest.mark.asyncio
    async def test_execute_pytest_agent_success(self):
        """Test successful Pytest execution."""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests"
        )

        # Mock TestAutomationAgent
        with patch('autoBMAD.epic_automation.test_automation_agent.TestAutomationAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.run_test_automation = AsyncMock(return_value={
                "status": "completed"
            })
            mock_agent_class.return_value = mock_agent

            result = await orchestrator.execute_pytest_agent("tests")

            assert result["success"] is True
            assert "duration" in result

    @pytest.mark.asyncio
    async def test_execute_pytest_agent_skipped(self):
        """Test Pytest execution skipped when skip_tests is True."""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests",
            skip_tests=True
        )

        result = await orchestrator.execute_pytest_agent("tests")

        assert result["success"] is True
        assert result["skipped"] is True
        assert "message" in result

    @pytest.mark.asyncio
    async def test_execute_quality_gates_complete_success(self):
        """Test complete quality gates pipeline with success."""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests"
        )

        # Mock all agents
        with patch('autoBMAD.epic_automation.quality_agents.RuffAgent') as mock_ruff_class, \
             patch('autoBMAD.epic_automation.quality_agents.BasedpyrightAgent') as mock_basedpyright_class, \
             patch('autoBMAD.epic_automation.test_automation_agent.TestAutomationAgent') as mock_pytest_class:

            # Setup mocks
            mock_ruff = Mock()
            mock_ruff.retry_cycle = AsyncMock(return_value={"successful_cycles": 1})
            mock_ruff_class.return_value = mock_ruff

            mock_basedpyright = Mock()
            mock_basedpyright.retry_cycle = AsyncMock(return_value={"successful_cycles": 1})
            mock_basedpyright_class.return_value = mock_basedpyright

            mock_pytest = Mock()
            mock_pytest.run_test_automation = AsyncMock(return_value={"status": "completed"})
            mock_pytest_class.return_value = mock_pytest

            result = await orchestrator.execute_quality_gates("test_epic")

            assert result["success"] is True
            assert "ruff" in result
            assert "basedpyright" in result
            assert "pytest" in result
            assert len(result["errors"]) == 0

    @pytest.mark.asyncio
    async def test_execute_quality_gates_with_skips(self):
        """Test quality gates with skip flags."""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests",
            skip_quality=True,
            skip_tests=True
        )

        # Mock TestAutomationAgent (should not be called for skipped phases)
        with patch('autoBMAD.epic_automation.test_automation_agent.TestAutomationAgent') as mock_pytest_class:
            mock_pytest = Mock()
            mock_pytest.run_test_automation = AsyncMock(return_value={"status": "completed"})
            mock_pytest_class.return_value = mock_pytest

            result = await orchestrator.execute_quality_gates("test_epic")

            assert result["success"] is True
            assert result["ruff"]["skipped"] is True
            assert result["basedpyright"]["skipped"] is True
            assert result["pytest"]["skipped"] is True

    @pytest.mark.asyncio
    async def test_execute_quality_gates_ruff_failure(self):
        """Test quality gates pipeline stops on Ruff failure."""
        orchestrator = QualityGateOrchestrator(
            source_dir="src",
            test_dir="tests"
        )

        # Mock RuffAgent to fail
        with patch('autoBMAD.epic_automation.quality_agents.RuffAgent') as mock_ruff_class:
            mock_ruff = Mock()
            mock_ruff.retry_cycle = AsyncMock(return_value={"successful_cycles": 0})
            mock_ruff_class.return_value = mock_ruff

            result = await orchestrator.execute_quality_gates("test_epic")

            assert result["success"] is False
            assert result["ruff"]["success"] is False
            assert result["basedpyright"] is None  # Should not execute

    def test_calculate_duration(self):
        """Test duration calculation."""
        orchestrator = QualityGateOrchestrator("src", "tests")
        start_time = 100.0
        end_time = 105.5
        duration = orchestrator._calculate_duration(start_time, end_time)
        assert duration == 5.5

    def test_update_progress(self):
        """Test progress tracking."""
        orchestrator = QualityGateOrchestrator("src", "tests")
        orchestrator._update_progress("phase_1_ruff", "in_progress", start=True)

        assert orchestrator.results["progress"]["phase_1_ruff"]["status"] == "in_progress"
        assert orchestrator.results["progress"]["phase_1_ruff"]["start_time"] is not None


class TestEpicDriverQualityGates:
    """Test suite for EpicDriver quality gates integration."""

    @pytest.mark.asyncio
    async def test_init(self):
        """Test EpicDriver initialization."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Epic\n")
            temp_path = f.name

        try:
            driver = EpicDriver(temp_path)
            assert driver.epic_path == Path(temp_path).resolve()
            assert driver.max_iterations == 3
            assert driver.retry_failed is False
            assert driver.verbose is False
            assert driver.skip_quality is False
            assert driver.skip_tests is False
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_init_with_quality_flags(self):
        """Test EpicDriver initialization with quality gate flags."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Epic\n")
            temp_path = f.name

        try:
            driver = EpicDriver(
                temp_path,
                skip_quality=True,
                skip_tests=True
            )
            assert driver.skip_quality is True
            assert driver.skip_tests is True
        finally:
            os.unlink(temp_path)


class TestCLIArguments:
    """Test suite for CLI argument parsing."""

    def test_parse_arguments_minimal(self):
        """Test parsing minimal arguments."""
        test_args = ["epic.md"]
        with patch('sys.argv', test_args):
            args = parse_arguments()
            assert args.epic_path == "epic.md"
            assert args.skip_quality is False
            assert args.skip_tests is False

    def test_parse_arguments_skip_quality(self):
        """Test parsing with --skip-quality flag."""
        test_args = ["epic.md", "--skip-quality"]
        with patch('sys.argv', test_args):
            args = parse_arguments()
            assert args.skip_quality is True
            assert args.skip_tests is False

    def test_parse_arguments_skip_tests(self):
        """Test parsing with --skip-tests flag."""
        test_args = ["epic.md", "--skip-tests"]
        with patch('sys.argv', test_args):
            args = parse_arguments()
            assert args.skip_quality is False
            assert args.skip_tests is True

    def test_parse_arguments_both_skips(self):
        """Test parsing with both skip flags."""
        test_args = ["epic.md", "--skip-quality", "--skip-tests"]
        with patch('sys.argv', test_args):
            args = parse_arguments()
            assert args.skip_quality is True
            assert args.skip_tests is True

    def test_parse_arguments_all_options(self):
        """Test parsing with all options."""
        test_args = [
            "epic.md",
            "--max-iterations", "5",
            "--retry-failed",
            "--verbose",
            "--source-dir", "my_src",
            "--test-dir", "my_tests",
            "--skip-quality",
            "--skip-tests"
        ]
        with patch('sys.argv', test_args):
            args = parse_arguments()
            assert args.epic_path == "epic.md"
            assert args.max_iterations == 5
            assert args.retry_failed is True
            assert args.verbose is True
            assert args.source_dir == "my_src"
            assert args.test_dir == "my_tests"
            assert args.skip_quality is True
            assert args.skip_tests is True


class TestEpicDriverIntegration:
    """Integration tests for EpicDriver with quality gates."""

    @pytest.mark.asyncio
    async def test_run_with_quality_gates_success(self):
        """Test complete run with quality gates success."""
        epic_content = """# Test Epic

### Story 1: Test Story 1

**Status**: Ready for Done
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(epic_content)
            temp_path = f.name

        try:
            # Create stories directory
            stories_dir = Path(temp_path).parent / "stories"
            stories_dir.mkdir(exist_ok=True)

            # Create story file
            story_path = stories_dir / "001-Test-Story-1.md"
            story_path.write_text(epic_content)

            driver = EpicDriver(
                temp_path,
                verbose=True,
                skip_quality=False,
                skip_tests=False
            )

            # Mock all agents to avoid actual execution
            with patch.object(driver.sm_agent, 'execute', new_callable=AsyncMock), \
                 patch.object(driver.dev_agent, 'execute', new_callable=AsyncMock) as mock_dev, \
                 patch.object(driver.qa_agent, 'execute', new_callable=AsyncMock) as mock_qa, \
                 patch.object(driver.state_manager, 'update_story_status', new_callable=AsyncMock), \
                 patch.object(driver.state_manager, 'get_story_status', new_callable=AsyncMock) as mock_get_status, \
                 patch('autoBMAD.epic_automation.quality_agents.RuffAgent') as mock_ruff_class, \
                 patch('autoBMAD.epic_automation.quality_agents.BasedpyrightAgent') as mock_basedpyright_class, \
                 patch('autoBMAD.epic_automation.test_automation_agent.TestAutomationAgent') as mock_pytest_class:

                # Setup mocks
                mock_dev.return_value = True
                mock_qa.return_value = {"passed": True}
                mock_get_status.return_value = None

                mock_ruff = Mock()
                mock_ruff.retry_cycle = AsyncMock(return_value={"successful_cycles": 1})
                mock_ruff_class.return_value = mock_ruff

                mock_basedpyright = Mock()
                mock_basedpyright.retry_cycle = AsyncMock(return_value={"successful_cycles": 1})
                mock_basedpyright_class.return_value = mock_basedpyright

                mock_pytest = Mock()
                mock_pytest.run_test_automation = AsyncMock(return_value={"status": "completed"})
                mock_pytest_class.return_value = mock_pytest

                result = await driver.run()

                assert result is True

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            if stories_dir.exists():
                import shutil
                shutil.rmtree(stories_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_run_with_skip_quality(self):
        """Test run with skip quality flag."""
        epic_content = """# Test Epic

### Story 1: Test Story 1

**Status**: Ready for Done
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(epic_content)
            temp_path = f.name

        try:
            driver = EpicDriver(
                temp_path,
                skip_quality=True,
                skip_tests=True
            )

            # Mock state manager
            with patch.object(driver.state_manager, 'update_story_status', new_callable=AsyncMock), \
                 patch.object(driver.state_manager, 'get_story_status', new_callable=AsyncMock) as mock_get_status:

                mock_get_status.return_value = {"status": "completed"}

                result = await driver.run()

                assert result is True

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
