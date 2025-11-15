from __future__ import annotations
from typing import Optional, TYPE_CHECKING
import json
from pathlib import Path

if TYPE_CHECKING:
    from openauto.subclassed_widgets.models.parts_tree_model import PartsTreeModel  # type-only import

class QuotesFolder:
    def __init__(self, quotes_dir: str | Path):
        self.dir = Path(quotes_dir)

    def sessions_map(self) -> dict:
        p = self.dir / "sessions.json"
        return json.loads(p.read_text("utf-8")) if p.exists() else {}

    def session_for_vin(self, vin: str) -> Optional[str]:
        entry = self.sessions_map().get(vin)
        return entry.get("sessionId") if isinstance(entry, dict) else None

    def payload_for_session(self, session_id: str) -> Optional[dict]:
        p = self.dir / f"{session_id}.json"
        return json.loads(p.read_text("utf-8")) if p.exists() else None

    def newest_payload(self) -> Optional[dict]:
        files = [p for p in self.dir.glob("*.json") if p.name != "sessions.json"]
        return json.loads(max(files, key=lambda p: p.stat().st_mtime).read_text("utf-8")) if files else None


def resolve_vin_from_ui(ui) -> Optional[str]:
    for attr in ("vehcle_line", "vehicle_line"):
        w = getattr(ui, attr, None)
        if w is not None:
            try:
                raw = (w.text() or "").strip()
                candidate = raw.split()[0] if raw else ""
                if len(candidate) == 17:
                    return candidate
            except Exception:
                pass
    return None



from typing import Optional

class PartsTreeLoader:
    def __init__(self, model: "PartsTreeModel", repo, quotes_dir, *, use_json_fallback: bool = False):
        self.model = model
        self.repo = repo
        self.quotes = QuotesFolder(quotes_dir)
        self.use_json_fallback = use_json_fallback
        self._last_estimate_id: int | None = None
        self._last_session_id: str | None = None
        self._last_signature: tuple[str, ...] | None = None

    def load(self, *, ui=None, estimate_id: Optional[int] = None, session_id: Optional[str] = None,
                        mode: str = "merge", fallback_to_newest: bool = False) -> int:

        rows: list[dict] = []
        if estimate_id:
            try:
                rows = self.repo.load_items_for_estimate(int(estimate_id)) or []
            except Exception as e:
                print(f"[PartsTreeLoader] load_items_for_estimate error: {e}")

        if not rows and session_id:
            try:
                rows = self.repo.load_items_for_session(session_id) or []
            except Exception as e:
                print(f"[PartsTreeLoader] load_items_for_session error: {e}")

        if not rows and fallback_to_newest and estimate_id:
            try:
                latest = self.repo.latest_session_for_estimate(int(estimate_id))
                if latest:
                    rows = self.repo.load_items_for_session(latest) or []
            except Exception as e:
                print(f"[PartsTreeLoader] latest_session_for_estimate error: {e}")

        if not rows and self.use_json_fallback and session_id:
            try:
                payload = self.quotes.payload_for_session(session_id)
                if payload and isinstance(payload, dict):
                    orders = payload.get("orders") or []
                    flat = []
                    for od in orders:
                        sup = (od or {}).get("supplier") or {}
                        for p in (od or {}).get("parts") or []:
                            price = p.get("price") or {}
                            core_amt = float(price.get("core") or 0.0)
                            taxonomy = p.get("taxonomy") or {}
                            flat.append({
                                "orderItemId": p.get("orderItemId") or p.get("id"),
                                "sessionId": payload.get("sessionId"),
                                "supplierName": sup.get("name"),
                                "partNumber": p.get("partNumber"),
                                "partTypeName": (p.get("taxonomy") or {}).get("partTypeName") or p.get("partTypeName"),
                                "quantity": p.get("quantity"),
                                "price": {"cost": price.get("cost"), "list": price.get("list"), "core": price.get("core")},
                                "core": core_amt,
                                "sku": p.get("partNumber"),
                                "unitCost": price.get("cost"),
                                "listPrice": price.get("list"),
                                "category": p.get("partCategory") or taxonomy.get("categoryName")

                            })
                    rows = flat
            except Exception as e:
                print(f"[PartsTreeLoader] JSON fallback error: {e}")

        try:
            sig: tuple[str, ...] | None = None
            if rows:
                oids = [str(r.get("orderItemId")) for r in rows if isinstance(r, dict) and r.get("orderItemId")]
                if oids:
                    sig = tuple(sorted(set(oids)))

            context_changed = (self._last_estimate_id != (int(estimate_id) if estimate_id else None)) \
                              or (session_id and self._last_session_id != session_id)

            if rows:
                if mode in ("replace", "refresh") or context_changed:
                    self.model.clear()
                    self.model.load_from_callback_objects(rows)
                else:
                    current_oids: set[str] = set()
                    root = self.model._root
                    for cat in root.children:
                        for ch in getattr(cat, "children", []):
                            if getattr(ch, "is_item", lambda: False)() and isinstance(ch.meta, dict):
                                oi = str(ch.meta.get("orderItemId") or ch.meta.get("id") or "")
                                if oi:
                                    current_oids.add(oi)

                    incoming_oids = set(oids) if oids else set()
                    to_add = incoming_oids - current_oids
                    to_remove = current_oids - incoming_oids

                    if to_remove:
                        self.model.remove_by_order_item_ids(sorted(to_remove))

                    if to_add:
                        add_rows = []


                        for r in rows:
                            oi = str(r.get("orderItemId") or "")
                            if oi not in to_add:
                                continue
                            add_rows.append({
                                "category": r.get("partTypeName") or r.get("category") or "PART",
                                "partName": r.get("partTypeName") or "PART",
                                "supplier": r.get("supplierName") or "",
                                "sku": r.get("partNumber") or "",
                                "description": r.get("partTypeName") or r.get("description") or "",
                                "qty": r.get("quantity"),
                                "unitCost": r.get("unitCost"),
                                "listPrice": r.get("listPrice"),
                                "core": r.get("core"),
                                "orderPlatform": "PartsTech",
                                "meta": dict(r),

                            })
                        if add_rows:
                            self.model.append_items(add_rows)
            else:
                if mode in ("replace", "refresh") or context_changed:
                    self.model.clear()

            self._last_estimate_id = int(estimate_id) if estimate_id else None
            self._last_session_id = session_id or self._last_session_id
            self._last_signature = sig
            return len(rows or [])
        except Exception as e:
            print(f"[PartsTreeLoader] model load error: {e}")
            return 0


