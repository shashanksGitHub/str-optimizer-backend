#!/bin/bash

# Install playwright browsers if needed
python -m playwright install chromium --with-deps || echo "Playwright install failed, continuing..."

# Start the application
exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --timeout 120 wsgi:application 