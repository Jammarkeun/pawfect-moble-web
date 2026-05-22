from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from app.utils.decorators import login_required
from app.models.user import User
from app.models.notification import Notification
from app.models.order import Order
from app.models.seller_request import SellerRequest
from app.models.review import Review
from app.models.cart import Cart
from app.models.product import Product
from app.utils.decorators import login_required
from app.forms import BecomeSellerForm, CheckoutForm, ReviewForm, CartUpdateForm, CartAddForm, ProfileUpdateForm, ChangePasswordForm
from werkzeug.utils import secure_filename
import os
import uuid

user_bp = Blueprint('user', __name__)

@user_bp.route('/notifications')
@login_required
def get_notifications():
    user_id = session.get('user_id')
    role = session.get('user_role') or session.get('role') or 'user'
    items = Notification.list_for_user(user_id, role, limit=int(request.args.get('limit', 20)))
    # Ensure items are JSON-serializable and consistent
    for it in items:
        if isinstance(it.get('data'), (bytes, bytearray)):
            try:
                it['data'] = it['data'].decode('utf-8', errors='ignore')
            except Exception:
                it['data'] = None
    return jsonify({'success': True, 'notifications': items})

@user_bp.route('/notifications/unread-count')
@login_required
def notifications_unread_count():
    user_id = session.get('user_id')
    role = session.get('user_role') or session.get('role') or 'user'
    count = Notification.unread_count(user_id, role)
    return jsonify({'success': True, 'count': count})

@user_bp.route('/notifications/mark-read', methods=['POST'])
@login_required
def mark_notification_read():
    user_id = session.get('user_id')
    nid = request.json.get('id') if request.is_json else request.form.get('id')
    if not nid:
        return jsonify({'success': False, 'message': 'Missing id'}), 400
    Notification.mark_read(nid, user_id)
    return jsonify({'success': True})

@user_bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    user_id = session.get('user_id')
    role = session.get('user_role') or session.get('role') or 'user'
    Notification.mark_all_read(user_id, role)
    return jsonify({'success': True})

@user_bp.route('/cart')
@login_required
def view_cart():
    """View shopping cart"""
    user_id = session['user_id']
    cart_items = Cart.get_user_cart(user_id)
    cart_total = Cart.get_cart_total(user_id)
    
    return render_template('user/cart.html',
                         cart_items=cart_items,
                         cart_total=cart_total,
                         subtotal=cart_total['subtotal'],
                         shipping_fee=sum(cart_total['shipping_fees'].values()) if cart_total['shipping_fees'] else 0,
                         total=cart_total['total'])

@user_bp.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    """Add product to cart"""
    form = CartAddForm()
    if form.validate_on_submit():
        user_id = session['user_id']
        product_id = form.product_id.data
        quantity = form.quantity.data
        variant_id = form.variant_id.data if form.variant_id.data else None
        
        try:
            Cart.add_item(user_id, product_id, quantity, variant_id)
            flash('Item added to cart!', 'success')
        except Exception as e:
            flash('Failed to add item to cart.', 'error')
    else:
        flash('Invalid form data.', 'error')
    
    return redirect(request.referrer or url_for('public.browse_products'))

@user_bp.route('/cart/update', methods=['POST'])
@login_required
def update_cart():
    """Update cart item quantity"""
    form = CartUpdateForm()
    if form.validate_on_submit():
        cart_id = form.cart_id.data
        quantity = form.quantity.data
        user_id = session['user_id']
        
        try:
            # Ensure item belongs to current user.
            cart_items = Cart.get_user_cart(user_id) or []
            cart_item = next((item for item in cart_items if item['id'] == cart_id), None)
            if not cart_item:
                flash('Cart item not found.', 'error')
                return redirect(url_for('user.view_cart'))

            # Validate requested quantity against available stock.
            product = Product.get_by_id(cart_item['product_id'])
            if quantity > 0 and (not product or int(product.get('stock_quantity') or 0) < quantity):
                available = int(product.get('stock_quantity') or 0) if product else 0
                flash(f'Only {available} item(s) available for this product.', 'error')
                return redirect(url_for('user.view_cart'))

            Cart.update_item(cart_id, quantity)
            if quantity > 0:
                flash('Cart updated!', 'success')
            else:
                flash('Item removed from cart!', 'info')
        except Exception as e:
            flash('Failed to update cart.', 'error')
    else:
        flash('Invalid form data.', 'error')
    
    return redirect(url_for('user.view_cart'))

@user_bp.route('/cart/remove/<int:cart_id>')
@login_required
def remove_from_cart(cart_id):
    """Remove item from cart"""
    try:
        Cart.remove_item_by_id(cart_id)
        flash('Item removed from cart!', 'info')
    except Exception as e:
        flash('Failed to remove item.', 'error')
    
    return redirect(url_for('user.view_cart'))

@user_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout process"""
    user_id = session['user_id']
    user = User.get_by_id(user_id)
    
    # Check if cart is empty
    cart_items = Cart.get_user_cart(user_id)
    if not cart_items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('user.view_cart'))
    
    form = CheckoutForm()
    if form.validate_on_submit():
        shipping_address = (form.shipping_address.data or '').strip()
        if not shipping_address:
            # Try to compose from submitted structured fields first
            sf_parts = []
            if hasattr(form, 'house_number') and (form.house_number.data or form.street.data):
                sf_parts.append(((form.house_number.data or '') + (' ' + form.street.data if form.street.data else '')).strip())
            if hasattr(form, 'barangay') and form.barangay.data:
                sf_parts.append('Barangay ' + form.barangay.data)
            if hasattr(form, 'city') and form.city.data:
                sf_parts.append(form.city.data)
            if hasattr(form, 'province') and form.province.data:
                sf_parts.append(form.province.data)
            if hasattr(form, 'postal_code') and form.postal_code.data:
                sf_parts.append(form.postal_code.data)
            if user.get('country'):
                sf_parts.append(user['country'])
            composed = ', '.join([p for p in sf_parts if p])
            if composed:
                shipping_address = composed

        if not shipping_address:
            # Compose from saved structured address as fallback
            parts = []
            if user.get('house_number') or user.get('street'):
                parts.append(((user.get('house_number') or '') + (' ' + user.get('street') if user.get('street') else '')).strip())
            if user.get('barangay'):
                parts.append('Barangay ' + user['barangay'])
            if user.get('city'):
                parts.append(user['city'])
            if user.get('province'):
                parts.append(user['province'])
            if user.get('postal_code'):
                parts.append(user['postal_code'])
            if user.get('country'):
                parts.append(user['country'])
            shipping_address = ', '.join([p for p in parts if p]) or (user.get('address') or '')
        payment_method = form.payment_method.data
        notes = form.notes.data.strip() if form.notes.data else None
        
        # Create orders
        try:
            order_ids = Order.create_from_cart(user_id, shipping_address, payment_method, notes)
            if order_ids:
                flash(f'Order(s) placed successfully! Order IDs: {", ".join(map(str, order_ids))}', 'success')
                return redirect(url_for('user.orders'))
            else:
                flash('Failed to place order. Please try again.', 'error')
        except Exception as e:
            flash('An error occurred while placing your order.', 'error')
    elif request.method == 'POST':
        flash('Please correct the errors in the form.', 'error')
    
    cart_total = Cart.get_cart_total(user_id, include_shipping=True)
    total_quantity = sum(item.get('quantity', 0) for item in cart_items)
    return render_template('user/checkout.html',
                         cart_items=cart_items,
                         user=user,
                         cart_total=cart_total,
                         total_quantity=total_quantity,
                         subtotal=cart_total['subtotal'],
                         shipping_fee=sum(cart_total['shipping_fees'].values()) if cart_total['shipping_fees'] else 0,
                         total=cart_total['total'])

@user_bp.route('/orders')
@login_required
def orders():
    """View user orders"""
    user_id = session['user_id']
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    
    user_orders = Order.list_for_user(user_id, limit=per_page, offset=offset)
    
    return render_template('customer/orders.html',
                         orders=user_orders)

@user_bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    """View order details"""
    user_id = session['user_id']
    order = Order.get_by_id(order_id)
    
    # Check if order belongs to current user
    if not order or order['user_id'] != user_id:
        flash('Order not found.', 'error')
        return redirect(url_for('user.orders'))
    
    return render_template('user/order_detail.html', order=order)

@user_bp.route('/api/order/<int:order_id>/rider-location')
@login_required
def get_rider_location(order_id):
    """Get current rider location for an order"""
    user_id = session['user_id']
    order = Order.get_by_id(order_id)
    
    # Check if order belongs to current user
    if not order or order['user_id'] != user_id:
        return jsonify({'success': False, 'message': 'Order not found'}), 404
    
    # Check if order is out for delivery
    if order.get('status') not in ['shipped', 'on_the_way', 'picked_up']:
        return jsonify({
            'success': False,
            'message': 'Order is not out for delivery yet',
            'status': order.get('status')
        }), 400
    
    # Check if order has a rider assigned
    if not order.get('rider_id'):
        return jsonify({'success': False, 'message': 'No rider assigned yet'}), 404
    
    try:
        import json
        from app.services.database import Database
        db = Database()
        
        # Get rider's current location from rider_availability table
        rider_location = db.execute_query("""
            SELECT 
                rider_id,
                current_location,
                last_seen,
                is_online
            FROM rider_availability
            WHERE rider_id = %s
        """, (order['rider_id'],), fetchone=True)
        
        # Default location (Manila, Philippines)
        latitude = 14.5995
        longitude = 120.9842
        is_online = False
        
        if rider_location:
            # Parse location from JSON string
            is_online = bool(rider_location.get('is_online', False))
            current_location = rider_location.get('current_location')
            
            if current_location:
                try:
                    location_data = json.loads(current_location)
                    if isinstance(location_data, dict):
                        if 'latitude' in location_data and 'longitude' in location_data:
                            latitude = float(location_data['latitude'])
                            longitude = float(location_data['longitude'])
                except (json.JSONDecodeError, ValueError, TypeError):
                    # Use default location if parsing fails
                    pass
        
        # Get rider information
        from app.models.user import User
        rider = User.get_by_id(order['rider_id'])
        rider_name = 'Unknown Rider'
        rider_phone = 'N/A'
        
        if rider:
            first_name = rider.get('first_name', 'Unknown') if isinstance(rider, dict) else getattr(rider, 'first_name', 'Unknown')
            last_name = rider.get('last_name', 'Rider') if isinstance(rider, dict) else getattr(rider, 'last_name', 'Rider')
            rider_name = f"{first_name} {last_name}".strip()
            rider_phone = rider.get('phone', 'N/A') if isinstance(rider, dict) else getattr(rider, 'phone', 'N/A')
        
        # Get delivery info if exists
        delivery = db.execute_query("""
            SELECT 
                id,
                status,
                picked_up_at,
                delivered_at
            FROM deliveries
            WHERE order_id = %s
            LIMIT 1
        """, (order_id,), fetchone=True)
        
        # Build response
        return jsonify({
            'success': True,
            'rider': {
                'id': order.get('rider_id'),
                'name': rider_name,
                'phone': rider_phone,
                'is_online': is_online
            },
            'location': {
                'latitude': latitude,
                'longitude': longitude
            },
            'delivery': {
                'status': delivery.get('status') if delivery else 'assigned',
                'picked_up_at': delivery.get('picked_up_at').isoformat() if (delivery and delivery.get('picked_up_at')) else None,
                'delivered_at': delivery.get('delivered_at').isoformat() if (delivery and delivery.get('delivered_at')) else None
            },
            'order': {
                'shipping_address': order.get('shipping_address', ''),
                'status': order.get('status')
            }
        })
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback_str = traceback.format_exc()
        current_app.logger.error(f"Error fetching rider location for order {order_id}: {error_msg}\n{traceback_str}")
        return jsonify({
            'success': False, 
            'message': 'Failed to fetch rider location',
            'error': error_msg
        }), 500

@user_bp.route('/review/add', methods=['POST'])
@login_required
def add_review():
    """Add a product review"""
    form = ReviewForm()
    if form.validate_on_submit():
        user_id = session['user_id']
        product_id = int(form.product_id.data)
        rating = int(form.rating.data)
        comment = form.comment.data.strip() if form.comment.data else None
        
        try:
            Review.create(user_id, product_id, rating, comment)
            flash('Review added successfully!', 'success')
        except Exception as e:
            flash('Failed to add review.', 'error')
        
        return redirect(request.referrer or url_for('public.product_detail', product_id=product_id))
    else:
        flash('Invalid review data.', 'error')
        return redirect(request.referrer or url_for('public.browse_products'))

@user_bp.route('/become-seller', methods=['GET', 'POST'])
@login_required
def become_seller():
    """Legacy seller application route.

    New seller registrations are now handled during account signup.
    This route is kept only to view existing request status for old users.
    """
    user_id = session['user_id']

    existing_request = SellerRequest.get_by_user_id(user_id)
    if existing_request:
        return render_template('user/seller_request_status.html', request=existing_request)

    flash('New seller registrations are now handled during account signup. Please create a new account and choose "Seller" during signup.', 'info')
    return redirect(url_for('public.browse_products'))

@user_bp.route('/seller-request-status')
@login_required
def seller_request_status():
    """Check seller request status"""
    user_id = session['user_id']
    seller_request = SellerRequest.get_by_user_id(user_id)
    
    if not seller_request:
        flash('No seller request found.', 'info')
        return redirect(url_for('user.become_seller'))
    
    return render_template('user/seller_request_status.html', request=seller_request)

@user_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User account settings"""
    user_id = session['user_id']
    user = User.get_by_id(user_id)
    
    profile_form = ProfileUpdateForm()
    password_form = ChangePasswordForm()
    
    if profile_form.validate_on_submit():
        # Check if username/email already exists (excluding current user)
        if profile_form.username.data != user['username']:
            existing_user = User.get_by_username(profile_form.username.data)
            if existing_user and existing_user['id'] != user_id:
                flash('Username already taken.', 'error')
                return render_template('user/settings.html', user=user, profile_form=profile_form, password_form=password_form)
        
        if profile_form.email.data != user['email']:
            existing_email = User.get_by_email(profile_form.email.data)
            if existing_email and existing_email['id'] != user_id:
                flash('Email already in use.', 'error')
                return render_template('user/settings.html', user=user, profile_form=profile_form, password_form=password_form)
        
        # Handle profile image upload
        profile_image_path = user.get('profile_image', None)
        if profile_form.profile_image.data:
            from PIL import Image
            import uuid

            # Generate unique filename
            file_ext = os.path.splitext(profile_form.profile_image.data.filename)[1].lower()
            if file_ext not in ['.jpg', '.jpeg', '.png', '.gif']:
                file_ext = '.jpg'  # Default to jpg if unknown extension
            unique_filename = f"{uuid.uuid4().hex}_{user_id}{file_ext}"
            upload_path = os.path.join('static', 'uploads', 'profiles', unique_filename)
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)

            try:
                # Open and process the image
                image = Image.open(profile_form.profile_image.data)

                # Convert to RGB if necessary (for PNG with transparency)
                if image.mode in ('RGBA', 'LA', 'P'):
                    image = image.convert('RGB')

                # Resize to a reasonable size (max 400x400 for profile images, maintain aspect ratio)
                max_size = (400, 400)
                image.thumbnail(max_size, Image.Resampling.LANCZOS)

                # Save as JPEG with good quality
                image.save(upload_path, 'JPEG', quality=85, optimize=True)
                profile_image_path = f"uploads/profiles/{unique_filename}"

            except Exception as e:
                # Fallback to original upload if processing fails
                filename = secure_filename(profile_form.profile_image.data.filename)
                if filename:
                    fallback_filename = f"{uuid.uuid4().hex}_{filename}"
                    fallback_path = os.path.join('static', 'uploads', 'profiles', fallback_filename)
                    profile_form.profile_image.data.save(fallback_path)
                    profile_image_path = f"uploads/profiles/{fallback_filename}"
        
        # Update profile
        try:
            User.update(user_id,
                      username=profile_form.username.data,
                      email=profile_form.email.data,
                      first_name=profile_form.first_name.data,
                      last_name=profile_form.last_name.data,
                      phone=profile_form.phone.data,
                      address=profile_form.address.data,
                      country=profile_form.country.data if hasattr(profile_form, 'country') else None,
                      city=profile_form.city.data if hasattr(profile_form, 'city') else None,
                      province=profile_form.province.data if hasattr(profile_form, 'province') else None,
                      house_number=profile_form.house_number.data if hasattr(profile_form, 'house_number') else None,
                      street=profile_form.street.data if hasattr(profile_form, 'street') else None,
                      barangay=profile_form.barangay.data if hasattr(profile_form, 'barangay') else None,
                      postal_code=profile_form.postal_code.data if hasattr(profile_form, 'postal_code') else None,
                      profile_image=profile_image_path)
            flash('Profile updated successfully!', 'success')
            user = User.get_by_id(user_id)  # Refresh user data
        except Exception as e:
            flash('Failed to update profile.', 'error')
    
    if password_form.validate_on_submit():
        # Validate current password
        if not User.authenticate(user['email'], password_form.current_password.data):
            flash('Current password is incorrect.', 'error')
            return render_template('user/settings.html', user=user, profile_form=profile_form, password_form=password_form)
        
        # Update password
        try:
            User.update_password(user_id, password_form.new_password.data)
            flash('Password changed successfully!', 'success')
        except Exception as e:
            flash('Failed to change password.', 'error')
    
    return render_template('user/settings.html', user=user, profile_form=profile_form, password_form=password_form)
