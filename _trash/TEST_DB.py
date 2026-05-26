import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'voting.db')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

print("\n" + "="*60)
print("DATABASE CHECK")
print("="*60)

# Check what's in the database
c.execute("SELECT user_id, email, role, is_active FROM users WHERE role IN ('admin', 'officer')")
users = c.fetchall()

print("\nCurrent users in database:")
for user in users:
    print(f"  {user[0]} | {user[1]} | {user[2]} | Active: {user[3]}")

print("\n" + "="*60)
print("TESTING LOGIN")
print("="*60)

# Test admin login
test_email = 'admin@admin.com'
test_pass = hash_password('admin123')

c.execute("""
SELECT user_id, email, role, password, is_active FROM users 
WHERE email=?
""", (test_email,))

result = c.fetchone()

if result:
    print(f"\n✓ Found user: {result[0]} | {result[1]} | {result[2]}")
    print(f"  Active: {result[4]}")
    print(f"  Password hash matches: {result[3] == test_pass}")
    
    # Try full login query
    c.execute("""
    SELECT * FROM users WHERE email=? AND password=? AND is_active=1
    """, (test_email, test_pass))
    
    login_test = c.fetchone()
    if login_test:
        print("\n  ✓✓ LOGIN WOULD WORK!")
    else:
        print("\n  ✗✗ LOGIN WOULD FAIL!")
        print("  Checking why...")
        if result[4] == 0:
            print("  → User is not active")
        if result[3] != test_pass:
            print("  → Password hash doesn't match")
            print(f"     Expected: {test_pass}")
            print(f"     Got:      {result[3]}")
else:
    print(f"\n✗ User {test_email} NOT FOUND in database!")

conn.close()

print("\n" + "="*60 + "\n")
