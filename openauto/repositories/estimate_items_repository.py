from __future__ import annotations
from openauto.repositories.db_handlers import connect_db
from typing import Any, Dict, List
import json

class EstimateItemsRepository:

    COLS: List[str] = [
        "estimate_id", "ro_id",
        "job_id", "job_order", "line_order",
        "type", "job_name",
        "sku_number", "item_description",
        "qty", "unit_cost", "unit_price",
        "taxable", "tax_pct", "vendor", "source", "metadata",
    ]

    @staticmethod
    def _coerce_for_db(item: Dict[str, Any]) -> Dict[str, Any]:
        kind = item.get("kind")
        if not kind:
            kind = item.get("type")
        kind = str(kind).strip().lower() if kind is not None else "part"
        if kind not in ("part", "labor", "tire", "fee", "sublet"):
            kind = "part"

        mapped = {
            "estimate_id": item["estimate_id"],
            "ro_id": item.get("ro_id"),
            "job_id": item.get("job_id"),
            "job_order": item.get("job_order"),
            "line_order": item.get("line_order"),
            "type": kind,  # <-- now guaranteed string
            "job_name": item.get("job_name"),
            "sku_number": item.get("sku_number"),
            "item_description": item.get("description") or item.get("item_description"),
            "qty": item.get("qty", 1),
            "unit_cost": item.get("unit_cost", 0.0),
            "unit_price": item.get("unit_price", 0.0),
            "taxable": item.get("taxable", 1),
            "tax_pct": item.get("tax_pct"),
            "vendor": item.get("vendor"),
            "source": item.get("source", "manual"),
            "metadata": item.get("metadata"),
        }
        md = mapped["metadata"]
        if isinstance(md, (dict, list)):
            mapped["metadata"] = json.dumps(md)
        return mapped

    @staticmethod
    def insert_item(item: dict) -> int:
        data = EstimateItemsRepository._coerce_for_db(item)
        cols = EstimateItemsRepository.COLS
        placeholders = ", ".join(["%s"] * len(cols))
        sql = f"INSERT INTO estimate_items ({', '.join(cols)}) VALUES ({placeholders})"

        conn = connect_db()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, [data.get(c) for c in cols])
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    @staticmethod
    def list_for_ro(ro_id: int):
        conn = connect_db()
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT
                      i.*,
                      j.id      AS job_id,
                      j.name    AS job_name,
                      j.status  AS job_status
                    FROM estimate_items i
                    LEFT JOIN estimate_jobs j ON j.id = i.job_id
                    WHERE i.ro_id = %s
                    ORDER BY j.name, i.job_order, i.line_order, i.id
                    """,
                    (ro_id,),
                )
                return cursor.fetchall() or None
        finally:
            conn.close()

    @staticmethod
    def delete_for_ro(ro_id: int):
        conn = connect_db()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM estimate_items WHERE ro_id = %s", (ro_id,))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def move_items(*, item_ids: list[int], target_job_id: int, insert_at: int):
        if not item_ids:
            return
        conn = connect_db()
        cur = conn.cursor()
        try:
            conn.start_transaction()

            # Read current locations (id, job_id, line_order)
            q = "SELECT id, job_id, line_order FROM estimate_items WHERE id IN (%s)" % \
                ",".join(["%s"] * len(item_ids))
            cur.execute(q, item_ids)
            rows = cur.fetchall()  # [(id, job_id, line_order), ...]

            # Compact each source job
            by_src = {}
            for row in rows:
                by_src.setdefault(row[1], []).append(row[2])
            for src_job_id, removed_orders in by_src.items():
                for lo in sorted(removed_orders):
                    cur.execute("""
                        UPDATE estimate_items
                           SET line_order = line_order - 1
                         WHERE job_id = %s AND line_order > %s
                    """, (src_job_id, lo))

            # Make room in target
            cur.execute("""
                UPDATE estimate_items
                   SET line_order = line_order + %s
                 WHERE job_id = %s AND line_order >= %s
            """, (len(item_ids), target_job_id, insert_at))

            # Place moved items in order
            for offset, iid in enumerate(item_ids):
                cur.execute("""
                    UPDATE estimate_items
                       SET job_id = %s, line_order = %s
                     WHERE id = %s
                """, (target_job_id, insert_at + offset, iid))

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_ids_for_estimate(estimate_id: int) -> list[int]:
        conn = connect_db()
        with conn.cursor() as c:
            c.execute("SELECT id FROM estimate_items WHERE estimate_id=%s", (estimate_id,))
            return [row[0] for row in c.fetchall()]

    @staticmethod
    def update_item(it: dict) -> None:
        if not it.get("id"):
            raise ValueError("update_item requires it['id']")

        data = EstimateItemsRepository._coerce_for_db(it)

        sql = """
            UPDATE estimate_items
               SET
                 estimate_id = %s,
                 ro_id       = %s,
                 job_id      = %s,
                 job_order   = %s,
                 line_order  = %s,
                 type        = %s,
                 job_name    = %s,
                 sku_number = %s,
                 item_description = %s,
                 qty         = %s,
                 unit_cost   = %s,
                 unit_price  = %s,
                 taxable     = %s,
                 tax_pct     = %s,
                 vendor      = %s,
                 source      = %s,
                 metadata    = %s
             WHERE id = %s
        """

        params = [
            data.get("estimate_id"),
            data.get("ro_id"),
            data.get("job_id"),
            data.get("job_order"),
            data.get("line_order"),
            data.get("type"),
            data.get("job_name"),
            data.get("sku_number"),
            data.get("item_description"),
            data.get("qty"),
            data.get("unit_cost"),
            data.get("unit_price"),
            data.get("taxable"),
            data.get("tax_pct"),
            data.get("vendor"),
            data.get("source"),
            data.get("metadata"),
            int(it["id"]),
        ]

        conn = connect_db()
        try:
            with conn, conn.cursor() as c:
                c.execute(sql, params)
        finally:
            conn.close()


    @staticmethod
    def delete_many(ids: list[int]) -> None:
        if not ids:
            return
        conn = connect_db()
        with conn, conn.cursor() as c:
            q = "DELETE FROM estimate_items WHERE id IN (%s)" % ",".join(["%s"] * len(ids))
            c.execute(q, ids)
        conn.close()
