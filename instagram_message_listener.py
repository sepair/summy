import os
import requests
import json
import time
import threading
from datetime import datetime
from flask import Flask, jsonify, send_file
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

class InstagramMessagingBot:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://graph.instagram.com/v19.0"
        self.processed_messages = set()  # Track processed message IDs
        self.running = False
        
    def get_conversations(self):
        """Get list of conversations"""
        url = f"{self.base_url}/me/conversations"
        params = {
            'access_token': self.access_token,
            'fields': 'id,participants,updated_time'
        }
        
        try:
            response = requests.get(url, params=params)
            logger.info(f"Conversations API Response: {response.status_code}")
            
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                logger.error(f"Failed to get conversations: {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting conversations: {e}")
            return []
    
    def get_conversation_messages(self, conversation_id):
        """Get messages from a specific conversation"""
        url = f"{self.base_url}/{conversation_id}/messages"
        params = {
            'access_token': self.access_token,
            'fields': 'id,created_time,from,to,message',
            'limit': 10  # Get last 10 messages
        }
        
        try:
            response = requests.get(url, params=params)
            logger.info(f"Messages API Response for {conversation_id}: {response.status_code}")
            
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                logger.error(f"Failed to get messages for {conversation_id}: {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting messages for {conversation_id}: {e}")
            return []
    
    def send_message(self, conversation_id, message_text):
        """Send a message to a conversation"""
        url = f"{self.base_url}/{conversation_id}/messages"
        
        payload = {
            'message': message_text,
            'access_token': self.access_token
        }
        
        try:
            response = requests.post(url, data=payload)
            logger.info(f"Send message API Response: {response.status_code}")
            logger.info(f"Send message response: {response.text}")
            
            if response.status_code == 200:
                logger.info(f"Message sent successfully to conversation {conversation_id}")
                return response.json()
            else:
                logger.error(f"Failed to send message: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending message: {e}")
            return None
    
    def get_user_info(self, user_id):
        """Get user information"""
        url = f"{self.base_url}/{user_id}"
        params = {
            'access_token': self.access_token,
            'fields': 'id,username'
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get user info for {user_id}: {response.text}")
                return {'id': user_id, 'username': 'User'}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting user info: {e}")
            return {'id': user_id, 'username': 'User'}
    
    def log_message_to_file(self, username, message_text, reply_text, timestamp):
        """Log message and reply to a text file"""
        try:
            log_entry = f"[{timestamp}] FROM: {username} | MESSAGE: {message_text} | REPLY: {reply_text}\n"
            
            with open('messages.txt', 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            logger.info(f"Message logged to file: {username}")
        except Exception as e:
            logger.error(f"Error logging message to file: {e}")
    
    def generate_auto_reply(self, username):
        """Generate a simple automatic reply"""
        return f"Hi {username}! Thanks for your message. I've received it and will get back to you soon! 🤖"
    
    def process_new_messages(self):
        """Check for new messages and respond"""
        logger.info("Checking for new messages...")
        
        conversations = self.get_conversations()
        logger.info(f"Found {len(conversations)} conversations")
        
        for conversation in conversations:
            conversation_id = conversation['id']
            messages = self.get_conversation_messages(conversation_id)
            
            for message in messages:
                message_id = message['id']
                
                # Skip if we've already processed this message
                if message_id in self.processed_messages:
                    continue
                
                # Skip if this is our own message (from bot)
                from_user = message.get('from', {})
                if from_user.get('id') == 'me':  # This would be our bot's messages
                    self.processed_messages.add(message_id)
                    continue
                
                # Process new incoming message
                message_text = message.get('message', '')
                from_user_id = from_user.get('id')
                
                logger.info(f"New message from {from_user_id}: {message_text}")
                
                # Get user info
                user_info = self.get_user_info(from_user_id)
                username = user_info.get('username', 'User')
                
                # Generate and send reply
                reply_text = self.generate_auto_reply(username)
                logger.info(f"Sending reply: {reply_text}")
                
                # Log message to file
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.log_message_to_file(username, message_text, reply_text, timestamp)
                
                result = self.send_message(conversation_id, reply_text)
                if result:
                    logger.info("Reply sent successfully")
                else:
                    logger.error("Failed to send reply")
                
                # Mark message as processed
                self.processed_messages.add(message_id)
    
    def start_polling(self):
        """Start polling for messages"""
        self.running = True
        logger.info("Starting Instagram message polling...")
        
        while self.running:
            try:
                self.process_new_messages()
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                time.sleep(10)  # Wait longer on error
    
    def stop_polling(self):
        """Stop polling for messages"""
        self.running = False
        logger.info("Stopped Instagram message polling")

# Initialize bot
bot = InstagramMessagingBot(ACCESS_TOKEN)

# Start polling in background thread
def start_background_polling():
    if ACCESS_TOKEN:
        polling_thread = threading.Thread(target=bot.start_polling, daemon=True)
        polling_thread.start()
        logger.info("Background polling thread started")
    else:
        logger.error("No access token provided - polling not started")

@app.route('/', methods=['GET'])
def landing_page():
    """Simple landing page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Instagram Messaging Bot</title>
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
            <h1>Instagram Bot</h1>
            <p>Instagram Messaging API Bot is Running</p>
            <p>🤖 Polling for messages every 5 seconds</p>
        </div>
    </body>
    </html>
    """

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    status = {
        'status': 'healthy',
        'message': 'Instagram messaging bot is running',
        'polling': bot.running,
        'processed_messages': len(bot.processed_messages)
    }
    return jsonify(status), 200

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get bot statistics"""
    stats = {
        'running': bot.running,
        'processed_messages_count': len(bot.processed_messages),
        'access_token_configured': bool(ACCESS_TOKEN)
    }
    return jsonify(stats), 200

@app.route('/test-conversations', methods=['GET'])
def test_conversations():
    """Test endpoint to check conversations"""
    conversations = bot.get_conversations()
    return jsonify({
        'conversations_count': len(conversations),
        'conversations': conversations
    }), 200

@app.route('/messages', methods=['GET'])
def view_messages():
    """View the messages log file"""
    try:
        if os.path.exists('messages.txt'):
            return send_file('messages.txt', as_attachment=False, mimetype='text/plain')
        else:
            return "No messages logged yet.", 200
    except Exception as e:
        return f"Error reading messages file: {e}", 500

@app.route('/messages/download', methods=['GET'])
def download_messages():
    """Download the messages log file"""
    try:
        if os.path.exists('messages.txt'):
            return send_file('messages.txt', as_attachment=True, download_name='instagram_messages.txt')
        else:
            return "No messages logged yet.", 404
    except Exception as e:
        return f"Error downloading messages file: {e}", 500

if __name__ == '__main__':
    # Check if required environment variables are set
    if not ACCESS_TOKEN:
        logger.error("INSTAGRAM_ACCESS_TOKEN not found in environment variables")
        exit(1)
    
    if not APP_SECRET:
        logger.error("INSTAGRAM_APP_SECRET not found in environment variables")
        exit(1)
    
    logger.info("Starting Instagram Messaging API bot...")
    logger.info("This bot uses polling instead of webhooks")
    logger.info("Make sure your Instagram account has messaging permissions")
    
    # Start background polling
    start_background_polling()
    
    # Run the Flask app
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
