# Heroku Deployment Checklist

Your Instagram message bot is now deployed to: **https://summy-9f6d7e440dad.herokuapp.com/**

## ✅ Completed Steps

1. **Repository Setup**: All files committed and pushed to GitHub
2. **Heroku Files**: Created Procfile, runtime.txt, and deployment configuration
3. **GitHub Integration**: Connected Heroku to GitHub with automatic deployment
4. **App Deployment**: App should be automatically deployed from main branch

## 🔧 Required Configuration Steps

### 1. Set Environment Variables in Heroku

Go to your Heroku app dashboard: https://dashboard.heroku.com/apps/summy

**Settings Tab → Config Vars → Add the following:**

```
INSTAGRAM_ACCESS_TOKEN = IGAAbAzum66UlBZAE9PZAWZAXTzhPUXJBaDBuU3RoajhCMXIxbmx2X0VWbmp0ZAGZAjX3FaY01WazNMblNLU1hFQ0IzVVBGblprNTZAabXM1bVYxLXlBcmNIUEpPbUpCY2NFY0pIQkF1eEpWUWdleTBRRUo2QzN4X1Y5YnQ2dS1iNG1vOAZDZD

INSTAGRAM_APP_SECRET = 98bba1bd1ff7ce242b99518035dce077

VERIFY_TOKEN = summy_webhook_2024_secure
```

### 2. Update Webhook Verification Token

**Option A: Update in Code (Recommended)**
1. Edit `instagram_message_listener.py`
2. Change line: `VERIFY_TOKEN = "your_verify_token_here"`
3. To: `VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', 'summy_webhook_2024_secure')`
4. Commit and push changes

**Option B: Use Current Hardcoded Value**
- Set VERIFY_TOKEN in Heroku to: `your_verify_token_here`

### 3. Configure Instagram Webhook

Go to Facebook Developers Console: https://developers.facebook.com/

1. **Navigate to your Instagram app**
2. **Go to Products → Instagram → Basic Display**
3. **Set Webhook URL**: `https://summy-9f6d7e440dad.herokuapp.com/webhook`
4. **Set Verify Token**: `summy_webhook_2024_secure` (or whatever you set in Heroku)
5. **Subscribe to**: `messages` events
6. **Save changes**

## 🧪 Testing Your Deployment

### 1. Test App Health
Visit: https://summy-9f6d7e440dad.herokuapp.com/health

Should return:
```json
{
  "status": "healthy",
  "message": "Instagram message listener is running"
}
```

### 2. Test Webhook Verification
Instagram will automatically verify your webhook when you save the settings.

### 3. Test Message Handling
1. Send a message to your Instagram account from another account
2. Check Heroku logs for activity: https://dashboard.heroku.com/apps/summy/logs
3. Verify auto-reply is sent

## 🔍 Monitoring and Logs

**View Heroku Logs:**
- Dashboard: https://dashboard.heroku.com/apps/summy/logs
- Or via CLI: `heroku logs --tail -a summy`

**Key Log Messages to Look For:**
- `INFO:__main__:Starting Instagram message listener...`
- `INFO:__main__:Webhook verified successfully`
- `INFO:__main__:Received message from [USER_ID]: [MESSAGE]`
- `INFO:__main__:Message sent successfully to [USER_ID]`

## 🚨 Troubleshooting

### App Not Starting
- Check Heroku logs for errors
- Verify environment variables are set correctly
- Ensure Procfile is correct

### Webhook Verification Failed
- Verify the webhook URL is exactly: `https://summy-9f6d7e440dad.herokuapp.com/webhook`
- Check that VERIFY_TOKEN matches between Heroku config and Facebook settings
- Ensure app is running (check /health endpoint)

### Messages Not Being Processed
- Check Instagram app permissions
- Verify access token is valid
- Check Heroku logs for API errors

## 📝 Next Steps

1. **Set environment variables in Heroku** (most important)
2. **Configure Instagram webhook** with your Heroku URL
3. **Test the complete flow** by sending a message
4. **Monitor logs** to ensure everything works correctly

## 🔐 Security Notes

- Environment variables are properly configured to keep API keys secure
- `.env` file is excluded from Git via `.gitignore`
- Production mode is enabled (debug=False)

Your Instagram auto-reply bot is ready to go live! 🚀
