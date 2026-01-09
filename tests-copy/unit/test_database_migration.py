"""
Database Migration Tests for Story 001.1 - Extend State Management for Quality Gates

Tests cover:
- Migration script execution
- Database backup creation and verification
- Schema changes (new tables and indexes)
- Rollback functionality
- Backward compatibility
- Foreign key constraints

Author: Claude Code
Date: 2026-01-05
Story: 001.1 - Extend State Management for Quality Gates
"""

import sqlite3
import os
import tempfile
from pathlib import Path
from unittest.mock import patch
import uuid

import sys
sys.path.insert(0, os.path.abspath('..'))

from autoBMAD.epic_automation.migrations.migration_001_add_quality_gates import (
    run_migration,
    create_backup,
    verify_backup,
    rollback_migration
)


class TestMigrationBackup:
    """Test database backup functionality"""

    def test_create_backup_success(self):
        """Test successful backup creation"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test_table (id INTEGER);")
            cursor.execute("INSERT INTO test_table VALUES (1);")
            conn.commit()
            conn.close()

            backup_path = create_backup(Path(db_path))

            assert backup_path.exists()
            assert backup_path != Path(db_path)
            assert backup_path.stat().st_size > 0

            conn = sqlite3.connect(backup_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM test_table;")
            count = cursor.fetchone()[0]
            conn.close()

            assert count == 1

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
            if 'backup_path' in locals() and backup_path.exists():
                backup_path.unlink()

    def test_verify_backup_success(self):
        """Test successful backup verification"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test_table (id INTEGER);")
            conn.commit()
            conn.close()

            backup_path = create_backup(Path(db_path))
            result = verify_backup(backup_path)

            assert result is True

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
            if 'backup_path' in locals() and backup_path.exists():
                backup_path.unlink()

    def test_verify_backup_nonexistent(self):
        """Test verification of non-existent backup"""
        result = verify_backup(Path("/nonexistent/backup.db"))
        assert result is False

    def test_verify_backup_empty(self):
        """Test verification of empty backup file"""
        fd, backup_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        try:
            result = verify_backup(Path(backup_path))
            assert result is False

        finally:
            if os.path.exists(backup_path):
                os.unlink(backup_path)


class TestMigrationExecution:
    """Test migration script execution"""

    def test_migration_creates_tables(self):
        """Test that migration creates required tables"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE stories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    epic_path TEXT NOT NULL,
                    story_path TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL,
                    iteration INTEGER DEFAULT 0,
                    qa_result TEXT,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    phase TEXT
                )
            """)
            conn.commit()
            conn.close()

            success = run_migration(db_path)

            assert success is True

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='code_quality_phase'
            """)
            assert cursor.fetchone() is not None

            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='test_automation_phase'
            """)
            assert cursor.fetchone() is not None

            conn.close()

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_migration_creates_indexes(self):
        """Test that migration creates performance indexes"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE stories (id INTEGER PRIMARY KEY, status TEXT);")
            conn.commit()
            conn.close()

            run_migration(db_path)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='index' AND name='idx_quality_epic'
            """)
            assert cursor.fetchone() is not None

            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='index' AND name='idx_test_epic'
            """)
            assert cursor.fetchone() is not None

            conn.close()

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_migration_idempotent(self):
        """Test that running migration multiple times is safe"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE stories (id INTEGER PRIMARY KEY, status TEXT);")
            conn.commit()
            conn.close()

            success1 = run_migration(db_path)
            success2 = run_migration(db_path)

            assert success1 is True
            assert success2 is True

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
            table_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index';")
            index_count = cursor.fetchone()[0]

            conn.close()

            assert table_count > 0
            assert index_count >= 2

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_migration_nonexistent_db(self):
        """Test migration with non-existent database"""
        result = run_migration("/nonexistent/path/db.db")
        assert result is False


class TestBackwardCompatibility:
    """Test that migration maintains backward compatibility"""

    def test_existing_stories_table_preserved(self):
        """Test that existing stories table is preserved"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE stories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    epic_path TEXT NOT NULL,
                    story_path TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL,
                    iteration INTEGER DEFAULT 0,
                    qa_result TEXT,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    phase TEXT
                )
            """)

            cursor.execute("""
                INSERT INTO stories
                (epic_path, story_path, status, iteration)
                VALUES ('test-epic.md', 'test-story.md', 'in_progress', 1)
            """)

            conn.commit()
            conn.close()

            run_migration(db_path)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM stories;")
            rows = cursor.fetchall()
            assert len(rows) == 1
            assert rows[0][1] == 'test-epic.md'
            assert rows[0][2] == 'test-story.md'

            conn.close()

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_existing_stories_table_functional(self):
        """Test that existing stories table remains functional after migration"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE stories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    epic_path TEXT NOT NULL,
                    story_path TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL,
                    iteration INTEGER DEFAULT 0
                )
            """)
            conn.commit()
            conn.close()

            success = run_migration(db_path)
            assert success is True

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO stories (epic_path, story_path, status)
                VALUES ('new-epic.md', 'new-story.md', 'completed')
            """)

            cursor.execute("SELECT * FROM stories WHERE story_path = 'new-story.md';")
            row = cursor.fetchone()

            assert row is not None
            assert row[1] == 'new-epic.md'
            assert row[2] == 'new-story.md'

            conn.close()

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestForeignKeyConstraints:
    """Test foreign key constraints on new tables"""

    def test_quality_phase_foreign_key(self):
        """Test code_quality_phase foreign key constraint"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE stories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    epic_path TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL
                )
            """)
            cursor.execute("INSERT INTO stories (epic_path, status) VALUES ('test-epic.md', 'active');")
            conn.commit()
            conn.close()

            run_migration(db_path)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("PRAGMA foreign_keys = ON;")

            cursor.execute("""
                INSERT INTO code_quality_phase
                (record_id, epic_id, file_path, error_count)
                VALUES (?, ?, ?, ?)
            """, (str(uuid.uuid4()), 'test-epic.md', 'test.py', 0))

            conn.commit()
            conn.close()

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_test_phase_foreign_key(self):
        """Test test_automation_phase foreign key constraint"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE stories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    epic_path TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL
                )
            """)
            cursor.execute("INSERT INTO stories (epic_path, status) VALUES ('test-epic.md', 'active');")
            conn.commit()
            conn.close()

            run_migration(db_path)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("PRAGMA foreign_keys = ON;")

            cursor.execute("""
                INSERT INTO test_automation_phase
                (record_id, epic_id, test_file_path, failure_count)
                VALUES (?, ?, ?, ?)
            """, (str(uuid.uuid4()), 'test-epic.md', 'test.py', 0))

            conn.commit()
            conn.close()

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestRollback:
    """Test rollback functionality"""

    def test_rollback_restores_database(self):
        """Test that rollback restores database to previous state"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE old_table (id INTEGER);")
            cursor.execute("INSERT INTO old_table VALUES (42);")
            conn.commit()
            conn.close()

            backup_path = create_backup(Path(db_path))

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE new_table (id INTEGER);")
            conn.commit()
            conn.close()

            success = rollback_migration(Path(db_path), backup_path)
            assert success is True

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]

            assert 'old_table' in tables
            assert 'new_table' not in tables

            cursor.execute("SELECT * FROM old_table;")
            row = cursor.fetchone()
            assert row[0] == 42

            conn.close()

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
            if 'backup_path' in locals() and backup_path.exists():
                backup_path.unlink()

    def test_rollback_nonexistent_backup(self):
        """Test rollback with non-existent backup"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        try:
            success = rollback_migration(Path(db_path), Path("/nonexistent/backup.db"))
            assert success is False

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestMigrationErrorHandling:
    """Test error handling during migration"""

    def test_migration_with_invalid_db_path(self):
        """Test migration with invalid database path"""
        invalid_path = "/invalid/path/to/database.db"
        result = run_migration(invalid_path)
        assert result is False

    @patch('shutil.copy2')
    def test_migration_backup_failure(self, mock_copy):
        """Test migration handles backup failure gracefully"""
        mock_copy.side_effect = Exception("Disk full")

        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        try:
            result = run_migration(db_path)
            assert result is False

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestTableStructure:
    """Test detailed table structure validation"""

    def test_code_quality_phase_table_structure(self):
        """Test code_quality_phase table has correct structure"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE stories (id INTEGER PRIMARY KEY, status TEXT);")
            conn.commit()
            conn.close()

            success = run_migration(db_path)
            assert success is True

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("PRAGMA table_info(code_quality_phase);")
            columns = {col[1]: col[2] for col in cursor.fetchall()}

            assert 'record_id' in columns
            assert 'epic_id' in columns
            assert 'file_path' in columns
            assert 'error_count' in columns
            assert 'fix_status' in columns
            assert 'basedpyright_errors' in columns
            assert 'ruff_errors' in columns
            assert 'timestamp' in columns

            assert columns['record_id'] == 'TEXT'
            assert columns['epic_id'] == 'TEXT'
            assert columns['error_count'] == 'INTEGER'

            conn.close()

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_test_automation_phase_table_structure(self):
        """Test test_automation_phase table has correct structure"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE stories (id INTEGER PRIMARY KEY, status TEXT);")
            conn.commit()
            conn.close()

            success = run_migration(db_path)
            assert success is True

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("PRAGMA table_info(test_automation_phase);")
            columns = {col[1]: col[2] for col in cursor.fetchall()}

            assert 'record_id' in columns
            assert 'epic_id' in columns
            assert 'test_file_path' in columns
            assert 'failure_count' in columns
            assert 'fix_status' in columns
            assert 'debug_info' in columns
            assert 'timestamp' in columns

            assert columns['record_id'] == 'TEXT'
            assert columns['epic_id'] == 'TEXT'
            assert columns['failure_count'] == 'INTEGER'

            conn.close()

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
