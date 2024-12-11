# MOJIZA/engine/database.py

import sqlite3
from contextlib import contextmanager

DB_NAME = 'mojiza.db'

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Foydalanuvchilar jadvalini yaratish
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        print("Database initialized and 'users' table ensured.")
