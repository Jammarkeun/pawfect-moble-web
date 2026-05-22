class PawfectChat {
    constructor() {
        this.socket = null;
        this.currentRoom = null;
        this.isConnected = false;
        this.userId = null;
        this.userRole = null;
        this.listenersAttached = false;
        this.typingTimeout = null;
        this.refreshUserContext();
        this.ensureSocket();
    }

    refreshUserContext() {
        if (!document.body) return;
        this.userId = document.body.dataset.userId || null;
        this.userRole = document.body.dataset.userRole || null;
    }

    ensureSocket() {
        if (this.socket) return this.socket;
        if (window.socket) {
            this.socket = window.socket;
            return this.socket;
        }
        if (typeof window.io === 'undefined') {
            console.warn('Socket.IO not available yet');
            return null;
        }
        this.socket = window.io();
        window.socket = this.socket;
        return this.socket;
    }

    connect() {
        this.refreshUserContext();
        const sock = this.ensureSocket();
        if (!sock) return null;

        if (!this.listenersAttached) {
            this.attachListeners(sock);
        }

        return sock;
    }

    attachListeners(sock) {
        if (!sock || this.listenersAttached) return;
        this.listenersAttached = true;

        sock.on('connect', () => {
            this.isConnected = true;
            this.refreshUserContext();
            this.subscribeToNotifications();
            this.updateUnreadCount();
            this.updateConnectionStatus(true);
            console.log('✓ Connected to chat server');
        });

        sock.on('disconnect', () => {
            this.isConnected = false;
            this.updateConnectionStatus(false);
            console.warn('✗ Disconnected from chat server');
        });

        sock.on('joined_room', (data) => {
            this.currentRoom = data.room_id;
            console.log('✓ Joined room:', data.room_id);
        });

        sock.on('new_message', (data) => {
            this.displayMessage(data);
            this.scrollToBottom();
            this.playNotificationSound();
        });

        sock.on('user_typing', (data) => {
            this.showTypingIndicator(data);
        });

        sock.on('messages_read', (data) => {
            this.markMessagesAsRead(data.user_id);
        });

        sock.on('error', (data) => {
            if (data && data.message) {
                this.showError(data.message);
            }
        });

        sock.on('notification', (data) => {
            this.handleNotification(data);
        });
    }

    subscribeToNotifications() {
        if (!this.socket || !this.userId) return;
        const payload = {
            user_id: parseInt(this.userId, 10),
            role: this.userRole
        };
        this.socket.emit('subscribe_notifications', payload);
    }

    joinRoom(roomId) {
        const sock = this.connect();
        if (!sock) {
            console.error('Socket connection not available');
            return;
        }

        if (this.currentRoom === roomId) return;

        if (this.currentRoom) {
            this.leaveRoom(this.currentRoom);
        }

        sock.emit('join_chat_room', { room_id: roomId });
        this.currentRoom = roomId;
        
        // Clear previous messages
        const messagesContainer = document.getElementById('chat-messages');
        if (messagesContainer) {
            messagesContainer.innerHTML = '';
        }
    }

    leaveRoom(roomId) {
        const sock = this.socket;
        if (sock && roomId) {
            sock.emit('leave_chat_room', { room_id: roomId });
        }
    }

    sendMessage(message) {
        const sock = this.socket;
        if (!sock || !this.isConnected || !this.currentRoom) {
            console.error('Not connected or no room joined');
            return false;
        }

        if (!message.trim()) return false;

        sock.emit('send_chat_message', {
            room_id: this.currentRoom,
            message: message
        });

        return true;
    }

    displayMessage(messageData) {
        const messagesContainer = document.getElementById('chat-messages');
        if (!messagesContainer) return;

        const messageElement = this.createMessageElement(messageData);
        messagesContainer.appendChild(messageElement);
    }

    createMessageElement(messageData) {
        const messageDiv = document.createElement('div');
        const isMine = String(messageData.user_id) === String(this.userId);
        const roleLabel = (messageData.sender_role || messageData.user_role || '').replace('_', ' ') || '';
        messageDiv.className = `message ${isMine ? 'own-message' : 'other-message'} ${messageData.is_support ? 'support-message' : ''}`;
        
        const timestamp = new Date(messageData.timestamp).toLocaleString();
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <strong>${messageData.user_name}</strong>
                <span class="message-time">${timestamp}</span>
            </div>
            <div class="message-content">${this.escapeHtml(messageData.message)}</div>
            ${roleLabel ? `<div class="message-role">${this.escapeHtml(roleLabel)}</div>` : ''}
        `;

        return messageDiv;
    }

    showTypingIndicator(data) {
        const typingContainer = document.getElementById('typing-indicator');
        if (!typingContainer) return;

        if (data.is_typing) {
            typingContainer.innerHTML = `<div class="typing">${data.user_name} is typing...</div>`;
            typingContainer.style.display = 'block';
        } else {
            typingContainer.style.display = 'none';
        }
    }

    startTyping() {
        if (this.isConnected && this.currentRoom && this.socket) {
            this.socket.emit('typing_chat', {
                room_id: this.currentRoom,
                is_typing: true
            });
            
            clearTimeout(this.typingTimeout);
            this.typingTimeout = setTimeout(() => {
                this.stopTyping();
            }, 1000);
        }
    }

    stopTyping() {
        if (this.isConnected && this.currentRoom && this.socket) {
            this.socket.emit('typing_chat', {
                room_id: this.currentRoom,
                is_typing: false
            });
        }
    }

    markMessagesAsRead(userId) {
        const unreadMessages = document.querySelectorAll('.message.unread');
        unreadMessages.forEach(msg => {
            msg.classList.remove('unread');
        });
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chat-messages');
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    playNotificationSound() {
        try {
            const audio = new Audio('/static/sounds/notification.mp3');
            audio.volume = 0.3;
            audio.play().catch(() => {});
        } catch (e) {
            // Fallback for browsers that don't support the audio file
            try {
                const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBDbF7+ijWxYNTqzj67RkFAw5jd7v1nggCjWH2fPCbikHMIzf+b==');
                audio.volume = 0.3;
                audio.play().catch(() => {});
            } catch (e2) {}
        }
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.textContent = connected ? 'Connected' : 'Disconnected';
            statusElement.className = connected ? 'status-connected' : 'status-disconnected';
        }
    }

    showError(message) {
        console.error('Chat error:', message);
        // You can implement toast notifications here
        if (typeof showToast === 'function') {
            showToast('Chat Error', message, 'danger');
        }
    }

    handleNotification(notification) {
        if (notification.type === 'message') {
            this.playNotificationSound();
            
            // Update unread count badge
            this.updateUnreadCount();
            
            // Show desktop notification if supported
            if ('Notification' in window && Notification.permission === 'granted') {
                new Notification(notification.title, {
                    body: notification.message,
                    icon: '/static/favicon.ico',
                    tag: 'new-message'
                });
            }
        }
    }

    updateUnreadCount() {
        if (!this.userId) return;

        fetch('/chat/api/unread-count')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const count = data.count || 0;
                    document.querySelectorAll('[data-chat-badge="global"]').forEach(badge => {
                        if (!badge) return;
                        if (count > 0) {
                            badge.textContent = count > 99 ? '99+' : String(count);
                            badge.style.display = badge.dataset.badgeDisplay || 'flex';
                        } else {
                            badge.style.display = 'none';
                        }
                    });
                }
            })
            .catch(err => console.error('Failed to update unread count:', err));
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
            this.isConnected = false;
        }
    }
}

window.pawfectChat = new PawfectChat();
window.pawfectChat.connect();

document.addEventListener('DOMContentLoaded', function() {
    window.pawfectChat.refreshUserContext();
    window.pawfectChat.subscribeToNotifications();
    if (window.pawfectChat.userId) {
        window.pawfectChat.updateUnreadCount();
    }
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
});