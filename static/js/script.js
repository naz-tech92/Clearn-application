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
    setupSkillAdvantageCardStyling();
    setupSolidHeroSections();
    setupFooterSocialIcons();
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
    toggleButton.innerHTML = '&#9789;';
    toggleButton.title = 'Toggle Brightness Theme';
    document.body.appendChild(toggleButton);

    // Load saved theme preference
    const savedTheme = localStorage.getItem('clearn-theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light-theme');
        toggleButton.classList.add('active');
        toggleButton.innerHTML = '&#9728;';
    }

    // Toggle theme on click
    toggleButton.addEventListener('click', function() {
        document.body.classList.toggle('light-theme');
        this.classList.toggle('active');

        if (document.body.classList.contains('light-theme')) {
            this.innerHTML = '&#9728;';
            localStorage.setItem('clearn-theme', 'light');
        } else {
            this.innerHTML = '&#9789;';
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
    aiChatButton.innerHTML = '&#128172;';
    aiChatButton.title = 'AI Assistant Chat';
    document.body.appendChild(aiChatButton);

    // Create AI chat panel
    const chatPanel = document.createElement('div');
    chatPanel.className = 'ai-chat-panel';
    chatPanel.innerHTML = `
        <div class="ai-chat-header">
            <h3>AI Assistant</h3>
            <div class="ai-chat-header-actions">
                <button class="ai-chat-expand" title="Expand Chat" aria-label="Expand chat">&#9974;</button>
                <button class="ai-chat-close" title="Close Chat" aria-label="Close chat">&times;</button>
            </div>
        </div>
        <div class="ai-chat-messages">
            <div class="ai-message">Hello! I'm your AI assistant. Ask me about CLearn skills, countries, education paths, resources, and navigation.</div>
        </div>
        <div class="ai-chat-input">
            <textarea placeholder="Type your message..." rows="2"></textarea>
            <button>Send</button>
        </div>
    `;
    document.body.appendChild(chatPanel);

    // Toggle chat panel on button click
    aiChatButton.addEventListener('click', function(e) {
        e.stopPropagation();
        positionChatPanelNearToggle(aiChatButton, chatPanel);
        chatPanel.classList.toggle('active');
        this.classList.toggle('active');
    });

    // Close chat panel
    const closeButton = chatPanel.querySelector('.ai-chat-close');
    const expandButton = chatPanel.querySelector('.ai-chat-expand');
    closeButton.addEventListener('click', function(e) {
        e.stopPropagation();
        chatPanel.classList.remove('active');
        chatPanel.classList.remove('expanded');
        aiChatButton.classList.remove('active');
        expandButton.innerHTML = '&#9974;';
        expandButton.title = 'Expand Chat';
        expandButton.setAttribute('aria-label', 'Expand chat');
    });

    expandButton.addEventListener('click', function(e) {
        e.stopPropagation();
        chatPanel.classList.toggle('expanded');
        const isExpanded = chatPanel.classList.contains('expanded');
        expandButton.innerHTML = isExpanded ? '&#11197;' : '&#9974;';
        expandButton.title = isExpanded ? 'Shrink Chat' : 'Expand Chat';
        expandButton.setAttribute('aria-label', isExpanded ? 'Shrink chat' : 'Expand chat');
        if (!isExpanded) {
            positionChatPanelNearToggle(aiChatButton, chatPanel);
        }
    });

    // Handle message sending
    const sendButton = chatPanel.querySelector('.ai-chat-input button');
    const textarea = chatPanel.querySelector('textarea');
    const messagesContainer = chatPanel.querySelector('.ai-chat-messages');

    async function sendMessage() {
        const message = textarea.value.trim();
        if (!message) {
            return;
        }
        const greetingOnly = isGreetingMessage(message);
        const complexPrompt = isComplexPrompt(message);

        const userMessage = document.createElement('div');
        userMessage.className = 'user-message';
        userMessage.textContent = message;
        messagesContainer.appendChild(userMessage);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        if (complexPrompt && !chatPanel.classList.contains('expanded')) {
            chatPanel.classList.add('expanded');
            expandButton.innerHTML = '&#11197;';
            expandButton.title = 'Shrink Chat';
            expandButton.setAttribute('aria-label', 'Shrink chat');
        }

        textarea.value = '';
        sendButton.disabled = true;
        sendButton.textContent = '...';

        const typingIndicator = createTypingIndicator();
        messagesContainer.appendChild(typingIndicator);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        const minWaitMs = greetingOnly ? 180 : 120;
        try {
            const aiResult = await withTimeout(
                requestAIResponse(message),
                5000,
                { text: getAIResponse(message), imageDataUrl: '' }
            );
            await wait(minWaitMs);
            typingIndicator.remove();

            const aiResponse = document.createElement('div');
            aiResponse.className = 'ai-message';
            aiResponse.textContent = aiResult.text || '';
            messagesContainer.appendChild(aiResponse);
            if (aiResult.imageDataUrl) {
                const imageWrap = document.createElement('div');
                imageWrap.className = 'ai-message';
                const img = document.createElement('img');
                img.src = aiResult.imageDataUrl;
                img.alt = 'Generated preview';
                img.style.width = '100%';
                img.style.maxWidth = '360px';
                img.style.borderRadius = '10px';
                img.style.border = '1px solid rgba(59,130,246,0.35)';
                img.style.display = 'block';
                imageWrap.appendChild(img);

                const download = document.createElement('a');
                download.href = aiResult.imageDataUrl;
                download.download = 'clearn-ai-image.svg';
                download.textContent = 'Download image';
                download.style.display = 'inline-block';
                download.style.marginTop = '8px';
                download.style.color = '#93c5fd';
                download.style.fontSize = '0.86rem';
                imageWrap.appendChild(download);
                messagesContainer.appendChild(imageWrap);
            }
        } catch (error) {
            typingIndicator.remove();
            const aiResponse = document.createElement('div');
            aiResponse.className = 'ai-message';
            aiResponse.textContent = 'I could not process that right now. Please try again.';
            messagesContainer.appendChild(aiResponse);
        } finally {
            sendButton.disabled = false;
            sendButton.textContent = 'Send';
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

    chatPanel.addEventListener('click', function(e) {
        e.stopPropagation();
    });

    document.addEventListener('click', function(e) {
        if (!chatPanel.classList.contains('active')) {
            return;
        }
        if (e.target === aiChatButton || aiChatButton.contains(e.target)) {
            return;
        }
        if (chatPanel.contains(e.target)) {
            return;
        }
        chatPanel.classList.remove('active');
        aiChatButton.classList.remove('active');
    });

    window.addEventListener('resize', function() {
        if (chatPanel.classList.contains('active')) {
            positionChatPanelNearToggle(aiChatButton, chatPanel);
        }
    });
}

/**
 * Position chat panel beside the AI toggle button.
 */
function positionChatPanelNearToggle(toggle, panel) {
    if (panel.classList.contains('expanded')) {
        panel.style.left = '50%';
        panel.style.top = '50%';
        panel.style.right = 'auto';
        panel.style.bottom = 'auto';
        panel.style.transform = 'translate(-50%, -50%)';
        return;
    }

    const rect = toggle.getBoundingClientRect();
    const panelWidth = panel.offsetWidth || 300;
    const panelHeight = panel.offsetHeight || 400;

    let leftPos = rect.left - panelWidth - 12;
    if (leftPos < 12) {
        leftPos = rect.right + 12;
    }
    leftPos = Math.min(leftPos, window.innerWidth - panelWidth - 12);

    let topPos = rect.top + (rect.height / 2) - (panelHeight / 2);
    topPos = Math.max(12, Math.min(topPos, window.innerHeight - panelHeight - 12));

    panel.style.left = leftPos + 'px';
    panel.style.right = 'auto';
    panel.style.bottom = 'auto';
    panel.style.top = topPos + 'px';
    panel.style.transform = 'none';
}

function createTypingIndicator() {
    const bubble = document.createElement('div');
    bubble.className = 'ai-message ai-typing';
    bubble.innerHTML = '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';
    return bubble;
}

function wait(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

function withTimeout(promise, timeoutMs, fallbackValue) {
    let settled = false;
    return new Promise((resolve) => {
        const timeoutId = setTimeout(() => {
            if (settled) {
                return;
            }
            settled = true;
            resolve(fallbackValue);
        }, timeoutMs);

        promise
            .then((value) => {
                if (settled) {
                    return;
                }
                settled = true;
                clearTimeout(timeoutId);
                resolve(value);
            })
            .catch(() => {
                if (settled) {
                    return;
                }
                settled = true;
                clearTimeout(timeoutId);
                resolve(fallbackValue);
            });
    });
}

function isGreetingMessage(message) {
    const m = String(message || '').trim().toLowerCase();
    return /^(hi|hello|hey|yo|good morning|good afternoon|good evening|greetings|what's up|whats up)\b[!.?]*$/.test(m);
}

function isComplexPrompt(message) {
    const m = String(message || '').trim().toLowerCase();
    if (m.length >= 120) {
        return true;
    }
    const signals = [
        'explain',
        'compare',
        'difference',
        'roadmap',
        'step by step',
        'detailed',
        'comprehensive',
        'career path',
        'requirements',
        'how do i',
        'what should i do'
    ];
    return signals.some((token) => m.includes(token));
}

let firebaseAIModelPromise = null;

async function getFirebaseWebConfig() {
    const response = await fetch('/api/firebase/web-config');
    const payload = await response.json();
    if (!response.ok || !payload.ok || !payload.config) {
        throw new Error(payload.message || 'Firebase web config unavailable.');
    }
    return payload.config;
}

async function loadFirebaseModulePair() {
    const versions = ['12.4.0', '11.10.0', '10.14.1'];
    let lastError = null;

    for (const version of versions) {
        try {
            const appMod = await import(`https://www.gstatic.com/firebasejs/${version}/firebase-app.js`);
            const aiMod = await import(`https://www.gstatic.com/firebasejs/${version}/firebase-ai.js`);
            return { appMod, aiMod };
        } catch (err) {
            lastError = err;
        }
    }
    throw (lastError || new Error('Unable to load Firebase AI SDK modules.'));
}

function extractGeneratedText(result) {
    const directText = result?.response?.text;
    if (typeof directText === 'function') {
        const out = directText.call(result.response);
        if (typeof out === 'string' && out.trim()) {
            return out.trim();
        }
    }
    if (typeof directText === 'string' && directText.trim()) {
        return directText.trim();
    }
    const altText = result?.text;
    if (typeof altText === 'string' && altText.trim()) {
        return altText.trim();
    }
    return '';
}

async function getFirebaseAIModel() {
    if (firebaseAIModelPromise) {
        return firebaseAIModelPromise;
    }

    firebaseAIModelPromise = (async () => {
        const config = await getFirebaseWebConfig();
        const { appMod, aiMod } = await loadFirebaseModulePair();
        const {
            initializeApp,
            getApp,
            getApps
        } = appMod;
        const {
            getAI,
            getGenerativeModel,
            GoogleAIBackend
        } = aiMod;

        const firebaseApp = getApps().length ? getApp() : initializeApp(config);
        const ai = getAI(firebaseApp, { backend: new GoogleAIBackend() });
        const modelName = window.CLEARN_GEMINI_MODEL || 'gemini-3-flash-preview';
        return getGenerativeModel(ai, { model: modelName });
    })().catch((error) => {
        firebaseAIModelPromise = null;
        throw error;
    });

    return firebaseAIModelPromise;
}

async function requestAIResponseFromFirebase(message) {
    const model = await getFirebaseAIModel();
    const prompt = [
        'You are CLearn AI assistant.',
        'Focus on CLearn categories, skills, countries, education pathways, and resources.',
        'Keep answers concise and practical.',
        `User question: ${message}`
    ].join(' ');
    const result = await model.generateContent(prompt);
    const text = extractGeneratedText(result);
    if (!text) {
        throw new Error('Empty response from Firebase AI.');
    }
    return text;
}

async function requestAIResponseFromServer(message) {
    const response = await fetch('/api/ai-assist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
    });
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
        throw new Error(payload.message || 'AI service unavailable');
    }
    return {
        text: payload.reply || '',
        imageDataUrl: payload.imageDataUrl || ''
    };
}

async function requestAIResponse(message) {
    try {
        const text = await requestAIResponseFromFirebase(message);
        return { text, imageDataUrl: '' };
    } catch (firebaseError) {
        try {
            const serverReply = await requestAIResponseFromServer(message);
            if (serverReply && (serverReply.text || serverReply.imageDataUrl)) {
                return serverReply;
            }
        } catch (serverError) {
            // Fall through to local deterministic helper.
        }
    }
    return { text: getAIResponse(message), imageDataUrl: '' };
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

    if (/(draw|generate image|make image|create image|illustration|poster|logo)/.test(lowerMessage)) {
        return "I can generate a basic preview image in this chat. Try: 'generate image for AI career roadmap'.";
    }

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

    if (/(visa|immigration|work permit|relocate|abroad)/.test(lowerMessage)) {
        return "Use skill-country pages to compare pathways and demand, then verify official visa sources. I can also build a country comparison checklist for you.";
    }

    if (/(cv|resume|interview|cover letter|job application)/.test(lowerMessage)) {
        return "I can help structure a beginner CV and interview prep plan by skill and country. Share your target role and level.";
    }

    return "I can answer using this site content and suggest off-site learning resources. Ask me about a skill, a country, certifications, schools, or job demand. " + sitePaths;
}

/**
 * Setup auto-scroll indicator
 */
function setupAutoScrollIndicator() {
    if (window.location.pathname !== '/') {
        return;
    }
    const scrollIndicator = document.createElement('button');
    scrollIndicator.className = 'scroll-indicator';
    scrollIndicator.innerHTML = ' Scroll to Explore';
    document.body.appendChild(scrollIndicator);

    // Show/hide based on scroll position
    let tick = false;
    const syncVisibility = () => {
        if (window.scrollY < 100) {
            scrollIndicator.classList.add('visible');
        } else {
            scrollIndicator.classList.remove('visible');
        }
        tick = false;
    };
    window.addEventListener(
        'scroll',
        function() {
            if (tick) {
                return;
            }
            tick = true;
            window.requestAnimationFrame(syncVisibility);
        },
        { passive: true }
    );
    syncVisibility();

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
    // Refresh policy remains active server-side; no visible window badge.
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

function setupSkillAdvantageCardStyling() {
    const sectionHeadings = document.querySelectorAll('section h2');
    sectionHeadings.forEach((heading) => {
        const label = (heading.textContent || '').toLowerCase();
        if (!label.includes('advantages & disadvantages')) {
            return;
        }

        const section = heading.closest('section');
        if (!section) {
            return;
        }

        const grid = section.querySelector('div[style*="grid-template-columns"]');
        if (!grid) {
            return;
        }
        grid.classList.add('skill-ad-grid');

        const cards = Array.from(grid.children).filter((el) => el.tagName === 'DIV');
        cards.forEach((card, index) => {
            card.classList.add('skill-ad-card');
            card.classList.add(index === 0 ? 'skill-adv-card' : 'skill-disadv-card');

            const title = card.querySelector('h3');
            if (title) {
                title.classList.add('skill-ad-title');
                title.classList.add(index === 0 ? 'skill-adv-title' : 'skill-disadv-title');
            }

            card.querySelectorAll('p, li').forEach((node) => {
                node.classList.add('skill-ad-text');
            });
        });
    });
}

function setupSolidHeroSections() {
    const path = window.location.pathname || '';
    const isTargetPage =
        path === '/category' ||
        path.startsWith('/skill/') ||
        path.startsWith('/country/');

    if (!isTargetPage) {
        return;
    }

    document
        .querySelectorAll('.hero, .country-hero')
        .forEach((section) => section.classList.add('page-hero-solid'));
}

function setupFooterSocialIcons() {
    const footers = document.querySelectorAll('footer');
    footers.forEach((footer) => {
        const sections = Array.from(footer.querySelectorAll('.footer-section'));
        const accountSection = sections.find((section) => {
            const heading = section.querySelector('h4');
            return heading && (heading.textContent || '').trim().toLowerCase() === 'account';
        });
        const touchSection = sections.find((section) => {
            const heading = section.querySelector('h4');
            return heading && (heading.textContent || '').trim().toLowerCase() === 'get in touch';
        });

        if (!touchSection) {
            return;
        }

        const list = touchSection.querySelector('ul');
        if (!list) {
            return;
        }

        list.classList.add('footer-social-links');
        const links = list.querySelectorAll('a[href]');
        links.forEach((link) => {
            const href = (link.getAttribute('href') || '').toLowerCase();
            let label = '';
            let icon = '';

            if (href.includes('facebook.com')) {
                label = 'Facebook';
                icon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M13.5 8.5V6.7c0-.8.5-1.2 1.2-1.2h1.8V2.1h-2.8c-3.1 0-4.8 1.9-4.8 4.7v1.7H6v3.6h2.9v9h3.9v-9h3l.5-3.6h-3.8z"/></svg>';
            } else if (href.includes('linkedin.com')) {
                label = 'LinkedIn';
                icon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M6.9 8.2A2.2 2.2 0 1 1 6.9 3.8a2.2 2.2 0 0 1 0 4.4zM5 20.2V9.7h3.9v10.5H5zm6.1 0V9.7h3.7v1.4h.1c.5-.9 1.8-1.8 3.6-1.8 3.9 0 4.6 2.6 4.6 5.9v5h-3.9v-4.4c0-1 0-2.4-1.5-2.4s-1.7 1.1-1.7 2.3v4.5h-3.9z"/></svg>';
            } else if (href.includes('instagram.com')) {
                label = 'Instagram';
                icon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M7.5 2h9A5.5 5.5 0 0 1 22 7.5v9a5.5 5.5 0 0 1-5.5 5.5h-9A5.5 5.5 0 0 1 2 16.5v-9A5.5 5.5 0 0 1 7.5 2zm0 1.8A3.7 3.7 0 0 0 3.8 7.5v9a3.7 3.7 0 0 0 3.7 3.7h9a3.7 3.7 0 0 0 3.7-3.7v-9a3.7 3.7 0 0 0-3.7-3.7h-9zm9.7 1.4a1.1 1.1 0 1 1 0 2.2 1.1 1.1 0 0 1 0-2.2zM12 7a5 5 0 1 1 0 10 5 5 0 0 1 0-10zm0 1.8a3.2 3.2 0 1 0 0 6.4 3.2 3.2 0 0 0 0-6.4z"/></svg>';
            } else {
                return;
            }

            link.classList.add('footer-social-link');
            link.setAttribute('aria-label', label);
            link.innerHTML = `<span class="footer-social-icon">${icon}</span>`;
        });

        if (accountSection) {
            const legacyIcons = accountSection.querySelector('.account-social-icons');
            if (legacyIcons) {
                legacyIcons.remove();
            }
            const inlineLabel = document.createElement('p');
            inlineLabel.className = 'footer-touch-inline-label';
            inlineLabel.textContent = 'Get in Touch';
            accountSection.appendChild(inlineLabel);
            accountSection.appendChild(list);
            touchSection.remove();
        }
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
    if (window.location.pathname !== '/') {
        return;
    }
    if (document.querySelector('.quote-slideshow')) {
        return;
    }
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
    const infoElements = Array.from(document.querySelectorAll('.feature-card h3, .topic-card h2')).slice(0, 14);
    const attachTooltips = () => {
        infoElements.forEach(element => {
            if (element.querySelector('.info-tooltip')) {
                return;
            }
            const tooltip = document.createElement('span');
            tooltip.className = 'info-tooltip';
            tooltip.innerHTML = '<span class="tooltip-text">Click to explore more about this topic and discover related resources.</span>';
            element.appendChild(tooltip);
        });
    };

    if ('requestIdleCallback' in window) {
        window.requestIdleCallback(attachTooltips, { timeout: 900 });
    } else {
        setTimeout(attachTooltips, 120);
    }
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

