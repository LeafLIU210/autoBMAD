# spec_state_manager.py

"""A state manager for the spec parser."""

import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional


class SpecStateManager:
    """A class to manage the state of the spec parser using a SQLite database."""

    def __init__(self, db_path: Path) -> None:
        """Initialize the SpecStateManager with the path to the database.

        Args:
            db_path: The path to the SQLite database file.
        """
        self.db_path = db_path
        self.connection: sqlite3.Connection | None = None
        self.init_db()

    def init_db(self) -> None:
        """Initialize the database connection and create the necessary tables."""
        self.connection = sqlite3.connect(self.db_path)
        self.create_tables()

    def create_tables(self) -> None:
        """Create the necessary tables in the database."""
        assert self.connection is not None
        cursor = self.connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS spec_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                section TEXT,
                data TEXT
            )
        """
        )
        self.connection.commit()

    def save_state(self, file_path: str, section: str, data: Dict[str, Any]) -> None:
        """Save the current state of the parser to the database.

        Args:
            file_path: The path to the file being parsed.
            section: The current section being parsed.
            data: The data extracted from the current section.
        """
        assert self.connection is not None
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO spec_state (file_path, section, data) VALUES (?, ?, ?)",
            (file_path, section, str(data)),
        )
        self.connection.commit()

    def load_state(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load the last saved state for a given file.

        Args:
            file_path: The path to the file.

        Returns:
            The last saved state for the file, or None if no state is found.
        """
        assert self.connection is not None
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT section, data FROM spec_state WHERE file_path = ? ORDER BY id DESC LIMIT 1",
            (file_path,),
        )
        row = cursor.fetchone()
        if row:
            return {"section": row[0], "data": row[1]}
        return None

    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None