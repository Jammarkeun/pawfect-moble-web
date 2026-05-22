from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import and_, or_, func, desc
from app import db
from app.models.models import (User, Product, Order, OrderItem, SellerApplication, 
                               Review, Category, Notification, SystemLog, PayoutRequest, RiderEarning)
from app.utils.auth import role_required, get_current_user
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@role_required('admin')
def dashboard():
    """Admin dashboard with system overview"""
    # Get system statistics
    total_users = User.query.count()
    total_customers = User.query.filter_by(role='customer').count()
    total_sellers = User.query.filter_by(role='seller').count()
    total_riders = User.query.filter_by(role='rider').count()
    
    total_products = Product.query.count()
    active_products = Product.query.filter_by(status='active').count()
    
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    
    # Pending seller applications
    pending_applications = SellerApplication.query.filter_by(status='pending').count()
    
    # Recent activities
    recent_orders = Order.query.order_by(desc(Order.created_at)).limit(5).all()
    recent_users = User.query.filter(User.role != 'admin').order_by(desc(User.created_at)).limit(5).all()
    recent_reviews = Review.query.filter_by(status='pending').order_by(desc(Review.created_at)).limit(5).all()
    
    # Sales analytics (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    monthly_sales = db.session.query(func.sum(Order.total_amount)).filter(
        Order.created_at >= thirty_days_ago,
        Order.status != 'cancelled'
    ).scalar() or 0
    
    # Recent seller requests
    recent_requests = SellerApplication.query.order_by(desc(SellerApplication.created_at)).limit(5).all()
    
    # Create stats dictionary
    stats = {
        'total_users': total_users,
        'total_sellers': total_sellers,
        'pending_requests': pending_applications,
        'total_orders': total_orders,
        'pending_orders': pending_orders
    }
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_requests=recent_requests,
                         recent_users=recent_users)

@admin_bp.route('/seller-applications')
@role_required('admin')
def seller_applications():
    """View and manage seller applications"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = SellerApplication.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    applications = query.order_by(desc(SellerApplication.created_at)).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('admin/seller_applications.html',
                         applications=applications.items,
                         pagination=applications,
                         status_filter=status_filter)

@admin_bp.route('/approve-seller/<int:application_id>', methods=['POST'])
@role_required('admin')
def approve_seller(application_id):
    """Approve a seller application"""
    admin = get_current_user()
    application = SellerApplication.query.get_or_404(application_id)
    
    try:
        # Update application status
        application.status = 'approved'
        application.reviewed_by = admin.id
        application.reviewed_at = datetime.now()
        
        # Update user role to seller
        user = User.query.get(application.user_id)
        user.role = 'seller'
        
        # Create notification for user
        notification = Notification(
            user_id=user['id'],
            type='seller_application',
            title='Seller Application Approved',
            message='Congratulations! Your seller application has been approved. You can now start selling on Pawfect Finds.',
            related_id=application.id
        )
        
        db.session.add(notification)
        db.session.commit()
        
        flash('Seller application approved successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Failed to approve seller application.', 'error')
    
    return redirect(url_for('admin.seller_applications'))

@admin_bp.route('/reject-seller/<int:application_id>', methods=['POST'])
@role_required('admin')
def reject_seller(application_id):
    """Reject a seller application"""
    admin = get_current_user()
    application = SellerApplication.query.get_or_404(application_id)
    admin_notes = request.form.get('admin_notes', '')
    
    try:
        # Update application status
        application.status = 'rejected'
        application.reviewed_by = admin.id
        application.reviewed_at = datetime.now()
        application.admin_notes = admin_notes
        
        # Create notification for user
        notification = Notification(
            user_id=application.user_id,
            type='seller_application',
            title='Seller Application Rejected',
            message=f'Your seller application has been rejected. {admin_notes if admin_notes else "Please contact support for more information."}',
            related_id=application.id
        )
        
        db.session.add(notification)
        db.session.commit()
        
        flash('Seller application rejected.', 'info')
        
    except Exception as e:
        db.session.rollback()
        flash('Failed to reject seller application.', 'error')
    
    return redirect(url_for('admin.seller_applications'))

@admin_bp.route('/users')
@role_required('admin')
def users():
    """Manage all users"""
    page = request.args.get('page', 1, type=int)
    role_filter = request.args.get('role', '')
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')
    
    query = User.query.filter(User.role != 'admin')
    
    if role_filter:
        query = query.filter_by(role=role_filter)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if search:
        query = query.filter(
            or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%')
            )
        )
    
    users_paginated = query.order_by(desc(User.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html',
                         users=users_paginated.items,
                         pagination=users_paginated,
                         role_filter=role_filter,
                         status_filter=status_filter,
                         search=search)

@admin_bp.route('/user/<int:user_id>')
@role_required('admin')
def user_detail(user_id):
    """View user details"""
    user = User.query.get_or_404(user_id)
    
    # Get user statistics
    if user.role == 'customer':
        order_count = Order.query.filter_by(user_id=user['id']).count()
        total_spent = db.session.query(func.sum(Order.total_amount)).filter_by(user_id=user['id']).scalar() or 0
        stats = {'orders': order_count, 'total_spent': total_spent}
    elif user.role == 'seller':
        product_count = Product.query.filter_by(seller_id=user['id']).count()
        total_sales = db.session.query(func.sum(OrderItem.total_price)).filter_by(seller_id=user['id']).scalar() or 0
        stats = {'products': product_count, 'total_sales': total_sales}
    else:
        stats = {}
    
    return render_template('admin/user_detail.html', user=user, stats=stats)

@admin_bp.route('/update-user-status', methods=['POST'])
@role_required('admin')
def update_user_status():
    """Update user status"""
    user_id = request.form.get('user_id', type=int)
    new_status = request.form.get('status')
    
    if not user_id or not new_status:
        flash('Invalid data provided.', 'error')
        return redirect(request.referrer)
    
    user = User.query.get_or_404(user_id)
    
    if user.role == 'admin':
        flash('Cannot modify admin user status.', 'error')
        return redirect(request.referrer)
    
    try:
        user.status = new_status
        db.session.commit()
        
        flash(f'User status updated to {new_status}.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Failed to update user status.', 'error')
    
    return redirect(request.referrer)

@admin_bp.route('/products')
@role_required('admin')
def products():
    """Manage all products"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')
    
    query = Product.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f'%{search}%'),
                Product.description.ilike(f'%{search}%'),
                Product.sku.ilike(f'%{search}%')
            )
        )
    
    products_paginated = query.order_by(desc(Product.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/products.html',
                         products=products_paginated.items,
                         pagination=products_paginated,
                         status_filter=status_filter,
                         search=search)

@admin_bp.route('/orders')
@role_required('admin')
def orders():
    """View all orders"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Order.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    orders_paginated = query.order_by(desc(Order.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/orders.html',
                         orders=orders_paginated.items,
                         pagination=orders_paginated,
                         status_filter=status_filter)

@admin_bp.route('/reviews')
@role_required('admin')
def reviews():
    """Moderate product reviews"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'pending')
    
    query = Review.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    reviews_paginated = query.order_by(desc(Review.created_at)).paginate(
        page=page, per_page=15, error_out=False
    )
    
    return render_template('admin/reviews.html',
                         reviews=reviews_paginated.items,
                         pagination=reviews_paginated,
                         status_filter=status_filter)

@admin_bp.route('/approve-review/<int:review_id>', methods=['POST'])
@role_required('admin')
def approve_review(review_id):
    """Approve a product review"""
    review = Review.query.get_or_404(review_id)
    
    try:
        review.status = 'approved'
        db.session.commit()
        flash('Review approved successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Failed to approve review.', 'error')
    
    return redirect(url_for('admin.reviews'))

@admin_bp.route('/reject-review/<int:review_id>', methods=['POST'])
@role_required('admin')
def reject_review(review_id):
    """Reject a product review"""
    review = Review.query.get_or_404(review_id)
    
    try:
        review.status = 'rejected'
        db.session.commit()
        flash('Review rejected.', 'info')
        
    except Exception as e:
        db.session.rollback()
        flash('Failed to reject review.', 'error')
    
    return redirect(url_for('admin.reviews'))

@admin_bp.route('/analytics')
@role_required('admin')
def analytics():
    """System analytics and reporting"""
    days = request.args.get('days', 30, type=int)
    start_date = datetime.now() - timedelta(days=days)
    
    # Sales analytics
    sales_data = db.session.query(
        func.date(Order.created_at).label('date'),
        func.sum(Order.total_amount).label('total_sales'),
        func.count(Order.id).label('order_count')
    ).filter(
        Order.created_at >= start_date,
        Order.status != 'cancelled'
    ).group_by(func.date(Order.created_at)).all()
    
    # Top selling products
    top_products = db.session.query(
        Product.name,
        func.sum(OrderItem.quantity).label('total_sold'),
        func.sum(OrderItem.total_price).label('total_revenue')
    ).join(OrderItem).filter(
        OrderItem.created_at >= start_date
    ).group_by(Product.id, Product.name).order_by(
        func.sum(OrderItem.total_price).desc()
    ).limit(10).all()
    
    # User registration trends
    user_data = db.session.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('new_users')
    ).filter(
        User.created_at >= start_date,
        User.role != 'admin'
    ).group_by(func.date(User.created_at)).all()
    
    return render_template('admin/analytics.html',
                         sales_data=sales_data,
                         top_products=top_products,
                         user_data=user_data,
                         days=days)

@admin_bp.route('/dashboard/stats')
@role_required('admin')
def dashboard_stats():
    """API endpoint for dashboard chart data"""
    days = request.args.get('days', 30, type=int)
    start_date = datetime.now() - timedelta(days=days)
    
    # Revenue data over time (last 30 days)
    revenue_data = []
    for i in range(days-1, -1, -1):
        date = datetime.now() - timedelta(days=i)
        daily_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            func.date(Order.created_at) == date.date(),
            Order.status != 'cancelled'
        ).scalar() or 0
        revenue_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'revenue': float(daily_revenue)
        })
    
    # Order status distribution
    order_status_counts = db.session.query(
        Order.status,
        func.count(Order.id).label('count')
    ).group_by(Order.status).all()
    
    status_distribution = [{'status': status, 'count': count} for status, count in order_status_counts]
    
    # User registration over time (last 30 days)
    user_registration_data = []
    for i in range(days-1, -1, -1):
        date = datetime.now() - timedelta(days=i)
        daily_users = db.session.query(func.count(User.id)).filter(
            func.date(User.created_at) == date.date(),
            User.role != 'admin'
        ).scalar() or 0
        user_registration_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'users': daily_users
        })
    
    # Top selling products (last 30 days)
    top_products = db.session.query(
        Product.name,
        func.sum(OrderItem.quantity).label('quantity')
    ).join(OrderItem).join(Order).filter(
        Order.created_at >= start_date,
        Order.status != 'cancelled'
    ).group_by(Product.id, Product.name).order_by(
        func.sum(OrderItem.quantity).desc()
    ).limit(5).all()
    
    top_products_data = [{'name': name, 'quantity': int(quantity)} for name, quantity in top_products]
    
    return jsonify({
        'revenue': revenue_data,
        'orderStatus': status_distribution,
        'userRegistration': user_registration_data,
        'topProducts': top_products_data
    })

# Route aliases for template compatibility
@admin_bp.route('/manage-users')
@role_required('admin')
def manage_users():
    """Alias for users()"""
    return users()

@admin_bp.route('/seller-requests')
@role_required('admin')
def seller_requests():
    """Alias for seller_applications()"""
    return seller_applications()

@admin_bp.route('/rider-requests')
@role_required('admin')
def rider_requests():
    """Rider applications management"""
    # Get pending rider applications
    applications = db.session.query(SellerApplication).filter_by(status='pending').all()
    
    return render_template('admin/rider_requests.html', applications=applications)

@admin_bp.route('/manage-products')
@role_required('admin')
def manage_products():
    """Alias for products()"""
    return products()

@admin_bp.route('/manage-orders')
@role_required('admin')
def manage_orders():
    """Alias for orders()"""
    return orders()

@admin_bp.route('/audit-logs')
@role_required('admin')
def audit_logs():
    """System audit logs"""
    logs = SystemLog.query.order_by(desc(SystemLog.timestamp)).paginate(per_page=50)
    return render_template('admin/audit_logs.html', logs=logs)


# ============================================================================
# RIDER PAYOUT MANAGEMENT
# ============================================================================

@admin_bp.route('/payouts')
@role_required('admin')
def payouts():
    """Manage rider payout requests"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = PayoutRequest.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    payouts_paginated = query.order_by(desc(PayoutRequest.requested_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get statistics
    pending_count = PayoutRequest.query.filter_by(status='pending').count()
    pending_amount = db.session.query(func.sum(PayoutRequest.amount)).filter_by(
        status='pending'
    ).scalar() or 0
    
    approved_count = PayoutRequest.query.filter_by(status='approved').count()
    approved_amount = db.session.query(func.sum(PayoutRequest.amount)).filter_by(
        status='approved'
    ).scalar() or 0
    
    paid_count = PayoutRequest.query.filter_by(status='paid').count()
    paid_amount = db.session.query(func.sum(PayoutRequest.amount)).filter_by(
        status='paid'
    ).scalar() or 0
    
    stats = {
        'pending_count': pending_count,
        'pending_amount': float(pending_amount) if pending_amount else 0,
        'approved_count': approved_count,
        'approved_amount': float(approved_amount) if approved_amount else 0,
        'paid_count': paid_count,
        'paid_amount': float(paid_amount) if paid_amount else 0,
    }
    
    return render_template('admin/payouts.html',
                         payouts=payouts_paginated.items,
                         pagination=payouts_paginated,
                         status_filter=status_filter,
                         stats=stats)


@admin_bp.route('/payout/<int:payout_id>')
@role_required('admin')
def payout_detail(payout_id):
    """View payout request details"""
    payout = PayoutRequest.query.get_or_404(payout_id)
    rider = User.query.get(payout.rider_id)
    
    # Get rider's earnings associated with this payout request
    earnings = RiderEarning.query.filter_by(rider_id=payout.rider_id).all()
    
    return render_template('admin/payout_detail.html',
                         payout=payout,
                         rider=rider,
                         earnings=earnings)


@admin_bp.route('/payout/<int:payout_id>/approve', methods=['POST'])
@role_required('admin')
def approve_payout(payout_id):
    """Approve a payout request"""
    admin = get_current_user()
    payout = PayoutRequest.query.get_or_404(payout_id)
    admin_notes = request.form.get('admin_notes', '').strip()
    
    try:
        # Update payout request
        payout.status = 'approved'
        payout.approved_at = datetime.utcnow()
        payout.admin_notes = admin_notes
        
        # Create notification for rider
        notification = Notification(
            user_id=payout.rider_id,
            type='payout_approval',
            title='Payout Request Approved',
            message=f'Your payout request for PHP {float(payout.amount):.2f} has been approved and will be processed soon.',
            data={'payout_request_id': payout.id}
        )
        
        db.session.add(notification)
        db.session.commit()
        
        flash(f'Payout request #{payout_id} approved successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to approve payout request: {str(e)}', 'error')
    
    return redirect(url_for('admin.payout_detail', payout_id=payout_id))


@admin_bp.route('/payout/<int:payout_id>/reject', methods=['POST'])
@role_required('admin')
def reject_payout(payout_id):
    """Reject a payout request"""
    admin = get_current_user()
    payout = PayoutRequest.query.get_or_404(payout_id)
    admin_notes = request.form.get('admin_notes', '').strip()
    
    if not admin_notes:
        flash('Please provide a reason for rejection.', 'error')
        return redirect(url_for('admin.payout_detail', payout_id=payout_id))
    
    try:
        # Update payout request
        payout.status = 'rejected'
        payout.admin_notes = admin_notes
        
        # Create notification for rider
        notification = Notification(
            user_id=payout.rider_id,
            type='payout_rejection',
            title='Payout Request Rejected',
            message=f'Your payout request for PHP {float(payout.amount):.2f} has been rejected. Reason: {admin_notes}',
            data={'payout_request_id': payout.id}
        )
        
        db.session.add(notification)
        db.session.commit()
        
        flash(f'Payout request #{payout_id} rejected.', 'info')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to reject payout request: {str(e)}', 'error')
    
    return redirect(url_for('admin.payout_detail', payout_id=payout_id))


@admin_bp.route('/payout/<int:payout_id>/mark-paid', methods=['POST'])
@role_required('admin')
def mark_payout_paid(payout_id):
    """Mark payout as paid and update rider earnings"""
    admin = get_current_user()
    payout = PayoutRequest.query.get_or_404(payout_id)
    transaction_id = request.form.get('transaction_id', '').strip()
    admin_notes = request.form.get('admin_notes', '').strip()
    
    if not transaction_id:
        flash('Please provide a transaction ID.', 'error')
        return redirect(url_for('admin.payout_detail', payout_id=payout_id))
    
    try:
        # Update payout request
        payout.status = 'paid'
        payout.paid_at = datetime.utcnow()
        payout.admin_notes = admin_notes
        
        # Update associated earnings to 'paid' status
        # Get the earnings that total up to this payout amount
        pending_earnings = RiderEarning.query.filter_by(
            rider_id=payout.rider_id,
            status='pending'
        ).order_by(RiderEarning.created_at).all()
        
        amount_to_mark = float(payout.amount)
        for earning in pending_earnings:
            if amount_to_mark <= 0:
                break
            
            earning_amount = float(earning.total_earning)
            if earning_amount <= amount_to_mark:
                earning.status = 'paid'
                amount_to_mark -= earning_amount
        
        # Create notification for rider
        notification = Notification(
            user_id=payout.rider_id,
            type='payout_paid',
            title='Payout Processed',
            message=f'Your payout of PHP {float(payout.amount):.2f} has been processed and transferred to your account. Transaction ID: {transaction_id}',
            data={'payout_request_id': payout.id, 'transaction_id': transaction_id}
        )
        
        db.session.add(notification)
        db.session.commit()
        
        flash(f'Payout #{payout_id} marked as paid!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to mark payout as paid: {str(e)}', 'error')
    
    return redirect(url_for('admin.payout_detail', payout_id=payout_id))

@admin_bp.route('/system-settings')
@role_required('admin')
def system_settings():
    """System settings management"""
    return render_template('admin/system_settings.html')
