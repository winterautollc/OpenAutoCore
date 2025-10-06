from PyQt6 import QtWidgets, QtCore
from openauto.subclassed_widgets.roles.tree_roles import COL_DESC
from openauto.repositories.settings_repository import SettingsRepository

def _skip_during_drop(table) -> bool:
    try:
        return getattr(table, "_dropping", False) or table.signalsBlocked()
    except Exception:
        return False

class ItemEntryController:
    def __init__(self, ui):
        self.ui = ui
        self.ui.type_box.clear()
        self._pricing_matrix = self._load_pricing_matrix()


    def _load_pricing_matrix(self):
        rows = SettingsRepository.load_matrix_table() or []
        matrix = []
        for min_cost, max_cost, multiplier, percent_return in rows:
            try:
                min_v = float(min_cost) if min_cost is not None else 0.0
                max_v = float(max_cost) if max_cost is not None else float("inf")
                mult  = float(multiplier) if multiplier is not None else 1.0
            except Exception:
                continue
            matrix.append({
                "min": min_v, "max": max_v, "mult": mult,
                "percent_return": float(percent_return) if percent_return is not None else None
            })
        matrix.sort(key=lambda r: r["min"])
        return matrix



    def _matrix_price_for_cost(self, cost: float) -> float | None:
        if cost is None:
            return None
        for r in self._pricing_matrix:
            if r["min"] <= cost <= r["max"]:
                return round(cost * r["mult"], 2)
        # If no bracket matched, option to choose last one.
        return None


### Auto-fill sell_edit based on Pricing Matrix for Part/Tire only ###
    def recalculate_sell_from_matrix(self):
        kind = (self.ui.type_box.currentText() or "").strip().lower()
        if kind not in ("part", "tire"):
            return  

        # parse cost
        cost_raw = (self.ui.cost_edit.text() or "").strip().replace("$", "").replace(",", "")
        try:
            cost_val = float(cost_raw) if cost_raw else None
        except ValueError:
            cost_val = None

        price = self._matrix_price_for_cost(cost_val) if cost_val is not None else None
        if price is not None:
            # Don’t fight the user if they already typed a price—only set when blank or cost changed.
            self.ui.sell_edit.setText(f"{price:.2f}")  



    def type_options(self):
        return ["Part", "Labor", "Fee", "Sublet", "Tire"]

    def adjust_item_lines(self):
        kind = (self.ui.type_box.currentText() or "").strip().lower()
        w = self.ui

        for e in (w.sku_edit, w.description_edit, w.cost_edit, w.sell_edit, w.quantity_edit):
            e.setVisible(True)
            e.setPlaceholderText("")

        w.tax_box.setVisible(True)
        w.labor_rate_box.setVisible(False)

        if kind == "labor":
            w.sku_edit.hide()
            w.cost_edit.hide()
            w.sell_edit.hide()
            w.labor_rate_box.setVisible(True)
            w.description_edit.setPlaceholderText("Description …")
            w.quantity_edit.setPlaceholderText("Hours")
        elif kind in ("fee", "sublet"):
            w.labor_rate_box.hide()
            w.sku_edit.setPlaceholderText("Op Code ...")
            w.cost_edit.setPlaceholderText("Cost ...")
            w.description_edit.setPlaceholderText("Description …")
            w.quantity_edit.setPlaceholderText("Qty")
            w.sell_edit.setPlaceholderText("Amount")
        else:
            w.labor_rate_box.hide()
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
        item = getattr(t, "currentItem", lambda: None)()
        job = None
        if item:
            job = item if (getattr(item, "parent", lambda: None)() is None) else item.parent()
        if job is None and hasattr(t, "topLevelItemCount") and t.topLevelItemCount() > 0:
            job = t.topLevelItem(0)
        if job is None and hasattr(t, "addJob"):
            job = t.addJob("New Job")
        if job is not None and hasattr(t, "expandItem"):
            t.expandItem(job)
        return job
    

    @staticmethod
    def _parse_money(text: str):
        t = (text or "").strip().replace(",", "").replace("$", "").replace("%", "")
        if not t:
            return None
        try:
            return float(t)
        except ValueError:
            return None
        


    def _combo_text(self, box: QtWidgets.QComboBox) -> str:
        if box.isEditable() and box.lineEdit() is not None:
            return box.lineEdit().text()
        return box.currentText()
    
    ### Prefer stored value from db, else parse text from user ###
    def _combo_value(self, box: QtWidgets.QComboBox):
        data = box.currentData(QtCore.Qt.ItemDataRole.UserRole)
        if data is not None:
            return data
        return self._parse_money(self._combo_text(box))

    def add_item(self):
        try:
            sku  = self.ui.sku_edit.text().strip()
            desc = self.ui.description_edit.text().strip()
            cost_text = self.ui.cost_edit.text().strip()
            sell_text = self.ui.sell_edit.text().strip()
            qty_text  = self.ui.quantity_edit.text()
            kind = (self.ui.type_box.currentText() or "Part").strip().lower()
            tax_val = self._combo_value(self.ui.tax_box) or 0.0

            self._ensure_ro_table_configured()
        except Exception:
            self.ui.add_job_item_button.setToolTip("Please make sure all fields exist for this input row.")
            return

        # Validate by kind
        if kind == "labor":
            labor_rate_val = self._combo_value(self.ui.labor_rate_box)
            if not desc or labor_rate_val is None:
                QtWidgets.QToolTip.showText(
                    self.ui.add_job_item_button.mapToGlobal(self.ui.add_job_item_button.rect().center()),
                    "For Labor, fill Description and select a Labor Rate."
                )
                return
        elif kind in ("fee", "sublet"):
            if not desc or not sell_text:
                QtWidgets.QToolTip.showText(
                    self.ui.add_job_item_button.mapToGlobal(self.ui.add_job_item_button.rect().center()),
                    "For Fee/Sublet, fill Description and Amount."
                )
                return
        else:
            # part/tire
            # if user didn’t provide sell_text, matrix handler (wired to cost_edit) likely filled it
            if not desc:
                QtWidgets.QToolTip.showText(
                    self.ui.add_job_item_button.mapToGlobal(self.ui.add_job_item_button.rect().center()),
                    "Fill Description"
                )
                return

        cost = self._parse_money(cost_text) or 0.0
        t = self.ui.ro_items_table
        job = self._get_or_create_job()
        if job is None:
            QtWidgets.QToolTip.showText(
                self.ui.add_job_item_button.mapToGlobal(self.ui.add_job_item_button.rect().center()),
                "Could not create/find a job header."
            )
            return


        if kind == "labor":
            hours_text = qty_text or "0"
            rate_val = self._combo_value(self.ui.labor_rate_box)
            row = t.addLabor(job_item=job,
                             description=desc or "Labor",
                             hours=hours_text,
                             rate=f"{float(rate_val):.2f}",
                             tax_pct=float(tax_val or 0.0),
                             sku=sku or ""
                             )
        elif kind == "part":
            # compute final sell: prefer user entry, else matrix suggestion
            sell = self._parse_money(sell_text)
            if sell is None and kind in ("part"):
                # last-chance compute from matrix
                computed = self._matrix_price_for_cost(cost)
                if computed is not None:
                    sell = computed
            if sell is None:
                QtWidgets.QToolTip.showText(
                    self.ui.add_job_item_button.mapToGlobal(self.ui.add_job_item_button.rect().center()),
                    "Sell must be a number."
                )
                return

            row = t.addPart(job_item=job,
                            description=desc or "New Part",
                            qty=qty_text,
                            unit_cost=f"{float(cost):.2f}",
                            unit_price=f"{float(sell):.2f}",
                            tax_pct=float(tax_val or 0.0),
                            sku=sku or ""
                            )
            
        elif kind == "sublet":
            sell = self._parse_money(sell_text)
            if sell is None and kind in ("sublet"):
                computed = self._matrix_price_for_cost(cost)
                if computed is not None:
                    sell = computed
            if sell is None:
                QtWidgets.QToolTip.showText(
                    self.ui.add_job_item_button.mapToGlobal(self.ui.add_job_item_button.rect().center()),
                    "Sell must be a number."
                )
                return

            row = t.addSublet(job_item=job,
                            description=desc or "New Part",
                            qty=qty_text,
                            unit_cost=f"{float(cost):.2f}",
                            unit_price=f"{float(sell):.2f}",
                            tax_pct=float(tax_val or 0.0),
                            sku=sku or ""
                            )    

        elif kind == "fee":
            sell = self._parse_money(sell_text)
            if sell is None and kind in ("fee"):
                computed = self._matrix_price_for_cost(cost)
                if computed is not None:
                    sell = computed
            if sell is None:
                QtWidgets.QToolTip.showText(
                    self.ui.add_job_item_button.mapToGlobal(self.ui.add_job_item_button.rect().center()),
                    "Sell must be a number."
                )
                return

            row = t.addFee(job_item=job,
                            description=desc or "New Part",
                            qty=qty_text,
                            unit_cost=f"{float(cost):.2f}",
                            unit_price=f"{float(sell):.2f}",
                            tax_pct=float(tax_val or 0.0),
                            sku=sku or ""
                            )   

    
        elif kind == "tire":
            sell = self._parse_money(sell_text)
            if sell is None and kind in ("tire"):
                computed = self._matrix_price_for_cost(cost)
                if computed is not None:
                    sell = computed
            if sell is None:
                QtWidgets.QToolTip.showText(
                    self.ui.add_job_item_button.mapToGlobal(self.ui.add_job_item_button.rect().center()),
                    "Sell must be a number."
                )
                return

            row = t.addTire(job_item=job,
                            description=desc or "New Part",
                            qty=qty_text,
                            unit_cost=f"{float(cost):.2f}",
                            unit_price=f"{float(sell):.2f}",
                            tax_pct=float(tax_val or 0.0),
                            sku=sku or ""
                            )  

        # Attach extra metadata
        row.setData(COL_DESC, QtCore.Qt.ItemDataRole.UserRole, {
            "sku": sku or "",
            "cost": float(cost or 0.0),
            "tax": float(tax_val or 0.0),
            "kind": kind,
        })

        # Reset inputs
        self.ui.sku_edit.clear()
        self.ui.description_edit.clear()
        self.ui.cost_edit.clear()
        self.ui.sell_edit.clear()
        self.ui.quantity_edit.clear()

        if self.ui.tax_box.count() > 0:
            self.ui.tax_box.setCurrentIndex(0)
        if self.ui.labor_rate_box.count() > 0:
            self.ui.labor_rate_box.setCurrentIndex(0)

        self.ui.sku_edit.setFocus()

    def remove_selected_item(self):
        t = self.ui.ro_items_table
        # QTreeWidget path (legacy)
        if isinstance(t, QtWidgets.QTreeWidget):
            deleter = getattr(t, "_deleteSelected", None)
            if callable(deleter):
                deleter()
            return
        # Model/View path
        deleter = getattr(t, "_deleteSelected", None)
        if callable(deleter):
            deleter()

