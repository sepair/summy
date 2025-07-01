# Instagram Webhook Not Receiving Real Messages

## Issue: Webhook works in Facebook test but not with real Instagram messages

This is a common problem with Instagram API setup. Here are the most likely causes and solutions:

## 1. Instagram App in Development Mode

**Problem**: Instagram apps in development mode only receive webhooks from test users, not real users.

**Solution**:
1. Go to Facebook Developers Console → Your App
2. Navigate to "App Review" → "Permissions and Features"
3. Request review for `instagram_manage_messages` permission
4. OR add test users who can send messages

**Alternative**: Add test users:
1. Go to "Roles" → "Test Users"
2. Add Instagram accounts as test users
3. Only these accounts can trigger webhooks in development mode

## 2. Instagram Business Account Setup

**Problem**: The Instagram account `get_voyage` might not be properly connected as a business account.

**Check**:
1. Go to Facebook Developers Console → Your App
2. Navigate to "Instagram" → "Basic Display"
3. Verify `get_voyage` is listed as a connected Instagram account
4. Ensure it's a Business or Creator account (not personal)

## 3. Webhook Subscription Issues

**Problem**: Webhook might not be subscribed to the correct events or account.

**Fix**:
1. In Facebook Developers Console → Instagram → Basic Display
2. Go to Webhooks section
3. Ensure you're subscribed to `messages` for the correct Instagram account
4. Try unsubscribing and re-subscribing

## 4. Instagram API Permissions

**Problem**: Missing required permissions for message handling.

**Required Permissions**:
- `instagram_basic`
- `instagram_manage_messages`
- `pages_messaging` (if using Facebook Pages)

**Check**: App Review → Permissions and Features

## 5. Message Source Restrictions

**Problem**: Instagram may only send webhooks for certain types of messages.

**Limitations**:
- Only messages from users who have interacted with your business before
- Only messages in response to your content or ads
- Not all direct messages trigger webhooks

## 6. Webhook Event Format Issues

**Problem**: The webhook payload might be different than expected.

**Debug Steps**:

1. **Add more detailed logging** to see what's actually being received:

```python
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """Handle incoming webhook from Instagram"""
    try:
        data = request.get_json()
        
        # Log the raw webhook data
        logger.info(f"Raw webhook received: {json.dumps(data, indent=2)}")
        
        # Log headers too
        logger.info(f"Webhook headers: {dict(request.headers)}")
        
        # Process each entry in the webhook
        for entry in data.get('entry', []):
            logger.info(f"Processing entry: {json.dumps(entry, indent=2)}")
            
            # Process messaging events
            for messaging_event in entry.get('messaging', []):
                logger.info(f"Processing messaging event: {json.dumps(messaging_event, indent=2)}")
                process_message_event(messaging_event)
        
        return jsonify({'status': 'success'}), 200
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({'error': str(e)}), 500
```

## 7. Test Different Message Types

Try sending:
- Regular text messages
- Messages with emojis
- Messages in response to Instagram stories
- Messages from accounts that follow `get_voyage`

## 8. Check Instagram Graph API Version

**Problem**: Using wrong API version or endpoints.

**Current Code Uses**: `https://graph.instagram.com/v18.0`

**Try**: Update to latest version or try v19.0

## Immediate Debugging Steps

1. **Check Heroku Logs** when sending real messages:
   ```
   https://dashboard.heroku.com/apps/summy/logs
   ```

2. **Look for ANY webhook activity** - even if it's not processing correctly

3. **Try sending from different accounts**:
   - Accounts that follow `get_voyage`
   - Accounts that have messaged before
   - New accounts

4. **Test with Instagram Stories**:
   - Post a story on `get_voyage`
   - Reply to the story from another account
   - This sometimes triggers webhooks when DMs don't

## Quick Fix: Enhanced Logging

Let me update your code to add better logging to see what's happening:
