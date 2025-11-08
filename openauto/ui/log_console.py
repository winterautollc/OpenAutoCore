from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtGui import QFont
import re

class LogConsole(QtWidgets.QPlainTextEdit):
    MAX_LINES = 500

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMaximumHeight(800)
        self.setMinimumWidth(0)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        f = QFont("Monospace")
        f.setStyleHint(QFont.StyleHint.TypeWriter)
        self.setFont(f)
        self.setWordWrapMode(QtGui.QTextOption.WrapMode.NoWrap)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._menu)

    def _menu(self, pos):
        m = QtWidgets.QMenu(self)
        m.addAction("Copy All", lambda: QtWidgets.QApplication.clipboard().setText(self.toPlainText()))
        m.addAction("Clear", self.clear)
        m.exec(self.mapToGlobal(pos))

    def append_line(self, text: str):
        if not text:
            return
        t = text

        # last-ditch scrub (UI-side, even though the sidecar already scrubs)
        t = re.sub(r"(-token)\s+\S+", r"\1 [REDACTED]", t, flags=re.I)
        t = re.sub(r"(authorization[:=]\s*)\S+", r"\1[REDACTED]", t, flags=re.I)
        t = re.sub(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b",
                   "[JWT-REDACTED]", t)
        t = re.sub(r"\bsession[_-]?id\s*[:=]\s*\S+", "session_id=[REDACTED]", t, flags=re.I)

        self.appendPlainText(t)

        # cap lines
        doc = self.document()
        while doc.blockCount() > self.MAX_LINES:
            cur = self.textCursor()
            cur.movePosition(QtGui.QTextCursor.MoveOperation.Start)
            cur.select(QtGui.QTextCursor.SelectionType.BlockUnderCursor)
            cur.removeSelectedText()
            cur.deleteChar()