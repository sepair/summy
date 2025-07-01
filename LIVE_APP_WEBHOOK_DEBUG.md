# Live Instagram App - Webhook Not Receiving Messages

## Issue: App is Live but No Webhooks from Real Messages

Since your app is live and approved, the issue is likely one of these:

## 1. Webhook Subscription Issues

### Check Current Subscriptions
1. **Go to Facebook Developers Console** → Your App → Instagram → Basic Display
2. **Check Webhooks section** - verify you're subscribed to:
   - ✅ `messages` events
   - ✅ For the correct Instagram account (`get_voyage`)

### Re-subscribe to Fix
1. **Unsubscribe** from `messages` events
2. **Save changes**
3. **Re-subscribe** to `messages` events  
4. **Save again**

## 2. Instagram Account Type Issues

### Verify Account Setup
The Instagram account `get_voyage` must be:
- ✅ **Business or Creator account** (not personal)
- ✅ **Connected to your Facebook app**
- ✅ **Properly linked in Instagram Basic Display settings**

### Check Connection
1. **Go to**: Instagram → Basic Display → Instagram Accounts
2. **Verify `get_voyage` is listed**
3. **If not listed**: Add it via "Add Instagram Account"

## 3. Message Source Restrictions

Even with live apps, Instagram has restrictions:

### Messages That Trigger Webhooks:
- ✅ Messages from users who follow the account
- ✅ Messages in response to stories
- ✅ Messages from users who have previously interacted
- ✅ Messages from business accounts

### Messages That DON'T Trigger Webhooks:
- ❌ Messages from completely new users (sometimes)
- ❌ Messages flagged as spam
- ❌ Messages from blocked accounts

## 4. API Version Issues

### Check Your API Version
Your code uses: `https://graph.instagram.com/v18.0`

### Try Latest Version
Update to v19.0 or v20.0:

```python
self.base_url = "https://graph.instagram.com/v19.0"
```

## 5. Webhook URL Issues

### Verify Exact URL
Ensure webhook URL is exactly:
```
https://summy-9f6d7e440dad.herokuapp.com/webhook
```

### Test Webhook Manually
```bash
curl -X POST https://summy-9f6d7e440dad.herokuapp.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

Should trigger the enhanced logging.

## 6. Instagram Account Permissions

### Required Permissions for get_voyage:
- ✅ Allow messages from everyone (not just followers)
- ✅ Business account with messaging enabled
- ✅ Not restricted or shadowbanned

### Check Settings:
1. **Instagram app** → Settings → Privacy → Messages
2. **Set to**: "Allow messages from everyone"

## 7. Facebook Page Connection

### If Using Facebook Pages:
Some Instagram messaging requires Facebook Page connection:

1. **Check if `get_voyage` is connected to a Facebook Page**
2. **If yes**: Ensure webhook is also subscribed to Page events
3. **Page webhook URL**: Same as Instagram webhook

## 8. Debugging Steps

### Test Different Message Sources:
1. **From followers** of `get_voyage`
2. **From business accounts**
3. **Reply to `get_voyage` stories**
4. **From accounts that previously messaged**

### Check Instagram Insights:
1. **Go to Instagram** → `get_voyage` → Insights
2. **Check if messages are being received** in Instagram's system
3. **If not showing in Insights**: Problem is with Instagram account setup

### Test with Different Accounts:
- ✅ Verified Instagram accounts
- ✅ Business accounts  
- ✅ Accounts that follow `get_voyage`
- ✅ Accounts in same country/region

## 9. Advanced Debugging

### Add Webhook Signature Verification
Instagram sends webhook signatures. Add this to verify:

```python
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected_signature}", signature)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    # Get signature from headers
    signature = request.headers.get('X-Hub-Signature-256')
    
    if signature:
        payload = request.get_data()
        if not verify_webhook_signature(payload, signature, APP_SECRET):
            logger.warning("Invalid webhook signature")
            return 'Invalid signature', 403
```

## 10. Contact Facebook Support

If none of the above works:

1. **Go to**: https://developers.facebook.com/support/
2. **Submit a bug report** with:
   - Your App ID
   - Instagram account: `get_voyage`
   - Webhook URL: `https://summy-9f6d7e440dad.herokuapp.com/webhook`
   - Description: "Live app not receiving Instagram message webhooks"

## Quick Checklist:

- [ ] Re-subscribe to `messages` webhook events
- [ ] Verify `get_voyage` is Business/Creator account
- [ ] Check Instagram message settings (allow from everyone)
- [ ] Test with follower accounts
- [ ] Test with story replies
- [ ] Try different API version (v19.0)
- [ ] Check if connected to Facebook Page
- [ ] Verify webhook URL is exact match

The most common fix for live apps is re-subscribing to webhook events or checking the Instagram account message settings.
