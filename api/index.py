import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import app
except Exception as e:
    import traceback
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    error_message = str(e)
    error_traceback = traceback.format_exc()
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def catch_all(path):
        return jsonify({
            "error": "Initialization failed in api/index.py",
            "message": error_message,
            "traceback": error_traceback
        }), 500
