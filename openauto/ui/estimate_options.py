from PyQt6 import QtCore, QtGui, QtWidgets
from openauto.theme import resources_rc

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(915, 150)
        Form.setStyleSheet("color: #333;\n"
"background-color: #f8f8f2;\n"
"background-image: none;")
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.open_ro_button = QtWidgets.QPushButton(parent=Form)
        self.open_ro_button.setStyleSheet("QPushButton {\n"
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
        icon.addPixmap(QtGui.QPixmap(":/resources/icons3/24x24/cil-folder-open.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.open_ro_button.setIcon(icon)
        self.open_ro_button.setIconSize(QtCore.QSize(30, 30))
        self.open_ro_button.setObjectName("open_ro_button")
        self.gridLayout.addWidget(self.open_ro_button, 0, 0, 1, 1)
        self.change_status_button = QtWidgets.QPushButton(parent=Form)
        self.change_status_button.setStyleSheet("QPushButton {\n"
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
        icon1.addPixmap(QtGui.QPixmap(":/resources/icons3/24x24/cil-list.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.change_status_button.setIcon(icon1)
        self.change_status_button.setIconSize(QtCore.QSize(30, 30))
        self.change_status_button.setObjectName("change_status_button")
        self.gridLayout.addWidget(self.change_status_button, 0, 1, 1, 1)
        self.duplicate_ro_button = QtWidgets.QPushButton(parent=Form)
        self.duplicate_ro_button.setStyleSheet("QPushButton {\n"
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
        icon2.addPixmap(QtGui.QPixmap(":/resources/icons3/24x24/cil-copy.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.duplicate_ro_button.setIcon(icon2)
        self.duplicate_ro_button.setIconSize(QtCore.QSize(30, 30))
        self.duplicate_ro_button.setObjectName("duplicate_ro_button")
        self.gridLayout.addWidget(self.duplicate_ro_button, 0, 2, 1, 1)
        self.delete_ro_button = QtWidgets.QPushButton(parent=Form)
        self.delete_ro_button.setStyleSheet("QPushButton {\n"
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
        icon3.addPixmap(QtGui.QPixmap(":/resources/icons3/24x24/cil-trash.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.delete_ro_button.setIcon(icon3)
        self.delete_ro_button.setIconSize(QtCore.QSize(30, 30))
        self.delete_ro_button.setObjectName("delete_ro_button")
        self.gridLayout.addWidget(self.delete_ro_button, 0, 3, 1, 1)
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
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/resources/icons3/24x24/cil-exit-to-app.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.cancel_button.setIcon(icon4)
        self.cancel_button.setIconSize(QtCore.QSize(30, 30))
        self.cancel_button.setObjectName("cancel_button")
        self.gridLayout.addWidget(self.cancel_button, 0, 4, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.open_ro_button.setText(_translate("Form", "Open RO"))
        self.change_status_button.setText(_translate("Form", "Change Status"))
        self.duplicate_ro_button.setText(_translate("Form", "Duplicate"))
        self.delete_ro_button.setText(_translate("Form", "Delete"))
        self.cancel_button.setText(_translate("Form", "Cancel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
