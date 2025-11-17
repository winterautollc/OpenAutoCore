from pathlib import Path
from PyQt6 import QtCore, QtWidgets, QtGui
from openauto.ui import new_appointment
from openauto.subclassed_widgets.views import small_tables
from openauto.utils.validator import Validator
from openauto.repositories.customer_repository import CustomerRepository
from openauto.repositories.vehicle_repository import VehicleRepository
from openauto.repositories.appointment_repository import AppointmentRepository
from openauto.repositories.repair_orders_repository import RepairOrdersRepository
from openauto.repositories.ro_c3_repository import ROC3Repository
from openauto.utils.fixed_popup_combo import FixedPopupCombo
from openauto.managers.appointments.print_controller import PrintController
from PyQt6.QtCore import QTime, QDate

from pyvin import VIN
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

class AppointmentsManager:
    def __init__(self, main_window, sql_monitor):
        self.ui = main_window
        self.sql_monitor = sql_monitor
        self.print_controller = PrintController(self.ui)
        self.selected_vehicle_id = None  ### ID NUMBER DECLARED EARLY
        self.selected_customer_id = None
        self.waiter = None
        self.dropper = None

        #create a print button for the daily schedule
        self.ui.print_schedule_button = QtWidgets.QPushButton(parent=self.ui.calender_frame)
        self.ui.print_schedule_button.setObjectName("print_schedule_button")
        self.ui.print_schedule_button.setMaximumSize(QtCore.QSize(200, 16777215))
        print_icon = QtGui.QIcon()
        print_icon.addPixmap(QtGui.QPixmap(":/resources/icons3/24x24/cil-print.png"))
        self.ui.print_schedule_button.setIcon(print_icon)
        self.ui.print_schedule_button.setIconSize(QtCore.QSize(30, 30))
        self.ui.print_schedule_button.setText("Print")
        self.ui.print_schedule_button.setFlat(True)
        self.ui.gridLayout_12.addWidget(self.ui.print_schedule_button, 0, 3, 1, 1)
        self.ui.print_schedule_button.clicked.connect(self.print_daily_schedule)

        try:
            # Show only when hourly schedule page (hub index 5) is active
            self._update_print_schedule_visibility(self.ui.hub_stacked_widget.currentIndex())
            self.ui.hub_stacked_widget.currentChanged.connect(self._update_print_schedule_visibility)
        except Exception:
            pass

        self._plate_sidecar = None

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
        self.ui.new_appointment_ui.notes_appt_label.setText("Customer Concern")
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
        
        self.ui.vehicle_window_ui.vehicle_cancel_button.clicked.connect(
            lambda: self.ui.widget_manager.close_and_delete("vehicle_window"))
        self.ui.vehicle_window_ui.vin_line.textChanged.connect(self._enforce_uppercase_vin)
        self.ui.vehicle_window_ui.plate_line.textChanged.connect(self._enforce_uppercase_plate)
        self.ui.vehicle_window_ui.vin_search_button.clicked.connect(self.search_vehicle)
        self.ui.vehicle_window_ui.vehicle_save_button.clicked.connect(self.save_vehicle)

        if _ptcli_available():
            old = self.ui.vehicle_window_ui.plate_state_box
            parent = old.parent()
            layout = parent.layout()

            combo = FixedPopupCombo(max_popup_height=200, parent=parent)
            combo.setObjectName("plate_state_box")
            combo.addItems(STATES)

            layout.replaceWidget(old, combo)
            old.deleteLater()
            
            self.ui.vehicle_window_ui.plate_state_box = combo
            self.ui.vehicle_window_ui.plate_state_box.setMinimumWidth(80)
            self.ui.vehicle_window_ui.plate_line.setVisible(True)
        else:
            self.ui.vehicle_window_ui.plate_state_box.hide()
            try:
                self.ui.vehicle_window_ui.plate_line.hide()
            except Exception:
                pass
        self.ui.vehicle_window.show()


### LOADS VEHICLE INFO BY VIN OR MANUALLY ENTERED DATA AND PASSES IT TO MYSQL VIA save_vehicle ###
    def search_vehicle(self):
        form = self.ui.vehicle_window_ui
        vin_text = (form.vin_line.text() or "").strip().upper()
        plate = (form.plate_line.text() or "").strip().upper()

        # Prefer Plate2VIN via GoSidecarManager, using plate + state
        if _ptcli_available() and plate:
            state = (form.plate_state_box.currentText() or "").strip().upper()
            if not state:
                Validator.show_validation_error(self.ui.message, "Select a plate state for Plate2VIN lookup.")
                return

            if self._plate_sidecar is None:
                ptcli_path = (Path(__file__).resolve().parent / "parts_tree" / "ptcli").resolve()
                self._plate_sidecar = GoSidecarManager(str(ptcli_path), parent=self.ui)
                self._plate_sidecar.plateDecoded.connect(
                    self._on_plate_decoded, QtCore.Qt.ConnectionType.UniqueConnection
                )
                self._plate_sidecar.errorText.connect(
                    lambda msg: Validator.show_validation_error(self.ui.message, msg)
                )

            token = ""
            ph = getattr(self.ui, "parts_hub_manager", None)
            if ph is not None:
                try:
                    token = ph._current_token() or ""
                except Exception:
                    token = ""

            if not token:
                Validator.show_validation_error(
                    self.ui.message,
                    "Plate lookup requires a valid token. Configure in Settings first.",
                )
                return

            self._plate_sidecar.plate_to_vin(token=token, plate=plate, state=state)
            return

        # Fallback: plain VIN decode when it looks valid
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

        Validator.show_validation_error(self.ui.message, "Invalid VIN or plate.")
        form.vin_line.clear()


### ENFORCES UPPERCASE INPUT TO VIN ###
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
            Validator.show_validation_error(self.ui.message, "No vehicle found for that plate.")
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
            customer_id,
        ]
        # Optional plate and state
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
        appt_id = AppointmentRepository.insert_appointment(
            customer_id=customer_id,
            vehicle_id=vehicle_id,
            vin=vin,
            date=date,
            time=time,
            notes=notes,
            dropoff_type=dropoff_type
        )

        try:
            current_user_id = getattr(self.ui, "current_user_id", None)
            if current_user_id is None:
                cu = getattr(self.ui, "current_user", None)
                current_user_id = cu.get("id") if isinstance(cu, dict) else getattr(cu, "id", None)

            assigned_writer_id = getattr(self.ui, "assigned_writer_id", None)
            if assigned_writer_id is None:
                aw = getattr(self.ui, "current_user", None)
                assigned_writer_id = aw.get("id") if isinstance(aw, dict) else getattr(aw, "id", None)

            if vehicle_id:
                ro_id = RepairOrdersRepository.create_repair_order(
                    customer_id=customer_id,
                    vehicle_id=vehicle_id,
                    appointment_id=appt_id,
                    ro_number=None,
                    created_by=current_user_id,
                    assigned_writer_id=assigned_writer_id,
                )

                if notes:
                    ROC3Repository.set_or_create_concern(ro_id, notes.strip(), created_by=current_user_id)
        except Exception as e:
            import traceback
            traceback.print_exc()

        self.ui.widget_manager.close_and_delete("new_appointment")
        msg = QtWidgets.QMessageBox(self.ui)
        msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
        msg.setWindowTitle("Saved")
        msg.setText("Appointment Saved Successfully" + (" + RO created." if vehicle_id else "."))
        msg.exec()
        

    def print_daily_schedule(self):
        date = self.ui.schedule_calendar.selectedDate()
        appointments = AppointmentRepository.get_appointments_for_week(date, date)
        self.print_controller.print_daily_schedule(appointments, date)
        
               
    def _update_print_schedule_visibility(self, index: int):
        btn = getattr(self.ui, "print_schedule_button", None)
        if not btn:
            return
        # Hourly schedule page lives at hub_stacked_widget index 5
        btn.setVisible(index == 5)

