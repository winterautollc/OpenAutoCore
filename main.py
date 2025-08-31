from PyQt6.QtWidgets import QApplication
from openauto.ui.home import MainWindow
import os, platform
from PyQt6 import QtCore, QtGui

### FORCE XWAYLAND IF USING LINUX ###
if platform.system() == "Linux" and os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland":
    os.environ["QT_QPA_PLATFORM"] = "xcb"

try:
    QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_UseDesktopOpenGL, True)
    fmt = QtGui.QSurfaceFormat()
    fmt.setSwapBehavior(QtGui.QSurfaceFormat.SwapBehavior.DoubleBuffer)
    fmt.setSwapInterval(1)
    QtGui.QSurfaceFormat.setDefaultFormat(fmt)
except Exception as e:
    print("OpenGL setup failed, falling back:", e)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    QtCore.QTimer.singleShot(1, window.showMaximized)
    app.exec()

