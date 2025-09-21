from PyQt6 import QtCore
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer

from openauto.repositories import (customer_repository, vehicle_repository,
                                   appointment_repository, repair_orders_repository)
import time
from PyQt6.QtCore import QPoint, QRect, QEasingCurve, QPropertyAnimation, QSequentialAnimationGroup, QParallelAnimationGroup, QPauseAnimation, QEvent
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QGraphicsOpacityEffect


### EVENT FILTER TO ANIMATE MENU COLLAPSE WHEN MOUSE ISIN'T HOVERED OVER IT AND EXPAND ON MOUSE HOVER  ###
class CMenuHandler(QObject):
    def __init__(self, target_widget):
        super().__init__()
        self.target = target_widget
        self.texts = ["RO's","Customers","Vehicles","Messages","Schedule","Analytics","Settings","Quit"]

        # overlay state
        self._detached = False
        self._grid_pos = None      # (row, col, rowSpan, colSpan)
        self._placeholder = None
        self._parent_filter_installed = False

        # visuals and animations
        self.icon_area = 40
        self.side_pad  = 24
        self.labels = self.target.findChildren(QtWidgets.QWidget)
        self.effects = []
        for lab in self.labels:
            eff = lab.graphicsEffect()
            if not isinstance(eff, QGraphicsOpacityEffect):
                eff = QGraphicsOpacityEffect(lab); eff.setOpacity(0.0); lab.setGraphicsEffect(eff)
            self.effects.append(eff)

        self.fade_in  = QParallelAnimationGroup(self.target)
        self.fade_out = QParallelAnimationGroup(self.target)
        for eff in self.effects:
            a = QPropertyAnimation(eff, b"opacity"); a.setDuration(180); a.setStartValue(0.0); a.setEndValue(1.0); a.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.fade_in.addAnimation(a)
            b = QPropertyAnimation(eff, b"opacity"); b.setDuration(120); b.setStartValue(1.0); b.setEndValue(0.0); b.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.fade_out.addAnimation(b)

        self.open_seq  = QSequentialAnimationGroup(self.target)
        self.close_seq = QSequentialAnimationGroup(self.target)
        self.pause = QPauseAnimation(60)
        self.open_seq.addAnimation(self.pause)
        self.open_seq.addAnimation(self.fade_in)
        self.close_seq.addAnimation(self.fade_out)

        self._geom_anim = None
        self._squelch_hover = False
        self._in_anim = False

    # helpers to find width of menu bar, detach from mainwindow when expanding and reclaim when contracting.
    def _expanded_width(self) -> int:
        fm = self.target.fontMetrics()
        text_w = max(fm.horizontalAdvance(t) for t in self.texts) if self.texts else 0
        collapsed = max(self.target.minimumWidth(), 60)
        return max(collapsed + 1, self.icon_area + self.side_pad + text_w) + 20


# finds coordinates on gridLayout_2
    def _find_grid_coords(self):
        win = self.target.window()
        grid = getattr(win, "gridLayout_2", None)
        if not grid: return None
        for i in range(grid.count()):
            it = grid.itemAt(i)
            if it and it.widget() is self.target:
                r,c,rs,cs = grid.getItemPosition(i)
                return grid, r, c, rs, cs
        return None

    def _ensure_placeholder(self, grid, r, c, rs, cs):
        if self._placeholder is None:
            ph = QtWidgets.QWidget(grid.parentWidget())
            ph.setFixedWidth(max(60, self.target.minimumWidth()))
            ph.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding)
            self._placeholder = ph
        grid.addWidget(self._placeholder, r, c, rs, cs)

#detaches from main_window while expanding so all widgets don't resize
    def _detach_to_overlay(self):
        if self._detached:
            return
        found = self._find_grid_coords()
        if not found:
            return
        grid, r, c, rs, cs = found
        self._grid_pos = (r, c, rs, cs)
        self._ensure_placeholder(grid, r, c, rs, cs)
        self._placeholder.show()

        # Prevent hover churn while we move the widget
        self._squelch_hover = True
        QTimer.singleShot(140, lambda: setattr(self, "_squelch_hover", False))

        grid.removeWidget(self.target)
        host = grid.parentWidget()

        self.target.setParent(host)
        self.target.show()
        self.target.raise_()

        tl = self._placeholder.mapTo(host, QPoint(0, 0))
        h  = self._placeholder.height()
        w0 = max(60, self.target.width())
        self.target.setGeometry(QRect(tl.x(), tl.y(), w0, h))

        self._detached = True
        host.installEventFilter(self)

#reattach to gridLayout_2 after contracting
    def _reattach_to_grid(self):
        if not self._detached:
            return
        host = self.target.parent()
        host.removeEventFilter(self)

        # Squelch synthetic Enter/Leave on reattach
        self._squelch_hover = True
        QTimer.singleShot(140, lambda: setattr(self, "_squelch_hover", False))

        grid = getattr(self.target.window(), "gridLayout_2", None)
        if grid and self._grid_pos:
            r, c, rs, cs = self._grid_pos
            grid.addWidget(self.target, r, c, rs, cs)
        if self._placeholder:
            self._placeholder.hide()
        self._detached = False

    def _menu_buttons(self):
        win = self.target.window()
        names = [
            "repair_orders_button", "customers_button", "vehicles_button",
            "messaging_button", "scheduling_button", "analytics_button",
            "settings_button", "quit_button"
        ]
        btns = []
        for n in names:
            b = getattr(win, n, None)
            if b is not None:
                btns.append(b)
        return btns

   #main event filter
    def eventFilter(self, obj, event):
        if obj is self.target and self._squelch_hover:
            return True

        if obj is self.target:
            if event.type() == QEvent.Type.Enter:
                self._detach_to_overlay()
                if self._geom_anim:
                    self._geom_anim.stop()
                self.close_seq.stop(); self.open_seq.stop()

                host = self.target.parent()
                tl = self._placeholder.mapTo(host, QPoint(0, 0))
                h = self._placeholder.height()
                start = QRect(tl.x(), tl.y(), max(60, self.target.width()), h)
                end = QRect(tl.x(), tl.y(), self._expanded_width(), h)

                self._geom_anim = QPropertyAnimation(self.target, b"geometry")
                self._geom_anim.setDuration(250)
                self._geom_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                self._geom_anim.setStartValue(start)
                self._geom_anim.setEndValue(end)

                for btn, text in zip(self._menu_buttons(), self.texts):
                    btn.setText(text)

                self._in_anim = True
                self._geom_anim.finished.connect(lambda: setattr(self, "_in_anim", False))
                self.fade_in.start()
                self._geom_anim.start()

            elif event.type() == QEvent.Type.Leave:
                if not self._detached:
                    return super().eventFilter(obj, event)
                if self._in_anim:
                    # Defer collapse until the open animation ends
                    self._geom_anim.finished.connect(lambda: self.eventFilter(obj, event))
                    return True

                if self._geom_anim:
                    self._geom_anim.stop()
                self.fade_out.stop()

                host = self.target.parent()
                tl = self._placeholder.mapTo(host, QPoint(0, 0))
                h = self._placeholder.height()
                start = self.target.geometry()
                end = QRect(tl.x(), tl.y(), 60, h)

                self._geom_anim = QPropertyAnimation(self.target, b"geometry")
                self._geom_anim.setDuration(200)
                self._geom_anim.setEasingCurve(QEasingCurve.Type.InCubic)
                self._geom_anim.setStartValue(start)
                self._geom_anim.setEndValue(end)

                def _after():
                    for btn in self._menu_buttons():
                        btn.setText("")
                    self._reattach_to_grid()

                self._geom_anim.finished.connect(_after)
                self.fade_out.start()
                self._geom_anim.start()

        if self._detached and event.type() == QEvent.Type.Resize and obj is self.target.parent():
            tl = self._placeholder.mapTo(obj, QPoint(0, 0))
            g = self.target.geometry()
            self.target.setGeometry(g.x(), tl.y(), g.width(), self._placeholder.height())

        return super().eventFilter(obj, event)


    
### QTHREAD TO MONITOR CHANGES IN DATABASE. USING ONE QTHREAD FOR ALL TABLES AS IT SHOULD BE MORE EFFICIENT###
### MAY CHANGE TO QEVENT LATER ###
class SQLMonitor(QThread):
    customer_updates = pyqtSignal(list)
    ro_updates = pyqtSignal(list)
    estimate_item_updates = pyqtSignal(list)
    vehicle_update = pyqtSignal(list)
    belongs_to_update = pyqtSignal(list)
    small_customers_update = pyqtSignal(list)
    small_vehicles_update = pyqtSignal(list)
    appointment_data = pyqtSignal(list)
    hourly_schedule_update = pyqtSignal()


    def __init__(self):
        super().__init__()
        self.last_customer_data = None
        self.last_ro_data = None
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
                    ro_data = repair_orders_repository.RepairOrdersRepository.load_repair_orders() or []
                    customer_data = customer_repository.CustomerRepository.get_all_customer_info() or []
                    vehicle_data = vehicle_repository.VehicleRepository.get_all_vehicle_info() or []
                    # belongs_to_data = customer_repository.CustomerRepository.get_all_customer_names()
                    customer_small_data = customer_repository.CustomerRepository.get_all_customer_names() or []
                    vehicle_small_data = vehicle_repository.VehicleRepository.get_all_vehicles() or []
                    appointment_data = appointment_repository.AppointmentRepository.get_appointment_ids_and_timestamps() or []

                    if ro_data != self.last_ro_data:
                        self.last_ro_data = ro_data
                        self.ro_updates.emit(ro_data)

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