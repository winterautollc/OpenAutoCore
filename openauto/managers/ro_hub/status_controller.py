from PyQt6 import QtWidgets, QtCore, QtGui
from typing import Callable, Optional
from openauto.repositories.repair_orders_repository import RepairOrdersRepository
from openauto.repositories.estimate_jobs_repository import EstimateJobsRepository
from openauto.subclassed_widgets.roles.tree_roles import APPROVED_ROLE, DECLINED_ROLE

TRANSITIONS = {
    "open": {"working"},
    "approved": {"working"},
    "working": {"checkout", "open"},
    "checkout": {"open", "archived"},
    "archived": {"open"},
}

class StatusDialogController(QtCore.QObject):
    statusChanged = QtCore.pyqtSignal(int, str)  # (ro_id, status_code)

    ACTIONS = [
       ("Move to Working",  "working"),
        ("Move to Checkout", "checkout"),
        ("Revert to Estimate","open"),
        ("Archive",          "archived"),
    ]
    NAME_MAP = {
        "open": "open_label",
        "approved": "approved_label",
        "working": "working_label",
        "checkout": "checkout_label",
        "archived": "archived_label",
    }


    def __init__(self, ui, *,
        get_current_status: Callable[[], str],
        get_current_ro_id: Callable[[], Optional[int]] = lambda: None,
        persist: Optional[Callable[[int, str], None]] = None,):

        super().__init__(ui)
        self.ui = ui
        self._get_status = get_current_status
        self._get_ro_id = get_current_ro_id
        self._persist = persist

    def attach(self, button: QtWidgets.QPushButton):
        self._button = button
        button.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        try:
            button.clicked.disconnect()
        except Exception:
            pass
        button.clicked.connect(lambda: self._maybe_show_menu(button))
        try:
            button.customContextMenuRequested.disconnect()
        except Exception:
            pass
        button.customContextMenuRequested.connect(lambda p: self._maybe_show_menu(button, p))
        self.refresh_button()

    def _any_jobs_approved(self, ro_id: Optional[int]) -> bool:
        if not ro_id:
            return False
        try:
            _total, approved, _declined = RepairOrdersRepository.jobs_counts_for_ro(ro_id)
            return bool(approved)
        except Exception:
            return False

    def refresh_button(self):
        btn = getattr(self, "_button", None)
        if not btn:
            return
        try:
            ro_id = self._get_ro_id()
        except Exception:
            ro_id = getattr(self, "ro_id", None)
        has_approved = self._any_jobs_approved(ro_id)
        if not has_approved:
            btn.setProperty("inactive", True)
            btn.setAutoDefault(False)
            btn.setDefault(False)
        else:
            btn.setProperty("inactive", False)
            btn.setToolTip("")

        s = self.ui.style()
        s.unpolish(btn)
        s.polish(btn)

    def _maybe_show_menu(self, anchor: QtWidgets.QWidget, local_pos: QtCore.QPoint | None = None):
        try:
            ro_id = self._get_ro_id()
        except Exception:
            ro_id = getattr(self, "ro_id", None)

        if not self._any_jobs_approved(ro_id):
            try:
                font = QtGui.QFont()
                font.setPointSize(14)
                QtWidgets.QToolTip.setFont(font)
                global_pt = (
                    anchor.mapToGlobal(local_pos) if isinstance(local_pos, QtCore.QPoint) else QtGui.QCursor.pos()
                )

                QtWidgets.QToolTip.showText(
                    global_pt,
                    "Mark Jobs Approved First",
                    anchor,
                    anchor.rect(),
                    3500 #msec
                )
            except  Exception:
                pass
            return
        self._show_menu(anchor, local_pos)

    def apply_status(self, status_code: str):
        status_code = (status_code or "open").strip().lower()
        if status_code not in ("open", "working", "checkout", "archived"):
            QtWidgets.QMessageBox.warning(self.ui, "Invalid Status",
                                f"Unknown status: {status_code}")
            return

        # Identify current RO
        try:
            ro_id = self._get_ro_id()
        except Exception:
            # Fallback if you keep it elsewhere
            ro_id = getattr(self, "ro_id", None)
        if not ro_id:
            QtWidgets.QMessageBox.warning(self.ui, "No Repair Order",
                                "No active Repair Order is loaded.")
            return

        # Capture previous status (for rollback on error)
        try:
            prev_status = (RepairOrdersRepository.get_status(ro_id) or "open").strip().lower()
        except Exception:
            prev_status = "open"

        # --- Optimistic UI update (instant feedback) ---
        lbl = self.ui.ro_status_label
        name = self.NAME_MAP.get(status_code, "open_label")
        lbl.setObjectName(name)
        lbl.setText(status_code.upper())
        s = self.ui.style()
        s.unpolish(lbl)
        s.polish(lbl)

        # --- Persist to DB ---
        try:
            RepairOrdersRepository.update_status(ro_id, status_code)
            if status_code == "open":
                try:
                    est = RepairOrdersRepository.estimate_id_for_ro(ro_id)
                    EstimateJobsRepository.set_all_status_for_estimate(est, "proposed")

                    tree = self.ui.ro_hub_manager.ui.ro_items_table
                    model = tree.model()
                    root = QtCore.QModelIndex()
                    for r in range(model.rowCount(root)):
                        idx = model.index(r, 0, root)
                        model.setData(idx, False, APPROVED_ROLE)
                        if DECLINED_ROLE:
                            model.setData(idx, False, DECLINED_ROLE)
                except Exception:
                     print("didnt work")
        except Exception as e:
            # Roll back optimistic UI on failure
            rollback_name = self.NAME_MAP.get(prev_status, "open_label")
            lbl.setObjectName(rollback_name)
            lbl.setText(prev_status.upper())
            s.unpolish(lbl)
            s.polish(lbl)

            QtWidgets.QMessageBox.critical(self.ui, "Couldn’t Change Status",
                                 f"Database error while saving status:\n{e}")
            return

        try:
            ro_id = self._get_ro_id()
        except Exception:
            ro_id = getattr(self, "ro_id", None)


        self.ui.ro_hub_manager._update_ro_status_label(ro_id)
        self.statusChanged.emit(ro_id, status_code)

    def _resolve_current_status(self) -> str:
        try:
            ro_id = self._get_ro_id() or 0
            if ro_id:
                db = RepairOrdersRepository.get_status(int(ro_id))
                s = self._normalize_status(db)
                if s:
                    return s.strip().lower()
        except Exception:
            pass
        try:
            return self._normalize_status(self._get_status())
        except Exception:
            return "open"

    def _show_menu(self, anchor: QtWidgets.QWidget, local_pos: QtCore.QPoint | None = None):
        cur = self._resolve_current_status()
        allowed = TRANSITIONS.get(cur, set())
        menu = QtWidgets.QMenu(anchor)

        for label, code in self.ACTIONS:
            if code == cur:  # hide the current status (your main ask)
                continue
            if code not in allowed:  # hide invalid transitions
                continue
            act = menu.addAction(label)
            act.triggered.connect(lambda _=False, s=code: self.apply_status(s))

        pt = anchor.mapToGlobal(local_pos) if isinstance(local_pos, QtCore.QPoint) \
            else anchor.mapToGlobal(anchor.rect().center())
        menu.exec(pt)

    @staticmethod
    def _normalize_status(value) -> str:
        t = str(value or "").strip().lower()
        for code in ("open", "approved", "working", "checkout", "archived"):
            if t == code or code in t:
                return code
        return "open"

    def cancel_ro_changes(self):
        self.ui.animations_manager.show_repair_orders()
