import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock request object
class MockRequest:
    def __init__(self, json_data):
        self.method = 'POST'
        self.path = '/api/login'
        self._json_data = json_data

    def get_json(self, silent=True):
        return self._json_data

# Mock the request
import app
app.request = MockRequest({'email': 'admin@admin.com', 'password': 'admin123'})

print('Calling login function directly...')
try:
    result = app.login()
    print('Login result:', result)
except Exception as e:
    print('Error:', e)
    import traceback
    traceback.print_exc()