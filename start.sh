#!/bin/bash

echo "🎭 Installing Playwright browsers - AGGRESSIVE MODE..."

# CRITICAL: Set Playwright to use system-wide installation
export PLAYWRIGHT_BROWSERS_PATH=/workspace/.cache/ms-playwright
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0

# Create necessary directories
mkdir -p /workspace/.cache/ms-playwright
mkdir -p /tmp/playwright-browsers

echo "🎭 Step 1: Install Playwright browsers with maximum verbosity..."
python -m playwright install chromium --verbose --force

echo "🎭 Step 2: Verify and retry if needed..."
if [ ! -f "/workspace/.cache/ms-playwright/chromium-*/chrome-linux/chrome" ]; then
    echo "🔄 First attempt failed, trying alternative installation..."
    
    # Try with different environment settings
    export PLAYWRIGHT_BROWSERS_PATH=/tmp/playwright-browsers
    python -m playwright install chromium --verbose --force
    
    # If still fails, try installing system dependencies
    echo "🔄 Installing system dependencies..."
    apt-get update || true
    apt-get install -y wget unzip || true
    
    # Manual Chromium download as last resort
    echo "🔄 Manual Chromium installation..."
    python -c "
import subprocess
import os
try:
    # Force reinstall with system deps
    result = subprocess.run(['python', '-m', 'playwright', 'install-deps', 'chromium'], capture_output=True, text=True)
    print(f'Install deps result: {result.returncode}')
    print(f'Install deps output: {result.stdout}')
    print(f'Install deps errors: {result.stderr}')
    
    result = subprocess.run(['python', '-m', 'playwright', 'install', 'chromium', '--force'], capture_output=True, text=True)
    print(f'Install result: {result.returncode}')
    print(f'Install output: {result.stdout}')
    print(f'Install errors: {result.stderr}')
except Exception as e:
    print(f'Manual installation error: {e}')
"
fi

echo "🔍 FINAL VERIFICATION..."
python -c "
import os
import glob
from playwright.sync_api import sync_playwright

print('=== PLAYWRIGHT INSTALLATION VERIFICATION ===')

# Check all possible locations
locations = [
    '/workspace/.cache/ms-playwright',
    '/tmp/playwright-browsers', 
    '~/.cache/ms-playwright',
    '/root/.cache/ms-playwright'
]

for loc in locations:
    expanded_loc = os.path.expanduser(loc)
    print(f'Checking location: {expanded_loc}')
    if os.path.exists(expanded_loc):
        files = glob.glob(f'{expanded_loc}/**/*', recursive=True)
        print(f'  Found {len(files)} files')
        chrome_files = [f for f in files if 'chrome' in f.lower() and 'linux' in f]
        print(f'  Chrome-related files: {len(chrome_files)}')
        for cf in chrome_files[:3]:
            print(f'    {cf}')
    else:
        print(f'  Location does not exist')

print('\\n=== PLAYWRIGHT API TEST ===')
try:
    with sync_playwright() as p:
        browser_path = p.chromium.executable_path
        print(f'Chromium executable path: {browser_path}')
        print(f'File exists: {os.path.exists(browser_path)}')
        if os.path.exists(browser_path):
            print(f'File size: {os.path.getsize(browser_path)} bytes')
            print('✅ CHROMIUM READY!')
        else:
            print('❌ CHROMIUM EXECUTABLE MISSING!')
except Exception as e:
    print(f'❌ Playwright test failed: {e}')
    import traceback
    traceback.print_exc()
"

echo "🚀 Starting application..."
exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --timeout 120 wsgi:application 