import os
import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:5000"

def request(method, path, payload=None, headers=None):
    url = f"{BASE_URL}{path}"
    data = json.dumps(payload).encode('utf-8') if payload else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Content-Type', 'application/json')
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            return response.status, json.loads(res_body)
    except urllib.error.HTTPError as e:
        res_body = e.read().decode('utf-8')
        return e.code, json.loads(res_body)

def run_tests():
    print("\n--- Starting End-to-End System Tests ---")
    
    # 1. Health check
    status, res = request('GET', '/api/health')
    assert status == 200, f"Health check failed: {res}"
    print("✓ 1. Health Check PASSED")

    # 2. Admin Login
    status, res = request('POST', '/api/login', {"email": "admin@admin.com", "password": "admin123"})
    assert status == 200 and res['success'], f"Admin login failed: {res}"
    admin_id = res['data']['user_id']
    admin_headers = {'X-User-ID': admin_id}
    print(f"✓ 2. Admin Login PASSED (User ID: {admin_id})")

    # 3. Admin Stats
    status, res = request('GET', '/api/admin/stats', headers=admin_headers)
    assert status == 200 and res['success'], f"Admin stats failed: {res}"
    print(f"✓ 3. Admin Stats PASSED ({res['data']})")

    # 4. Officer Login
    status, res = request('POST', '/api/login', {"email": "officer@admin.com", "password": "officer123"})
    assert status == 200 and res['success'], f"Officer login failed: {res}"
    officer_id = res['data']['user_id']
    officer_headers = {'X-User-ID': officer_id}
    print(f"✓ 4. Officer Login PASSED (User ID: {officer_id})")

    # 5. Generate Eth Address
    status, res = request('GET', '/api/generate-eth-address')
    assert status == 200 and res['success'], f"Eth address generation failed: {res}"
    voter_eth_addr = res['data']['address']
    print(f"✓ 5. Eth Address Generation PASSED ({voter_eth_addr[:10]}...)")

    # 6. Officer Add Voter
    voter_id = "V100"
    voter_phone = "555-9999"
    status, res = request('POST', '/api/officer/add-voter', {
        "user_id": voter_id,
        "name": "Test Voter 100",
        "email": "voter100@test.com",
        "phone": voter_phone,
        "ethereum_address": voter_eth_addr
    }, headers=officer_headers)
    assert status == 200 and res['success'], f"Add voter failed: {res}"
    print("✓ 6. Officer Add Voter PASSED")

    # 7. Voter Request OTP
    status, res = request('POST', '/api/voter/request-otp', {"voter_id": voter_id, "phone": voter_phone})
    assert status == 200 and res['success'], f"Request OTP failed: {res}"
    otp_code = res['data']['otp_for_testing']
    print(f"✓ 7. Voter Request OTP PASSED (OTP: {otp_code})")

    # 8. Voter Verify OTP
    status, res = request('POST', '/api/voter/verify-otp', {"voter_id": voter_id, "otp_code": otp_code})
    assert status == 200 and res['success'], f"Verify OTP failed: {res}"
    voter_headers = {'X-User-ID': voter_id}
    print("✓ 8. Voter Verify OTP PASSED")

    # 9. Admin Create Election
    status, res = request('POST', '/api/admin/create-election', {
        "name": "General Election 2026",
        "description": "National Election Test",
        "candidates": ["Alice (Progressive)", "Bob (Conservative)", "Charlie (Independent)"]
    }, headers=admin_headers)
    assert status == 200 and res['success'], f"Create election failed: {res}"
    election_id = res['data']['election_id']
    print(f"✓ 9. Admin Create Election PASSED (Election ID: {election_id})")

    # 10. Admin Activate Election
    status, res = request('POST', f'/api/admin/activate-election/{election_id}', headers=admin_headers)
    assert status == 200 and res['success'], f"Activate election failed: {res}"
    print("✓ 10. Admin Activate Election PASSED")

    # 11. Voter Check Vote Status
    status, res = request('GET', f'/api/voter/check-vote-status/{election_id}', headers=voter_headers)
    assert status == 200 and not res['data']['has_voted'], f"Check vote status failed: {res}"
    print("✓ 11. Voter Check Vote Status PASSED (Has not voted yet)")

    # 12. Voter Cast Vote
    status, res = request('POST', '/api/cast-vote', {
        "election_id": election_id,
        "candidate_index": 0
    }, headers=voter_headers)
    assert status == 200 and res['success'], f"Cast vote failed: {res}"
    print(f"✓ 12. Voter Cast Vote PASSED (Tx Hash: {res['data']['tx_hash'][:12]}...)")

    # 13. Verify Double Voting Blocked
    status, res = request('POST', '/api/cast-vote', {
        "election_id": election_id,
        "candidate_index": 1
    }, headers=voter_headers)
    assert status == 400 and not res['success'], f"Double voting protection failed: {res}"
    print("✓ 13. Double Voting Blocked PASSED")

    # 14. Admin Tally Check
    status, res = request('GET', '/api/admin/elections', headers=admin_headers)
    assert status == 200 and res['success'], f"Get elections failed: {res}"
    target_election = next((e for e in res['data']['elections'] if e['election_id'] == election_id), None)
    assert target_election and target_election['total_votes'] == 1, f"Tally check failed: {target_election}"
    print(f"✓ 14. Real-time Tally PASSED (Total Votes: {target_election['total_votes']})")

    # 15. Admin Close Election
    status, res = request('POST', f'/api/admin/close-election/{election_id}', headers=admin_headers)
    assert status == 200 and res['success'], f"Close election failed: {res}"
    print("✓ 15. Admin Close Election PASSED")

    # 16. Admin Delete/Cancel Test Election
    status, res = request('DELETE', f'/api/admin/delete-election/{election_id}', headers=admin_headers)
    assert status == 200 and res['success'], f"Delete election failed: {res}"
    print("✓ 16. Admin Delete Election Endpoint PASSED")

    print("\n🎉 ALL 16 E2E SYSTEM TESTS PASSED PERFECTLY!\n")

if __name__ == '__main__':
    run_tests()
