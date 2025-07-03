class InstagramMessagesApp {
    constructor() {
        this.messages = [];
        this.webhookEvents = [];
        this.isLoading = false;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadMessages();
        this.loadWebhookEvents();
        this.startAutoRefresh();
    }
    
    bindEvents() {
        const refreshBtn = document.getElementById('refresh-btn');
        refreshBtn.addEventListener('click', () => this.refreshData());
    }
    
    async loadMessages() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.updateStatus('Loading messages...', 'loading');
        
        try {
            const response = await fetch('/api/messages');
            const data = await response.json();
            
            if (response.ok) {
                this.messages = data.messages || [];
                this.renderMessages();
                this.updateStatus('Connected', 'success');
                this.updateMessageCount(this.messages.length);
            } else {
                throw new Error(data.error || 'Failed to load messages');
            }
        } catch (error) {
            console.error('Error loading messages:', error);
            this.updateStatus('Connection error', 'error');
            this.renderError('Failed to load messages: ' + error.message);
        } finally {
            this.isLoading = false;
        }
    }
    
    async loadWebhookEvents() {
        try {
            const response = await fetch('/api/webhook-events');
            const data = await response.json();
            
            if (response.ok) {
                this.webhookEvents = data.webhook_events || [];
                this.renderWebhookEvents();
            }
        } catch (error) {
            console.error('Error loading webhook events:', error);
        }
    }
    
    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();
            
            if (response.ok) {
                this.updateMessageCount(data.processed_messages || 0);
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }
    
    renderMessages() {
        const messagesList = document.getElementById('messages-list');
        
        if (this.messages.length === 0) {
            messagesList.innerHTML = `
                <div class="empty-state">
                    <h3>No messages yet</h3>
                    <p>Waiting for Instagram messages to arrive via webhook...</p>
                </div>
            `;
            return;
        }
        
        const messagesHtml = this.messages.map(message => {
            if (message.raw) {
                return `
                    <div class="message-item">
                        <div class="message-text">${this.escapeHtml(message.raw)}</div>
                    </div>
                `;
            }
            
            return `
                <div class="message-item">
                    <div class="message-header">
                        <span class="message-from">@${this.escapeHtml(message.from)}</span>
                        <span class="message-time">${this.formatTime(message.timestamp)}</span>
                    </div>
                    <div class="message-text">
                        ${this.escapeHtml(message.message)}
                    </div>
                    <div class="message-reply">
                        🤖 ${this.escapeHtml(message.reply)}
                    </div>
                </div>
            `;
        }).join('');
        
        messagesList.innerHTML = messagesHtml;
    }
    
    renderWebhookEvents() {
        const eventsList = document.getElementById('webhook-events-list');
        
        if (this.webhookEvents.length === 0) {
            eventsList.innerHTML = `
                <div class="empty-state">
                    <p>No webhook events yet</p>
                </div>
            `;
            return;
        }
        
        const eventsHtml = this.webhookEvents.map(event => {
            let className = 'webhook-event';
            if (event.status === 'completed' || event.status === 'signature_verified') {
                className += ' success';
            } else if (event.status === 'error') {
                className += ' error';
            } else if (event.status === 'signature_failed_but_proceeding') {
                className += ' warning';
            }
            
            return `
                <div class="${className}">
                    <div><strong>${event.timestamp}</strong></div>
                    <div>Status: ${event.status}</div>
                    <div>Messages: ${event.messages_processed || 0}</div>
                    <div>Size: ${event.payload_size} bytes</div>
                </div>
            `;
        }).join('');
        
        eventsList.innerHTML = eventsHtml;
    }
    
    renderError(message) {
        const messagesList = document.getElementById('messages-list');
        messagesList.innerHTML = `
            <div class="error-message">
                <strong>Error:</strong> ${this.escapeHtml(message)}
            </div>
        `;
    }
    
    updateStatus(text, type) {
        const statusText = document.getElementById('status-text');
        const statusDot = document.getElementById('status-dot');
        
        statusText.textContent = text;
        
        statusDot.className = 'status-dot';
        if (type === 'error') {
            statusDot.classList.add('error');
        }
    }
    
    updateMessageCount(count) {
        const messageCount = document.getElementById('message-count');
        messageCount.textContent = count;
    }
    
    async refreshData() {
        await Promise.all([
            this.loadMessages(),
            this.loadWebhookEvents(),
            this.loadStats()
        ]);
    }
    
    startAutoRefresh() {
        // Refresh every 10 seconds
        setInterval(() => {
            if (!this.isLoading) {
                this.refreshData();
            }
        }, 10000);
    }
    
    formatTime(timestamp) {
        try {
            const date = new Date(timestamp);
            return date.toLocaleString();
        } catch (error) {
            return timestamp;
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new InstagramMessagesApp();
});
