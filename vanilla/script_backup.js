// EquityAI Vanilla JavaScript

// Simple routing system
const pages = {
    'home': 'home-page',
    'marketplace': 'marketplace-page',
    'analyzer': 'analyzer-page',
    'agent-connect': 'agent-connect-page',
    'pricing': 'pricing-page',
    'signin': 'signin-page',
    'signup': 'signup-page',
    'property-details': 'property-details-page'
};

let currentPage = 'home';
let currentFilters = {}; // Store marketplace filters

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 EquityNest JavaScript loaded - v2.2 (hashchange fix)!');
    console.log('Pages available:', Object.keys(pages));
    
    // Test if initRouter function exists
    console.log('initRouter function exists:', typeof initRouter);
    
    // Initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

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

        // Initialize page-specific functionality
        if (pageId === 'marketplace') {
            initializeMarketplace();
        }

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

    // Initialize router
    try {
        initRouter();
        console.log('✅ Router initialized successfully!');
    } catch (error) {
        console.error('❌ Router initialization failed:', error);
    }

    // Add a simple test click handler
    document.addEventListener('click', function(e) {
        if (e.target.closest('.property-card')) {
            console.log('🎯 PROPERTY CARD CLICKED! (Direct handler)');
            const card = e.target.closest('.property-card');
            const propertyId = card.getAttribute('data-property-id');
            console.log('Property ID:', propertyId);
        }
    });

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

// Marketplace functionality
const PROPERTIES = [
    {
        id: "p_001",
        address1: "123 Maple St",
        city: "Austin",
        state: "TX",
        zip: "78701",
        beds: 3,
        baths: 2,
        sqft: 2100,
        lotSqft: 8500,
        yearBuilt: 2018,
        hasGarage: true,
        type: "House",
        listPrice: 485000,
        estValue: 572000,
        photo: "hero-house.jpg",
        photos: ["hero-house.jpg", "investment-house.jpg", "houses-grid.jpg"]
    },
    {
        id: "p_002",
        address1: "456 Oak Ave",
        city: "Dallas",
        state: "TX",
        zip: "75201",
        beds: 4,
        baths: 3,
        sqft: 2850,
        lotSqft: 7200,
        yearBuilt: 2015,
        hasGarage: true,
        type: "House",
        listPrice: 625000,
        estValue: 590000,
        photo: "investment-house.jpg",
        photos: ["investment-house.jpg", "hero-house.jpg"]
    },
    {
        id: "p_003",
        address1: "789 Pine Dr",
        city: "Houston",
        state: "TX",
        zip: "77001",
        beds: 2,
        baths: 2,
        sqft: 1200,
        lotSqft: null,
        yearBuilt: 2020,
        hasGarage: false,
        type: "Condo",
        listPrice: 325000,
        estValue: 385000,
        photo: "houses-grid.jpg",
        photos: ["houses-grid.jpg", "hero-house.jpg", "investment-house.jpg"]
    },
    {
        id: "p_004",
        address1: "321 Elm St",
        city: "Phoenix",
        state: "AZ",
        zip: "85001",
        beds: 5,
        baths: 4,
        sqft: 3200,
        lotSqft: 12000,
        yearBuilt: 2017,
        hasGarage: true,
        type: "House",
        listPrice: 750000,
        estValue: 820000,
        photo: "hero-house.jpg",
        photos: ["hero-house.jpg", "investment-house.jpg", "houses-grid.jpg"]
    },
    {
        id: "p_005",
        address1: "654 Cedar Ln",
        city: "Miami",
        state: "FL",
        zip: "33101",
        beds: 3,
        baths: 2,
        sqft: 1850,
        lotSqft: 3200,
        yearBuilt: 2019,
        hasGarage: true,
        type: "Townhouse",
        listPrice: 545000,
        estValue: 525000,
        photo: "investment-house.jpg",
        photos: ["investment-house.jpg", "houses-grid.jpg"]
    },
    {
        id: "p_006",
        address1: "987 Birch Way",
        city: "Denver",
        state: "CO",
        zip: "80201",
        beds: 4,
        baths: 3,
        type: "House",
        listPrice: 695000,
        estValue: 745000,
        photo: "houses-grid.jpg"
    },
    {
        id: "p_007",
        address1: "147 Willow St",
        city: "Seattle",
        state: "WA",
        zip: "98101",
        beds: 2,
        baths: 1,
        type: "Apartment",
        listPrice: 425000,
        estValue: 465000,
        photo: "hero-house.jpg"
    },
    {
        id: "p_008",
        address1: "258 Spruce Ave",
        city: "Portland",
        state: "OR",
        zip: "97201",
        beds: 3,
        baths: 2,
        type: "House",
        listPrice: 535000,
        estValue: 580000,
        photo: "investment-house.jpg"
    },
    {
        id: "p_009",
        address1: "369 Maple Ct",
        city: "Nashville",
        state: "TN",
        zip: "37201",
        beds: 4,
        baths: 3,
        type: "House",
        listPrice: 450000,
        estValue: 520000,
        photo: "houses-grid.jpg"
    },
    {
        id: "p_010",
        address1: "741 Oak Ridge",
        city: "Atlanta",
        state: "GA",
        zip: "30301",
        beds: 3,
        baths: 2,
        type: "Condo",
        listPrice: 375000,
        estValue: 395000,
        photo: "hero-house.jpg"
    },
    {
        id: "p_011",
        address1: "852 Pine Valley",
        city: "Charlotte",
        state: "NC",
        zip: "28201",
        beds: 5,
        baths: 4,
        type: "House",
        listPrice: 680000,
        estValue: 725000,
        photo: "investment-house.jpg"
    },
    {
        id: "p_012",
        address1: "963 Cedar Hills",
        city: "Raleigh",
        state: "NC",
        zip: "27601",
        beds: 2,
        baths: 2,
        type: "Townhouse",
        listPrice: 295000,
        estValue: 340000,
        photo: "houses-grid.jpg"
    },
    {
        id: "p_013",
        address1: "159 Elm Grove",
        city: "Tampa",
        state: "FL",
        zip: "33601",
        beds: 3,
        baths: 3,
        type: "House",
        listPrice: 465000,
        estValue: 485000,
        photo: "hero-house.jpg"
    },
    {
        id: "p_014",
        address1: "357 Birch Bay",
        city: "Orlando",
        state: "FL",
        zip: "32801",
        beds: 4,
        baths: 2,
        type: "House",
        listPrice: 385000,
        estValue: 435000,
        photo: "investment-house.jpg"
    },
    {
        id: "p_015",
        address1: "486 Willow Creek",
        city: "Las Vegas",
        state: "NV",
        zip: "89101",
        beds: 3,
        baths: 2,
        type: "House",
        listPrice: 415000,
        estValue: 445000,
        photo: "houses-grid.jpg"
    },
    {
        id: "p_016",
        address1: "792 Spruce Mountain",
        city: "Salt Lake City",
        state: "UT",
        zip: "84101",
        beds: 4,
        baths: 3,
        type: "House",
        listPrice: 525000,
        estValue: 565000,
        photo: "hero-house.jpg"
    },
    {
        id: "p_017",
        address1: "135 Maple Ridge",
        city: "Kansas City",
        state: "MO",
        zip: "64101",
        beds: 5,
        baths: 3,
        type: "House",
        listPrice: 345000,
        estValue: 395000,
        photo: "investment-house.jpg"
    },
    {
        id: "p_018",
        address1: "246 Oak Terrace",
        city: "Columbus",
        state: "OH",
        zip: "43201",
        beds: 2,
        baths: 1,
        type: "Condo",
        listPrice: 235000,
        estValue: 275000,
        photo: "houses-grid.jpg"
    },
    {
        id: "p_019",
        address1: "468 Pine Street",
        city: "Richmond",
        state: "VA",
        zip: "23220",
        beds: 3,
        baths: 2,
        type: "Townhouse",
        listPrice: 315000,
        estValue: 355000,
        photo: "hero-house.jpg"
    },
    {
        id: "p_020",
        address1: "579 Cedar Park",
        city: "Indianapolis",
        state: "IN",
        zip: "46201",
        beds: 4,
        baths: 3,
        type: "House",
        listPrice: 285000,
        estValue: 335000,
        photo: "investment-house.jpg"
    },
    {
        id: "p_021",
        address1: "681 Elm Heights",
        city: "Milwaukee",
        state: "WI",
        zip: "53201",
        beds: 3,
        baths: 2,
        type: "Multifamily",
        listPrice: 395000,
        estValue: 425000,
        photo: "houses-grid.jpg"
    },
    {
        id: "p_022",
        address1: "792 Birch Glen",
        city: "Minneapolis",
        state: "MN",
        zip: "55401",
        beds: 2,
        baths: 2,
        type: "Condo",
        listPrice: 365000,
        estValue: 385000,
        photo: "hero-house.jpg"
    },
    {
        id: "p_023",
        address1: "813 Willow Park",
        city: "San Antonio",
        state: "TX",
        zip: "78201",
        beds: 4,
        baths: 3,
        type: "House",
        listPrice: 425000,
        estValue: 475000,
        photo: "investment-house.jpg"
    },
    {
        id: "p_024",
        address1: "924 Spruce Hill",
        city: "Oklahoma City",
        state: "OK",
        zip: "73101",
        beds: 5,
        baths: 4,
        type: "House",
        listPrice: 355000,
        estValue: 405000,
        photo: "houses-grid.jpg"
    }
];

let filteredProperties = [...PROPERTIES];
let currentSort = 'price-low';
let currentPageNum = 1;
const itemsPerPage = 9;

// Marketplace initialization
function initializeMarketplace() {
    // Set up event listeners
    const locationInput = document.getElementById('location-input');
    const stateSelect = document.getElementById('state-select');
    const minPriceInput = document.getElementById('min-price');
    const maxPriceInput = document.getElementById('max-price');
    const bedsSelect = document.getElementById('beds-select');
    const bathsSelect = document.getElementById('baths-select');
    const typeSelect = document.getElementById('type-select');
    const sortSelect = document.getElementById('sort-select');
    const resetButton = document.querySelector('.reset-filters');
    const prevButton = document.getElementById('prev-page');
    const nextButton = document.getElementById('next-page');

    // Debounced filter function
    const debouncedFilter = debounce(applyFilters, 250);

    // Event listeners
    if (locationInput) locationInput.addEventListener('input', debouncedFilter);
    if (stateSelect) stateSelect.addEventListener('change', applyFilters);
    if (minPriceInput) minPriceInput.addEventListener('input', updatePriceLabels);
    if (maxPriceInput) maxPriceInput.addEventListener('input', updatePriceLabels);
    if (minPriceInput) minPriceInput.addEventListener('change', applyFilters);
    if (maxPriceInput) maxPriceInput.addEventListener('change', applyFilters);
    if (bedsSelect) bedsSelect.addEventListener('change', applyFilters);
    if (bathsSelect) bathsSelect.addEventListener('change', applyFilters);
    if (typeSelect) typeSelect.addEventListener('change', applyFilters);
    if (sortSelect) sortSelect.addEventListener('change', (e) => {
        currentSort = e.target.value;
        sortResults();
        renderResults();
    });
    if (resetButton) resetButton.addEventListener('click', resetFilters);
    if (prevButton) prevButton.addEventListener('click', () => changePage(-1));
    if (nextButton) nextButton.addEventListener('click', () => changePage(1));

    // Initial render
    updatePriceLabels();
    applyFilters();
    
    // Debug: Check property cards after they're created
    setTimeout(() => {
        const propertyCards = document.querySelectorAll('.property-card');
        console.log('✅ Property cards found:', propertyCards.length);
        propertyCards.forEach((card, index) => {
            const id = card.getAttribute('data-property-id');
            console.log(`📋 Card ${index}: ID = ${id}`);
        });
    }, 200);
}

function updatePriceLabels() {
    const minPrice = document.getElementById('min-price')?.value || 0;
    const maxPrice = document.getElementById('max-price')?.value || 10000000;
    const minLabel = document.getElementById('min-price-label');
    const maxLabel = document.getElementById('max-price-label');
    
    if (minLabel) minLabel.textContent = formatMoney(minPrice);
    if (maxLabel) maxLabel.textContent = formatMoney(maxPrice);
}

function applyFilters() {
    const location = document.getElementById('location-input')?.value.toLowerCase() || '';
    const state = document.getElementById('state-select')?.value || '';
    const minPrice = parseInt(document.getElementById('min-price')?.value || 0);
    const maxPrice = parseInt(document.getElementById('max-price')?.value || 10000000);
    const beds = parseInt(document.getElementById('beds-select')?.value || 0);
    const baths = parseInt(document.getElementById('baths-select')?.value || 0);
    const type = document.getElementById('type-select')?.value || '';

    filteredProperties = PROPERTIES.filter(property => {
        // Location filter (city or ZIP)
        if (location) {
            const matchesCity = property.city.toLowerCase().includes(location);
            const matchesZip = property.zip.includes(location);
            if (!matchesCity && !matchesZip) return false;
        }

        // State filter
        if (state && property.state !== state) return false;

        // Price range filter
        if (property.listPrice < minPrice || property.listPrice > maxPrice) return false;

        // Beds filter (at least N)
        if (beds && property.beds < beds) return false;

        // Baths filter (at least N)
        if (baths && property.baths < baths) return false;

        // Type filter
        if (type && property.type !== type) return false;

        return true;
    });

    currentPageNum = 1;
    sortResults();
    renderResults();
}

function sortResults() {
    filteredProperties.sort((a, b) => {
        switch (currentSort) {
            case 'price-low':
                return a.listPrice - b.listPrice;
            case 'price-high':
                return b.listPrice - a.listPrice;
            case 'savings-high':
                return computeSavings(b) - computeSavings(a);
            case 'savings-low':
                return computeSavings(a) - computeSavings(b);
            default:
                return 0;
        }
    });
}

function renderResults() {
    const grid = document.getElementById('properties-grid');
    const resultsCount = document.getElementById('results-count');
    const pageInfo = document.getElementById('page-info');
    const prevButton = document.getElementById('prev-page');
    const nextButton = document.getElementById('next-page');

    if (!grid) return;

    // Calculate pagination
    const totalPages = Math.ceil(filteredProperties.length / itemsPerPage);
    const startIndex = (currentPageNum - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const currentPageProperties = filteredProperties.slice(startIndex, endIndex);

    // Update results count
    if (resultsCount) {
        resultsCount.textContent = `${filteredProperties.length} properties found`;
    }

    // Update page info
    if (pageInfo) {
        pageInfo.textContent = `Page ${currentPageNum} of ${totalPages || 1}`;
    }

    // Update pagination buttons
    if (prevButton) {
        prevButton.disabled = currentPageNum <= 1;
    }
    if (nextButton) {
        nextButton.disabled = currentPageNum >= totalPages;
    }

    // Render property cards
    grid.innerHTML = currentPageProperties.map(property => {
        const savings = computeSavings(property);
        const savingsClass = savings > 0 ? 'positive' : 'neutral';
        const savingsText = savings > 0 ? `You save ${formatMoney(savings)}` : '—';

        return `
            <div class="property-card" data-property-id="${property.id}">
                <img src="${property.photo}" alt="${property.address1}" class="property-photo">
                <div class="property-info">
                    <div class="property-address">${property.address1}</div>
                    <div class="property-location">${property.city}, ${property.state} ${property.zip}</div>
                    <div class="property-details">
                        <span>${property.beds} beds</span>
                        <span>${property.baths} baths</span>
                        <span>${property.type}</span>
                    </div>
                    <div class="property-prices">
                        <div class="property-list-price">${formatMoney(property.listPrice)}</div>
                        <div class="property-est-value">Est. Value: ${formatMoney(property.estValue)}</div>
                        <div class="property-savings ${savingsClass}">${savingsText}</div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function resetFilters() {
    document.getElementById('location-input').value = '';
    document.getElementById('state-select').value = '';
    document.getElementById('min-price').value = '0';
    document.getElementById('max-price').value = '10000000';
    document.getElementById('beds-select').value = '';
    document.getElementById('baths-select').value = '';
    document.getElementById('type-select').value = '';
    document.getElementById('sort-select').value = 'price-low';
    
    currentSort = 'price-low';
    updatePriceLabels();
    applyFilters();
}

function changePage(direction) {
    const totalPages = Math.ceil(filteredProperties.length / itemsPerPage);
    const newPage = currentPageNum + direction;
    
    if (newPage >= 1 && newPage <= totalPages) {
        currentPageNum = newPage;
        renderResults();
        
        // Scroll to top of results
        const resultsPanel = document.querySelector('.results-panel');
        if (resultsPanel) {
            resultsPanel.scrollIntoView({ behavior: 'smooth' });
        }
    }
}

// Utility functions
function formatMoney(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function computeSavings(property) {
    return property.estValue - property.listPrice;
}

// Router System
function initRouter() {
    // Handle browser back/forward
    window.addEventListener('popstate', handleRoute);
    
    // ✅ Also handle hash-based navigation
    window.addEventListener('hashchange', handleRoute);
    
    // Handle initial page load
    handleRoute();
    
    // Add click handlers for property cards (will be added dynamically)
    document.addEventListener('click', (e) => {
        if (e.target.closest('.property-card')) {
            e.preventDefault();
            const card = e.target.closest('.property-card');
            const propertyId = card.getAttribute('data-property-id');
            console.log('Property card clicked:', propertyId, card);
            if (propertyId) {
                navigateToProperty(propertyId);
            } else {
                console.log('No property ID found on card:', card);
            }
        }
    });
}

function handleRoute() {
    const hash = window.location.hash.slice(1); // Remove #
    console.log('Handling route:', hash);
    
    if (hash.startsWith('property/')) {
        const propertyId = hash.split('/')[1];
        console.log('Property route detected, ID:', propertyId);
        showPropertyDetails(propertyId);
    } else if (hash === 'marketplace') {
        console.log('Marketplace route detected');
        showPage('marketplace');
    } else {
        console.log('Home route detected');
        showPage('home');
    }
}

function navigateToProperty(propertyId) {
    console.log('Navigating to property:', propertyId);
    window.location.hash = `property/${propertyId}`;
}

function navigateToMarketplace() {
    window.location.hash = 'marketplace';
}

function navigateToHome() {
    window.location.hash = '';
}

function showPropertyDetails(propertyId) {
    console.log('Showing property details for:', propertyId);
    const property = PROPERTIES.find(p => p.id === propertyId);
    if (!property) {
        console.log('Property not found:', propertyId);
        showPage('home');
        return;
    }
    
    console.log('Found property:', property);
    
    // Show property details page
    Object.keys(pages).forEach(page => {
        const pageElement = document.getElementById(pages[page]);
        if (pageElement) pageElement.style.display = 'none';
    });
    const detailsPage = document.getElementById(pages['property-details']);
    if (detailsPage) detailsPage.style.display = 'block';
    
    // Render property details
    renderPropertyDetails(property);
}

function renderPropertyDetails(property) {
    // Update hero image
    const heroImage = document.getElementById('property-hero-image');
    if (heroImage) {
        heroImage.src = property.photo;
        heroImage.alt = `${property.address1}, ${property.city}`;
    }
    
    // Update address
    const addressElement = document.getElementById('property-address');
    if (addressElement) {
        addressElement.textContent = `${property.address1}, ${property.city}, ${property.state} ${property.zip}`;
    }
    
    // Update price
    const priceElement = document.getElementById('property-list-price');
    if (priceElement) {
        priceElement.textContent = formatMoney(property.listPrice);
    }
    
    // Update estimated value
    const estValueElement = document.getElementById('property-est-value');
    if (estValueElement) {
        estValueElement.textContent = formatMoney(property.estValue);
    }
    
    // Calculate and update potential savings
    const savings = property.estValue - property.listPrice;
    const savingsElement = document.getElementById('property-savings');
    if (savingsElement) {
        if (savings > 0) {
            savingsElement.textContent = `+${formatMoney(savings)}`;
            savingsElement.style.color = '#16a34a';
        } else {
            savingsElement.textContent = formatMoney(savings);
            savingsElement.style.color = '#dc2626';
        }
    }
    
    // Update property facts
    const factsGrid = document.getElementById('property-facts');
    if (factsGrid) {
        factsGrid.innerHTML = `
            <div class="fact-item">
                <dt>Bedrooms</dt>
                <dd>${property.beds}</dd>
            </div>
            <div class="fact-item">
                <dt>Bathrooms</dt>
                <dd>${property.baths}</dd>
            </div>
            <div class="fact-item">
                <dt>Square Feet</dt>
                <dd>${property.sqft ? property.sqft.toLocaleString() : 'N/A'}</dd>
            </div>
            <div class="fact-item">
                <dt>Lot Size</dt>
                <dd>${property.lotSqft ? property.lotSqft.toLocaleString() + ' sqft' : 'N/A'}</dd>
            </div>
            <div class="fact-item">
                <dt>Year Built</dt>
                <dd>${property.yearBuilt || 'N/A'}</dd>
            </div>
            <div class="fact-item">
                <dt>Garage</dt>
                <dd>${property.hasGarage ? 'Yes' : 'No'}</dd>
            </div>
            <div class="fact-item">
                <dt>Property Type</dt>
                <dd>${property.type}</dd>
            </div>
        `;
    }
    
    // Update photo thumbnails
    const photoStrip = document.getElementById('photo-strip');
    if (photoStrip && property.photos && property.photos.length > 1) {
        photoStrip.style.display = 'block';
        photoStrip.innerHTML = property.photos.map(photo => `
            <img src="${photo}" alt="Property photo" class="photo-thumbnail" onclick="updateMainPhoto('${photo}')">
        `).join('');
    } else if (photoStrip) {
        photoStrip.style.display = 'none';
    }
}

function updateMainPhoto(photoSrc) {
    const heroImage = document.querySelector('#property-details .property-hero-image');
    if (heroImage) {
        heroImage.src = photoSrc;
    }
}