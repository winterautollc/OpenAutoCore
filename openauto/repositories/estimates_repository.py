from openauto.repositories.db_handlers import connect_db



class EstimatesRepository:
    @staticmethod
    def get_by_ro_id(ro_id: int):
        conn = connect_db()
        try:
            with conn.cursor(dictionary=True) as cur:
                # Works whether or not 'ro_id' exists (fallback handled below)
                try:
                    cur.execute("SELECT * FROM estimates WHERE ro_id = %s LIMIT 1", (ro_id,))
                    return cur.fetchone()
                except Exception:
                    return None
        finally:
            conn.close()



    @staticmethod
    def create_for_ro(ro: dict, writer_name: str | None, tech_name: str | None) -> int:
        conn = connect_db()
        with conn.cursor() as cur:
            # try with ro_id + snapshots
            new_id = None
            try:
                cur.execute("""
                    INSERT INTO estimates (ro_id, customer_id, first_name, last_name,
                                           estimate_date, total_amount, writer, technician, archived)
                    VALUES (%s, %s, %s, %s, CURRENT_DATE(), 0.00, %s, %s, 0)
                """, (ro["id"], ro["customer_id"], ro.get("first_name",""), ro.get("last_name",""),
                      writer_name or "", tech_name or ""))
                new_id = cur.lastrowid
            except Exception:
                # fallback: no ro_id column in estimates
                cur.execute("""
                    INSERT INTO estimates (customer_id, first_name, last_name,
                                           estimate_date, total_amount, writer, technician, archived)
                    VALUES (%s, %s, %s, CURRENT_DATE(), 0.00, %s, %s, 0)
                """, (ro["customer_id"], ro.get("first_name",""), ro.get("last_name",""),
                      writer_name or "", tech_name or ""))
                new_id = cur.lastrowid

            # --- NEW: link back to RO so future UI edits can resolve estimate_id ---
            try:
                cur.execute("UPDATE repair_orders SET estimate_id=%s WHERE id=%s", (new_id, ro["id"]))
            except Exception:
                # If the column doesn't exist yet, silently ignore
                pass

            conn.commit()
            conn.close()
            return new_id

    @staticmethod
    def update_total(estimate_id: int, total: float):
        conn = connect_db()
        with conn.cursor() as cur:
            cur.execute("UPDATE estimates SET total_amount=%s WHERE id=%s", (total, estimate_id))
            conn.commit()

    @staticmethod
    def get_internal_memo(estimate_id: int) -> str | None:
        conn = connect_db()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute("SELECT internal_memo FROM estimates WHERE id=%s", (estimate_id, ))
                row = cur.fetchone()
                return row["internal_memo"] if row and "internal_memo" in row else None
        finally:
            conn.close()


    @staticmethod
    def set_internal_memo(estimate_id: int, memo: str | None) -> None:
        conn = connect_db()
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE estimates SET internal_memo=%s WHERE id=%s", (memo, estimate_id))
                conn.commit()
        finally:
            conn.close()

    @staticmethod
    def get_by_id(estimate_id: int):
        conn = connect_db()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute("SELECT * FROM estimates WHERE id = %s", (estimate_id, ))
                return cur.fetchone()
        finally:
            conn.close()