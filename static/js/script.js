// CLearn JavaScript - Main Application Logic

document.addEventListener('DOMContentLoaded', function() {
    console.log('CLearn application loaded successfully');

    // Initialize all features
    setupSmoothScrolling();
    setupScrollAnimations();
    setupBrightnessToggle();
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
    // Create quote slider
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
        }
    ];

    // Create quote slider container
    const quoteSlider = document.createElement('div');
    quoteSlider.className = 'quote-slider';

    // Create quote slides
    quotes.forEach((quote, index) => {
        const slide = document.createElement('div');
        slide.className = 'quote-slide';
        if (index === 0) slide.classList.add('active');

        slide.innerHTML = `
            <div class="quote-text">"${quote.text}"</div>
            <div class="quote-author">— ${quote.author}</div>
        `;
        quoteSlider.appendChild(slide);
    });

    // Create navigation dots
    const navigation = document.createElement('div');
    navigation.className = 'quote-navigation';

    quotes.forEach((_, index) => {
        const dot = document.createElement('div');
        dot.className = 'quote-dot';
        if (index === 0) dot.classList.add('active');

        dot.addEventListener('click', () => {
            showQuoteSlide(index);
        });

        navigation.appendChild(dot);
    });

    quoteSlider.appendChild(navigation);

    // Add quote slider to a random section
    const sections = document.querySelectorAll('section');
    if (sections.length > 0) {
        const randomSection = sections[Math.floor(Math.random() * sections.length)];
        randomSection.appendChild(quoteSlider);
    }

    // Auto-rotate quotes every 8 seconds
    let currentQuoteIndex = 0;
    setInterval(() => {
        currentQuoteIndex = (currentQuoteIndex + 1) % quotes.length;
        showQuoteSlide(currentQuoteIndex);
    }, 8000);

    function showQuoteSlide(index) {
        const slides = quoteSlider.querySelectorAll('.quote-slide');
        const dots = quoteSlider.querySelectorAll('.quote-dot');

        slides.forEach(slide => slide.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));

        slides[index].classList.add('active');
        dots[index].classList.add('active');

        currentQuoteIndex = index;
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

