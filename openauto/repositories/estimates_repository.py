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
            try:
                cur.execute("""
                    INSERT INTO estimates (ro_id, customer_id, first_name, last_name,
                                           estimate_date, total_amount, writer, technician, archived)
                    VALUES (%s, %s, %s, %s, CURRENT_DATE(), 0.00, %s, %s, 0)
                """, (ro["id"], ro["customer_id"], ro.get("first_name",""), ro.get("last_name",""),
                      writer_name or "", tech_name or ""))
            except Exception:
                # fallback: no ro_id column in estimates
                cur.execute("""
                    INSERT INTO estimates (customer_id, first_name, last_name,
                                           estimate_date, total_amount, writer, technician, archived)
                    VALUES (%s, %s, %s, CURRENT_DATE(), 0.00, %s, %s, 0)
                """, (ro["customer_id"], ro.get("first_name",""), ro.get("last_name",""),
                      writer_name or "", tech_name or ""))
            conn.commit()
            return cur.lastrowid

    @staticmethod
    def update_total(estimate_id: int, total: float):
        conn = connect_db()
        with conn.cursor() as cur:
            cur.execute("UPDATE estimates SET total_amount=%s WHERE id=%s", (total, estimate_id))
            conn.commit()

