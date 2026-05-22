/**
 * Real-time Analytics Updates
 * Fetches analytics data from API and updates dashboard in real-time
 */

class RealtimeAnalytics {
    constructor(apiEndpoint, updateInterval = 30000) {
        this.apiEndpoint = apiEndpoint;
        this.updateInterval = updateInterval;
        this.intervalId = null;
        this.lastUpdate = null;
        
        // Start polling on initialization
        this.start();
    }
    
    /**
     * Start polling for real-time updates
     */
    start() {
        // Initial update
        this.updateAnalytics();
        
        // Set up interval
        this.intervalId = setInterval(() => {
            this.updateAnalytics();
        }, this.updateInterval);
        
        console.log(`Analytics realtime started - polling every ${this.updateInterval}ms`);
    }
    
    /**
     * Stop polling
     */
    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
            console.log('Analytics realtime stopped');
        }
    }
    
    /**
     * Fetch analytics data from API
     */
    async updateAnalytics() {
        try {
            const response = await fetch(this.apiEndpoint, {
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.lastUpdate = new Date();
                this.updateUI(data);
            }
        } catch (error) {
            console.error('Error fetching analytics:', error);
        }
    }
    
    /**
     * Update UI elements with new data
     * This method should be overridden in subclasses
     */
    updateUI(data) {
        console.log('Base updateUI - override in subclass', data);
    }
    
    /**
     * Format currency
     */
    formatCurrency(value) {
        return new Intl.NumberFormat('en-PH', {
            style: 'currency',
            currency: 'PHP'
        }).format(value);
    }
    
    /**
     * Update element text if element exists
     */
    updateElement(selector, value) {
        const element = document.querySelector(selector);
        if (element) {
            element.textContent = value;
        }
    }
}

/**
 * Seller Dashboard Analytics
 */
class SellerAnalytics extends RealtimeAnalytics {
    updateUI(data) {
        if (!data) return;
        
        // Update revenue metrics
        if (data.total_revenue !== undefined) {
            this.updateElement('#total-revenue', this.formatCurrency(data.total_revenue));
        }
        if (data.today_revenue !== undefined) {
            this.updateElement('#today-revenue', this.formatCurrency(data.today_revenue));
        }
        if (data.month_revenue !== undefined) {
            this.updateElement('#month-revenue', this.formatCurrency(data.month_revenue));
        }
        
        // Update order metrics
        if (data.orders) {
            this.updateElement('#total-orders', data.orders.total || 0);
            this.updateElement('#pending-orders', data.orders.pending || 0);
            this.updateElement('#confirmed-orders', data.orders.confirmed || 0);
            this.updateElement('#delivered-orders', data.orders.delivered || 0);
            this.updateElement('#cancelled-orders', data.orders.cancelled || 0);
        }
        
        // Update product metrics
        if (data.products) {
            this.updateElement('#total-products', data.products.total || 0);
            this.updateElement('#active-products', data.products.active || 0);
            this.updateElement('#low-stock-items', data.products.low_stock || 0);
        }
        
        // Update financial overview
        if (data.financial) {
            this.updateElement('#gross-revenue', this.formatCurrency(data.financial.gross_revenue));
            this.updateElement('#commission-due', this.formatCurrency(data.financial.commission_due));
            this.updateElement('#net-revenue', this.formatCurrency(data.financial.net_revenue));
            this.updateElement('#commission-rate', `${data.financial.commission_rate.toFixed(1)}%`);
        }
    }
}

/**
 * Rider Dashboard Analytics
 */
class RiderAnalytics extends RealtimeAnalytics {
    updateUI(data) {
        if (!data) return;
        
        // Update earnings
        if (data.earnings) {
            this.updateElement('#total-earnings', this.formatCurrency(data.earnings.total));
            this.updateElement('#today-earnings', this.formatCurrency(data.earnings.today));
            this.updateElement('#month-earnings', this.formatCurrency(data.earnings.this_month));
        }
        
        // Update delivery metrics
        if (data.deliveries) {
            this.updateElement('#total-deliveries', data.deliveries.total || 0);
            this.updateElement('#assigned-deliveries', data.deliveries.assigned || 0);
            this.updateElement('#picked-up-deliveries', data.deliveries.picked_up || 0);
            this.updateElement('#on-the-way-deliveries', data.deliveries.on_the_way || 0);
            this.updateElement('#delivered-deliveries', data.deliveries.delivered || 0);
            this.updateElement('#failed-deliveries', data.deliveries.failed || 0);
            this.updateElement('#pending-deliveries', data.deliveries.pending || 0);
            this.updateElement('#completed-deliveries', data.deliveries.completed || 0);
        }
        
        // Update today's stats
        if (data.today) {
            this.updateElement('#today-deliveries', data.today.deliveries || 0);
            this.updateElement('#today-completed', data.today.completed || 0);
        }
        
        // Update rating
        if (data.rating) {
            const ratingElement = document.querySelector('#avg-rating');
            if (ratingElement) {
                ratingElement.textContent = data.rating.average.toFixed(1);
            }
            this.updateElement('#total-ratings', data.rating.total_ratings || 0);
        }
    }
}

/**
 * Admin Dashboard Analytics
 */
class AdminAnalytics extends RealtimeAnalytics {
    updateUI(data) {
        if (!data) return;
        
        // Update revenue metrics
        if (data.revenue) {
            this.updateElement('#total-revenue', this.formatCurrency(data.revenue.total));
            this.updateElement('#today-revenue', this.formatCurrency(data.revenue.today));
            this.updateElement('#month-revenue', this.formatCurrency(data.revenue.this_month));
            this.updateElement('#platform-commission', this.formatCurrency(data.revenue.commission));
        }
        
        // Update order metrics
        if (data.orders) {
            this.updateElement('#total-orders', data.orders.total || 0);
            this.updateElement('#pending-orders', data.orders.pending || 0);
            this.updateElement('#confirmed-orders', data.orders.confirmed || 0);
            this.updateElement('#delivered-orders', data.orders.delivered || 0);
            this.updateElement('#cancelled-orders', data.orders.cancelled || 0);
        }
        
        // Update user metrics
        if (data.users) {
            this.updateElement('#total-users', data.users.total || 0);
            this.updateElement('#total-customers', data.users.customers || 0);
            this.updateElement('#total-sellers', data.users.sellers || 0);
            this.updateElement('#total-riders', data.users.riders || 0);
        }
        
        // Update delivery metrics
        if (data.deliveries) {
            this.updateElement('#total-deliveries', data.deliveries.total || 0);
            this.updateElement('#completed-deliveries', data.deliveries.completed || 0);
            this.updateElement('#failed-deliveries', data.deliveries.failed || 0);
            this.updateElement('#pending-deliveries', data.deliveries.pending || 0);
        }
        
        // Update product metrics
        if (data.products) {
            this.updateElement('#total-products', data.products.total || 0);
            this.updateElement('#active-products', data.products.active || 0);
            this.updateElement('#out-of-stock-products', data.products.out_of_stock || 0);
        }
    }
}

/**
 * Initialize analytics based on page context
 */
document.addEventListener('DOMContentLoaded', function() {
    // Detect which dashboard we're on
    const isSellerDashboard = document.body.classList.contains('seller-dashboard') || 
                             window.location.pathname.includes('/seller/dashboard');
    const isRiderDashboard = document.body.classList.contains('rider-dashboard') || 
                            window.location.pathname.includes('/rider/dashboard');
    const isAdminDashboard = document.body.classList.contains('admin-dashboard') || 
                            window.location.pathname.includes('/admin/dashboard');
    
    let analytics = null;
    
    if (isSellerDashboard) {
        analytics = new SellerAnalytics('/seller/api/analytics/realtime', 30000);
        console.log('Seller Analytics initialized');
    } else if (isRiderDashboard) {
        analytics = new RiderAnalytics('/rider/api/analytics/realtime', 30000);
        console.log('Rider Analytics initialized');
    } else if (isAdminDashboard) {
        analytics = new AdminAnalytics('/admin/api/analytics/realtime', 30000);
        console.log('Admin Analytics initialized');
    }
    
    // Store in window for access if needed
    if (analytics) {
        window.realtimeAnalytics = analytics;
    }
});

// Stop analytics when page is unloaded
window.addEventListener('beforeunload', function() {
    if (window.realtimeAnalytics) {
        window.realtimeAnalytics.stop();
    }
});
