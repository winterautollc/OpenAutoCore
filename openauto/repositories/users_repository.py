# repositories/users_repository.py
from __future__ import annotations
import bcrypt
from openauto.repositories.db_handlers import connect_db
import secrets
from datetime import timedelta, datetime

class UsersRepository:
    # -------- bcrypt helpers --------
    @staticmethod
    def hash_password(plain: str) -> str:
        return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")



    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
        except Exception:
            return False



    ### QUERIES ###
    @classmethod
    def create_user(cls, *, username: str, email: str, password_plain: str,
                    user_type: str, first_name: str="", last_name: str="", phone: str="") -> int:
        pw_hash = cls.hash_password(password_plain)
        sql = """
            INSERT INTO users (username, email, password_hash, user_type, first_name, last_name, phone, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """
        conn = connect_db()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (username, email, pw_hash, user_type, first_name, last_name, phone))
                user_id = cur.lastrowid
                cur.execute("INSERT IGNORE INTO user_settings (user_id, theme) VALUES (%s, 'light')", (user_id,))
            conn.commit()
            return user_id
        except:
            conn.rollback()
            raise
        finally:
            conn.close()

    @classmethod
    def get_by_username_or_email(cls, user_or_email: str) -> dict | None:
        sql = """
            SELECT id, username, email, password_hash, user_type, first_name, last_name, phone, created_at
            FROM users
            WHERE username = %s OR email = %s
            LIMIT 1
        """
        conn = connect_db()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (user_or_email, user_or_email))
                return cur.fetchone()
        finally:
            conn.close()

    @classmethod
    def verify_credentials(cls, user_or_email: str, password_plain: str) -> dict | None:
        user = cls.get_by_username_or_email(user_or_email)
        if not user:
            return None
        return user if cls.verify_password(password_plain, user["password_hash"]) else None


    @classmethod
    def get_theme(cls, user_id: int) -> str:
        conn = connect_db()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT theme FROM user_settings WHERE user_id=%s LIMIT 1", (user_id,))
                row = cur.fetchone()
                return (row[0] if row and row[0] else "light")
        finally:
            conn.close()

    @classmethod
    def set_theme(cls, user_id: int, theme: str) -> None:
        conn = connect_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO user_settings (user_id, theme)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE theme = VALUES(theme)
                    """,
                    (user_id, theme),
                )
            conn.commit()
        finally:
            conn.close()

    @classmethod
    def create_persistent_session(cls, user_id: int, days: int = 30) -> str:
        token = secrets.token_hex(32)
        conn = connect_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO user_sessions (token, user_id, expires_at) VALUES (%s, %s, NOW() + INTERVAL %s DAY)",
                    (token, user_id, days),
                )
            conn.commit()
            return token
        finally:
            conn.close()

    @classmethod
    def get_user_by_token(cls, token: str) -> dict | None:
        conn = connect_db()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    """
                    SELECT u.*
                    FROM user_sessions s
                    JOIN users u ON u.id = s.user_id
                    WHERE s.token=%s AND (s.expires_at IS NULL OR s.expires_at > NOW())
                    LIMIT 1
                    """,
                    (token,),
                )
                return cur.fetchone()
        finally:
            conn.close()

    @classmethod
    def delete_token(cls, token: str) -> None:
        conn = connect_db()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM user_sessions WHERE token=%s", (token,))
            conn.commit()
        finally:
            conn.close()



    @staticmethod
    def list_writers_and_managers():
        query = """
            SELECT id, first_name, last_name, user_type
            FROM users
            WHERE user_type IN ('writer','manager')
            ORDER BY user_type, first_name, last_name
        """
        conn = connect_db()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(query)
            return list(cur.fetchall() or [])


### RETURNS ID, FIRST_NAME: 'JANE', LAST_NAME: 'DOE' ####
    @staticmethod
    def list_by_role(role: str):
        query = "SELECT id, first_name, last_name FROM users WHERE user_type = %s ORDER BY first_name, last_name"
        conn = connect_db()
        with conn.cursor(dictionary=True) as cur:
            cur.execute(query, (role,))
            return list(cur.fetchall() or [])