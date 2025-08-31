from PyQt6 import QtCore, QtGui, QtWidgets
from openauto.theme import resources_rc

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(941, 405)
        Form.setStyleSheet("color: black;\n"
"background-color: #A2A29D;\n"
"background-image: none;\n"
"border-radius: 10px;")
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.name_label = QtWidgets.QLabel(parent=Form)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.name_label.setFont(font)
        self.name_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.name_label.setObjectName("name_label")
        self.horizontalLayout.addWidget(self.name_label)
        self.name_edit = QtWidgets.QLineEdit(parent=Form)
        self.name_edit.setMinimumSize(QtCore.QSize(0, 30))
        self.name_edit.setMaximumSize(QtCore.QSize(500, 16777215))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.name_edit.setFont(font)
        self.name_edit.setStyleSheet("border-radius: 5px;\n"
"background-color: #fefeff;\n"
"color: black;")
        self.name_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.name_edit.setReadOnly(True)
        self.name_edit.setObjectName("name_edit")
        self.horizontalLayout.addWidget(self.name_edit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.vehicle_label = QtWidgets.QLabel(parent=Form)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.vehicle_label.setFont(font)
        self.vehicle_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.vehicle_label.setObjectName("vehicle_label")
        self.horizontalLayout_2.addWidget(self.vehicle_label)
        self.vehicle_box = QtWidgets.QComboBox(parent=Form)
        self.vehicle_box.setMinimumSize(QtCore.QSize(500, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.vehicle_box.setFont(font)
        self.vehicle_box.setStyleSheet("QComboBox {\n"
"    border-radius: 5px;\n"
"    color: #fff;\n"
"    background-color: #76ABAE;\n"
"}\n"
"\n"
"QComboBox:hover {\n"
"    background-color: #828786;\n"
"    color: #fff;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QComboBox:drop-down {\n"
"    background-color: #828786;\n"
"    color: #fff;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    background-color: #828786;\n"
"    color: #fff;\n"
"    border-radius: 5px;\n"
"}")
        self.vehicle_box.setObjectName("vehicle_box")
        self.horizontalLayout_2.addWidget(self.vehicle_box)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.time_label = QtWidgets.QLabel(parent=Form)
        self.time_label.setMaximumSize(QtCore.QSize(103, 16777215))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.time_label.setFont(font)
        self.time_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.time_label.setObjectName("time_label")
        self.horizontalLayout_3.addWidget(self.time_label)
        self.time_box = QtWidgets.QComboBox(parent=Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.time_box.sizePolicy().hasHeightForWidth())
        self.time_box.setSizePolicy(sizePolicy)
        self.time_box.setMinimumSize(QtCore.QSize(500, 30))
        self.time_box.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.time_box.setFont(font)
        self.time_box.setStyleSheet("QComboBox {\n"
"    border-radius: 5px;\n"
"    color: #fff;\n"
"    background-color: #76ABAE;\n"
"}\n"
"\n"
"QComboBox:hover {\n"
"    background-color: #828786;\n"
"    color: #fff;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QComboBox:drop-down {\n"
"    background-color: #828786;\n"
"    color: #fff;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    background-color: #828786;\n"
"    color: #fff;\n"
"    border-radius: 5px;\n"
"}")
        self.time_box.setObjectName("time_box")
        self.horizontalLayout_3.addWidget(self.time_box)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 2)
        self.date_widget = QtWidgets.QCalendarWidget(parent=Form)
        self.date_widget.setStyleSheet("border-radius: 5px;\n"
"background-color: #fefeff;\n"
"color: black;")
        self.date_widget.setObjectName("date_widget")
        self.gridLayout.addWidget(self.date_widget, 0, 2, 2, 2)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.notes_label = QtWidgets.QLabel(parent=Form)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.notes_label.setFont(font)
        self.notes_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.notes_label.setObjectName("notes_label")
        self.verticalLayout_2.addWidget(self.notes_label)
        self.notes_edit = QtWidgets.QTextEdit(parent=Form)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.notes_edit.setFont(font)
        self.notes_edit.setStyleSheet("border-radius: 5px;\n"
"background-color: #fefeff;\n"
"color: black;")
        self.notes_edit.setObjectName("notes_edit")
        self.verticalLayout_2.addWidget(self.notes_edit)
        self.gridLayout.addLayout(self.verticalLayout_2, 1, 0, 1, 2)
        self.wait_button = QtWidgets.QRadioButton(parent=Form)
        self.wait_button.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.wait_button.setFont(font)
        self.wait_button.setObjectName("wait_button")
        self.gridLayout.addWidget(self.wait_button, 2, 0, 1, 1)
        self.drop_button = QtWidgets.QRadioButton(parent=Form)
        self.drop_button.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.drop_button.setFont(font)
        self.drop_button.setObjectName("drop_button")
        self.gridLayout.addWidget(self.drop_button, 2, 1, 1, 1)
        self.cancel_button = QtWidgets.QPushButton(parent=Form)
        self.cancel_button.setMinimumSize(QtCore.QSize(150, 30))
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
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/resources/icons3/24x24/cil-x.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.cancel_button.setIcon(icon)
        self.cancel_button.setIconSize(QtCore.QSize(30, 30))
        self.cancel_button.setObjectName("cancel_button")
        self.gridLayout.addWidget(self.cancel_button, 2, 2, 1, 1)
        self.confirm_button = QtWidgets.QPushButton(parent=Form)
        self.confirm_button.setMinimumSize(QtCore.QSize(150, 30))
        self.confirm_button.setStyleSheet("QPushButton {\n"
"    border-radius: 5px;\n"
"    color: #fff;\n"
"    background-color: #0B5598;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #828786;\n"
"    color: #fff;\n"
"    border-radius: 10px;\n"
"}")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/resources/icons3/24x24/cil-check.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.confirm_button.setIcon(icon1)
        self.confirm_button.setIconSize(QtCore.QSize(30, 30))
        self.confirm_button.setObjectName("confirm_button")
        self.gridLayout.addWidget(self.confirm_button, 2, 3, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.name_label.setText(_translate("Form", "Customer"))
        self.vehicle_label.setText(_translate("Form", "Vehicle"))
        self.time_label.setText(_translate("Form", "Time"))
        self.notes_label.setText(_translate("Form", "Notes"))
        self.wait_button.setText(_translate("Form", "Wait"))
        self.drop_button.setText(_translate("Form", "Drop"))
        self.cancel_button.setText(_translate("Form", "Cancel"))
        self.confirm_button.setText(_translate("Form", "Confirm"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
