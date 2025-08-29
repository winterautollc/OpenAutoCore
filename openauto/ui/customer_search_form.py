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
        Form.resize(636, 278)
        Form.setStyleSheet("color: black;\n"
"background-color: #ebebe6;\n"
"background-image: none;\n"
"border-radius: 10px;")
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.customer_search_edit = QtWidgets.QLineEdit(parent=Form)
        self.customer_search_edit.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.customer_search_edit.setFont(font)
        self.customer_search_edit.setStyleSheet("border-radius: 5px;\n"
"background-color: #fefeff;\n"
"color: black;")
        self.customer_search_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.customer_search_edit.setObjectName("customer_search_edit")
        self.gridLayout.addWidget(self.customer_search_edit, 1, 1, 1, 3)
        self.belongs_to_label = QtWidgets.QLabel(parent=Form)
        self.belongs_to_label.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setItalic(True)
        self.belongs_to_label.setFont(font)
        self.belongs_to_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.belongs_to_label.setObjectName("belongs_to_label")
        self.gridLayout.addWidget(self.belongs_to_label, 1, 0, 1, 1)
        self.confirm_button = QtWidgets.QPushButton(parent=Form)
        self.confirm_button.setMinimumSize(QtCore.QSize(150, 30))
        self.confirm_button.setStyleSheet("QPushButton {\n"
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
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../theme/Icons/check.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.confirm_button.setIcon(icon)
        self.confirm_button.setIconSize(QtCore.QSize(30, 30))
        self.confirm_button.setObjectName("confirm_button")
        self.gridLayout.addWidget(self.confirm_button, 4, 3, 1, 1)
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
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("../theme/Icons/cross.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.cancel_button.setIcon(icon1)
        self.cancel_button.setIconSize(QtCore.QSize(30, 30))
        self.cancel_button.setObjectName("cancel_button")
        self.gridLayout.addWidget(self.cancel_button, 4, 2, 1, 1)
        self.customer_name_box = QtWidgets.QComboBox(parent=Form)
        self.customer_name_box.setMinimumSize(QtCore.QSize(300, 30))
        self.customer_name_box.setStyleSheet("QComboBox {\n"
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
        self.customer_name_box.setObjectName("customer_name_box")
        self.customer_name_box.addItem("")
        self.gridLayout.addWidget(self.customer_name_box, 0, 0, 1, 1)
        self.add_customer_button = QtWidgets.QPushButton(parent=Form)
        self.add_customer_button.setStyleSheet("QPushButton {\n"
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
        icon2.addPixmap(QtGui.QPixmap("../theme/Icons/user-add.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.add_customer_button.setIcon(icon2)
        self.add_customer_button.setIconSize(QtCore.QSize(30, 30))
        self.add_customer_button.setObjectName("add_customer_button")
        self.gridLayout.addWidget(self.add_customer_button, 0, 3, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Search Customer"))
        self.customer_search_edit.setPlaceholderText(_translate("Form", "Search ..."))
        self.belongs_to_label.setText(_translate("Form", "Vehicle Belongs To..."))
        self.confirm_button.setText(_translate("Form", "Confirm"))
        self.cancel_button.setText(_translate("Form", "Cancel"))
        self.customer_name_box.setItemText(0, _translate("Form", "Customer"))
        self.add_customer_button.setText(_translate("Form", "New Customer"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
