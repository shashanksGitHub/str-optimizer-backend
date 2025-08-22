"""
WSGI entry point for Digital Ocean App Platform
This file ensures the Flask app can be found by gunicorn
"""

from app import app

if __name__ == "__main__":
    app.run()

# This is what gunicorn will import
application = app 