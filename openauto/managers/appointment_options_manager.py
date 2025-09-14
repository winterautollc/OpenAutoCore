from PyQt6 import QtWidgets, QtCore
from openauto.ui import appointment_options, edit_appointment
from openauto.subclassed_widgets.event_handlers import WidgetManager
from openauto.repositories import appointment_repository, vehicle_repository
from PyQt6.QtCore import QDate, QTime
import datetime


class AppointmentOptionsManager:
    def __init__(self, parent, appt_id):
        self.parent = parent
        self.widget_manager = WidgetManager()
        self.appointment_id = appt_id
        self.message = QtWidgets.QMessageBox(self.parent)
        self.message_confirm = QtWidgets.QMessageBox(self.parent)

        self.window, self.ui = self.widget_manager.create_or_restore(
            "appointment_options", QtWidgets.QWidget, appointment_options.Ui_appointment_options_form
            )

        self.edit_window, self.edit_ui = self.widget_manager.create_or_restore(
            "edit_appointment", QtWidgets.QWidget, edit_appointment.Ui_edit_appt_form
            )

        self._setup_ui()



    def _setup_ui(self):
        self.window.setParent(self.parent, QtCore.Qt.WindowType.Dialog)
        self.window.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Dialog)
        self.window.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self.edit_window.setParent(self.parent, QtCore.Qt.WindowType.Dialog)
        self.edit_window.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Dialog)
        self.edit_window.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self.ui.cancel_appt_options_button.clicked.connect(lambda: self.widget_manager.close_and_delete("appointment_options"))
        self.ui.delete_appointment_button.clicked.connect(self._delete_appointment)
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
        self.get_appt_id()
        if not getattr(self, "appt_data", None):
            QtWidgets.QMessageBox.warning(self.window, "Not found", "Couldn't load this appointment.")
            return
        self.name_box_items()
        self.edit_appt_show()
        self.widget_manager.close_and_delete("appointment_options")

    def get_appt_id(self):
        data = appointment_repository.AppointmentRepository.get_appointment_details_by_id(self.appointment_id)
        if isinstance(data, list):
            data = data[0] if data else {}
        self.appt_data = data or {}


    def name_box_items(self):
        appt = self.appt_data or {}
        customer_id = appt.get("customer_id")
        results = vehicle_repository.VehicleRepository.get_vehicles_by_customer_id(customer_id)
        combo = self.edit_ui.vehicle_box
        combo.clear()

        if not results:
            combo.addItem("No vehicles found", None)
            return

        for row in results:
            if len(row) >= 6:
                vin, year, make, model, owner_id, vehicle_id = row
            else:
                vin, year, make, model, owner_id = row
                vehicle_id = None
            combo.addItem(f"{vin}  {year}  {make}  {model}", vehicle_id)


    def edit_appt_show(self):
        appt = self.appt_data
        if not appt:
            QtWidgets.QMessageBox.critical(self.window, "Error", "Appointment not found.")
            return



        if appt.get("dropoff_type") == "drop":
            self.edit_ui.drop_edit_button.setChecked(True)
        else:
            self.edit_ui.wait_edit_button.setChecked(True)

        first = appt.get('first_name') or ""
        last = appt.get('last_name') or ""
        phone = appt.get('phone') or ""
        self.edit_ui.name_edit_line.setText(f"{first} {last},  {phone}")

        self.edit_ui.notes_appt_edit.setText(str(appt.get("notes") or ""))

        py_date = appt.get("appointment_date")
        qdate = QDate.currentDate()
        if isinstance(py_date, datetime.datetime):
            d = py_date.date()
            qdate = QDate(d.year, d.month, d.day)
        elif isinstance(py_date, datetime.date):
            qdate = QDate(py_date.year, py_date.month, py_date.day)
        elif isinstance(py_date, str):
            for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
                try:
                    d = datetime.datetime.strptime(py_date, fmt).date()
                    qdate = QDate(d.year, d.month, d.day)
                    break
                except ValueError:
                    pass

        self.edit_ui.date_widget.setMinimumDate(QDate.currentDate())
        self.edit_ui.date_widget.setSelectedDate(qdate)
        self.edit_ui.date_widget.setMaximumDate(QDate.currentDate().addYears(1))

        self.edit_ui.time_box.clear()
        time_slots = [
            "07:00 AM", "07:30 AM", "08:00 AM", "08:30 AM", "09:00 AM", "09:30 AM",
            "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM",
            "01:00 PM", "01:30 PM", "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM",
            "04:00 PM", "04:30 PM", "05:00 PM", "05:30 PM", "06:00 PM"
        ]
        self.edit_ui.time_box.addItems(time_slots)

        hour, minute = 7, 0
        tval = appt.get("appointment_time")
        if isinstance(tval, datetime.timedelta):
            total_minutes = int(tval.total_seconds() // 60)
            hour, minute = total_minutes // 60, total_minutes % 60
        elif isinstance(tval, datetime.time):
            hour, minute = tval.hour, tval.minute
        elif isinstance(tval, datetime.datetime):
            hour, minute = tval.hour, tval.minute
        elif isinstance(tval, str):
            for fmt in ("%H:%M:%S", "%I:%M %p", "%H:%M"):
                try:
                    parsed = datetime.datetime.strptime(tval, fmt)
                    hour, minute = parsed.hour, parsed.minute
                    break
                except ValueError:
                    pass

        formatted_time = QTime(hour, minute).toString("hh:mm AP")
        idx = self.edit_ui.time_box.findText(formatted_time, QtCore.Qt.MatchFlag.MatchExactly)
        if idx != -1:
            self.edit_ui.time_box.setCurrentIndex(idx)

        self.edit_ui.cancel_edit_appt_button.clicked.connect(
            lambda: self.widget_manager.close_and_delete("edit_appointment")
        )
        self.edit_ui.confirm_edit_appt_button.clicked.connect(self._save_edit)
        self.edit_window.show()


    def _save_edit(self):
        appt = self.appt_data or {}
        customer_id = appt.get("customer_id")

        vehicle_id = self.edit_ui.vehicle_box.currentData()

        vin = None
        txt = self.edit_ui.vehicle_box.currentText()
        if txt and " " in txt:
            vin = txt.split()[0]

        time_text = self.edit_ui.time_box.currentText()
        time_obj = QTime.fromString(time_text, "hh:mm AP")
        if not time_obj.isValid():
            QtWidgets.QMessageBox.warning(self.edit_window, "Invalid Time", "Selected time is not valid.")
            return

        dropoff_type = "drop" if self.edit_ui.drop_edit_button.isChecked() else "wait"


        appointment_repository.AppointmentRepository.update_appointment(
            appointment_id=self.appointment_id,
            customer_id=customer_id,
            vehicle_id=vehicle_id,
            vin=vin,
            date=self.edit_ui.date_widget.selectedDate(),
            time=time_obj,
            notes=self.edit_ui.notes_appt_edit.toPlainText(),
            dropoff_type=dropoff_type
        )
        self.message.setWindowTitle("Alter Appointment")
        self.message.setText("Appointment Changed")
        self.widget_manager.close_and_delete("edit_appointment")
        self.message.exec()









