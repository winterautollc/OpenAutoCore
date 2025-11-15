from PyQt6 import QtCore
from openauto.repositories.repair_orders_repository import RepairOrdersRepository
from openauto.repositories.customer_repository import CustomerRepository
from openauto.repositories.vehicle_repository import VehicleRepository
from openauto.repositories.estimate_items_repository import EstimateItemsRepository
from openauto.repositories.estimate_jobs_repository import EstimateJobsRepository
from openauto.repositories.settings_repository import SettingsRepository
from openauto.repositories.estimates_repository import EstimatesRepository
from openauto.services.ro_status_service import ROStatusService
from openauto.managers.ro_hub.staff_controller import StaffAssignmentController
from openauto.managers.ro_hub.item_entry_controller import ItemEntryController
from openauto.managers.ro_hub.status_controller import StatusDialogController
from openauto.managers.ro_hub.tax_controller import TaxConfigController
from openauto.managers.ro_hub.save_estimate_service import SaveEstimateService
from openauto.managers.ro_hub.totals_controller import TotalsController
from openauto.managers.ro_hub.c3_controller import C3Controller
from openauto.managers.repair_orders_manager import RepairOrdersManager
from openauto.managers.ro_hub.autosave_controller import AutosaveController
from openauto.managers.ro_hub.mpi_manager import MpiManager
from openauto.managers.ro_hub.print_controller import PrintController
import datetime
from openauto.subclassed_widgets.roles.tree_roles import COL_DESC, COL_TYPE, JOB_ID_ROLE, APPROVED_ROLE, DECLINED_ROLE
from openauto.subclassed_widgets.roles.tree_roles import (
    JOB_ID_ROLE, JOB_NAME_ROLE, ITEM_ID_ROLE, LINE_ORDER_ROLE, ROW_KIND_ROLE
)

def _skip_during_drop(table) -> bool:
    try:
        return getattr(table, "_dropping", False) or table.signalsBlocked()
    except Exception:
        return False

def _safe_int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _to_qdatetime(dt) -> QtCore.QDateTime:
    if isinstance(dt, datetime.datetime):
        return QtCore.QDateTime(
            dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second
        )
    if isinstance(dt, str) and dt:
        ts = dt.split('.')[0]
        qdt = QtCore.QDateTime.fromString(ts, "yyyy-MM-dd HH:mm:ss")
        if qdt.isValid():
            return qdt
    return QtCore.QDateTime()


def _format_miles_line_edit(le):
    txt = le.text().strip()
    digits = "".join(ch for ch in txt if ch.isdigit())
    if digits:
        le.setText(QtCore.QLocale().toString(int(digits)))  # adds grouping per OS locale
    else:
        le.clear()


class ROHubManager(QtCore.QObject):
    roContextReady = QtCore.pyqtSignal(int, int, str)
    def __init__(self, ui):
        super().__init__(ui)
        self.ui = ui
        self.staff  = StaffAssignmentController(ui)
        self.items  = ItemEntryController(ui)
        self.ui.repair_orders_manager = RepairOrdersManager(self.ui)
        QtCore.QTimer.singleShot(0, self.ui.repair_orders_manager.refresh_all)

        self.status = StatusDialogController(
            ui=self.ui,
            get_current_status=lambda: self.ui.ro_status_label.text(),
            get_current_ro_id=lambda: getattr(self.ui, "current_ro_id", None),
            persist=lambda ro_id, code: ROStatusService.persist(
                ro_id, code, user_id=getattr(self.ui, "current_user_id", None)
            ),)
        self.status.statusChanged.connect(self._on_status_changed)
        self.tax    = TaxConfigController(ui)
        self.saver  = SaveEstimateService(ui)
        self.autosaver = AutosaveController(ui)
        self.totals = TotalsController(ui)
        self.print_controller = PrintController(ui)
        self.roContextReady.connect(self.print_controller.set_context)
        self.ui.print_ro_button.setMenu(self.ui.print_menu)

        self.c3 = C3Controller(ui)
        self.mpi_manager = MpiManager(ui)
        self.ui.roTable = self.ui.ro_items_table
        self._load_pricing_inputs()
        self._wire_item_entry_signals()
        self._wire_signals()
        self.staff.populate_and_connect()
        self.tax.connect_tax_rate()
        self.items.adjust_item_lines()
        self.totals.attach(self.ui.ro_items_table)



    def _load_pricing_inputs(self):

        # labor rates populate in combobox with labor type description
        self.ui.labor_rate_box.clear()
        labor_rate_rows = SettingsRepository.load_labor_table() or []

        for labor_rate, labor_type in labor_rate_rows:
            label = f"{labor_rate: .2f} ({labor_type})" if isinstance(labor_rate, (int, float)) else f"{labor_rate} ({labor_type})"
            self.ui.labor_rate_box.addItem(label, labor_rate)

        self.ui.tax_box.clear()
        tax_rows = SettingsRepository.get_tax_info() or []

        for tax_rate, tax_type in tax_rows:
            suffix = f"{tax_type}" if tax_type else ""
            self.ui.tax_box.addItem(f"{tax_rate}% {suffix}", float(tax_rate) if tax_rate is not None else 0.0)
        self.ui.tax_box.addItem(f"{float(0)}% None")
  

    def _wire_item_entry_signals(self):
        self.ui.cost_edit.textChanged.connect(self.items.recalculate_sell_from_matrix)
        self.ui.cost_edit.editingFinished.connect(self.items.recalculate_sell_from_matrix)
        self.ui.type_box.currentTextChanged.connect(self.items.recalculate_sell_from_matrix)
        self.ui.miles_in_edit.editingFinished.connect(lambda: _format_miles_line_edit(self.ui.miles_in_edit))
        self.ui.miles_out_edit.editingFinished.connect(lambda: _format_miles_line_edit(self.ui.miles_out_edit))


    def _wire_signals(self):
        # mirror original connections
        self.ui.type_box.addItems(self.items.type_options())
        self.ui.type_box.currentTextChanged.connect(self.items.adjust_item_lines)
        self.ui.add_job_item_button.clicked.connect(self.items.add_item)
        self.ui.remove_item_button.clicked.connect(self.items.remove_selected_item)
        self.ui.new_job_button.clicked.connect(self._new_job)
        self.ui.save_ro_button.hide()
        self.ui.save_ro_button.clicked.connect(self.saver.save)
        self.autosaver.saved.connect(self.on_estimate_saved)
        self.ui.concern_button.toggled.connect(lambda checked: self._toggle_3c_stack(0, checked))
        self.ui.cause_button.toggled.connect(lambda checked: self._toggle_3c_stack(1, checked))
        self.ui.correction_button.toggled.connect(lambda checked: self._toggle_3c_stack(2, checked))
        self.ui.concern_button.setChecked(True)
        self.ui.approved_placer_label.setText("Updated")
        self.status.attach(self.ui.ro_status_button)
        self.status.refresh_button()
        self.ui.cancel_ro_button.setText("Exit")
        self.ui.cancel_ro_button.clicked.connect(self.status.cancel_ro_changes)

        delegate = getattr(self.ui.ro_items_table, "itemDelegate", None)
        if callable(delegate):
            try:
                d = self.ui.ro_items_table.itemDelegate()
                d.closeEditor.connect(lambda *_: (
                    self.autosaver.resume(),
                    self.autosaver.mark_dirty(),
                    QtCore.QTimer.singleShot(0, self.autosaver.flush_if_dirty)
                ))
            except Exception:
                pass

        self.ui.ro_items_table.approvalChanged.connect(
            lambda: self._sync_approval_to_db_and_refresh(getattr(self.ui, "current_ro_id", None) or 0))

        self.ui.ro_items_table.declineJobChanged.connect(
            lambda: self._sync_approval_to_db_and_refresh(getattr(self.ui, "current_ro_id", None) or 0))

        self.ui.ro_items_table.jobsChanged.connect(self._reload_after_job_change)



        for e in (self.ui.name_edit, self.ui.number_edit, self.ui.vehcle_line,
                  self.ui.ro_created_edit, self.ui.ro_approved_edit):
            e.setReadOnly(True)


        view = self.ui.ro_items_table
        m = None
        try:
            m = view.model()
        except Exception:
            m = None
        if m is not None:
            self.connect_ro_model_signals(m)

        if hasattr(view, "modelAttached"):
            view.modelAttached.connect(self.connect_ro_model_signals)

        if hasattr(view, "jobsChanged"):
            view.jobsChanged.connect(self.autosaver.mark_dirty)

        if hasattr(self.ui, "notes_text_edit"):
            self.ui.notes_text_edit.textChanged.connect(self.autosaver.mark_dirty)

        # miles edits
        if hasattr(self.ui, "miles_in_edit"):
            self.ui.miles_in_edit.editingFinished.connect(self.autosaver.mark_dirty)
        if hasattr(self.ui, "miles_out_edit"):
            self.ui.miles_out_edit.editingFinished.connect(self.autosaver.mark_dirty)

        # tax / labor rate changes
        if hasattr(self.ui, "tax_box"):
            self.ui.tax_box.currentIndexChanged.connect(self.autosaver.mark_dirty)
        if hasattr(self.ui, "labor_rate_box"):
            self.ui.labor_rate_box.currentIndexChanged.connect(self.autosaver.mark_dirty)

        if hasattr(self.ui, "place_order_button"):
            try:
                self.ui.place_order_button.clicked.connect(self.autosaver.flush_if_dirty)
            except Exception:
                pass

        # add/remove item buttons
        self.ui.add_job_item_button.clicked.connect(self.autosaver.mark_dirty)
        self.ui.remove_item_button.clicked.connect(self.autosaver.mark_dirty)

        # new job button
        self.ui.new_job_button.clicked.connect(self.autosaver.mark_dirty)
        self.ui.mpi_button.clicked.connect(self.mpi_manager.setup_ui)






    def _toggle_3c_stack(self, index: int, checked: bool):
        if checked:
            self.ui.three_c_stacked.setCurrentIndex(index)


    # Defensive action to reinforce moving tiles around between open, working, checkout
    def _on_status_changed(self):
        QtCore.QTimer.singleShot(0, self.ui.repair_orders_manager.refresh_all)


    # span multiple controllers
    def load_ro_into_hub(self, ro_id: int):
        try: self.autosaver.pause()
        except Exception: pass
        self.ui.current_ro_id = ro_id
        ro_data = RepairOrdersRepository.get_repair_order_by_id(ro_id)
        customer = CustomerRepository.get_customer_info_by_id(ro_data["customer_id"])
        vehicle  = VehicleRepository.get_vehicle_info_for_new_ro(ro_data["customer_id"])
        dates_miles = RepairOrdersRepository.get_create_altered_date(ro_id)
        self.ui.name_edit.setText(f"{customer['first_name']} {customer['last_name']}")
        self.ui.ro_number_label.setText(ro_data["ro_number"])
        self.ui.number_edit.setText(customer["phone"])
        self.ui.vehcle_line.setText(f"{vehicle['vin']}   {vehicle['year']}   {vehicle['make']}   {vehicle['model']}")
        self.ui.ro_hub_tabs.setCurrentIndex(0)

        created_qdt = _to_qdatetime(dates_miles.get("created_at"))
        updated_qtd = _to_qdatetime(dates_miles.get("updated_at"))
        ro_status = dates_miles.get("status")
        miles_in = str(dates_miles.get("miles_in"))
        miles_out = str(dates_miles.get("miles_out"))

        self.ui.ro_status_label.setText(ro_status.upper())
        self.ui.miles_in_edit.setText(miles_in)
        self.ui.miles_out_edit.setText(miles_out)

        if miles_in == "None":
            self.ui.miles_in_edit.setText("")

        if miles_out == "None":
            self.ui.miles_out_edit.setText("")

        style = self.ui.style()

        if created_qdt.isValid():
            self.ui.ro_created_edit.setDateTime(created_qdt)
            self.ui.ro_approved_edit.setDateTime(updated_qtd)
        else:
            self.ui.ro_created_edit.clear()
            self.ui.ro_approved_edit.clear()

        if hasattr(self, "c3"):
            self.c3.set_ro_id(ro_id)

        # delegate staff select resolution to the staff controller
        self.staff.sync_selects_from_ro(ro_data)
        self._load_estimate_items(ro_id)
        est_id = getattr(self.ui.ro_items_table, "current_estimate_id", None) or 0
        vin = (self.ui.vehcle_line.text() or "").split()[0] if self.ui.vehcle_line.text() else ""
        self.roContextReady.emit(ro_id, int(est_id), vin)
        self._update_ro_status_label(ro_id)
        self.status.refresh_button()
        try: self.autosaver.resume()
        except Exception: pass

    def _load_estimate_items(self, ro_id: int):
        tree  = self.ui.ro_items_table
        self.ui.ro_items_table.current_ro_id = ro_id
        est_id = RepairOrdersRepository.estimate_id_for_ro(ro_id)
        self.ui.ro_items_table.current_estimate_id = est_id
        memo = EstimatesRepository.get_internal_memo(est_id) or "" if est_id else ""
        self.ui.notes_text_edit.blockSignals(True)
        self.ui.notes_text_edit.setPlainText(memo)
        self.ui.notes_text_edit.blockSignals(False)

        # --- Preserve expansion & selection BEFORE clearing ---
        expanded = {}
        selected_path = {"job": None, "child_index": None}

        if tree.topLevelItemCount() > 0:
            for i in range(tree.topLevelItemCount()):
                job_item = tree.topLevelItem(i)
                key = job_item.data(0, JOB_NAME_ROLE) or tree._base_name(job_item.text(0))
                expanded[key] = job_item.isExpanded()

            cur = tree.currentItem()
            if cur:
                if cur.parent() is None:
                    selected_path["job"] = tree._base_name(cur.text(0))
                else:
                    selected_path["job"] = tree._base_name(cur.parent().text(0))
                    selected_path["child_index"] = cur.parent().indexOfChild(cur)

        # --- Block signals/updates during rebuild ---
        prev_block = tree.blockSignals(True)
        prev_updates = tree.updatesEnabled()
        tree.setUpdatesEnabled(False)

        try:
            tree.clear()

            # Pull items (joined to jobs) and jobs (to include empty jobs)
            rows = EstimateItemsRepository.list_for_ro(ro_id) or []

            try:
                job_rows = EstimateJobsRepository.list_for_estimate(est_id) if est_id else []
            except Exception:
                job_rows = []

            # Bucket items by canonical job name
            from collections import defaultdict
            jobs = defaultdict(list)
            for r in rows:
                nm = tree._base_name(r.get("job_name") or "New Job") or "New Job"
                jobs[nm].append(r)

            # Ensure empty jobs render
            for j in job_rows:
                nm = tree._base_name(j.get("name") or "New Job") or "New Job"
                if nm not in jobs:
                    jobs[nm] = []

            if not jobs:
                return  # nothing to render


            pos_hint = {(j.get("name") or "New Job"): idx for idx, j in enumerate(job_rows)}

            def job_sort_key(name: str):
                # look for any line that has job_order
                sample = next((x for x in jobs[name] if x.get("job_order") is not None), None)
                if sample is not None:
                    try:
                        return (0, int(sample.get("job_order") or 0), name.lower())
                    except Exception:
                        return (0, 0, name.lower())
                # fallback to job_rows position (or a large number)
                return (1, int(pos_hint.get(name, 10_000)), name.lower())

            for job_name in sorted(jobs.keys(), key=job_sort_key):
                # Create job header
                job_item = tree.addJob(job_name)

                # Determine job_id + status from either items or job_rows
                lines = jobs[job_name]
                job_id = None
                job_status = ""

                if lines:
                    job_id = lines[0].get("job_id")
                    job_status = (lines[0].get("job_status") or "").lower()
                    # if items carry job_order, you can put it on a role if you like
                else:
                    jr = next((j for j in job_rows if (j.get("name") or "").strip() == job_name), None)
                    if jr:
                        job_id = jr.get("id")
                        job_status = (jr.get("status") or "").lower()

                if job_id is not None:
                    job_item.setData(0, JOB_ID_ROLE, int(job_id))
                job_item.setData(0, JOB_NAME_ROLE, job_name)

                # Paint approved/declined decoration in header
                job_item.setText(0, job_name)  # raw, undecorated
                job_item.setData(0, APPROVED_ROLE, job_status == "approved")
                job_item.setData(0, DECLINED_ROLE, job_status == "declined")

                # Sort lines within job by line_order (stable)
                lines.sort(key=lambda x: int(x.get("line_order") or 0))

                # Render lines (skip truly empty placeholders)
                for ln in lines:
                    # Normalize the DB type; prefer 'type' column
                    t = (ln.get("type") or ln.get("row_type") or "").strip().lower()
                    desc = (ln.get("item_description") or ln.get("description") or "").strip()

                    def _f(key, default=0.0):
                        v = ln.get(key, None)
                        if v in ("", None):
                            return default
                        try:
                            return float(v)
                        except (TypeError, ValueError):
                            return default

                    qty = _f("qty", 0.0)
                    unit_cost = _f("unit_cost", 0.0)
                    unit_price = _f("unit_price", 0.0)
                    sku = ln.get("sku_number") or ""
                    tax_pct = _f("tax_pct", None)
                    if tax_pct is None:
                        tax_pct = _f("tax_rate", 0.0)


                    # Skip empty lines
                    if not desc and qty == 0.0 and unit_cost == 0.0:
                        continue

                    item_id = ln.get("id")
                    line_order = int(ln.get("line_order") or 0)

                    if t == "labor":
                        # For labor, qty is hours and unit_price is rate
                        tree.addLabor(job_item,
                                      description=desc,
                                      hours=qty,
                                      rate=unit_price,
                                      tax_pct=tax_pct,
                                      sku=sku,
                                      item_id=item_id,
                                      line_order=line_order)
                    elif t in ("part", "tire", "fee", "sublet"):
                        if t == "part":
                            tree.addPart(job_item, description=desc, qty=qty, 
                                         unit_cost=unit_cost, unit_price=unit_price, tax_pct=tax_pct, sku=sku,
                                         row_type="PART", item_id=item_id, line_order=line_order)
                        elif t == "tire":
                            tree.addTire(job_item, description=desc, qty=qty, 
                                         unit_cost=unit_cost, unit_price=unit_price, tax_pct=tax_pct, sku=sku,
                                         item_id=item_id, line_order=line_order)
                        elif t == "fee":
                            tree.addFee(job_item, description=desc, qty=qty, 
                                        unit_cost=unit_cost, unit_price=unit_price, tax_pct=tax_pct, sku=sku,
                                        item_id=item_id, line_order=line_order)
                        else:
                            tree.addSublet(job_item, description=desc, qty=qty, 
                                           unit_cost=unit_cost, unit_price=unit_price, tax_pct=tax_pct, sku=sku,
                                           item_id=item_id, line_order=line_order)
                    else:
                        # Unknown kind -> treat as part
                        tree.addPart(job_item, description=desc, qty=qty, 
                                     unit_cost=unit_cost, unit_price=unit_price,
                                     row_type="PART", item_id=item_id, line_order=line_order, tax_pct=tax_pct, sku=sku,)

                # Ensure one subtotal row and restore expansion
                tree._ensureJobSubtotal(job_item)
                key = job_item.data(0, JOB_NAME_ROLE) or tree._base_name(job_item.text(0))
                job_item.setExpanded(expanded.get(key, True))




            # --- Restore selection AFTER rebuild ---
            if selected_path["job"] is not None:
                for i in range(tree.topLevelItemCount()):
                    job = tree.topLevelItem(i)
                    base = job.data(0, JOB_NAME_ROLE) or tree._base_name(job.text(0))
                    if base == selected_path["job"]:
                        if selected_path["child_index"] is None or job.childCount() == 0:
                            tree.setCurrentItem(job)
                        else:
                            idx = min(selected_path["child_index"], max(0, job.childCount() - 1))
                            child = job.child(idx) if job.childCount() else job
                            tree.setCurrentItem(child)
                        break

        finally:
            tree.blockSignals(prev_block)
            tree.setUpdatesEnabled(prev_updates)

        # Fit “Type” column and repaint
        type_col = tree._col_index("Type")
        tree.resizeColumnToContents(type_col)
        tree.viewport().update()

        model = self.ui.ro_items_table.model()
        if hasattr(model, "sanitize_job_headers"):
            model.sanitize_job_headers()

        QtCore.QTimer.singleShot(0, lambda: (
            tree.selectionModel().clearSelection(),
            tree.setCurrentIndex(QtCore.QModelIndex()),
            tree.clearFocus()
        ))
        if hasattr(self, "totals"):
            QtCore.QTimer.singleShot(0, self.totals._recompute_and_render_totals)

    def _reload_after_job_change(self):
        return

    def _new_job(self):
        self.autosaver.pause()
        job = self.ui.ro_items_table.addJob("New Job")
        if job is not None:
            QtCore.QTimer.singleShot(0, lambda: self.ui.ro_items_table.editItem(job, COL_TYPE))


    def _sync_approval_to_db_and_refresh(self, ro_id:int):
        tree = self.ui.ro_items_table
        m = tree.model()
        rows = m.rowCount(QtCore.QModelIndex())
        user_id = getattr(self.ui, "current_user_id", None)

        for r in range(rows):
            job_idx = m.index(r, 0)
            job_id = job_idx.data(JOB_ID_ROLE)
            if not job_id:
                continue
            approved = bool(job_idx.data(APPROVED_ROLE))
            declined = bool(job_idx.data(DECLINED_ROLE))
            status = "approved" if approved else ("declined" if declined else "proposed")
            EstimateJobsRepository.set_status(job_id, status, by_user_id=user_id)

        RepairOrdersRepository.recompute_ro_approval(ro_id)
        self._update_ro_status_label(ro_id)
        self.status.refresh_button()


    def _update_ro_status_label(self, ro_id: int):
        tree = self.ui.ro_items_table
        m = tree.model()
        root = QtCore.QModelIndex()
        rows = m.rowCount(root)
        label = self.ui.ro_status_label
        style = self.ui.style()

        dates_miles = RepairOrdersRepository.get_create_altered_date(ro_id)
        status = (dates_miles.get("status") or "open").strip().lower()
        approved_at = RepairOrdersRepository.get_approved_at(ro_id)
        total, approved, _declined = RepairOrdersRepository.jobs_counts_for_ro(ro_id)

        if approved_at:
            qdt = _to_qdatetime(approved_at)
            stamp = qdt.toString("MM/dd/yyyy h:mmAP")
            label.setText(f"APPROVED: {stamp}")
            label.setObjectName("approved_label")
        elif total and 0 < approved < total:
            updated_qdt = _to_qdatetime(dates_miles.get("updated_at"))
            stamp = updated_qdt.toString("MM/dd/yyyy h:mmAP") if updated_qdt.isValid() else ""
            label.setText(f"PARTIALLY APPROVED {approved}/{total} JOBS: " + (f"   {stamp}" if stamp else ""))
            label.setObjectName("partial_label")


        else:
            # Fall back to the RO's own lifecycle status
            mapping = {
                "open": ("OPEN", "open_label"),
                "working": ("WORKING", "working_label"),
                "checkout": ("CHECKOUT", "checkout_label"),
                "archived": ("ARCHIVED", "archived_label"),
            }
            text, objname = mapping.get(status, ("OPEN", "open_label"))
            label.setText(text)
            label.setObjectName(objname)

        if  status == "working":
            updated_qdt = _to_qdatetime(dates_miles.get("updated_at"))
            stamp = updated_qdt.toString("MM/dd/yyyy h:mmAP") if updated_qdt.isValid() else ""
            label.setText(f"WORK STARTED: {stamp}" if stamp else "")
            label.setObjectName("working_label")

        elif status == "checkout":
            updated_qdt = _to_qdatetime(dates_miles.get("updated_at"))
            stamp = updated_qdt.toString("MM/dd/yyyy h:mmAP") if updated_qdt.isValid() else ""
            label.setText(f"READY FOR CHECKOUT: {stamp}" if stamp else "")
            label.setObjectName("checkout_label")

        style.unpolish(label)
        style.polish(label)

    def connect_ro_model_signals(self, model):
        if getattr(model, "_oa_mark_dirty_wired", False):
            return
        try:
            model.dataChanged.connect(lambda *_: self.autosaver.mark_dirty(),
                                      QtCore.Qt.ConnectionType.UniqueConnection)
        except TypeError:
            model.dataChanged.connect(lambda *_: self.autosaver.mark_dirty())
        try:
            model.rowsInserted.connect(lambda *_: self.autosaver.mark_dirty(),
                                       QtCore.Qt.ConnectionType.UniqueConnection)
        except TypeError:
            model.rowsInserted.connect(lambda *_: self.autosaver.mark_dirty())
        try:
            model.rowsRemoved.connect(lambda *_: self.autosaver.mark_dirty(),
                                      QtCore.Qt.ConnectionType.UniqueConnection)
        except TypeError:
            model.rowsRemoved.connect(lambda *_: self.autosaver.mark_dirty())
        try:
            model._oa_mark_dirty_wired = True
        except Exception:
            pass


    def on_estimate_saved(self, est_id: int):
        try:
            self.ui.current_estimate_id = int(est_id)
            self.ui.ro_items_table.current_estimate_id = int(est_id)
        except Exception:
            pass
