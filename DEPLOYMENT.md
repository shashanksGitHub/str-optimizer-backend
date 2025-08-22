# DigitalOcean Deployment Guide

## 🚀 Deploy STR Optimizer Backend to DigitalOcean

This guide will help you deploy your Flask backend to your DigitalOcean droplet.

### Prerequisites
- DigitalOcean droplet running Ubuntu 22.04
- SSH access to your droplet
- Your API keys and configuration ready

### Droplet Information
- **IP Address**: 159.203.166.39
- **OS**: Ubuntu 22.04
- **Droplet Name**: django-s-1vcpu-1gb-nyc3-01

## Step 1: Deploy Files to Droplet

Run the deployment script from your local machine:

```bash
./deploy.sh
```

This will:
- Copy all backend files to `/var/www/str-optimizer-backend/`
- Create initial environment file from template

## Step 2: SSH into Your Droplet

```bash
ssh root@159.203.166.39
```

## Step 3: Navigate to App Directory

```bash
cd /var/www/str-optimizer-backend
```

## Step 4: Configure Environment Variables

Edit the `.env` file with your actual values:

```bash
nano .env
```

Update these required values:
- `FLASK_SECRET_KEY`: Generate a secure random key
- `OPENAI_API_KEY`: Your OpenAI API key
- `STRIPE_SECRET_KEY`: Your Stripe secret key
- `STRIPE_PUBLISHABLE_KEY`: Your Stripe publishable key
- `EMAIL_USERNAME`: Your Gmail address
- `EMAIL_PASSWORD`: Your Gmail app password

## Step 5: Run Server Setup

```bash
./setup-server.sh
```

This will:
- Install Python 3.11, Nginx, and dependencies
- Create virtual environment and install packages
- Configure Gunicorn and systemd service
- Set up Nginx reverse proxy
- Start all services

## Step 6: Verify Deployment

Your app should now be accessible at: **http://159.203.166.39**

### Useful Commands

Check service status:
```bash
systemctl status str-optimizer
systemctl status nginx
```

View logs:
```bash
journalctl -u str-optimizer -f
```

Restart services:
```bash
systemctl restart str-optimizer
systemctl restart nginx
```

## Step 7: Update Frontend Configuration

Update your frontend's API URL to point to your droplet:

In `str-optimizer-react/.env`:
```
REACT_APP_API_URL=http://159.203.166.39
```

Then redeploy your frontend to Firebase.

## 🔒 Security Notes

- Consider setting up SSL/HTTPS with Let's Encrypt
- Change default SSH port for security
- Set up firewall rules
- Use environment-specific secrets

## Troubleshooting

If something goes wrong:
1. Check logs: `journalctl -u str-optimizer -f`
2. Check Nginx logs: `tail -f /var/log/nginx/error.log`
3. Verify services are running: `systemctl status str-optimizer nginx`
4. Test connectivity: `curl http://localhost:5001` 