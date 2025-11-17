import pyqtgraph as pg
from datetime import date, timedelta
from enum import Enum
from openauto.managers.analytics.car_count import CarCount
from openauto.managers.analytics.gross_profit import GrossProfit
from openauto.managers.analytics.jobs_approved import JobsApproved
from openauto.managers.analytics.profit_loss import ProfitLoss
from openauto.managers.analytics.ro_averages import ROAverages
from openauto.managers.analytics.sales import Sales


class Range(Enum):
    YESTERDAY = "yesterday"
    TODAY = "today"
    LAST_7 = "last_7"
    LAST_30 = "last_30"
    LAST_12 = "last_12"


class AnalyticsManager:
    def __init__(self, ui):
        self.ui = ui
        self.current_range = Range.TODAY

        # Align pyqtgraph with the light UI theme
        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "#314455")

        self.car_count = CarCount(ui)
        self.gross_profit = GrossProfit(ui)
        self.jobs_approved = JobsApproved(ui)
        self.profit_loss = ProfitLoss(ui)
        self.ro_averages = ROAverages(ui)
        self.sales = Sales(ui)
        self.ui.reports_tree.expandAll()
        self._wire_range_buttons()
        self.refresh_all()

    def set_range(self, rng: Range):
        if rng == self.current_range:
            return
        self.current_range = rng
        self.refresh_all()

    def range_dates(self) -> tuple[date, date]:
        today = date.today()
        if self.current_range is Range.TODAY:
            return today, today
        if self.current_range is Range.YESTERDAY:
            d = today - timedelta(days=1)
            return d, d
        if self.current_range is Range.LAST_7:
            return today - timedelta(days=6), today
        if self.current_range is Range.LAST_30:
            return today - timedelta(days=29), today
        # fallback: trailing 12 months ~ 365 days
        return today - timedelta(days=365), today

    def refresh_all(self):
        start, end = self.range_dates()
        self.car_count.refresh(start, end)
        self.sales.refresh(start, end)
        self.profit_loss.refresh(start, end)
        self.jobs_approved.refresh(start, end)
        self.gross_profit.refresh(start, end)
        self.ro_averages.refresh(start, end)

    def _wire_range_buttons(self):
        button_map = [
            ("analytics_yesterday_button", Range.YESTERDAY),
            ("analytics_today_button", Range.TODAY),
            ("analytics_last_seven", Range.LAST_7),
            ("analytics_last_thirty", Range.LAST_30),
            ("analytics_last_twelve", Range.LAST_12),
        ]
        for attr, rng in button_map:
            btn = getattr(self.ui, attr, None)
            if btn is not None:
                btn.clicked.connect(lambda _, r=rng: self.set_range(r))
