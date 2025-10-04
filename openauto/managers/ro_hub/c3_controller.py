from PyQt6 import QtCore, QtWidgets
from typing import Optional
from openauto.repositories.ro_c3_repository import ROC3Repository


### Concern/Cause/Correction editor for one RO ###
class C3Controller(QtCore.QObject):
    def __init__(self, ui, parent = None):
        super().__init__(parent)
        self.ui = ui
        self._ro_id: Optional[int] = None
        self._line_id: Optional[int] = None

        self._stack: Optional[QtWidgets.QStackedWidget] = getattr(ui, "three_c_stacked", None)
        self._edit_concern: Optional[QtWidgets.QTextEdit] = getattr(ui, "concern_edit", None)
        self._edit_cause: Optional[QtWidgets.QTextEdit] = getattr(ui, "cause_edit", None)
        self._edit_correction: Optional[QtWidgets.QTextEdit] = getattr(ui, "correction_edit", None)

        self._button_concern = getattr(ui, "concern_button", None)
        self._button_cause = getattr(ui, "cause_button", None)
        self._button_correction = getattr(ui, "correction_button", None)
        

        if isinstance(self._button_concern, QtWidgets.QAbstractButton):
            self._button_concern.clicked.connect(lambda: self._switch_tab(0))
        if isinstance(self._button_cause, QtWidgets.QAbstractButton):
            self._button_cause.clicked.connect(lambda: self._switch_tab(2))
        if isinstance(self._button_correction, QtWidgets.QAbstractButton):
            self._button_correction.clicked.connect(lambda: self._switch_tab(1))


    # Call whenever an ro is opened/changed
    def set_ro_id(self, ro_id: Optional[int]):
        self._ro_id = ro_id
        self._load_first_line()


    def _switch_tab(self, idx: int):
        if isinstance(self._stack, QtWidgets.QStackedWidget):
            self._stack.setCurrentIndex(idx)

    def _block_text_signals(self, block: bool):
        for ed in (self._edit_concern, self._edit_cause, self._edit_correction):
            if isinstance(ed, QtWidgets.QTextEdit):
                ed.blockSignals(block)

    def _set_edits(self, concern: str, cause: str, correction: str):
        self._block_text_signals(True)
        if isinstance(self._edit_concern, QtWidgets.QTextEdit):
            self._edit_concern.setPlainText(concern or "")
        if isinstance(self._edit_cause, QtWidgets.QTextEdit):
            self._edit_cause.setPlainText(cause or "")
        if isinstance(self._edit_correction, QtWidgets.QTextEdit):
            self._edit_correction.setPlainText(correction or "")
        self._block_text_signals(False)


    # Load (or create on first save) the primary C3 line for this RO
    def _load_first_line(self):
        self._line_id = None
        if not self._ro_id:
            self._set_edits("", "", "")
            return
        rows = ROC3Repository.list_for_ro(int(self._ro_id)) or []
        if rows:
            # Use the first line (lowest line_no) as the primary editor
            r = rows[0]
            self._line_id = int(r["id"])
            self._set_edits(r.get("concern") or "", r.get("cause") or "", r.get("correction") or "")
        else:
            self._set_edits("", "", "")