#!/bin/bash

echo "🎭 Installing Playwright browsers..."

# Install system dependencies that might be needed
apt-get update -y || echo "apt-get update failed, continuing..."
apt-get install -y libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2 || echo "System deps install failed, continuing..."

# Install playwright browsers with verbose output
echo "🎭 Installing Chromium browser..."
python -m playwright install chromium --with-deps --verbose || echo "❌ Playwright install failed, continuing anyway..."

# Verify installation
echo "🔍 Checking Playwright installation..."
python -m playwright --version || echo "❌ Playwright not available"

# Check if chromium is installed
echo "🔍 Checking Chromium installation..."
python -c "
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser_path = p.chromium.executable_path
        print(f'✅ Chromium found at: {browser_path}')
except Exception as e:
    print(f'❌ Chromium check failed: {e}')
" || echo "❌ Chromium verification failed"

echo "🚀 Starting application..."
# Start the application
exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --timeout 120 wsgi:application 