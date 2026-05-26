import sys
import os

print("\n" + "="*60)
print("E-VOTING SYSTEM - STARTUP CHECK")
print("="*60 + "\n")

checks_passed = 0
checks_total = 5

# Check 1: Ganache
try:
    from web3 import Web3
    web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
    if web3.is_connected():
        print("✓ [1/5] Ganache connected on port 7545")
        accounts = web3.eth.accounts
        print(f"        Found {len(accounts)} accounts")
        checks_passed += 1
    else:
        print("✗ [1/5] Ganache NOT connected")
        print("        ACTION: Start Ganache on port 7545")
except:
    print("✗ [1/5] Ganache check failed")
    print("        ACTION: Start Ganache")

# Check 2: Contract ABI
abi_path = 'contracts/SecureVoting_ABI.json'
if os.path.exists(abi_path):
    print(f"✓ [2/5] Contract ABI found: {abi_path}")
    checks_passed += 1
else:
    print(f"✗ [2/5] Contract ABI NOT found")
    print(f"        ACTION: Deploy contract and save ABI to {abi_path}")

# Check 3: Database
db_path = 'database/voting.db'
if os.path.exists(db_path):
    print(f"✓ [3/5] Database found: {db_path}")
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
    admin_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='voter'")
    voter_count = cursor.fetchone()[0]
    conn.close()
    print(f"        Admins: {admin_count}, Voters: {voter_count}")
    checks_passed += 1
else:
    print(f"✗ [3/5] Database NOT found")
    print(f"        ACTION: Will be created on first run")

# Check 4: Dependencies
try:
    import flask
    import flask_cors
    import web3
    print("✓ [4/5] Python dependencies installed")
    checks_passed += 1
except ImportError as e:
    print("✗ [4/5] Missing dependencies")
    print(f"        ACTION: pip install -r requirements.txt")

# Check 5: Frontend
if os.path.exists('frontend/package.json'):
    print("✓ [5/5] Frontend found")
    checks_passed += 1
else:
    print("✗ [5/5] Frontend NOT found")
    print("        ACTION: Check frontend directory")

print("\n" + "="*60)
print(f"RESULT: {checks_passed}/{checks_total} checks passed")
print("="*60 + "\n")

if checks_passed == checks_total:
    print("✅ READY TO START")
    print("\nNext steps:")
    print("1. Ensure contract is deployed in Ganache")
    print("2. Load contract: python -c \"from utils.blockchain_utils import blockchain; blockchain.load_contract('0xYOUR_ADDRESS')\"")
    print("3. Run: START.bat")
elif checks_passed >= 3:
    print("⚠️  MOSTLY READY - Fix warnings above")
else:
    print("❌ NOT READY - Fix errors above")

print("\n" + "="*60 + "\n")
