from PyQt6 import QtWidgets, QtCore
from openauto.managers import ro_status_manager

class StatusDialogController:
    def __init__(self, ui):
        self.ui = ui

    def open_ro_status(self, checked=False):
        ro_status_manager.ROStatusManager(self.ui)

    def cancel_ro_changes(self):
        message_box = QtWidgets.QMessageBox(self.ui)
        message_box.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        message_box.setWindowTitle("Cancel Changes")
        message_box.setText("Cancel and discard unsaved changes.\n\nAre you sure?")
        message_box.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        message_box.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if message_box.exec() == QtWidgets.QMessageBox.StandardButton.Yes:
            self.ui.animations_manager.show_repair_orders()
