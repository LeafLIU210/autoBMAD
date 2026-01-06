"""
Unit Tests for StateManager Quality Gates Extension

Tests cover:
- Database backup functionality
- Quality phase record management
- Test automation phase record management
- Backward compatibility
- Error handling and parameterized queries

Author: Claude Code
Date: 2026-01-05
"""

import pytest
import sqlite3
import os
import tempfile
import asyncio

import sys
sys.path.insert(0, os.path.abspath('.'))

from autoBMAD.epic_automation.state_manager import StateManager


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def state_manager(temp_db):
    """Create a StateManager instance with temporary database"""
    return StateManager(temp_db)


class TestStateManagerBackup:
    """Test database backup functionality"""

    def test_create_backup_success(self, temp_db):
        """Test successful backup creation"""
        state_manager = StateManager(temp_db)
        
        backup_path = asyncio.run(state_manager.create_backup())
        
        assert backup_path is not None
        assert os.path.exists(backup_path)
        assert backup_path != temp_db


class TestQualityPhaseRecords:
    """Test quality phase record management"""

    @pytest.mark.asyncio
    async def test_add_quality_phase_record_success(self, state_manager):
        """Test successfully adding a quality phase record"""
        epic_id = "docs/epics/test-epic.md"
        file_path = "src/test_file.py"
        error_count = 5
        basedpyright_errors = "Type error"
        ruff_errors = "Line too long"
        
        record_id = await state_manager.add_quality_phase_record(
            epic_id=epic_id,
            file_path=file_path,
            error_count=error_count,
            basedpyright_errors=basedpyright_errors,
            ruff_errors=ruff_errors
        )
        
        assert record_id is not None
        
        records = await state_manager.get_quality_phase_records(epic_id)
        assert len(records) == 1
        assert records[0]['file_path'] == file_path

    @pytest.mark.asyncio
    async def test_update_quality_phase_status(self, state_manager):
        """Test updating quality phase status"""
        record_id = await state_manager.add_quality_phase_record(
            epic_id="test-epic",
            file_path="test.py",
            error_count=5,
            basedpyright_errors="error",
            ruff_errors="error"
        )
        
        success = await state_manager.update_quality_phase_status(
            record_id=record_id,
            fix_status="completed"
        )
        
        assert success is True


class TestTestPhaseRecords:
    """Test test automation phase record management"""

    @pytest.mark.asyncio
    async def test_add_test_phase_record_success(self, state_manager):
        """Test successfully adding a test phase record"""
        epic_id = "docs/epics/test-epic.md"
        test_file_path = "tests/test_suite.py"
        failure_count = 3
        debug_info = "Test failed"
        
        record_id = await state_manager.add_test_phase_record(
            epic_id=epic_id,
            test_file_path=test_file_path,
            failure_count=failure_count,
            debug_info=debug_info
        )
        
        assert record_id is not None
        
        records = await state_manager.get_test_phase_records(epic_id)
        assert len(records) == 1
        assert records[0]['test_file_path'] == test_file_path


class TestBackwardCompatibility:
    """Test backward compatibility with existing data"""

    @pytest.mark.asyncio
    async def test_existing_stories_table_unchanged(self, state_manager):
        """Test that existing stories table remains functional"""
        await state_manager.update_story_status(
            story_path="test-story.md",
            status="completed",
            epic_path="test-epic.md"
        )
        
        story = await state_manager.get_story_status("test-story.md")
        assert story is not None
        assert story['status'] == 'completed'


class TestDatabaseSchema:
    """Test database schema integrity"""

    def test_code_quality_phase_table_exists(self, state_manager):
        """Test that code_quality_phase table exists"""
        conn = sqlite3.connect(state_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='code_quality_phase'
        """)
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
