from PyQt6 import QtWidgets, QtCore, QtGui
from typing import Callable, Optional
from openauto.repositories.repair_orders_repository import RepairOrdersRepository
from openauto.repositories.estimate_jobs_repository import EstimateJobsRepository
from openauto.subclassed_widgets.ro_tree.roles import APPROVED_ROLE, DECLINED_ROLE


class StatusDialogController:
    ACTIONS = [
        ("Approve All Jobs", "approved"),
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


        self.ui = ui
        self._get_status = get_current_status
        self._get_ro_id = get_current_ro_id
        self._persist = persist

    def attach(self, button: QtWidgets.QPushButton):
        button.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        button.clicked.connect(lambda: self._show_menu(button))  # left-click
        button.customContextMenuRequested.connect(  # right-click
            lambda p: self._show_menu(button, p)
        )

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


        self.ui.ro_hub_manager._update_ro_status_label(ro_id)



    def _show_menu(self, anchor: QtWidgets.QWidget, local_pos: QtCore.QPoint | None = None):
        cur = self._normalize_status(self._get_status())
        menu = QtWidgets.QMenu(anchor)

        for label, code in self.ACTIONS:
            if code == cur:
                continue  # mirror ROTile behavior: omit current status
            act = menu.addAction(label)
            act.triggered.connect(lambda _=False, s=code: self.apply_status(s))

        global_pt = (anchor.mapToGlobal(local_pos)
                     if isinstance(local_pos, QtCore.QPoint)
                     else anchor.mapToGlobal(anchor.rect().center()))
        menu.exec(global_pt)

    @staticmethod
    def _normalize_status(text: str) -> str:
        t = (text or "").strip().lower()
        for code in ("open", "approved", "working", "checkout", "archived"):
            if code in t:
                return code
        return "open"

    def open_ro_status(self, event: QtGui.QContextMenuEvent):
        menu = QtWidgets.QMenu(self.ui)

        actions = [
            ("Move to Approved", "approved"),
            ("Move to Working", "working"),
            ("Move to Checkout", "checkout"),
            ("Revert to Estimate", "open"),
            ("Archive", "archived"),
        ]

        for label, target_status in actions:
            menu.addAction(label)

        menu.exec(event.globalPos())

    def cancel_ro_changes(self):
        message_box = QtWidgets.QMessageBox(self.ui)
        message_box.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        message_box.setWindowTitle("Cancel Changes")
        message_box.setText("Cancel and discard unsaved changes.\n\nAre you sure?")
        message_box.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        message_box.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if message_box.exec() == QtWidgets.QMessageBox.StandardButton.Yes:
            self.ui.animations_manager.show_repair_orders()
