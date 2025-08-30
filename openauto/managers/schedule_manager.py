from PyQt6 import QtWidgets, QtCore
from openauto.repositories import appointment_repository
from openauto.ui import new_ro
from openauto.subclassed_widgets import small_tables


class ScheduleManager:
    def __init__(self, main_window):
        self.ui = main_window

    def open_appointment_popup(self, selected_time, selected_date):
        self.ui.appointment_popup, self.ui.appointment_popup_ui = self.ui.widget_manager.create_or_restore(
            "appointment_popup", QtWidgets.QWidget, new_ro.Ui_create_ro
        )

        self.ui.appointment_popup.setParent(self.ui, QtCore.Qt.WindowType.Dialog)

        self.ui.appointment_popup.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Dialog
        )

        self.ui.appointment_popup.setWindowModality(QtCore.Qt.WindowModality.WindowModal)

        self.selected_time = selected_time
        self.selected_date = selected_date

        self._load_small_tables()
        self._connect_signals()

        self.ui.appointment_popup_ui.abort_button.clicked.connect(
            lambda: self.ui.widget_manager.close_and_delete("appointment_popup")
        )
        self.ui.appointment_popup_ui.save_button.clicked.connect(self._save_appointment)

        self.ui.appointment_popup_ui.add_vehicle_button.hide()
        self.ui.appointment_popup.show()

    def _load_small_tables(self):
        self.ui.customer_table_small = small_tables.CustomerTableSmall()
        self.ui.appointment_popup_ui.gridLayout_2.addWidget(self.ui.customer_table_small, 2, 0, 1, 1)

        self.ui.vehicle_table_small = small_tables.VehicleTableSmall()
        self.ui.appointment_popup_ui.gridLayout_3.addWidget(self.ui.vehicle_table_small, 1, 0, 1, 1)

    def _connect_signals(self):
        self.ui.appointment_popup_ui.customer_line_edit.textChanged.connect(self._filter_customers_and_vehicles)
        self.ui.customer_table_small.cellClicked.connect(self._filter_vehicles_by_customer)

    def _filter_customers_and_vehicles(self, text):
        visible_customer_ids = set()

        for row in range(self.ui.customer_table_small.rowCount()):
            match = any(
                text.lower() in (self.ui.customer_table_small.item(row, col).text().lower()
                                 if self.ui.customer_table_small.item(row, col) else "")
                for col in range(self.ui.customer_table_small.columnCount())
            )
            self.ui.customer_table_small.setRowHidden(row, not match)

            if match:
                id_item = self.ui.customer_table_small.item(row, 3)
                if id_item:
                    visible_customer_ids.add(id_item.text().strip())

        for row in range(self.ui.vehicle_table_small.rowCount()):
            vehicle_owner_item = self.ui.vehicle_table_small.item(row, 3)
            if vehicle_owner_item:
                owner_id = vehicle_owner_item.text().strip()
                self.ui.vehicle_table_small.setRowHidden(row, owner_id not in visible_customer_ids)

    def _filter_vehicles_by_customer(self, row):
        id_item = self.ui.customer_table_small.item(row, 3)
        if not id_item:
            return

        self.selected_customer_id = id_item.text().strip()

        for v_row in range(self.ui.vehicle_table_small.rowCount()):
            vehicle_owner_item = self.ui.vehicle_table_small.item(v_row, 3)
            if vehicle_owner_item:
                match = vehicle_owner_item.text().strip() == self.selected_customer_id
                self.ui.vehicle_table_small.setRowHidden(v_row, not match)

        self.ui.customer_table_small.selectRow(row)

        for v_row in range(self.ui.vehicle_table_small.rowCount()):
            if not self.ui.vehicle_table_small.isRowHidden(v_row):
                self.ui.vehicle_table_small.selectRow(v_row)
                break

    def _save_appointment(self):
        customer_row = self.ui.customer_table_small.currentRow()
        vehicle_row = self.ui.vehicle_table_small.currentRow()

        if customer_row == -1 or vehicle_row == -1:
            QtWidgets.QMessageBox.warning(self.ui.appointment_popup, "Selection Error",
                                          "Please select both a customer and a vehicle.")
            return

        customer_id = int(self.ui.customer_table_small.item(customer_row, 3).text())
        vehicle_id = int(self.ui.vehicle_table_small.item(vehicle_row, 3).text())

        appointment_repository.AppointmentRepository.create_appointment(
            customer_id=customer_id,
            vehicle_id=vehicle_id,
            appointment_date=self.selected_date.toString("yyyy-MM-dd"),
            appointment_time=self.selected_time,
            notes="Scheduled via calendar"
        )

        QtWidgets.QMessageBox.information(self.ui.appointment_popup, "Success", "Appointment created successfully.")
        self.ui.widget_manager.close_and_delete("appointment_popup")
