"""
Comprehensive tests for SpecStateManager.

This test suite validates:
- Database initialization
- State tracking and updates
- Query operations
- Error handling
"""

import sqlite3

import pytest

from spec_automation.spec_state_manager import SpecStateManager


class TestSpecStateManager:
    """Test suite for SpecStateManager."""

    def test_init_creates_database(self, tmp_path):
        """Test that initialization creates the database."""
        db_path = tmp_path / "test.db"
        manager = SpecStateManager(db_path=db_path)

        assert db_path.exists()
        assert manager.db_path == db_path

    def test_init_creates_tables(self, tmp_path):
        """Test that initialization creates database tables."""
        db_path = tmp_path / "test.db"
        manager = SpecStateManager(db_path=db_path)

        # Check that tables exist by querying them
        conn = manager._get_connection()
        cursor = conn.cursor()

        # Check story_status table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='story_status'"
        )
        assert cursor.fetchone() is not None

        # Check qa_results table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='qa_results'"
        )
        assert cursor.fetchone() is not None

        conn.close()

    def test_update_story_status(self, tmp_path):
        """Test updating story status."""
        db_path = tmp_path / "test.db"
        manager = SpecStateManager(db_path=db_path)

        # Update status
        manager.update_story_status(
            story_path="/test/story.md",
            status="in_progress",
            phase="development",
        )

        # Verify status was updated
        status = manager.get_story_status(story_path="/test/story.md")
        assert status is not None
        assert status["status"] == "in_progress"
        assert status["phase"] == "development"

    def test_get_story_status_not_found(self, tmp_path):
        """Test getting status for non-existent story."""
        db_path = tmp_path / "test.db"
        manager = SpecStateManager(db_path=db_path)

        status = manager.get_story_status(story_path="/nonexistent/story.md")
        assert status is None

    def test_update_status_multiple_stories(self, tmp_path):
        """Test updating status for multiple stories."""
        db_path = tmp_path / "test.db"
        manager = SpecStateManager(db_path=db_path)

        # Update first story
        manager.update_story_status(
            story_path="/test/story1.md",
            status="in_progress",
            phase="development",
        )

        # Update second story
        manager.update_story_status(
            story_path="/test/story2.md",
            status="completed",
            phase="done",
        )

        # Verify both stories have correct status
        status1 = manager.get_story_status(story_path="/test/story1.md")
        status2 = manager.get_story_status(story_path="/test/story2.md")

        assert status1["status"] == "in_progress"
        assert status2["status"] == "completed"

    def test_update_status_overwrites(self, tmp_path):
        """Test that updating status overwrites previous values."""
        db_path = tmp_path / "test.db"
        manager = SpecStateManager(db_path=db_path)

        # First update
        manager.update_story_status(
            story_path="/test/story.md",
            status="in_progress",
            phase="development",
        )

        # Second update
        manager.update_story_status(
            story_path="/test/story.md",
            status="completed",
            phase="done",
        )

        # Verify only the latest status exists
        status = manager.get_story_status(story_path="/test/story.md")
        assert status["status"] == "completed"
        assert status["phase"] == "done"

    def test_get_all_stories(self, tmp_path):
        """Test getting all stories."""
        db_path = tmp_path / "test.db"
        manager = SpecStateManager(db_path=db_path)

        # Add multiple stories
        manager.update_story_status(
            story_path="/test/story1.md",
            status="in_progress",
            phase="development",
        )
        manager.update_story_status(
            story_path="/test/story2.md",
            status="completed",
            phase="done",
        )

        # Get all stories
        stories = manager.get_all_stories()
        assert len(stories) == 2

        # Verify both stories are present
        story_paths = [s["story_path"] for s in stories]
        assert "/test/story1.md" in story_paths
        assert "/test/story2.md" in story_paths

    def test_get_all_stories_empty(self, tmp_path):
        """Test getting all stories when database is empty."""
        db_path = tmp_path / "test.db"
        manager = SpecStateManager(db_path=db_path)

        stories = manager.get_all_stories()
        assert stories == []

    def test_delete_story(self, tmp_path):
        """Test deleting a story."""
        db_path = tmp_path / "test.db"
        manager = SpecStateManager(db_path=db_path)

        # Add story
        manager.update_story_status(
            story_path="/test/story.md",
            status="in_progress",
            phase="development",
        )

        # Verify it exists
        status = manager.get_story_status(story_path="/test/story.md")
        assert status is not None

        # Delete story
        manager.delete_story(story_path="/test/story.md")

        # Verify it's gone
        status = manager.get_story_status(story_path="/test/story.md")
        assert status is None

    def test_delete_nonexistent_story(self, tmp_path):
        """Test deleting a story that doesn't exist."""
        db_path = tmp_path / "test.db"
        manager = SpecStateManager(db_path=db_path)

        # Should not raise an error
        manager.delete_story(story_path="/nonexistent/story.md")

    def test_update_qa_result(self, tmp_path):
        """Test updating QA results."""
        db_path = tmp_path / "test.db"
        manager = SpecStateManager(db_path=db_path)

        # Update QA result
        manager.update_qa_result(
            story_path="/test/story.md",
            requirement="Test requirement",
            status="PASS",
            findings="All tests passed",
            test_coverage=85.0,
        )

        # Get QA results
        results = manager.get_qa_results(story_path="/test/story.md")
        assert len(results) == 1

        result = results[0]
        assert result["requirement"] == "Test requirement"
        assert result["status"] == "PASS"
        assert result["findings"] == "All tests passed"
        assert result["test_coverage"] == 85.0

    def test_get_qa_results_not_found(self, tmp_path):
        """Test getting QA results for non-existent story."""
        db_path = tmp_path / "test.db"
        manager = SpecStateManager(db_path=db_path)

        results = manager.get_qa_results(story_path="/nonexistent/story.md")
        assert results == []

    def test_update_qa_result_multiple(self, tmp_path):
        """Test updating multiple QA results for same story."""
        db_path = tmp_path / "test.db"
        manager = SpecStateManager(db_path=db_path)

        # Add multiple QA results
        manager.update_qa_result(
            story_path="/test/story.md",
            requirement="Requirement 1",
            status="PASS",
            findings="OK",
            test_coverage=90.0,
        )
        manager.update_qa_result(
            story_path="/test/story.md",
            requirement="Requirement 2",
            status="FAIL",
            findings="Missing implementation",
            test_coverage=50.0,
        )

        # Get all QA results
        results = manager.get_qa_results(story_path="/test/story.md")
        assert len(results) == 2

    def test_get_stories_by_status(self, tmp_path):
        """Test getting stories filtered by status."""
        db_path = tmp_path / "test.db"
        manager = SpecStateManager(db_path=db_path)

        # Add stories with different statuses
        manager.update_story_status(
            story_path="/test/story1.md",
            status="in_progress",
            phase="development",
        )
        manager.update_story_status(
            story_path="/test/story2.md",
            status="completed",
            phase="done",
        )
        manager.update_story_status(
            story_path="/test/story3.md",
            status="in_progress",
            phase="testing",
        )

        # Get stories by status
        in_progress = manager.get_stories_by_status(status="in_progress")
        completed = manager.get_stories_by_status(status="completed")

        assert len(in_progress) == 2
        assert len(completed) == 1
        assert in_progress[0]["status"] == "in_progress"

    def test_database_persistence(self, tmp_path):
        """Test that database persists across instances."""
        db_path = tmp_path / "test.db"

        # Create first manager and update status
        manager1 = SpecStateManager(db_path=db_path)
        manager1.update_story_status(
            story_path="/test/story.md",
            status="in_progress",
            phase="development",
        )

        # Create second manager and verify data persists
        manager2 = SpecStateManager(db_path=db_path)
        status = manager2.get_story_status(story_path="/test/story.md")
        assert status["status"] == "in_progress"
        assert status["phase"] == "development"

    def test_invalid_db_path(self, tmp_path):
        """Test handling of invalid database path."""
        # Path points to an existing non-database file
        file_path = tmp_path / "file.txt"
        file_path.write_text("test")

        # SQLite will fail to open an existing non-database file
        with pytest.raises(sqlite3.DatabaseError):
            SpecStateManager(db_path=file_path)

    def test_special_characters_in_paths(self, tmp_path):
        """Test handling of special characters in story paths."""
        db_path = tmp_path / "test.db"
        manager = SpecStateManager(db_path=db_path)

        special_path = "/test/story with spaces & symbols!.md"
        manager.update_story_status(
            story_path=special_path,
            status="completed",
            phase="done",
        )

        status = manager.get_story_status(story_path=special_path)
        assert status["status"] == "completed"
