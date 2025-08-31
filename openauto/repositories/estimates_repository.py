from openauto.repositories import db_handlers

class EstimateRepository:

    @staticmethod
    def load_estimate(limit=200, offset=0):
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
                 ''  AS tech,   
                 0.00 AS total 
             FROM repair_orders ro
             LEFT JOIN customers c ON c.customer_id = ro.customer_id
             LEFT JOIN vehicles  v ON v.customer_id  = ro.vehicle_id
             ORDER BY ro.ro_number
             LIMIT %s OFFSET %s
         """
        cursor.execute(query, (limit, offset))
        result = cursor.fetchall() or []
        cursor.close()
        conn.close()
        return result

    @staticmethod
    def delete_estimate(estimate_id: int):
        conn = db_handlers.connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM repair_orders WHERE id = %s", (estimate_id,))
        conn.commit()
        cursor.close()
        conn.close()

