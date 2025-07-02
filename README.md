# Instagram Auto-Reply Bot

A simple Instagram bot that automatically replies to direct messages using the official Instagram Graph API.

## 🚀 Live App

**URL**: https://summy-9f6d7e440dad.herokuapp.com/

## 📱 What It Does

- Receives Instagram direct messages via webhook
- Automatically replies with a friendly message
- Works with Instagram Business/Creator accounts
- Uses official Instagram Graph API v19.0

## 🤖 Bot Response

The bot sends a simple, generic reply to any message:

> "Hi [username]! Thanks for your message. I've received it and will get back to you soon! 🤖"

## 🔧 Setup Requirements

### 1. Instagram Account
- Must be a **Business** or **Creator** account (not personal)
- Account: `get_voyage`

### 2. Facebook App Configuration
1. Go to [Facebook Developers Console](https://developers.facebook.com/)
2. Create/configure your app with Instagram product
3. Set webhook URL: `https://summy-9f6d7e440dad.herokuapp.com/webhook`
4. Set verify token: `summy_webhook_2024_secure`
5. Subscribe to `messages` events

### 3. Required Permissions
- `instagram_basic`
- `instagram_manage_messages`
- `pages_messaging` (if using Facebook Pages)

## 🧪 Testing

### Health Check
```bash
curl https://summy-9f6d7e440dad.herokuapp.com/health
```

### Webhook Verification
```bash
curl "https://summy-9f6d7e440dad.herokuapp.com/webhook?hub.mode=subscribe&hub.verify_token=summy_webhook_2024_secure&hub.challenge=test"
```

### Test Message Processing
```bash
curl -X POST https://summy-9f6d7e440dad.herokuapp.com/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "object": "instagram",
    "entry": [
      {
        "id": "instagram_account_id",
        "messaging": [
          {
            "sender": {"id": "test_user"},
            "recipient": {"id": "instagram_account_id"},
            "message": {"text": "Hello"}
          }
        ]
      }
    ]
  }'
```

## 📝 Environment Variables

Required environment variables (configured in `.env`):
- `INSTAGRAM_ACCESS_TOKEN`: Your Instagram access token
- `INSTAGRAM_APP_SECRET`: Your app secret
- `VERIFY_TOKEN`: Webhook verification token

## 🔍 Troubleshooting

### Not Receiving Messages?

1. **Development Mode**: Instagram apps in development mode only receive webhooks from test users
   - Add test users in Facebook Developers Console → Roles → Test Users
   - OR submit app for review to go live

2. **Account Type**: Ensure Instagram account is Business/Creator (not personal)

3. **Webhook Configuration**: Verify webhook is properly configured in Facebook Developers Console

4. **Permissions**: Ensure app has required Instagram messaging permissions

## 📊 Monitoring

Check Heroku logs to see webhook activity:
```bash
heroku logs --tail --app summy
```

Look for log messages like:
```
INSTAGRAM WEBHOOK RECEIVED
Processing Instagram webhook...
Received Instagram message from [USER_ID]: [MESSAGE]
Generated reply: Hi [username]! Thanks for your message...
```

## 🚀 Deployment

The app is automatically deployed to Heroku when changes are pushed to the main branch.

## 📁 Project Structure

```
├── instagram_message_listener.py  # Main Flask application
├── requirements.txt              # Python dependencies
├── Procfile                     # Heroku deployment config
├── runtime.txt                  # Python version
├── .env                        # Environment variables
└── README.md                   # This file
```

## 🔗 API Endpoints

- `GET /` - Landing page
- `GET /health` - Health check
- `GET /webhook` - Webhook verification
- `POST /webhook` - Webhook message processing
- `POST /test-send` - Manual message sending (for testing)

---

**Status**: ✅ Live and operational with official Instagram Graph API
