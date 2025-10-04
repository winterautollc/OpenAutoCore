from PyQt6.QtWidgets import QAbstractItemView
from PyQt6 import QtCore


MANAGER_ONLY = [
    "analytics_button",
    "matrix_frame", "matrix_table",
    "add_row_button", "remove_row_button", "save_matrix_button",
    "labor_table", "add_labor_row", "remove_labor_row", "save_labor_button",
    "warranty_miles_checkbox", "warranty_miles_line",
    "warranty_time_checkbox", "warranty_time_line",
    "shop_name_line", "facility_id_line", "address_line", "city_line",
    "state_line", "zipcode_line", "disclamer_edit",
    "import_logo_button", "save_settings_button",
    "users_button", "parts_integrate_button", "quickbooks_button",
]

class PermissionsManager:
    def __init__(self, ui):
        self.ui = ui
        self.user_type = None

    def apply(self, user_type: str | None):
        self.user_type = user_type
        is_manager = (self.user_type == "manager")
        if self.user_type == "technician":
            tech_permissions = ["customers_button", "vehicles_button", "messaging_button"]
            self.ui.hourly_schedule_table.cellClicked.disconnect()
            self.ui.weekly_schedule_table.cellClicked.disconnect()
            self.ui.hourly_schedule_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
            self.ui.weekly_schedule_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
            self.ui.hourly_schedule_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.ui.weekly_schedule_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.ui.hourly_schedule_table.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
            self.ui.weekly_schedule_table.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
            MANAGER_ONLY.extend(tech_permissions)

        self._set_group_enabled(MANAGER_ONLY, is_manager)
        self._set_group_tooltip(MANAGER_ONLY, "Managers only" if not is_manager else None)





    # --- helpers ---
    def _set_group_enabled(self, names: list[str], enabled: bool):
        for name in names:
            w = getattr(self.ui, name, None)
            if w is not None:
                w.setEnabled(enabled)

    def _set_group_tooltip(self, names: list[str], tip: str | None):
        for name in names:
            w = getattr(self.ui, name, None)
            if w is not None:
                w.setToolTip(tip or "")
