from PyQt6 import QtCore, QtWidgets
from openauto.repositories.repair_orders_repository import RepairOrdersRepository
from openauto.repositories.customer_repository import CustomerRepository
from openauto.repositories.vehicle_repository import VehicleRepository
from .staff_controller import StaffAssignmentController
from .item_entry_controller import ItemEntryController
from .status_controller import StatusDialogController
from .tax_controller import TaxConfigController
from .save_estimate_service import SaveEstimateService

class ROHubManager:
    def __init__(self, ui):
        self.ui = ui
        self.staff  = StaffAssignmentController(ui)
        self.items  = ItemEntryController(ui)
        self.status = StatusDialogController(ui)
        self.tax    = TaxConfigController(ui)
        self.saver  = SaveEstimateService(ui)

        self._wire_signals()
        self.staff.populate_and_connect()
        self.tax.connect_tax_rate()
        self.items.adjust_item_lines()

    def _wire_signals(self):
        # mirror original connections
        self.ui.type_box.addItems(self.items.type_options())
        self.ui.type_box.currentTextChanged.connect(self.items.adjust_item_lines)

        self.ui.add_job_item_button.clicked.connect(self.items.add_item)
        self.ui.remove_item_button.clicked.connect(self.items.remove_selected_item)

        self.ui.save_ro_button.clicked.connect(self.saver.save)

        self.ui.concern_button.toggled.connect(lambda checked: self._toggle_3c_stack(0, checked))
        self.ui.cause_button.toggled.connect(lambda checked: self._toggle_3c_stack(1, checked))
        self.ui.correction_button.toggled.connect(lambda checked: self._toggle_3c_stack(2, checked))

        self.ui.ro_status_button.clicked.connect(self.status.open_ro_status)
        self.ui.cancel_ro_button.clicked.connect(self.status.cancel_ro_changes)

        # set read-only + zero labels (unchanged behavior)
        for e in (self.ui.name_edit, self.ui.number_edit, self.ui.vehcle_line,
                  self.ui.ro_created_edit, self.ui.ro_approved_edit):
            e.setReadOnly(True)
        for lab in (self.ui.parts_label, self.ui.labor_label, self.ui.tires_label,
                    self.ui.label_2, self.ui.subtotal_label, self.ui.shop_supplies_label,
                    self.ui.tax_label, self.ui.total_label, self.ui.fees_label):
            lab.setText("0.00")




    def _toggle_3c_stack(self, index: int, checked: bool):
        if checked:
            self.ui.three_c_stacked.setCurrentIndex(index)



    # span multiple controllers
    def load_ro_into_hub(self, ro_id: int):
        self.ui.current_ro_id = ro_id
        ro_data = RepairOrdersRepository.get_repair_order_by_id(ro_id)
        customer = CustomerRepository.get_customer_info_by_id(ro_data["customer_id"])
        vehicle  = VehicleRepository.get_vehicle_info_for_new_ro(ro_data["customer_id"])

        self.ui.name_edit.setText(f"{customer['first_name']} {customer['last_name']}")
        self.ui.ro_number_label.setText(ro_data["ro_number"])
        self.ui.number_edit.setText(customer["phone"])
        self.ui.vehcle_line.setText(f"{vehicle['vin']}   {vehicle['year']}   {vehicle['make']}   {vehicle['model']}")

        # delegate staff select resolution to the staff controller
        self.staff.sync_selects_from_ro(ro_data)
