from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QTableWidget, QApplication
from PyQt6 import QtWidgets, QtCore
from openauto.repositories import db_handlers, customer_repository, vehicle_repository, estimates_repository
from openauto.managers.customer_options_manager import CustomerOptionsManager
from openauto.managers.estimate_options_manager import EstimateOptionsManager


### SUBCLASSED QTABLEWIDGET THAT LOADS ALL RECORDED CUSTOMERS AND CONTACT INFO STORED IN MYSQL ###
class CustomerTable(QTableWidget):
    vehicle_signal_request = pyqtSignal(int)  ### PYQTSIGNALS FOR PUSHBUTTONS IN managers.customer_options_manager.py ###
    ro_signal_request = pyqtSignal()
    estimate_signal_request = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        customer_table_names = ("LAST NAME", "FIRST NAME", "ADDRESS", "CITY", "STATE", "ZIP", "PHONE", "ALT PHONE", "EMAIL", "ID")
        self.setColumnCount(10)
        self.setColumnHidden(9, True)
        self.setGridStyle(QtCore.Qt.PenStyle.DashDotLine)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.setHorizontalHeaderLabels(customer_table_names)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.customer_id = None
        self.load_customer_data()
        self.cellDoubleClicked.connect(self.options_load)

    def options_load(self):
        self.get_customer_id()
        self.show_customer_options()

### DECLARES customer_options SEE managers/customer_options_manager.py ###
    def show_customer_options(self):
        self.customer_options_manager = CustomerOptionsManager(
            parent=self.window(),
            customer_id=self.customer_id,
            vehicle_signal=self.vehicle_signal_request,
            ro_signal=self.ro_signal_request
        )




###  LOADS DATA FROM MYSQL TO CUSTOMERS PAGE.  FUNCTION IS ONLY CALLED ONCE ON STARTUP ###
    def load_customer_data(self):
        self.setRowCount(db_handlers.customer_rows())
        result = customer_repository.CustomerRepository.get_all_customer_info() or []
        table_row = 0
        for row in result:
            for col in range(10):
                item = QtWidgets.QTableWidgetItem(str(row[col]))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.setItem(table_row, col, item)
            table_row += 1


####  CONNECTED TO QTHREAD THAT MONITORS ALL MYSQL CHANGES FOR EVERY TABLE AND UPDATES QTABLEWIDGET ####
    def update_customers(self, customer_data):
        table_row = 0
        self.setRowCount(db_handlers.customer_rows())
        for row in customer_data:
            for col in range(10):
                item = QtWidgets.QTableWidgetItem(str(row[col]))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.setItem(table_row, col, item)
            table_row += 1


    ### FINDS PRIMARY KEY ID FOR CUSTOMERS AND RETURNS IT TO MAKE CUSTOMER CHANGES ###
    def get_customer_id(self):
        selected_row = self.currentRow()
        selected_column = self.currentColumn()
        selected_data = []
        selected_name = self.itemAt(selected_row, selected_column)
        for column in range(self.model().columnCount()):
            index = self.model().index(selected_row, column)
            selected_data.append(index.data())
        self.customer_id = selected_data[9]


class EstimateTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.estimate_id = None
        estimate_names = ("ID", "RO NUMBER", "DATE", "NAME", "YEAR", "MAKE", "MODEL", "TECH", "TOTAL")
        self.setGridStyle(QtCore.Qt.PenStyle.DashDotLine)
        self.setColumnCount(9)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.setHorizontalHeaderLabels(estimate_names)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.setColumnHidden(0, True)
        self._show_estimates()
        self.cellDoubleClicked.connect(self._estimate_options_load)

    def _show_estimates(self):
        self.setRowCount(db_handlers.estimate_rows())
        result = estimates_repository.EstimateRepository.load_estimate() or []
        table_row = 0
        for row in result:
            for col in range(9):
                item = QtWidgets.QTableWidgetItem(str(row[col]))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.setItem(table_row, col, item)
            table_row += 1
    def update_estimates(self, estimate_data):
        table_row = 0
        self.setRowCount(db_handlers.estimate_rows())
        for row in estimate_data:
            for col in range(9):
                item = QtWidgets.QTableWidgetItem(str(row[col]))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.setItem(table_row, col, item)
            table_row += 1



    def _estimate_options_load(self):
        self.get_estimate_id()
        self._show_options()

    def get_estimate_id(self):
        selected_row = self.currentRow()
        selected_column = self.currentColumn()
        selected_data = []
        selected_name = self.itemAt(selected_row, selected_column)
        for column in range(self.model().columnCount()):
            index = self.model().index(selected_row, column)
            selected_data.append(index.data())
        self.estimate_id = selected_data[0]

    def _show_options(self):
        self.estimate_options_manager = EstimateOptionsManager(
            parent=self.window(),
            estimate_id = self.estimate_id)



class ShowAll(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        all_table_names = ("RO NUMBER", "DATE", "NAME", "YEAR", "MAKE", "MODEL", "TECH", "TOTAL", "STATUS")
        self.setMouseTracking(True)
        self.setColumnCount(9)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.setHorizontalHeaderLabels(all_table_names)
        self.setVisible(False)


class WorkingTable(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        working_names = ("RO NUMBER", "DATE", "NAME", "YEAR", "MAKE", "MODEL", "TECH", "TOTAL")
        self.setGridStyle(QtCore.Qt.PenStyle.DashDotLine)
        self.setColumnCount(8)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.setHorizontalHeaderLabels(working_names)



class ApprovedTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        approved_names = ("RO NUMBER", "DATE", "NAME", "YEAR", "MAKE", "MODEL", "TECH", "TOTAL")
        self.setMouseTracking(True)
        self.setGridStyle(QtCore.Qt.PenStyle.DashDotLine)
        self.setColumnCount(8)
        self.setHorizontalHeaderLabels(approved_names)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)


class CheckoutTable(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        checkout_names = ("RO NUMBER", "DATE", "NAME", "YEAR", "MAKE", "MODEL", "TECH", "TOTAL")
        self.setMouseTracking(True)
        self.setGridStyle(QtCore.Qt.PenStyle.DashDotLine)
        self.setColumnCount(8)
        self.setHorizontalHeaderLabels(checkout_names)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)


### SUBCLASSED QTABLEWIDGET FOR vehicles DATABASE TABLE ###
class VehicleTable(QtWidgets.QTableWidget):
    ro_signal_request = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        vehicle_table_names = ("VIN", "YEAR", "MAKE", "MODEL", "ENGINE", "TRIM", "LAST NAME", "FIRST NAME", "ID")
        self.setColumnCount(9)
        self.setColumnHidden(8, True)
        self.clearSelection()
        self.setRowCount(db_handlers.vehicle_rows())
        self.setGridStyle(QtCore.Qt.PenStyle.DashDotLine)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.setHorizontalHeaderLabels(vehicle_table_names)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setFrameStyle(QtWidgets.QFrame.Shape.NoFrame)
        self.setAlternatingRowColors(True)
        self.vehicle_id = None
        self.load_vehicle_data()
        self.cellClicked.connect(self.copy_vin)
        self.cellDoubleClicked.connect(self.on_vehicle_row_clicked)


### INITIAL LOADING OF VEHICLE DATA FROM DATABASE TABLE TO THE QTABLEWIDGET. CALLED ONLY ONCE ####
    def load_vehicle_data(self):
        result = vehicle_repository.VehicleRepository.get_all_vehicle_info() or []
        table_row = 0
        for row in result:
            for col in range(9):
                item = QtWidgets.QTableWidgetItem(str(row[col]))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.setItem(table_row, col, item)
            table_row += 1



### CONNECTED TO SQLMONITOR QTHREAD IN event_handlers TO DO REAL TIME UPDATES TO THE VEHICLE QTABLEWIDGET ###
    def update_vehicles(self, vehicle_data):
        self.setRowCount(db_handlers.vehicle_rows())
        table_row = 0
        for row in vehicle_data:
            for col in range(9):
                item = QtWidgets.QTableWidgetItem(str(row[col]))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.setItem(table_row, col, item)
            table_row += 1

    def on_vehicle_row_clicked(self):
        self.get_vehicle_id()
        self.show_vehicle_options()


    def get_vehicle_id(self):
        selected_row = self.currentRow()
        selected_column = self.currentColumn()
        selected_data = []
        selected_name = self.itemAt(selected_row, selected_column)
        for column in range(self.model().columnCount()):
            index = self.model().index(selected_row, column)
            selected_data.append(index.data())
        self.vehicle_id = selected_data[8]
        # self.vehicle_id = vehicle_repository.VehicleRepository.get_vehicle_id_by_details(selected_data[:6])
        self.vin_veh_id = [selected_data[0], self.vehicle_id]





    def show_vehicle_options(self):
        from openauto.managers.vehicle_options_manager import VehicleOptionsManager

        self.vehicle_options_manager = VehicleOptionsManager(
            parent=self.window(),
            vehicle_id=self.vin_veh_id,
            new_ro_request=self.ro_signal_request
            )

    def copy_vin(self):
        row = self.currentRow()
        item = self.item(row, 0)
        if item:
            clipboard = QApplication.clipboard()
            clipboard.setText(item.text())

class ROTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        ro_headers = ["TYPE", "PART NUMBER", "DESCRIPTION", "COST", "SELL", "TAX"]
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(ro_headers)

        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.resizeColumnsToContents()
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)


