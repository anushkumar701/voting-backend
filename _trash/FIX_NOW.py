import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'voting.db')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

print("\n=== FIXING LOGIN ===\n")

# Delete ALL old accounts
c.execute("DELETE FROM users")
conn.commit()

# Admin
c.execute("""
INSERT INTO users (user_id, name, email, password, role, is_active)
VALUES (?, ?, ?, ?, ?, 1)
""", ('ADMIN001', 'Admin', 'admin@admin.com', hash_password('admin123'), 'admin'))

# Officer
c.execute("""
INSERT INTO users (user_id, name, email, password, role, is_active)
VALUES (?, ?, ?, ?, ?, 1)
""", ('OFFICER001', 'Officer', 'officer@admin.com', hash_password('officer123'), 'officer'))

# Voter 1
c.execute("""
INSERT INTO users (user_id, name, email, password, role, phone, ethereum_address, is_active)
VALUES (?, ?, ?, ?, ?, ?, ?, 1)
""", ('VOTER001', 'Voter One', 'voter1@test.com', hash_password('voter123'), 'voter', '1234567890', '0x1234567890123456789012345678901234567890'))

# Voter 2
c.execute("""
INSERT INTO users (user_id, name, email, password, role, phone, ethereum_address, is_active)
VALUES (?, ?, ?, ?, ?, ?, ?, 1)
""", ('VOTER002', 'Voter Two', 'voter2@test.com', hash_password('voter123'), 'voter', '0987654321', '0x0987654321098765432109876543210987654321'))

conn.commit()

# Test
c.execute("SELECT email, role FROM users")
print("Created users:")
for row in c.fetchall():
    print(f"  {row[0]} - {row[1]}")

print("\nCredentials:")
print("Admin: admin@admin.com / admin123")
print("Officer: officer@admin.com / officer123")
print("Voter: VOTER001 / 1234567890 (OTP login)")

conn.close()
print("\n=== DONE ===\n")
