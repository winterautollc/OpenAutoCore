from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_estimate_options_form(object):
    def setupUi(self, estimate_options_form):
        estimate_options_form.setObjectName("estimate_options_form")
        estimate_options_form.resize(915, 150)
        estimate_options_form.setStyleSheet("")
        self.gridLayout = QtWidgets.QGridLayout(estimate_options_form)
        self.gridLayout.setObjectName("gridLayout")
        self.open_ro_button = QtWidgets.QPushButton(parent=estimate_options_form)
        self.open_ro_button.setStyleSheet("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/resources/icons3/24x24/cil-folder-open.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.open_ro_button.setIcon(icon)
        self.open_ro_button.setIconSize(QtCore.QSize(30, 30))
        self.open_ro_button.setObjectName("open_ro_button")
        self.gridLayout.addWidget(self.open_ro_button, 0, 0, 1, 1)
        self.change_ro_status_button = QtWidgets.QPushButton(parent=estimate_options_form)
        self.change_ro_status_button.setStyleSheet("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/resources/icons3/24x24/cil-list.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.change_ro_status_button.setIcon(icon1)
        self.change_ro_status_button.setIconSize(QtCore.QSize(30, 30))
        self.change_ro_status_button.setObjectName("change_ro_status_button")
        self.gridLayout.addWidget(self.change_ro_status_button, 0, 1, 1, 1)
        self.duplicate_ro_button = QtWidgets.QPushButton(parent=estimate_options_form)
        self.duplicate_ro_button.setStyleSheet("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/resources/icons3/24x24/cil-copy.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.duplicate_ro_button.setIcon(icon2)
        self.duplicate_ro_button.setIconSize(QtCore.QSize(30, 30))
        self.duplicate_ro_button.setObjectName("duplicate_ro_button")
        self.gridLayout.addWidget(self.duplicate_ro_button, 0, 2, 1, 1)
        self.delete_ro_button = QtWidgets.QPushButton(parent=estimate_options_form)
        self.delete_ro_button.setStyleSheet("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/resources/icons3/24x24/cil-trash.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.delete_ro_button.setIcon(icon3)
        self.delete_ro_button.setIconSize(QtCore.QSize(30, 30))
        self.delete_ro_button.setObjectName("delete_ro_button")
        self.gridLayout.addWidget(self.delete_ro_button, 0, 3, 1, 1)
        self.cancel_ro_options_button = QtWidgets.QPushButton(parent=estimate_options_form)
        self.cancel_ro_options_button.setStyleSheet("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/resources/icons3/24x24/cil-exit-to-app.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.cancel_ro_options_button.setIcon(icon4)
        self.cancel_ro_options_button.setIconSize(QtCore.QSize(30, 30))
        self.cancel_ro_options_button.setObjectName("cancel_ro_options_button")
        self.gridLayout.addWidget(self.cancel_ro_options_button, 0, 4, 1, 1)

        self.retranslateUi(estimate_options_form)
        QtCore.QMetaObject.connectSlotsByName(estimate_options_form)

    def retranslateUi(self, estimate_options_form):
        _translate = QtCore.QCoreApplication.translate
        estimate_options_form.setWindowTitle(_translate("estimate_options_form", "Form"))
        self.open_ro_button.setText(_translate("estimate_options_form", "Open RO"))
        self.change_ro_status_button.setText(_translate("estimate_options_form", "Change Status"))
        self.duplicate_ro_button.setText(_translate("estimate_options_form", "Duplicate"))
        self.delete_ro_button.setText(_translate("estimate_options_form", "Delete"))
        self.cancel_ro_options_button.setText(_translate("estimate_options_form", "Cancel"))
from openauto.theme import resources_rc


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    estimate_options_form = QtWidgets.QWidget()
    ui = Ui_estimate_options_form()
    ui.setupUi(estimate_options_form)
    estimate_options_form.show()
    sys.exit(app.exec())
