from decimal import Decimal

def parse_money(text: str) -> float | None:
    t = (text or "").strip().replace(",", "").replace("$", "").replace("%", "")
    if not t: return None
    try: return float(t)
    except ValueError: return None

def D(x, fallback="0") -> Decimal:
    try:
        s = str(x or "").replace(",", "").replace("$", "").strip()
        return Decimal(s if s != "" else fallback)
    except Exception:
        return Decimal(fallback)