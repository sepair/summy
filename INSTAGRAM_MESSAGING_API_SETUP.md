# Instagram Messaging API Setup Guide

## Updated Code for Instagram Messaging API

I've updated your bot to use the proper Instagram Messaging API with fallback to Facebook Pages API. Here's what changed:

### Key Updates:
- ✅ **Updated to API v19.0** (latest version)
- ✅ **Instagram Messaging API first** with Facebook Pages fallback
- ✅ **Better error handling** and logging
- ✅ **Dual API support** for maximum compatibility

## Required Setup Steps

### 1. Instagram Account Requirements

Your `get_voyage` account MUST be:
- ✅ **Business or Creator Account** (not personal)
- ✅ **Connected to a Facebook Page** (recommended)
- ✅ **Proper messaging permissions enabled**

### 2. Facebook App Configuration

#### A. Instagram Basic Display (Current Setup)
1. **Go to**: Facebook Developers → Your App → Instagram → Basic Display
2. **Add Instagram Account**: Connect `get_voyage`
3. **Webhook Settings**:
   - URL: `https://summy-9f6d7e440dad.herokuapp.com/webhook`
   - Verify Token: `summy_webhook_2024_secure`
   - Subscribe to: `messages`

#### B. Instagram Messaging API (Recommended)
1. **Add Instagram Product**: Products → Add Product → Instagram
2. **Configure Messaging**: Instagram → Configuration
3. **Connect Instagram Account**: Link `get_voyage` to your app
4. **Webhook Configuration**: Same URL and token as above

#### C. Facebook Pages Integration (Most Reliable)
1. **Add Messenger Product**: Products → Add Product → Messenger
2. **Create/Connect Facebook Page**: 
   - Go to https://www.facebook.com/pages/create/
   - Create a business page for your bot
3. **Connect Instagram to Page**:
   - Facebook Page Settings → Instagram
   - Connect `get_voyage` account
4. **Configure Page Webhook**:
   - Messenger → Settings → Webhooks
   - Same webhook URL: `https://summy-9f6d7e440dad.herokuapp.com/webhook`
   - Subscribe to: `messages`, `messaging_postbacks`

### 3. Access Token Requirements

#### Current Token Type Check
Test what type of token you have:

```bash
curl "https://graph.facebook.com/v19.0/me?access_token=YOUR_ACCESS_TOKEN"
```

#### Required Token Types:
- **Instagram User Access Token**: For direct Instagram API
- **Page Access Token**: For Facebook Pages API (more reliable)
- **App Access Token**: For some operations

### 4. Required Permissions

Ensure your app has these permissions:
- ✅ `instagram_basic`
- ✅ `instagram_manage_messages`
- ✅ `pages_messaging` (if using Facebook Pages)
- ✅ `pages_read_engagement`

### 5. Webhook Event Types

Your webhook should be subscribed to:
- ✅ `messages` (Instagram direct messages)
- ✅ `messaging_postbacks` (if using Facebook Pages)
- ✅ `message_deliveries` (optional, for delivery confirmations)

## Testing the Updated Code

### 1. Deploy Updated Code
```bash
git add .
git commit -m "Update to Instagram Messaging API with Facebook Pages fallback"
git push origin main
```

### 2. Test API Endpoints

**Test Instagram API:**
```bash
curl "https://graph.instagram.com/v19.0/me?access_token=YOUR_ACCESS_TOKEN"
```

**Test Facebook API:**
```bash
curl "https://graph.facebook.com/v19.0/me?access_token=YOUR_ACCESS_TOKEN"
```

### 3. Monitor Enhanced Logs

The updated code provides detailed logging:
- ✅ Which API is being used (Instagram vs Facebook)
- ✅ Fallback attempts
- ✅ Detailed error messages
- ✅ API response information

## Expected Webhook Payload Formats

### Instagram Messaging API:
```json
{
  "entry": [
    {
      "id": "INSTAGRAM_ACCOUNT_ID",
      "messaging": [
        {
          "sender": {"id": "USER_ID"},
          "recipient": {"id": "INSTAGRAM_ACCOUNT_ID"},
          "timestamp": 1234567890,
          "message": {
            "mid": "MESSAGE_ID",
            "text": "Hello"
          }
        }
      ]
    }
  ]
}
```

### Facebook Pages API (for Instagram):
```json
{
  "entry": [
    {
      "id": "PAGE_ID",
      "messaging": [
        {
          "sender": {"id": "USER_ID"},
          "recipient": {"id": "PAGE_ID"},
          "timestamp": 1234567890,
          "message": {
            "mid": "MESSAGE_ID",
            "text": "Hello"
          }
        }
      ]
    }
  ]
}
```

## Troubleshooting

### If Still Not Receiving Messages:

1. **Check Account Connection**:
   ```bash
   curl "https://graph.instagram.com/v19.0/me/accounts?access_token=YOUR_ACCESS_TOKEN"
   ```

2. **Verify Page Connection** (if using Pages):
   ```bash
   curl "https://graph.facebook.com/v19.0/me/accounts?access_token=YOUR_ACCESS_TOKEN"
   ```

3. **Test Webhook Manually**:
   ```bash
   curl -X POST https://summy-9f6d7e440dad.herokuapp.com/webhook \
     -H "Content-Type: application/json" \
     -d '{"entry":[{"messaging":[{"sender":{"id":"test"},"message":{"text":"test"}}]}]}'
   ```

### Common Issues:

- **Token Scope**: Ensure token has messaging permissions
- **Account Type**: Must be Business/Creator, not personal
- **Page Connection**: Instagram account must be connected to Facebook Page
- **App Review**: Some permissions require Facebook app review

## Next Steps

1. **Deploy the updated code**
2. **Verify Instagram account is properly connected**
3. **Consider setting up Facebook Page integration** for more reliable messaging
4. **Test with the enhanced logging** to see exactly what's happening
5. **Check Heroku logs** for detailed API interaction information

The updated code should provide much better compatibility and detailed logging to help identify any remaining issues.
