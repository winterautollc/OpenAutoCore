from PyQt6 import QtWidgets


class PartsTree(QtWidgets.QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
