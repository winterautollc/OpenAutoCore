from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP
from PyQt6 import QtCore, QtGui
from openauto.repositories.settings_repository import SettingsRepository

from openauto.subclassed_widgets.roles.tree_roles import (
    COL_TYPE, COL_SKU, COL_DESC, COL_QTY, COL_UNIT_COST, COL_SELL, COL_HOURS, COL_RATE, COL_TAX, COL_TOTAL,
    NUM_COLUMNS,
    JOB_ID_ROLE, JOB_NAME_ROLE, ITEM_ID_ROLE, LINE_ORDER_ROLE, ROW_KIND_ROLE, APPROVED_ROLE,
    HEADER_TITLES, DECLINED_ROLE, PARTIALLY_APPROVED_ROLE, JOB_STATUS_COLOR,
     _BOLD, TYPE_COLOR, _qcolor
)

import re
_STRIP_STATUS_RE = re.compile(r"\s*[–—-]\s*(Approved|Declined)\s*$", re.IGNORECASE)

NONE = QtCore.Qt.ItemFlag(0)

def _q2(x: Decimal) -> Decimal:
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def _strip_status_suffix(text: str | None) -> str:
    if not text:
        return ""
    return _STRIP_STATUS_RE.sub("", str(text))



### Generic tree node for jobs and line items.
### For jobs: kind='job' carries job_id/name, Children are line items + one SUBTOTAL row.
### For lines: kind in {'part', 'labor', 'tire', 'fee', 'sublet', 'subtotal'}
class ItemNode:
    __slots__ = ("parent", "children", "kind", "columns", "data_roles")

    def __init__(self, kind: str, columns: list, parent: ItemNode | None = None):
        self.parent: ItemNode | None = parent
        self.children: list[ItemNode] = []
        self.kind: str = kind
        # columns is a fixed-length list of length NUM_COLUMNS
        self.columns: list = columns
        # extra per-row metadata for roles like ids and booleans
        self.data_roles: dict[int, object] = {}

    def row_in_parent(self) -> int:
        return self.parent.children.index(self) if self.parent else 0

    # convenience getters/setters
    def get(self, col: int):
        return self.columns[col]

    def set(self, col: int, value):
        self.columns[col] = value

    def is_job(self):
        return self.kind == 'job'

    def is_subtotal(self):
        return self.kind == 'subtotal'

### Model for Repair Order Tree
### Responsibilities:
    # Holds jobs "top-level" and their line items as children
    # Computes per-line and per-job subtotal totals
    # Provides editing for description/qty/price/hours/rate/tax
    # Enforces exactly one SUBTOTAL child at bottom of each child
    # Supports DnD (reorder within a job and moving line items between jobs is allowed
class ROTreeModel(QtCore.QAbstractItemModel):
    requestFocusEditor = QtCore.pyqtSignal(QtCore.QModelIndex)  # optional for the view/delegate
    totalsChanged = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._root = ItemNode('root', [None]*NUM_COLUMNS, None)
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
            matrix.append({"min": min_v, "max": max_v, "mult": mult})
        matrix.sort(key=lambda r: r["min"])
        return matrix

    def _matrix_price_for_cost(self, cost: float | None) -> float | None:
        if cost is None:
            return None
        for r in self._pricing_matrix:
            if r["min"] <= cost <= r["max"]:
                return round(cost * r["mult"], 2)
        return None

    # Public API (called by controllers/managers)
    def clear(self):
        self.beginResetModel()
        self._root = ItemNode('root', [None]*NUM_COLUMNS, None)
        self.endResetModel()

    def add_job(self, name: str, job_id: int | None = None) -> QtCore.QModelIndex:
        name = _strip_status_suffix(name or "New Job")
        self.beginInsertRows(QtCore.QModelIndex(), self._root_child_count(), self._root_child_count())
        # job name lives in TYPE column (idx 0)
        job = ItemNode('job', [name, "", None, None, None, None, None, None, None, None], self._root)
        if job_id is not None:
            job.data_roles[JOB_ID_ROLE] = job_id
        job.data_roles[JOB_NAME_ROLE] = name
        job.data_roles[APPROVED_ROLE] = False  # default
        self._root.children.append(job)
        self.endInsertRows()
        self._ensure_job_subtotal(job)
        return self.index(job.row_in_parent(), COL_TYPE, QtCore.QModelIndex())


    def add_line(self, job_index: QtCore.QModelIndex, kind: str, *, sku_number: str, description="",
                 qty: float | None = None, unit_cost: float | None = None,
                 unit_price: float | None = None,
                 hours: float | None = None, rate: float | None = None,
                 tax_pct: float | None = None, item_id: int | None = None,
                 line_order: int | None = None, row_type: str | None = None) -> QtCore.QModelIndex:
        job_node = self._node(job_index)
        if not job_node or not job_node.is_job():
            return QtCore.QModelIndex()
        # insert above subtotal (last child is subtotal)
        insert_row = max(0, len(job_node.children) - 1)
        canonical = kind

        if row_type:
            rt = str(row_type).strip().lower()
            mapping = {"part": "part", "fee": "fee", "sublet": "sublet", "tire": "tire", "labor": "labor"}
            canonical = mapping.get(rt, canonical)

        visible_type = (row_type or canonical.upper())
        row = [visible_type, sku_number or "", description, qty, unit_cost, unit_price, hours, rate, tax_pct, None]

        self.beginInsertRows(job_index, insert_row, insert_row)

        node = ItemNode(canonical, row, job_node)
        if item_id is not None:
            node.data_roles[ITEM_ID_ROLE] = item_id
        if line_order is not None:
            node.data_roles[LINE_ORDER_ROLE] = line_order
        job_node.children.insert(insert_row, node)
        self.endInsertRows()
        self._recompute_line_total(node)
        self._recompute_job_subtotal(job_node)
        self.totalsChanged.emit()
        return self.index(insert_row, COL_DESC, job_index)

    def remove_index(self, index: QtCore.QModelIndex):
        node = self._node(index)
        if not node or node.is_subtotal():
            return
        parent = node.parent
        if not parent:
            return  # top-level job must be removed via remove_job
        try:
            row = parent.children.index(node)
        except ValueError:
            return  # already removed / stale
        self.beginRemoveRows(self.parent(index), row, row)
        parent.children.pop(row)
        self.endRemoveRows()
        if parent.is_job():
            self._recompute_job_subtotal(parent)
        self.totalsChanged.emit()

    def remove_job(self, job_index: QtCore.QModelIndex) -> None:
        # must be top-level
        if (not job_index.isValid()) or job_index.parent().isValid():
            return

        # Recompute row from the node pointer (safer than trusting job_index.row())
        node = self._node(job_index)
        if not node or not node.is_job():
            return
        try:
            row = self._root.children.index(node)
        except ValueError:
            return  # stale index already removed

        self.beginRemoveRows(QtCore.QModelIndex(), row, row)
        self._root.children.pop(row)
        self.endRemoveRows()
        self.totalsChanged.emit()

# Return a list[dict] where each dict is a job with its lines, ready for DB service
    def collect_serializable(self) -> list[dict]:
        out: list[dict] = []
        for job in self._root.children:
            if not job.is_job():
                continue
            job_bundle = {
                "job_id": job.data_roles.get(JOB_ID_ROLE),
                "job_name": (job.data_roles.get(JOB_NAME_ROLE) or job.get(COL_TYPE)),
                "approved": bool(job.data_roles.get(APPROVED_ROLE, False)),
                "lines": []
            }
            for ch in job.children:
                if ch.is_subtotal():
                    continue
                job_bundle["lines"].append({
                    "item_id": ch.data_roles.get(ITEM_ID_ROLE),
                    "kind": ch.kind,
                    "description": ch.get(COL_DESC),
                    "qty": ch.get(COL_QTY),
                    "unit_cost": ch.get(COL_UNIT_COST),
                    "unit_price": ch.get(COL_SELL),
                    "hours": ch.get(COL_HOURS),
                    "rate": ch.get(COL_RATE),
                    "tax_pct": ch.get(COL_TAX),
                    "line_total": ch.get(COL_TOTAL),
                })
            out.append(job_bundle)
        return out

    # QAbstractItemModel required overrides, essentially making our own QTreeWidget functions so code
    # still works in managers/
    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        node = self._node(parent)
        return len(node.children) if node else 0

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return NUM_COLUMNS

    def index(self, row: int, column: int, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> QtCore.QModelIndex:
        parent_node = self._node(parent)
        if not parent_node: parent_node = self._root
        if 0 <= row < len(parent_node.children):
            child = parent_node.children[row]
            return self.createIndex(row, column, child)
        return QtCore.QModelIndex()

    def parent(self, index: QtCore.QModelIndex) -> QtCore.QModelIndex:
        node = self._node(index)
        if not node or node.parent is None or node.parent is self._root:
            return QtCore.QModelIndex()
        return self.createIndex(node.parent.row_in_parent(), 0, node.parent)

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.ItemDataRole.DisplayRole) -> object:
        node = self._node(index)
        if not node:
            return None

        # Display/Edit Text
        if role in (QtCore.Qt.ItemDataRole.DisplayRole, QtCore.Qt.ItemDataRole.EditRole):
            if node.is_job() and index.column() == COL_TYPE:
                base = node.data_roles.get(JOB_NAME_ROLE)
                if not base:
                    base = _strip_status_suffix(node.get(COL_TYPE) or "New Job")
                approved = bool(node.data_roles.get(APPROVED_ROLE))
                declined = bool(node.data_roles.get(DECLINED_ROLE))
                if approved:
                    return f"{base} - Approved"
                if declined:
                    return f"{base} - Declined"
                return base
            return node.get(index.column())

        if role == QtCore.Qt.ItemDataRole.ForegroundRole and index.column() == COL_TYPE:
            if node.is_job():
                if node.data_roles.get(APPROVED_ROLE):
                    return _qcolor(JOB_STATUS_COLOR["approved"])
                if node.data_roles.get(DECLINED_ROLE):
                    return _qcolor(JOB_STATUS_COLOR["declined"])
                return None


            kind = (node.kind or "").lower()
            return _qcolor(TYPE_COLOR.get(kind))
        

        if role == QtCore.Qt.ItemDataRole.FontRole and node.is_job():
            if node.data_roles.get(APPROVED_ROLE) is True or node.data_roles.get(DECLINED_ROLE) is True:
                return _BOLD
            return None

        if role == ROW_KIND_ROLE:
            return node.kind
        if role in (JOB_ID_ROLE, JOB_NAME_ROLE, ITEM_ID_ROLE, LINE_ORDER_ROLE, APPROVED_ROLE, DECLINED_ROLE):
            return node.data_roles.get(role)
        
        r = index.row()
        c = index.column()

        if role in (QtCore.Qt.ItemDataRole.DisplayRole, QtCore.Qt.ItemDataRole.EditRole):
            val = node.get(c)
            if c == COL_TOTAL and role == QtCore.Qt.ItemDataRole.DisplayRole:
                return f"{(val or 0.0):.2f}"
            if c in (COL_UNIT_COST, COL_SELL, COL_RATE) and role == QtCore.Qt.ItemDataRole.DisplayRole:
                 return f"{(val or 0.0):.2f}"
            return val

        return None

    def setData(self, index: QtCore.QModelIndex, value, role: int = QtCore.Qt.ItemDataRole.EditRole) -> bool:
        node = self._node(index)
        if not node:
            return False
        if role in (QtCore.Qt.ItemDataRole.EditRole, QtCore.Qt.ItemDataRole.DisplayRole):
            val = value
            if index.column() in (COL_QTY, COL_UNIT_COST, COL_SELL, COL_HOURS, COL_RATE, COL_TAX):
                try:
                    val = float(val) if val not in (None, "") else None
                except Exception:
                    val = None

            if node.is_job() and index.column() == COL_TYPE:
                base = _strip_status_suffix("" if val is None else str(val))
                node.set(COL_TYPE, base)
                node.data_roles[JOB_NAME_ROLE] = base
                self.dataChanged.emit(index, index, [role])
                return True

            node.set(index.column(), val)
            if not node.is_job():
                if index.column() == COL_UNIT_COST and node.kind in ("part", "tire"):
                    cost = node.get(COL_UNIT_COST)
                    price = self._matrix_price_for_cost(cost if cost is not None else 0.0)
                    if price is not None:
                        node.set(COL_SELL, float(price))
                        sell_idx = self.index(index.row(), COL_SELL, index.parent())
                        self.dataChanged.emit(sell_idx, sell_idx, [QtCore.Qt.ItemDataRole.DisplayRole, QtCore.Qt.ItemDataRole.EditRole])


                self._recompute_line_total(node)
                if node.parent and node.parent.is_job():
                    self._recompute_job_subtotal(node.parent)
            self.dataChanged.emit(index, index, [role])
            self.totalsChanged.emit()
            return True

        if role in (JOB_ID_ROLE, JOB_NAME_ROLE, ITEM_ID_ROLE, LINE_ORDER_ROLE):
            node.data_roles[role] = value
            self.dataChanged.emit(index, index, [role])
            return True

        # approval roles: make them mutually exclusive
        if role == APPROVED_ROLE:
            v = bool(value)
            node.data_roles[APPROVED_ROLE] = v
            if v:
                node.data_roles[DECLINED_ROLE] = False
            self.dataChanged.emit(index, index, [APPROVED_ROLE, DECLINED_ROLE])
            return True

        if role == DECLINED_ROLE:
            v = bool(value)
            node.data_roles[DECLINED_ROLE] = v
            if v:
                node.data_roles[APPROVED_ROLE] = False
            self.dataChanged.emit(index, index, [APPROVED_ROLE, DECLINED_ROLE])
            return True

        if role in (JOB_ID_ROLE, JOB_NAME_ROLE, ITEM_ID_ROLE, LINE_ORDER_ROLE):
            node.data_roles[role] = value
            self.dataChanged.emit(index, index, [role])
            return True

        if role != QtCore.Qt.ItemDataRole.EditRole or not index.isValid():
            return False

        return False

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags:
        base = QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled
        if not index.isValid():
            return base
        
        node = self._node(index)
        if not node:
            return base
        
        col = index.column()

        if node.is_job():
            f = base | QtCore.Qt.ItemFlag.ItemIsDropEnabled
            if col == COL_TYPE:
                f |= QtCore.Qt.ItemFlag.ItemIsEditable
            return f
        
        if node.kind == "subtotal":
            return base | QtCore.Qt.ItemFlag.ItemIsDropEnabled
        
        editable_columns = {COL_SKU, COL_DESC, COL_QTY, COL_UNIT_COST, COL_SELL, COL_HOURS, COL_RATE, COL_TAX}

        k = (node.kind or "").lower()
        if k == "labor":
            editable_columns.discard(COL_UNIT_COST)
            editable_columns.discard(COL_SELL)
            editable_columns.discard(COL_QTY)

        elif k in {"part", "fee", "sublet", "tire"}:
            editable_columns.discard(COL_HOURS)
            editable_columns.discard(COL_RATE)

        f = base | QtCore.Qt.ItemFlag.ItemIsDragEnabled
        if col in editable_columns:
            f |= QtCore.Qt.ItemFlag.ItemIsEditable
        return f

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.ItemDataRole.DisplayRole) -> object:
        if orientation == QtCore.Qt.Orientation.Horizontal and role == QtCore.Qt.ItemDataRole.DisplayRole:
            if 0 <= section < len(HEADER_TITLES):
                return HEADER_TITLES[section]
        return None

    # -------------------- Drag & Drop --------------------
    def supportedDropActions(self) -> QtCore.Qt.DropAction:
        return QtCore.Qt.DropAction.MoveAction

    def mimeTypes(self) -> list[str]:
        return ["application/x-openauto-rotree"]

    def mimeData(self, indexes: list[QtCore.QModelIndex]) -> QtCore.QMimeData:
        mime = QtCore.QMimeData()
        if not indexes:
            return mime
        idx = indexes[0]
        node = self._node(idx)
        if not node or node.is_job() or node.is_subtotal():
            return mime
        parent = node.parent
        src_job_row = self._row_for_node(parent)
        payload = QtCore.QByteArray(f"{src_job_row}|{node.row_in_parent()}".encode("utf-8"))
        mime.setData("application/x-openauto-rotree", payload)
        return mime

    def dropMimeData(self, data: QtCore.QMimeData, action: QtCore.Qt.DropAction, row: int, column: int,
                     parent: QtCore.QModelIndex) -> bool:
        if action != QtCore.Qt.DropAction.MoveAction:
            return False
        if not data.hasFormat("application/x-openauto-rotree"):
            return False

        try:
            src_job_row_str, src_child_row_str = bytes(
                data.data("application/x-openauto-rotree")
            ).decode("utf-8").split("|")
            src_job_row = int(src_job_row_str)
            src_child_row = int(src_child_row_str)
        except Exception:
            return False

        # Resolve source parent/job
        if not (0 <= src_job_row < len(self._root.children)):
            return False
        src_job = self._root.children[src_job_row]
        if src_child_row < 0 or src_child_row >= len(src_job.children):
            return False

        moving = src_job.children[src_child_row]
        if moving.is_subtotal():
            return False  # never move subtotal

        # Resolve destination job parent
        dest_parent_node = self._node(parent)
        if dest_parent_node and dest_parent_node.is_job():
            dst_job = dest_parent_node
        else:
            # if dropping on a child row, parent() is the job
            p = parent.parent() if parent.isValid() else QtCore.QModelIndex()
            dst_job = self._node(p) if p.isValid() else None
            if not dst_job or not dst_job.is_job():
                # dropped in whitespace: move to last job if any, else cancel
                if self._root.children:
                    dst_job = self._root.children[-1]
                else:
                    return False

        # Compute destination row (never after subtotal)
        if row < 0:
            dest_row = max(0, len(dst_job.children) - 1)  # just before subtotal
        else:
            dest_row = min(row, max(0, len(dst_job.children) - 1))

        # Same-parent adjustment for beginMoveRows semantics
        same_parent = (dst_job is src_job)
        if same_parent:
            # Qt expects destinationRow as if the source row was removed first
            if dest_row > src_child_row:
                dest_row += 1

        # Build model indexes
        src_parent_idx = self.index(self._row_for_node(src_job), 0, QtCore.QModelIndex())
        dst_parent_idx = self.index(self._row_for_node(dst_job), 0, QtCore.QModelIndex())

        # Bounds check again after adjustments
        if same_parent:
            if dest_row == src_child_row or dest_row == src_child_row + 1:
                return False  # no-op move
            if dest_row < 0 or dest_row > len(src_job.children):
                return False
        else:
            if dest_row < 0 or dest_row > len(dst_job.children):
                return False

        # Perform the move
        self.beginMoveRows(src_parent_idx, src_child_row, src_child_row, dst_parent_idx, dest_row)
        # --- mutate underlying data ---
        src_job.children.pop(src_child_row)
        # When moving within the same job and dest_row > src_child_row, after pop the insertion index decreases by 1
        if same_parent and dest_row > src_child_row:
            dest_row -= 1
        dst_job.children.insert(dest_row, moving)
        moving.parent = dst_job
        self.endMoveRows()

        self._normalize_job_subtotal(src_job)
        if dst_job is not src_job:
            self._normalize_job_subtotal(dst_job)

        # Recompute subtotals for both jobs
        self._recompute_job_subtotal(src_job)
        if dst_job is not src_job:
            self._recompute_job_subtotal(dst_job)
        return True

# Ensure only on job subtotal per job
    # Drag and drop would normally duplicate subtotal if moved around under the same job.
    def _normalize_job_subtotal(self, job: ItemNode):
        # find all subtotal rows
        subs = [i for i, ch in enumerate(job.children) if ch.is_subtotal()]
        if not subs:
            # none → append one
            cols = [None] * NUM_COLUMNS
            cols[COL_TYPE] = "SUBTOTAL"
            cols[COL_TOTAL] = 0.0
            subtotal = ItemNode('subtotal', cols, job)
            job.children.append(subtotal)
            return

        keep = subs[0]
        # delete any extra subtotal rows (iterate from the end to keep indices valid)
        for i in reversed(subs[1:]):
            job.children.pop(i)

        # move the kept subtotal to the end if needed
        if keep != len(job.children) - 1:
            sub = job.children.pop(keep)
            job.children.append(sub)

    # -------------------- Helpers & totals --------------------
    def _root_child_count(self) -> int:
        return len(self._root.children)

    def _row_for_node(self, node: ItemNode | None) -> int:
        if node is None:
            return -1
        if node.parent is None:
            return self._root.children.index(node)
        return node.row_in_parent()

    def _node(self, index: QtCore.QModelIndex | None) -> ItemNode | None:
        if not index or not index.isValid():
            # for a parentless index, return root
            return self._root
        return index.internalPointer()

    def _ensure_job_subtotal(self, job: ItemNode):
        if job.children and job.children[-1].is_subtotal():
            return
        cols = [None] * NUM_COLUMNS
        cols[COL_TYPE] = "SUBTOTAL"
        cols[COL_TOTAL] = 0.0
        subtotal = ItemNode('subtotal', cols, job)
        job.children.append(subtotal)



    def _recompute_line_total(self, node: ItemNode):
        if node.kind == 'labor':
            hours = Decimal(str(node.get(COL_HOURS) or 0))
            rate  = Decimal(str(node.get(COL_RATE)  or 0))
            total = hours * rate
        elif node.kind == 'subtotal':
            return
        else:
            qty   = Decimal(str(node.get(COL_QTY) or 0))
            sell = Decimal(str((node.get(COL_SELL) or 0)))
            total = qty * sell
        tax_pct = Decimal(str(node.get(COL_TAX) or 0))
        total = total * (Decimal("1") + (tax_pct/Decimal("100")))
        total = _q2(total)
        node.set(COL_TOTAL, float(total))

    def _recompute_job_subtotal(self, job: ItemNode):
        # ensure we have a trailing subtotal row
        self._ensure_job_subtotal(job)
        subtotal_val = Decimal("0")
        for ch in job.children:
            if ch.is_subtotal():
                continue
            # guarantee each line has current total
            self._recompute_line_total(ch)
            subtotal_val += Decimal(str(ch.get(COL_TOTAL) or 0))
        job.children[-1].set(COL_TOTAL, float(subtotal_val))
        # notify view: emit dataChanged for subtotal total column
        job_row = self._row_for_node(job)
        sub_row = len(job.children) - 1
        idx = self.index(sub_row, COL_TOTAL, self.index(job_row, 0))
        self.dataChanged.emit(idx, idx, [QtCore.Qt.ItemDataRole.DisplayRole])
        self.totalsChanged.emit()


    # Ensure every job header stores the *raw* name (no '- Approved/Declined')
    def sanitize_job_headers(self):
        for job in self._root.children:
            if not job.is_job():
                continue
            raw = job.data_roles.get(JOB_NAME_ROLE) or job.get(COL_TYPE) or "Job"
            base = _strip_status_suffix(raw)
            if base != raw or (job.data_roles.get(JOB_NAME_ROLE) or "") != base:
                job.set(COL_TYPE, base)
                job.data_roles[JOB_NAME_ROLE] = base
                r = self._row_for_node(job)
                idx = self.index(r, COL_TYPE, QtCore.QModelIndex())
                self.dataChanged.emit(idx, idx, [QtCore.Qt.ItemDataRole.DisplayRole])