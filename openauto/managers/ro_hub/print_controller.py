from pathlib import Path
from PyQt6 import QtWidgets, QtGui, QtCore
from openauto.printing.print_service import PrintService
from openauto.managers.settings_manager import SettingsManager
from openauto.repositories.repair_orders_repository import RepairOrdersRepository
from openauto.repositories.customer_repository import CustomerRepository
from openauto.repositories.vehicle_repository import VehicleRepository
from openauto.repositories.estimates_repository import EstimatesRepository
from openauto.repositories.estimate_items_repository import EstimateItemsRepository
from openauto.repositories.estimate_jobs_repository import EstimateJobsRepository
from openauto.repositories.ro_c3_repository import ROC3Repository
from openauto.managers.ro_hub.save_estimate_service import SaveEstimateService

_BASE = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = _BASE / "printing" / "templates"
ASSETS_DIR   = _BASE / "printing" / "assets"
assets_url = QtCore.QUrl.fromLocalFile(str(ASSETS_DIR)).toString()


def _money(x) -> float:
    try: return float(x or 0)
    except: return 0.0

def _sum(rows, key): return sum(_money(r.get(key)) for r in rows)


class PrintController(QtCore.QObject):
    def __init__(self, ui):
        super().__init__(ui)
        self.ui = ui
        app = QtWidgets.QApplication.instance()
        self.print_service = PrintService(template_dir=TEMPLATE_DIR, assets_dir=ASSETS_DIR, app=app)
        existing_menu = getattr(self.ui, "print_menu", None)
        if existing_menu is None:
            existing_menu = QtWidgets.QMenu(self.ui.print_ro_button)
            self.ui.print_menu = existing_menu
        self.print_menu = existing_menu
        self._menu_initialized = False
        self._setup_print_menu()
        self.settings_manager = SettingsManager
        self.estimates_repo = EstimatesRepository()
        self.customers_repo = CustomerRepository()
        self.vehicles_repo = VehicleRepository()
        self.repair_orders_repo = RepairOrdersRepository()
        self.estimate_items_repo = EstimateItemsRepository()
        self.estimate_jobs_repo = EstimateJobsRepository()
        self.ro_c_three_repo = ROC3Repository()
        self.save_estimator = SaveEstimateService(self.ui)
        self.load_estimate_items = self.save_estimator._collect_ui_items_for_estimate
        self._ctx_ro_id = None
        self._ctx_est_id = None
        self._ctx_vin = None


    def _setup_print_menu(self):
        if self._menu_initialized:
            return
        self.print_menu.clear()
        self.estimate_action = self.print_menu.addAction("Print Estimate For Customer")
        self.job_ticket_action = self.print_menu.addAction("Print Job Ticket For Technician")
        self.estimate_action.triggered.connect(
            lambda: self.on_print_ro_clicked_with_ids(
                getattr(self.ui, "current_ro_id", None) or 0,
                getattr(self.ui.ro_items_table, "current_estimate_id", None) or 0,
                "estimate",
            )
        )
        self.job_ticket_action.triggered.connect(
            lambda: self.on_print_ro_clicked_with_ids(
                getattr(self.ui, "current_ro_id", None) or 0,
                getattr(self.ui.ro_items_table, "current_estimate_id", None) or 0,
                "job_ticket",
            )
        )
        self._menu_initialized = True

    def on_print_context_menu(self):
        self._setup_print_menu()
        global_pos = self.ui.print_ro_button.mapToGlobal(self.ui.print_ro_button.rect().bottomLeft())
        self.print_menu.popup(global_pos)
        

    @QtCore.pyqtSlot(int, int, str)
    def set_context(self, ro_id: int, est_id: int, vin: str = ""):
        self._ctx_ro_id = int(ro_id) if ro_id else None
        self._ctx_est_id = int(est_id) if est_id else None
        self._ctx_vin = vin or None


    @QtCore.pyqtSlot(int, int, str)
    def on_print_ro_clicked_with_ids(self, ro_id: int, est_id: int, mode: str = "estimate"):
        self._ctx_ro_id = int(ro_id) if ro_id else None
        self._ctx_est_id = int(est_id) if est_id else None
        self.on_print_ro_clicked(mode=mode)

    def on_print_ro_clicked(self, mode: str = "estimate"):
        sel = self.current_selection()
        self.ro_id = self._ctx_ro_id if self._ctx_ro_id is not None else getattr(sel, "ro_id", None)
        self.est_id = self._ctx_est_id if self._ctx_est_id is not None else getattr(sel, "estimate_id", None)
        if not self.est_id:
            self.est_id = getattr(self.ui, "current_estimate_id", None)
        if not self.est_id and self.ro_id:
            self.est_id = self.repair_orders_repo.estimate_id_for_ro(self.ro_id)

        if self.ro_id:
            ro, customer, vehicle, items, jobs, ro_c3 = self._load_ro_with_items(self.ro_id)
            doc_number = ro.get("ro_number") or f"RO-{self.ro_id}"
            opened = ro.get("created_at") or ""
        else:
            est, customer, vehicle, items, jobs, ro_c3 = self._load_estimate_with_items(self.est_id)
            doc_number = est.get("estimate_number") or f"EST-{self.est_id}"
            opened = est.get("created_at_str") or ""

        current_tech = ""
        if hasattr(self.ui, "technician_box"):
            current_tech = (self.ui.technician_box.currentText() or "").strip()
        if current_tech:
            for job in jobs:
                job["tech"] = current_tech

        # Exclude declined jobs from printed totals while still showing them in the job list
        status_by_job = {
            j.get("id"): (j.get("status") or "proposed").lower()
            for j in jobs
            if j.get("id") is not None
        }
        items_for_totals = []
        for it in items:
            jid = it.get("job_id") or 0
            if jid and status_by_job.get(jid) == "declined":
                continue
            items_for_totals.append(it)

        subtotal = _sum(items_for_totals, "total")
        tax_rate = (getattr(self.settings_manager, "sales_tax_rate", 0.0) or 0.0)
        tax = float(self.ui.tax_label.text())
        fees = 0.0
        grand = round(subtotal + tax + fees, 2)

        shop = {
            "name": self.ui.shop_name_line.text(),
            "addr1": self.ui.address_line.text(),
            "city": self.ui.city_line.text(),
            "state": self.ui.state_line.text(),
            "zip": self.ui.zipcode_line.text(),
            "phone": self.ui.settings_phone_line.text(),
            "disclaimer": self.ui.disclamer_edit.toPlainText(),
            "logo": self.ui.shop_logo.pixmap(),
        }

        ctx = {
            "shop": shop,
            "customer": {
                "full_name": customer.get("full_name") or f"{customer.get('first_name','')} {customer.get('last_name','')}".strip(),
                "phone": customer.get("phone",""),
                "email": customer.get("email",""),
            },
            "vehicle": {
                "year": vehicle.get("year",""),
                "make": vehicle.get("make",""),
                "model": vehicle.get("model",""),
                "vin": vehicle.get("vin",""),
                "miles_in": self.ui.miles_in_edit.text(),
                "miles_out": self.ui.miles_out_edit.text(),
            },
            "ro": {"number": doc_number, "opened": opened},
            "items": items,
            "jobs": jobs,
            "ro_c3" : ro_c3,
            "totals": {"subtotal": subtotal, "tax": tax, "fees": fees, "grand": grand},
            "assets_path": assets_url,
        }

        template_name, payload, suggested = self._prepare_print_payload(mode, ctx)
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self.ui, "Save RO as PDF", suggested, "PDF Files (*.pdf)")
        if not path:
            return

        html = self.print_service.render(template_name, payload)
        out_path = self.print_service.html_to_pdf(html, Path(path))
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(out_path)))

    def _prepare_print_payload(self, mode: str, ctx: dict):
        doc_number = ctx["ro"]["number"]
        if mode == "job_ticket":
            payload = self._build_job_ticket_context(ctx)
            template = "job_ticket.html"
            suggested = f"{doc_number}-job-ticket.pdf"
        else:
            payload = ctx
            template = "repair_order.html"
            suggested = f"{doc_number}.pdf"
        return template, payload, suggested

    def _build_job_ticket_context(self, ctx: dict) -> dict:
        def _labor_only(lines):
            labor = [ln for ln in lines if (ln.get("kind") or "").lower() == "labor"]
            return labor or lines

        jobs = []
        for job in ctx.get("jobs", []):
            # Only include approved jobs on technician job tickets
            if (job.get("status") or "").lower() != "approved":
                continue
            jobs.append({
                "id": job.get("id"),
                "title": job.get("title"),
                "tech": job.get("tech"),
                "po": job.get("po"),
                "lines": [
                    {
                        "desc": ln.get("desc"),
                        "qty": ln.get("qty"),
                        "notes": ln.get("notes", ""),
                    }
                    for ln in _labor_only(job.get("lines", []))
                ],
            })

        return {
            "mode": "job_ticket",
            "shop": ctx.get("shop", {}),
            "customer": ctx.get("customer", {}),
            "vehicle": ctx.get("vehicle", {}),
            "ro": ctx.get("ro", {}),
            "jobs": jobs,
            "ro_c3": ctx.get("ro_c3"),
            "items": ctx.get("items"),
            "assets_path": ctx.get("assets_path"),
        }

    #tailor info from repos
    def _load_ro_with_items(self, ro_id: int):
        ro = self.repair_orders_repo.get_repair_order_by_id(ro_id)
        customer = self.customers_repo.get_customer_info_by_id(ro["customer_id"])
        vehicle = (self.vehicles_repo.get_vehicle_by_id(ro.get("vehicle_id"))
                   if ro.get("vehicle_id")
                   else self.vehicles_repo.get_vehicle_info_for_new_ro(ro["customer_id"]))

        lines = self.estimate_items_repo.list_for_ro(ro_id) or []

        items = []
        for ln in lines:
            qty = float(ln.get("qty") or 1)
            rate = float(ln.get("unit_price") or 0)
            total = round(qty * rate, 2)
            items.append({
                "desc": ln.get("item_description") or "",
                "qty": qty,
                "rate": rate,
                "total": total,
                "kind": (ln.get("type") or "").lower(),
                "job_id": ln.get("job_id") or 0,
            })
        jobs_meta = []
        try:
            jobs_meta = self.estimate_jobs_repo.get_jobs_for_ro(ro_id) or []
        except Exception:
            jobs_meta = []
        c3_rows = self.ro_c_three_repo.list_for_ro(ro_id) or []
        ro_c3 = {"concern": "", "cause": "", "correction": ""}
        for r in c3_rows:
            if not ro_c3["concern"] and r.get("concern"):
                ro_c3["concern"] = r.get("concern", "")
            if not ro_c3["cause"] and r.get("cause"):
                ro_c3["cause"] = r.get("cause", "")
            if not ro_c3["correction"] and r.get("correction"):
                ro_c3["correction"] = r.get("correction", "")

        meta_by_id = {(j.get("id") or j.get("job_id")): j for j in jobs_meta if (j.get("id") or j.get("job_id")) is not None}
        grouped = {}
        for it in items:
            jid = it.get("job_id") or 0
            grouped.setdefault(jid, []).append(it)
        jobs = []
        for jid, rows in grouped.items():
            meta = meta_by_id.get(jid, {}) if jid else {}
            status = (meta.get("status") or "proposed").lower()
            status_label = "Approved" if status == "approved" else ("Declined" if status == "declined" else "Proposed")
            title = (
                meta.get("name")
                or meta.get("title")
                or meta.get("job_title")
                or f"Job {jid or ''}".strip()
            )
            jobs.append({
                "id": jid,
                "title": title,
                "tech": meta.get("tech") or meta.get("technician") or "",
                "po": meta.get("po") or "",
                "status": status,
                "status_label": status_label,
                "lines": rows,
            })

        jobs.sort(key=lambda j: (j["id"]==0, j["id"]))
        return ro, customer, vehicle, items, jobs, ro_c3

    def _load_estimate_with_items(self, estimate_id: int):
        est = self.estimates_repo.get_by_id(estimate_id) if estimate_id else None

        if est is None and getattr(self, "ro_id", None):
            est = self.estimates_repo.get_by_ro_id(self.ro_id)
            if est:
                estimate_id = est.get("id")

        if est is None and getattr(self.ui, "current_estimate_id", None):
            est = self.estimates_repo.get_by_id(self.ui.current_estimate_id)
            if est:
                estimate_id = est.get("id")

        if est is None:
            QtWidgets.QMessageBox.warning(self.ui, "Print",
                    "No estimate found. Save the RO to create/refresh its estimate, then try again.")
            return {"estimate_number": f"EST-{estimate_id or 'UNKNOWN'}"}, {}, {}, [], [], {"concern": "", "cause": "",
                                                                                            "correction": ""}

        customer = self.customers_repo.get_customer_info_by_id(est["customer_id"])
        vehicle = (self.vehicles_repo.get_vehicle_by_id(est.get("vehicle_id"))
                   if est.get("vehicle_id")
                   else self.vehicles_repo.get_vehicle_info_for_new_ro(est["customer_id"]))
        lines = self.load_estimate_items(ro_id=est.get("ro_id"), estimate_id=estimate_id) or []

        items = []
        for ln in lines:
            qty = float(ln.get("qty") or ln.get("hours") or 1)
            rate = float(ln.get("unit_price") or ln.get("rate") or ln.get("price") or 0)
            total = float(ln.get("total") or ln.get("ext") or (qty * rate))
            items.append({
                "desc": ln.get("item_description") or ln.get("description") or ln.get("desc") or "",
                "qty": qty,
                "rate": rate,
                "total": total,
                "kind": (ln.get("type") or ln.get("kind") or "").lower(),
                "job_id": ln.get("job_id") or ln.get("estimate_job_id") or 0,
            })

        jobs_meta = []
        try:
            if hasattr(self.estimate_jobs_repo, "get_jobs_for_estimate"):
                jobs_meta = self.estimate_jobs_repo.get_jobs_for_estimate(estimate_id) or []
            else:
                jobs_meta = self.estimate_jobs_repo.get_jobs_for_ro(est.get("ro_id")) or []
        except Exception:
            jobs_meta = {}

        meta_by_id = {(j.get("id") or j.get("job_id")): j for j in jobs_meta if
                      (j.get("id") or j.get("job_id")) is not None}
        grouped = {}
        for it in items:
            jid = it.get("job_id") or 0
            grouped.setdefault(jid, []).append(it)
        jobs = []
        for jid, rows in grouped.items():
            meta = meta_by_id.get(jid, {}) if jid else {}
            status = (meta.get("status") or "proposed").lower()
            status_label = "Approved" if status == "approved" else ("Declined" if status == "declined" else "Proposed")
            title = (
                meta.get("name")
                or meta.get("title")
                or meta.get("job_title")
                or f"Job {jid or ''}".strip()
            )

            jobs.append({
                "id": jid,
                "title": title,
                "tech": meta.get("tech") or meta.get("technician") or "",
                "po": meta.get("po") or "",
                "complaint": meta.get("complaint") or meta.get("c1") or "",
                "cause": meta.get("cause") or meta.get("c2") or "",
                "correction": meta.get("correction") or meta.get("c3") or "",
                "status": status,
                "status_label": status_label,
                "lines": rows,
            })

        jobs.sort(key=lambda j: (j["id"] == 0, j["id"]))
        ro_c3 = {"concern": "", "cause": "", "correction": ""}
        if est.get("ro_id"):
            c3_rows = self.ro_c_three_repo.list_for_ro(est["ro_id"]) or []
            for r in c3_rows:
                if not ro_c3["concern"] and r.get("concern"):
                    ro_c3["concern"] = r["concern"]
                if not ro_c3["cause"] and r.get("cause"):
                    ro_c3["cause"] = r["cause"]
                if not ro_c3["correction"] and r.get("correction"):
                    ro_c3["correction"] = r["correction"]

        return est, customer, vehicle, items, jobs, ro_c3



    # Provide a selection helper if you don’t have one already
    def current_selection(self):
        from types import SimpleNamespace
        data = {}
        try:
            idx = self.ui.ro_tabs.currentIndex()
            data = (self.ui.ro_tabs.widget(idx).property("ro_meta") or {})
        except Exception:
            pass
        if not data:
            try:
                idx = self.ui.ro_cards.currentIndex()
                data = (self.ui.ro_cards.widget(idx).property("ro_meta") or {})
            except Exception:
                data = {}

        if data and data.get("ro_id"):
            return SimpleNamespace(ro_id=data["ro_id"])
        if data and data.get("estimate_id"):
            return SimpleNamespace(estimate_id=data["estimate_id"])
        return SimpleNamespace()
