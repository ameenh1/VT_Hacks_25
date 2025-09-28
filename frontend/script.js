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
        // Special handling for demo page - redirect to separate HTML file
        if (pageId === 'demo') {
            window.location.href = 'pages/try-equitynest.html';
            return;
        }

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

    // Auto-detect and initialize demo page if we're on try-equitynest.html
    if (window.location.pathname.includes('try-equitynest.html') || 
        window.location.href.includes('try-equitynest.html') ||
        document.querySelector('.demo-search-section')) {
        console.log('🎯 Detected Try EquityNest page, initializing demo functionality...');
        // Delay initialization slightly to ensure DOM is fully ready
        setTimeout(() => {
            initDemoPage();
        }, 100);
    }

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
        
        let iconType = 'home'; // default for assistant
        if (role === 'user') iconType = 'user';
        else if (role === 'system') iconType = 'settings';
        
        messageEl.innerHTML = `
            <div class="chat-message-avatar">
                <i data-lucide="${iconType}"></i>
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
    
    // Store chatbot instance globally so it can be accessed from form handlers
    window.chatbot = chatbot;
    
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

document.body.classList.add('loaded');

// ===== TRY EQUITYNEST DEMO PAGE FUNCTIONALITY =====

// Demo page state
let demoPageInitialized = false;
let chatSession = null;

// Initialize demo page functionality
function initDemoPage() {
    if (demoPageInitialized) return;
    
    console.log('Initializing Try EquityNest demo page...');
    
    // Initialize location examples
    initLocationExamples();
    
    // Initialize budget functionality
    initBudgetFunctionality();
    
    // Initialize search functionality
    initSearchFunctionality();
    
    // Initialize chat functionality
    initChatFunctionality();
    
    demoPageInitialized = true;
    console.log('✅ Demo page initialized successfully');
}

// Location examples functionality
function initLocationExamples() {
    const examples = document.querySelectorAll('.demo-example');
    const locationInput = document.getElementById('demo-location');
    
    if (!locationInput) return;
    
    examples.forEach(example => {
        example.addEventListener('click', function() {
            locationInput.value = this.textContent.trim();
            locationInput.focus();
            
            // Add a subtle animation to show the input was updated
            locationInput.style.transform = 'scale(1.02)';
            setTimeout(() => {
                locationInput.style.transform = 'scale(1)';
            }, 150);
        });
    });
}

// Price slider functionality
// Budget functionality
function initBudgetFunctionality() {
    const customBudgetToggle = document.getElementById('custom-budget-toggle');
    const customBudgetInputs = document.getElementById('custom-budget-inputs');
    const minPriceSelect = document.getElementById('min-price');
    const maxPriceSelect = document.getElementById('max-price');
    
    if (!customBudgetToggle || !customBudgetInputs) {
        console.warn('Budget elements not found');
        return;
    }
    
    // Handle custom budget toggle
    customBudgetToggle.addEventListener('change', function() {
        if (this.checked) {
            customBudgetInputs.style.display = 'grid';
            // Disable select dropdowns when using custom inputs
            if (minPriceSelect) minPriceSelect.disabled = true;
            if (maxPriceSelect) maxPriceSelect.disabled = true;
        } else {
            customBudgetInputs.style.display = 'none';
            // Re-enable select dropdowns
            if (minPriceSelect) minPriceSelect.disabled = false;
            if (maxPriceSelect) maxPriceSelect.disabled = false;
        }
    });
    
    // Format number inputs with commas as user types
    const customMinPrice = document.getElementById('custom-min-price');
    const customMaxPrice = document.getElementById('custom-max-price');
    
    if (customMinPrice) {
        customMinPrice.addEventListener('input', formatNumberInput);
    }
    
    if (customMaxPrice) {
        customMaxPrice.addEventListener('input', formatNumberInput);
    }
    
    // Validation for min/max relationship
    function validateBudgetRange() {
        const isCustom = customBudgetToggle.checked;
        let minVal, maxVal;
        
        if (isCustom) {
            minVal = parseInt(customMinPrice?.value) || 0;
            maxVal = parseInt(customMaxPrice?.value) || 0;
        } else {
            minVal = parseInt(minPriceSelect?.value) || 0;
            maxVal = parseInt(maxPriceSelect?.value) || 0;
        }
        
        if (minVal > 0 && maxVal > 0 && minVal >= maxVal) {
            // Show validation message
            console.warn('Minimum price should be less than maximum price');
            return false;
        }
        
        return true;
    }
    
    // Add change listeners for validation
    if (minPriceSelect) {
        minPriceSelect.addEventListener('change', validateBudgetRange);
    }
    
    if (maxPriceSelect) {
        maxPriceSelect.addEventListener('change', validateBudgetRange);
    }
    
    if (customMinPrice) {
        customMinPrice.addEventListener('blur', validateBudgetRange);
    }
    
    if (customMaxPrice) {
        customMaxPrice.addEventListener('blur', validateBudgetRange);
    }
}

function formatNumberInput(event) {
    let value = event.target.value.replace(/,/g, '');
    if (value && !isNaN(value)) {
        // Add commas for thousands
        event.target.value = parseInt(value).toLocaleString();
    }
}

// Search functionality
function initSearchFunctionality() {
    const searchButton = document.getElementById('demo-search-btn');
    
    if (!searchButton) {
        console.warn('Search button not found');
        return;
    }
    
    searchButton.addEventListener('click', handleSearch);
}

async function handleSearch() {
    console.log('🔍 Handling property search...');
    
    // Get form data
    const searchData = getSearchFormData();
    console.log('📝 Form data collected:', searchData);
    
    if (!validateSearchData(searchData)) {
        console.log('❌ Validation failed, stopping search');
        return;
    }
    
    console.log('✅ Validation passed, starting chatbot with form data');
    
    // Show loading state
    showLoadingState();
    
    try {
        // Option 1: Start chatbot with form data
        await startChatbotWithFormData(searchData);
        
        // Option 2: Or simulate direct search (keeping original functionality)
        // await simulatePropertySearch(searchData);
        // displaySearchResults(searchData);
        
    } catch (error) {
        console.error('Search failed:', error);
        showSearchError(error.message);
    } finally {
        hideLoadingState();
    }
}

async function startChatbotWithFormData(searchData) {
    console.log('🤖 Updating existing chatbot widget with form data:', searchData);
    
    const CHATBOT_API_BASE = 'http://localhost:8001';
    
    try {
        // Prepare frontend data for the chatbot
        const frontendData = {
            location: searchData.location,
            property_types: searchData.propertyTypes,
            budget_min: searchData.budget.min || null,
            budget_max: searchData.budget.max || null
        };
        
        console.log('📤 Sending to chatbot API:', frontendData);
        
        // Check if the chatbot widget exists and get its instance
        const chatbotWidget = document.getElementById('chatbot-widget');
        if (!chatbotWidget) {
            throw new Error('Chatbot widget not found');
        }
        
        // Get the existing chatbot instance (assuming it's stored globally)
        let chatbot = window.chatbot;
        if (!chatbot) {
            console.log('🔄 No existing chatbot instance, will create new session with form data');
        }
        
        // Start chatbot session with form data
        const startResponse = await fetch(`${CHATBOT_API_BASE}/chat/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                frontend_data: frontendData
            })
        });
        
        console.log('📥 API Response status:', startResponse.status);
        
        if (!startResponse.ok) {
            const errorText = await startResponse.text();
            console.error('❌ API Error:', errorText);
            throw new Error(`HTTP error! status: ${startResponse.status} - ${errorText}`);
        }
        
        const chatSession = await startResponse.json();
        console.log('✅ Chatbot session started:', chatSession);
        
        // Update the existing chatbot widget instead of creating new interface
        updateExistingChatbot(chatSession, frontendData);
        
    } catch (error) {
        console.error('❌ Failed to start chatbot:', error);
        
        // Show user-friendly error message
        alert(`Sorry, there was an error connecting to the chatbot: ${error.message}. Please make sure the chatbot server is running on port 8001.`);
        
        throw error;
    }
}

function updateExistingChatbot(chatSession, frontendData) {
    console.log('🔄 Updating existing chatbot widget with session data');
    
    // Get or create the chatbot instance
    let chatbot = window.chatbot;
    if (!chatbot) {
        console.log('📱 No existing chatbot found, this should not happen');
        return;
    }
    
    // If chatbot already has a session, we need to handle this carefully
    if (chatbot.sessionId && chatbot.sessionId !== chatSession.session_id) {
        console.log('🔄 Chatbot has existing session, updating with new session that has form data');
        // Clear existing messages to avoid confusion
        chatbot.elements.messages.innerHTML = '';
    }
    
    // Update the chatbot's session ID with the new one that has form data
    chatbot.sessionId = chatSession.session_id;
    
    // Open the chatbot widget if it's not already open
    if (!chatbot.isOpen) {
        chatbot.openChat();
    }
    
    // Add the initial message that acknowledges the form data
    chatbot.addMessage('assistant', chatSession.message);
    
    // Add a visual indicator that form data was processed
    const formSummary = createFormDataSummary(frontendData);
    if (formSummary) {
        chatbot.addMessage('system', `📋 ${formSummary}`);
    }
    
    console.log('✅ Chatbot widget updated successfully');
    
    // Show success message to user
    showSuccessMessage('Form data sent to chatbot! The chat widget is now updated with your preferences.');
}

function createFormDataSummary(frontendData) {
    const parts = [];
    
    if (frontendData.location) {
        parts.push(`📍 ${frontendData.location}`);
    }
    
    if (frontendData.property_types && frontendData.property_types.length > 0) {
        const typeNames = frontendData.property_types.map(type => {
            const typeMap = {
                'primary-residence': 'Primary Residence',
                'fix-flip': 'Fix & Flip',
                'rental-property': 'Rental Property',
                'multi-family': 'Multi-Family',
                'quick-deals': 'Quick Deals'
            };
            return typeMap[type] || type;
        });
        parts.push(`🏠 ${typeNames.join(', ')}`);
    }
    
    if (frontendData.budget_min || frontendData.budget_max) {
        const budget = [];
        if (frontendData.budget_min) budget.push(`$${frontendData.budget_min.toLocaleString()}`);
        if (frontendData.budget_max) budget.push(`$${frontendData.budget_max.toLocaleString()}`);
        parts.push(`💰 ${budget.join(' - ')}`);
    }
    
    return parts.join(' • ');
}

function showSuccessMessage(message) {
    // Create a temporary success notification
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #10b981;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        z-index: 10000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        animation: slideIn 0.3s ease;
    `;
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
    
    // Add CSS animation
    if (!document.getElementById('success-animation-styles')) {
        const style = document.createElement('style');
        style.id = 'success-animation-styles';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
}



function getSearchFormData() {
    console.log('📋 Collecting form data...');
    
    const customBudgetEnabled = document.getElementById('custom-budget-toggle')?.checked;
    console.log('💰 Custom budget enabled:', customBudgetEnabled);
    
    let minPrice, maxPrice;
    
    if (customBudgetEnabled) {
        minPrice = parseInt(document.getElementById('custom-min-price')?.value) || 0;
        maxPrice = parseInt(document.getElementById('custom-max-price')?.value) || 0;
    } else {
        minPrice = parseInt(document.getElementById('min-price')?.value) || 0;
        maxPrice = parseInt(document.getElementById('max-price')?.value) || 0;
    }
    
    const location = document.getElementById('demo-location')?.value || '';
    const propertyTypes = getSelectedStrategies();
    
    console.log('📍 Location:', location);
    console.log('🏠 Property types:', propertyTypes);
    console.log('💵 Budget:', { min: minPrice, max: maxPrice });
    
    const formData = {
        location: location,
        propertyTypes: propertyTypes,
        budget: {
            min: minPrice,
            max: maxPrice,
            customBudget: customBudgetEnabled
        }
    };
    
    console.log('📦 Complete form data:', formData);
    return formData;
}

function getSelectedStrategies() {
    console.log('🎯 Checking selected strategies...');
    
    const strategies = [];
    
    const primaryResidence = document.getElementById('primary-residence')?.checked;
    const fixFlip = document.getElementById('fix-flip')?.checked;
    const rentalProperty = document.getElementById('rental-property')?.checked;
    const multiFamily = document.getElementById('multi-family')?.checked;
    const quickDeals = document.getElementById('quick-deals')?.checked;
    
    console.log('✓ Primary residence:', primaryResidence);
    console.log('✓ Fix & flip:', fixFlip);
    console.log('✓ Rental property:', rentalProperty);
    console.log('✓ Multi-family:', multiFamily);
    console.log('✓ Quick deals:', quickDeals);
    
    if (primaryResidence) {
        strategies.push('primary-residence');
    }
    if (fixFlip) {
        strategies.push('fix-flip');
    }
    if (rentalProperty) {
        strategies.push('rental-property');
    }
    if (multiFamily) {
        strategies.push('multi-family');
    }
    if (quickDeals) {
        strategies.push('quick-deals');
    }
    
    console.log('📋 Selected strategies:', strategies);
    return strategies;
}

function validateSearchData(data) {
    if (!data.location || data.location.trim() === '') {
        alert('Please enter a location (city, state, ZIP code, or address)');
        return false;
    }
    
    if (data.propertyTypes.length === 0) {
        alert('Please select at least one property type');
        return false;
    }
    
    return true;
}

async function simulatePropertySearch(searchData) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    console.log('Search parameters:', searchData);
}

function displaySearchResults(searchData) {
    const resultsSection = document.getElementById('demo-results-section');
    const resultsGrid = document.getElementById('demo-results-grid');
    
    if (!resultsSection || !resultsGrid) {
        console.warn('Results section elements not found');
        return;
    }
    
    // Generate sample results
    const sampleResults = generateSampleResults(searchData);
    
    // Clear previous results
    resultsGrid.innerHTML = '';
    
    // Add result cards
    sampleResults.forEach(property => {
        const card = createPropertyCard(property);
        resultsGrid.appendChild(card);
    });
    
    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function generateSampleResults(searchData) {
    const location = `${searchData.city || 'Sample City'}, ${searchData.state || 'ST'}`;
    const strategies = searchData.strategies;
    
    return [
        {
            price: '$245,000',
            address: `123 Investment St, ${location}`,
            bedrooms: 3,
            bathrooms: 2,
            sqft: 1850,
            tags: strategies.slice(0, 2),
            analysis: {
                potential: 'High',
                roi: '15.2%',
                cashFlow: '+$420/month'
            }
        },
        {
            price: '$189,500',
            address: `456 Opportunity Ave, ${location}`,
            bedrooms: 2,
            bathrooms: 1,
            sqft: 1200,
            tags: strategies.slice(0, 1),
            analysis: {
                potential: 'Medium',
                roi: '12.8%',
                cashFlow: '+$280/month'
            }
        },
        {
            price: '$315,000',
            address: `789 Profit Plaza, ${location}`,
            bedrooms: 4,
            bathrooms: 2.5,
            sqft: 2200,
            tags: strategies,
            analysis: {
                potential: 'High',
                roi: '18.5%',
                cashFlow: '+$650/month'
            }
        }
    ];
}

function createPropertyCard(property) {
    const card = document.createElement('div');
    card.className = 'demo-property-card animate-fade-in';
    
    const strategyLabels = {
        'fixer-upper': 'Fixer-Upper',
        'long-term-cashflow': 'Cash Flow',
        'quick-buy-sell': 'Quick Flip'
    };
    
    card.innerHTML = `
        <div class="demo-property-image">
            <i data-lucide="home" size="48"></i>
        </div>
        <div class="demo-property-info">
            <div class="demo-property-price">${property.price}</div>
            <div class="demo-property-address">${property.address}</div>
            <div class="demo-property-details">
                <div class="demo-property-detail">
                    <i data-lucide="bed" size="16"></i>
                    <span>${property.bedrooms} bed</span>
                </div>
                <div class="demo-property-detail">
                    <i data-lucide="bath" size="16"></i>
                    <span>${property.bathrooms} bath</span>
                </div>
                <div class="demo-property-detail">
                    <i data-lucide="maximize" size="16"></i>
                    <span>${property.sqft} sqft</span>
                </div>
            </div>
            <div class="demo-property-tags">
                ${property.tags.map(tag => 
                    `<span class="demo-property-tag">${strategyLabels[tag] || tag}</span>`
                ).join('')}
            </div>
        </div>
    `;
    
    return card;
}

// Chat functionality
function initChatFunctionality() {
    const chatInput = document.getElementById('demo-chat-input');
    const sendButton = document.getElementById('demo-chat-send');
    
    if (!chatInput || !sendButton) {
        console.warn('Chat elements not found');
        return;
    }
    
    sendButton.addEventListener('click', handleChatMessage);
    
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleChatMessage();
        }
    });
}

async function handleChatMessage() {
    const chatInput = document.getElementById('demo-chat-input');
    const messagesContainer = document.getElementById('demo-chat-messages');
    
    if (!chatInput || !messagesContainer) return;
    
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Clear input
    chatInput.value = '';
    
    // Add user message
    addChatMessage(message, 'user');
    
    // Simulate AI processing
    setTimeout(async () => {
        const response = await generateAIResponse(message);
        addChatMessage(response, 'ai');
    }, 1000);
}

function addChatMessage(content, type) {
    const messagesContainer = document.getElementById('demo-chat-messages');
    if (!messagesContainer) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `demo-message demo-message-${type}`;
    
    messageDiv.innerHTML = `
        <div class="demo-message-content">
            <p>${content}</p>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

async function generateAIResponse(userMessage) {
    // Simulate AI responses based on message content
    const responses = {
        default: "I'd be happy to help you with your real estate investment questions! I can assist with property analysis, market insights, and finding the right investment opportunities.",
        
        price: "Property prices vary significantly by location and market conditions. I analyze current market data, comparable sales, and price trends to help you identify undervalued opportunities.",
        
        location: "Location is crucial for real estate investment success. I consider factors like job growth, population trends, school districts, and future development plans when evaluating areas.",
        
        cash: "Cash flow properties typically offer steady monthly income. I look for properties where rental income exceeds all expenses (mortgage, taxes, insurance, maintenance) by a healthy margin.",
        
        flip: "For fix-and-flip properties, I analyze renovation costs, after-repair value (ARV), and local market demand. The key is finding properties with good bones in desirable neighborhoods."
    };
    
    const lowerMessage = userMessage.toLowerCase();
    
    if (lowerMessage.includes('price') || lowerMessage.includes('cost')) {
        return responses.price;
    } else if (lowerMessage.includes('location') || lowerMessage.includes('area') || lowerMessage.includes('where')) {
        return responses.location;
    } else if (lowerMessage.includes('cash') || lowerMessage.includes('rent') || lowerMessage.includes('income')) {
        return responses.cash;
    } else if (lowerMessage.includes('flip') || lowerMessage.includes('fix') || lowerMessage.includes('renovation')) {
        return responses.flip;
    } else {
        return responses.default;
    }
}

// Loading states
function showLoadingState() {
    const loading = document.getElementById('demo-loading');
    if (loading) {
        loading.style.display = 'flex';
    }
}

function hideLoadingState() {
    const loading = document.getElementById('demo-loading');
    if (loading) {
        loading.style.display = 'none';
    }
}

function showSearchError(message) {
    alert(`Search Error: ${message}`);
}

// Initialize demo page when it becomes active
const originalShowPage = showPage;
showPage = function(pageId) {
    originalShowPage(pageId);
    
    // Initialize demo page when it's shown
    if (pageId === 'demo') {
        setTimeout(() => {
            initDemoPage();
            // Re-initialize Lucide icons
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        }, 100);
    }
};

// ===== BACKEND API INTEGRATION =====

// API Configuration
const API_CONFIG = {
    baseUrl: 'http://localhost:8000', // Customer Agent Server
    endpoints: {
        chat: '/api/chat',
        search: '/api/search',
        preferences: '/api/preferences'
    }
};

// API Integration Functions
class EquityNestAPI {
    constructor() {
        this.sessionId = this.generateSessionId();
    }
    
    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }
    
    async sendChatMessage(message, context = {}) {
        try {
            const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.chat}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId,
                    context: {
                        page: 'demo',
                        user_preferences: context.preferences || {},
                        search_criteria: context.searchCriteria || {}
                    }
                })
            });
            
            if (!response.ok) {
                throw new Error(`Chat API request failed: ${response.status}`);
            }
            
            const data = await response.json();
            return data.response || data.message || 'Sorry, I had trouble processing that request.';
            
        } catch (error) {
            console.error('Chat API Error:', error);
            // Fallback to simulated response
            return await generateAIResponse(message);
        }
    }
    
    async searchProperties(searchData) {
        try {
            const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.search}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    location: {
                        state: searchData.state,
                        city: searchData.city,
                        zip_code: searchData.zip
                    },
                    investment_strategies: searchData.strategies,
                    price_range: {
                        min: searchData.priceRange.min,
                        max: searchData.priceRange.max
                    },
                    preferences: {
                        property_types: searchData.strategies,
                        budget_range: searchData.priceRange
                    }
                })
            });
            
            if (!response.ok) {
                throw new Error(`Search API request failed: ${response.status}`);
            }
            
            const data = await response.json();
            return data.properties || data.results || [];
            
        } catch (error) {
            console.error('Search API Error:', error);
            // Fallback to simulated results
            return generateSampleResults(searchData);
        }
    }
    
    async saveUserPreferences(preferences) {
        try {
            const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.preferences}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    preferences: preferences
                })
            });
            
            if (!response.ok) {
                throw new Error(`Preferences API request failed: ${response.status}`);
            }
            
            return await response.json();
            
        } catch (error) {
            console.error('Preferences API Error:', error);
            return { success: false, error: error.message };
        }
    }
}

// Global API instance
const equityNestAPI = new EquityNestAPI();

// Enhanced API-integrated functions
async function handleChatMessageWithAPI() {
    const chatInput = document.getElementById('demo-chat-input');
    const messagesContainer = document.getElementById('demo-chat-messages');
    
    if (!chatInput || !messagesContainer) return;
    
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Clear input
    chatInput.value = '';
    
    // Add user message
    addChatMessage(message, 'user');
    
    try {
        // Get current search context if available
        const searchContext = {
            searchCriteria: getSearchFormData(),
            preferences: getSelectedStrategies()
        };
        
        // Send to API
        const response = await equityNestAPI.sendChatMessage(message, searchContext);
        addChatMessage(response, 'ai');
        
    } catch (error) {
        console.error('Chat error:', error);
        addChatMessage('Sorry, I\'m having trouble connecting right now. Please try again later.', 'ai');
    }
}

async function handleSearchWithAPI() {
    console.log('Handling property search with API integration...');
    
    // Get form data
    const searchData = getSearchFormData();
    
    if (!validateSearchData(searchData)) {
        return;
    }
    
    // Save user preferences
    await equityNestAPI.saveUserPreferences({
        location: searchData,
        investment_strategies: searchData.strategies,
        price_range: searchData.priceRange
    });
    
    // Show loading state
    showLoadingState();
    
    try {
        // Call API for property search
        const properties = await equityNestAPI.searchProperties(searchData);
        
        // Display results
        displayAPISearchResults(properties, searchData);
        
        // Add chat message about search
        setTimeout(() => {
            addChatMessage(
                `I found ${properties.length} properties matching your criteria. These properties align with your selected investment strategies and price range. Would you like me to explain the analysis for any specific property?`, 
                'ai'
            );
        }, 500);
        
    } catch (error) {
        console.error('Search failed:', error);
        showSearchError(error.message);
    } finally {
        hideLoadingState();
    }
}

function displayAPISearchResults(properties, searchData) {
    const resultsSection = document.getElementById('demo-results-section');
    const resultsGrid = document.getElementById('demo-results-grid');
    
    if (!resultsSection || !resultsGrid) {
        console.warn('Results section elements not found');
        return;
    }
    
    // Clear previous results
    resultsGrid.innerHTML = '';
    
    // Handle empty results
    if (!properties || properties.length === 0) {
        resultsGrid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 2rem;">
                <h3>No properties found</h3>
                <p>Try adjusting your search criteria or expanding your location.</p>
            </div>
        `;
    } else {
        // Add result cards
        properties.forEach(property => {
            const card = createAPIPropertyCard(property);
            resultsGrid.appendChild(card);
        });
    }
    
    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function createAPIPropertyCard(property) {
    const card = document.createElement('div');
    card.className = 'demo-property-card animate-fade-in';
    
    // Handle both API response format and sample data format
    const price = property.price || property.list_price || '$0';
    const address = property.address || property.full_address || 'Address not available';
    const bedrooms = property.bedrooms || property.beds || 'N/A';
    const bathrooms = property.bathrooms || property.baths || 'N/A';
    const sqft = property.sqft || property.square_feet || property.size || 'N/A';
    const tags = property.tags || property.investment_types || ['Property'];
    
    card.innerHTML = `
        <div class="demo-property-image">
            ${property.image_url ? 
                `<img src="${property.image_url}" alt="Property" style="width: 100%; height: 100%; object-fit: cover;">` :
                `<i data-lucide="home" size="48"></i>`
            }
        </div>
        <div class="demo-property-info">
            <div class="demo-property-price">${price}</div>
            <div class="demo-property-address">${address}</div>
            <div class="demo-property-details">
                <div class="demo-property-detail">
                    <i data-lucide="bed" size="16"></i>
                    <span>${bedrooms} bed</span>
                </div>
                <div class="demo-property-detail">
                    <i data-lucide="bath" size="16"></i>
                    <span>${bathrooms} bath</span>
                </div>
                <div class="demo-property-detail">
                    <i data-lucide="maximize" size="16"></i>
                    <span>${sqft} sqft</span>
                </div>
            </div>
            <div class="demo-property-tags">
                ${Array.isArray(tags) ? tags.map(tag => 
                    `<span class="demo-property-tag">${tag}</span>`
                ).join('') : `<span class="demo-property-tag">${tags}</span>`}
            </div>
            ${property.ai_analysis ? `
                <div class="demo-property-analysis">
                    <small><strong>AI Analysis:</strong> ${property.ai_analysis}</small>
                </div>
            ` : ''}
        </div>
    `;
    
    return card;
}

// Update the existing handlers to use API integration
function updateDemoPageHandlers() {
    const searchButton = document.getElementById('demo-search-btn');
    const chatInput = document.getElementById('demo-chat-input');
    const sendButton = document.getElementById('demo-chat-send');
    
    if (searchButton) {
        searchButton.removeEventListener('click', handleSearch);
        searchButton.addEventListener('click', handleSearchWithAPI);
    }
    
    if (sendButton) {
        sendButton.removeEventListener('click', handleChatMessage);
        sendButton.addEventListener('click', handleChatMessageWithAPI);
    }
    
    if (chatInput) {
        chatInput.removeEventListener('keypress', handleChatKeypress);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleChatMessageWithAPI();
            }
        });
    }
}

function handleChatKeypress(e) {
    if (e.key === 'Enter') {
        handleChatMessageWithAPI();
    }
}

// Update initialization to use API handlers
const originalInitDemoPage = initDemoPage;
initDemoPage = function() {
    if (demoPageInitialized) return;
    
    console.log('Initializing Try EquityNest demo page with API integration...');
    
    // Initialize price sliders
    initPriceSliders();
    
    // Initialize search and chat with API integration
    updateDemoPageHandlers();
    
    demoPageInitialized = true;
    console.log('✅ Demo page with API integration initialized successfully');
};

document.head.appendChild(style);

document.body.classList.add('loaded');