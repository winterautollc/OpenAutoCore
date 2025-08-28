from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6 import QtWidgets, QtCore
from PyQt6 import QtGui
from PyQt6.QtWidgets import QStyledItemDelegate
from openauto.repositories import customer_repository, vehicle_repository, settings_repository, db_handlers
from openauto.subclassed_widgets import event_handlers
import decimal
import os




def apply_stylesheet(widget, relative_path):
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    theme_path = os.path.join(base_path, relative_path)
    try:
        with open(theme_path, "r") as f:
            widget.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"⚠️ Could not load theme: {theme_path}")

class CustomerTableSmall(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        customer_columns = ("LAST", "FIRST NAME", "PHONE", "ID")
        self.setColumnCount(4)
        self.setColumnHidden(3, True)
        self.setHorizontalHeaderLabels(customer_columns)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        theme = "theme/dark_theme.qss"
        apply_stylesheet(self, theme)
        self.load_customer_data()



    def load_customer_data(self):
        self.setRowCount(db_handlers.customer_rows())
        result = customer_repository.CustomerRepository.get_all_customer_names() or []
        table_row = 0
        for row in result:
            for col in range(4):
                item = QtWidgets.QTableWidgetItem(str(row[col]))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.setItem(table_row, col, item)
            table_row += 1

    def update_customers(self, customer_small_data):
        table_row = 0
        self.setRowCount(db_handlers.customer_rows())
        for row in customer_small_data:
            for col in range(4):
                item = QtWidgets.QTableWidgetItem(str(row[col]))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.setItem(table_row, col, item)
            table_row += 1



class VehicleTableSmall(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        vehicle_columns = ("YEAR", "MAKE", "MODEL", "ID", "VIN")
        self.setColumnCount(5)
        self.setColumnHidden(3, True)
        self.setColumnHidden(4, True)
        self.setHorizontalHeaderLabels(vehicle_columns)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        theme = "theme/dark_theme.qss"
        apply_stylesheet(self, theme)
        self.load_vehicle_data()

    def load_vehicle_data(self):
        self.setRowCount(db_handlers.vehicle_rows())
        result = vehicle_repository.VehicleRepository.get_all_vehicles() []
        table_row = 0
        for row in result:
            for col in range(5):
                item = QtWidgets.QTableWidgetItem(str(row[col]))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.setItem(table_row, col, item)
            table_row += 1

    def update_vehicles(self, vehicle_small_data):
        self.setRowCount(db_handlers.vehicle_rows())
        table_row = 0
        for row in vehicle_small_data:
            for col in range(5):
                item = QtWidgets.QTableWidgetItem(str(row[col]))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.setItem(table_row, col, item)
            table_row += 1

### SUBCLASSED QTABLEWIDGET TO SHOW PARTS MATRIX DATA ###
class MatrixTable(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        matrix_table_names = ("$ From", "$ To", "Multiply", "% Average Margin")
        self.setColumnCount(4)
        self.setGridStyle(QtCore.Qt.PenStyle.DashDotLine)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.setHorizontalHeaderLabels(matrix_table_names)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setItemDelegateForColumn(0, FloatDelegate(self))
        self.setItemDelegateForColumn(1, FloatDelegate(self))
        self.setItemDelegateForColumn(3, FloatDelegate(self))
        self.itemChanged.connect(self.update_changes)
        self.load_matrix_data()

#### LOADS SAVED PRICING MATRIX DATA TO QTABLEWIDGET ####
    def load_matrix_data(self):
        result = settings_repository.SettingsRepository.load_matrix_table() or []

        for row_index, row_data in enumerate(result):
            self.insertRow(row_index)
            for col_index, value in enumerate(row_data):
                if isinstance(value, decimal.Decimal):
                    item = QTableWidgetItem(f"{value:.2f}")
                else:
                    item = QTableWidgetItem(str(value))

                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
                self.setItem(row_index, col_index, item)


### AUTO POPULATES THE PERCENT MARGIN WHEN CREATING PRICING MATRIX ###
    def update_changes(self, item):
        row = item.row()
        try:
            min_item_cost = self.item(row, 0)
            max_item_cost = self.item(row, 1)
            item_multiplier = self.item(row, 2)

            if not all([min_item_cost, max_item_cost, item_multiplier]):
                return

            min_cost = float(min_item_cost.text())
            max_cost = float(max_item_cost.text())
            multiplier = float(item_multiplier.text())
            cost_price = float(min_cost + max_cost / 2)
            selling_price = float(cost_price * multiplier)


            if min_cost == 0:
                percent_return = 0
            else:
                percent_return = ((selling_price - cost_price) / selling_price * 100)

                result_item = QTableWidgetItem(f"{percent_return:.2f}")
                result_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
                result_item.setFlags(result_item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)

                self.blockSignals(True)
                self.setItem(row, 3, result_item)
                self.blockSignals(False)

        except ValueError:
            pass



### ONLY ALLOWS NUMBERS TO PUT INTO PRICING MATRIX QTABLEWIDGET ###
class FloatDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QtWidgets.QLineEdit(parent)
        validator = QtGui.QDoubleValidator(0.0, 999999.99, 2, parent)  # Adjust range/precision as needed
        validator.setNotation(QtGui.QDoubleValidator.Notation.StandardNotation)
        editor.setValidator(validator)
        return editor




class LaborTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        labor_items = ("LABOR RATE", "LABOR TYPE")
        self.setColumnCount(2)
        self.setGridStyle(QtCore.Qt.PenStyle.DashDotLine)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.setHorizontalHeaderLabels(labor_items)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setItemDelegateForColumn(0, FloatDelegate(self))
        self.load_labor_rates()


    def load_labor_rates(self):
        result = settings_repository.SettingsRepository.load_labor_table() []

        for row_index, row_data in enumerate(result):
            self.insertRow(row_index)
            for col_index, value in enumerate(row_data):
                if isinstance(value, decimal.Decimal):
                    item = QTableWidgetItem(f"{value:.2f}")
                else:
                    item = QTableWidgetItem(str(value))

                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
                self.setItem(row_index, col_index, item)
