from PyQt6 import QtCore
from openauto.repositories.users_repository import UsersRepository
from openauto.repositories.repair_orders_repository import RepairOrdersRepository

class StaffAssignmentController:
    def __init__(self, ui):
        self.ui = ui

    def populate_and_connect(self):
        self._populate()
        self._connect()

    def _populate(self):
        def _fill(box, rows):
            box.blockSignals(True)
            box.clear()
            box.addItem("Unassigned", None)
            for p in rows:
                name = f"{(p.get('first_name') or '').strip()} {(p.get('last_name') or '').strip()}".strip() or "Unnamed"
                box.addItem(name, p["id"])
            box.setCurrentIndex(0)
            box.blockSignals(False)

        writers = UsersRepository.list_writers_and_managers()
        techs   = UsersRepository.list_by_role("technician")
        _fill(self.ui.writer_box, writers)
        _fill(self.ui.technician_box, techs)

    def _connect(self):
        self.ui.writer_box.currentIndexChanged.connect(self._on_writer_changed)
        self.ui.technician_box.currentIndexChanged.connect(self._on_tech_changed)

    def _current_ro_id(self):
        return getattr(self.ui, "current_ro_id", None)

    def _on_writer_changed(self, _idx: int):
        ro_id = self._current_ro_id()
        if not ro_id:
            return
        writer_id = self.ui.writer_box.currentData(QtCore.Qt.ItemDataRole.UserRole) or None
        RepairOrdersRepository.assign_staff(ro_id, writer_id=writer_id)
        tile = getattr(self.ui, "active_ro_tile", None)
        if tile and hasattr(tile, "set_writer_text"):
            tile.set_writer_text(self.ui.writer_box.currentText())

    def _on_tech_changed(self, _idx: int):
        ro_id = self._current_ro_id()
        if not ro_id:
            return
        tech_id = self.ui.technician_box.currentData(QtCore.Qt.ItemDataRole.UserRole) or None
        RepairOrdersRepository.assign_staff(ro_id, tech_id=tech_id)
        tile = getattr(self.ui, "active_ro_tile", None)
        if tile and hasattr(tile, "set_tech_text"):
            tile.set_tech_text(self.ui.technician_box.currentText())

    def sync_selects_from_ro(self, ro_data: dict):
        def _select_by_id(box, user_id):
            if not user_id:
                box.setCurrentIndex(0); return
            idx = box.findData(user_id, QtCore.Qt.ItemDataRole.UserRole)
            box.setCurrentIndex(idx if idx >= 0 else 0)

        writer_id = ro_data.get("assigned_writer_id") or ro_data.get("created_by") or None
        _select_by_id(self.ui.writer_box, writer_id)
        _select_by_id(self.ui.technician_box, ro_data.get("assigned_tech_id"))
