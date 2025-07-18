import os
import json
import time
import requests
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
import hashlib
import hmac
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Instagram Messaging API configuration (uses Facebook Graph API)
ACCESS_TOKEN = os.getenv('INSTAGRAM_ACCESS_TOKEN')  # This should be a Page Access Token
APP_SECRET = os.getenv('INSTAGRAM_APP_SECRET')
IG_BUSINESS_ID = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')  # Instagram Business Account ID
WEBHOOK_VERIFY_TOKEN = "summy_webhook_verify_token_2025"

# In-memory storage
processed_messages = set()
webhook_events = []

def verify_webhook_signature(payload, signature):
    """Verify the webhook signature"""
    if not signature or not APP_SECRET:
        return False
    
    try:
        sig = signature.replace('sha256=', '') if signature.startswith('sha256=') else signature
        expected_signature = hmac.new(
            APP_SECRET.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(sig, expected_signature)
    except Exception as e:
        print(f"Error verifying signature: {e}")
        return False

def log_message(username, message_text, reply_text):
    """Log message to file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] FROM: {username} | MESSAGE: {message_text} | REPLY: {reply_text}\n"
    
    try:
        with open('messages.txt', 'a', encoding='utf-8') as f:
            f.write(log_entry)
        print(f"✅ Message logged: {username}")
    except Exception as e:
        print(f"Error logging message: {e}")

def get_user_info(user_id):
    """Get user information from Facebook Graph API (for Instagram users)"""
    try:
        # For Instagram users, we can try to get basic info
        url = f"https://graph.facebook.com/v19.0/{user_id}"
        params = {
            'access_token': ACCESS_TOKEN,
            'fields': 'id,name'
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return {'id': user_id, 'username': data.get('name', f'User_{user_id}')}
        else:
            print(f"Error getting user info: {response.status_code}")
            return {'id': user_id, 'username': f'User_{user_id}'}
    except Exception as e:
        print(f"Error getting user info for {user_id}: {e}")
        return {'id': user_id, 'username': f'User_{user_id}'}

# Note: Instagram Messaging API doesn't support conversations endpoint like Messenger
# Messages are handled directly via webhook recipient.id

def send_message(recipient_id, message_text):
    """Send message via Instagram Messaging API (Facebook Graph API)"""
    try:
        if not IG_BUSINESS_ID:
            print("❌ IG_BUSINESS_ID not configured")
            return None
            
        url = f"https://graph.facebook.com/v19.0/{IG_BUSINESS_ID}/messages"
        data = {
            "messaging_product": "instagram",
            "recipient": {"id": recipient_id},
            "message": {"text": message_text},
            "access_token": ACCESS_TOKEN
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print(f"✅ Instagram message sent to user {recipient_id}")
            return response.json()
        else:
            print(f"❌ Failed to send Instagram message: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Failed to send Instagram message to {recipient_id}: {e}")
        return None

def generate_auto_reply(username):
    """Generate auto-reply message"""
    return f"Hi {username}! Thanks for your message. I've received it and will get back to you soon! 🤖"

def process_webhook_message(messaging_event):
    """Process incoming webhook message"""
    try:
        print('🔔 WEBHOOK MESSAGE RECEIVED:', json.dumps(messaging_event, indent=2))
        
        sender = messaging_event.get('sender', {})
        recipient = messaging_event.get('recipient', {})
        message = messaging_event.get('message', {})
        
        from_user_id = sender.get('id')
        to_user_id = recipient.get('id')
        message_id = message.get('mid')
        message_text = message.get('text', '')
        timestamp = messaging_event.get('timestamp', '')
        is_echo = message.get('is_echo', False)
        
        print('🔔 PROCESSING MESSAGE:')
        print(f'   Message ID: {message_id}')
        print(f'   From User ID: {from_user_id}')
        print(f'   To User ID: {to_user_id}')
        print(f'   Message Text: "{message_text}"')
        print(f'   Is Echo: {is_echo}')
        
        # Skip echo messages (our own messages)
        if is_echo:
            print('   ⏭️  SKIPPING: Echo message (bot\'s own message)')
            return
        
        # Skip already processed messages
        if message_id in processed_messages:
            print('   ⏭️  SKIPPING: Already processed')
            return
        
        # Skip messages from bot account
        if not from_user_id or from_user_id == '17841473964575374':
            print('   ⏭️  SKIPPING: Bot\'s own message')
            processed_messages.add(message_id)
            return
        
        print(f'   ✅ NEW MESSAGE DETECTED from user {from_user_id}')
        
        # Get user info
        user_info = get_user_info(from_user_id)
        username = user_info.get('username', f'User_{from_user_id}')
        print(f'   👤 From: @{username}')
        
        # Generate reply
        reply_text = generate_auto_reply(username)
        print(f'   💬 Generating reply: {reply_text}')
        
        # Log message
        display_text = message_text or '[Webhook message - no text]'
        
        # Send reply directly to the user
        result = send_message(from_user_id, reply_text)
        if result:
            print('   ✅ Reply sent successfully!')
            log_message(username, display_text, reply_text)
        else:
            print('   ❌ Failed to send reply')
            log_message(username, display_text, 'Failed to send reply')
        
        # Mark as processed
        processed_messages.add(message_id)
        print('   📝 Message marked as processed')
        
    except Exception as e:
        print(f"❌ Error processing webhook message: {e}")

# Simple message display HTML template
SIMPLE_MESSAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>get_voyage Instagram Messages</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8f9fa;
            color: #333;
            padding: 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 28px;
            margin-bottom: 8px;
        }

        .header p {
            opacity: 0.9;
            font-size: 16px;
        }

        .stats {
            display: flex;
            justify-content: space-around;
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }

        .stat {
            text-align: center;
        }

        .stat-number {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }

        .stat-label {
            font-size: 14px;
            color: #6c757d;
            margin-top: 4px;
        }

        .messages-container {
            padding: 20px;
            max-height: 600px;
            overflow-y: auto;
        }

        .message {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
            border-left: 4px solid #667eea;
        }

        .message-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }

        .username {
            font-weight: bold;
            color: #667eea;
        }

        .timestamp {
            font-size: 12px;
            color: #6c757d;
        }

        .message-text {
            color: #333;
            margin-bottom: 8px;
        }

        .reply-text {
            background: #e3f2fd;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            color: #1976d2;
            border-left: 3px solid #1976d2;
        }

        .no-messages {
            text-align: center;
            padding: 40px;
            color: #6c757d;
        }

        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            margin: 20px;
            transition: background 0.3s;
        }

        .refresh-btn:hover {
            background: #5a6fd8;
        }

        .status {
            text-align: center;
            padding: 10px;
            background: #e8f5e8;
            color: #2e7d32;
            border-radius: 6px;
            margin: 20px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📱 get_voyage Instagram Messages</h1>
            <p>Messages received by @get_voyage on Instagram</p>
        </div>

        <div class="stats">
            <div class="stat">
                <div class="stat-number" id="total-messages">{{ total_messages }}</div>
                <div class="stat-label">Total Messages</div>
            </div>
            <div class="stat">
                <div class="stat-number" id="today-messages">{{ today_messages }}</div>
                <div class="stat-label">Today</div>
            </div>
            <div class="stat">
                <div class="stat-number" id="status-indicator">🟢</div>
                <div class="stat-label">Status</div>
            </div>
        </div>

        <div class="messages-container" id="messages-container">
            {% if messages %}
                {% for message in messages %}
                <div class="message">
                    <div class="message-header">
                        <span class="username">@{{ message.from }}</span>
                        <span class="timestamp">{{ message.timestamp }}</span>
                    </div>
                    <div class="message-text">{{ message.message }}</div>
                    <div class="reply-text">🤖 {{ message.reply }}</div>
                </div>
                {% endfor %}
            {% else %}
                <div class="no-messages">
                    <h3>📭 No messages yet</h3>
                    <p>Messages from Instagram will appear here when received</p>
                </div>
            {% endif %}
        </div>

        <div style="text-align: center; padding: 20px;">
            <button class="refresh-btn" onclick="loadMessages()">🔄 Refresh Messages</button>
        </div>

        <div class="status" id="status">
            ✅ Bot is running and monitoring for new messages
        </div>
    </div>

    <script>
        async function loadMessages() {
            try {
                const response = await fetch('/api/messages');
                const data = await response.json();
                
                const container = document.getElementById('messages-container');
                
                if (data.messages && data.messages.length > 0) {
                    container.innerHTML = data.messages.map(message => `
                        <div class="message">
                            <div class="message-header">
                                <span class="username">@${message.from}</span>
                                <span class="timestamp">${message.timestamp}</span>
                            </div>
                            <div class="message-text">${message.message}</div>
                            <div class="reply-text">🤖 ${message.reply}</div>
                        </div>
                    `).join('');
                } else {
                    container.innerHTML = `
                        <div class="no-messages">
                            <h3>📭 No messages yet</h3>
                            <p>Messages from Instagram will appear here when received</p>
                        </div>
                    `;
                }
                
                // Update stats
                document.getElementById('total-messages').textContent = data.messages ? data.messages.length : 0;
                
                // Update status
                document.getElementById('status').innerHTML = '✅ Bot is running and monitoring for new messages';
                document.getElementById('status-indicator').textContent = '🟢';
                
            } catch (error) {
                console.error('Error loading messages:', error);
                document.getElementById('status').innerHTML = '❌ Error loading messages';
                document.getElementById('status-indicator').textContent = '🔴';
            }
        }

        // Load messages on page load
        loadMessages();

        // Auto-refresh every 30 seconds
        setInterval(loadMessages, 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """Simple message display homepage"""
    # Get messages from the API
    try:
        if os.path.exists('messages.txt'):
            with open('messages.txt', 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = [line for line in content.strip().split('\n') if line.strip()]
            messages = []
            
            for line in lines:
                # Parse log format: [timestamp] FROM: username | MESSAGE: text | REPLY: reply
                import re
                match = re.match(r'\[(.*?)\] FROM: (.*?) \| MESSAGE: (.*?) \| REPLY: (.*)', line)
                if match:
                    messages.append({
                        'timestamp': match.group(1),
                        'from': match.group(2),
                        'message': match.group(3),
                        'reply': match.group(4)
                    })
        else:
            messages = []
    except Exception as e:
        print(f"Error loading messages: {e}")
        messages = []
    
    # Count today's messages
    today = datetime.now().strftime('%Y-%m-%d')
    today_messages = len([m for m in messages if m['timestamp'].startswith(today)])
    
    return render_template_string(SIMPLE_MESSAGE_HTML, 
                                messages=messages,
                                total_messages=len(messages),
                                today_messages=today_messages)

@app.route('/webhook', methods=['GET'])
def webhook_verify():
    """Webhook verification"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    print(f"Webhook verification: mode={mode}, token={token}")
    
    if mode == 'subscribe' and token == WEBHOOK_VERIFY_TOKEN:
        print('✅ Webhook verified successfully!')
        return challenge
    else:
        print('❌ Webhook verification failed')
        return 'Forbidden', 403

@app.route('/webhook', methods=['POST'])
def webhook_receive():
    """Webhook message receiver"""
    signature = request.headers.get('X-Hub-Signature-256', '')
    payload = request.get_data()
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    webhook_event = {
        'timestamp': timestamp,
        'type': 'webhook_received',
        'signature': signature[:20] + '...' if signature else 'none',
        'payload_size': len(payload),
        'status': 'processing'
    }
    
    webhook_events.append(webhook_event)
    
    print(f'🔔 WEBHOOK RECEIVED at {timestamp}')
    print(f'   Signature: {signature[:20]}...' if signature else '   No signature')
    print(f'   Payload size: {len(payload)} bytes')
    print(f'   Raw payload: {payload.decode("utf-8", errors="ignore")[:500]}...')
    
    # Verify signature (temporarily disabled for testing)
    signature_valid = verify_webhook_signature(payload, signature)
    if not signature_valid:
        print('   ⚠️  SIGNATURE VERIFICATION FAILED - PROCEEDING FOR TESTING')
        webhook_event['status'] = 'signature_failed_but_proceeding'
    else:
        print('   ✅ Signature verified successfully')
        webhook_event['status'] = 'signature_verified'
    
    try:
        data = request.get_json()
        if not data:
            print('   ❌ No JSON data in webhook')
            webhook_event['status'] = 'no_json'
            return 'Bad Request', 400
        
        print('   📋 JSON data parsed successfully')
        print(f'   📋 Full webhook data: {json.dumps(data, indent=2)}')
        webhook_event['data'] = data
        webhook_event['status'] = 'processing_messages'
        
        # Process webhook entries
        messages_processed = 0
        entries = data.get('entry', [])
        print(f'   📨 Found {len(entries)} entries in webhook')
        
        for i, entry in enumerate(entries):
            print(f'   📨 Processing entry {i+1}: {entry.get("id", "unknown")}')
            print(f'   📨 Entry keys: {list(entry.keys())}')
            
            if 'messaging' in entry:
                messaging_events = entry['messaging']
                print(f'   💬 Found {len(messaging_events)} messaging events')
                for j, messaging_event in enumerate(messaging_events):
                    print(f'   💬 Processing messaging event {j+1}')
                    process_webhook_message(messaging_event)
                    messages_processed += 1
            else:
                print(f'   ⚠️  No "messaging" field in entry. Available fields: {list(entry.keys())}')
        
        webhook_event['messages_processed'] = messages_processed
        webhook_event['status'] = 'completed'
        
        print(f'   ✅ Webhook processing completed - {messages_processed} messages processed')
        
        # Keep only last 50 webhook events
        if len(webhook_events) > 50:
            webhook_events[:] = webhook_events[-50:]
        
        return 'OK'
        
    except Exception as e:
        print(f'❌ Error processing webhook: {e}')
        import traceback
        print(f'❌ Full traceback: {traceback.format_exc()}')
        webhook_event['status'] = 'error'
        webhook_event['error'] = str(e)
        return 'Internal Server Error', 500

@app.route('/api/webhook-events')
def api_webhook_events():
    """API endpoint for webhook events"""
    return jsonify({
        'webhook_events': webhook_events[-10:],  # Last 10 events
        'total_events': len(webhook_events)
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Instagram messaging bot is running',
        'processed_messages': len(processed_messages),
        'polling': False
    })

@app.route('/api/messages')
def api_messages():
    """API endpoint for messages"""
    try:
        if os.path.exists('messages.txt'):
            with open('messages.txt', 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = [line for line in content.strip().split('\n') if line.strip()]
            messages = []
            
            for line in lines:
                # Parse log format: [timestamp] FROM: username | MESSAGE: text | REPLY: reply
                import re
                match = re.match(r'\[(.*?)\] FROM: (.*?) \| MESSAGE: (.*?) \| REPLY: (.*)', line)
                if match:
                    messages.append({
                        'timestamp': match.group(1),
                        'from': match.group(2),
                        'message': match.group(3),
                        'reply': match.group(4)
                    })
                else:
                    messages.append({'raw': line})
            
            return jsonify({'messages': list(reversed(messages))})  # Most recent first
        else:
            return jsonify({'messages': []})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug')
def debug():
    """Debug endpoint to check configuration"""
    return jsonify({
        'access_token_configured': bool(ACCESS_TOKEN),
        'app_secret_configured': bool(APP_SECRET),
        'ig_business_id_configured': bool(IG_BUSINESS_ID),
        'ig_business_id': IG_BUSINESS_ID[:10] + '...' if IG_BUSINESS_ID else None,
        'webhook_events_count': len(webhook_events),
        'processed_messages_count': len(processed_messages),
        'recent_webhook_events': webhook_events[-3:] if webhook_events else []
    })

@app.route('/test-message')
def test_message():
    """Test endpoint to simulate a message"""
    test_username = "test_user"
    test_message = "This is a test message from the bot"
    test_reply = "Hi test_user! Thanks for your message. I've received it and will get back to you soon! 🤖"
    
    # Log the test message
    log_message(test_username, test_message, test_reply)
    
    return jsonify({
        'status': 'success',
        'message': 'Test message logged successfully',
        'username': test_username,
        'message_text': test_message,
        'reply': test_reply
    })

if __name__ == '__main__':
    print('🚀 Instagram webhook bot starting...')
    print(f'📱 Webhook URL: https://summy-9f6d7e440dad.herokuapp.com/webhook')
    print(f'🔑 Verify Token: {WEBHOOK_VERIFY_TOKEN}')
    
    if not ACCESS_TOKEN:
        print('❌ INSTAGRAM_ACCESS_TOKEN not configured')
    if not APP_SECRET:
        print('❌ INSTAGRAM_APP_SECRET not configured')
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
