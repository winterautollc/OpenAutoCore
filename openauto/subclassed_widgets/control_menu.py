from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QFrame, QLabel, QPushButton
from openauto.subclassed_widgets import event_handlers

### CLASS TO CALL MAIN LEFT MENU ###

class ControlMenu(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("cmenu_frame")
        self.setMouseTracking(True)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                           QtWidgets.QSizePolicy.Policy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)

        self.setSizePolicy(size_policy)
        self.collapsed_width = 60
        self.setMinimumWidth(self.collapsed_width)
        self.setMaximumWidth(60)
        self.setStyleSheet("color: #ffffff;\n"
                                       "background-color: #314455;\n"
                                       "background-image: none;\n"
                                       "border-radius: 5px;")

        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.setLineWidth(1)

        # hover open/close handler
        self.frame_filter = event_handlers.CMenuHandler(self)
        self.installEventFilter(self.frame_filter)