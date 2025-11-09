from PyQt6 import QtCore
from PyQt6.QtWidgets import QMessageBox
from openauto.repositories.repair_orders_repository import RepairOrdersRepository
from openauto.repositories.estimates_repository import EstimatesRepository
from openauto.repositories.estimate_items_repository import EstimateItemsRepository
from openauto.repositories.estimate_jobs_repository import EstimateJobsRepository
from openauto.repositories.ro_c3_repository import ROC3Repository
import re
from decimal import Decimal, ROUND_HALF_UP
from openauto.subclassed_widgets.roles.tree_roles import (
    JOB_ID_ROLE, JOB_NAME_ROLE, ITEM_ID_ROLE, LINE_ORDER_ROLE, ROW_KIND_ROLE
)
from openauto.subclassed_widgets.views.ro_tiles import update_all_tiles




def _num(x, default="0"):
    s = str(x or "").replace(",", "").replace("$", "").strip()
    try:
        return Decimal(s if s else default)
    except Exception:
        return Decimal(default)

class SaveEstimateService:
    def __init__(self, ui):
        self.ui = ui

    def _current_ro_id(self):
        return getattr(self.ui, "current_ro_id", None)

    def _collect_ui_items_for_estimate(self, ro_id: int, estimate_id: int) -> list[dict]:
        out: list[dict] = []

        def _num(x, fallback="0"):
            from decimal import Decimal
            try:
                return Decimal(str(x)) if str(x).strip() != "" else Decimal(fallback)
            except Exception:
                return Decimal(fallback)

        tree = getattr(self.ui, "ro_items_table", None) or getattr(self.ui, "roTable", None)
        if not tree:
            return out

        # Resolve the column indexes once
        def col_idx(name_fallback, default):
            try:
                return getattr(tree, f"_COL_{name_fallback.upper()}")
            except Exception:
                return default

        COL_TYPE = col_idx("type", 0)
        COL_DESC = col_idx("desc", 1)
        COL_QTY = col_idx("qty", 2)
        COL_RATE = col_idx("rate", 3)
        COL_PRICE = col_idx("price", 4)
        COL_TAX = col_idx("tax", 5)

        # Helper to read a numeric cell, preferring EditRole
        def D(item, col, fallback="0"):
            val = item.data(col, QtCore.Qt.ItemDataRole.EditRole)
            if val is None or val == "":
                val = item.text(col)
            return _num(val, fallback)

        # Kind resolver (UserRole first, falls back to visible text)
        def _kind_of(row) -> str:
            v = row.data(COL_TYPE, QtCore.Qt.ItemDataRole.UserRole)
            if isinstance(v, (dict, list, tuple, set)):
                v = None
            k = (v or row.text(COL_TYPE) or "part")
            try:
                return str(k).strip().lower()
            except Exception:
                return "part"

        for i in range(tree.topLevelItemCount()):
            job_header = tree.topLevelItem(i)
            job_name = job_header.data(0, JOB_NAME_ROLE) or self._strip_status_suffix(job_header.text(0))

            for r in range(job_header.childCount()):
                row = job_header.child(r)

                # skip subtotal
                if (row.text(COL_TYPE) or "").strip().upper() == "SUBTOTAL":
                    continue

                kind = _kind_of(row)
                desc = (row.text(COL_DESC) or "").strip()
                qty = D(row, COL_QTY, "1")
                rate = D(row, COL_RATE, "0") if COL_RATE >= 0 else _num("0")
                price = D(row, COL_PRICE, "0")
                tax_pct = D(row, COL_TAX, "0")

                # skip truly empty lines
                if not desc and qty == 0 and rate == 0 and price == 0:
                    continue

                # item identity/line order if present
                try:
                    item_id = row.data(0, ITEM_ID_ROLE)
                    if isinstance(item_id, int):
                        item_id = int(item_id)
                    else:
                        item_id = None
                except Exception:
                    item_id = None
                try:
                    line_order_role = row.data(0, LINE_ORDER_ROLE)
                    line_order = int(line_order_role) if line_order_role is not None else None
                except Exception:
                    line_order = None

                if kind == "labor":
                    unit_price = rate
                    unit_cost = _num("0")
                else:
                    unit_price = price
                    unit_cost = _num("0")

                out.append({
                    "id": item_id,
                    "estimate_id": estimate_id, "ro_id": ro_id,
                    "description": desc,
                    "qty": qty, 
                    "unit_cost": unit_cost,
                    "unit_price": unit_price,
                    "taxable": 1,
                    "tax_pct": float(tax_pct or 0),
                    "vendor": None,
                    "source": {"part": "manual", "labor": "labor", "tire": "tire", "fee": "fee",
                               "sublet": "sublet"}.get(kind, "manual"),
                    "metadata": None,
                    "kind": kind,  # <-- saved to DB “type”
                    "job_name": job_name,
                    "line_order": line_order,
                })

        return out

    def _attach_jobs_and_order(self, estimate_id: int, items: list[dict], tree=None):
        job_names: list[str] = []
        job_ids: dict[str, int] = {}

        if tree:
            # Use the visible order of headers
            for i in range(tree.topLevelItemCount()):
                header = tree.topLevelItem(i)
                base_name = self._strip_status_suffix(header.data(0, JOB_NAME_ROLE) or header.text(0))
                base_name = (base_name or "General").strip()

                if base_name not in job_names:
                    job_names.append(base_name)

                jid = header.data(0, JOB_ID_ROLE)

                if isinstance(jid, int):
                    # Persist header rename now so Save always sticks the rename
                    kept = EstimateJobsRepository.rename_or_merge(int(jid), base_name)
                    header.setData(0, JOB_ID_ROLE, int(kept))
                    header.setData(0, JOB_NAME_ROLE, base_name)
                    job_ids[base_name] = int(kept)

        else:
            # Infer from items as they appear
            for it in items:
                nm = self._strip_status_suffix(it.get("job_name"))
                if nm not in job_names:
                    job_names.append(nm)
            if not job_names:
                job_names = ["General"]

        # Ensure jobs exist and map to ids (ALWAYS run this)
        for nm in job_names:
            if nm not in job_ids:
                job_ids[nm] = EstimateJobsRepository.get_or_create(estimate_id, nm)

        #push the resolved/created ids back into headers so they’re usable immediately
        if tree:
            for i in range(tree.topLevelItemCount()):
                header = tree.topLevelItem(i)

                # normalize the name exactly the same way every time
                raw_name = (header.data(0, JOB_NAME_ROLE) or header.text(0) or "").strip()
                base_name = self._strip_status_suffix(raw_name) or "General"

                # if the name wasn't in the earlier map for any reason, create/insert now
                jid = job_ids.get(base_name)
                if jid is None:
                    jid = EstimateJobsRepository.get_or_create(estimate_id, base_name)
                    job_ids[base_name] = int(jid)

                header.setData(0, JOB_ID_ROLE, int(jid))
                header.setData(0, JOB_NAME_ROLE, base_name)

        # Assign job_id + job_order + line_order to each item
        line_counters: dict[str, int] = {nm: 0 for nm in job_names}

        for it in items:
            nm = self._strip_status_suffix(it.get("job_name"))
            if nm not in job_ids:
                job_names.append(nm)
                job_ids[nm] = EstimateJobsRepository.get_or_create(estimate_id, nm)
                line_counters[nm] = 0

            it["job_id"] = job_ids[nm]
            it["job_order"] = job_names.index(nm) + 1

            # Preserve UI-provided line_order; only assign if missing
            if it.get("line_order") is None:
                it["line_order"] = line_counters[nm]
                line_counters[nm] += 1
            else:
                # keep counters in sync for any subsequent items without line_order
                try:
                    lo = int(it["line_order"])
                except Exception:
                    lo = 0
                line_counters[nm] = max(line_counters[nm], lo + 1)

    def _strip_status_suffix(self, name: str | None) -> str:
        if not name:
            return "General"
        s = str(name).strip()

        s = re.sub(
             r"\s*[-—]\s*(approved|declined|quoted|ordered|received|returned|cancelled)\s*$",
             "",
                    s,
                flags = re.IGNORECASE,
            )
        return s.strip() or "General"


    def save(self, *, silent: bool = False) -> int | None:
        ro_id = self._current_ro_id()
        if not ro_id:
            if not silent:
                QMessageBox.warning(self.ui, "Save RO", "No Repair Order selected.")
            return

        ro = RepairOrdersRepository.get_repair_order_by_id(ro_id)

        def _miles(x):
            s = str(x or "").strip()
            # keep only digits (so "52,000" or "52 000 mi" becomes "52000")
            s = re.sub(r"[^\d]", "", s)
            if not s:
                return None
            try:
                return int(s)
            except Exception:
                return None


        writer_name = ro.get("writer_name") or (self.ui.writer_box.currentText() if hasattr(self.ui, "writer_box") else "")
        tech_name   = ro.get("tech_name") or (self.ui.technician_box.currentText() if hasattr(self.ui, "technician_box") else "")
        miles_in_text  = self.ui.miles_in_edit.text() if hasattr(self.ui, "miles_in_edit") else ""
        miles_out_text = self.ui.miles_out_edit.text() if hasattr(self.ui, "miles_out_edit") else ""
        miles_in = _miles(miles_in_text)
        miles_out = _miles(miles_out_text)
        est = EstimatesRepository.get_by_ro_id(ro_id)
        estimate_id = est["id"] if est else EstimatesRepository.create_for_ro(ro, writer_name, tech_name)
        memo = (self.ui.notes_text_edit.toPlainText() or "").strip()
        tree = getattr(self.ui, "ro_items_table", None)

        est = EstimatesRepository.get_by_ro_id(ro_id)
        estimate_id = est["id"] if est else EstimatesRepository.create_for_ro(ro, writer_name, tech_name)

        if tree and hasattr(tree, "to_legacy_items"):
            items = tree.to_legacy_items()
        else:
            items = self._collect_ui_items_for_estimate(ro_id, estimate_id)

        for it in items:
            it["estimate_id"] = estimate_id
            it["ro_id"] = ro_id
            if not it.get("sku_number") and it.get("sku"):
                it["sku_number"] = it["sku"] or ""
            it["sku_number"] = it.get("sku_number") or ""

    # Ensure tax_pct is numeric and not None
            try:
                it["tax_pct"] = float(it.get("tax_pct", 0.0) or 0.0)
            except (TypeError, ValueError):
                it["tax_pct"] = 0.0

        self._attach_jobs_and_order(estimate_id, items, tree)

        try:
            from openauto.repositories.db_handlers import connect_db
            _cn = connect_db()
            with _cn, _cn.cursor() as _c:
                _c.execute(
                    "UPDATE repair_orders SET estimate_id=%s WHERE id=%s AND (estimate_id IS NULL OR estimate_id<>%s)",
                    (estimate_id, ro_id, estimate_id))
                _cn.commit()
        except Exception:
            pass

        # ---- Save Concern / Cause / Correction for this RO ----
        def _text(widget_name: str) -> str:
            w = getattr(self.ui, widget_name, None)
            try:
                return (w.toPlainText() or "").strip() if w is not None else ""
            except Exception:
                return ""

        concern_txt    = _text("concern_edit")
        cause_txt      = _text("cause_edit")
        correction_txt = _text("correction_edit")

        try:
            # Get existing C3 rows (if any) and update the first one; else create it.
            rows = ROC3Repository.list_for_ro(int(ro_id)) or []
            if rows:
                line_id = int(rows[0]["id"])
                ROC3Repository.update_line(line_id, {
                    "concern":    concern_txt,
                    "cause":      cause_txt,
                    "correction": correction_txt,
                })
            else:
                ROC3Repository.create_line(
                    ro_id=int(ro_id),
                    concern=concern_txt,
                    cause=cause_txt,
                    correction=correction_txt,
                    estimate_item_id=None,   # keep unattached; wire later if you add per-line C3
                    created_by=getattr(self.ui, "current_user_id", None),
                )
        except Exception:
            # Non-fatal; keep the Save flow alive even if C3 write hiccups.
            pass



        RepairOrdersRepository.update_miles(
            miles_in=miles_in or None,
            miles_out=miles_out or None,
            ro_id=ro_id
        )

        tree = getattr(self.ui, "ro_items_table", None) or getattr(self.ui, "roTable", None)
        self._attach_jobs_and_order(estimate_id, items, tree)

        existing_ids = set(EstimateItemsRepository.get_ids_for_estimate(estimate_id))

        # Split incoming rows by presence of id
        to_update = [it for it in items if it.get("id")]
        to_insert = [it for it in items if not it.get("id")]

        # Update existing rows (job_id, line_order, description, qty, unit_price, etc.)
        for it in to_update:
            EstimateItemsRepository.update_item(it)  # must use it["id"]


        EstimatesRepository.set_internal_memo(estimate_id, memo)

        # Insert new rows; capture new ids if you want to push back to the UI later
        for it in to_insert:
            if it["description"] == "" or None:
                it["description"] = "EMPTY"
            new_id = EstimateItemsRepository.insert_item(it)
            it["id"] = new_id  

        existing_item_ids = set(EstimateItemsRepository.get_ids_for_estimate(estimate_id))
        present_item_ids = {it["id"] for it in items if it.get("id")}

        item_ids_to_delete = list(existing_item_ids - present_item_ids)
        if item_ids_to_delete:
            EstimateItemsRepository.delete_many(item_ids_to_delete)

        #JOB reconciliation (by job id)
        present_jobs = tree.current_jobs() if hasattr(tree, "current_jobs") else []
        present_job_ids = {j["job_id"] for j in present_jobs if j.get("job_id")}

        existing_jobs = EstimateJobsRepository.list_for_estimate(estimate_id)  # [{id, job_name, job_order, ...}]
        existing_job_ids = {j["id"] for j in existing_jobs}

        job_ids_to_delete = list(existing_job_ids - present_job_ids)
        if job_ids_to_delete:
            EstimateJobsRepository.delete_jobs(estimate_id, job_ids_to_delete)


        def _D(x) -> Decimal:
            # works for None/float/int/str
            try:
                return Decimal(str(x if x is not None else "0"))
            except Exception:
                return Decimal("0")

        total = sum((_D(i.get("qty")) * _D(i.get("unit_price")) for i in items), Decimal("0"))
        tax_total = sum((_D(i.get("line_total")) - (_D(i.get("qty")) * _D(i.get("unit_price"))) for i in items), Decimal("0"))
        grand_total = sum((_D(i.get("line_total")) for i in items), Decimal("0"))
        total = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        EstimatesRepository.update_total(estimate_id, float(total))
        EstimateJobsRepository.recompute_totals_for_estimate(estimate_id)
        QtCore.QTimer.singleShot(0, lambda: update_all_tiles(ro_id, total=float(total)))
        try:
            update_all_tiles(ro_id, total=float(total))
        except Exception:
            pass
        if not silent:
            QMessageBox.information(self.ui, "Save RO", f"Estimate #{estimate_id} saved with {len(items)} items.")
        return int(estimate_id)

