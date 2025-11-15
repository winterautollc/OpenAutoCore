from __future__ import annotations
from typing import Optional
from openauto.repositories.parts_tree_repository import PartsTreeRepository
import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv()

class SessionsCache:
    def __init__(self):
        self._data = {}
        self._by_session = {}
        self.repo = PartsTreeRepository()


    def get_redirect(self, vin: str) -> Optional[str]:
        item = self._data.get(vin.upper())
        return item.get("redirectUrl") if isinstance(item, dict) else None

    def put_redirect(self, vin: str, session_id: str, redirect_url: str) -> None:
        if not vin:
            return
        self._data[vin.upper()] = {"sessionId": session_id, "redirectUrl": redirect_url}


    def clear_for_vin(self, vin: str) -> None:
        if not vin:
            return
        self._data.pop(vin.upper(), None)


    def get_session_id(self, vin: str) -> Optional[str]:
        item = self._data.get(vin.upper())
        return item.get("sessionId") if isinstance(item, dict) else None

    def set_session_link(self, *, session_id: str, ro_id: int, estimate_id: int, vin: str = "") -> None:
        if not session_id:
            return
        try:
            est = int(estimate_id)
        except Exception:
            return
        if est <= 0:
            return
        self._by_session[str(session_id)] = {"estimate_id": est, "vin": vin or ""}
        self.repo.ensure_session(session_id=str(session_id), ro_id=ro_id, estimate_id=est, vin=(vin or None ))



    def get_estimate_id(self, session_id: str) -> int | None:
        if not session_id:
            return None
        rec = self._by_session.get(str(session_id)) or {}
        return rec.get("estimate_id")


    def clear_session(self, session_id: str) -> None:
        if not session_id:
            return
        self._by_session.pop(str(session_id), None)
        try:
            vin = self.get_vin(session_id)
            if vin:
                self.clear_for_vin(vin)
        except Exception:
            pass


    def find_session_for_estimate(self, estimate_id: int, vin: str | None = None) -> str:
        try:
            est = int(estimate_id)
        except Exception:
            return None

        if est <= 0:
            return None
        found = None
        for sid, rec in (self._by_session or {}).items():
            if  not isinstance(rec, dict):
                continue
            if int(rec.get("estimate_id") or 0) != est:
                continue
            if vin and rec.get("vin") and vin and rec.get("vin").upper() != vin.upper():
                continue

            try:
                if self.repo.session_has_ordered_items(sid):
                    continue
            except Exception:
                pass
            found = sid
            break
        return found


    def get_vin(self, session_id: str) -> str | None:
        if not session_id:
            return None
        rec = self._by_session.get(str(session_id)) or {}
        v = rec.get("vin") or ""
        return v if v else None




    @staticmethod
    def build_redirect_url(partner_id: str, user_id: str, session_id: str) -> str:
        link = os.getenv("QU_CBTF_TFBSDI")
        return f"{link}/{partner_id}/{user_id}/{session_id}/"

