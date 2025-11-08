from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QIntValidator
from openauto.ui import mpi
from openauto.subclassed_widgets.event_handlers import WidgetManager
from openauto.repositories.mpi_repository import MPIRepository
import sys

class MpiManager:
    def __init__(self, ui):
        self.ui = ui
        self.widget_manager = WidgetManager()
        self.mpi_repo = MPIRepository()

    def setup_ui(self):
        self.mpi, self.mpi_ui = self.widget_manager.create_or_restore("mpi_page", QtWidgets.QWidget, mpi.Ui_Form)
        self.mpi.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.Dialog
        )
        self.mpi.setFixedHeight(self.ui.hub_stacked_widget.height() - 50)
        self.mpi.setFixedWidth(self.ui.hub_stacked_widget.width() - 50)
        self.mpi.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        self.mpi_ui.scrollArea.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self._wire_signals()
        self.two_digit_inputs()
        self.mpi_ui.mpi_cancel_button.clicked.connect(lambda: self.widget_manager.close_and_delete("mpi_page"))
        self.mpi_ui.mpi_save_button.clicked.connect(self.on_mpi_save_clicked)
        self.load_from_db()
        self.mpi.show()




    def _wire_signals(self):
        current_date = QtCore.QDateTime.currentDateTime().toString("MM/dd/yy hh:mm AP")
        for le in (
            "cust_mpi_line","phone_mpi_line","email_mpi_line","date_mpi_line",
            "ro_mpi_line","vehc_mpi_line","plate_mpi_line","miles_mpi_line"
        ):
            w = getattr(self.mpi_ui, le, None)
            if w: w.setReadOnly(True)

        self.mpi_ui.plate_mpi_label.hide()
        self.mpi_ui.plate_mpi_line.hide()
        self.mpi_ui.vin_mpi_line.hide()
        self.mpi_ui.vin_mpi_label.hide()
        self.mpi_ui.cust_mpi_line.setText(self.ui.name_edit.text())
        self.mpi_ui.phone_mpi_line.setText(self.ui.number_edit.text())
        self.mpi_ui.vehc_mpi_line.setText(self.ui.vehcle_line.text())
        self.mpi_ui.date_mpi_line.setText(current_date)
        self.mpi_ui.ro_mpi_line.setText(self.ui.ro_number_label.text())
        self.mpi_ui.miles_mpi_line.setText(self.ui.miles_in_edit.text())


    #allows only digits to be entered in line items.
    def two_digit_inputs(self):
        two_digit = QIntValidator(0, 99, self.mpi)
        for name in (
            "rf_tire_line","lf_tire_line","lr_tire_line","rr_tire_line",
            "rf_brake_line","lf_brake_line","lr_brake_line","rr_brake_line",
        ):
            w = getattr(self.mpi_ui, name, None)
            if not isinstance(w, QtWidgets.QLineEdit):
                continue
            w.setValidator(two_digit)
            w.setMaxLength(2)
            w.setInputMethodHints(QtCore.Qt.InputMethodHint.ImhDigitsOnly)



    def _clear_form_state(self):
        # uncheck all *_ok/_attention/_fail boxes
        for cb in self.mpi_ui.scrollAreaWidgetContents.findChildren(QtWidgets.QCheckBox):
            cb.setChecked(False)
        # clear the 8 two-digit fields
        for name in (
            "rf_tire_line","lf_tire_line","lr_tire_line","rr_tire_line",
            "rf_brake_line","lf_brake_line","lr_brake_line","rr_brake_line",
        ):
            w = getattr(self.mpi_ui, name, None)
            if isinstance(w, QtWidgets.QLineEdit):
                w.clear()

    # fetch pre done inspection
    def load_from_db(self):
        try:
            self._clear_form_state()

            ro_number = self.mpi_ui.ro_mpi_line.text().strip()
            if not ro_number:
                return

            # use repo to resolve RO and then find the latest inspection for it
            ctx = self.mpi_repo._resolve_ro_context(ro_number)
            if not ctx or not ctx.get("ro_id"):
                return

            iid = self.mpi_repo.find_latest_by_context(
                ro_id=ctx["ro_id"],
                vin=ctx.get("vehicle_vin"),
                include_final=True,
            )
            if not iid:
                return

            head, findings = self.mpi_repo.get_inspection_with_findings(iid)
            if not findings:
                return

            for f in findings:
                state = (f.result_label or "").lower()
                if state in ("ok", "attention", "fail"):
                    prefix = f.item_code
                    cb = getattr(self.mpi_ui, f"{prefix}_{state}", None)
                    if isinstance(cb, QtWidgets.QCheckBox):
                        cb.setChecked(True)

            for f in findings:
                if (f.result_label or "").lower() == "measured":
                    line_name = f"{f.item_code}_line"
                    w = getattr(self.mpi_ui, line_name, None)
                    if isinstance(w, QtWidgets.QLineEdit) and f.measurement_value is not None:
                        try:
                            w.setText(str(int(round(float(f.measurement_value)))))
                        except Exception:
                            w.setText(str(f.measurement_value))
        except Exception as e:
            QtWidgets.QMessageBox.warning(self.mpi, "MPI Load Warning", str(e))

    # ensure exclusivity with checkbox groups
    @staticmethod
    def _tri_state(ok: bool, attn: bool, fail: bool):
        if fail:
            return "fail"
        if attn:
            return "attention"
        if ok:
            return "ok"
        return None


    # gather groups and append to dictionary. ex: rf_tire: "ok"
    def _collect_checkbox_states(self):
        result = {}
        form = self.mpi_ui

        boxes = {}
        for child in form.scrollAreaWidgetContents.findChildren(QtWidgets.QCheckBox):
            name = child.objectName() or ""
            if name.endswith(("_ok", "_attention", "_fail")):
                prefix, suffix = name.rsplit("_", 1)
                boxes.setdefault(prefix, {})[suffix] = child

        for prefix, group in boxes.items():
            ok = bool(group.get("ok") and group["ok"].isChecked())
            att = bool(group.get("attention") and group["attention"].isChecked())
            fail = bool(group.get("fail") and group["fail"].isChecked())
            state = self._tri_state(ok, att, fail)
            if state:
                result[prefix] = state

        return result

    # gather the two digit fields and return them as ints or None if empty.
    def _collect_measurements(self):
        vals = {}
        for name in (
            "rf_tire_line","lf_tire_line","lr_tire_line","rr_tire_line",
            "rf_brake_line","lf_brake_line","lr_brake_line","rr_brake_line",
        ):
            w = getattr(self.mpi_ui, name, None)
            if isinstance(w, QtWidgets.QLineEdit):
                t = (w.text() or "").strip()
                vals[name] = int(t) if t.isdigit() else None
        return vals


    #gather all into a single payload to attach to ro and submit to db. Then close widget.
    def on_mpi_save_clicked(self):
        header = {
            "customer": self.mpi_ui.cust_mpi_line.text().strip(),
            "phone": self.mpi_ui.phone_mpi_line.text().strip(),
            "email": self.mpi_ui.email_mpi_line.text().strip(),
            "date": self.mpi_ui.date_mpi_line.text().strip(),
            "ro_number": self.mpi_ui.ro_mpi_line.text().strip(),
            "vehicle": self.mpi_ui.vehc_mpi_line.text().strip(),
            "vin": self.mpi_ui.vin_mpi_line.text().strip(),
            "plate": self.mpi_ui.plate_mpi_line.text().strip(),
            "mileage": self.mpi_ui.miles_mpi_line.text().strip(),
        }

        checks = self._collect_checkbox_states()
        measures = self._collect_measurements()

        payload = {
            "header": header,
            "checks": checks,
            "measurements": measures,
        }

        repo = self.mpi_repo
        if repo and hasattr(repo, "save_inspection"):
            try:
                repo.save_inspection(ro_number=header["ro_number"], data=payload)
            except Exception as e:
                print("didnt work")
                QtWidgets.QMessageBox.critical(self.mpi, "MPI Save Error", str(e))
                return
        else:
            emitter = getattr(self.ui, "mpiSaved", None)
            if callable(getattr(emitter, "emit", None)):
                emitter.emit(payload)


        self.widget_manager.close_and_delete("mpi_page")





