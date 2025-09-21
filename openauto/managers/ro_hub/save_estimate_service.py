from PyQt6.QtWidgets import QMessageBox
from openauto.repositories.repair_orders_repository import RepairOrdersRepository
from openauto.repositories.estimates_repository import EstimatesRepository
from openauto.repositories.estimate_items_repository import EstimateItemsRepository

class SaveEstimateService:
    def __init__(self, ui):
        self.ui = ui

    def _current_ro_id(self):
        return getattr(self.ui, "current_ro_id", None)

    def _collect_ui_items_for_estimate(self, ro_id: int, estimate_id: int) -> list[dict]:
        out: list[dict] = []
        parts_tree = getattr(self.ui, "partsTree", None)
        if parts_tree and hasattr(parts_tree, "iter_rows"):
            for row in parts_tree.iter_rows():
                out.append({
                    "estimate_id": estimate_id, "ro_id": ro_id,
                    "part_number": row.part_number, "description": row.description,
                    "qty": row.qty, "unit_cost": row.unit_cost, "unit_price": row.unit_price,
                    "taxable": 1 if row.taxable else 0, "vendor": row.vendor,
                    "source": "catalog", "metadata": None
                })
        ro_table = getattr(self.ui, "roTable", None)
        if ro_table and hasattr(ro_table, "iter_rows"):
            for row in ro_table.iter_rows():
                out.append({
                    "estimate_id": estimate_id, "ro_id": ro_id,
                    "part_number": None, "description": row.description,
                    "qty": row.hours, "unit_cost": 0.0, "unit_price": row.rate,
                    "taxable": 1 if row.taxable else 0, "vendor": None,
                    "source": "labor", "metadata": None
                })
        return out

    def save(self):
        ro_id = self._current_ro_id()
        if not ro_id:
            QMessageBox.warning(self.ui, "Save RO", "No Repair Order selected.")
            return

        ro = RepairOrdersRepository.get_repair_order_by_id(ro_id)
        writer_name = ro.get("writer_name") or (self.ui.writer_box.currentText() if hasattr(self.ui, "writer_box") else "")
        tech_name   = ro.get("tech_name") or (self.ui.technician_box.currentText() if hasattr(self.ui, "technician_box") else "")

        est = EstimatesRepository.get_by_ro_id(ro_id)
        estimate_id = est["id"] if est else EstimatesRepository.create_for_ro(ro, writer_name, tech_name)

        items = self._collect_ui_items_for_estimate(ro_id, estimate_id)
        for it in items:
            EstimateItemsRepository.insert_item(it)

        total = sum(round(i.get("qty", 1) * i.get("unit_price", 0.0), 2) for i in items)
        EstimatesRepository.update_total(estimate_id, total)

        QMessageBox.information(self.ui, "Save RO", f"Estimate #{estimate_id} saved with {len(items)} items.")
