from PyQt6 import QtWidgets, QtCore

class Validator:
    @staticmethod
    def fields_filled(fields):

        return all(bool(field.strip()) for field in fields)

    @staticmethod
    def vehicle_fields_filled(fields):
        # Require Year, Make, and Model
        return Validator.fields_filled([fields[1], fields[2], fields[3]])

    @staticmethod
    def show_validation_error(message_box, text):
        message_box.setText(text)
        message_box.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        message_box.show()
