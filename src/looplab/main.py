"""LoopLab main entry point."""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt


def main():
    """Main application entry point."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("LoopLab")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("LoopLab")
    
    # Import here to avoid issues with OpenGL context
    from .app.main_window import MainWindow
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
