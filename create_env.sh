#!/bin/bash

# Script to create .env file with Firebase credentials
# This file is generated from your Firebase service account JSON

cat > .env << 'EOF'
# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key-here
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key-here

# Email Configuration (Gmail SMTP)
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password-here

# Server Configuration
PORT=5001
HOST=0.0.0.0

# Ngrok Configuration (for tunnel access)
NGROK_URL=https://your-ngrok-url.ngrok.io
ALLOW_ALL_ORIGINS=false

# Admin Configuration - CHANGE THIS TO YOUR OWN SECRET CODE!
ADMIN_SECRET_CODE=admin123secure

# Firebase Admin SDK Configuration (for admin dashboard)
FIREBASE_PRIVATE_KEY_ID=bf3f130c1b59eabbfeec79fadb32ab789e6a0603
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCj1yk6BTc+Kx7t\nqy0HCphpx/xeWqqu9Z4bkTD3SeIR+EMdfDnkTjKS0HFa18y+clLci3e7UTU9nCqy\nPPpX8JF4sqZzWcAW/MKwGo2tJNVJB6PBrpInFTmzTm/l5OEmAqfDHEt2bkaASntx\nMbounfrr5fWQi8QxAFWQ5V7AwimQfeRqV/pyWz/zcGj0TSW5GbPP1Wp9UEvpwfUz\ndVOwN4E58KxDeEV+Ew35YE5EbvOjpEpnpWdtYuQz59uaYQD7JzqkU2BRfMAhIHaH\nNfxkcFk1BrE18hwXOWSVeM0P3/rlocy0XyyneLL5wy7wnrezGAiRjf3Yg2+B0AUr\n169gc4H5AgMBAAECggEAR4zks7JobC1vrdJl8R/G7NdJ1rjYtlyMZjSTgkMRR9C4\nGq3QKGyf+G6wOkBo6TjLCAaeTL8LtbK4EKvBllr4ZJH8T/6/fSp4KWkHOziNLn34\nHVLL/+ZskuorwuWgD7X0Jqh6KifBgTBF1WqmiMo0NQXxpmTrUoz3UTZiGWMRvMgR\n2OttPLqFu6d4tM3Dusxp40QKyRkxO1JqwC2WmGt31HYNXMMZViG64k3l9pWcFctU\nnhPAVlE9xAagwpzK9sREyBRWJECguFF49Lyvll2u5vv52x7k9OHr6/t7pDegehpc\nDkRbsantnnlx+Rpu71bxOsn06hMveFGzuHEwLDQgYwKBgQDkyjO5gEZqTvVO2RxI\nsBGUYSQWci7ZZoe2sjRDceG/F9mLJgXwK/rgOT4eT6bKjBbPRTemmYs3JDZ6Ww3r\n2eWxGVYxvCpkwmmeHDMBZyJo0dAfR6Dgk5RHMEYPfWD8rQI9Tpj3bwdLXvXzqf5d\neHoLHmPCHCKDxSiZKJdyCV50qwKBgQC3U34YwYgz7AAXk68xVV0uHi2b7iZ1NG7Q\nzE46PjND/NGwchAv9z9ldj5sVAKjmBntDwZGAzZr3azo0tSAdwvh52Ud3pNsx/yG\nsGFpGPV3F6Cp7/4AfrsiQMtcnE92x4iBASb+Ypte048u3WFQlY7xzUfQ372GNxrD\nPnX1x5E76wKBgC7tEkLf/pFbdJEhkt2Nz21Bp2c7METC9N8SGgojV4wcVjBmMh2a\nx7ApzYXmDG3K4frNVabEI3vB37Kk7mwLm0MB0V4OHBvijEszuXp2LuaU8j0YMfUe\nD/GyAwy2SKhKzATLFDDcAwEAjy3VFikRxuZ06z0rDCE+1R7k5nsrVMZVAoGAKsVF\n9Ayi9EopM1b3VrEtziaoSWrkeg/Dkt83mQsN9tyzJ1FVSXuLxOYzZh6rhvNjiRUq\nR4dUWRIc1yzo+xfLI+dShgd5qbV2yw23jEeQbTqL91nQjtkCW9l2GKM3PuUKid50\n9ICY8yS0kSCBJcXe1bco/ChXFUsh6U9XQgJPdgUCgYBR0Tn7u6iKHFjS93wh0If6\nzPehZc5mmhHV/Mu9CQ9GUoHtdjqyivE0tUUOT3qQ6nQ9a/WelYjawiLn0koQjao7\ngM7oEhZ8H/wyetLxjrbTYLCnhDLqES+f5vgPWFVyo8bnZy8cfDCjJ14qMkf5HJvs\n/Q5baXtUXAMctMLWPYntMA==\n-----END PRIVATE KEY-----"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-fbsvc@str-optimizer.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=118012918649896355295
FIREBASE_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40str-optimizer.iam.gserviceaccount.com
EOF

echo "✅ .env file created successfully!"
echo ""
echo "⚠️  IMPORTANT: Please update these values in your .env file:"
echo "   - FLASK_SECRET_KEY (generate a secure random key)"
echo "   - OPENAI_API_KEY (your OpenAI API key)"
echo "   - STRIPE_SECRET_KEY and STRIPE_PUBLISHABLE_KEY (your Stripe keys)"
echo "   - EMAIL_USERNAME and EMAIL_PASSWORD (your email SMTP credentials)"
echo "   - ADMIN_SECRET_CODE (change from default 'admin123secure' to something secure!)"
echo ""
echo "Firebase Admin SDK credentials have been configured automatically."

