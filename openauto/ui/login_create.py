from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6 import QtCore
from openauto.ui.login_create_form import Ui_Form


class LoginCreate(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.create_user_button.clicked.connect(self.create_page)
        self.login_tab_button.clicked.connect(self.login_page)
        self.animate_users_create = QtCore.QPropertyAnimation(self.stackedWidget, b'geometry')
        self.animate_users_create.setDuration(300)
        self.stacked_height = self.stackedWidget.height()



    def login_page(self):
        self.animate_users_create.setStartValue(QtCore.QRect(9, 0, 990, 648))
        self.animate_users_create.setEndValue(QtCore.QRect(9, 73, 990, 648))
        self.animate_users_create.setEasingCurve(QtCore.QEasingCurve.Type.Linear)
        self.animate_users_create.start()

        self.stackedWidget.setCurrentIndex(0)

    def create_page(self):
        self.animate_users_create.setStartValue(QtCore.QRect(9, 0, 990, 648))
        self.animate_users_create.setEndValue(QtCore.QRect(9, 73, 990, 648))
        self.animate_users_create.setEasingCurve(QtCore.QEasingCurve.Type.Linear)
        self.animate_users_create.start()
        self.stackedWidget.setCurrentIndex(1)




if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = LoginCreate()
    window.show()
    app.exec()