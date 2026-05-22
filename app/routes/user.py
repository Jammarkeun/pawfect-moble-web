"""
User routes blueprint - Aliases for customer routes for template compatibility
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

# Import all customer route functions
from app.routes.customer import (
    dashboard as customer_dashboard,
    my_messages,
    cart,
    add_to_cart,
    update_cart,
    remove_from_cart,
    checkout,
    place_order,
    orders,
    order_detail,
    profile,
    update_profile,
    wishlist,
    add_to_wishlist,
    remove_from_wishlist,
    review_product
)

# Create user blueprint
user_bp = Blueprint('user', __name__)

# Route aliases for template compatibility
@user_bp.route('/dashboard')
def dashboard():
    """Customer dashboard"""
    return customer_dashboard()

@user_bp.route('/messages')
def messages():
    """Customer messages"""
    return my_messages()

@user_bp.route('/cart')
def user_cart():
    """Shopping cart"""
    return cart()

@user_bp.route('/add-to-cart', methods=['POST'])
def user_add_to_cart():
    """Add item to cart"""
    return add_to_cart()

@user_bp.route('/update-cart', methods=['POST'])
def user_update_cart():
    """Update cart"""
    return update_cart()

@user_bp.route('/remove-from-cart/<int:cart_id>')
def user_remove_from_cart(cart_id):
    """Remove item from cart"""
    return remove_from_cart(cart_id)

@user_bp.route('/checkout')
def user_checkout():
    """Checkout page"""
    return checkout()

@user_bp.route('/place-order', methods=['POST'])
def user_place_order():
    """Place order"""
    return place_order()

@user_bp.route('/orders')
def user_orders():
    """Customer orders"""
    return orders()

@user_bp.route('/order/<int:order_id>')
def user_order_detail(order_id):
    """Order details"""
    return order_detail(order_id)

@user_bp.route('/profile')
def user_profile():
    """Customer profile"""
    return profile()

@user_bp.route('/update-profile', methods=['POST'])
def user_update_profile():
    """Update profile"""
    return update_profile()

@user_bp.route('/wishlist')
def user_wishlist():
    """Wishlist"""
    return wishlist()

@user_bp.route('/add-to-wishlist', methods=['POST'])
def user_add_to_wishlist():
    """Add to wishlist"""
    return add_to_wishlist()

@user_bp.route('/remove-from-wishlist/<int:product_id>', methods=['GET', 'POST'])
def user_remove_from_wishlist(product_id):
    """Remove from wishlist"""
    return remove_from_wishlist(product_id)

@user_bp.route('/review/<int:order_item_id>', methods=['GET', 'POST'])
def user_review_product(order_item_id):
    """Review product"""
    return review_product(order_item_id)

@user_bp.route('/settings')
def user_settings():
    """User settings"""
    return profile()

@user_bp.route('/become-seller')
def user_become_seller():
    """Become seller page"""
    from app.routes.main import become_seller
    return become_seller()

# Notification routes
@user_bp.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    """Get user notifications"""
    try:
        from app.models.models import Notification
        from app import db
        
        limit = request.args.get('limit', 10, type=int)
        notifications = Notification.query.filter_by(user_id=current_user['id'])\
            .order_by(Notification.created_at.desc())\
            .limit(limit)\
            .all()
        
        data = [{
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'type': n.type,
            'is_read': n.is_read,
            'created_at': n.created_at.isoformat() if n.created_at else None,
            'link': n.link if hasattr(n, 'link') else None
        } for n in notifications]
        
        return jsonify({
            'success': True,
            'notifications': data,
            'count': len(data)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@user_bp.route('/notifications/unread-count', methods=['GET'])
@login_required
def get_unread_count():
    """Get unread notification count"""
    try:
        from app.models.models import Notification
        
        count = Notification.query.filter_by(user_id=current_user['id'], is_read=False).count()
        return jsonify({
            'success': True,
            'count': count
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'count': 0}), 500

@user_bp.route('/notifications/mark-read', methods=['POST'])
@login_required
def mark_notification_read():
    """Mark single notification as read"""
    try:
        from app.models.models import Notification
        from app import db
        
        data = request.get_json() or {}
        notif_id = data.get('id')
        
        if not notif_id:
            return jsonify({'success': False, 'error': 'Missing notification ID'}), 400
        
        notification = Notification.query.filter_by(
            id=notif_id, 
            user_id=current_user['id']
        ).first()
        
        if not notification:
            return jsonify({'success': False, 'error': 'Notification not found'}), 404
        
        notification.is_read = True
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@user_bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read"""
    try:
        from app.models.models import Notification
        from app import db
        
        Notification.query.filter_by(user_id=current_user['id'], is_read=False).update({'is_read': True})
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
