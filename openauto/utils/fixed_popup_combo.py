from PyQt6 import QtWidgets, QtCore


class FixedPopupCombo(QtWidgets.QComboBox):
    def __init__(self, max_popup_height=200, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._max_popup_height = max_popup_height

    def showPopup(self):
        super().showPopup()
        view = self.view()
        popup = view.window()

        rows = min(self.maxVisibleItems(), self.count() or 1)
        row_h = view.sizeHintForRow(0) or self.height()
        frame = popup.frameGeometry().height() - popup.geometry().height()
        height = min(self._max_popup_height, rows * row_h + frame + 4)

        pos = self.mapToGlobal(QtCore.QPoint(0, self.height()))
        popup.setGeometry(pos.x(), pos.y(), popup.width(), height)