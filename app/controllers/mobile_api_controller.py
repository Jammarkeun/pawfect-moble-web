from datetime import datetime
from decimal import Decimal
from typing import Optional

from flask import Blueprint, current_app, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.models.cart import Cart
from app.models.notification import Notification
from app.models.product import Product
from app.models.rider import Rider
from app.models.seller_request import SellerRequest
from app.models.user import User
from app.services.database import Database

mobile_api_bp = Blueprint('mobile_api', __name__)

_ACCESS_TOKEN_TTL_SECONDS = 60 * 60
_REFRESH_TOKEN_TTL_SECONDS = 60 * 60 * 24 * 30


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])


def _json_default(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _normalize_role(raw: str) -> str:
    return 'customer' if raw == 'user' else raw


def _token_for_user(user_id: int, token_type: str) -> str:
    payload = {
        'uid': int(user_id),
        'typ': token_type,
    }
    return _serializer().dumps(payload, salt='pawfect-mobile-api')


def _decode_token(token: str, expected_type: str, max_age_seconds: int):
    payload = _serializer().loads(
        token,
        salt='pawfect-mobile-api',
        max_age=max_age_seconds,
    )
    if payload.get('typ') != expected_type:
        raise BadSignature('Unexpected token type')
    return payload


def _bearer_token() -> Optional[str]:
    header = request.headers.get('Authorization', '')
    if not header.startswith('Bearer '):
        return None
    return header[7:].strip()


def _current_user_from_access_token():
    token = _bearer_token()
    if not token:
        return None

    try:
        payload = _decode_token(token, 'access', _ACCESS_TOKEN_TTL_SECONDS)
    except (BadSignature, SignatureExpired):
        return None

    user = User.get_by_id(payload.get('uid'))
    if not user:
        return None
    if user.get('status') != 'active':
        return None
    return user


def _auth_error(message: str = 'Unauthorized', status: int = 401):
    return jsonify({
        'code': 'unauthorized',
        'message': message,
        'trace_id': '',
    }), status


def _role_error(message: str = 'Forbidden'):
    return jsonify({
        'code': 'forbidden',
        'message': message,
        'trace_id': '',
    }), 403


def _require_role(*allowed_roles):
    user = _current_user_from_access_token()
    if not user:
        return None, _auth_error()

    role = _normalize_role(user.get('role') or 'user')
    if role not in allowed_roles:
        return None, _role_error('Insufficient role permissions')

    return user, None


def _is_truthy(value) -> bool:
    return str(value).strip().lower() in {'1', 'true', 'yes', 'y', 'on'}


def _include_inactive_allowed_for_admin() -> bool:
    # Production-safe default is active-only. Inactive records are returned
    # only when explicitly requested by an authenticated admin.
    requested = _is_truthy(request.args.get('include_inactive', 'false'))
    if not requested:
        return False

    user = _current_user_from_access_token()
    if not user:
        return False

    role = _normalize_role(user.get('role') or 'user')
    return role == 'admin'


def _paginate_meta(page: int, per_page: int, total: int):
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    return {
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
    }


@mobile_api_bp.after_request
def _add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PATCH, DELETE, OPTIONS'
    return response


@mobile_api_bp.route('/api/v1/<path:_path>', methods=['OPTIONS'])
def preflight(_path):
    return ('', 204)


@mobile_api_bp.route('/api/v1/auth/login', methods=['POST'])
def mobile_login():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip()
    password = (data.get('password') or '').strip()

    if not email or not password:
        return jsonify({
            'code': 'validation_error',
            'message': 'Email and password are required',
            'trace_id': '',
        }), 400

    user = User.authenticate(email, password)
    if not user:
        return jsonify({
            'code': 'invalid_credentials',
            'message': 'Invalid email or password',
            'trace_id': '',
        }), 401

    if user.get('status') != 'active':
        return jsonify({
            'code': 'account_inactive',
            'message': 'Account is not active',
            'trace_id': '',
        }), 403

    seller_request = SellerRequest.get_by_user_id(user['id'])
    rider_application = Rider.get_application_by_user(user['id'])

    if user.get('role') != 'admin' and seller_request and seller_request.get('status') == 'pending':
        return jsonify({
            'code': 'account_pending_approval',
            'message': 'Seller application is pending approval',
            'trace_id': '',
        }), 403

    if user.get('role') != 'admin' and rider_application and rider_application.get('status') == 'pending':
        return jsonify({
            'code': 'account_pending_approval',
            'message': 'Rider application is pending approval',
            'trace_id': '',
        }), 403

    access_token = _token_for_user(user['id'], 'access')
    refresh_token = _token_for_user(user['id'], 'refresh')

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': _ACCESS_TOKEN_TTL_SECONDS,
        'user': {
            'id': int(user['id']),
            'email': user.get('email') or '',
            'role': _normalize_role(user.get('role') or 'user'),
            'status': user.get('status') or 'inactive',
        },
    })


@mobile_api_bp.route('/api/v1/auth/register', methods=['POST'])
def mobile_register():
    data = request.get_json(silent=True) or {}

    first_name = (data.get('first_name') or '').strip()
    last_name = (data.get('last_name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    phone = (data.get('phone') or '').strip() or None

    if not first_name or not last_name or not email or not password:
        return jsonify({
            'code': 'validation_error',
            'message': 'first_name, last_name, email, and password are required',
            'trace_id': '',
        }), 400

    if '@' not in email:
        return jsonify({
            'code': 'validation_error',
            'message': 'Invalid email format',
            'trace_id': '',
        }), 400

    if len(password) < 6:
        return jsonify({
            'code': 'validation_error',
            'message': 'Password must be at least 6 characters',
            'trace_id': '',
        }), 400

    if User.email_exists(email):
        return jsonify({
            'code': 'duplicate_email',
            'message': 'Email is already registered',
            'trace_id': '',
        }), 409

    username_base = email.split('@')[0]
    username = username_base
    counter = 1
    while User.get_by_username(username):
        counter += 1
        username = f'{username_base}{counter}'

    created = User.create(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        address='',
        country='Philippines',
        city='Manila',
        role='user',
    )

    if not created:
        return jsonify({
            'code': 'registration_failed',
            'message': 'Unable to create account right now',
            'trace_id': '',
        }), 500

    user_id = int(created['id'])
    return jsonify({
        'access_token': _token_for_user(user_id, 'access'),
        'refresh_token': _token_for_user(user_id, 'refresh'),
        'expires_in': _ACCESS_TOKEN_TTL_SECONDS,
        'user': {
            'id': user_id,
            'email': created.get('email') or email,
            'role': _normalize_role(created.get('role') or 'user'),
            'status': created.get('status') or 'active',
        },
    }), 201


@mobile_api_bp.route('/api/v1/auth/refresh', methods=['POST'])
def mobile_refresh():
    data = request.get_json(silent=True) or {}
    refresh_token = (data.get('refresh_token') or '').strip()

    if not refresh_token:
        return jsonify({
            'code': 'validation_error',
            'message': 'refresh_token is required',
            'trace_id': '',
        }), 400

    try:
        payload = _decode_token(refresh_token, 'refresh', _REFRESH_TOKEN_TTL_SECONDS)
    except SignatureExpired:
        return jsonify({
            'code': 'token_expired',
            'message': 'Refresh token expired',
            'trace_id': '',
        }), 401
    except BadSignature:
        return _auth_error('Invalid refresh token')

    user = User.get_by_id(payload.get('uid'))
    if not user or user.get('status') != 'active':
        return _auth_error('Account unavailable')

    return jsonify({
        'access_token': _token_for_user(user['id'], 'access'),
        'refresh_token': _token_for_user(user['id'], 'refresh'),
        'expires_in': _ACCESS_TOKEN_TTL_SECONDS,
        'user': {
            'id': int(user['id']),
            'email': user.get('email') or '',
            'role': _normalize_role(user.get('role') or 'user'),
            'status': user.get('status') or 'inactive',
        },
    })


@mobile_api_bp.route('/api/v1/auth/me', methods=['GET'])
def mobile_me():
    user = _current_user_from_access_token()
    if not user:
        return _auth_error()

    return jsonify({
        'id': int(user['id']),
        'email': user.get('email') or '',
        'role': _normalize_role(user.get('role') or 'user'),
        'status': user.get('status') or 'inactive',
    })


@mobile_api_bp.route('/api/v1/auth/logout', methods=['POST'])
def mobile_logout():
    return jsonify({'success': True})


@mobile_api_bp.route('/api/v1/catalog/products', methods=['GET'])
def mobile_products():
    page = max(1, int(request.args.get('page', 1)))
    per_page = max(1, min(100, int(request.args.get('per_page', 20))))
    search = (request.args.get('search') or '').strip() or None
    offset = (page - 1) * per_page
    status_filter = None if _include_inactive_allowed_for_admin() else 'active'

    items = Product.list(
        search=search,
        status=status_filter,
        limit=per_page,
        offset=offset,
    ) or []
    total = Product.count(search=search, status=status_filter)

    mapped = []
    for item in items:
        mapped.append({
            'id': int(item.get('id') or 0),
            'name': item.get('name') or '',
            'price': float(item.get('effective_price') or item.get('price') or 0),
            'stock_quantity': int(item.get('stock_quantity') or 0),
            'status': item.get('status') or 'inactive',
            'image_url': item.get('image_url') or '',
        })

    return jsonify({
        'items': mapped,
        'meta': _paginate_meta(page, per_page, total),
    })


@mobile_api_bp.route('/api/v1/catalog/search/suggestions', methods=['GET'])
def mobile_search_suggestions():
    query = (request.args.get('q') or '').strip()
    if len(query) < 2:
        return jsonify([])

    include_inactive = _include_inactive_allowed_for_admin()
    status_clause = '' if include_inactive else "status = 'active' AND "

    db = Database()
    rows = db.execute_query(
        f"""
        SELECT id, name, price
        FROM products
        WHERE {status_clause}name LIKE %s
        ORDER BY name ASC
        LIMIT 8
        """,
        (f'%{query}%',),
        fetch=True,
    ) or []

    return jsonify([
        {
            'id': int(row.get('id') or 0),
            'name': row.get('name') or '',
            'price': float(row.get('price') or 0),
        }
        for row in rows
    ])


@mobile_api_bp.route('/api/v1/cart', methods=['GET'])
def mobile_cart():
    user = _current_user_from_access_token()
    if not user:
        return _auth_error()

    cart_items = Cart.get_user_cart(user['id']) or []
    items = []
    total_amount = 0.0

    for item in cart_items:
        quantity = int(item.get('quantity') or 0)
        unit_price = float(item.get('price') or 0)
        line_total = unit_price * quantity
        total_amount += line_total

        items.append({
            'id': int(item.get('id') or 0),
            'product_id': int(item.get('product_id') or 0),
            'variant_id': item.get('variant_id'),
            'quantity': quantity,
            'unit_price': unit_price,
            'total_price': line_total,
        })

    return jsonify({
        'items': items,
        'total_amount': total_amount,
    })


@mobile_api_bp.route('/api/v1/cart/items', methods=['POST'])
def mobile_add_cart_item():
    user = _current_user_from_access_token()
    if not user:
        return _auth_error()

    data = request.get_json(silent=True) or {}
    product_id_raw = data.get('product_id')
    quantity_raw = data.get('quantity', 1)
    variant_id_raw = data.get('variant_id')

    try:
        product_id = int(product_id_raw)
        quantity = int(quantity_raw)
    except (TypeError, ValueError):
        return jsonify({
            'code': 'validation_error',
            'message': 'product_id and quantity must be valid integers',
            'trace_id': '',
        }), 400

    if quantity <= 0:
        return jsonify({
            'code': 'validation_error',
            'message': 'quantity must be greater than zero',
            'trace_id': '',
        }), 400

    variant_id = None
    if variant_id_raw is not None and str(variant_id_raw).strip() != '':
        try:
            variant_id = int(variant_id_raw)
        except (TypeError, ValueError):
            return jsonify({
                'code': 'validation_error',
                'message': 'variant_id must be an integer when provided',
                'trace_id': '',
            }), 400

    product = Product.get_by_id(product_id)
    if not product:
        return jsonify({
            'code': 'not_found',
            'message': 'Product not found',
            'trace_id': '',
        }), 404

    if product.get('status') != 'active':
        return jsonify({
            'code': 'product_inactive',
            'message': 'Product is not available',
            'trace_id': '',
        }), 409

    stock_quantity = int(product.get('stock_quantity') or 0)
    existing = Cart.get_item(int(user['id']), product_id, variant_id)
    existing_qty = int(existing.get('quantity') or 0) if existing else 0
    requested_total = existing_qty + quantity

    if requested_total > stock_quantity:
        return jsonify({
            'code': 'insufficient_stock',
            'message': 'Requested quantity exceeds available stock',
            'trace_id': '',
            'details': {
                'stock_quantity': stock_quantity,
                'requested_quantity': requested_total,
            },
        }), 409

    Cart.add_item(
        user_id=int(user['id']),
        product_id=product_id,
        quantity=quantity,
        variant_id=variant_id,
    )

    return jsonify({'success': True}), 201


@mobile_api_bp.route('/api/v1/checkout/summary', methods=['POST'])
def mobile_checkout_summary():
    user = _current_user_from_access_token()
    if not user:
        return _auth_error()

    data = request.get_json(silent=True) or {}
    selected_ids = data.get('selected_item_ids') or []
    selected_ids = {int(item_id) for item_id in selected_ids if str(item_id).isdigit()}

    cart_items = Cart.get_user_cart(user['id']) or []
    if selected_ids:
        cart_items = [item for item in cart_items if int(item.get('id') or 0) in selected_ids]

    product_total = 0.0
    for item in cart_items:
        quantity = int(item.get('quantity') or 0)
        unit_price = float(item.get('price') or 0)
        product_total += unit_price * quantity

    delivery_fee = 50.0 if cart_items else 0.0
    total_amount = product_total + delivery_fee

    return jsonify({
        'product_total': product_total,
        'delivery_fee': delivery_fee,
        'total_amount': total_amount,
    })


@mobile_api_bp.route('/api/v1/orders', methods=['GET'])
def mobile_orders():
    user = _current_user_from_access_token()
    if not user:
        return _auth_error()

    db = Database()
    rows = db.execute_query(
        """
        SELECT id, total_amount, status, created_at
        FROM orders
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 50
        """,
        (user['id'],),
        fetch=True,
    ) or []

    items = []
    for row in rows:
        order_id = int(row.get('id') or 0)
        items.append({
            'id': order_id,
            'order_number': f'PF-{order_id:06d}',
            'status': row.get('status') or 'pending',
            'total_amount': float(row.get('total_amount') or 0),
        })

    return jsonify({'items': items})


@mobile_api_bp.route('/api/v1/seller/dashboard', methods=['GET'])
def mobile_seller_dashboard():
    user, error = _require_role('seller', 'admin')
    if error:
        return error

    seller_id = int(user['id'])
    db = Database()

    product_stats = db.execute_query(
        """
        SELECT
            COUNT(*) as total_products,
            SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_products
        FROM products
        WHERE seller_id = %s
        """,
        (seller_id,),
        fetch=True,
        fetchone=True,
    ) or {}

    order_stats = db.execute_query(
        """
        SELECT
            COUNT(*) as total_orders,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_orders,
            COALESCE(SUM(total_amount), 0) as total_revenue
        FROM orders
        WHERE seller_id = %s AND status <> 'cancelled'
        """,
        (seller_id,),
        fetch=True,
        fetchone=True,
    ) or {}

    return jsonify({
        'total_products': int(product_stats.get('total_products') or 0),
        'active_products': int(product_stats.get('active_products') or 0),
        'total_orders': int(order_stats.get('total_orders') or 0),
        'pending_orders': int(order_stats.get('pending_orders') or 0),
        'total_revenue': float(order_stats.get('total_revenue') or 0),
    })


@mobile_api_bp.route('/api/v1/seller/products', methods=['GET'])
def mobile_seller_products():
    user, error = _require_role('seller', 'admin')
    if error:
        return error

    page = max(1, int(request.args.get('page', 1)))
    per_page = max(1, min(100, int(request.args.get('per_page', 20))))
    offset = (page - 1) * per_page

    items = Product.list(
        seller_id=int(user['id']),
        status=None,
        limit=per_page,
        offset=offset,
    ) or []

    mapped = []
    for item in items:
        mapped.append({
            'id': int(item.get('id') or 0),
            'name': item.get('name') or '',
            'price': float(item.get('price') or 0),
            'stock_quantity': int(item.get('stock_quantity') or 0),
            'status': item.get('status') or 'inactive',
        })

    return jsonify({'items': mapped, 'meta': {'page': page, 'per_page': per_page}})


@mobile_api_bp.route('/api/v1/seller/orders', methods=['GET'])
def mobile_seller_orders():
    user, error = _require_role('seller', 'admin')
    if error:
        return error

    status = (request.args.get('status') or '').strip() or None
    db = Database()
    rows = db.execute_query(
        """
        SELECT id, total_amount, status, created_at
        FROM orders
        WHERE seller_id = %s
          AND (%s IS NULL OR status = %s)
        ORDER BY created_at DESC
        LIMIT 50
        """,
        (int(user['id']), status, status),
        fetch=True,
    ) or []

    items = []
    for row in rows:
        order_id = int(row.get('id') or 0)
        items.append({
            'id': order_id,
            'order_number': f'PF-{order_id:06d}',
            'status': row.get('status') or 'pending',
            'total_amount': float(row.get('total_amount') or 0),
        })

    return jsonify({'items': items})


@mobile_api_bp.route('/api/v1/seller/orders/<int:order_id>/status', methods=['PATCH'])
def mobile_seller_update_order_status(order_id: int):
    user, error = _require_role('seller', 'admin')
    if error:
        return error

    data = request.get_json(silent=True) or {}
    new_status = (data.get('status') or '').strip()
    allowed_statuses = {'confirmed', 'preparing', 'shipped', 'cancelled'}

    if new_status not in allowed_statuses:
        return jsonify({
            'code': 'validation_error',
            'message': f'status must be one of: {", ".join(sorted(allowed_statuses))}',
            'trace_id': '',
        }), 400

    db = Database()
    current = db.execute_query(
        "SELECT id, status FROM orders WHERE id = %s AND seller_id = %s",
        (order_id, int(user['id'])),
        fetch=True,
        fetchone=True,
    )
    if not current:
        return jsonify({
            'code': 'not_found',
            'message': 'Order not found for this seller',
            'trace_id': '',
        }), 404

    if current.get('status') in ('delivered', 'cancelled'):
        return jsonify({
            'code': 'invalid_transition',
            'message': 'Cannot modify delivered or cancelled orders',
            'trace_id': '',
        }), 409

    db.execute_query(
        "UPDATE orders SET status = %s, updated_at = NOW() WHERE id = %s AND seller_id = %s",
        (new_status, order_id, int(user['id'])),
    )

    return jsonify({'success': True, 'order_id': order_id, 'status': new_status})


@mobile_api_bp.route('/api/v1/rider/dashboard', methods=['GET'])
def mobile_rider_dashboard():
    user, error = _require_role('rider', 'admin')
    if error:
        return error

    rider_id = int(user['id'])
    db = Database()

    delivery_stats = db.execute_query(
        """
        SELECT
            COUNT(*) as total_deliveries,
            SUM(CASE WHEN status = 'assigned' THEN 1 ELSE 0 END) as assigned,
            SUM(CASE WHEN status = 'picked_up' THEN 1 ELSE 0 END) as picked_up,
            SUM(CASE WHEN status = 'on_the_way' THEN 1 ELSE 0 END) as on_the_way,
            SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as delivered
        FROM deliveries
        WHERE rider_id = %s
        """,
        (rider_id,),
        fetch=True,
        fetchone=True,
    ) or {}

    earnings = db.execute_query(
        """
        SELECT COALESCE(SUM(total_earning), 0) as total_earnings
        FROM rider_earnings
        WHERE rider_id = %s
        """,
        (rider_id,),
        fetch=True,
        fetchone=True,
    ) or {}

    return jsonify({
        'total_deliveries': int(delivery_stats.get('total_deliveries') or 0),
        'assigned': int(delivery_stats.get('assigned') or 0),
        'picked_up': int(delivery_stats.get('picked_up') or 0),
        'on_the_way': int(delivery_stats.get('on_the_way') or 0),
        'delivered': int(delivery_stats.get('delivered') or 0),
        'total_earnings': float(earnings.get('total_earnings') or 0),
    })


@mobile_api_bp.route('/api/v1/rider/available-orders', methods=['GET'])
def mobile_rider_available_orders():
    user, error = _require_role('rider', 'admin')
    if error:
        return error

    db = Database()
    rows = db.execute_query(
        """
        SELECT id, status, total_amount, shipping_address, created_at
        FROM orders
        WHERE rider_id IS NULL
          AND status IN ('confirmed', 'preparing', 'shipped')
        ORDER BY created_at ASC
        LIMIT 50
        """,
        fetch=True,
    ) or []

    items = []
    for row in rows:
        order_id = int(row.get('id') or 0)
        items.append({
            'id': order_id,
            'order_number': f'PF-{order_id:06d}',
            'status': row.get('status') or 'confirmed',
            'total_amount': float(row.get('total_amount') or 0),
            'shipping_address': row.get('shipping_address') or '',
        })

    return jsonify({'items': items})


@mobile_api_bp.route('/api/v1/rider/my-deliveries', methods=['GET'])
def mobile_rider_my_deliveries():
    user, error = _require_role('rider', 'admin')
    if error:
        return error

    db = Database()
    rows = db.execute_query(
        """
        SELECT o.id, o.status, o.total_amount, o.shipping_address
        FROM orders o
        WHERE o.rider_id = %s
        ORDER BY o.updated_at DESC
        LIMIT 50
        """,
        (int(user['id']),),
        fetch=True,
    ) or []

    items = []
    for row in rows:
        order_id = int(row.get('id') or 0)
        items.append({
            'id': order_id,
            'order_number': f'PF-{order_id:06d}',
            'status': row.get('status') or 'assigned',
            'total_amount': float(row.get('total_amount') or 0),
            'shipping_address': row.get('shipping_address') or '',
        })

    return jsonify({'items': items})


@mobile_api_bp.route('/api/v1/rider/delivery/accept', methods=['POST'])
def mobile_rider_accept_delivery():
    user, error = _require_role('rider', 'admin')
    if error:
        return error

    data = request.get_json(silent=True) or {}
    order_id = data.get('order_id')
    if not str(order_id).isdigit():
        return jsonify({
            'code': 'validation_error',
            'message': 'order_id is required',
            'trace_id': '',
        }), 400

    db = Database()
    conn = db.connect()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id
            FROM orders
            WHERE id = %s
              AND rider_id IS NULL
              AND status IN ('confirmed', 'preparing', 'shipped')
            FOR UPDATE
            """,
            (int(order_id),),
        )
        row = cursor.fetchone()
        if not row:
            conn.rollback()
            return jsonify({
                'code': 'order_unavailable',
                'message': 'Order is no longer available',
                'trace_id': '',
            }), 409

        cursor.execute(
            """
            UPDATE orders
            SET rider_id = %s, status = 'picked_up', updated_at = NOW()
            WHERE id = %s
            """,
            (int(user['id']), int(order_id)),
        )
        cursor.execute(
            """
            INSERT INTO deliveries (order_id, rider_id, status, assigned_at)
            VALUES (%s, %s, 'assigned', NOW())
            ON DUPLICATE KEY UPDATE
                rider_id = VALUES(rider_id),
                status = 'assigned',
                assigned_at = NOW()
            """,
            (int(order_id), int(user['id'])),
        )
        conn.commit()
        return jsonify({'success': True})
    except Exception:
        conn.rollback()
        return jsonify({
            'code': 'server_error',
            'message': 'Failed to accept delivery',
            'trace_id': '',
        }), 500
    finally:
        conn.close()


@mobile_api_bp.route('/api/v1/rider/deliveries/<int:order_id>/status', methods=['PATCH'])
def mobile_rider_update_delivery_status(order_id: int):
    user, error = _require_role('rider', 'admin')
    if error:
        return error

    data = request.get_json(silent=True) or {}
    new_status = (data.get('status') or '').strip()
    allowed_statuses = {'picked_up', 'on_the_way', 'delivered'}

    if new_status not in allowed_statuses:
        return jsonify({
            'code': 'validation_error',
            'message': f'status must be one of: {", ".join(sorted(allowed_statuses))}',
            'trace_id': '',
        }), 400

    db = Database()
    current = db.execute_query(
        "SELECT id, status FROM orders WHERE id = %s AND rider_id = %s",
        (order_id, int(user['id'])),
        fetch=True,
        fetchone=True,
    )
    if not current:
        return jsonify({
            'code': 'not_found',
            'message': 'Delivery not found for this rider',
            'trace_id': '',
        }), 404

    current_status = current.get('status') or ''
    valid_next = {
        'picked_up': {'on_the_way'},
        'on_the_way': {'delivered'},
        'delivered': set(),
    }
    if new_status not in valid_next.get(current_status, set()):
        return jsonify({
            'code': 'invalid_transition',
            'message': f'Cannot transition from {current_status} to {new_status}',
            'trace_id': '',
        }), 409

    db.execute_query(
        "UPDATE orders SET status = %s, updated_at = NOW() WHERE id = %s AND rider_id = %s",
        (new_status, order_id, int(user['id'])),
    )

    delivery_status_map = {
        'on_the_way': 'on_the_way',
        'delivered': 'delivered',
    }
    if new_status in delivery_status_map:
        status_value = delivery_status_map[new_status]
        if new_status == 'delivered':
            db.execute_query(
                """
                UPDATE deliveries
                SET status = %s, delivered_at = NOW()
                WHERE order_id = %s AND rider_id = %s
                """,
                (status_value, order_id, int(user['id'])),
            )
        else:
            db.execute_query(
                """
                UPDATE deliveries
                SET status = %s
                WHERE order_id = %s AND rider_id = %s
                """,
                (status_value, order_id, int(user['id'])),
            )

    return jsonify({'success': True, 'order_id': order_id, 'status': new_status})


@mobile_api_bp.route('/api/v1/admin/dashboard', methods=['GET'])
def mobile_admin_dashboard():
    user, error = _require_role('admin')
    if error:
        return error

    db = Database()
    users = db.execute_query(
        """
        SELECT
            COUNT(*) as total_users,
            SUM(CASE WHEN role = 'user' THEN 1 ELSE 0 END) as customers,
            SUM(CASE WHEN role = 'seller' THEN 1 ELSE 0 END) as sellers,
            SUM(CASE WHEN role = 'rider' THEN 1 ELSE 0 END) as riders
        FROM users
        WHERE role <> 'admin'
        """,
        fetch=True,
        fetchone=True,
    ) or {}

    orders = db.execute_query(
        """
        SELECT
            COUNT(*) as total_orders,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_orders,
            SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as delivered_orders,
            COALESCE(SUM(CASE WHEN status <> 'cancelled' THEN total_amount ELSE 0 END), 0) as total_revenue
        FROM orders
        """,
        fetch=True,
        fetchone=True,
    ) or {}

    pending = {
        'seller_requests': SellerRequest.get_requests_count(status='pending'),
        'rider_requests': Rider.get_applications_count(status='pending'),
    }

    return jsonify({
        'users': {
            'total': int(users.get('total_users') or 0),
            'customers': int(users.get('customers') or 0),
            'sellers': int(users.get('sellers') or 0),
            'riders': int(users.get('riders') or 0),
        },
        'orders': {
            'total': int(orders.get('total_orders') or 0),
            'pending': int(orders.get('pending_orders') or 0),
            'delivered': int(orders.get('delivered_orders') or 0),
            'revenue': float(orders.get('total_revenue') or 0),
        },
        'pending': pending,
    })


@mobile_api_bp.route('/api/v1/admin/users', methods=['GET'])
def mobile_admin_users():
    user, error = _require_role('admin')
    if error:
        return error

    role = (request.args.get('role') or '').strip() or None
    status = (request.args.get('status') or '').strip() or None
    page = max(1, int(request.args.get('page', 1)))
    per_page = max(1, min(100, int(request.args.get('per_page', 20))))
    offset = (page - 1) * per_page

    rows = User.get_all_users(role=role, status=status, limit=per_page, offset=offset) or []

    items = []
    for row in rows:
        items.append({
            'id': int(row.get('id') or 0),
            'email': row.get('email') or '',
            'username': row.get('username') or '',
            'first_name': row.get('first_name') or '',
            'last_name': row.get('last_name') or '',
            'role': _normalize_role(row.get('role') or 'user'),
            'status': row.get('status') or 'inactive',
        })

    return jsonify({'items': items, 'meta': {'page': page, 'per_page': per_page}})


@mobile_api_bp.route('/api/v1/admin/users/<int:user_id>/status', methods=['PATCH'])
def mobile_admin_update_user_status(user_id: int):
    admin_user, error = _require_role('admin')
    if error:
        return error

    data = request.get_json(silent=True) or {}
    new_status = (data.get('status') or '').strip()
    reason = (data.get('reason') or '').strip()
    allowed_statuses = {'active', 'inactive', 'banned'}

    if new_status not in allowed_statuses:
        return jsonify({
            'code': 'validation_error',
            'message': f'status must be one of: {", ".join(sorted(allowed_statuses))}',
            'trace_id': '',
        }), 400

    target = User.get_by_id(user_id)
    if not target or target.get('role') == 'admin':
        return jsonify({'code': 'not_found', 'message': 'User not found', 'trace_id': ''}), 404

    User.update_status(user_id, new_status)

    notice_title = 'Account status updated'
    notice_message = f'Your account status has been set to {new_status}.'
    if reason:
        notice_message = f'{notice_message} Reason: {reason}'
    Notification.create(
        user_id=user_id,
        role=target.get('role') or 'user',
        type_='general',
        title=notice_title,
        message=notice_message,
        related_id=user_id,
        data={'status': new_status},
    )

    return jsonify({'success': True, 'user_id': user_id, 'status': new_status})


@mobile_api_bp.route('/api/v1/admin/seller-requests', methods=['GET'])
def mobile_admin_seller_requests():
    user, error = _require_role('admin')
    if error:
        return error

    status = (request.args.get('status') or '').strip() or None
    rows = SellerRequest.get_all_requests(status=status) or []

    items = []
    for row in rows:
        items.append({
            'id': int(row.get('id') or 0),
            'user_id': int(row.get('user_id') or 0),
            'applicant_name': f"{row.get('first_name') or ''} {row.get('last_name') or ''}".strip(),
            'business_name': row.get('business_name') or '',
            'status': row.get('status') or 'pending',
            'requested_at': row.get('requested_at').isoformat() if row.get('requested_at') else None,
        })

    return jsonify({'items': items})


@mobile_api_bp.route('/api/v1/admin/seller-requests/<int:request_id>/approve', methods=['POST'])
def mobile_admin_approve_seller(request_id: int):
    user, error = _require_role('admin')
    if error:
        return error

    data = request.get_json(silent=True) or {}
    notes = (data.get('notes') or '').strip() or None
    req = SellerRequest.get_by_id(request_id)
    if not req:
        return jsonify({'code': 'not_found', 'message': 'Request not found', 'trace_id': ''}), 404

    success = SellerRequest.approve_request(request_id, notes)
    if not success:
        return jsonify({'code': 'invalid_request', 'message': 'Unable to approve request', 'trace_id': ''}), 409

    Notification.create(
        user_id=req['user_id'],
        role='seller',
        type_='general',
        title='Seller Application Approved',
        message='Your seller application has been approved. You can now access seller features.',
        related_id=request_id,
        data={'account_type': 'seller', 'status': 'approved'},
    )

    return jsonify({'success': True, 'request_id': request_id, 'status': 'approved'})


@mobile_api_bp.route('/api/v1/admin/seller-requests/<int:request_id>/reject', methods=['POST'])
def mobile_admin_reject_seller(request_id: int):
    user, error = _require_role('admin')
    if error:
        return error

    data = request.get_json(silent=True) or {}
    notes = (data.get('notes') or '').strip()
    if not notes:
        return jsonify({'code': 'validation_error', 'message': 'notes is required', 'trace_id': ''}), 400

    req = SellerRequest.get_by_id(request_id)
    if not req:
        return jsonify({'code': 'not_found', 'message': 'Request not found', 'trace_id': ''}), 404

    SellerRequest.reject_request(request_id, notes)
    Notification.create(
        user_id=req['user_id'],
        role='user',
        type_='general',
        title='Seller Application Rejected',
        message=f'Your seller application was rejected. Reason: {notes}',
        related_id=request_id,
        data={'account_type': 'seller', 'status': 'rejected'},
    )

    return jsonify({'success': True, 'request_id': request_id, 'status': 'rejected'})


@mobile_api_bp.route('/api/v1/admin/rider-requests', methods=['GET'])
def mobile_admin_rider_requests():
    user, error = _require_role('admin')
    if error:
        return error

    status = (request.args.get('status') or '').strip() or None
    rows = Rider.get_all_applications(status=status) or []
    items = []
    for row in rows:
        items.append({
            'id': int(row.get('id') or 0),
            'user_id': int(row.get('user_id') or 0),
            'applicant_name': f"{row.get('first_name') or ''} {row.get('last_name') or ''}".strip(),
            'vehicle_type': row.get('vehicle_type') or '',
            'status': row.get('status') or 'pending',
            'created_at': row.get('created_at').isoformat() if row.get('created_at') else None,
        })

    return jsonify({'items': items})


@mobile_api_bp.route('/api/v1/admin/rider-requests/<int:application_id>/approve', methods=['POST'])
def mobile_admin_approve_rider(application_id: int):
    user, error = _require_role('admin')
    if error:
        return error

    data = request.get_json(silent=True) or {}
    notes = (data.get('notes') or '').strip() or None
    application = Rider.get_application_by_id(application_id)
    if not application:
        return jsonify({'code': 'not_found', 'message': 'Request not found', 'trace_id': ''}), 404

    Rider.update_application_status(application_id, 'approved', notes)
    Rider.activate_rider_account(application['user_id'])
    Notification.create(
        user_id=application['user_id'],
        role='rider',
        type_='general',
        title='Rider Application Approved',
        message='Your rider application has been approved. You can now access rider features.',
        related_id=application_id,
        data={'account_type': 'rider', 'status': 'approved'},
    )

    return jsonify({'success': True, 'request_id': application_id, 'status': 'approved'})


@mobile_api_bp.route('/api/v1/admin/rider-requests/<int:application_id>/reject', methods=['POST'])
def mobile_admin_reject_rider(application_id: int):
    user, error = _require_role('admin')
    if error:
        return error

    data = request.get_json(silent=True) or {}
    notes = (data.get('notes') or '').strip()
    if not notes:
        return jsonify({'code': 'validation_error', 'message': 'notes is required', 'trace_id': ''}), 400

    application = Rider.get_application_by_id(application_id)
    if not application:
        return jsonify({'code': 'not_found', 'message': 'Request not found', 'trace_id': ''}), 404

    Rider.update_application_status(application_id, 'rejected', notes)
    Notification.create(
        user_id=application['user_id'],
        role='user',
        type_='general',
        title='Rider Application Rejected',
        message=f'Your rider application was rejected. Reason: {notes}',
        related_id=application_id,
        data={'account_type': 'rider', 'status': 'rejected'},
    )

    return jsonify({'success': True, 'request_id': application_id, 'status': 'rejected'})


@mobile_api_bp.route('/api/v1/admin/settings', methods=['GET'])
def mobile_admin_settings_get():
    user, error = _require_role('admin')
    if error:
        return error

    from app.utils.settings import Settings

    return jsonify({'items': Settings.get_all()})


@mobile_api_bp.route('/api/v1/admin/settings', methods=['PATCH'])
def mobile_admin_settings_patch():
    user, error = _require_role('admin')
    if error:
        return error

    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict) or not data:
        return jsonify({'code': 'validation_error', 'message': 'settings payload required', 'trace_id': ''}), 400

    from app.utils.settings import Settings

    Settings.set_multiple(data)
    return jsonify({'success': True})


@mobile_api_bp.route('/api/v1/notifications', methods=['GET'])
def mobile_notifications():
    user = _current_user_from_access_token()
    if not user:
        return _auth_error()

    role = user.get('role') or 'user'
    limit = max(1, min(100, int(request.args.get('limit', 20))))
    items = Notification.list_for_user(user['id'], role, limit=limit) or []

    mapped = []
    for item in items:
        mapped.append({
            'id': int(item.get('id') or 0),
            'type': item.get('type') or 'general',
            'title': item.get('title') or '',
            'message': item.get('message') or '',
            'is_read': bool(item.get('is_read') or False),
            'created_at': item.get('created_at').isoformat() if item.get('created_at') else None,
        })

    return jsonify({'items': mapped})


@mobile_api_bp.route('/api/v1/notifications/unread-count', methods=['GET'])
def mobile_notifications_unread_count():
    user = _current_user_from_access_token()
    if not user:
        return _auth_error()

    role = user.get('role') or 'user'
    return jsonify({'count': Notification.unread_count(user['id'], role)})


@mobile_api_bp.route('/api/v1/notifications/mark-read', methods=['POST'])
def mobile_notifications_mark_read():
    user = _current_user_from_access_token()
    if not user:
        return _auth_error()

    data = request.get_json(silent=True) or {}
    notification_id = data.get('id')
    if not str(notification_id).isdigit():
        return jsonify({'code': 'validation_error', 'message': 'id is required', 'trace_id': ''}), 400

    Notification.mark_read(int(notification_id), user['id'])
    return jsonify({'success': True})


@mobile_api_bp.route('/api/v1/notifications/mark-all-read', methods=['POST'])
def mobile_notifications_mark_all_read():
    user = _current_user_from_access_token()
    if not user:
        return _auth_error()

    role = user.get('role') or 'user'
    Notification.mark_all_read(user['id'], role)
    return jsonify({'success': True})


@mobile_api_bp.route('/api/v1/payments/history', methods=['GET'])
def mobile_payments_history():
    user = _current_user_from_access_token()
    if not user:
        return _auth_error()

    db = Database()
    rows = db.execute_query(
        """
        SELECT id, total_amount, payment_method, payment_status, status, created_at
        FROM orders
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 50
        """,
        (int(user['id']),),
        fetch=True,
    ) or []

    items = []
    for row in rows:
        order_id = int(row.get('id') or 0)
        items.append({
            'order_id': order_id,
            'order_number': f'PF-{order_id:06d}',
            'amount': float(row.get('total_amount') or 0),
            'payment_method': row.get('payment_method') or 'cod',
            'payment_status': row.get('payment_status') or 'pending',
            'order_status': row.get('status') or 'pending',
            'created_at': row.get('created_at').isoformat() if row.get('created_at') else None,
        })

    return jsonify({'items': items})
