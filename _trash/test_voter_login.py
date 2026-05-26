import requests

print('Testing voter login system...')

# Test health
try:
    r = requests.get('http://localhost:5000/api/health', timeout=5)
    print('✓ Health check passed - Status:', r.status_code)
except Exception as e:
    print('✗ Health check failed:', e)
    exit(1)

# Test voter OTP request
print('\nTesting OTP request for Senjan (SEN001)...')
try:
    response = requests.post('http://localhost:5000/api/voter/request-otp',
                           json={'voter_id': 'SEN001', 'mobile': '9876543210'},
                           timeout=10)
    print('OTP Request - Status:', response.status_code)
    if response.status_code == 200:
        data = response.json()
        print('Success:', data.get('success'))
        if data.get('success'):
            otp_code = data.get('data', {}).get('otp')
            print('✓ OTP Generated:', otp_code)
            print('Expires in:', data.get('data', {}).get('expires_in'), 'seconds')

            # Test OTP verification
            print('\nTesting OTP verification...')
            verify_response = requests.post('http://localhost:5000/api/voter/verify-otp',
                                          json={'voter_id': 'SEN001', 'otp_code': otp_code},
                                          timeout=10)
            print('OTP Verify - Status:', verify_response.status_code)
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                print('✓ OTP Verification Success:', verify_data.get('success'))
                if verify_data.get('success'):
                    print('✓ Voter login successful!')
                else:
                    print('✗ OTP verification failed:', verify_data.get('message'))
            else:
                print('✗ OTP verification request failed')
        else:
            print('✗ OTP request failed:', data.get('message'))
    else:
        print('✗ OTP request failed with status:', response.status_code)
        print('Response:', response.text)

except Exception as e:
    print('✗ OTP test error:', e)