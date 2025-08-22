#!/bin/bash

# DigitalOcean Deployment Script for STR Optimizer Backend
set -e

# Configuration
DROPLET_IP="YOUR_NEW_DROPLET_IP"  # Update this with your new droplet IP
DROPLET_USER="root"  # Change this if you use a different user
APP_NAME="str-optimizer-backend"
REMOTE_DIR="/var/www/$APP_NAME"

echo "🚀 Starting deployment to DigitalOcean droplet..."

# Create deployment directory on remote server
ssh $DROPLET_USER@$DROPLET_IP "mkdir -p $REMOTE_DIR"

# Copy files to droplet (excluding .env and other sensitive files)
echo "📁 Copying files to droplet..."
rsync -avz --exclude='.env' --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' \
    ./ $DROPLET_USER@$DROPLET_IP:$REMOTE_DIR/

# Copy the correct production environment file
echo "🔧 Setting up production environment..."
scp env.production $DROPLET_USER@$DROPLET_IP:$REMOTE_DIR/.env

# Make scripts executable
ssh $DROPLET_USER@$DROPLET_IP "chmod +x $REMOTE_DIR/setup-server.sh"

# Restart the service
echo "🔄 Restarting STR Optimizer service..."
ssh $DROPLET_USER@$DROPLET_IP "cd $REMOTE_DIR && systemctl restart str-optimizer"

# Check service status
echo "✅ Checking service status..."
ssh $DROPLET_USER@$DROPLET_IP "systemctl status str-optimizer --no-pager -l"

# Test the API
echo "🧪 Testing API endpoint..."
sleep 2
if curl -s -f "https://159-203-166-39.nip.io/" > /dev/null; then
    echo "✅ API is responding correctly!"
else
    echo "❌ API test failed - check logs"
fi

echo "✅ Deployment completed successfully!"
echo "🌐 Frontend: https://str-optimizer.web.app"
echo "🔧 Backend: https://159-203-166-39.nip.io" 