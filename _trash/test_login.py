import requests
import time

print('Testing login API...')
start = time.time()

try:
    response = requests.post(
        'http://localhost:5000/api/login',
        json={'email': 'admin@admin.com', 'password': 'admin123'},
        timeout=15
    )
    end = time.time()
    print(f'Request completed in {end-start:.2f} seconds')
    print(f'Status: {response.status_code}')
    print(f'Response: {response.json()}')
except requests.exceptions.Timeout:
    end = time.time()
    print(f'Request timed out after {end-start:.2f} seconds')
except Exception as e:
    end = time.time()
    print(f'Error after {end-start:.2f} seconds: {e}')