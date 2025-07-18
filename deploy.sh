#!/bin/bash

# Instagram Bot Deployment Script

echo "🚀 Instagram Bot Deployment"
echo "=========================="
echo

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please run: python3 setup_env.py"
    exit 1
fi

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found!"
    echo "Please install it first:"
    echo "  brew install heroku/brew/heroku"
    exit 1
fi

# Check if logged into Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo "🔐 Please login to Heroku:"
    heroku login
fi

# Check if we have a Heroku app
if ! heroku apps:info &> /dev/null; then
    echo "📱 Creating new Heroku app..."
    heroku create
fi

# Get app name
APP_NAME=$(heroku apps:info --json | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
echo "📱 Using Heroku app: $APP_NAME"

# Set environment variables
echo "🔧 Setting environment variables..."
source .env
heroku config:set INSTAGRAM_ACCESS_TOKEN="$INSTAGRAM_ACCESS_TOKEN"
heroku config:set INSTAGRAM_APP_SECRET="$INSTAGRAM_APP_SECRET"
heroku config:set INSTAGRAM_BUSINESS_ACCOUNT_ID="$INSTAGRAM_BUSINESS_ACCOUNT_ID"
heroku config:set WEBHOOK_VERIFY_TOKEN="$WEBHOOK_VERIFY_TOKEN"

# Deploy
echo "🚀 Deploying to Heroku..."
git add .
git commit -m "Deploy Instagram bot"
git push heroku main

echo
echo "✅ Deployment complete!"
echo "🌐 Your bot is live at: https://$APP_NAME.herokuapp.com/"
echo
echo "📋 Next steps:"
echo "1. Configure Instagram webhook in Facebook Developer Console"
echo "2. Set webhook URL to: https://$APP_NAME.herokuapp.com/webhook"
echo "3. Test by sending a DM to your Instagram account"
echo
echo "📊 Monitor logs: heroku logs --tail --app $APP_NAME" 