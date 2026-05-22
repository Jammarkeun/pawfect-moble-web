// PawfectBot Chatbot Widget
(function() {
    // Create chatbot HTML structure
    function initializeChatbot() {
        // Only show chatbot for users (customers), not for admin/seller/rider
        const userRole = document.documentElement.getAttribute('data-user-role');
        if (userRole && userRole !== 'user') {
            return; // Don't show for non-customer roles
        }

        // Check if chatbot already exists
        if (document.getElementById('pawfect-chatbot')) return;

        const chatbotHTML = `
            <!-- Floating Chat Button -->
            <button id="chatbot-toggle" class="chatbot-toggle" title="Chat with PawfectBot">
                💬
            </button>

            <!-- Chatbot Window -->
            <div id="pawfect-chatbot" class="chatbot-container hidden">
                <!-- Chat Header -->
                <div class="chatbot-header">
                    <h3 class="chatbot-title">PawfectBot 🐾</h3>
                    <button id="chatbot-close" class="chatbot-close" title="Close chat">×</button>
                </div>

                <!-- Messages Container -->
                <div id="chatbot-messages" class="chatbot-messages">
                    <div class="chatbot-message bot-message">
                        <p>Hi! I'm PawfectBot. How can I help you today?</p>
                    </div>
                </div>

                <!-- Questions/Input Area -->
                <div id="chatbot-options" class="chatbot-options">
                    <button class="chatbot-question-btn" data-question="How to order?">
                        📦 How to order?
                    </button>
                    <button class="chatbot-question-btn" data-question="Delivery time?">
                        🚚 Delivery time?
                    </button>
                    <button class="chatbot-question-btn" data-question="Payment methods?">
                        💳 Payment methods?
                    </button>
                    <button class="chatbot-question-btn" data-question="Return & Refund policy">
                        🔄 Return & Refund policy
                    </button>
                    <button class="chatbot-question-btn" data-question="Contact support">
                        📞 Contact support
                    </button>
                </div>
            </div>
        `;

        // Inject into body
        const chatbotContainer = document.createElement('div');
        chatbotContainer.innerHTML = chatbotHTML;
        document.body.appendChild(chatbotContainer.firstElementChild);
        document.body.appendChild(chatbotContainer.lastElementChild);

        // Initialize event listeners
        setupEventListeners();
    }

    // Setup all event listeners
    function setupEventListeners() {
        const toggleBtn = document.getElementById('chatbot-toggle');
        const closeBtn = document.getElementById('chatbot-close');
        const chatbot = document.getElementById('pawfect-chatbot');
        const questionBtns = document.querySelectorAll('.chatbot-question-btn');

        // Toggle chatbot window
        if (toggleBtn) {
            toggleBtn.addEventListener('click', function() {
                chatbot.classList.toggle('hidden');
                if (!chatbot.classList.contains('hidden')) {
                    // Focus on messages when opened
                    const messagesContainer = document.getElementById('chatbot-messages');
                    setTimeout(() => messagesContainer.scrollTop = messagesContainer.scrollHeight, 100);
                }
            });
        }

        // Close chatbot
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                chatbot.classList.add('hidden');
            });
        }

        // Handle question clicks
        questionBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const question = this.getAttribute('data-question');
                handleUserQuestion(question);
            });
        });
    }

    // Bot responses database
    const botResponses = {
        'How to order?': 'To order, just browse items, add to cart, then proceed to checkout!',
        'Delivery time?': 'Delivery takes 2–3 days in Metro Manila and 3–5 days provincial.',
        'Payment methods?': 'We accept COD, Credit Card via Stripe.',
        'Return & Refund policy': 'You can request a refund/return within 7 days.',
        'Contact support': 'You can reach us at support@pawfectfinds.com'
    };

    // Handle user question
    function handleUserQuestion(question) {
        const messagesContainer = document.getElementById('chatbot-messages');
        
        // Add user message
        const userMessage = document.createElement('div');
        userMessage.className = 'chatbot-message user-message';
        userMessage.innerHTML = `<p>${question}</p>`;
        messagesContainer.appendChild(userMessage);

        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Add bot response after a short delay
        setTimeout(() => {
            const botMessage = document.createElement('div');
            botMessage.className = 'chatbot-message bot-message';
            botMessage.innerHTML = `<p>${botResponses[question] || 'I didn\'t understand that. Please try another question.'}</p>`;
            messagesContainer.appendChild(botMessage);

            // Scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 500);
    }

    // Initialize chatbot when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeChatbot);
    } else {
        initializeChatbot();
    }
})();
