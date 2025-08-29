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
        Form.resize(1008, 730)
        Form.setStyleSheet("color: black;\n"
"background-color: #ebebe6;\n"
"background-image: none;\n"
"border-radius: 10px;")
        self.gridLayout_3 = QtWidgets.QGridLayout(Form)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.frame = QtWidgets.QFrame(parent=Form)
        self.frame.setStyleSheet("color: black;\n"
"background-color: #d8d8d2;\n"
"background-image: none;\n"
"border-radius: 10px;")
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setObjectName("gridLayout")
        self.create_user_button = QtWidgets.QPushButton(parent=self.frame)
        self.create_user_button.setMinimumSize(QtCore.QSize(90, 40))
        self.create_user_button.setStyleSheet("QPushButton {\n"
"    color: #fff;\n"
"    background-color: #94C4C1;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #CE6A6C;\n"
"    color: #fff;\n"
"    border-radius: 10px;\n"
"}")
        self.create_user_button.setObjectName("create_user_button")
        self.gridLayout.addWidget(self.create_user_button, 0, 1, 1, 1)
        self.login_tab_button = QtWidgets.QPushButton(parent=self.frame)
        self.login_tab_button.setMinimumSize(QtCore.QSize(90, 40))
        self.login_tab_button.setStyleSheet("QPushButton {\n"
"    color: #fff;\n"
"    background-color: #94C4C1;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #CE6A6C;\n"
"    color: #fff;\n"
"    border-radius: 10px;\n"
"}")
        self.login_tab_button.setObjectName("login_tab_button")
        self.gridLayout.addWidget(self.login_tab_button, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.frame, 0, 1, 1, 1)
        self.stackedWidget = QtWidgets.QStackedWidget(parent=Form)
        self.stackedWidget.setStyleSheet("color: black;\n"
"background-color: #ebebe6;\n"
"background-image: none;\n"
"border-radius: 10px;")
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.page)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.password_label = QtWidgets.QLabel(parent=self.page)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.password_label.setFont(font)
        self.password_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.password_label.setObjectName("password_label")
        self.gridLayout_2.addWidget(self.password_label, 6, 0, 1, 1)
        self.login_name_label = QtWidgets.QLabel(parent=self.page)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.login_name_label.setFont(font)
        self.login_name_label.setTextFormat(QtCore.Qt.TextFormat.RichText)
        self.login_name_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.login_name_label.setObjectName("login_name_label")
        self.gridLayout_2.addWidget(self.login_name_label, 5, 0, 1, 1)
        self.remember_me = QtWidgets.QCheckBox(parent=self.page)
        self.remember_me.setObjectName("remember_me")
        self.gridLayout_2.addWidget(self.remember_me, 6, 3, 1, 1)
        self.login_name_line = QtWidgets.QLineEdit(parent=self.page)
        self.login_name_line.setMinimumSize(QtCore.QSize(0, 30))
        self.login_name_line.setMaximumSize(QtCore.QSize(200, 16777215))
        self.login_name_line.setStyleSheet("border-radius: 10px;\n"
"background-color: #fefeff;\n"
"color: black;")
        self.login_name_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.login_name_line.setObjectName("login_name_line")
        self.gridLayout_2.addWidget(self.login_name_line, 5, 1, 1, 1)
        self.password_line = QtWidgets.QLineEdit(parent=self.page)
        self.password_line.setMinimumSize(QtCore.QSize(0, 30))
        self.password_line.setMaximumSize(QtCore.QSize(220, 16777215))
        self.password_line.setStyleSheet("border-radius: 10px;\n"
"background-color: #fefeff;\n"
"color: black;")
        self.password_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.password_line.setObjectName("password_line")
        self.gridLayout_2.addWidget(self.password_line, 6, 1, 1, 1)
        self.cancel_login_button = QtWidgets.QPushButton(parent=self.page)
        self.cancel_login_button.setMinimumSize(QtCore.QSize(0, 35))
        self.cancel_login_button.setMaximumSize(QtCore.QSize(200, 16777215))
        self.cancel_login_button.setStyleSheet("QPushButton {\n"
"    color: #fff;\n"
"    border-radius: 10px;\n"
"    background-color: #CE6A6C;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #94C4C1;\n"
"    color: #fff;\n"
"    border-radius: 10px;\n"
"}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../theme/Icons/cross.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.cancel_login_button.setIcon(icon)
        self.cancel_login_button.setIconSize(QtCore.QSize(30, 30))
        self.cancel_login_button.setObjectName("cancel_login_button")
        self.gridLayout_2.addWidget(self.cancel_login_button, 10, 1, 1, 1)
        self.login_button = QtWidgets.QPushButton(parent=self.page)
        self.login_button.setMinimumSize(QtCore.QSize(0, 35))
        self.login_button.setMaximumSize(QtCore.QSize(200, 16777215))
        self.login_button.setStyleSheet("QPushButton {\n"
"    color: #fff;\n"
"    border-radius: 10px;\n"
"    background-color: #94C4C1;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #CE6A6C;\n"
"    color: #fff;\n"
"    border-radius: 10px;\n"
"}")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("../theme/Icons/check.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.login_button.setIcon(icon1)
        self.login_button.setIconSize(QtCore.QSize(30, 30))
        self.login_button.setObjectName("login_button")
        self.gridLayout_2.addWidget(self.login_button, 10, 3, 1, 1)
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.page_2)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.first_name_label = QtWidgets.QLabel(parent=self.page_2)
        self.first_name_label.setMinimumSize(QtCore.QSize(0, 50))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.first_name_label.setFont(font)
        self.first_name_label.setObjectName("first_name_label")
        self.verticalLayout.addWidget(self.first_name_label)
        self.first_name_line = QtWidgets.QLineEdit(parent=self.page_2)
        self.first_name_line.setMinimumSize(QtCore.QSize(0, 30))
        self.first_name_line.setMaximumSize(QtCore.QSize(250, 16777215))
        self.first_name_line.setStyleSheet("border-radius: 10px;\n"
"background-color: #fefeff;\n"
"color: black;")
        self.first_name_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.first_name_line.setObjectName("first_name_line")
        self.verticalLayout.addWidget(self.first_name_line)
        self.last_name_label = QtWidgets.QLabel(parent=self.page_2)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.last_name_label.setFont(font)
        self.last_name_label.setObjectName("last_name_label")
        self.verticalLayout.addWidget(self.last_name_label)
        self.last_name_line = QtWidgets.QLineEdit(parent=self.page_2)
        self.last_name_line.setMinimumSize(QtCore.QSize(0, 30))
        self.last_name_line.setMaximumSize(QtCore.QSize(250, 16777215))
        self.last_name_line.setStyleSheet("border-radius: 10px;\n"
"background-color: #fefeff;\n"
"color: black;")
        self.last_name_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.last_name_line.setObjectName("last_name_line")
        self.verticalLayout.addWidget(self.last_name_line)
        self.phone_label = QtWidgets.QLabel(parent=self.page_2)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.phone_label.setFont(font)
        self.phone_label.setObjectName("phone_label")
        self.verticalLayout.addWidget(self.phone_label)
        self.phone_line = QtWidgets.QLineEdit(parent=self.page_2)
        self.phone_line.setMinimumSize(QtCore.QSize(0, 30))
        self.phone_line.setMaximumSize(QtCore.QSize(250, 16777215))
        self.phone_line.setStyleSheet("border-radius: 10px;\n"
"background-color: #fefeff;\n"
"color: black;")
        self.phone_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.phone_line.setObjectName("phone_line")
        self.verticalLayout.addWidget(self.phone_line)
        self.type_selector = QtWidgets.QComboBox(parent=self.page_2)
        self.type_selector.setMinimumSize(QtCore.QSize(0, 35))
        self.type_selector.setMaximumSize(QtCore.QSize(250, 16777215))
        self.type_selector.setStyleSheet("QComboBox {\n"
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
        self.type_selector.setObjectName("type_selector")
        self.type_selector.addItem("")
        self.type_selector.addItem("")
        self.type_selector.addItem("")
        self.type_selector.addItem("")
        self.verticalLayout.addWidget(self.type_selector)
        self.gridLayout_4.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.username_label = QtWidgets.QLabel(parent=self.page_2)
        self.username_label.setMaximumSize(QtCore.QSize(1677215, 100))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.username_label.setFont(font)
        self.username_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.username_label.setObjectName("username_label")
        self.verticalLayout_2.addWidget(self.username_label)
        self.username_line = QtWidgets.QLineEdit(parent=self.page_2)
        self.username_line.setMinimumSize(QtCore.QSize(0, 30))
        self.username_line.setMaximumSize(QtCore.QSize(250, 16777215))
        self.username_line.setStyleSheet("border-radius: 10px;\n"
"background-color: #fefeff;\n"
"color: black;")
        self.username_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.username_line.setObjectName("username_line")
        self.verticalLayout_2.addWidget(self.username_line)
        self.email_label = QtWidgets.QLabel(parent=self.page_2)
        self.email_label.setMaximumSize(QtCore.QSize(16777215, 100))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.email_label.setFont(font)
        self.email_label.setObjectName("email_label")
        self.verticalLayout_2.addWidget(self.email_label)
        self.email_line = QtWidgets.QLineEdit(parent=self.page_2)
        self.email_line.setMinimumSize(QtCore.QSize(0, 30))
        self.email_line.setMaximumSize(QtCore.QSize(250, 16777215))
        self.email_line.setStyleSheet("border-radius: 10px;\n"
"background-color: #fefeff;\n"
"color: black;")
        self.email_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.email_line.setObjectName("email_line")
        self.verticalLayout_2.addWidget(self.email_line)
        self.password_label_2 = QtWidgets.QLabel(parent=self.page_2)
        self.password_label_2.setMaximumSize(QtCore.QSize(16777215, 100))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.password_label_2.setFont(font)
        self.password_label_2.setObjectName("password_label_2")
        self.verticalLayout_2.addWidget(self.password_label_2)
        self.password_line_2 = QtWidgets.QLineEdit(parent=self.page_2)
        self.password_line_2.setMinimumSize(QtCore.QSize(0, 30))
        self.password_line_2.setMaximumSize(QtCore.QSize(250, 16777215))
        self.password_line_2.setStyleSheet("border-radius: 10px;\n"
"background-color: #fefeff;\n"
"color: black;")
        self.password_line_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.password_line_2.setObjectName("password_line_2")
        self.verticalLayout_2.addWidget(self.password_line_2)
        self.gridLayout_4.addLayout(self.verticalLayout_2, 0, 1, 1, 1)
        self.cancel_create_button = QtWidgets.QPushButton(parent=self.page_2)
        self.cancel_create_button.setMinimumSize(QtCore.QSize(150, 35))
        self.cancel_create_button.setStyleSheet("QPushButton {\n"
"    color: #fff;\n"
"    border-radius: 10px;\n"
"    background-color: #CE6A6C;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #94C4C1;\n"
"    color: #fff;\n"
"    border-radius: 10px;\n"
"}")
        self.cancel_create_button.setIcon(icon)
        self.cancel_create_button.setIconSize(QtCore.QSize(30, 30))
        self.cancel_create_button.setObjectName("cancel_create_button")
        self.gridLayout_4.addWidget(self.cancel_create_button, 1, 0, 1, 1)
        self.save_user_button = QtWidgets.QPushButton(parent=self.page_2)
        self.save_user_button.setMinimumSize(QtCore.QSize(150, 35))
        self.save_user_button.setStyleSheet("QPushButton {\n"
"    color: #fff;\n"
"    background-color: #94C4C1;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #CE6A6C;\n"
"    color: #fff;\n"
"    border-radius: 10px;\n"
"}")
        self.save_user_button.setIcon(icon1)
        self.save_user_button.setIconSize(QtCore.QSize(30, 30))
        self.save_user_button.setObjectName("save_user_button")
        self.gridLayout_4.addWidget(self.save_user_button, 1, 1, 1, 1)
        self.stackedWidget.addWidget(self.page_2)
        self.gridLayout_3.addWidget(self.stackedWidget, 1, 1, 1, 1)

        self.retranslateUi(Form)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.create_user_button.setText(_translate("Form", "Create"))
        self.login_tab_button.setText(_translate("Form", "Login"))
        self.password_label.setText(_translate("Form", "Password"))
        self.login_name_label.setText(_translate("Form", "User Or Email"))
        self.remember_me.setText(_translate("Form", "Remember Me"))
        self.cancel_login_button.setText(_translate("Form", "Cancel"))
        self.login_button.setText(_translate("Form", "Login"))
        self.first_name_label.setText(_translate("Form", "First Name"))
        self.last_name_label.setText(_translate("Form", "Last Name"))
        self.phone_label.setText(_translate("Form", "Phone"))
        self.type_selector.setItemText(0, _translate("Form", "TYPE"))
        self.type_selector.setItemText(1, _translate("Form", "Service Writer"))
        self.type_selector.setItemText(2, _translate("Form", "Technician"))
        self.type_selector.setItemText(3, _translate("Form", "Manager"))
        self.username_label.setText(_translate("Form", "User Name"))
        self.email_label.setText(_translate("Form", "Email"))
        self.password_label_2.setText(_translate("Form", "Password"))
        self.cancel_create_button.setText(_translate("Form", "Cancel"))
        self.save_user_button.setText(_translate("Form", "Save"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
