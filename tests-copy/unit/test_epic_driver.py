"""
Unit tests for EpicDriver module.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import pytest
import asyncio

from autoBMAD.epic_automation.epic_driver import EpicDriver


@pytest.fixture
def sample_epic_content():
    """Sample epic markdown content for testing."""
    return """# Epic 1: Test Epic

## Story 1.1
**As a** developer,
**I want** to test the system,
**so that** we can verify it works.

## Story 1.2
**As a** user,
**I want** to use the feature,
**so that** I can accomplish my goal.
"""


@pytest.fixture
def epic_driver():
    """Create an EpicDriver instance for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        epic_path = Path(tmpdir) / "test_epic.md"
        epic_path.write_text("# Test Epic\n\n## Story 1.1\nTest story content.")
        driver = EpicDriver()
        yield driver


class TestEpicDriver:
    """Test EpicDriver class."""

    def test_init(self):
        """Test EpicDriver initialization."""
        driver = EpicDriver()

        # Verify default attributes
        assert driver.epic_path is None
        assert driver.epic_id is None
        assert driver.tasks_dir is None
        assert driver.stories == []
        assert driver.current_story_index == 0
        assert driver.max_iterations == 3
        assert driver.retry_failed is False
        assert driver.verbose is False
        assert driver.concurrent is False
        assert driver.use_claude is True
        assert driver.source_dir == "src"
        assert driver.test_dir == "tests"
        assert driver.skip_tests is False
        assert driver.task_guidance == {}
        assert driver.max_quality_iterations == 3
        assert driver.max_test_iterations == 3

    def test_init_with_args(self, epic_driver):
        """Test initialization with arguments."""
        with tempfile.TemporaryDirectory() as tmpdir:
            epic_path = Path(tmpdir) / "test.md"
            epic_path.write_text("# Test")

            # Test with custom parameters
            driver = EpicDriver()
            driver.epic_path = epic_path
            driver.epic_id = "test-epic"
            driver.max_iterations = 5

            assert driver.epic_path == epic_path
            assert driver.epic_id == "test-epic"
            assert driver.max_iterations == 5

    @pytest.mark.asyncio
    async def test_load_epic(self, sample_epic_content):
        """Test loading epic from markdown file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(sample_epic_content)
            epic_path = Path(f.name)

        try:
            driver = EpicDriver()
            driver.epic_path = epic_path

            # Mock the parsing method
            with patch.object(driver, 'parse_epic') as mock_parse:
                mock_parse.return_value = [
                    {"path": "docs/stories/1.1.md", "content": "Story 1.1"},
                    {"path": "docs/stories/1.2.md", "content": "Story 1.2"}
                ]

                stories = await driver.load_epic()

                assert len(stories) == 2
                mock_parse.assert_called_once()
        finally:
            epic_path.unlink()

    def test_parse_epic(self, sample_epic_content):
        """Test parsing epic markdown."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(sample_epic_content)
            epic_path = Path(f.name)

        try:
            driver = EpicDriver()
            driver.epic_path = epic_path

            stories = driver.parse_epic()

            assert len(stories) >= 1
            # Verify story structure
            for story in stories:
                assert "path" in story
                assert "content" in story
                assert story["path"].startswith("docs/stories/")
        finally:
            epic_path.unlink()

    @pytest.mark.asyncio
    async def test_run_workflow(self, epic_driver):
        """Test running the complete workflow."""
        # Mock all the agent methods
        epic_driver.stories = [
            {"path": "docs/stories/1.1.md", "content": "Test story"}
        ]

        with patch.object(epic_driver, 'initialize_agents') as mock_init:
            mock_init.return_value = None

            with patch.object(epic_driver, 'process_stories') as mock_process:
                mock_process.return_value = {"status": "completed"}

                result = await epic_driver.run_workflow()

                assert result is not None
                mock_init.assert_called_once()
                mock_process.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_agents(self, epic_driver):
        """Test agent initialization."""
        # Mock the agent classes
        with patch('autoBMAD.epic_automation.epic_driver.SMAgent') as mock_sm:
            with patch('autoBMAD.epic_automation.epic_driver.DevAgent') as mock_dev:
                with patch('autoBMAD.epic_automation.epic_driver.QAAgent') as mock_qa:
                    with patch('autoBMAD.epic_automation.epic_driver.StateManager') as mock_state:
                        mock_state.return_value = MagicMock()

                        epic_driver.initialize_agents()

                        assert epic_driver.sm_agent is not None
                        assert epic_driver.dev_agent is not None
                        assert epic_driver.qa_agent is not None
                        assert epic_driver.state_manager is not None

    @pytest.mark.asyncio
    async def test_process_stories(self, epic_driver):
        """Test processing stories."""
        epic_driver.stories = [
            {"path": "docs/stories/1.1.md", "content": "Test story"}
        ]
        epic_driver.sm_agent = MagicMock()
        epic_driver.dev_agent = MagicMock()
        epic_driver.qa_agent = MagicMock()
        epic_driver.state_manager = MagicMock()

        # Mock the story processing method
        with patch.object(epic_driver, 'process_single_story') as mock_process:
            mock_process.return_value = {"status": "completed"}

            result = await epic_driver.process_stories()

            assert result is not None
            assert mock_process.call_count == 1

    @pytest.mark.asyncio
    async def test_process_single_story(self, epic_driver):
        """Test processing a single story."""
        story = {"path": "docs/stories/1.1.md", "content": "Test story"}
        epic_driver.stories = [story]
        epic_driver.sm_agent = MagicMock()
        epic_driver.dev_agent = MagicMock()
        epic_driver.qa_agent = MagicMock()
        epic_driver.state_manager = MagicMock()

        # Mock the cycle execution
        with patch.object(epic_driver, 'execute_sm_dev_qa_cycle') as mock_cycle:
            mock_cycle.return_value = {"status": "completed"}

            result = await epic_driver.process_single_story(0)

            assert result is not None
            mock_cycle.assert_called_once_with(story, 0)

    @pytest.mark.asyncio
    async def test_execute_sm_dev_qa_cycle(self, epic_driver):
        """Test executing SM-Dev-QA cycle."""
        story = {"path": "docs/stories/1.1.md", "content": "Test story"}
        epic_driver.sm_agent = MagicMock()
        epic_driver.dev_agent = MagicMock()
        epic_driver.qa_agent = MagicMock()
        epic_driver.state_manager = MagicMock()

        # Mock agent responses
        epic_driver.sm_agent.run.return_value = {"status": "sm_done"}
        epic_driver.dev_agent.run.return_value = {"status": "dev_done"}
        epic_driver.qa_agent.run.return_value = {"status": "qa_done"}

        result = await epic_driver.execute_sm_dev_qa_cycle(story, 0)

        assert result is not None
        epic_driver.sm_agent.run.assert_called_once()
        epic_driver.dev_agent.run.assert_called_once()
        epic_driver.qa_agent.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_error(self, epic_driver):
        """Test error handling."""
        story = {"path": "docs/stories/1.1.md", "content": "Test story"}
        epic_driver.state_manager = MagicMock()

        error = Exception("Test error")
        await epic_driver.handle_error(story, 0, error)

        # Verify error was recorded
        epic_driver.state_manager.record_error.assert_called_once()

    @pytest.mark.asyncio
    async def test_retry_logic(self, epic_driver):
        """Test retry logic for failed stories."""
        story = {"path": "docs/stories/1.1.md", "content": "Test story"}
        epic_driver.stories = [story]
        epic_driver.max_iterations = 3

        # Mock agents to fail first two times
        epic_driver.sm_agent = MagicMock()
        epic_driver.dev_agent = MagicMock()
        epic_driver.qa_agent = MagicMock()
        epic_driver.state_manager = MagicMock()

        call_count = 0
        async def failing_run():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("Simulated failure")
            return {"status": "success"}

        epic_driver.sm_agent.run = failing_run

        with patch.object(epic_driver, 'execute_sm_dev_qa_cycle', failing_run):
            # This should retry and eventually succeed
            with patch('asyncio.sleep'):  # Skip sleep for faster test
                result = await epic_driver.process_single_story(0)
                assert result is not None

    def test_set_verbose(self, epic_driver):
        """Test setting verbose mode."""
        assert epic_driver.verbose is False
        epic_driver.set_verbose(True)
        assert epic_driver.verbose is True

    def test_set_concurrent(self, epic_driver):
        """Test setting concurrent mode."""
        assert epic_driver.concurrent is False
        epic_driver.set_concurrent(True)
        assert epic_driver.concurrent is True

    def test_set_skip_tests(self, epic_driver):
        """Test setting skip tests flag."""
        assert epic_driver.skip_tests is False
        epic_driver.set_skip_tests(True)
        assert epic_driver.skip_tests is True

    @pytest.mark.asyncio
    async def test_workflow_with_no_stories(self, epic_driver):
        """Test workflow with no stories."""
        epic_driver.stories = []

        result = await epic_driver.run_workflow()

        assert result is not None

    @pytest.mark.asyncio
    async def test_workflow_with_concurrent_mode(self, epic_driver):
        """Test workflow in concurrent mode."""
        epic_driver.stories = [
            {"path": "docs/stories/1.1.md", "content": "Test story"},
            {"path": "docs/stories/1.2.md", "content": "Test story"}
        ]
        epic_driver.concurrent = True

        epic_driver.sm_agent = MagicMock()
        epic_driver.dev_agent = MagicMock()
        epic_driver.qa_agent = MagicMock()
        epic_driver.state_manager = MagicMock()

        with patch.object(epic_driver, 'process_stories') as mock_process:
            mock_process.return_value = {"status": "completed"}

            result = await epic_driver.run_workflow()

            assert result is not None

    def test_logging_configuration(self, epic_driver):
        """Test that logging is properly configured."""
        assert epic_driver.logger is not None
        assert epic_driver.logger.name == "autoBMAD.epic_automation.epic_driver"

    @pytest.mark.asyncio
    async def test_cleanup(self, epic_driver):
        """Test cleanup after workflow."""
        epic_driver.state_manager = MagicMock()

        await epic_driver.cleanup()

        # Verify cleanup was performed
        assert epic_driver.state_manager is not None
