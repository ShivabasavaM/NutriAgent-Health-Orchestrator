import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

try:
    db_pool = pool.SimpleConnectionPool(1, 10, DB_URL)
    print("✅ PostgreSQL Connection Pool Initialized.")
except Exception as e:
    print(f"❌ Connection Pool Error: {e}")
    db_pool = None

def get_connection():
    """Fetches a connection from the pool."""
    if db_pool:
        return db_pool.getconn()
    return None

def release_connection(conn):
    """Returns the connection to the pool."""
    if db_pool and conn:
        db_pool.putconn(conn)

def init_db():
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        access_token TEXT,
        refresh_token TEXT,
        expires_at REAL,
        height REAL,
        weight REAL,
        goal TEXT,
        daily_calorie_target INTEGER,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- ⏱️ Added for Token Guard
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_logs (
        id SERIAL PRIMARY KEY,
        date DATE DEFAULT CURRENT_DATE,
        user_id INTEGER REFERENCES users(id),
        food_name TEXT,
        calories_in INTEGER
    )
    """)

    cursor.execute("INSERT INTO users (id) VALUES (1) ON CONFLICT (id) DO NOTHING")
    conn.commit()
    cursor.close()
    release_connection(conn)

def update_tokens(access_token, refresh_token, expires_at):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET access_token = %s, refresh_token = %s, expires_at = %s WHERE id = 1", 
                   (access_token, refresh_token, expires_at))
    conn.commit()
    cursor.close()
    release_connection(conn)

def get_tokens():
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT access_token, refresh_token, expires_at FROM users WHERE id=1")
    row = cursor.fetchone()
    cursor.close()
    release_connection(conn)
    
    if row and row['access_token']:
         return {"access_token": row['access_token'], "refresh_token": row['refresh_token'], "expires_at": row['expires_at']}
    return None

def mark_user_active():
    """Updates the last_active timestamp (Feedback Point 5)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE id = 1")
    conn.commit()
    cursor.close()
    release_connection(conn)