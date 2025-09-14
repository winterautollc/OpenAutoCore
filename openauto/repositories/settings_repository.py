from openauto.repositories import db_handlers


class SettingsRepository:
    @staticmethod
    def load_matrix_table():
        db_conn = db_handlers.connect_db()
        db_cursor = db_conn.cursor()

        query = "SELECT min_cost, max_cost, multiplier, percent_return FROM pricing_matrix"

        db_cursor.execute(query)
        result = db_cursor.fetchall()

        db_cursor.close()
        db_conn.close()

        return result if result else None


    @staticmethod
    def load_labor_table():
        db_conn = db_handlers.connect_db()
        db_cursor = db_conn.cursor()

        query = "SELECT labor_rate, labor_type FROM labor_rates"
        db_cursor.execute(query)
        result = db_cursor.fetchall()

        db_cursor.close()
        db_conn.close()

        return result if result else None


    @staticmethod
    def get_theme(conn, default="dark"):
        cur = conn.cursor()
        cur.execute("SELECT setting_value FROM app_settings WHERE setting_key='theme';")
        row = cur.fetchone()
        return row[0] if row else default


    @staticmethod
    def set_theme(conn, theme: str):
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO app_settings (setting_key, setting_value)
            VALUES ('theme', %s)
            ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value);
        """, (theme,))
        conn.commit()