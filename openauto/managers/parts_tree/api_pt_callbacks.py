import os
from fastapi import FastAPI, Request, Response
from pathlib import Path
from datetime import datetime
import json, hashlib, tempfile, time

from openauto.repositories.parts_tree_repository import PartsTreeRepository
from openauto.repositories.db_handlers import connect_db
from openauto.managers.parts_tree.sessions_cache import SessionsCache


sessions = SessionsCache()
app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
DATA_ROOT = Path(os.getenv("OPENAUTO_DATA_DIR", BASE_DIR / "data"))
_LAST_HASH_BY_SESSION: dict[str, tuple[float, str]] = {}
repo = PartsTreeRepository()

def _log_payload(kind: str, payload: dict, source: str = "callback", http_status: int | None = None, estimate_id=None):
    try:
        sess = str(payload.get("sessionId") or "")
        h = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
        conn = connect_db(); cur = conn.cursor()
        cur.execute(
            """INSERT INTO partstech_payloads
               (session_id, estimate_id, payload_type, source, payload, payload_hash, http_status, created_at)
               VALUES (%s,%s,%s,%s,CAST(%s AS JSON),%s,%s,%s)
               ON DUPLICATE KEY UPDATE http_status=VALUES(http_status)""",
            (sess or None, estimate_id, kind, source, json.dumps(payload), h, http_status, datetime.utcnow())
        )
        conn.commit()
    except Exception:
        pass

def _extract_vin(payload: dict) -> str | None:
    v = payload.get("vehicle") or {}
    return v.get("vin") or payload.get("vin")


def _payload_fingerprint(payload: dict) -> str:
    orders = payload.get("orders") or []
    h = hashlib.sha256()
    for od in orders:
        sup = (od.get("supplier") or {}).get("id")
        for p in (od.get("parts") or []):
            oi = p.get("orderItemId") or p.get("id")
            q  = p.get("quantity")
            pn = p.get("partNumber") or p.get("partId")
            c  = (p.get("price") or {}).get("cost")
            l  = (p.get("price") or {}).get("list")
            h.update(str((sup, oi, pn, q, c, l)).encode("utf-8"))
    return h.hexdigest()


def _is_duplicate_recent(session_id: str, fp: str, ttl_sec: int = 3) -> bool:
    ts = time.time()
    prev = _LAST_HASH_BY_SESSION.get(session_id)
    if prev and prev[1] == fp and (ts - prev[0]) <= ttl_sec:
        return True
    _LAST_HASH_BY_SESSION[session_id] = (ts, fp)
    return False


def _upsert(payload: dict, estimate_id: int | None = None, default_status: str = "quoted"):
    if not isinstance(payload, dict):
        return {"ok": False, "reason": "bad payload"}

    session_id = str(payload.get("sessionId") or "")
    if not session_id:
        return {"ok": False, "reason": "no sessionId"}

    fp = _payload_fingerprint(payload)
    if _is_duplicate_recent(session_id, fp):
        return {"ok": True, "skipped": "duplicate_recent"}

    if estimate_id is None:
        estimate_id = sessions.get_estimate_id(session_id) or repo.get_estimate_for_session(session_id)

    repo.ensure_session(session_id=session_id, estimate_id=estimate_id,
                        ro_id=None, vin=(payload.get("vin") or (payload.get("vehicle") or {}).get("vin")))
    repo.upsert_submit_cart(payload, estimate_id=estimate_id, default_status=default_status)

    _log_payload(kind="quote/order/return", payload=payload, source="callback", http_status=200,
                 estimate_id=estimate_id)
    return {"ok": True}


@app.post("/callbacks/order")
async def cb_order(req: Request):
    body = await req.json()
    return _upsert(body, default_status="ordered")

@app.post("/callbacks/quote")
async def cb_quote(req: Request):
    body = await req.json()
    return _upsert(body, default_status="quoted")

@app.post("/callbacks/return")
async def return_cb(req: Request):
    body = await req.json()
    return _upsert(body, default_status="returned")


@app.get("/healthz", include_in_schema=False)
@app.head("/healthz", include_in_schema=False)
async def healthz():
    return Response(status_code=200)

@app.get("/readyz", include_in_schema=False)
async def readyz():
    root = DATA_ROOT
    try:
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=root, delete=True) as _:
            pass
        return {"ok": True}
    except Exception as e:
        return Response(content=f"not ready: {e}", status_code=503)

@app.get("/done")
def done():
    return Response(content="<html><body>OK</body></html>", media_type="text/html")

