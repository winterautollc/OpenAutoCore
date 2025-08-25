import os
from dotenv import load_dotenv
import mysql.connector





### ESTABLISH CONNECTION WITH DATABASE AND LIST AMOUNT OF ROWS FOR EACH TABLE ###

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv()

def connect_db():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_NAME"),
        connection_timeout=600,
        autocommit=True
        )


def customer_rows():
    my_db = connect_db()
    conn = my_db.cursor()
    query = "SELECT COUNT(*) FROM customers"
    conn.execute(query)
    result = conn.fetchone()
    customer_row_count = result[0]
    my_db.close()
    return customer_row_count


def vehicle_rows():
    my_db = connect_db()
    conn = my_db.cursor()
    query = "SELECT COUNT(*) FROM vehicles"
    conn.execute(query)
    result = conn.fetchone()
    vehicle_row_count = result[0]
    my_db.close()
    return vehicle_row_count

def estimate_rows():
    my_db = connect_db()
    conn = my_db.cursor()
    query = "SELECT COUNT(*) FROM repair_orders"
    conn.execute(query)
    result = conn.fetchone()
    estimate_row_count = result[0]
    my_db.close()
    return estimate_row_count