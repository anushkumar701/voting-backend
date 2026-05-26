import sqlite3
import os
db_path = os.path.join('database', 'voting.db')
print('Checking database...')
try:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    count = c.fetchone()[0]
    print(f'Users in database: {count}')
    c.execute("SELECT email, role FROM users WHERE role IN ('admin', 'officer')")
    admins = c.fetchall()
    print('Admins:', admins)
    conn.close()
    print('Database OK')
except Exception as e:
    print('Database error:', e)