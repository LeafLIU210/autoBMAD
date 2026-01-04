"""
State Manager - SQLite-based State Management

Handles progress tracking and state persistence for BMAD automation.
"""

import json
import sqlite3
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, List
import logging

logger = logging.getLogger(__name__)


class StateManager:
    """SQLite-based state manager for tracking story progress."""

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

        conn.commit()
        conn.close()

        logger.info(f"Database initialized: {self.db_path}")

    async def update_story_status(
        self,
        story_path: str,
        status: str,
        phase: Optional[str] = None,
        iteration: Optional[int] = None,
        qa_result: Optional[Dict] = None,
        error: Optional[str] = None,
        epic_path: Optional[str] = None
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
                        qa_result_str = json.dumps(qa_result)

                    if existing:
                        # Update existing record
                        cursor.execute('''
                            UPDATE stories
                            SET status = ?,
                                phase = COALESCE(?, phase),
                                iteration = COALESCE(?, iteration),
                                qa_result = COALESCE(?, qa_result),
                                error_message = COALESCE(?, error_message),
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

            except Exception as e:
                logger.error(f"Failed to update story status: {e}")
                return False

    async def get_story_status(self, story_path: str) -> Optional[Dict[str, Any]]:
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

    async def get_all_stories(self) -> List[Dict[str, Any]]:
        """
        Get all stories from database.

        Returns:
            List of story dictionaries
        """
        async with self._lock:
            try:
                def _get_all():
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

                    stories = []
                    for row in rows:
                        story = {
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

    async def get_stories_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get all stories with a specific status.

        Args:
            status: Status to filter by

        Returns:
            List of story dictionaries
        """
        async with self._lock:
            try:
                def _get_by_status():
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

                    stories = []
                    for row in rows:
                        story = {
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

    async def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about story statuses.

        Returns:
            Dictionary with status counts
        """
        async with self._lock:
            try:
                def _get_stats():
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()

                    cursor.execute('''
                        SELECT status, COUNT(*) as count
                        FROM stories
                        GROUP BY status
                    ''')

                    rows = cursor.fetchall()
                    conn.close()

                    stats = {}
                    for status, count in rows:
                        stats[status] = count

                    return stats

                return await asyncio.to_thread(_get_stats)

            except Exception as e:
                logger.error(f"Failed to get stats: {e}")
                return {}
