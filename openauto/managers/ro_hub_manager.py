from openauto.repositories.repair_orders_repository import RepairOrdersRepository
from openauto.repositories.customer_repository import CustomerRepository
from openauto.repositories.vehicle_repository import VehicleRepository

class ROHubManager:
    def __init__(self, ui):
        self.ui = ui
        self._connect_signals()

    def _connect_signals(self):
        self.ui.save_ro_button.clicked.connect(self._save_repair_order)
        self.ui.cancel_ro_button.clicked.connect(self._cancel_edit)
        self.ui.add_item_button.clicked.connect(self._add_item)
        self.ui.remove_item_button.clicked.connect(self._remove_selected_item)
        self.ui.concern_button.toggled.connect(lambda checked: self._toggle_3c_stack(0, checked))
        self.ui.cause_button.toggled.connect(lambda checked: self._toggle_3c_stack(1, checked))
        self.ui.correction_button.toggled.connect(lambda checked: self._toggle_3c_stack(2, checked))
        self.ui.name_edit.setReadOnly(True)
        self.ui.number_edit.setReadOnly(True)
        self.ui.vehcle_line.setReadOnly(True)
        self.ui.parts_label.setText("0.00")
        self.ui.labor_label.setText("0.00")
        self.ui.tires_label.setText("0.00")
        self.ui.label_2.setText("0.00")
        self.ui.subtotal_label.setText("0.00")
        self.ui.shop_supplies_label.setText("0.00")
        self.ui.tax_label.setText("0.00")
        self.ui.total_label.setText("0.00")
        self.ui.fees_label.setText("0.00")

    def load_ro_into_hub(self, ro_id):
        self.ui.current_ro_id = ro_id

        ro_data = RepairOrdersRepository.get_repair_order_by_id(ro_id)
        customer = CustomerRepository.get_customer_info_by_id(ro_data['customer_id'])
        vehicle = VehicleRepository.get_vehicles_by_customer_id(ro_data['vehicle_id'])

        full_name = f"{customer['first_name']} {customer['last_name']}"
        vehicle_desc = f"{vehicle['vin']}   {vehicle['year']}, {vehicle['make']}, {vehicle['model']}"

        self.ui.name_edit.setText(full_name)
        self.ui.number_edit.setText(ro_data['ro_number'])
        self.ui.vehcle_line.setText(vehicle_desc)

    def _toggle_3c_stack(self, index, checked):
        if checked:
            self.ui.three_c_stacked.setCurrentIndex(index)

    def _add_item(self):
        # Get values from input fields
        # Append to self.ui.ro_items_table
        pass

    def _remove_selected_item(self):
        row = self.ui.ro_items_table.currentRow()
        if row != -1:
            self.ui.ro_items_table.removeRow(row)

    def _save_repair_order(self):
        # Collect all form values and call RepairOrdersRepository.create/update
        pass

    def _cancel_edit(self):
        # Optionally clear fields or go back to RO list
        pass
