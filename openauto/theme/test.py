from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
import sys
from OpenAuto import control_menu, workflow_tables, event_handlers

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the UI file
        uic.loadUi("main.ui", self)

        # Clean bold fonts and styles from RO Control Page
        self._remove_styles(self.ro_control_page)

        # Replace the full interface with just ro_control_page
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.addWidget(self.ro_control_page)
        self.setCentralWidget(wrapper)

        self.setWindowTitle("Test RO Hub Page (No Styling)")
        self.resize(800, 600)

    def _remove_styles(self, parent_widget):
        for child in parent_widget.findChildren(QWidget):
            child.setStyleSheet("")
            font = child.font()
            if font.bold():
                font.setBold(False)
                child.setFont(font)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
