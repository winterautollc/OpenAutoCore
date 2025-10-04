from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QCalendarWidget, QTableWidget
from PyQt6.QtCore import QDate, pyqtSignal
from openauto.repositories.appointment_repository import AppointmentRepository


### INTERACTIVE QCALENDARWIDGET THAT LOADS DAILY APPOINTMENTS ###
class AptCalendar(QCalendarWidget):
    date_selected = pyqtSignal(QDate)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.setGridVisible(True)
        self.setMinimumDate(QDate.currentDate())
        self.setMaximumDate(QDate.currentDate().addYears(1))
        self.setSelectedDate(QDate.currentDate())
        self.showSelectedDate()
        self.clicked.connect(self.handle_date_clicked)
        self.hide()

### EMITS SELECTED DATE ###
    def handle_date_clicked(self, date: QDate):
        self.date_selected.emit(date)


### WEEKLY SCHEDULE QTABLEWIDGET ###
class WeeklySchedule(QTableWidget):
    add_appointment = pyqtSignal()
    appointment_options = pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(7)
        self.set_horizontal_headers_for_date(QDate.currentDate())
        self.selected_row = None
        self.selected_column = None
        self.selected_date = QDate.currentDate()
        self.setRowCount(23)
        self.setVerticalHeaderLabels([
            "7:00 AM", "7:30 AM", "8:00 AM", "8:30 AM", "9:00 AM", "9:30 AM", "10:00 AM", "10:30 AM", "11:00 AM",
            "11:30 AM", "12:00 PM", "12:30 PM", "1:00 PM", "1:30 PM", "2:00 PM", "2:30 PM", "3:00 PM", "3:30 PM",
            "4:00 PM", "4:30 PM", "5:00 PM", "5:30 PM", "6:00 PM"
        ])
        self.verticalHeader().setDefaultSectionSize(50)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.load_appointments(QDate.currentDate())
        self.cellClicked.connect(self.date_clicked)


    def load_appointments(self, selected_date: QDate):
        self.clearContents()

        start_of_week = selected_date.addDays(1 - selected_date.dayOfWeek())  # Monday
        end_of_week = start_of_week.addDays(6)

        appointments = AppointmentRepository.get_appointments_for_week(start_of_week, end_of_week)

        for appt in appointments:
            py_date = appt["appointment_date"]
            date = QDate(py_date.year, py_date.month, py_date.day)
            time_delta = appt["appointment_time"]
            total_minutes = time_delta.total_seconds() // 60
            hour = int(total_minutes // 60)
            minute = int(total_minutes % 60)

            row = (hour - 7) * 2 + (1 if minute >= 30 else 0)  # assuming schedule starts at 7:00 AM
            col = date.dayOfWeek() - 1  # Monday = 0

            if 0 <= row < self.rowCount() and 0 <= col < self.columnCount():
                name = f"{appt['first_name']} {appt['last_name']},   {appt["notes"]}, {appt["dropoff_type"]}"
                item = QtWidgets.QTableWidgetItem(name)
                item.setData(QtCore.Qt.ItemDataRole.UserRole, appt)  # store metadata
                self.setItem(row, col, item)

    ### LOADS CURRENT WEEK TO DATE IN COLUMNS ###
    def set_horizontal_headers_for_date(self, selected_date: QDate):
        day_of_week = selected_date.dayOfWeek()  # 1 = Monday
        monday = selected_date.addDays(-(day_of_week - 1))  # Get Monday of the current week

        self.week_dates = [monday.addDays(i) for i in range(7)]
        labels = [f"{d.toString('ddd')} {d.toString('MM/dd')}" for d in self.week_dates]
        self.setHorizontalHeaderLabels(labels)


    def date_clicked(self, row, column):
        self.selected_row = row
        self.selected_column = column
        self.selected_date = self.week_dates[column]  # assumes horizontal headers already set

        item = self.item(row, column)
        if item is None or item.text().strip() == "":
            self.add_appointment.emit()
        else:
        # Extract appointment ID from the cell
            appointment_data = item.data(QtCore.Qt.ItemDataRole.UserRole)
            if appointment_data:
                appt_id = appointment_data.get("id")
                self.appointment_options.emit(appt_id)






### LOADS SCHEDULE FOR THE DAY ###
class HourlySchedule(QTableWidget):
    add_appointment = pyqtSignal()
    edit_appointment = pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(1)
        self.setRowCount(23)
        self.selected_row = None
        self.selected_date = QDate.currentDate()
        self.setHorizontalHeaderLabels(["Appointments"])
        self.setVerticalHeaderLabels([
            "7:00 AM", "7:30 AM", "8:00 AM", "8:30 AM", "9:00 AM", "9:30 AM", "10:00 AM", "10:30 AM", "11:00 AM",
            "11:30 AM", "12:00 PM", "12:30 PM", "1:00 PM", "1:30 PM", "2:00 PM", "2:30 PM", "3:00 PM", "3:30 PM",
            "4:00 PM", "4:30 PM", "5:00 PM", "5:30 PM", "6:00 PM"
        ])
        self.verticalHeader().setDefaultSectionSize(50)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.load_schedule_for_day(QDate.currentDate())
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.cellClicked.connect(self.add_or_edit_appointment)

    def load_schedule_for_day(self, date: QDate):
        self.clearContents()
        self.selected_date = date
        appointments = AppointmentRepository.get_appointments_for_week(date, date)
        for appt in appointments:
            time_delta = appt["appointment_time"]
            total_minutes = time_delta.total_seconds() // 60
            hour = int(total_minutes // 60)
            minute = int(total_minutes % 60)

            row = (hour - 7) * 2 + (1 if minute >= 30 else 0)
            if 0 <= row < self.rowCount():
                summary = f"{appt['first_name']} {appt['last_name']} - {appt["notes"]}, {appt["dropoff_type"]}"
                item = QtWidgets.QTableWidgetItem(summary)
                item.setData(QtCore.Qt.ItemDataRole.UserRole, appt)
                self.setItem(row, 0, item)



    def add_or_edit_appointment(self, row, column):
        self.selected_row = row
        item = self.item(row, column)
        if item is None or item.text().strip() == "":
            self.add_appointment.emit()
        else:
            # Extract appointment ID from the cell
            appointment_data = item.data(QtCore.Qt.ItemDataRole.UserRole)
            if appointment_data:
                appt_id = appointment_data.get("id")
                self.edit_appointment.emit(appt_id)

