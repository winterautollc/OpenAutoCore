import json, time, os
from pathlib import Path
from PyQt6.QtCore import QProcess, QEventLoop, QTimer

TOKEN_PATH = Path("data/partstech_token.json")
SKEW = 120

def _run_ptcli(args: list[str], timeout_ms: int = 15000) -> str:
    proc = QProcess()
    proc.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)  # stdout+stderr together
    proc.setProgram(args[0])
    proc.setArguments(args[1:])

    buf: list[str] = []
    proc.readyReadStandardOutput.connect(lambda: buf.append(bytes(proc.readAll()).decode("utf-8", "ignore")))
    proc.readyReadStandardError.connect(lambda: buf.append(bytes(proc.readAll()).decode("utf-8", "ignore")))

    loop = QEventLoop()
    proc.finished.connect(lambda *_: loop.quit())

    proc.start()
    if not proc.waitForStarted(3000):
        raise RuntimeError(f"ptcli failed to start: {args[0]}")

    t = QTimer()
    t.setSingleShot(True)
    t.timeout.connect(lambda: (proc.kill(), loop.quit()))
    t.start(timeout_ms)
    loop.exec()
    t.stop()

    return "".join(buf).strip()

def get_partstech_token(ptcli_path: str, base: str,
                        partner_id: str, partner_key: str,
                        user_id: str, user_key: str,
                        timeout_ms: int = 15000) -> dict:

    args = [
        ptcli_path,
        "-op", "auth",
        "-auth_url", base,
        "-partner", partner_id,
        "-partner_key", partner_key,
        "-user_id", user_id,
        "-user_key", user_key,
    ]
    out = _run_ptcli(args, timeout_ms=timeout_ms)

    try:
        data = json.loads(out)
    except Exception:
        raise RuntimeError(f"ptcli auth returned non-JSON:\n{out[:1000]}")

    token = (data.get("accessToken") or data.get("token") or data.get("access_token") or data.get("Token"))
    ttl   = data.get("expiresIn") or data.get("expires_in") or 3600
    try:
        ttl = int(ttl)
    except Exception:
        ttl = 3600

    if not token:
        raise RuntimeError(f"Auth returned no token. Raw:\n{json.dumps(data, indent=2)[:1000]}")

    expires_at = int(time.time()) + ttl

    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    with TOKEN_PATH.open("w") as f:
        json.dump({"accessToken": token, "expiresAt": expires_at}, f, indent=2)

    return {"accessToken": token, "expiresAt": expires_at}

def _load_cached():
    try:
        with TOKEN_PATH.open() as f:
            return json.load(f)
    except Exception:
        return None

def get_valid_token(ptcli_path: str, base: str,
                    partner_id: str, partner_key: str,
                    user_id: str, user_key: str,
                    force_refresh: bool = False) -> str:

    now = int(time.time())
    if not force_refresh:
        cached = _load_cached()
        if cached and cached.get("accessToken") and cached.get("expiresAt"):
            if int(cached["expiresAt"]) - SKEW > now:
                return cached["accessToken"]

    fresh = get_partstech_token(ptcli_path, base, partner_id, partner_key, user_id, user_key)
    return fresh["accessToken"]
