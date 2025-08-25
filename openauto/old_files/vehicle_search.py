from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6 import QtCore
from vehicle_search_form import Ui_Form
from pyvin import VIN
import db_handlers
import mysql.connector



class VehicleSearch(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.vin_search_button.clicked.connect(self.find_info)
        self.abort_button.clicked.connect(self.cancel_changes)
        self.vin = VIN

    def cancel_changes(self):
        self.close()

    def find_info(self):
        try:
            self.vin = VIN(self.vin_line.text())
            self.year_line.setText(self.vin.ModelYear)
            self.make_line.setText(self.vin.Make)
            self.model_line.setText(self.vin.Model)
            self.engine_line.setText(self.vin.DisplacementL)
            self.trim_line.setText(self.vin.Trim)
        except:
            self.vin_line.setText("Please choose a proper vin number")



    def add_vehicle(self):
        self.vin_search_button.clicked.connect(self.find_info)


### RETURNS customer_id PRIMARY KEY ID FROM MYSQL customers TABLE AND CALLS save_vehicle FUNCTION###
    def load_customer_id(self):
        db_conn = db_handlers.connect_db()
        customer_curser = db_conn.cursor()
        selected_row = self.customer_table.currentRow()
        row_data = []
        for col in range(self.customer_table.columnCount()):
            item = self.customer_table.item(selected_row, col)
            row_data.append(item.text() if item else "")
        load_options = """SELECT customer_id FROM customers WHERE(last_name = %s AND first_name = %s AND
                                address = %s AND city = %s AND state = %s AND zip = %s AND phone = %s AND alt_phone = %s AND
                                email = %s)"""

        customer_curser.execute(load_options, row_data)
        self.customer_id = customer_curser.fetchone()
        self.save_vehicle()

if __name__ == "__main__":
    import sys
    new_vehicle_opener = QApplication(sys.argv)
    window = VehicleSearch()
    window.show()
    new_vehicle_opener.exec()
