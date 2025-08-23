# Heroku Deployment Guide

## 🚀 Deploy STR Optimizer Backend to Heroku

This guide will help you deploy your Flask backend to Heroku with wkhtmltopdf support.

### Prerequisites
- Heroku CLI installed ([install here](https://devcenter.heroku.com/articles/heroku-cli))
- Git repository with your backend code
- Your API keys and configuration ready

## Step 1: Create Heroku App

```bash
# Login to Heroku
heroku login

# Create new app (replace with your app name)
heroku create str-optimizer-backend

# Or use existing app
# heroku git:remote -a your-existing-app-name
```

## Step 2: Add Buildpacks (Order Matters!)

```bash
# 1. Add apt buildpack for system dependencies (FIRST)
heroku buildpacks:add --index 1 heroku-community/apt

# 2. Add wkhtmltopdf buildpack (SECOND) 
heroku buildpacks:add --index 2 https://github.com/dscout/wkhtmltopdf-buildpack.git

# 3. Add Python buildpack (THIRD)
heroku buildpacks:add --index 3 heroku/python

# Verify buildpacks are in correct order
heroku buildpacks
```

## Step 3: Configure Environment Variables

Set all your API keys and configuration:

```bash
# Required API Keys
heroku config:set FLASK_SECRET_KEY="your-secret-key-here"
heroku config:set OPENAI_API_KEY="your-openai-key"
heroku config:set STRIPE_SECRET_KEY="sk_test_your-stripe-key"
heroku config:set STRIPE_WEBHOOK_SECRET="whsec_your-webhook-secret"
heroku config:set STRIPE_PUBLISHABLE_KEY="pk_test_your-publishable-key"

# Email Configuration
heroku config:set GMAIL_EMAIL="your-gmail@gmail.com"
heroku config:set GMAIL_APP_PASSWORD="your-app-specific-password"
heroku config:set SENDGRID_API_KEY="SG.your-sendgrid-key"

# Optional: Set wkhtmltopdf version (defaults to 0.12.3)
heroku config:set WKHTMLTOPDF_VERSION="0.12.6"
```

## Step 4: Deploy to Heroku

```bash
# Deploy your code
git push heroku main

# Check deployment logs
heroku logs --tail
```

## Step 5: Verify Deployment

```bash
# Open your app
heroku open

# Test the debug endpoint
curl https://your-app-name.herokuapp.com/debug/wkhtmltopdf

# Check app status
heroku ps:scale web=1
heroku ps
```

## Step 6: Update Frontend Configuration

Update your frontend's API URL to point to Heroku:

In `str-optimizer-react/.env`:
```
REACT_APP_API_URL=https://your-app-name.herokuapp.com
```

Then redeploy your frontend to Firebase.

## 📋 File Structure

Your app should have these Heroku-specific files:

```
backend/
├── Procfile              # Defines how to start your app
├── runtime.txt           # Python version specification  
├── requirements.txt      # Python dependencies
├── Aptfile              # System packages for apt buildpack
├── gunicorn_config.py   # Gunicorn server configuration
└── app.py              # Your main Flask app
```

## 🔧 Configuration Files

**Procfile:**
```
web: gunicorn --config gunicorn_config.py app:app
```

**Aptfile:**
```
xvfb
fontconfig
fonts-liberation
fonts-dejavu-core
```

**runtime.txt:**
```
python-3.11.0
```

## 🎯 Expected Results

After successful deployment, the debug endpoint should show:

```json
{
  "path_checks": {
    "/app/bin/wkhtmltopdf": true
  },
  "which_wkhtmltopdf": "/app/bin/wkhtmltopdf",
  "wkhtmltopdf_version": "wkhtmltopdf 0.12.6",
  "xvfb_available": "/usr/bin/xvfb-run",
  "app_bin_contents": ["wkhtmltopdf", "wkhtmltoimage"]
}
```

## 💰 Pricing

- **Eco Dynos**: $5/month (perfect for development/staging)
- **Basic Dynos**: $7/month (recommended for production)
- **Standard Dynos**: $25+/month (for high-traffic applications)

## 🔧 Useful Heroku Commands

```bash
# View logs
heroku logs --tail

# Restart app
heroku ps:restart

# Run commands on server
heroku run python

# Scale dynos
heroku ps:scale web=1

# Access PostgreSQL (if using)
heroku pg:psql

# Config management
heroku config
heroku config:set KEY=value
heroku config:unset KEY
```

## 🚨 Troubleshooting

**PDF Generation Fails:**
1. Check buildpacks are in correct order: `heroku buildpacks`
2. Verify debug endpoint shows wkhtmltopdf installed
3. Check logs: `heroku logs --tail`

**App Won't Start:**
1. Check Procfile syntax
2. Verify requirements.txt includes all dependencies  
3. Check runtime.txt specifies supported Python version

**Environment Variables:**
1. Verify all required config vars are set: `heroku config`
2. Check for typos in variable names
3. Ensure sensitive values are properly quoted

## ✅ Success Checklist

- [ ] Heroku app created
- [ ] Buildpacks added in correct order  
- [ ] All environment variables configured
- [ ] Code deployed successfully
- [ ] Debug endpoint shows wkhtmltopdf installed
- [ ] PDF generation works
- [ ] Frontend updated with new API URL 