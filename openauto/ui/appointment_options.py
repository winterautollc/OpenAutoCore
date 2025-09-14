from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_appointment_options_form(object):
    def setupUi(self, appointment_options_form):
        appointment_options_form.setObjectName("appointment_options_form")
        appointment_options_form.resize(915, 150)
        appointment_options_form.setStyleSheet("")
        self.gridLayout = QtWidgets.QGridLayout(appointment_options_form)
        self.gridLayout.setObjectName("gridLayout")
        self.create_ro_button = QtWidgets.QPushButton(parent=appointment_options_form)
        self.create_ro_button.setStyleSheet("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/resources/Icons/add-document.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.create_ro_button.setIcon(icon)
        self.create_ro_button.setIconSize(QtCore.QSize(30, 30))
        self.create_ro_button.setFlat(True)
        self.create_ro_button.setObjectName("create_ro_button")
        self.gridLayout.addWidget(self.create_ro_button, 0, 0, 1, 1)
        self.edit_appointment_button = QtWidgets.QPushButton(parent=appointment_options_form)
        self.edit_appointment_button.setStyleSheet("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/resources/Icons/edit.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.edit_appointment_button.setIcon(icon1)
        self.edit_appointment_button.setIconSize(QtCore.QSize(30, 30))
        self.edit_appointment_button.setFlat(True)
        self.edit_appointment_button.setObjectName("edit_appointment_button")
        self.gridLayout.addWidget(self.edit_appointment_button, 0, 1, 1, 1)
        self.delete_appointment_button = QtWidgets.QPushButton(parent=appointment_options_form)
        self.delete_appointment_button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.OpenHandCursor))
        self.delete_appointment_button.setStyleSheet("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/resources/Icons/trash.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.delete_appointment_button.setIcon(icon2)
        self.delete_appointment_button.setIconSize(QtCore.QSize(30, 30))
        self.delete_appointment_button.setFlat(True)
        self.delete_appointment_button.setObjectName("delete_appointment_button")
        self.gridLayout.addWidget(self.delete_appointment_button, 0, 2, 1, 1)
        self.cancel_appt_options_button = QtWidgets.QPushButton(parent=appointment_options_form)
        self.cancel_appt_options_button.setStyleSheet("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/resources/icons3/24x24/cil-x.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.cancel_appt_options_button.setIcon(icon3)
        self.cancel_appt_options_button.setIconSize(QtCore.QSize(30, 30))
        self.cancel_appt_options_button.setFlat(True)
        self.cancel_appt_options_button.setObjectName("cancel_appt_options_button")
        self.gridLayout.addWidget(self.cancel_appt_options_button, 0, 3, 1, 1)

        self.retranslateUi(appointment_options_form)
        QtCore.QMetaObject.connectSlotsByName(appointment_options_form)

    def retranslateUi(self, appointment_options_form):
        _translate = QtCore.QCoreApplication.translate
        appointment_options_form.setWindowTitle(_translate("appointment_options_form", "Form"))
        self.create_ro_button.setText(_translate("appointment_options_form", "Create RO"))
        self.edit_appointment_button.setText(_translate("appointment_options_form", "Edit Appt"))
        self.delete_appointment_button.setText(_translate("appointment_options_form", "Delete"))
        self.cancel_appt_options_button.setText(_translate("appointment_options_form", "Cancel"))
from openauto.theme import resources_rc


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    appointment_options_form = QtWidgets.QWidget()
    ui = Ui_appointment_options_form()
    ui.setupUi(appointment_options_form)
    appointment_options_form.show()
    sys.exit(app.exec())
