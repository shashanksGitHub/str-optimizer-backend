#!/bin/bash

echo "🎭 CHROMIUM INSTALLATION - DIGITAL OCEAN OPTIMIZED..."

# Set environment variables for maximum compatibility
export PLAYWRIGHT_BROWSERS_PATH=/workspace/.cache/ms-playwright
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0
export DEBIAN_FRONTEND=noninteractive

# Create directories with proper permissions
echo "📁 Creating browser directories..."
mkdir -p /workspace/.cache/ms-playwright
mkdir -p /tmp/playwright-browsers
chmod 755 /workspace/.cache/ms-playwright
chmod 755 /tmp/playwright-browsers

echo "🔧 Installing system dependencies first..."
# Install essential system dependencies
apt-get update -qq || echo "apt-get update failed"
apt-get install -y -qq \
    wget \
    curl \
    unzip \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    xvfb \
    || echo "System dependencies installation completed with some failures"

echo "🎭 Installing Playwright browsers..."
# Try multiple installation approaches
SUCCESS=false

# Approach 1: Standard installation
echo "🔄 Attempt 1: Standard Playwright install..."
if python -m playwright install chromium --verbose; then
    echo "✅ Standard installation succeeded"
    SUCCESS=true
else
    echo "❌ Standard installation failed"
fi

# Approach 2: Force installation with deps
if [ "$SUCCESS" = false ]; then
    echo "🔄 Attempt 2: Force install with system deps..."
    if python -m playwright install-deps chromium && python -m playwright install chromium --force; then
        echo "✅ Force installation succeeded"
        SUCCESS=true
    else
        echo "❌ Force installation failed"
    fi
fi

# Approach 3: Manual download
if [ "$SUCCESS" = false ]; then
    echo "🔄 Attempt 3: Manual Chromium download..."
    CHROMIUM_URL="https://playwright.azureedge.net/builds/chromium/1091/chromium-linux.zip"
    CHROMIUM_DIR="/workspace/.cache/ms-playwright/chromium-1091"
    
    mkdir -p "$CHROMIUM_DIR"
    cd "$CHROMIUM_DIR"
    
    if wget -q "$CHROMIUM_URL" -O chromium.zip; then
        if unzip -q chromium.zip; then
            if [ -f "chrome-linux/chrome" ]; then
                chmod +x chrome-linux/chrome
                echo "✅ Manual download succeeded"
                SUCCESS=true
            else
                echo "❌ Chrome executable not found after manual download"
            fi
        else
            echo "❌ Failed to unzip Chromium"
        fi
    else
        echo "❌ Failed to download Chromium"
    fi
    
    cd /workspace
fi

echo "🔍 COMPREHENSIVE VERIFICATION..."
python -c "
import os
import subprocess
from playwright.sync_api import sync_playwright

print('=== ENVIRONMENT CHECK ===')
print(f'Working directory: {os.getcwd()}')
print(f'User: {os.getenv(\"USER\", \"unknown\")}')
print(f'PATH: {os.getenv(\"PATH\", \"unknown\")}')

print('\\n=== DIRECTORY STRUCTURE ===')
for root, dirs, files in os.walk('/workspace/.cache/ms-playwright'):
    level = root.replace('/workspace/.cache/ms-playwright', '').count(os.sep)
    indent = ' ' * 2 * level
    print(f'{indent}{os.path.basename(root)}/')
    subindent = ' ' * 2 * (level + 1)
    for file in files[:5]:  # Limit to first 5 files per directory
        size = 'unknown'
        try:
            size = os.path.getsize(os.path.join(root, file))
        except:
            pass
        print(f'{subindent}{file} ({size} bytes)')
    if len(files) > 5:
        print(f'{subindent}... and {len(files) - 5} more files')

print('\\n=== PLAYWRIGHT TEST ===')
try:
    with sync_playwright() as p:
        browser_path = p.chromium.executable_path
        print(f'Expected path: {browser_path}')
        print(f'File exists: {os.path.exists(browser_path)}')
        
        if os.path.exists(browser_path):
            size = os.path.getsize(browser_path)
            print(f'File size: {size} bytes')
            
            # Test if executable
            result = subprocess.run([browser_path, '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f'Version check: {result.stdout.strip()}')
                print('🎉 CHROMIUM IS FULLY FUNCTIONAL!')
            else:
                print(f'Version check failed: {result.stderr}')
        else:
            print('❌ Chromium executable missing')
            
except Exception as e:
    print(f'❌ Playwright test error: {e}')
    import traceback
    traceback.print_exc()
"

echo "🚀 Starting application..."
exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --timeout 120 wsgi:application 