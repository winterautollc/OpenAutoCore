from pathlib import Path
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from openauto.printing.print_service import PrintService
from openauto.repositories.vehicle_repository import VehicleRepository


_BASE = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = _BASE / "printing" / "templates"
ASSETS_DIR   = _BASE / "printing" / "assets"
assets_url = QtCore.QUrl.fromLocalFile(str(ASSETS_DIR)).toString()



class PrintController(QtCore.QObject):
    def __init__(self, ui):
        super().__init__(ui)
        self.ui = ui
        app = QtWidgets.QApplication.instance()
        self.print_service = PrintService(template_dir=TEMPLATE_DIR, assets_dir=ASSETS_DIR, app=app)


    def print_daily_schedule(self, appointments: list, date: QtCore.QDate):
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        print_dialog = QPrintDialog(printer, self.ui)
        print_dialog.setWindowTitle("Print Daily Schedule")

        if print_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            rows = []
            for appt in appointments or []:
                time_delta = appt.get("appointment_time")
                try:
                    total_minutes = int(time_delta.total_seconds() // 60)
                except Exception:
                    total_minutes = 0
                hour = total_minutes // 60
                minute = total_minutes % 60

                start_time = f"{hour:02d}:{minute:02d}"
                end_total = total_minutes + 30  # assume 30-minute slots
                end_hour = end_total // 60
                end_minute = end_total % 60
                end_time = f"{end_hour:02d}:{end_minute:02d}"

                customer = f"{appt.get('first_name','')} {appt.get('last_name','')}".strip()
                vehicle_str = ""
                vid = appt.get("vehicle_id")
                if vid:
                    vehicle_info = VehicleRepository.get_vehicle_info_for_new_ro(int(vid))
                    if vehicle_info:
                        parts = [
                            vehicle_info.get("year") or "",
                            vehicle_info.get("make") or "",
                            vehicle_info.get("model") or "",
                        ]
                        vehicle_str = " ".join(p for p in parts if p)
                        vin_val = (vehicle_info.get("vin") or "").strip()
                        if vin_val:
                            vehicle_str = f"{vehicle_str} ({vin_val})" if vehicle_str else vin_val
                if not vehicle_str:
                    vehicle_str = (appt.get("vin") or "").strip()
                            
                reason = (appt.get("notes") or "").strip()
                drop = (appt.get("dropoff_type") or "").strip()
                if drop:
                    reason_display = f"{reason} ({drop})" if reason else f"({drop})"
                else:
                    reason_display = reason

                rows.append({
                    "start_time": start_time,
                    "end_time": end_time,
                    "customer": customer or "-",
                    "vehicle": vehicle_str or "-",
                    "reason": reason_display,
                    "tech": "",
                    "phone": "-",
                })

            self.print_service.print_appointments_schedule(printer, rows, date)
