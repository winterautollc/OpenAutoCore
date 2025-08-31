from PyQt6 import QtCore
from PyQt6.QtCore import QEvent, QObject, pyqtSignal, QThread, QDate
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtCore import (QPropertyAnimation, QEasingCurve, QRect, QSequentialAnimationGroup,
                          QPauseAnimation, QParallelAnimationGroup)
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from PyQt6 import QtWidgets
from openauto.repositories import customer_repository, vehicle_repository, appointment_repository, estimates_repository
import time


### EVENT FILTER TO ANIMATE MENU COLLAPSE WHEN MOUSE ISIN'T HOVERED OVER IT AND EXPAND ON MOUSE HOVER  ###
class CMenuHandler(QObject):
    def __init__(self, target_widget):
        super().__init__()
        self.target = target_widget
        self.texts = [
            "  Customers", "  Repair Orders", "  Vehicles", "  Messages",
            "  Schedule", "  Analytics", "  Settings", "  Quit"
        ]
        # Width animations: use minimumWidth so grid honors it
        self.animate_menu_open  = QPropertyAnimation(self.target, b"minimumWidth")
        self.animate_menu_close = QPropertyAnimation(self.target, b"minimumWidth")
        for a in (self.animate_menu_open, self.animate_menu_close):
            a.setDuration(350)
            a.setEasingCurve(QEasingCurve.Type.InOutQuart)

        # sane padding for width calc
        self.icon_area = 40
        self.side_pad  = 24
        self.labels = self.target.findChildren(QtWidgets.QWidget)

        # Ensure each label has a persistent opacity effect (start invisible)
        self.effects = []
        for lab in self.labels:
            eff = lab.graphicsEffect()
            if not isinstance(eff, QGraphicsOpacityEffect):
                eff = QGraphicsOpacityEffect(lab)
                eff.setOpacity(0.0)
                lab.setGraphicsEffect(eff)
            self.effects.append(eff)

        # 4) Build persistent fade groups (no per-hover allocations)
        self.fade_in  = QParallelAnimationGroup(self.target)
        self.fade_out = QParallelAnimationGroup(self.target)
        for eff in self.effects:
            ain = QPropertyAnimation(eff, b"opacity")
            ain.setDuration(180)
            ain.setStartValue(0.0)
            ain.setEndValue(1.0)
            ain.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.fade_in.addAnimation(ain)

            aout = QPropertyAnimation(eff, b"opacity")
            aout.setDuration(120)
            aout.setStartValue(1.0)
            aout.setEndValue(0.0)
            aout.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.fade_out.addAnimation(aout)

        # 5) Sequences: OPEN = width -> pause -> fade-in; CLOSE = fade-out -> width
        self.open_seq  = QSequentialAnimationGroup(self.target)
        self.close_seq = QSequentialAnimationGroup(self.target)
        self.pause = QPauseAnimation(60)
        self.open_seq.addAnimation(self.animate_menu_open)
        self.open_seq.addAnimation(self.pause)
        self.open_seq.addAnimation(self.fade_in)

        self.close_seq.addAnimation(self.fade_out)
        self.close_seq.addAnimation(self.animate_menu_close)

    def _expanded_width(self) -> int:
        fm = self.target.fontMetrics()
        # use the canonical texts instead of empty labels
        text_w = max(fm.horizontalAdvance(t) for t in self.texts) if self.texts else 0
        collapsed = max(self.target.minimumWidth(), 60)
        return max(collapsed + 1, self.icon_area + self.side_pad + text_w)

    def eventFilter(self, obj, event):
        buttons = obj.findChildren(QtWidgets.QPushButton)
        if obj is self.target:
            if event.type() == QEvent.Type.Enter:
                self.close_seq.stop(); self.open_seq.stop()
                self.animate_menu_open.setStartValue(self.target.width())
                self.animate_menu_open.setEndValue(self._expanded_width())
                self.open_seq.start()
                for button, text in zip(buttons, self.texts):
                    QtWidgets.QPushButton.setText(button, text)

            elif event.type() == QEvent.Type.Leave:
                self.open_seq.stop(); self.close_seq.stop()
                self.animate_menu_close.setStartValue(self.target.width())
                self.animate_menu_close.setEndValue(60)
                self.close_seq.start()
                for button, text in zip(buttons, self.texts):
                    QtWidgets.QPushButton.setText(button, "")
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
                    estimate_data = estimates_repository.EstimateRepository.load_estimate() or []
                    customer_data = customer_repository.CustomerRepository.get_all_customer_info() or []
                    vehicle_data = vehicle_repository.VehicleRepository.get_all_vehicle_info() or []
                    # belongs_to_data = customer_repository.CustomerRepository.get_all_customer_names()
                    customer_small_data = customer_repository.CustomerRepository.get_all_customer_names() or []
                    vehicle_small_data = vehicle_repository.VehicleRepository.get_all_vehicles() or []
                    appointment_data = appointment_repository.AppointmentRepository.get_appointment_ids_and_timestamps() or []
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
                    if estimate_data != self.last_estimates_data:
                        self.last_estimates_data = estimate_data
                        self.estimate_updates.emit(estimate_data)

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