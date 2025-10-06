from PyQt6 import QtWidgets, QtGui, QtCore
from openauto.repositories.ro_c3_repository import ROC3Repository
from openauto.repositories.repair_orders_repository import RepairOrdersRepository
from openauto.repositories.estimate_jobs_repository import EstimateJobsRepository
import os

MAX_TILE_W = 380

def _iter_all_tiles():
    # Walk all widgets and yield any ROTile instances, even if they’re on hidden pages.
    for w in QtWidgets.QApplication.allWidgets():
        try:
            if isinstance(w, ROTile):
                yield w
        except Exception:
            pass


# Update any live ROTile for moving tiles to working, checkout etc..
def update_all_tiles(ro_id: int, **fields):
    for tile in _iter_all_tiles():
        if getattr(tile, "ro_id", None) == ro_id:
            # quick pathways for common fields
            if "status" in fields:
                tile.set_status(fields["status"])
            if "total" in fields and fields["total"] is not None:
                try:
                    tile.total_label.setText(f"Estimate Total:  ${float(fields['total']):,.2f}")
                except Exception:
                    pass
            if fields:
                tile.update_from_record(fields)
            tile.update()

def _maybe_icon(path: str, fallback_text: str) -> QtWidgets.QLabel:
    lbl = QtWidgets.QLabel()
    lbl.setObjectName("icon_label")
    if path and os.path.exists(path):
        pm = QtGui.QPixmap(path)
        if not pm.isNull():
            lbl.setPixmap(pm.scaled(16, 16, QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                    QtCore.Qt.TransformationMode.SmoothTransformation))
            lbl.setProperty("kind", "pix")
            return lbl
    # fallback: small text/emoji
    lbl.setText(fallback_text)
    lbl.setProperty("kind", "text")
    return lbl

class ElideLabel(QtWidgets.QLabel):
    def __init__(self, text="", parent=None):
        super().__init__("", parent)

        self._full_text = ""
        self.setWordWrap(False)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                           QtWidgets.QSizePolicy.Policy.Fixed)
        if text:
            self.setText(text)

    def setText(self, text: str) -> None:
        self._full_text = text or ""
        self.setToolTip(self._full_text if self._full_text else "")
        self._update_elided()

    def resizeEvent(self, e: QtGui.QResizeEvent) -> None:
        super().resizeEvent(e)
        self._update_elided()

    def _update_elided(self):
        fm = self.fontMetrics()
        w = max(0, self.width() - 10)
        elided = fm.elidedText(self._full_text, QtCore.Qt.TextElideMode.ElideRight, w)
        super().setText(elided)


class MultiLineElideLabel(QtWidgets.QLabel):
    def __init__(self, text="", parent=None, max_lines=2):
        super().__init__("", parent)
        self._full_text = ""
        self._max_lines = max_lines
        self.setWordWrap(False)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred,
                           QtWidgets.QSizePolicy.Policy.Fixed)
        if text:
            self.setText(text)

    def setText(self, text: str) -> None:
        self._full_text = text or ""
        self.setToolTip(self._full_text if self._full_text else "")
        self._update_elided()

    def resizeEvent(self, e: QtGui.QResizeEvent) -> None:
        super().resizeEvent(e)
        self._update_elided()

    def _update_elided(self):
        fm = self.fontMetrics()
        width = max(0, self.width() - 2)
        text = self._full_text
        if not text or width <= 0:
            super().setText(text or "")
            return

        layout = QtGui.QTextLayout(text, self.font())
        layout.beginLayout()
        lines, consumed = [], 0
        while True:
            line = layout.createLine()
            if not line.isValid():
                break
            line.setLineWidth(width)
            start = line.textStart()
            length = line.textLength()
            seg = text[start:start+length]
            lines.append(seg)
            consumed += len(seg)
            if len(lines) >= self._max_lines:
                break
        layout.endLayout()

        if not lines:
            super().setText("")
            return

        overflow = consumed < len(text)
        if overflow:
            lines[-1] = fm.elidedText(lines[-1] + " …", QtCore.Qt.TextElideMode.ElideRight, width)

        super().setText("\n".join(lines))
        self.setMaximumHeight(fm.lineSpacing() * self._max_lines)

class ROTile(QtWidgets.QFrame):
    clicked = QtCore.pyqtSignal()
    statusRequested = QtCore.pyqtSignal()
    statusChangeRequested = QtCore.pyqtSignal(int, str)

    def __init__(self, ro_id, ro_number, customer_name, vehicle, tech, writer, concern, status,
                 parent=None, icon_dir: str = "theme/icons", page_context: str = "ro_hub"):
        super().__init__(parent)
        self.ro_id = ro_id
        self.status = status
        self.page_context = (page_context or "ro_hub").strip().lower()
        self.setMaximumWidth(MAX_TILE_W)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinAndMaxSize)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.OpenHandCursor))
        self.setObjectName("ro_tile")
        self.ro_label = QtWidgets.QLabel(f"RO #{ro_number}")
        self.ro_label.setObjectName("title")
        self.customer_label = ElideLabel(customer_name)
        self.vehicle_label = ElideLabel(vehicle)

        roles = QtWidgets.QHBoxLayout(); roles.setSpacing(8)

        tech_wrap = QtWidgets.QHBoxLayout(); tech_wrap.setSpacing(6)
        tech_icon = _maybe_icon(os.path.join(icon_dir, "tech.png"), "🛠")
        tech_lbl  = QtWidgets.QLabel(tech or "Unassigned")
        tech_lbl.setObjectName("ro_tech")
        tech_lbl.setProperty("role", "chip")
        self.tech_box = QtWidgets.QWidget()
        self.tech_box.setObjectName("chip_block")
        self.tech_box.setLayout(tech_wrap)
        tech_wrap.addWidget(tech_icon)
        tech_wrap.addWidget(tech_lbl)

        writer_wrap = QtWidgets.QHBoxLayout(); writer_wrap.setSpacing(6)
        writer_icon = _maybe_icon(os.path.join(icon_dir, "writer.png"), "💬")
        writer_lbl  = QtWidgets.QLabel(writer or "Unassigned")
        writer_lbl.setObjectName("ro_writer")
        writer_lbl.setProperty("role", "chip")
        self.writer_box = QtWidgets.QWidget()
        self.writer_box.setObjectName("chip_block")
        self.writer_box.setLayout(writer_wrap)
        writer_wrap.addWidget(writer_icon)
        writer_wrap.addWidget(writer_lbl)

        roles.addWidget(self.tech_box)
        roles.addWidget(self.writer_box)
        roles.addStretch(1)

        self.concern_label = ElideLabel(concern)
        self.total_label = QtWidgets.QLabel("Estimate Total: -")
        self.created_label = QtWidgets.QLabel("Created: -")

        # assemble
        layout.addWidget(self.ro_label)
        layout.addWidget(self.customer_label)
        layout.addWidget(self.vehicle_label)
        layout.addLayout(roles)
        layout.addWidget(self.concern_label)
        layout.addWidget(self.created_label)
        layout.addWidget(self.total_label)
        layout.addStretch()

        self.refresh_meta()

    ### Stub for now.
    # Maybe implement color changes to tiles in the future or any other UI imporvements.
    def set_status(self, status: str):
        self.status = (status or "open").strip().lower()

    ### Also stub
        # see above function set_status()
    def update_from_record(self, rec: dict):
        if "status" in rec: self.set_status(rec["status"])
        if "customer" in rec: self.customer_label.setText(rec["customer"] or "")
        if "vehicle" in rec: self.vehicle_label.setText(rec["vehicle"] or "")
        if "concern" in rec:
            self.concern_label.setText(f"Concern:  {rec['concern'] or 'No concern Entered'}")
        if "total" in rec and rec["total"] is not None:
            self.total_label.setText(f"Estimate Total:  ${rec['total']:,.2f}")
        if "created_at" in rec and rec["created_at"]:
            self.created_label.setText(f"Created:  {rec['created_at']:%m/%d/%Y %I:%M%p}")

    def refresh_meta(self):
        concern = None
        try:
            concern = ROC3Repository.get_primary_concern(self.ro_id)
        except Exception:
            concern = None

        concern_text = concern or "No concern Entered"
        fm = self.concern_label.fontMetrics()
        self.concern_label.setText(f"Concern:  {concern_text}")
        self.concern_label.setMaximumHeight(fm.lineSpacing() * 2)

        try:
            meta = RepairOrdersRepository.get_create_altered_date(self.ro_id) or {}
            created = meta.get("created_at")
            if created:
                self.created_label.setText(f"Created:  {created:%m/%d/%Y %I:%M%p}")
            else:
                self.created_label.setText("Created: -")
        except Exception:
            self.created_label.setText("Created -")

        try:
            total = RepairOrdersRepository.estimate_total_for_ro(self.ro_id)
            self.total_label.setText(f"Estimate Total:  ${total:,.2f}" if total is not None else "Estimate Total: —")
        except Exception:
            self.total_label.setText("Estimate Total: -")


    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            self.clicked.emit()

        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


    ### SCROLL AREA FOR RO TILES ###
class ROTileContainer(QtWidgets.QScrollArea):
    def __init__(self, parent=None, columns=4, hgap=12, vgap=12):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setObjectName("ro_tile_scroll")
        self.viewport().setObjectName("ro_tile_viewport")
        self._columns = columns
        self._hgap = hgap
        self._vgap = vgap


    ### INNER WRAP FOR GRID ###
        self._wrap = QtWidgets.QWidget()
        self._wrap.setObjectName("ro_tile_wrap")
        self._grid = QtWidgets.QGridLayout(self._wrap)
        self._grid.setContentsMargins(8, 8, 8, 8)
        self._grid.setHorizontalSpacing(hgap)
        self._grid.setVerticalSpacing(vgap)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self._grid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.setWidget(self._wrap)

    def clear(self):
        while self._grid.count():
            it = self._grid.takeAt(0)
            w = it.widget()
            if w:
                w.setParent(None)
                w.deleteLater()


    def add_tile(self, tile: ROTile, row: int = None, col: int = None):
        tile.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Maximum)
        if not tile.sizeHint().isValid() or tile.sizeHint().width() < 260:
            tile.setFixedWidth(320)  # tweak to taste

        count = self._grid.count()
        # allow manual row/col (for backward compat), else auto-place
        if row is None or col is None:
            r = count // self._columns
            c = count % self._columns
        else:
            r, c = row, col
        self._grid.addWidget(tile, r, c)



    def set_columns(self, n: int):
        n = max(1, int(n))
        if n != self._columns:
            self._columns = n
            self._relayout()

    def resizeEvent(self, e: QtGui.QResizeEvent):
        # infer card width from first child if present; otherwise use 320
        vw = self.viewport().width()
        card_w = 260
        if self._grid.count():
            w0 = self._grid.itemAt(0).widget()
            if w0:
                card_w = max(1, w0.sizeHint().width())
        target = max(1, int((vw + self._hgap) / (card_w + self._hgap)))
        if target != self._columns:
            self._columns = target
            self._relayout()
        super().resizeEvent(e)

    def _relayout(self):
        widgets = [self._grid.itemAt(i).widget() for i in range(self._grid.count())]
        while self._grid.count():
            self._grid.takeAt(0)
        for i, wdg in enumerate(widgets):
            r = i // self._columns
            c = i % self._columns
            self._grid.addWidget(wdg, r, c)

    def _take_out(self, tile: ROTile):
        # remove a specific tile from our grid
        idx = None
        for i in range(self._grid.count()):
            it = self._grid.itemAt(i)
            if it and it.widget() is tile:
                idx = i
                break
        if idx is not None:
            it = self._grid.takeAt(idx)
            w = it.widget()
            if w:
                w.setParent(None)