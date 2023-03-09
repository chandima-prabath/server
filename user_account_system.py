import bcrypt
import sqlite3
from datetime import datetime, timedelta
import queue
import threading

class SQLiteConnectionPool:
    def __init__(self, max_connections, db_file):
        self.max_connections = max_connections
        self.db_file = db_file
        self.connections = queue.Queue(maxsize=max_connections)

    def get_connection(self):
        if self.connections.qsize() < self.max_connections:
            conn = sqlite3.connect(self.db_file, isolation_level='EXCLUSIVE')
            self.connections.put(conn)
        else:
            conn = self.connections.get()
        return conn

    def release_connection(self, conn):
        self.connections.put(conn)

class UserAccountSystem:
    def __init__(self, db_file, max_connections=5):
        self.connection_pool = SQLiteConnectionPool(max_connections=max_connections, db_file=db_file)

        with self.connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE,
                            password TEXT,
                            password_last_changed TEXT,
                            password_expires_at TEXT,
                            is_2fa_enabled BOOLEAN)''')
            conn.commit()

    def register_user(self, username, password):
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        expires_at = (datetime.utcnow() + timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S')
        try:
            with self.connection_pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, password, password_last_changed, password_expires_at, is_2fa_enabled) VALUES (?, ?, ?, ?, ?)", (username, hashed_password, now, expires_at, False))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def authenticate_user(self, username, password):
        with self.connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=?", (username,))
            row = cursor.fetchone()
            if row is not None:
                hashed_password = row[2]
                if bcrypt.checkpw(password.encode(), hashed_password):
                    return True
            return False

    def delete_user(self, username):
        with self.connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username=?", (username,))
            conn.commit()

    def update_password(self, username, new_password):
        hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        expires_at = (datetime.utcnow() + timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S')
        with self.connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password=?, password_last_changed=?, password_expires_at=? WHERE username=?", (hashed_password, now, expires_at, username))
            conn.commit()

    def list_users(self):
        with self.connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users")
            return [row[0] for row in cursor.fetchall()]
        
    def update_username(self, current_username, new_username):
        with self.connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET username=? WHERE username=?", (new_username, current_username))
            conn.commit()
