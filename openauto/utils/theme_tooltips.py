import re
from PyQt6 import QtWidgets

_QTOOLTIP_BLOCK_RE = re.compile(r"QToolTip\s*\{[^}]*\}", re.IGNORECASE | re.DOTALL | re.MULTILINE)

def extract_qtooltip_block(qss: str) -> str | None:
    m = _QTOOLTIP_BLOCK_RE.search(qss or "")
    return m.group(0) if m else None


def upsert_qtooltip_block(app: QtWidgets.QApplication, qtooltip_block: str) -> None:
    current = app.styleSheet() or ""
    if _QTOOLTIP_BLOCK_RE.search(current):
        new = _QTOOLTIP_BLOCK_RE.sub(qtooltip_block, current, count=1)
    else:
        sep = "\n\n" if current and not current.endswith("\n") else "\n"
        new = f"{current}{sep}{qtooltip_block}\n"
    app.setStyleSheet(new)

def elevate_stylesheet_to_app(app: QtWidgets.QApplication, window: QtWidgets.QWidget) -> None:
    win_qss = window.styleSheet() or ""
    app_qss = app.styleSheet() or ""
    if win_qss and win_qss != app_qss:
        app.setStyleSheet(win_qss)

def apply_tooltip_for_theme(app: QtWidgets.QApplication, theme_name: str, light_tt: str, dark_tt: str) -> None:
    tt = light_tt if str(theme_name).lower().startswith("light") else dark_tt
    upsert_qtooltip_block(app, tt)

def sync_tooltips_with_theme(app: QtWidgets.QApplication, theme_qss: str, fallback_css: str = ""):
    block = extract_qtooltip_block(theme_qss)
    if block:
        upsert_qtooltip_block(app, block)
    elif fallback_css.strip():
        upsert_qtooltip_block(app, fallback_css.strip())