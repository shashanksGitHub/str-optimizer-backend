#!/usr/bin/env python3
"""
STR Optimizer Backend Startup Script
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import and run the Flask app
from app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print(f"🚀 Starting STR Optimizer Backend...")
    print(f"📍 Server: {host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"🌍 Environment: {os.environ.get('FLASK_ENV', 'development')}")
    
    app.run(host=host, port=port, debug=debug) 