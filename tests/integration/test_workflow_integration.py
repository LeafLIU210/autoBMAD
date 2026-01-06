"""
Integration tests for workflow components.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import pytest

from autoBMAD.epic_automation.state_manager import StateManager, StoryStatus
from autoBMAD.epic_automation.sm_agent import SMAgent
from autoBMAD.epic_automation.dev_agent import DevAgent
from autoBMAD.epic_automation.qa_agent import QAAgent
from autoBMAD.epic_automation.epic_driver import EpicDriver


@pytest.fixture
def temp_project():
    """Create a temporary project structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create directory structure
        (project_root / "docs" / "stories").mkdir(parents=True)
        (project_root / "src").mkdir(parents=True)
        (project_root / "tests").mkdir(parents=True)

        yield project_root


@pytest.fixture
def sample_story():
    """Sample story content."""
    return """# Story 1.1: Test Integration

## Status
**Status:** Ready for Development

## Story
**As a** developer,
**I want** to test integration,
**so that** we can verify workflows.

## Acceptance Criteria
1. Integration works
2. Components communicate properly
3. Tests pass

## Tasks / Subtasks
- [ ] Task 1
- [ ] Task 2
"""


class TestWorkflowIntegration:
    """Integration tests for the complete workflow."""

    @pytest.mark.asyncio
    async def test_sm_dev_qa_cycle(self, temp_project, sample_story):
        """Test the complete SM-Dev-QA cycle."""
        # Create state manager
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        state_manager = StateManager(db_path=db_path)

        try:
            # Create agents
            sm_agent = SMAgent(project_root=str(temp_project))
            dev_agent = DevAgent(use_claude=False)
            qa_agent = QAAgent()

            # Add story to state manager
            await state_manager.add_story(
                epic_path="epics/epic-1.md",
                story_path="docs/stories/1.1-test.md",
                status=StoryStatus.PENDING,
                phase="development"
            )

            # Mock the actual implementation
            with patch.object(sm_agent, '_parse_story_metadata') as mock_parse:
                with patch.object(dev_agent, '_execute_development_tasks') as mock_dev:
                    with patch.object(qa_agent, '_perform_validations') as mock_qa:
                        mock_parse.return_value = {"story_id": "1.1", "title": "Test"}
                        mock_dev.return_value = True
                        mock_qa.return_value = {"status": "PASS", "checks": [], "issues": []}

                        # Execute SM phase
                        sm_result = await sm_agent.execute(
                            story_content=sample_story,
                            task_guidance="Test guidance",
                            story_path="docs/stories/1.1-test.md"
                        )

                        # Execute Dev phase
                        dev_result = await dev_agent.execute(
                            story_content=sample_story,
                            task_guidance="Test guidance",
                            story_path="docs/stories/1.1-test.md"
                        )

                        # Execute QA phase
                        qa_result = await qa_agent.execute(
                            story_content=sample_story,
                            story_path="docs/stories/1.1-test.md"
                        )

                        # Verify results
                        assert sm_result is True
                        assert dev_result is True
                        assert qa_result["passed"] is True

        finally:
            # Cleanup
            Path(db_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_state_manager_integration(self, temp_project):
        """Test state manager integration with agents."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        state_manager = StateManager(db_path=db_path)

        try:
            # Add multiple stories
            for i in range(1, 4):
                await state_manager.add_story(
                    epic_path="epics/epic-1.md",
                    story_path=f"docs/stories/1.{i}-test.md",
                    status=StoryStatus.PENDING,
                    phase="development"
                )

            # Update status of one story
            await state_manager.update_story_status(
                "docs/stories/1.2-test.md",
                StoryStatus.IN_PROGRESS
            )

            # Set QA result
            from autoBMAD.epic_automation.state_manager import QAResult
            await state_manager.update_qa_result(
                "docs/stories/1.2-test.md",
                QAResult.PASS
            )

            # Verify state
            all_stories = await state_manager.get_all_stories()
            assert len(all_stories) == 3

            pending_stories = await state_manager.get_stories_by_status(StoryStatus.PENDING)
            assert len(pending_stories) == 2

            in_progress_stories = await state_manager.get_stories_by_status(StoryStatus.IN_PROGRESS)
            assert len(in_progress_stories) == 1

        finally:
            Path(db_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_epic_driver_integration(self, temp_project):
        """Test EpicDriver integration with all components."""
        # Create epic file
        epic_path = temp_project / "epics" / "epic-1.md"
        epic_path.parent.mkdir(parents=True)
        epic_path.write_text("""
# Epic 1

## Story 1.1
Content for story 1.1

## Story 1.2
Content for story 1.2
""")

        # Create story files
        (temp_project / "docs" / "stories").mkdir(parents=True)
        for i in range(1, 3):
            story_file = temp_project / "docs" / "stories" / f"1.{i}-test.md"
            story_file.write_text(f"""
# Story 1.{i}: Test Story

## Status
**Status:** Ready for Development

## Story
Content for story 1.{i}

## Acceptance Criteria
1. Criterion 1
2. Criterion 2
""")

        # Create EpicDriver
        driver = EpicDriver()
        driver.epic_path = epic_path
        driver.epic_id = "epic-1"

        # Mock agent initialization and execution
        with patch.object(driver, 'initialize_agents') as mock_init:
            with patch.object(driver, 'process_stories') as mock_process:
                mock_init.return_value = None
                mock_process.return_value = {"status": "completed"}

                result = await driver.run_workflow()

                assert result is not None
                mock_init.assert_called_once()
                mock_process.assert_called_once()

    @pytest.mark.asyncio
    async def test_agent_coordination(self, temp_project, sample_story):
        """Test coordination between multiple agents."""
        # Create agents
        sm_agent = SMAgent(project_root=str(temp_project))
        dev_agent = DevAgent(use_claude=False)
        qa_agent = QAAgent()

        # Mock the implementations
        with patch.object(sm_agent, '_parse_story_metadata') as mock_parse_sm:
            with patch.object(dev_agent, '_parse_requirements') as mock_parse_dev:
                with patch.object(qa_agent, '_parse_story_for_qa') as mock_parse_qa:
                    # Setup mock returns
                    mock_parse_sm.return_value = {"story_id": "1.1"}
                    mock_parse_dev.return_value = {"story_id": "1.1"}
                    mock_parse_qa.return_value = {"story_id": "1.1"}

                    # Execute all agents
                    sm_result = await sm_agent.execute(sample_story)
                    dev_result = await dev_agent.execute(sample_story)
                    qa_result = await qa_agent.execute(sample_story)

                    # Verify all executed successfully
                    assert sm_result is True
                    assert dev_result is True
                    assert qa_result["passed"] is True

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, temp_project):
        """Test error handling across the workflow."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        state_manager = StateManager(db_path=db_path)

        try:
            # Add story
            await state_manager.add_story(
                epic_path="epics/epic-1.md",
                story_path="docs/stories/1.1-test.md",
                status=StoryStatus.PENDING,
                phase="development"
            )

            # Record error
            await state_manager.record_error(
                "docs/stories/1.1-test.md",
                "Test error message"
            )

            # Verify error was recorded
            story = await state_manager.get_story("docs/stories/1.1-test.md")
            assert story['error_message'] == "Test error message"

        finally:
            Path(db_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_concurrent_story_processing(self, temp_project):
        """Test processing multiple stories concurrently."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        state_manager = StateManager(db_path=db_path)

        try:
            # Add multiple stories
            story_contents = [
                f"# Story 1.{i}\n\nContent for story {i}"
                for i in range(1, 6)
            ]

            # Process stories concurrently
            qa_agent = QAAgent()

            results = await asyncio.gather(*[
                qa_agent.execute(content, story_path=f"docs/stories/1.{i}-test.md")
                for i, content in enumerate(story_contents, 1)
            ])

            # Verify all processed
            assert len(results) == 5
            for result in results:
                assert "passed" in result

        finally:
            Path(db_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_workflow_with_retry(self, temp_project):
        """Test workflow with retry logic."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        state_manager = StateManager(db_path=db_path)

        try:
            # Add story
            await state_manager.add_story(
                epic_path="epics/epic-1.md",
                story_path="docs/stories/1.1-test.md",
                status=StoryStatus.PENDING,
                phase="development"
            )

            # Increment iteration
            await state_manager.increment_iteration("docs/stories/1.1-test.md")
            await state_manager.increment_iteration("docs/stories/1.1-test.md")

            # Verify iterations
            story = await state_manager.get_story("docs/stories/1.1-test.md")
            assert story['iteration'] == 2

        finally:
            Path(db_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_file_system_integration(self, temp_project):
        """Test integration with file system operations."""
        stories_dir = temp_project / "docs" / "stories"
        story_file = stories_dir / "1.1-test.md"

        # Create story file
        story_file.write_text("# Story 1.1\n\nTest content")

        # Verify file exists
        assert story_file.exists()

        # Read and verify content
        content = story_file.read_text()
        assert "Story 1.1" in content

        # Update file
        story_file.write_text("# Story 1.1\n\nUpdated content")

        # Verify update
        updated_content = story_file.read_text()
        assert "Updated content" in updated_content

    @pytest.mark.asyncio
    async def test_workflow_termination(self, temp_project):
        """Test proper cleanup and termination."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        state_manager = StateManager(db_path=db_path)

        try:
            # Add and process story
            await state_manager.add_story(
                epic_path="epics/epic-1.md",
                story_path="docs/stories/1.1-test.md",
                status=StoryStatus.PENDING,
                phase="development"
            )

            # Simulate cleanup
            # (In a real scenario, this would close connections, etc.)
            all_stories = await state_manager.get_all_stories()
            assert len(all_stories) == 1

        finally:
            Path(db_path).unlink(missing_ok=True)
