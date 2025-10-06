import logging
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6 import QtCore, QtGui
import os, platform
from openauto.utils.theme_tooltips import upsert_qtooltip_block, apply_tooltip_for_theme, elevate_stylesheet_to_app

from openauto.utils.error_reporter import (
    init_error_reporter, ErrorReporterConfig, install_global_excepthook
)

LIGHT_TT = """
QToolTip { color:#333; background-color:#F9F9F9; border:1px solid #AAA; border-radius:6px; padding:2px 4px; font-size:16px; }
""".strip()

DARK_TT = """
QToolTip { color:#ECECEC; background-color:#2A2A2A; border:1px solid #505050; border-radius:6px; padding:2px 4px; font-size:16px; }
""".strip()

init_error_reporter(ErrorReporterConfig(
    app_name="OpenAuto",
    app_version="dev",
    github_issues_url="https://github.com/winterautollc/OpenAutoCore/issues/new",
    log_level=logging.INFO,
))
from openauto.ui.home import MainWindow
from openauto.managers.login_manager import LoginCreate

# FORCE XWAYLAND / X11 FOR LINUX #
if platform.system() == "Linux" and os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland":
    os.environ["QT_QPA_PLATFORM"] = "xcb"

try:
    QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_UseDesktopOpenGL, True)
    fmt = QtGui.QSurfaceFormat()
    fmt.setSwapBehavior(QtGui.QSurfaceFormat.SwapBehavior.DoubleBuffer)
    fmt.setSwapInterval(1)
    QtGui.QSurfaceFormat.setDefaultFormat(fmt)
except Exception as e:
    import traceback
    traceback.print_exc()

### LOAD USERS THEME ###
def _load_user_theme(user_id: int):
    import mysql.connector
    from openauto.repositories.db_handlers import connect_db
    conn = connect_db()

    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("SELECT theme FROM user_settings WHERE user_id=%s LIMIT 1", (user_id,))
            row = cur.fetchone()
            return (row or {}).get("theme", "dark")
    except mysql.connector.Error:
        return "light"
    finally:
        try:
            conn.close()
        except Exception:
            pass

if __name__ == "__main__":
    app = QApplication([])
    install_global_excepthook(parent_getter=lambda: QApplication.activeWindow())
    login = LoginCreate()
    _user_ctx = {}

    if hasattr(login, "loginSucceeded"):
        login.loginSucceeded.connect(lambda user_id, user: _user_ctx.update({"id": user_id, "user": user}))

    # Block until user logs in or cancels
    result = login.exec()
    if result != QDialog.DialogCode.Accepted or not _user_ctx:
        raise SystemExit(0)

    ### CREATE MAINWINDOW WITH LOGGED IN USER ###
    window = MainWindow(current_user=_user_ctx["user"])  # pass user to your app

    theme_name = _load_user_theme(_user_ctx["id"])
    if hasattr(window, "switch_theme"):
        window.switch_theme(theme_name, persist=False)

    ### APPLY USERS THEME ###
    try:
        theme_name = _load_user_theme(_user_ctx["id"])
        if hasattr(window, "switch_theme"):
            window.switch_theme(theme_name)
    except Exception as e:
        print("Theme load/apply failed:", e)

    elevate_stylesheet_to_app(app, window)

    apply_tooltip_for_theme(app, theme_name, LIGHT_TT, DARK_TT)

    if hasattr(window, "switch_theme"):
        _orig_switch = window.switch_theme


        def _switch_theme_and_sync(name, persist=True, *args, **kwargs):
            rv = _orig_switch(name, persist=persist)
            # In case switch_theme applied QSS on the window, lift it to the app
            elevate_stylesheet_to_app(app, window)
            # Now update QToolTip styling for this theme
            apply_tooltip_for_theme(app, name, LIGHT_TT, DARK_TT)
            return rv


        window.switch_theme = _switch_theme_and_sync

    # Show and maximize (preserving your timing)
    window.show()
    QtCore.QTimer.singleShot(5, window.showMaximized)

    app.exec()
