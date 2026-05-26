import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'voting.db')

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Check what's in database
print("\n=== CURRENT DATABASE ===")
c.execute("SELECT user_id, email, role FROM users WHERE role IN ('admin','officer')")
for row in c.fetchall():
    print(f"{row[0]} | {row[1]} | {row[2]}")

# Delete and recreate
print("\n=== FIXING ===")
c.execute("DELETE FROM users WHERE role IN ('admin','officer')")

admin_hash = hashlib.sha256('admin123'.encode()).hexdigest()
officer_hash = hashlib.sha256('officer123'.encode()).hexdigest()

c.execute("""
INSERT INTO users (user_id, name, email, password, role, is_active)
VALUES ('ADMIN001', 'Admin', 'admin@admin.com', ?, 'admin', 1)
""", (admin_hash,))

c.execute("""
INSERT INTO users (user_id, name, email, password, role, is_active)
VALUES ('OFFICER001', 'Officer', 'officer@admin.com', ?, 'officer', 1)
""", (officer_hash,))

conn.commit()

# Verify
print("\n=== VERIFICATION ===")
c.execute("""
SELECT user_id, email, password, is_active FROM users 
WHERE email='admin@admin.com'
""")
result = c.fetchone()
if result:
    print(f"Admin found: {result[0]} | {result[1]}")
    print(f"Password match: {result[2] == admin_hash}")
    print(f"Active: {result[3] == 1}")
    
    # Test actual login query
    c.execute("""
    SELECT user_id FROM users 
    WHERE email='admin@admin.com' AND password=? AND is_active=1
    """, (admin_hash,))
    
    if c.fetchone():
        print("✓✓✓ LOGIN WILL WORK ✓✓✓")
    else:
        print("✗✗✗ LOGIN WILL FAIL ✗✗✗")
else:
    print("✗ Admin NOT found!")

conn.close()
print("\n=== DONE ===\n")
