from __future__ import annotations
from typing import Iterable, Optional, Sequence
from dataclasses import dataclass
import time
from openauto.utils.log_sanitizer import scrub

from PyQt6 import QtCore, QtWidgets

@dataclass(frozen=True)
class CartItemRef:
    order_item_id: Optional[str]
    local_id: Optional[int]
    session_id: Optional[str]

class PartsItemController(QtCore.QObject):
    deletedLocally = QtCore.pyqtSignal(list)
    deleteFailed = QtCore.pyqtSignal(list, str)
    addedLocally = QtCore.pyqtSignal(list)
    addFailed = QtCore.pyqtSignal(list, str)
    callbackReady = QtCore.pyqtSignal(object)
    requestRemove = QtCore.pyqtSignal(str, str, list)
    orderSubmitted = QtCore.pyqtSignal(object)

    def __init__(self, tree_view: QtWidgets.QTreeView, tree_model, *, sidecar, get_token=None,
                 get_session_id=None, parts_repo=None, parent=None):
        super().__init__(parent)
        self.view = tree_view
        self.model = tree_model
        self.sidecar = sidecar
        self.repo = parts_repo
        self.get_token = get_token or (lambda: None)
        self.get_session_id = get_session_id or (lambda: None)
        self.requestRemove.connect(self._on_request_remove)
        self._suppression_until: dict[str, float] = {}

        self._pool = QtCore.QThreadPool.globalInstance()
        if hasattr(self.model, "set_local_suppression_fn"):
            self.model.set_local_suppression_fn(self._is_suppressed)
        self.callbackReady.connect(self._on_callback_ready)
        if hasattr(self.model, "quantityEdited"):
            self.model.quantityEdited.connect(self._on_qty_edited)




    @QtCore.pyqtSlot(str, str, list)
    def _on_request_remove(self, token, session_id, order_ids):
        self.sidecar.update_cart(token=token, session_id=session_id, removes=order_ids)

    @QtCore.pyqtSlot()
    def delete_selected(self):
        refs = self._selection_to_refs()
        if not refs:
            return
        self._remove_from_model(refs)
        self.deletedLocally.emit(refs)

        by_session: dict[str, list[str]] = {}
        for r in refs:
            if r.order_item_id and r.session_id:
                by_session.setdefault(r.session_id, []).append(r.order_item_id)

        fallback_session = self.get_session_id() or ""

        for sess, ids in (
                by_session.items() or [(fallback_session, [r.order_item_id for r in refs if r.order_item_id])]):
            token = self.get_token()
            if token and sess and ids:
                self.requestRemove.emit(token, str(sess), ids)

    @QtCore.pyqtSlot(object)
    def _on_callback_ready(self, payload):
        cb, result = payload
        cb(result)

    @QtCore.pyqtSlot(object)
    def add_from_payload(self, payload: dict | list[dict]):
        if isinstance(self.model, QtCore.QAbstractItemModel) and hasattr(self.model, "load_from_callback_objects"):
            if isinstance(payload, dict):
                for key in ("orders", "items", "parts", "results", "data"):
                    if isinstance(payload.get(key), (list, tuple)):
                        self.model.load_from_callback_objects(payload[key])
                        break
                else:
                    self.model.load_from_callback_objects([payload])
            elif isinstance(payload, (list, tuple)):
                self.model.load_from_callback_objects(payload)

    @QtCore.pyqtSlot(object)
    def on_part_removed(self, payload: dict):
        order_id = str(payload["orderItemId"])
        session_id = payload["sessionId"]
        if not order_id or not session_id:
            if hasattr(self, "debugText"):
                self.debugText.emit(scrub(f"[pt] remove-part callback missing id/session: {payload}"))
            return

        if hasattr(self.model, "remove_by_order_item_ids"):
            self.model.remove_by_order_item_ids([order_id])  # <- list, not str

        if self.repo and hasattr(self.repo, "delete_order_items"):
            try:
                affected = self.repo.delete_order_items(session_id, order_id)
                if hasattr(self, "debugText"):
                    self.debugText.emit(scrub(
                        f"[pt] removed orderItemId={order_id} sid={session_id} (db affected={affected})"
                    ))
            except Exception as e:
                if hasattr(self, "debugText"):
                    self.debugText.emit(scrub(f"[pt] delete_order_items error for {order_id}: {e}"))

        self.deletedLocally.emit([CartItemRef(order_item_id=order_id, session_id=session_id, local_id=None)])


    @QtCore.pyqtSlot(object)
    def on_cart_updated(self, payload: dict):
        raw = (payload or {}).get("Raw") or payload or {}
        self.add_from_payload(raw)

    @QtCore.pyqtSlot(object)
    def on_cart_submitted(self, payload: dict):
        self.orderSubmitted.emit(payload)

    @QtCore.pyqtSlot(str, str, int)
    def _on_qty_edited(self, order_item_id: str, session_id: str, new_qty: int):
        if not session_id:
            session_id = self.get_session_id() or ""

        token = self.get_token() or ""

        if token and session_id and order_item_id:
            print("token, session_id and order_item_id found")
            self.sidecar.update_cart(
                token=token,
                session_id=session_id,
                adds=[{"orderItemId": order_item_id, "quantity": int(max(1, new_qty))}]
            )

        try:
            if self.repo and hasattr(self.repo, "update_item_qty"):
                self.repo.update_item_qty(session_id, order_item_id, int(max(1, new_qty)))
        except Exception:
            pass

    @QtCore.pyqtSlot(str, str)
    def remove_one(self, session_id: str, order_item_id: str):
        if not (session_id and order_item_id):
            return
        if hasattr(self.model, "remove_by_order_item_ids"):
            self.model.remove_by_order_item_ids([order_item_id])
        token = self.get_token() or ""
        if token:
            self.requestRemove.emit(token, session_id, [order_item_id])

    def add_items(self, rows: Sequence[dict]):
        if not rows:
            return
        inserted_refs = self._insert_into_model(rows)
        self.addedLocally.emit(inserted_refs)
        self._async_add_to_sources(inserted_refs, rows)

    def set_suppression_ttl(self, seconds: float):
        self._suppression_ttl = max(0.0, float(seconds))


    def _selection_to_refs(self) -> list[CartItemRef]:
        sm = self.view.selectionModel()
        if not sm:
            return []
        leaf_idxs = [ix for ix in sm.selectedRows(0) if not self.model.hasChildren(ix)]
        refs: list[CartItemRef] = []
        for ix in leaf_idxs:
            meta = self.model.data(ix, QtCore.Qt.ItemDataRole.UserRole)
            if isinstance(meta, dict):
                oid = meta.get("orderItemId") or meta.get("order_item_id")
                local_id = meta.get("id") or meta.get("pk")
                sess = meta.get("sessionId") or meta.get("session_id")
            else:
                oid = None;
                local_id = None;
                sess = None
            refs.append(CartItemRef(order_item_id=str(oid) if oid else None,
                                    local_id=local_id,
                                    session_id=str(sess) if sess else None))
        return refs

    def _remove_from_model(self, refs: Iterable[CartItemRef]):
        now = time.monotonic()
        for r in refs:
            if r.order_item_id:
                self._suppression_until[r.order_item_id] = now + getattr(self, "_suppression_ttl", 2.0)

        if hasattr(self.model, "remove_by_order_item_ids"):
            self.model.remove_by_order_item_ids([r.order_item_id for r in refs if r.order_item_id])
            return

        sm = self.view.selectionModel()
        if sm:
            parents = {}
            for ix in sm.selectedRows(0):
                if self.model.hasChildren(ix):
                    continue
                parents.setdefault(ix.parent(), []).append(ix.row())
            for parent, rows in parents.items():
                for row in sorted(rows, reverse=True):
                    self.model.removeRow(row, parent)

    def _insert_into_model(self, rows: Sequence[dict]) -> list[CartItemRef]:
        if hasattr(self.model, "append_items"):
            inserted_meta = self.model.append_items(rows)
        else:
            inserted_meta = rows
        refs = []
        for m in inserted_meta:
            meta = m.get("meta", m)
            oid = meta.get("orderItemId") or meta.get("order_item_id")
            local_id = meta.get("id") or meta.get("pk")
            refs.append(CartItemRef(order_item_id=str(oid) if oid else None, local_id=local_id))
        return refs


    def _async_add_to_sources(self, refs: list[CartItemRef], rows: Sequence[dict]):
        def work():
            try:
                if self.repo and hasattr(self.repo, "insert_parts_rows"):
                    self.repo.insert_parts_rows(rows)
                return True, ""
            except Exception as e:
                return False, str(e)

        def done(ok_msg):
            ok, msg = ok_msg
            if not ok:
                self.addFailed.emit(refs, msg)

        self._run_in_pool(work, done)

    def _run_in_pool(self, fn, cb):
        controller = self

        class Task(QtCore.QRunnable):
            def run(self_nonlocal):
                result = fn()
                controller.callbackReady.emit((cb, result))

        self._pool.start(Task())

    def _is_suppressed(self, order_item_id: str) -> bool:
        t = self._suppression_until.get(order_item_id)
        if not t:
            return False
        if time.monotonic() > t:
            self._suppression_until.pop(order_item_id, None)
            return False
        return True
