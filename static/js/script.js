// CLearn JavaScript - Main Application Logic

document.addEventListener('DOMContentLoaded', function() {
    console.log('CLearn application loaded successfully');
    
    // Add smooth scrolling
    setupSmoothScrolling();
    
    // Add animation on scroll
    setupScrollAnimations();
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

