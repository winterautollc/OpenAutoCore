from PyQt6 import QtCore
from PyQt6.QtCore import QRect, QEasingCurve
from openauto.subclassed_widgets import event_handlers

class AnimationsManager:
    def __init__(self, main_window):
        self.ui = main_window
        self._setup_animations()

    def _setup_animations(self):
        def anim(target, duration=300):
            return QtCore.QPropertyAnimation(target, b'geometry', duration=duration)


        self.animate_open_header = anim(self.ui.customer_frame)
        self.animate_ctable = anim(self.ui.customer_table, 700)
        self.animate_ro_header = anim(self.ui.ro_frame)
        self.animate_rtable = anim(self.ui.ro_tabs, 700)
        self.animate_vehicle_header = anim(self.ui.vehicle_header_frame)
        self.animate_vehicle_table = anim(self.ui.vehicle_table, 700)
        self.animate_settings_header = anim(self.ui.settings_header_buttons)
        self.animate_settings_frame = anim(self.ui.settings_frame, 700)
        self.animate_ro_hub_page = anim(self.ui.ro_control_page, 300)
        self.animate_schedule_header = anim(self.ui.calender_header_buttons, 500)

        self.cmenu_hover_filter = event_handlers.CMenuHandler(self.ui.cmenu_frame)
        self.ui.cmenu_frame.installEventFilter(self.cmenu_hover_filter)

    def show_page(self, hub_index: int, tab_index: int = None, table_widget=None, top_bar_index: int = None):
        self.ui.hub_stacked_widget.setCurrentIndex(hub_index)

        if tab_index is not None:
            self.ui.ro_tabs.setCurrentIndex(tab_index)

        if top_bar_index is not None:
            self.ui.top_buttons_stacked.setCurrentIndex(top_bar_index)

        if table_widget:
            table_widget.show()

    def show_estimates(self):
        r_table_w = self.ui.ro_tabs.width()
        r_table_h = self.ui.ro_tabs.height()
        self.ui.animate_rtable.setStartValue(QRect(9, 9, 0, 0))
        self.ui.animate_rtable.setEndValue(QRect(9, 9, r_table_w, r_table_h))
        self.ui.animate_rtable.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.ui.animate_rtable.start()
        self.show_page(hub_index=0, tab_index=0, table_widget=self.ui.estimates_table, top_bar_index=0)

    def show_working(self):
        r_table_w = self.ui.ro_tabs.width()
        r_table_h = self.ui.ro_tabs.height()
        self.ui.animate_rtable.setStartValue(QRect(9, 9, 0, 0))
        self.ui.animate_rtable.setEndValue(QRect(9, 9, r_table_w, r_table_h))
        self.ui.animate_rtable.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.ui.animate_rtable.start()
        self.show_page(hub_index=0, tab_index=1, table_widget=self.ui.working_table, top_bar_index=0)

    def show_approved(self):
        r_table_w = self.ui.ro_tabs.width()
        r_table_h = self.ui.ro_tabs.height()
        self.ui.animate_rtable.setStartValue(QRect(9, 9, 0, 0))
        self.ui.animate_rtable.setEndValue(QRect(9, 9, r_table_w, r_table_h))
        self.ui.animate_rtable.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.ui.animate_rtable.start()
        self.show_page(hub_index=0, tab_index=2, table_widget=self.ui.approved_table, top_bar_index=0)

    def show_checkout(self):
        r_table_w = self.ui.ro_tabs.width()
        r_table_h = self.ui.ro_tabs.height()
        self.ui.animate_rtable.setStartValue(QRect(9, 9, 0, 0))
        self.ui.animate_rtable.setEndValue(QRect(9, 9, r_table_w, r_table_h))
        self.ui.animate_rtable.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.ui.animate_rtable.start()
        self.show_page(hub_index=0, tab_index=3, table_widget=self.ui.checkout_table, top_bar_index=0)

    def show_all_ros(self):
        r_table_w = self.ui.ro_tabs.width()
        r_table_h = self.ui.ro_tabs.height()
        self.ui.animate_rtable.setStartValue(QRect(9, 9, 0, 0))
        self.ui.animate_rtable.setEndValue(QRect(9, 9, r_table_w, r_table_h))
        self.ui.animate_rtable.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.ui.animate_rtable.start()
        self.show_page(hub_index=0, tab_index=4, table_widget=self.ui.show_all_table, top_bar_index=0)

    def customer_page_show(self):
        c_header_w = self.ui.ro_frame.width()
        c_header_h = self.ui.ro_frame.height()
        ctable_w = self.ui.ro_tabs.width()
        ctable_h = self.ui.ro_tabs.height()
        self.ui.animate_open_header.setStartValue(QRect(0, 0, 0, 0))
        self.ui.animate_ctable.setStartValue(QRect(9, 9, 0, 0))
        self.ui.animate_open_header.setEndValue(QRect(0, 0, c_header_w, c_header_h))
        self.ui.animate_ctable.setEndValue((QRect(9, 9, ctable_w, ctable_h)))
        self.ui.animate_open_header.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.ui.animate_ctable.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.ui.animate_open_header.start()
        self.ui.animate_ctable.start()
        self.show_page(hub_index=1, table_widget=self.ui.customer_table, top_bar_index=3)

    def vehicle_page_show(self):
        v_table_w = self.ui.ro_tabs.width()
        v_table_h = self.ui.ro_tabs.height()
        v_header_w = self.ui.ro_frame.width()
        v_header_h = self.ui.ro_frame.height()
        self.ui.animate_vehicle_header.setStartValue(QRect(0, 0, 0, 0))
        self.ui.animate_vehicle_table.setStartValue(QRect(9, 9, 0, 0))
        self.ui.animate_vehicle_header.setEndValue(QRect(0, 0, v_header_w, v_header_h))
        self.ui.animate_vehicle_table.setEndValue(QRect(9, 9, v_table_w, v_table_h))
        self.ui.animate_vehicle_header.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.ui.animate_vehicle_table.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.ui.animate_vehicle_header.start()
        self.ui.animate_vehicle_table.start()
        self.show_page(hub_index=4, table_widget=self.ui.vehicle_table, top_bar_index=1)

    def settings_page_show(self):
        s_frame_w = self.ui.ro_tabs.width()
        s_frame_h = self.ui.ro_tabs.height()
        s_header_w = self.ui.ro_frame.width()
        s_header_h = self.ui.ro_frame.height()
        self.ui.animate_settings_header.setStartValue(QRect(0, 0, 0, 0))
        self.ui.animate_settings_frame.setStartValue(QRect(9, 9, 0, 0))
        self.ui.animate_settings_header.setEndValue(QRect(0, 0, s_header_w, s_header_h))
        self.ui.animate_settings_frame.setEndValue(QRect(9, 9, s_frame_w, s_frame_h))
        self.ui.animate_settings_frame.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.ui.animate_settings_header.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.ui.animate_settings_header.start()
        self.ui.animate_settings_frame.start()
        self.show_page(hub_index=7, table_widget=self.ui.matrix_table, top_bar_index=5)

    def ro_page_show(self):
        self.show_page(hub_index=0, top_bar_index=0)  # RO page base view only

    def ro_hub_page_show(self):
        w, h = self.ui.ro_tabs.width(), self.ui.ro_tabs.height()
        self.animate_ro_hub_page.setStartValue(QRect(0, 0, 0, 0))
        self.animate_ro_hub_page.setEndValue(QRect(9, 9, w, h))
        self.animate_ro_hub_page.start()
        self.ui.top_buttons_stacked.setCurrentIndex(2)
        self.ui.hub_stacked_widget.setCurrentIndex(8)

    def show_repair_orders(self):
        r_table_w = self.ui.ro_tabs.width()
        r_table_h = self.ui.ro_tabs.height()
        self.ui.animate_rtable.setStartValue(QRect(9, 9, 0, 0))
        self.ui.animate_rtable.setEndValue(QRect(9, 9, r_table_w, r_table_h))
        self.ui.animate_rtable.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.ui.animate_rtable.start()
        self.ui.ro_tabs.setCurrentIndex(0)
        self.ui.hub_stacked_widget.setCurrentIndex(0)
        self.ui.top_buttons_stacked.setCurrentIndex(0)
        self.ui.estimates_table.show()

    def show_schedule(self):
        w, h = self.ui.ro_tabs.width(), self.ui.ro_tabs.height()
        h_w, h_h = self.ui.ro_frame.width(), self.ui.ro_frame.height()
        self.ui.animate_month_calendar.setStartValue(QRect(9, 9, 0, 0))
        self.ui.animate_month_calendar.setEndValue(QRect(9, 9, w, h))
        self.animate_schedule_header.setStartValue(QRect(0, 0, 0, 0))
        self.animate_schedule_header.setEndValue(QRect(0, 0, h_w, h_h))
        self.ui.animate_month_calendar.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.ui.animate_month_calendar.start()
        self.animate_schedule_header.start()
        self.show_page(hub_index=2, table_widget=self.ui.schedule_calendar, top_bar_index=4)
        self.ui.schedule_calendar.show()
        self.ui.calender_header_buttons.show()


    def show_week(self):
        w, h = self.ui.ro_tabs.width(), self.ui.ro_tabs.height()

        self.ui.animate_week.setStartValue(QRect(0, 0, 0, 0))
        self.ui.animate_week.setEndValue(QRect(9, 9, w, h))
        self.ui.animate_week.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.ui.animate_week.start()
        self.show_page(hub_index=6, table_widget=self.ui.weekly_schedule_table, top_bar_index=4)


    def show_hourly(self):
        w, h = self.ui.ro_tabs.width(), self.ui.ro_tabs.height()
        self.ui.animate_day.setStartValue(QRect(0, 0, 0, 0))
        self.ui.animate_day.setEndValue(QRect(9, 9, w, h))
        self.ui.animate_day.start()
        self.show_page(hub_index=5, table_widget=self.ui.hourly_schedule_table, top_bar_index=4)
