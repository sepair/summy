# Instagram Message Auto-Reply Bot

This Python application listens for incoming Instagram messages and automatically replies to them using the Instagram Graph API.

## Features

- Listens for incoming Instagram messages via webhooks
- Automatically replies with customized messages based on content
- Personalizes responses using the sender's username
- Includes health check and test endpoints
- Comprehensive logging

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

The `.env` file is already created with your Instagram API credentials:
- `INSTAGRAM_ACCESS_TOKEN`: Your Instagram access token
- `INSTAGRAM_APP_SECRET`: Your Instagram app secret

### 3. Update Webhook Verification Token

Edit `instagram_message_listener.py` and replace `"your_verify_token_here"` with a secure token of your choice:

```python
VERIFY_TOKEN = "your_secure_verify_token_123"
```

### 4. Instagram App Configuration

1. Go to your Instagram App in Facebook Developers Console
2. Add webhook URL: `https://your-domain.com/webhook`
3. Set the verify token to match what you set in step 3
4. Subscribe to `messages` webhook events
5. Ensure your app has the following permissions:
   - `instagram_basic`
   - `instagram_manage_messages`

### 5. Run the Application

```bash
python instagram_message_listener.py
```

The server will start on `http://localhost:5001`

## API Endpoints

### Webhook Endpoints
- `GET /webhook` - Webhook verification
- `POST /webhook` - Receive Instagram message events

### Utility Endpoints
- `GET /health` - Health check
- `POST /test-send` - Test sending a message manually

### Test Sending a Message

```bash
curl -X POST http://localhost:5001/test-send \
  -H "Content-Type: application/json" \
  -d '{"recipient_id": "USER_ID", "message": "Test message"}'
```

## Auto-Reply Logic

The bot responds differently based on message content:

- **Greetings** ("hello", "hi") → Personalized greeting
- **Help requests** ("help") → Assistance offer
- **Thanks** ("thank") → Acknowledgment
- **Questions** (contains "?") → Promise to respond
- **Default** → Generic acknowledgment

## Customization

You can modify the `generate_auto_reply()` function to customize responses based on your needs.

## Important Notes

1. **Webhook URL**: You need a publicly accessible HTTPS URL for webhooks to work
2. **Permissions**: Ensure your Instagram app has proper messaging permissions
3. **Rate Limits**: Be aware of Instagram API rate limits
4. **Security**: Keep your access tokens secure and never commit them to version control

## Deployment

For production deployment, consider:
- Using a production WSGI server like Gunicorn
- Setting up HTTPS with SSL certificates
- Using environment variables for all sensitive data
- Implementing proper error handling and monitoring

## Troubleshooting

1. **Webhook not receiving events**: Check your webhook URL and verification token
2. **Messages not sending**: Verify your access token and app permissions
3. **API errors**: Check the logs for detailed error messages

## Security Considerations

- Never share your access tokens or app secrets
- Use HTTPS for all webhook endpoints
- Validate webhook signatures in production
- Implement rate limiting to prevent abuse
