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
        conn = db_handlers.connect_db()
        with conn.cursor() as cur:
            for idx, line_id in enumerate(ordered_ids, start=1):
                cur.execute("UPDATE ro_c3_lines SET line_no=%s WHERE id=%s AND ro_id=%s",
                            (idx, line_id, ro_id))
            conn.commit()

    @staticmethod
    def concern_for_ro(ro_id: int, concern: str | None):
        if concern is None:
            return
        ROC3Repository.set_or_create_concern(ro_id, concern, created_by=None)

    @staticmethod
    def get_primary_concern(ro_id: int) -> str | None:
        conn = db_handlers.connect_db()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT concern
                FROM ro_c3_lines
                Where ro_id=%s
                ORDER BY line_no ASC, id ASC
                LIMIT 1
                """, (ro_id, ))
            row = cur.fetchone()
            return row[0] if row and row[0] is not None else None


    @staticmethod
    def set_or_create_concern(ro_id: int, concern: str, created_by: int | None) -> int:
        concern = (concern or "").strip()
        if not concern:
            return 0

        conn = db_handlers.connect_db()
        with conn.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT id FROM ro_c3_lines
                WHERE ro_id=%s
                ORDER BY line_no ASC, id ASC
                LIMIT 1
                """, (ro_id, ))
            row = cur.fetchone()
            if row:
                line_id = int(row["id"])
                cur.execute("UPDATE ro_c3_lines SET concern=%s, updated_at=NOW() WHERE id=%s", (concern, line_id))
                conn.commit()
                return line_id
            else:
                with conn.cursor() as cur2:
                    cur2.execute("SELECT COALESCE(MAX(line_no),0)+1 FROM ro_c3_lines WHERE ro_id=%s", (ro_id,))
                    (next_no, ) = cur2.fetchone()
                cur.execute("""
                    INSERT INTO ro_c3_lines (ro_id, line_no, concern, created_by)
                    VALUES (%s, %s, %s, %s)
                    """, (ro_id, int(next_no or 1), concern, created_by))
                conn.commit()
                return cur.lastrowid
