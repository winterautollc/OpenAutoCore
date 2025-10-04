from openauto.repositories import db_handlers

class ROC3Repository:
    @staticmethod
    def list_for_ro(ro_id: int) -> list[dict]:
        conn = db_handlers.connect_db()
        with conn.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT id, ro_id, line_no, concern, cause, correction, estimate_item_id,
                       created_by, created_at, updated_at
                FROM ro_c3_lines
                WHERE ro_id = %s
                ORDER BY line_no ASC, id ASC
            """, (ro_id,))
            return list(cur.fetchall() or [])

    @staticmethod
    def next_line_no(ro_id: int) -> int:
        conn = db_handlers.connect_db()
        with conn.cursor() as cur:
            cur.execute("SELECT COALESCE(MAX(line_no),0)+1 FROM ro_c3_lines WHERE ro_id=%s", (ro_id,))
            (n,) = cur.fetchone()
            return int(n or 1)

    @staticmethod
    def create_line(ro_id: int, concern: str, cause: str | None, correction: str | None,
                    estimate_item_id: int | None, created_by: int | None) -> int:
        line_no = ROC3Repository.next_line_no(ro_id)
        conn = db_handlers.connect_db()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO ro_c3_lines (ro_id, line_no, concern, cause, correction, estimate_item_id, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (ro_id, line_no, concern, cause, correction, estimate_item_id, created_by))
            conn.commit()
            return cur.lastrowid

    @staticmethod
    def update_line(line_id: int, fields: dict):
        if not fields: return
        keys = []
        vals = []
        for k, v in fields.items():
            keys.append(f"{k}=%s")
            vals.append(v)
        vals.append(line_id)
        q = f"UPDATE ro_c3_lines SET {', '.join(keys)} WHERE id=%s"
        conn = db_handlers.connect_db()
        with conn.cursor() as cur:
            cur.execute(q, tuple(vals))
            conn.commit()

    @staticmethod
    def delete_line(line_id: int):
        conn = db_handlers.connect_db()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM ro_c3_lines WHERE id=%s", (line_id,))
            conn.commit()

    @staticmethod
    def reorder(ro_id: int, ordered_ids: list[int]):
        # Renumber 1..N in the passed order to keep it simple and deterministic
        conn = db_handlers.connect_db()
        with conn.cursor() as cur:
            for idx, line_id in enumerate(ordered_ids, start=1):
                cur.execute("UPDATE ro_c3_lines SET line_no=%s WHERE id=%s AND ro_id=%s",
                            (idx, line_id, ro_id))
            conn.commit()
