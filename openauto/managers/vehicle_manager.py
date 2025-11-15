from pathlib import Path
from PyQt6 import QtWidgets, QtCore
from openauto.ui import vehicle_search_form
from pyvin import VIN
from openauto.utils.validator import Validator
from openauto.repositories.vehicle_repository import VehicleRepository
from openauto.repositories.customer_repository import CustomerRepository
from openauto.managers.belongs_to_manager import BelongsToManager
from openauto.utils.fixed_popup_combo import FixedPopupCombo


STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO",
    "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA",
    "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
]


def _ptcli_available() -> bool:
    try:
        ptcli_path = (Path(__file__).resolve().parent / "parts_tree" / "ptcli").resolve()
        return ptcli_path.is_file()
    except Exception:
        return False


class VehicleManager:
    def __init__(self, main_window):
        self.ui = main_window
        self.belongs_to_manager = BelongsToManager(main_window)

    def add_vehicle(self):
        if not self.ui.customer_table.currentItem():
            self._show_message("No Customer Selected, Please Highlight A Customer!")
            return

        self._open_vehicle_form()
        self.ui.vehicle_window_ui.vin_search_button.clicked.connect(self.search_vehicle)
        self.ui.vehicle_window_ui.vehicle_save_button.clicked.connect(self.load_customer_id)

    def _open_vehicle_form(self):
        self.ui.vehicle_window, self.ui.vehicle_window_ui = self.ui.widget_manager.create_or_restore(
            "vehicle_window", QtWidgets.QWidget, vehicle_search_form.Ui_vehicle_search_form
        )

        self.ui.vehicle_window.setParent(self.ui, QtCore.Qt.WindowType.Dialog)
        self.ui.vehicle_window.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Dialog
        )



        self.ui.vehicle_window.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self.ui.vehicle_window.setFocus()

        # Only expose plate/state controls when ptcli is available (Plate2VIN)
        if _ptcli_available():
            old_box = self.ui.vehicle_window_ui.plate_state_box
            parent = old_box.parent()
            layout = parent.layout()

            combo = FixedPopupCombo(max_popup_height=200, parent=parent)
            combo.setObjectName("plate_state_box")
            combo.addItems(STATES)

            layout.replaceWidget(old_box, combo)
            old_box.deleteLater()
            self.ui.vehicle_window_ui.plate_state_box = combo
        else:
            # Hide the plate/state selector when Plate2VIN is not available
            self.ui.vehicle_window_ui.plate_state_box.hide()
        
        
        self.ui.vehicle_window_ui.vehicle_cancel_button.clicked.connect(
            lambda: self.ui.widget_manager.close_and_delete("vehicle_window"))

        self.ui.vehicle_window_ui.vin_line.textChanged.connect(self._enforce_uppercase_vin)

        self.ui.vehicle_window.show()

    def search_vehicle(self):
        vin_text = self.ui.vehicle_window_ui.vin_line.text()
        try:
            vin = VIN(vin_text)
            form = self.ui.vehicle_window_ui
            form.year_line.setText(vin.ModelYear)
            form.make_line.setText(vin.Make)
            form.model_line.setText(vin.Model)
            form.engine_line.setText(vin.DisplacementL)
            form.trim_line.setText(vin.Trim)
        except:
            self._show_message("Please Enter A Valid 17 Digit VIN")
            # Validator.show_validation_error(self.ui.message, "Please Enter A Valid 17 Digit VIN")
            self.ui.vehicle_window_ui.vin_line.clear()

    def load_customer_id(self):
        row = self.ui.customer_table.currentRow()
        customer_data = [
            self.ui.customer_table.item(row, col).text() if self.ui.customer_table.item(row, col) else ""
            for col in range(self.ui.customer_table.columnCount())
        ]

        customer_id = customer_data[9]

        if customer_id:
            self.save_vehicle(customer_id)
        else:
            self._show_message("Could not find customer ID.")

    def save_vehicle(self, customer_id):
        form = self.ui.vehicle_window_ui
        vehicle_data = [
            form.vin_line.text(),
            form.year_line.text(),
            form.make_line.text(),
            form.model_line.text(),
            form.engine_line.text(),
            form.trim_line.text(),
            customer_id
        ]

        if not Validator.vehicle_fields_filled(vehicle_data[:6]):
            self._show_message("Please decode VIN or fill in year, make, and model.")
            return

        VehicleRepository.insert_vehicle(vehicle_data)
        self.ui.widget_manager.close_and_delete("vehicle_window")
        QtCore.QTimer.singleShot(0, lambda: QtWidgets.QMessageBox.information(self.ui, "Vehicle Added",
                        "Vehicle has been added."))

    def vehicle_search_filter(self, text):
        for row in range(self.ui.vehicle_table.rowCount()):
            match = any(
                text.lower() in (self.ui.vehicle_table.item(row, col).text().lower() if self.ui.vehicle_table.item(row, col) else "")
                for col in range(self.ui.vehicle_table.columnCount())
            )
            self.ui.vehicle_table.setRowHidden(row, not match)

    def add_new_vehicle(self):
        self._open_vehicle_form()
        self.ui.vehicle_window_ui.vehicle_save_button.setText("Next")
        self.ui.vehicle_window_ui.vin_search_button.clicked.connect(self.search_vehicle)
        self.ui.vehicle_window_ui.vehicle_save_button.clicked.connect(self.belongs_to_manager.belongs_to)

    def _show_message(self, text):
        self.ui.message.setParent(self.ui.vehicle_window)
        self.ui.message.setText(text)
        self.ui.message.show()

    def _enforce_uppercase_vin(self, text):
        cursor_pos = self.ui.vehicle_window_ui.vin_line.cursorPosition()
        self.ui.vehicle_window_ui.vin_line.setText(text.upper())
        self.ui.vehicle_window_ui.vin_line.setCursorPosition(cursor_pos)
