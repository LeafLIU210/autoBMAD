"""
Integration tests for complete 5-phase workflow

Tests cover:
- Complete 5-phase workflow execution
- Backward compatibility
- Skip flags functionality
- Progress tracking accuracy
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import os

# Import the EpicDriver class
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "autoBMAD" / "epic_automation"))

from epic_driver import EpicDriver


@pytest.mark.integration
class TestCompleteWorkflow:
    """Integration tests for complete 5-phase workflow."""

    @pytest.mark.asyncio
    async def test_full_5_phase_workflow(self):
        """Test complete epic with all 5 phases executing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup directories
            epic_path = Path(tmpdir) / "test_epic.md"
            source_dir = Path(tmpdir) / "src"
            test_dir = Path(tmpdir) / "tests"
            stories_dir = Path(tmpdir) / "docs" / "stories"

            source_dir.mkdir()
            test_dir.mkdir()
            stories_dir.mkdir(parents=True)

            # Create epic file
            epic_content = """# Epic: Test Epic

## Stories
- Story 001: Test Story

### Story 001: Test Story
**Story ID**: 001

**As a** developer,
**I want to** test the complete workflow,
**So that** I can verify all phases work correctly.

## Acceptance Criteria
- [ ] Criterion 1

## Tasks / Subtasks
- [ ] Task 1: Test task

## Dev Notes
Implementation notes here.
"""
            epic_path.write_text(epic_content)

            # Create story file
            story_content = """# Story 001: Test Story

**Status**: Approved

## Story
**As a** developer,
**I want to** test the complete workflow,
**So that** I can verify all phases work correctly.

## Acceptance Criteria
- [ ] Criterion 1

## Tasks / Subtasks
- [ ] Task 1: Test task

## Dev Notes
Implementation notes here.
"""
            (stories_dir / "001.md").write_text(story_content)

            # Create dummy source files
            (source_dir / "test_module.py").write_text("def hello(): pass\n")
            (source_dir / "__init__.py").write_text("")

            # Create dummy test files
            (test_dir / "test_sample.py").write_text("def test_sample(): pass\n")

            # Mock all agent classes
            with patch('autoBMAD.epic_automation.sm_agent.SMAgent') as sm_agent_class, \
                 patch('autoBMAD.epic_automation.dev_agent.DevAgent') as dev_agent_class, \
                 patch('autoBMAD.epic_automation.qa_agent.QAAgent') as qa_agent_class:

                # Setup SM agent mock
                sm_agent = AsyncMock()
                sm_agent.execute = AsyncMock(return_value=True)
                sm_agent_class.return_value = sm_agent

                # Setup Dev agent mock
                dev_agent = AsyncMock()
                dev_agent.execute = AsyncMock(return_value=True)
                dev_agent_class.return_value = dev_agent

                # Setup QA agent mock
                qa_agent = AsyncMock()
                qa_agent.execute = AsyncMock(return_value={"passed": True})
                qa_agent_class.return_value = qa_agent

                # Create driver
                driver = EpicDriver(
                    epic_path=str(epic_path),
                    source_dir=str(source_dir),
                    test_dir=str(test_dir),
                    skip_quality=False,
                    skip_tests=False,
                    verbose=True
                )

                # Run the complete workflow
                result = await driver.run()

                # Verify result
                assert result is True

                # Verify all phases were called
                assert sm_agent.execute.called
                assert dev_agent.execute.called
                assert qa_agent.execute.called

    @pytest.mark.asyncio
    async def test_workflow_skip_quality(self):
        """Test workflow with quality gates skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup directories
            epic_path = Path(tmpdir) / "test_epic.md"
            source_dir = Path(tmpdir) / "src"
            test_dir = Path(tmpdir) / "tests"
            stories_dir = Path(tmpdir) / "docs" / "stories"

            source_dir.mkdir()
            test_dir.mkdir()
            stories_dir.mkdir(parents=True)

            # Create epic file
            epic_content = """# Epic: Test Epic

### Story 001: Test Story
**Story ID**: 001
"""
            epic_path.write_text(epic_content)

            # Create story file
            (stories_dir / "001.md").write_text("# Story 001\n")

            # Create dummy files
            (source_dir / "test.py").write_text("pass\n")
            (test_dir / "test_sample.py").write_text("def test_sample(): pass\n")

            # Mock agents
            with patch('autoBMAD.epic_automation.SMAgent') as sm_agent_class, \
                 patch('autoBMAD.epic_automation.DevAgent') as dev_agent_class, \
                 patch('autoBMAD.epic_automation.QAAgent') as qa_agent_class:

                sm_agent = AsyncMock()
                sm_agent.execute = AsyncMock(return_value=True)
                sm_agent_class.return_value = sm_agent

                dev_agent = AsyncMock()
                dev_agent.execute = AsyncMock(return_value=True)
                dev_agent_class.return_value = dev_agent

                qa_agent = AsyncMock()
                qa_agent.execute = AsyncMock(return_value={"passed": True})
                qa_agent_class.return_value = qa_agent

                # Create driver with skip_quality
                driver = EpicDriver(
                    epic_path=str(epic_path),
                    source_dir=str(source_dir),
                    test_dir=str(test_dir),
                    skip_quality=True,
                    skip_tests=False,
                    verbose=True
                )

                result = await driver.run()

                assert result is True

    @pytest.mark.asyncio
    async def test_workflow_skip_tests(self):
        """Test workflow with test automation skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup directories
            epic_path = Path(tmpdir) / "test_epic.md"
            source_dir = Path(tmpdir) / "src"
            test_dir = Path(tmpdir) / "tests"
            stories_dir = Path(tmpdir) / "docs" / "stories"

            source_dir.mkdir()
            test_dir.mkdir()
            stories_dir.mkdir(parents=True)

            # Create epic file
            epic_content = """# Epic: Test Epic

### Story 001: Test Story
**Story ID**: 001
"""
            epic_path.write_text(epic_content)

            # Create story file
            (stories_dir / "001.md").write_text("# Story 001\n")

            # Create dummy files
            (source_dir / "test.py").write_text("pass\n")
            (test_dir / "test_sample.py").write_text("def test_sample(): pass\n")

            # Mock agents
            with patch('autoBMAD.epic_automation.SMAgent') as sm_agent_class, \
                 patch('autoBMAD.epic_automation.DevAgent') as dev_agent_class, \
                 patch('autoBMAD.epic_automation.QAAgent') as qa_agent_class:

                sm_agent = AsyncMock()
                sm_agent.execute = AsyncMock(return_value=True)
                sm_agent_class.return_value = sm_agent

                dev_agent = AsyncMock()
                dev_agent.execute = AsyncMock(return_value=True)
                dev_agent_class.return_value = dev_agent

                qa_agent = AsyncMock()
                qa_agent.execute = AsyncMock(return_value={"passed": True})
                qa_agent_class.return_value = qa_agent

                # Create driver with skip_tests
                driver = EpicDriver(
                    epic_path=str(epic_path),
                    source_dir=str(source_dir),
                    test_dir=str(test_dir),
                    skip_quality=False,
                    skip_tests=True,
                    verbose=True
                )

                result = await driver.run()

                assert result is True

    @pytest.mark.asyncio
    async def test_workflow_skip_both(self):
        """Test workflow with both quality gates and test automation skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup directories
            epic_path = Path(tmpdir) / "test_epic.md"
            source_dir = Path(tmpdir) / "src"
            test_dir = Path(tmpdir) / "tests"
            stories_dir = Path(tmpdir) / "docs" / "stories"

            source_dir.mkdir()
            test_dir.mkdir()
            stories_dir.mkdir(parents=True)

            # Create epic file
            epic_content = """# Epic: Test Epic

### Story 001: Test Story
**Story ID**: 001
"""
            epic_path.write_text(epic_content)

            # Create story file
            (stories_dir / "001.md").write_text("# Story 001\n")

            # Create dummy files
            (source_dir / "test.py").write_text("pass\n")
            (test_dir / "test_sample.py").write_text("def test_sample(): pass\n")

            # Mock agents
            with patch('autoBMAD.epic_automation.SMAgent') as sm_agent_class, \
                 patch('autoBMAD.epic_automation.DevAgent') as dev_agent_class, \
                 patch('autoBMAD.epic_automation.QAAgent') as qa_agent_class:

                sm_agent = AsyncMock()
                sm_agent.execute = AsyncMock(return_value=True)
                sm_agent_class.return_value = sm_agent

                dev_agent = AsyncMock()
                dev_agent.execute = AsyncMock(return_value=True)
                dev_agent_class.return_value = dev_agent

                qa_agent = AsyncMock()
                qa_agent.execute = AsyncMock(return_value={"passed": True})
                qa_agent_class.return_value = qa_agent

                # Create driver with both skip flags
                driver = EpicDriver(
                    epic_path=str(epic_path),
                    source_dir=str(source_dir),
                    test_dir=str(test_dir),
                    skip_quality=True,
                    skip_tests=True,
                    verbose=True
                )

                result = await driver.run()

                assert result is True

    @pytest.mark.asyncio
    async def test_workflow_multiple_stories(self):
        """Test workflow with multiple stories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup directories
            epic_path = Path(tmpdir) / "test_epic.md"
            source_dir = Path(tmpdir) / "src"
            test_dir = Path(tmpdir) / "tests"
            stories_dir = Path(tmpdir) / "docs" / "stories"

            source_dir.mkdir()
            test_dir.mkdir()
            stories_dir.mkdir(parents=True)

            # Create epic file with multiple stories
            epic_content = """# Epic: Test Epic

### Story 001: First Story
**Story ID**: 001

### Story 002: Second Story
**Story ID**: 002

### Story 003: Third Story
**Story ID**: 003
"""
            epic_path.write_text(epic_content)

            # Create story files
            for i in range(1, 4):
                (stories_dir / f"{i:03d}.md").write_text(f"# Story {i:03d}\n")

            # Create dummy files
            (source_dir / "test.py").write_text("pass\n")
            (test_dir / "test_sample.py").write_text("def test_sample(): pass\n")

            # Mock agents
            with patch('autoBMAD.epic_automation.SMAgent') as sm_agent_class, \
                 patch('autoBMAD.epic_automation.DevAgent') as dev_agent_class, \
                 patch('autoBMAD.epic_automation.QAAgent') as qa_agent_class:

                sm_agent = AsyncMock()
                sm_agent.execute = AsyncMock(return_value=True)
                sm_agent_class.return_value = sm_agent

                dev_agent = AsyncMock()
                dev_agent.execute = AsyncMock(return_value=True)
                dev_agent_class.return_value = dev_agent

                qa_agent = AsyncMock()
                qa_agent.execute = AsyncMock(return_value={"passed": True})
                qa_agent_class.return_value = qa_agent

                # Create driver
                driver = EpicDriver(
                    epic_path=str(epic_path),
                    source_dir=str(source_dir),
                    test_dir=str(test_dir),
                    skip_quality=True,
                    skip_tests=True,
                    verbose=True
                )

                result = await driver.run()

                assert result is True
                # Verify all 3 stories were processed
                assert sm_agent.execute.call_count == 3
                assert dev_agent.execute.call_count == 3
                assert qa_agent.execute.call_count == 3

    @pytest.mark.asyncio
    async def test_workflow_qa_failure(self):
        """Test workflow handles QA failure correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup directories
            epic_path = Path(tmpdir) / "test_epic.md"
            source_dir = Path(tmpdir) / "src"
            test_dir = Path(tmpdir) / "tests"
            stories_dir = Path(tmpdir) / "docs" / "stories"

            source_dir.mkdir()
            test_dir.mkdir()
            stories_dir.mkdir(parents=True)

            # Create epic file
            epic_content = """# Epic: Test Epic

### Story 001: Test Story
**Story ID**: 001
"""
            epic_path.write_text(epic_content)

            # Create story file
            (stories_dir / "001.md").write_text("# Story 001\n")

            # Create dummy files
            (source_dir / "test.py").write_text("pass\n")
            (test_dir / "test_sample.py").write_text("def test_sample(): pass\n")

            # Mock agents
            with patch('autoBMAD.epic_automation.SMAgent') as sm_agent_class, \
                 patch('autoBMAD.epic_automation.DevAgent') as dev_agent_class, \
                 patch('autoBMAD.epic_automation.QAAgent') as qa_agent_class:

                sm_agent = AsyncMock()
                sm_agent.execute = AsyncMock(return_value=True)
                sm_agent_class.return_value = sm_agent

                dev_agent = AsyncMock()
                dev_agent.execute = AsyncMock(return_value=True)
                dev_agent_class.return_value = dev_agent

                qa_agent = AsyncMock()
                # QA fails
                qa_agent.execute = AsyncMock(return_value={"passed": False})
                qa_agent_class.return_value = qa_agent

                # Create driver
                driver = EpicDriver(
                    epic_path=str(epic_path),
                    source_dir=str(source_dir),
                    test_dir=str(test_dir),
                    skip_quality=True,
                    skip_tests=True,
                    verbose=True,
                    retry_failed=False  # Don't retry
                )

                result = await driver.run()

                # Should fail due to QA failure
                assert result is False

    @pytest.mark.asyncio
    async def test_workflow_with_retry(self):
        """Test workflow with retry on QA failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup directories
            epic_path = Path(tmpdir) / "test_epic.md"
            source_dir = Path(tmpdir) / "src"
            test_dir = Path(tmpdir) / "tests"
            stories_dir = Path(tmpdir) / "docs" / "stories"

            source_dir.mkdir()
            test_dir.mkdir()
            stories_dir.mkdir(parents=True)

            # Create epic file
            epic_content = """# Epic: Test Epic

### Story 001: Test Story
**Story ID**: 001
"""
            epic_path.write_text(epic_content)

            # Create story file
            (stories_dir / "001.md").write_text("# Story 001\n")

            # Create dummy files
            (source_dir / "test.py").write_text("pass\n")
            (test_dir / "test_sample.py").write_text("def test_sample(): pass\n")

            # Mock agents
            with patch('autoBMAD.epic_automation.SMAgent') as sm_agent_class, \
                 patch('autoBMAD.epic_automation.DevAgent') as dev_agent_class, \
                 patch('autoBMAD.epic_automation.QAAgent') as qa_agent_class:

                sm_agent = AsyncMock()
                sm_agent.execute = AsyncMock(return_value=True)
                sm_agent_class.return_value = sm_agent

                dev_agent = AsyncMock()
                dev_agent.execute = AsyncMock(return_value=True)
                dev_agent_class.return_value = dev_agent

                qa_agent = AsyncMock()
                # First call fails, second call passes
                qa_agent.execute = AsyncMock(side_effect=[
                    {"passed": False},
                    {"passed": True}
                ])
                qa_agent_class.return_value = qa_agent

                # Create driver with retry enabled
                driver = EpicDriver(
                    epic_path=str(epic_path),
                    source_dir=str(source_dir),
                    test_dir=str(test_dir),
                    skip_quality=True,
                    skip_tests=True,
                    verbose=True,
                    retry_failed=True,  # Enable retry
                    max_iterations=3
                )

                result = await driver.run()

                # Should succeed with retry
                assert result is True
                # QA should be called twice
                assert qa_agent.execute.call_count == 2

    @pytest.mark.asyncio
    async def test_progress_tracking_accuracy(self):
        """Test that progress is tracked accurately across phases."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup directories
            epic_path = Path(tmpdir) / "test_epic.md"
            source_dir = Path(tmpdir) / "src"
            test_dir = Path(tmpdir) / "tests"
            stories_dir = Path(tmpdir) / "docs" / "stories"

            source_dir.mkdir()
            test_dir.mkdir()
            stories_dir.mkdir(parents=True)

            # Create epic file
            epic_content = """# Epic: Test Epic

### Story 001: Test Story
**Story ID**: 001
"""
            epic_path.write_text(epic_content)

            # Create story file
            (stories_dir / "001.md").write_text("# Story 001\n")

            # Create dummy files
            (source_dir / "test.py").write_text("pass\n")
            (test_dir / "test_sample.py").write_text("def test_sample(): pass\n")

            # Mock agents
            with patch('autoBMAD.epic_automation.SMAgent') as sm_agent_class, \
                 patch('autoBMAD.epic_automation.DevAgent') as dev_agent_class, \
                 patch('autoBMAD.epic_automation.QAAgent') as qa_agent_class, \
                 patch('autoBMAD.epic_automation.CodeQualityAgent') as quality_agent_class, \
                 patch('autoBMAD.epic_automation.TestAutomationAgent') as test_agent_class:

                sm_agent = AsyncMock()
                sm_agent.execute = AsyncMock(return_value=True)
                sm_agent_class.return_value = sm_agent

                dev_agent = AsyncMock()
                dev_agent.execute = AsyncMock(return_value=True)
                dev_agent_class.return_value = dev_agent

                qa_agent = AsyncMock()
                qa_agent.execute = AsyncMock(return_value={"passed": True})
                qa_agent_class.return_value = qa_agent

                quality_agent = AsyncMock()
                quality_agent.run_quality_gates = AsyncMock(return_value={
                    'status': 'completed',
                    'errors': 0
                })
                quality_agent_class.return_value = quality_agent

                test_agent = AsyncMock()
                test_agent.run_test_automation = AsyncMock(return_value={
                    'status': 'completed'
                })
                test_agent_class.return_value = test_agent

                # Create driver
                driver = EpicDriver(
                    epic_path=str(epic_path),
                    source_dir=str(source_dir),
                    test_dir=str(test_dir),
                    skip_quality=False,
                    skip_tests=False,
                    verbose=True
                )

                # Run workflow
                result = await driver.run()

                assert result is True

                # Verify state manager updates
                assert driver.state_manager.update_story_status.called
