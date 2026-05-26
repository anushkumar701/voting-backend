from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os, sys
from functools import wraps
import re

load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_setup import init_database, register_user, authenticate_user, get_user_by_id, get_user_by_voter_id, get_all_voters, update_voter, delete_voter_permanently, add_election, update_election_status, get_all_elections, get_election_by_id, record_vote, has_voted, get_election_stats, get_voter_stats
from utils.blockchain_utils import blockchain
from otp_manager import OTPManager

app = Flask(__name__)
_frontend_url = os.getenv('FRONTEND_URL')
CORS(app, origins=[_frontend_url] if _frontend_url else '*')
app.config['JSON_SORT_KEYS'] = False

init_database()
otp_manager = OTPManager()

def init_blockchain():
    addr = os.getenv('CONTRACT_ADDRESS')
    if not addr and os.path.exists('contract_address.txt'):
        try:
            with open('contract_address.txt', 'r') as f:
                addr = f.read().strip()
        except:
            addr = None
    if addr:
        if blockchain.load_contract(addr):
            print(f"[Auto] Contract loaded: {addr[:10]}...")

init_blockchain()

def success(data, message="Success"):
    return jsonify({"success": True, "message": message, "data": data}), 200

def error(message, code=400):
    return jsonify({"success": False, "message": message, "data": None}), code

def sanitize_input(value):
    if not value:
        return value
    return re.sub(r'[^\w\s@._-]', '', str(value))

def require_role(roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_id = request.headers.get('X-User-ID')
            if not user_id:
                return error("Authentication required", 401)
            user = get_user_by_id(user_id)
            if not user or not user.get('is_active'):
                return error("Invalid or inactive user", 401)
            if user['role'] not in roles:
                return error(f"Access denied", 403)
            request.current_user = user
            return f(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/', methods=['GET'])
def root():
    return jsonify({"message": "E-Voting API", "version": "2.0"}), 200

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "running", "blockchain": blockchain.contract is not None}), 200

@app.route('/api/ganache-accounts', methods=['GET'])
def ganache_accounts():
    if blockchain.web3 and blockchain.web3.is_connected():
        accounts = blockchain.web3.eth.accounts[1:11]
        return success({"accounts": accounts}, "Ganache accounts")
    return error("Ganache not connected")

@app.route('/api/voter/request-otp', methods=['POST'])
def request_otp():
    data = request.get_json()
    voter_id = sanitize_input(data.get('voter_id'))
    phone = sanitize_input(data.get('phone'))
    
    if not voter_id or not phone:
        return error("voter_id and phone required")
    
    voter = get_user_by_voter_id(voter_id)
    if not voter:
        return error("Voter not found", 404)
    if voter['role'] != 'voter':
        return error("Invalid voter ID")
    if not voter.get('is_active'):
        return error("Account deactivated")
    if voter.get('phone') != phone:
        return error("Phone number mismatch")
    
    result = otp_manager.request_otp(voter_id, phone)
    if result['success']:
        return success({"expires_in_minutes": result['expires_in_minutes'], "otp_for_testing": result.get('otp_for_testing')}, result['message'])
    return error(result['message'])

@app.route('/api/voter/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    voter_id = sanitize_input(data.get('voter_id'))
    otp_code = sanitize_input(data.get('otp_code'))
    
    if not voter_id or not otp_code:
        return error("voter_id and otp_code required")
    
    result = otp_manager.verify_otp(voter_id, otp_code)
    if not result['success']:
        return error(result['message'], 401)
    
    voter = get_user_by_voter_id(voter_id)
    if not voter:
        return error("Voter not found", 404)
    
    voter.pop('password', None)
    return success(voter, "Login successful")

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = sanitize_input(data.get('email'))
    password = data.get('password')
    
    if not email or not password:
        return error("Email and password required")
    
    user = authenticate_user(email, password)
    if not user:
        return error("Invalid credentials", 401)
    if user['role'] == 'voter':
        return error("Voters must use OTP login")
    
    return success(user, f"Login successful")

@app.route('/api/admin/stats', methods=['GET'])
@require_role(['admin'])
def admin_stats():
    return success(get_election_stats(), "Stats retrieved")

@app.route('/api/admin/create-election', methods=['POST'])
@require_role(['admin'])
def create_election():
    data = request.get_json()
    name = sanitize_input(data.get('name'))
    description = sanitize_input(data.get('description', ''))
    candidates = [sanitize_input(c) for c in data.get('candidates', [])]
    
    if not name or len(candidates) < 2:
        return error("Name and at least 2 candidates required")
    if not blockchain.contract:
        return error("Contract not loaded", 503)
    
    import random
    election_id = random.randint(1000, 999999)
    
    bc_result = blockchain.create_election(election_id, candidates)
    if not bc_result['success']:
        return error(bc_result['message'], 500)
    
    db_result = add_election(election_id, name, description, candidates, blockchain.contract_address)
    if not db_result['success']:
        return error(db_result['message'])
    
    return success({"election_id": election_id, "tx_hash": bc_result['tx_hash']}, "Election created")

@app.route('/api/admin/activate-election/<int:election_id>', methods=['POST'])
@require_role(['admin'])
def activate_election(election_id):
    election = get_election_by_id(election_id)
    if not election:
        return error("Election not found", 404)
    if election['status'] != 'CREATED':
        return error("Only CREATED elections can be activated")
    
    bc_result = blockchain.activate_election(election_id)
    if not bc_result['success']:
        return error(bc_result['message'], 500)
    
    update_election_status(election_id, 'ACTIVE')
    return success({"election_id": election_id, "tx_hash": bc_result['tx_hash']}, "Election activated")

@app.route('/api/admin/close-election/<int:election_id>', methods=['POST'])
@require_role(['admin'])
def close_election(election_id):
    election = get_election_by_id(election_id)
    if not election:
        return error("Election not found", 404)
    if election['status'] != 'ACTIVE':
        return error("Only ACTIVE elections can be closed")
    
    bc_result = blockchain.close_election(election_id)
    if not bc_result['success']:
        return error(bc_result['message'], 500)
    
    update_election_status(election_id, 'CLOSED')
    return success({"election_id": election_id, "tx_hash": bc_result['tx_hash']}, "Election closed")

@app.route('/api/admin/archive-election/<int:election_id>', methods=['POST'])
@require_role(['admin'])
def archive_election(election_id):
    election = get_election_by_id(election_id)
    if not election:
        return error("Election not found", 404)
    if election['status'] != 'CLOSED':
        return error("Only CLOSED elections can be archived")
    
    update_election_status(election_id, 'ARCHIVED')
    return success({"election_id": election_id}, "Election archived")

@app.route('/api/admin/elections', methods=['GET'])
@require_role(['admin'])
def admin_elections():
    elections = get_all_elections()
    for e in elections:
        e['total_votes'] = 0
        e['candidates_with_votes'] = []
        if blockchain.contract:
            bc_result = blockchain.get_results(e['election_id'])
            if bc_result['success']:
                e['total_votes'] = bc_result['total_votes']
                e['candidates_with_votes'] = [{"name": e['candidates'][i], "votes": bc_result['votes'][i]} for i in range(len(e['candidates']))]
    return success({"elections": elections, "count": len(elections)}, "Elections retrieved")

@app.route('/api/officer/stats', methods=['GET'])
@require_role(['officer'])
def officer_stats():
    return success(get_voter_stats(), "Stats retrieved")

@app.route('/api/officer/voters', methods=['GET'])
@require_role(['officer'])
def get_voters():
    voters = get_all_voters()
    return success({"voters": voters, "count": len(voters)}, "Voters retrieved")

@app.route('/api/officer/add-voter', methods=['POST'])
@require_role(['officer'])
def add_voter():
    data = request.get_json()
    result = register_user(sanitize_input(data.get('user_id')), sanitize_input(data.get('name')), sanitize_input(data.get('email')), 'voter123', 'voter', sanitize_input(data.get('phone')), sanitize_input(data.get('ethereum_address')))
    if not result['success']:
        return error(result['message'])
    return success(result, "Voter added")

@app.route('/api/officer/update-voter/<user_id>', methods=['PUT'])
@require_role(['officer'])
def update_voter_route(user_id):
    data = request.get_json()
    result = update_voter(user_id, sanitize_input(data.get('name')), sanitize_input(data.get('email')), sanitize_input(data.get('phone')), data.get('is_active'))
    if not result['success']:
        return error(result['message'])
    return success({"user_id": user_id}, "Voter updated")

@app.route('/api/officer/delete-voter/<user_id>', methods=['DELETE'])
@require_role(['officer'])
def delete_voter(user_id):
    result = delete_voter_permanently(user_id)
    if not result['success']:
        return error(result['message'])
    return success({"user_id": user_id}, "Voter deleted")

@app.route('/api/elections', methods=['GET'])
def list_elections():
    user_id = request.headers.get('X-User-ID')
    if user_id:
        user = get_user_by_id(user_id)
        if user and user.get('is_active') and user['role'] in ['admin', 'officer']:
            return success({"elections": get_all_elections()}, "All elections")
    return success({"elections": [e for e in get_all_elections() if e['status'] == 'ACTIVE']}, "Active elections")

@app.route('/api/election/<int:election_id>', methods=['GET'])
def get_election(election_id):
    election = get_election_by_id(election_id)
    if not election:
        return error("Election not found", 404)
    return success(election, "Election retrieved")

@app.route('/api/voter/check-vote-status/<int:election_id>', methods=['GET'])
@require_role(['voter'])
def check_vote_status(election_id):
    voter = request.current_user
    if not voter.get('ethereum_address'):
        return error("Voter ethereum address not configured")
    return success({"has_voted": has_voted(election_id, voter['ethereum_address'])}, "Status retrieved")

@app.route('/api/cast-vote', methods=['POST'])
@require_role(['voter'])
def cast_vote():
    data = request.get_json()
    election_id = data.get('election_id')
    candidate_index = data.get('candidate_index')
    
    voter = request.current_user
    if not voter.get('ethereum_address'):
        return error("Voter ethereum address not configured")
    
    election = get_election_by_id(election_id)
    if not election:
        return error("Election not found", 404)
    if election['status'] != 'ACTIVE':
        return error("Election not active")
    if candidate_index is None or candidate_index >= len(election['candidates']):
        return error("Invalid candidate")
    if has_voted(election_id, voter['ethereum_address']):
        return error("Already voted")
    
    bc_result = blockchain.cast_vote(election_id, candidate_index, voter['ethereum_address'])
    if not bc_result['success']:
        return error(bc_result['message'])
    
    record_vote(election_id, voter['ethereum_address'], bc_result['tx_hash'])
    return success({"tx_hash": bc_result['tx_hash']}, "Vote recorded")

@app.route('/api/load-contract', methods=['POST'])
def load_contract():
    data = request.get_json()
    contract_address = data.get('contract_address')
    if not contract_address:
        return error("contract_address required")
    if not blockchain.load_contract(contract_address):
        return error("Failed to load contract")
    try:
        with open('contract_address.txt', 'w') as f:
            f.write(blockchain.contract_address)
    except:
        pass
    return success({"contract_address": blockchain.contract_address}, "Contract loaded")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("E-VOTING SYSTEM")
    print("="*60)
    print("Admin: admin@admin.com / admin123")
    print("Officer: officer@admin.com / officer123")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
