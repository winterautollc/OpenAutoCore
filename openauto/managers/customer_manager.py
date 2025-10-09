from PyQt6 import QtWidgets, QtCore
from openauto.ui import new_customer_form
from openauto.repositories.customer_repository import CustomerRepository
from openauto.utils.validator import Validator

class CustomerManager:
    def __init__(self, main_window):
        self.ui = main_window

### OPENS new_customer_form ###
    def open_new_customer(self):
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
        self.ui.show_new_customer_page.setFocus()
        self.ui.show_new_customer_page.setFixedSize(606, 693)
        self.ui.show_new_customer_page.setWindowTitle("New Customer")
        self.ui.show_new_customer_page_ui.phone_line.setInputMask('(000) 000-0000;_')
        self.ui.show_new_customer_page.show()

        self.ui.show_new_customer_page_ui.save_customer_button.clicked.connect(self.save_customer)

### SAVES NEW CUSTOMER TO DB ###
    def save_customer(self):
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
            Validator.show_validation_error(self.ui.message, "Please provide at least a name and phone number.")
            return
        CustomerRepository.insert_customer(customer_data)
        self.ui.widget_manager.close_and_delete("new_customer")
        QtCore.QTimer.singleShot(0, lambda: QtWidgets.QMessageBox.information(self.ui, "Customer Added",
                        "Customer has been added."))

    def customer_search_filter(self, text):
        for row in range(self.ui.customer_table.rowCount()):
            match = any(
                text.lower() in (self.ui.customer_table.item(row, col).text().lower() if self.ui.customer_table.item(row, col) else "")
                for col in range(self.ui.customer_table.columnCount())
            )
            self.ui.customer_table.setRowHidden(row, not match)


    def _show_message(self, text):
        self.ui.message.setText(text)
        self.ui.message.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.ui.message.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.ui.message.show()
