"""Pytest configuration and global fixtures."""

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for the test session.
    
    This fixture ensures a single QApplication instance exists
    for all tests that require Qt functionality.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Cleanup is handled automatically by pytest-qt
