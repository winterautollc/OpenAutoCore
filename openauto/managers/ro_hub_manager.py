from PyQt6 import QtWidgets, QtCore
from openauto.repositories.repair_orders_repository import RepairOrdersRepository
from openauto.repositories.customer_repository import CustomerRepository
from openauto.repositories.vehicle_repository import VehicleRepository
from openauto.managers import ro_status_manager

class ROHubManager:
    def __init__(self, ui):
        self.ui = ui
        self._connect_signals()

    def _connect_signals(self):
        self.ui.type_box.addItems(["Part", "Labor", "Fee", "Sublet"])
        self.ui.save_ro_button.clicked.connect(self._save_repair_order)
        self.ui.add_job_item_button.clicked.connect(self._add_item)
        self.ui.remove_item_button.clicked.connect(self._remove_selected_item)
        self.ui.concern_button.toggled.connect(lambda checked: self._toggle_3c_stack(0, checked))
        self.ui.cause_button.toggled.connect(lambda checked: self._toggle_3c_stack(1, checked))
        self.ui.correction_button.toggled.connect(lambda checked: self._toggle_3c_stack(2, checked))
        self.ui.ro_status_button.clicked.connect(self.open_ro_status)
        self.ui.cancel_ro_button.clicked.connect(self.cancel_ro_changes)
        self.ui.name_edit.setReadOnly(True)
        self.ui.number_edit.setReadOnly(True)
        self.ui.vehcle_line.setReadOnly(True)
        self.ui.ro_created_edit.setReadOnly(True)
        self.ui.ro_approved_edit.setReadOnly(True)
        self.ui.parts_label.setText("0.00")
        self.ui.labor_label.setText("0.00")
        self.ui.tires_label.setText("0.00")
        self.ui.label_2.setText("0.00")
        self.ui.subtotal_label.setText("0.00")
        self.ui.shop_supplies_label.setText("0.00")
        self.ui.tax_label.setText("0.00")
        self.ui.total_label.setText("0.00")
        self.ui.fees_label.setText("0.00")
        self.ui.ro_status_label.setText("Open: Not Approved")
        self.ui.ro_status_label.setStyleSheet("background-color: #76ABAE; \n"
                                              "color: #fff; \n"
                                              "border-radius: 5px;")


    def load_ro_into_hub(self, ro_id):
        self.ui.current_ro_id = ro_id
        ro_data = RepairOrdersRepository.get_repair_order_by_id(ro_id)
        customer = CustomerRepository.get_customer_info_by_id(ro_data['customer_id'])
        vehicle = VehicleRepository.get_vehicle_info_for_new_ro(ro_data['customer_id'])
        full_name = f"{customer['first_name']} {customer['last_name']}"
        vehicle_desc = f"{vehicle['vin']}   {vehicle['year']}   {vehicle['make']}   {vehicle['model']}"
        self.ui.name_edit.setText(full_name)
        self.ui.ro_number_label.setText(ro_data['ro_number'])
        self.ui.number_edit.setText(customer['phone'])
        self.ui.vehcle_line.setText(vehicle_desc)


    def _toggle_3c_stack(self, index, checked):
        if checked:
            self.ui.three_c_stacked.setCurrentIndex(index)

    def _add_item(self):
        self._ensure_ro_table_configured()  # headers/columns if UI wiped them

        # collect inputs
        sku  = self.ui.sku_edit.text().strip()
        desc = self.ui.description_edit.text().strip()
        cost_text = self.ui.cost_edit.text().strip()
        sell_text = self.ui.sell_edit.text().strip()
        tax_text  = self.ui.tax_edit.text().strip()

        if not all([sku, desc, cost_text, sell_text, tax_text]):
            QtWidgets.QToolTip.showText(
                self.ui.add_job_item_button.mapToGlobal(self.ui.add_job_item_button.rect().center()),
                "Fill SKU, Description, Cost, Sell, and Tax before adding."
            )
            return

        cost = self._parse_money(cost_text)
        sell = self._parse_money(sell_text)
        tax  = self._parse_money(tax_text)
        if any(v is None for v in (cost, sell, tax)):
            QtWidgets.QToolTip.showText(
                self.ui.add_job_item_button.mapToGlobal(self.ui.add_job_item_button.rect().center()),
                "Cost, Sell, and Tax must be numbers."
            )
            return

        t = self.ui.ro_items_table
        row = t.rowCount()
        t.insertRow(row)

        # --- TYPE column as a per-row QComboBox mirroring type_box ---
        combo = QtWidgets.QComboBox(t)
        combo.setStyleSheet("QComboBox {\n"
"    border-radius: 5px;\n"
"    color: #fff;\n"
"    background-color: #76ABAE;\n"
"}\n"
"\n"
"QComboBox:hover {\n"
"    background-color: #828786;\n"
"    color: #fff;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QComboBox:drop-down {\n"
"    background-color: #828786;\n"
"    color: #fff;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    background-color: #828786;\n"
"    color: #fff;\n"
"    border-radius: 5px;\n"
"}")
        combo.addItems(self._type_options())
        # default to the current selection in the toolbar type_box (if any), else first option
        current = self.ui.type_box.currentText().strip()
        if current:
            idx = combo.findText(current, QtCore.Qt.MatchFlag.MatchFixedString)
            combo.setCurrentIndex(idx if idx >= 0 else 0)
        t.setCellWidget(row, 0, combo)

        # Other columns as read-only items, centered
        def _item(val: str) -> QtWidgets.QTableWidgetItem:
            it = QtWidgets.QTableWidgetItem(val)
            it.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            return it

        t.setItem(row, 1, _item(sku))
        t.setItem(row, 2, _item(desc))
        t.setItem(row, 3, _item(f"{cost:.2f}"))
        t.setItem(row, 4, _item(f"{sell:.2f}"))
        t.setItem(row, 5, _item(f"{tax:.2f}"))

        # reset inputs
        self.ui.sku_edit.clear()
        self.ui.description_edit.clear()
        self.ui.cost_edit.clear()
        self.ui.sell_edit.clear()
        self.ui.tax_edit.clear()
        self.ui.sku_edit.setFocus()


### REMOVES ROW FROM ROTable ###
    def _remove_selected_item(self):
        row = self.ui.ro_items_table.currentRow()
        if row != -1:
            self.ui.ro_items_table.removeRow(row)

    def _save_repair_order(self):
        # Collect all form values and call RepairOrdersRepository.create/update
        pass

    def open_ro_status(self, checked=False):
        ro_status_manager.ROStatusManager(self.ui)

### DISCARDS CHANGES TO REPAIR ORDER AND RETURNS TO MAIN PAGE ###
    def cancel_ro_changes(self):
        message_box = QtWidgets.QMessageBox(self.ui)
        message_box.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        message_box.setWindowTitle("Cancel Changes")
        message_box.setText(
            "Cancel and discard unsaved changes.\n\nAre you sure?"
        )
        message_box.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        message_box.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        response = message_box.exec()

        if response == QtWidgets.QMessageBox.StandardButton.Yes:
            self.ui.animations_manager.show_repair_orders()

### MIRROR OPTIONS FROM THE TOP-LEVEL TYPE_BOX: FALL BACK TO SANE DEFAULTS ###
    def _type_options(self):
        items = [self.ui.type_box.itemText(i).strip()
                 for i in range(self.ui.type_box.count())
                 if self.ui.type_box.itemText(i).strip()]
        return items or ["Part", "Labor", "Fee", "Sublet"]

### REAPPLY EXPECTED COLUMNS/HEADERS IF setupUi RESETS THEM TO 0 COLUMNS
    # def _ensure_ro_table_configured(self):
    #     """(Re)apply expected columns/headers if setupUi reset them to 0 columns."""
    #     t = self.ui.ro_items_table
    #     if t.columnCount() < 6:
    #         t.setColumnCount(6)
    #         t.setHorizontalHeaderLabels(["TYPE", "PART NUMBER", "DESCRIPTION", "COST", "SELL", "TAX"])
    #         t.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
    #         t.verticalHeader().setVisible(False)
    #         t.setEditTriggers(QtWidgets.QTableWidget.EditTrigger.NoEditTriggers)
    #         t.setSelectionBehavior(QtWidgets.QTableWidget.SelectionBehavior.SelectRows)

    @staticmethod
    def _parse_money(text: str):
        t = (text or "").strip().replace(",", "")
        if not t:
            return None
        try:
            return float(t)
        except ValueError:
            return None