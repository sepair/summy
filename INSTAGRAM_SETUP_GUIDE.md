# Instagram Messaging Bot Setup Guide

## 🚀 Your Instagram Bot is Ready!

Your Instagram messaging bot is fully deployed and working at:
**https://summy-9f6d7e440dad.herokuapp.com/**

## 📋 Required Environment Variables

The following environment variables need to be configured in your `.env` file:

### 1. INSTAGRAM_ACCESS_TOKEN (CRITICAL - Currently Missing)
- **What:** Page Access Token with Instagram Messaging permissions
- **Where to get:** Facebook Developer Console > Your App > Instagram > Generate Token
- **Current status:** `YOUR_PAGE_ACCESS_TOKEN_HERE` (placeholder)
- **Required for:** Sending Instagram messages

### 2. INSTAGRAM_APP_SECRET (✅ Configured)
- **What:** Facebook App Secret
- **Where to get:** Facebook Developer Console > Your App > Settings > Basic > App Secret
- **Current status:** Configured
- **Required for:** Webhook signature verification

### 3. INSTAGRAM_BUSINESS_ACCOUNT_ID (✅ Configured)
- **What:** Instagram Business Account ID (NOT Page ID)
- **Where to get:** Facebook Developer Console > Your App > Instagram > Instagram Business Account
- **Current status:** `17841473964575374` (get_voyage account)
- **Required for:** Sending Instagram messages

### 4. WEBHOOK_VERIFY_TOKEN (✅ Configured)
- **What:** Webhook verification token
- **Current status:** `summy_webhook_verify_token_2025`
- **Required for:** Webhook verification

## 🔧 Facebook Developer Console Setup

### Step 1: Configure Webhook
1. Go to Facebook Developer Console > Your App > Webhooks
2. Set **Callback URL:** `https://summy-9f6d7e440dad.herokuapp.com/webhook`
3. Set **Verify Token:** `summy_webhook_verify_token_2025`
4. Subscribe to **Page** object (not Instagram object)
5. Select **messages** field

### Step 2: Get Page Access Token
1. Go to Facebook Developer Console > Your App > Instagram > Instagram Messaging
2. Generate a Page Access Token with these permissions:
   - `pages_messaging`
   - `instagram_messaging`
3. Copy the token and replace `YOUR_PAGE_ACCESS_TOKEN_HERE` in `.env`

### Step 3: Link Instagram Account
1. Ensure your Instagram Business Account is linked to a Facebook Page
2. The Instagram Business Account ID should be: `17841473964575374`

## 🧪 Testing Your Bot

### Test Webhook Reception
```bash
curl -X POST https://summy-9f6d7e440dad.herokuapp.com/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "object": "instagram",
    "entry": [{
      "id": "17841405822304914",
      "time": 1234567890,
      "messaging": [{
        "sender": {"id": "test_user"},
        "recipient": {"id": "17841405822304914"},
        "timestamp": 1234567890,
        "message": {
          "mid": "test_message",
          "text": "Test message"
        }
      }]
    }]
  }'
```

### Check Bot Status
- **Health Check:** https://summy-9f6d7e440dad.herokuapp.com/health
- **Webhook Monitor:** https://summy-9f6d7e440dad.herokuapp.com/
- **Message History:** https://summy-9f6d7e440dad.herokuapp.com/api/messages

## 📱 How It Works

1. **User sends DM** to @get_voyage Instagram account
2. **Instagram sends webhook** to your bot
3. **Bot processes message** and generates personalized reply
4. **Bot sends reply** back to user via Instagram Messaging API
5. **All conversations logged** to messages.txt file

## 🔍 Monitoring

The bot includes a real-time webhook monitor at:
**https://summy-9f6d7e440dad.herokuapp.com/**

This shows:
- Live webhook events
- Message processing status
- Real-time statistics
- Professional terminal-style interface

## ⚠️ Current Status

- ✅ **Webhook Processing:** Fully working
- ✅ **Message Logging:** Working
- ✅ **User Identification:** Working
- ✅ **Real-time Monitoring:** Working
- ❌ **Message Sending:** Needs Page Access Token

## 🚨 Next Steps

1. **Get Page Access Token** from Facebook Developer Console
2. **Replace placeholder** in `.env` file
3. **Deploy updated environment variables** to Heroku
4. **Test with real Instagram messages** to @get_voyage

Once the Page Access Token is configured, your bot will be fully operational and able to send automatic replies to Instagram DMs!
