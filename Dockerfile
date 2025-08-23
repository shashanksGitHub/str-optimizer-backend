# Use browserless/chrome image with Chromium pre-installed
FROM browserless/chrome:latest

# Install Python, pip, and additional Chrome/Chromium as backup
USER root
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    chromium-browser \
    fonts-liberation \
    fonts-noto-color-emoji \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# Set up Python environment
RUN ln -sf /usr/bin/python3 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

# Set environment variables for Playwright to use system Chrome
ENV PLAYWRIGHT_BROWSERS_PATH=""
ENV PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH="/usr/bin/google-chrome"

# Set working directory
WORKDIR /workspace

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright but skip browser downloads (use system Chrome)
RUN pip install playwright==1.40.0
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

# Copy application code
COPY . .

# Verify Chrome/Chromium is available and can generate PDFs
RUN python -c "
import os
import sys
from playwright.sync_api import sync_playwright

print('=== CHROME/CHROMIUM VERIFICATION ===')

# Test multiple Chrome locations
possible_chrome_paths = [
    '/usr/bin/google-chrome',
    '/usr/bin/google-chrome-stable', 
    '/usr/bin/chromium-browser',
    '/usr/bin/chromium',
    '/opt/google/chrome/chrome'
]

chrome_found = False
working_chrome_path = None

for chrome_path in possible_chrome_paths:
    if os.path.exists(chrome_path):
        print(f'✅ Chrome found at: {chrome_path} ({os.path.getsize(chrome_path):,} bytes)')
        working_chrome_path = chrome_path
        chrome_found = True
        break
    else:
        print(f'❌ Chrome not found at: {chrome_path}')

if not chrome_found:
    print('⚠️  No Chrome found at standard locations, testing Playwright default...')

try:
    with sync_playwright() as p:
        # Test Chrome launch
        launch_options = {
            'headless': True,
            'args': ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
        }
        
        if working_chrome_path:
            launch_options['executable_path'] = working_chrome_path
            
        browser = p.chromium.launch(**launch_options)
        page = browser.new_page()
        page.set_content('<html><body><h1>PDF Test</h1><p>Chrome PDF system ready!</p></body></html>')
        
        # Test PDF generation capability
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
            page.pdf(path=tmp.name, format='A4')
            print('✅ PDF generation test successful')
            
        browser.close()
        
except Exception as e:
    print(f'❌ Chrome verification failed: {e}')
    sys.exit(1)

print('🎉 CHROME PDF SYSTEM READY!')
"

# Expose port
EXPOSE 8080

# Start command
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "120", "wsgi:application"] 