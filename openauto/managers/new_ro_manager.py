from pathlib import Path
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QAbstractItemView
from openauto.utils.validator import Validator
from openauto.ui import new_appointment, new_customer_form, vehicle_search_form
from openauto.managers import vehicle_manager
from openauto.subclassed_widgets.views import small_tables
from openauto.repositories.repair_orders_repository import RepairOrdersRepository
from openauto.repositories.customer_repository import CustomerRepository
from openauto.repositories.vehicle_repository import VehicleRepository
from openauto.repositories.ro_c3_repository import ROC3Repository
from openauto.utils.fixed_popup_combo import FixedPopupCombo
from pyvin import VIN


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
class NewROManager:
    cust_id_small_signal = pyqtSignal(str)

    def __init__(self, main_window, sql_monitor):
        self.ui = main_window
        self.sql_monitor = sql_monitor
        self.vehicle_manager = vehicle_manager.VehicleManager(self)
        self.selected_customer_id = None

    def add_repair_order(self):
        # Reuse new_appointment.ui, but for RO creation
        self.ui.new_ro_page, self.ui.new_ro_page_ui = self.ui.widget_manager.create_or_restore(
            "new_repair_order", QtWidgets.QWidget, new_appointment.Ui_new_appointment_form
        )

        self.ui.new_ro_page.setParent(self.ui, QtCore.Qt.WindowType.Dialog)
        self.ui.new_ro_page.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Dialog
        )
        self.ui.new_ro_page.setWindowModality(QtCore.Qt.WindowModality.WindowModal)

        # Retitle & tweak labels for RO context
        self.ui.new_ro_page.setWindowTitle("Create Repair Order")
        self.ui.new_ro_page_ui.customer_label.setText("Customer")
        self.ui.new_ro_page_ui.vehicle_label.setText("Vehicle")
        self.ui.new_ro_page_ui.notes_appt_label.setText("Customer Concern")

        # Hide appointment-only controls
        self.ui.new_ro_page_ui.drop_appt_button.hide()
        self.ui.new_ro_page_ui.wait_appt_button.hide()
        self.ui.new_ro_page_ui.new_vehicle_appt_button.hide()

        # Wire buttons
        self.ui.new_ro_page_ui.cancel_appt_button.clicked.connect(
            lambda: self.ui.widget_manager.close_and_delete("new_repair_order")
        )
        self.ui.new_ro_page_ui.save_appt_button.setText("Create RO")
        self.ui.new_ro_page_ui.save_appt_button.setEnabled(False)

        # Allow adding a new customer/vehicle from here as well
        self.ui.new_ro_page_ui.new_customer_appt_button.clicked.connect(self._open_new_customer)
        self.ui.new_ro_page_ui.new_vehicle_appt_button.clicked.connect(
            lambda: self.add_vehicle(self.selected_customer_id))

        self._load_small_tables()
        self._connect_signals()
        self.ui.new_ro_page.show()

    def _load_small_tables(self):

        self.ui.customer_table_small = small_tables.CustomerTableSmall()
        self.ui.new_ro_page_ui.gridLayout.addWidget(self.ui.customer_table_small, 2, 0, 1, 2)

        self.ui.vehicle_table_small = small_tables.VehicleTableSmall()
        self.ui.new_ro_page_ui.gridLayout.addWidget(self.ui.vehicle_table_small, 1, 2, 2, 2)
        self.ui.vehicle_table_small.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        self.sql_monitor.small_customers_update.connect(self.ui.customer_table_small.update_customers)
        self.sql_monitor.small_vehicles_update.connect(self.ui.vehicle_table_small.update_vehicles)

    def _connect_signals(self):
        self.ui.new_ro_page_ui.customer_search__appt_line.textChanged.connect(self._filter_customers_and_vehicles)
        self.ui.customer_table_small.cellClicked.connect(self._filter_vehicles_by_customer)
        self.ui.customer_table_small.itemSelectionChanged.connect(self._validate_ro_selections)
        self.ui.vehicle_table_small.itemSelectionChanged.connect(self._validate_ro_selections)
        self.ui.new_ro_page_ui.save_appt_button.clicked.connect(self._save_ro)



    # --- Filtering logic mirrors your existing NewROManager, but using embedded tables ---
    def _filter_customers_and_vehicles(self, text: str):
        visible_customer_ids = set()

        # Filter customer table
        for row in range(self.ui.customer_table_small.rowCount()):
            match = any(
                text.lower() in (self.ui.customer_table_small.item(row, col).text().lower()
                                    if self.ui.customer_table_small.item(row, col) else "")
                for col in range(self.ui.customer_table_small.columnCount())
            )
            self.ui.customer_table_small.setRowHidden(row, not match)

            if match:
                id_item = self.ui.customer_table_small.item(row, 3)  # ID column
                if id_item:
                    visible_customer_ids.add(id_item.text().strip())

        # Filter vehicle table by matching customer IDs
        for row in range(self.ui.vehicle_table_small.rowCount()):
            vehicle_owner_item = self.ui.vehicle_table_small.item(row, 3)  # Owner ID column
            if vehicle_owner_item:
                owner_id = vehicle_owner_item.text().strip()
                self.ui.vehicle_table_small.setRowHidden(row, owner_id not in visible_customer_ids)

    def _filter_vehicles_by_customer(self, row: int):
        if self.ui.customer_table_small.cellClicked:
            self.ui.vehicle_table_small.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            self.ui.new_ro_page_ui.new_vehicle_appt_button.show()
        else:
            self.ui.vehicle_table_small.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
            self.ui.new_ro_page_ui.new_vehicle_appt_button.hide()

        id_item = self.ui.customer_table_small.item(row, 3)
        if not id_item:
            return

        customer_id = id_item.text().strip()
        self.ui.customer_id_small = customer_id
        self.selected_customer_id = customer_id

        for v_row in range(self.ui.vehicle_table_small.rowCount()):
            vehicle_owner_item = self.ui.vehicle_table_small.item(v_row, 3)
            if vehicle_owner_item:
                match = vehicle_owner_item.text().strip() == customer_id
                self.ui.vehicle_table_small.setRowHidden(v_row, not match)

        self.ui.customer_table_small.selectRow(row)

        for v_row in range(self.ui.vehicle_table_small.rowCount()):
            if not self.ui.vehicle_table_small.isRowHidden(v_row):
                self.ui.vehicle_table_small.selectRow(v_row)
                break

    # --- Actions ---
    def _open_new_customer(self):
        self.ui.show_new_customer_page, self.ui.show_new_customer_page_ui = self.ui.widget_manager.create_or_restore(
            "new_customer", QtWidgets.QWidget, new_customer_form.Ui_create_customer_form
        )

        self.ui.show_new_customer_page.setParent(self.ui, QtCore.Qt.WindowType.Dialog)

        self.ui.show_new_customer_page.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Dialog
        )

        self.ui.show_new_customer_page.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self.ui.show_new_customer_page_ui.cancel_customer_button.clicked.connect(
            lambda: self.ui.widget_manager.close_and_delete("new_customer"))

        self.ui.show_new_customer_page_ui.edit_customer_button.hide()
        self.ui.show_new_customer_page.setFocus()
        self.ui.show_new_customer_page.setFixedSize(606, 693)
        self.ui.show_new_customer_page.setWindowTitle("New Customer")
        self.ui.show_new_customer_page_ui.phone_line.setInputMask('(000) 000-0000;_')
        self.ui.show_new_customer_page.show()
        self.ui.show_new_customer_page_ui.save_customer_button.clicked.connect(self.save_customer)


    def save_customer(self):
        form = self.ui.show_new_customer_page_ui

        customer_data = [
            form.last_name_line.text(),
            form.first_name_line.text(),
            form.phone_line.text(),
            form.address_line.text(),
            form.city_line.text(),
            form.state_line.text(),
            form.zipcode_line.text(),
            form.alt_line.text(),
            form.email_line.text()
        ]

        if not Validator.fields_filled(customer_data[:3]):
            Validator.show_validation_error(self.ui.message, "Please provide at least a name and phone number.")
            return
        customer_id = CustomerRepository.insert_customer(customer_data)
        # self.add_vehicle(self.selected_customer_id)
        self.ui.widget_manager.close_and_delete("new_customer")


    def add_vehicle(self, customer_id=None):
        if customer_id is not None:
            self.selected_customer_id = customer_id


        self.ui.vehicle_window, self.ui.vehicle_window_ui = self.ui.widget_manager.create_or_restore(
            "vehicle_window", QtWidgets.QWidget, vehicle_search_form.Ui_vehicle_search_form
        )

        self.ui.vehicle_window.setParent(self.ui, QtCore.Qt.WindowType.Dialog
                                         )
        self.ui.vehicle_window.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Dialog
        )

        self.ui.vehicle_window.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self.ui.vehicle_window.setFocus()
        self.ui.vehicle_window_ui.vehicle_cancel_button.clicked.connect(
            lambda: self.ui.widget_manager.close_and_delete("vehicle_window"))
        self.ui.vehicle_window_ui.vin_line.textChanged.connect(self._enforce_uppercase_vin)
        self.ui.vehicle_window_ui.vin_search_button.clicked.connect(self.search_vehicle)
        self.ui.vehicle_window_ui.vehicle_save_button.clicked.connect(self.save_vehicle)

        if _ptcli_available():
            old = self.ui.vehicle_window_ui.plate_state_box
            parent = old.parent()
            layout = old.parent().layout()

            combo = FixedPopupCombo(max_popup_height=200, parent=parent)
            combo.setObjectName("plate_state_box")
            combo.addItems(STATES)

            layout.replaceWidget(old, combo)
            old.deleteLater()
            self.ui.vehicle_window_ui.plate_state_box = combo
            
            self.ui.vehicle_window_ui.vin_line.setPlaceholderText("Search Plate Number Or VIN")
            
        else:
            self.ui.vehicle_window_ui.plate_state_box.hide()
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
            Validator.show_validation_error(self.ui.message, "Invalid VIN")
            self.ui.vehicle_window_ui.vin_line.clear()


    def _enforce_uppercase_vin(self, text):
        cursor_pos = self.ui.vehicle_window_ui.vin_line.cursorPosition()
        self.ui.vehicle_window_ui.vin_line.setText(text.upper())
        self.ui.vehicle_window_ui.vin_line.setCursorPosition(cursor_pos)

    def save_vehicle(self):
        customer_id = self.selected_customer_id or getattr(self.ui, "customer_id_small", None)
        if customer_id is None:
            Validator.show_validation_error(self.ui.message, "No customer selected.")
            return

        form = self.ui.vehicle_window_ui
        vin_raw = form.vin_line.text().strip().upper()
        vin = vin_raw if vin_raw else ""  # NOT NULL column: use empty string, not None

        # Only check duplicates/transfers if VIN looks real
        existing = None
        if len(vin_raw) >= 11:  # or == 17 if for full VINs only
            existing = VehicleRepository.find_by_vin(vin_raw)

        if existing:
            if str(existing["customer_id"]) == str(customer_id):
                self.ui.message.setWindowTitle("Vehicle already exists")
                self.ui.message.setText("This vehicle (VIN) is already attached to the selected customer.")
                self.ui.message.show()
                self.ui.widget_manager.close_and_delete("vehicle_window")
                self._select_vehicle_row_by_vin(vin_raw)
                return
            else:
                reply = QtWidgets.QMessageBox.question(
                    self.ui, "Duplicate VIN Found",
                    "This VIN already exists on a different customer.\n\n"
                    "Transfer this vehicle to the selected customer?",
                    QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                    QtWidgets.QMessageBox.StandardButton.No
                )
                if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                    VehicleRepository.transfer_vehicle_to_customer(existing["id"], int(customer_id))
                    self.ui.message.setText("Vehicle transferred to the selected customer.")
                    self.ui.message.show()
                    self.ui.widget_manager.close_and_delete("vehicle_window")
                    self._select_vehicle_row_by_vin(vin_raw)
                    return
                else:
                    return

        vehicle_data = [
            vin,  # empty string allowed; satisfies NOT NULL
            form.year_line.text().strip(),
            form.make_line.text().strip(),
            form.model_line.text().strip(),
            form.engine_line.text().strip(),
            form.trim_line.text().strip(),
            customer_id
        ]
        if not Validator.vehicle_fields_filled(vehicle_data[:6]):
            return

        VehicleRepository.insert_vehicle(vehicle_data)
        self.ui.widget_manager.close_and_delete("vehicle_window")
        self.ui.new_ro_page.show()
        if vin_raw:
            self._select_vehicle_row_by_vin(vin_raw)



    def _select_vehicle_row_by_vin(self, vin: str):
        tbl = self.ui.vehicle_table_small
        for r in range(tbl.rowCount()):
            item = tbl.item(r, 4)  # VIN column (hidden)
            if item and item.text().strip().upper() == vin.upper() and not tbl.isRowHidden(r):
                tbl.selectRow(r)
                break

    def _validate_ro_selections(self):
        cust_tbl = self.ui.customer_table_small
        veh_tbl = self.ui.vehicle_table_small
        btn = self.ui.new_ro_page_ui.save_appt_button

        # must have a selected row in both tables
        c_row = cust_tbl.currentRow()
        v_row = veh_tbl.currentRow()
        ok = (c_row is not None and c_row >= 0 and v_row is not None and v_row >= 0)

        # and the selected vehicle must belong to the selected customer
        if ok:
            cust_id_item = cust_tbl.item(c_row, 3)  # hidden customer_id
            owner_id_item = veh_tbl.item(v_row, 3)  # hidden vehicle owner customer_id
            ok = bool(cust_id_item and owner_id_item and
                      cust_id_item.text().strip() == owner_id_item.text().strip())

        btn.setEnabled(ok)

    def _save_ro(self):
        # use the programmatic small tables
        cust_tbl = self.ui.customer_table_small
        veh_tbl = self.ui.vehicle_table_small

        c_row = cust_tbl.currentRow()
        v_row = veh_tbl.currentRow()

        # fall back to first visible row if nothing is formally selected
        if c_row < 0:
            for r in range(cust_tbl.rowCount()):
                if not cust_tbl.isRowHidden(r):
                    c_row = r
                    cust_tbl.selectRow(r)
                    break
        if v_row < 0:
            for r in range(veh_tbl.rowCount()):
                if not veh_tbl.isRowHidden(r):
                    v_row = r
                    veh_tbl.selectRow(r)
                    break

        if c_row < 0:
            self.ui.message.setText("Select a customer.")
            self.ui.message.show()
            return
        if v_row < 0:
            self.ui.message.setText("Select a vehicle.")
            self.ui.message.show()
            return

        customer_id = cust_tbl.item(c_row, 3).text().strip()  # owner customer_id
        owner_id = veh_tbl.item(v_row, 3).text().strip()  # owner customer_id (hidden)
        vin = veh_tbl.item(v_row, 4).text().strip()  # vin (hidden)
        vehicle_id = int(veh_tbl.item(v_row, 5).text().strip())  # <-- vehicle PK (hidden)

        if owner_id != customer_id:
            self.ui.message.setText("Selected vehicle does not belong to the selected customer.")
            self.ui.message.show()
            return

        current_user_id = getattr(self.ui, "current_user_id", None)
        assigned_writer_id = getattr(self.ui, "assigned_writer_id", None)
        if current_user_id is None:
            cu = getattr(self.ui, "current_user", None)
            if isinstance(cu, dict):
                current_user_id = cu.get("id")
            else:
                current_user_id = getattr(cu, "id", None)

        if assigned_writer_id is None:
            aw = getattr(self.ui, "current_user", None)
            if isinstance(aw, dict ):
                assigned_writer_id = aw.get("id")
            else:
                assigned_writer_id = getattr(aw, "id", None)



        ro_id = RepairOrdersRepository.create_repair_order(
            customer_id=customer_id,
            vehicle_id=vehicle_id,
            appointment_id=None,
            ro_number=None,
            created_by=current_user_id,
            assigned_writer_id=assigned_writer_id,
        )

        try:
            concern = self.ui.new_ro_page_ui.notes_appt_edit.toPlainText().strip()
            if concern:
                ROC3Repository.set_or_create_concern(ro_id, concern, created_by=current_user_id)
        except Exception:
            pass

        self.ui.widget_manager.close_and_delete("new_repair_order")


