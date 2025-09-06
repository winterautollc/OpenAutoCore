from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtGui import QDoubleValidator
from openauto.subclassed_widgets import small_tables, workflow_tables, apt_calendar, event_handlers, control_menu
from openauto.ui import main_form
from openauto.managers import (
    customer_manager, vehicle_manager, settings_manager,
    animations_manager, new_ro_manager, belongs_to_manager, appointments_manager, appointment_options_manager,
    ro_hub_manager
)
from pyvin import VIN
import os


class ExpandingTabBar(QtWidgets.QTabBar):
    def tabSizeHint(self, index: int) -> QtCore.QSize:
        s = super().tabSizeHint(index)
        count = max(1, self.count())
        # width: fall back safely if width() is 0 early in layout
        avail = self.width()
        if not avail and self.parent():
            avail = self.parent().width()
        if not avail:
            avail = s.width() or 1
        w = max(s.width(), avail // count)

        # height: never let it collapse
        fm = self.fontMetrics()
        min_h = max(28, fm.height() + fm.leading() + 12)  # ~ one line + padding
        return QtCore.QSize(w, max(min_h, s.height()))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.updateGeometry()

def apply_stylesheet(widget, relative_path):
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    theme_path = os.path.join(base_path, relative_path)
    try:
        with open(theme_path, "r") as f:
            widget.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"⚠️ Could not load theme: {theme_path}")
def load_icon(rel_path: str) -> QtGui.QIcon:
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    full_path = os.path.join(base_path, rel_path)
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(full_path), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
    return icon

class MainWindow(QtWidgets.QMainWindow, main_form.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.ro_hub_tabs.tabBar().setUsesScrollButtons(True)
        self.ro_hub_tabs.setUsesScrollButtons(True)
        # self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.sql_monitor = event_handlers.SQLMonitor()
        self.sql_monitor.start()
        self._init_managers()
        self._init_validators()
        self._init_tables()
        self._init_state()
        self._connect_signals()
        self._setup_animations()
        self.toggle_theme()
        self._setup_menu_label_opacity()


    ### DECLARE MANAGERS ###
    def _init_managers(self):
        self.widget_manager = event_handlers.WidgetManager()
        self.customer_manager = customer_manager.CustomerManager(self)
        self.vehicle_manager = vehicle_manager.VehicleManager(self)
        self.settings_manager = settings_manager.SettingsManager(self)
        self.animations_manager = animations_manager.AnimationsManager(self)
        self.new_ro_manager = new_ro_manager.NewROManager(self)
        self.belongs_to_manager = belongs_to_manager.BelongsToManager(self)
        self.appointments_manager = appointments_manager.AppointmentsManager(self, self.sql_monitor)
        self.ro_hub_manager = ro_hub_manager.ROHubManager(self)


### VALIDATORS TO ONLY ALLOW CERTAIN CHARACTERS ENTERED ###
    def _init_validators(self):
        self.float_validator = QDoubleValidator()
        self.float_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.float_validator.setDecimals(1)
        self.warranty_time_line.setValidator(self.float_validator)
        self.warranty_miles_line.setValidator(self.float_validator)

### DECLARE SUBCLASSED TABLE WIDGETS ###
    def _init_tables(self):
        self.cmenu_frame = control_menu.ControlMenu(parent=self)
        self.customer_table = workflow_tables.CustomerTable(parent=self)
        self.vehicle_table = workflow_tables.VehicleTable(parent=self)
        self.matrix_table = small_tables.MatrixTable(parent=self)
        self.labor_table = small_tables.LaborTable(parent=self)
        self.estimates_table = workflow_tables.EstimateTable(parent=self)
        self.working_table = workflow_tables.WorkingTable(parent=self)
        self.approved_table = workflow_tables.ApprovedTable(parent=self)
        self.checkout_table = workflow_tables.CheckoutTable(parent=self)
        self.show_all_table = workflow_tables.ShowAll(parent=self)
        self.schedule_calendar = apt_calendar.AptCalendar(parent=self)
        self.hourly_schedule_table = apt_calendar.HourlySchedule(parent=self)
        self.weekly_schedule_table = apt_calendar.WeeklySchedule(parent=self)

### ADD MAIN BUTTONS TO CMENU ###
        self.verticalLayout = QtWidgets.QVBoxLayout(self.cmenu_frame)
        self.verticalLayout.addWidget(self.customers_button)
        self.verticalLayout.addWidget(self.repair_orders_button)
        self.verticalLayout.addWidget(self.vehicles_button)
        self.verticalLayout.addWidget(self.messaging_button)
        self.verticalLayout.addWidget(self.scheduling_button)
        self.verticalLayout.addWidget(self.analytics_button)
        self.verticalLayout.addWidget(self.settings_button)
        self.verticalLayout.addWidget(self.quit_button)


### ADD ALL SUBCLASSED WIDGETS TO LAYOUT ###
        self.gridLayout_2.addWidget(self.cmenu_frame, 2, 0, 2, 1)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_11.addWidget(self.customer_table, 0, 0, 1, 1)
        self.gridLayout_19.addWidget(self.vehicle_table, 0, 0, 1, 1)
        self.gridLayout_24.addWidget(self.matrix_table, 1, 0, 1, 2)
        self.gridLayout_26.addWidget(self.labor_table, 1, 0, 1, 2)
        self.gridLayout_5.addWidget(self.estimates_table, 1, 0, 1, 1)
        self.gridLayout_7.addWidget(self.working_table, 0, 0, 1, 1)
        self.gridLayout_6.addWidget(self.approved_table, 0, 0, 1, 1)
        self.gridLayout_8.addWidget(self.checkout_table, 0, 0, 1, 1)
        self.gridLayout_9.addWidget(self.show_all_table, 0, 0, 1, 1)
        self.gridLayout_33.addWidget(self.schedule_calendar, 0, 0, 1, 1)
        self.gridLayout_31.addWidget(self.weekly_schedule_table, 0, 0, 1, 1)
        self.gridLayout_34.addWidget(self.hourly_schedule_table, 0, 0, 1, 1)


    def _init_state(self):
        self.message = QtWidgets.QMessageBox()
        self.name_box_result = None
        self.warranty_time_line.hide()
        self.warranty_miles_line.hide()
        self.ro_tabs.setCurrentIndex(0)


        # dynamic windows
        self.show_new_customer_page = None
        self.show_new_customer_page_ui = None
        self.vehicle_window = None
        self.vehicle_window_ui = None
        self.belongs_to_window = None
        self.belongs_to_window_ui = None
        self.new_ro_page = None
        self.new_ro_page_ui = None
        self.customer_table_small = None
        self.vehicle_table_small = None
        self.customer_id_small = None
        self.vehicle_id_small = None
        self.customer_id = None
        self.vin = VIN
        self.current_ro_id = None
        self.settings_manager.load_shop_info()


### HIDE LABELS IN CMENU ###
    def _setup_menu_label_opacity(self):
        texts = [
            "Customers", "Repair Orders", "Vehicles", "Messages",
            "Schedule", "Analytics", "Settings", "Quit"
        ]
        buttons = [
            self.customers_button, self.repair_orders_button, self.vehicles_button,
            self.messaging_button, self.scheduling_button, self.analytics_button,
            self.settings_button, self.quit_button
        ]
        for button, text in zip(buttons, texts):
            QtWidgets.QPushButton.setText(button, "")


### SIGNALS/SLOTS FOR PUSHBUTTONS ETC.. ###
    def _connect_signals(self):
        self.search_customer_line.setPlaceholderText("Search ...")
        self.vehicle_search_line.setPlaceholderText("Search ...")
        self.ro_search_edit.setPlaceholderText("Search ...")
        self.search_customer_line.textChanged.connect(self.customer_manager.customer_search_filter)
        self.vehicle_search_line.textChanged.connect(self.vehicle_manager.vehicle_search_filter)
        self.customer_table.vehicle_signal_request.connect(self.vehicle_manager.add_vehicle)
        self.customer_table.ro_signal_request.connect(self.animations_manager.ro_hub_page_show)
        self.vehicle_table.ro_signal_request.connect(self.animations_manager.ro_hub_page_show)
        self.quit_button.clicked.connect(self.ask_quit)
        self.show_all_ro_button.clicked.connect(self.animations_manager.show_all_ros)
        self.estimates_button.clicked.connect(self.animations_manager.show_estimates)
        self.approved_button.clicked.connect(self.animations_manager.show_approved)
        self.working_ro_button.clicked.connect(self.animations_manager.show_working)
        self.checkout_button.clicked.connect(self.animations_manager.show_checkout)
        self.customers_button.clicked.connect(self.animations_manager.customer_page_show)
        self.repair_orders_button.clicked.connect(self.animations_manager.show_repair_orders)
        self.repair_orders_button.clicked.connect(self.animations_manager.ro_page_show)
        self.new_customer_button.clicked.connect(self.customer_manager.open_new_customer)
        self.vehicles_button.clicked.connect(self.animations_manager.vehicle_page_show)
        self.new_vehicle_button.setMaximumWidth(200)
        self.month_button.setMaximumWidth(200)
        self.day_button.setMaximumWidth(200)
        self.week_button.setMaximumWidth(200)
        self.new_vehicle_button.clicked.connect(self.vehicle_manager.add_new_vehicle)
        self.settings_button.clicked.connect(self.animations_manager.settings_page_show)
        self.appearance_button.clicked.connect(self.show_appearance)
        self.add_row_button.clicked.connect(self.settings_manager.add_matrix_row)
        self.add_labor_row.clicked.connect(self.settings_manager.add_labor_rates)
        self.remove_labor_row.clicked.connect(self.settings_manager.remove_labor_rate)
        self.remove_row_button.clicked.connect(self.settings_manager.remove_matrix_row)
        self.save_matrix_button.clicked.connect(self.settings_manager.save_pricing_matrix)
        self.save_settings_button.clicked.connect(self.settings_manager.save_shop_settings)
        self.save_labor_button.clicked.connect(self.settings_manager.save_labor_rates)
        self.warranty_time_checkbox.toggled.connect(self.settings_manager.set_warranty_time)
        self.warranty_miles_checkbox.toggled.connect(self.settings_manager.set_warranty_duration)
        self.import_logo_button.clicked.connect(self.settings_manager.load_shop_logo)
        self.new_ro_button.clicked.connect(self.new_ro_manager.add_repair_order)
        self.scheduling_button.clicked.connect(self.animations_manager.show_schedule)
        self.week_button.hide()
        self.month_button.clicked.connect(self.animations_manager.show_schedule)
        self.day_button.setText("Today")
        self.day_button.clicked.connect(self.animations_manager.show_hourly)
        self.schedule_calendar.date_selected.connect(self.weekly_schedule_table.set_horizontal_headers_for_date)
        self.schedule_calendar.date_selected.connect(self.weekly_schedule_table.load_appointments)
        self.schedule_calendar.date_selected.connect(self.animations_manager.show_week)
        self.weekly_schedule_table.add_appointment.connect(self.appointments_manager.open_new_appointment)
        self.weekly_schedule_table.appointment_options.connect(self._open_appointment_options)
        self.sql_monitor.customer_updates.connect(self.customer_table.update_customers)
        self.sql_monitor.estimate_updates.connect(self.estimates_table.update_estimates)
        self.sql_monitor.vehicle_update.connect(self.vehicle_table.update_vehicles)
        self.sql_monitor.appointment_data.connect(lambda: self.weekly_schedule_table.load_appointments(self.schedule_calendar.selectedDate()))
        self.sql_monitor.appointment_data.connect(lambda: self.hourly_schedule_table.load_schedule_for_day(self.schedule_calendar.selectedDate()))
        self.messaging_button.clicked.connect(self.texting_not_ready)
        self.hourly_schedule_table.edit_appointment.connect(self._open_appointment_options)
        self.hourly_schedule_table.add_appointment.connect(self.appointments_manager.open_new_appointment)

### DECLARES ANIMATIONS FOR SWITCHING PAGES ###
    def _setup_animations(self):
        def anim(target, duration=300):
            return QtCore.QPropertyAnimation(target, b'geometry', duration=duration)

        self.animate_open_header = anim(self.customer_frame)
        self.animate_ctable = anim(self.customer_table, 700)
        self.animate_ro_header = anim(self.ro_frame)
        self.animate_rtable = anim(self.ro_tabs, 700)
        self.animate_vehicle_header = anim(self.vehicle_header_frame)
        self.animate_vehicle_table = anim(self.vehicle_table, 700)
        self.animate_settings_header = anim(self.settings_header_buttons)
        self.animate_settings_frame = anim(self.settings_frame, 700)
        self.animate_ro_hub_page = anim(self.ro_control_page, 500)
        self.animate_month_calendar = anim(self.schedule_calendar, 500)
        self.animate_week = anim(self.weekly_schedule_table, 300)
        self.animate_day = anim(self.hourly_schedule_table, 300)

    def toggle_theme(self):
        theme = "theme/dark_theme.qss"
        apply_stylesheet(self, theme)

    def show_appearance(self):
        self.message.setText("I Know It's Ugly But Appearance Customization Isn't Ready Yet... Sorry")
        self.message.show()

    def ask_quit(self):
        reply = QtWidgets.QMessageBox.question(
            self, 'Confirm Quit', 'Really quit?',
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            QtWidgets.QApplication.quit()


    def ro_hub_items(self):
        self.vin_ro_box.addItem(self.vehicle_window_ui.vin_line.text())
        self.year_ro_label.setText(self.vehicle_window_ui.year_line.text())
        self.make_ro_label.setText(self.vehicle_window_ui.make_line.text())
        self.model_ro_label.setText(self.vehicle_window_ui.model_line.text())
        self.engine_size_ro_label.setText(self.vehicle_window_ui.engine_line.text())

    def _open_appointment_options(self, appt_id):
        self.appointment_options_window = appointment_options_manager.AppointmentOptionsManager(self, appt_id)


    def texting_not_ready(self):
        self.message.setWindowTitle("SMS To Customers")
        self.message.setText("SMS To Customers, Plate2VIN And Parts Ordering Will Require A Monthly Subscription")
        self.message.exec()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.processEvents()
    sys.exit(app.exec())
