"""
Tests for StateManager class.

Tests the SQLite state management functionality including:
- Database initialization
- Story state CRUD operations
- Progress tracking
- State persistence and recovery
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from autoBMAD.epic_automation.state_manager import StateManager


class TestStateManager:
    """Test cases for StateManager"""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        temp_dir = tempfile.mkdtemp()
        db_path = temp_dir + "/test_progress.db"
        yield db_path
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def state_manager(self, temp_db):
        """Create a StateManager instance with temporary database"""
        return StateManager(temp_db)

    def test_init_database(self, temp_db):
        """Test successful database initialization"""
        sm = StateManager(temp_db)
        assert Path(temp_db).exists()

        # Verify tables were created
        conn = sm._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        assert 'stories' in tables
        conn.close()

    def test_update_story_state_new(self, state_manager):
        """Test creating a new story state"""
        state_manager.update_story_state(
            story_id='001.1',
            epic_path='/path/to/epic.md',
            status='pending',
            iteration=0
        )

        # Verify state was saved
        state = state_manager.get_story_state('001.1')
        assert state is not None
        assert state['story_id'] == '001.1'
        assert state['status'] == 'pending'
        assert state['iteration'] == 0

    def test_update_story_state_existing(self, state_manager):
        """Test updating an existing story state"""
        # Create initial state
        state_manager.update_story_state(
            story_id='001.1',
            epic_path='/path/to/epic.md',
            status='pending',
            iteration=0
        )

        # Update to in_progress
        state_manager.update_story_state(
            story_id='001.1',
            epic_path='/path/to/epic.md',
            status='in_progress',
            iteration=1
        )

        # Verify update
        state = state_manager.get_story_state('001.1')
        assert state['status'] == 'in_progress'
        assert state['iteration'] == 1

    def test_get_story_state_not_found(self, state_manager):
        """Test retrieving a non-existent story"""
        state = state_manager.get_story_state('999.9')
        assert state is None

    def test_get_stories_by_status(self, state_manager):
        """Test filtering stories by status"""
        # Create stories with different statuses
        state_manager.update_story_state('001.1', '/path/to/epic.md', 'pass', 1)
        state_manager.update_story_state('001.2', '/path/to/epic.md', 'pending', 0)
        state_manager.update_story_state('001.3', '/path/to/epic.md', 'fail', 1)
        state_manager.update_story_state('001.4', '/path/to/epic.md', 'pass', 1)

        # Filter by status
        passed = state_manager.get_stories_by_status('pass')
        assert len(passed) == 2
        assert all(s['status'] == 'pass' for s in passed)

        pending = state_manager.get_stories_by_status('pending')
        assert len(pending) == 1
        assert pending[0]['story_id'] == '001.2'

    def test_get_all_stories(self, state_manager):
        """Test retrieving all stories"""
        # Create some stories
        state_manager.update_story_state('001.1', '/path/to/epic.md', 'pass', 1)
        state_manager.update_story_state('001.2', '/path/to/epic.md', 'pending', 0)
        state_manager.update_story_state('001.3', '/path/to/epic.md', 'fail', 1)

        # Get all stories
        all_stories = state_manager.get_all_stories()
        assert len(all_stories) == 3

        # Verify order
        story_ids = [s['story_id'] for s in all_stories]
        assert story_ids == ['001.1', '001.2', '001.3']

    def test_mark_story_in_progress(self, state_manager):
        """Test marking a story as in progress"""
        state_manager.mark_story_in_progress('001.1', '/path/to/epic.md')

        state = state_manager.get_story_state('001.1')
        assert state['status'] == 'in_progress'

    def test_mark_story_pass(self, state_manager):
        """Test marking a story as passed"""
        # First create the story
        state_manager.update_story_state('001.1', '/path/to/epic.md', 'in_progress', 1)

        # Mark as pass
        qa_result = {'tests_passed': 10, 'quality_score': 95}
        state_manager.mark_story_pass('001.1', qa_result)

        state = state_manager.get_story_state('001.1')
        assert state['status'] == 'pass'
        assert state['qa_result'] == qa_result
        assert state['completed_at'] is not None

    def test_mark_story_fail(self, state_manager):
        """Test marking a story as failed"""
        # First create the story
        state_manager.update_story_state('001.1', '/path/to/epic.md', 'in_progress', 1)

        # Mark as fail
        error_msg = "Implementation failed tests"
        state_manager.mark_story_fail('001.1', error_msg)

        state = state_manager.get_story_state('001.1')
        assert state['status'] == 'fail'
        assert state['error_message'] == error_msg
        assert state['completed_at'] is not None

    def test_mark_story_not_found(self, state_manager):
        """Test error when marking a non-existent story"""
        with pytest.raises(ValueError, match="Story 999.9 not found"):
            state_manager.mark_story_pass('999.9', {})

    def test_qa_result_serialization(self, state_manager):
        """Test that QA results are properly serialized/deserialized"""
        qa_result = {
            'tests_passed': 15,
            'tests_failed': 2,
            'quality_score': 92,
            'issues': ['Minor code style issue']
        }

        state_manager.update_story_state(
            story_id='001.1',
            epic_path='/path/to/epic.md',
            status='pass',
            iteration=1,
            qa_result=qa_result
        )

        state = state_manager.get_story_state('001.1')
        assert state['qa_result'] == qa_result

    def test_notes_storage(self, state_manager):
        """Test storing notes for different phases"""
        state_manager.update_story_state(
            story_id='001.1',
            epic_path='/path/to/epic.md',
            status='pass',
            iteration=1,
            sm_notes='SM phase completed successfully',
            dev_notes='Implementation done',
            qa_notes='All tests passed'
        )

        state = state_manager.get_story_state('001.1')
        assert state['sm_notes'] == 'SM phase completed successfully'
        assert state['dev_notes'] == 'Implementation done'
        assert state['qa_notes'] == 'All tests passed'

    def test_print_state_report_empty(self, state_manager, capsys):
        """Test printing state report with no stories"""
        state_manager.print_state_report()
        captured = capsys.readouterr()

        assert "No stories tracked yet" in captured.out

    def test_print_state_report_with_data(self, state_manager, capsys):
        """Test printing state report with stories"""
        # Create some stories
        state_manager.update_story_state('001.1', '/path/to/epic.md', 'pass', 1)
        state_manager.update_story_state('001.2', '/path/to/epic.md', 'pending', 0)
        state_manager.update_story_state('001.3', '/path/to/epic.md', 'fail', 1)

        state_manager.print_state_report()
        captured = capsys.readouterr()

        # Check summary
        assert "Total Stories: 3" in captured.out
        assert "✓ Passed: 1" in captured.out
        assert "✗ Failed: 1" in captured.out
        assert "⏸ Pending: 1" in captured.out
        assert "Success Rate:" in captured.out

        # Check detailed status
        assert "Story 001.1" in captured.out
        assert "Story 001.2" in captured.out
        assert "Story 001.3" in captured.out

    def test_reset_story(self, state_manager):
        """Test resetting a story to pending"""
        # Create a story that's completed
        state_manager.update_story_state('001.1', '/path/to/epic.md', 'pass', 1)

        # Reset it
        state_manager.reset_story('001.1')

        # Verify reset
        state = state_manager.get_story_state('001.1')
        assert state['status'] == 'pending'
        assert state['iteration'] == 0
        assert state['error_message'] is None

    def test_reset_story_not_found(self, state_manager):
        """Test error when resetting a non-existent story"""
        with pytest.raises(ValueError, match="Story 999.9 not found"):
            state_manager.reset_story('999.9')

    def test_clear_all_states(self, state_manager):
        """Test clearing all story states"""
        # Create some stories
        state_manager.update_story_state('001.1', '/path/to/epic.md', 'pass', 1)
        state_manager.update_story_state('001.2', '/path/to/epic.md', 'pending', 0)

        # Clear all
        state_manager.clear_all_states()

        # Verify all cleared
        all_stories = state_manager.get_all_stories()
        assert len(all_stories) == 0

    def test_multiple_iterations(self, state_manager):
        """Test tracking multiple iterations of a story"""
        # Iteration 1 - fails
        state_manager.update_story_state('001.1', '/path/to/epic.md', 'fail', 0)

        # Iteration 2 - still fails
        state_manager.update_story_state('001.1', '/path/to/epic.md', 'fail', 1)

        # Iteration 3 - passes
        state_manager.update_story_state('001.1', '/path/to/epic.md', 'pass', 2)

        state = state_manager.get_story_state('001.1')
        assert state['iteration'] == 2
        assert state['status'] == 'pass'

    def test_timestamps(self, state_manager):
        """Test that timestamps are properly set"""
        before_time = datetime.now()

        state_manager.update_story_state('001.1', '/path/to/epic.md', 'in_progress', 0)

        after_time = datetime.now()

        state = state_manager.get_story_state('001.1')
        assert state['created_at'] is not None
        assert state['updated_at'] is not None

        # Verify timestamps are reasonable
        created = datetime.fromisoformat(state['created_at'])
        updated = datetime.fromisoformat(state['updated_at'])

        assert before_time <= created <= after_time
        assert before_time <= updated <= after_time

    def test_concurrent_access(self, state_manager):
        """Test database handles concurrent access properly"""
        import threading

        results = []

        def create_story(story_id):
            try:
                state_manager.update_story_state(
                    story_id, '/path/to/epic.md', 'pending', 0
                )
                results.append(f"Success: {story_id}")
            except Exception as e:
                results.append(f"Error: {story_id} - {e}")

        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_story, args=(f'001.{i}',))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Verify all succeeded
        assert len(results) == 10
        assert all("Success" in result for result in results)

        # Verify all stories were created
        all_stories = state_manager.get_all_stories()
        assert len(all_stories) == 10
