from PyQt6.QtWidgets import QApplication
from openauto.ui.home import MainWindow
import os
from PyQt6 import QtCore



if __name__ == "__main__":
    if os.environ.get("XDG_SESSION_TYPE") == "wayland":
        os.environ["QT_QPA_PLATFORM"] = "xcb"
    app = QApplication([])
    window = MainWindow()
    window.show()
    QtCore.QTimer.singleShot(0, window.showMaximized)
    print("Device Pixel Ratio:", app.primaryScreen().devicePixelRatio())
    app.exec()

