from PyQt6 import QtWidgets, QtCore

class ItemEntryController:
    def __init__(self, ui):
        self.ui = ui

    def type_options(self):
        return ["Part", "Labor", "Fee", "Sublet"]

    def adjust_item_lines(self):
        kind = (self.ui.type_box.currentText() or "").strip().lower()
        w = self.ui

        for e in (w.sku_edit, w.description_edit, w.cost_edit, w.sell_edit, w.quantity_edit, w.tax_edit):
            e.setVisible(True); e.setPlaceholderText("")

        if kind == "labor":
            w.sku_edit.hide()
            w.cost_edit.hide()
            w.description_edit.setPlaceholderText("Description")
            w.quantity_edit.setPlaceholderText("Hours")
            w.sell_edit.setPlaceholderText("Labor Rate")
            w.tax_edit.setText(f" {str(getattr(self.ui, 'tax_rate', ''))}%")
        elif kind in ("fee", "sublet"):
            w.sku_edit.hide()
            w.cost_edit.hide()
            w.quantity_edit.setPlaceholderText("Qty")
            w.sell_edit.setPlaceholderText("Amount")
            w.tax_edit.setPlaceholderText("Tax (opt)")
        else:
            w.sku_edit.setPlaceholderText("Part # …")
            w.description_edit.setPlaceholderText("Description …")
            w.cost_edit.setPlaceholderText("Cost …")
            w.sell_edit.setPlaceholderText("Sell Price …")
            w.quantity_edit.setPlaceholderText("Qty …")

    def _ensure_ro_table_configured(self):
        t = self.ui.ro_items_table
        if isinstance(t, QtWidgets.QTreeWidget) and t.topLevelItemCount() == 0:
            t.addJob("New Job")

    def _get_or_create_job(self):
        t = self.ui.ro_items_table
        item = t.currentItem()
        job = None
        if item:
            job = item if (item.parent() is None and item.text(0) == "JOB") else item.parent()
        if job is None and t.topLevelItemCount() > 0:
            job = t.topLevelItem(0)
        if job is None:
            job = t.addJob("New Job")
        t.expandItem(job)
        return job

    @staticmethod
    def _parse_money(text: str):
        t = (text or "").strip().replace(",", "")
        if not t:
            return None
        try:
            return float(t)
        except ValueError:
            return None

    def add_item(self):
        self._ensure_ro_table_configured()
        try:
            sku = self.ui.sku_edit.text().strip()
            desc = self.ui.description_edit.text().strip()
            cost_text = self.ui.cost_edit.text().strip()
            sell_text = self.ui.sell_edit.text().strip()
            tax_text = self.ui.tax_edit.text().strip()
            qty_text = self.ui.quantity_edit.text.strip()
        except Exception:
            self.ui.add_job_item_button.setToolTip("Please Fill All Fields")
            return

        if not all([desc, sell_text]):
            QtWidgets.QToolTip.showText(
                self.ui.add_job_item_button.mapToGlobal(self.ui.add_job_item_button.rect().center()),
                "Fill at least Description and Sell."
            )
            return

        cost = self._parse_money(cost_text) if cost_text else 0.0
        sell = self._parse_money(sell_text)
        tax  = self._parse_money(tax_text) if tax_text else 0.0
        if sell is None:
            QtWidgets.QToolTip.showText(
                self.ui.add_job_item_button.mapToGlobal(self.ui.add_job_item_button.rect().center()),
                "Sell must be a number."
            )
            return

        t = self.ui.ro_items_table
        job = self._get_or_create_job()

        kind = (self.ui.type_box.currentText() or "Part").strip().lower()
        desc_full = f"{sku} - {desc}" if (sku and kind in ("part", "fee", "sublet")) else desc

        if kind == "labor":
            row = t.addLabor(jobItem=job, desc=desc_full or "Labor", hours=qty_text, rate=f"{sell:.2f}")
        else:
            row = t.addPart(jobItem=job, desc=desc_full or "New Part", qty="1", unit_price=f"{sell:.2f}")

        row.setData(0, QtCore.Qt.ItemDataRole.UserRole, {
            "sku": sku or "",
            "cost": float(cost or 0.0),
            "tax": float(tax or 0.0),
            "kind": kind
        })

        self.ui.sku_edit.clear()
        self.ui.description_edit.clear()
        self.ui.cost_edit.clear()
        self.ui.sell_edit.clear()
        self.ui.tax_edit.clear()
        self.ui.sku_edit.setFocus()

    def remove_selected_item(self):
        t = self.ui.ro_items_table
        if isinstance(t, QtWidgets.QTreeWidget):
            deleter = getattr(t, "_deleteSelected", None)
            if callable(deleter):
                deleter()
            return
        row = t.currentRow()
        if row != -1:
            t.removeRow(row)
