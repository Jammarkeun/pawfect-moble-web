// Enhanced notifications UI/UX
// - Renders beautiful list with icons, relative time, unread state
// - Works for all roles (user/seller/rider/admin) via the same endpoints
// - Requires elements: #notification-count, #notification-list, #mark-all-notifs

(function(){
  try {
    var socket = null;
    if (window.pawfectChat && typeof window.pawfectChat.connect === 'function') {
      socket = window.pawfectChat.connect();
    }
    socket = socket || window.socket || (window.io ? window.io() : null);
    var role = (window.CURRENT_USER && window.CURRENT_USER.role) || 'user';

    // Utilities
    function $(id){ return document.getElementById(id); }
    function setBadge(n){
      var badge = $('notification-count');
      if (!badge) return;
      n = parseInt(n || 0, 10) || 0;
      badge.textContent = String(n);
      badge.style.display = n > 0 ? 'inline-block' : 'none';
    }
    function incBadge(){
      var badge = $('notification-count');
      if (!badge) return;
      var n = parseInt(badge.textContent || '0', 10) || 0;
      setBadge(n + 1);
    }
    function timeAgo(ts){
      try {
        var d = ts ? new Date(ts) : new Date();
        var s = Math.floor((Date.now() - d.getTime())/1000);
        if (s < 60) return 'just now';
        var m = Math.floor(s/60); if (m < 60) return m + 'm ago';
        var h = Math.floor(m/60); if (h < 24) return h + 'h ago';
        var d2 = Math.floor(h/24); if (d2 < 7) return d2 + 'd ago';
        return d.toLocaleString();
      } catch(e){ return new Date().toLocaleString(); }
    }
    function iconFor(type){
      var map = {
        order_status: {icon:'fa-box', bg:'bg-primary'},
        order_status_update: {icon:'fa-box', bg:'bg-primary'},
        seller_application: {icon:'fa-handshake', bg:'bg-success'},
        message: {icon:'fa-envelope', bg:'bg-info'},
        default: {icon:'fa-bell', bg:'bg-secondary'}
      };
      return map[type] || map.default;
    }

    function emptyState(show){
      var list = $('notification-list');
      if (!list) return;
      var empty = document.querySelector('#notification-empty');
      if (!empty){
        empty = document.createElement('li');
        empty.id = 'notification-empty';
        empty.className = 'notif-empty';
        empty.innerHTML = '<i class="fas fa-bell-slash"></i><p>No notifications yet</p>';
        empty.style.animation = 'fadeIn 0.3s ease-out';
        list.appendChild(empty);
      }
      empty.style.display = show ? 'block' : 'none';
    }

    function renderItem(n, options){
      options = options || {};
      var li = document.createElement('li');
      li.className = 'notif-item' + (n.is_read ? '' : ' unread');
      li.setAttribute('data-id', n.id || '');

      var meta = iconFor(n.type);
      var created = n.created_at || new Date().toISOString();
      var title = n.title || 'Notification';
      var message = n.message || '';

      li.innerHTML =
        '<div class="notif-icon ' + meta.bg + '"><i class="fas ' + meta.icon + '"></i></div>' +
        '<div class="notif-body">' +
          '<div class="notif-title">' + title + '</div>' +
          '<div class="notif-message">' + message + '</div>' +
          '<div class="notif-time" title="' + (new Date(created)).toLocaleString() + '"><i class="far fa-clock"></i>' + timeAgo(created) + '</div>' +
        '</div>' +
        '<button class="btn btn-sm btn-link notif-mark" title="Mark as read"><i class="fas fa-check"></i></button>';

      return li;
    }

    function prependItem(n){
      var list = $('notification-list');
      if (!list) return;
      var empty = $('notification-empty'); 
      if (empty) empty.remove();
      var item = renderItem(n);
      item.style.animation = 'slideInLeft 0.3s ease-out';
      list.prepend(item);
      incBadge();
    }

    // Socket subscriptions (if available)
    if (socket){
      try {
        socket.on('notification', function(data){
          try { incBadge(); prependItem(data || {}); } catch(e) {}
        });

        // Optional: react to order status updates
        socket.on('order_status_updated', function(data){
          try {
            incBadge();
            prependItem({
              type: 'order_status_update',
              title: 'Order status updated',
              message: 'Order #' + (data.order_id || '') + ' is now ' + (data.status_display || data.status || ''),
              created_at: data.updated_at || new Date().toISOString(),
              is_read: 0
            });
          } catch(e) {}
        });
      } catch(e) {}
    }

    // Delegated click handlers (mark single as read)
    var listEl = $('notification-list');
    if (listEl){
      listEl.addEventListener('click', function(ev){
        var btn = ev.target.closest('.notif-mark');
        var item = ev.target.closest('.notif-item');
        if (!item) return;
        var id = item.getAttribute('data-id');
        if (!id) return;
        ev.preventDefault();
        var csrfToken = document.querySelector('meta[name="csrf-token"]');
        var headers = { 'Content-Type': 'application/json' };
        if (csrfToken) headers['X-CSRFToken'] = csrfToken.getAttribute('content');
        fetch('/user/notifications/mark-read', {
          method: 'POST',
          headers: headers,
          body: JSON.stringify({ id: id })
        }).then(function(r){ return r.json(); }).then(function(){
          item.classList.remove('unread');
          // decrement badge
          var badge = $('notification-count');
          var n = parseInt((badge && badge.textContent) || '0', 10) || 0;
          setBadge(Math.max(0, n - 1));
        }).catch(function(){});
      });
    }

    // Mark all as read
    var markAll = $('mark-all-notifs');
    if (markAll){
      markAll.addEventListener('click', function(ev){
        ev.preventDefault();
        var csrfToken = document.querySelector('meta[name="csrf-token"]');
        var headers = {};
        if (csrfToken) headers['X-CSRFToken'] = csrfToken.getAttribute('content');
        fetch('/user/notifications/mark-all-read', { method: 'POST', headers: headers })
          .then(function(r){ return r.json(); })
          .then(function(){
            setBadge(0);
            document.querySelectorAll('.notif-item').forEach(function(el){ el.classList.remove('unread'); });
          }).catch(function(){});
      });
    }

    // Initial unread count
    fetch('/user/notifications/unread-count')
      .then(function(r){ return r.json(); })
      .then(function(j){ 
        if (j && j.success) setBadge(j.count || 0); 
      })
      .catch(function(e){ console.log('Error fetching unread count:', e); });

    // Populate list
    function loadNotifications(){
      var list = $('notification-list');
      if (!list) return;
      
      fetch('/user/notifications?limit=10')
        .then(function(r){ return r.json(); })
        .then(function(j){
          var items = (j && j.success && j.notifications) ? j.notifications : [];
          if (!list) return;
          list.innerHTML = '';
          if (!items || items.length === 0){ 
            emptyState(true); 
            return; 
          }
          items.forEach(function(n){ 
            var item = renderItem(n);
            list.appendChild(item);
          });
          emptyState(false);
        })
        .catch(function(e){ 
          console.log('Error fetching notifications:', e);
          emptyState(true); 
        });
    }
    
    // Load notifications on page load
    loadNotifications();
    
    // Reload notifications when dropdown is opened
    var notifDropdown = document.getElementById('notifDropdown');
    if (notifDropdown) {
      notifDropdown.addEventListener('click', function(){
        setTimeout(loadNotifications, 100);
      });
    }

  } catch(e) {}
})();
