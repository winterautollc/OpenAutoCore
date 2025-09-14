from PyQt6 import QtWidgets, QtCore, QtGui
from openauto.ui import theme
from openauto.subclassed_widgets.event_handlers import WidgetManager
import os
from openauto.theme import resources_rc


def apply_stylesheet(widget, relative_path):
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    theme_path = os.path.join(base_path, relative_path)
    try:
        with open(theme_path, "r") as f:
            widget.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"⚠️ Could not load theme: {theme_path}")

class ThemeManager:
    def __init__(self, main_window):
        self.ui = main_window
        self.widget_manager = WidgetManager()
        self.theme, self.theme_ui = self.widget_manager.create_or_restore(
            "theme", QtWidgets.QWidget, theme.Ui_Form)

        self._setup_ui()




    def _setup_ui(self):
        self.theme.setParent(self.ui, QtCore.Qt.WindowType.Dialog)

        self.theme.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.Dialog
        )

        self.theme.setWindowModality(QtCore.Qt.WindowModality.WindowModal)

        self.theme_ui.cancel_button.clicked.connect(
                lambda: self.widget_manager.close_and_delete("theme"))

        self.theme_ui.save_button.clicked.connect(self.switch_theme)
        self.theme.show()



    def switch_theme(self):
        style = self.ui.style()
        light_theme = "theme/light_theme.qss"
        dark_theme = "theme/dark_theme.qss"

        if self.theme_ui.light_radiobutton.isChecked():
            chosen = "light"
            pixmap = QtGui.QPixmap(":/resources/OpenAuto_Icons_48x48_dark_light/mainwindow_icon/light_theme_logo.png")
            style.unpolish(self.ui)
            apply_stylesheet(self.ui, light_theme)
            style.polish(self.ui)

        elif self.theme_ui.dark_radiobutton.isChecked():
            chosen = "dark"
            pixmap = QtGui.QPixmap(":/resources/OpenAuto_Icons_48x48_dark_light/mainwindow_icon/dark_theme_logo.png")
            style.unpolish(self.ui)
            apply_stylesheet(self.ui, dark_theme)
            style.polish(self.ui)

        else:
            return

        self.ui.label_3.setPixmap(pixmap)

        if hasattr(self.ui, "switch_theme"):
            self.ui.switch_theme(chosen)
        else:
            path = "theme/light_theme.qss" if chosen == "light" else "theme/dark_theme.qss"
            apply_stylesheet(self.ui, path)

        self.widget_manager.close_and_delete("theme")

