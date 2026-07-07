import sqlite3
import os
import hashlib
import json

DB_PATH = os.path.join(os.path.dirname(__file__), 'voting.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT UNIQUE NOT NULL, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('admin', 'voter', 'officer')), phone TEXT, ethereum_address TEXT UNIQUE, registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, is_active BOOLEAN DEFAULT 1)")
    cursor.execute("CREATE TABLE IF NOT EXISTS elections (id INTEGER PRIMARY KEY AUTOINCREMENT, election_id INTEGER UNIQUE NOT NULL, name TEXT NOT NULL, description TEXT, candidates TEXT NOT NULL, contract_address TEXT, created_by TEXT DEFAULT 'admin', created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, status TEXT DEFAULT 'CREATED' CHECK(status IN ('CREATED', 'ACTIVE', 'CLOSED', 'ARCHIVED')))")
    cursor.execute("CREATE TABLE IF NOT EXISTS votes (id INTEGER PRIMARY KEY AUTOINCREMENT, election_id INTEGER NOT NULL, voter_address TEXT NOT NULL, tx_hash TEXT NOT NULL, candidate_index INTEGER DEFAULT 0, vote_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, UNIQUE(election_id, voter_address))")
    # Migration: add candidate_index to existing databases
    try:
        cursor.execute("ALTER TABLE votes ADD COLUMN candidate_index INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # Column already exists
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON users(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_role ON users(role)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_election_id ON elections(election_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_election_status ON elections(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_votes_election ON votes(election_id)")
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (user_id, name, email, password, role) VALUES (?, ?, ?, ?, ?)", ('ADMIN001', 'System Admin', 'admin@admin.com', hash_password('admin123'), 'admin'))
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='officer'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (user_id, name, email, password, role) VALUES (?, ?, ?, ?, ?)", ('OFFICER001', 'Election Officer', 'officer@admin.com', hash_password('officer123'), 'officer'))
    conn.commit()
    conn.close()

def register_user(user_id, name, email, password, role, phone=None, ethereum_address=None):
    if role not in ['admin', 'voter', 'officer']:
        return {"success": False, "message": "Invalid role"}
    if role == 'voter' and not ethereum_address:
        return {"success": False, "message": "Voter ethereum address required"}
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (user_id, name, email, password, role, phone, ethereum_address) VALUES (?, ?, ?, ?, ?, ?, ?)", (user_id, name, email, hash_password(password), role, phone, ethereum_address))
        conn.commit()
        conn.close()
        return {"success": True, "user_id": user_id}
    except sqlite3.IntegrityError as e:
        return {"success": False, "message": str(e)}

def authenticate_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=? AND password=? AND is_active=1", (email, hash_password(password)))
    row = cursor.fetchone()
    conn.close()
    if row:
        user = dict(row)
        user.pop("password", None)
        return user
    return None

def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        user = dict(row)
        user.pop("password", None)
        return user
    return None

def get_user_by_voter_id(voter_id):
    return get_user_by_id(voter_id)

def get_all_voters():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, email, phone, ethereum_address, registration_date, is_active FROM users WHERE role='voter' ORDER BY registration_date DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_voter(user_id, name=None, email=None, phone=None, is_active=None):
    updates, params = [], []
    if name is not None:
        updates.append("name=?"); params.append(name)
    if email is not None:
        updates.append("email=?"); params.append(email)
    if phone is not None:
        updates.append("phone=?"); params.append(phone)
    if is_active is not None:
        updates.append("is_active=?"); params.append(is_active)
    if not updates:
        return {"success": False, "message": "No changes"}
    params.append(user_id)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE user_id=?", params)
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        return {"success": False, "message": str(e)}

def delete_voter_permanently(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id=? AND role='voter'", (user_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        if deleted:
            return {"success": True, "message": "Voter deleted"}
        return {"success": False, "message": "Voter not found"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def add_election(election_id, name, description, candidates, contract_address):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO elections (election_id, name, description, candidates, contract_address, status) VALUES (?, ?, ?, ?, ?, 'CREATED')", (election_id, name, description, json.dumps(candidates), contract_address))
        conn.commit()
        conn.close()
        return {"success": True}
    except sqlite3.IntegrityError:
        return {"success": False, "message": "Election ID already exists"}

def update_election_status(election_id, status):
    if status not in ['CREATED', 'ACTIVE', 'CLOSED', 'ARCHIVED']:
        return {"success": False, "message": "Invalid status"}
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE elections SET status=? WHERE election_id=?", (status, election_id))
    conn.commit()
    conn.close()
    return {"success": True}

def get_all_elections():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM elections ORDER BY created_date DESC")
    rows = cursor.fetchall()
    conn.close()
    elections = []
    for r in rows:
        e = dict(r)
        e["candidates"] = json.loads(e["candidates"])
        elections.append(e)
    return elections

def get_election_by_id(election_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM elections WHERE election_id = ?", (election_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        election = dict(row)
        election["candidates"] = json.loads(election["candidates"])
        return election
    return None

def record_vote(election_id, voter_address, tx_hash, candidate_index=0):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO votes (election_id, voter_address, tx_hash, candidate_index) VALUES (?, ?, ?, ?)", (election_id, voter_address, tx_hash, candidate_index))
        conn.commit()
        conn.close()
        return {"success": True}
    except sqlite3.IntegrityError:
        return {"success": False, "message": "Already voted"}

def has_voted(election_id, voter_address):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM votes WHERE election_id=? AND voter_address=?", (election_id, voter_address))
    voted = cursor.fetchone()[0] > 0
    conn.close()
    return voted

def get_election_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM elections")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM elections WHERE status='ACTIVE'")
    active = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM votes")
    votes = cursor.fetchone()[0]
    conn.close()
    return {"total": total, "active": active, "total_votes": votes}

def get_voter_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='voter'")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='voter' AND is_active=1")
    active = cursor.fetchone()[0]
    conn.close()
    return {"total": total, "active": active, "inactive": total - active}

def get_all_votes():
    """Return all vote records for blockchain simulator state reconstruction."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT election_id, voter_address, candidate_index FROM votes")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

if __name__ == "__main__":
    init_database()
