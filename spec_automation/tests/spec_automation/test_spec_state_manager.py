"""
Tests for spec_state_manager.py
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from spec_automation.spec_state_manager import SpecStateManager, StoryStatus, QAResult


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_spec_progress.db"
        yield db_path


@pytest.fixture
def state_manager(temp_db):
    """Create a SpecStateManager instance for testing."""
    return SpecStateManager(temp_db)


class TestStoryStatus:
    """Test cases for StoryStatus enum."""

    def test_all_statuses_exist(self):
        """Test that all expected statuses exist."""
        assert hasattr(StoryStatus, "PENDING")
        assert hasattr(StoryStatus, "IN_PROGRESS")
        assert hasattr(StoryStatus, "REVIEW")
        assert hasattr(StoryStatus, "COMPLETED")
        assert hasattr(StoryStatus, "FAILED")
        assert hasattr(StoryStatus, "CANCELLED")
        assert hasattr(StoryStatus, "ERROR")

    def test_status_values(self):
        """Test status enum values."""
        assert StoryStatus.PENDING.value == "pending"
        assert StoryStatus.IN_PROGRESS.value == "in_progress"
        assert StoryStatus.REVIEW.value == "review"
        assert StoryStatus.COMPLETED.value == "completed"
        assert StoryStatus.FAILED.value == "failed"
        assert StoryStatus.CANCELLED.value == "cancelled"
        assert StoryStatus.ERROR.value == "error"


class TestQAResult:
    """Test cases for QAResult enum."""

    def test_all_qa_results_exist(self):
        """Test that all expected QA results exist."""
        assert hasattr(QAResult, "PASS")
        assert hasattr(QAResult, "CONCERNS")
        assert hasattr(QAResult, "FAIL")
        assert hasattr(QAResult, "WAIVED")

    def test_qa_result_values(self):
        """Test QA result enum values."""
        assert QAResult.PASS.value == "PASS"
        assert QAResult.CONCERNS.value == "CONCERNS"
        assert QAResult.FAIL.value == "FAIL"
        assert QAResult.WAIVED.value == "WAIVED"


class TestSpecStateManager:
    """Test cases for SpecStateManager."""

    def test_init_creates_database(self, temp_db):
        """Test that initialization creates the database."""
        assert not temp_db.exists()
        manager = SpecStateManager(temp_db)
        assert temp_db.exists()

    def test_init_creates_table(self, state_manager, temp_db):
        """Test that initialization creates the stories table."""
        import sqlite3

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='stories'
        """)
        table = cursor.fetchone()

        conn.close()

        assert table is not None
        assert table[0] == "stories"

    def test_init_creates_indices(self, state_manager, temp_db):
        """Test that initialization creates database indices."""
        import sqlite3

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND tbl_name='stories'
        """)
        indices = cursor.fetchall()

        conn.close()

        index_names = [idx[0] for idx in indices]
        assert any("story_path" in name for name in index_names)
        assert any("status" in name for name in index_names)

    def test_get_story_status_nonexistent(self, state_manager):
        """Test getting status of a non-existent story."""
        result = state_manager.get_story_status("/nonexistent/story.md")
        assert result is None

    def test_update_story_status_new(self, state_manager):
        """Test updating status of a new story."""
        story_path = "/test/story1.md"
        status = "in_progress"
        phase = "development"

        state_manager.update_story_status(story_path, status, phase)

        result = state_manager.get_story_status(story_path)

        assert result is not None
        assert result["story_path"] == story_path
        assert result["status"] == status
        assert result["phase"] == phase

    def test_update_story_status_existing(self, state_manager):
        """Test updating status of an existing story."""
        story_path = "/test/story2.md"

        # First update
        state_manager.update_story_status(story_path, "pending", "planning")

        # Second update
        state_manager.update_story_status(story_path, "in_progress", "development")

        result = state_manager.get_story_status(story_path)

        assert result is not None
        assert result["status"] == "in_progress"
        assert result["phase"] == "development"

    def test_update_story_status_with_qa_result(self, state_manager):
        """Test updating story status with QA result."""
        story_path = "/test/story3.md"
        state_manager.update_story_status(
            story_path,
            "completed",
            "qa",
            qa_result="PASS"
        )

        result = state_manager.get_story_status(story_path)

        assert result is not None
        assert result["status"] == "completed"
        assert result["qa_result"] == "PASS"

    def test_update_story_status_with_error(self, state_manager):
        """Test updating story status with error message."""
        story_path = "/test/story4.md"
        error_msg = "Test error message"
        state_manager.update_story_status(
            story_path,
            "failed",
            "testing",
            error_message=error_msg
        )

        result = state_manager.get_story_status(story_path)

        assert result is not None
        assert result["status"] == "failed"
        assert result["error_message"] == error_msg

    def test_get_all_stories_empty(self, state_manager):
        """Test getting all stories when database is empty."""
        stories = state_manager.get_all_stories()
        assert stories == []

    def test_get_all_stories_multiple(self, state_manager):
        import time
        time.sleep(0.001)
        state_manager.update_story_status("/test/story2.md", "in_progress", "dev")
        time.sleep(0.001)
        state_manager.update_story_status("/test/story3.md", "pending", "planning")

        stories = state_manager.get_all_stories()

        assert len(stories) == 3
        # Stories should be ordered by updated_at DESC (newest first)
        assert stories[0]["story_path"] == "/test/story3.md"
        assert stories[1]["story_path"] == "/test/story2.md"
        assert stories[2]["story_path"] == "/test/story1.md"

    def test_get_stories_by_status(self, state_manager):
        """Test getting stories filtered by status."""
        state_manager.update_story_status("/test/story1.md", "completed", "done")
        state_manager.update_story_status("/test/story2.md", "in_progress", "dev")
        state_manager.update_story_status("/test/story3.md", "in_progress", "dev")
        state_manager.update_story_status("/test/story4.md", "pending", "planning")

        in_progress = state_manager.get_stories_by_status("in_progress")
        completed = state_manager.get_stories_by_status("completed")
        pending = state_manager.get_stories_by_status("pending")

        assert len(in_progress) == 2
        assert len(completed) == 1
        assert len(pending) == 1

        # All in_progress stories should have correct status
        for story in in_progress:
            assert story["status"] == "in_progress"

    def test_delete_story_existing(self, state_manager):
        """Test deleting an existing story."""
        story_path = "/test/story_to_delete.md"
        state_manager.update_story_status(story_path, "pending", "planning")

        # Verify it exists
        assert state_manager.get_story_status(story_path) is not None

        # Delete it
        result = state_manager.delete_story(story_path)
        assert result is True

        # Verify it's gone
        assert state_manager.get_story_status(story_path) is None

    def test_delete_story_nonexistent(self, state_manager):
        """Test deleting a non-existent story."""
        result = state_manager.delete_story("/nonexistent/story.md")
        assert result is False

    def test_multiple_updates_same_story(self, state_manager):
        """Test multiple updates to the same story."""
        story_path = "/test/story_multi.md"

        # Update 1
        state_manager.update_story_status(story_path, "pending", "planning")

        # Update 2
        state_manager.update_story_status(story_path, "in_progress", "development")

        # Update 3
        state_manager.update_story_status(story_path, "review", "qa")

        # Update 4
        state_manager.update_story_status(story_path, "completed", "done")

        # Should only have one story
        all_stories = state_manager.get_all_stories()
        assert len(all_stories) == 1

        # Final status should be the last update
        result = state_manager.get_story_status(story_path)
        assert result["status"] == "completed"
        assert result["phase"] == "done"

    def test_database_persists(self, temp_db):
        """Test that database persists data across instances."""
        # Create first manager and add data
        manager1 = SpecStateManager(temp_db)
        manager1.update_story_status("/test/story.md", "in_progress", "dev")

        # Create second manager with same database
        manager2 = SpecStateManager(temp_db)

        # Should be able to read the data
        result = manager2.get_story_status("/test/story.md")
        assert result is not None
        assert result["status"] == "in_progress"
        assert result["phase"] == "dev"

    def test_timestamps_created(self, state_manager):
        """Test that timestamps are created on insert."""
        import time

        story_path = "/test/timestamp_test.md"
        state_manager.update_story_status(story_path, "pending", "planning")

        result = state_manager.get_story_status(story_path)

        assert "created_at" in result
        assert "updated_at" in result
        assert result["created_at"] is not None
        assert result["updated_at"] is not None

    def test_timestamps_updated(self, state_manager):
        """Test that updated_at timestamp changes on update."""
        import time

        story_path = "/test/timestamp_update.md"

        # First insert
        state_manager.update_story_status(story_path, "pending", "planning")
        result1 = state_manager.get_story_status(story_path)
        created_at = result1["created_at"]
        updated_at = result1["updated_at"]

        # Wait a bit
        time.sleep(0.01)

        # Update
        state_manager.update_story_status(story_path, "in_progress", "development")
        result2 = state_manager.get_story_status(story_path)

        # created_at should be the same
        assert result2["created_at"] == created_at

        # updated_at should be different (newer)
        import sqlite3

        conn = sqlite3.connect(state_manager.db_path)
        cursor = conn.cursor()

        # Try to select version column
        cursor.execute("SELECT version FROM stories LIMIT 1")
        cursor.fetchone()

        conn.close()

    def test_update_with_all_parameters(self, state_manager):
        """Test updating story with all optional parameters."""
        story_path = "/test/complete_update.md"
        qa_result = "CONCERNS"
        error_msg = "Minor issues found"

        state_manager.update_story_status(
            story_path=story_path,
            status="review",
            phase="qa",
            qa_result=qa_result,
            error_message=error_msg
        )

        result = state_manager.get_story_status(story_path)

        assert result["story_path"] == story_path
        assert result["status"] == "review"
        assert result["phase"] == "qa"
        assert result["qa_result"] == qa_result
        assert result["error_message"] == error_msg

    def test_special_characters_in_paths(self, state_manager):
        """Test handling special characters in story paths."""
        story_path = "/test/特殊字符/path with spaces & symbols!@#.md"

        state_manager.update_story_status(story_path, "pending", "planning")

        result = state_manager.get_story_status(story_path)

        assert result is not None
        assert result["story_path"] == story_path

    def test_empty_string_parameters(self, state_manager):
        """Test handling empty string parameters."""
        story_path = "/test/empty_params.md"

        state_manager.update_story_status(
            story_path,
            "pending",
            "",
            qa_result="",
            error_message=""
        )

        result = state_manager.get_story_status(story_path)

        assert result is not None
        assert result["phase"] == ""
        assert result["qa_result"] == ""
        assert result["error_message"] == ""

    def test_status_with_enum(self, state_manager):
        """Test using StoryStatus enum values."""
        story_path = "/test/enum_test.md"

        state_manager.update_story_status(
            story_path,
            StoryStatus.IN_PROGRESS.value,
            "development"
        )

        result = state_manager.get_story_status(story_path)

        assert result["status"] == StoryStatus.IN_PROGRESS.value

    def test_qa_result_with_enum(self, state_manager):
        """Test using QAResult enum values."""
        story_path = "/test/qa_enum_test.md"

        state_manager.update_story_status(
            story_path,
            "completed",
            "qa",
            qa_result=QAResult.PASS.value
        )

        result = state_manager.get_story_status(story_path)

        assert result["qa_result"] == QAResult.PASS.value
