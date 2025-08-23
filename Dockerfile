# Use official Microsoft Playwright image with Chromium pre-installed
FROM mcr.microsoft.com/playwright/python:v1.40.0-focal

# Set environment variables for Playwright
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms/playwright
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

# Set working directory
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    fonts-liberation \
    fonts-noto-color-emoji \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install Playwright browsers with explicit configuration
ENV PLAYWRIGHT_BROWSERS_PATH=/ms/playwright
RUN python -m playwright install chromium --with-deps

# Create additional symlinks for path compatibility
RUN mkdir -p /workspace/.cache && \
    ln -sf /ms/playwright /workspace/.cache/ms-playwright 2>/dev/null || true && \
    ln -sf /ms/playwright /root/.cache/ms-playwright 2>/dev/null || true

# Set up proper permissions for browser execution
RUN chmod -R 755 /ms/playwright 2>/dev/null || true

# Verify Chromium installation and PDF generation capability
RUN python -c "
import os
import sys
from playwright.sync_api import sync_playwright

print('=== CHROMIUM VERIFICATION FOR PDF GENERATION ===')
print(f'PLAYWRIGHT_BROWSERS_PATH: {os.environ.get(\"PLAYWRIGHT_BROWSERS_PATH\")}')

try:
    with sync_playwright() as p:
        browser_path = p.chromium.executable_path
        print(f'✅ Chromium path: {browser_path}')
        
        if os.path.exists(browser_path):
            print(f'✅ Chromium exists ({os.path.getsize(browser_path):,} bytes)')
            
            # Test browser launch with production settings
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
            )
            page = browser.new_page()
            page.set_content('<html><body><h1>PDF Test</h1><p>Chromium is ready for PDF generation!</p></body></html>')
            
            # Test PDF generation capability
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
                page.pdf(path=tmp.name, format='A4')
                print('✅ PDF generation test successful')
                
            browser.close()
        else:
            print(f'❌ Chromium not found at: {browser_path}')
            sys.exit(1)
            
except Exception as e:
    print(f'❌ Chromium verification failed: {e}')
    sys.exit(1)

print('🎉 CHROMIUM PDF SYSTEM READY!')
"

# Set runtime environment
ENV PLAYWRIGHT_BROWSERS_PATH=/ms/playwright

# Expose port
EXPOSE 8080

# Start command with proper environment
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "120", "wsgi:application"] 