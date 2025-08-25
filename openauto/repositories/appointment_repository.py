from openauto.repositories.db_handlers import connect_db
from PyQt6.QtCore import QDate, QTime


class AppointmentRepository:

    @staticmethod
    def insert_appointment(customer_id, vehicle_id, vin, date, time, notes: str = "", dropoff_type=None):
        conn = connect_db()
        cursor = conn.cursor()
        date_str = date.toString("yyyy-MM-dd")
        time_str = time.toString("HH:mm:ss")

        query = """
            INSERT INTO appointments (customer_id, vehicle_id, vin, appointment_date, appointment_time, notes, dropoff_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            customer_id,
            vehicle_id,
            vin,
            date.toString("yyyy-MM-dd"),
            time.toString("HH:mm:ss"),
            notes,
            dropoff_type
        )

        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_appointments_for_week(start_date: QDate, end_date: QDate):
        start_str = start_date.toString("yyyy-MM-dd")
        end_str = end_date.toString("yyyy-MM-dd")

        conn = connect_db()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT a.id, a.customer_id, a.vehicle_id, a.appointment_date, a.appointment_time, a.dropoff_type,
                   a.notes, a.vin, c.first_name, c.last_name
            FROM appointments a
            JOIN customers c ON a.customer_id = c.customer_id
            WHERE a.appointment_date BETWEEN %s AND %s
        """
        cursor.execute(query, (start_str, end_str))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results if results else []

    @staticmethod
    def update_appointment(appointment_id, customer_id, vehicle_id, vin, date, time, notes: str = "", dropoff_type=None):
        conn = connect_db()
        cursor = conn.cursor()

        date_str = date.toString("yyyy-MM-dd")
        time_str = time.toString("HH:mm:ss")

        query = """
            UPDATE appointments
            SET customer_id = %s,
                vehicle_id = %s,
                vin = %s,
                appointment_date = %s,
                appointment_time = %s,
                notes = %s,
                dropoff_type = %s
            WHERE id = %s
        """
        cursor.execute(query, (customer_id, vehicle_id, vin, date_str, time_str, notes, dropoff_type, appointment_id))
        conn.commit()
        cursor.close()
        conn.close()


    @staticmethod
    def delete_appointment(appointment_id: int):
        conn = connect_db()
        cursor = conn.cursor()
        query = "DELETE FROM appointments WHERE id = %s"
        cursor.execute(query, (appointment_id,))
        conn.commit()
        cursor.close()
        conn.close()


    @staticmethod
    def get_appointment_ids_and_timestamps():
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, last_updated FROM appointments")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results

    @staticmethod
    def get_appointment_details_by_id(appointment_id: int):
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)
        query = """SELECT a.id, a.customer_id, a.vehicle_id, a.appointment_date, a.appointment_time, a.dropoff_type,
                   a.appointment_date, a.notes, a.vin, c.first_name, c.last_name, c.phone, v.year, v.make, v.model
            FROM appointments a
            JOIN customers c ON a.customer_id = c.customer_id
            JOIN vehicles v ON a.vehicle_id = v.customer_id
            WHERE a.id = %s"""
        cursor.execute(query, (appointment_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
