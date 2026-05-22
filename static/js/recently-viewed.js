/**
 * PAWFECT FINDS - RECENTLY VIEWED PRODUCTS
 * Tracks and displays recently viewed products using localStorage
 */

(function() {
    'use strict';

    const STORAGE_KEY = 'pawfect-finds-recently-viewed';
    const MAX_ITEMS = 8; // Maximum number of products to track

    /**
     * Get recently viewed products from localStorage
     */
    function getRecentlyViewed() {
        try {
            const data = localStorage.getItem(STORAGE_KEY);
            return data ? JSON.parse(data) : [];
        } catch (e) {
            console.error('Error reading recently viewed products:', e);
            return [];
        }
    }

    /**
     * Save recently viewed products to localStorage
     */
    function saveRecentlyViewed(products) {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(products));
        } catch (e) {
            console.error('Error saving recently viewed products:', e);
        }
    }

    /**
     * Add a product to recently viewed list
     */
    function addProduct(product) {
        if (!product || !product.id) {
            console.warn('Invalid product data');
            return;
        }

        let products = getRecentlyViewed();

        // Remove if already exists (to move to front)
        products = products.filter(p => p.id !== product.id);

        // Add to beginning
        products.unshift({
            id: product.id,
            name: product.name,
            price: product.price,
            image_url: product.image_url,
            category: product.category,
            seller: product.seller,
            timestamp: Date.now()
        });

        // Keep only MAX_ITEMS
        if (products.length > MAX_ITEMS) {
            products = products.slice(0, MAX_ITEMS);
        }

        saveRecentlyViewed(products);

        // Dispatch event for UI updates
        window.dispatchEvent(new CustomEvent('recentlyViewedUpdated', { 
            detail: { products } 
        }));
    }

    /**
     * Remove a product from recently viewed
     */
    function removeProduct(productId) {
        let products = getRecentlyViewed();
        products = products.filter(p => p.id !== productId);
        saveRecentlyViewed(products);

        window.dispatchEvent(new CustomEvent('recentlyViewedUpdated', { 
            detail: { products } 
        }));
    }

    /**
     * Clear all recently viewed products
     */
    function clearAll() {
        localStorage.removeItem(STORAGE_KEY);
        window.dispatchEvent(new CustomEvent('recentlyViewedUpdated', { 
            detail: { products: [] } 
        }));
    }

    /**
     * Render recently viewed products in a container
     */
    function renderProducts(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const products = getRecentlyViewed();

        if (products.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center py-4">
                    <i class="fas fa-eye-slash fa-3x text-muted mb-3"></i>
                    <p class="text-muted">No recently viewed products yet</p>
                </div>
            `;
            return;
        }

        const html = products.map(product => `
            <div class="col-md-6 col-lg-3">
                <div class="card product-card h-100">
                    <img src="${escapeHtml(product.image_url || '/static/placeholder.png')}" 
                         class="card-img-top" 
                         alt="${escapeHtml(product.name)}" 
                         style="height: 200px; object-fit: cover;"
                         loading="lazy">
                    <div class="card-body d-flex flex-column">
                        <h6 class="card-title">${escapeHtml(product.name)}</h6>
                        <div class="d-flex justify-content-between align-items-center mt-auto">
                            <strong class="text-primary">$${parseFloat(product.price).toFixed(2)}</strong>
                            ${product.seller ? `<small class="text-muted">${escapeHtml(product.seller)}</small>` : ''}
                        </div>
                        <a href="/product/${product.id}" class="btn btn-primary btn-sm mt-2">
                            View Details
                        </a>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    /**
     * Escape HTML to prevent XSS
     */
    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return String(text).replace(/[&<>"']/g, m => map[m]);
    }

    /**
     * Auto-track product view on product detail pages
     */
    function autoTrackProductView() {
        // Look for product data in page meta tags or data attributes
        const productData = document.querySelector('[data-product-info]');
        
        if (productData) {
            try {
                const product = JSON.parse(productData.getAttribute('data-product-info'));
                addProduct(product);
            } catch (e) {
                console.error('Error parsing product data:', e);
            }
        }
    }

    /**
     * Initialize recently viewed tracking
     */
    function init() {
        // Auto-track if on product page
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', autoTrackProductView);
        } else {
            autoTrackProductView();
        }

        // Render recently viewed if container exists
        const container = document.getElementById('recentlyViewedProducts');
        if (container) {
            renderProducts('recentlyViewedProducts');
        }

        // Listen for updates
        window.addEventListener('recentlyViewedUpdated', (e) => {
            if (container) {
                renderProducts('recentlyViewedProducts');
            }
        });
    }

    /**
     * Public API
     */
    window.RecentlyViewed = {
        add: addProduct,
        remove: removeProduct,
        getAll: getRecentlyViewed,
        clear: clearAll,
        render: renderProducts
    };

    // Initialize
    init();
})();
