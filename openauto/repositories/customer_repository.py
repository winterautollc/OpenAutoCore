from openauto.repositories import db_handlers
import logging


### INSERTS A NEW CUSTOMER INTO THE customers table ###
class CustomerRepository:
    @staticmethod
    def insert_customer(customer_data):
        conn = db_handlers.connect_db()
        cursor = conn.cursor()
        query = """
        INSERT INTO customers (
            last_name, first_name, phone, address, city, state, zip, alt_phone, email
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, customer_data)
        conn.commit()
        customer_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return customer_id if customer_id else None

### DELETES CUSTOMER AND FROM DATABASE ###
    @staticmethod
    def delete_customer(customer_id):
        conn = db_handlers.connect_db()
        cursor = conn.cursor()
        try:
            query = "DELETE FROM customers WHERE customer_id = %s"
            cursor.execute(query, (customer_id,))
            conn.commit()
        finally:
            cursor.close()
            conn.close()


### RETRIEVES CUSTOMER ID BY FULL FIELD MATCH ###
    @staticmethod
    def get_customer_id_by_details(customer_data):
        conn = db_handlers.connect_db()
        cursor = conn.cursor()
        query = """
        SELECT customer_id FROM customers
        WHERE last_name = %s AND first_name = %s AND phone = %s AND address = %s
          AND city = %s AND state = %s AND zip = %s
          AND alt_phone = %s AND email = %s
        """

        cursor.execute(query, customer_data)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return result[0] if result else None

### RETURNS A SMALLER LIST OF CUSTOMER last_name, first_name, phone, AND customer_id ###
    @staticmethod
    def get_all_customer_names():

        conn = db_handlers.connect_db()
        cursor = conn.cursor()

        query = "SELECT last_name, first_name, phone, customer_id FROM customers ORDER BY last_name"
        cursor.execute(query)
        result = cursor.fetchall()

        cursor.close()
        conn.close()

        return result if result else None

### RETRIEVES ALL CUSTOMER INFORMATION FROM customer_table ###
    @staticmethod
    def get_all_customer_info():
        conn = db_handlers.connect_db()
        cursor = conn.cursor()

        query = "SELECT * FROM customers ORDER BY last_name"
        cursor.execute(query)
        result = cursor.fetchall()

        cursor.close()
        conn.close()

        return result if result else None


### GETS customer_id ###
    @staticmethod
    def get_customer_info_by_id(customer_id):
        db_conn = db_handlers.connect_db()
        cursor = db_conn.cursor(dictionary=True)
        query = """
            SELECT first_name, last_name, address, city, state, zip, phone, alt_phone, email
            FROM customers
            WHERE customer_id = %s
        """
        cursor.execute(query, (customer_id,))
        result = cursor.fetchone()
        cursor.close()
        db_conn.close()
        return result if result else None

### UPDATES CUSTOMER INFORMATION ###
    @staticmethod
    def update_customer_by_id(customer_id, changed_values):
        if not changed_values:
            raise ValueError("No values provided for update.")

        # Basic validation (extend as needed)
        for key, value in changed_values.items():
            if value is None or value == "":
                raise ValueError(f"'{key}' cannot be empty.")

        db_conn = db_handlers.connect_db()
        cursor = db_conn.cursor()
        try:
            db_conn.start_transaction()  # Begin transaction

            updates = [f"{column} = %s" for column in changed_values.keys()]
            values = list(changed_values.values()) + [customer_id]
            sql = f"UPDATE customers SET {', '.join(updates)} WHERE customer_id = %s"

            cursor.execute(sql, values)
            db_conn.commit()  # Commit if everything is okay

            logging.info(f"Updated customer_id={customer_id} with: {changed_values}")

        except Exception as e:
            db_conn.rollback()  # Roll back on failure
            logging.error(f"Failed to update customer_id={customer_id}: {e}")
            raise  # Reraise for the UI to handle

        finally:
            cursor.close()
            db_conn.close()