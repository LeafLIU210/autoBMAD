"""Module for managing the state of specifications."""

import sqlite3
from pathlib import Path
from typing import Any


class SpecStateManager:
    """A class to manage the state of specifications using SQLite."""

    def __init__(self, db_path: Path):
        """Initialize the SpecStateManager with a database path.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self.connection: sqlite3.Connection | None = None

    def create_tables(self) -> None:
        """Create the necessary tables in the database."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
        cursor = self.connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS spec_state (
                file_path TEXT NOT NULL,
                section TEXT NOT NULL,
                data TEXT NOT NULL,
                PRIMARY KEY (file_path)
            )
            """
        )
        self.connection.commit()

    def save_state(self, file_path: str, section: str, data: dict[str, Any]) -> None:
        """Save the state to the database.

        Args:
            file_path: The path to the file.
            section: The section of the file.
            data: The data to be saved.
        """
        if self.connection is None:
            self.create_tables()
        if self.connection is not None:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO spec_state (file_path, section, data) VALUES (?, ?, ?)",
                (file_path, section, str(data)),
            )
            self.connection.commit()

    def load_state(self, file_path: str) -> dict[str, Any] | None:
        """Load the state from the database.

        Args:
            file_path: The path to the file.

        Returns:
            The loaded state, or None if no state is found.
        """
        if self.connection is None:
            return None
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT section, data FROM spec_state WHERE file_path = ?", (file_path,)
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
