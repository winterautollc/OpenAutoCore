from PyQt6 import QtWidgets, QtCore
from openauto.ui import customer_options, new_customer_form
from openauto.subclassed_widgets.event_handlers import WidgetManager
from openauto.repositories import customer_repository
from openauto.managers import vehicle_manager, animations_manager


class CustomerOptionsManager:
    def __init__(self, parent, customer_id, vehicle_signal, ro_signal):
        self.parent = parent
        self.customer_id = customer_id
        self.vehicle_signal = vehicle_signal
        self.ro_signal = ro_signal
        self.widget_manager = WidgetManager()
        self.vehicle_manager = vehicle_manager.VehicleManager(self)
        self.animations_manager = animations_manager.AnimationsManager

        self.customer_options, self.customer_options_ui = self.widget_manager.create_or_restore(
            "customer_options", QtWidgets.QWidget, customer_options.Ui_customer_options_form
        )

        self._setup_ui()

### SETS UP customer_options POPUP ###
    def _setup_ui(self):
        self.customer_options.setParent(self.parent, QtCore.Qt.WindowType.Dialog)
        self.customer_options.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.Dialog
        )

        self.customer_options.setWindowModality(QtCore.Qt.WindowModality.WindowModal)

        self.customer_options_ui.cancel_customer_options_button.clicked.connect(
            lambda: self.widget_manager.close_and_delete("customer_options")
        )
        self.customer_options_ui.delete_customer_button.clicked.connect(self.confirm_delete)
        self.customer_options_ui.edit_customer_button.clicked.connect(self.open_edit_window)
        self.customer_options_ui.add_customer_vehicle_button.clicked.connect(self.add_vehicle)
        self.customer_options_ui.create_ro_customer_button.hide()
        self.customer_options_ui.create_ro_customer_button.clicked.connect(self.create_ro)

        self.customer_options.show()

    def confirm_delete(self):
        message_box = QtWidgets.QMessageBox(self.customer_options)
        message_box.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        message_box.setWindowTitle("Confirm Delete")
        message_box.setText(
            "This will permanently delete the customer, all vehicles associated, and any open estimates.\n\nAre you sure?"
        )
        message_box.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        message_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        response = message_box.exec()
        message_confirm = QtWidgets.QMessageBox(self.customer_options)
        message_confirm.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        message_confirm.setStyleSheet("QLabel { color: black; }")
        message_confirm.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        message_confirm.setText("Customer Deleted!! This Cannot Be Undone")

        if response == QtWidgets.QMessageBox.StandardButton.Yes:
            customer_id = self.customer_id
            customer_repository.CustomerRepository.delete_customer(customer_id)
            message_confirm.exec()
            self.widget_manager.close_and_delete("customer_options")

### OPENS customer_search_form POPUP ###
    def open_edit_window(self):

        self.edit_customer_page, self.edit_customer_page_ui = self.widget_manager.create_or_restore(
            "edit_customer_page", QtWidgets.QWidget, new_customer_form.Ui_create_customer_form
        )

        self.edit_customer_page.setParent(self.parent, QtCore.Qt.WindowType.Dialog)
        self.edit_customer_page.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Dialog
        )

        self.edit_customer_page.setWindowModality(QtCore.Qt.WindowModality.WindowModal)

        self.edit_customer_page_ui.abort_button.clicked.connect(
            lambda: self.widget_manager.close_and_delete("edit_customer_page")
        )

        self.edit_customer_page_ui.save_button.hide()
        self.edit_customer_page.setWindowTitle("Edit Customer")
        self.edit_customer_page.show()
        self.widget_manager.close_and_delete("customer_options")
        self._populate_customer_fields()

### FILLS DATA FROM SELECTED CELL IN CUSTOMERTABLE TO customer_search_form ###
    def _populate_customer_fields(self):
        data = customer_repository.CustomerRepository.get_customer_info_by_id(self.customer_id)

        self.edit_customer_page_ui.first_name_line.setText(data['first_name'])
        self.edit_customer_page_ui.last_name_line.setText(data['last_name'])
        self.edit_customer_page_ui.address_line.setText(data['address'])
        self.edit_customer_page_ui.city_line.setText(data['city'])
        self.edit_customer_page_ui.state_line.setText(data['state'])
        self.edit_customer_page_ui.zipcode_line.setText(data['zip'])
        self.edit_customer_page_ui.phone_line.setText(data['phone'])
        self.edit_customer_page_ui.alt_line.setText(data['alt_phone'])
        self.edit_customer_page_ui.email_line.setText(data['email'])

        self.changed_values = {}

        self.edit_customer_page_ui.last_name_line.textChanged.connect(lambda: self.track_changes("last_name", self.edit_customer_page_ui.last_name_line.text()))
        self.edit_customer_page_ui.first_name_line.textChanged.connect(lambda: self.track_changes("first_name", self.edit_customer_page_ui.first_name_line.text()))
        self.edit_customer_page_ui.address_line.textChanged.connect(lambda: self.track_changes("address", self.edit_customer_page_ui.address_line.text()))
        self.edit_customer_page_ui.city_line.textChanged.connect(lambda: self.track_changes("city", self.edit_customer_page_ui.city_line.text()))
        self.edit_customer_page_ui.state_line.textChanged.connect(lambda: self.track_changes("state", self.edit_customer_page_ui.state_line.text()))
        self.edit_customer_page_ui.zipcode_line.textChanged.connect(lambda: self.track_changes("zip", self.edit_customer_page_ui.zipcode_line.text()))
        self.edit_customer_page_ui.phone_line.textChanged.connect(lambda: self.track_changes("phone", self.edit_customer_page_ui.phone_line.text()))
        self.edit_customer_page_ui.alt_line.textChanged.connect(lambda: self.track_changes("alt_phone", self.edit_customer_page_ui.alt_line.text()))
        self.edit_customer_page_ui.email_line.textChanged.connect(lambda: self.track_changes("email", self.edit_customer_page_ui.email_line.text()))

        self.edit_customer_page_ui.edit_button.clicked.connect(self.make_customer_changes)

### TRACKS EDIT TO CUSTOMER ###
    def track_changes(self, column, value):
        if not hasattr(self, 'changed_values'):
            self.changed_values = {}
        self.changed_values[column] = value.strip()

### MAKES CHANGES TO CUSTOMER ###
    def make_customer_changes(self):
        try:
            customer_repository.CustomerRepository.update_customer_by_id(
                self.customer_id, self.changed_values
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.edit_customer_page, "Database Error", str(e))

        self.edit_customer_page_ui.edit_button.clicked.disconnect()
        self.widget_manager.close_and_delete("edit_customer_page")
        self.widget_manager.close_and_delete("customer_options")
        message_box = QtWidgets.QMessageBox(self.edit_customer_page)
        message_box.setWindowTitle("Success")
        message_box.setText("Customer changes have been saved successfully.")
        message_box.setIcon(QtWidgets.QMessageBox.Icon.Information)
        message_box.setStyleSheet("QLabel { color: black; }")
        message_box.exec()


### PYQTSIGNALS FROM workflow_tables.CUSTOMERTABLE ###
    def add_vehicle(self):
        self.vehicle_signal.emit(int(self.customer_id))
        self.widget_manager.close_and_delete("customer_options")

    def create_ro(self):
        self.ro_signal.emit()
        self.widget_manager.close_and_delete("customer_options")
