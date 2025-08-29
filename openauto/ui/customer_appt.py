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


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(644, 256)
        Form.setStyleSheet("color: black;\n"
"background-color: #ebebe6;\n"
"background-image: none;\n"
"border-radius: 10px;")
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.customer_combo_box = QtWidgets.QComboBox(parent=Form)
        self.customer_combo_box.setMinimumSize(QtCore.QSize(300, 30))
        self.customer_combo_box.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.customer_combo_box.setStyleSheet("QComboBox {\n"
"    border-radius: 10px;\n"
"    color: #fff;\n"
"    background-color: #94C4C1;\n"
"}\n"
"\n"
"QComboBox:hover {\n"
"    background-color: #CE6A6C;\n"
"    color: #fff;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"QComboBox:drop-down {\n"
"    background-color: #CE6A6C;\n"
"    color: #fff;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    background-color: #CE6A6C;\n"
"    color: #fff;\n"
"    border-radius: 10px;\n"
"}")
        self.customer_combo_box.setObjectName("customer_combo_box")
        self.gridLayout.addWidget(self.customer_combo_box, 0, 0, 1, 1)
        self.label = QtWidgets.QLabel(parent=Form)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)
        self.vehicle_combo_box = QtWidgets.QComboBox(parent=Form)
        self.vehicle_combo_box.setMinimumSize(QtCore.QSize(300, 30))
        self.vehicle_combo_box.setStyleSheet("QComboBox {\n"
"    border-radius: 10px;\n"
"    color: #fff;\n"
"    background-color: #94C4C1;\n"
"}\n"
"\n"
"QComboBox:hover {\n"
"    background-color: #CE6A6C;\n"
"    color: #fff;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"QComboBox:drop-down {\n"
"    background-color: #CE6A6C;\n"
"    color: #fff;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    background-color: #CE6A6C;\n"
"    color: #fff;\n"
"    border-radius: 10px;\n"
"}")
        self.vehicle_combo_box.setObjectName("vehicle_combo_box")
        self.gridLayout.addWidget(self.vehicle_combo_box, 1, 0, 1, 1)
        self.customer_search_edit = QtWidgets.QLineEdit(parent=Form)
        self.customer_search_edit.setMinimumSize(QtCore.QSize(312, 30))
        self.customer_search_edit.setStyleSheet("border-radius: 5px;\n"
"background-color: #fefeff;")
        self.customer_search_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.customer_search_edit.setObjectName("customer_search_edit")
        self.gridLayout.addWidget(self.customer_search_edit, 2, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.cancel_button = QtWidgets.QPushButton(parent=Form)
        self.cancel_button.setMinimumSize(QtCore.QSize(150, 0))
        self.cancel_button.setStyleSheet("QPushButton {\n"
"    border-radius: 10px;\n"
"    color: #fff;\n"
"    background-color: #CE6A6C;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #C49497;\n"
"    color: #fff;\n"
"    border-radius: 10px;\n"
"}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../theme/icons3/24x24/cil-x.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.cancel_button.setIcon(icon)
        self.cancel_button.setIconSize(QtCore.QSize(30, 30))
        self.cancel_button.setObjectName("cancel_button")
        self.horizontalLayout.addWidget(self.cancel_button)
        self.create_button = QtWidgets.QPushButton(parent=Form)
        self.create_button.setMinimumSize(QtCore.QSize(150, 0))
        self.create_button.setMaximumSize(QtCore.QSize(147, 16777215))
        self.create_button.setStyleSheet("QPushButton {\n"
"    border-radius: 10px;\n"
"    color: #fff;\n"
"    background-color: #94C4C1;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #828786;\n"
"    color: #fff;\n"
"    border-radius: 10px;\n"
"}")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("../theme/icons3/24x24/cil-check.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.create_button.setIcon(icon1)
        self.create_button.setIconSize(QtCore.QSize(30, 30))
        self.create_button.setObjectName("create_button")
        self.horizontalLayout.addWidget(self.create_button)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Choose Customer And Vehicle"))
        self.customer_search_edit.setPlaceholderText(_translate("Form", "Search ..."))
        self.cancel_button.setText(_translate("Form", "Cancel"))
        self.create_button.setText(_translate("Form", "Create"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
