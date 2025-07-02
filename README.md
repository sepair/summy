# Instagram Auto-Reply Bot

A simple Instagram bot that automatically replies to direct messages using the Instagram Messaging API with polling.

## 🚀 Live App

**URL**: https://summy-9f6d7e440dad.herokuapp.com/

## 📱 What It Does

- Polls Instagram conversations every 5 seconds for new messages
- Automatically replies with a friendly message to any new message
- Works with Instagram Business/Creator accounts
- Uses Instagram Messaging API (not webhooks)

## 🤖 Bot Response

The bot sends a simple, generic reply to any message:

> "Hi [username]! Thanks for your message. I've received it and will get back to you soon! 🤖"

## 🔧 Setup Requirements

### 1. Instagram Account
- Must be a **Business** or **Creator** account (not personal)
- Account: `get_voyage`

### 2. Instagram App Configuration
1. Go to [Facebook Developers Console](https://developers.facebook.com/)
2. Create an Instagram app (not Facebook app)
3. Get Instagram Messaging API permissions:
   - `instagram_basic`
   - `instagram_manage_messages`
4. Generate access token for your Instagram account

### 3. No Webhooks Required
Unlike traditional Instagram bots, this uses the Instagram Messaging API which:
- Polls for messages every 5 seconds
- Doesn't require webhook setup
- Works directly with Instagram conversations

## 🧪 Testing

### Health Check
```bash
curl https://summy-9f6d7e440dad.herokuapp.com/health
```

### Bot Statistics
```bash
curl https://summy-9f6d7e440dad.herokuapp.com/stats
```

### Test Conversations Access
```bash
curl https://summy-9f6d7e440dad.herokuapp.com/test-conversations
```

## 📝 Environment Variables

Required environment variables (configured in `.env`):
- `INSTAGRAM_ACCESS_TOKEN`: Your Instagram Messaging API access token
- `INSTAGRAM_APP_SECRET`: Your Instagram app secret

## 🔄 How It Works

1. **Background Polling**: Bot runs a background thread that checks for new messages every 5 seconds
2. **Conversation Detection**: Fetches all conversations using Instagram Messaging API
3. **Message Processing**: Checks each conversation for new messages
4. **Auto-Reply**: Sends generic reply to any new incoming message
5. **Duplicate Prevention**: Tracks processed message IDs to avoid duplicate replies

## 🔍 Monitoring

### Check Bot Status
The `/health` endpoint shows:
- Bot running status
- Polling status
- Number of processed messages

### Heroku Logs
```bash
heroku logs --tail --app summy
```

Look for log messages like:
```
Starting Instagram message polling...
Checking for new messages...
Found X conversations
New message from [USER_ID]: [MESSAGE]
Sending reply: Hi [username]! Thanks for your message...
Reply sent successfully
```

## 🚀 Deployment

The app is automatically deployed to Heroku when changes are pushed to the main branch.

## 📁 Project Structure

```
├── instagram_message_listener.py  # Main Flask app with polling bot
├── requirements.txt              # Python dependencies
├── Procfile                     # Heroku deployment config
├── runtime.txt                  # Python version
├── .env                        # Environment variables
└── README.md                   # This file
```

## 🔗 API Endpoints

- `GET /` - Landing page showing bot status
- `GET /health` - Health check with polling status
- `GET /stats` - Bot statistics (messages processed, etc.)
- `GET /test-conversations` - Test conversations API access

## ⚡ Key Differences from Webhook Approach

### Instagram Messaging API (Current)
✅ **Polling-based**: Checks for messages every 5 seconds
✅ **Direct API access**: Uses `graph.instagram.com` endpoints
✅ **No webhook setup**: No need for webhook configuration
✅ **Real-time-ish**: 5-second delay maximum
✅ **Simpler setup**: Just need API access token

### Webhook Approach (Previous)
❌ **Event-driven**: Requires webhook configuration
❌ **Complex setup**: Facebook app, webhook verification, etc.
❌ **Development mode issues**: Only works with test users
❌ **More dependencies**: Requires proper Facebook app review

## 🔧 Troubleshooting

### Not Receiving/Responding to Messages?

1. **Check Access Token**: Ensure your Instagram access token has messaging permissions
2. **Account Type**: Instagram account must be Business/Creator
3. **API Permissions**: Verify `instagram_manage_messages` permission
4. **Check Logs**: Monitor Heroku logs for API errors
5. **Test Conversations**: Use `/test-conversations` endpoint to verify API access

### Common Issues

- **403 Errors**: Usually means insufficient permissions
- **Rate Limiting**: Instagram API has rate limits for polling
- **Token Expiry**: Access tokens may need to be refreshed

---

**Status**: ✅ Live with Instagram Messaging API polling (no webhooks)
