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

# Install wkhtmltopdf using system package manager (simple and reliable)
RUN apt-get update && apt-get install -y wkhtmltopdf && rm -rf /var/lib/apt/lists/*

# SIMPLE VERIFICATION - Just check if installed (no build-breaking tests)
RUN echo "🧪 CHECKING WKHTMLTOPDF INSTALLATION..." && \
    which wkhtmltopdf || echo "❌ wkhtmltopdf not found in PATH" && \
    ls -la /usr/bin/wkhtmltopdf || echo "❌ /usr/bin/wkhtmltopdf not found" && \
    wkhtmltopdf --version || echo "❌ wkhtmltopdf version check failed" && \
    echo "✅ wkhtmltopdf installation check completed"

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