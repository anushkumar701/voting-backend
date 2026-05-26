import sqlite3
import hashlib
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'voting.db')

print("\n=== CREATING FRESH DATABASE ===\n")

# Delete old database if exists
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("✓ Deleted old database")

# Create new database
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Create tables
print("✓ Creating tables...")

c.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'voter', 'officer')),
    phone TEXT,
    ethereum_address TEXT,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
)
""")

c.execute("""
CREATE TABLE elections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    election_id INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    candidates TEXT NOT NULL,
    contract_address TEXT,
    status TEXT DEFAULT 'CREATED',
    created_by TEXT DEFAULT 'admin',
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

c.execute("""
CREATE TABLE votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    election_id INTEGER NOT NULL,
    voter_address TEXT NOT NULL,
    candidate_index INTEGER NOT NULL,
    tx_hash TEXT NOT NULL,
    vote_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(election_id, voter_address)
)
""")

c.execute("""
CREATE TABLE otps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    voter_id TEXT NOT NULL,
    otp_code TEXT NOT NULL,
    created_at REAL NOT NULL,
    expires_at REAL NOT NULL,
    is_used BOOLEAN DEFAULT 0
)
""")

c.execute("""
CREATE TABLE face_encodings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    voter_id TEXT UNIQUE NOT NULL,
    encoding TEXT NOT NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

print("✓ Tables created")

# Create credentials
print("\n=== CREATING USERS ===\n")

def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

# Admin
c.execute("""
INSERT INTO users (user_id, name, email, password, role, is_active)
VALUES (?, ?, ?, ?, ?, 1)
""", ('ADMIN001', 'System Admin', 'admin@admin.com', hash_password('admin123'), 'admin'))
print("✓ Admin: admin@admin.com / admin123")

# Officer
c.execute("""
INSERT INTO users (user_id, name, email, password, role, is_active)
VALUES (?, ?, ?, ?, ?, 1)
""", ('OFFICER001', 'Election Officer', 'officer@admin.com', hash_password('officer123'), 'officer'))
print("✓ Officer: officer@admin.com / officer123")

# Voters
voters = [
    ('VOTER001', 'John Doe', 'voter1@test.com', '1234567890', '0x1234567890123456789012345678901234567890'),
    ('VOTER002', 'Jane Smith', 'voter2@test.com', '0987654321', '0x0987654321098765432109876543210987654321'),
    ('VOTER003', 'Bob Johnson', 'voter3@test.com', '5555555555', '0x5555555555555555555555555555555555555555'),
]

for voter_id, name, email, phone, eth_addr in voters:
    c.execute("""
    INSERT INTO users (user_id, name, email, password, role, phone, ethereum_address, is_active)
    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
    """, (voter_id, name, email, hash_password('voter123'), 'voter', phone, eth_addr))
    print(f"✓ Voter: {voter_id} / {phone}")

# Create sample election
print("\n=== CREATING SAMPLE ELECTION ===\n")

c.execute("""
INSERT INTO elections (election_id, name, description, candidates, contract_address, status)
VALUES (?, ?, ?, ?, ?, ?)
""", (
    100001,
    '2026 General Election',
    'Annual general election',
    json.dumps(['Candidate A - Progressive', 'Candidate B - Democratic', 'Candidate C - Unity']),
    '0xDD3daF29B0993d4421a8277Daade72d623B76466',
    'ACTIVE'
))
print("✓ Election created (ID: 100001, Status: ACTIVE)")

conn.commit()

# Verify
print("\n=== VERIFICATION ===\n")

c.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
print(f"Admins: {c.fetchone()[0]}")

c.execute("SELECT COUNT(*) FROM users WHERE role='officer'")
print(f"Officers: {c.fetchone()[0]}")

c.execute("SELECT COUNT(*) FROM users WHERE role='voter'")
print(f"Voters: {c.fetchone()[0]}")

c.execute("SELECT COUNT(*) FROM elections WHERE status='ACTIVE'")
print(f"Active Elections: {c.fetchone()[0]}")

# Test login
print("\n=== TESTING LOGIN ===\n")

admin_hash = hash_password('admin123')
c.execute("""
SELECT user_id, email, role FROM users 
WHERE email='admin@admin.com' AND password=? AND is_active=1
""", (admin_hash,))

result = c.fetchone()
if result:
    print(f"✓✓✓ ADMIN LOGIN WORKS: {result[0]} | {result[1]} | {result[2]}")
else:
    print("✗✗✗ ADMIN LOGIN FAILED")

conn.close()

print("\n=== DATABASE READY ===\n")
print("Login Credentials:")
print("  Admin:   admin@admin.com / admin123")
print("  Officer: officer@admin.com / officer123")
print("  Voter:   VOTER001 / 1234567890 (OTP)")
print("\n")
