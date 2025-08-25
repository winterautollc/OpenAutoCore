from PyQt6 import QtCore
from PyQt6.QtCore import QEvent, QObject, pyqtSignal, QThread, QDate
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from PyQt6 import QtWidgets
from openauto.repositories import customer_repository, vehicle_repository, appointment_repository
import time


### EVENT FILTER TO ANIMATE MENU COLLAPSE WHEN MOUSE ISIN'T HOVERED OVER IT AND EXPAND ON MOUSE HOVER  ###
class CMenuHandler(QObject):
    def __init__(self, target_widget):
        super().__init__()
        self.target_widget = target_widget
        self.animate_menu_open = QPropertyAnimation(self.target_widget, b'geometry')
        self.animate_menu_close = QPropertyAnimation(self.target_widget, b'geometry')
        self.animate_menu_open.setDuration(300)
        self.animate_menu_close.setDuration(300)
        self.opacity_effect = QGraphicsOpacityEffect()
        self.frame_height = self.target_widget.height()
        self.texts = ["Customers", "Repair Orders", "Vehicles", "Messages", "Schedule", "Analytics", "Settings", "Quit"]

    def eventFilter(self, obj, event: QMouseEvent):
        buttons = obj.findChildren(QtWidgets.QPushButton)

        if obj is self.target_widget:
            if event.type() == QEvent.Type.Enter:
                self.animate_menu_open.setEndValue(QRect(9, 65, 125, 890))
                self.animate_menu_open.setEasingCurve(QEasingCurve.Type.InOutQuart)
                self.animate_menu_open.start()
                for button, text in zip(buttons, self.texts):
                    button.setToolTip(text)
                    # QtWidgets.QToolTip.showText(button, text)
                    # QtWidgets.QToolTip.showText(button.mapToGlobal(QtCore.QPoint(0, button.height())), text)


            elif event.type() == QEvent.Type.Leave:
                self.animate_menu_close.setEndValue(QRect(9, 65, 60, 890))
                self.animate_menu_close.setEasingCurve(QEasingCurve.Type.InOutQuart)
                self.animate_menu_close.start()

                for button, text in zip(buttons, self.texts):
                    button.setToolTip("")
                    # QtWidgets.QToolTip.hideText()

        return super().eventFilter(obj, event)
    
### QTHREAD TO MONITOR CHANGES IN DATABASE. USING ONE QTHREAD FOR ALL TABLES AS IT SHOULD BE MORE EFFICIENT###
### MAY CHANGE TO QEVENT LATER ###
class SQLMonitor(QThread):
    customer_updates = pyqtSignal(list)
    estimate_updates = pyqtSignal(list)
    estimate_item_updates = pyqtSignal(list)
    invoice_update = pyqtSignal(list)
    vehicle_update = pyqtSignal(list)
    belongs_to_update = pyqtSignal(list)
    small_customers_update = pyqtSignal(list)
    small_vehicles_update = pyqtSignal(list)
    appointment_data = pyqtSignal(list)
    hourly_schedule_update = pyqtSignal()


    def __init__(self):
        super().__init__()
        self.last_customer_data = None
        self.last_estimates_data = None
        self.last_estimate_item_data = None
        self.last_invoice_data = None
        self.last_vehicle_data = None
        self.last_belongs_to_data = None
        self.last_customer_small_data = None
        self.last_vehicle_small_data = None
        self.last_appointment_data = None
        self.last_hourly_data = None

    def run(self):
            while True:
                try:
                    customer_data = customer_repository.CustomerRepository.get_all_customer_info()
                    vehicle_data = vehicle_repository.VehicleRepository.get_all_vehicle_info()
                    # belongs_to_data = customer_repository.CustomerRepository.get_all_customer_names()
                    customer_small_data = customer_repository.CustomerRepository.get_all_customer_names()
                    vehicle_small_data = vehicle_repository.VehicleRepository.get_all_vehicles()
                    appointment_data = appointment_repository.AppointmentRepository.get_appointment_ids_and_timestamps()
                    # try:
                    #     today = QDate.currentDate().toString("yyyy-MM-dd")
                    #     data = appointment_repository.AppointmentRepository.get_appointments_for_week(
                    #         QDate.fromString(today, "yyyy-MM-dd"), QDate.fromString(today, "yyyy-MM-dd")
                    #     )
                    #
                    #     # Simple version: compare row count
                    #     if self.last_hourly_data is None or len(data) != len(self.last_hourly_data):
                    #         self.last_hourly_data = data
                    #         self.hourly_schedule_update.emit()
                    # except Exception as e:
                    #     print("[SQLMonitor] Error in hourly schedule polling:", e)

                    if customer_data != self.last_customer_data:
                        self.last_customer_data = customer_data
                        self.customer_updates.emit(customer_data)

                    if vehicle_data != self.last_vehicle_data:
                        self.last_vehicle_data = vehicle_data
                        self.vehicle_update.emit(vehicle_data)
                    #
                    # if belongs_to_data != self.last_belongs_to_data:
                    #     self.last_belongs_to_data = belongs_to_data
                    #     self.belongs_to_update.emit(belongs_to_data)

                    if customer_small_data != self.last_customer_small_data:
                        self.last_customer_small_data = customer_small_data
                        self.small_customers_update.emit(customer_small_data)

                    if vehicle_small_data != self.last_vehicle_small_data:
                        self.last_vehicle_small_data = vehicle_small_data
                        self.small_vehicles_update.emit(vehicle_small_data)

                    if appointment_data != self.last_appointment_data:
                        self.last_appointment_data = appointment_data
                        self.appointment_data.emit(appointment_data)

                except Exception as e:
                    print(f"[SQLMonitor] Error during polling: {e}")

                time.sleep(1)




### CLASS TO CREATE AND DELETE WIDGETS AND WINDOWS FROM MEMORY WHEN CLOSED ###
class WidgetManager:
    def __init__(self):
        self.widgets = {}

    def create_or_restore(self, key, widget_class, ui_class, *args, **kwargs):
        # If widget exists and hasn't been deleted, delete it
        if key in self.widgets and self.widgets[key] is not None:
            try:
                self.widgets[key].close()
                self.widgets[key].deleteLater()
            except Exception:
                pass
            self.widgets[key] = None

        # Create new widget
        widget = widget_class(*args, **kwargs)
        widget.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        ui = ui_class()
        ui.setupUi(widget)

        self.widgets[key] = widget
        return widget, ui

    def get_widget(self, key):
        return self.widgets.get(key, None)

    def close_and_delete(self, key):
        if key in self.widgets and self.widgets[key] is not None:
            self.widgets[key].close()
            self.widgets[key].deleteLater()
            self.widgets[key] = None