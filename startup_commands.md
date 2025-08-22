# Digital Ocean App Platform Run Commands

If the automatic deployment fails, try these run commands in the Digital Ocean console:

## Option 1 (Recommended):
```
gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 wsgi:application
```

## Option 2 (Alternative):
```
gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app:app
```

## Option 3 (Direct Flask):
```
python app.py
```

## Option 4 (With startup script):
```
bash start.sh
```

## How to set in Digital Ocean:
1. Go to your app settings
2. Find "Commands" or "Run Command" section
3. Replace the default command with one of the above
4. Deploy the changes

## Environment Variables Required:
- PORT=8080
- FLASK_ENV=production
- All your API keys (OpenAI, Stripe, SendGrid, etc.) 