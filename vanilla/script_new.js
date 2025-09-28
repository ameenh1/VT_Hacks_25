// EquityNest - Clean Implementation

// Simple page navigation
const pages = {
    'home': 'home-page',
    'marketplace': 'marketplace-page',
    'property-details': 'property-details-page'
};

let currentPage = 'home';
let selectedProperty = null;

// Sample property data
const PROPERTIES = [
    {
        id: "p_001",
        address1: "123 Oak Street",
        city: "Austin",
        state: "TX",
        zip: "78701",
        beds: 3,
        baths: 2,
        sqft: 1850,
        lotSqft: 7200,
        yearBuilt: 2018,
        hasGarage: true,
        type: "Single Family",
        listPrice: 485000,
        estValue: 510000,
        photo: "hero-house.jpg",
        photos: ["hero-house.jpg", "houses-grid.jpg"]
    },
    {
        id: "p_002",
        address1: "456 Pine Avenue",
        city: "Dallas",
        state: "TX",
        zip: "75201",
        beds: 4,
        baths: 3,
        sqft: 2200,
        lotSqft: 8500,
        yearBuilt: 2020,
        hasGarage: true,
        type: "Single Family",
        listPrice: 625000,
        estValue: 645000,
        photo: "houses-grid.jpg",
        photos: ["houses-grid.jpg", "investment-house.jpg"]
    },
    {
        id: "p_003",
        address1: "789 Maple Drive",
        city: "Houston",
        state: "TX",
        zip: "77001",
        beds: 2,
        baths: 2,
        sqft: 1200,
        lotSqft: 5000,
        yearBuilt: 2015,
        hasGarage: false,
        type: "Condo",
        listPrice: 285000,
        estValue: 295000,
        photo: "investment-house.jpg",
        photos: ["investment-house.jpg", "hero-house.jpg"]
    }
];

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 EquityNest - Clean Version Loaded!');
    
    // Initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    // Set up navigation
    setupNavigation();
    
    // Initialize marketplace when loaded
    if (document.getElementById('marketplace-page')) {
        initializeMarketplace();
    }
    
    // Set up property details functionality
    setupPropertyDetails();
});

// Simple navigation system
function setupNavigation() {
    // Handle nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const pageId = link.getAttribute('data-page');
            showPage(pageId);
        });
    });
    
    // Logo click goes home
    const logo = document.querySelector('.navbar-brand');
    if (logo) {
        logo.addEventListener('click', (e) => {
            e.preventDefault();
            showPage('home');
        });
    }
}

function showPage(pageId) {
    console.log('Showing page:', pageId);
    
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.style.display = 'none';
    });
    
    // Show target page
    const targetPageId = pages[pageId] || pages['home'];
    const targetPage = document.getElementById(targetPageId);
    if (targetPage) {
        targetPage.style.display = 'block';
        currentPage = pageId;
        
        // Initialize page-specific functionality
        if (pageId === 'marketplace') {
            renderProperties();
        }
    }
    
    // Re-initialize icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

// Marketplace functionality
function initializeMarketplace() {
    console.log('Marketplace initialized');
}

function renderProperties() {
    const container = document.getElementById('properties-grid');
    if (!container) return;
    
    console.log('Rendering', PROPERTIES.length, 'properties');
    
    const propertiesHTML = PROPERTIES.map(property => {
        const savings = property.estValue - property.listPrice;
        const savingsClass = savings > 0 ? 'positive' : savings < 0 ? 'negative' : 'neutral';
        const savingsText = savings > 0 ? `You save ${formatMoney(savings)}` : savings < 0 ? `${formatMoney(savings)}` : 'Fair value';
        
        return `
            <div class="property-card" onclick="showPropertyDetails('${property.id}')">
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
    
    container.innerHTML = propertiesHTML;
    console.log('Properties rendered to container');
}

// Property details functionality
function setupPropertyDetails() {
    // Back button
    const backButton = document.querySelector('.back-to-results');
    if (backButton) {
        backButton.addEventListener('click', () => {
            showPage('marketplace');
        });
    }
}

function showPropertyDetails(propertyId) {
    console.log('📋 Showing property details for:', propertyId);
    
    const property = PROPERTIES.find(p => p.id === propertyId);
    if (!property) {
        console.error('Property not found:', propertyId);
        return;
    }
    
    selectedProperty = property;
    
    // Show property details page
    showPage('property-details');
    
    // Render the property details
    renderPropertyDetails(property);
}

function renderPropertyDetails(property) {
    console.log('Rendering details for:', property.address1);
    
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
    
    // Update prices
    const listPriceElement = document.getElementById('property-list-price');
    if (listPriceElement) {
        listPriceElement.textContent = formatMoney(property.listPrice);
    }
    
    const estValueElement = document.getElementById('property-est-value');
    if (estValueElement) {
        estValueElement.textContent = formatMoney(property.estValue);
    }
    
    // Update savings
    const savings = property.estValue - property.listPrice;
    const savingsElement = document.getElementById('property-savings');
    if (savingsElement) {
        if (savings > 0) {
            savingsElement.textContent = `You save ${formatMoney(savings)}`;
            savingsElement.className = 'savings-pill positive';
        } else if (savings < 0) {
            savingsElement.textContent = `${formatMoney(savings)}`;
            savingsElement.className = 'savings-pill negative';
        } else {
            savingsElement.textContent = 'Fair value';
            savingsElement.className = 'savings-pill neutral';
        }
    }
    
    // Update facts
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
    const heroImage = document.getElementById('property-hero-image');
    if (heroImage) {
        heroImage.src = photoSrc;
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