# 🚀 Instagram Bot - Quick Start

## ✅ What's Ready

Your Instagram bot has been **simplified and optimized** with:

- ✅ **Clean Frontend**: Simple message display (no complex webhook monitoring)
- ✅ **Webhook Processing**: Ready to receive Instagram messages
- ✅ **Auto-Reply**: Friendly responses to all messages
- ✅ **Message Logging**: All conversations saved to `messages.txt`
- ✅ **Deployment Ready**: Heroku configuration complete

## 🎯 Current Status

- **Frontend**: ✅ Simplified and working
- **Backend**: ✅ Webhook processing ready
- **Environment**: ❌ Need API credentials
- **Deployment**: ❌ Need to deploy

## 🚀 Quick Deployment

### Step 1: Get Instagram API Credentials
1. Go to [Facebook Developers Console](https://developers.facebook.com/)
2. Create an Instagram app
3. Get these credentials:
   - **Instagram Access Token**
   - **Facebook App Secret**
   - **Instagram Business Account ID**

### Step 2: Setup Environment
```bash
# Run the setup script
python3 setup_env.py

# This will create a .env file with your credentials
```

### Step 3: Deploy to Heroku
```bash
# Option A: Use the deployment script
./deploy.sh

# Option B: Manual deployment
heroku create
heroku config:set INSTAGRAM_ACCESS_TOKEN=your_token
heroku config:set INSTAGRAM_APP_SECRET=your_secret
heroku config:set INSTAGRAM_BUSINESS_ACCOUNT_ID=17841473964575374
git push heroku main
```

## 📱 What Your Bot Does

1. **Receives Instagram DMs** via webhook
2. **Auto-replies** with friendly message
3. **Logs all conversations** to `messages.txt`
4. **Shows messages** on clean web interface

## 🎨 Frontend Features

- **Clean Design**: Modern, responsive interface
- **Message History**: View all received messages
- **Real-time Updates**: Auto-refresh every 30 seconds
- **Statistics**: Total messages and today's count
- **Easy Testing**: `/test-message` endpoint

## 🔗 Useful URLs

After deployment, your bot will be available at:
- **Main Interface**: `https://your-app.herokuapp.com/`
- **API Endpoint**: `https://your-app.herokuapp.com/api/messages`
- **Health Check**: `https://your-app.herokuapp.com/health`
- **Test Message**: `https://your-app.herokuapp.com/test-message`

## 📋 Next Steps

1. **Get Instagram API credentials** (see `INSTAGRAM_SETUP_GUIDE.md`)
2. **Run setup**: `python3 setup_env.py`
3. **Deploy**: `./deploy.sh`
4. **Configure webhook** in Facebook Developer Console
5. **Test** by sending DMs to your Instagram account

## 🆘 Need Help?

- **Setup Guide**: `INSTAGRAM_SETUP_GUIDE.md`
- **Deployment Guide**: `DEPLOYMENT_GUIDE.md`
- **Cleanup Summary**: `CLEANUP_SUMMARY.md`

---

**Status**: ✅ Ready for deployment with simplified frontend! 