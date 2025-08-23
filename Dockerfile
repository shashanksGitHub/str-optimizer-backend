# CACHE BUSTER - Forces DO to rebuild everything
ARG CACHE_BUST=6
ENV CACHE_BUST=${CACHE_BUST}

FROM python:3.11-slim

# Force cache invalidation with new number
RUN echo "Cache bust: ${CACHE_BUST}"

# SIMPLE DIRECT INSTALL - No multi-stage complexity
RUN apt-get update && apt-get install -y \
    wget \
    xvfb \
    fontconfig \
    fonts-liberation \
    fonts-dejavu-core \
    fonts-noto-color-emoji \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libjpeg62-turbo \
    libpng16-16 \
    libssl3 \
    libfontconfig1 \
    libfreetype6 \
    libxft2 \
    libglib2.0-0 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Download and install wkhtmltopdf directly
RUN wget -q -O wkhtmltox.deb https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.bullseye_amd64.deb && \
    dpkg -i wkhtmltox.deb || apt-get -f install -y && \
    apt-get -f install -y && \
    rm wkhtmltox.deb

# ENHANCED VERIFICATION - More detailed testing
RUN echo "🧪 ENHANCED NUCLEAR TEST - VERIFYING WKHTMLTOPDF" && \
    echo "📍 Checking if files exist..." && \
    ls -la /usr/local/bin/wkhtmltopdf && \
    ls -la /usr/local/bin/wkhtmltoimage && \
    echo "📋 Testing version..." && \
    /usr/local/bin/wkhtmltopdf --version && \
    echo "✅ wkhtmltopdf version check passed" && \
    echo "🧪 Testing PDF generation..." && \
    echo '<html><head><title>Nuclear Test</title></head><body><h1>NUCLEAR PDF TEST</h1><p>Cache bust: ${CACHE_BUST}</p><p>This PDF generation test must work!</p></body></html>' > /tmp/test.html && \
    xvfb-run -a --server-args="-screen 0 1024x768x24" /usr/local/bin/wkhtmltopdf --page-size A4 /tmp/test.html /tmp/test.pdf && \
    test -f /tmp/test.pdf && \
    echo "📊 PDF size: $(stat -c%s /tmp/test.pdf) bytes" && \
    test $(stat -c%s /tmp/test.pdf) -gt 1000 && \
    echo "🎉 ENHANCED NUCLEAR SUCCESS - PDF GENERATION FULLY VERIFIED!" && \
    rm -f /tmp/test.html /tmp/test.pdf

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Start application
CMD ["python", "app.py"] 