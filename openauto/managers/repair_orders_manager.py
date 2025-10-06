from PyQt6 import QtWidgets, QtCore
from openauto.subclassed_widgets.views import ro_tiles
from openauto.repositories.repair_orders_repository import RepairOrdersRepository
from openauto.managers.estimate_options_manager import EstimateOptionsManager
from mysql.connector import Error as MySQLError

from functools import partial



class RepairOrdersManager:
    def __init__(self, ui):
        self.ui = ui
        # self.refresh_all()

    def refresh_all(self):
        self.update_tiles(self.ui.estimate_tiles, "open")
        self.update_tiles(self.ui.approved_tiles, "approved")
        self.update_tiles(self.ui.working_tiles,  "working")
        self.update_tiles(self.ui.checkout_tiles, "checkout")

    def update_tiles(self, container, status):
        container.clear()
        rows = RepairOrdersRepository.load_repair_orders(status=status, limit=200, offset=0)

        for (ro_id, ro_number, created_at, customer_name, year, make, model, tech, writer, total) in rows:
            vehicle = f"{year} {make} {model}".strip()
            tile = ro_tiles.ROTile(
                ro_id=ro_id,
                ro_number=ro_number,
                customer_name=customer_name or "Unknown",
                vehicle=vehicle or "Unknown",
                tech=tech or "Unassigned",
                writer=writer or "Unassigned",
                concern="No concern entered",
                status=status,
                page_context="estimates",
            )
            tile.clicked.connect(partial(self._open_estimate_options, ro_id))
            tile.statusChangeRequested.connect(self._on_status_change_requested)
            container.add_tile(tile)


    def _open_estimate_options(self, ro_id: int):
        self.estimate_options_manager = EstimateOptionsManager(
            parent=self.ui,
            estimate_id=ro_id,
            )


    def _on_status_change_requested(self, ro_id: int, new_status: str):
        try:
            RepairOrdersRepository.update_status(ro_id, new_status)
        except (ValueError, MySQLError) as e:
            QtWidgets.QMessageBox.critical(self.ui, "Status Update Failed", str(e))
        finally:
            self.refresh_all()
