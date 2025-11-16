from openauto.repositories import db_handlers



### ADDS VEHICLE TO DATABASE ###
class VehicleRepository:
    @staticmethod
    def insert_vehicle(vehicle_data):
        vin = (vehicle_data[0] or "").strip().upper()
        year = vehicle_data[1]
        make = vehicle_data[2]
        model = vehicle_data[3]
        engine_size = vehicle_data[4]
        trim = vehicle_data[5]
        customer_id = vehicle_data[6]

        plate = vehicle_data[7] if len(vehicle_data) > 7 else None
        plate_state = vehicle_data[8] if len(vehicle_data) > 8 else None

        plate = (plate or "").strip().upper() or None
        plate_state = (plate_state or "").strip().upper() or None

        row = [
            (vin if vin else None),  # normalize '' -> None
            plate,
            plate_state,
            year,
            make,
            model,
            engine_size,
            trim,
            customer_id,
        ]

        conn = db_handlers.connect_db()
        cursor = conn.cursor()
        query = """INSERT INTO vehicles (vin, plate, plate_state, year, make, model, engine_size, trim, customer_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, row)
        conn.commit()
        cursor.close()
        conn.close()

### GETS CUSTOMER ID ###
    @staticmethod
    def get_customer_id_by_details(customer_data):
        conn = db_handlers.connect_db()
        cursor = conn.cursor()
        query = """SELECT customer_id FROM customers WHERE (
                   last_name = %s AND first_name = %s AND address = %s AND city = %s AND
                   state = %s AND zip = %s AND phone = %s AND alt_phone = %s AND email = %s)"""
        cursor.execute(query, customer_data)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] if result else None

### GETS customer_id BY VEHICLE ATTRS ###
    @staticmethod
    def get_vehicle_id_by_details(vehicle_data):
        conn = db_handlers.connect_db()
        cursor = conn.cursor()
        query = """SELECT customer_id FROM vehicles WHERE (
                    vin = %s AND year = %s AND make = %s AND model = %s AND engine_size = %s AND trim = %s)"""
        cursor.execute(query, vehicle_data)
        result = cursor.fetchone()
        conn.close()
        cursor.close()
        return result[0] if result else None

### GATHERS year, make, model AND customer_id FORM vehicles TABLE ###
    @staticmethod
    def get_all_vehicles():
        conn = db_handlers.connect_db()
        cursor = conn.cursor()
        query = """Select year, make, model, customer_id, vin, id FROM vehicles"""
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result if result else None

### GETS ALL VEHICLE INFO AND CUSTOMERS LAST AND FIRST NAME TO POPULATE VehicleTable ###
    @staticmethod
    def get_all_vehicle_info():
        conn = db_handlers.connect_db()
        cursor = conn.cursor()
        query = """select vehicles.vin, vehicles.year, vehicles.make, vehicles.model, vehicles.engine_size,
                               vehicles.trim, customers.last_name, customers.first_name , vehicles.customer_id from vehicles inner join
                                customers on customers.customer_id = vehicles.customer_id order by make"""
        cursor.execute(query)
        result = cursor.fetchall()

        cursor.close()
        conn.close()

        return result if result else None

### CHANGES customer_id NUMBER TO CHANGE WHO VEHICLE BELONGS TO ###
    @staticmethod
    def change_vehicle_owner(vin, vehicle_id, customer_id):
        conn = db_handlers.connect_db()
        cursor = conn.cursor()
        query = """UPDATE vehicles SET customer_id = %s WHERE vin = %s AND customer_id = %s"""
        cursor.execute(query, (customer_id, vin, vehicle_id))
        conn.commit()

        print(f"Rows affected: {cursor.rowcount}")
        cursor.close()
        conn.close()

### DELETES VEHICLE FROM DB ###
    @staticmethod
    def delete_vehicle(vin, vehicle_id):
        conn = db_handlers.connect_db()
        cursor = conn.cursor()
        query = """DELETE FROM vehicles WHERE customer_id = %s AND vin = %s"""
        cursor.execute(query, (vehicle_id, vin))
        cursor.close()
        conn.close()


    @staticmethod
    def get_vehicles_by_customer_id(cust_id):
        conn = db_handlers.connect_db()
        cursor = conn.cursor()
        query = """SELECT vin, year, make, model, customer_id FROM vehicles WHERE customer_id = %s"""
        cursor.execute(query, (cust_id, ))
        result = cursor.fetchall()
        return result

    @staticmethod
    def get_vehicle_info_for_new_ro(vehicle_id):
        conn = db_handlers.connect_db()
        cursor = conn.cursor(dictionary=True)
        query = """SELECT vin, year, make, model, engine_size, trim, customer_id FROM vehicles WHERE id = %s
                    LIMIT 1"""
        cursor.execute(query, (vehicle_id, ))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    @staticmethod
    def find_by_vin(vin: str):
        conn = db_handlers.connect_db()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, customer_id FROM vehicles WHERE vin=%s LIMIT 1", (vin,))
            row = cur.fetchone()
            if row:
                return {"id": int(row[0]), "customer_id": int(row[1])}
            return None
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def transfer_vehicle_to_customer(vehicle_id: int, new_customer_id: int):
        conn = db_handlers.connect_db()
        try:
            cur = conn.cursor()
            cur.execute("UPDATE vehicles SET customer_id=%s WHERE id=%s", (new_customer_id, vehicle_id))
            conn.commit()
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_vehicle_by_id(vehicle_id: int):
        conn = db_handlers.connect_db()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT id, vin, year, make, model, engine_size, trim, customer_id 
                    from vehicles WHERE id = %s""", (vehicle_id, ))

            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
