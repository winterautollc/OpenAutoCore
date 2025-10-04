from PyQt6 import QtCore, QtGui

COL_TYPE        = 0
COL_SKU         = 1
COL_DESC        = 2
COL_QTY         = 3
COL_UNIT_COST   = 4
COL_SELL        = 5
COL_HOURS       = 6
COL_RATE        = 7
COL_TAX         = 8
COL_TOTAL       = 9
NUM_COLUMNS     = 10


# Custom roles (start from Qt.UserRole + 1)
JOB_ID_ROLE         = QtCore.Qt.ItemDataRole.UserRole + 1
JOB_NAME_ROLE       = QtCore.Qt.ItemDataRole.UserRole + 2
ITEM_ID_ROLE        = QtCore.Qt.ItemDataRole.UserRole + 3
LINE_ORDER_ROLE     = QtCore.Qt.ItemDataRole.UserRole + 4
ROW_KIND_ROLE       = QtCore.Qt.ItemDataRole.UserRole + 5   # 'job'|'part'|'labor'|'tire'|'fee'|'sublet'|'subtotal'
APPROVED_ROLE       = QtCore.Qt.ItemDataRole.UserRole + 6   # bool
DECLINED_ROLE       = QtCore.Qt.ItemDataRole.UserRole + 7
WORKING_ROLE        = QtCore.Qt.ItemDataRole.UserRole + 8
PARTIALLY_APPROVED_ROLE = QtCore.Qt.ItemDataRole.UserRole + 9
CHECKOUT_ROLE       = QtCore.Qt.ItemDataRole.UserRole + 10
ARCHIVED_ROLE       = QtCore.Qt.ItemDataRole.UserRole + 11


JOB_STATUS_COLOR = {
    "approved": "#2E7D32",
    "declined": "#B71C1C",
    "partial": "#F39C12",
}


TYPE_COLOR = {
    "part":   "#0b60eb",
    "labor":  "#1ca44e",
    "tire":   "#b91048",
    "fee":    "#d08609",
    "sublet": "#7c53f8",
    "subtotal": "#9d9689",
}

_BOLD = QtGui.QFont()
_BOLD.setBold(True)
_ITALIC = QtGui.QFont()
_ITALIC.setItalic(True)



HEADER_TITLES = [
    "Type", "SKU / Op Code", "Description", "Qty", "Unit Cost", "Sell", "Hours", "Rate", "Tax %", "Line Total"
]

def _qcolor(hex_or_none):
    if not hex_or_none: 
        return None
    c = QtGui.QColor(hex_or_none)
    return QtGui.QBrush(c)