from PyQt6 import QtWidgets
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QStandardPaths, QCoreApplication
import sys, os

app = QtWidgets.QApplication(QtWidgets.QApplication.instance() and [] or (sys.argv or ["openauto"]))
QCoreApplication.setOrganizationName("WinterAuto LLC")
QCoreApplication.setApplicationName("OpenAuto")

# Long-lived profile (parent it to the app so it outlives pages/views)
profile = QWebEngineProfile("openauto_profile", app)
profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)

base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)  # <-- scoped enum
store = os.path.join(base, "webprofile")
os.makedirs(store, exist_ok=True)
profile.setPersistentStoragePath(store)
profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
profile.setCachePath(os.path.join(store, "httpcache"))


view = QWebEngineView()
page = QWebEnginePage(profile, view)
view.setPage(page)
view.resize(1000, 700)
view.load(QUrl("https://www.advancepro.com/"))
view.show()

sys.exit(app.exec())