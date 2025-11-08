from PyQt6 import QtWidgets, QtCore, QtGui
from openauto.subclassed_widgets.roles.tree_roles import (
    COL_DESC, COL_SKU, COL_TOTAL, ROW_KIND_ROLE, HEADER_TITLES,
    COL_TYPE, COL_QTY, COL_UNIT_COST, COL_SELL, COL_HOURS, COL_RATE, COL_TAX,
    JOB_ID_ROLE, JOB_NAME_ROLE, ITEM_ID_ROLE, LINE_ORDER_ROLE, APPROVED_ROLE, DECLINED_ROLE
)
import re


class _LineItemProxy:
    def __init__(self, view: 'ROTreeView', index: QtCore.QModelIndex):
        self._v = view
        self._i = index  # row index, arbitrary column

    # --- Compat: methods used by controllers ---
    def text(self, col: int) -> str:
        return str(self._v.model().index(self._i.row(), col, self._i.parent()).data())

    def setText(self, col: int, value: str):
        i = self._v.model().index(self._i.row(), col, self._i.parent())
        self._v.model().setData(i, value, QtCore.Qt.ItemDataRole.EditRole)

    def data(self, col: int, role: int):
        return self._v.model().index(self._i.row(), col, self._i.parent()).data(role)

    def setData(self, col: int, role: int, value):
        self._v.model().setData(self._v.model().index(self._i.row(), col, self._i.parent()), value, role)

    def parent(self):
        return _JobItemProxy(self._v, self._i.parent())


class _JobItemProxy:
    def __init__(self, view: 'ROTreeView', index: QtCore.QModelIndex):
        self._v = view
        self._i = index  # job row index, any column

    # --- Compat: headers ---
    def text(self, col: int) -> str:
        return str(self._v.model().index(self._i.row(), col, QtCore.QModelIndex()).data())

    def setText(self, col: int, value: str):
        i = self._v.model().index(self._i.row(), col, QtCore.QModelIndex())
        self._v.model().setData(i, value, QtCore.Qt.ItemDataRole.EditRole)

    def data(self, col: int, role: int):
        return self._v.model().index(self._i.row(), col, QtCore.QModelIndex()).data(role)

    def setData(self, col: int, role: int, value):
        self._v.model().setData(self._v.model().index(self._i.row(), col, QtCore.QModelIndex()), value, role)

    # --- Children helpers ---
    def parent(self):
        return None

    def childCount(self) -> int:
        return self._v.model().rowCount(self._i)

    def child(self, r: int) -> _LineItemProxy:
        idx = self._v.model().index(r, 0, self._i)
        return _LineItemProxy(self._v, idx)

    def indexOfChild(self, child: _LineItemProxy) -> int:
        return child._i.row()

    # --- Expansion + paint ---
    def isExpanded(self) -> bool:
        return self._v.isExpanded(self._i)

    def setExpanded(self, on: bool):
        self._v.setExpanded(self._i, on)

    def setForeground(self, col: int, brush: QtGui.QBrush):
        # emulate by setting a role the delegate/view can read; here we just set data
        self.setData(col, QtCore.Qt.ItemDataRole.ForegroundRole, brush)

class _TabDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, owner_view: 'ROTreeView'):
        super().__init__(owner_view)
        self._v = owner_view

    def eventFilter(self, editor, event):
        if event.type() == QtCore.QEvent.Type.KeyPress and event.key() in (
            QtCore.Qt.Key.Key_Tab, QtCore.Qt.Key.Key_Backtab
        ):
            backwards = (event.key() == QtCore.Qt.Key.Key_Backtab)
            self._v._advance_edit_index(backwards=backwards)
            return True  # swallow so editor doesn't move focus itself
        return super().eventFilter(editor, event)

    def createEditor(self, parent, option, index):
        ed = super().createEditor(parent, option, index)
        ed.installEventFilter(self)
        return ed


### View for ROTree while mimicking QTreeWidget functions, creating our own to keep code in managers/ intact
class ROTreeView(QtWidgets.QTreeView):
    # Old signals expected by ro_hub_manager
    approvalChanged = QtCore.pyqtSignal()
    declineJobChanged = QtCore.pyqtSignal()
    jobsChanged = QtCore.pyqtSignal()
    modelAttached = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUniformRowHeights(True)
        self.setAlternatingRowColors(True)
        self.setAllColumnsShowFocus(True)
        self.setExpandsOnDoubleClick(False)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.EditKeyPressed |
                             QtWidgets.QAbstractItemView.EditTrigger.SelectedClicked |
                             QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setColumnWidth(COL_TYPE, 90)
        self.setColumnWidth(COL_SKU, 120)
        self.setColumnWidth(COL_DESC, 320)
        self.setColumnWidth(COL_QTY, 60)
        self.setColumnWidth(COL_UNIT_COST, 100)
        self.setColumnWidth(COL_SELL, 100)
        self.setColumnWidth(COL_HOURS, 70)
        self.setColumnWidth(COL_RATE, 90)
        self.setColumnWidth(COL_TAX, 70)
        self.setColumnWidth(COL_TOTAL, 110)
        self.header().setStretchLastSection(True)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.header().setMinimumSectionSize(80)
        self.header().setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.header().setSectionsMovable(False)
        self.header().setSectionsClickable(False)
        delete_shortcut = QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key.Key_Delete), self)
        delete_shortcut.activated.connect(self._deleteSelected)
        self._tab_delegate = _TabDelegate(self)
        self.setItemDelegate(self._tab_delegate)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._openContextMenu)
        # Bridge model signals → compat signals
        self.modelChanged = False

    def setModel(self, model):
        super().setModel(model)
        self.expandAll()
        self.modelChanged = True
        if hasattr(model, "sanitize_job_headers"):
            model.sanitize_job_headers()
        model.modelReset.connect(self.expandAll)
        model.rowsInserted.connect(lambda *_: self.jobsChanged.emit())
        model.rowsRemoved.connect(lambda *_: self.jobsChanged.emit())
        model.dataChanged.connect(self._maybe_emit_approval)
        self.modelAttached.emit(model)

    # ---- QTreeWidget compat: headers ----
    def setHeaderLabels(self, titles: list[str]):
        if hasattr(self.model(), 'set_header_titles'):
            self.model().set_header_titles(titles)
        # Otherwise, headerData already provides defaults
        self.header().reset()

    # ---- QTreeWidget compat: top-level helpers ----
    def topLevelItemCount(self) -> int:
        return self.model().rowCount(QtCore.QModelIndex())

    def topLevelItem(self, i: int) -> _JobItemProxy:
        idx = self.model().index(i, 0, QtCore.QModelIndex())
        return _JobItemProxy(self, idx)

    def editItem(self, proxy, column: int):
        # proxy is _JobItemProxy or _LineItemProxy
        idx = proxy._i.sibling(proxy._i.row(), column)
        self.setCurrentIndex(idx)
        self.edit(idx)

    def clear(self):
        self.model().clear()

    # ---- Selection compat ----
    def currentItem(self):
        idx = self.currentIndex()
        if not idx.isValid():
            return None
        # normalize to column 0
        idx = self.model().index(idx.row(), 0, idx.parent())
        # return job or line proxy accordingly
        if not idx.parent().isValid():
            return _JobItemProxy(self, idx)
        return _LineItemProxy(self, idx)

    def setCurrentItem(self, proxy):
        if isinstance(proxy, _JobItemProxy):
            idx = proxy._i
        elif isinstance(proxy, _LineItemProxy):
            idx = proxy._i
        else:
            return
        self.setCurrentIndex(idx)

    def expandItem(self, proxy):
        if isinstance(proxy, _JobItemProxy):
            self.setExpanded(proxy._i, True)

    # ---- Old API shims to add lines/jobs ----
    def addJob(self, name: str):
        idx = self.model().add_job(name)
        self.setCurrentIndex(idx)
        self.edit(idx)
        return _JobItemProxy(self, idx)

    def _normalize_job_idx(self, job_item_or_index):
        if isinstance(job_item_or_index, _JobItemProxy):
            return job_item_or_index._i
        if isinstance(job_item_or_index, QtCore.QModelIndex):
            return job_item_or_index
        return QtCore.QModelIndex()

    def _kw_desc(self, kwargs):
        if "description" in kwargs:
            return kwargs
        if "desc" in kwargs:
            kwargs = dict(kwargs)
            kwargs["description"] = kwargs.pop("desc")
        return kwargs

    def addPart(self, job_item, description=None, qty=None, unit_price=None, sku=None, **kwargs):
        j = self._normalize_job_idx(job_item)
        kwargs = self._kw_desc(kwargs)
        if description is None and "description" in kwargs:
            description = kwargs["description"]
        idx = self.model().add_line(j, 'part', description=description, qty=qty, unit_price=unit_price, sku_number=(sku or ""), **kwargs)
        return _LineItemProxy(self, idx)

    def addLabor(self, job_item, description=None, hours=None, rate=None, sku=None, **kwargs):
        j = self._normalize_job_idx(job_item)
        kwargs = self._kw_desc(kwargs)
        if description is None and "description" in kwargs:
            description = kwargs["description"]
        idx = self.model().add_line(j, 'labor', description=description, hours=hours, rate=rate, sku_number=(sku or ""), **kwargs)
        return _LineItemProxy(self, idx)

    def addFee(self, job_item, sku: str = "", description: str = "Fee", qty=1.0, unit_price=0.0, row_type="FEE", **kwargs):
        j = self._normalize_job_idx(job_item)
        idx = self.model().add_line(j, 'fee', description=description, qty=qty, unit_price=unit_price, sku_number=(sku or ""),  **kwargs)
        return _LineItemProxy(self, idx)

    def addTire(self, job_item, sku: str = "", description: str = "Tire", qty=1.0, unit_price=0.0, row_type="FEE", **kwargs):
        j = self._normalize_job_idx(job_item)
        idx = self.model().add_line(j, 'tire', description=description, qty=qty, unit_price=unit_price, sku_number=(sku or ""), **kwargs)
        return _LineItemProxy(self, idx)

    def addSublet(self, job_item, sku: str = "", description: str = "Sublet", qty=1.0, unit_price=0.0, row_type="FEE", **kwargs):
        j = self._normalize_job_idx(job_item)
        idx = self.model().add_line(j, 'sublet', description=description, qty=qty, unit_price=unit_price, sku_number=(sku or ""), **kwargs)
        return _LineItemProxy(self, idx)

    # ---- Misc helpers used by existing code ----
    def _ensureJobSubtotal(self, job_proxy):
        # Model enforces this; keep stub for compatibility
        pass

    def _base_name(self, s: str | None) -> str:
        if not s:
            return ""
        return re.sub(r"\s*[–—-]\s*(Approved|Declined)\s*$", "", s, flags=re.IGNORECASE)


    def _col_index(self, visible_name: str) -> int:
        mapping = {
            'Type': COL_TYPE, 'Description': COL_DESC, 'Qty': COL_QTY, 'Qty/Hrs': COL_QTY,
            'Rate': COL_RATE, 'Unit Cost': COL_UNIT_COST, 'Sell': COL_SELL, 'Hours': COL_HOURS, 'Tax %': COL_TAX,
            'Line Total': COL_TOTAL,
        }
        return mapping.get(visible_name, 0)

    def _deleteSelected(self):
        m = self.model()
        sm = self.selectionModel()
        if not sm:
            return

        # Collect unique column-0 indexes as persistent indexes (stable across removals)
        #    Prefer selectedRows(0) if available; otherwise derive from selectedIndexes().
        if hasattr(sm, "selectedRows"):
            idxs0 = [QtCore.QPersistentModelIndex(i) for i in sm.selectedRows(0)]
        else:
            seen = set()
            idxs0 = []
            for idx in sm.selectedIndexes():
                i0 = idx.sibling(idx.row(), 0)
                key = (i0.model(), i0.row(), i0.parent().internalPointer())
                if key not in seen:
                    seen.add(key)
                    idxs0.append(QtCore.QPersistentModelIndex(i0))

        # Split into top-level jobs and child lines (group children by parent)
        top_job_rows: list[int] = []
        children_by_parent: dict[QtCore.QPersistentModelIndex, list[int]] = {}

        for pidx in idxs0:
            idx = QtCore.QModelIndex(pidx)
            if not idx.isValid():
                continue
            if not idx.parent().isValid():
                # top-level -> job row
                top_job_rows.append(idx.row())
            else:
                parent_idx = idx.parent()
                pparent = QtCore.QPersistentModelIndex(parent_idx)
                children_by_parent.setdefault(pparent, []).append(idx.row())

        # Remove child lines first, per parent, in descending row order
        for pparent, child_rows in children_by_parent.items():
            parent_idx = QtCore.QModelIndex(pparent)
            for r in sorted(child_rows, reverse=True):
                i0 = m.index(r, 0, parent_idx)
                # never delete subtotal rows; model recomputes subtotal after deletes
                kind = i0.data(ROW_KIND_ROLE)
                if kind == "subtotal":
                    continue
                m.remove_index(i0)

        # Remove whole jobs last, in descending row order
        for r in sorted(set(top_job_rows), reverse=True):
            job_idx = m.index(r, 0, QtCore.QModelIndex())
            m.remove_job(job_idx)

    # Return jobs in the view: [{job_id, job_name, job_order}]
    def current_jobs(self) -> list[dict]:
        m = self.model()
        out = []
        rows = m.rowCount(QtCore.QModelIndex())
        for r in range(rows):
            job_idx = m.index(r, 0, QtCore.QModelIndex())
            job_id = job_idx.data(JOB_ID_ROLE)
            # job name is shown under COL_TYPE for headers
            job_name = m.index(r, COL_TYPE, QtCore.QModelIndex()).data() or ""
            out.append({"job_id": job_id, "job_name": job_name, "job_order": r})
        return out

    ### Return list[dict] shaped like the old QTreeWidget collector expected.
    def to_legacy_items(self) -> list[dict]:
        items = []
        m = self.model()
        root_rows = m.rowCount(QtCore.QModelIndex())

        for r in range(root_rows):
            job_idx = m.index(r, 0, QtCore.QModelIndex())
            job_name = job_idx.data(JOB_NAME_ROLE)
            if not job_name:
                job_name = m.index(r, COL_TYPE, QtCore.QModelIndex()).data() or "New Job"
            job_name = self._base_name(job_name)
            job_rows = m.rowCount(job_idx)
            for cr in range(job_rows):
                line_idx = m.index(cr, 0, job_idx)
                kind = line_idx.data(ROW_KIND_ROLE)
                if kind in ("job", "subtotal"):
                    continue
                
                sku = m.index(cr, COL_SKU, job_idx).data()
                ucost = m.index(cr, COL_UNIT_COST, job_idx).data()
                desc = m.index(cr, COL_DESC, job_idx).data()
                qty = m.index(cr, COL_QTY, job_idx).data()
                price = m.index(cr, COL_SELL, job_idx).data()
                hours = m.index(cr, COL_HOURS, job_idx).data()
                rate = m.index(cr, COL_RATE, job_idx).data()
                tax = m.index(cr, COL_TAX, job_idx).data()
                total = m.index(cr, COL_TOTAL, job_idx).data()
                item_id = m.index(cr, 0, job_idx).data(ITEM_ID_ROLE)

                # Legacy flattening: labor → qty=hours, unit_price=rate
                if (kind or "").lower() == "labor":
                    qty_legacy = float(hours or 0)
                    price_legacy = float(rate or 0)
                    unit_cost = 0.0
                else:
                    qty_legacy = float(qty or 0)
                    price_legacy = float(price or 0)
                    unit_cost = float(ucost or 0)

                items.append({
                    "item_id": item_id,
                    "kind": kind,
                    "job_name": job_name,
                    "description": desc or "",
                    "qty": qty_legacy,
                    "unit_cost": unit_cost,
                    "unit_price": price_legacy,
                    "sku_number": str(sku or ""),
                    "hours": float(hours or 0),
                    "rate": float(rate or 0),
                    "tax": float(tax or 0),  # legacy key
                    "tax_pct": float(tax or 0),  # new key (kept both)
                    "line_total": float(total or 0),
                })
        return items


    def _advance_edit_index(self, *, backwards: bool = False):
        m = self.model()
        idx = self.currentIndex()
        if not idx.isValid():
            return
        parent = idx.parent()
        row = idx.row()
        cols = m.columnCount(parent)

        def editable(i: QtCore.QModelIndex) -> bool:
            return bool(m.flags(i) & QtCore.Qt.ItemFlag.ItemIsEditable)

        step = -1 if backwards else 1
        # try within row
        c = idx.column() + step
        while 0 <= c < cols:
            nxt = m.index(row, c, parent)
            if editable(nxt):
                self.setCurrentIndex(nxt)
                self.edit(nxt)
                return
            c += step
        # wrap to prev/next row
        next_row = row - 1 if backwards else row + 1
        if 0 <= next_row < m.rowCount(parent):
            scan = range(cols - 1, -1, -1) if backwards else range(cols)
            for c in scan:
                nxt = m.index(next_row, c, parent)
                if editable(nxt):
                    self.setCurrentIndex(nxt)
                    self.edit(nxt)
                    return

    def _openContextMenu(self, pos: QtCore.QPoint):
        idx = self.indexAt(pos)
        menu = QtWidgets.QMenu(self)

        # figure out job index (header) for adds/approval
        job_idx = idx if not idx.isValid() or not idx.parent().isValid() else idx.parent()

        # Approve / Decline (toggle)
        def toggle_approve():
            on = not bool(job_idx.data(APPROVED_ROLE))
            self.model().setData(job_idx, on, APPROVED_ROLE)
            if on:
                self.model().setData(job_idx, False, DECLINED_ROLE)

        act_approve = menu.addAction("Approve Job")
        act_approve.triggered.connect(toggle_approve)

        menu.addSeparator()

        def toggle_decline():
            on = not bool(job_idx.data(DECLINED_ROLE))
            self.model().setData(job_idx, on, DECLINED_ROLE)
            if on:
                self.model().setData(job_idx, False, APPROVED_ROLE)

        act_decline = menu.addAction("Decline Job")
        act_decline.triggered.connect(toggle_decline)

        menu.addSeparator()

        # Add items
        def add(kind):
            j = job_idx if job_idx.isValid() else self.model().index(0, 0, QtCore.QModelIndex())
            if kind == "labor":
                self.addLabor(j, description="",  hours=1.0, rate=0.0, row_type="LABOR")
            elif kind == "fee":
                self.addFee(j, description="", qty=1.0, unit_price=0.0, row_type="FEE")
            elif kind == "sublet":
                self.addSublet(j, description="", qty=1.0, unit_price=0.0, row_type="SUBLET")
            elif kind == "tire":
                self.addTire(j, description="", qty=1.0, unit_price=0.0, row_type="TIRE")
            else:
                self.addPart(j, description="", qty=1.0, unit_price=0.0, row_type="PART")

        for text, kind in [
            ("Add Part", "part"), ("Add Labor", "labor"),
            ("Add Fee", "fee"), ("Add Sublet", "sublet"), ("Add Tire", "tire")
        ]:
            a = menu.addAction(text)
            a.triggered.connect(lambda _, k=kind: add(k))

        # Remove
        menu.addSeparator()
        rm = menu.addAction("Delete Selected")
        rm.triggered.connect(self._deleteSelected)

        menu.exec(self.viewport().mapToGlobal(pos))

    def keyPressEvent(self, e: QtGui.QKeyEvent):
        if e.key() in (QtCore.Qt.Key.Key_Tab, QtCore.Qt.Key.Key_Backtab):
            backwards = (e.key() == QtCore.Qt.Key.Key_Backtab)
            idx = self.currentIndex()
            if not idx.isValid():
                return super().keyPressEvent(e)

            # compute the next editable index in the same row
            m = self.model()
            parent = idx.parent()
            row = idx.row()
            cols = m.columnCount(parent)
            step = -1 if backwards else 1

            # simple helper: is this index editable?
            def editable(i: QtCore.QModelIndex) -> bool:
                return bool(m.flags(i) & QtCore.Qt.ItemFlag.ItemIsEditable)

            # try moving within the row
            c = idx.column() + step
            while 0 <= c < cols:
                nxt = m.index(row, c, parent)
                if editable(nxt):
                    self.setCurrentIndex(nxt)
                    self.edit(nxt)
                    return
                c += step

            # wrap: go to prev/next row’s first editable column
            next_row = row - 1 if backwards else row + 1
            if 0 <= next_row < m.rowCount(parent):
                for c in range(cols) if not backwards else range(cols - 1, -1, -1):
                    nxt = m.index(next_row, c, parent)
                    if editable(nxt):
                        self.setCurrentIndex(nxt)
                        self.edit(nxt)
                        return
            return  # swallow the key if no candidate
        return super().keyPressEvent(e)

    def _maybe_emit_approval(self, topLeft, bottomRight, roles):
        roles = roles or []
        if APPROVED_ROLE in roles:
            self.approvalChanged.emit()
        if DECLINED_ROLE in roles:
            self.declineJobChanged.emit()
