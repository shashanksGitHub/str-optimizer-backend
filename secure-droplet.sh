#!/bin/bash

# Security Setup Script for Digital Ocean Droplet
set -e

echo "🔒 Securing your Digital Ocean droplet..."

# Update system first
apt update && apt upgrade -y

# Install fail2ban (protects against brute force attacks)
echo "🛡️ Installing fail2ban..."
apt install -y fail2ban

# Configure firewall
echo "🔥 Setting up UFW firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 5001/tcp  # For our Flask app
ufw --force enable

# Create non-root user (optional but recommended)
echo "👤 Creating deployment user..."
if ! id "deploy" &>/dev/null; then
    adduser --disabled-password --gecos "" deploy
    usermod -aG sudo deploy
    
    # Copy SSH keys to new user
    if [ -d /root/.ssh ]; then
        mkdir -p /home/deploy/.ssh
        cp /root/.ssh/authorized_keys /home/deploy/.ssh/
        chown -R deploy:deploy /home/deploy/.ssh
        chmod 700 /home/deploy/.ssh
        chmod 600 /home/deploy/.ssh/authorized_keys
    fi
fi

# Configure SSH security
echo "🔐 Securing SSH..."
sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart ssh

echo "✅ Security setup complete!"
echo "📝 Remember to use 'deploy' user for future deployments" 