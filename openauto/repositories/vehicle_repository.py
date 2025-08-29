from openauto.repositories import db_handlers



### ADDS VEHICLE TO DATABASE ###
class VehicleRepository:
    @staticmethod
    def insert_vehicle(vehicle_data):
        conn = db_handlers.connect_db()
        cursor = conn.cursor()
        query = """INSERT INTO vehicles (vin, year, make, model, engine_size, trim, customer_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, vehicle_data)
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
        query = """Select year, make, model, customer_id, vin FROM vehicles"""
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