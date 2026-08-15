import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from server import app as flask_app
    app = flask_app
except Exception as e:
    import traceback
    error_trace = traceback.format_exc()
    
    def error_app(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/plain; charset=utf-8')]
        start_response(status, headers)
        return [f"WSGI Startup Error:\n{error_trace}".encode('utf-8')]
    
    app = error_app
