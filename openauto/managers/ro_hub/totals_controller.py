from PyQt6 import QtCore
from decimal import Decimal
from openauto.subclassed_widgets.ro_tree.roles import (
    ROW_KIND_ROLE, COL_QTY, COL_SELL, COL_HOURS, COL_RATE, COL_TAX, COL_TOTAL, DECLINED_ROLE
)


### This class watches the ROTree and updates all of the "total" labels:
    # parts, labor, tires, fees, sublet, subtotal, shop_supplies, tax, total
class TotalsController(QtCore.QObject):
    def __init__(self, ui, parent = None):
        super().__init__(parent)
        self.ui = ui
        self._shop_supplies_pct = Decimal("0.00")

    # connect to ROTreeView
    def attach(self, view):
        self._view = view
        self._debounce_timer = QtCore.QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(0)

        if view.model():
            self._hook_model(view.model())


        if hasattr(view, "modelAttached"):
            view.modelAttached.connect(self._hook_model)

    def _hook_model(self, model):
    # avoid duplicate connections if setModel is called more than once
        try:
            model.totalsChanged.disconnect(self._recompute_and_render_totals_debounced)
        except Exception:
            pass
        try:
            model.dataChanged.disconnect(self._recompute_and_render_totals_debounced)
            model.rowsInserted.disconnect(self._recompute_and_render_totals_debounced)
            model.rowsRemoved.disconnect(self._recompute_and_render_totals_debounced)
            model.modelReset.disconnect(self._recompute_and_render_totals_debounced)
        except Exception:
            pass

        if hasattr(model, "totalsChanged"):
            model.totalsChanged.connect(self._recompute_and_render_totals_debounced)
        model.dataChanged.connect(self._recompute_and_render_totals_debounced)
        model.rowsInserted.connect(self._recompute_and_render_totals_debounced)
        model.rowsRemoved.connect(self._recompute_and_render_totals_debounced)
        model.modelReset.connect(self._recompute_and_render_totals_debounced)


    ### monitors real time changes in estimate and labels reflect changes
    def _recompute_and_render_totals_debounced(self, *args):
        self._debounce_timer.timeout.disconnect() if self._debounce_timer.receivers(self._debounce_timer.timeout) else None
        self._debounce_timer.timeout.connect(self._recompute_and_render_totals)
        self._debounce_timer.start()

    def _recompute_and_render_totals(self, *args):
        view = self.ui.ro_items_table
        model = view.model()
        if not model:
            return

        decimal = Decimal

        def d(v):
            try:
                if v in (None, ""): 
                    return decimal("0")
                return decimal(str(v))
            except Exception:
                return decimal("0")
            
        parts = decimal("0"); labor = decimal("0"); tires = decimal("0"); fees = decimal("0"); sublet = decimal("0")
        subtotal = decimal("0")

        tax_total = decimal("0")
        grand_total = decimal("0")

        root = QtCore.QModelIndex()
        jobs = model.rowCount(root)

        for r in range(jobs):
            job_idx = model.index(r, 0, root)

            job_declined = bool(model.data(job_idx, DECLINED_ROLE) or False)

            if job_declined:
                continue

            for i in range(model.rowCount(job_idx)):
                line_idx = model.index(i, 0, job_idx)
                kind = (line_idx.data(ROW_KIND_ROLE) or line_idx.data() or "").strip().lower()
                if kind in ("job", "subtotal") or not kind:
                    continue

                line_declined = bool(model.data(line_idx, DECLINED_ROLE) or False) # If Approve or Decline is ever implemented for single items

                if line_declined:
                    continue

                qty     = d(model.index(i, COL_QTY, job_idx).data())
                sell    = d(model.index(i, COL_SELL, job_idx).data())
                hours   = d(model.index(i, COL_HOURS, job_idx).data())
                rate    = d(model.index(i, COL_RATE, job_idx).data())
                # tax_pct = d(model.index(i, COL_TAX, job_idx).data()) # If needed in the future
                line_total = d(model.index(i, COL_TOTAL, job_idx).data())


                base = (hours * rate) if kind == "labor" else (qty * sell)

                tax_part = line_total - base
                if tax_part < decimal("0"):
                    tax_part = decimal("0")

                if kind == "part":
                    parts += base
                elif kind == "tire":
                    tires += base
                elif kind == "fee":
                    fees += base
                elif kind == "sublet":
                    sublet += base
                elif kind == "labor":
                    labor += base


                subtotal += base
                tax_total += tax_part
                grand_total += line_total

        ### SHOP SUPPLIES STUB FOR NOW
        shop_supplies = (subtotal * self._shop_supplies_pct / decimal("100")).quantize(decimal("0.01"))

        def set_labels(labels, val: Decimal):
            labels.setText(f"{val.quantize(Decimal('0.01')):.2f}")

        set_labels(self.ui.parts_label, parts)
        set_labels(self.ui.labor_label, labor)
        set_labels(self.ui.tires_label, tires)
        set_labels(self.ui.fees_label, fees)
        set_labels(self.ui.shop_supplies_label, shop_supplies)
        set_labels(self.ui.tax_label, tax_total)
        set_labels(self.ui.label_2, sublet)
        set_labels(self.ui.subtotal_label, subtotal)
        set_labels(self.ui.total_label, grand_total + shop_supplies)
            
            
