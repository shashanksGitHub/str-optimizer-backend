#!/bin/bash

echo "🎭 Installing Playwright browsers..."

# Set environment variables for Playwright
export PLAYWRIGHT_BROWSERS_PATH=/tmp/playwright-browsers

# Create browsers directory
mkdir -p $PLAYWRIGHT_BROWSERS_PATH

# Install playwright browsers without system dependencies first
echo "🎭 Installing Chromium browser (minimal)..."
python -m playwright install chromium || echo "❌ Playwright install failed"

# If that fails, try with --with-deps
if [ ! -d "$PLAYWRIGHT_BROWSERS_PATH" ] || [ -z "$(ls -A $PLAYWRIGHT_BROWSERS_PATH 2>/dev/null)" ]; then
    echo "🎭 Trying Chromium install with deps..."
    python -m playwright install chromium --with-deps || echo "❌ Playwright with deps failed"
fi

# Verify installation
echo "🔍 Checking Playwright installation..."
python -m playwright --version || echo "❌ Playwright not available"

# Check if chromium is installed and where
echo "🔍 Checking Chromium installation..."
python -c "
import os
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        try:
            browser_path = p.chromium.executable_path
            print(f'✅ Chromium found at: {browser_path}')
            print(f'✅ File exists: {os.path.exists(browser_path)}')
        except Exception as e:
            print(f'❌ Chromium executable check failed: {e}')
            
        # Try to launch browser to test
        try:
            browser = p.chromium.launch()
            print('✅ Chromium can be launched successfully')
            browser.close()
        except Exception as e:
            print(f'❌ Chromium launch test failed: {e}')
            
except Exception as e:
    print(f'❌ Playwright import failed: {e}')
" || echo "❌ Chromium verification script failed"

# List what's in the playwright cache
echo "🔍 Checking playwright cache contents..."
ls -la /root/.cache/ms-playwright/ 2>/dev/null || echo "No playwright cache found"
ls -la /tmp/playwright-browsers/ 2>/dev/null || echo "No tmp playwright browsers found"

echo "🚀 Starting application..."
# Start the application
exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --timeout 120 wsgi:application 