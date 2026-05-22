// Global Bootstrap toast helper for showing success/error/info messages
// Exposes: window.showToast({ message, category, delay }) and auto-renders Flask flashes
(function(){
  try {
    var container = document.getElementById('toastContainer');
    if (!container) {
      // Create container if missing
      var wrapper = document.createElement('div');
      wrapper.className = 'position-fixed top-50 start-50 translate-middle p-3';
      wrapper.style.zIndex = 1080;
      wrapper.style.width = 'min(90vw, 480px)';
      container = document.createElement('div');
      container.id = 'toastContainer';
      container.className = 'toast-container w-100';
      wrapper.appendChild(container);
      document.body.appendChild(wrapper);
    }

    function bootstrapToast(el, opts){
      // Use Bootstrap 5 toast API if present
      if (window.bootstrap && bootstrap.Toast) return new bootstrap.Toast(el, opts || {});
      // Fallback: mimic minimal auto-hide behavior
      return {
        show: function(){
          el.classList.add('show');
          if (!opts || opts.autohide !== false) {
            setTimeout(function(){ el.remove(); }, (opts && opts.delay) || 3000);
          }
        }
      };
    }

    function classFor(category){
      switch((category||'').toLowerCase()){
        case 'success': return 'text-bg-success';
        case 'danger':
        case 'error': return 'text-bg-danger';
        case 'warning': return 'text-bg-warning';
        case 'info': return 'text-bg-info';
        default: return 'text-bg-secondary';
      }
    }

    function makeCard(opts){
      var category = (opts.category || 'info').toLowerCase();
      var title = opts.title || (category === 'success' ? 'Success!' : category === 'danger' || category === 'error' ? 'Oops!' : category === 'warning' ? 'Heads up' : 'Notice');
      var el = document.createElement('div');
      el.className = 'pf-toast-modal pf-toast-' + (category === 'error' ? 'danger' : category);
      el.setAttribute('role','status');
      el.setAttribute('aria-live','polite');
      el.innerHTML = ''+
        '<div class="pf-toast-icon"><i class="fas '+ (category==='success' ? 'fa-check' : category==='warning' ? 'fa-exclamation' : category==='danger'||category==='error' ? 'fa-times' : 'fa-info') +'"></i></div>'+
        '<div class="pf-toast-title">'+ title +'</div>'+
        '<div class="pf-toast-msg">'+ (opts.message || '') +'</div>'+
        '<div class="pf-toast-action">'+ (opts.actionText ? '<button type="button" class="btn btn-primary">'+ opts.actionText +'</button>' : '') +'</div>';
      // Action handler
      if (opts.actionText && (opts.onAction || opts.actionHref)){
        var btn = el.querySelector('.pf-toast-action .btn');
        if (btn){
          btn.addEventListener('click', function(){
            try {
              if (opts.onAction) opts.onAction();
              if (opts.actionHref) window.location.href = opts.actionHref;
            } catch(e) {}
          });
          el.querySelector('.pf-toast-action').style.display = 'block';
        }
      }
      return el;
    }

    function ensureOverlay(show){
      var overlay = document.getElementById('toastOverlay');
      if (!overlay){
        overlay = document.createElement('div');
        overlay.id = 'toastOverlay';
        overlay.className = 'pf-toast-overlay';
        overlay.style.display = 'none';
        document.body.appendChild(overlay);
      }
      overlay.style.display = show ? 'block' : 'none';
    }

    window.showToast = function(opts){
      opts = opts || {};
      // Show one card at a time (modal feel)
      container.innerHTML = '';
      var card = makeCard(opts);
      container.appendChild(card);
      ensureOverlay(true);
      // Auto remove without requiring an X button
      var delay = opts.delay || 1500;
      setTimeout(function(){
        try {
          card.style.animation = 'pf-toast-out 120ms ease-in forwards';
          setTimeout(function(){
            card.remove();
            if (!container.firstChild) ensureOverlay(false);
          }, 130);
        } catch(e) {
          card.remove();
          ensureOverlay(false);
        }
      }, delay);
    };

    // Render any server-flashed messages injected on page load
    if (Array.isArray(window.FLASH_MESSAGES)){
      // Only show the first on load to avoid stacking
      var first = window.FLASH_MESSAGES[0];
      if (first){
        try { window.showToast({ message: first.message, category: first.category, delay: 2200 }); } catch(e) {}
      }
      window.FLASH_MESSAGES = [];
    }
  } catch(e) { /* no-op */ }
})();
