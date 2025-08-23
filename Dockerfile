# Use browserless/chrome image with Chromium pre-installed
FROM browserless/chrome:latest

# Install Python and pip
USER root
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
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

print('=== BROWSERLESS/CHROME VERIFICATION ===')
print(f'PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH: {os.environ.get(\"PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH\")}')

# Test Chrome availability
chrome_path = '/usr/bin/google-chrome'
if os.path.exists(chrome_path):
    print(f'✅ Chrome found at: {chrome_path}')
    print(f'✅ Chrome exists ({os.path.getsize(chrome_path):,} bytes)')
else:
    print('❌ Chrome not found at expected path')
    sys.exit(1)

try:
    with sync_playwright() as p:
        # Launch Chrome with explicit path
        browser = p.chromium.launch(
            headless=True,
            executable_path=chrome_path,
            args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
        )
        page = browser.new_page()
        page.set_content('<html><body><h1>PDF Test</h1><p>Browserless Chrome is ready!</p></body></html>')
        
        # Test PDF generation capability
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
            page.pdf(path=tmp.name, format='A4')
            print('✅ PDF generation test successful')
            
        browser.close()
        
except Exception as e:
    print(f'❌ Chrome verification failed: {e}')
    sys.exit(1)

print('🎉 BROWSERLESS CHROME PDF SYSTEM READY!')
"

# Expose port
EXPOSE 8080

# Start command
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "120", "wsgi:application"] 