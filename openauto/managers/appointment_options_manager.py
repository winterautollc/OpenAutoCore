from PyQt6 import QtWidgets, QtCore
from openauto.ui import appointment_options, edit_appointment
from openauto.subclassed_widgets.event_handlers import WidgetManager
from openauto.repositories import appointment_repository, vehicle_repository
from PyQt6.QtCore import QDate, QTime


class AppointmentOptionsManager:
    def __init__(self, parent, appt_id):
        self.parent = parent
        self.widget_manager = WidgetManager()
        self.appointment_id = appt_id
        self.message = QtWidgets.QMessageBox(self.parent)
        self.message_confirm = QtWidgets.QMessageBox(self.parent)

        self.window, self.ui = self.widget_manager.create_or_restore(
            "appointment_options", QtWidgets.QWidget, appointment_options.Ui_Form
            )

        self.edit_window, self.edit_ui = self.widget_manager.create_or_restore(
            "edit_appointment", QtWidgets.QWidget, edit_appointment.Ui_Form
            )

        self._setup_ui()



    def _setup_ui(self):
        self.window.setParent(self.parent, QtCore.Qt.WindowType.Dialog)
        self.window.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Dialog)
        self.window.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self.edit_window.setParent(self.parent, QtCore.Qt.WindowType.Dialog)
        self.edit_window.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Dialog)
        self.edit_window.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self.ui.cancel_button.clicked.connect(lambda: self.widget_manager.close_and_delete("appointment_options"))
        self.ui.delete_button.clicked.connect(self._delete_appointment)
        self.ui.edit_appointment_button.clicked.connect(self._edit_calls)
        self.window.show()


    def _delete_appointment(self):
        self.message.setWindowTitle("Confirm Delete")
        self.message.setText("Delete Appointment?")
        self.message.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        self.message.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.message.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        response = self.message.exec()
        self.message_confirm.setStyleSheet("QLabel { color: black; }")
        self.message_confirm.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        self.message_confirm.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.message_confirm.setText("Appointment Deleted")
        if response == QtWidgets.QMessageBox.StandardButton.Yes:
            appt_id = self.appointment_id
            appointment_repository.AppointmentRepository.delete_appointment(appt_id)
            self.message_confirm.exec()
            self.widget_manager.close_and_delete("appointment_options")


    def _edit_calls(self):
        self.widget_manager.close_and_delete("appointment_options")
        self.get_appt_id()
        self.name_box_items()
        self.edit_appt_show()


    def get_appt_id(self):
        self.appt_data = appointment_repository.AppointmentRepository.get_appointment_details_by_id(self.appointment_id)

    def name_box_items(self):
        appt_data = self.appt_data or []
        vehicle_id = appt_data.get("vehicle_id")
        results = vehicle_repository.VehicleRepository.get_vehicles_by_customer_id(vehicle_id)
        combo = self.edit_ui.vehicle_box
        combo.clear()

        if not results:
            combo.addItem("No vehicles found", None)
            return

        for row in results:
             vin, year, make, model, customer_id = row
             combo.addItem(f"{vin}  {year}  {make}  {model}", customer_id)

    def edit_appt_show(self):
        appt = self.appt_data
        if not appt:
            QtWidgets.QMessageBox.critical(self.window, "Error", "Appointment not found.")

        if appt.get("dropoff_type") == "drop":
            self.edit_ui.drop_button.setChecked(True)
        else:
            self.edit_ui.wait_button.setChecked(True)

        self.edit_ui.name_edit.setText(f"{appt.get("first_name")} {appt.get("last_name")},  {appt.get("phone")}")
        self.edit_ui.notes_edit.setText(str(self.appt_data.get("notes")))
        py_date = appt.get("appointment_date")
        date = QDate(py_date.year, py_date.month, py_date.day)
        self.edit_ui.date_widget.setMinimumDate(QDate.currentDate())
        self.edit_ui.date_widget.setSelectedDate(date)
        self.edit_ui.date_widget.setMaximumDate(QDate.currentDate().addYears(1))
        time_slots = [
            "07:00 AM", "07:30 AM", "08:00 AM", "08:30 AM", "09:00 AM", "09:30 AM",
            "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM",
            "01:00 PM", "01:30 PM", "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM",
            "04:00 PM", "04:30 PM", "05:00 PM", "05:30 PM", "06:00 PM"
        ]
        self.edit_ui.time_box.clear()
        self.edit_ui.time_box.addItems(time_slots)
        time_delta = appt.get("appointment_time")
        total_minutes = time_delta.total_seconds() // 60
        hour = int(total_minutes // 60)
        minute = int(total_minutes % 60)

        # Correct formatting
        formatted_time = QTime(hour, minute).toString("hh:mm AP")
        index = self.edit_ui.time_box.findText(formatted_time, QtCore.Qt.MatchFlag.MatchExactly)
        if index != -1:
            self.edit_ui.time_box.setCurrentIndex(index)
        self.edit_ui.cancel_button.clicked.connect(lambda: self.widget_manager.close_and_delete("edit_appointment"))
        self.edit_ui.confirm_button.clicked.connect(self._save_edit)
        self.edit_window.show()

    def _save_edit(self):
        appt_data = self.appt_data
        customer_id, vehicle_id = appt_data.get("customer_id"), appt_data.get("vehicle_id")
        vin, appointment_date = self.edit_ui.vehicle_box.currentData(), self.edit_ui.date_widget.selectedDate(),
        time_text, notes, dropoff_type = self.edit_ui.time_box.currentText(), self.edit_ui.notes_edit.toPlainText(), None
        time_obj = QTime.fromString(time_text, "h:mm AP")  # flexible 12-hour format
        if not time_obj.isValid():
            QtWidgets.QMessageBox.warning(self.edit_window, "Invalid Time", "Selected time is not valid.")
            return
        if self.edit_ui.drop_button.isChecked():
            dropoff_type = "drop"
        elif self.edit_ui.wait_button.isChecked():
            dropoff_type = "wait"

        appointment_repository.AppointmentRepository.update_appointment(
            appointment_id=self.appointment_id,
            customer_id=customer_id,
            vehicle_id=vehicle_id,
            vin=vin,
            date=self.edit_ui.date_widget.selectedDate(),
            time=time_obj,
            notes=notes,
            dropoff_type=dropoff_type
        )
        self.message.setWindowTitle("Alter Appointment")
        self.message.setText("Appointment Changed")
        self.widget_manager.close_and_delete("edit_appointment")
        self.message.exec()








