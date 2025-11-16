from __future__ import annotations
from typing import Any, Iterable

from PyQt6 import QtCore

# Re‑use existing tree role/column definitions
from openauto.subclassed_widgets.roles.tree_roles import (
    COL_TYPE, COL_SKU, COL_DESC, COL_QTY, COL_UNIT_COST, COL_SELL, COL_SUPPLIER, COL_ORDER_PLATFORM, COL_STATUS,
    NUM_COLUMNS, ROW_KIND_ROLE, _BOLD, TYPE_COLOR, _qcolor, PART_STATUS_COLOR
)



# Data Node
class PTNode:
    __slots__ = ("parent", "children", "kind", "columns", "meta")

    def __init__(self, kind: str, columns: list[Any], parent: 'PTNode | None' = None, meta: dict | None = None):
        self.parent: PTNode | None = parent
        self.children: list[PTNode] = []
        self.kind: str = kind  # 'category' | 'item'
        self.columns: list[Any] = columns  # fixed length = NUM_COLUMNS
        self.meta: dict[str, Any] = (meta or {})

    def row_in_parent(self) -> int:
        return self.parent.children.index(self) if self.parent else 0

    def get(self, col: int):
        return self.columns[col]

    def set(self, col: int, value: Any):
        self.columns[col] = value

    def is_category(self) -> bool: return self.kind == "category"
    def is_item(self) -> bool: return self.kind == "item"


class PartsTreeModel(QtCore.QAbstractItemModel):
    # emitted if selection/controllers want to react to inserts
    modelFilled = QtCore.pyqtSignal()
    quantityEdited = QtCore.pyqtSignal(str, str, int) # order_item_id, session_id, new_qty

    def __init__(self, parent: QtCore.QObject | None = None):
        super().__init__(parent)
        self.COL_ASSIGNED = max(COL_SELL, COL_SUPPLIER, COL_ORDER_PLATFORM, COL_STATUS) + 1
        self._pt_num_columns = self.COL_ASSIGNED + 1
        self._root = PTNode("root", [None] * self._pt_num_columns, None)
        self.group_per_item = True
        # local headers, keeps global HEADER_TITLES intact for RO
        self._headers = [
            "Type",        # COL_TYPE
            "Supplier",      # COL_SUPPLIER
            "SKU",         # COL_SKU
            "Description", # COL_DESC
            "Qty",         # COL_QTY
            "Unit Cost",   # COL_UNIT_COST
            "List Price",  # COL_SELL
            "Order Platform", # COL_ORDER_PLATFORM
            "Status",       # COL_STATUS
            "Assigned Job",  # COL_ASSIGNED (local, separate from tree_roles)

        ]

    # public API
    def clear(self):
        self.beginResetModel()
        self._root = PTNode("root", [None] * self._pt_num_columns, None)
        self.endResetModel()

    def ensure_category(self, label: str) -> PTNode:
        label = (label or "") or "PARTS"
        # find existing
        for ch in self._root.children:
            if ch.is_category() and (str(ch.get(COL_TYPE)) == label):
                return ch
        # create new
        self.beginInsertRows(QtCore.QModelIndex(), len(self._root.children), len(self._root.children))
        cat = PTNode("category", [None] * self._pt_num_columns, self._root)
        cat.set(COL_TYPE, label)
        self._root.children.append(cat)
        self.endInsertRows()
        return cat

    def _normalize_meta(self, meta: dict | None) -> dict:
        m = dict(meta or {})

        if "assigned_job_name" in m and "assignedJobName" not in m:
            m["assignedJobName"] = m.get("assigned_job_name") or ""
        if "assigned_job_id" in m and "assignedJobId" not in m:
            m["assignedJobId"] = m.get("assigned_job_id")
        return m

    def add_item(self,
                 *,
                 category: str,
                 part_name: str,
                 supplier: str = "",
                 sku: str | None = None,
                 description: str | None = None,
                 qty: float | int | None = None,
                 unit_cost: float | None = None,
                 list_price: float | None = None,
                 order_platform: str = "",
                 meta: dict | None = None,
                 core_amt: float | None = None) -> QtCore.QModelIndex:

        if self.group_per_item:
            parent_label = (supplier or "") or "UNKNOWN SUPPLIER"
            cat = self.ensure_category(parent_label)
        else:
            parent_label = (category or "PART")
            cat = self.ensure_category(parent_label)
        parent_idx = self.index(self._row_for_node(cat), 0, QtCore.QModelIndex())

        row: list[Any] = [None] * self._pt_num_columns
        norm_kind = None
        if meta and isinstance(meta, dict):
            norm_kind = (meta.get("__norm_kind__") or "").strip().upper()
        row[COL_TYPE] = norm_kind or (part_name or "PART")
        row[COL_SUPPLIER] = supplier or ""
        row[COL_SKU] = sku or ""
        row[COL_DESC] = description or ""
        row[COL_QTY] = int(qty) if qty not in (None, "") else None
        row[COL_UNIT_COST] = float(unit_cost) if unit_cost not in (None, "") else None
        row[COL_SELL] = float(list_price) if list_price not in (None, "") else None
        row[COL_ORDER_PLATFORM] =  order_platform or  "PartsTech"
        row[COL_STATUS] = (meta or {}).get("status", "quoted")

        insert_at = len(cat.children)
        self.beginInsertRows(parent_idx, insert_at, insert_at)
        node = PTNode("item", row, parent=cat, meta=self._normalize_meta(meta))
        cat.children.append(node)
        self.endInsertRows()

        if core_amt is None:
            price = (meta or {}).get("price") or {}
            try:
                core_amt = float(price.get("core") or 0.0)
            except Exception:
                core_amt = 0.0

        if (core_amt or 0.0) > 0.0:
            fee_row: list[Any] = [None] * self._pt_num_columns
            fee_row[COL_TYPE] = "FEE"  # color/format as fee
            fee_row[COL_SUPPLIER] = supplier or ""
            fee_row[COL_SKU] = sku or ""
            fee_row[COL_DESC] = f"CORE CHARGE FOR {sku or (part_name or 'PART')}"
            fee_row[COL_QTY] = int(qty) if qty not in (None, "") else None
            fee_row[COL_UNIT_COST] = float(core_amt)
            fee_row[COL_SELL] = None
            fee_row[COL_ORDER_PLATFORM] = order_platform or "PartsTech"
            fee_meta = dict(meta or {})
            fee_meta.update({"__norm_kind__": "FEE", "row_type": "fee", "isCore": True})
            insert_fee_at = len(cat.children)
            self.beginInsertRows(parent_idx, insert_fee_at, insert_fee_at)
            fee_node = PTNode("item", fee_row, parent=cat, meta=fee_meta)
            cat.children.append(fee_node)
            self.endInsertRows()

        return self.index(insert_at, COL_TYPE, parent_idx)

    # Loading helpers
    def load_from_callback_objects(self, items: Iterable[dict[str, Any]]):
        self.layoutAboutToBeChanged.emit()

        def g(d: dict, *keys: str, default=None):
            norm = {str(k).replace("_", "").lower(): v for k, v in d.items()}
            for k in keys:
                k2 = k.replace("_", "").lower()
                if k2 in norm:
                    return norm[k2]
            return default

        def normalize_category(obj: dict) -> str:
            # Prefer explicit signals, then heuristics based on names
            price = obj.get("price") or {}
            # if g(obj, "coreCharge", "core", default=False) or (price.get("core") not in (None, 0, 0.0)):
            #     return "FEE"

            # Collect strings we can scan
            taxonomy = obj.get("taxonomy") or {}
            part_type = (taxonomy.get("partTypeName") or "").strip().lower()
            cat_name = (taxonomy.get("categoryName") or "").strip().lower()
            subcat = (taxonomy.get("subCategoryName") or "").strip().lower()
            part_name = (g(obj, "partName", "name") or "").strip().lower()
            desc = (g(obj, "description", "longDescription") or "").strip().lower()
            tokens = " ".join([part_type, cat_name, subcat, part_name, desc])

            # Tires: look for 'tire' keywords or known IDs
            if "tire" in tokens:
                return "TIRE"

            # Fluids/Chemicals
            fluid_words = [
                "oil", "coolant", "antifreeze", "brake fluid", "atf", "automatic transmission fluid",
                "power steering", "washer fluid", "def", "diesel exhaust fluid", "gear oil"
            ]
            if any(w in tokens for w in fluid_words):
                return "OILS & CHEMICALS"

            # Default
            return "PART"

        for obj in (items or []):
            part_name = g(obj, "partName", "name", "part") or ""
            sku = g(obj, "sku", "partNumber", "number", "id")
            desc = g(obj, "description", "desc", "longDescription", "partTypeName")
            price = obj.get("price") or {}
            core_amt = float(price.get("core") or 0.0)
            if not desc:
                taxonomy = obj.get("taxonomy") or {}
                desc = taxonomy.get("partTypeName") or ""
            qty_raw = g(obj, "qty", "quantity")
            try:
                qty = int(qty_raw) if qty_raw not in (None, "") else None
            except Exception:
                qty = None
            if qty is not None:
                qty = max(1, qty)
            unit_cost = g(obj, "unitCost", "cost")
            list_price = g(obj, "listPrice", "price", "msrp", "list")
            supplier = g(obj, "supplierName", "supplier") or ""
            order_platform = g(obj, "partstechCatalogURL") or ""
            if order_platform:
                order_platform = "PartsTech"
            cat = normalize_category(obj)
            obj["__norm_kind__"] = cat  # keep normalized type for painting
            self.add_item(category=cat, part_name=part_name, supplier=supplier, sku=sku, description=desc,
                          qty=qty, unit_cost=unit_cost, list_price=list_price,
                          order_platform=order_platform, meta=obj, core_amt=core_amt)
        self.layoutChanged.emit()
        self.modelFilled.emit()


    ### Append rows shaped like PartsTree.selected_items() return. Returns a list of inserted dicts (meta) ###
    def append_items(self, rows: Iterable[dict]) -> list[dict]:
        inserted = []
        for r in rows or []:
            meta = self._normalize_meta(r.get("meta") or {})
            price = meta.get("price") or {}
            core_amt = r.get("coreAmt")

            if core_amt is None:
                core_amt = price.get("core")

            try:
                core_amt = float(core_amt or 0.0)
            except Exception:
                core_amt = 0.0

            idx = self.add_item(
                category=r.get("category") or meta.get("__norm_kind__") or "PART",
                part_name=r.get("partName") or meta.get("partTypeName") or "PART",
                supplier=r.get("supplier") or "",
                sku=r.get("sku") or meta.get("partNumber") or "",
                description=r.get("description") or meta.get("description") or "",
                qty=r.get("qty") or meta.get("quantity"),
                unit_cost=r.get("unitCost") or (meta.get("price") or {}).get("cost"),
                list_price=r.get("listPrice") or (meta.get("price") or {}).get("list"),
                order_platform=r.get("orderPlatform") or "PartsTech",
                meta=meta,
                core_amt=core_amt,
            )
            # collect the node's meta back out
            m = self.data(idx, QtCore.Qt.ItemDataRole.UserRole)
            if isinstance(m, dict):
                inserted.append(m)
        return inserted

    def remove_by_order_item_ids(self, ids: list[str]) -> int:
        if not ids:
            return 0
        to_remove = {}
        ids_set = {str(x) for x in ids}
        # find rows grouped by parent
        for pi, parent in enumerate(self._root.children):
            if not parent or not parent.is_category():
                continue
            parent_idx = self.index(self._row_for_node(parent), 0, QtCore.QModelIndex())
            rows = []
            for row, child in enumerate(list(parent.children)):
                if child.is_item() and str(child.meta.get("orderItemId") or "") in ids_set:
                    rows.append(row)
            if rows:
                to_remove[parent_idx] = rows

        removed = 0
        for parent_idx, rows in to_remove.items():
            for row in sorted(rows, reverse=True):
                self.beginRemoveRows(parent_idx, row, row)
                parent = self._node(parent_idx)
                parent.children.pop(row)
                self.endRemoveRows()
                removed += 1
        return removed


    # Qt overrides
    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        node = self._node(parent)
        return len(node.children) if node else 0

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return self._pt_num_columns

    def index(self, row: int, column: int, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> QtCore.QModelIndex:
        parent_node = self._node(parent) or self._root
        if 0 <= row < len(parent_node.children):
            child = parent_node.children[row]
            return self.createIndex(row, column, child)
        return QtCore.QModelIndex()

    def parent(self, index: QtCore.QModelIndex) -> QtCore.QModelIndex:
        node = self._node(index)
        if not node or node.parent is None or node.parent is self._root:
            return QtCore.QModelIndex()
        return self.createIndex(node.parent.row_in_parent(), 0, node.parent)

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.ItemDataRole.DisplayRole) -> Any:
        node = self._node(index)
        if not node:
            return None

        if role == ROW_KIND_ROLE:
            return node.kind


        if role in (QtCore.Qt.ItemDataRole.DisplayRole, QtCore.Qt.ItemDataRole.EditRole):
            val = node.get(index.column())
            if role == QtCore.Qt.ItemDataRole.DisplayRole and index.column() in (COL_UNIT_COST, COL_SELL):
                return f"{(val or 0.0):.2f}" if val is not None else ""
            if index.column() == self.COL_ASSIGNED and node.is_item():
                return (node.meta or {}).get("assignedJobName") or ""
            return val

        if role == QtCore.Qt.ItemDataRole.ForegroundRole and index.column() in (COL_TYPE, COL_DESC):
            if node.is_category():
                # top-level category
                return _qcolor("#555555")
            # child item rows
            norm = (node.meta.get("__norm_kind__") or "").strip().lower()
            # map display bucket → TYPE_COLOR key
            key_map = {
                "part": "part",
                "tire": "tire",
                "oils & chemicals": "part",
                "core": "core",
                "fee": "fee",
                "status": "part"
            }
            color_key = key_map.get(norm, "part")
            return _qcolor(TYPE_COLOR.get(color_key))

        if role == QtCore.Qt.ItemDataRole.ForegroundRole and index.column() == COL_STATUS:
            status = str(node.get(COL_STATUS) or "").strip().lower()
            return _qcolor(PART_STATUS_COLOR.get(status))

        if role == QtCore.Qt.ItemDataRole.FontRole and node.is_category():
            return _BOLD

        if role == QtCore.Qt.ItemDataRole.UserRole:
            return dict(node.meta) if node and node.is_item() else None

        return None

    def setData(self, index: QtCore.QModelIndex, value: Any, role: int = QtCore.Qt.ItemDataRole.EditRole) -> bool:
        node = self._node(index)
        if not node or not node.is_item():
            return False

        if role in (QtCore.Qt.ItemDataRole.EditRole, QtCore.Qt.ItemDataRole.DisplayRole):
            col = index.column()
            val = value
            if col == COL_QTY:
                try:
                    val = int(value) if value not in (None, "") else None
                except Exception:
                    val = None
                if val is not None:
                    val = max(1, val)
                node.set(col, val)
                self.dataChanged.emit(index, index, [role])

                # emit the live-update signal with ids from this node's meta
                meta = node.meta if isinstance(node.meta, dict) else {}
                oid = str(meta.get("orderItemId") or meta.get("id") or "")
                sid = str(meta.get("sessionId") or meta.get("session_id") or "")
                if val is not None and oid:
                    self.quantityEdited.emit(oid, sid, int(val))
                return True

            elif col in (COL_UNIT_COST, COL_SELL):
                try:
                    val = float(value) if value not in (None, "") else None
                except Exception:
                    val = None
            node.set(col, val)
            self.dataChanged.emit(index, index, [role])
            return True
        return False



    def remove_index(self, index: QtCore.QModelIndex):
        node = self._node(index)
        if not node or node.is_category():
            return  # so category headers aren't deleted, that would delete multiple items at once
        parent = node.parent
        if not parent:
            return
        try:
            row = parent.children.index(node)
        except ValueError:
            return
        parent_idx = self.index(self._row_for_node(parent), 0, QtCore.QModelIndex())
        self.beginRemoveRows(parent_idx, row, row)
        parent.children.pop(row)
        self.endRemoveRows()


    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags:
        base = QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled
        if not index.isValid():
            return base
        node = self._node(index)
        if not node:
            return base
        if node.is_category():
            return base | QtCore.Qt.ItemFlag.ItemIsDropEnabled
        # Item rows: allow editing of Qty only by default
        editable_cols = {COL_QTY}
        f = base | QtCore.Qt.ItemFlag.ItemIsDragEnabled
        if index.column() in editable_cols:
            f |= QtCore.Qt.ItemFlag.ItemIsEditable
        return f

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.ItemDataRole.DisplayRole) -> Any:
        if orientation == QtCore.Qt.Orientation.Horizontal and role == QtCore.Qt.ItemDataRole.DisplayRole:
            custom = {
                COL_TYPE: self._headers[0],
                COL_SUPPLIER: self._headers[1],
                COL_SKU: self._headers[2],
                COL_DESC: self._headers[3],
                COL_QTY: self._headers[4],
                COL_UNIT_COST: self._headers[5],
                COL_SELL: self._headers[6],
                COL_ORDER_PLATFORM: self._headers[7],
                COL_STATUS: self._headers[8],
                self.COL_ASSIGNED: self._headers[9]
            }
            if section in custom:
                return custom[section]
        return None

    #helpers
    def _node(self, index: QtCore.QModelIndex | None) -> PTNode | None:
        if not index or not index.isValid():
            return self._root
        return index.internalPointer()

    def _row_for_node(self, node: PTNode | None) -> int:
        if node is None:
            return -1
        if node.parent is None:
            return self._root.children.index(node)
        return node.row_in_parent()


    def set_assigned_job_by_order_item_id(self, order_item_id: str, job_name: str) -> bool:
        if not order_item_id:
            return False

        updated = False
        root = QtCore.QModelIndex()
        for pi, parent in enumerate(self._root.children):
            if not parent or not parent.is_category():
                continue
            parent_idx = self.index(self._row_for_node(parent), 0, root)
            for row, child in enumerate(parent.children):
                if not child.is_item():
                    continue
                meta = child.meta or {}
                if str(meta.get("orderItemId") or meta.get("id") or "") == str(order_item_id):
                    meta["assignedJobName"] = job_name or ""
                    left = self.index(row, self.COL_ASSIGNED, parent_idx)
                    self.dataChanged.emit(left, left, [QtCore.Qt.ItemDataRole.DisplayRole])
                    updated = True
        return updated


