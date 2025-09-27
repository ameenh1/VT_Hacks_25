// EquityAI Vanilla JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // Simple routing system
    const pages = {
        'home': 'home-page',
        'marketplace': 'marketplace-page',
        'analyzer': 'analyzer-page',
        'agent-connect': 'agent-connect-page',
        'pricing': 'pricing-page',
        'signin': 'signin-page',
        'signup': 'signup-page'
    };

    let currentPage = 'home';

    // Navigation functionality
    function showPage(pageId) {
        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });

        // Show selected page
        const targetPage = document.getElementById(pages[pageId] || pages['home']);
        if (targetPage) {
            targetPage.classList.add('active');
        }

        // Update active nav link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });

        const activeLink = document.querySelector(`[data-page="${pageId}"]`);
        if (activeLink && activeLink.classList.contains('nav-link')) {
            activeLink.classList.add('active');
        }

        currentPage = pageId;

        // Re-initialize icons for new page content
        if (typeof lucide !== 'undefined') {
            setTimeout(() => lucide.createIcons(), 100);
        }
    }

    // Add click handlers for navigation
    document.addEventListener('click', function(e) {
        const target = e.target.closest('[data-page]');
        if (target) {
            e.preventDefault();
            const pageId = target.getAttribute('data-page');
            showPage(pageId);
        }
    });

    // Animation on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe elements with animation classes
    document.querySelectorAll('.animate-fade-in, .animate-fade-in-up, .animate-scale-in').forEach(el => {
        // Set initial state
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        
        observer.observe(el);
    });

    // Smooth scrolling for anchor links
    document.addEventListener('click', function(e) {
        if (e.target.tagName === 'A' && e.target.getAttribute('href')?.startsWith('#')) {
            e.preventDefault();
            const target = document.querySelector(e.target.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        }
    });

    // Navbar scroll effect
    let lastScrollY = window.scrollY;
    
    window.addEventListener('scroll', () => {
        const navbar = document.querySelector('.navbar');
        const scrollY = window.scrollY;

        if (scrollY > 50) {
            navbar.style.background = 'rgba(255, 255, 255, 0.95)';
            navbar.style.backdropFilter = 'blur(20px)';
        } else {
            navbar.style.background = 'rgba(255, 255, 255, 0.95)';
        }

        lastScrollY = scrollY;
    });

    // Button hover effects
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            if (this.classList.contains('btn-primary')) {
                this.style.transform = 'translateY(-2px)';
                this.style.boxShadow = 'var(--shadow-glow)';
            }
        });

        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            if (!this.classList.contains('btn-cta')) {
                this.style.boxShadow = '';
            }
        });
    });

    // Floating cards animation
    document.querySelectorAll('.floating-card').forEach((card, index) => {
        card.style.animationDelay = `${index * 0.5}s`;
    });

    // Stats counter animation
    function animateCounter(element, target, duration = 2000) {
        const start = 0;
        const increment = target / (duration / 16);
        let current = start;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }

            // Format number based on content
            let displayValue;
            if (element.textContent.includes('$')) {
                displayValue = '$' + (current / 1000000).toFixed(1) + 'M+';
            } else if (element.textContent.includes('%')) {
                displayValue = Math.round(current) + '%';
            } else if (element.textContent.includes('Days')) {
                displayValue = Math.round(current) + ' Days';
            } else {
                displayValue = Math.round(current).toLocaleString() + '+';
            }

            element.textContent = displayValue;
        }, 16);
    }

    // Trigger counter animation when stats come into view
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const statNumber = entry.target.querySelector('.stat-number');
                if (statNumber && !statNumber.dataset.animated) {
                    statNumber.dataset.animated = 'true';
                    
                    // Extract target values
                    const text = statNumber.textContent;
                    let target;
                    
                    if (text.includes('$2.1M+')) target = 2100000;
                    else if (text.includes('10,000+')) target = 10000;
                    else if (text.includes('95%')) target = 95;
                    else if (text.includes('18 Days')) target = 18;
                    
                    if (target) {
                        animateCounter(statNumber, target);
                    }
                }
                statsObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('.stat-item').forEach(stat => {
        statsObserver.observe(stat);
    });

    // Testimonial stars animation
    document.querySelectorAll('.testimonial-card').forEach(card => {
        const stars = card.querySelectorAll('.testimonial-stars i');
        card.addEventListener('mouseenter', () => {
            stars.forEach((star, index) => {
                setTimeout(() => {
                    star.style.animation = 'pulse 0.5s ease';
                }, index * 100);
            });
        });

        card.addEventListener('mouseleave', () => {
            stars.forEach(star => {
                star.style.animation = '';
            });
        });
    });

    // Feature card hover effects
    document.querySelectorAll('.feature-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            const icon = this.querySelector('.feature-icon');
            if (icon) {
                icon.style.transform = 'scale(1.1)';
            }
        });

        card.addEventListener('mouseleave', function() {
            const icon = this.querySelector('.feature-icon');
            if (icon) {
                icon.style.transform = 'scale(1)';
            }
        });
    });

    // Logo hover effects
    document.querySelectorAll('.trust-logo').forEach(logo => {
        logo.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
            const img = this.querySelector('img');
            if (img) {
                img.style.transform = 'scale(1.1)';
            }
        });

        logo.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            const img = this.querySelector('img');
            if (img) {
                img.style.transform = 'scale(1)';
            }
        });
    });

    // Parallax effect for hero background
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const heroSection = document.querySelector('.hero-section');
        
        if (heroSection) {
            const speed = scrolled * 0.5;
            heroSection.style.transform = `translateY(${speed}px)`;
        }
    });

    // Initialize page
    showPage('home');

    console.log('EquityAI initialized successfully!');
});

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Add loading animation
window.addEventListener('load', () => {
    document.body.classList.add('loaded');
});

// Add CSS for loading state
const loadingStyles = `
    body:not(.loaded) {
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    body.loaded {
        opacity: 1;
    }
`;

const style = document.createElement('style');
style.textContent = loadingStyles;
document.head.appendChild(style);