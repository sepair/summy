import os
import requests
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Instagram API credentials
ACCESS_TOKEN = os.getenv('INSTAGRAM_ACCESS_TOKEN')
APP_SECRET = os.getenv('INSTAGRAM_APP_SECRET')

# Verify token for webhook (set via environment variable)
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', 'summy_webhook_2024_secure')

class InstagramMessageHandler:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://graph.instagram.com/v18.0"
    
    def send_message(self, recipient_id, message_text):
        """Send a message to a specific user"""
        url = f"{self.base_url}/me/messages"
        
        payload = {
            'recipient': {'id': recipient_id},
            'message': {'text': message_text},
            'access_token': self.access_token
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            logger.info(f"Message sent successfully to {recipient_id}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending message: {e}")
            return None
    
    def get_user_info(self, user_id):
        """Get user information"""
        url = f"{self.base_url}/{user_id}"
        params = {
            'fields': 'id,username',
            'access_token': self.access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting user info: {e}")
            return None

# Initialize message handler
message_handler = InstagramMessageHandler(ACCESS_TOKEN)

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Verify webhook for Instagram"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return challenge
    else:
        logger.warning("Webhook verification failed")
        return 'Verification failed', 403

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """Handle incoming webhook from Instagram"""
    try:
        data = request.get_json()
        
        # Enhanced logging to debug webhook issues
        logger.info("=" * 50)
        logger.info("WEBHOOK RECEIVED")
        logger.info("=" * 50)
        logger.info(f"Raw webhook data: {json.dumps(data, indent=2)}")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request URL: {request.url}")
        
        # Check if data exists
        if not data:
            logger.warning("No data received in webhook")
            return jsonify({'status': 'no_data'}), 200
        
        # Process each entry in the webhook
        entries = data.get('entry', [])
        logger.info(f"Number of entries: {len(entries)}")
        
        for i, entry in enumerate(entries):
            logger.info(f"Processing entry {i+1}: {json.dumps(entry, indent=2)}")
            
            # Check for messaging events
            messaging_events = entry.get('messaging', [])
            logger.info(f"Number of messaging events in entry {i+1}: {len(messaging_events)}")
            
            for j, messaging_event in enumerate(messaging_events):
                logger.info(f"Processing messaging event {j+1}: {json.dumps(messaging_event, indent=2)}")
                process_message_event(messaging_event)
        
        logger.info("Webhook processing completed successfully")
        logger.info("=" * 50)
        return jsonify({'status': 'success'}), 200
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

def process_message_event(messaging_event):
    """Process individual message events"""
    sender_id = messaging_event.get('sender', {}).get('id')
    recipient_id = messaging_event.get('recipient', {}).get('id')
    
    # Check if this is an incoming message (not sent by us)
    if 'message' in messaging_event and sender_id != recipient_id:
        message_text = messaging_event['message'].get('text', '')
        
        logger.info(f"Received message from {sender_id}: {message_text}")
        
        # Get user info
        user_info = message_handler.get_user_info(sender_id)
        username = user_info.get('username', 'User') if user_info else 'User'
        
        # Generate auto-reply
        reply_text = generate_auto_reply(message_text, username)
        
        # Send reply
        message_handler.send_message(sender_id, reply_text)

def generate_auto_reply(incoming_message, username):
    """Generate an automatic reply based on the incoming message"""
    incoming_message_lower = incoming_message.lower()
    
    # Customize these responses based on your needs
    if 'hello' in incoming_message_lower or 'hi' in incoming_message_lower:
        return f"Hello {username}! Thanks for reaching out. How can I help you today?"
    
    elif 'help' in incoming_message_lower:
        return f"Hi {username}! I'm here to help. What do you need assistance with?"
    
    elif 'thank' in incoming_message_lower:
        return f"You're welcome, {username}! Feel free to reach out anytime."
    
    elif '?' in incoming_message:
        return f"Hi {username}! Thanks for your question. I'll get back to you as soon as possible!"
    
    else:
        return f"Hi {username}! Thanks for your message. I've received it and will respond soon!"

@app.route('/', methods=['GET'])
def landing_page():
    """Simple landing page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Instagram Bot</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                text-align: center;
                padding: 2rem;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                backdrop-filter: blur(10px);
            }
            h1 {
                font-size: 3rem;
                margin-bottom: 1rem;
            }
            p {
                font-size: 1.2rem;
                opacity: 0.9;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Hello World</h1>
            <p>Instagram Auto-Reply Bot is Running</p>
            <p>🤖 Ready to respond to messages</p>
        </div>
    </body>
    </html>
    """

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Instagram message listener is running'}), 200

@app.route('/test-send', methods=['POST'])
def test_send_message():
    """Test endpoint to send a message manually"""
    data = request.get_json()
    recipient_id = data.get('recipient_id')
    message_text = data.get('message', 'Test message from Instagram bot')
    
    if not recipient_id:
        return jsonify({'error': 'recipient_id is required'}), 400
    
    result = message_handler.send_message(recipient_id, message_text)
    
    if result:
        return jsonify({'status': 'success', 'result': result}), 200
    else:
        return jsonify({'error': 'Failed to send message'}), 500

if __name__ == '__main__':
    # Check if required environment variables are set
    if not ACCESS_TOKEN:
        logger.error("INSTAGRAM_ACCESS_TOKEN not found in environment variables")
        exit(1)
    
    if not APP_SECRET:
        logger.error("INSTAGRAM_APP_SECRET not found in environment variables")
        exit(1)
    
    logger.info("Starting Instagram message listener...")
    logger.info("Make sure to:")
    logger.info("1. Set up webhook URL in your Instagram app settings")
    logger.info("2. Update VERIFY_TOKEN in this script")
    logger.info("3. Ensure your app has proper permissions for messaging")
    
    # Run the Flask app
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
