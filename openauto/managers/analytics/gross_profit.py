from PyQt6 import QtWidgets
from pyqtgraph import PlotWidget



class GrossProfit:
    def __init__(self, ui):
        self.ui = ui
        self.frame = self.ui.gross_profit_dashboard_frame
        self.ui.gross_profit_dashboard_frame.setMaximumHeight(300)
        self._init_ui()
        
        
    def _init_ui(self):
        layout = self.frame.layout()
        if isinstance(layout, QtWidgets.QFormLayout):
            self.plot = PlotWidget(self.frame)
            self.plot.setMouseEnabled(x=False, y=False)
            layout.setWidget(1, QtWidgets.QFormLayout.ItemRole.SpanningRole, self.plot)
        else:
            if layout is None:
                layout = QtWidgets.QVBoxLayout(self.frame)
                layout.setContentsMargins(0, 0, 0, 0)
                self.frame.setLayout(layout)
            self.plot = PlotWidget(self.frame)
            self.plot.setMouseEnabled(x=False, y=False)
            layout.addWidget(self.plot)
            
            
    def refresh(self, start_date=None, end_date=None):
        self.plot.clear()
