import sqlite3
import hashlib

DB_NAME = "users.db"

def create_user_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            full_name TEXT,
            password TEXT,
            role TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_user(username, full_name, password, role):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    try:
        c.execute(
            "INSERT INTO users (username, full_name, password, role) VALUES (?,?,?,?)",
            (username, full_name, hashed_pw, role)
        )
        conn.commit()
        success = True
    except:
        success = False
    conn.close()
    return success

def validate_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    c.execute(
        "SELECT username, full_name, password, role FROM users WHERE username=? AND password=?",
        (username, hashed_pw)
    )
    user = c.fetchone()
    conn.close()
    return user
