from PyQt6.QtWidgets import QLineEdit, QDialog
from PyQt6.QtCore import QSettings
from PyQt6 import QtCore, QtWidgets
from openauto.ui.login_create_form import Ui_Form
from openauto.repositories import users_repository
import mysql.connector
import os
import keyring


APP_ORG = "WinterAuto"
APP_NAME = "OpenAuto"
KEYRING_SERVICE = "OpenAutoLogin"

TYPE_MAP = {
    "Service Writer": "writer",
    "Technician": "technician",
    "Manager": "manager",
}


def apply_stylesheet(widget, relative_path):
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    theme_path = os.path.join(base_path, relative_path)
    try:
        with open(theme_path, "r") as f:
            widget.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"⚠️ Could not load theme: {theme_path}")

class LoginCreate(QDialog, Ui_Form):
    loginSucceeded = QtCore.pyqtSignal(int, dict)
    accountCreated = QtCore.pyqtSignal(int, dict)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setModal(True)
        dark_theme = "theme/light_theme.qss"
        apply_stylesheet(self, dark_theme)
        self.setFixedSize(661, 437)
        self.create_user_button.clicked.connect(self.show_create_page)
        self.login_tab_button.clicked.connect(self.show_login_page)
        self.cancel_login_button.clicked.connect(self.reject)
        self.cancel_create_button.clicked.connect(self.reject)
        # self.login_button.setDefault(True)
        self.login_button.clicked.connect(self._on_login_clicked)
        # self.save_user_button.setDefault(True)
        self.save_user_button.clicked.connect(self._on_create_clicked)
        self.animate_users_create = QtCore.QPropertyAnimation(self.stackedWidget, b'geometry')
        self.animate_users_create.setDuration(300)
        self.stacked_height = self.stackedWidget.height()
        self.password_line.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_line_2.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_enter()

        ### LOAD USER AND PASS FOR STARTUP IF CHECKED "REMEMBER ME" ###
        settings = QSettings(APP_ORG, APP_NAME)
        saved_user = settings.value("auth/username", "", type=str)
        remember = settings.value("auth/remember", False, type=bool)

        if remember and saved_user:
            self.login_name_line.setText(saved_user)
            try:
                saved_pw = keyring.get_password(KEYRING_SERVICE, saved_user)
                if saved_pw:
                    self.password_line.setText(saved_pw)
                    if hasattr(self, "remember_me"):
                        self.remember_me.setChecked(True)
            except Exception:
                pass

        if saved_user:
            from openauto.repositories.users_repository import UsersRepository
            user = UsersRepository.get_by_username_or_email(saved_user)
            if user:
                theme = UsersRepository.get_theme(user["id"])
                theme_path = {"light": "theme/light_theme.qss", "dark": "theme/dark_theme.qss"}.get(theme,"theme/light_theme.qss")
                apply_stylesheet(self, theme_path)



    ### ANIMATE LOGIN PAGE ###
    def show_login_page(self):
        self.animate_users_create.setStartValue(QtCore.QRect(9, 0, 643, 363))
        self.animate_users_create.setEndValue(QtCore.QRect(9, 73, 643, 363))
        self.animate_users_create.setEasingCurve(QtCore.QEasingCurve.Type.Linear)
        self.animate_users_create.start()

        self.stackedWidget.setCurrentIndex(0)


### ANIMATE CREATE USER PAGE ###
    def show_create_page(self):
        self.animate_users_create.setStartValue(QtCore.QRect(9, 0, 643, 363))
        self.animate_users_create.setEndValue(QtCore.QRect(9, 73, 643, 363))
        self.animate_users_create.setEasingCurve(QtCore.QEasingCurve.Type.Linear)
        self.animate_users_create.start()
        self.stackedWidget.setCurrentIndex(1)


    def _on_login_clicked(self):
        user_or_email = self.login_name_line.text().strip()
        password = self.password_line.text()

        if not user_or_email or not password:
            QtWidgets.QMessageBox.warning(self, "Missing Info", "Enter your username/email and password.")
            return

        user = users_repository.UsersRepository.verify_credentials(user_or_email, password)
        if not user:
            QtWidgets.QMessageBox.critical(self, "Login Failed", "Invalid credentials.")
            return

        if hasattr(self, "remember_me") and self.remember_me.isChecked():
            settings = QSettings(APP_ORG, APP_NAME)
            settings.setValue("auth/remember", True)
            settings.setValue("auth/username", user["username"])
            try:
                keyring.set_password(KEYRING_SERVICE, user["username"], password)
            except Exception:
                pass
        else:
            # Clear saved creds
            settings = QSettings(APP_ORG, APP_NAME)
            last_user = settings.value("auth/username", "", type=str)
            settings.setValue("auth/remember", False)
            if last_user:
                try:
                    keyring.delete_password(KEYRING_SERVICE, last_user)
                except Exception:
                    pass
            settings.remove("auth/username")



        self.loginSucceeded.emit(user["id"], user)
        self.accept()


    def _on_create_clicked(self):
        username = self.username_line.text().strip()
        email = self.email_line.text().strip()
        password = self.password_line_2.text()
        first = self.first_name_line.text().strip()
        last = self.last_name_line.text().strip()
        phone = self.phone_line.text().strip()

        type_label = self.type_selector.currentText()
        if type_label == "TYPE":
            QtWidgets.QMessageBox.warning(self, "Missing Info", "Please select a user type.")
            return
        user_type = TYPE_MAP.get(type_label, "technician")

        if not username or not email or not password:
            QtWidgets.QMessageBox.warning(self, "Missing Info", "Username, email, and password are required.")
            return

        try:
            user_id = users_repository.UsersRepository.create_user(
                username=username,
                email=email,
                password_plain=password,
                user_type=user_type,
                first_name=first,
                last_name=last,
                phone=phone,
            )
        except mysql.connector.Error as e:
            # duplicate usernames/emails will raise here (unique constraints)
            QtWidgets.QMessageBox.critical(self, "Create Failed", f"Could not create user.\n\n{e}")
            return
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Create Failed", f"Unexpected error.\n\n{e}")
            return

        # Optional: immediately log in, or flip back to login page
        user = users_repository.UsersRepository.get_by_username_or_email(username) or {"id": user_id, "username": username}
        self.accountCreated.emit(user_id, user)
        QtWidgets.QMessageBox.information(self, "Success", "Account created. You can now log in.")
        self.show_login_page()


    def login_enter(self):
        if self.stackedWidget.currentIndex() == 0:
            self.login_button.setDefault(True)

        elif self.stackedWidget.currentIndex() == 1:
            self.login_button.setDefault(True)


