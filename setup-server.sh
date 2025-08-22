#!/bin/bash

# Server Setup Script for STR Optimizer Backend on Ubuntu 22.04
set -e

echo "🔧 Setting up STR Optimizer Backend on Ubuntu 22.04..."

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install Python 3.11 and pip
echo "🐍 Installing Python 3.11..."
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Install nginx (no database needed!)
echo "🌐 Installing Nginx..."
apt install -y nginx

# Create Python virtual environment
echo "🔨 Creating virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Set up environment variables
echo "⚙️ Setting up environment variables..."
if [ ! -f .env ]; then
    echo "❌ .env file not found! Please create one from env.example"
    exit 1
fi

# Create Gunicorn configuration
echo "🦄 Creating Gunicorn configuration..."
cat > gunicorn.conf.py << 'EOF'
import multiprocessing

bind = "127.0.0.1:5001"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
EOF

# Create systemd service for the Flask app
echo "🔧 Creating systemd service..."
cat > /etc/systemd/system/str-optimizer.service << EOF
[Unit]
Description=STR Optimizer Flask Application
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/var/www/str-optimizer-backend
Environment=PATH=/var/www/str-optimizer-backend/venv/bin
ExecStart=/var/www/str-optimizer-backend/venv/bin/gunicorn --config gunicorn.conf.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
echo "🌐 Configuring Nginx..."
cat > /etc/nginx/sites-available/str-optimizer << 'EOF'
server {
    listen 80;
    server_name 159.203.166.39;  # Your droplet IP

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/str-optimizer /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
echo "🧪 Testing Nginx configuration..."
nginx -t

# Start and enable services
echo "🚀 Starting services..."
systemctl daemon-reload
systemctl enable str-optimizer
systemctl start str-optimizer
systemctl restart nginx

# Check service status
echo "📊 Service status:"
systemctl status str-optimizer --no-pager
systemctl status nginx --no-pager

echo "✅ Setup complete!"
echo "🌐 Your Flask app should now be accessible at: http://159.203.166.39"
echo "📋 To check logs: journalctl -u str-optimizer -f"
echo "🔧 To restart the app: systemctl restart str-optimizer" 