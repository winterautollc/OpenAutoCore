from datetime import datetime
from PyQt6.QtCore import Qt, QObject, QTimer, QModelIndex
from openauto.utils.log_sanitizer import scrub, mask_sid
from openauto.managers.parts_tree.go_sidecar_manager import GoSidecarManager
from openauto.managers.parts_tree.auth_token import get_valid_token
from pathlib import Path
from openauto.managers.parts_tree.sessions_cache import SessionsCache
from PyQt6.QtWidgets import QMessageBox
from openauto.subclassed_widgets.models.parts_tree_model import PartsTreeModel
from openauto.managers.parts_tree.parts_tree_loader import PartsTreeLoader
from openauto.repositories.parts_tree_repository import PartsTreeRepository
from openauto.managers.ro_hub.save_estimate_service import SaveEstimateService
from openauto.repositories.repair_orders_repository import RepairOrdersRepository
from openauto.repositories.estimates_repository import EstimatesRepository
from openauto.managers.parts_tree.parts_item_controller import PartsItemController
from openauto.managers.parts_tree import api_pt_callbacks
from dotenv import load_dotenv
import re
import os

USE_JSON_WATCH = False

ENV_PATH = (Path(__file__).parent / ".env").resolve()
try:
    load_dotenv(dotenv_path=str(ENV_PATH))
except Exception:
    pass

QUOTES_DIR = str((Path(__file__).parent / "data" / "quotes").resolve())
PTCLI  = str((Path(__file__).parent / "ptcli").resolve())
API    = os.getenv("QU_VSM")
PUBLIC = os.getenv("QU_UVOOFM")
LOCAL = "http://127.0.0.1:8000"


class PartsHubManager(QObject):
    def __init__(self, ui):
        super().__init__()
        self._is_active = False
        self.ui = ui
        self._ptcli_available = Path(PTCLI).is_file()

        self.ro_hub_index = 8
        self.set_active(self.ui.hub_stacked_widget.currentIndex() == self.ro_hub_index)
        self.ui.hub_stacked_widget.currentChanged.connect(lambda i: self.set_active(i == self.ro_hub_index))

        try:
            self.ui.quote_browser.closedWithSuccess.connect(self._hide_quote_overlay, Qt.ConnectionType.UniqueConnection)
        except Exception:
            pass

        self.current_ro_id = None
        self.current_estimate_id = None
        self.current_vin = None
        self.modal_open = False
        self.show_debug_modals = True
        self.last_debug_signal = None
        self.last_debug_ts = 0
        self._awaiting_submit = False
        self._awaiting_submit_sid = None
        self._active_pt_session_id = None
        self.parts_model = PartsTreeModel()
        self.parts_repo = PartsTreeRepository()
        self.sessions = SessionsCache()
        self.ui.parts_tree.setModel(self.parts_model)
        self.ui.parts_tree.partActionRequested.connect(self._on_part_action, Qt.ConnectionType.UniqueConnection)
        self.parts_loader = PartsTreeLoader(model=self.parts_model, repo=self.parts_repo,
                                            quotes_dir=QUOTES_DIR, use_json_fallback=False)

        self.ui.ro_hub_manager.roContextReady.connect(self._on_ro_context_ready)
        self.sidecar = GoSidecarManager(PTCLI, parent=self.ui, public_base=PUBLIC, local_return_base=LOCAL)

        self.parts_controller = PartsItemController (
            tree_view=self.ui.parts_tree,
            tree_model=self.parts_model,
            sidecar=self.sidecar,
            parts_repo=self.parts_repo,
            get_token=self._current_token,
            get_session_id=self._current_session_id,
            parent=self
        )

        try:
            self.sidecar.debugText.disconnect()
            self.sidecar.errorText.disconnect()
        except Exception:
            pass

        self.sidecar.debugText.connect(lambda s: self.ui.log_console.append_line(scrub(s)))
        self.sidecar.errorText.connect(lambda s: self.on_pt_error_details(scrub(s)))
        self.sidecar.errorText.connect(self.on_pt_error_details)

        self.connect_signals()


    def set_active(self, active: bool):
        if self._is_active and not bool(active):
            try:
                self.ui.ro_hub_manager.autosaver.flush_if_dirty()
            except Exception:
                pass
        self._is_active = bool(active)

    def ensure_active(self) -> bool:
        return self._is_active

    def _on_ro_context_ready(self, ro_id: int, estimate_id: int, vin: str):
        self.current_ro_id = ro_id
        self.current_estimate_id = estimate_id
        self.current_vin = vin

        try:
            self.sidecar.set_default_estimate_id(estimate_id)
        except Exception:
            pass

        self._load_parts_tree(est_id=self.current_estimate_id, mode="replace")


    def connect_signals(self):
        try:
            self.ui.place_order_button.setAutoDefault(False)
            self.ui.place_order_button.setDefault(False)
        except Exception:
            pass

        self.ui.order_parts_button.clicked.connect(self.open_parts_browser)
        self.ui.place_order_button.clicked.connect(self.on_place_order_clicked)
        self.ui.delete_parts_button.clicked.connect(self.parts_controller.delete_selected)

        try:
            self.sidecar.cartUpdated.disconnect()
            self.sidecar.cartSubmitted.disconnect()
            self.sidecar.partRemoved.disconnect()
        except Exception:
            pass

        self.sidecar.cartSubmitted.connect(self._on_cart_submitted, Qt.ConnectionType.UniqueConnection)

        self.sidecar.partRemoved.connect(
            self.parts_controller.on_part_removed, Qt.ConnectionType.UniqueConnection
        )


        self.sidecar.partRemoved.connect(
            lambda _p: self._on_parts_tree_update(self.current_estimate_id),
            Qt.ConnectionType.UniqueConnection,
        )

        try:
            self.ui.quote_browser.closedWithSuccess.disconnect()
        except Exception:
            pass
        self.ui.quote_browser.closedWithSuccess.connect(
            self._on_quote_browser_closed_success, Qt.ConnectionType.UniqueConnection
        )


    def _show_quote_overlay(self):
        self.current_index = self.ui.hub_stacked_widget.currentIndex()
        self.ui.quote_page.show()
        self.ui.hub_stacked_widget.setCurrentIndex(self.ui.quote_page_index)

    def _hide_quote_overlay(self):
        self.ui.quote_page.hide()
        self.ui.hub_stacked_widget.setCurrentIndex(self.current_index)

    def _on_parts_tree_update(self, est_id: int):
        if not self.current_estimate_id or int(est_id) != int(self.current_estimate_id):
            return
        if getattr(self, "_pt_cooldown", None) and self._pt_cooldown.isActive():
            self._pt_pending = est_id
            return
        self._load_parts_tree(est_id, mode="merge")
        self._start_pt_cooldown(est_id)

    def _start_pt_cooldown(self, est_id: int):
        from PyQt6.QtCore import QTimer
        self._pt_pending = None
        t = getattr(self, "_pt_cooldown", None)
        if t is None:
            t = QTimer(self)
            t.setSingleShot(True)
            t.timeout.connect(self._flush_pt_pending)
            self._pt_cooldown = t
        t.start(350)  # 350ms

    def _flush_pt_pending(self):
        if self._pt_pending is not None:
            self._load_parts_tree(self._pt_pending, mode="merge")
            self._pt_pending = None

    def _load_parts_tree(self, est_id: int, *, mode: str = "merge"):
        self.parts_loader.load(ui=self.ui, estimate_id=est_id,
                               mode=mode, fallback_to_newest=False)

    def _sync_db_from_payload(self, payload: dict):
        raw = (payload or {}).get("Raw") or payload or {}
        sid = (raw.get("sessionId") or raw.get("sessionID") or "").strip()
        orders = raw.get("orders")
        if not (sid and isinstance(orders, list)):
            return
        est = int(self.current_estimate_id) if self.current_estimate_id else None
        api_pt_callbacks._upsert(raw, estimate_id=est, default_status="quoted")

    def open_parts_browser(self):
        if not self.ensure_active():
            return
        if not self._ptcli_available:
            self.show_message_box(
                icon=QMessageBox.Icon.Warning,
                title="PartsTech",
                text="Parts ordering is disabled because the PartsTech helper (ptcli) is not installed."
            )
            return
        cache = self.sessions
        vin = (self.current_vin or "").strip() or None
        if not vin or len(vin) != 17:
            try:
                raw = getattr(self.ui, "vehcle_line", None).text()
                vin = (raw or "").split()[0]
            except Exception:
                vin = ""

        if not vin or len(vin) != 17:
            self.show_message_box(icon=QMessageBox.Icon.Warning, title="PartsTech", text="No VIN is on this Repair Order")

        self.current_ro_id = self.current_ro_id or getattr(self.ui, "current_ro_id", None)
        if not self.current_ro_id:
            self.show_message_box(icon=QMessageBox.Icon.Warning, title="Partstech",
                                  text="Open a Repair Order in RO Hub before ordering parts.")
            return

        if not self.current_estimate_id or int(self.current_estimate_id) <= 0:
            est_id = SaveEstimateService(self.ui).save(silent=True)
            if not est_id:
                return
            self.current_estimate_id = int(est_id)

        def _present(redirect_url: str):
            self.ui.quote_browser.load(redirect_url, f"{LOCAL}/done")
            self._show_quote_overlay()

        sess_from_estimate = cache.find_session_for_estimate(self.current_estimate_id, vin=vin)
        if sess_from_estimate and self.parts_repo.session_has_ordered_items(sess_from_estimate):
            sess_from_estimate = None
        if not sess_from_estimate and self.current_estimate_id and int(self.current_estimate_id) > 0:
            candidate = self.parts_repo.latest_session_for_estimate(self.current_estimate_id, vin=vin)
            if candidate and not self.parts_repo.session_has_ordered_items(candidate):
                sess_from_estimate = candidate
        if sess_from_estimate:
            self._active_pt_session_id = sess_from_estimate

            self.sessions.set_session_link(
                session_id=sess_from_estimate,
                estimate_id=int(self.current_estimate_id),
                ro_id=int(self.current_ro_id or 0),
                vin=(vin or "")
            )

            redirect = cache.get_redirect(vin or "") or cache.build_redirect_url(
                partner_id=os.getenv("QU_QBSUOFS_JE"),
                user_id=os.getenv("QU_VTFS_JE"),
                session_id=sess_from_estimate
            )

            cache.put_redirect(vin or "", sess_from_estimate, redirect)
            _present(redirect)
            token = self._current_token()
            self.sidecar.fetch_cart(token=token, session_id=sess_from_estimate, timeout_s=20)
            return

        def _open_on_update(payload: dict):
            raw = (payload or {}).get("Raw") or payload or {}
            redirect = (raw.get("redirectUrl") or raw.get("RedirectURL") or "").strip()
            session_id = (raw.get("sessionId") or raw.get("sessionID") or "").strip()
            self._active_pt_session_id = session_id
            if redirect:
                self.sessions.set_session_link(
                    session_id=session_id,
                    estimate_id=int(self.current_estimate_id),
                    ro_id=int(self.current_ro_id),
                    vin=(self.current_vin or "")
                )
                self.sessions.put_redirect(self.current_vin or "", session_id, redirect)
                self.ui.quote_browser.load(redirect, f"{LOCAL}/done")
                self._show_quote_overlay()

            try:
                est = int(self.current_estimate_id) if self.current_estimate_id else None
                api_pt_callbacks._upsert(raw, estimate_id=est, default_status="quoted")
            except Exception:
                pass

            try:
                self.sidecar.cartUpdated.disconnect(_open_on_update)
            except Exception:
                pass

        self.sidecar.cartUpdated.connect(_open_on_update, Qt.ConnectionType.UniqueConnection)

        self.sidecar.create_cart(
            token=self._current_token(),
            vin=vin,
            part_type_ids=[0],
            keyword="Air Filter",
            po_number=self._po_number_for_current_ro(),
            api_base=os.getenv("QU_CBTF"),
            timeout_s=25,
        )




        reused = cache.get_redirect(vin) if vin else None
        if reused:
            _present(reused)
            sid = cache.get_session_id(vin)
            if sid:
                token = self._current_token()
                self.sidecar.fetch_cart(token=token, session_id=sid, timeout_s=20)
            return


    def _current_session_id(self) -> str | None:
        cache = self.sessions

        est_id = int(self.current_estimate_id or 0)
        vin_hint = (self.current_vin or "").strip()

        if est_id > 0:
            s = cache.find_session_for_estimate(est_id, vin=vin_hint or None)
            if s:
                return str(s)

            s = self.parts_repo.latest_session_for_estimate(est_id, vin=vin_hint or "")
            if s:
                cache.set_session_link(
                    session_id=str(s),
                    ro_id=int(self.current_ro_id or 0),
                    estimate_id=est_id,
                    vin=vin_hint or ""
                )
                return str(s)

        vin = (
                self.current_vin
                or (getattr(self.ui, "vehicle_line", None) and self.ui.vehicle_line.text().split()[0])
                or (getattr(self.ui, "vehcle_line", None) and self.ui.vehcle_line.text().split()[0])
                or ""
        ).strip()

        if len(vin) != 17:
            return None

        s = cache.get_session_id(vin)
        if s:
            return str(s)

        if est_id > 0:
            s = self.parts_repo.latest_session_for_estimate(est_id, vin=vin)
            if s:
                cache.set_session_link(
                    session_id=str(s),
                    ro_id=int(self.current_ro_id or 0),
                    estimate_id=est_id,
                    vin=vin
                )
                return str(s)

        return None

    def _current_token(self) -> str:
        if not self._ptcli_available:
            return ""
        try:
            return get_valid_token(
                PTCLI,
                API,
                partner_id=os.getenv("QU_QBSUOFS_JE"),
                partner_key=os.getenv("QU_QBSUOFS_LFZ"),
                user_id=os.getenv("QU_VTFS_JE"),
                user_key=os.getenv("QU_VTFS_LFZ"),
                force_refresh=False,
            )
        except Exception:
            return ""


    def on_place_order_clicked(self):
        try:
            if not self.current_estimate_id or int(self.current_estimate_id) <= 0:
                SaveEstimateService(self.ui).save(silent=True)
                self.current_estimate_id = RepairOrdersRepository.estimate_id_for_ro(self.current_ro_id) \
                                           or (EstimatesRepository.get_by_ro_id(self.current_ro_id) or {}).get("id")
        except Exception:
            pass

        session = self._active_pt_session_id
        if not session and (self.current_vin or ""):
            session = self.sessions.get_session_id(self.current_vin or "")
        if not session:
            candidate = self.parts_repo.latest_session_for_estimate(self.current_estimate_id,
                                                                    vin=(self.current_vin or ""))
            if candidate and not self.parts_repo.session_has_ordered_items(candidate):
                session = candidate

        if not session:
            session = self._current_session_id()
        token = self._current_token()
        if not token:
            self.show_message_box(
                icon=QMessageBox.Icon.Warning,
                title="PartsTech",
                text="Parts ordering is disabled because the PartsTech helper (ptcli) is not available or misconfigured."
            )
            return
        po = self._po_number_for_current_ro()
        self.ui.log_console.append_line("[debug] Place Order clicked (explicit handler)")

        self._awaiting_submit = True
        self._awaiting_submit_sid = session
        self.ui.log_console.append_line(f"[debug] submit-cart in flight for sid={session}")
        self.sidecar.submit_cart(token=token, session_id=session, po=po)


    def _on_quote_browser_closed_success(self):
        self._hide_quote_overlay()
        if self.current_estimate_id:
            self._load_parts_tree(est_id=int(self.current_estimate_id), mode="replace")



    def _on_cart_updated(self, payload: dict):
        raw = (payload or {}).get("Raw") or {}
        self.parts_controller.add_from_payload(raw)


    def _on_cart_submitted(self, payload: dict):
        op = (payload or {}).get("op", "").lower()
        sid_from_payload = (payload or {}).get("sessionId") or ""
        self._active_pt_session_id = None
        if not self._awaiting_submit:
            self.ui.log_console.append_line("[debug] cartSubmitted ignored (no submit in flight)")
            return
        if self._awaiting_submit_sid and sid_from_payload and sid_from_payload != self._awaiting_submit_sid:
            self.ui.log_console.append_line(
                f"[debug] cartSubmitted ignored (sid mismatch {sid_from_payload} != {self._awaiting_submit_sid})")
            return

        self._awaiting_submit = False
        self._awaiting_submit_sid = None

        if payload and payload.get("raw"):
            self._sync_db_from_payload(payload["raw"])

        sid = sid_from_payload or self.parts_repo.latest_session_for_estimate(self.current_estimate_id)
        if sid:
            try:
                self.parts_repo.update_items_status(session_id=sid, order_item_id=None, status="ordered")
            except Exception:
                pass
        try:
            vin = self.current_vin or self.sessions.get_vin(sid) or ""
            if vin:
                self.sessions.clear_for_vin(vin)
            if sid:
                self.sessions.clear_session(sid)
        except Exception:
            pass

        self._load_parts_tree(est_id=self.current_estimate_id, mode="replace")
        self.show_message_box(icon=QMessageBox.Icon.Information, title="PartsTech", text="Order submitted.")


    def _po_number_for_current_ro(self) -> str:
        ro_id = (
                getattr(self, "current_ro_id", None)
                or getattr(self.ui, "current_ro_id", None)
                or getattr(self.ui, "ro_id", None)
        )

        est_id = (
                getattr(self, "current_estimate_id", None)
                or getattr(self.ui, "current_estimate_id", None)
                or getattr(self.ui, "estimate_id", None)
        )

        vin = (
                getattr(self, "current_vin", None)
                or getattr(self.ui, "current_vin", None)
                or ""
        )
        vin_tail = (vin[-6:].upper() if isinstance(vin, str) and len(vin) >= 6 else "")

        if ro_id:
            base = f"RO-{ro_id}"
        elif est_id:
            base = f"EST-{est_id}"
        else:
            base = "ORDER-" + datetime.now().strftime("%Y%m%d-%H%M%S")

        if vin_tail:
            base = f"{base}-{vin_tail}"

        po = re.sub(r"[^A-Z0-9\-_]+", "-", str(base).upper()).strip("-_")
        if len(po) > 32:
            po = po[:32].rstrip("-_")
        return po or "ORDER"


    def on_pt_error_details(self, msg: str):
        from datetime import datetime
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        vin = self.current_vin or getattr(self.ui, "current_vin", "") or ""
        ro_id = self.current_ro_id or getattr(self.ui, "current_ro_id", None)
        est_id = self.current_estimate_id or getattr(self.ui, "current_estimate_id", None)
        sess = self._current_session_id() or ""

        details = (
            f"Timestamp: {ts}\n"
            f"VIN: {vin}\n"
            f"RO ID: {ro_id}\n"
            f"Estimate ID: {est_id}\n"
            f"Session ID: {sess}\n\n"
            f"Error:\n{msg}"
        )

        self.show_modal_with_details("PartsTech", msg, details, QMessageBox.Icon.Critical)

    def _on_part_action(self, msg: dict):
        op = msg.get("op")
        sid = msg.get("session_id")
        oi = msg.get("order_item_id")
        if op == "remove-part":
            self._act_remove_part(sid, oi, token=self._current_token())
        elif op == "mark-returned":
            self._act_mark_returned(sid, oi)
        elif op == "mark-received":
            self._act_mark_received(sid, oi)
        elif op == "mark-cancelled":
            self._act_mark_cancelled(sid, oi)
        elif op == "assign-to-job":
            self._act_assign_to_job(msg)
        elif op == "assign-to-new-job":
            self._act_assign_to_new_job(msg)

    def _act_remove_part(self, session_id: str, order_item_id: str, token: str):
        self.parts_controller.delete_selected()


    def _act_mark_returned(self, session_id: str, order_item_id: str):
        sid = session_id or self.parts_repo.get_session_for_order_item(order_item_id) or self._current_session_id()
        if not (sid and order_item_id):
            return
        self.parts_repo.update_items_status(session_id=sid, order_item_id=order_item_id, status="returned")
        self._load_parts_tree(est_id=self.current_estimate_id, mode="replace")

    def _act_mark_received(self, session_id: str, order_item_id: str):
        sid = session_id or self.parts_repo.get_session_for_order_item(order_item_id) or self._current_session_id()
        if not (sid and order_item_id):
            return
        self.parts_repo.update_items_status(session_id=sid, order_item_id=order_item_id, status="received")
        self._load_parts_tree(est_id=self.current_estimate_id, mode="replace")

    def _act_mark_cancelled(self, session_id: str, order_item_id: str):
        sid = session_id or self.parts_repo.get_session_for_order_item(order_item_id) or self._current_session_id()
        if not (sid and order_item_id):
            return
        self.parts_repo.update_items_status(session_id=sid, order_item_id=order_item_id, status="cancelled")
        self._load_parts_tree(est_id=self.current_estimate_id, mode="replace")

    def _add_fields_to_job(self, job_row: int, fields: dict):
        view = self.ui.ro_items_table
        m = view.model()
        root = QModelIndex()
        if m.rowCount(root) == 0:
            view.addJob("New Job")

        job_row = max(0, min(job_row, m.rowCount(root) - 1))
        job_idx = m.index(job_row, 0, root)

        view.addPart(
            job_item=job_idx,
            description=str(fields.get("description") or "New Part"),
            qty=str(fields.get("qty") or "1"),
            unit_cost=f"{float(fields.get('unit_cost') or 0.0):.2f}",
            unit_price=f"{float(fields.get('unit_price') or 0.0):.2f}",
            tax_pct=float(fields.get("tax_pct") or 0.0),
            sku=str(fields.get("sku") or ""),
            row_type="PART",
        )
        try:
            self.ui.ro_hub_manager.autosaver.mark_dirty()
        except Exception:
            pass

    def _act_assign_to_job(self, msg: dict):
        fields = msg.get("fields") or {}
        job_row = int(msg.get("job_row") or 0)
        self._add_fields_to_job(job_row, fields)

        try:
            ro_view = getattr(self.ui, "ro_items_table", None)
            jobs = ro_view.current_jobs() if ro_view and hasattr(ro_view, "current_jobs") else []
            job_name = (jobs[job_row].get("job_name") if 0 <= job_row < len(jobs) else "New Job") or "New Job"
            job_id = (int(jobs[job_row].get("job_id")) if 0 <= job_row < len(jobs) and jobs[job_row].get(
                "job_id") is not None else None)
            oid = str(msg.get("order_item_id") or "")
            if oid and hasattr(self.parts_model, "set_assigned_job_by_order_item_id"):
                self.parts_model.set_assigned_job_by_order_item_id(oid, job_name)

            if hasattr(self.parts_repo, "update_assigned_job"):
                self.parts_repo.update_assigned_job(
                    session_id=msg.get("session_id"),
                    order_item_id=oid,
                    assigned_job_id=job_id,
                    assigned_job_name=job_name
                )
        except Exception:
            pass


    def _act_assign_to_new_job(self, msg: dict):
        fields = msg.get("fields") or {}
        try:
            self.ui.ro_hub_manager._new_job()
        except Exception:
            self.ui.ro_items_table.addJob("New Job")

        view = self.ui.ro_items_table
        m = view.model()
        root = QModelIndex()

        def _after_new_job():
            job_row = max(0, m.rowCount(root) - 1)
            self._add_fields_to_job(job_row, fields)

            try:
                ro_view = self.ui.ro_items_table
                jobs = ro_view.current_jobs() if hasattr(ro_view, "current_jobs") else []
                job_id = int(jobs[job_row].get("job_id")) if 0 <= job_row < len(jobs) and jobs[job_row].get(
                    "job_id") is not None else None
                job_name = (jobs[job_row].get("job_name") if 0 <= job_row < len(jobs) else "New Job") or "New Job"
                oid = str(msg.get("order_item_id") or "")
                if oid and hasattr(self.parts_model, "set_assigned_job_by_order_item_id"):
                    self.parts_model.set_assigned_job_by_order_item_id(oid, job_name)
                if hasattr(self.parts_repo, "update_assigned_job"):
                    self.parts_repo.update_assigned_job(
                        session_id=msg.get("session_id"),
                        order_item_id=oid,
                        assigned_job_name=job_name,
                        assigned_job_id=job_id,
                    )

            except Exception:
                pass
        QTimer.singleShot(0, _after_new_job)



    def show_modal_with_details(self, title: str, text: str, details: str,
                                 icon: QMessageBox.Icon = QMessageBox.Icon.Information):
        if self.modal_open:
            return
        self.modal_open = True
        try:
            parent = self.ui if hasattr(self, "ui") else None
            box = QMessageBox(parent)
            box.setWindowFlags(Qt.WindowType.Dialog |
                               Qt.WindowType.FramelessWindowHint |
                               Qt.WindowType.WindowStaysOnTopHint)
            box.setWindowModality(Qt.WindowModality.ApplicationModal)
            box.setIcon(icon)
            box.setText(text)
            box.setWindowTitle(title)
            box.setDetailedText(details)
            box.setStandardButtons(QMessageBox.StandardButton.Ok)
            box.show()
            box.raise_()
            box.activateWindow()
            box.exec()
        finally:
            self.modal_open = False

    def show_message_box(self, icon, title, text):
        box = QMessageBox(parent=self.ui)
        box.setWindowFlags(Qt.WindowType.Dialog |
                           Qt.WindowType.FramelessWindowHint |
                           Qt.WindowType.WindowStaysOnTopHint)
        box.setWindowModality(Qt.WindowModality.ApplicationModal)
        box.setIcon(icon)
        box.setWindowTitle(title)
        box.setText(text)
        box.exec()
