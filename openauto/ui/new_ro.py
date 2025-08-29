from PyQt6 import QtCore, QtGui, QtWidgets
import os
from PyQt6 import QtGui
_QPIX = QtGui.QPixmap

class _QPixFix(QtGui.QPixmap):
    def __init__(self, path=None, *a, **kw):
        if isinstance(path, str) and (path.startswith("../theme/") or path.startswith("theme/")):
            path = os.path.normpath(os.path.join(os.path.dirname(__file__), path))
        super().__init__(path)
QtGui.QPixmap = _QPixFix

class Ui_create_ro(object):
    def setupUi(self, create_ro):
        create_ro.setObjectName("create_ro")
        create_ro.resize(993, 527)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../theme/Icons/edit.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        create_ro.setWindowIcon(icon)
        create_ro.setStyleSheet("color: black;\n"
"background-color: #ebebe6;\n"
"background-image: none;\n"
"border-radius: 10px;\n"
"")
        self.gridLayout = QtWidgets.QGridLayout(create_ro)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.customer_label = QtWidgets.QLabel(parent=create_ro)
        self.customer_label.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.customer_label.setFont(font)
        self.customer_label.setStyleSheet("QLabel {\n"
"    border-radius: 5px;\n"
"    color: #fff;\n"
"    background-color: #828786;\n"
"}\n"
"")
        self.customer_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.customer_label.setObjectName("customer_label")
        self.verticalLayout.addWidget(self.customer_label)
        self.gridLayout_2.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.customer_line_edit = QtWidgets.QLineEdit(parent=create_ro)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.customer_line_edit.setFont(font)
        self.customer_line_edit.setStyleSheet("border-radius: 10px;\n"
"background-color: #fefeff;")
        self.customer_line_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.customer_line_edit.setObjectName("customer_line_edit")
        self.gridLayout_2.addWidget(self.customer_line_edit, 1, 0, 1, 1)
        self.customer_table_small = CustomerTableSmall(parent=create_ro)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.customer_table_small.sizePolicy().hasHeightForWidth())
        self.customer_table_small.setSizePolicy(sizePolicy)
        self.customer_table_small.setMinimumSize(QtCore.QSize(0, 0))
        self.customer_table_small.setObjectName("customer_table_small")
        self.customer_table_small.setColumnCount(0)
        self.customer_table_small.setRowCount(0)
        self.gridLayout_2.addWidget(self.customer_table_small, 2, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 2, 1)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.customer_states_label = QtWidgets.QLabel(parent=create_ro)
        self.customer_states_label.setMaximumSize(QtCore.QSize(16777215, 100))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.customer_states_label.setFont(font)
        self.customer_states_label.setStyleSheet("QLabel {\n"
"    border-radius: 5px;\n"
"    color: #fff;\n"
"    background-color: #C49497;\n"
"}\n"
"")
        self.customer_states_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.customer_states_label.setObjectName("customer_states_label")
        self.verticalLayout_4.addWidget(self.customer_states_label)
        self.customer_states = QtWidgets.QTextEdit(parent=create_ro)
        self.customer_states.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.customer_states.setFont(font)
        self.customer_states.setStyleSheet("border-radius: 10px;\n"
"background-color: #fefeff;")
        self.customer_states.setObjectName("customer_states")
        self.verticalLayout_4.addWidget(self.customer_states)
        self.gridLayout.addLayout(self.verticalLayout_4, 2, 0, 1, 2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.abort_button = QtWidgets.QPushButton(parent=create_ro)
        self.abort_button.setMinimumSize(QtCore.QSize(30, 30))
        self.abort_button.setStyleSheet("QPushButton {\n"
"    border-radius: 10px;\n"
"    color: #fff;\n"
"    background-color: #A0153E;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #C49497;\n"
"    color: #fff;\n"
"    border-radius: 10px;\n"
"}")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("../theme/icons3/24x24/cil-x.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.abort_button.setIcon(icon1)
        self.abort_button.setIconSize(QtCore.QSize(30, 30))
        self.abort_button.setFlat(True)
        self.abort_button.setObjectName("abort_button")
        self.horizontalLayout.addWidget(self.abort_button)
        self.save_button = QtWidgets.QPushButton(parent=create_ro)
        self.save_button.setMinimumSize(QtCore.QSize(30, 30))
        self.save_button.setStyleSheet("QPushButton {\n"
"    border-radius: 5px;\n"
"    color: #fff;\n"
"    background-color: #76ABAE;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #828786;\n"
"    color: #fff;\n"
"    border-radius: 10px;\n"
"}")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("../theme/icons3/24x24/cil-check.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.save_button.setIcon(icon2)
        self.save_button.setIconSize(QtCore.QSize(30, 30))
        self.save_button.setFlat(True)
        self.save_button.setObjectName("save_button")
        self.horizontalLayout.addWidget(self.save_button)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 1, 1, 1)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.vehicle_label = QtWidgets.QLabel(parent=create_ro)
        self.vehicle_label.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.vehicle_label.setFont(font)
        self.vehicle_label.setStyleSheet("QLabel {\n"
"    border-radius: 5px;\n"
"    color: #fff;\n"
"    background-color: #828786;\n"
"}\n"
"")
        self.vehicle_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.vehicle_label.setObjectName("vehicle_label")
        self.gridLayout_3.addWidget(self.vehicle_label, 0, 0, 1, 1)
        self.vehicle_table_small = VehicleTableSmall(parent=create_ro)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.vehicle_table_small.sizePolicy().hasHeightForWidth())
        self.vehicle_table_small.setSizePolicy(sizePolicy)
        self.vehicle_table_small.setMinimumSize(QtCore.QSize(0, 0))
        self.vehicle_table_small.setObjectName("vehicle_table_small")
        self.vehicle_table_small.setColumnCount(0)
        self.vehicle_table_small.setRowCount(0)
        self.gridLayout_3.addWidget(self.vehicle_table_small, 1, 0, 1, 1)
        self.add_vehicle_button = QtWidgets.QPushButton(parent=create_ro)
        self.add_vehicle_button.setStyleSheet("QPushButton {\n"
"    border-radius: 5px;\n"
"    color: #fff;\n"
"    background-color: #76ABAE;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #828786;\n"
"    color: #fff;\n"
"    border-radius: 10px;\n"
"}")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("../theme/icons3/24x24/cil-plus.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.add_vehicle_button.setIcon(icon3)
        self.add_vehicle_button.setIconSize(QtCore.QSize(30, 30))
        self.add_vehicle_button.setObjectName("add_vehicle_button")
        self.gridLayout_3.addWidget(self.add_vehicle_button, 2, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_3, 0, 1, 2, 1)

        self.retranslateUi(create_ro)
        QtCore.QMetaObject.connectSlotsByName(create_ro)

    def retranslateUi(self, create_ro):
        _translate = QtCore.QCoreApplication.translate
        create_ro.setWindowTitle(_translate("create_ro", "Create Ro"))
        self.customer_label.setText(_translate("create_ro", "Customer"))
        self.customer_line_edit.setPlaceholderText(_translate("create_ro", "Search ..."))
        self.customer_states_label.setText(_translate("create_ro", "Customer States"))
        self.abort_button.setText(_translate("create_ro", "Cancel"))
        self.save_button.setText(_translate("create_ro", "Save"))
        self.vehicle_label.setText(_translate("create_ro", "Vehicle"))
        self.add_vehicle_button.setText(_translate("create_ro", "Add Vehicle"))
from openauto.subclassed_widgets.small_tables import CustomerTableSmall, VehicleTableSmall


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    create_ro = QtWidgets.QWidget()
    ui = Ui_create_ro()
    ui.setupUi(create_ro)
    create_ro.show()
    sys.exit(app.exec())
