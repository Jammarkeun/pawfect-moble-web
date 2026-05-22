/**
 * Rider Location Tracking System
 * Handles GPS permission, location updates, and background tracking
 */

class RiderLocationTracker {
    constructor() {
        this.riderId = document.querySelector('[data-rider-id]')?.dataset.riderId;
        this.locationPermissionModal = null;
        this.watchId = null;
        this.updateInterval = null;
        this.isTrackingEnabled = false;
        this.lastUpdate = null;
        this.hasPermission = false;
        
        this.init();
    }

    /**
     * Initialize the location tracker
     */
    init() {
        this.locationPermissionModal = new (window.bootstrap?.Modal || function() {})('#locationPermissionModal');
        this.setupEventListeners();
        this.checkLocationPermission();
    }

    /**
     * Setup button event listeners
     */
    setupEventListeners() {
        const allowBtn = document.getElementById('allowLocationBtn');
        const skipBtn = document.getElementById('skipLocationBtn');

        if (allowBtn) {
            allowBtn.addEventListener('click', () => this.requestLocationPermission());
        }
        if (skipBtn) {
            skipBtn.addEventListener('click', () => this.dismissModal());
        }
    }

    /**
     * Check if location permission was previously granted
     */
    checkLocationPermission() {
        // Check if browser supports Geolocation API
        if (!navigator.geolocation) {
            console.error('Geolocation not supported');
            return;
        }

        // Check if location permission was already granted
        if (localStorage.getItem('locationPermissionGranted') === 'true') {
            console.log('Location permission already granted');
            this.startTracking();
        } else if (localStorage.getItem('locationPermissionDenied') !== 'true') {
            // Show modal only if permission hasn't been explicitly denied
            this.showModal();
        }
    }

    /**
     * Show location permission modal
     */
    showModal() {
        try {
            const modal = new (window.bootstrap?.Modal)(document.getElementById('locationPermissionModal'));
            modal.show();
        } catch (e) {
            console.error('Could not show modal:', e);
        }
    }

    /**
     * Dismiss the modal
     */
    dismissModal() {
        try {
            const modal = window.bootstrap?.Modal.getInstance(document.getElementById('locationPermissionModal'));
            if (modal) modal.hide();
        } catch (e) {
            console.error('Could not hide modal:', e);
        }
        localStorage.setItem('locationPermissionDenied', 'true');
    }

    /**
     * Request location permission from user
     */
    requestLocationPermission() {
        const allowBtn = document.getElementById('allowLocationBtn');
        const originalText = allowBtn.innerHTML;
        
        // Show loading state
        allowBtn.disabled = true;
        allowBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Requesting...';

        navigator.geolocation.getCurrentPosition(
            (position) => {
                console.log('Location permission granted!', position.coords);
                localStorage.setItem('locationPermissionGranted', 'true');
                localStorage.setItem('locationPermissionDenied', 'false');
                this.hasPermission = true;
                this.dismissModal();
                this.startTracking();
            },
            (error) => {
                console.error('Location permission denied:', error);
                localStorage.setItem('locationPermissionDenied', 'true');
                
                let message = 'Unable to access location. ';
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        message += 'Please enable location access in your browser settings.';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        message += 'Location information is unavailable.';
                        break;
                    case error.TIMEOUT:
                        message += 'Location request timed out.';
                        break;
                }
                
                alert(message);
                this.dismissModal();
                
                // Reset button
                allowBtn.disabled = false;
                allowBtn.innerHTML = originalText;
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    }

    /**
     * Start continuous location tracking
     */
    startTracking() {
        if (this.isTrackingEnabled) return;
        
        console.log('Starting location tracking for rider:', this.riderId);
        this.isTrackingEnabled = true;

        // Watch position with continuous updates
        if (navigator.geolocation) {
            this.watchId = navigator.geolocation.watchPosition(
                (position) => this.onLocationUpdate(position),
                (error) => this.onLocationError(error),
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }
            );

            // Also update on a set interval to ensure consistency
            this.updateInterval = setInterval(() => {
                this.sendLocationToServer();
            }, 15000); // Update every 15 seconds

            // Send initial location immediately
            this.sendLocationToServer();
        }
    }

    /**
     * Handle location update from GPS
     */
    onLocationUpdate(position) {
        const { latitude, longitude, accuracy } = position.coords;
        
        console.log('Location updated:', {
            latitude,
            longitude,
            accuracy: Math.round(accuracy) + ' meters',
            timestamp: new Date().toLocaleTimeString()
        });

        // Update last known location
        this.lastUpdate = {
            latitude,
            longitude,
            accuracy,
            timestamp: new Date()
        };

        // Send to server
        this.sendLocationToServer(latitude, longitude, accuracy);
    }

    /**
     * Handle location error
     */
    onLocationError(error) {
        console.error('Location tracking error:', error);
        
        let message = 'Location tracking error: ';
        switch(error.code) {
            case error.PERMISSION_DENIED:
                message += 'Location permission was denied.';
                break;
            case error.POSITION_UNAVAILABLE:
                message += 'Unable to retrieve your position.';
                break;
            case error.TIMEOUT:
                message += 'Location request timed out.';
                break;
        }
        console.warn(message);
    }

    /**
     * Send location to server
     */
    async sendLocationToServer(latitude = null, longitude = null, accuracy = null) {
        if (!this.riderId) return;

        // Use last known location if current coords not provided
        if (!latitude && this.lastUpdate) {
            latitude = this.lastUpdate.latitude;
            longitude = this.lastUpdate.longitude;
            accuracy = this.lastUpdate.accuracy;
        }

        if (!latitude || !longitude) {
            console.warn('No location data to send');
            return;
        }

        try {
            const response = await fetch('/rider/api/update-location', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    latitude: parseFloat(latitude),
                    longitude: parseFloat(longitude),
                    accuracy: accuracy ? Math.round(accuracy) : null
                })
            });

            const data = await response.json();
            if (data.success) {
                console.log('Location sent to server');
                // Update UI indicator if needed
                this.updateLocationIndicator('online');
            } else {
                console.warn('Failed to send location:', data.message);
                this.updateLocationIndicator('error');
            }
        } catch (error) {
            console.error('Error sending location to server:', error);
            this.updateLocationIndicator('error');
        }
    }

    /**
     * Update location indicator UI
     */
    updateLocationIndicator(status) {
        const connectionStatus = document.getElementById('connection-status');
        if (!connectionStatus) return;

        let badge = 'bg-secondary';
        let text = 'Connecting...';

        switch(status) {
            case 'online':
                badge = 'bg-success';
                text = '📍 Location Tracking Active';
                break;
            case 'offline':
                badge = 'bg-warning';
                text = '📍 Location Tracking Inactive';
                break;
            case 'error':
                badge = 'bg-danger';
                text = '⚠️ Location Error';
                break;
        }

        connectionStatus.className = `badge ${badge}`;
        connectionStatus.textContent = text;
    }

    /**
     * Stop location tracking
     */
    stopTracking() {
        if (this.watchId) {
            navigator.geolocation.clearWatch(this.watchId);
        }
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        this.isTrackingEnabled = false;
        console.log('Location tracking stopped');
    }

    /**
     * Cleanup on page unload
     */
    destroy() {
        this.stopTracking();
    }
}

// Initialize on document ready
document.addEventListener('DOMContentLoaded', function() {
    window.riderLocationTracker = new RiderLocationTracker();
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.riderLocationTracker) {
        window.riderLocationTracker.destroy();
    }
});
