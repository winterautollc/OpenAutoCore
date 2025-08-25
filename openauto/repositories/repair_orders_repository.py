from openauto.repositories.db_handlers import connect_db
import datetime
class RepairOrdersRepository:

    @staticmethod
    def create_repair_order(customer_id, vehicle_id, appointment_id=None, ro_number=None):
        if ro_number is None:
            ro_number = RepairOrdersRepository.generate_next_ro_number()

        conn = connect_db()
        cursor = conn.cursor()
        query = """
            INSERT INTO repair_orders (customer_id, vehicle_id, appointment_id, ro_number)
            VALUES (%s, %s, %s, %s)
        """
        values = (customer_id, vehicle_id, appointment_id, ro_number)
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
        cursor.execute("SELECT * FROM repair_orders WHERE id = %s", (ro_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    @staticmethod
    def update_status(ro_id, status):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE repair_orders SET status = %s WHERE id = %s", (status, ro_id))
        conn.commit()
        cursor.close()
        conn.close()

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
