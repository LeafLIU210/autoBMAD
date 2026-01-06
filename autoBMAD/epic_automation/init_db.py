#!/usr/bin/env python3
"""
Database Initialization Script for autoBMAD Epic Automation

This script creates and initializes the progress.db SQLite database
with all required tables and indexes for the BMAD automation system.

Usage:
    python init_db.py [options]

Options:
    --db-path PATH    Path to database file (default: progress.db)
    --force           Force recreation of existing database
    --verify          Verify existing database structure
    --verbose, -v     Enable verbose output
"""

import argparse
import sqlite3
import sys
from pathlib import Path


def create_tables(conn: sqlite3.Connection) -> None:
    """
    Create all required tables in the database.

    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()

    # Create stories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stories (
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
    ''')

    # Create index on story_path for faster lookups
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_story_path
        ON stories(story_path)
    ''')

    # Create index on status for filtering
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_status
        ON stories(status)
    ''')

    # Create code_quality_phase table (for quality gates)
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

    # Create test_automation_phase table (for test automation)
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

    # Create indexes for performance on epic_id columns
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_quality_epic
        ON code_quality_phase(epic_id)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_test_epic
        ON test_automation_phase(epic_id)
    ''')

    # Create epic_processing table (for tracking epic-level progress)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS epic_processing (
            epic_id TEXT PRIMARY KEY,
            file_path TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_stories INTEGER,
            completed_stories INTEGER,
            quality_phase_status TEXT DEFAULT 'pending',
            test_phase_status TEXT DEFAULT 'pending',
            quality_phase_errors INTEGER DEFAULT 0,
            test_phase_failures INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
    print("[OK] All tables created successfully")


def verify_tables(conn: sqlite3.Connection, verbose: bool = False) -> bool:
    """
    Verify that all required tables exist in the database.

    Args:
        conn: SQLite database connection
        verbose: Enable verbose output

    Returns:
        True if all tables exist, False otherwise
    """
    cursor = conn.cursor()

    # Get list of existing tables
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
        ORDER BY name
    """)
    existing_tables = {row[0] for row in cursor.fetchall()}

    # Required tables
    required_tables = {
        'stories',
        'code_quality_phase',
        'test_automation_phase',
        'epic_processing'
    }

    # Required indexes
    required_indexes = {
        'idx_story_path',
        'idx_status',
        'idx_quality_epic',
        'idx_test_epic'
    }

    # Check tables
    missing_tables = required_tables - existing_tables
    if missing_tables:
        print(f"[ERROR] Missing tables: {missing_tables}")
        return False

    if verbose:
        print(f"[OK] All {len(required_tables)} required tables exist")

    # Check indexes
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='index' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    existing_indexes = {row[0] for row in cursor.fetchall()}

    missing_indexes = required_indexes - existing_indexes
    if missing_indexes:
        print(f"[ERROR] Missing indexes: {missing_indexes}")
        return False

    if verbose:
        print(f"[OK] All {len(required_indexes)} required indexes exist")

    # Show table details if verbose
    if verbose:
        print("\nTable Details:")
        for table in sorted(required_tables):
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            print(f"\n  {table}:")
            for col in columns:
                print(f"    - {col[1]} ({col[2]})")

    return True


def check_database_exists(db_path: Path, force: bool = False) -> bool:
    """
    Check if database file exists and handle force option.

    Args:
        db_path: Path to database file
        force: If True, remove existing database

    Returns:
        True if database should be created, False otherwise
    """
    if db_path.exists():
        if force:
            print(f"[WARNING] Removing existing database: {db_path}")
            db_path.unlink()
            return True
        else:
            print(f"[WARNING] Database already exists: {db_path}")
            response = input("Do you want to verify the existing database? (y/n): ")
            return response.lower() == 'y'
    return True


def initialize_database(db_path: str, force: bool = False, verify_only: bool = False,
                       verbose: bool = False) -> int:
    """
    Initialize the database.

    Args:
        db_path: Path to database file
        force: Force recreation of existing database
        verify_only: Only verify existing database, don't create
        verbose: Enable verbose output

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Convert string path to Path object for type safety
    db_path_obj = Path(db_path).resolve()

    try:
        # Create directory if it doesn't exist
        db_path_obj.parent.mkdir(parents=True, exist_ok=True)

        if verify_only:
            # Only verify, don't create
            if not db_path_obj.exists():
                print(f"[ERROR] Database does not exist: {db_path_obj}")
                return 1

            conn = sqlite3.connect(db_path_obj)
            try:
                if verify_tables(conn, verbose):
                    print(f"[OK] Database verification successful: {db_path_obj}")
                    return 0
                else:
                    print(f"[ERROR] Database verification failed: {db_path_obj}")
                    return 1
            finally:
                conn.close()

        # Check if we should create database
        if not check_database_exists(db_path_obj, force):
            return 1

        # Create and initialize database
        print(f"Creating database: {db_path_obj}")
        conn = sqlite3.connect(db_path_obj)
        try:
            create_tables(conn)
            if verbose:
                print("\nVerifying database structure...")
            if verify_tables(conn, verbose):
                print(f"\n[OK] Database initialized successfully: {db_path_obj}")
                return 0
            else:
                print(f"\n[ERROR] Database verification failed: {db_path_obj}")
                return 1
        finally:
            conn.close()

    except PermissionError as e:
        print(f"[ERROR] Permission denied: {e}")
        return 1
    except Exception as e:
        print(f"[ERROR] Error initializing database: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Initialize autoBMAD Epic Automation Database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create database in default location (progress.db)
  python init_db.py

  # Create database at specific path
  python init_db.py --db-path /path/to/progress.db

  # Force recreation of existing database
  python init_db.py --force

  # Verify existing database
  python init_db.py --verify

  # Verify with verbose output
  python init_db.py --verify --verbose

  # Create with verbose output
  python init_db.py --verbose
        """
    )

    parser.add_argument(
        '--db-path',
        type=str,
        default='progress.db',
        help='Path to database file (default: progress.db)'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Force recreation of existing database'
    )

    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify existing database structure without creating'
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Initialize database
    exit_code = initialize_database(
        db_path=args.db_path,
        force=args.force,
        verify_only=args.verify,
        verbose=args.verbose
    )

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
