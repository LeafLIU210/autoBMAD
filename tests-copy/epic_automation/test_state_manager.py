"""
Tests for StateManager class.

Tests the SQLite state management functionality including:
- Database initialization
- Story state CRUD operations (async)
- Progress tracking
- State persistence and recovery
"""

import pytest
import tempfile
import shutil
import asyncio
from pathlib import Path

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

        # Verify tables were created by checking directly with sqlite
        import sqlite3
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        assert 'stories' in tables
        conn.close()

    @pytest.mark.asyncio
    async def test_update_story_status_new(self, state_manager):
        """Test creating a new story status"""
        result = await state_manager.update_story_status(
            story_path='/path/to/story/001.1.md',
            status='pending',
            phase='sm',
            iteration=0,
            epic_path='/path/to/epic.md'
        )

        assert result is True

        # Verify state was saved
        state = await state_manager.get_story_status('/path/to/story/001.1.md')
        assert state is not None
        assert state['story_path'] == '/path/to/story/001.1.md'
        assert state['status'] == 'pending'
        assert state['iteration'] == 0

    @pytest.mark.asyncio
    async def test_update_story_status_existing(self, state_manager):
        """Test updating an existing story status"""
        # Create initial state
        await state_manager.update_story_status(
            story_path='/path/to/story/001.1.md',
            status='pending',
            phase='sm',
            iteration=0,
            epic_path='/path/to/epic.md'
        )

        # Update to in_progress
        await state_manager.update_story_status(
            story_path='/path/to/story/001.1.md',
            status='in_progress',
            phase='dev',
            iteration=1
        )

        # Verify update
        state = await state_manager.get_story_status('/path/to/story/001.1.md')
        assert state['status'] == 'in_progress'
        assert state['iteration'] == 1

    @pytest.mark.asyncio
    async def test_get_story_status_not_found(self, state_manager):
        """Test retrieving a non-existent story"""
        state = await state_manager.get_story_status('/nonexistent/story.md')
        assert state is None

    @pytest.mark.asyncio
    async def test_get_stories_by_status(self, state_manager):
        """Test filtering stories by status"""
        # Create stories with different statuses
        await state_manager.update_story_status('/story/001.1.md', 'completed', epic_path='/epic.md')
        await state_manager.update_story_status('/story/001.2.md', 'pending', epic_path='/epic.md')
        await state_manager.update_story_status('/story/001.3.md', 'failed', epic_path='/epic.md')
        await state_manager.update_story_status('/story/001.4.md', 'completed', epic_path='/epic.md')

        # Filter by status
        completed = await state_manager.get_stories_by_status('completed')
        assert len(completed) == 2
        assert all(s['status'] == 'completed' for s in completed)

        pending = await state_manager.get_stories_by_status('pending')
        assert len(pending) == 1

    @pytest.mark.asyncio
    async def test_get_all_stories(self, state_manager):
        """Test retrieving all stories"""
        # Create some stories
        await state_manager.update_story_status('/story/001.1.md', 'completed', epic_path='/epic.md')
        await state_manager.update_story_status('/story/001.2.md', 'pending', epic_path='/epic.md')
        await state_manager.update_story_status('/story/001.3.md', 'failed', epic_path='/epic.md')

        # Get all stories
        all_stories = await state_manager.get_all_stories()
        assert len(all_stories) == 3

    @pytest.mark.asyncio
    async def test_update_story_in_progress(self, state_manager):
        """Test marking a story as in progress"""
        await state_manager.update_story_status(
            story_path='/story/001.1.md',
            status='in_progress',
            phase='dev',
            epic_path='/epic.md'
        )

        state = await state_manager.get_story_status('/story/001.1.md')
        assert state['status'] == 'in_progress'

    @pytest.mark.asyncio
    async def test_update_story_completed(self, state_manager):
        """Test marking a story as completed"""
        # First create the story
        await state_manager.update_story_status(
            story_path='/story/001.1.md',
            status='in_progress',
            phase='qa',
            iteration=1,
            epic_path='/epic.md'
        )

        # Mark as completed with qa_result
        qa_result = {'tests_passed': 10, 'quality_score': 95}
        await state_manager.update_story_status(
            story_path='/story/001.1.md',
            status='completed',
            phase='qa',
            qa_result=qa_result
        )

        state = await state_manager.get_story_status('/story/001.1.md')
        assert state['status'] == 'completed'
        assert state['qa_result'] is not None

    @pytest.mark.asyncio
    async def test_update_story_failed(self, state_manager):
        """Test marking a story as failed"""
        # First create the story
        await state_manager.update_story_status(
            story_path='/story/001.1.md',
            status='in_progress',
            phase='dev',
            iteration=1,
            epic_path='/epic.md'
        )

        # Mark as failed
        error_msg = "Implementation failed tests"
        await state_manager.update_story_status(
            story_path='/story/001.1.md',
            status='failed',
            error=error_msg
        )

        state = await state_manager.get_story_status('/story/001.1.md')
        assert state['status'] == 'failed'
        assert state['error'] == error_msg

    @pytest.mark.asyncio
    async def test_delete_story_not_found(self, state_manager):
        """Test deleting a non-existent story (should still return True)"""
        result = await state_manager.delete_story('/nonexistent/story.md')
        assert result is True  # SQLite DELETE doesn't fail for non-existent rows

    @pytest.mark.asyncio
    async def test_qa_result_serialization(self, state_manager):
        """Test that QA results are properly serialized/deserialized"""
        qa_result = {
            'tests_passed': 15,
            'tests_failed': 2,
            'quality_score': 92,
            'issues': ['Minor code style issue']
        }

        await state_manager.update_story_status(
            story_path='/story/001.1.md',
            status='completed',
            phase='qa',
            iteration=1,
            qa_result=qa_result,
            epic_path='/epic.md'
        )

        state = await state_manager.get_story_status('/story/001.1.md')
        assert state['qa_result'] == qa_result

    @pytest.mark.asyncio
    async def test_phase_storage(self, state_manager):
        """Test storing phase information"""
        await state_manager.update_story_status(
            story_path='/story/001.1.md',
            status='in_progress',
            phase='dev',
            iteration=1,
            epic_path='/epic.md'
        )

        state = await state_manager.get_story_status('/story/001.1.md')
        assert state['phase'] == 'dev'

    @pytest.mark.asyncio
    async def test_get_stats(self, state_manager):
        """Test getting statistics"""
        # Create stories with different statuses
        await state_manager.update_story_status('/story/001.1.md', 'completed', epic_path='/epic.md')
        await state_manager.update_story_status('/story/001.2.md', 'pending', epic_path='/epic.md')
        await state_manager.update_story_status('/story/001.3.md', 'failed', epic_path='/epic.md')
        await state_manager.update_story_status('/story/001.4.md', 'completed', epic_path='/epic.md')

        stats = await state_manager.get_stats()
        assert stats.get('completed', 0) == 2
        assert stats.get('pending', 0) == 1
        assert stats.get('failed', 0) == 1

    @pytest.mark.asyncio
    async def test_delete_story(self, state_manager):
        """Test deleting a story"""
        # Create a story
        await state_manager.update_story_status('/story/001.1.md', 'completed', epic_path='/epic.md')

        # Delete it
        result = await state_manager.delete_story('/story/001.1.md')
        assert result is True

        # Verify deleted
        state = await state_manager.get_story_status('/story/001.1.md')
        assert state is None

    @pytest.mark.asyncio
    async def test_multiple_iterations(self, state_manager):
        """Test tracking multiple iterations of a story"""
        # Iteration 1 - fails
        await state_manager.update_story_status('/story/001.1.md', 'failed', iteration=0, epic_path='/epic.md')

        # Iteration 2 - still fails
        await state_manager.update_story_status('/story/001.1.md', 'failed', iteration=1)

        # Iteration 3 - passes
        await state_manager.update_story_status('/story/001.1.md', 'completed', iteration=2)

        state = await state_manager.get_story_status('/story/001.1.md')
        assert state['iteration'] == 2
        assert state['status'] == 'completed'

    @pytest.mark.asyncio
    async def test_timestamps(self, state_manager):
        """Test that timestamps are set"""
        await state_manager.update_story_status('/story/001.1.md', 'in_progress', epic_path='/epic.md')

        state = await state_manager.get_story_status('/story/001.1.md')
        assert state['created_at'] is not None
        assert state['updated_at'] is not None

    @pytest.mark.asyncio
    async def test_concurrent_access(self, state_manager):
        """Test database handles concurrent access properly"""
        async def create_story(story_path):
            try:
                await state_manager.update_story_status(
                    story_path, 'pending', epic_path='/epic.md'
                )
                return f"Success: {story_path}"
            except Exception as e:
                return f"Error: {story_path} - {e}"

        # Create multiple tasks
        tasks = [create_story(f'/story/001.{i}.md') for i in range(10)]
        results = await asyncio.gather(*tasks)

        # Verify all succeeded
        assert len(results) == 10
        assert all("Success" in result for result in results)

        # Verify all stories were created
        all_stories = await state_manager.get_all_stories()
        assert len(all_stories) == 10
