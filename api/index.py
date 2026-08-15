import os
import sys

# Add root directory to python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Export WSGI application for Vercel Serverless Functions
app = app
