from datetime import date
import pyqtgraph as pg
from PyQt6 import QtWidgets
from openauto.repositories.repair_orders_repository import RepairOrdersRepository


class CarCount:
    def __init__(self, ui):
        self.ui = ui
        self.frame = self.ui.car_count_dashboard_frame
        self.ui.car_count_dashboard_frame.setMaximumHeight(300)
        self._init_ui()

    def _init_ui(self):
        layout = self.frame.layout()
        if isinstance(layout, QtWidgets.QFormLayout):
            self.plot = pg.PlotWidget(self.frame)
            layout.setWidget(1, QtWidgets.QFormLayout.ItemRole.SpanningRole, self.plot)
        else:
            if layout is None:
                layout = QtWidgets.QVBoxLayout(self.frame)
                layout.setContentsMargins(0, 0, 0, 0)
                self.frame.setLayout(layout)
            self.plot = pg.PlotWidget(self.frame)
            layout.addWidget(self.plot)
        self.plot.setMenuEnabled(False)
        self.plot.setMouseEnabled(x=False, y=False)
        self.plot.showGrid(x=True, y=True, alpha=0.15)

    def refresh(self, start_date: date, end_date: date):
        self.plot.clear()
        rows = RepairOrdersRepository.car_counts_by_day(start_date, end_date) or []
        axis = self.plot.getPlotItem().getAxis("bottom")
        axis.setTicks([])
        if not rows:
            return

        counts = [cnt for _, cnt in rows]
        x_vals = list(range(len(rows)))
        labels = [
            (idx, day.strftime("%m/%d") if hasattr(day, "strftime") else str(day))
            for idx, (day, _) in enumerate(rows)
        ]
        axis.setTicks([labels])
        self.plot.getPlotItem().setLabel("left", "Vehicles")
        self.plot.getPlotItem().setLabel("bottom", "Date")

        total_days = (end_date - start_date).days + 1
        if total_days <= 7:
            bars = pg.BarGraphItem(x=x_vals, height=counts, width=0.6, brush="#2f80ed", pen=pg.mkPen("#1b4fb5"))
            self.plot.addItem(bars)
        else:
            self.plot.plot(
                x_vals,
                counts,
                pen=pg.mkPen("#2f80ed", width=2),
                symbol="o",
                symbolSize=6,
                symbolBrush="#2f80ed",
            )
