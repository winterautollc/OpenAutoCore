import sys
from pathlib import Path
from PyQt6.QtCore import QObject, QProcess, pyqtSignal, QTimer, QProcessEnvironment
import json
from openauto.managers.parts_tree.parts_tree_loader import PartsTreeLoader
import re, subprocess
from openauto.repositories.parts_tree_repository import PartsTreeRepository
from openauto.managers.parts_tree.sessions_cache import SessionsCache
from openauto.utils.log_sanitizer import scrub


repo = PartsTreeRepository()
sessions = SessionsCache()

BASE_DIR = Path(__file__).resolve().parent
QUOTES_DIR  = BASE_DIR / "data" / "quotes"
DEFAULT_PTCLI_TIMEOUT = 2
DEFAULT_EST_ID = None

_SENSITIVE_PATTERNS = (
    r"-token\s+\S+",
    r"authorization[:=]\s*\S+",
    r"\beyJ[a-zA-Z0-9_\-]{10,}\.[a-zA-Z0-9_\-]{10,}\.[a-zA-Z0-9_\-]{10,}\b",
)


def _save_cart_snapshot(payload: dict):
    raw = payload.get("Raw") or payload.get("Data") or payload
    sid = (raw.get("sessionId") or payload.get("sessionId") or payload.get("Data", {}).get("sessionId"))
    if not sid:
        return
    QUOTES_DIR.mkdir(parents=True, exist_ok=True)
    (QUOTES_DIR / f"{sid}.json").write_text(json.dumps(raw, indent=2))

class GoSidecarManager(QObject):
    quoteReady = pyqtSignal(dict)
    errorText = pyqtSignal(str)
    debugText = pyqtSignal(str)
    partRemoved = pyqtSignal(dict)
    cartUpdated = pyqtSignal(dict)
    cartSubmitted = pyqtSignal(dict)
    plateDecoded = pyqtSignal(dict)

    def __init__(self, ptcli_path: str, parent=None, timeout_ms: int = 60, public_base: str | None = None,
                 local_return_base: str | None = None):
        super().__init__(parent)
        self._delete_queue: list[str] = []
        self._delete_ctx: dict | None = None
        self.ptcli_path = ptcli_path
        self.supported_ops = set()
        self.supported_ops = {"auth", "plate2vin", "create-cart",
                              "submit-cart", "remove-part", "update-cart", "available"}
        try:
            out = subprocess.run([self.ptcli_path, "-h"], capture_output=True, text=True, timeout=2).stdout
            m = re.search(r"-op string\s+Operation:\s*(.+)", out, re.S)
            if m:
                self.supported_ops |= {s.strip() for s in m.group(1).split("|")}
            self.uses_session_id = "-session_id string" in out
        except Exception:
            self.uses_session_id = True
            self.uses_session_id = True
        self._proc = None
        self._buffer = b""
        self.parts_tree_loader = PartsTreeLoader
        self._timeout = timeout_ms
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._on_timeout)
        self._current_op: str | None = None
        self._default_estimate_id: int | None = None
        self.public_base = (public_base or "").rstrip("/")
        self.local_return_base = (local_return_base or "").rstrip("/")
        self._pending_fetch = None

    def _run(self, args: list[str]):
        if self._proc:
            try:
                self._proc.setProperty("killedByManager", True)
            except Exception:
                pass
            self._proc.kill()
            self._proc = None

        try:
            self._current_op = args[args.index("-op") + 1]
        except Exception:
            self._current_op = None

        self._buffer = b""
        self._proc = QProcess(self)


        env = QProcessEnvironment.systemEnvironment()
        if self.public_base:
            env.insert("PUBLIC_CALLBACK_BASE", self.public_base)
        if self.local_return_base:
            env.insert("LOCAL_RETURN_BASE", self.local_return_base)
        self._proc.setProcessEnvironment(env)


        self._proc.setProgram(self.ptcli_path)
        self._proc.setArguments(args)

        self._proc.readyReadStandardOutput.connect(self._on_stdout)
        self._proc.readyReadStandardError.connect(self._on_stderr)
        self._proc.finished.connect(self._on_finished)
        self._proc.start()


    def _on_timeout(self):
        if self._proc:
            self._proc.kill()
        self.errorText.emit("ptcli timed out")

    def _on_stdout(self):
        self._buffer += bytes(self._proc.readAllStandardOutput())

    def _has_secret(self, text: str) -> bool:
        import re
        t = text or ""
        return any(re.search(pat, t, flags=re.I) for pat in _SENSITIVE_PATTERNS) or ("ARGS:" in t)

    def _scrub(self, text: str) -> str:
        import re
        t = text or ""
        t = re.sub(r"(-token)\s+\S+", r"\1 [REDACTED]", t, flags=re.I)
        t = re.sub(r"(authorization[:=]\s*)\S+", r"\1[REDACTED]", t, flags=re.I)
        t = re.sub(r"\beyJ[a-zA-Z0-9_\-]{10,}\.[a-zA-Z0-9_\-]{10,}\.[a-zA-Z0-9_\-]{10,}\b",
                   "[JWT-REDACTED]", t)
        return t

    def _on_stderr(self):
        msg = bytes(self._proc.readAllStandardError()).decode(errors="replace")
        if not msg.strip():
            return
        cleaned = self._scrub(msg)
        self.debugText.emit(scrub(cleaned))

    def _on_proc_error(self, err):
        self.errorText.emit(f"ptcli launch error: {err}")

    def _emit_for_op(self, op: str, payload: dict):
        # Normalize op and emit existing UI signals
        op = (op or "").lower()
        
        if op == "plate2vin":
            self.debugText.emit(scrub("[ptcli] emitting plateDecoded"))
            self.plateDecoded.emit(payload)
            return
        
        if op == "submit-cart":
            self.debugText.emit(scrub("[ptcli] emitting cartSubmitted"))
            self.cartSubmitted.emit(payload)


        elif op in ("available", "update-cart", "create-cart"):
            self.cartUpdated.emit(payload)
            self.debugText.emit(scrub(f"cart - {op}, with {payload}"))

        elif op == "remove-part":
            if "sessionId" not in payload and self._delete_ctx:
                try:
                    payload["sessionId"] = self._delete_ctx.get("session_id") or payload.get("sessionID")
                except Exception:
                    pass
            if self._delete_ctx and not any(k in payload for k in
                                            ("removals", "removed", "removes", "orderItemIds", "orderItems",
                                             "orderItemId", "id", "order_item")):
                hint = str(self._delete_ctx.get("current_removed") or "")
                if hint:
                    payload["_currentRemoved"] = hint
                    payload["orderItemId"] = hint
            try:
                self.debugText.emit(scrub(f"removing {payload.get('orderItemId')}"))
            except Exception:
                pass
            self.partRemoved.emit(payload)
        else:
            self.cartUpdated.emit(payload)


    def _on_finished(self, code, status):
        sender = self.sender()
        if hasattr(sender, "property") and sender.property("killedByManager"):
            return

        raw = self._buffer.decode(errors="replace").strip()

        payload = {}
        try:
            payload = json.loads(raw) if raw else {}
        except Exception as e:
            try:
                matches = list(re.finditer(r"\{.*\}", raw, re.S))
                if matches:
                    last = matches[-1].group(0)
                    payload = json.loads(last)
                    self.debugText.emit("[ptcli] recovered JSON from trailing block")
                else:
                    self.debugText.emit(scrub(f"ptcli parse failed {e}"))
            except Exception as e2:
                self.debugText.emit(scrub(f"ptcli parse failed {e}; recover failed {e2}"))
                payload = {}

        if code != 0 and not raw:
            st = "CrashExit" if status == QProcess.ExitStatus.CrashExit else "NormalExit"
            op = (self._current_op or "").lower()

            if st == "NormalExit" and op == "submit-cart":
                payload = {"op": "submit-cart", "ok": True, "_note": "empty-stdout-treated-as-success",
                           "_exit_code": code}
                self._emit_for_op("submit-cart", payload)
                return

            self.errorText.emit(scrub(f"ptcli exited {code} ({st}) with no output [op={self._current_op or '?'}]"))
            return

        op_run = (self._current_op or "").lower()
        op_payload = (payload.get("op") or payload.get("_op_hint") or "").lower()
        op = op_run or op_payload
        if op_payload and op_run and op_payload != op_run:
            self.debugText.emit(scrub(f"[ptcli] op mismatch: payload='{op_payload}' vs run='{op_run}' — using run op"))

        if isinstance(payload, dict):
            self._emit_for_op(op, payload)
        if (op or "").lower() == "update-cart" and self._pending_fetch:
            try:
                ctx = self._pending_fetch
                self._pending_fetch = None
                self.fetch_cart(token=ctx["token"], session_id=ctx["session_id"], timeout_s=ctx["timeout_s"])

            except Exception:
                self._pending_fetch = None

        if (op or "").lower() == "remove-part":
            try:
                self._kickoff_next_delete()
            except Exception:
                pass


    def create_cart(self, token: str, vin: str | None = None,
                    part_type_ids: list[int] | None = None,
                    keyword: str | None = None,
                    po_number: str | None = None,
                    api_base: str = "https://api.partstech.com",
                    timeout_s: int = 25):

        args = ["-op", "create-cart", "-base", api_base, "-token", token]
        if vin: args += ["-vin", vin]
        if keyword: args += ["-keyword", keyword]
        if po_number: args += ["-po", po_number]
        for pid in (part_type_ids or []): args += ["-part", str(pid)]
        args += ["-timeout", f"{timeout_s}s", "-dump"]
        self._run(args)



    def remove_part(self, token, session_id, part_id, timeout_s: int = DEFAULT_PTCLI_TIMEOUT):
        args = ["-op", "remove-part", "-token", token,
                "-session_id", session_id,
                "-order_item", str(part_id),
                "-timeout", f"{max(timeout_s, 15)}s", "-dump"]
        self._run(args)


    def update_cart(self, token: str, session_id: str, adds=None, removes=None, qty: int = 1, timeout_s: int = DEFAULT_PTCLI_TIMEOUT):
        self.debugText.emit(scrub(f"[ptcli] update_cart removes={removes} adds={bool(adds)}"))
        if removes:
            self._delete_queue = [str(r) for r in removes if r]
            self._delete_ctx = {"token": token, "session_id": session_id, "timeout_s": max(timeout_s, 15)}
            self._kickoff_next_delete()
            return
        if not adds:
            self.errorText.emit("update-cart requires either an add/update target or 'removes'.")
            return

        item = adds[0]
        order_item = str(item.get("orderItemId") or item.get("id"))
        qty_val = int(item.get("quantity") or qty or 1)

        args = ["-op", "update-cart", "-token", token,
                "-session_id", session_id,
                "-order_item", order_item,
                "-item_qty", str(qty_val),
                "-timeout", f"{timeout_s}s",
                "-dump"
                ]
        self._run(args)

    def _kickoff_next_delete(self):
        if not self._delete_queue or not self._delete_ctx:
            if self._delete_ctx:
                self.fetch_cart(
                    token=self._delete_ctx["token"],
                    session_id=self._delete_ctx["session_id"],
                    timeout_s=15
                )
            self._delete_ctx = None
            return

        part_id = self._delete_queue.pop(0)
        ctx = self._delete_ctx
        self.debugText.emit(scrub(f"[ptcli] remove-part orderItemId={part_id}"))
        args = [
            "-op", "remove-part", "-token", ctx["token"],
            "-session_id", ctx["session_id"],
            "-order_item", str(part_id),
            "-timeout", f'{ctx["timeout_s"]}s',
            "-dump",
        ]

        ctx["current_removed"] = str(part_id)
        self._run(args)

    def submit_cart(self, token: str, session_id: str, po: str | None = None, timeout_s: int = DEFAULT_PTCLI_TIMEOUT):
        if "submit-cart" not in self.supported_ops:
            self.errorText.emit("Your ptcli does not support -op submit-cart. Rebuild/upgrade the binary.")
            return
        args = ["-op", "submit-cart", "-token", token,
                "-session_id", session_id, "-timeout", f"{timeout_s}s", "-dump"]
        if po: args += ["-po", po]
        self._run(args)

    def fetch_cart(self, token: str, session_id: str, timeout_s: int = 20):
        args = ["-op", "available", "-token", token, "-session_id", session_id,
                "-timeout", f"{max(timeout_s, 20)}s", "-dump"]
        self.debugText.emit("If this fails you will see an immediate segfault to go with this")
        self._run(args)

    def _refresh_parts_tree_from_payload(self, payload: dict):
        try:
            session_id = payload.get("sessionId") or payload.get("sessionID")
            if session_id:
                out = Path(QUOTES_DIR) / f"{session_id}.json"
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(json.dumps(payload, indent=2))

        except Exception as e:
            print("save payload failed", e)

        try:
            self.parts_tree_loader.load()
        except Exception as e:
            print("reload failed", e)


    def set_default_estimate_id(self, estimate_id: int | None):
        try:
            est = int(estimate_id) if estimate_id is not None else None
        except Exception:
            est = None
        self._default_estimate_id = est if est and est > 0 else None
        
        
    def plate_to_vin(self, token: str, plate: str, state: str | None = None,
                     timeout_s: int = DEFAULT_PTCLI_TIMEOUT):
        if "plate2vin" not in self.supported_ops:
            self.errorText.emit("Your ptcli does not support -op plate2vin. Rebuild/upgrade the binary.")
            return
        args = ["-op", "plate2vin", "-token", token,
                "-plate", plate,
                "-timeout", f"{timeout_s}s", "-dump"]
        if state:
            args += ["-state", state]
        self._run(args)

class UvicornManager(QObject):
    debugText = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self._proc = None

        def ensure_data_folders():
            for sub in ("data/quotes", "data/orders", "data/returns"):
                Path(sub).mkdir(parents=True, exist_ok=True)

    def start(self, host="127.0.0.1", port=8000, module="openauto.managers.parts_tree.api_pt_callbacks:app", python=None):
        if self._proc:
            return
        self._proc = QProcess(self)
        self._proc.setProgram(python or sys.executable)
        self._proc.setArguments(["-m", "uvicorn", module, "--host", host, "--port", str(port)])
        self._proc.readyReadStandardError.connect(lambda: self.debugText.emit(bytes(self._proc.readAllStandardError()).decode()))
        self._proc.readyReadStandardOutput.connect(lambda: self.debugText.emit(bytes(self._proc.readAllStandardOutput()).decode()))
        self._proc.start()

    def stop(self):
        if self._proc:
            self._proc.terminate()
            self._proc.waitForFinished(2000)
            self._proc.kill()
            self._proc = None
