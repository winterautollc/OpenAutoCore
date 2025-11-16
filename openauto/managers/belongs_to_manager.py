from PyQt6 import QtCore, QtWidgets
from openauto.ui import customer_search_form, new_customer_form
from openauto.utils.validator import Validator
from openauto.repositories.customer_repository import CustomerRepository
from openauto.repositories.vehicle_repository import VehicleRepository
from openauto.repositories import vehicle_repository
from openauto.utils.fixed_popup_combo import FixedPopupCombo

class BelongsToManager:
    def __init__(self, main_window, vehicle_id=None):
        self.ui = main_window
        self.vehicle_id = vehicle_id
### OPENS customer_search PYUIC FILE ###
    def belongs_to(self):
        form = self.ui.vehicle_window_ui

        if not Validator.vehicle_fields_filled([
            form.vin_line.text(),
            form.year_line.text(),
            form.make_line.text(),
            form.model_line.text()
        ]):
            Validator.show_validation_error(self.ui.message, "Please decode VIN or enter Year, Make, and Model")
            return

        self.ui.belongs_to_window, self.ui.belongs_to_window_ui = self.ui.widget_manager.create_or_restore(
            "belongs_to", QtWidgets.QWidget, customer_search_form.Ui_customer_search_form
        )

        self.ui.belongs_to_window.setParent(self.ui, QtCore.Qt.WindowType.Dialog)
        self.ui.belongs_to_window.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Dialog
        )

        self.ui.belongs_to_window.setWindowModality(QtCore.Qt.WindowModality.WindowModal)

        self.ui.belongs_to_window.setFixedSize(636, 256)

        self.ui.belongs_to_window_ui.cancel_customer_search_button.clicked.connect(
            lambda: self.ui.widget_manager.close_and_delete("belongs_to"))

        self.ui.belongs_to_window_ui.customer_search_edit.setPlaceholderText("Search ...")
        self.ui.belongs_to_window_ui.customer_search_edit.textChanged.connect(self.customer_combo_filter)
        
        old = self.ui.belongs_to_window_ui.customer_name_box
        parent = old.parent()
        layout = parent.layout()
        
        combo = FixedPopupCombo(max_popup_height=200, parent=parent)
        combo.setObjectName("customer_name_box")
        
        layout.replaceWidget(old, combo)
        old.deleteLater()
        
        self.ui.belongs_to_window_ui.customer_name_box = combo
        self.ui.vehicle_window.hide()
        self.name_box_items()
        self.ui.belongs_to_window.show()

        self.ui.belongs_to_window_ui.confirm_customer_search_button.clicked.connect(self.new_vehicle_customer)
        self.ui.belongs_to_window_ui.add_customer_button.clicked.connect(self.join_vehicle_customer)


### ADDS VEHICLE TO CUSTOMER ALREADY IN THE SYSTEM ###
    def new_vehicle_customer(self):
        customer_id = self.ui.belongs_to_window_ui.customer_name_box.currentData()
        if customer_id is None:
            Validator.show_validation_error(self.ui.message, "Please select a customer")
            return

        form = self.ui.vehicle_window_ui
        vin_raw = (form.vin_line.text() or "").strip().upper()
        vin = vin_raw if vin_raw else None

        vehicle_data = [
            vin,
            form.year_line.text(),
            form.make_line.text(),
            form.model_line.text(),
            form.engine_line.text(),
            form.trim_line.text(),
            customer_id,
        ]
        # Optional plate and state
        try:
            plate = (form.plate_line.text() or "").strip().upper()
        except Exception:
            plate = ""
        try:
            state = (form.plate_state_box.currentText() or "").strip().upper()
        except Exception:
            state = ""

        vehicle_data.append(plate)
        vehicle_data.append(state)

        VehicleRepository.insert_vehicle(vehicle_data)
        self._show_message("Vehicle Added")
        self._close_windows(["vehicle_window", "belongs_to"])


### LOADS customer_search_form.py FOR ADDING NEW CUSTOMER WITH VEHICLE ###
    def join_vehicle_customer(self):
        self.ui.show_new_customer_page, self.ui.show_new_customer_page_ui = self.ui.widget_manager.create_or_restore(
            "new_customer", QtWidgets.QWidget, new_customer_form.Ui_create_customer_form
        )

        self.ui.show_new_customer_page.setParent(self.ui, QtCore.Qt.WindowType.Dialog)
        self.ui.show_new_customer_page.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Dialog
        )

        self.ui.show_new_customer_page.setWindowModality(QtCore.Qt.WindowModality.WindowModal)

        self.ui.show_new_customer_page_ui.cancel_customer_button.clicked.connect(
            lambda: self.ui.widget_manager.close_and_delete("new_customer"))

        self.ui.show_new_customer_page_ui.edit_customer_button.hide()
        self.ui.show_new_customer_page.setWindowTitle("New Customer")
        self.ui.show_new_customer_page_ui.first_name_line.setFocus()
        self.ui.show_new_customer_page.setFixedSize(606, 693)
        self.ui.show_new_customer_page_ui.phone_line.setInputMask('(000) 000-0000;_')


        self.ui.belongs_to_window.hide()
        self.ui.show_new_customer_page.show()
        self.ui.show_new_customer_page_ui.save_customer_button.clicked.connect(self.save_cust_vehc_join)

### CREATES NEW CUSTOMER AND ADDS NEW VEHICLE ASSOCIATED WITH THEM ###
    def save_cust_vehc_join(self):
        form = self.ui.show_new_customer_page_ui
        customer_data = [
            form.last_name_line.text(),
            form.first_name_line.text(),
            form.phone_line.text(),
            form.address_line.text(),
            form.city_line.text(),
            form.state_line.text(),
            form.zipcode_line.text(),
            form.alt_line.text(),
            form.email_line.text()
        ]

        if not Validator.fields_filled(customer_data[:3]):
            Validator.show_validation_error(self.ui.message, "Please enter at least name and phone number.")
            return

        CustomerRepository.insert_customer(customer_data)
        customer_id = CustomerRepository.get_customer_id_by_details(customer_data)

        if not customer_id:
            Validator.show_validation_error(self.ui.message, "Unable to find newly created customer.")
            return

        form = self.ui.vehicle_window_ui
        vin_raw = (form.vin_line.text() or "").strip().upper()
        vin = vin_raw if vin_raw else None

        vehicle_data = [
            vin,
            form.year_line.text(),
            form.make_line.text(),
            form.model_line.text(),
            form.engine_line.text(),
            form.trim_line.text(),
            customer_id
        ]
        VehicleRepository.insert_vehicle(vehicle_data)
        self._show_message("New Vehicle and Customer Added")
        self._close_windows(["vehicle_window", "belongs_to", "new_customer"])

### LOADS EXISTING CUSTOMERS INTO belongs_to.py ###
    def name_box_items(self):
        results = CustomerRepository.get_all_customer_names()
        combo = self.ui.belongs_to_window_ui.customer_name_box
        combo.clear()
        for row in results:
            last_name, first_name, phone, cust_id = row
            combo.addItem(f"{last_name} - {first_name} - {cust_id}", cust_id)

    def _show_message(self, text):
        self.ui.message.setParent(self.ui)
        self.ui.message.setText(text)
        self.ui.message.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self.ui.message.setWindowFlags(QtCore.Qt.WindowType.Dialog)
        self.ui.message.show()

    def _close_windows(self, window_keys):
        for key in window_keys:
            self.ui.widget_manager.close_and_delete(key)


### CHANGES VEHICLE OWNER TO A DIFFERENT EXISTING CUSTOMER ###
    def belongs_to_cust_change(self):
        self.ui.belongs_to_window, self.ui.belongs_to_window_ui = self.ui.widget_manager.create_or_restore(
            "belongs_to", QtWidgets.QWidget, customer_search_form.Ui_customer_search_form
        )

        self.ui.belongs_to_window.setParent(self.ui, QtCore.Qt.WindowType.Dialog)
        self.ui.belongs_to_window.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Dialog
        )

        self.ui.belongs_to_window.setWindowModality(QtCore.Qt.WindowModality.WindowModal)

        self.ui.belongs_to_window.setFixedSize(636, 256)

        self.ui.belongs_to_window_ui.cancel_customer_search_button.clicked.connect(
            lambda: self.ui.widget_manager.close_and_delete("belongs_to"))

        self.ui.belongs_to_window_ui.customer_search_edit.setPlaceholderText("Search ...")
        self.ui.belongs_to_window_ui.customer_search_edit.textChanged.connect(self.customer_combo_filter)

        old = self.ui.belongs_to_window_ui.customer_name_box
        parent = old.parent()
        layout = parent.layout()
        
        combo = FixedPopupCombo(max_popup_height=200, parent=parent)
        combo.setObjectName("customer_name_box")
        
        layout.replaceWidget(old, combo)
        old.deleteLater()
        
        self.ui.belongs_to_window_ui.customer_name_box = combo

        self.name_box_items()
        self.ui.belongs_to_window_ui.confirm_customer_search_button.clicked.connect(self.change_vehicle_owner)
        self.ui.belongs_to_window_ui.add_customer_button.clicked.connect(self.new_vehicle_owner)
        self.ui.belongs_to_window.show()

    def change_vehicle_owner(self):
        customer_id = self.ui.belongs_to_window_ui.customer_name_box.currentData()
        if customer_id is None:
            Validator.show_validation_error(self.ui.message, "Please select a customer")
            return

        vehicle_repository.VehicleRepository.change_vehicle_owner(vin=self.vehicle_id[0],
                                                                vehicle_id=self.vehicle_id[1],
                                                                customer_id=customer_id)

        self.ui.widget_manager.close_and_delete("belongs_to")
        message_box = QtWidgets.QMessageBox()
        message_box.setText("Vehicle Owner Changed Successfully")
        message_box.setWindowTitle("Success")
        message_box.setIcon(QtWidgets.QMessageBox.Icon.Information)
        message_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        message_box.exec()


    def customer_combo_filter(self, text):
        original_items = getattr(self, "_original_customer_items", None)

        # First time run: store all items
        if original_items is None:
            self._original_customer_items = [
                (self.ui.belongs_to_window_ui.customer_name_box.itemText(i),
                 self.ui.belongs_to_window_ui.customer_name_box.itemData(i))
                for i in range(self.ui.belongs_to_window_ui.customer_name_box.count())
            ]
            original_items = self._original_customer_items

        combo = self.ui.belongs_to_window_ui.customer_name_box
        combo.clear()

        text = text.lower()

        for display_text, user_data in original_items:
            if text in display_text.lower():
                combo.addItem(display_text, user_data)

    def new_vehicle_owner(self):
        self.ui.show_new_customer_page, self.ui.show_new_customer_page_ui = self.ui.widget_manager.create_or_restore(
            "new_customer", QtWidgets.QWidget, new_customer_form.Ui_create_customer_form
        )

        self.ui.show_new_customer_page.setParent(self.ui, QtCore.Qt.WindowType.Dialog)

        self.ui.show_new_customer_page.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Dialog
        )

        self.ui.show_new_customer_page.setWindowModality(QtCore.Qt.WindowModality.WindowModal)

        self.ui.show_new_customer_page_ui.cancel_customer_button.clicked.connect(
            lambda: self.ui.widget_manager.close_and_delete("new_customer"))

        self.ui.show_new_customer_page_ui.edit_customer_button.hide()
        self.ui.show_new_customer_page.setWindowTitle("New Customer")
        self.ui.show_new_customer_page_ui.first_name_line.setFocus()
        self.ui.show_new_customer_page.setFixedSize(606, 693)
        self.ui.show_new_customer_page_ui.phone_line.setInputMask('(000) 000-0000;_')


        self.ui.belongs_to_window.hide()
        self.ui.show_new_customer_page.show()
        self.ui.show_new_customer_page_ui.save_customer_button.clicked.connect(self.new_cust_old_vehc)


    def new_cust_old_vehc(self):
        form = self.ui.show_new_customer_page_ui
        customer_data = [
            form.last_name_line.text(),
            form.first_name_line.text(),
            form.phone_line.text(),
            form.address_line.text(),
            form.city_line.text(),
            form.state_line.text(),
            form.zipcode_line.text(),
            form.alt_line.text(),
            form.email_line.text()
        ]


        CustomerRepository.insert_customer(customer_data)
        customer_id = CustomerRepository.get_customer_id_by_details(customer_data)
        vehicle_repository.VehicleRepository.change_vehicle_owner(self.vehicle_id, customer_id)
        message_box = QtWidgets.QMessageBox()
        message_box.setText("Vehicle Owner Changed Successfully")
        message_box.setWindowTitle("Success")
        message_box.setIcon(QtWidgets.QMessageBox.Icon.Information)
        message_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        message_box.exec()
        self._close_windows(["vehicle_window", "belongs_to", "new_customer"])
