const express = require('express');
const bodyParser = require('body-parser');
const crypto = require('crypto');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5001;

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.raw({ type: 'application/json' }));
app.use(express.static('public'));

// Instagram API configuration
const ACCESS_TOKEN = process.env.INSTAGRAM_ACCESS_TOKEN;
const APP_SECRET = process.env.INSTAGRAM_APP_SECRET;
const BUSINESS_ACCOUNT_ID = process.env.INSTAGRAM_BUSINESS_ACCOUNT_ID;
const WEBHOOK_VERIFY_TOKEN = "summy_webhook_verify_token_2025";

// In-memory storage
let processedMessages = new Set();
let webhookEvents = [];

// Utility functions
function verifyWebhookSignature(payload, signature) {
    if (!signature || !APP_SECRET) return false;
    
    try {
        const sig = signature.startsWith('sha256=') ? signature.slice(7) : signature;
        const expectedSignature = crypto
            .createHmac('sha256', APP_SECRET)
            .update(payload)
            .digest('hex');
        
        return crypto.timingSafeEqual(
            Buffer.from(sig, 'hex'),
            Buffer.from(expectedSignature, 'hex')
        );
    } catch (error) {
        console.error('Error verifying signature:', error);
        return false;
    }
}

function logMessage(username, messageText, replyText) {
    const timestamp = new Date().toISOString().replace('T', ' ').slice(0, 19);
    const logEntry = `[${timestamp}] FROM: ${username} | MESSAGE: ${messageText} | REPLY: ${replyText}\n`;
    
    try {
        fs.appendFileSync('messages.txt', logEntry, 'utf8');
        console.log(`✅ Message logged: ${username}`);
    } catch (error) {
        console.error('Error logging message:', error);
    }
}

async function getUserInfo(userId) {
    try {
        const response = await axios.get(`https://graph.instagram.com/v19.0/${userId}`, {
            params: {
                access_token: ACCESS_TOKEN,
                fields: 'id,username'
            }
        });
        return response.data;
    } catch (error) {
        console.error(`Error getting user info for ${userId}:`, error.message);
        return { id: userId, username: `User_${userId}` };
    }
}

async function getConversations() {
    try {
        const response = await axios.get('https://graph.instagram.com/v19.0/me/conversations', {
            params: {
                access_token: ACCESS_TOKEN,
                fields: 'id,participants,updated_time'
            }
        });
        return response.data.data || [];
    } catch (error) {
        console.error('Error getting conversations:', error.message);
        return [];
    }
}

async function sendMessage(conversationId, messageText) {
    try {
        const response = await axios.post(
            `https://graph.instagram.com/v19.0/${conversationId}/messages`,
            {
                message: messageText,
                access_token: ACCESS_TOKEN
            }
        );
        console.log(`✅ Message sent to conversation ${conversationId}`);
        return response.data;
    } catch (error) {
        console.error(`❌ Failed to send message to ${conversationId}:`, error.message);
        return null;
    }
}

function generateAutoReply(username) {
    return `Hi ${username}! Thanks for your message. I've received it and will get back to you soon! 🤖`;
}

async function processWebhookMessage(messagingEvent) {
    try {
        console.log('🔔 WEBHOOK MESSAGE RECEIVED:', JSON.stringify(messagingEvent, null, 2));
        
        const sender = messagingEvent.sender || {};
        const recipient = messagingEvent.recipient || {};
        const message = messagingEvent.message || {};
        
        const fromUserId = sender.id;
        const toUserId = recipient.id;
        const messageId = message.mid;
        const messageText = message.text || '';
        const timestamp = messagingEvent.timestamp || '';
        const isEcho = message.is_echo || false;
        
        console.log('🔔 PROCESSING MESSAGE:');
        console.log(`   Message ID: ${messageId}`);
        console.log(`   From User ID: ${fromUserId}`);
        console.log(`   To User ID: ${toUserId}`);
        console.log(`   Message Text: '${messageText}'`);
        console.log(`   Is Echo: ${isEcho}`);
        
        // Skip echo messages (our own messages)
        if (isEcho) {
            console.log('   ⏭️  SKIPPING: Echo message (bot\'s own message)');
            return;
        }
        
        // Skip already processed messages
        if (processedMessages.has(messageId)) {
            console.log('   ⏭️  SKIPPING: Already processed');
            return;
        }
        
        // Skip messages from bot account (get_voyage's Instagram ID)
        if (!fromUserId || fromUserId === '17841473964575374') {
            console.log('   ⏭️  SKIPPING: Bot\'s own message');
            processedMessages.add(messageId);
            return;
        }
        
        console.log(`   ✅ NEW MESSAGE DETECTED from user ${fromUserId}`);
        
        // Get user info
        const userInfo = await getUserInfo(fromUserId);
        const username = userInfo.username || `User_${fromUserId}`;
        console.log(`   👤 From: @${username}`);
        
        // Generate reply
        const replyText = generateAutoReply(username);
        console.log(`   💬 Generating reply: ${replyText}`);
        
        // Find conversation ID
        const conversations = await getConversations();
        let conversationId = null;
        
        for (const conv of conversations) {
            const participants = conv.participants?.data || [];
            for (const participant of participants) {
                if (participant.id === fromUserId) {
                    conversationId = conv.id;
                    break;
                }
            }
            if (conversationId) break;
        }
        
        // Log message
        const displayText = messageText || '[Webhook message - no text]';
        
        if (conversationId) {
            // Send reply
            const result = await sendMessage(conversationId, replyText);
            if (result) {
                console.log('   ✅ Reply sent successfully!');
                logMessage(username, displayText, replyText);
            } else {
                console.log('   ❌ Failed to send reply');
                logMessage(username, displayText, 'Failed to send reply');
            }
        } else {
            console.log('   ⚠️  Could not find conversation ID');
            logMessage(username, displayText, 'Could not send reply - conversation not found');
        }
        
        // Mark as processed
        processedMessages.add(messageId);
        console.log('   📝 Message marked as processed');
        
    } catch (error) {
        console.error('❌ Error processing webhook message:', error);
    }
}

// Routes
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Webhook verification
app.get('/webhook', (req, res) => {
    const mode = req.query['hub.mode'];
    const token = req.query['hub.verify_token'];
    const challenge = req.query['hub.challenge'];
    
    console.log(`Webhook verification: mode=${mode}, token=${token}`);
    
    if (mode === 'subscribe' && token === WEBHOOK_VERIFY_TOKEN) {
        console.log('✅ Webhook verified successfully!');
        res.status(200).send(challenge);
    } else {
        console.log('❌ Webhook verification failed');
        res.status(403).send('Forbidden');
    }
});

// Webhook message receiver
app.post('/webhook', (req, res) => {
    const signature = req.headers['x-hub-signature-256'] || '';
    const payload = JSON.stringify(req.body);
    
    const timestamp = new Date().toISOString().replace('T', ' ').slice(0, 19);
    const webhookEvent = {
        timestamp,
        type: 'webhook_received',
        signature: signature.slice(0, 20) + '...',
        payload_size: payload.length,
        status: 'processing'
    };
    
    webhookEvents.push(webhookEvent);
    
    console.log(`🔔 WEBHOOK RECEIVED at ${timestamp}`);
    console.log(`   Signature: ${signature.slice(0, 20)}...`);
    console.log(`   Payload size: ${payload.length} bytes`);
    
    // Verify signature (temporarily disabled for testing)
    const signatureValid = verifyWebhookSignature(payload, signature);
    if (!signatureValid) {
        console.log('   ⚠️  SIGNATURE VERIFICATION FAILED - PROCEEDING FOR TESTING');
        webhookEvent.status = 'signature_failed_but_proceeding';
    } else {
        console.log('   ✅ Signature verified successfully');
        webhookEvent.status = 'signature_verified';
    }
    
    const data = req.body;
    if (!data) {
        console.log('   ❌ No JSON data in webhook');
        webhookEvent.status = 'no_json';
        return res.status(400).send('Bad Request');
    }
    
    console.log('   📋 JSON data parsed successfully');
    webhookEvent.data = data;
    webhookEvent.status = 'processing_messages';
    
    // Process webhook entries
    let messagesProcessed = 0;
    const entries = data.entry || [];
    
    for (const entry of entries) {
        console.log(`   📨 Processing entry: ${entry.id || 'unknown'}`);
        
        if (entry.messaging) {
            for (const messagingEvent of entry.messaging) {
                console.log('   💬 Found messaging event');
                processWebhookMessage(messagingEvent);
                messagesProcessed++;
            }
        }
    }
    
    webhookEvent.messages_processed = messagesProcessed;
    webhookEvent.status = 'completed';
    
    console.log(`   ✅ Webhook processing completed - ${messagesProcessed} messages processed`);
    
    // Keep only last 50 webhook events
    if (webhookEvents.length > 50) {
        webhookEvents = webhookEvents.slice(-50);
    }
    
    res.status(200).send('OK');
});

// API endpoints
app.get('/api/messages', (req, res) => {
    try {
        if (fs.existsSync('messages.txt')) {
            const content = fs.readFileSync('messages.txt', 'utf8');
            const lines = content.trim().split('\n').filter(line => line.length > 0);
            
            const messages = lines.map(line => {
                const match = line.match(/\[(.*?)\] FROM: (.*?) \| MESSAGE: (.*?) \| REPLY: (.*)/);
                if (match) {
                    return {
                        timestamp: match[1],
                        from: match[2],
                        message: match[3],
                        reply: match[4]
                    };
                }
                return { raw: line };
            });
            
            res.json({ messages: messages.reverse() }); // Most recent first
        } else {
            res.json({ messages: [] });
        }
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.get('/api/webhook-events', (req, res) => {
    res.json({
        webhook_events: webhookEvents.slice(-10), // Last 10 events
        total_events: webhookEvents.length
    });
});

app.get('/api/stats', (req, res) => {
    res.json({
        processed_messages: processedMessages.size,
        webhook_events: webhookEvents.length,
        access_token_configured: !!ACCESS_TOKEN,
        app_secret_configured: !!APP_SECRET
    });
});

// Health check
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        message: 'Instagram webhook bot is running',
        processed_messages: processedMessages.size
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 Node.js Instagram webhook bot running on port ${PORT}`);
    console.log(`📱 Webhook URL: https://summy-9f6d7e440dad.herokuapp.com/webhook`);
    console.log(`🔑 Verify Token: ${WEBHOOK_VERIFY_TOKEN}`);
    console.log(`📋 Node.js app successfully deployed! v2.1`);
    
    if (!ACCESS_TOKEN) {
        console.error('❌ INSTAGRAM_ACCESS_TOKEN not configured');
    }
    if (!APP_SECRET) {
        console.error('❌ INSTAGRAM_APP_SECRET not configured');
    }
});
