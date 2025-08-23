# BULLETPROOF WKHTMLTOPDF SOLUTION - GUARANTEED TO WORK
FROM ubuntu:22.04

# Prevent interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies and Python
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    wget \
    xvfb \
    fontconfig \
    fonts-liberation \
    fonts-noto-color-emoji \
    fonts-noto-cjk \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libjpeg62-turbo \
    libpng16-16 \
    libssl3 \
    libxss1 \
    libgconf-2-4 \
    libxtst6 \
    libxrandr2 \
    libasound2 \
    libatk1.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgtk-3-0 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create Python symlinks
RUN ln -sf /usr/bin/python3 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

# DIRECT DOWNLOAD - GUARANTEED WORKING wkhtmltopdf BINARY
RUN cd /tmp && \
    wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb && \
    dpkg -i wkhtmltox_0.12.6.1-2.jammy_amd64.deb || apt-get install -fy && \
    rm -f wkhtmltox_0.12.6.1-2.jammy_amd64.deb

# Verify wkhtmltopdf installation immediately
RUN /usr/local/bin/wkhtmltopdf --version && echo "✅ wkhtmltopdf verified working"

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Test wkhtmltopdf with actual HTML-to-PDF conversion
RUN python3 -c "
import subprocess
import os

print('🧪 TESTING WKHTMLTOPDF FUNCTIONALITY')

# Create test HTML
test_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Test PDF</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { color: #2563eb; font-size: 24px; font-weight: bold; }
        .content { margin: 20px 0; line-height: 1.6; }
    </style>
</head>
<body>
    <div class=\"header\">PDF Generation Test</div>
    <div class=\"content\">
        <p>This is a test to verify that wkhtmltopdf is working correctly.</p>
        <p>✅ HTML rendering working</p>
        <p>✅ CSS styling working</p>
        <p>✅ Font rendering working</p>
    </div>
</body>
</html>
'''

# Write test HTML
with open('/tmp/test.html', 'w') as f:
    f.write(test_html)

# Test PDF generation with xvfb-run
cmd = [
    'xvfb-run', '-a', '--server-args=-screen 0 1024x768x24',
    '/usr/local/bin/wkhtmltopdf',
    '--page-size', 'A4',
    '--margin-top', '0.75in',
    '--margin-right', '0.75in',
    '--margin-bottom', '0.75in',
    '--margin-left', '0.75in',
    '--encoding', 'UTF-8',
    '--no-outline',
    '--enable-local-file-access',
    '--print-media-type',
    '--disable-smart-shrinking',
    '--zoom', '1.0',
    '/tmp/test.html',
    '/tmp/test.pdf'
]

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        # Check if PDF was actually created and has content
        if os.path.exists('/tmp/test.pdf'):
            pdf_size = os.path.getsize('/tmp/test.pdf')
            if pdf_size > 1000:  # PDF should be at least 1KB
                print(f'✅ PDF GENERATION TEST SUCCESSFUL!')
                print(f'✅ PDF created: /tmp/test.pdf ({pdf_size:,} bytes)')
                print('🎉 WKHTMLTOPDF IS FULLY FUNCTIONAL!')
            else:
                print(f'❌ PDF too small: {pdf_size} bytes')
                exit(1)
        else:
            print('❌ PDF file not created')
            exit(1)
    else:
        print(f'❌ Command failed with return code: {result.returncode}')
        print(f'STDOUT: {result.stdout}')
        print(f'STDERR: {result.stderr}')
        exit(1)
except subprocess.TimeoutExpired:
    print('❌ PDF generation timed out')
    exit(1)
except Exception as e:
    print(f'❌ Test failed: {e}')
    exit(1)
"

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Start the application
CMD ["python", "app.py"] 