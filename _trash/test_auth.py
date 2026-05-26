import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'voting.db')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

print('Testing authenticate_user logic...')
email = 'admin@admin.com'
password = 'admin123'

print(f'Email: {email}')
print(f'Password: {password}')

hashed = hash_password(password)
print(f'Hashed password: {hashed}')

conn = get_db_connection()
print('Connected to database')

try:
    row = conn.execute("""
    SELECT * FROM users WHERE email=? AND password=? AND is_active=1
    """, (email, hashed)).fetchone()
    print(f'Query result: {row}')
    if row:
        u = dict(row)
        u.pop("password", None)
        print(f'User found: {u}')
    else:
        print('No user found')
except Exception as e:
    print(f'Error: {e}')
finally:
    conn.close()
    print('Connection closed')