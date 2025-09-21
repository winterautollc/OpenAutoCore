from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QBuffer, QIODeviceBase
from PyQt6.QtWidgets import QTableWidgetItem
from openauto.repositories import db_handlers
import decimal


class SettingsManager:
    def __init__(self, main_window):
        self.ui = main_window

### SAVES ALL SHOP SETTINGS TO DB. NO PRIMARY KEYS IN THIS TABLE SO THE ENTIRE TABLE IS TRUNCATED AND REWRITTEN ###
    def save_shop_settings(self):
        db = db_handlers.connect_db()
        cursor = db.cursor()
        cursor.execute("TRUNCATE TABLE shop_info")

        image_bytes = self._get_logo_bytes()
        warranty_time = self.ui.warranty_time_checkbox.isChecked()
        warranty_duration = self.ui.warranty_miles_checkbox.isChecked()

        if not warranty_time:
            self.ui.warranty_time_line.setText("")
        if not warranty_duration:
            self.ui.warranty_miles_line.setText("")

        settings = [
            self.ui.shop_name_line.text(),
            self.ui.facility_id_line.text(),
            self.ui.address_line.text(),
            self.ui.city_line.text(),
            self.ui.state_line.text(),
            self.ui.zipcode_line.text(),
            self.ui.disclamer_edit.toPlainText(),
            int(warranty_duration),
            int(warranty_time),
            self.ui.warranty_time_line.text(),
            self.ui.warranty_miles_line.text(),
            float(self.ui.sales_tax_line.text()),
            image_bytes
        ]

        query = '''INSERT INTO shop_info (shop_name, facility_id, address, city, state, zip, disclaimer,
                  warranty_duration, warranty_time, months, miles, sales_tax_rate, shop_logo)
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        cursor.execute(query, settings)
        db.commit()
        cursor.close()
        db.close()

        self._show_message("Shop Settings Saved")

### SAVES PRICING MATRIX TO DB. NO PRIMARY KEYS USED SO ENTIRE TABLE IS TRUNCATED AND REWRITTEN. ###
    def save_pricing_matrix(self):
        db_conn = db_handlers.connect_db()
        cursor = db_conn.cursor()
        cursor.execute("TRUNCATE TABLE pricing_matrix")

        for row in range(self.ui.matrix_table.rowCount()):
            try:
                min_cost = float(self.ui.matrix_table.item(row, 0).text())
                max_cost = float(self.ui.matrix_table.item(row, 1).text())
                multiplier = float(self.ui.matrix_table.item(row, 2).text())
                percent_return = float(self.ui.matrix_table.item(row, 3).text())
            except (ValueError, TypeError, AttributeError):
                continue

            cursor.execute("""
                INSERT INTO pricing_matrix (min_cost, max_cost, multiplier, percent_return)
                VALUES (%s, %s, %s, %s)
            """, (min_cost, max_cost, multiplier, percent_return))

        db_conn.commit()
        cursor.close()
        db_conn.close()
        self._show_message("Your Pricing Matrix Has Been Saved")


### LOADS ALL INFORMATION FROM shop_info TABLE ###
    def load_shop_info(self):
        db = db_handlers.connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM shop_info")
        info = cursor.fetchone()
        cursor.close()
        db.close()

        self.ui.warranty_time_line.hide()
        self.ui.months_label.hide()
        self.ui.warranty_miles_line.hide()
        self.ui.distance_label.hide()

        if not info:
            self._show_message("You Currently Have No Shop Info Saved. Please Navigate To Settings.")
            return

        self._set_warranty_flags(info)
        self._populate_shop_info(info)

    def _set_warranty_flags(self, info):
        if info[7] == 1:
            self.ui.warranty_miles_checkbox.setChecked(True)
            self.ui.distance_label.show()
            self.ui.warranty_miles_line.show()
        if info[8] == 1:
            self.ui.warranty_time_checkbox.setChecked(True)
            self.ui.warranty_time_line.show()
            self.ui.months_label.show()

    def _populate_shop_info(self, info):
        self.ui.shop_name_line.setText(info[0])
        self.ui.facility_id_line.setText(info[1])
        self.ui.address_line.setText(info[2])
        self.ui.city_line.setText(info[3])
        self.ui.state_line.setText(info[4])
        self.ui.zipcode_line.setText(info[5])
        self.ui.disclamer_edit.setText(info[6])
        self.ui.warranty_time_line.setText(info[9])
        self.ui.warranty_miles_line.setText(info[10])
        self.ui.sales_tax_line.setText(str(info[13]))

        buffer = QBuffer()
        buffer.setData(info[11])
        buffer.open(QIODeviceBase.OpenModeFlag.ReadOnly)
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.data())
        buffer.close()
        self.ui.shop_logo.setPixmap(pixmap)

    def set_warranty_time(self):
        if self.ui.warranty_time_checkbox.isChecked():
            self.ui.warranty_time_line.show()
            self.ui.months_label.show()
        else:
            self.ui.warranty_time_line.hide()
            self.ui.warranty_time_line.setText("")
            self.ui.months_label.hide()

    def set_warranty_duration(self):
        if self.ui.warranty_miles_checkbox.isChecked():
            self.ui.warranty_miles_line.show()
            self.ui.distance_label.show()
        else:
            self.ui.warranty_miles_line.hide()
            self.ui.warranty_miles_line.setText("")
            self.ui.distance_label.hide()

    def load_shop_logo(self):
        file_filter = "Image Files (*.jpg *.png *.svg)"
        logo_select = QtWidgets.QFileDialog.getOpenFileName(
            caption="Select Image", filter=file_filter,
            initialFilter="Image Files (*.jpg *.png *.svg)"
        )

        if logo_select[0]:
            pixmap = QPixmap(logo_select[0])
            self.ui.shop_logo.setPixmap(pixmap)
            self.ui.shop_logo.setScaledContents(True)

    def save_labor_rates(self):
        db_conn = db_handlers.connect_db()
        cursor = db_conn.cursor()
        cursor.execute("TRUNCATE TABLE labor_rates")

        for row in range(self.ui.labor_table.rowCount()):
            try:
                labor_rate = float(self.ui.labor_table.item(row, 0).text())
                labor_type = self.ui.labor_table.item(row, 1).text()
            except (ValueError, TypeError, AttributeError):
                continue

            cursor.execute("INSERT INTO labor_rates (labor_rate, labor_type) VALUES (%s, %s)", (labor_rate, labor_type))

        db_conn.commit()
        cursor.close()
        db_conn.close()
        self._show_message("Your Labor Rates Have Been Saved")

    def add_labor_rates(self):
        self._add_empty_row(self.ui.labor_table)

    def add_matrix_row(self):
        row_count = self.ui.matrix_table.rowCount()
        new_min_cost = decimal.Decimal("0.00")

        if row_count > 0:
            last_max_item = self.ui.matrix_table.item(row_count - 1, 1)
            if last_max_item and last_max_item.text().strip():
                try:
                    last_max = decimal.Decimal(last_max_item.text())
                    new_min_cost = last_max + decimal.Decimal("0.01")
                except Exception as e:
                    print(f"Decimal error: {e}")

        self.ui.matrix_table.insertRow(row_count)

        min_item = QTableWidgetItem(f"{new_min_cost:.2f}")
        min_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.ui.matrix_table.setItem(row_count, 0, min_item)

        for col in range(1, self.ui.matrix_table.columnCount()):
            item = QTableWidgetItem("")
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.ui.matrix_table.setItem(row_count, col, item)

    def remove_matrix_row(self):
        self._remove_current_row(self.ui.matrix_table)

    def remove_labor_rate(self):
        self._remove_current_row(self.ui.labor_table)

    def _remove_current_row(self, table):
        current_row = table.currentRow()
        if current_row >= 0:
            table.removeRow(current_row)

    def _add_empty_row(self, table):
        row_count = table.rowCount()
        table.insertRow(row_count)
        for col in range(table.columnCount()):
            item = QTableWidgetItem("")
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            table.setItem(row_count, col, item)

    def _get_logo_bytes(self):
        pixmap = self.ui.shop_logo.pixmap()
        buffer = QBuffer()
        buffer.open(QIODeviceBase.OpenModeFlag.WriteOnly)
        pixmap.save(buffer, "PNG")
        image_bytes = buffer.data().data()
        buffer.close()
        return image_bytes

    def _show_message(self, text):
        self.ui.message.setText(text)
        self.ui.message.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.ui.message.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.ui.message.show()
