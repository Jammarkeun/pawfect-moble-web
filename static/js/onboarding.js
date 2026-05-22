/**
 * PAWFECT FINDS - ONBOARDING TOOLTIPS
 * Interactive tour for first-time users
 */

(function() {
    'use strict';

    const STORAGE_KEY = 'pawfect-finds-onboarding-completed';
    const TOUR_VERSION = '1.0';

    /**
     * Check if user has completed onboarding
     */
    function hasCompletedOnboarding() {
        try {
            const completed = localStorage.getItem(STORAGE_KEY);
            return completed === TOUR_VERSION;
        } catch (e) {
            return false;
        }
    }

    /**
     * Mark onboarding as completed
     */
    function markAsCompleted() {
        try {
            localStorage.setItem(STORAGE_KEY, TOUR_VERSION);
        } catch (e) {
            console.error('Error saving onboarding status:', e);
        }
    }

    /**
     * Tour steps configuration for landing page
     */
    const landingPageSteps = [
        {
            element: '.navbar',
            title: '🐾 Welcome to Pawfect Finds!',
            content: 'Your one-stop shop for all pet supplies. Let me show you around!',
            placement: 'bottom'
        },
        {
            element: '.navbar .nav-link[href*="products"]',
            title: '🛍️ Browse Products',
            content: 'Click here to explore our wide range of pet products for dogs, cats, birds, and more!',
            placement: 'bottom'
        },
        {
            element: '.category-card',
            title: '📦 Shop by Category',
            content: 'Browse products by category to find exactly what your pet needs.',
            placement: 'top'
        },
        {
            element: '.product-card',
            title: '⭐ Featured Products',
            content: 'Check out our featured products, highly rated by pet lovers like you!',
            placement: 'top'
        }
    ];

    /**
     * Create tooltip element
     */
    function createTooltip(step, currentIndex, totalSteps) {
        const tooltip = document.createElement('div');
        tooltip.className = 'onboarding-tooltip';
        tooltip.innerHTML = `
            <div class="onboarding-tooltip-content">
                <button class="onboarding-close" aria-label="Close tour">&times;</button>
                <div class="onboarding-header">
                    <h5 class="onboarding-title">${step.title}</h5>
                    <span class="onboarding-counter">${currentIndex + 1}/${totalSteps}</span>
                </div>
                <p class="onboarding-text">${step.content}</p>
                <div class="onboarding-footer">
                    ${currentIndex > 0 ? '<button class="btn btn-sm btn-outline-secondary onboarding-prev">Previous</button>' : '<button class="btn btn-sm btn-outline-secondary onboarding-skip">Skip Tour</button>'}
                    ${currentIndex < totalSteps - 1 ? '<button class="btn btn-sm btn-primary onboarding-next">Next</button>' : '<button class="btn btn-sm btn-success onboarding-finish">Got it!</button>'}
                </div>
            </div>
            <div class="onboarding-arrow"></div>
        `;
        return tooltip;
    }

    /**
     * Position tooltip relative to target element
     */
    function positionTooltip(tooltip, targetElement, placement) {
        if (!targetElement) return;

        const rect = targetElement.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        const arrow = tooltip.querySelector('.onboarding-arrow');

        let top, left;

        switch (placement) {
            case 'top':
                top = rect.top - tooltipRect.height - 15;
                left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
                arrow.style.top = 'auto';
                arrow.style.bottom = '-8px';
                arrow.style.left = '50%';
                arrow.style.transform = 'translateX(-50%) rotate(180deg)';
                break;

            case 'bottom':
                top = rect.bottom + 15;
                left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
                arrow.style.top = '-8px';
                arrow.style.bottom = 'auto';
                arrow.style.left = '50%';
                arrow.style.transform = 'translateX(-50%)';
                break;

            case 'left':
                top = rect.top + (rect.height / 2) - (tooltipRect.height / 2);
                left = rect.left - tooltipRect.width - 15;
                arrow.style.top = '50%';
                arrow.style.right = '-8px';
                arrow.style.transform = 'translateY(-50%) rotate(90deg)';
                break;

            case 'right':
                top = rect.top + (rect.height / 2) - (tooltipRect.height / 2);
                left = rect.right + 15;
                arrow.style.top = '50%';
                arrow.style.left = '-8px';
                arrow.style.transform = 'translateY(-50%) rotate(-90deg)';
                break;

            default:
                top = rect.bottom + 15;
                left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
        }

        // Keep tooltip within viewport
        const padding = 10;
        if (left < padding) left = padding;
        if (left + tooltipRect.width > window.innerWidth - padding) {
            left = window.innerWidth - tooltipRect.width - padding;
        }
        if (top < padding) top = padding;

        tooltip.style.top = `${top + window.scrollY}px`;
        tooltip.style.left = `${left}px`;
    }

    /**
     * Highlight target element
     */
    function highlightElement(element) {
        if (!element) return;

        // Remove previous highlights
        document.querySelectorAll('.onboarding-highlight').forEach(el => {
            el.classList.remove('onboarding-highlight');
        });

        element.classList.add('onboarding-highlight');
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    /**
     * Tour controller
     */
    class Tour {
        constructor(steps) {
            this.steps = steps;
            this.currentStep = 0;
            this.tooltip = null;
            this.overlay = null;
        }

        start() {
            // Create overlay
            this.overlay = document.createElement('div');
            this.overlay.className = 'onboarding-overlay';
            document.body.appendChild(this.overlay);

            // Add body class
            document.body.classList.add('onboarding-active');

            this.showStep(0);
        }

        showStep(index) {
            if (index < 0 || index >= this.steps.length) return;

            this.currentStep = index;
            const step = this.steps[index];

            // Remove previous tooltip
            if (this.tooltip) {
                this.tooltip.remove();
            }

            // Find target element
            const targetElement = document.querySelector(step.element);
            if (!targetElement) {
                // Skip to next step if element not found
                if (index < this.steps.length - 1) {
                    this.showStep(index + 1);
                } else {
                    this.end();
                }
                return;
            }

            // Highlight element
            highlightElement(targetElement);

            // Create and position tooltip
            this.tooltip = createTooltip(step, index, this.steps.length);
            document.body.appendChild(this.tooltip);

            // Position after render
            setTimeout(() => {
                positionTooltip(this.tooltip, targetElement, step.placement);
                this.tooltip.classList.add('show');
            }, 10);

            // Attach event listeners
            this.attachEventListeners();

            // Reposition on window resize
            this.resizeHandler = () => positionTooltip(this.tooltip, targetElement, step.placement);
            window.addEventListener('resize', this.resizeHandler);
        }

        attachEventListeners() {
            if (!this.tooltip) return;

            const nextBtn = this.tooltip.querySelector('.onboarding-next');
            const prevBtn = this.tooltip.querySelector('.onboarding-prev');
            const skipBtn = this.tooltip.querySelector('.onboarding-skip');
            const finishBtn = this.tooltip.querySelector('.onboarding-finish');
            const closeBtn = this.tooltip.querySelector('.onboarding-close');

            if (nextBtn) nextBtn.addEventListener('click', () => this.next());
            if (prevBtn) prevBtn.addEventListener('click', () => this.prev());
            if (skipBtn) skipBtn.addEventListener('click', () => this.end());
            if (finishBtn) finishBtn.addEventListener('click', () => this.end());
            if (closeBtn) closeBtn.addEventListener('click', () => this.end());
        }

        next() {
            if (this.currentStep < this.steps.length - 1) {
                this.showStep(this.currentStep + 1);
            } else {
                this.end();
            }
        }

        prev() {
            if (this.currentStep > 0) {
                this.showStep(this.currentStep - 1);
            }
        }

        end() {
            // Remove elements
            if (this.tooltip) this.tooltip.remove();
            if (this.overlay) this.overlay.remove();

            // Remove highlights
            document.querySelectorAll('.onboarding-highlight').forEach(el => {
                el.classList.remove('onboarding-highlight');
            });

            // Remove body class
            document.body.classList.remove('onboarding-active');

            // Remove resize listener
            if (this.resizeHandler) {
                window.removeEventListener('resize', this.resizeHandler);
            }

            // Mark as completed
            markAsCompleted();

            // Dispatch event
            window.dispatchEvent(new CustomEvent('onboardingCompleted'));
        }
    }

    /**
     * Start tour for landing page
     */
    function startLandingPageTour() {
        const tour = new Tour(landingPageSteps);
        tour.start();
    }

    /**
     * Initialize onboarding
     */
    function init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', checkAndStart);
        } else {
            checkAndStart();
        }
    }

    function checkAndStart() {
        // Only run on landing page for first-time users
        const isLandingPage = window.location.pathname === '/' || window.location.pathname.includes('/landing');
        
        if (isLandingPage && !hasCompletedOnboarding()) {
            // Delay to ensure page is fully loaded
            setTimeout(startLandingPageTour, 1000);
        }
    }

    /**
     * Public API
     */
    window.Onboarding = {
        start: startLandingPageTour,
        reset: () => {
            localStorage.removeItem(STORAGE_KEY);
        }
    };

    // Initialize
    init();
})();
