from PyQt6 import QtWidgets, QtCore
from openauto.ui import ro_status_options
from openauto.subclassed_widgets.event_handlers import WidgetManager

class ROStatusManager:
    def __init__(self, ui):
        self.ui = ui
        self.widget_manager = WidgetManager()

        self.ro_status_options, self.ro_status_options_ui = self.widget_manager.create_or_restore(
            "ro_options", QtWidgets.QWidget, ro_status_options.Ui_Form
        )

        self._setup_ui()


    def _setup_ui(self):
       self.ro_status_options.setParent(self.ui, QtCore.Qt.WindowType.Dialog)
       self.ro_status_options.setWindowFlags(
           QtCore.Qt.WindowType.FramelessWindowHint |
           QtCore.Qt.WindowType.Dialog
       )

       self.ro_status_options.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
       self.ro_status_options_ui.cancel_button.clicked.connect(
           lambda: self.widget_manager.close_and_delete("ro_options")
       )
       self.ro_status_options.show()