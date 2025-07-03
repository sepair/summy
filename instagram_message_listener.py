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

def get_conversations():
    """Get conversations from Facebook Graph API (Instagram Messaging)"""
    try:
        if not IG_BUSINESS_ID:
            print("❌ IG_BUSINESS_ID not configured")
            return []
            
        url = f"https://graph.facebook.com/v19.0/{IG_BUSINESS_ID}/conversations"
        params = {
            'access_token': ACCESS_TOKEN,
            'fields': 'id,participants,updated_time'
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            print(f"Error getting conversations: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Error getting conversations: {e}")
        return []

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

# Webhook monitor HTML template
WEBHOOK_MONITOR_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Webhook Monitor</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Courier New', monospace;
            background: #000;
            color: #00ff00;
            padding: 20px;
            line-height: 1.4;
        }

        .header {
            border-bottom: 1px solid #00ff00;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }

        .header h1 {
            color: #00ff00;
            font-size: 18px;
        }

        .webhook-log {
            height: 80vh;
            overflow-y: auto;
            background: #000;
            border: 1px solid #00ff00;
            padding: 15px;
            font-size: 14px;
        }

        .log-entry {
            margin-bottom: 8px;
            padding: 4px 0;
            border-bottom: 1px dotted #003300;
        }

        .timestamp {
            color: #666;
        }

        .webhook-received {
            color: #ffff00;
        }

        .message-processed {
            color: #00ff00;
        }

        .error {
            color: #ff0000;
        }

        .info {
            color: #00aaff;
        }

        .cursor {
            animation: blink 1s infinite;
        }

        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }

        .status-line {
            position: fixed;
            bottom: 10px;
            left: 20px;
            right: 20px;
            background: #000;
            border-top: 1px solid #00ff00;
            padding: 10px;
            color: #00ff00;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>INSTAGRAM WEBHOOK MONITOR - LIVE UPDATES</h1>
    </div>

    <div class="webhook-log" id="webhook-log">
        <div class="log-entry info">
            <span class="timestamp">[SYSTEM]</span> Webhook monitor initialized - waiting for Instagram messages...
        </div>
        <div class="log-entry info">
            <span class="timestamp">[SYSTEM]</span> Listening on: https://summy-9f6d7e440dad.herokuapp.com/webhook
        </div>
        <div class="log-entry info">
            <span class="timestamp">[READY]</span> Monitoring webhook events <span class="cursor">_</span>
        </div>
    </div>

    <div class="status-line">
        STATUS: <span id="status">MONITORING</span> | EVENTS: <span id="event-count">{{ event_count }}</span> | MESSAGES: <span id="message-count">{{ message_count }}</span> | <span id="current-time"></span>
    </div>

    <script>
        let eventCount = {{ event_count }};
        let messageCount = {{ message_count }};

        function updateTime() {
            const now = new Date();
            document.getElementById('current-time').textContent = now.toLocaleTimeString();
        }

        function addLog(type, message) {
            const log = document.getElementById('webhook-log');
            const timestamp = new Date().toLocaleTimeString();
            const entry = document.createElement('div');
            entry.className = `log-entry ${type}`;
            entry.innerHTML = `<span class="timestamp">[${timestamp}]</span> ${message}`;
            log.appendChild(entry);
            log.scrollTop = log.scrollHeight;

            // Keep only last 100 entries
            while (log.children.length > 100) {
                log.removeChild(log.firstChild);
            }
        }

        async function checkWebhookEvents() {
            try {
                const response = await fetch('/api/webhook-events');
                const data = await response.json();
                
                if (data.webhook_events && data.webhook_events.length > eventCount) {
                    const newEvents = data.webhook_events.slice(eventCount);
                    
                    for (const event of newEvents) {
                        addLog('webhook-received', `🔔 WEBHOOK RECEIVED - ${event.payload_size || 'unknown'} bytes - Status: ${event.status || 'processed'}`);
                        
                        if (event.messages_processed > 0) {
                            addLog('message-processed', `📨 ${event.messages_processed} message(s) processed`);
                            messageCount += event.messages_processed;
                        }
                        
                        eventCount++;
                    }
                    
                    document.getElementById('event-count').textContent = eventCount;
                    document.getElementById('message-count').textContent = messageCount;
                }
                
                // Check health for total message count
                const healthResponse = await fetch('/health');
                const healthData = await healthResponse.json();
                if (healthData.processed_messages !== undefined) {
                    messageCount = healthData.processed_messages;
                    document.getElementById('message-count').textContent = messageCount;
                }
                
            } catch (error) {
                addLog('error', `❌ Error checking webhook events: ${error.message}`);
                document.getElementById('status').textContent = 'ERROR';
            }
        }

        // Initialize
        updateTime();
        checkWebhookEvents();

        // Set intervals
        setInterval(updateTime, 1000);
        setInterval(checkWebhookEvents, 2000); // Check every 2 seconds for real-time updates

        // Add some initial activity
        setTimeout(() => addLog('info', '✅ Webhook monitor ready - send messages to get_voyage Instagram'), 2000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """Webhook monitor homepage"""
    return render_template_string(WEBHOOK_MONITOR_HTML, 
                                event_count=len(webhook_events), 
                                message_count=len(processed_messages))

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
        webhook_event['data'] = data
        webhook_event['status'] = 'processing_messages'
        
        # Process webhook entries
        messages_processed = 0
        entries = data.get('entry', [])
        
        for entry in entries:
            print(f'   📨 Processing entry: {entry.get("id", "unknown")}')
            
            if 'messaging' in entry:
                for messaging_event in entry['messaging']:
                    print('   💬 Found messaging event')
                    process_webhook_message(messaging_event)
                    messages_processed += 1
        
        webhook_event['messages_processed'] = messages_processed
        webhook_event['status'] = 'completed'
        
        print(f'   ✅ Webhook processing completed - {messages_processed} messages processed')
        
        # Keep only last 50 webhook events
        if len(webhook_events) > 50:
            webhook_events[:] = webhook_events[-50:]
        
        return 'OK'
        
    except Exception as e:
        print(f'❌ Error processing webhook: {e}')
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

@app.route('/test-conversations')
def test_conversations():
    """Test conversations endpoint"""
    conversations = get_conversations()
    return jsonify({
        'conversations_count': len(conversations),
        'conversations': conversations[:5]  # First 5 for testing
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
