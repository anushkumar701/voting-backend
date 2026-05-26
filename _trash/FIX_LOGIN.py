import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'voting.db')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

print("\n" + "="*60)
print("FIXING LOGIN CREDENTIALS")
print("="*60)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Delete ALL admin/officer accounts
c.execute("DELETE FROM users WHERE role IN ('admin', 'officer')")
conn.commit()

print("\n✓ Deleted old accounts")

# Create fresh admin
admin_pass = hash_password('admin123')
c.execute("""
INSERT INTO users (user_id, name, email, password, role, is_active)
VALUES (?, ?, ?, ?, ?, 1)
""", ('ADMIN001', 'System Admin', 'admin@admin.com', admin_pass, 'admin'))

print("✓ Created admin account")

# Create fresh officer
officer_pass = hash_password('officer123')
c.execute("""
INSERT INTO users (user_id, name, email, password, role, is_active)
VALUES (?, ?, ?, ?, ?, 1)
""", ('OFFICER001', 'Election Officer', 'officer@admin.com', officer_pass, 'officer'))

print("✓ Created officer account")

conn.commit()

# TEST the login
print("\n" + "="*60)
print("TESTING LOGIN")
print("="*60)

# Test admin
c.execute("""
SELECT user_id, email, role FROM users 
WHERE email='admin@admin.com' AND password=? AND is_active=1
""", (admin_pass,))
admin_test = c.fetchone()

# Test officer  
c.execute("""
SELECT user_id, email, role FROM users 
WHERE email='officer@admin.com' AND password=? AND is_active=1
""", (officer_pass,))
officer_test = c.fetchone()

if admin_test:
    print(f"✓ Admin login: WORKING ({admin_test[0]})")
else:
    print("✗ Admin login: FAILED")

if officer_test:
    print(f"✓ Officer login: WORKING ({officer_test[0]})")
else:
    print("✗ Officer login: FAILED")

conn.close()

print("\n" + "="*60)
print("LOGIN CREDENTIALS")
print("="*60)
print("\nAdmin:   admin@admin.com / admin123")
print("Officer: officer@admin.com / officer123")
print("\n" + "="*60 + "\n")
