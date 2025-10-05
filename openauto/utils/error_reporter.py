# openauto/utils/error_reporter.py
from __future__ import annotations

import logging
import os
import platform
import sys
import textwrap
import traceback
from dataclasses import dataclass
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Any, Callable, Dict, Optional

# PyQt6 imports are lazy-imported inside functions to avoid import cost in non-UI contexts.


# ---------------------------
# Configuration & initialization
# ---------------------------

@dataclass
class ErrorReporterConfig:
    app_name: str = "OpenAuto"
    app_version: Optional[str] = None
    github_issues_url: Optional[str] = None  # e.g., "https://github.com/YourOrg/OpenAuto/issues/new"
    log_dir: Optional[str] = None            # default: ~/.local/share/OpenAuto/logs on Linux, similar elsewhere
    log_file: str = "openauto.log"
    log_level: int = logging.INFO
    max_bytes: int = 2_000_000               # ~2MB
    backup_count: int = 5

_logger: Optional[logging.Logger] = None
_config: ErrorReporterConfig = ErrorReporterConfig()
_parent_getter: Optional[Callable[[], Any]] = None  # returns a QWidget for message boxes (or None)


def init_error_reporter(
    config: Optional[ErrorReporterConfig] = None,
    parent_getter: Optional[Callable[[], Any]] = None,
) -> logging.Logger:
    """
    Call once at app startup.
    parent_getter: function returning a QWidget (or None) used as parent for message boxes.
    """
    global _logger, _config, _parent_getter

    _config = config or ErrorReporterConfig()

    # Determine log directory
    if not _config.log_dir:
        _config.log_dir = _default_log_dir(_config.app_name)
    os.makedirs(_config.log_dir, exist_ok=True)
    log_path = os.path.join(_config.log_dir, _config.log_file)

    # Configure logger
    logger = logging.getLogger(_config.app_name)
    logger.setLevel(_config.log_level)
    logger.propagate = False  # don’t double-log to root

    # Clear existing handlers if re-init
    logger.handlers.clear()

    # File (rotating)
    file_handler = RotatingFileHandler(
        log_path, maxBytes=_config.max_bytes, backupCount=_config.backup_count, encoding="utf-8"
    )
    file_handler.setLevel(_config.log_level)
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(file_handler)

    # Console (dev)
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(_config.log_level)
    console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(console)

    _logger = logger
    _parent_getter = parent_getter
    return logger


def _default_log_dir(app_name: str) -> str:
    home = os.path.expanduser("~")
    if sys.platform.startswith("win"):
        base = os.getenv("LOCALAPPDATA", home)
        return os.path.join(base, app_name, "logs")
    elif sys.platform == "darwin":
        return os.path.join(home, "Library", "Logs", app_name)
    else:
        # Linux & everything else
        return os.path.join(home, ".local", "share", app_name, "logs")


# ---------------------------
# Core reporting APIs
# ---------------------------

def report_exception(
    exc: BaseException,
    *,
    context: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
    show_messagebox: bool = True,
    copy_to_clipboard: bool = True,
) -> None:
    """
    Call this inside an except-block:
        except Exception as e:
            report_exception(e, context="Saving appointment")
    """
    logger = _logger or init_error_reporter()

    # Gather traceback
    tb_str = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

    # Compose a compact log line and a detailed issue body
    summary = f"{type(exc).__name__}: {exc}"
    issue_md = _build_issue_markdown(summary, tb_str, context=context, extra=extra)

    # Log
    logger.error("%s\n%s", summary, tb_str)

    # Also print for dev runs
    print(summary, file=sys.stderr)
    print(tb_str, file=sys.stderr)

    # UI feedback (Qt)
    if show_messagebox:
        _show_qt_messagebox(summary, issue_md)

    # Copy for user to paste into GitHub issue
    if copy_to_clipboard:
        _copy_to_clipboard(issue_md)


def report_current_exception(
    *,
    context: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
    show_messagebox: bool = True,
    copy_to_clipboard: bool = True,
) -> None:
    """
    Like report_exception but uses sys.exc_info() for convenience.
    """
    ex_type, ex, tb = sys.exc_info()
    if ex is None:
        return
    tb_str = "".join(traceback.format_exception(ex_type, ex, tb))
    summary = f"{ex_type.__name__}: {ex}"
    issue_md = _build_issue_markdown(summary, tb_str, context=context, extra=extra)

    logger = _logger or init_error_reporter()
    logger.error("%s\n%s", summary, tb_str)

    print(summary, file=sys.stderr)
    print(tb_str, file=sys.stderr)

    if show_messagebox:
        _show_qt_messagebox(summary, issue_md)
    if copy_to_clipboard:
        _copy_to_clipboard(issue_md)


# ---------------------------
# Decorator & context manager
# ---------------------------

def catch_and_report(
    *,
    context: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
    re_raise: bool = False,
    show_messagebox: bool = True,
):
    """
    Decorator to wrap slot/callbacks:
        @catch_and_report(context="New RO Save")
        def _save_ro(self): ...
    """
    def _decorator(func):
        def _wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:  # noqa: BLE001 (intentional)
                report_exception(
                    e, context=context or func.__name__, extra=extra,
                    show_messagebox=show_messagebox
                )
                if re_raise:
                    raise
                return None
        return _wrapped
    return _decorator


class error_guard:
    """
    Context manager for quick try/except blocks:

        with error_guard(context="Appointments: Save"):
            # ... risky code ...
    """
    def __init__(self, *, context: Optional[str] = None, show_messagebox: bool = True, re_raise: bool = False):
        self.context = context
        self.show = show_messagebox
        self.re_raise = re_raise

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex, tb):
        if ex is None:
            return False
        tb_str = "".join(traceback.format_exception(ex_type, ex, tb))
        summary = f"{ex_type.__name__}: {ex}"
        issue_md = _build_issue_markdown(summary, tb_str, context=self.context)

        logger = _logger or init_error_reporter()
        logger.error("%s\n%s", summary, tb_str)
        print(summary, file=sys.stderr)
        print(tb_str, file=sys.stderr)
        if self.show:
            _show_qt_messagebox(summary, issue_md)
        _copy_to_clipboard(issue_md)
        return not self.re_raise  # swallow unless re_raise=True


# ---------------------------
# Global excepthook (optional)
# ---------------------------

def install_global_excepthook(parent_getter: Optional[Callable[[], Any]] = None) -> None:
    """
    Route uncaught exceptions through our reporter.
    """
    global _parent_getter
    if parent_getter is not None:
        _parent_getter = parent_getter

    def _hook(ex_type, ex, tb):
        tb_str = "".join(traceback.format_exception(ex_type, ex, tb))
        summary = f"{ex_type.__name__}: {ex}"
        issue_md = _build_issue_markdown(summary, tb_str, context="Uncaught exception")
        logger = _logger or init_error_reporter()
        logger.critical("%s\n%s", summary, tb_str)
        print(summary, file=sys.stderr)
        print(tb_str, file=sys.stderr)
        _show_qt_messagebox(summary, issue_md)
        _copy_to_clipboard(issue_md)

    sys.excepthook = _hook


# ---------------------------
# Helpers (Qt UI, clipboard, markdown)
# ---------------------------

def _show_qt_messagebox(summary: str, details: str) -> None:
    """
    Show a user-friendly error dialog from the GUI thread.
    Uses a single-shot to hop to the main loop if needed.
    """
    try:
        # Lazy import
        from PyQt6 import QtWidgets, QtCore

        def _run():
            parent = _parent_getter() if callable(_parent_getter) else None
            mbox = QtWidgets.QMessageBox(parent)
            mbox.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            title = _config.app_name or "Application"
            mbox.setWindowTitle(f"{title} Error")
            mbox.setText(f"{summary}\n\nA detailed error report was copied to your clipboard.\n"
                         f"Please paste it into a GitHub issue.")
            if _config.github_issues_url:
                mbox.setInformativeText(_config.github_issues_url)
            # Expandable "Show Details"
            mbox.setDetailedText(details)
            mbox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
            mbox.exec()

        # Ensure this runs on the GUI thread
        try:
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            if app is None:
                # headless or not yet created; skip dialog
                return
        except Exception:
            return

        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, _run)

    except Exception:
        # If Qt is unavailable or we fail to show, we silently ignore UI feedback
        pass


def _copy_to_clipboard(text: str) -> None:
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            app.clipboard().setText(text)
    except Exception:
        pass


def _build_issue_markdown(summary: str, tb_str: str, *, context: Optional[str], extra: Optional[Dict[str, Any]] = None) -> str:
    now = datetime.now().isoformat(timespec="seconds")
    sysinfo = {
        "OS": f"{platform.system()} {platform.release()} ({platform.version()})",
        "Python": platform.python_version(),
        "App": f"{_config.app_name} {(_config.app_version or '')}".strip(),
    }
    lines = [
        f"# {_config.app_name} Error Report",
        "",
        f"**Summary:** {summary}",
        f"**When:** {now}",
        f"**Context:** {context or '(none)'}",
        "",
        "## System",
        *[f"- {k}: {v}" for k, v in sysinfo.items()],
    ]
    if extra:
        lines += ["", "## Extra", *[f"- {k}: {v}" for k, v in extra.items()]]

    lines += [
        "",
        "## Traceback",
        "```text",
        tb_str.rstrip(),
        "```",
        "",
        "## Steps to Reproduce",
        "1. _Write steps here_",
        "",
        "## Expected Behavior",
        "_What you expected to happen_",
        "",
        "## Actual Behavior",
        "_What actually happened_",
    ]
    return "\n".join(lines)
