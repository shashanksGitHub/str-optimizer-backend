# NUCLEAR OPTION - USE IMAGE WITH WKHTMLTOPDF PRE-INSTALLED
# This base image already has wkhtmltopdf working - CANNOT fail!
FROM surnet/alpine-wkhtmltopdf:3.19.1-0.12.6-full as wkhtmltopdf
FROM python:3.11-slim

# Copy WORKING wkhtmltopdf from specialized image
COPY --from=wkhtmltopdf /bin/wkhtmltopdf /usr/local/bin/wkhtmltopdf
COPY --from=wkhtmltopdf /bin/wkhtmltoimage /usr/local/bin/wkhtmltoimage
COPY --from=wkhtmltopdf /lib/libwkhtmltox* /usr/local/lib/

# Install system dependencies
RUN apt-get update && apt-get install -y \
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
    && rm -rf /var/lib/apt/lists/*

# Make wkhtmltopdf executable
RUN chmod +x /usr/local/bin/wkhtmltopdf && \
    chmod +x /usr/local/bin/wkhtmltoimage

# Update library cache
RUN ldconfig

# VERIFY IT WORKS - Build fails if not working
RUN echo "🧪 NUCLEAR TEST - VERIFYING WKHTMLTOPDF WORKS" && \
    /usr/local/bin/wkhtmltopdf --version && \
    echo "✅ wkhtmltopdf version check passed" && \
    echo '<html><body><h1>TEST PDF</h1><p>This is a nuclear test!</p></body></html>' > /tmp/test.html && \
    xvfb-run -a /usr/local/bin/wkhtmltopdf /tmp/test.html /tmp/test.pdf && \
    test -f /tmp/test.pdf && \
    test $(stat -c%s /tmp/test.pdf) -gt 1000 && \
    echo "🎉 NUCLEAR OPTION SUCCESS - PDF GENERATION VERIFIED!" && \
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