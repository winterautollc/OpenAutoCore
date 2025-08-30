from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import pyqtSignal
from openauto.ui import new_ro
from openauto.subclassed_widgets import small_tables
from openauto.managers import vehicle_manager
from openauto.repositories.repair_orders_repository import RepairOrdersRepository


class NewROManager:
    cust_id_small_signal = pyqtSignal(str)

    def __init__(self, main_window):
        self.ui = main_window
        self.vehicle_manager = vehicle_manager.VehicleManager(self)
    def add_repair_order(self):
        self.ui.new_ro_page, self.ui.new_ro_page_ui = self.ui.widget_manager.create_or_restore(
            "new_repair_order", QtWidgets.QWidget, new_ro.Ui_create_ro
        )

        self.ui.new_ro_page.setParent(self.ui, QtCore.Qt.WindowType.Dialog)

        self.ui.new_ro_page.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.Dialog
        )

        self.ui.new_ro_page.setWindowModality(QtCore.Qt.WindowModality.WindowModal)

        self.ui.new_ro_page_ui.abort_button.clicked.connect(
            lambda: self.ui.widget_manager.close_and_delete("new_repair_order"))

        self._load_small_tables()
        self._connect_signals()
        self.ui.new_ro_page_ui.add_vehicle_button.hide()
        self.ui.new_ro_page.show()

    def _load_small_tables(self):
        self.ui.customer_table_small = small_tables.CustomerTableSmall()
        self.ui.new_ro_page_ui.gridLayout_2.addWidget(self.ui.customer_table_small, 2, 0, 1, 1)

        self.ui.vehicle_table_small = small_tables.VehicleTableSmall()
        self.ui.new_ro_page_ui.gridLayout_3.addWidget(self.ui.vehicle_table_small, 1, 0, 1, 1)

    def _connect_signals(self):
        self.ui.new_ro_page_ui.customer_line_edit.textChanged.connect(self._filter_customers_and_vehicles)
        self.ui.customer_table_small.cellClicked.connect(self._filter_vehicles_by_customer)
        self.ui.new_ro_page_ui.save_button.clicked.connect(self._open_ro_page)

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

    def _open_ro_page(self):
        selected_customer_row = self.ui.customer_table_small.currentRow()
        selected_vehicle_row = self.ui.vehicle_table_small.currentRow()

        customer_id = self.ui.customer_table_small.item(selected_customer_row, 3).text().strip()
        vehicle_id = self.ui.vehicle_table_small.item(selected_vehicle_row, 3).text().strip()

        ro_id = RepairOrdersRepository.create_repair_order(customer_id, vehicle_id)
        self.ui.ro_hub_manager.load_ro_into_hub(ro_id)
        self.ui.widget_manager.close_and_delete("new_repair_order")

        self.ui.animations_manager.ro_hub_page_show()
