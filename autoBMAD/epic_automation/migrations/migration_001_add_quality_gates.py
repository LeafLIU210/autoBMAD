"""
Migration Script 001: Add Quality Gates Support

This migration adds support for tracking code quality and test automation phases
in the BMAD automation system database.

Migration: 001
Date: 2026-01-05
Description: Add code_quality_phase and test_automation_phase tables with indexes

Changes:
- Add code_quality_phase table for tracking basedpyright and ruff errors
- Add test_automation_phase table for tracking test failures and debug info
- Add indexes on epic_id columns for performance
- Maintain 100% backward compatibility with existing data
"""

import sqlite3
import shutil
import os
from pathlib import Path
from datetime import datetime
from typing import Union
import logging

logger = logging.getLogger(__name__)


def create_backup(db_path: Path) -> Path:
    """
    Create a timestamped backup of the database.

    Args:
        db_path: Path to the database file

    Returns:
        Path to the backup file

    Raises:
        Exception: If backup creation fails
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = db_path.parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    backup_path = backup_dir / f"{db_path.stem}_backup_{timestamp}{db_path.suffix}"

    shutil.copy2(db_path, backup_path)
    logger.info(f"Database backup created: {backup_path}")
    return backup_path


def verify_backup(backup_path: Path) -> bool:
    """
    Verify that the backup file was created successfully.

    Args:
        backup_path: Path to the backup file

    Returns:
        True if backup is valid, False otherwise
    """
    try:
        if not backup_path.exists():
            logger.error(f"Backup file does not exist: {backup_path}")
            return False

        if backup_path.stat().st_size == 0:
            logger.error(f"Backup file is empty: {backup_path}")
            return False

        conn = sqlite3.connect(backup_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()

        if not tables:
            logger.error(f"Backup file has no tables: {backup_path}")
            return False

        logger.info(f"Backup verified successfully: {backup_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to verify backup: {e}")
        return False


def rollback_migration(db_path: Path, backup_path: Path) -> bool:
    """
    Rollback migration by restoring from backup.

    Args:
        db_path: Path to the database file
        backup_path: Path to the backup file

    Returns:
        True if rollback successful, False otherwise
    """
    try:
        if backup_path.exists():
            shutil.copy2(backup_path, db_path)
            logger.info(f"Database rolled back from backup: {backup_path}")
            return True
        else:
            logger.error(f"Backup file not found for rollback: {backup_path}")
            return False

    except Exception as e:
        logger.error(f"Failed to rollback: {e}")
        return False


def run_migration(db_path: Union[str, Path]) -> bool:
    """
    Execute the migration to add quality gates support.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        True if migration successful, False otherwise
    """
    # Ensure db_path is a Path object for consistent type handling
    db_path_obj = Path(db_path) if isinstance(db_path, str) else db_path

    try:
        logger.info(f"Starting migration: {db_path_obj}")

        if not db_path_obj.exists():
            logger.error(f"Database file not found: {db_path_obj}")
            return False

        backup_path = create_backup(db_path_obj)

        if not verify_backup(backup_path):
            logger.error("Backup verification failed, aborting migration")
            return False

        conn = sqlite3.connect(db_path_obj)
        cursor = conn.cursor()

        logger.info("Creating code_quality_phase table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_quality_phase (
                record_id TEXT PRIMARY KEY,
                epic_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                error_count INTEGER DEFAULT 0,
                fix_status TEXT DEFAULT 'pending',
                basedpyright_errors TEXT,
                ruff_errors TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (epic_id) REFERENCES stories(epic_path)
            )
        ''')

        logger.info("Creating test_automation_phase table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_automation_phase (
                record_id TEXT PRIMARY KEY,
                epic_id TEXT NOT NULL,
                test_file_path TEXT NOT NULL,
                failure_count INTEGER DEFAULT 0,
                fix_status TEXT DEFAULT 'pending',
                debug_info TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (epic_id) REFERENCES stories(epic_path)
            )
        ''')

        logger.info("Creating indexes for performance...")
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_quality_epic
            ON code_quality_phase(epic_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_test_epic
            ON test_automation_phase(epic_id)
        ''')

        conn.commit()
        conn.close()

        logger.info("Migration completed successfully!")
        logger.info(f"Backup available at: {backup_path}")

        return True

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        logger.error("Attempting rollback...")

        import glob
        # Create backup pattern using the Path object
        backup_pattern = str(db_path_obj.parent / f"{db_path_obj.stem}_backup_*")
        backups = glob.glob(backup_pattern)
        if backups:
            latest_backup = max(backups, key=os.path.getctime)
            rollback_migration(db_path_obj, Path(latest_backup))
        return False


def main():
    """Main entry point for the migration script."""
    db_path = os.environ.get('BMAD_DB_PATH', 'progress.db')
    success = run_migration(db_path)

    exit(0 if success else 1)

