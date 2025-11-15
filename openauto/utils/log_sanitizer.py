from __future__ import annotations
import re
from typing import Optional

_PATTERNS = [
    (re.compile(r"(-token)\s+\S+", re.I), r"\1 [REDACTED]"),
    (re.compile(r"(authorization[:=]\s*)\S+", re.I), r"\1[REDACTED]"),
    (re.compile(r"(x-api-key[:=]\s*)\S+", re.I), r"\1[REDACTED]"),
    (re.compile(r"(api[_-]?key[:=]\s*)\S+", re.I), r"\1[REDACTED]"),
    (re.compile(r"\beyJ[a-zA-Z0-9_\-]{10,}\.[a-zA-Z0-9_\-]{10,}\.[a-zA-Z0-9_\-]{10,}\b"), "[JWT-REDACTED]"),
    (re.compile(r'("sessionId"\s*:\s*")([^"]+)(")', re.I), r'\1[SID-REDACTED]\3'),
    (re.compile(r"(sessionId\s*=\s*)(\S+)", re.I), r"\1[SID-REDACTED]"),
]

def scrub(text: Optional[str]) -> str:
    t = text or ""
    for rx, repl in _PATTERNS:
        t = rx.sub(repl, t)
    return t

def mask_sid(sid: Optional[str]) -> str:
    s = (sid or "").strip()
    if len(s) <= 6:
        return "[SID-REDACTED]"
    return f"[SID]…{s[-6:]}"
