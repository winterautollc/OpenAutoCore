from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QTableWidget, QApplication
from PyQt6 import QtWidgets, QtCore, QtGui
from openauto.repositories import db_handlers, customer_repository, vehicle_repository, repair_orders_repository
from openauto.managers.customer_options_manager import CustomerOptionsManager
from openauto.managers.estimate_options_manager import EstimateOptionsManager
from decimal import Decimal, ROUND_HALF_UP



### SUBCLASSED QTABLEWIDGET THAT LOADS ALL RECORDED CUSTOMERS AND CONTACT INFO STORED IN MYSQL ###
class CustomerTable(QTableWidget):
    vehicle_signal_request = pyqtSignal(int)  ### PYQTSIGNALS FOR PUSHBUTTONS IN managers.customer_options_manager.py ###
    ro_signal_request = pyqtSignal()
    estimate_signal_request = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        customer_table_names = ("LAST NAME", "FIRST NAME", "ADDRESS", "CITY", "STATE", "ZIP", "PHONE", "ALT PHONE", "EMAIL", "ID")
        self.setColumnCount(10)
        self.setColumnHidden(9, True)
        # self.setGridStyle(QtCore.Qt.PenStyle.DashDotLine)
        self.setShowGrid(False)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.setHorizontalHeaderLabels(customer_table_names)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        # self.setAlternatingRowColors(True)
        self.customer_id = None
        self.load_customer_data()
        self.cellDoubleClicked.connect(self.options_load)

    def options_load(self):
        self.get_customer_id()
        self.show_customer_options()

### DECLARES customer_options SEE managers/customer_options_manager.py ###
    def show_customer_options(self):
        self.customer_options_manager = CustomerOptionsManager(
            parent=self.window(),
            customer_id=self.customer_id,
            vehicle_signal=self.vehicle_signal_request,
            ro_signal=self.ro_signal_request
        )




###  LOADS DATA FROM MYSQL TO CUSTOMERS PAGE.  FUNCTION IS ONLY CALLED ONCE ON STARTUP ###
    def load_customer_data(self):
        self.setRowCount(db_handlers.customer_rows())
        result = customer_repository.CustomerRepository.get_all_customer_info() or []
        table_row = 0
        for row in result:
            for col in range(10):
                item = QtWidgets.QTableWidgetItem(str(row[col]))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.setItem(table_row, col, item)
                # self.setStyleSheet("background-color: #97aabd")
            table_row += 1


####  CONNECTED TO QTHREAD THAT MONITORS ALL MYSQL CHANGES FOR EVERY TABLE AND UPDATES QTABLEWIDGET ####
    def update_customers(self, customer_data):
        table_row = 0
        self.setRowCount(db_handlers.customer_rows())
        for row in customer_data:
            for col in range(10):
                item = QtWidgets.QTableWidgetItem(str(row[col]))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.setItem(table_row, col, item)
                # self.setStyleSheet("background-color: #97aabd")

            table_row += 1


    ### FINDS PRIMARY KEY ID FOR CUSTOMERS AND RETURNS IT TO MAKE CUSTOMER CHANGES ###
    def get_customer_id(self):
        selected_row = self.currentRow()
        selected_column = self.currentColumn()
        selected_data = []
        selected_name = self.itemAt(selected_row, selected_column)
        for column in range(self.model().columnCount()):
            index = self.model().index(selected_row, column)
            selected_data.append(index.data())
        self.customer_id = selected_data[9]


class EstimateTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.setMouseTracking(True)
        self.estimate_id = None
        estimate_names = ("ID", "RO NUMBER", "DATE", "NAME", "YEAR", "MAKE", "MODEL", "TECH", "TOTAL")
        # self.setGridStyle(QtCore.Qt.PenStyle.DashDotLine)
        self.setColumnCount(9)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.setHorizontalHeaderLabels(estimate_names)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setShowGrid(False)
        self.setColumnHidden(0, True)
        self._show_estimates()
        self.cellDoubleClicked.connect(self._estimate_options_load)

    def _show_estimates(self):
        pass
        # self.setRowCount(db_handlers.estimate_rows())
        # result = repair_orders_repository.RepairOrdersRepository.load_repair_orders() or []
        # table_row = 0
        # for row in result:
        #     for col in range(9):
        #         item = QtWidgets.QTableWidgetItem(str(row[col]))
        #         item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        #         self.setItem(table_row, col, item)
                # self.setStyleSheet("background-color: #97aabd")

            # table_row += 1
    def update_estimates(self, estimate_data):
        pass
        # table_row = 0
        # self.setRowCount(db_handlers.estimate_rows())
        # for row in estimate_data:
        #     for col in range(9):
        #         item = QtWidgets.QTableWidgetItem(str(row[col]))
        #         item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        #         self.setItem(table_row, col, item)
        #         # self.setStyleSheet("background-color: #97aabd")
        #
        #     table_row += 1



    def _estimate_options_load(self):
        self.get_estimate_id()
        self._show_options()

    def get_estimate_id(self):
        selected_row = self.currentRow()
        selected_column = self.currentColumn()
        selected_data = []
        selected_name = self.itemAt(selected_row, selected_column)
        for column in range(self.model().columnCount()):
            index = self.model().index(selected_row, column)
            selected_data.append(index.data())
        self.estimate_id = selected_data[0]

    def _show_options(self):
        self.estimate_options_manager = EstimateOptionsManager(
            parent=self.window(),
            estimate_id = self.estimate_id)



class ShowAll(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        all_table_names = ("RO NUMBER", "DATE", "NAME", "YEAR", "MAKE", "MODEL", "TECH", "TOTAL", "STATUS")
        self.setMouseTracking(True)
        self.setColumnCount(9)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.setHorizontalHeaderLabels(all_table_names)
        self.setVisible(False)


class WorkingTable(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        working_names = ("RO NUMBER", "DATE", "NAME", "YEAR", "MAKE", "MODEL", "TECH", "TOTAL")
        self.setGridStyle(QtCore.Qt.PenStyle.DashDotLine)
        self.setColumnCount(8)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.setHorizontalHeaderLabels(working_names)



class ApprovedTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        approved_names = ("RO NUMBER", "DATE", "NAME", "YEAR", "MAKE", "MODEL", "TECH", "TOTAL")
        self.setMouseTracking(True)
        self.setGridStyle(QtCore.Qt.PenStyle.DashDotLine)
        self.setColumnCount(8)
        self.setHorizontalHeaderLabels(approved_names)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)


class CheckoutTable(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        checkout_names = ("RO NUMBER", "DATE", "NAME", "YEAR", "MAKE", "MODEL", "TECH", "TOTAL")
        self.setMouseTracking(True)
        self.setGridStyle(QtCore.Qt.PenStyle.DashDotLine)
        self.setColumnCount(8)
        self.setHorizontalHeaderLabels(checkout_names)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)


### SUBCLASSED QTABLEWIDGET FOR vehicles DATABASE TABLE ###
class VehicleTable(QtWidgets.QTableWidget):
    ro_signal_request = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        vehicle_table_names = ("VIN", "YEAR", "MAKE", "MODEL", "ENGINE", "TRIM", "LAST NAME", "FIRST NAME", "ID")
        self.setColumnCount(9)
        self.setColumnHidden(8, True)
        self.clearSelection()
        self.setRowCount(db_handlers.vehicle_rows())
        self.setGridStyle(QtCore.Qt.PenStyle.DashDotLine)
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.setHorizontalHeaderLabels(vehicle_table_names)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setFrameStyle(QtWidgets.QFrame.Shape.NoFrame)
        self.vehicle_id = None
        self.load_vehicle_data()
        self.cellClicked.connect(self.copy_vin)
        self.cellDoubleClicked.connect(self.on_vehicle_row_clicked)


### INITIAL LOADING OF VEHICLE DATA FROM DATABASE TABLE TO THE QTABLEWIDGET. CALLED ONLY ONCE ####
    def load_vehicle_data(self):
        result = vehicle_repository.VehicleRepository.get_all_vehicle_info() or []
        table_row = 0
        for row in result:
            for col in range(9):
                item = QtWidgets.QTableWidgetItem(str(row[col]))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.setItem(table_row, col, item)
                # self.setStyleSheet("background-color: #97aabd")

            table_row += 1



### CONNECTED TO SQLMONITOR QTHREAD IN event_handlers TO DO REAL TIME UPDATES TO THE VEHICLE QTABLEWIDGET ###
    def update_vehicles(self, vehicle_data):
        self.setRowCount(db_handlers.vehicle_rows())
        table_row = 0
        for row in vehicle_data:
            for col in range(9):
                item = QtWidgets.QTableWidgetItem(str(row[col]))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.setItem(table_row, col, item)
                # self.setStyleSheet("background-color: #97aabd")

            table_row += 1

    def on_vehicle_row_clicked(self):
        self.get_vehicle_id()
        self.show_vehicle_options()


    def get_vehicle_id(self):
        selected_row = self.currentRow()
        selected_column = self.currentColumn()
        selected_data = []
        selected_name = self.itemAt(selected_row, selected_column)
        for column in range(self.model().columnCount()):
            index = self.model().index(selected_row, column)
            selected_data.append(index.data())
        self.vehicle_id = selected_data[8]
        # self.vehicle_id = vehicle_repository.VehicleRepository.get_vehicle_id_by_details(selected_data[:6])
        self.vin_veh_id = [selected_data[0], self.vehicle_id]





    def show_vehicle_options(self):
        from openauto.managers.vehicle_options_manager import VehicleOptionsManager

        self.vehicle_options_manager = VehicleOptionsManager(
            parent=self.window(),
            vehicle_id=self.vin_veh_id,
            new_ro_request=self.ro_signal_request
            )

    def copy_vin(self):
        row = self.currentRow()
        item = self.item(row, 0)
        if item:
            clipboard = QApplication.clipboard()
            clipboard.setText(item.text())

COL_TYPE, COL_DESC, COL_QTY, COL_RATE, COL_PRICE, COL_TOTAL = range(6)

TYPE_JOB = "JOB"
TYPE_PART = "PART"
TYPE_LABOR = "LABOR"

money = lambda x: f"${Decimal(x).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}"

class ROTable(QtWidgets.QTreeWidget):
    totalsChanged = QtCore.pyqtSignal(Decimal, Decimal)  # jobTotals, grandTotal

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(6)
        self.setHeaderLabels(["Type", "Description", "Qty/Hrs", "Rate", "Unit Price", "Line Total"])
        self.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
        self.header().setStretchLastSection(True)
        self.setAlternatingRowColors(True)
        self.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked)

        # Only connect once
        self.itemChanged.connect(self._onItemChanged)
        self._updating = False

        # Context menu
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._openContextMenu)

        # (Optional) fonts
        self._bold = QtGui.QFont()
        self._bold.setBold(True)
        self._italic = QtGui.QFont()
        self._italic.setItalic(True)

    # ---------- Public API ----------
    def addJob(self, title: str = "New Job"):
        job = QtWidgets.QTreeWidgetItem([TYPE_JOB, title, "", "", "", ""])
        job.setFirstColumnSpanned(False)
        job.setFlags(
            job.flags() | QtCore.Qt.ItemFlag.ItemIsEditable | QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
        self._styleJob(job)
        self.addTopLevelItem(job)

        # Add a “subtotal” pseudo-row under job
        self._ensureJobSubtotal(job)
        self.expandItem(job)
        return job

    def addPart(self, jobItem: QtWidgets.QTreeWidgetItem, desc="New Part", qty="1", unit_price="0.00"):
        part = QtWidgets.QTreeWidgetItem([TYPE_PART, desc, qty, "", unit_price, ""])
        self._makeEditable(part, editable_cols=[COL_DESC, COL_QTY, COL_PRICE])
        jobItem.insertChild(jobItem.childCount() - 1, part)  # before subtotal row
        self._recalcRow(part)
        self._recalcJob(jobItem)
        return part

    def addLabor(self, jobItem: QtWidgets.QTreeWidgetItem, desc="Labor", hours="1.0", rate="100.00"):
        labor = QtWidgets.QTreeWidgetItem([TYPE_LABOR, desc, hours, rate, "", ""])
        self._makeEditable(labor, editable_cols=[COL_DESC, COL_QTY, COL_RATE])
        jobItem.insertChild(jobItem.childCount() - 1, labor)  # before subtotal row
        self._recalcRow(labor)
        self._recalcJob(jobItem)
        return labor

    # ---------- UI Helpers ----------
    def _styleJob(self, job):
        for c in range(self.columnCount()):
            job.setFont(c, self._bold)
        job.setForeground(0, QtGui.QBrush(QtGui.QColor("#0b6efd")))
        job.setText(COL_TOTAL, "")  # job header row shows no total

    def _styleSubtotal(self, row):
        for c in range(self.columnCount()):
            row.setFont(c, self._italic)
        row.setForeground(0, QtGui.QBrush(QtGui.QColor("#444")))
        row.setFirstColumnSpanned(False)

    def _makeEditable(self, item, editable_cols):
        flags = item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable | QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled
        item.setFlags(flags)
        # lock other columns
        for c in range(self.columnCount()):
            if c not in editable_cols:
                itf = item.flags()
                item.setFlags(itf & ~QtCore.Qt.ItemFlag.ItemIsEditable)

    def _ensureJobSubtotal(self, jobItem):
        # Ensure last child is a subtotal row
        if jobItem.childCount() == 0 or jobItem.child(jobItem.childCount() - 1).text(COL_TYPE) != "SUBTOTAL":
            st = QtWidgets.QTreeWidgetItem(["SUBTOTAL", "Job Subtotal", "", "", "", "$0.00"])
            self._styleSubtotal(st)
            # subtotal row not editable
            st.setFlags(st.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
            jobItem.addChild(st)
        self._recalcJob(jobItem)

    # ---------- Calculations ----------
    def _onItemChanged(self, item, column):
        if self._updating:
            return
        t = item.text(COL_TYPE)
        if t in (TYPE_PART, TYPE_LABOR):
            self._recalcRow(item)
            job = item.parent()
            if job is not None:
                self._recalcJob(job)

    def _recalcRow(self, item):
        """Compute line total for PART or LABOR rows."""
        t = item.text(COL_TYPE)
        qty = Decimal(self._safe(item.text(COL_QTY), default="0"))
        rate = Decimal(self._safe(item.text(COL_RATE), default="0"))
        price = Decimal(self._safe(item.text(COL_PRICE), default="0"))

        if t == TYPE_PART:
            # qty * unit_price
            line_total = qty * price
        elif t == TYPE_LABOR:
            # hours * labor_rate
            line_total = qty * rate
        else:
            return

        self._setText(item, COL_TOTAL, money(line_total))

    def _recalcJob(self, jobItem):
        """Sum all child line totals (exclude the subtotal row)."""
        self._updating = True
        try:
            subtotal = Decimal("0")
            n = jobItem.childCount()
            for i in range(n):
                row = jobItem.child(i)
                if row.text(COL_TYPE) == "SUBTOTAL":
                    continue
                val = self._parseMoney(row.text(COL_TOTAL))
                subtotal += val
            # write to subtotal row (last child)
            st = jobItem.child(jobItem.childCount() - 1)
            if st and st.text(COL_TYPE) == "SUBTOTAL":
                self._setText(st, COL_TOTAL, money(subtotal))
        finally:
            self._updating = False

        self._recalcGrandTotal()

    def _recalcGrandTotal(self):
        gt = Decimal("0")
        for i in range(self.topLevelItemCount()):
            job = self.topLevelItem(i)
            st = job.child(job.childCount() - 1) if job.childCount() else None
            if st and st.text(COL_TYPE) == "SUBTOTAL":
                gt += self._parseMoney(st.text(COL_TOTAL))
        # Emit if you want to mirror totals elsewhere
        self.totalsChanged.emit(Decimal("0"), gt)

    # ---------- Utils ----------
    def _parseMoney(self, s: str) -> Decimal:
        return Decimal(self._safe(s.replace("$", ""), default="0")).quantize(Decimal("0.01"))

    def _safe(self, s, default="0"):
        try:
            return str(Decimal(str(s)))
        except Exception:
            return default

    def _setText(self, item, col, text):
        self._updating = True
        try:
            item.setText(col, text)
        finally:
            self._updating = False

    # ---------- Context Menu ----------
    def _openContextMenu(self, pos):
        item = self.itemAt(pos)
        menu = QtWidgets.QMenu(self)

        actAddJob = menu.addAction("Add Job")
        act = menu.addSeparator()

        actAddPart = menu.addAction("Add Part to Job")
        actAddLabor = menu.addAction("Add Labor to Job")
        menu.addSeparator()
        actDelete = menu.addAction("Delete Selected")

        chosen = menu.exec(self.viewport().mapToGlobal(pos))
        if not chosen:
            return

        if chosen == actAddJob:
            job = self.addJob("New Job")
            self.editItem(job, COL_DESC)
            return

        # Find job context
        jobItem = None
        if item:
            if item.parent() is None and item.text(COL_TYPE) == TYPE_JOB:
                jobItem = item
            elif item.parent() is not None:
                jobItem = item.parent()

        if chosen == actAddPart:
            if jobItem is None:
                jobItem = self.addJob("New Job")
            row = self.addPart(jobItem)
            self.editItem(row, COL_DESC)

        elif chosen == actAddLabor:
            if jobItem is None:
                jobItem = self.addJob("New Job")
            row = self.addLabor(jobItem)
            self.editItem(row, COL_DESC)

        elif chosen == actDelete:
            self._deleteSelected()

    def _deleteSelected(self):
        item = self.currentItem()
        if not item:
            return
        if item.text(COL_TYPE) == "SUBTOTAL":
            return  # don't delete subtotal row directly
        parent = item.parent()
        if parent is None:
            # deleting a job: remove entire job
            idx = self.indexOfTopLevelItem(item)
            if idx >= 0:
                self.takeTopLevelItem(idx)
        else:
            parent.removeChild(item)
            self._ensureJobSubtotal(parent)
            self._recalcJob(parent)
        self._recalcGrandTotal()



class PartsTree(QtWidgets.QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)



