from PyQt6 import QtCore, QtGui, QtWidgets
from openauto.theme import resources_rc


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(944, 481)
        Form.setStyleSheet("color: black;\n"
"background-color: #ebebe6;\n"
"background-image: none;\n"
"border-radius: 10px;")
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.customer_label = QtWidgets.QLabel(parent=Form)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.customer_label.setFont(font)
        self.customer_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.customer_label.setObjectName("customer_label")
        self.gridLayout.addWidget(self.customer_label, 0, 0, 1, 2)
        self.vehicle_label = QtWidgets.QLabel(parent=Form)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.vehicle_label.setFont(font)
        self.vehicle_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.vehicle_label.setObjectName("vehicle_label")
        self.gridLayout.addWidget(self.vehicle_label, 0, 2, 1, 2)
        self.customer_search_line = QtWidgets.QLineEdit(parent=Form)
        self.customer_search_line.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.customer_search_line.setFont(font)
        self.customer_search_line.setStyleSheet("border-radius: 5px;\n"
"background-color: #fefeff;\n"
"color: black;")
        self.customer_search_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.customer_search_line.setObjectName("customer_search_line")
        self.gridLayout.addWidget(self.customer_search_line, 1, 0, 1, 2)
        self.vehicle_table_small = VehicleTableSmall(parent=Form)
        self.vehicle_table_small.setObjectName("vehicle_table_small")
        self.vehicle_table_small.setColumnCount(0)
        self.vehicle_table_small.setRowCount(0)
        self.gridLayout.addWidget(self.vehicle_table_small, 1, 2, 2, 2)
        self.customer_table_small = CustomerTableSmall(parent=Form)
        self.customer_table_small.setObjectName("customer_table_small")
        self.customer_table_small.setColumnCount(0)
        self.customer_table_small.setRowCount(0)
        self.gridLayout.addWidget(self.customer_table_small, 2, 0, 1, 2)
        self.new_customer_button = QtWidgets.QPushButton(parent=Form)
        self.new_customer_button.setStyleSheet("QPushButton {\n"
"    background-color: #C49497;\n"
"    color: #fff;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #828786;\n"
"    color: #fff;\n"
"    border-radius: 10px;\n"
"}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/resources/icons3/24x24/cil-plus.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.new_customer_button.setIcon(icon)
        self.new_customer_button.setIconSize(QtCore.QSize(30, 30))
        self.new_customer_button.setObjectName("new_customer_button")
        self.gridLayout.addWidget(self.new_customer_button, 3, 0, 1, 2)
        self.new_vehicle_button = QtWidgets.QPushButton(parent=Form)
        self.new_vehicle_button.setStyleSheet("QPushButton {\n"
"    background-color: #C49497;\n"
"    color: #fff;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #828786;\n"
"    color: #fff;\n"
"    border-radius: 10px;\n"
"}")
        self.new_vehicle_button.setIcon(icon)
        self.new_vehicle_button.setIconSize(QtCore.QSize(30, 30))
        self.new_vehicle_button.setObjectName("new_vehicle_button")
        self.gridLayout.addWidget(self.new_vehicle_button, 3, 2, 1, 2)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(parent=Form)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setItalic(True)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.notes_edit = QtWidgets.QTextEdit(parent=Form)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.notes_edit.setFont(font)
        self.notes_edit.setStyleSheet("border-radius: 5px;\n"
"background-color: #fefeff;\n"
"color: black;\n"
"text-align: center;")
        self.notes_edit.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.notes_edit.setObjectName("notes_edit")
        self.verticalLayout.addWidget(self.notes_edit)
        self.gridLayout.addLayout(self.verticalLayout, 4, 0, 1, 4)
        self.drop_button = QtWidgets.QRadioButton(parent=Form)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.drop_button.setFont(font)
        self.drop_button.setObjectName("drop_button")
        self.gridLayout.addWidget(self.drop_button, 5, 0, 1, 1)
        self.wait_button = QtWidgets.QRadioButton(parent=Form)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.wait_button.setFont(font)
        self.wait_button.setObjectName("wait_button")
        self.gridLayout.addWidget(self.wait_button, 5, 1, 1, 1)
        self.cancel_button = QtWidgets.QPushButton(parent=Form)
        self.cancel_button.setStyleSheet("QPushButton {\n"
"    border-radius: 5px;\n"
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
        icon1.addPixmap(QtGui.QPixmap(":/resources/icons3/24x24/cil-x.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.cancel_button.setIcon(icon1)
        self.cancel_button.setIconSize(QtCore.QSize(30, 30))
        self.cancel_button.setObjectName("cancel_button")
        self.gridLayout.addWidget(self.cancel_button, 5, 2, 1, 1)
        self.save_button = QtWidgets.QPushButton(parent=Form)
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
        icon2.addPixmap(QtGui.QPixmap(":/resources/icons3/24x24/cil-check.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.save_button.setIcon(icon2)
        self.save_button.setIconSize(QtCore.QSize(30, 30))
        self.save_button.setObjectName("save_button")
        self.gridLayout.addWidget(self.save_button, 5, 3, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.customer_label.setText(_translate("Form", "Customer"))
        self.vehicle_label.setText(_translate("Form", "Vehicle"))
        self.customer_search_line.setPlaceholderText(_translate("Form", "Search ..."))
        self.new_customer_button.setText(_translate("Form", "New Customer"))
        self.new_vehicle_button.setText(_translate("Form", "New Vehicle"))
        self.label.setText(_translate("Form", "Notes"))
        self.drop_button.setText(_translate("Form", "Drop"))
        self.wait_button.setText(_translate("Form", "Wait"))
        self.cancel_button.setText(_translate("Form", "Cancel"))
        self.save_button.setText(_translate("Form", "Save"))
from openauto.subclassed_widgets.small_tables import CustomerTableSmall, VehicleTableSmall


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
