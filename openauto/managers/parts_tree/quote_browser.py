from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QSizePolicy
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PyQt6.QtCore import QUrl, pyqtSignal, Qt

class QuoteBrowser(QWidget):
    closedWithSuccess = pyqtSignal()

    def __init__(self, redirect_url: str, return_url: str, parent=None,
                 profile: QWebEngineProfile | None = None):
        super().__init__(parent)
        self._return_url = return_url.rstrip("/")

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._loading = QLabel("Loading…", self)
        self._loading.setStyleSheet("padding:6px; color:#314455;")
        self._loading.setMaximumHeight(50)
        layout.addWidget(self._loading)

        from PyQt6.QtWebEngineWidgets import QWebEngineView
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)
        self.web = QWebEngineView(self)
        self.web.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        page = QWebEnginePage(self.profile, self.web)
        self.web.setPage(page)
        layout.addWidget(self.web, 1, 0)

        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 1)
        layout.setColumnStretch(0, 1)


        try:
            self.web.page().windowCloseRequested.connect(self._emit_done)
        except Exception:
            pass

        self.web.urlChanged.connect(self._on_url_changed)
        self.web.loadStarted.connect(lambda: self._loading.setVisible(True))
        self.web.loadFinished.connect(self._on_load_finished)

        self.web.setUrl(QUrl(redirect_url))

    def _emit_done(self):
        self.closedWithSuccess.emit()

    def _maybe_close_if_done(self, url_str: str):
        if url_str.startswith(self._return_url):
            self.closedWithSuccess.emit()
            return True
        return False

    def _on_url_changed(self, url: QUrl):
        self._maybe_close_if_done(url.toString())

    def _on_load_finished(self, ok: bool):
        self._loading.setVisible(False)
        self._maybe_close_if_done(self.web.url().toString())

    def load(self, redirect_url: str, return_url: str | None = None):
        if return_url:
            self._return_url = return_url.rstrip("/")
        self.web.setUrl(QUrl(redirect_url))