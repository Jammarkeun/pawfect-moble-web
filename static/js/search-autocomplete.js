/**
 * PAWFECT FINDS - ENHANCED SEARCH WITH AUTOCOMPLETE
 * Real-time search suggestions with keyboard navigation
 */

(function() {
    'use strict';

    const DEBOUNCE_DELAY = 300; // milliseconds
    const MIN_SEARCH_LENGTH = 2;
    const MAX_RESULTS = 8;

    let searchTimeout = null;
    let currentFocus = -1;
    let searchInput = null;
    let autocompleteContainer = null;

    /**
     * Initialize search autocomplete
     */
    function init() {
        searchInput = document.getElementById('search');
        if (!searchInput) return;

        // Create autocomplete container
        createAutocompleteContainer();

        // Attach event listeners
        searchInput.addEventListener('input', handleInput);
        searchInput.addEventListener('keydown', handleKeyDown);
        searchInput.addEventListener('focus', handleFocus);

        // Close autocomplete when clicking outside
        document.addEventListener('click', function(e) {
            if (e.target !== searchInput) {
                closeAutocomplete();
            }
        });
    }

    /**
     * Create autocomplete dropdown container
     */
    function createAutocompleteContainer() {
        autocompleteContainer = document.createElement('div');
        autocompleteContainer.id = 'search-autocomplete';
        autocompleteContainer.className = 'search-autocomplete';
        
        // Position relative to search input
        const parent = searchInput.closest('.search-bar') || searchInput.parentElement;
        parent.style.position = 'relative';
        parent.appendChild(autocompleteContainer);
    }

    /**
     * Handle input event with debouncing
     */
    function handleInput(e) {
        const query = e.target.value.trim();

        // Clear previous timeout
        clearTimeout(searchTimeout);

        // Close autocomplete if query is too short
        if (query.length < MIN_SEARCH_LENGTH) {
            closeAutocomplete();
            return;
        }

        // Show loading state
        showLoading();

        // Debounce the search
        searchTimeout = setTimeout(() => {
            fetchSuggestions(query);
        }, DEBOUNCE_DELAY);
    }

    /**
     * Handle focus event - show recent searches
     */
    function handleFocus() {
        const query = searchInput.value.trim();
        if (query.length >= MIN_SEARCH_LENGTH) {
            fetchSuggestions(query);
        } else {
            showRecentSearches();
        }
    }

    /**
     * Handle keyboard navigation
     */
    function handleKeyDown(e) {
        const items = autocompleteContainer.querySelectorAll('.autocomplete-item');
        
        if (!items.length) return;

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            currentFocus++;
            if (currentFocus >= items.length) currentFocus = 0;
            setActive(items);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            currentFocus--;
            if (currentFocus < 0) currentFocus = items.length - 1;
            setActive(items);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (currentFocus > -1 && items[currentFocus]) {
                items[currentFocus].click();
            } else {
                // Submit the form with current search
                searchInput.closest('form').submit();
            }
        } else if (e.key === 'Escape') {
            closeAutocomplete();
        }
    }

    /**
     * Set active item in autocomplete list
     */
    function setActive(items) {
        items.forEach((item, index) => {
            if (index === currentFocus) {
                item.classList.add('active');
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove('active');
            }
        });
    }

    /**
     * Fetch search suggestions from server
     */
    async function fetchSuggestions(query) {
        try {
            const response = await fetch(`/search/suggestions?q=${encodeURIComponent(query)}`);
            
            if (!response.ok) {
                // Fallback to client-side filtering if API not available
                showClientSideSuggestions(query);
                return;
            }

            const data = await response.json();
            const normalized = [];

            if (Array.isArray(data.products)) {
                data.products.forEach(product => {
                    normalized.push({
                        name: product.name,
                        type: 'product',
                        url: product.id ? `/product/${product.id}` : null
                    });
                });
            }

            if (Array.isArray(data.categories)) {
                data.categories.forEach(category => {
                    normalized.push({
                        name: category.name,
                        type: 'category',
                        url: category.id ? `/search?category=${category.id}` : null
                    });
                });
            }

            displaySuggestions(normalized.slice(0, MAX_RESULTS), query);
        } catch (error) {
            console.error('Search error:', error);
            showClientSideSuggestions(query);
        }
    }

    /**
     * Client-side filtering fallback
     */
    function showClientSideSuggestions(query) {
        // Get all product names from the page
        const productCards = document.querySelectorAll('.product-card .card-title');
        const suggestions = [];

        productCards.forEach(card => {
            const name = card.textContent.trim();
            if (name.toLowerCase().includes(query.toLowerCase())) {
                suggestions.push({
                    name: name,
                    type: 'product',
                    url: card.closest('.card').querySelector('a[href*="product"]')?.href || '#'
                });
            }
        });

        displaySuggestions(suggestions.slice(0, MAX_RESULTS), query);
    }

    /**
     * Display suggestions in autocomplete dropdown
     */
    function displaySuggestions(suggestions, query) {
        autocompleteContainer.innerHTML = '';
        currentFocus = -1;

        if (suggestions.length === 0) {
            showNoResults(query);
            return;
        }

        suggestions.forEach((suggestion, index) => {
            const item = createSuggestionItem(suggestion, query);
            autocompleteContainer.appendChild(item);
        });

        autocompleteContainer.style.display = 'block';
        saveRecentSearch(query);
    }

    /**
     * Create suggestion item element
     */
    function createSuggestionItem(suggestion, query) {
        const item = document.createElement('div');
        item.className = 'autocomplete-item';

        // Highlight matching text
        const name = suggestion.name || suggestion.query || '';
        const highlightedName = highlightMatch(name, query);

        // Determine icon based on type
        let icon = 'fas fa-search';
        if (suggestion.type === 'product') icon = 'fas fa-box';
        else if (suggestion.type === 'category') icon = 'fas fa-tag';
        else if (suggestion.type === 'recent') icon = 'fas fa-history';

        item.innerHTML = `
            <i class="${icon}"></i>
            <span class="autocomplete-text">${highlightedName}</span>
            ${suggestion.category ? `<span class="autocomplete-category">${escapeHtml(suggestion.category)}</span>` : ''}
        `;

        // Handle click
        item.addEventListener('click', () => {
            if (suggestion.url) {
                window.location.href = suggestion.url;
            } else {
                searchInput.value = name;
                searchInput.closest('form').submit();
            }
        });

        return item;
    }

    /**
     * Highlight matching text
     */
    function highlightMatch(text, query) {
        const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
        return escapeHtml(text).replace(regex, '<strong>$1</strong>');
    }

    /**
     * Show no results message
     */
    function showNoResults(query) {
        autocompleteContainer.innerHTML = `
            <div class="autocomplete-item no-results">
                <i class="fas fa-info-circle"></i>
                <span>No results found for "${escapeHtml(query)}"</span>
            </div>
        `;
        autocompleteContainer.style.display = 'block';
    }

    /**
     * Show loading state
     */
    function showLoading() {
        autocompleteContainer.innerHTML = `
            <div class="autocomplete-item loading">
                <div class="spinner"></div>
                <span>Searching...</span>
            </div>
        `;
        autocompleteContainer.style.display = 'block';
    }

    /**
     * Show recent searches
     */
    function showRecentSearches() {
        const recent = getRecentSearches();
        if (recent.length === 0) return;

        autocompleteContainer.innerHTML = '<div class="autocomplete-header">Recent Searches</div>';

        recent.forEach(search => {
            const item = createSuggestionItem({
                name: search,
                type: 'recent'
            }, '');
            autocompleteContainer.appendChild(item);
        });

        // Add clear button
        const clearBtn = document.createElement('div');
        clearBtn.className = 'autocomplete-item clear-recent';
        clearBtn.innerHTML = '<i class="fas fa-trash"></i><span>Clear history</span>';
        clearBtn.addEventListener('click', () => {
            clearRecentSearches();
            closeAutocomplete();
        });
        autocompleteContainer.appendChild(clearBtn);

        autocompleteContainer.style.display = 'block';
    }

    /**
     * Close autocomplete dropdown
     */
    function closeAutocomplete() {
        if (autocompleteContainer) {
            autocompleteContainer.style.display = 'none';
            autocompleteContainer.innerHTML = '';
        }
        currentFocus = -1;
    }

    /**
     * Recent searches management
     */
    const RECENT_SEARCHES_KEY = 'pawfect-finds-recent-searches';
    const MAX_RECENT = 5;

    function getRecentSearches() {
        try {
            const stored = localStorage.getItem(RECENT_SEARCHES_KEY);
            return stored ? JSON.parse(stored) : [];
        } catch (e) {
            return [];
        }
    }

    function saveRecentSearch(query) {
        if (!query || query.length < MIN_SEARCH_LENGTH) return;

        try {
            let recent = getRecentSearches();
            
            // Remove if already exists
            recent = recent.filter(s => s.toLowerCase() !== query.toLowerCase());
            
            // Add to beginning
            recent.unshift(query);
            
            // Keep only MAX_RECENT
            recent = recent.slice(0, MAX_RECENT);
            
            localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(recent));
        } catch (e) {
            console.error('Error saving recent search:', e);
        }
    }

    function clearRecentSearches() {
        try {
            localStorage.removeItem(RECENT_SEARCHES_KEY);
        } catch (e) {
            console.error('Error clearing recent searches:', e);
        }
    }

    /**
     * Utility functions
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

    function escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    /**
     * Public API
     */
    window.SearchAutocomplete = {
        close: closeAutocomplete,
        clearRecent: clearRecentSearches
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
