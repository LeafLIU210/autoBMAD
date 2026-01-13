# test_spec_state_manager.py

"""Unit tests for the spec_state_manager module."""

import pytest
from pathlib import Path
from autoBMAD.epic_automation.spec_state_manager import SpecStateManager


@pytest.fixture
def temp_db(tmp_path):
    """Creates a temporary database file for testing."""
    db_path = tmp_path / "test.db"
    yield db_path
    if db_path.exists():
        db_path.unlink()


class TestSpecStateManager:
    """Test cases for the SpecStateManager class."""

    def test_init(self, temp_db):
        """Test the initialization of SpecStateManager."""
        manager = SpecStateManager(temp_db)
        assert manager.db_path == temp_db
        assert manager.connection is not None
        manager.close()

    def test_create_tables(self, temp_db):
        """Test the create_tables method."""
        manager = SpecStateManager(temp_db)
        manager.create_tables()

        # Verify that the table was created
        cursor = manager.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='spec_state'")
        assert cursor.fetchone() is not None
        manager.close()

    def test_save_state(self, temp_db):
        """Test the save_state method."""
        manager = SpecStateManager(temp_db)
        file_path = "test.md"
        section = "Heading 1"
        data = {"key": "value"}

        manager.save_state(file_path, section, data)

        # Verify that the state was saved
        cursor = manager.connection.cursor()
        cursor.execute("SELECT file_path, section, data FROM spec_state WHERE file_path = ?", (file_path,))
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == file_path
        assert row[1] == section
        assert row[2] == str(data)
        manager.close()

    def test_load_state(self, temp_db):
        """Test the load_state method."""
        manager = SpecStateManager(temp_db)
        file_path = "test.md"
        section = "Heading 1"
        data = {"key": "value"}

        # Save a state
        manager.save_state(file_path, section, data)

        # Load the state
        loaded_state = manager.load_state(file_path)
        assert loaded_state is not None
        assert loaded_state["section"] == section
        assert loaded_state["data"] == str(data)
        manager.close()

    def test_load_state_no_state(self, temp_db):
        """Test load_state when no state is saved."""
        manager = SpecStateManager(temp_db)
        file_path = "nonexistent.md"

        loaded_state = manager.load_state(file_path)
        assert loaded_state is None
        manager.close()

    def test_close(self, temp_db):
        """Test the close method."""
        manager = SpecStateManager(temp_db)
        manager.close()
        assert manager.connection is None