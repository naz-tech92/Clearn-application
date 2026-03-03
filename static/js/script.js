// CLearn JavaScript - Main Application Logic



document.addEventListener('DOMContentLoaded', function() {
    console.log('CLearn application loaded successfully');

    // Initialize all features
    setupGlobalNavbarBrandAndLanguage();
    setupSmoothScrolling();
    setupScrollAnimations();
    setupBrightnessToggle();
    setupFontSizeToggle();
    setupAIChatToggle();
    setupAutoScrollIndicator();
    setupAutoRefresh();
    setupKnowledgeHub();
    setupEnlighteningFeatures();
    setupSiteLanguageTranslation();
});

function setupGlobalNavbarBrandAndLanguage() {
    const logos = document.querySelectorAll('.nav-logo');
    logos.forEach((logo) => {
        if (!logo.querySelector('.nav-logo-icon')) {
            const labelText = (logo.textContent || '').replace(/\s+/g, ' ').trim();
            const suffix = labelText.toLowerCase().endsWith('learn') ? 'Learn' : labelText || 'Learn';
            logo.innerHTML = `<img src="/static/images/clearn-c-logo.svg" alt="CLearn logo" class="nav-logo-icon">${suffix}`;
        }
    });

    const navMenus = document.querySelectorAll('.nav-menu');
    navMenus.forEach((menu) => {
        if (menu.querySelector('#languageSelector')) {
            return;
        }
        const item = document.createElement('li');
        item.className = 'nav-item nav-language-wrap';
        item.innerHTML = `
            <select id="languageSelector" class="nav-language-select" aria-label="Select site language">
                <option value="en">English</option>
                <option value="fr">Francais</option>
                <option value="es">Espanol</option>
                <option value="de">Deutsch</option>
            </select>
        `;
        menu.appendChild(item);
    });
}

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
    toggleButton.innerHTML = '☾';
    toggleButton.title = 'Toggle Brightness Theme';
    document.body.appendChild(toggleButton);

    // Load saved theme preference
    const savedTheme = localStorage.getItem('clearn-theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light-theme');
        toggleButton.classList.add('active');
        toggleButton.innerHTML = '☀';
    }

    // Toggle theme on click
    toggleButton.addEventListener('click', function() {
        document.body.classList.toggle('light-theme');
        this.classList.toggle('active');

        if (document.body.classList.contains('light-theme')) {
            this.innerHTML = '☀';
            localStorage.setItem('clearn-theme', 'light');
        } else {
            this.innerHTML = '☾';
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
    fontSizeButton.innerHTML = 'A+';
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
        positionChatPanelNearToggle(aiChatButton, chatPanel);
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

    window.addEventListener('resize', function() {
        if (chatPanel.classList.contains('active')) {
            positionChatPanelNearToggle(aiChatButton, chatPanel);
        }
    });
}

/**
 * Position chat panel above the AI toggle button.
 */
function positionChatPanelNearToggle(toggle, panel) {
    const rect = toggle.getBoundingClientRect();
    const panelWidth = panel.offsetWidth || 300;
    const leftPos = Math.min(
        window.innerWidth - panelWidth - 12,
        Math.max(12, rect.right - panelWidth)
    );

    let topPos = rect.top - panel.offsetHeight - 12;
    if (topPos < 12) {
        topPos = Math.min(window.innerHeight - panel.offsetHeight - 12, rect.bottom + 12);
    }

    panel.style.left = leftPos + 'px';
    panel.style.right = 'auto';
    panel.style.top = topPos + 'px';
    panel.style.transform = 'none';
}

/**
 * Make floating control elements draggable and persist their position.
 */
function makeElementMovable(element, storageKey, onMove) {
    let isDragging = false;
    let moved = false;
    let startX = 0;
    let startY = 0;
    let offsetX = 0;
    let offsetY = 0;

    const saved = localStorage.getItem(storageKey);
    if (saved) {
        try {
            const parsed = JSON.parse(saved);
            if (typeof parsed.left === 'number' && typeof parsed.top === 'number') {
                element.style.left = parsed.left + 'px';
                element.style.top = parsed.top + 'px';
                element.style.right = 'auto';
                element.style.transform = 'none';
            }
        } catch (err) {
            localStorage.removeItem(storageKey);
        }
    }

    element.addEventListener('pointerdown', function(e) {
        if (e.button !== 0) {
            return;
        }
        isDragging = true;
        moved = false;
        startX = e.clientX;
        startY = e.clientY;
        const rect = element.getBoundingClientRect();
        offsetX = e.clientX - rect.left;
        offsetY = e.clientY - rect.top;
        element.classList.add('dragging');
        element.setPointerCapture(e.pointerId);
    });

    element.addEventListener('pointermove', function(e) {
        if (!isDragging) {
            return;
        }

        const deltaX = Math.abs(e.clientX - startX);
        const deltaY = Math.abs(e.clientY - startY);
        if (deltaX > 3 || deltaY > 3) {
            moved = true;
        }

        const maxLeft = window.innerWidth - element.offsetWidth - 6;
        const maxTop = window.innerHeight - element.offsetHeight - 6;
        const nextLeft = Math.min(Math.max(6, e.clientX - offsetX), maxLeft);
        const nextTop = Math.min(Math.max(6, e.clientY - offsetY), maxTop);

        element.style.left = nextLeft + 'px';
        element.style.top = nextTop + 'px';
        element.style.right = 'auto';
        element.style.transform = 'none';

        if (typeof onMove === 'function') {
            onMove();
        }
    });

    element.addEventListener('pointerup', function(e) {
        if (!isDragging) {
            return;
        }
        isDragging = false;
        element.classList.remove('dragging');
        element.releasePointerCapture(e.pointerId);

        const left = parseFloat(element.style.left);
        const top = parseFloat(element.style.top);
        if (!Number.isNaN(left) && !Number.isNaN(top)) {
            localStorage.setItem(storageKey, JSON.stringify({ left, top }));
        }

        if (moved) {
            element.dataset.dragging = 'true';
            setTimeout(() => {
                element.dataset.dragging = 'false';
            }, 0);
        }
    });
}

/**
 * Get AI response based on user message
 */
function getAIResponse(message) {
    const lowerMessage = message.toLowerCase();
    const sitePaths = "Useful site pages: /category, /topics, /resources, /about, /contact.";
    const externalBlock = "External resources you can check: Coursera, edX, LinkedIn Learning, Cisco Skills for All, Google Career Certificates.";

    if (/(category|categories|skill|skills|career path|which skill|choose)/.test(lowerMessage)) {
        return "Start from /category to compare Technology, Health, and Business paths. Then open a skill and check the country cards for demand and education requirements. Suggested search: 'cybersecurity vs data science beginner path'.";
    }

    if (/(country|cameroon|usa|canada|germany|uk|singapore|australia|uae|abroad)/.test(lowerMessage)) {
        return "Use the country detail pages from each skill to compare requirements, demand level, and study paths by location. " + sitePaths + " Suggested search: 'best country for [your skill] entry-level jobs'.";
    }

    if (/(school|university|college|recommended school|study)/.test(lowerMessage)) {
        return "Open a skill country page and review 'Recommended Schools for this Career' for founding year, focus, and official links. " + externalBlock + " Suggested search: 'accredited [skill] programs in [country]'.";
    }

    if (/(resource|book|course|certificate|certification|training)/.test(lowerMessage)) {
        return "For on-site learning, check /resources and each skill page references. For off-site learning, use Coursera, edX, and vendor tracks like AWS, Microsoft Learn, and Cisco. Suggested search: '[skill] certification roadmap 2026'.";
    }

    if (/(job|salary|demand|market|opportunity)/.test(lowerMessage)) {
        return "You can compare demand and study pathways on skill-country pages, then validate with external labor reports. Suggested search: '[skill] salary trend [country]' and '[skill] hiring demand 2026'.";
    }

    if (/(how to use|navigate|where to start|new here|beginner)/.test(lowerMessage)) {
        return "Quick start: 1) /category 2) select one skill 3) open country cards 4) compare education and certifications 5) check /resources for deeper learning.";
    }

    return "I can answer using this site content and suggest off-site learning resources. Ask me about a skill, a country, certifications, schools, or job demand. " + sitePaths;
}

/**
 * Setup auto-scroll indicator
 */
function setupAutoScrollIndicator() {
    const scrollIndicator = document.createElement('button');
    scrollIndicator.className = 'scroll-indicator';
    scrollIndicator.innerHTML = ' Scroll to Explore';
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
 * Setup language selector to translate the whole site.
 * Uses Google Translate element with persisted language preference.
 */
function setupSiteLanguageTranslation() {
    const selector = document.getElementById('languageSelector');
    const savedLanguage = localStorage.getItem('clearn-language') || 'en';
    const supported = ['en', 'fr', 'es', 'de'];

    if (selector && supported.includes(savedLanguage)) {
        selector.value = savedLanguage;
    }
    document.documentElement.lang = savedLanguage;

    ensureTranslateElementLoaded(function() {
        if (savedLanguage !== 'en') {
            applySiteLanguage(savedLanguage);
        }
    });

    if (!selector) {
        return;
    }

    selector.addEventListener('change', function(e) {
        const language = e.target.value;
        localStorage.setItem('clearn-language', language);
        document.documentElement.lang = language;
        applySiteLanguage(language);
    });
}

function ensureTranslateElementLoaded(onReady) {
    if (!document.getElementById('google_translate_element')) {
        const holder = document.createElement('div');
        holder.id = 'google_translate_element';
        holder.style.display = 'none';
        document.body.appendChild(holder);
    }

    window.googleTranslateElementInit = function() {
        new google.translate.TranslateElement(
            { pageLanguage: 'en', autoDisplay: false },
            'google_translate_element'
        );
        if (typeof onReady === 'function') {
            onReady();
        }
    };

    if (window.google && window.google.translate) {
        window.googleTranslateElementInit();
        return;
    }

    if (!document.getElementById('google-translate-script')) {
        const script = document.createElement('script');
        script.id = 'google-translate-script';
        script.src = 'https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
        script.async = true;
        document.head.appendChild(script);
    }
}

function setGoogleTranslateCookie(language) {
    const value = language === 'en' ? '/en/en' : '/en/' + language;
    document.cookie = 'googtrans=' + value + ';path=/';
}

function applySiteLanguage(language) {
    setGoogleTranslateCookie(language);

    // Returning to English requires resetting translated DOM.
    if (language === 'en') {
        window.location.reload();
        return;
    }

    let tries = 0;
    const timer = setInterval(function() {
        const combo = document.querySelector('.goog-te-combo');
        if (combo) {
            combo.value = language;
            combo.dispatchEvent(new Event('change'));
            clearInterval(timer);
            return;
        }
        tries += 1;
        if (tries > 25) {
            clearInterval(timer);
        }
    }, 200);
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
                            <div class="quote-author"> ${quote.author}</div>
                        </div>
                    </div>
                `).join('')}
                ${quotes.map(quote => `
                    <div class="quote-slide-item">
                        <div class="quote-content">
                            <div class="quote-text">"${quote.text}"</div>
                            <div class="quote-author"> ${quote.author}</div>
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
        tooltip.innerHTML = '<span class="tooltip-text">Click to explore more about this topic and discover related resources.</span>';
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
