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

class Ui_create_customer_form(object):
    def setupUi(self, create_customer_form):
        create_customer_form.setObjectName("create_customer_form")
        create_customer_form.resize(606, 693)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("/home/fred/PycharmProjects/OpenAuto/openauto/theme/../../OpenAutoLite/ui_files/designer_files/Images/winter_auto.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        icon.addPixmap(QtGui.QPixmap("/home/fred/PycharmProjects/OpenAuto/openauto/theme/../../OpenAutoLite/ui_files/designer_files/Images/winter_auto.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On)
        create_customer_form.setWindowIcon(icon)
        create_customer_form.setStyleSheet("color: #ffffff;\n"
"background-color: #f2f2f8;\n"
"background-image: none;")
        self.formLayout = QtWidgets.QFormLayout(create_customer_form)
        self.formLayout.setObjectName("formLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetDefaultConstraint)
        self.gridLayout.setContentsMargins(-1, 0, -1, 0)
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setVerticalSpacing(15)
        self.gridLayout.setObjectName("gridLayout")
        self.zipcode_line = QtWidgets.QLineEdit(parent=create_customer_form)
        self.zipcode_line.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.zipcode_line.setFont(font)
        self.zipcode_line.setStyleSheet("border-radius: 10px;\n"
"background-color: #fefeff;\n"
"color: black;\n"
"")
        self.zipcode_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.zipcode_line.setObjectName("zipcode_line")
        self.gridLayout.addWidget(self.zipcode_line, 6, 1, 1, 1)
        self.city_line = QtWidgets.QLineEdit(parent=create_customer_form)
        self.city_line.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.city_line.setFont(font)
        self.city_line.setStyleSheet("border-radius: 10px;\n"
"background-color: #fefeff;\n"
"color: black;\n"
"")
        self.city_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.city_line.setObjectName("city_line")
        self.gridLayout.addWidget(self.city_line, 4, 1, 1, 1)
        self.state_line = QtWidgets.QLineEdit(parent=create_customer_form)
        self.state_line.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.state_line.setFont(font)
        self.state_line.setStyleSheet("border-radius: 10px;\n"
"background-color: #fefeff;\n"
"color: black;\n"
"")
        self.state_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.state_line.setObjectName("state_line")
        self.gridLayout.addWidget(self.state_line, 5, 1, 1, 1)
        self.address_line = QtWidgets.QLineEdit(parent=create_customer_form)
        self.address_line.setMinimumSize(QtCore.QSize(0, 40))
        self.address_line.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.address_line.setFont(font)
        self.address_line.setStyleSheet("border-radius: 10px;\n"
"background-color: #fefeff;\n"
"color: black;\n"
"")
        self.address_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.address_line.setObjectName("address_line")
        self.gridLayout.addWidget(self.address_line, 3, 1, 1, 1)
        self.first_name_line = QtWidgets.QLineEdit(parent=create_customer_form)
        self.first_name_line.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.first_name_line.setFont(font)
        self.first_name_line.setStyleSheet("border-radius: 10px;\n"
"background-color: #fefeff;\n"
"color: black;\n"
"")
        self.first_name_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.first_name_line.setObjectName("first_name_line")
        self.gridLayout.addWidget(self.first_name_line, 0, 1, 1, 1)
        self.alt_line = QtWidgets.QLineEdit(parent=create_customer_form)
        self.alt_line.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.alt_line.setFont(font)
        self.alt_line.setStyleSheet("border-radius: 10px;\n"
"background-color: #fefeff;\n"
"color: black;\n"
"")
        self.alt_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.alt_line.setObjectName("alt_line")
        self.gridLayout.addWidget(self.alt_line, 8, 1, 1, 1)
        self.phone_line = QtWidgets.QLineEdit(parent=create_customer_form)
        self.phone_line.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.phone_line.setFont(font)
        self.phone_line.setStyleSheet("border-radius: 10px;\n"
"background-color: #fefeff;\n"
"color: black;\n"
"")
        self.phone_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.phone_line.setObjectName("phone_line")
        self.gridLayout.addWidget(self.phone_line, 7, 1, 1, 1)
        self.last_name_line = QtWidgets.QLineEdit(parent=create_customer_form)
        self.last_name_line.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.last_name_line.setFont(font)
        self.last_name_line.setStyleSheet("border-radius: 10px;\n"
"background-color: #fefeff;\n"
"color: black;")
        self.last_name_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.last_name_line.setObjectName("last_name_line")
        self.gridLayout.addWidget(self.last_name_line, 2, 1, 1, 1)
        self.email_line = QtWidgets.QLineEdit(parent=create_customer_form)
        self.email_line.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.email_line.setFont(font)
        self.email_line.setStyleSheet("border-radius: 10px;\n"
"background-color: #fefeff;\n"
"color: black;\n"
"")
        self.email_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.email_line.setObjectName("email_line")
        self.gridLayout.addWidget(self.email_line, 9, 1, 1, 1)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.ItemRole.SpanningRole, self.gridLayout)
        spacerItem = QtWidgets.QSpacerItem(40, 125, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.formLayout.setItem(4, QtWidgets.QFormLayout.ItemRole.FieldRole, spacerItem)
        spacerItem1 = QtWidgets.QSpacerItem(40, 125, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.formLayout.setItem(4, QtWidgets.QFormLayout.ItemRole.LabelRole, spacerItem1)
        spacerItem2 = QtWidgets.QSpacerItem(120, 125, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.formLayout.setItem(5, QtWidgets.QFormLayout.ItemRole.FieldRole, spacerItem2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.abort_button = QtWidgets.QPushButton(parent=create_customer_form)
        self.abort_button.setStyleSheet("QPushButton {\n"
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
        icon1.addPixmap(QtGui.QPixmap("../theme/icons3/24x24/cil-x.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.abort_button.setIcon(icon1)
        self.abort_button.setIconSize(QtCore.QSize(30, 30))
        self.abort_button.setFlat(True)
        self.abort_button.setObjectName("abort_button")
        self.horizontalLayout.addWidget(self.abort_button)
        self.edit_button = QtWidgets.QPushButton(parent=create_customer_form)
        self.edit_button.setMinimumSize(QtCore.QSize(0, 30))
        self.edit_button.setStyleSheet("QPushButton {\n"
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
        icon2.addPixmap(QtGui.QPixmap("../theme/icons3/24x24/cil-check.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.edit_button.setIcon(icon2)
        self.edit_button.setIconSize(QtCore.QSize(30, 30))
        self.edit_button.setObjectName("edit_button")
        self.horizontalLayout.addWidget(self.edit_button)
        self.save_button = QtWidgets.QPushButton(parent=create_customer_form)
        self.save_button.setStyleSheet("QPushButton {\n"
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
        self.save_button.setIcon(icon2)
        self.save_button.setIconSize(QtCore.QSize(30, 30))
        self.save_button.setAutoRepeatDelay(100)
        self.save_button.setFlat(True)
        self.save_button.setObjectName("save_button")
        self.horizontalLayout.addWidget(self.save_button)
        self.formLayout.setLayout(6, QtWidgets.QFormLayout.ItemRole.SpanningRole, self.horizontalLayout)

        self.retranslateUi(create_customer_form)
        QtCore.QMetaObject.connectSlotsByName(create_customer_form)

    def retranslateUi(self, create_customer_form):
        _translate = QtCore.QCoreApplication.translate
        create_customer_form.setWindowTitle(_translate("create_customer_form", "Edit Customer"))
        self.zipcode_line.setPlaceholderText(_translate("create_customer_form", "Zip"))
        self.city_line.setPlaceholderText(_translate("create_customer_form", "City"))
        self.state_line.setPlaceholderText(_translate("create_customer_form", "State"))
        self.address_line.setPlaceholderText(_translate("create_customer_form", "Address"))
        self.first_name_line.setPlaceholderText(_translate("create_customer_form", "First Name"))
        self.alt_line.setPlaceholderText(_translate("create_customer_form", "Second #"))
        self.phone_line.setPlaceholderText(_translate("create_customer_form", "Phone #"))
        self.last_name_line.setPlaceholderText(_translate("create_customer_form", "Last Name"))
        self.email_line.setPlaceholderText(_translate("create_customer_form", "Email"))
        self.abort_button.setText(_translate("create_customer_form", "Cancel"))
        self.edit_button.setText(_translate("create_customer_form", "Edit"))
        self.save_button.setText(_translate("create_customer_form", "Save"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    create_customer_form = QtWidgets.QWidget()
    ui = Ui_create_customer_form()
    ui.setupUi(create_customer_form)
    create_customer_form.show()
    sys.exit(app.exec())
