from PyQt6 import QtWidgets, QtCore


class EstimatesManager:
    def __init__(self, main_window):
        self.ui = main_window

        self.ui.alt_ro_label.hide()
        self.ui.alt_number_label.hide()
