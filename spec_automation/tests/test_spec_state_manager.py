"""
Tests for SpecStateManager module.
"""

import pytest
import sqlite3
from pathlib import Path
import tempfile
from spec_automation.spec_state_manager import SpecStateManager, StoryStatus, QAResult


class TestSpecStateManager:
    """Test suite for SpecStateManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.state_manager = SpecStateManager(self.db_path)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_creates_database(self):
        """Test that initialization creates the database file."""
        assert self.db_path.exists()

    def test_init_creates_table(self):
        """Test that initialization creates the stories table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='stories'
        """)
        table = cursor.fetchone()
        assert table is not None
        assert table[0] == "stories"

        # Check table structure
        cursor.execute("PRAGMA table_info(stories)")
        columns = {col[1]: col[2] for col in cursor.fetchall()}

        assert "id" in columns
        assert "story_path" in columns
        assert "status" in columns
        assert "phase" in columns
        assert "qa_result" in columns
        assert "error_message" in columns
        assert "created_at" in columns
        assert "updated_at" in columns
        assert "version" in columns

        conn.close()

    def test_init_creates_indices(self):
        """Test that initialization creates database indices."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check indices exist
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND tbl_name='stories'
        """)
        indices = [idx[0] for idx in cursor.fetchall()]

        assert any("idx_story_path" in idx for idx in indices)
        assert any("idx_status" in idx for idx in indices)

        conn.close()

    def test_update_and_get_story_status(self):
        """Test updating and retrieving story status."""
        story_path = "docs/stories/test-story.md"
        status = "in_progress"
        phase = "implementation"

        # Update story status
        self.state_manager.update_story_status(
            story_path=story_path,
            status=status,
            phase=phase
        )

        # Retrieve story status
        result = self.state_manager.get_story_status(story_path)

        assert result is not None
        assert result["story_path"] == story_path
        assert result["status"] == status
        assert result["phase"] == phase
        assert result["qa_result"] is None
        assert result["error_message"] is None

    def test_update_story_with_qa_result(self):
        """Test updating story with QA result."""
        story_path = "docs/stories/qa-story.md"

        self.state_manager.update_story_status(
            story_path=story_path,
            status="review",
            phase="qa",
            qa_result="PASS",
            error_message=None
        )

        result = self.state_manager.get_story_status(story_path)

        assert result["status"] == "review"
        assert result["qa_result"] == "PASS"

    def test_update_story_with_error(self):
        """Test updating story with error message."""
        story_path = "docs/stories/error-story.md"

        self.state_manager.update_story_status(
            story_path=story_path,
            status="error",
            phase="implementation",
            qa_result=None,
            error_message="Test error message"
        )

        result = self.state_manager.get_story_status(story_path)

        assert result["status"] == "error"
        assert result["error_message"] == "Test error message"

    def test_get_nonexistent_story(self):
        """Test retrieving non-existent story returns None."""
        result = self.state_manager.get_story_status("nonexistent/story.md")
        assert result is None

    def test_update_existing_story(self):
        """Test updating an existing story updates instead of inserting."""
        story_path = "docs/stories/update-test.md"

        # First insert
        self.state_manager.update_story_status(
            story_path=story_path,
            status="pending",
            phase="planning"
        )

        result1 = self.state_manager.get_story_status(story_path)
        created_at = result1["created_at"]
        updated_at = result1["updated_at"]

        # Update the same story
        self.state_manager.update_story_status(
            story_path=story_path,
            status="in_progress",
            phase="implementation"
        )

        result2 = self.state_manager.get_story_status(story_path)

        # Verify it was updated, not inserted
        assert result2["created_at"] == created_at
        assert result2["updated_at"] != updated_at
        assert result2["status"] == "in_progress"
        assert result2["phase"] == "implementation"

    def test_get_all_stories(self):
        """Test retrieving all stories."""
        # Add multiple stories
        self.state_manager.update_story_status("story1.md", "pending", "planning")
        self.state_manager.update_story_status("story2.md", "in_progress", "implementation")
        self.state_manager.update_story_status("story3.md", "completed", "done")

        all_stories = self.state_manager.get_all_stories()

        assert len(all_stories) == 3
        # Verify structure
        for story in all_stories:
            assert "story_path" in story
            assert "status" in story
            assert "phase" in story

    def test_get_all_stories_empty(self):
        """Test retrieving all stories when database is empty."""
        all_stories = self.state_manager.get_all_stories()
        assert all_stories == []

    def test_get_stories_by_status(self):
        """Test retrieving stories filtered by status."""
        self.state_manager.update_story_status("story1.md", "pending", "planning")
        self.state_manager.update_story_status("story2.md", "in_progress", "implementation")
        self.state_manager.update_story_status("story3.md", "pending", "done")

        pending_stories = self.state_manager.get_stories_by_status("pending")

        assert len(pending_stories) == 2
        for story in pending_stories:
            assert story["status"] == "pending"

    def test_get_stories_by_status_none_match(self):
        """Test retrieving stories with no matching status."""
        self.state_manager.update_story_status("story1.md", "pending", "planning")

        completed_stories = self.state_manager.get_stories_by_status("completed")

        assert completed_stories == []

    def test_delete_existing_story(self):
        """Test deleting an existing story."""
        story_path = "docs/stories/delete-test.md"

        self.state_manager.update_story_status(story_path, "pending", "planning")

        # Verify story exists
        result = self.state_manager.get_story_status(story_path)
        assert result is not None

        # Delete story
        deleted = self.state_manager.delete_story(story_path)
        assert deleted is True

        # Verify story is gone
        result = self.state_manager.get_story_status(story_path)
        assert result is None

    def test_delete_nonexistent_story(self):
        """Test deleting a non-existent story returns False."""
        deleted = self.state_manager.delete_story("nonexistent/story.md")
        assert deleted is False

    def test_delete_removes_from_database(self):
        """Test that delete actually removes from database."""
        story_path = "docs/stories/delete-verify.md"

        self.state_manager.update_story_status(story_path, "pending", "planning")

        # Get all stories before delete
        all_before = self.state_manager.get_all_stories()
        count_before = len(all_before)

        # Delete story
        self.state_manager.delete_story(story_path)

        # Get all stories after delete
        all_after = self.state_manager.get_all_stories()
        count_after = len(all_after)

        assert count_after == count_before - 1

    def test_database_connection_isolation(self):
        """Test that database operations are properly isolated."""
        story_path = "docs/stories/isolation-test.md"

        # Create another state manager instance with same DB
        manager2 = SpecStateManager(self.db_path)

        # Update from first manager
        self.state_manager.update_story_status(story_path, "pending", "planning")

        # Retrieve from second manager
        result = manager2.get_story_status(story_path)

        assert result is not None
        assert result["status"] == "pending"

    def test_enum_values(self):
        """Test that enums have expected values."""
        # Test StoryStatus values
        assert StoryStatus.PENDING.value == "pending"
        assert StoryStatus.IN_PROGRESS.value == "in_progress"
        assert StoryStatus.REVIEW.value == "review"
        assert StoryStatus.COMPLETED.value == "completed"
        assert StoryStatus.FAILED.value == "failed"
        assert StoryStatus.CANCELLED.value == "cancelled"
        assert StoryStatus.ERROR.value == "error"

        # Test QAResult values
        assert QAResult.PASS.value == "PASS"
        assert QAResult.CONCERNS.value == "CONCERNS"
        assert QAResult.FAIL.value == "FAIL"
        assert QAResult.WAIVED.value == "WAIVED"

    def test_database_constraints(self):
        """Test database constraints work properly."""
        story_path = "docs/stories/constraint-test.md"

        # Insert story twice with same path
        self.state_manager.update_story_status(story_path, "pending", "planning")

        # This should update, not fail due to UNIQUE constraint
        self.state_manager.update_story_status(story_path, "in_progress", "implementation")

        # Should only have one story
        all_stories = self.state_manager.get_all_stories()
        matching_stories = [s for s in all_stories if s["story_path"] == story_path]
        assert len(matching_stories) == 1

    def test_special_characters_in_paths(self):
        """Test handling of special characters in story paths."""
        story_path = "docs/stories/test-with-dashes_underscores.md"

        self.state_manager.update_story_status(story_path, "pending", "planning")

        result = self.state_manager.get_story_status(story_path)

        assert result is not None
        assert result["story_path"] == story_path

    def test_unicode_in_error_messages(self):
        """Test handling of unicode characters in error messages."""
        story_path = "docs/stories/unicode-test.md"
        error_msg = "错误信息 with émojis 😀"

        self.state_manager.update_story_status(
            story_path,
            "error",
            "testing",
            error_message=error_msg
        )

        result = self.state_manager.get_story_status(story_path)

        assert result["error_message"] == error_msg

    def test_multiple_updates_sequence(self):
        """Test a sequence of status updates."""
        story_path = "docs/stories/sequence-test.md"

        # Initial status
        self.state_manager.update_story_status(story_path, "pending", "planning")
        result1 = self.state_manager.get_story_status(story_path)
        assert result1["status"] == "pending"

        # Update to in progress
        self.state_manager.update_story_status(story_path, "in_progress", "implementation")
        result2 = self.state_manager.get_story_status(story_path)
        assert result2["status"] == "in_progress"

        # Update to review
        self.state_manager.update_story_status(story_path, "review", "qa")
        result3 = self.state_manager.get_story_status(story_path)
        assert result3["status"] == "review"

        # Update to completed
        self.state_manager.update_story_status(story_path, "completed", "done")
        result4 = self.state_manager.get_story_status(story_path)
        assert result4["status"] == "completed"

    def test_timestamps_are_set(self):
        """Test that created_at and updated_at timestamps are set."""
        story_path = "docs/stories/timestamp-test.md"

        self.state_manager.update_story_status(story_path, "pending", "planning")

        result = self.state_manager.get_story_status(story_path)

        assert result["created_at"] is not None
        assert result["updated_at"] is not None
        assert isinstance(result["created_at"], str)
        assert isinstance(result["updated_at"], str)

    def test_version_field(self):
        """Test that version field is tracked."""
        story_path = "docs/stories/version-test.md"

        self.state_manager.update_story_status(story_path, "pending", "planning")

        result = self.state_manager.get_story_status(story_path)

        assert "version" in result
        assert result["version"] == 1
