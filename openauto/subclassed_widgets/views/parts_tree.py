from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import Qt
from openauto.subclassed_widgets.models.parts_tree_model import PartsTreeModel
from openauto.subclassed_widgets.roles.tree_roles import (
    COL_DESC, COL_SKU, COL_TOTAL, ROW_KIND_ROLE, HEADER_TITLES,
    COL_TYPE, COL_QTY, COL_UNIT_COST, COL_SELL, COL_HOURS, COL_RATE, COL_TAX,
    JOB_ID_ROLE, JOB_NAME_ROLE, ITEM_ID_ROLE, LINE_ORDER_ROLE, APPROVED_ROLE, DECLINED_ROLE, COL_SUPPLIER,
    COL_ORDER_PLATFORM, COL_STATUS
)


class IntQtyDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        sb = QtWidgets.QSpinBox(parent)
        sb.setMinimum(1)
        sb.setMaximum(999999)   # pick a sane upper bound
        sb.setAccelerated(True)
        return sb

    def setEditorData(self, editor, index):
        val = index.model().data(index, Qt.ItemDataRole.EditRole)
        try:
            editor.setValue(int(val) if val is not None and val != "" else 1)
        except Exception:
            editor.setValue(1)

    def setModelData(self, editor, model, index):
        model.setData(index, int(editor.value()), Qt.ItemDataRole.EditRole)


class PartsTree(QtWidgets.QTreeView):
    modelAttached = QtCore.pyqtSignal(object)
    partActionRequested = QtCore.pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_ctx_menu)

        self.setUniformRowHeights(True)
        self.setAlternatingRowColors(True)
        self.setAllColumnsShowFocus(True)
        self.setExpandsOnDoubleClick(False)
        self.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.EditKeyPressed
            | QtWidgets.QAbstractItemView.EditTrigger.SelectedClicked
            | QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked
        )
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)

        # sensible defaults for column widths
        self.setColumnWidth(COL_TYPE, 240)
        self.setColumnWidth(COL_SKU, 140)
        self.setColumnWidth(COL_SUPPLIER, 160)
        self.setColumnWidth(COL_DESC, 360)
        self.setColumnWidth(COL_QTY, 70)
        self.setColumnWidth(COL_UNIT_COST, 110)
        self.setColumnWidth(COL_SELL, 110)
        self.setColumnWidth(COL_STATUS, 120)
        self._col_assigned = None
        self.header().setStretchLastSection(True)
        self.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.header().setMinimumSectionSize(80)
        self.header().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header().setSectionsMovable(False)
        self.header().setSectionsClickable(False)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)

    def setModel(self, model: QtCore.QAbstractItemModel) -> None:
        super().setModel(model)
        try:
            self._col_assigned = getattr(model, "COL_ASSIGNED", None)
        except Exception:
            self._col_assigned = None
        h = self.header()
        try:
            v_from = h.visualIndex(COL_SUPPLIER)
            if v_from != 1 and v_from != -1:
                h.moveSection(v_from, 1)
        except Exception:
            pass

        used = {COL_TYPE, COL_SUPPLIER, COL_SKU, COL_DESC, COL_QTY, COL_UNIT_COST, COL_SELL, COL_ORDER_PLATFORM, COL_STATUS}
        if isinstance(self._col_assigned, int):
            used.add(self._col_assigned)

        try:
            for c in range(model.columnCount()):
                self.setColumnHidden(c, c not in used)
        except Exception:
            pass

        if isinstance(self._col_assigned, int):
            self.setColumnWidth(self._col_assigned, 180)


        try:
            if hasattr(model, "modelFilled"):
                model.modelFilled.connect(self.expandAll, Qt.ConnectionType.UniqueConnection)
                def _resize_once():
                    cols = [COL_TYPE, COL_SUPPLIER, COL_SKU, COL_DESC]
                    if isinstance(self._col_assigned, int):
                        cols.append(self._col_assigned)
                    for col in cols:
                        self.resizeColumnToContents(col)
                model.modelFilled.connect(_resize_once, Qt.ConnectionType.UniqueConnection)
        except Exception:
            pass
        self.modelAttached.emit(model)
        self.setItemDelegateForColumn(COL_QTY, IntQtyDelegate(self))

    # quick loader from raw callback JSON (already parsed into dict/list)
    def load_callback(self, payload: dict | list[dict]):
        m = self.model()
        if isinstance(m, PartsTreeModel):
            if isinstance(payload, dict):
                # try common envelope keys then fallback to flat list
                for key in ("orders", "items", "parts", "results", "data"):
                    if key in payload and isinstance(payload[key], (list, tuple)):
                        if key == "orders":
                            m.load_from_partstech_submit_cart(payload)
                        else:
                            m.load_from_callback_objects(payload[key])
                        break
                else:
                    # If dict does not contain a list, assume it's one item
                    m.load_from_callback_objects([payload])
            elif isinstance(payload, (list, tuple)):
                m.load_from_callback_objects(payload)

    # Helper to fetch selected item nodes as dictionaries (useful for controllers)
    def selected_items(self) -> list[dict]:
        out: list[dict] = []
        m: PartsTreeModel = self.model()  # type: ignore
        sm = self.selectionModel()
        if not sm:
            return out
        rows = set()
        for idx in sm.selectedIndexes():
            i0 = idx.sibling(idx.row(), 0)
            rows.add((i0.parent(), i0.row()))
        for parent_idx, row in sorted(rows, key=lambda t: (t[0].internalPointer() if t[0].isValid() else None, t[1])):
            node = m._node(m.index(row, 0, parent_idx))
            if not node or not node.is_item():
                continue
            out.append({
                "category": node.parent.get(COL_TYPE) if node.parent else "",
                "partName": node.get(COL_TYPE),
                "supplier": node.get(COL_SUPPLIER),
                "sku": node.get(COL_SKU),
                "description": node.get(COL_DESC),
                "qty": node.get(COL_QTY),
                "unitCost": node.get(COL_UNIT_COST),
                "listPrice": node.get(COL_SELL),
                "orderPlatform": node.get(COL_ORDER_PLATFORM),
                "meta": dict(node.meta),
            })
        return out

    def delete_selected(self):
        m: PartsTreeModel = self.model()  # type: ignore
        sm = self.selectionModel()
        if not sm:
            return
        # Using persistent column-0 indexes as it's more stable when removing
        rows0 = [QtCore.QPersistentModelIndex(i) for i in sm.selectedRows(0)]
        by_parent: dict[QtCore.QPersistentModelIndex, list[int]] = {}
        for p in rows0:
            idx = QtCore.QModelIndex(p)
            if not idx.isValid():
                continue
            if idx.parent().isValid():  # only item rows, skip top-level categories
                parent_p = QtCore.QPersistentModelIndex(idx.parent())
                by_parent.setdefault(parent_p, []).append(idx.row())
        # Remove per parent, descending
        for parent_p, rows in by_parent.items():
            parent_idx = QtCore.QModelIndex(parent_p)
            for r in sorted(rows, reverse=True):
                i0 = m.index(r, 0, parent_idx)
                m.remove_index(i0)

    def _get_current_item_meta(self):
        idx = self.currentIndex()
        if not idx.isValid():
            return None
        # assume model.data(index, UserRole) returns the node meta dict (your model already does this)
        meta = self.model().data(idx, Qt.ItemDataRole.UserRole)
        if not isinstance(meta, dict):
            return None
        # we only act on leaf items (parts), not supplier branches
        # your model nodes usually have meta["orderItemId"] for leaves
        if not meta.get("orderItemId"):
            return None
        return meta

    ### collects current jobs in ro_items_table ###
    def current_part_fields(self):
        m = self.model()
        idx = self.currentIndex()
        if not idx.isValid():
            return None
        row0 = idx.sibling(idx.row(), 0)
        if m.hasChildren(row0):
            return None
        parent = row0.parent()
        def v(col):
            return m.index(row0.row(), col, parent).data()

        return {
            "description": v(COL_DESC) or v(COL_TYPE) or "New Part",
            "qty": v(COL_QTY) or 1,
            "unit_cost": v(COL_UNIT_COST) or 0.0,
            "unit_price": v(COL_SELL) or 0.0,
            "sku": v(COL_SKU) or "",
            "tax_pct": v(COL_TAX) or 0.0,
        }

    def _on_ctx_menu(self, pos):
        meta = self._get_current_item_meta()
        menu = QtWidgets.QMenu(self)

        if meta:
            act_remove   = menu.addAction("Remove Part")
            act_returned = menu.addAction("Mark as Returned")
            act_received = menu.addAction("Mark as Received")
            act_cancelled = menu.addAction("Mark Cancelled")
            menu.addSeparator()
            assign_menu = menu.addMenu("Assign to Job")
            jobs = []
            try:
                ro_view = getattr(self.window(), "ro_items_table", None)
                if ro_view and hasattr(ro_view, "current_jobs"):
                    jobs = ro_view.current_jobs()
            except Exception:
                jobs = []
            if not jobs:
                act_assign_none = assign_menu.addAction("(No Jobs)")
                act_assign_none.setEnabled(False)
            else:
                for i , j in enumerate(jobs):
                    a = assign_menu.addAction(f"Assign to Job: {j.get('job_name') or 'New Job'}")
                    a.setData({"job_row": i})
            menu.addSeparator()
            act_newjob = menu.addAction("Add to New Job")
        else:
            # disabled entries if not on a leaf
            act_remove = menu.addAction("Remove Part");   act_remove.setEnabled(False)
            act_returned = menu.addAction("Mark as Returned"); act_returned.setEnabled(False)
            act_received = menu.addAction("Mark as Received"); act_received.setEnabled(False)
            act_cancelled = menu.addAction("Mark Cancelled"); act_cancelled.setEnabled(False)
            menu.addSeparator()
            act_assign = menu.addAction("Assign to Existing Job…"); act_assign.setEnabled(False)
            act_newjob = menu.addAction("Add to New Job…"); act_newjob.setEnabled(False)

        chosen = menu.exec(self.viewport().mapToGlobal(pos))
        if not chosen or not meta:
            return

        session_id = meta.get("sessionId") or meta.get("session_id")
        order_item_id = str(meta.get("orderItemId") or meta.get("id") or "")
        fields = self.current_part_fields() or {}

        if chosen == act_remove:
            self.partActionRequested.emit({"op": "remove-part", "session_id": session_id, "order_item_id": order_item_id})
        elif chosen == act_returned:
            self.partActionRequested.emit({"op": "mark-returned", "session_id": session_id, "order_item_id": order_item_id})
        elif chosen == act_received:
            self.partActionRequested.emit({"op": "mark-received", "session_id": session_id, "order_item_id": order_item_id})
        elif chosen == act_cancelled:
            self.partActionRequested.emit({"op": "mark-cancelled", "session_id": session_id, "order_item_id": order_item_id})
        elif chosen.parent() and chosen.parent().title() == "Assign to Job":
            payload = {"op": "assign-to-job", "session_id": session_id, "order_item_id": order_item_id,
                       "job_row": (chosen.data() or {}).get("job_row", 0), "fields": fields}
            self.partActionRequested.emit(payload)

        elif chosen == act_newjob:
            payload = {"op": "assign-to-new-job", "session_id": session_id, "order_item_id": order_item_id,
                       "fields": fields}
            self.partActionRequested.emit(payload)


