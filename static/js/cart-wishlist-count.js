// Real-time Cart & Wishlist Count Updater
// Updates badge counts for cart and wishlist items
(function(){
  try {
    var socket = window.socket || (window.io ? window.io() : null);
    
    // Utility functions
    function $(id) { return document.getElementById(id); }
    
    function setBadge(elementId, count) {
      var badge = $(elementId);
      if (!badge) return;
      count = parseInt(count || 0, 10) || 0;
      badge.textContent = String(count);
      badge.style.display = count > 0 ? 'inline-block' : 'none';
    }
    
    function updateCartCount() {
      fetch('/cart/count')
        .then(function(r) { return r.json(); })
        .then(function(data) {
          if (data && data.success) {
            setBadge('cart-count', data.count || 0);
          }
        })
        .catch(function() {});
    }
    
    function updateWishlistCount() {
      fetch('/wishlist/count')
        .then(function(r) { return r.json(); })
        .then(function(data) {
          if (data && data.success) {
            setBadge('wishlist-count', data.count || 0);
          }
        })
        .catch(function() {});
    }
    
    // Initial load
    updateCartCount();
    updateWishlistCount();
    
    // Socket.IO real-time updates (if available)
    if (socket && window.CURRENT_USER && window.CURRENT_USER.id) {
      // Listen for cart updates
      socket.on('cart_updated', function(data) {
        try {
          if (data && data.user_id === window.CURRENT_USER.id) {
            setBadge('cart-count', data.count || 0);
          }
        } catch(e) {}
      });
      
      // Listen for wishlist updates
      socket.on('wishlist_updated', function(data) {
        try {
          if (data && data.user_id === window.CURRENT_USER.id) {
            setBadge('wishlist-count', data.count || 0);
          }
        } catch(e) {}
      });
    }
    
    // Fallback: Poll every 30 seconds for count updates
    setInterval(function() {
      updateCartCount();
      updateWishlistCount();
    }, 30000);
    
  } catch(e) {}
})();
