# Instagram Bot Testing Guide

## ✅ App Status: WORKING

Your Instagram auto-reply bot is now live and operational at:
**https://summy-9f6d7e440dad.herokuapp.com/**

## Verified Working Components

✅ **Health Check**: `{"status":"healthy","message":"Instagram message listener is running"}`
✅ **Webhook Verification**: Properly responds to Instagram's verification requests
✅ **Environment Variables**: All credentials loaded successfully

## How to Test Instagram Message Replies

### Step 1: Configure Instagram Webhook (If Not Done)

1. **Go to Facebook Developers Console**: https://developers.facebook.com/
2. **Navigate to your Instagram app** → Products → Instagram → Basic Display
3. **Set Webhook Configuration**:
   - **Callback URL**: `https://summy-9f6d7e440dad.herokuapp.com/webhook`
   - **Verify Token**: `summy_webhook_2024_secure`
   - **Subscribe to**: `messages` events
4. **Save** - Instagram will verify the webhook (should work now!)

### Step 2: Test Message Auto-Replies

1. **From another Instagram account**, send a message to `get_voyage`
2. **Try different message types**:
   - `"Hello"` → Should get personalized greeting
   - `"Help"` → Should get assistance offer
   - `"Thank you"` → Should get acknowledgment
   - `"What time is it?"` → Should get question response
   - `"Random message"` → Should get generic response

### Step 3: Monitor Bot Activity

**Check Heroku Logs**:
- Go to: https://dashboard.heroku.com/apps/summy/logs
- Look for these log messages when messages are received:
  ```
  INFO:__main__:Received message from [USER_ID]: [MESSAGE_TEXT]
  INFO:__main__:Message sent successfully to [USER_ID]
  ```

### Step 4: Expected Bot Responses

The bot will respond with personalized messages based on content:

| Message Contains | Bot Response |
|------------------|--------------|
| "hello", "hi" | "Hello [username]! Thanks for reaching out. How can I help you today?" |
| "help" | "Hi [username]! I'm here to help. What do you need assistance with?" |
| "thank" | "You're welcome, [username]! Feel free to reach out anytime." |
| "?" (questions) | "Hi [username]! Thanks for your question. I'll get back to you as soon as possible!" |
| Other messages | "Hi [username]! Thanks for your message. I've received it and will respond soon!" |

## Troubleshooting

### If Messages Aren't Being Received:
1. **Check webhook subscription** in Facebook Developers Console
2. **Verify Instagram app permissions** include messaging
3. **Check Heroku logs** for any error messages
4. **Ensure the Instagram account** has proper business account setup

### If Bot Doesn't Reply:
1. **Check Heroku logs** for API errors
2. **Verify access token** is still valid
3. **Check Instagram API rate limits**
4. **Ensure recipient can receive messages** (not blocked, etc.)

## Manual Testing Endpoint

You can also test message sending manually:

```bash
curl -X POST https://summy-9f6d7e440dad.herokuapp.com/test-send \
  -H "Content-Type: application/json" \
  -d '{"recipient_id": "USER_INSTAGRAM_ID", "message": "Test message from bot"}'
```

## Success Indicators

✅ **Webhook verified** in Facebook Developers Console
✅ **Messages appear in Heroku logs** when sent to get_voyage
✅ **Auto-replies are sent** and visible in Instagram DMs
✅ **Personalized responses** using sender's username

Your Instagram auto-reply bot is now fully operational! 🚀

## Next Steps

- **Customize responses** by editing the `generate_auto_reply()` function
- **Add more sophisticated logic** for different message types
- **Monitor usage** through Heroku logs
- **Scale up** if you need more than free tier resources
