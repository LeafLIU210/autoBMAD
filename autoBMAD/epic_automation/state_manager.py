"""
State Manager - SQLite-based State Management

Handles progress tracking and state persistence for BMAD automation.
"""

import json
import sqlite3
import asyncio
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Union
import logging
import uuid
from enum import Enum

logger = logging.getLogger(__name__)


class StoryStatus(Enum):
    """Story status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    PASS = "pass"
    FAIL = "fail"


class QAResult(Enum):
    """QA result enumeration."""
    PASS = "PASS"
    CONCERNS = "CONCERNS"
    FAIL = "FAIL"
    WAIVED = "WAIVED"


class StateManager:
    """SQLite-based state manager for tracking story progress."""

    db_path: Path
    _lock: asyncio.Lock

    def __init__(self, db_path: str = "progress.db"):
        """
        Initialize StateManager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._lock = asyncio.Lock()
        self._init_db_sync()

    def _init_db_sync(self):
        """Initialize database schema (synchronous)."""
        conn = sqlite3.connect(self.db_path)
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
        cursor.fetchall()  # Acknowledge result for strict type checking

        # Create index on story_path for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_story_path
            ON stories(story_path)
        ''')
        cursor.fetchall()  # Acknowledge result for strict type checking

        # Create index on status for filtering
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_status
            ON stories(status)
        ''')
        cursor.fetchall()  # Acknowledge result for strict type checking

        # Create code_quality_phase table (NEW - for quality gates)
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
        cursor.fetchall()  # Acknowledge result for strict type checking

        # Create test_automation_phase table (NEW - for test automation)
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
        cursor.fetchall()  # Acknowledge result for strict type checking

        # Create indexes for performance on epic_id columns
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_quality_epic
            ON code_quality_phase(epic_id)
        ''')
        cursor.fetchall()  # Acknowledge result for strict type checking

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_test_epic
            ON test_automation_phase(epic_id)
        ''')
        cursor.fetchall()  # Acknowledge result for strict type checking

        # Create epic_processing table (NEW - for tracking epic-level progress)
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
        cursor.fetchall()  # Acknowledge result for strict type checking

        conn.commit()
        conn.close()

        logger.info(f"Database initialized: {self.db_path}")

    async def update_story_status(
        self,
        story_path: str,
        status: str,
        phase: Union[str, None] = None,
        iteration: Union[int, None] = None,
        qa_result: Union["dict[str, Any]", None] = None,
        error: Union[str, None] = None,
        epic_path: Union[str, None] = None
    ) -> bool:
        """
        Update or insert story status.

        Args:
            story_path: Path to the story file
            status: Current status (pending, in_progress, sm_completed, dev_completed, qa_completed, completed, failed, error)
            phase: Current phase (sm, dev, qa)
            iteration: Current iteration count
            qa_result: QA result dictionary
            error: Error message if any
            epic_path: Path to epic file

        Returns:
            True if successful, False otherwise
        """
        async with self._lock:
            try:
                def _update():
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()

                    # Check if story exists
                    cursor.execute(
                        'SELECT id FROM stories WHERE story_path = ?',
                        (story_path,)
                    )
                    existing = cursor.fetchone()

                    qa_result_str = None
                    if qa_result:
                        # Clean qa_result to make it JSON serializable
                        # Remove non-serializable objects like QAStatus enums
                        def clean_for_json(obj: Any) -> Any:
                            if hasattr(obj, 'value'):
                                return obj.value
                            elif isinstance(obj, dict):
                                return {k: clean_for_json(v) for k, v in obj.items()}  # type: ignore[union-attr]
                            elif isinstance(obj, list):
                                return [clean_for_json(v) for v in obj]  # type: ignore[union-attr]
                            else:
                                return obj

                        cleaned_qa_result = clean_for_json(qa_result)
                        qa_result_str = json.dumps(cleaned_qa_result)

                    if existing:
                        # Update existing record
                        # Fix: Use explicit NULL checks instead of COALESCE for proper handling of 0 and False
                        cursor.execute('''
                            UPDATE stories
                            SET status = ?,
                                phase = ?,
                                iteration = ?,
                                qa_result = ?,
                                error_message = ?,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE story_path = ?
                        ''', (
                            status,
                            phase,
                            iteration,
                            qa_result_str,
                            error,
                            story_path
                        ))
                        logger.info(f"Updated status for {story_path}: {status}")
                    else:
                        # Insert new record
                        cursor.execute('''
                            INSERT INTO stories
                            (epic_path, story_path, status, phase, iteration, qa_result, error_message)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            epic_path or '',
                            story_path,
                            status,
                            phase,
                            iteration or 0,
                            qa_result_str,
                            error
                        ))
                        logger.info(f"Inserted new record for {story_path}: {status}")

                    conn.commit()
                    conn.close()
                    return True

                return await asyncio.to_thread(_update)

            except asyncio.CancelledError as e:
                cause = getattr(e, '__cause__', None)
                cause_type = cause.__class__.__name__ if cause else 'timeout_or_cancellation'
                cause_str = str(cause) if cause else 'No cause'

                logger.warning(
                    f"State update cancelled for {story_path}: {cause_type}, "
                    f"cause={cause_str[:100]}, "
                    f"operation={status}, phase={phase}"
                )

                # Distinguish between timeout cancellation and user cancellation
                if "timeout" in cause_str.lower():
                    logger.warning(
                        f"Operation timed out for {story_path}. "
                        f"Consider increasing timeout or optimizing the operation."
                    )
                else:
                    logger.info(
                        f"Operation was cancelled by user/system for {story_path}. "
                        f"This is expected during cleanup."
                    )

                # Don't propagate cancellation error, just mark as failed
                return False
            except Exception as e:
                logger.error(f"Failed to update story status: {e}")
                return False

    async def get_story_status(self, story_path: str) -> Union["dict[str, Any]", None]:
        """
        Get current status for a story.

        Args:
            story_path: Path to the story file

        Returns:
            Dictionary with story status and metadata, or None if not found
        """
        async with self._lock:
            try:
                def _get():
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()

                    cursor.execute('''
                        SELECT epic_path, story_path, status, iteration, qa_result,
                               error_message, created_at, updated_at, phase
                        FROM stories
                        WHERE story_path = ?
                    ''', (story_path,))

                    row = cursor.fetchone()
                    conn.close()

                    if row:
                        result = {
                            'epic_path': row[0],
                            'story_path': row[1],
                            'status': row[2],
                            'iteration': row[3],
                            'created_at': row[6],
                            'updated_at': row[7],
                            'phase': row[8]
                        }

                        if row[4]:  # qa_result
                            try:
                                result['qa_result'] = json.loads(row[4])
                            except json.JSONDecodeError:
                                result['qa_result'] = row[4]

                        if row[5]:  # error_message
                            result['error'] = row[5]

                        return result

                    return None

                return await asyncio.to_thread(_get)

            except Exception as e:
                logger.error(f"Failed to get story status: {e}")
                return None

    async def get_all_stories(self) -> "list[dict[str, Any]]":
        """
        Get all stories from database.

        Returns:
            List of story dictionaries
        """
        async with self._lock:
            try:
                def _get_all() -> "list[dict[str, Any]]":
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()

                    cursor.execute('''
                        SELECT epic_path, story_path, status, iteration, qa_result,
                               error_message, created_at, updated_at, phase
                        FROM stories
                        ORDER BY created_at
                    ''')

                    rows = cursor.fetchall()
                    conn.close()

                    stories: "list[dict[str, Any]]" = []
                    for row in rows:
                        story: "dict[str, Any]" = {
                            'epic_path': row[0],
                            'story_path': row[1],
                            'status': row[2],
                            'iteration': row[3],
                            'created_at': row[6],
                            'updated_at': row[7],
                            'phase': row[8]
                        }

                        if row[4]:  # qa_result
                            try:
                                story['qa_result'] = json.loads(row[4])
                            except json.JSONDecodeError:
                                story['qa_result'] = row[4]

                        if row[5]:  # error_message
                            story['error'] = row[5]

                        stories.append(story)

                    return stories

                return await asyncio.to_thread(_get_all)

            except Exception as e:
                logger.error(f"Failed to get all stories: {e}")
                return []

    async def get_stories_by_status(self, status: str) -> "list[dict[str, Any]]":
        """
        Get all stories with a specific status.

        Args:
            status: Status to filter by

        Returns:
            List of story dictionaries
        """
        async with self._lock:
            try:
                def _get_by_status() -> "list[dict[str, Any]]":
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()

                    cursor.execute('''
                        SELECT epic_path, story_path, status, iteration, qa_result,
                               error_message, created_at, updated_at, phase
                        FROM stories
                        WHERE status = ?
                        ORDER BY created_at
                    ''', (status,))

                    rows = cursor.fetchall()
                    conn.close()

                    stories: "list[dict[str, Any]]" = []
                    for row in rows:
                        story: "dict[str, Any]" = {
                            'epic_path': row[0],
                            'story_path': row[1],
                            'status': row[2],
                            'iteration': row[3],
                            'created_at': row[6],
                            'updated_at': row[7],
                            'phase': row[8]
                        }

                        if row[4]:  # qa_result
                            try:
                                story['qa_result'] = json.loads(row[4])
                            except json.JSONDecodeError:
                                story['qa_result'] = row[4]

                        if row[5]:  # error_message
                            story['error'] = row[5]

                        stories.append(story)

                    return stories

                return await asyncio.to_thread(_get_by_status)

            except Exception as e:
                logger.error(f"Failed to get stories by status: {e}")
                return []

    async def delete_story(self, story_path: str) -> bool:
        """
        Delete a story from the database.

        Args:
            story_path: Path to the story file

        Returns:
            True if successful, False otherwise
        """
        async with self._lock:
            try:
                def _delete():
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()

                    cursor.execute(
                        'DELETE FROM stories WHERE story_path = ?',
                        (story_path,)
                    )

                    conn.commit()
                    conn.close()

                    logger.info(f"Deleted story: {story_path}")
                    return True

                return await asyncio.to_thread(_delete)

            except Exception as e:
                logger.error(f"Failed to delete story: {e}")
                return False

    async def get_stats(self) -> "dict[str, int]":
        """
        Get statistics about story statuses.

        Returns:
            Dictionary with status counts
        """
        async with self._lock:
            try:
                def _get_stats() -> "dict[str, int]":
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()

                    cursor.execute('''
                        SELECT status, COUNT(*) as count
                        FROM stories
                        GROUP BY status
                    ''')

                    rows = cursor.fetchall()
                    conn.close()

                    stats: "dict[str, int]" = {}
                    for status, count in rows:
                        stats[status] = count

                    return stats

                return await asyncio.to_thread(_get_stats)

            except Exception as e:
                logger.error(f"Failed to get stats: {e}")
                return {}

    async def create_backup(self) -> Union[str, None]:
        """
        Create a backup of the database before schema changes.

        Returns:
            Path to the backup file, or None if backup failed
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.db_path.parent / f"{self.db_path.stem}_backup_{timestamp}{self.db_path.suffix}"

            def _create_backup():
                shutil.copy2(self.db_path, backup_path)
                return str(backup_path)

            backup_file = await asyncio.to_thread(_create_backup)
            logger.info(f"Database backup created: {backup_file}")
            return backup_file

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None

    async def add_quality_phase_record(
        self,
        epic_id: str,
        file_path: str,
        error_count: int,
        basedpyright_errors: str,
        ruff_errors: str,
        fix_status: str = "pending"
    ) -> Union[str, None]:
        """
        Add a new code quality phase record.

        Args:
            epic_id: Epic identifier
            file_path: Path to the file being tracked
            error_count: Number of errors found
            basedpyright_errors: BasedPyright error details
            ruff_errors: Ruff error details
            fix_status: Fix status (pending, in_progress, completed, failed)

        Returns:
            record_id for the created record, or None if failed
        """
        async with self._lock:
            try:
                def _add_record():
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()

                    record_id = str(uuid.uuid4())
                    cursor.execute('''
                        INSERT INTO code_quality_phase
                        (record_id, epic_id, file_path, error_count, fix_status, basedpyright_errors, ruff_errors)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        record_id,
                        epic_id,
                        file_path,
                        error_count,
                        fix_status,
                        basedpyright_errors,
                        ruff_errors
                    ))

                    conn.commit()
                    conn.close()

                    logger.info(f"Added quality phase record: {record_id}")
                    return record_id

                return await asyncio.to_thread(_add_record)

            except Exception as e:
                logger.error(f"Failed to add quality phase record: {e}")
                return None

    async def add_test_phase_record(
        self,
        epic_id: str,
        test_file_path: str,
        failure_count: int,
        debug_info: str,
        fix_status: str = "pending"
    ) -> Union[str, None]:
        """
        Add a new test automation phase record.

        Args:
            epic_id: Epic identifier
            test_file_path: Path to the test file
            failure_count: Number of test failures
            debug_info: Debug information
            fix_status: Fix status (pending, in_progress, completed, failed)

        Returns:
            record_id for the created record, or None if failed
        """
        async with self._lock:
            try:
                def _add_record():
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()

                    record_id = str(uuid.uuid4())
                    cursor.execute('''
                        INSERT INTO test_automation_phase
                        (record_id, epic_id, test_file_path, failure_count, fix_status, debug_info)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        record_id,
                        epic_id,
                        test_file_path,
                        failure_count,
                        fix_status,
                        debug_info
                    ))

                    conn.commit()
                    conn.close()

                    logger.info(f"Added test phase record: {record_id}")
                    return record_id

                return await asyncio.to_thread(_add_record)

            except Exception as e:
                logger.error(f"Failed to add test phase record: {e}")
                return None

    async def get_quality_phase_records(self, epic_id: str) -> "list[dict[str, Any]]":
        """
        Get all quality phase records for an epic.

        Args:
            epic_id: Epic identifier

        Returns:
            List of quality phase record dictionaries
        """
        async with self._lock:
            try:
                def _get_records() -> "list[dict[str, Any]]":
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()

                    cursor.execute('''
                        SELECT record_id, epic_id, file_path, error_count, fix_status,
                               basedpyright_errors, ruff_errors, timestamp
                        FROM code_quality_phase
                        WHERE epic_id = ?
                        ORDER BY timestamp DESC
                    ''', (epic_id,))

                    rows = cursor.fetchall()
                    conn.close()

                    records: "list[dict[str, Any]]" = []
                    for row in rows:
                        records.append({
                            'record_id': row[0],
                            'epic_id': row[1],
                            'file_path': row[2],
                            'error_count': row[3],
                            'fix_status': row[4],
                            'basedpyright_errors': row[5],
                            'ruff_errors': row[6],
                            'timestamp': row[7]
                        })

                    return records

                return await asyncio.to_thread(_get_records)

            except Exception as e:
                logger.error(f"Failed to get quality phase records: {e}")
                return []

    async def get_test_phase_records(self, epic_id: str) -> "list[dict[str, Any]]":
        """
        Get all test automation phase records for an epic.

        Args:
            epic_id: Epic identifier

        Returns:
            List of test phase record dictionaries
        """
        async with self._lock:
            try:
                def _get_records() -> "list[dict[str, Any]]":
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()

                    cursor.execute('''
                        SELECT record_id, epic_id, test_file_path, failure_count, fix_status,
                               debug_info, timestamp
                        FROM test_automation_phase
                        WHERE epic_id = ?
                        ORDER BY timestamp DESC
                    ''', (epic_id,))

                    rows = cursor.fetchall()
                    conn.close()

                    records: "list[dict[str, Any]]" = []
                    for row in rows:
                        records.append({
                            'record_id': row[0],
                            'epic_id': row[1],
                            'test_file_path': row[2],
                            'failure_count': row[3],
                            'fix_status': row[4],
                            'debug_info': row[5],
                            'timestamp': row[6]
                        })

                    return records

                return await asyncio.to_thread(_get_records)

            except Exception as e:
                logger.error(f"Failed to get test phase records: {e}")
                return []

    async def update_quality_phase_status(
        self,
        record_id: str,
        fix_status: str,
        error_count: Union[int, None] = None
    ) -> bool:
        """
        Update the fix status of a quality phase record.

        Args:
            record_id: Record identifier
            fix_status: New fix status
            error_count: Updated error count (optional)

        Returns:
            True if successful, False otherwise
        """
        async with self._lock:
            try:
                def _update_status():
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()

                    if error_count is not None:
                        cursor.execute('''
                            UPDATE code_quality_phase
                            SET fix_status = ?, error_count = ?
                            WHERE record_id = ?
                        ''', (fix_status, error_count, record_id))
                    else:
                        cursor.execute('''
                            UPDATE code_quality_phase
                            SET fix_status = ?
                            WHERE record_id = ?
                        ''', (fix_status, record_id))

                    conn.commit()

                    # Check if any rows were updated
                    rows_updated = cursor.rowcount > 0
                    conn.close()

                    if rows_updated:
                        logger.info(f"Updated quality phase status: {record_id} -> {fix_status}")
                    else:
                        logger.warning(f"No quality phase record found to update: {record_id}")

                    return rows_updated

                return await asyncio.to_thread(_update_status)

            except Exception as e:
                logger.error(f"Failed to update quality phase status: {e}")
                return False

    async def update_test_phase_status(
        self,
        record_id: str,
        fix_status: str,
        failure_count: Union[int, None] = None,
        debug_info: Union[str, None] = None
    ) -> bool:
        """
        Update the fix status of a test phase record.

        Args:
            record_id: Record identifier
            fix_status: New fix status
            failure_count: Updated failure count (optional)
            debug_info: Updated debug info (optional)

        Returns:
            True if successful, False otherwise
        """
        async with self._lock:
            try:
                def _update_status():
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()

                    if failure_count is not None and debug_info is not None:
                        cursor.execute('''
                            UPDATE test_automation_phase
                            SET fix_status = ?, failure_count = ?, debug_info = ?
                            WHERE record_id = ?
                        ''', (fix_status, failure_count, debug_info, record_id))
                    elif failure_count is not None:
                        cursor.execute('''
                            UPDATE test_automation_phase
                            SET fix_status = ?, failure_count = ?
                            WHERE record_id = ?
                        ''', (fix_status, failure_count, record_id))
                    elif debug_info is not None:
                        cursor.execute('''
                            UPDATE test_automation_phase
                            SET fix_status = ?, debug_info = ?
                            WHERE record_id = ?
                        ''', (fix_status, debug_info, record_id))
                    else:
                        cursor.execute('''
                            UPDATE test_automation_phase
                            SET fix_status = ?
                            WHERE record_id = ?
                        ''', (fix_status, record_id))

                    conn.commit()

                    # Check if any rows were updated
                    rows_updated = cursor.rowcount > 0
                    conn.close()

                    if rows_updated:
                        logger.info(f"Updated test phase status: {record_id} -> {fix_status}")
                    else:
                        logger.warning(f"No test phase record found to update: {record_id}")

                    return rows_updated

                return await asyncio.to_thread(_update_status)

            except Exception as e:
                logger.error(f"Failed to update test phase status: {e}")
                return False

    async def update_epic_status(
        self,
        epic_id: str,
        file_path: str,
        status: str,
        total_stories: Union[int, None] = None,
        completed_stories: Union[int, None] = None,
        quality_phase_status: Union[str, None] = None,
        test_phase_status: Union[str, None] = None,
        quality_phase_errors: Union[int, None] = None,
        test_phase_failures: Union[int, None] = None
    ) -> bool:
        """
        Update or insert epic processing status.

        Args:
            epic_id: Epic identifier
            file_path: Path to epic file
            status: Overall epic status
            total_stories: Total number of stories
            completed_stories: Number of completed stories
            quality_phase_status: Quality gate phase status
            test_phase_status: Test automation phase status
            quality_phase_errors: Number of quality phase errors
            test_phase_failures: Number of test phase failures

        Returns:
            True if successful, False otherwise
        """
        async with self._lock:
            try:
                def _update():
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()

                    # Check if epic exists
                    cursor.execute(
                        'SELECT epic_id FROM epic_processing WHERE epic_id = ?',
                        (epic_id,)
                    )
                    existing = cursor.fetchone()

                    if existing:
                        # Update existing record
                        cursor.execute('''
                            UPDATE epic_processing
                            SET status = ?,
                                total_stories = COALESCE(?, total_stories),
                                completed_stories = COALESCE(?, completed_stories),
                                quality_phase_status = COALESCE(?, quality_phase_status),
                                test_phase_status = COALESCE(?, test_phase_status),
                                quality_phase_errors = COALESCE(?, quality_phase_errors),
                                test_phase_failures = COALESCE(?, test_phase_failures),
                                updated_at = CURRENT_TIMESTAMP
                            WHERE epic_id = ?
                        ''', (
                            status,
                            total_stories,
                            completed_stories,
                            quality_phase_status,
                            test_phase_status,
                            quality_phase_errors,
                            test_phase_failures,
                            epic_id
                        ))
                        logger.info(f"Updated epic status: {epic_id} -> {status}")
                    else:
                        # Insert new record
                        cursor.execute('''
                            INSERT INTO epic_processing
                            (epic_id, file_path, status, total_stories, completed_stories,
                             quality_phase_status, test_phase_status, quality_phase_errors, test_phase_failures)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            epic_id,
                            file_path,
                            status,
                            total_stories or 0,
                            completed_stories or 0,
                            quality_phase_status or 'pending',
                            test_phase_status or 'pending',
                            quality_phase_errors or 0,
                            test_phase_failures or 0
                        ))
                        logger.info(f"Inserted new epic record: {epic_id} -> {status}")

                    conn.commit()
                    conn.close()
                    return True

                return await asyncio.to_thread(_update)

            except Exception as e:
                logger.error(f"Failed to update epic status: {e}")
                return False

    async def get_epic_status(self, epic_id: str) -> Union["dict[str, Any]", None]:
        """
        Get current status for an epic.

        Args:
            epic_id: Epic identifier

        Returns:
            Dictionary with epic status and metadata, or None if not found
        """
        async with self._lock:
            try:
                def _get():
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()

                    cursor.execute('''
                        SELECT epic_id, file_path, status, created_at, updated_at,
                               total_stories, completed_stories, quality_phase_status,
                               test_phase_status, quality_phase_errors, test_phase_failures
                        FROM epic_processing
                        WHERE epic_id = ?
                    ''', (epic_id,))

                    row = cursor.fetchone()
                    conn.close()

                    if row:
                        return {
                            'epic_id': row[0],
                            'file_path': row[1],
                            'status': row[2],
                            'created_at': row[3],
                            'updated_at': row[4],
                            'total_stories': row[5],
                            'completed_stories': row[6],
                            'quality_phase_status': row[7],
                            'test_phase_status': row[8],
                            'quality_phase_errors': row[9],
                            'test_phase_failures': row[10]
                        }

                    return None

                return await asyncio.to_thread(_get)

            except Exception as e:
                logger.error(f"Failed to get epic status: {e}")
                return None

    async def update_stories_status_batch(
        self,
        stories: "list[dict[str, Any]]",
        lock_timeout: float = 30.0
    ) -> bool:
        """
        Batch update multiple story statuses with transactional support.

        Args:
            stories: List of story update dicts with keys:
                - story_path: str (required)
                - status: str (required)
                - phase: Optional[str]
                - iteration: Optional[int]
                - qa_result: Optional[Dict]
                - error: Optional[str]
                - epic_path: Optional[str]
            lock_timeout: Maximum time to wait for lock (seconds)

        Returns:
            True if all updates succeeded, False otherwise
        """
        try:
            # Use wait_for to timeout on lock acquisition
            await asyncio.wait_for(self._lock.acquire(), timeout=lock_timeout)
        except asyncio.TimeoutError:
            logger.error(f"Failed to acquire database lock within {lock_timeout}s")
            return False

        try:
            def _batch_update():
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                try:
                    for story_data in stories:
                        story_path = story_data.get('story_path')
                        if not story_path:
                            logger.warning(f"Skipping story without path: {story_data}")
                            continue

                        # Check if story exists
                        cursor.execute(
                            'SELECT id FROM stories WHERE story_path = ?',
                            (story_path,)
                        )
                        existing = cursor.fetchone()

                        # Clean qa_result if present
                        qa_result_str = None
                        if story_data.get('qa_result'):
                            # Clean qa_result to make it JSON serializable
                            def clean_for_json(obj: Any) -> Any:
                                if hasattr(obj, 'value'):
                                    return obj.value
                                elif isinstance(obj, dict):
                                    return {k: clean_for_json(v) for k, v in obj.items()}  # type: ignore[union-attr]
                                elif isinstance(obj, list):
                                    return [clean_for_json(v) for v in obj]  # type: ignore[union-attr]
                                else:
                                    return obj

                            cleaned_qa_result = clean_for_json(story_data['qa_result'])
                            qa_result_str = json.dumps(cleaned_qa_result)

                        if existing:
                            # Update existing record
                            # Fix: Use explicit NULL checks instead of COALESCE for proper handling of 0 and False
                            cursor.execute('''
                                UPDATE stories
                                SET status = ?,
                                    phase = ?,
                                    iteration = ?,
                                    qa_result = ?,
                                    error_message = ?,
                                    updated_at = CURRENT_TIMESTAMP
                                WHERE story_path = ?
                            ''', (
                                story_data['status'],
                                story_data.get('phase'),
                                story_data.get('iteration', 0),
                                qa_result_str,
                                story_data.get('error'),
                                story_path
                            ))
                        else:
                            # Insert new record
                            cursor.execute('''
                                INSERT INTO stories
                                (epic_path, story_path, status, phase, iteration, qa_result, error_message)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                story_data.get('epic_path', ''),
                                story_path,
                                story_data['status'],
                                story_data.get('phase'),
                                story_data.get('iteration', 0),
                                qa_result_str,
                                story_data.get('error')
                            ))

                    # Commit all changes in a single transaction
                    conn.commit()
                    logger.info(f"Successfully batch updated {len(stories)} stories")
                    return True

                except Exception as e:
                    # Rollback on any error
                    conn.rollback()
                    logger.error(f"Batch update failed, rolled back: {e}")
                    return False
                finally:
                    conn.close()

            result = await asyncio.to_thread(_batch_update)
            return result

        except Exception as e:
            logger.error(f"Batch update failed: {e}")
            return False
        finally:
            self._lock.release()
