# Instagram Webhook Callback URL Setup Guide

This guide will walk you through setting up the callback URL for your Instagram message bot to receive webhook events.

## Prerequisites

1. Your Flask app is running (locally on port 5001 or deployed)
2. You have an Instagram Business Account
3. You have a Facebook App with Instagram Basic Display API enabled

## Step 1: Make Your Local Server Publicly Accessible

Since Instagram needs to send webhooks to your server, you need a publicly accessible URL. Here are several options:

### Option A: Using ngrok (Recommended for Testing)

1. **Install ngrok:**
   ```bash
   # On macOS with Homebrew
   brew install ngrok
   
   # Or download from https://ngrok.com/download
   ```

2. **Start your Flask app** (if not already running):
   ```bash
   python3 instagram_message_listener.py
   ```

3. **In a new terminal, expose your local server:**
   ```bash
   ngrok http 5001
   ```

4. **Copy the HTTPS URL** from ngrok output (looks like `https://abc123.ngrok.io`)

### Option B: Using Cloudflare Tunnel

1. **Install cloudflared:**
   ```bash
   # On macOS
   brew install cloudflare/cloudflare/cloudflared
   ```

2. **Start tunnel:**
   ```bash
   cloudflared tunnel --url http://localhost:5001
   ```

3. **Copy the HTTPS URL** provided

### Option C: Deploy to Cloud Platform

Deploy your app to:
- **Heroku**: `https://your-app-name.herokuapp.com`
- **Railway**: `https://your-app-name.railway.app`
- **Render**: `https://your-app-name.onrender.com`
- **DigitalOcean App Platform**
- **AWS/GCP/Azure**

## Step 2: Update Your Verification Token

1. **Edit `instagram_message_listener.py`:**
   ```python
   # Replace this line:
   VERIFY_TOKEN = "your_verify_token_here"
   
   # With a secure token of your choice:
   VERIFY_TOKEN = "my_secure_webhook_token_2024"
   ```

2. **Restart your Flask app** after making this change.

## Step 3: Configure Instagram App in Facebook Developers

1. **Go to Facebook Developers Console:**
   - Visit: https://developers.facebook.com/
   - Log in with your Facebook account

2. **Select Your App:**
   - Go to "My Apps" → Select your Instagram app
   - If you don't have an app, create one with Instagram Basic Display product

3. **Navigate to Instagram Basic Display:**
   - In left sidebar: Products → Instagram → Basic Display
   - Click "Basic Display" settings

4. **Set Up Webhooks:**
   - Scroll down to "Webhooks" section
   - Click "Edit" next to Webhooks

5. **Add Webhook URL:**
   - **Callback URL**: `https://your-public-url.com/webhook`
     - Replace `your-public-url.com` with your ngrok/cloudflare/deployed URL
     - Example: `https://abc123.ngrok.io/webhook`
   
   - **Verify Token**: Enter the same token you set in Step 2
     - Example: `my_secure_webhook_token_2024`

6. **Subscribe to Events:**
   - Check the box for `messages`
   - This tells Instagram to send message events to your webhook

7. **Save Changes:**
   - Click "Save" or "Update"

## Step 4: Test Webhook Verification

1. **Instagram will verify your webhook** by sending a GET request to your callback URL
2. **Check your Flask app logs** - you should see:
   ```
   INFO:__main__:Webhook verified successfully
   ```

3. **If verification fails**, check:
   - Your callback URL is correct and accessible
   - Your verify token matches exactly
   - Your Flask app is running and responding

## Step 5: Test Message Handling

1. **Send a message to your Instagram account** from another account
2. **Check your Flask app logs** for incoming webhook data
3. **Verify the auto-reply is sent**

## Common Issues and Solutions

### Issue: Webhook Verification Failed
**Solutions:**
- Ensure your callback URL is publicly accessible (test in browser)
- Verify the token matches exactly (case-sensitive)
- Check Flask app is running and not showing errors

### Issue: Not Receiving Message Events
**Solutions:**
- Ensure you subscribed to `messages` events
- Check your Instagram app has proper permissions
- Verify your access token is valid and has messaging permissions

### Issue: ngrok URL Changes
**Solutions:**
- ngrok free tier gives you a new URL each time you restart
- Update the webhook URL in Facebook Developers when ngrok URL changes
- Consider upgrading to ngrok paid plan for persistent URLs

### Issue: SSL/HTTPS Required
**Solutions:**
- Instagram requires HTTPS for webhooks
- ngrok and cloudflare provide HTTPS automatically
- For custom domains, ensure SSL certificate is properly configured

## Production Deployment Considerations

When deploying to production:

1. **Use a stable domain** (not ngrok free tier)
2. **Implement webhook signature verification** for security
3. **Use environment variables** for all sensitive data
4. **Set up proper logging and monitoring**
5. **Use a production WSGI server** (like Gunicorn)
6. **Implement rate limiting** to prevent abuse

## Example Webhook URLs

- **ngrok**: `https://abc123.ngrok.io/webhook`
- **Heroku**: `https://my-instagram-bot.herokuapp.com/webhook`
- **Custom domain**: `https://mybot.example.com/webhook`

## Testing Your Setup

You can test your webhook endpoint manually:

```bash
# Test webhook verification (replace with your URL and token)
curl "https://your-url.com/webhook?hub.mode=subscribe&hub.verify_token=your_token&hub.challenge=test123"

# Should return: test123
```

## Next Steps

Once your webhook is set up and verified:
1. Test by sending messages to your Instagram account
2. Monitor the logs to ensure messages are being processed
3. Customize the auto-reply logic in `generate_auto_reply()` function
4. Consider adding more sophisticated message handling features
