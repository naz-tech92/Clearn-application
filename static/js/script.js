// CLearn JavaScript - Main Application Logic

document.addEventListener('DOMContentLoaded', function() {
    console.log('CLearn application loaded successfully');

    // Initialize all features
    setupSmoothScrolling();
    setupScrollAnimations();
    setupBrightnessToggle();
    setupFontSizeToggle();
    setupAIChatToggle();
    setupAutoScrollIndicator();
    setupAutoRefresh();
    setupKnowledgeHub();
    setupEnlighteningFeatures();
});

/**
 * Setup smooth scrolling for anchor links
 */
function setupSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });
}

/**
 * Setup scroll animations for cards
 */
function setupScrollAnimations() {
    const cards = document.querySelectorAll('.feature-card, .topic-card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease forwards';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    cards.forEach(card => {
        observer.observe(card);
    });
}

/**
 * Setup brightness toggle functionality
 */
function setupBrightnessToggle() {
    // Create brightness toggle button
    const toggleButton = document.createElement('button');
    toggleButton.className = 'brightness-toggle';
    toggleButton.innerHTML = '☀️';
    toggleButton.title = 'Toggle Brightness Theme';
    document.body.appendChild(toggleButton);

    // Load saved theme preference
    const savedTheme = localStorage.getItem('clearn-theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light-theme');
        toggleButton.classList.add('active');
        toggleButton.innerHTML = '🌙';
    }

    // Toggle theme on click
    toggleButton.addEventListener('click', function() {
        document.body.classList.toggle('light-theme');
        this.classList.toggle('active');

        if (document.body.classList.contains('light-theme')) {
            this.innerHTML = '🌙';
            localStorage.setItem('clearn-theme', 'light');
        } else {
            this.innerHTML = '☀️';
            localStorage.setItem('clearn-theme', 'dark');
        }
    });
}

/**
 * Setup font size toggle functionality
 */
function setupFontSizeToggle() {
    // Create font size toggle button
    const fontSizeButton = document.createElement('button');
    fontSizeButton.className = 'font-size-toggle';
    fontSizeButton.innerHTML = '🔤';
    fontSizeButton.title = 'Toggle Font Size';
    document.body.appendChild(fontSizeButton);

    // Load saved font size preference
    const savedFontSize = localStorage.getItem('clearn-font-size') || 'medium';
    applyFontSize(savedFontSize);
    if (savedFontSize === 'large') {
        fontSizeButton.classList.add('active');
    }

    // Toggle font size on click
    fontSizeButton.addEventListener('click', function() {
        const currentSize = localStorage.getItem('clearn-font-size') || 'medium';
        let newSize;

        if (currentSize === 'medium') {
            newSize = 'large';
            this.classList.add('active');
        } else {
            newSize = 'medium';
            this.classList.remove('active');
        }

        applyFontSize(newSize);
        localStorage.setItem('clearn-font-size', newSize);
    });
}

/**
 * Apply font size to the document
 */
function applyFontSize(size) {
    const root = document.documentElement;
    if (size === 'large') {
        root.style.fontSize = '18px';
    } else {
        root.style.fontSize = '16px';
    }
}

/**
 * Setup AI chat toggle functionality
 */
function setupAIChatToggle() {
    // Create AI chat toggle button
    const aiChatButton = document.createElement('button');
    aiChatButton.className = 'ai-chat-toggle';
    aiChatButton.innerHTML = '💬';
    aiChatButton.title = 'AI Assistant Chat';
    document.body.appendChild(aiChatButton);

    // Create AI chat panel
    const chatPanel = document.createElement('div');
    chatPanel.className = 'ai-chat-panel';
    chatPanel.innerHTML = `
        <div class="ai-chat-header">
            <h3>AI Assistant</h3>
            <button class="ai-chat-close" title="Close Chat">&times;</button>
        </div>
        <div class="ai-chat-messages">
            <div class="ai-message">Hello! I'm your AI assistant. How can I help you with your learning journey today?</div>
        </div>
        <div class="ai-chat-input">
            <textarea placeholder="Type your message..." rows="2"></textarea>
            <button>Send</button>
        </div>
    `;
    document.body.appendChild(chatPanel);

    // Toggle chat panel on button click
    aiChatButton.addEventListener('click', function() {
        chatPanel.classList.toggle('active');
        this.classList.toggle('active');
    });

    // Close chat panel
    const closeButton = chatPanel.querySelector('.ai-chat-close');
    closeButton.addEventListener('click', function() {
        chatPanel.classList.remove('active');
        aiChatButton.classList.remove('active');
    });

    // Handle message sending
    const sendButton = chatPanel.querySelector('button');
    const textarea = chatPanel.querySelector('textarea');
    const messagesContainer = chatPanel.querySelector('.ai-chat-messages');

    function sendMessage() {
        const message = textarea.value.trim();
        if (message) {
            // Add user message
            const userMessage = document.createElement('div');
            userMessage.className = 'user-message';
            userMessage.textContent = message;
            messagesContainer.appendChild(userMessage);

            // Clear textarea
            textarea.value = '';

            // Simulate AI response (you can replace this with actual AI integration)
            setTimeout(() => {
                const aiResponse = document.createElement('div');
                aiResponse.className = 'ai-message';
                aiResponse.textContent = getAIResponse(message);
                messagesContainer.appendChild(aiResponse);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }, 1000);

            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    sendButton.addEventListener('click', sendMessage);
    textarea.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

/**
 * Get AI response based on user message
 */
function getAIResponse(message) {
    const responses = [
        "That's a great question! Let me help you understand that concept better.",
        "I can assist you with that. Here's what you need to know:",
        "Excellent choice! This topic is fundamental to your learning path.",
        "I'm here to help you succeed. Let's break this down step by step.",
        "That's an interesting point. Here's some additional context:",
        "Great observation! This connects to several important concepts.",
        "I understand your concern. Let me provide some clarification:",
        "Perfect timing! This is a key concept you'll use throughout your studies.",
        "That's a common question. Here's the explanation:",
        "I'm glad you asked! This is actually quite straightforward once you see it this way."
    ];

    // Simple keyword-based responses
    const lowerMessage = message.toLowerCase();

    if (lowerMessage.includes('help') || lowerMessage.includes('assist')) {
        return "I'm here to help! I can answer questions about cybersecurity, provide learning tips, explain concepts, or guide you through your studies.";
    } else if (lowerMessage.includes('course') || lowerMessage.includes('learn')) {
        return "CLearn offers comprehensive courses in cybersecurity, networking, programming, and more. What specific area interests you most?";
    } else if (lowerMessage.includes('difficult') || lowerMessage.includes('hard')) {
        return "Don't worry! Every expert was once a beginner. Break complex topics into smaller parts, practice regularly, and don't hesitate to ask questions.";
    } else if (lowerMessage.includes('career') || lowerMessage.includes('job')) {
        return "Cybersecurity offers excellent career opportunities! Roles like security analyst, penetration tester, and security engineer are in high demand.";
    }

    return responses[Math.floor(Math.random() * responses.length)];
}

/**
 * Setup auto-scroll indicator
 */
function setupAutoScrollIndicator() {
    const scrollIndicator = document.createElement('button');
    scrollIndicator.className = 'scroll-indicator';
    scrollIndicator.innerHTML = '⬇️ Scroll to Explore';
    document.body.appendChild(scrollIndicator);

    // Show/hide based on scroll position
    window.addEventListener('scroll', function() {
        if (window.scrollY < 100) {
            scrollIndicator.classList.add('visible');
        } else {
            scrollIndicator.classList.remove('visible');
        }
    });

    // Auto-scroll functionality
    scrollIndicator.addEventListener('click', function() {
        window.scrollTo({
            top: window.innerHeight,
            behavior: 'smooth'
        });
    });
}

/**
 * Setup auto-refresh functionality
 */
function setupAutoRefresh() {
    // Auto-refresh button removed as requested
    // This function is kept for future use if needed
}

/**
 * Setup knowledge hub interactions
 */
function setupKnowledgeHub() {
    const knowledgeItems = document.querySelectorAll('.knowledge-hub li');
    knowledgeItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(5px)';
        });

        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateX(0)';
        });
    });
}

/**
 * Setup enlightening features and animations
 */
function setupEnlighteningFeatures() {
    // Create continuous quote slideshow
    const quotes = [
        {
            text: "The beautiful thing about learning is that no one can take it away from you.",
            author: "B.B. King"
        },
        {
            text: "Education is the most powerful weapon which you can use to change the world.",
            author: "Nelson Mandela"
        },
        {
            text: "The future belongs to those who believe in the beauty of their dreams.",
            author: "Eleanor Roosevelt"
        },
        {
            text: "Knowledge is power, but enthusiasm pulls the switch.",
            author: "Ivern Ball"
        },
        {
            text: "Your career is a journey, not a destination. Embrace every step.",
            author: "Unknown"
        },
        {
            text: "Success is not final, failure is not fatal: It is the courage to continue that counts.",
            author: "Winston Churchill"
        },
        {
            text: "The only way to do great work is to love what you do.",
            author: "Steve Jobs"
        },
        {
            text: "Believe you can and you're halfway there.",
            author: "Theodore Roosevelt"
        }
    ];

    // Create quote slideshow container
    const quoteSlideshow = document.createElement('section');
    quoteSlideshow.className = 'quote-slideshow';
    quoteSlideshow.innerHTML = `
        <div class="quote-slideshow-container">
            <div class="quote-slideshow-track">
                ${quotes.map(quote => `
                    <div class="quote-slide-item">
                        <div class="quote-content">
                            <div class="quote-text">"${quote.text}"</div>
                            <div class="quote-author">— ${quote.author}</div>
                        </div>
                    </div>
                `).join('')}
                ${quotes.map(quote => `
                    <div class="quote-slide-item">
                        <div class="quote-content">
                            <div class="quote-text">"${quote.text}"</div>
                            <div class="quote-author">— ${quote.author}</div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;

    // Insert immediately after hero section
    const heroSection = document.querySelector('.hero-fullwidth');
    if (heroSection) {
        heroSection.insertAdjacentElement('afterend', quoteSlideshow);
    }

    // Add tooltips to important information
    const infoElements = document.querySelectorAll('.feature-card h3, .topic-card h2');
    infoElements.forEach(element => {
        const tooltip = document.createElement('span');
        tooltip.className = 'info-tooltip';
        tooltip.innerHTML = 'ℹ️<span class="tooltip-text">Click to explore more about this topic and discover related resources.</span>';
        element.appendChild(tooltip);
    });
}

/**
 * Fetch topics from API
 */
async function fetchTopics() {
    try {
        const response = await fetch('/api/topics');
        if (!response.ok) {
            throw new Error('Failed to fetch topics');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching topics:', error);
        return [];
    }
}

// Add fadeInUp animation
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);

