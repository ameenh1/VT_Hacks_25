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

    // Initialize chatbot
    initializeChatbot();

    console.log('EquityAI initialized successfully!');
});

// ================================
// CHATBOT FUNCTIONALITY
// ================================

class ChatbotManager {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8001';
        this.sessionId = null;
        this.isOpen = false;
        this.isTyping = false;
        
        this.elements = {
            widget: document.getElementById('chatbot-widget'),
            toggle: document.getElementById('chatbot-toggle'),
            window: document.getElementById('chatbot-window'),
            minimize: document.getElementById('chatbot-minimize'),
            messages: document.getElementById('chatbot-messages'),
            input: document.getElementById('chatbot-input'),
            send: document.getElementById('chatbot-send'),
            typing: document.getElementById('chatbot-typing'),
            notification: document.getElementById('chat-notification')
        };
        
        this.bindEvents();
    }
    
    bindEvents() {
        // Toggle chatbot
        this.elements.toggle.addEventListener('click', () => this.toggleChat());
        this.elements.minimize.addEventListener('click', () => this.closeChat());
        
        // Send message
        this.elements.send.addEventListener('click', () => this.sendMessage());
        this.elements.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize input
        this.elements.input.addEventListener('input', () => {
            this.elements.input.style.height = 'auto';
            this.elements.input.style.height = Math.min(this.elements.input.scrollHeight, 100) + 'px';
        });
    }
    
    async toggleChat() {
        if (this.isOpen) {
            this.closeChat();
        } else {
            await this.openChat();
        }
    }
    
    async openChat() {
        this.isOpen = true;
        this.elements.toggle.classList.add('active');
        this.elements.window.classList.remove('hidden');
        this.hideNotification();
        
        // Small delay for animation
        setTimeout(() => {
            this.elements.window.classList.add('visible');
            this.elements.input.focus();
        }, 10);
        
        // Start session if not already started
        if (!this.sessionId) {
            await this.startSession();
        }
    }
    
    closeChat() {
        this.isOpen = false;
        this.elements.toggle.classList.remove('active');
        this.elements.window.classList.remove('visible');
        
        setTimeout(() => {
            this.elements.window.classList.add('hidden');
        }, 300);
    }
    
    async startSession() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/chat/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            });
            
            if (!response.ok) {
                throw new Error('Failed to start chat session');
            }
            
            const data = await response.json();
            this.sessionId = data.session_id;
            
            // Add initial message
            this.addMessage('assistant', data.message);
            
        } catch (error) {
            console.error('Error starting chat session:', error);
            this.addMessage('assistant', 'Sorry, I encountered an error starting our conversation. Please try refreshing the page.');
        }
    }
    
    async sendMessage() {
        const message = this.elements.input.value.trim();
        if (!message || this.isTyping) return;
        
        // Add user message to chat
        this.addMessage('user', message);
        this.elements.input.value = '';
        this.elements.input.style.height = 'auto';
        
        // Show typing indicator
        this.showTyping();
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/chat/message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    message: message
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to send message');
            }
            
            const data = await response.json();
            
            // Hide typing indicator
            this.hideTyping();
            
            // Add assistant response
            this.addMessage('assistant', data.message);
            
            // Check if conversation is complete
            if (data.completed && data.preferences_collected) {
                setTimeout(() => {
                    this.addMessage('assistant', 'Perfect! I have all the information I need. Our property finding team will now search for investments that match your criteria. You should hear from us soon with some exciting opportunities!');
                }, 1000);
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTyping();
            this.addMessage('assistant', 'Sorry, I encountered an error processing your message. Please try again.');
        }
    }
    
    addMessage(role, content) {
        const messageEl = document.createElement('div');
        messageEl.className = `chat-message ${role}`;
        
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageEl.innerHTML = `
            <div class="chat-message-avatar">
                <i data-lucide="${role === 'user' ? 'user' : 'home'}"></i>
            </div>
            <div class="chat-message-content">
                ${this.formatMessage(content)}
                <div class="chat-message-time">${time}</div>
            </div>
        `;
        
        this.elements.messages.appendChild(messageEl);
        this.scrollToBottom();
        
        // Re-initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
    
    formatMessage(content) {
        // Convert line breaks to <br> tags
        return content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }
    
    showTyping() {
        this.isTyping = true;
        this.elements.typing.style.display = 'flex';
        this.elements.send.disabled = true;
        this.scrollToBottom();
    }
    
    hideTyping() {
        this.isTyping = false;
        this.elements.typing.style.display = 'none';
        this.elements.send.disabled = false;
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.elements.messages.scrollTop = this.elements.messages.scrollHeight;
        }, 100);
    }
    
    showNotification() {
        this.elements.notification.style.display = 'block';
    }
    
    hideNotification() {
        this.elements.notification.style.display = 'none';
    }
}

// Initialize chatbot
function initializeChatbot() {
    const chatbot = new ChatbotManager();
    
    // Show notification after a delay if chat hasn't been opened
    setTimeout(() => {
        if (!chatbot.isOpen) {
            chatbot.showNotification();
        }
    }, 5000);
}

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