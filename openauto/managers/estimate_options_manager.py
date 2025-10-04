from PyQt6 import QtWidgets, QtCore
from openauto.subclassed_widgets.event_handlers import WidgetManager
from openauto.subclassed_widgets.models.ro_tree_model import ROTreeModel
from openauto.ui import estimate_options
from openauto.repositories import repair_orders_repository
from openauto.managers import ro_status_manager


class EstimateOptionsManager:
    def __init__(self, parent, estimate_id):
        self.ui = parent
        self.estimate_id = estimate_id
        # self.estimate_options_signal = estimate_options_signal
        self.widget_manager = WidgetManager()

        self.estimate_options, self.estimate_options_ui = self.widget_manager.create_or_restore(
            "estimate_options", QtWidgets.QWidget, estimate_options.Ui_estimate_options_form
        )

        self._setup_ui()


    def _setup_ui(self):
        self.estimate_options.setParent(self.ui, QtCore.Qt.WindowType.Dialog)
        self.estimate_options.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.Dialog
        )

        self.estimate_options.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self.estimate_options_ui.cancel_ro_options_button.clicked.connect(
            lambda: self.widget_manager.close_and_delete("estimate_options")
        )
        self.estimate_options_ui.delete_ro_button.clicked.connect(self.confirm_delete)
        self.estimate_options_ui.open_ro_button.clicked.connect(self._open_ro_page)
        self.estimate_options_ui.change_ro_status_button.hide()
        self.estimate_options_ui.change_ro_status_button.clicked.connect(self.open_ro_status)
        self.estimate_options.show()

    def confirm_delete(self):
        message_box = QtWidgets.QMessageBox(self.estimate_options)
        message_box.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        message_box.setWindowTitle("Confirm Delete")
        message_box.setText(
            "This will permanently delete the estimate.\n\nAre you sure?"
        )
        message_box.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        message_box.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        response = message_box.exec()
        message_confirm = QtWidgets.QMessageBox(self.estimate_options)
        message_confirm.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        # message_confirm.setStyleSheet("QLabel { color: black; }")
        message_confirm.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        message_confirm.setText("Estimate Deleted!! This Cannot Be Undone")

        if response == QtWidgets.QMessageBox.StandardButton.Yes:
            estimate_id = self.estimate_id
            repair_orders_repository.RepairOrdersRepository.delete_repair_order(estimate_id)
            message_confirm.exec()
            self.widget_manager.close_and_delete("estimate_options")


    def _open_ro_page(self):
        selected_estimate_row = self.ui.estimates_table.currentRow()
        model: ROTreeModel = self.ui.ro_items_table.model()
        model.clear()
        ro_id = self.estimate_id
        self.ui.ro_hub_manager.load_ro_into_hub(ro_id)
        self.widget_manager.close_and_delete("estimate_options")
        self.ui.animations_manager.ro_hub_page_show()

    def open_ro_status(self, checked=False):
        self.widget_manager.close_and_delete("estimate_options")
        ro_status_manager.ROStatusManager(self.ui)