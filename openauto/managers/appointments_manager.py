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
        self.waiter = None
        self.dropper = None

### OPENS new_appointment WIDGET ###
    def open_new_appointment(self):
        self.ui.new_appointment, self.ui.new_appointment_ui = self.ui.widget_manager.create_or_restore(
            "new_appointment", QtWidgets.QWidget, new_appointment.Ui_Form)

        self.ui.new_appointment.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint
        )

        self.ui.new_appointment.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.ui.new_appointment_ui.cancel_button.clicked.connect(
            lambda: self.ui.widget_manager.close_and_delete("new_appointment"))

        self._load_small_tables()
        self._connect_signals()
        self.ui.new_appointment_ui.new_customer_button.clicked.connect(self._create_new_customer)
        self.ui.new_appointment_ui.new_vehicle_button.clicked.connect(lambda: self.add_vehicle(self.selected_vehicle_id))
        self.ui.new_appointment_ui.save_button.clicked.connect(self._save_appointment)
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
        self.ui.new_appointment_ui.customer_search_line.textChanged.connect(self._filter_customers_and_vehicles)
        self.ui.customer_table_small.cellClicked.connect(self._filter_vehicles_by_customer)
        self.ui.customer_table_small.cellClicked.connect(self.store_selected_vehicle_id)


### OPENS new_customer_form ###
    def _create_new_customer(self):
        from openauto.ui import new_customer_form
        self.ui.show_new_customer_page, self.ui.show_new_customer_page_ui = self.ui.widget_manager.create_or_restore(
            "new_customer", QtWidgets.QWidget, new_customer_form.Ui_create_customer_form
        )

        self.ui.show_new_customer_page.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.ui.show_new_customer_page.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.ui.show_new_customer_page_ui.abort_button.clicked.connect(
            lambda: self.ui.widget_manager.close_and_delete("new_customer"))

        self.ui.show_new_customer_page_ui.edit_button.hide()
        self.ui.show_new_customer_page_ui.first_name_line.setFocus()
        self.ui.show_new_customer_page.setFixedSize(606, 693)
        self.ui.show_new_customer_page.setWindowTitle("New Customer")
        self.ui.show_new_customer_page_ui.phone_line.setInputMask('(000) 000-0000;_')
        self.ui.new_appointment.hide()
        self.ui.show_new_customer_page.show()
        self.ui.show_new_customer_page_ui.save_button.clicked.connect(self.save_customer)



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
        id_item = self.ui.customer_table_small.item(row, 3)  # ID column
        if not id_item:
            return

        customer_id = id_item.text().strip()
        self.ui.customer_id_small = customer_id

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

### GRABS THE ID NUMBER OF THE CUSTOMER SELECTED SO OTHER FUNCTIONS CAN USE IT FOR MYSQL ###
    def store_selected_vehicle_id(self, row, column):
        item = self.ui.customer_table_small.item(row, 3)
        if item:
            try:
                self.selected_vehicle_id = int(item.text())
            except ValueError:
                self.selected_vehicle_id = None
        else:
            print("No vehicle_id found in that cell.")
            self.selected_vehicle_id = None

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
            "vehicle_window", QtWidgets.QWidget, vehicle_search_form.Ui_Form
        )

        self.ui.vehicle_window.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint
        )

        self.ui.vehicle_window.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)

        self.ui.vehicle_window_ui.abort_button.clicked.connect(
            lambda: self.ui.widget_manager.close_and_delete("vehicle_window"))
        self.ui.vehicle_window_ui.vin_line.textChanged.connect(self._enforce_uppercase_vin)
        self.ui.vehicle_window_ui.vin_search_button.clicked.connect(self.search_vehicle)
        self.ui.vehicle_window_ui.save_create_button.clicked.connect(self.save_vehicle)
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
        row = self.ui.weekly_schedule_table.selected_row  # <- store this when cellClicked is triggered
        col = self.ui.weekly_schedule_table.selected_column

        # Calculate the time based on the row index
        base_hour = 7
        half_hour_slots = row
        hour = base_hour + half_hour_slots // 2
        minute = 30 if half_hour_slots % 2 else 0

        # Build QTime
        time = QTime(hour, minute)

        # Then continue with your normal save logic
        date = self.ui.weekly_schedule_table.selected_date  # <- should be the selected day from schedule_calendar
        notes = self.ui.new_appointment_ui.notes_edit.toPlainText()
        customer_id = self.ui.customer_id_small
        vehicle_id = self.selected_vehicle_id
        selected_row = self.ui.vehicle_table_small.currentRow()
        vin_item= self.ui.vehicle_table_small.item(selected_row, 4)
        vin = vin_item.text().strip() if vin_item else None
        if self.ui.new_appointment_ui.drop_button.isChecked():
            dropoff_type = "drop"
        elif self.ui.new_appointment_ui.wait_button.isChecked():
            dropoff_type = "wait"
        else:
            self.ui.message.setText("Please select 'wait' or 'drop'")
            self.ui.message.show()
            return

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
