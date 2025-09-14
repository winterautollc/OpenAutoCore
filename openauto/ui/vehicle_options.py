from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_vehcile_options_form(object):
    def setupUi(self, vehcile_options_form):
        vehcile_options_form.setObjectName("vehcile_options_form")
        vehcile_options_form.resize(915, 150)
        vehcile_options_form.setStyleSheet("")
        self.gridLayout = QtWidgets.QGridLayout(vehcile_options_form)
        self.gridLayout.setObjectName("gridLayout")
        self.create_ro_vehicle_button = QtWidgets.QPushButton(parent=vehcile_options_form)
        self.create_ro_vehicle_button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.OpenHandCursor))
        self.create_ro_vehicle_button.setStyleSheet("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/resources/Icons/add-document.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.create_ro_vehicle_button.setIcon(icon)
        self.create_ro_vehicle_button.setIconSize(QtCore.QSize(30, 30))
        self.create_ro_vehicle_button.setFlat(True)
        self.create_ro_vehicle_button.setObjectName("create_ro_vehicle_button")
        self.gridLayout.addWidget(self.create_ro_vehicle_button, 0, 0, 1, 1)
        self.change_owner_vehicle_button = QtWidgets.QPushButton(parent=vehcile_options_form)
        self.change_owner_vehicle_button.setStyleSheet("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/resources/Icons/user.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.change_owner_vehicle_button.setIcon(icon1)
        self.change_owner_vehicle_button.setIconSize(QtCore.QSize(30, 30))
        self.change_owner_vehicle_button.setFlat(True)
        self.change_owner_vehicle_button.setObjectName("change_owner_vehicle_button")
        self.gridLayout.addWidget(self.change_owner_vehicle_button, 0, 1, 1, 1)
        self.delete_vehicle_button = QtWidgets.QPushButton(parent=vehcile_options_form)
        self.delete_vehicle_button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.OpenHandCursor))
        self.delete_vehicle_button.setStyleSheet("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/resources/Icons/trash.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.delete_vehicle_button.setIcon(icon2)
        self.delete_vehicle_button.setIconSize(QtCore.QSize(30, 30))
        self.delete_vehicle_button.setFlat(True)
        self.delete_vehicle_button.setObjectName("delete_vehicle_button")
        self.gridLayout.addWidget(self.delete_vehicle_button, 0, 2, 1, 1)
        self.cancel_vehicle_options_button = QtWidgets.QPushButton(parent=vehcile_options_form)
        self.cancel_vehicle_options_button.setStyleSheet("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/resources/icons3/24x24/cil-x.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.cancel_vehicle_options_button.setIcon(icon3)
        self.cancel_vehicle_options_button.setIconSize(QtCore.QSize(30, 30))
        self.cancel_vehicle_options_button.setFlat(True)
        self.cancel_vehicle_options_button.setObjectName("cancel_vehicle_options_button")
        self.gridLayout.addWidget(self.cancel_vehicle_options_button, 0, 3, 1, 1)

        self.retranslateUi(vehcile_options_form)
        QtCore.QMetaObject.connectSlotsByName(vehcile_options_form)

    def retranslateUi(self, vehcile_options_form):
        _translate = QtCore.QCoreApplication.translate
        vehcile_options_form.setWindowTitle(_translate("vehcile_options_form", "Form"))
        self.create_ro_vehicle_button.setText(_translate("vehcile_options_form", "Create RO"))
        self.change_owner_vehicle_button.setText(_translate("vehcile_options_form", "Change Owner"))
        self.delete_vehicle_button.setText(_translate("vehcile_options_form", "Delete"))
        self.cancel_vehicle_options_button.setText(_translate("vehcile_options_form", "Cancel"))
from openauto.theme import resources_rc


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    vehcile_options_form = QtWidgets.QWidget()
    ui = Ui_vehcile_options_form()
    ui.setupUi(vehcile_options_form)
    vehcile_options_form.show()
    sys.exit(app.exec())
