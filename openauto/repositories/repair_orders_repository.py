from openauto.repositories.db_handlers import connect_db
import datetime
from openauto.repositories import db_handlers




class RepairOrdersRepository:
    ALLOWED_STATUSES = {"open", "approved", "working", "checkout", "archived"}


    @staticmethod
    def create_repair_order(customer_id, vehicle_id, appointment_id=None, ro_number=None, created_by=None, assigned_writer_id=None):
        if ro_number is None:
            ro_number = RepairOrdersRepository.generate_next_ro_number()

        conn = connect_db()
        cursor = conn.cursor()
        query = """
            INSERT INTO repair_orders (customer_id, vehicle_id, appointment_id, ro_number, created_by, assigned_writer_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (customer_id, vehicle_id, appointment_id, ro_number, created_by, assigned_writer_id)
        cursor.execute(query, values)
        conn.commit()
        ro_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return ro_id


    @staticmethod
    def get_repair_order_by_id(ro_id):
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT ro.*,
                   CONCAT(t.first_name,' ',t.last_name) AS tech_name,
                   CONCAT(w.first_name,' ',w.last_name) AS writer_name,
                   ro.assigned_tech_id,
                   ro.assigned_writer_id,
                   ro.created_by
            FROM repair_orders ro
            LEFT JOIN users t ON t.id = ro.assigned_tech_id
            -- writer fallback: assigned writer OR creator (writer can be writer or manager)
            LEFT JOIN users w ON w.id = COALESCE(ro.assigned_writer_id, ro.created_by)
            WHERE ro.id = %s
        """, (ro_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result


    @staticmethod
    def lock_repair_order(ro_id, locked_by):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE repair_orders
            SET locked_by = %s, locked_at = NOW()
            WHERE id = %s AND (locked_by IS NULL OR locked_by = %s)
        """, (locked_by, ro_id, locked_by))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def release_lock(ro_id, locked_by):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE repair_orders
            SET locked_by = NULL, locked_at = NULL
            WHERE id = %s AND locked_by = %s
        """, (ro_id, locked_by))
        conn.commit()
        cursor.close()
        conn.close()


    @staticmethod
    def generate_next_ro_number():
        conn = connect_db()
        cursor = conn.cursor()
        year = datetime.datetime.now().year
        prefix = f"{year}-%"

        query = """
            SELECT ro_number FROM repair_orders
            WHERE ro_number LIKE %s
            ORDER BY ro_number DESC LIMIT 1
        """
        cursor.execute(query, (prefix,))
        last = cursor.fetchone()
        cursor.close()
        conn.close()

        if last and last[0]:
            last_seq = int(last[0].split("-")[1])
        else:
            last_seq = 0

        return f"{year}-{last_seq + 1:05d}"

    @staticmethod
    def load_repair_orders(status="open", limit=200, offset=0):
        conn = db_handlers.connect_db()
        cursor = conn.cursor()
        query = """
            SELECT
                ro.id,
                ro.ro_number,
                ro.created_at,
                CONCAT(c.first_name, ' ', c.last_name) AS name,
                v.year,
                v.make,
                v.model,
                CONCAT(t.first_name,' ',t.last_name) AS tech,
                -- writer fallback to creator if no assigned writer
                CONCAT(w.first_name,' ',w.last_name) AS writer,
                0.00 AS total
            FROM repair_orders ro
            LEFT JOIN customers c ON c.customer_id = ro.customer_id
            LEFT JOIN vehicles  v ON v.id = ro.vehicle_id
            LEFT JOIN users     t ON t.id = ro.assigned_tech_id
            LEFT JOIN users     w ON w.id = COALESCE(ro.assigned_writer_id, ro.created_by)
            WHERE ro.status = %s
            ORDER BY ro.ro_number
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (status, limit, offset))
        result = cursor.fetchall() or []
        cursor.close()
        conn.close()
        return result

    @staticmethod
    def delete_repair_order(estimate_id: int):
        conn = db_handlers.connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM repair_orders WHERE id = %s", (estimate_id,))
        conn.commit()
        cursor.close()
        conn.close()


    @staticmethod
    def update_status(ro_id: int, new_status: str):
        new_status = (new_status or "").strip().lower()
        if new_status not in RepairOrdersRepository.ALLOWED_STATUSES:
            raise ValueError(f"Invalid status: {new_status}")

        conn = db_handlers.connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE repair_orders SET status = %s WHERE id = %s",
            (new_status, ro_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def assign_staff(ro_id: int, writer_id: int | None = None, tech_id: int | None = None):
        sets, vals = [], []
        if writer_id is not None:
            sets.append("assigned_writer_id = %s")
            vals.append(writer_id)
        if tech_id is not None:
            sets.append("assigned_tech_id = %s")
            vals.append(tech_id)
        if not sets:
            return
        vals.append(ro_id)
        q = f"UPDATE repair_orders SET {', '.join(sets)} WHERE id = %s"

        cnx = db_handlers.connect_db()
        with cnx.cursor() as cur:
            cur.execute(q, tuple(vals))
            cnx.commit()