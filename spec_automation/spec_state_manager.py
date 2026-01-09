import sqlite3
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class SpecStateManager:
    """State manager for spec automation with SQLite database."""

    def __init__(self, db_path: Path) -> None:
        """
        Initialize the state manager.

        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = db_path
        self._init_database()
        logger.info(f"SpecStateManager initialized with database: {db_path}")

    def _init_database(self) -> None:
        """Initialize the database schema."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS story_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_path TEXT UNIQUE NOT NULL,
                status TEXT NOT NULL,
                phase TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS qa_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_path TEXT NOT NULL,
                requirement TEXT NOT NULL,
                status TEXT NOT NULL,
                findings TEXT,
                test_coverage REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (story_path) REFERENCES story_status (story_path)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_path TEXT NOT NULL,
                report_json TEXT NOT NULL,
                overall_status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (story_path) REFERENCES story_status (story_path)
            )
        """)

        conn.commit()
        conn.close()

    def _get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection.

        Returns:
            SQLite connection
        """
        conn = sqlite3.connect(str(self.db_path))
        return conn

    def get_story_status(self, story_path: str) -> Optional[Dict[str, Any]]:
        """
        Get story status from database.

        Args:
            story_path: Path to the story file

        Returns:
            Story status dictionary or None
        """
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM story_status WHERE story_path = ? ORDER BY updated_at DESC LIMIT 1",
            (story_path,)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def update_story_status(
        self,
        story_path: str,
        status: str,
        phase: str,
    ) -> None:
        """
        Update story status in database.

        Args:
            story_path: Path to the story file
            status: New status
            phase: Current phase
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO story_status (story_path, status, phase, updated_at)
            VALUES (?, ?, ?, ?)
        """, (story_path, status, phase, datetime.now()))

        conn.commit()
        conn.close()
        logger.debug(f"Updated status for {story_path}: {status} ({phase})")

    def save_qa_result(
        self,
        story_path: str,
        requirement: str,
        status: str,
        findings: Optional[Any] = None,
        test_coverage: Optional[float] = None,
    ) -> None:
        """
        Save QA result for a requirement.

        Args:
            story_path: Path to the story file
            requirement: The requirement text
            status: QA status (PASS/FAIL/CONCERNS)
            findings: Findings as string or list of strings
            test_coverage: Test coverage percentage
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Handle findings - accept both string and list
        if findings is None:
            findings_str = None
        elif isinstance(findings, list):
            findings_str = "\n".join(findings)
        else:
            findings_str = str(findings)

        cursor.execute("""
            INSERT INTO qa_results (story_path, requirement, status, findings, test_coverage)
            VALUES (?, ?, ?, ?, ?)
        """, (
            story_path,
            requirement,
            status,
            findings_str,
            test_coverage,
        ))

        conn.commit()
        conn.close()

    def update_qa_result(
        self,
        story_path: str,
        requirement: str,
        status: str,
        findings: Optional[Any] = None,
        test_coverage: Optional[float] = None,
    ) -> None:
        """
        Update QA result for a requirement.

        This is an alias for save_qa_result for backward compatibility.

        Args:
            story_path: Path to the story file
            requirement: The requirement text
            status: QA status (PASS/FAIL/CONCERNS)
            findings: List of findings
            test_coverage: Test coverage percentage
        """
        self.save_qa_result(
            story_path=story_path,
            requirement=requirement,
            status=status,
            findings=findings,
            test_coverage=test_coverage,
        )

    def get_qa_results(self, story_path: str) -> List[Dict[str, Any]]:
        """
        Get all QA results for a story.

        Args:
            story_path: Path to the story file

        Returns:
            List of QA result dictionaries
        """
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM qa_results WHERE story_path = ? ORDER BY created_at DESC",
            (story_path,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def save_review_report(
        self,
        story_path: str,
        report_json: str,
        overall_status: str,
    ) -> None:
        """
        Save a review report.

        Args:
            story_path: Path to the story file
            report_json: Report as JSON string
            overall_status: Overall status
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO review_reports (story_path, report_json, overall_status)
            VALUES (?, ?, ?)
        """, (story_path, report_json, overall_status))

        conn.commit()
        conn.close()

    def get_review_reports(self, story_path: str) -> List[Dict[str, Any]]:
        """
        Get all review reports for a story.

        Args:
            story_path: Path to the story file

        Returns:
            List of review report dictionaries
        """
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM review_reports WHERE story_path = ? ORDER BY created_at DESC",
            (story_path,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def delete_story(self, story_path: str) -> None:
        """
        Delete a story and all related data.

        Args:
            story_path: Path to the story file
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM qa_results WHERE story_path = ?", (story_path,))
        cursor.execute("DELETE FROM review_reports WHERE story_path = ?", (story_path,))
        cursor.execute("DELETE FROM story_status WHERE story_path = ?", (story_path,))

        conn.commit()
        conn.close()

    def list_stories(self) -> List[str]:
        """
        List all story paths in the database.

        Returns:
            List of story paths
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT story_path FROM story_status ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        conn.close()

        return [row[0] for row in rows]

    def get_all_stories(self) -> List[Dict[str, Any]]:
        """
        Get all story status records.

        Returns:
            List of story status dictionaries
        """
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM story_status ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_stories_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get all stories with a specific status.

        Args:
            status: The status to filter by

        Returns:
            List of story status dictionaries matching the status
        """
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM story_status WHERE status = ? ORDER BY updated_at DESC",
            (status,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]
