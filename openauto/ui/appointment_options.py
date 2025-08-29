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
        Form.resize(915, 150)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.create_ro_button = QtWidgets.QPushButton(parent=Form)
        self.create_ro_button.setStyleSheet("QPushButton {\n"
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
        icon.addPixmap(QtGui.QPixmap("../theme/Icons/add-document.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.create_ro_button.setIcon(icon)
        self.create_ro_button.setIconSize(QtCore.QSize(30, 30))
        self.create_ro_button.setObjectName("create_ro_button")
        self.gridLayout.addWidget(self.create_ro_button, 0, 0, 1, 1)
        self.edit_appointment_button = QtWidgets.QPushButton(parent=Form)
        self.edit_appointment_button.setStyleSheet("QPushButton {\n"
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
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("../theme/Icons/edit.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.edit_appointment_button.setIcon(icon1)
        self.edit_appointment_button.setIconSize(QtCore.QSize(30, 30))
        self.edit_appointment_button.setObjectName("edit_appointment_button")
        self.gridLayout.addWidget(self.edit_appointment_button, 0, 1, 1, 1)
        self.delete_button = QtWidgets.QPushButton(parent=Form)
        self.delete_button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.OpenHandCursor))
        self.delete_button.setStyleSheet("QPushButton {\n"
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
        icon2.addPixmap(QtGui.QPixmap("../theme/Icons/trash.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.delete_button.setIcon(icon2)
        self.delete_button.setIconSize(QtCore.QSize(30, 30))
        self.delete_button.setFlat(True)
        self.delete_button.setObjectName("delete_button")
        self.gridLayout.addWidget(self.delete_button, 0, 2, 1, 1)
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
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("../theme/icons3/24x24/cil-x.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.cancel_button.setIcon(icon3)
        self.cancel_button.setIconSize(QtCore.QSize(30, 30))
        self.cancel_button.setObjectName("cancel_button")
        self.gridLayout.addWidget(self.cancel_button, 0, 3, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.create_ro_button.setText(_translate("Form", "Create RO"))
        self.edit_appointment_button.setText(_translate("Form", "Edit Appt"))
        self.delete_button.setText(_translate("Form", "Delete"))
        self.cancel_button.setText(_translate("Form", "Cancel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
