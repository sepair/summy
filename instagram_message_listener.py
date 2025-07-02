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
        self.graph_api_url = "https://graph.facebook.com/v19.0"
    
    def send_message(self, recipient_id, message_text):
        """Send a message via Instagram Graph API"""
        # Use the official Instagram Graph API endpoint
        url = f"{self.graph_api_url}/me/messages"
        
        payload = {
            'recipient': {'id': recipient_id},
            'message': {'text': message_text},
            'access_token': self.access_token
        }
        
        try:
            response = requests.post(url, json=payload)
            logger.info(f"API Response Status: {response.status_code}")
            logger.info(f"API Response: {response.text}")
            
            if response.status_code == 200:
                logger.info(f"Message sent successfully to {recipient_id}")
                return response.json()
            else:
                logger.error(f"Failed to send message. Status: {response.status_code}, Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error when sending message: {e}")
            return None
    
    def get_user_info(self, user_id):
        """Get user information via Graph API"""
        url = f"{self.graph_api_url}/{user_id}"
        params = {
            'fields': 'id,name,first_name',
            'access_token': self.access_token
        }
        
        try:
            response = requests.get(url, params=params)
            logger.info(f"User info API Response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    'id': user_data.get('id'),
                    'username': user_data.get('name', user_data.get('first_name', 'User'))
                }
            else:
                logger.error(f"Failed to get user info. Status: {response.status_code}")
                return {'id': user_id, 'username': 'User'}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting user info: {e}")
            return {'id': user_id, 'username': 'User'}

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
    """Handle incoming webhook from Instagram Graph API"""
    try:
        data = request.get_json()
        
        # Enhanced logging to debug webhook issues
        logger.info("=" * 50)
        logger.info("INSTAGRAM WEBHOOK RECEIVED")
        logger.info("=" * 50)
        logger.info(f"Raw webhook data: {json.dumps(data, indent=2)}")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request URL: {request.url}")
        logger.info(f"Content-Type: {request.headers.get('Content-Type', 'Not specified')}")
        
        # Check if data exists
        if not data:
            logger.warning("No data received in webhook")
            return jsonify({'status': 'no_data'}), 200
        
        # Check webhook object type
        webhook_object = data.get('object')
        logger.info(f"Webhook object type: {webhook_object}")
        
        # Process Instagram webhooks
        if webhook_object == 'instagram':
            return handle_instagram_webhook(data)
        elif webhook_object == 'page':
            return handle_page_webhook(data)
        else:
            logger.warning(f"Unknown webhook object type: {webhook_object}")
            return jsonify({'status': 'unknown_object_type'}), 200
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

def handle_instagram_webhook(data):
    """Handle Instagram-specific webhook format"""
    logger.info("Processing Instagram webhook...")
    
    entries = data.get('entry', [])
    logger.info(f"Number of Instagram entries: {len(entries)}")
    
    for i, entry in enumerate(entries):
        logger.info(f"Processing Instagram entry {i+1}: {json.dumps(entry, indent=2)}")
        
        # Instagram messaging events
        messaging_events = entry.get('messaging', [])
        logger.info(f"Number of Instagram messaging events: {len(messaging_events)}")
        
        for j, messaging_event in enumerate(messaging_events):
            logger.info(f"Processing Instagram messaging event {j+1}: {json.dumps(messaging_event, indent=2)}")
            process_instagram_message_event(messaging_event)
    
    logger.info("Instagram webhook processing completed")
    return jsonify({'status': 'success'}), 200

def handle_page_webhook(data):
    """Handle Facebook Page webhook format (for Instagram connected to Pages)"""
    logger.info("Processing Facebook Page webhook...")
    
    entries = data.get('entry', [])
    logger.info(f"Number of Page entries: {len(entries)}")
    
    for i, entry in enumerate(entries):
        logger.info(f"Processing Page entry {i+1}: {json.dumps(entry, indent=2)}")
        
        # Page messaging events
        messaging_events = entry.get('messaging', [])
        logger.info(f"Number of Page messaging events: {len(messaging_events)}")
        
        for j, messaging_event in enumerate(messaging_events):
            logger.info(f"Processing Page messaging event {j+1}: {json.dumps(messaging_event, indent=2)}")
            process_page_message_event(messaging_event)
    
    logger.info("Page webhook processing completed")
    return jsonify({'status': 'success'}), 200

def process_instagram_message_event(messaging_event):
    """Process Instagram-specific message events"""
    sender_id = messaging_event.get('sender', {}).get('id')
    recipient_id = messaging_event.get('recipient', {}).get('id')
    
    logger.info(f"Instagram message - Sender: {sender_id}, Recipient: {recipient_id}")
    
    # Check if this is an incoming message (not sent by us)
    if 'message' in messaging_event and sender_id != recipient_id:
        message_text = messaging_event['message'].get('text', '')
        
        logger.info(f"Received Instagram message from {sender_id}: {message_text}")
        
        # Get user info
        user_info = message_handler.get_user_info(sender_id)
        username = user_info.get('username', 'User') if user_info else 'User'
        
        # Generate auto-reply
        reply_text = generate_auto_reply(message_text, username)
        logger.info(f"Generated reply: {reply_text}")
        
        # Send reply
        result = message_handler.send_message(sender_id, reply_text)
        if result:
            logger.info("Instagram reply sent successfully")
        else:
            logger.error("Failed to send Instagram reply")

def process_page_message_event(messaging_event):
    """Process Facebook Page message events (for Instagram connected to Pages)"""
    sender_id = messaging_event.get('sender', {}).get('id')
    recipient_id = messaging_event.get('recipient', {}).get('id')
    
    logger.info(f"Page message - Sender: {sender_id}, Recipient: {recipient_id}")
    
    # Check if this is an incoming message (not sent by us)
    if 'message' in messaging_event and sender_id != recipient_id:
        message_text = messaging_event['message'].get('text', '')
        
        logger.info(f"Received Page message from {sender_id}: {message_text}")
        
        # Get user info
        user_info = message_handler.get_user_info(sender_id)
        username = user_info.get('username', 'User') if user_info else 'User'
        
        # Generate auto-reply
        reply_text = generate_auto_reply(message_text, username)
        logger.info(f"Generated reply: {reply_text}")
        
        # Send reply
        result = message_handler.send_message(sender_id, reply_text)
        if result:
            logger.info("Page reply sent successfully")
        else:
            logger.error("Failed to send Page reply")

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
