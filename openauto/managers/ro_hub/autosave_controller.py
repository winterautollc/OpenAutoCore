from PyQt6 import QtCore, QtWidgets
from openauto.managers.ro_hub.save_estimate_service import SaveEstimateService

class AutosaveController(QtCore.QObject):
    saved = QtCore.pyqtSignal(int)  # emits estimate_id

    def __init__(self, ui, interval_ms: int = 2500):
        super().__init__(ui)
        self.ui = ui
        self._dirty = False
        self._paused = 0
        self._timer = None
        try:
            app = QtWidgets.QApplication.instance()
            if app:
                app.applicationStateChanged.connect(self._on_app_state_changed)
        except Exception:
            pass


    def pause(self):
        self._paused += 1

    def resume(self):
        self._paused = max(0, self._paused - 1)


    def _is_editing_anything(self) -> bool:
        view = getattr(self.ui, "ro_items_table", None)
        if isinstance(view, QtWidgets.QAbstractItemView):
            if view.state() == QtWidgets.QAbstractItemView.State.EditingState:
                return True
            if view.findChild(QtWidgets.QLineEdit) is not None:
                return True
        return False

    def mark_dirty(self):
        self._dirty = True

    def _do_save(self):
        if self._paused > 0 or self._is_editing_anything():
            if self._timer:
                self._timer.start(800)
            return

        if not self._dirty:
            return
        self._dirty = False
        est_id = SaveEstimateService(self.ui).save(silent=True)
        if est_id:
            try:
                self.ui.current_estimate_id = est_id
            except Exception:
                pass
            self.saved.emit(int(est_id))

    def flush_if_dirty(self):
        if not self._dirty:
            return
        self._do_save()

    def enable_debounce(self, interval_ms: int = 2500):
        if self._timer is None:
            self._timer = QtCore.QTimer(self)
            self._timer.setSingleShot(True)
            self._timer.timeout.connect(self._do_save)
        self._timer.setInterval(interval_ms)

    def _on_app_state_changed(self, state):
        try:
            if int(state) != int(QtCore.Qt.ApplicationState.ApplicationActive):
                self.flush_if_dirty()
        except Exception:
            pass