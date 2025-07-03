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

# Instagram Graph API credentials
ACCESS_TOKEN = os.getenv('INSTAGRAM_ACCESS_TOKEN')
APP_SECRET = os.getenv('INSTAGRAM_APP_SECRET')
BUSINESS_ACCOUNT_ID = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')

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
            'fields': 'id,created_time,from,to,message,attachments',
            'limit': 10  # Get last 10 messages
        }
        
        try:
            response = requests.get(url, params=params)
            logger.info(f"Messages API Response for {conversation_id}: {response.status_code}")
            logger.info(f"Messages API Full Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json().get('data', [])
                logger.info(f"Messages returned: {len(data)}")
                return data
            else:
                logger.error(f"Failed to get messages for {conversation_id}: {response.text}")
                # Try alternative endpoint
                return self.try_alternative_messages_endpoint(conversation_id)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting messages for {conversation_id}: {e}")
            return []
    
    def try_alternative_messages_endpoint(self, conversation_id):
        """Try alternative messages endpoint"""
        # Try without specific fields
        url = f"{self.base_url}/{conversation_id}/messages"
        params = {
            'access_token': self.access_token,
            'limit': 10
        }
        
        try:
            response = requests.get(url, params=params)
            logger.info(f"Alternative Messages API Response: {response.status_code}")
            logger.info(f"Alternative Messages API Response: {response.text}")
            
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                logger.error(f"Alternative endpoint also failed: {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error with alternative endpoint: {e}")
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
        print("=" * 80)
        print("🔍 CHECKING FOR NEW MESSAGES...")
        logger.info("Checking for new messages...")
        
        conversations = self.get_conversations()
        print(f"📋 Found {len(conversations)} conversations")
        logger.info(f"Found {len(conversations)} conversations")
        
        for conversation in conversations:
            conversation_id = conversation['id']
            print(f"\n💬 Checking conversation: {conversation_id}")
            messages = self.get_conversation_messages(conversation_id)
            
            print(f"📨 Found {len(messages)} messages in this conversation")
            logger.info(f"Conversation {conversation_id}: Found {len(messages)} messages")
            
            # Debug: Log all messages in this conversation
            for i, message in enumerate(messages):
                print(f"  Message {i+1}:")
                print(f"    ID: {message.get('id')}")
                print(f"    From: {message.get('from', {})}")
                print(f"    Text: '{message.get('message', 'No text')}'")
                print(f"    Created: {message.get('created_time', 'No time')}")
                logger.info(f"Message {i+1}: ID={message.get('id')}, From={message.get('from', {})}, Message={message.get('message', 'No text')}")
            
            for message in messages:
                message_id = message['id']
                
                # Skip if we've already processed this message
                if message_id in self.processed_messages:
                    logger.info(f"Skipping already processed message: {message_id}")
                    continue
                
                # Get message details
                from_user = message.get('from', {})
                from_user_id = from_user.get('id')
                message_text = message.get('message', '')
                created_time = message.get('created_time', '')
                
                print(f"🔍 PROCESSING MESSAGE:")
                print(f"   ID: {message_id}")
                print(f"   From User ID: {from_user_id}")
                print(f"   Message Text: '{message_text}'")
                print(f"   Created: {created_time}")
                
                logger.info(f"Processing message: ID={message_id}, From={from_user_id}, Text='{message_text}'")
                
                # Skip if this is our own message (from bot)
                # Check if from_user_id matches our bot's Instagram account ID
                if not from_user_id or from_user_id == '17841473964575374':  # get_voyage's Instagram ID
                    print(f"   ⏭️  SKIPPING: Bot's own message")
                    logger.info(f"Skipping bot's own message: {message_id}")
                    self.processed_messages.add(message_id)
                    continue
                
                # Process message even if text is empty (Instagram API might not return text)
                print(f"   ✅ NEW MESSAGE DETECTED from user {from_user_id}")
                logger.info(f"NEW MESSAGE DETECTED from {from_user_id}: {message_text}")
                
                # Get user info
                user_info = self.get_user_info(from_user_id)
                username = user_info.get('username', 'User')
                print(f"   👤 From: @{username}")
                
                # Generate and send reply
                reply_text = self.generate_auto_reply(username)
                print(f"   💬 Sending reply: {reply_text}")
                logger.info(f"Sending reply: {reply_text}")
                
                # Log message to file (even if text is empty)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                display_text = message_text if message_text else "[No text content available from API]"
                self.log_message_to_file(username, display_text, reply_text, timestamp)
                
                result = self.send_message(conversation_id, reply_text)
                if result:
                    print(f"   ✅ Reply sent successfully!")
                    logger.info("Reply sent successfully")
                else:
                    print(f"   ❌ Failed to send reply")
                    logger.error("Failed to send reply")
                
                # Mark message as processed
                self.processed_messages.add(message_id)
                print(f"   📝 Message marked as processed")
    
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
    """Console-style frontend"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Instagram Bot Console</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Courier New', monospace;
                background: white;
                color: black;
                overflow: hidden;
                font-weight: bold;
            }
            
            .console-container {
                height: 100vh;
                display: flex;
                flex-direction: column;
                padding: 20px;
            }
            
            .header {
                border-bottom: 2px solid black;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }
            
            .header h1 {
                color: black;
                font-size: 24px;
                font-weight: bold;
            }
            
            .status-bar {
                display: flex;
                justify-content: space-between;
                margin-bottom: 20px;
                padding: 10px;
                background: #f5f5f5;
                border: 1px solid black;
            }
            
            .status-item {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .status-dot {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: green;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
            
            .console-output {
                flex: 1;
                background: white;
                border: 1px solid black;
                padding: 15px;
                overflow-y: auto;
                font-size: 14px;
                line-height: 1.4;
            }
            
            .log-entry {
                margin-bottom: 5px;
                padding: 2px 0;
            }
            
            .log-timestamp {
                color: #666;
            }
            
            .log-info {
                color: black;
            }
            
            .log-message {
                color: #0066cc;
                font-weight: bold;
            }
            
            .log-reply {
                color: #009900;
            }
            
            .log-error {
                color: #cc0000;
            }
            
            .log-polling {
                color: #666;
            }
            
            .cursor {
                animation: blink 1s infinite;
            }
            
            @keyframes blink {
                0%, 50% { opacity: 1; }
                51%, 100% { opacity: 0; }
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 10px;
                margin-bottom: 20px;
            }
            
            .stat-box {
                background: #f5f5f5;
                border: 1px solid black;
                padding: 10px;
                text-align: center;
            }
            
            .stat-value {
                font-size: 24px;
                font-weight: bold;
                color: black;
            }
            
            .stat-label {
                font-size: 12px;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="console-container">
            <div class="header">
                <h1>INSTAGRAM BOT CONSOLE v2.0</h1>
                <div class="status-bar">
                    <div class="status-item">
                        <div class="status-dot"></div>
                        <span>POLLING ACTIVE</span>
                    </div>
                    <div class="status-item">
                        <span id="current-time"></span>
                    </div>
                    <div class="status-item">
                        <span>STATUS: <span id="bot-status">ONLINE</span></span>
                    </div>
                </div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-value" id="processed-count">0</div>
                    <div class="stat-label">MESSAGES PROCESSED</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" id="conversations-count">0</div>
                    <div class="stat-label">ACTIVE CONVERSATIONS</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" id="uptime">00:00:00</div>
                    <div class="stat-label">UPTIME</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" id="last-poll">Never</div>
                    <div class="stat-label">LAST POLL</div>
                </div>
            </div>
            
            <div class="console-output" id="console-output">
                <div class="log-entry log-info">
                    <span class="log-timestamp">[SYSTEM]</span> Instagram Bot Console initialized
                </div>
                <div class="log-entry log-info">
                    <span class="log-timestamp">[SYSTEM]</span> Connecting to Instagram Messaging API...
                </div>
                <div class="log-entry log-info">
                    <span class="log-timestamp">[SYSTEM]</span> Polling started - checking every 5 seconds
                </div>
                <div class="log-entry log-polling">
                    <span class="log-timestamp">[POLL]</span> Waiting for messages... <span class="cursor">_</span>
                </div>
            </div>
        </div>
        
        <script>
            let startTime = Date.now();
            let lastLogCount = 0;
            
            // Update current time
            function updateTime() {
                const now = new Date();
                document.getElementById('current-time').textContent = now.toLocaleTimeString();
            }
            
            // Update uptime
            function updateUptime() {
                const elapsed = Date.now() - startTime;
                const hours = Math.floor(elapsed / 3600000);
                const minutes = Math.floor((elapsed % 3600000) / 60000);
                const seconds = Math.floor((elapsed % 60000) / 1000);
                document.getElementById('uptime').textContent = 
                    `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }
            
            // Add log entry
            function addLog(type, message) {
                const output = document.getElementById('console-output');
                const timestamp = new Date().toLocaleTimeString();
                const entry = document.createElement('div');
                entry.className = `log-entry log-${type}`;
                entry.innerHTML = `<span class="log-timestamp">[${timestamp}]</span> ${message}`;
                output.appendChild(entry);
                output.scrollTop = output.scrollHeight;
                
                // Keep only last 100 entries
                while (output.children.length > 100) {
                    output.removeChild(output.firstChild);
                }
            }
            
            // Fetch bot stats
            async function fetchStats() {
                try {
                    const [healthResponse, statsResponse, conversationsResponse] = await Promise.all([
                        fetch('/health'),
                        fetch('/stats'),
                        fetch('/test-conversations')
                    ]);
                    
                    const health = await healthResponse.json();
                    const stats = await statsResponse.json();
                    const conversations = await conversationsResponse.json();
                    
                    // Update stats display
                    document.getElementById('processed-count').textContent = health.processed_messages || 0;
                    document.getElementById('conversations-count').textContent = conversations.conversations_count || 0;
                    document.getElementById('bot-status').textContent = health.polling ? 'ONLINE' : 'OFFLINE';
                    document.getElementById('last-poll').textContent = new Date().toLocaleTimeString();
                    
                    // Check for new messages
                    const currentCount = health.processed_messages || 0;
                    if (currentCount > lastLogCount) {
                        const newMessages = currentCount - lastLogCount;
                        addLog('message', `📨 ${newMessages} new message(s) processed`);
                        lastLogCount = currentCount;
                    }
                    
                    // Add polling log
                    addLog('polling', `🔄 Polling completed - ${conversations.conversations_count} conversations checked`);
                    
                } catch (error) {
                    addLog('error', `❌ Error fetching stats: ${error.message}`);
                    document.getElementById('bot-status').textContent = 'ERROR';
                }
            }
            
            // Simulate message activity for demo
            function simulateActivity() {
                const activities = [
                    'info|🔍 Scanning conversations for new messages...',
                    'polling|⏱️ Waiting 5 seconds before next poll...',
                    'info|📡 API connection stable',
                    'polling|🔄 Checking Instagram Messaging API...'
                ];
                
                const activity = activities[Math.floor(Math.random() * activities.length)];
                const [type, message] = activity.split('|');
                addLog(type, message);
            }
            
            // Initialize
            updateTime();
            updateUptime();
            fetchStats();
            
            // Set intervals
            setInterval(updateTime, 1000);
            setInterval(updateUptime, 1000);
            setInterval(fetchStats, 10000); // Every 10 seconds
            setInterval(simulateActivity, 15000); // Every 15 seconds
            
            // Initial activity simulation
            setTimeout(() => addLog('info', '✅ Bot initialization complete'), 2000);
            setTimeout(() => addLog('info', '🎯 Ready to receive Instagram messages'), 3000);
        </script>
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

@app.route('/debug', methods=['GET'])
def debug_info():
    """Debug endpoint to show detailed bot information"""
    try:
        # Get conversations and their messages
        conversations = bot.get_conversations()
        debug_data = {
            'bot_status': {
                'running': bot.running,
                'processed_messages': list(bot.processed_messages),
                'processed_count': len(bot.processed_messages)
            },
            'conversations': []
        }
        
        for conv in conversations[:3]:  # Limit to first 3 conversations
            conv_id = conv['id']
            messages = bot.get_conversation_messages(conv_id)
            
            conv_debug = {
                'id': conv_id,
                'participants': conv.get('participants', []),
                'message_count': len(messages),
                'messages': []
            }
            
            for msg in messages[:5]:  # Limit to first 5 messages per conversation
                conv_debug['messages'].append({
                    'id': msg.get('id'),
                    'from': msg.get('from', {}),
                    'message': msg.get('message', ''),
                    'created_time': msg.get('created_time', ''),
                    'processed': msg.get('id') in bot.processed_messages
                })
            
            debug_data['conversations'].append(conv_debug)
        
        return jsonify(debug_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/processed-messages', methods=['GET'])
def show_processed_messages():
    """Show actual content of processed messages"""
    try:
        processed_details = []
        conversations = bot.get_conversations()
        
        for conv in conversations:
            conv_id = conv['id']
            messages = bot.get_conversation_messages(conv_id)
            
            for msg in messages:
                if msg.get('id') in bot.processed_messages:
                    # Get user info
                    from_user = msg.get('from', {})
                    from_user_id = from_user.get('id')
                    
                    if from_user_id and from_user_id != '17841473964575374':  # Not bot's own message
                        user_info = bot.get_user_info(from_user_id)
                        
                        processed_details.append({
                            'message_id': msg.get('id'),
                            'conversation_id': conv_id,
                            'from_user_id': from_user_id,
                            'from_username': user_info.get('username', 'Unknown'),
                            'message_text': msg.get('message', ''),
                            'created_time': msg.get('created_time', ''),
                            'participants': [p.get('username', p.get('id')) for p in conv.get('participants', {}).get('data', [])]
                        })
        
        return jsonify({
            'processed_messages_count': len(processed_details),
            'processed_messages': processed_details
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
