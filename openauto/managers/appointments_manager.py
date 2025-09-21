from PyQt6 import QtCore, QtWidgets
from openauto.ui import new_appointment
from openauto.subclassed_widgets import small_tables
from openauto.utils.validator import Validator
from openauto.repositories.customer_repository import CustomerRepository
from openauto.repositories.vehicle_repository import VehicleRepository
from openauto.repositories.appointment_repository import AppointmentRepository
from PyQt6.QtCore import QTime

from pyvin import VIN



class AppointmentsManager:
    def __init__(self, main_window, sql_monitor):
        self.ui = main_window
        self.sql_monitor = sql_monitor
        self.selected_vehicle_id = None  ### ID NUMBER DECLARED EARLY
        self.selected_customer_id = None
        self.waiter = None
        self.dropper = None

### OPENS new_appointment WIDGET ###
    def open_new_appointment(self):
        self.ui.new_appointment, self.ui.new_appointment_ui = self.ui.widget_manager.create_or_restore(
            "new_appointment", QtWidgets.QWidget, new_appointment.Ui_new_appointment_form)

        self.ui.new_appointment.setParent(self.ui, QtCore.Qt.WindowType.Dialog)
        self.ui.new_appointment.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Dialog
        )

        self.ui.new_appointment.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self.ui.new_appointment_ui.cancel_appt_button.clicked.connect(
            lambda: self.ui.widget_manager.close_and_delete("new_appointment"))

        self._load_small_tables()
        self._connect_signals()
        self.ui.new_appointment_ui.new_customer_appt_button.clicked.connect(self._create_new_customer)

        self.ui.new_appointment_ui.new_vehicle_appt_button.clicked.connect(
            lambda: self.add_vehicle(getattr(self.ui, "customer_id_small", None)))

        self.ui.new_appointment_ui.save_appt_button.clicked.connect(self._save_appointment)
        self.ui.new_appointment.show()

### LOADS SUBCLASSED WIDGETS customer_table_small AND vehicle_table_small ###
    def _load_small_tables(self):
        self.ui.customer_table_small = small_tables.CustomerTableSmall()
        self.ui.new_appointment_ui.gridLayout.addWidget(self.ui.customer_table_small, 2, 0, 1, 2)

        self.ui.vehicle_table_small = small_tables.VehicleTableSmall()
        self.ui.new_appointment_ui.gridLayout.addWidget(self.ui.vehicle_table_small, 1, 2, 2, 2)

        self.sql_monitor.small_customers_update.connect(self.ui.customer_table_small.update_customers)
        self.sql_monitor.small_vehicles_update.connect(self.ui.vehicle_table_small.update_vehicles)


### CONNECTS SIGNALS TO ELIMINATE TABLE CELLS USING LINE EDIT AS SEARCH BAR, AND CELLCLICKED ON custoemr_table_small
### FILTERS OUT vehicle_table_small WITH MATCHING ID NUMBERS ###
    def _connect_signals(self):
        self.ui.new_appointment_ui.customer_search__appt_line.textChanged.connect(self._filter_customers_and_vehicles)
        self.ui.customer_table_small.cellClicked.connect(self._filter_vehicles_by_customer)
        self.ui.vehicle_table_small.cellClicked.connect(self._remember_vehicle_pk)
        self.ui.customer_table_small.cellClicked.connect(self._remember_customer_pk)

    def _remember_vehicle_pk(self, row, column):
        # VehicleTableSmall should now have hidden VEHICLE_ID in column 5
        item = self.ui.vehicle_table_small.item(row, 5)
        try:
            self.selected_vehicle_id = int(item.text()) if item else None
        except (TypeError, ValueError):
            self.selected_vehicle_id = None

    def _remember_customer_pk(self, row, column):
        item = self.ui.customer_table_small.item(row, 3)  # customer ID column
        try:
            self.selected_customer_id = int(item.text()) if item else None
        except (TypeError, ValueError):
            self.selected_customer_id = None

    ### OPENS new_customer_form ###
    def _create_new_customer(self):
        from openauto.ui import new_customer_form
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
        self.ui.new_appointment.hide()
        self.ui.show_new_customer_page.show()
        self.ui.show_new_customer_page_ui.save_customer_button.clicked.connect(self.save_customer)



### FILTERS CUSTOMERS AND VEHICLES UNDER SEARCH ###
    def _filter_customers_and_vehicles(self, text):
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


### FILTERS VEHICLES WHEN A CELL IS CLICKED IN customer_table_small ###
    def _filter_vehicles_by_customer(self, row):
        id_item = self.ui.customer_table_small.item(row, 3)
        if not id_item:
            return
        customer_id = id_item.text().strip()
        self.ui.customer_id_small = customer_id
        try:
            self.selected_customer_id = int(customer_id)
        except ValueError:
            self.selected_customer_id = None


        for v_row in range(self.ui.vehicle_table_small.rowCount()):
            vehicle_owner_item = self.ui.vehicle_table_small.item(v_row, 3)  # Vehicle owner ID column
            if vehicle_owner_item:
                match = vehicle_owner_item.text().strip() == customer_id
                self.ui.vehicle_table_small.setRowHidden(v_row, not match)

        self.ui.customer_table_small.selectRow(row)

        for v_row in range(self.ui.vehicle_table_small.rowCount()):
            if not self.ui.vehicle_table_small.isRowHidden(v_row):
                self.ui.vehicle_table_small.selectRow(v_row)
                break

        for v_row in range(self.ui.vehicle_table_small.rowCount()):
            if not self.ui.vehicle_table_small.isRowHidden(v_row):
                self.ui.vehicle_table_small.selectRow(v_row)
                self._remember_vehicle_pk(v_row, 0)  # set selected_vehicle_id
                break
        else:
            # No vehicles visible for this customer
            self.selected_vehicle_id = None

### GRABS THE ID NUMBER OF THE CUSTOMER SELECTED SO OTHER FUNCTIONS CAN USE IT FOR MYSQL ###
    def store_selected_vehicle_id(self, row, column):
        item = self.ui.customer_table_small.item(row, 3)
        if item:
            try:
                self.selected_customer_id = int(item.text())
            except ValueError:
                self.selected_customer_id = None
        else:
            self.selected_customer_id = None

    ### SAVES NEW CUSTOMER TO DB ###
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
        self.add_vehicle(customer_id)
        self.ui.widget_manager.close_and_delete("new_customer")


### OPENS vehicle_search_form ###
    def add_vehicle(self, customer_id=None):
        if customer_id is not None:
            self.selected_customer_id = customer_id

        from openauto.ui import vehicle_search_form

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
        self.ui.vehicle_window.show()


### LOADS VEHICLE INFO BY VIN OR MANUALLY ENTERED DATA AND PASSES IT TO MYSQL VIA save_vehicle ###
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


### ENFORCES UPPERCASE INPUT TO VIN ###
    def _enforce_uppercase_vin(self, text):
        cursor_pos = self.ui.vehicle_window_ui.vin_line.cursorPosition()
        self.ui.vehicle_window_ui.vin_line.setText(text.upper())
        self.ui.vehicle_window_ui.vin_line.setCursorPosition(cursor_pos)



### SAVES VEHICLE TO DATABASE WITH MATCHING ID NUMBER WITH SELECTED CUSTOMER OR CREATED CUSTOMER ###
    def save_vehicle(self):
        customer_id = self.selected_customer_id
        if customer_id is None:
            Validator.show_validation_error(self.ui.message, "No customer selected.")
            return

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
            return

        VehicleRepository.insert_vehicle(vehicle_data)
        self.ui.widget_manager.close_and_delete("vehicle_window")
        self.ui.new_appointment.show()

    def _save_appointment(self):
        w = self.ui.weekly_schedule_table
        d = self.ui.hourly_schedule_table

        # Prefer weekly context; if not available, use hourly context
        row = getattr(w, "selected_row", None)
        date = getattr(w, "selected_date", None)
        if row is None or date is None:
            row = getattr(d, "selected_row", None)
            date = getattr(d, "selected_date", None)

        if row is None or date is None:
            self.ui.message.setText("Pick a time slot in the schedule first.")
            self.ui.message.show()
            return

        # Row -> time (7:00 AM start, 30-min slots)
        base_hour = 7
        hour = base_hour + (row // 2)
        minute = 30 if (row % 2) else 0
        time = QTime(hour, minute)

        # --- Save rest as before ---
        notes = self.ui.new_appointment_ui.notes_appt_edit.toPlainText().strip()
        customer_id = self.selected_customer_id or getattr(self.ui, "customer_id_small", None)

        vehicle_id = self.selected_vehicle_id

        if not customer_id:
            self.ui.message.setText("Select a customer first.")
            self.ui.message.show()
            return

        # VIN (optional, for reference/search)
        vin = None
        vr = self.ui.vehicle_table_small.currentRow()
        if vr is not None and vr >= 0:
            vin_item = self.ui.vehicle_table_small.item(vr, 4)  # hidden VIN col
            vin = vin_item.text().strip() if vin_item else None

        if self.ui.new_appointment_ui.drop_appt_button.isChecked():
            dropoff_type = "drop"
        elif self.ui.new_appointment_ui.wait_appt_button.isChecked():
            dropoff_type = "wait"
        else:
            self.ui.message.setText("Please select 'wait' or 'drop'")
            self.ui.message.show()
            return

        if not customer_id:
            self.ui.message.setText("Select a customer first.")
            self.ui.message.show()
            return

        # Insert: vehicle_id may be None (DB now allows it)
        AppointmentRepository.insert_appointment(
            customer_id=customer_id,
            vehicle_id=vehicle_id,
            vin=vin,
            date=date,
            time=time,
            notes=notes,
            dropoff_type=dropoff_type
        )

        self.ui.widget_manager.close_and_delete("new_appointment")
        self.ui.message.setText("Appointment saved successfully.")
        self.ui.message.show()


