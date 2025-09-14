from PyQt6 import QtWidgets, QtCore
from openauto.ui import ro_status_options
from openauto.subclassed_widgets.event_handlers import WidgetManager
import os

def apply_stylesheet(widget, relative_path):
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    theme_path = os.path.join(base_path, relative_path)
    try:
        with open(theme_path, "r") as f:
            widget.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"⚠️ Could not load theme: {theme_path}")


class ROStatusManager:
    def __init__(self, ui):
        self.ui = ui
        self.widget_manager = WidgetManager()

        self.ro_status_options, self.ro_status_options_ui = self.widget_manager.create_or_restore(
            "ro_options", QtWidgets.QWidget, ro_status_options.Ui_ro_options_widget
        )

        self._setup_ui()


    def _setup_ui(self):
       self.ro_status_options.setParent(self.ui, QtCore.Qt.WindowType.Dialog)
       self.ro_status_options.setWindowFlags(
           QtCore.Qt.WindowType.FramelessWindowHint |
           QtCore.Qt.WindowType.Dialog
       )

       self.ro_status_options.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
       self.ro_status_options_ui.cancel_status_button.clicked.connect(
           lambda: self.widget_manager.close_and_delete("ro_options")
       )
       self.ro_status_options.show()