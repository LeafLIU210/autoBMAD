"""Main application startup logic."""

import sys
from PySide6.QtWidgets import QApplication


def main() -> int:
    """Initialize and run the Qt application.
    
    Returns:
        Exit code from the application.
    """
    app = QApplication(sys.argv)
    
    # TODO: Import and show main window
    # from my_qt_app.ui.main_window import MainWindow
    # window = MainWindow()
    # window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
