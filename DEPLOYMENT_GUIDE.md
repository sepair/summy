# 🚀 Instagram Bot Deployment Guide

## 📋 Prerequisites

### 1. Environment Variables Setup
You need to create a `.env` file with your Instagram API credentials:

```bash
# Copy the template
cp .env.example .env

# Edit the .env file with your actual values
nano .env
```

**Required Environment Variables:**
- `INSTAGRAM_ACCESS_TOKEN` - Your Instagram Page Access Token
- `INSTAGRAM_APP_SECRET` - Your Facebook App Secret  
- `INSTAGRAM_BUSINESS_ACCOUNT_ID` - Your Instagram Business Account ID

### 2. Get Instagram API Credentials

#### Step 1: Facebook Developer Console
1. Go to [Facebook Developers Console](https://developers.facebook.com/)
2. Create or select your Instagram app
3. Get Instagram Messaging API permissions:
   - `instagram_basic`
   - `instagram_manage_messages`

#### Step 2: Generate Access Token
1. Go to your app > Instagram > Instagram Messaging
2. Generate a Page Access Token with permissions:
   - `pages_messaging`
   - `instagram_messaging`
3. Copy the token to your `.env` file

#### Step 3: Get App Secret
1. Go to your app > Settings > Basic
2. Copy the App Secret to your `.env` file

## 🚀 Deployment Options

### Option 1: Heroku (Recommended)

#### Using Heroku CLI:
```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Login to Heroku
heroku login

# Create new app (if needed)
heroku create your-app-name

# Add Heroku remote
heroku git:remote -a your-app-name

# Set environment variables
heroku config:set INSTAGRAM_ACCESS_TOKEN=your_token_here
heroku config:set INSTAGRAM_APP_SECRET=your_secret_here
heroku config:set INSTAGRAM_BUSINESS_ACCOUNT_ID=17841473964575374

# Deploy
git push heroku main
```

#### Using Heroku Dashboard:
1. Go to [Heroku Dashboard](https://dashboard.heroku.com/)
2. Create new app or connect to existing
3. Connect your GitHub repository
4. Set environment variables in Settings > Config Vars
5. Enable automatic deploys

### Option 2: Railway
1. Go to [Railway](https://railway.app/)
2. Connect your GitHub repository
3. Set environment variables
4. Deploy automatically

### Option 3: Render
1. Go to [Render](https://render.com/)
2. Create new Web Service
3. Connect your GitHub repository
4. Set environment variables
5. Deploy

## 🔧 Local Testing

### Install Dependencies:
```bash
pip3 install -r requirements.txt
```

### Run Locally:
```bash
python3 instagram_message_listener.py
```

### Test Endpoints:
```bash
# Test the frontend
curl http://localhost:5000/

# Test API
curl http://localhost:5000/api/messages

# Test message logging
curl http://localhost:5000/test-message
```

## 📱 After Deployment

### 1. Configure Instagram Webhook
1. Go to Facebook Developer Console > Your App > Webhooks
2. Set Callback URL: `https://your-app-name.herokuapp.com/webhook`
3. Set Verify Token: `summy_webhook_verify_token_2025`
4. Subscribe to **Page** object
5. Select **messages** field

### 2. Test Your Bot
1. Send a DM to your Instagram account
2. Check the web interface for received messages
3. Verify auto-replies are working

### 3. Monitor Logs
```bash
# Heroku logs
heroku logs --tail --app your-app-name

# Look for messages like:
# 🔔 WEBHOOK RECEIVED at [timestamp]
# 📨 Processing message from [USER_ID]: [MESSAGE]
# ✅ Reply sent successfully!
```

## 🎯 Current Status

- ✅ **Frontend**: Simplified and ready
- ✅ **Webhook Processing**: Working
- ✅ **Message Logging**: Working
- ❌ **Environment Variables**: Need to be configured
- ❌ **Instagram API**: Need access token

## 🚨 Next Steps

1. **Get Instagram API credentials** from Facebook Developer Console
2. **Create `.env` file** with your credentials
3. **Deploy to Heroku** using one of the methods above
4. **Configure webhook** in Facebook Developer Console
5. **Test with real Instagram messages**

---

**Need Help?** Check the `INSTAGRAM_SETUP_GUIDE.md` for detailed Instagram API setup instructions. 