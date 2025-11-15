from pathlib import Path
from PyQt6 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets, QtWebEngineCore
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from jinja2 import Environment, FileSystemLoader, select_autoescape
import base64

class PrintService(QtCore.QObject):
    def __init__(self, app, template_dir: Path, assets_dir: Path):
        super().__init__()
        self.app = app  # QApplication
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True, lstrip_blocks=True,
        )
        self.assets_dir = assets_dir

    def _embed_logo_b64(self, filename="logo.png"):
        p = self.assets_dir / filename
        if not p.exists():
            return ""
        b = p.read_bytes()
        return f"data:image/png;base64,{base64.b64encode(b).decode()}"

    def render(self, template_name: str, ctx: dict) -> str:
        tpl = self.env.get_template(template_name)
        full_ctx = dict(**ctx)
        shop = full_ctx.setdefault("shop", {})
        logo = shop.get("logo")
        try:
            if isinstance(logo, QtGui.QPixmap) and not logo.isNull():
                ba = QtCore.QByteArray()
                buf = QtCore.QBuffer(ba)
                buf.open(QtCore.QIODevice.OpenModeFlag.WriteOnly)
                logo.save(buf, "PNG")
                shop["logo_b64"] = f"data:image/png;base64,{bytes(ba.toBase64()).decode()}"
            else:
                shop["logo_b64"] = self._embed_logo_b64()
        except Exception:
            shop["logo_b64"] = self._embed_logo_b64()

        return tpl.render(**full_ctx)

    def html_to_pdf(self, html: str, out_path: Path) -> Path:
        page = QtWebEngineCore.QWebEnginePage()
        loop = QtCore.QEventLoop()

        def on_load_finished(_ok: bool):
            page.printToPdf(str(out_path), pageLayout=QtGui.QPageLayout(
                QtGui.QPageSize(QtGui.QPageSize.PageSizeId.A4),
                QtGui.QPageLayout.Orientation.Portrait,
                QtCore.QMarginsF(0,0,0,0)
            ))
        def on_pdf_ready(_path: str):
            loop.quit()

        page.pdfPrintingFinished.connect(on_pdf_ready)
        page.loadFinished.connect(on_load_finished)

        base_url = QtCore.QUrl.fromLocalFile(str(self.assets_dir))
        page.setHtml(html, base_url)
        loop.exec()  # block until PDF is written
        return out_path

    def print_native(self, html: str):
        # Optional: print directly to a selected printer via QTextDocument
        doc = QtGui.QTextDocument()
        doc.setHtml(html)
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dlg = QPrintDialog(printer)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            doc.print(printer)

    # Convenience entry points
    def print_invoice_pdf(self, ctx: dict, out_path: Path) -> Path:
        html = self.render("invoice.html", ctx)
        return self.html_to_pdf(html, out_path)

    def print_ro_pdf(self, ctx: dict, out_path: Path) -> Path:
        html = self.render("repair_order.html", ctx)
        return self.html_to_pdf(html, out_path)

    def print_schedule_pdf(self, ctx: dict, out_path: Path) -> Path:
        html = self.render("schedule_day.html", ctx)
        return self.html_to_pdf(html, out_path)

    def print_mpi_pdf(self, ctx: dict, out_path: Path) -> Path:
        html = self.render("mpi.html", ctx)
        return self.html_to_pdf(html, out_path)

    def print_job_ticket_pdf(self, ctx: dict, out_path: Path) -> Path:
        html = self.render("job_ticket.html", ctx)
        return self.html_to_pdf(html, out_path)
        
        

