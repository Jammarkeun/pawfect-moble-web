from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.models.inventory import Wishlist
from app.models.product import Product
from app.utils.decorators import login_required

wishlist_bp = Blueprint('wishlist', __name__)

@wishlist_bp.route('/')
@login_required
def index():
    """View user's wishlist"""
    user_id = session['user_id']
    wishlist_items = Wishlist.get_user_wishlist(user_id)
    return render_template('user/wishlist.html', wishlist_items=wishlist_items)

@wishlist_bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_wishlist(product_id):
    """Add product to wishlist"""
    user_id = session['user_id']
    
    # Check if product exists
    product = Product.get_by_id(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Add to wishlist
    wishlist_id = Wishlist.add_to_wishlist(user_id, product_id)
    
    if wishlist_id:
        flash('Added to wishlist!', 'success')
        return jsonify({'success': True, 'message': 'Added to wishlist'})
    else:
        flash('Item already in wishlist', 'info')
        return jsonify({'error': 'Already in wishlist'}), 400

@wishlist_bp.route('/remove/<int:product_id>', methods=['POST'])
@login_required
def remove_from_wishlist(product_id):
    """Remove product from wishlist"""
    user_id = session['user_id']
    Wishlist.remove_from_wishlist(user_id, product_id)
    flash('Removed from wishlist', 'success')
    
    if request.is_json:
        return jsonify({'success': True, 'message': 'Removed from wishlist'})
    return redirect(url_for('wishlist.index'))

@wishlist_bp.route('/move-to-cart/<int:product_id>', methods=['POST'])
@login_required
def move_to_cart(product_id):
    """Move wishlist item to cart"""
    user_id = session['user_id']
    
    try:
        Wishlist.move_to_cart(user_id, product_id)
        flash('Moved to cart!', 'success')
        return jsonify({'success': True, 'message': 'Moved to cart'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wishlist_bp.route('/update-notes/<int:product_id>', methods=['POST'])
@login_required
def update_notes(product_id):
    """Update wishlist item notes"""
    user_id = session['user_id']
    notes = request.form.get('notes', '').strip()
    
    Wishlist.update_notes(user_id, product_id, notes)
    return jsonify({'success': True, 'message': 'Notes updated'})

@wishlist_bp.route('/update-priority/<int:product_id>', methods=['POST'])
@login_required
def update_priority(product_id):
    """Update wishlist item priority"""
    user_id = session['user_id']
    priority = request.form.get('priority', 'medium')
    
    if priority not in ['low', 'medium', 'high']:
        return jsonify({'error': 'Invalid priority'}), 400
    
    Wishlist.update_priority(user_id, product_id, priority)
    return jsonify({'success': True, 'message': 'Priority updated'})

@wishlist_bp.route('/toggle-notification/<int:product_id>', methods=['POST'])
@login_required
def toggle_notification(product_id):
    """Toggle back-in-stock notification"""
    user_id = session['user_id']
    Wishlist.toggle_notification(user_id, product_id)
    return jsonify({'success': True, 'message': 'Notification preference updated'})

@wishlist_bp.route('/count')
@login_required
def get_count():
    """Get wishlist count (for navbar badge)"""
    user_id = session['user_id']
    count = Wishlist.get_count(user_id)
    return jsonify({'success': True, 'count': count})
