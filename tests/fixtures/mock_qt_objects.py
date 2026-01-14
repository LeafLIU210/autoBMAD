"""Mock Qt objects for testing."""

from unittest.mock import MagicMock
from PySide6.QtWidgets import QWidget


def create_mock_widget() -> MagicMock:
    """Create a mock QWidget for testing.
    
    Returns:
        MagicMock instance configured to simulate a QWidget.
    """
    mock_widget = MagicMock(spec=QWidget)
    return mock_widget
