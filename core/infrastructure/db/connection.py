"""Database connection management"""
import sqlite3
from core.common.settings import settings


def get_db_connection():
    return sqlite3.connect(settings.db_path)

def init_database():
    # Minimal table to ensure DB exists; app.py manages full schema
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS judgments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            judgment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


