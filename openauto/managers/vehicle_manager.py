from pathlib import Path
from PyQt6 import QtWidgets, QtCore
from openauto.ui import vehicle_search_form
from pyvin import VIN
from openauto.utils.validator import Validator
from openauto.repositories.vehicle_repository import VehicleRepository
from openauto.repositories.customer_repository import CustomerRepository
from openauto.managers.belongs_to_manager import BelongsToManager
from openauto.utils.fixed_popup_combo import FixedPopupCombo
from openauto.managers.parts_tree.go_sidecar_manager import GoSidecarManager


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
        self._plate_sidecar = None

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
        
        btn = self.ui.vehicle_window_ui.vin_search_button
        btn.setMinimumWidth(120)
        btn.setMaximumWidth(120)
        btn.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            btn.sizePolicy().verticalPolicy(),
        )
        
        layout = self.ui.vehicle_window_ui.horizontalLayout
        layout.addItem(QtWidgets.QSpacerItem(
            40, 20,
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        ))

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
            self.ui.vehicle_window_ui.plate_line.setVisible(True)
        else:
            self.ui.vehicle_window_ui.plate_state_box.hide()
            try:
                self.ui.vehicle_window_ui.plate_line.hide()
            except Exception:
                pass
        
        
        self.ui.vehicle_window_ui.vehicle_cancel_button.clicked.connect(
            lambda: self.ui.widget_manager.close_and_delete("vehicle_window"))

        self.ui.vehicle_window_ui.vin_line.textChanged.connect(self._enforce_uppercase_vin)
        self.ui.vehicle_window_ui.plate_line.textChanged.connect(self._enforce_uppercase_plate)

        self.ui.vehicle_window.show()

    def search_vehicle(self):
        form = self.ui.vehicle_window_ui
        vin_text = (form.vin_line.text() or "").strip().upper()
        plate = (form.plate_line.text() or "").strip().upper()

        if _ptcli_available() and plate:
            state = (form.plate_state_box.currentText() or "").strip().upper()
            if not state:
                self._show_message("Select a plate state for Plate2VIN lookup.")
                return

            if self._plate_sidecar is None:
                ptcli_path = (Path(__file__).resolve().parent / "parts_tree" / "ptcli").resolve()
                self._plate_sidecar = GoSidecarManager(str(ptcli_path), parent=self.ui)
                self._plate_sidecar.plateDecoded.connect(
                    self._on_plate_decoded, QtCore.Qt.ConnectionType.UniqueConnection
                )
                self._plate_sidecar.errorText.connect(
                    lambda msg: self._show_message(msg)
                )

            token = ""
            ph = getattr(self.ui, "parts_hub_manager", None)
            if ph is not None:
                try:
                    token = ph._current_token() or ""
                except Exception:
                    token = ""

            if not token:
                self._show_message("Plate lookup requires a valid token. Configure in Settings first.")
                return

            self._plate_sidecar.plate_to_vin(token=token, plate=plate, state=state)
            self._show_message("Looking up plate, please wait...")
            return

        ### Fallback to VIN decoding if propietary plate2vin is not available ###
        if vin_text and len(vin_text) == 17:
            try:
                vin = VIN(vin_text)
                form.year_line.setText(vin.ModelYear)
                form.make_line.setText(vin.Make)
                form.model_line.setText(vin.Model)
                form.engine_line.setText(vin.DisplacementL)
                form.trim_line.setText(vin.Trim)
                return
            except Exception:
                pass

        self._show_message("Please enter a valid 17 digit VIN or plate.")
        form.vin_line.clear()

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
            customer_id,
        ]

        try:
            plate = (form.plate_line.text() or "").strip().upper()
        except Exception:
            plate = ""
        try:
            state = (form.plate_state_box.currentText() or "").strip().upper() if _ptcli_available() else ""
        except Exception:
            state = ""

        vehicle_data.append(plate)
        vehicle_data.append(state)

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
        msg = getattr(self.ui, "message", None)
        if msg is None:
            return
        parent = getattr(self.ui, "vehicle_window", None)
        try:
            if parent is not None and parent.isVisible():
                msg.setParent(parent)
            else:
                msg.setParent(self.ui)
        except RuntimeError:
            return
        msg.setText(text)
        msg.show()

    def _enforce_uppercase_vin(self, text):
        cleaned = (text or "").replace(" ", "").upper()
        le = self.ui.vehicle_window_ui.vin_line
        cursor_pos = le.cursorPosition()
        le.setText(cleaned)
        le.setCursorPosition(min(cursor_pos, len(cleaned)))
        
    def _enforce_uppercase_plate(self, text):
        cleaned = (text or "").replace(" ", "").upper()
        le = self.ui.vehicle_window_ui.plate_line
        cursor_pos = le.cursorPosition()
        le.setText(cleaned)
        le.setCursorPosition(min(cursor_pos, len(cleaned)))

    def _on_plate_decoded(self, payload: dict):
        form = getattr(self.ui, "vehicle_window_ui", None)
        vw = getattr(self.ui, "vehicle_window", None)
        try:
            if form is None or vw is None or not vw.isVisible():
                return
        except RuntimeError:
            return

        results = payload.get("results") or payload.get("Results") or []
        if isinstance(results, list) and results:
            result = results[0]
        elif isinstance(results, dict):
            result = results
        else:
            self._show_message("No vehicle found for that plate.")
            return

        vin_str = (result.get("vin") or result.get("VIN") or "").strip().upper()
        decode = result.get("vinDecode") or result.get("vin_decode") or {}

        if vin_str:
            try:
                form.vin_line.setText(vin_str)
            except RuntimeError:
                return

        year = decode.get("MDL_YR") or decode.get("ACES_YEAR_ID") or ""
        make = decode.get("ACES_MAKE_NAME") or decode.get("MAK_NM") or ""
        model = decode.get("ACES_MODEL_NAME") or decode.get("MDL_DESC") or ""
        liters = decode.get("ACES_LITERS") or decode.get("ENG_DISPLCMNT_CL")
        trim = decode.get("TRIM_DESC") or decode.get("ACES_SUB_MODEL_NAME") or ""

        engine = ""
        if liters:
            l_str = str(liters)
            if l_str and "." not in l_str and len(l_str) == 1:
                l_str = f"{l_str}.0"
            engine = f"{l_str}L"

        try:
            if year:
                form.year_line.setText(str(year))
            if make:
                form.make_line.setText(str(make))
            if model:
                form.model_line.setText(str(model))
            if engine:
                form.engine_line.setText(engine)
            if trim:
                form.trim_line.setText(str(trim))
        except RuntimeError:
            return
