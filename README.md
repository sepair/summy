# Instagram Auto-Reply Bot

A simple Instagram bot that automatically replies to direct messages using the Instagram Messaging API with polling.

## 🚀 Live App

**URL**: https://summy-9f6d7e440dad.herokuapp.com/

## 📱 What It Does

- Receives Instagram direct messages via webhooks
- Automatically replies with a friendly message to any new message
- Works with Instagram Business/Creator accounts
- Uses Instagram Messaging API with webhook integration
- Simple, clean frontend to view received messages

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

1. **Webhook Reception**: Instagram sends webhook events when new messages arrive
2. **Message Processing**: Bot processes incoming webhook messages
3. **Auto-Reply**: Sends friendly reply to any new incoming message
4. **Message Logging**: All conversations are logged to `messages.txt`
5. **Frontend Display**: Simple web interface shows all received messages

## 🔍 Monitoring

### Check Bot Status
The `/health` endpoint shows:
- Bot running status
- Number of processed messages
- Webhook event count

### Heroku Logs
```bash
heroku logs --tail --app summy
```

Look for log messages like:
```
🔔 WEBHOOK RECEIVED at [timestamp]
📨 Processing message from [USER_ID]: [MESSAGE]
✅ Reply sent successfully!
📝 Message logged: [username]
```

## 🚀 Deployment

The app is automatically deployed to Heroku when changes are pushed to the main branch.

## 📁 Project Structure

```
├── instagram_message_listener.py  # Main Flask app with webhook bot
├── requirements.txt              # Python dependencies
├── Procfile                     # Heroku deployment config
├── .env                        # Environment variables
└── README.md                   # This file
```

## 🔗 API Endpoints

- `GET /` - Landing page showing bot status
- `GET /health` - Health check with polling status
- `GET /stats` - Bot statistics (messages processed, etc.)
- `GET /test-conversations` - Test conversations API access
- `GET /messages` - View all logged messages in browser
- `GET /messages/download` - Download messages log file

## 🎨 Frontend Features

### Simple Message Display
✅ **Clean Interface**: Modern, responsive design
✅ **Message History**: View all received messages
✅ **Real-time Updates**: Auto-refresh every 30 seconds
✅ **Statistics**: Total messages and today's count
✅ **Easy Testing**: `/test-message` endpoint for testing

### Message Format
- **Username**: Shows who sent the message
- **Timestamp**: When the message was received
- **Original Message**: What the user sent
- **Bot Reply**: The automatic response sent

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

**Status**: ✅ Live with simplified frontend and webhook processing
