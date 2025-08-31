from PyQt6.QtWidgets import QApplication
from openauto.ui.home import MainWindow

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()  # Create instance of MainWindow
    window.showMaximized()
    print("Device Pixel Ratio:", app.primaryScreen().devicePixelRatio())
    app.exec()

