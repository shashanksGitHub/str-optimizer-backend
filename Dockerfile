# ULTIMATE BULLETPROOF PDF SOLUTION - CACHE BUSTING VERSION 
# Breaking cache with timestamp: 2025-08-23-12:42:00
FROM ubuntu:22.04

# Force cache invalidation
ENV DOCKER_BUILD_TIMESTAMP=2025-08-23-12:42:00
ENV DEBIAN_FRONTEND=noninteractive

# Update system and install core dependencies
RUN apt-get update -y && apt-get upgrade -y && apt-get install -y \
    wget \
    curl \
    ca-certificates \
    gnupg \
    software-properties-common \
    apt-transport-https \
    && rm -rf /var/lib/apt/lists/*

# Install Python and development tools
RUN apt-get update -y && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create Python symlinks
RUN ln -sf /usr/bin/python3 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip && \
    python --version && pip --version

# Install system dependencies for wkhtmltopdf
RUN apt-get update -y && apt-get install -y \
    xvfb \
    fontconfig \
    fonts-liberation \
    fonts-dejavu-core \
    fonts-dejavu-extra \
    fonts-noto-color-emoji \
    fonts-noto-cjk \
    libxrender1 \
    libxext6 \
    libx11-6 \
    libxss1 \
    libgconf-2-4 \
    libxtst6 \
    libxrandr2 \
    libasound2 \
    libatk1.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgtk-3-0 \
    libjpeg62-turbo \
    libpng16-16 \
    libssl3 \
    zlib1g \
    && rm -rf /var/lib/apt/lists/*

# MULTIPLE INSTALLATION STRATEGIES - ONE WILL WORK!

# Strategy 1: Official Ubuntu package (if available)
RUN apt-get update -y && \
    (apt-get install -y wkhtmltopdf || echo "Ubuntu package failed") && \
    rm -rf /var/lib/apt/lists/*

# Strategy 2: Direct download from official releases
RUN echo "=== DOWNLOADING OFFICIAL WKHTMLTOPDF ===" && \
    cd /tmp && \
    wget -q --timeout=30 --tries=3 \
    https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb \
    -O wkhtmltox.deb && \
    echo "Downloaded wkhtmltox.deb" && \
    ls -la wkhtmltox.deb && \
    dpkg -i wkhtmltox.deb || apt-get install -fy && \
    echo "Installation attempt completed" && \
    rm -f wkhtmltox.deb

# Strategy 3: Alternative source if needed
RUN if [ ! -f "/usr/local/bin/wkhtmltopdf" ] && [ ! -f "/usr/bin/wkhtmltopdf" ]; then \
        echo "=== TRYING ALTERNATIVE SOURCE ===" && \
        cd /tmp && \
        wget -q --timeout=30 --tries=3 \
        https://downloads.wkhtmltopdf.org/0.12/0.12.6.1/wkhtmltox_0.12.6.1-2.jammy_amd64.deb \
        -O wkhtmltox_alt.deb && \
        dpkg -i wkhtmltox_alt.deb || apt-get install -fy && \
        rm -f wkhtmltox_alt.deb; \
    fi

# Strategy 4: Snap package as final fallback  
RUN if [ ! -f "/usr/local/bin/wkhtmltopdf" ] && [ ! -f "/usr/bin/wkhtmltopdf" ]; then \
        echo "=== TRYING SNAP PACKAGE ===" && \
        apt-get update -y && apt-get install -y snapd && \
        systemctl enable snapd && \
        snap install wkhtmltopdf-proxy && \
        ln -sf /snap/bin/wkhtmltopdf-proxy /usr/local/bin/wkhtmltopdf; \
    fi

# VERIFY INSTALLATION - FAIL BUILD IF NOT WORKING
RUN echo "=== VERIFICATION PHASE ===" && \
    echo "Checking for wkhtmltopdf..." && \
    (ls -la /usr/local/bin/wkhtmltopdf 2>/dev/null || echo "Not at /usr/local/bin/wkhtmltopdf") && \
    (ls -la /usr/bin/wkhtmltopdf 2>/dev/null || echo "Not at /usr/bin/wkhtmltopdf") && \
    (which wkhtmltopdf || echo "Not in PATH") && \
    if [ -f "/usr/local/bin/wkhtmltopdf" ]; then \
        echo "✅ Found at /usr/local/bin/wkhtmltopdf" && \
        /usr/local/bin/wkhtmltopdf --version; \
    elif [ -f "/usr/bin/wkhtmltopdf" ]; then \
        echo "✅ Found at /usr/bin/wkhtmltopdf" && \
        /usr/bin/wkhtmltopdf --version; \
    else \
        echo "❌ wkhtmltopdf not found anywhere!" && \
        echo "=== DEBUG INFO ===" && \
        find / -name "*wkhtmltopdf*" 2>/dev/null || echo "No wkhtmltopdf files found" && \
        echo "=== DPKG INFO ===" && \
        dpkg -l | grep wkhtmltopdf || echo "No wkhtmltopdf packages installed" && \
        exit 1; \
    fi

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies  
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# COMPREHENSIVE PDF GENERATION TEST
RUN echo "=== COMPREHENSIVE PDF TEST ===" && \
    python3 -c "
import subprocess
import os
import sys
import tempfile

print('🧪 RUNNING COMPREHENSIVE PDF TESTS')

# Find wkhtmltopdf
wkhtmltopdf_paths = ['/usr/local/bin/wkhtmltopdf', '/usr/bin/wkhtmltopdf']
wkhtmltopdf_cmd = None

for path in wkhtmltopdf_paths:
    if os.path.exists(path):
        print(f'✅ Found wkhtmltopdf at: {path}')
        try:
            result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f'✅ Version check passed: {result.stdout.strip()}')
                wkhtmltopdf_cmd = path
                break
            else:
                print(f'❌ Version check failed for {path}')
        except Exception as e:
            print(f'❌ Error testing {path}: {e}')

if not wkhtmltopdf_cmd:
    print('❌ No working wkhtmltopdf found!')
    # Show all installed packages for debugging
    try:
        result = subprocess.run(['dpkg', '-l'], capture_output=True, text=True)
        print('Installed packages:')
        for line in result.stdout.split('\n'):
            if 'wkhtmltopdf' in line.lower():
                print(f'  {line}')
    except:
        pass
    sys.exit(1)

# Test HTML content
test_html = '''<!DOCTYPE html>
<html>
<head>
    <title>PDF Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { color: #2563eb; font-size: 24px; font-weight: bold; margin-bottom: 20px; }
        .content { margin: 20px 0; line-height: 1.6; }
        .success { color: #16a34a; font-weight: bold; }
    </style>
</head>
<body>
    <div class=\"header\">🎯 BULLETPROOF PDF GENERATION TEST</div>
    <div class=\"content\">
        <p class=\"success\">✅ HTML parsing working</p>
        <p class=\"success\">✅ CSS styling working</p>
        <p class=\"success\">✅ Font rendering working</p>
        <p class=\"success\">✅ Unicode support: ★★★★★ 🎉</p>
        <p>Build timestamp: 2025-08-23-12:42:00</p>
    </div>
</body>
</html>'''

# Write test HTML
with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
    f.write(test_html)
    html_path = f.name

with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
    pdf_path = f.name

print(f'📝 HTML file: {html_path}')
print(f'📄 PDF file: {pdf_path}')

# Test PDF generation
cmd = [
    'xvfb-run', '-a', '--server-args=-screen 0 1920x1080x24',
    wkhtmltopdf_cmd,
    '--page-size', 'A4',
    '--margin-top', '0.75in',
    '--margin-right', '0.75in',
    '--margin-bottom', '0.75in',
    '--margin-left', '0.75in',
    '--encoding', 'UTF-8',
    '--enable-local-file-access',
    '--print-media-type',
    html_path,
    pdf_path
]

print(f'🔧 Command: {\" \".join(cmd)}')

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    if result.returncode == 0:
        if os.path.exists(pdf_path):
            pdf_size = os.path.getsize(pdf_path)
            if pdf_size > 5000:
                print(f'🎉 PDF GENERATION TEST SUCCESSFUL!')
                print(f'📊 PDF size: {pdf_size:,} bytes')
                print('✅ WKHTMLTOPDF IS FULLY OPERATIONAL!')
            else:
                print(f'❌ PDF too small: {pdf_size} bytes')
                print(f'STDERR: {result.stderr}')
                sys.exit(1)
        else:
            print(f'❌ PDF not created')
            print(f'STDERR: {result.stderr}')
            sys.exit(1)
    else:
        print(f'❌ Command failed: {result.returncode}')
        print(f'STDOUT: {result.stdout}')
        print(f'STDERR: {result.stderr}')
        sys.exit(1)
        
except subprocess.TimeoutExpired:
    print('❌ PDF generation timed out')
    sys.exit(1)
except Exception as e:
    print(f'❌ Test failed: {e}')
    sys.exit(1)
finally:
    # Cleanup
    try:
        os.unlink(html_path)
        os.unlink(pdf_path)
    except:
        pass

print('🏆 ALL TESTS PASSED - BUILD SUCCESSFUL!')
"

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Start application
CMD ["python", "app.py"] 