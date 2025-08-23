# 🚀 Quick Heroku Deployment

## Prerequisites
- Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
- Have your API keys ready

## 1. Create & Configure Heroku App

```bash
# Login and create app
heroku login
heroku create str-optimizer-backend

# Add buildpacks in correct order
heroku buildpacks:add --index 1 heroku-community/apt
heroku buildpacks:add --index 2 https://github.com/dscout/wkhtmltopdf-buildpack.git
heroku buildpacks:add --index 3 heroku/python
```

## 2. Set Environment Variables

```bash
# Copy from your current .env file
heroku config:set FLASK_SECRET_KEY="your-secret-key"
heroku config:set OPENAI_API_KEY="your-openai-key"
heroku config:set STRIPE_SECRET_KEY="sk_test_..."
heroku config:set STRIPE_WEBHOOK_SECRET="whsec_..."
heroku config:set STRIPE_PUBLISHABLE_KEY="pk_test_..."
heroku config:set GMAIL_EMAIL="your-email@gmail.com"
heroku config:set GMAIL_APP_PASSWORD="your-app-password"
heroku config:set SENDGRID_API_KEY="SG...."
```

## 3. Deploy

```bash
git add .
git commit -m "Configure for Heroku deployment"
git push heroku main
```

## 4. Test

```bash
# Test debug endpoint
curl https://your-app-name.herokuapp.com/debug/wkhtmltopdf
```

You should see:
```json
{
  "path_checks": {
    "/app/bin/wkhtmltopdf": true
  },
  "which_wkhtmltopdf": "/app/bin/wkhtmltopdf"
}
```

## 5. Update Frontend

Update your frontend API URL to `https://your-app-name.herokuapp.com`

✅ **Done!** PDF generation will now work perfectly! 