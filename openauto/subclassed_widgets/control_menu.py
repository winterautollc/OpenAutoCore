from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QFrame
from openauto.subclassed_widgets import event_handlers

### CLASS TO CALL MAIN LEFT MENU ###

class ControlMenu(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.menu_frame = QtWidgets.QFrame()
        self.setMouseTracking(True)
        self.menu_height = self.height()
        self.frame_filter = event_handlers.CMenuHandler(self)
        self.installEventFilter(self.frame_filter)

###        FEATURES FOR THE MENU FRAME. PROBABLY REDUNDANT AS THE GENERATED PYUIC DESCRIBES THIS ALREADY ###

        self.setGeometry(QtCore.QRect(120, 40, 60, 890))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasWidthForHeight())
        sizePolicy.setVerticalStretch(0)
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(60, 0))
        self.setMaximumSize(QtCore.QSize(1677215, 1677215))
        self.setSizeIncrement(QtCore.QSize(0, 0))
        self.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.setStyleSheet("color: #ffffff;\n"
                                       "background-color: #434b56;\n"
                                       "background-image: none;\n"
                                       "border-radius: 10px;")
        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.setLineWidth(1)

