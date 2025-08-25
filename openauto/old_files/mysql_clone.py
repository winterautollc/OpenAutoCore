import os
import subprocess
import mysql.connector
from mysql.connector import errorcode

# MySQL connection info
host = "localhost"
admin_user = "openautoadmin"
admin_pass = "OpenAuto1!"
new_db = "OpenAuto"
sql_dump_file = "openauto_dump.sql"

def create_database():
    try:
        conn = mysql.connector.connect(
            host=host,
            user=admin_user,
            password=admin_pass
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {new_db}")
        print(f"[✓] Database '{new_db}' ensured.")
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"[✗] Database creation failed: {err}")
        exit(1)

def import_sql_dump():
    print("[...] Importing SQL dump...")
    command = [
        "mysql",
        f"-u{admin_user}",
        f"-p{admin_pass}",
        new_db
    ]
    try:
        with open(sql_dump_file, 'r', encoding='utf-8') as sql_file:
            result = subprocess.run(command, stdin=sql_file, shell=True)
        if result.returncode == 0:
            print(f"[✓] SQL dump imported into '{new_db}' successfully.")
        else:
            print(f"[✗] Error during SQL import.")
    except FileNotFoundError:
        print(f"[✗] SQL dump file '{sql_dump_file}' not found.")
        exit(1)

if __name__ == "__main__":
    print("[*] Starting OpenAuto DB setup...")
    create_database()
    import_sql_dump()
    print("[✓] All done.")