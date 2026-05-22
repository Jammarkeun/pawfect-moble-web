from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.models.return_request import ReturnRequest
from app.models.order import Order
from app.models.user import User
from app.utils.decorators import login_required, seller_required, admin_required
from app.services.database import Database

return_bp = Blueprint('returns', __name__)

@return_bp.route('/request/<int:order_id>', methods=['GET', 'POST'])
@login_required
def request_return(order_id):
    """Create a return/refund request"""
    user_id = session['user_id']
    order = Order.get_by_id(order_id)
    
    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('user.orders'))
    
    # Verify order belongs to user
    if order['user_id'] != user_id:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('user.orders'))
    
    # Check if order is eligible for return (delivered status)
    if order['status'] not in ['delivered']:
        flash('Only delivered orders can be returned.', 'error')
        return redirect(url_for('user.order_detail', order_id=order_id))
    
    if request.method == 'POST':
        order_item_id = request.form.get('order_item_id')
        reason = request.form.get('reason')
        description = request.form.get('description', '').strip()
        
        if not order_item_id or not reason:
            flash('Please select an item and provide a reason.', 'error')
            return redirect(request.url)
        
        # Check if return request already exists for this item
        db = Database()
        existing = db.execute_query("""
            SELECT id FROM return_requests 
            WHERE order_item_id = %s AND status NOT IN ('rejected', 'cancelled')
        """, (order_item_id,), fetch=True, fetchone=True)
        
        if existing:
            flash('A return request already exists for this item.', 'error')
            return redirect(url_for('user.order_detail', order_id=order_id))
        
        # Create return request
        return_req = ReturnRequest.create(
            order_id=order_id,
            order_item_id=order_item_id,
            user_id=user_id,
            reason=reason,
            description=description if description else None
        )
        
        if return_req:
            flash('Return request submitted successfully!', 'success')
            return redirect(url_for('returns.my_returns'))
        else:
            flash('Failed to submit return request.', 'error')
    
    return render_template('user/request_return.html', order=order)

@return_bp.route('/my-returns')
@login_required
def my_returns():
    """View user's return requests"""
    user_id = session['user_id']
    status_filter = request.args.get('status')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    
    returns = ReturnRequest.get_by_user(
        user_id, 
        status=status_filter,
        limit=per_page,
        offset=offset
    )
    
    total = ReturnRequest.count(user_id=user_id, status=status_filter)
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('user/my_returns.html',
                         returns=returns,
                         current_status=status_filter,
                         page=page,
                         total_pages=total_pages,
                         has_prev=page > 1,
                         has_next=page < total_pages)

@return_bp.route('/detail/<int:return_id>')
@login_required
def return_detail(return_id):
    """View return request details"""
    user_id = session['user_id']
    user = User.get_by_id(user_id)
    return_req = ReturnRequest.get_by_id(return_id)
    
    if not return_req:
        flash('Return request not found.', 'error')
        return redirect(url_for('public.browse_products'))
    
    # Check permissions
    is_admin = user['role'] == 'admin'
    is_seller = user['role'] == 'seller'
    is_owner = return_req['user_id'] == user_id
    
    # Get seller_id from order
    db = Database()
    order = db.execute_query(
        "SELECT seller_id FROM orders WHERE id = %s",
        (return_req['order_id'],),
        fetch=True,
        fetchone=True
    )
    
    is_order_seller = order and order['seller_id'] == user_id
    
    if not (is_owner or is_admin or is_order_seller):
        flash('Unauthorized access.', 'error')
        return redirect(url_for('public.browse_products'))
    
    return render_template('user/return_detail.html', return_req=return_req)

@return_bp.route('/seller/returns')
@login_required
@seller_required
def seller_returns():
    """View return requests for seller's products"""
    seller_id = session['user_id']
    status_filter = request.args.get('status')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    
    returns = ReturnRequest.get_by_seller(
        seller_id,
        status=status_filter,
        limit=per_page,
        offset=offset
    )
    
    total = ReturnRequest.count(seller_id=seller_id, status=status_filter)
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('seller/returns.html',
                         returns=returns,
                         current_status=status_filter,
                         page=page,
                         total_pages=total_pages,
                         has_prev=page > 1,
                         has_next=page < total_pages)

@return_bp.route('/admin/returns')
@login_required
@admin_required
def admin_returns():
    """View all return requests (admin)"""
    status_filter = request.args.get('status')
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page
    
    returns = ReturnRequest.get_all(
        status=status_filter,
        limit=per_page,
        offset=offset
    )
    
    total = ReturnRequest.count(status=status_filter)
    total_pages = (total + per_page - 1) // per_page
    
    # Get statistics
    db = Database()
    stats = db.execute_query("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
            SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected,
            SUM(CASE WHEN status = 'approved' THEN refund_amount ELSE 0 END) as total_refunded
        FROM return_requests
    """, fetch=True, fetchone=True)
    
    return render_template('admin/returns.html',
                         returns=returns,
                         stats=stats,
                         current_status=status_filter,
                         page=page,
                         total_pages=total_pages,
                         has_prev=page > 1,
                         has_next=page < total_pages)

@return_bp.route('/update-status/<int:return_id>', methods=['POST'])
@login_required
def update_return_status(return_id):
    """Update return request status"""
    user_id = session['user_id']
    user = User.get_by_id(user_id)
    return_req = ReturnRequest.get_by_id(return_id)
    
    if not return_req:
        return jsonify({'error': 'Return request not found'}), 404
    
    # Check permissions (admin or seller)
    is_admin = user['role'] == 'admin'
    
    db = Database()
    order = db.execute_query(
        "SELECT seller_id FROM orders WHERE id = %s",
        (return_req['order_id'],),
        fetch=True,
        fetchone=True
    )
    
    is_seller = order and order['seller_id'] == user_id
    
    if not (is_admin or is_seller):
        return jsonify({'error': 'Unauthorized'}), 403
    
    status = request.form.get('status')
    admin_notes = request.form.get('admin_notes', '').strip()
    refund_amount = request.form.get('refund_amount')
    
    if status not in ['pending', 'approved', 'rejected', 'processing']:
        return jsonify({'error': 'Invalid status'}), 400
    
    # Sellers can only approve/reject, admins can do everything
    if is_seller and not is_admin and status not in ['approved', 'rejected']:
        return jsonify({'error': 'Unauthorized status change'}), 403
    
    try:
        refund_amt = float(refund_amount) if refund_amount else None
    except ValueError:
        refund_amt = None
    
    updated = ReturnRequest.update_status(
        return_id,
        status,
        admin_notes if admin_notes else None,
        refund_amt
    )
    
    if updated:
        flash(f'Return request {status} successfully!', 'success')
        return jsonify({'success': True, 'message': f'Return request {status}'})
    else:
        return jsonify({'error': 'Failed to update status'}), 500

@return_bp.route('/cancel/<int:return_id>', methods=['POST'])
@login_required
def cancel_return(return_id):
    """Cancel a return request (user only, if pending)"""
    user_id = session['user_id']
    return_req = ReturnRequest.get_by_id(return_id)
    
    if not return_req:
        flash('Return request not found.', 'error')
        return redirect(url_for('returns.my_returns'))
    
    # Only owner can cancel
    if return_req['user_id'] != user_id:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('returns.my_returns'))
    
    # Can only cancel if pending
    if return_req['status'] != 'pending':
        flash('Can only cancel pending requests.', 'error')
        return redirect(url_for('returns.return_detail', return_id=return_id))
    
    ReturnRequest.update_status(return_id, 'cancelled')
    flash('Return request cancelled.', 'success')
    return redirect(url_for('returns.my_returns'))
