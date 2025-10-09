from PyQt6 import QtWidgets, QtCore
from openauto.ui import vehicle_options
from openauto.subclassed_widgets.event_handlers import WidgetManager
from openauto.managers import animations_manager, customer_manager


class VehicleOptionsManager:
    def __init__(self, parent, vehicle_id, new_ro_request):
        self.parent = parent
        self.vehicle_id = vehicle_id
        self.new_ro_request = new_ro_request
        self.widget_manager = WidgetManager()
        self.customer_manager = customer_manager.CustomerManager(self)
        self.animations_manager = animations_manager.AnimationsManager

        self.vehicle_options, self.vehicle_options_ui = self.widget_manager.create_or_restore(
            "vehicle_options", QtWidgets.QWidget, vehicle_options.Ui_vehcile_options_form)

        self._setup_ui()


    def _setup_ui(self):
        self.vehicle_options.setParent(self.parent, QtCore.Qt.WindowType.Dialog)
        self.vehicle_options.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.Dialog
        )

        self.vehicle_options.setWindowModality(QtCore.Qt.WindowModality.WindowModal)

        self.vehicle_options_ui.cancel_vehicle_options_button.clicked.connect(
            lambda: self.widget_manager.close_and_delete("vehicle_options")
        )
        self.vehicle_options_ui.change_owner_vehicle_button.clicked.connect(self.change_owner)
        self.vehicle_options_ui.create_ro_vehicle_button.hide()
        self.vehicle_options_ui.delete_vehicle_button.clicked.connect(self.delete_vehicle)

        self.vehicle_options.show()


    def change_owner(self):
        from openauto.managers import belongs_to_manager

        temp_belongs_to_manager = belongs_to_manager.BelongsToManager(self.parent, vehicle_id=self.vehicle_id)
        temp_belongs_to_manager.belongs_to_cust_change()
        self.widget_manager.close_and_delete("vehicle_options")


    def create_ro(self):
        self.new_ro_request.emit()
        self.widget_manager.close_and_delete("vehicle_options")

    def delete_vehicle(self):
        confirmation = QtWidgets.QMessageBox(self.vehicle_options)
        confirmation.setWindowTitle("Confirm Delete")
        confirmation.setText("Are you sure you want to delete this vehicle?")
        confirmation.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        confirmation.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        response = confirmation.exec()

        if response == QtWidgets.QMessageBox.StandardButton.Yes:
            from openauto.repositories.vehicle_repository import VehicleRepository
            VehicleRepository.delete_vehicle(vin = self.vehicle_id[0], vehicle_id=self.vehicle_id[1])
            self.widget_manager.close_and_delete("vehicle_options")