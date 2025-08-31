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
        self.open_button = QtWidgets.QPushButton(parent=Form)
        self.open_button.setStyleSheet("QPushButton {\n"
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
        icon.addPixmap(QtGui.QPixmap(":/resources/Icons/ballot.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.open_button.setIcon(icon)
        self.open_button.setIconSize(QtCore.QSize(30, 30))
        self.open_button.setObjectName("open_button")
        self.gridLayout.addWidget(self.open_button, 0, 0, 1, 1)
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
        self.gridLayout.addWidget(self.cancel_button, 0, 4, 1, 1)
        self.in_progress_button = QtWidgets.QPushButton(parent=Form)
        self.in_progress_button.setStyleSheet("QPushButton {\n"
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
        icon2.addPixmap(QtGui.QPixmap(":/resources/Icons/document.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.in_progress_button.setIcon(icon2)
        self.in_progress_button.setIconSize(QtCore.QSize(30, 30))
        self.in_progress_button.setObjectName("in_progress_button")
        self.gridLayout.addWidget(self.in_progress_button, 0, 2, 1, 1)
        self.completed_button = QtWidgets.QPushButton(parent=Form)
        self.completed_button.setStyleSheet("QPushButton {\n"
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
        icon3.addPixmap(QtGui.QPixmap(":/resources/Icons/list-check.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.completed_button.setIcon(icon3)
        self.completed_button.setIconSize(QtCore.QSize(30, 30))
        self.completed_button.setObjectName("completed_button")
        self.gridLayout.addWidget(self.completed_button, 0, 3, 1, 1)
        self.approved_button = QtWidgets.QPushButton(parent=Form)
        self.approved_button.setStyleSheet("QPushButton {\n"
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
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/resources/icons3/24x24/cil-thumb-up.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.approved_button.setIcon(icon4)
        self.approved_button.setIconSize(QtCore.QSize(30, 30))
        self.approved_button.setObjectName("approved_button")
        self.gridLayout.addWidget(self.approved_button, 0, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.open_button.setText(_translate("Form", "Estimate"))
        self.cancel_button.setText(_translate("Form", "Cancel"))
        self.in_progress_button.setText(_translate("Form", "In Progress"))
        self.completed_button.setText(_translate("Form", "Completed"))
        self.approved_button.setText(_translate("Form", "Approved"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
