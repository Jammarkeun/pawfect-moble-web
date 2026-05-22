from flask import Flask, request, jsonify, session, current_app, redirect, url_for
from flask_session import Session
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import logging
from datetime import timedelta
from dotenv import load_dotenv
from app.services.database import Database

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Initialize extensions
sess = Session()
csrf = CSRFProtect()

# Initialize SocketIO with CORS enabled and other configurations
socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode='eventlet',
    logger=False,
    engineio_logger=False,
    ping_timeout=60,
    ping_interval=25
)

# Import WebSocket services
from app.services.chat_websocket import init_chat_websocket

def create_app(config_name='default'):
    """Create and configure the Flask application."""
    # Get the root directory (parent of app package)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(root_dir, 'templates')
    static_dir = os.path.join(root_dir, 'static')
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    
    # Load environment variables from .env file in the root directory
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        logger.info(f"Loaded .env file from: {env_path}")
    else:
        logger.warning(f".env file not found at {env_path}")
    
    # Debug: Log important environment variables
    logger.info("=== Application Configuration ===")
    for key in [
        'FLASK_ENV', 'DEBUG', 'DATABASE_URL', 'MAIL_SERVER', 'MAIL_PORT', 
        'MAIL_USE_TLS', 'MAIL_USERNAME', 'REDIS_URL'
    ]:
        logger.info(f"{key}: {os.getenv(key, '[NOT SET]')}")
    logger.info("================================")
    
    # Basic configuration
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
        SESSION_TYPE='filesystem',
        UPLOAD_FOLDER='static/uploads',
        SESSION_COOKIE_SECURE=os.getenv('FLASK_ENV') == 'production',
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        JSON_SORT_KEYS=False,
        JSON_AS_ASCII=False,
        TEMPLATES_AUTO_RELOAD=True,
        SEND_FILE_MAX_AGE_DEFAULT=timedelta(days=30)
    )
    
    # Database configuration - Supabase
    app.config.update(
        SUPABASE_URL=os.getenv('SUPABASE_URL', ''),
        SUPABASE_KEY=os.getenv('SUPABASE_KEY', ''),
        SUPABASE_SERVICE_KEY=os.getenv('SUPABASE_SERVICE_KEY', ''),
        # Redis for message queue if available
        REDIS_URL=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    )
    
    # Configure session to use Redis if available
    if 'redis' in os.getenv('CACHE_TYPE', '').lower():
        app.config.update(
            SESSION_TYPE='redis',
            SESSION_REDIS=redis.from_url(app.config['REDIS_URL'])
        )
    
    # Email configuration - load directly from environment
    email_from = os.getenv('EMAIL_FROM')
    sender_name = 'Pawfect Finds'
    
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', '1']
    app.config['MAIL_USERNAME'] = email_from
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    
    # Set the default sender with both name and email
    app.config['MAIL_DEFAULT_SENDER'] = (sender_name, email_from)
    app.config['MAIL_SENDER_NAME'] = sender_name
    
    # Debug email config
    print("\n=== Email Configuration ===")
    print(f"MAIL_SERVER: {app.config['MAIL_SERVER']}")
    print(f"MAIL_PORT: {app.config['MAIL_PORT']}")
    print(f"MAIL_USE_TLS: {app.config['MAIL_USE_TLS']}")
    print(f"MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
    print(f"MAIL_DEFAULT_SENDER: {app.config['MAIL_DEFAULT_SENDER']}")
    print("MAIL_PASSWORD:", "[SET]" if app.config['MAIL_PASSWORD'] else "[NOT SET]")
    print("=========================\n")
    
    # Initialize extensions with app
    sess.init_app(app)
    csrf.init_app(app)
    
    # Initialize WebSocket with the app
    socketio.init_app(
        app,
        message_queue=app.config.get('REDIS_URL') if 'redis' in os.getenv('CACHE_TYPE', '').lower() else None,
        cors_allowed_origins="*"
    )
    app.socketio = socketio
    
    # Initialize chat WebSocket handlers
    init_chat_websocket(socketio)
    
    # Ensure NO_PROXY is set to avoid proxy issues with Supabase
    os.environ.setdefault('NO_PROXY', 'supabase.co')
    
    # Initialize Supabase database service
    db_service = Database()
    db_service.init_app(app)
    
    # Set currency helpers
    def _currency_php(value):
        try:
            return f"₱{float(value):.2f}"
        except Exception:
            return f"₱{value}"
    def _image_url_filter(image_url):
        if not image_url:
            return ''
        if image_url.startswith(('http://', 'https://', '/static/')):
            return image_url
        if image_url.startswith('uploads/'):
            return f'/static/{image_url}'
        return image_url
    def _php_filter(value):
        try:
            formatted = f"{float(value or 0):,.2f}"
            from markupsafe import Markup
            return Markup(f"&#8369;{formatted}")
        except Exception:
            from markupsafe import Markup
            return Markup("&#8369;0.00")
    def _apply_discount(value):
        try:
            discounted = float(value or 0) * 0.95
            return round(discounted, 2)
        except Exception:
            return value
    def _format_datetime(value, fmt='%B %d, %Y at %I:%M %p'):
        if not value:
            return ''
        try:
            from datetime import datetime
            if isinstance(value, datetime):
                return value.strftime(fmt)
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            return dt.strftime(fmt)
        except Exception:
            return str(value)
    
    app.jinja_env.filters['image_url'] = _image_url_filter
    app.jinja_env.filters['currency'] = _currency_php
    app.jinja_env.filters['php'] = _php_filter
    app.jinja_env.filters['apply_discount'] = _apply_discount
    app.jinja_env.filters['format_datetime'] = _format_datetime
    app.jinja_env.globals['CURRENCY_SYMBOL'] = '&#8369;'
    # Static asset version for cache busting of JS/CSS
    try:
        import time as _time
        app.jinja_env.globals['ASSET_VERSION'] = str(int(_time.time()))
    except Exception:
        app.jinja_env.globals['ASSET_VERSION'] = '1'

    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        import traceback
        logger.error(f"Internal Server Error: {str(error)}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal server error", "detail": str(error)}), 500
    
    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        logger.warning(f"CSRF Error: {str(error)}")
        return jsonify({"error": "Invalid CSRF token"}), 400
    
    # Register before/after request handlers
    @app.before_request
    def before_request():
        # Allow public and static paths without auth
        public_paths = ['/static', '/auth', '/api/ph/', '/health', '/products', '/product/', '/search', '/about', '/contact', '/category/']
        current_path = request.path
        if any(current_path.startswith(p) for p in public_paths):
            return None
        endpoints_noauth = ['static', 'public.landing', 'public.browse_products', 'public.product_detail',
                           'public.category_products', 'public.about', 'public.contact',
                           'auth.login', 'auth.signup', 'auth.verify_otp', 'auth.resend_otp',
                           'auth.forgot_password', 'auth.reset_password', 'auth.oauth', 'auth.signup_complete',
                           'auth.api_send_otp', 'auth.api_verify_otp', 'auth.test_otp',
                           'auth.api_ph_regions', 'auth.api_ph_provinces', 'auth.api_ph_cities', 'auth.api_ph_barangays',
                           'health_check', 'payments.stripe_webhook']
        if 'user_id' not in session and request.endpoint not in endpoints_noauth and request.endpoint is not None:
            return redirect(url_for('auth.login'))
    
    @app.after_request
    def add_security_headers(response):
        # Add security headers to all responses
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        if 'Content-Security-Policy' not in response.headers:
            response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval'; script-src 'self' 'unsafe-inline' 'unsafe-eval' cdn.jsdelivr.net code.jquery.com cdn.socket.io cdnjs.cloudflare.com js.stripe.com; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com fonts.googleapis.com; font-src 'self' cdnjs.cloudflare.com fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://pplprkapzevcuelsqcfv.supabase.co wss: cdn.jsdelivr.net cdnjs.cloudflare.com cdn.socket.io; frame-src 'self' https: js.stripe.com;"
        return response
    
    # Register blueprints
    from app.controllers import (
        auth_controller, admin_controller, admin_requests_controller, seller_controller, 
        user_controller, public_controller, cart_controller,
        order_controller, search_controller, review_controller,
        rider_controller, rider_registration_controller, chat_controller,
        wishlist_controller, seller_product_enhancements
    )
    
    app.register_blueprint(auth_controller.auth_bp)
    app.register_blueprint(admin_controller.admin_bp, url_prefix='/admin')
    app.register_blueprint(admin_requests_controller.admin_requests_bp)
    app.register_blueprint(seller_controller.seller_bp, url_prefix='/seller')
    app.register_blueprint(seller_product_enhancements.seller_enhancements_bp, url_prefix='/seller')
    app.register_blueprint(user_controller.user_bp, url_prefix='/user')
    app.register_blueprint(public_controller.public_bp)
    app.register_blueprint(cart_controller.cart_bp, url_prefix='/cart')
    app.register_blueprint(order_controller.order_bp, url_prefix='/order')
    app.register_blueprint(search_controller.search_bp, url_prefix='/search')
    app.register_blueprint(review_controller.review_bp, url_prefix='/review')
    app.register_blueprint(rider_controller.rider_bp, url_prefix='/rider')
    app.register_blueprint(rider_registration_controller.rider_registration_bp, url_prefix='/rider-registration')
    app.register_blueprint(chat_controller.chat_bp, url_prefix='/chat')
    app.register_blueprint(wishlist_controller.wishlist_bp, url_prefix='/wishlist')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        from datetime import datetime as _dt
        return jsonify({"status": "ok", "timestamp": _dt.utcnow().isoformat()})
    
    # Import models to ensure they are registered
    from app.models import models
    
    # Create upload directories
    upload_folders = [
        app.config['UPLOAD_FOLDER'],
        os.path.join(app.config['UPLOAD_FOLDER'], 'products'),
        os.path.join(app.config['UPLOAD_FOLDER'], 'profiles'),
        os.path.join(app.config['UPLOAD_FOLDER'], 'documents')
    ]
    
    for folder in upload_folders:
        os.makedirs(folder, exist_ok=True)
    
    # Payments (Stripe) endpoints - exempt from CSRF
    try:
        from app.controllers.payment_controller import payment_bp
        app.register_blueprint(payment_bp, url_prefix='/payments')
        csrf.exempt(payment_bp)
        logger.info("Successfully registered payments blueprint")
    except Exception as e:
        logger.error(f"Failed to register payments blueprint: {e}")
    
    @app.context_processor
    def inject_global_data():
        """Inject global template variables"""
        from flask_wtf.csrf import generate_csrf
        from app.models.user import User
        
        data = {
            'csrf_token_value': generate_csrf()
        }
        
        # Inject current user
        if 'user_id' in session:
            current_user = User.get_by_id(session['user_id'])
            data['current_user'] = current_user
        else:
            data['current_user'] = None
        
        # Add seller-specific data
        seller_id = session.get('user_id') if session.get('user_role') == 'seller' else None
        if seller_id:
            try:
                db = Database()
                orders = db.select('orders', filters={'seller_id': seller_id, 'status': 'pending'})
                data['pending_orders'] = len(orders)
                unread = db.select('notifications', filters={'user_id': seller_id, 'is_read': False})
                data['unread_messages'] = len(unread)
            except Exception:
                data.update({'pending_orders': 0, 'unread_messages': 0})
        else:
            data.update({'pending_orders': 0, 'unread_messages': 0})
        
        return data
    
    return app
