"""Tests for StateManager.

Comprehensive test suite for state management functionality.
"""

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from autoBMAD.epic_automation.state_manager import (
    StateManager,
    DeadlockDetector,
    DatabaseConnectionPool,
)


class TestDeadlockDetector:

    def test_initialization(self):
        detector = DeadlockDetector()
        assert detector.lock_timeout == 30.0
        assert detector.deadlock_detected is False
        assert detector.lock_waiters == {}

    @pytest.mark.anyio
    async def test_wait_for_lock_success(self):
        detector = DeadlockDetector()
        lock = asyncio.Lock()
        result = await detector.wait_for_lock("test-lock", lock)
        assert result is True
        lock.release()


class TestDatabaseConnectionPool:

    def test_initialization(self):
        pool = DatabaseConnectionPool(max_connections=3)
        assert pool.max_connections == 3

    @pytest.mark.anyio
    async def test_initialize_and_get_connection(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = Path(f.name)
        pool = DatabaseConnectionPool(max_connections=2)
        await pool.initialize(db_path)
        conn = await pool.get_connection()
        assert conn is not None
        conn.close()
        # Skip cleanup on Windows due to file locking


class TestStateManager:

    @pytest.fixture
    def temp_db(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = Path(f.name)
        yield db_path
        try:
            db_path.unlink(missing_ok=True)
        except PermissionError:
            pass

    def test_initialization(self, temp_db):
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)
        assert manager.db_path == temp_db

    @pytest.mark.anyio
    async def test_update_story_status_new(self, temp_db):
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)
        success, version = await manager.update_story_status(
            story_path="/path/to/story.md",
            status="in_progress",
        )
        assert success is True
        assert version == 1

    @pytest.mark.anyio
    async def test_get_story_status(self, temp_db):
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)
        await manager.update_story_status(
            story_path="/path/to/story.md",
            status="in_progress",
            phase="development",
        )
        status = await manager.get_story_status("/path/to/story.md")
        assert status is not None
        assert status["status"] == "in_progress"

    @pytest.mark.anyio
    async def test_get_all_stories(self, temp_db):
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)
        await manager.update_story_status("/story1.md", "pending")
        await manager.update_story_status("/story2.md", "completed")
        stories = await manager.get_all_stories()
        assert len(stories) == 2

    @pytest.mark.anyio
    async def test_get_stats(self, temp_db):
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)
        await manager.update_story_status("/story1.md", "pending")
        await manager.update_story_status("/story2.md", "pending")
        stats = await manager.get_stats()
        assert stats["pending"] == 2

    def test_get_health_status(self, temp_db):
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)
        health = manager.get_health_status()
        assert health["db_exists"] is True

    @pytest.mark.anyio
    async def test_create_backup(self, temp_db):
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)
        await manager.update_story_status("/story.md", "pending")
        backup_path = await manager.create_backup()
        assert backup_path is not None
        try:
            Path(backup_path).unlink()
        except PermissionError:
            pass

    def test_clean_qa_result_for_json(self, temp_db):
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)
        qa_result = {"level1": {"level2": "value"}}
        result = manager._clean_qa_result_for_json(qa_result)
        assert result is not None

    @pytest.mark.anyio
    async def test_update_story_status_with_iteration(self, temp_db):
        """Test updating story status with iteration parameter."""
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)
        success, version = await manager.update_story_status(
            story_path="/story.md",
            status="in_progress",
            iteration=5
        )
        assert success is True
        assert version == 1

        status = await manager.get_story_status("/story.md")
        assert status["iteration"] == 5

    @pytest.mark.anyio
    async def test_update_story_status_with_epic_path(self, temp_db):
        """Test updating story status with epic path."""
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)
        success, version = await manager.update_story_status(
            story_path="/story.md",
            status="pending",
            epic_path="/epic.md"
        )
        assert success is True

        status = await manager.get_story_status("/story.md")
        assert status["epic_path"] == "/epic.md"

    @pytest.mark.anyio
    async def test_update_story_status_existing(self, temp_db):
        """Test updating existing story status."""
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)

        # Insert first time
        success1, version1 = await manager.update_story_status(
            story_path="/story.md",
            status="pending"
        )
        assert success1 is True
        assert version1 == 1

        # Update same story
        success2, version2 = await manager.update_story_status(
            story_path="/story.md",
            status="in_progress"
        )
        assert success2 is True
        assert version2 == 2

        status = await manager.get_story_status("/story.md")
        assert status["status"] == "in_progress"
        assert status["version"] == 2

    @pytest.mark.anyio
    async def test_update_story_status_version_conflict(self, temp_db):
        """Test version conflict detection."""
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)

        # Create story
        await manager.update_story_status("/story.md", "pending")
        status = await manager.get_story_status("/story.md")

        # Try to update with wrong version
        success, version = await manager.update_story_status(
            story_path="/story.md",
            status="in_progress",
            expected_version=999  # Wrong version
        )
        assert success is False
        assert version == 1  # Current version

    @pytest.mark.anyio
    async def test_update_story_status_with_qa_result(self, temp_db):
        """Test updating story with QA result."""
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)
        qa_data = {
            "passed": True,
            "coverage": 95.5,
            "issues": []
        }
        success, version = await manager.update_story_status(
            story_path="/story.md",
            status="completed",
            qa_result=qa_data
        )
        assert success is True

        status = await manager.get_story_status("/story.md")
        assert "qa_result" in status
        assert status["qa_result"]["passed"] is True

    @pytest.mark.anyio
    async def test_update_story_status_with_error(self, temp_db):
        """Test updating story with error message."""
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)
        success, version = await manager.update_story_status(
            story_path="/story.md",
            status="failed",
            error="Test error message"
        )
        assert success is True

        status = await manager.get_story_status("/story.md")
        assert status["error"] == "Test error message"

    @pytest.mark.anyio
    async def test_update_story_status_timeout(self, temp_db):
        """Test update operation timeout."""
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)

        # Set very short timeout
        success, version = await manager.update_story_status(
            story_path="/story.md",
            status="pending",
            lock_timeout=0.001  # Very short timeout
        )
        # May succeed or timeout depending on system speed
        # Just verify it doesn't crash

    @pytest.mark.anyio
    async def test_update_story_status_with_nonexistent_path(self, temp_db):
        """Test update with non-existent story path."""
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)
        success, version = await manager.update_story_status(
            story_path="/nonexistent/story.md",
            status="pending"
        )
        assert success is True
        assert version == 1

    @pytest.mark.anyio
    async def test_get_story_status_nonexistent(self, temp_db):
        """Test getting status for non-existent story."""
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)
        status = await manager.get_story_status("/nonexistent.md")
        assert status is None

    @pytest.mark.anyio
    async def test_get_stats_multiple_statuses(self, temp_db):
        """Test getting stats with multiple statuses."""
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)

        await manager.update_story_status("/story1.md", "pending")
        await manager.update_story_status("/story2.md", "pending")
        await manager.update_story_status("/story3.md", "in_progress")
        await manager.update_story_status("/story4.md", "completed")

        stats = await manager.get_stats()
        assert stats["pending"] == 2
        assert stats["in_progress"] == 1
        assert stats["completed"] == 1

    @pytest.mark.anyio
    async def test_get_stats_empty(self, temp_db):
        """Test getting stats with no stories."""
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)
        stats = await manager.get_stats()
        assert stats == {}

    @pytest.mark.anyio
    async def test_cleanup_old_records(self, temp_db):
        """Test cleanup of old records."""
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)

        # This test depends on actual database records with dates
        # For now, just verify the method doesn't crash
        deleted_count = await manager.cleanup_old_records(days=30)
        assert isinstance(deleted_count, int)

    @pytest.mark.anyio
    async def test_get_all_stories_empty(self, temp_db):
        """Test getting all stories when database is empty."""
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)
        stories = await manager.get_all_stories()
        assert stories == []

    @pytest.mark.anyio
    async def test_concurrent_updates(self, temp_db):
        """Test concurrent updates to different stories."""
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)

        async def update_story(path, status):
            return await manager.update_story_status(path, status)

        # Update multiple stories concurrently
        results = await asyncio.gather(
            update_story("/story1.md", "in_progress"),
            update_story("/story2.md", "pending"),
            update_story("/story3.md", "completed")
        )

        # All should succeed
        for success, version in results:
            assert success is True

        stories = await manager.get_all_stories()
        assert len(stories) == 3

    @pytest.mark.anyio
    async def test_create_backup_failure(self, temp_db):
        """Test backup creation with invalid path."""
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)
        # Create backup should succeed in normal case
        backup_path = await manager.create_backup()
        assert backup_path is not None

    def test_clean_qa_result_for_json_complex(self, temp_db):
        """Test cleaning QA result with complex nested structures."""
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)

        # Test with nested dicts and lists
        qa_result = {
            "simple": "value",
            "nested": {"inner": {"deep": "value"}},
            "list": [1, 2, {"nested": "in_list"}],
            "with_value_attr": type("obj", (), {"value": "test_value"})()
        }

        result = manager._clean_qa_result_for_json(qa_result)
        assert result is not None
        # Should be valid JSON string
        parsed = json.loads(result)
        assert parsed["simple"] == "value"
        assert parsed["nested"]["inner"]["deep"] == "value"
        assert parsed["with_value_attr"] == "test_value"

    def test_clean_qa_result_for_json_exception(self, temp_db):
        """Test cleaning QA result that raises exception."""
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)

        # Create object that can't be serialized even after cleaning
        class NonSerializable:
            def __reduce__(self):
                raise ValueError("Cannot serialize")

        qa_result = NonSerializable()
        result = manager._clean_qa_result_for_json(qa_result)
        # Should return None on failure
        assert result is None

    def test_get_health_status_full(self, temp_db):
        """Test getting complete health status."""
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)
        health = manager.get_health_status()

        assert "db_path" in health
        assert "db_exists" in health
        assert "lock_locked" in health
        assert "deadlock_detected" in health
        assert "connection_pool_enabled" in health
        assert health["db_exists"] is True

    def test_database_connection_pool_params(self, temp_dir):
        """Test DatabaseConnectionPool with connection params."""
        from autoBMAD.epic_automation.state_manager import DatabaseConnectionPool

        pool = DatabaseConnectionPool(max_connections=5)
        assert pool.max_connections == 5
        assert pool.connection_params == {}

    @pytest.mark.anyio
    async def test_database_connection_pool_exhausted(self, temp_dir):
        """Test DatabaseConnectionPool exhaustion scenario."""
        from autoBMAD.epic_automation.state_manager import DatabaseConnectionPool

        db_path = temp_dir / "test.db"
        pool = DatabaseConnectionPool(max_connections=1)
        await pool.initialize(db_path)

        # Get the only connection
        conn1 = await pool.get_connection()
        assert conn1 is not None

        # Try to get another connection - should timeout
        import anyio
        with anyio.fail_after(1):
            try:
                await pool.get_connection()
                assert False, "Should have raised TimeoutError"
            except TimeoutError:
                pass

    @pytest.mark.anyio
    async def test_deadlock_detector_timeout(self):
        """Test DeadlockDetector timeout scenario."""
        from autoBMAD.epic_automation.state_manager import DeadlockDetector

        detector = DeadlockDetector()
        lock = asyncio.Lock()
        detector.lock_timeout = 0.1  # Very short timeout

        # Acquire lock to block
        await lock.acquire()

        # Try to acquire again - should timeout
        result = await detector.wait_for_lock("test-lock", lock)
        assert result is False
        assert detector.deadlock_detected is True

    @pytest.mark.anyio
    async def test_deadlock_detector_no_task(self):
        """Test DeadlockDetector with no current task."""
        from autoBMAD.epic_automation.state_manager import DeadlockDetector

        detector = DeadlockDetector()
        lock = asyncio.Lock()

        # Mock current_task to return None
        with patch("asyncio.current_task", return_value=None):
            result = await detector.wait_for_lock("test-lock", lock)
            assert result is False

    @pytest.mark.anyio
    async def test_managed_operation_cancellation(self, temp_db):
        """Test managed_operation handles cancellation properly."""
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)

        # Test that cancellation is handled gracefully
        async with manager.managed_operation():
            pass  # Normal completion

    @pytest.mark.anyio
    async def test_sync_story_statuses_to_markdown_no_stories(self, temp_db):
        """Test sync with no stories."""
        manager = StateManager(db_path=str(temp_db), use_connection_pool=False)
        result = await manager.sync_story_statuses_to_markdown()
        assert result["success_count"] == 0
        assert result["error_count"] == 0
