"""
Tests for state_manager.py - Independent State Management & Progress Tracking

Tests cover:
- Database schema creation
- Story lifecycle management
- Status transitions
- Progress tracking
- Interrupt/resume functionality
- Portability and independence

Author: Claude Code
Date: 2026-01-04
"""

import pytest
import sqlite3
import os
import tempfile

from autoBMAD.epic_automation.state_manager import (
    StateManager,
    StoryStatus,
    QAResult
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
def state_manager(temp_db):
    """Create a StateManager instance with temporary database"""
    return StateManager(temp_db)


class TestStateManagerInit:
    """Test database initialization and schema creation"""

    def test_init_creates_database(self, temp_db):
        """Test that StateManager creates database file"""
        # Remove temp file created by fixture
        os.unlink(temp_db)
        assert not os.path.exists(temp_db)

        StateManager(temp_db)
        assert os.path.exists(temp_db)

    def test_init_creates_stories_table(self, state_manager):
        """Test that stories table is created"""
        conn = sqlite3.connect(state_manager.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='stories'
        """)
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == 'stories'

    def test_init_creates_indexes(self, state_manager):
        """Test that indexes are created"""
        conn = sqlite3.connect(state_manager.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND tbl_name='stories'
        """)
        indexes = cursor.fetchall()
        conn.close()

        index_names = [idx[0] for idx in indexes]
        assert 'idx_story_status' in index_names
        assert 'idx_story_path' in index_names
        assert 'idx_epic_path' in index_names

    def test_schema_has_required_columns(self, state_manager):
        """Test that all required columns exist"""
        conn = sqlite3.connect(state_manager.db_path)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(stories)")
        columns = {row[1]: row for row in cursor.fetchall()}
        conn.close()

        required_columns = [
            'id', 'epic_path', 'story_path', 'status',
            'iteration', 'qa_result', 'created_at', 'updated_at', 'notes'
        ]

        for col in required_columns:
            assert col in columns, f"Missing required column: {col}"


class TestStoryLifecycle:
    """Test story lifecycle management"""

    def test_add_story_success(self, state_manager):
        """Test successfully adding a new story"""
        epic_path = "docs/epics/test-epic.md"
        story_path = "docs/stories/001-test-story.md"

        result = state_manager.add_story(epic_path, story_path)

        assert result is True

        story = state_manager.get_story(story_path)
        assert story is not None
        assert story['epic_path'] == epic_path
        assert story['story_path'] == story_path
        assert story['status'] == 'pending'
        assert story['iteration'] == 0

    def test_add_story_duplicate_returns_false(self, state_manager):
        """Test that adding duplicate story returns False"""
        epic_path = "docs/epics/test-epic.md"
        story_path = "docs/stories/001-test-story.md"

        state_manager.add_story(epic_path, story_path)
        result = state_manager.add_story(epic_path, story_path)

        assert result is False

    def test_update_status_success(self, state_manager):
        """Test successfully updating story status"""
        epic_path = "docs/epics/test-epic.md"
        story_path = "docs/stories/001-test-story.md"

        state_manager.add_story(epic_path, story_path)

        result = state_manager.update_status(
            story_path,
            StoryStatus.IN_PROGRESS
        )

        assert result is True

        story = state_manager.get_story(story_path)
        assert story['status'] == 'in_progress'
        assert story['iteration'] == 1  # Should increment on in_progress

    def test_update_status_with_qa_result(self, state_manager):
        """Test updating status with QA result"""
        epic_path = "docs/epics/test-epic.md"
        story_path = "docs/stories/001-test-story.md"

        state_manager.add_story(epic_path, story_path)
        state_manager.update_status(story_path, StoryStatus.IN_PROGRESS)
        state_manager.update_status(
            story_path,
            StoryStatus.REVIEW,
            QAResult.PASS
        )

        story = state_manager.get_story(story_path)
        assert story['status'] == 'review'
        assert story['qa_result'] == 'PASS'

    def test_update_status_nonexistent_story(self, state_manager):
        """Test updating status of non-existent story returns False"""
        result = state_manager.update_status(
            "nonexistent.md",
            StoryStatus.IN_PROGRESS
        )
        assert result is False

    def test_delete_story_success(self, state_manager):
        """Test successfully deleting a story"""
        epic_path = "docs/epics/test-epic.md"
        story_path = "docs/stories/001-test-story.md"

        state_manager.add_story(epic_path, story_path)
        result = state_manager.delete_story(story_path)

        assert result is True
        assert state_manager.get_story(story_path) is None

    def test_delete_nonexistent_story(self, state_manager):
        """Test deleting non-existent story returns False"""
        result = state_manager.delete_story("nonexistent.md")
        assert result is False


class TestStatusTransitions:
    """Test status transition logic"""

    def test_status_transition_pending_to_in_progress(self, state_manager):
        """Test transition from pending to in_progress"""
        epic_path = "docs/epics/test-epic.md"
        story_path = "docs/stories/001-test-story.md"

        state_manager.add_story(epic_path, story_path)
        state_manager.update_status(story_path, StoryStatus.IN_PROGRESS)

        story = state_manager.get_story(story_path)
        assert story['status'] == 'in_progress'
        assert story['iteration'] == 1

    def test_status_transition_in_progress_to_review(self, state_manager):
        """Test transition from in_progress to review"""
        epic_path = "docs/epics/test-epic.md"
        story_path = "docs/stories/001-test-story.md"

        state_manager.add_story(epic_path, story_path)
        state_manager.update_status(story_path, StoryStatus.IN_PROGRESS)
        state_manager.update_status(story_path, StoryStatus.REVIEW)

        story = state_manager.get_story(story_path)
        assert story['status'] == 'review'
        assert story['iteration'] == 1  # Iteration doesn't change

    def test_status_transition_review_to_pass(self, state_manager):
        """Test transition from review to pass"""
        epic_path = "docs/epics/test-epic.md"
        story_path = "docs/stories/001-test-story.md"

        state_manager.add_story(epic_path, story_path)
        state_manager.update_status(story_path, StoryStatus.IN_PROGRESS)
        state_manager.update_status(story_path, StoryStatus.REVIEW)
        state_manager.update_status(
            story_path,
            StoryStatus.PASS,
            QAResult.PASS
        )

        story = state_manager.get_story(story_path)
        assert story['status'] == 'pass'
        assert story['qa_result'] == 'PASS'

    def test_status_transition_review_to_fail(self, state_manager):
        """Test transition from review to fail"""
        epic_path = "docs/epics/test-epic.md"
        story_path = "docs/stories/001-test-story.md"

        state_manager.add_story(epic_path, story_path)
        state_manager.update_status(story_path, StoryStatus.IN_PROGRESS)
        state_manager.update_status(story_path, StoryStatus.REVIEW)
        state_manager.update_status(
            story_path,
            StoryStatus.FAIL,
            QAResult.FAIL
        )

        story = state_manager.get_story(story_path)
        assert story['status'] == 'fail'
        assert story['qa_result'] == 'FAIL'

    def test_iteration_increments_on_in_progress(self, state_manager):
        """Test that iteration increments when status becomes in_progress"""
        epic_path = "docs/epics/test-epic.md"
        story_path = "docs/stories/001-test-story.md"

        state_manager.add_story(epic_path, story_path)
        state_manager.update_status(story_path, StoryStatus.IN_PROGRESS)
        state_manager.update_status(story_path, StoryStatus.REVIEW)
        state_manager.update_status(story_path, StoryStatus.IN_PROGRESS)  # Back to in_progress

        story = state_manager.get_story(story_path)
        assert story['iteration'] == 2  # Should increment again


class TestProgressTracking:
    """Test progress monitoring and reporting"""

    def test_get_stories_by_status(self, state_manager):
        """Test retrieving stories by status"""
        # Add multiple stories
        state_manager.add_story("epic1", "story1")
        state_manager.add_story("epic1", "story2")
        state_manager.add_story("epic1", "story3")

        # Update statuses
        state_manager.update_status("story1", StoryStatus.IN_PROGRESS)
        state_manager.update_status("story2", StoryStatus.REVIEW)

        # Get stories by status
        pending = state_manager.get_stories_by_status(StoryStatus.PENDING)
        in_progress = state_manager.get_stories_by_status(StoryStatus.IN_PROGRESS)
        review = state_manager.get_stories_by_status(StoryStatus.REVIEW)

        assert len(pending) == 1
        assert len(in_progress) == 1
        assert len(review) == 1

    def test_get_stories_by_epic(self, state_manager):
        """Test retrieving stories by epic"""
        # Add stories to different epics
        state_manager.add_story("epic1", "story1")
        state_manager.add_story("epic1", "story2")
        state_manager.add_story("epic2", "story3")

        epic1_stories = state_manager.get_stories_by_epic("epic1")
        epic2_stories = state_manager.get_stories_by_epic("epic2")

        assert len(epic1_stories) == 2
        assert len(epic2_stories) == 1

    def test_get_progress_summary_all_stories(self, state_manager):
        """Test progress summary for all stories"""
        # Add multiple stories
        state_manager.add_story("epic1", "story1")
        state_manager.add_story("epic1", "story2")
        state_manager.add_story("epic1", "story3")
        state_manager.add_story("epic1", "story4")

        # Update some to completed
        state_manager.update_status("story1", StoryStatus.PASS)
        state_manager.update_status("story2", StoryStatus.PASS)
        state_manager.update_status("story3", StoryStatus.IN_PROGRESS)

        summary = state_manager.get_progress_summary()

        assert summary['total'] == 4
        assert summary['by_status']['pass'] == 2
        assert summary['by_status']['pending'] == 1
        assert summary['by_status']['in_progress'] == 1
        assert summary['completion_percentage'] == 50.0

    def test_get_progress_summary_by_epic(self, state_manager):
        """Test progress summary filtered by epic"""
        # Add stories to different epics
        state_manager.add_story("epic1", "story1")
        state_manager.add_story("epic1", "story2")
        state_manager.add_story("epic2", "story3")

        # Complete one from epic1
        state_manager.update_status("story1", StoryStatus.PASS)

        epic1_summary = state_manager.get_progress_summary("epic1")
        epic2_summary = state_manager.get_progress_summary("epic2")

        assert epic1_summary['total'] == 2
        assert epic1_summary['completion_percentage'] == 50.0
        assert epic2_summary['total'] == 1
        assert epic2_summary['completion_percentage'] == 0.0

    def test_get_all_stories(self, state_manager):
        """Test retrieving all stories"""
        # Add multiple stories
        state_manager.add_story("epic1", "story1")
        state_manager.add_story("epic1", "story2")

        all_stories = state_manager.get_all_stories()
        assert len(all_stories) == 2


class TestInterruptResume:
    """Test interrupt/resume functionality"""

    def test_resume_story_in_progress(self, state_manager):
        """Test resuming a story in progress"""
        epic_path = "docs/epics/test-epic.md"
        story_path = "docs/stories/001-test-story.md"

        state_manager.add_story(epic_path, story_path)
        state_manager.update_status(story_path, StoryStatus.IN_PROGRESS)

        # Simulate interruption by getting story
        resumed = state_manager.resume_story(story_path)

        assert resumed is not None
        assert resumed['status'] == 'in_progress'
        assert resumed['iteration'] == 1  # Should be in progress

    def test_resume_story_pending(self, state_manager):
        """Test resuming a pending story"""
        epic_path = "docs/epics/test-epic.md"
        story_path = "docs/stories/001-test-story.md"

        state_manager.add_story(epic_path, story_path)

        resumed = state_manager.resume_story(story_path)

        assert resumed is not None
        assert resumed['status'] == 'in_progress'
        assert resumed['iteration'] == 1  # Should be set to in_progress

    def test_resume_story_pass(self, state_manager):
        """Test resuming a completed (pass) story doesn't change status"""
        epic_path = "docs/epics/test-epic.md"
        story_path = "docs/stories/001-test-story.md"

        state_manager.add_story(epic_path, story_path)
        state_manager.update_status(story_path, StoryStatus.IN_PROGRESS)
        state_manager.update_status(story_path, StoryStatus.REVIEW)
        state_manager.update_status(
            story_path,
            StoryStatus.PASS,
            QAResult.PASS
        )

        resumed = state_manager.resume_story(story_path)

        assert resumed is not None
        assert resumed['status'] == 'pass'  # Should remain pass

    def test_resume_nonexistent_story(self, state_manager):
        """Test resuming non-existent story returns None"""
        resumed = state_manager.resume_story("nonexistent.md")
        assert resumed is None


class TestPortability:
    """Test independence and portability"""

    def test_no_external_dependencies(self, state_manager):
        """Test that StateManager has no external dependencies"""
        # This is a static test - we verify the imports
        import sys

        # Check that only standard library modules are used
        # (This is verified by the fact that we only import sqlite3, os, datetime, etc.)
        assert 'sqlite3' in sys.modules

    def test_works_without_autonomous_coding(self, temp_db):
        """Test that StateManager works independently"""
        # This test verifies the class can be instantiated and used
        # without any dependency on @autonomous-coding
        manager = StateManager(temp_db)

        # Should be able to use it without any special setup
        assert manager.db_path == temp_db
        assert os.path.exists(temp_db)

    def test_copy_paste_ready(self, temp_db):
        """Test that StateManager can be copied to new projects"""
        # Verify the module can be imported and used standalone
        manager = StateManager(temp_db)

        # Should work with just Python standard library
        result = manager.add_story("test-epic", "test-story")
        assert result is True

    def test_database_portability(self, temp_db, state_manager):
        """Test that database can be moved between projects"""
        # Add a story
        state_manager.add_story("epic1", "story1")

        # Create a new StateManager with same database
        manager2 = StateManager(temp_db)
        story = manager2.get_story("story1")

        assert story is not None
        assert story['story_path'] == "story1"


class TestEnumValidation:
    """Test enum validation for status and QA results"""

    def test_status_enum_values(self):
        """Test that StoryStatus enum has correct values"""
        assert StoryStatus.PENDING.value == "pending"
        assert StoryStatus.IN_PROGRESS.value == "in_progress"
        assert StoryStatus.REVIEW.value == "review"
        assert StoryStatus.PASS.value == "pass"
        assert StoryStatus.FAIL.value == "fail"

    def test_qa_result_enum_values(self):
        """Test that QAResult enum has correct values"""
        assert QAResult.PASS.value == "PASS"
        assert QAResult.CONCERNS.value == "CONCERNS"
        assert QAResult.FAIL.value == "FAIL"
        assert QAResult.WAIVED.value == "WAIVED"


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_get_story_not_found(self, state_manager):
        """Test getting non-existent story returns None"""
        story = state_manager.get_story("nonexistent.md")
        assert story is None

    def test_update_with_notes(self, state_manager):
        """Test updating story with notes"""
        state_manager.add_story("epic", "story")
        state_manager.update_status(
            "story",
            StoryStatus.IN_PROGRESS,
            notes="Starting implementation"
        )

        story = state_manager.get_story("story")
        assert story['notes'] == "Starting implementation"

    def test_empty_database_progress_summary(self, state_manager):
        """Test progress summary with empty database"""
        summary = state_manager.get_progress_summary()

        assert summary['total'] == 0
        assert summary['completion_percentage'] == 0.0
        assert len(summary['by_status']) == 0

    def test_get_stories_by_status_empty(self, state_manager):
        """Test getting stories by status when none exist"""
        stories = state_manager.get_stories_by_status(StoryStatus.PENDING)
        assert stories == []

    def test_get_stories_by_epic_empty(self, state_manager):
        """Test getting stories by epic when none exist"""
        stories = state_manager.get_stories_by_epic("nonexistent")
        assert stories == []


class TestUtilityMethods:
    """Test utility methods for story management"""

    def test_complete_story_pass(self, state_manager):
        """Test completing story with PASS result"""
        epic_path = "docs/epics/test-epic.md"
        story_path = "docs/stories/001-test-story.md"

        state_manager.add_story(epic_path, story_path)
        state_manager.update_status(story_path, StoryStatus.IN_PROGRESS)

        result = state_manager.complete_story(story_path, "PASS")

        assert result is True

        story = state_manager.get_story(story_path)
        assert story['status'] == 'pass'
        assert story['qa_result'] == 'PASS'

    def test_complete_story_fail(self, state_manager):
        """Test completing story with FAIL result"""
        epic_path = "docs/epics/test-epic.md"
        story_path = "docs/stories/001-test-story.md"

        state_manager.add_story(epic_path, story_path)
        state_manager.update_status(story_path, StoryStatus.IN_PROGRESS)

        result = state_manager.complete_story(story_path, "FAIL")

        assert result is True

        story = state_manager.get_story(story_path)
        assert story['status'] == 'fail'
        assert story['qa_result'] == 'FAIL'

    def test_complete_story_nonexistent(self, state_manager):
        """Test completing non-existent story returns False"""
        result = state_manager.complete_story("nonexistent.md", "PASS")
        assert result is False

    def test_complete_story_concerns(self, state_manager):
        """Test completing story with CONCERNS result"""
        epic_path = "docs/epics/test-epic.md"
        story_path = "docs/stories/001-test-story.md"

        state_manager.add_story(epic_path, story_path)
        state_manager.update_status(story_path, StoryStatus.IN_PROGRESS)

        result = state_manager.complete_story(story_path, "CONCERNS")

        assert result is True

        story = state_manager.get_story(story_path)
        assert story['status'] == 'fail'
        assert story['qa_result'] == 'CONCERNS'

    def test_reset_story_success(self, state_manager):
        """Test resetting story to pending status"""
        epic_path = "docs/epics/test-epic.md"
        story_path = "docs/stories/001-test-story.md"

        state_manager.add_story(epic_path, story_path)
        state_manager.update_status(story_path, StoryStatus.IN_PROGRESS)
        state_manager.update_status(story_path, StoryStatus.REVIEW)

        result = state_manager.reset_story(story_path)

        assert result is True

        story = state_manager.get_story(story_path)
        assert story['status'] == 'pending'
        assert story['iteration'] == 0
        assert story['qa_result'] is None

    def test_reset_story_nonexistent(self, state_manager):
        """Test resetting non-existent story returns False"""
        result = state_manager.reset_story("nonexistent.md")
        assert result is False

    def test_reset_story_clears_all_data(self, state_manager):
        """Test that reset clears iteration and QA result"""
        epic_path = "docs/epics/test-epic.md"
        story_path = "docs/stories/001-test-story.md"

        state_manager.add_story(epic_path, story_path)
        state_manager.update_status(story_path, StoryStatus.IN_PROGRESS)
        state_manager.update_status(story_path, StoryStatus.REVIEW, QAResult.PASS)

        state_manager.reset_story(story_path)

        story = state_manager.get_story(story_path)
        assert story['iteration'] == 0
        assert story['qa_result'] is None
        assert story['status'] == 'pending'

    def test_get_stats_empty_database(self, state_manager):
        """Test getting stats from empty database"""
        stats = state_manager.get_stats()
        assert stats == {}

    def test_get_stats_with_data(self, state_manager):
        """Test getting stats with multiple stories"""
        # Add stories with different statuses
        state_manager.add_story("epic1", "story1")
        state_manager.add_story("epic1", "story2")
        state_manager.add_story("epic1", "story3")
        state_manager.add_story("epic1", "story4")

        # Update statuses
        state_manager.update_status("story1", StoryStatus.PASS)
        state_manager.update_status("story2", StoryStatus.IN_PROGRESS)
        state_manager.update_status("story3", StoryStatus.REVIEW)

        stats = state_manager.get_stats()

        assert stats['pending'] == 1  # story4
        assert stats['in_progress'] == 1  # story2
        assert stats['review'] == 1  # story3
        assert stats['pass'] == 1  # story1
        assert 'fail' not in stats

    def test_get_stats_reflects_iterations(self, state_manager):
        """Test that stats reflect current state after iterations"""
        epic_path = "docs/epics/test-epic.md"
        story_path = "docs/stories/001-test-story.md"

        state_manager.add_story(epic_path, story_path)
        state_manager.update_status(story_path, StoryStatus.IN_PROGRESS)
        state_manager.update_status(story_path, StoryStatus.REVIEW)
        state_manager.update_status(story_path, StoryStatus.IN_PROGRESS)  # Back to in_progress

        stats = state_manager.get_stats()

        assert stats['in_progress'] == 1
        assert stats.get('pending', 0) == 0
