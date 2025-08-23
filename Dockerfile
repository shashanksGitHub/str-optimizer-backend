# Use official Microsoft Playwright image with Chromium pre-installed
FROM mcr.microsoft.com/playwright/python:v1.40.0-focal

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms/playwright
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

# Ensure environment variables are available at runtime
RUN echo 'export PLAYWRIGHT_BROWSERS_PATH=/ms/playwright' >> /etc/environment
RUN echo 'export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1' >> /etc/environment

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Verify Chromium is available
RUN python -c "
from playwright.sync_api import sync_playwright
import os
try:
    with sync_playwright() as p:
        browser_path = p.chromium.executable_path
        print(f'✅ Chromium found at: {browser_path}')
        print(f'✅ File exists: {os.path.exists(browser_path)}')
        if os.path.exists(browser_path):
            print(f'✅ File size: {os.path.getsize(browser_path)} bytes')
        print('🎉 CHROMIUM READY IN DOCKER IMAGE!')
except Exception as e:
    print(f'❌ Chromium verification failed: {e}')
    exit(1)
"

# Expose port
EXPOSE 8080

# Start command - no need for complex startup script
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "120", "wsgi:application"] 