from openauto.repositories import db_handlers


class EstimateRepository:

    @staticmethod
    def load_estimate():
        conn = db_handlers.connect_db()
        cursor = conn.cursor()
        query = """SELECT * FROM repair_orders ORDER BY id"""
        cursor.execute(query)
        result = cursor.fetchall()
        return result
