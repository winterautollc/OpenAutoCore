from PyQt6 import QtWidgets, QtGui, QtCore
import os


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

class ROTile(QtWidgets.QFrame):
    clicked = QtCore.pyqtSignal()
    statusChangeRequested = QtCore.pyqtSignal(int, str)

    def __init__(self, ro_id, ro_number, customer_name, vehicle, tech, writer, concern, status,
                 parent=None, icon_dir: str = "theme/icons"):
        super().__init__(parent)
        self.ro_id = ro_id
        self.status = status
        layout = QtWidgets.QVBoxLayout(self)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.OpenHandCursor))
        self.setObjectName("ro_tile")

        self.setStyleSheet("""
                     QFrame {
                         background-color: #d2d7db;
                         border-radius: 12px;
                         padding: 12px;
                     }
                     QLabel {
                         font-size: 12pt;
                         color: #1E1E1E,
                     }
                     QLabel.title {
                         font-weight: bold;
                         font-size: 14pt;
                     }
                 """)
        self.ro_label = QtWidgets.QLabel(f"RO #{ro_number}")
        self.ro_label.setObjectName("title")
        self.customer_label = QtWidgets.QLabel(f"Customer: {customer_name}")
        self.vehicle_label = QtWidgets.QLabel(f"Vehicle: {vehicle}")

        roles = QtWidgets.QHBoxLayout(); roles.setSpacing(8)

        tech_wrap = QtWidgets.QHBoxLayout(); tech_wrap.setSpacing(6)
        tech_icon = _maybe_icon(os.path.join(icon_dir, "tech.png"), "🛠")
        tech_lbl  = QtWidgets.QLabel(tech or "Unassigned")
        tech_lbl.setObjectName("ro_tech")
        tech_lbl.setProperty("role", "chip")
        tech_box = QtWidgets.QWidget()
        tech_box.setObjectName("chip_block")
        tech_box.setStyleSheet("background-color: #d2d7db; color: #050608")
        tech_box.setLayout(tech_wrap)
        tech_wrap.addWidget(tech_icon)
        tech_wrap.addWidget(tech_lbl)

        writer_wrap = QtWidgets.QHBoxLayout(); writer_wrap.setSpacing(6)
        writer_icon = _maybe_icon(os.path.join(icon_dir, "writer.png"), "💬")
        writer_lbl  = QtWidgets.QLabel(writer or "Unassigned")
        writer_lbl.setObjectName("ro_writer")
        writer_lbl.setProperty("role", "chip")
        writer_box = QtWidgets.QWidget()
        writer_box.setObjectName("chip_block")
        writer_box.setStyleSheet("background-color: #d2d7db; color: #050608")
        writer_box.setLayout(writer_wrap)
        writer_wrap.addWidget(writer_icon)
        writer_wrap.addWidget(writer_lbl)

        roles.addWidget(tech_box)
        roles.addWidget(writer_box)
        roles.addStretch(1)

        self.concern_label = QtWidgets.QLabel(f"Concern: {concern}")

        # assemble
        layout.addWidget(self.ro_label)
        layout.addWidget(self.customer_label)
        layout.addWidget(self.vehicle_label)
        layout.addLayout(roles)
        layout.addWidget(self.concern_label)
        layout.addStretch()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent):
        menu = QtWidgets.QMenu(self)

        actions = [
            ("Move to Approved", "approved"),
            ("Move to Working", "working"),
            ("Move to Checkout", "checkout"),
            ("Revert to Estimate", "open"),
            ("Archive", "archived"),
        ]

        for label, target_status in actions:
            # Skip any action that would set the *current* status
            if target_status == self.status:
                continue
            act = menu.addAction(label)
            # capture target_status correctly for each action
            act.triggered.connect(lambda _, s=target_status: self.statusChangeRequested.emit(self.ro_id, s))

        menu.exec(event.globalPos())


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
        # effect = QtWidgets.QGraphicsOpacityEffect(tile)
        # tile.setGraphicsEffect(effect)
        # effect.setOpacity(0.0)
        # anim = QtCore.QPropertyAnimation(effect, b"opacity", tile)
        # anim.setDuration(300)
        # anim.setStartValue(0.0)
        # anim.setEndValue(1.0)
        # anim.start(QtCore.QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)


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
