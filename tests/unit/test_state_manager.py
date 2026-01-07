"""
Unit tests for StateManager module.
"""

import asyncio
import json
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import pytest

from autoBMAD.epic_automation.state_manager import StateManager, StoryStatus, QAResult


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    yield db_path
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def state_manager(temp_db):
    """Create a StateManager instance with temporary database."""
    return StateManager(db_path=temp_db)


class TestStateManager:
    """Test StateManager class."""

    def test_init_creates_database(self, temp_db):
        """Test that initialization creates the database file."""
        assert not Path(temp_db).exists()
        StateManager(db_path=temp_db)
        assert Path(temp_db).exists()

    def test_init_creates_tables(self, state_manager):
        """Test that database tables are created."""
        conn = sqlite3.connect(state_manager.db_path)
        cursor = conn.cursor()

        # Check stories table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stories'")
        assert cursor.fetchone() is not None

        # Check indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_story_path'")
        assert cursor.fetchone() is not None

        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_status'")
        assert cursor.fetchone() is not None

        conn.close()

    @pytest.mark.asyncio
    async def test_add_story(self, state_manager):
        """Test adding a new story."""
        await state_manager.add_story(
            epic_path="epics/epic-1.md",
            story_path="docs/stories/1.1-test.md",
            status=StoryStatus.PENDING,
            phase="development"
        )

        # Verify story was added
        story = await state_manager.get_story("docs/stories/1.1-test.md")
        assert story is not None
        assert story['epic_path'] == "epics/epic-1.md"
        assert story['status'] == StoryStatus.PENDING.value
        assert story['phase'] == "development"

    @pytest.mark.asyncio
    async def test_update_story_status(self, state_manager):
        """Test updating story status."""
        await state_manager.add_story(
            epic_path="epics/epic-1.md",
            story_path="docs/stories/1.1-test.md",
            status=StoryStatus.PENDING,
            phase="development"
        )

        # Update status
        await state_manager.update_story_status(
            "docs/stories/1.1-test.md",
            StoryStatus.IN_PROGRESS
        )

        # Verify update
        story = await state_manager.get_story("docs/stories/1.1-test.md")
        assert story['status'] == StoryStatus.IN_PROGRESS.value

    @pytest.mark.asyncio
    async def test_get_story_by_status(self, state_manager):
        """Test getting stories by status."""
        # Add multiple stories
        await state_manager.add_story(
            epic_path="epics/epic-1.md",
            story_path="docs/stories/1.1-test.md",
            status=StoryStatus.PENDING,
            phase="development"
        )
        await state_manager.add_story(
            epic_path="epics/epic-1.md",
            story_path="docs/stories/1.2-test.md",
            status=StoryStatus.IN_PROGRESS,
            phase="development"
        )

        # Get pending stories
        pending_stories = await state_manager.get_stories_by_status(StoryStatus.PENDING)
        assert len(pending_stories) == 1
        assert pending_stories[0]['story_path'] == "docs/stories/1.1-test.md"

    @pytest.mark.asyncio
    async def test_update_qa_result(self, state_manager):
        """Test updating QA result."""
        await state_manager.add_story(
            epic_path="epics/epic-1.md",
            story_path="docs/stories/1.1-test.md",
            status=StoryStatus.PENDING,
            phase="development"
        )

        await state_manager.update_qa_result(
            "docs/stories/1.1-test.md",
            QAResult.PASS
        )

        story = await state_manager.get_story("docs/stories/1.1-test.md")
        assert story['qa_result'] == QAResult.PASS.value

    @pytest.mark.asyncio
    async def test_record_error(self, state_manager):
        """Test recording error message."""
        await state_manager.add_story(
            epic_path="epics/epic-1.md",
            story_path="docs/stories/1.1-test.md",
            status=StoryStatus.PENDING,
            phase="development"
        )

        await state_manager.record_error(
            "docs/stories/1.1-test.md",
            "Test error message"
        )

        story = await state_manager.get_story("docs/stories/1.1-test.md")
        assert story['error_message'] == "Test error message"

    @pytest.mark.asyncio
    async def test_increment_iteration(self, state_manager):
        """Test incrementing story iteration."""
        await state_manager.add_story(
            epic_path="epics/epic-1.md",
            story_path="docs/stories/1.1-test.md",
            status=StoryStatus.PENDING,
            phase="development"
        )

        # Increment iteration
        await state_manager.increment_iteration("docs/stories/1.1-test.md")

        story = await state_manager.get_story("docs/stories/1.1-test.md")
        assert story['iteration'] == 1

    @pytest.mark.asyncio
    async def test_get_all_stories(self, state_manager):
        """Test getting all stories."""
        # Add multiple stories
        await state_manager.add_story(
            epic_path="epics/epic-1.md",
            story_path="docs/stories/1.1-test.md",
            status=StoryStatus.PENDING,
            phase="development"
        )
        await state_manager.add_story(
            epic_path="epics/epic-1.md",
            story_path="docs/stories/1.2-test.md",
            status=StoryStatus.IN_PROGRESS,
            phase="development"
        )

        all_stories = await state_manager.get_all_stories()
        assert len(all_stories) == 2

    @pytest.mark.asyncio
    async def test_get_story_not_found(self, state_manager):
        """Test getting non-existent story returns None."""
        story = await state_manager.get_story("docs/stories/nonexistent.md")
        assert story is None

    @pytest.mark.asyncio
    async def test_add_story_duplicate(self, state_manager):
        """Test adding duplicate story raises error."""
        await state_manager.add_story(
            epic_path="epics/epic-1.md",
            story_path="docs/stories/1.1-test.md",
            status=StoryStatus.PENDING,
            phase="development"
        )

        # Try to add same story again
        with pytest.raises(Exception):  # Should raise integrity error
            await state_manager.add_story(
                epic_path="epics/epic-1.md",
                story_path="docs/stories/1.1-test.md",
                status=StoryStatus.PENDING,
                phase="development"
            )

    @pytest.mark.asyncio
    async def test_code_quality_phase_operations(self, state_manager):
        """Test code quality phase operations."""
        await state_manager.record_code_quality_phase(
            record_id="test-record-1",
            epic_id="epic-1",
            file_path="src/test.py",
            basedpyright_errors={"error1": "test"},
            ruff_errors={"error2": "test"}
        )

        record = await state_manager.get_code_quality_record("test-record-1")
        assert record is not None
        assert record['epic_id'] == "epic-1"
        assert record['file_path'] == "src/test.py"

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, state_manager):
        """Test concurrent operations don't cause issues."""
        async def add_story(i):
            await state_manager.add_story(
                epic_path="epics/epic-1.md",
                story_path=f"docs/stories/1.{i}-test.md",
                status=StoryStatus.PENDING,
                phase="development"
            )

        # Add 10 stories concurrently
        await asyncio.gather(*[add_story(i) for i in range(10)])

        # Verify all were added
        all_stories = await state_manager.get_all_stories()
        assert len(all_stories) == 10

    @pytest.mark.asyncio
    async def test_update_with_nonexistent_story(self, state_manager):
        """Test updating non-existent story handles gracefully."""
        # Should not raise error, just log
        await state_manager.update_story_status(
            "docs/stories/nonexistent.md",
            StoryStatus.IN_PROGRESS
        )

    def test_story_status_enum(self):
        """Test StoryStatus enum values."""
        assert StoryStatus.PENDING.value == "pending"
        assert StoryStatus.IN_PROGRESS.value == "in_progress"
        assert StoryStatus.REVIEW.value == "review"
        assert StoryStatus.PASS.value == "pass"
        assert StoryStatus.FAIL.value == "fail"

    def test_qa_result_enum(self):
        """Test QAResult enum values."""
        assert QAResult.PASS.value == "PASS"
        assert QAResult.CONCERNS.value == "CONCERNS"
        assert QAResult.FAIL.value == "FAIL"
        assert QAResult.WAIVED.value == "WAIVED"
