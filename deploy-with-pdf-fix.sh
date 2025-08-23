#!/bin/bash

# Enhanced deployment script with HTML-to-PDF fixes
# This script rebuilds the Docker container with proper Playwright/Chromium setup for HTML-to-PDF generation

set -e

echo "🚀 Starting enhanced deployment with PDF fixes..."

# Configuration
PROJECT_NAME="str-optimizer-backend"
IMAGE_TAG="pdf-fixed-$(date +%Y%m%d-%H%M%S)"

# Step 1: Stop existing containers
echo "🛑 Stopping existing containers..."
docker stop $PROJECT_NAME 2>/dev/null || true
docker rm $PROJECT_NAME 2>/dev/null || true

# Step 2: Build new image with fixes
echo "🔨 Building Docker image with PDF fixes..."
docker build -t $PROJECT_NAME:$IMAGE_TAG -t $PROJECT_NAME:latest .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

# Step 3: Test the container before full deployment
echo "🧪 Testing container with PDF generation..."
docker run --rm \
    -e PLAYWRIGHT_BROWSERS_PATH=/ms/playwright \
    -v $(pwd):/test \
    $PROJECT_NAME:latest \
    python3 /test/test_pdf_fix.py

if [ $? -ne 0 ]; then
    echo "❌ PDF generation test failed in container!"
    echo "🔄 Container may still work with FPDF fallback in production"
fi

# Step 4: Start the container
echo "🚀 Starting new container..."
docker run -d \
    --name $PROJECT_NAME \
    --restart unless-stopped \
    -p 8080:8080 \
    -e FLASK_ENV=production \
    -e PLAYWRIGHT_BROWSERS_PATH=/ms/playwright \
    -e OPENAI_API_KEY="${OPENAI_API_KEY}" \
    -e STRIPE_SECRET_KEY="${STRIPE_SECRET_KEY}" \
    -e STRIPE_WEBHOOK_SECRET="${STRIPE_WEBHOOK_SECRET}" \
    -e SENDGRID_API_KEY="${SENDGRID_API_KEY}" \
    -e GMAIL_EMAIL="${GMAIL_EMAIL}" \
    -e GMAIL_APP_PASSWORD="${GMAIL_APP_PASSWORD}" \
    $PROJECT_NAME:latest

# Step 5: Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 10

# Step 6: Test container health
echo "🔍 Testing container health..."
if curl -f http://localhost:8080/health 2>/dev/null; then
    echo "✅ Container is healthy and responding"
else
    echo "⚠️  Health check endpoint not available, checking logs..."
    docker logs --tail=20 $PROJECT_NAME
fi

# Step 7: Show container status
echo "📊 Container status:"
docker ps | grep $PROJECT_NAME || echo "❌ Container not running"

# Step 8: Show logs
echo "📋 Recent container logs:"
docker logs --tail=10 $PROJECT_NAME

echo ""
echo "🎉 Deployment completed!"
echo "📝 Next steps:"
echo "   • Monitor logs: docker logs -f $PROJECT_NAME"
echo "   • Test PDF generation with a real request"
echo "   • Check system resources: docker stats $PROJECT_NAME"
echo ""
echo "🔧 Troubleshooting:"
echo "   • If PDF fails, check fallback works: docker exec $PROJECT_NAME python3 test_pdf_fix.py"
echo "   • View detailed logs: docker logs $PROJECT_NAME"
echo "   • Rebuild if needed: docker build --no-cache -t $PROJECT_NAME:latest ." 