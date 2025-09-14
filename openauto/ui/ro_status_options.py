from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_ro_options_widget(object):
    def setupUi(self, ro_options_widget):
        ro_options_widget.setObjectName("ro_options_widget")
        ro_options_widget.resize(915, 150)
        ro_options_widget.setStyleSheet("")
        self.gridLayout = QtWidgets.QGridLayout(ro_options_widget)
        self.gridLayout.setObjectName("gridLayout")
        self.open_status_button = QtWidgets.QPushButton(parent=ro_options_widget)
        self.open_status_button.setStyleSheet("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/resources/Icons/ballot.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.open_status_button.setIcon(icon)
        self.open_status_button.setIconSize(QtCore.QSize(30, 30))
        self.open_status_button.setObjectName("open_status_button")
        self.gridLayout.addWidget(self.open_status_button, 0, 0, 1, 1)
        self.cancel_status_button = QtWidgets.QPushButton(parent=ro_options_widget)
        self.cancel_status_button.setStyleSheet("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/resources/icons3/24x24/cil-x.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.cancel_status_button.setIcon(icon1)
        self.cancel_status_button.setIconSize(QtCore.QSize(30, 30))
        self.cancel_status_button.setObjectName("cancel_status_button")
        self.gridLayout.addWidget(self.cancel_status_button, 0, 4, 1, 1)
        self.in_progress_status_button = QtWidgets.QPushButton(parent=ro_options_widget)
        self.in_progress_status_button.setStyleSheet("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/resources/Icons/document.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.in_progress_status_button.setIcon(icon2)
        self.in_progress_status_button.setIconSize(QtCore.QSize(30, 30))
        self.in_progress_status_button.setObjectName("in_progress_status_button")
        self.gridLayout.addWidget(self.in_progress_status_button, 0, 2, 1, 1)
        self.completed_status_button = QtWidgets.QPushButton(parent=ro_options_widget)
        self.completed_status_button.setStyleSheet("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/resources/Icons/list-check.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.completed_status_button.setIcon(icon3)
        self.completed_status_button.setIconSize(QtCore.QSize(30, 30))
        self.completed_status_button.setObjectName("completed_status_button")
        self.gridLayout.addWidget(self.completed_status_button, 0, 3, 1, 1)
        self.approved_status_button = QtWidgets.QPushButton(parent=ro_options_widget)
        self.approved_status_button.setStyleSheet("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/resources/icons3/24x24/cil-thumb-up.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.approved_status_button.setIcon(icon4)
        self.approved_status_button.setIconSize(QtCore.QSize(30, 30))
        self.approved_status_button.setObjectName("approved_status_button")
        self.gridLayout.addWidget(self.approved_status_button, 0, 1, 1, 1)

        self.retranslateUi(ro_options_widget)
        QtCore.QMetaObject.connectSlotsByName(ro_options_widget)

    def retranslateUi(self, ro_options_widget):
        _translate = QtCore.QCoreApplication.translate
        ro_options_widget.setWindowTitle(_translate("ro_options_widget", "Form"))
        self.open_status_button.setText(_translate("ro_options_widget", "Estimate"))
        self.cancel_status_button.setText(_translate("ro_options_widget", "Cancel"))
        self.in_progress_status_button.setText(_translate("ro_options_widget", "In Progress"))
        self.completed_status_button.setText(_translate("ro_options_widget", "Completed"))
        self.approved_status_button.setText(_translate("ro_options_widget", "Approved"))
from openauto.theme import resources_rc


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ro_options_widget = QtWidgets.QWidget()
    ui = Ui_ro_options_widget()
    ui.setupUi(ro_options_widget)
    ro_options_widget.show()
    sys.exit(app.exec())
