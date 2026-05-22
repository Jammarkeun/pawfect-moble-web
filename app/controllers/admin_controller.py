from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from app.utils.decorators import login_required, admin_required
from app.models.user import User
from app.models.seller_request import SellerRequest
from app.models.rider import Rider
from app.models.product import Product
from app.models.order import Order
from app.models.notification import Notification
from app.services.database import Database
from app.services.email_service import EmailService
from app.forms import AdminNotesForm, RejectNotesForm, CategoryForm, SystemSettingsForm
from app.utils.audit_logger import AuditLogger
from app.utils.export_helper import ExportHelper
from datetime import datetime, timedelta
import json

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with key metrics"""
    # Get statistics
    db = Database()
    
    stats = {}
    stats['total_users'] = User.get_users_count()
    stats['total_sellers'] = User.get_users_count(role='seller')
    stats['total_riders'] = User.get_users_count(role='rider')
    stats['total_customers'] = User.get_users_count(role='user')
    stats['pending_requests'] = SellerRequest.get_requests_count(status='pending')
    stats['pending_rider_requests'] = Rider.get_applications_count(status='pending')
    stats['total_orders'] = Order.count()
    stats['pending_orders'] = Order.count(status='pending')
    
    # Recent seller requests
    recent_requests = SellerRequest.get_all_requests(limit=5) or []
    recent_rider_requests = Rider.get_all_applications(limit=5) or []
    
    # Recent users
    recent_users = User.get_all_users(limit=10)
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_requests=recent_requests,
                         recent_rider_requests=recent_rider_requests,
                         recent_users=recent_users)

@admin_bp.route('/dashboard/stats')
@login_required
@admin_required
def dashboard_stats():
    """API endpoint for dashboard chart data"""
    days = int(request.args.get('days', 30))
    db = Database()
    
    try:
        revenue_data = []
        for i in range(days-1, -1, -1):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            date_start = f"{date}T00:00:00"
            date_end = f"{date}T23:59:59"
            result = db.client.table('orders').select('total_amount').gte('created_at', date_start).lte('created_at', date_end).not_.in_('status', ['cancelled']).execute()
            daily_revenue = sum(float(r.get('total_amount', 0) or 0) for r in (result.data or []))
            revenue_data.append({
                'date': date,
                'revenue': daily_revenue
            })
        
        status_result = db.client.table('orders').select('status').execute()
        status_counts = {}
        for r in (status_result.data or []):
            s = r.get('status', 'unknown')
            status_counts[s] = status_counts.get(s, 0) + 1
        status_distribution = [{'status': k, 'count': v} for k, v in status_counts.items()]
        
        user_registration_data = []
        for i in range(days-1, -1, -1):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            date_start = f"{date}T00:00:00"
            date_end = f"{date}T23:59:59"
            result = db.client.table('profiles').select('id', count='exact').gte('created_at', date_start).lte('created_at', date_end).not_.eq('role', 'admin').execute()
            user_registration_data.append({
                'date': date,
                'users': result.count if hasattr(result, 'count') else len(result.data or [])
            })
        
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        try:
            top_result = db.client.table('order_items').select('product_id, quantity').execute()
            products_map = {}
            for item in (top_result.data or []):
                pid = item.get('product_id')
                if pid:
                    products_map[pid] = products_map.get(pid, 0) + int(item.get('quantity', 0) or 0)
            sorted_products = sorted(products_map.items(), key=lambda x: x[1], reverse=True)[:5]
            top_products_data = []
            for pid, qty in sorted_products:
                p = db.client.table('products').select('name').eq('id', pid).limit(1).execute()
                if p.data:
                    top_products_data.append({'name': p.data[0].get('name', f'Product #{pid}'), 'quantity': qty})
        except Exception:
            top_products_data = []
        
        return jsonify({
            'revenue': revenue_data,
            'orderStatus': status_distribution,
            'userRegistration': user_registration_data,
            'topProducts': top_products_data
        })
    except Exception as e:
        import traceback
        print(f"Error in dashboard_stats: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/analytics/realtime')
@login_required
@admin_required
def analytics_realtime():
    """Real-time platform analytics API"""
    db = Database()
    
    try:
        orders_all = db.client.table('orders').select('total_amount, status, created_at').execute()
        orders_data = orders_all.data or []
        cancelled_statuses = ['cancelled']
        
        total_revenue = sum(float(r.get('total_amount', 0) or 0) for r in orders_data if r.get('status') not in cancelled_statuses)
        
        today_str = datetime.now().strftime('%Y-%m-%d')
        today_revenue = sum(float(r.get('total_amount', 0) or 0) for r in orders_data
                          if r.get('status') not in cancelled_statuses
                          and (r.get('created_at') or '').startswith(today_str))
        
        current_month = datetime.now().month
        current_year = datetime.now().year
        month_revenue = 0
        total_orders = 0
        pending = confirmed = delivered = cancelled = 0
        for r in orders_data:
            total_orders += 1
            s = r.get('status', '')
            if s == 'pending': pending += 1
            elif s == 'confirmed': confirmed += 1
            elif s == 'delivered': delivered += 1
            elif s == 'cancelled': cancelled += 1
            if r.get('status') not in cancelled_statuses:
                created = r.get('created_at', '')
                try:
                    dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    if dt.month == current_month and dt.year == current_year:
                        month_revenue += float(r.get('total_amount', 0) or 0)
                except Exception:
                    pass
        
        profiles_all = db.client.table('profiles').select('role').neq('role', 'admin').execute()
        profiles_data = profiles_all.data or []
        total_users = len(profiles_data)
        customers = sum(1 for r in profiles_data if r.get('role') == 'user')
        sellers = sum(1 for r in profiles_data if r.get('role') == 'seller')
        riders = sum(1 for r in profiles_data if r.get('role') == 'rider')
        
        deliveries_all = db.client.table('deliveries').select('status').execute()
        deliveries_data = deliveries_all.data or []
        total_deliveries = len(deliveries_data)
        d_completed = sum(1 for r in deliveries_data if r.get('status') == 'delivered')
        d_failed = sum(1 for r in deliveries_data if r.get('status') == 'failed')
        d_pending = sum(1 for r in deliveries_data if r.get('status') in ('assigned', 'picked_up', 'on_the_way'))
        
        products_all = db.client.table('products').select('status, stock_quantity').execute()
        products_data = products_all.data or []
        total_products = len(products_data)
        active_products = sum(1 for r in products_data if r.get('status') == 'active')
        out_of_stock = sum(1 for r in products_data if int(r.get('stock_quantity', 0) or 0) == 0)
        
        commission_rate = float(current_app.config.get('SELLER_COMMISSION_RATE', 0.05))
        platform_commission = round(total_revenue * commission_rate, 2)
        
        return jsonify({
            'success': True,
            'revenue': {
                'total': round(total_revenue, 2),
                'today': round(today_revenue, 2),
                'this_month': round(month_revenue, 2),
                'commission': platform_commission
            },
            'orders': {
                'total': total_orders,
                'pending': pending,
                'confirmed': confirmed,
                'delivered': delivered,
                'cancelled': cancelled
            },
            'users': {
                'total': total_users,
                'customers': customers,
                'sellers': sellers,
                'riders': riders
            },
            'deliveries': {
                'total': total_deliveries,
                'completed': d_completed,
                'failed': d_failed,
                'pending': d_pending
            },
            'products': {
                'total': total_products,
                'active': active_products,
                'out_of_stock': out_of_stock
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in analytics_realtime: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/seller-requests')
@login_required
@admin_required
def seller_requests():
    """Manage seller requests"""
    status = request.args.get('status', 'pending')
    requests = SellerRequest.get_all_requests(status=status if status != 'all' else None)
    
    return render_template('admin/seller_requests.html',
                         requests=requests,
                         current_status=status)

@admin_bp.route('/seller-requests/<int:request_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_seller_request(request_id):
    """Approve a seller request"""
    form = AdminNotesForm(request.form)
    admin_notes = None
    if form.validate_on_submit():
        admin_notes = form.admin_notes.data.strip() if form.admin_notes.data else None
    else:
        # Check if CSRF is the only error (for optional notes)
        if form.errors and len(form.errors) == 1 and 'csrf_token' in form.errors:
            # CSRF passed, but form not validated - use raw data
            admin_notes = request.form.get('admin_notes', '').strip() or None
        else:
            flash('Invalid form data.', 'error')
            return redirect(url_for('admin.seller_requests'))
        
    try:
        # Get request details before approval
        req = SellerRequest.get_by_id(request_id)
        
        success = SellerRequest.approve_request(request_id, admin_notes)
        if success:
            # Log the approval action
            if req:
                AuditLogger.log_seller_approval(
                    request_id,
                    session.get('user_id'),
                    f"{req['first_name']} {req['last_name']}"
                )

                # Notify approved seller in-app and via email
                Notification.create(
                    user_id=req['user_id'],
                    role='seller',
                    type_='general',
                    title='Seller Application Approved',
                    message='Your seller application has been approved. You can now access seller features.',
                    related_id=request_id,
                    data={'account_type': 'seller', 'status': 'approved'}
                )
                EmailService.send_application_status_email(
                    req.get('email'),
                    account_type='seller',
                    status='approved',
                    admin_notes=admin_notes
                )
            flash('Seller request approved successfully!', 'success')
        else:
            flash('Failed to approve request. Request may not exist or already processed.', 'error')
    except Exception as e:
        flash('An error occurred while approving the request.', 'error')
    
    return redirect(url_for('admin.seller_requests'))

@admin_bp.route('/seller-requests/<int:request_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_seller_request(request_id):
    """Reject a seller request"""
    form = RejectNotesForm(request.form)
    admin_notes = None
    if form.validate_on_submit():
        admin_notes = form.admin_notes.data.strip()
    else:
        # Check if CSRF is the only error and notes are provided
        if form.errors and len(form.errors) == 1 and 'csrf_token' in form.errors:
            admin_notes = request.form.get('admin_notes', '').strip()
            if not admin_notes:
                flash('Please provide a reason for rejection.', 'error')
                return redirect(url_for('admin.seller_requests'))
        else:
            flash('Please provide a reason for rejection.', 'error')
            return redirect(url_for('admin.seller_requests'))
        
    try:
        # Get request details before rejection
        req = SellerRequest.get_by_id(request_id)
        
        success = SellerRequest.reject_request(request_id, admin_notes)
        if success:
            # Log the rejection action
            if req:
                AuditLogger.log_seller_rejection(
                    request_id,
                    session.get('user_id'),
                    f"{req['first_name']} {req['last_name']}",
                    admin_notes or 'No reason provided'
                )

                # Notify rejected applicant in-app and via email
                Notification.create(
                    user_id=req['user_id'],
                    role='user',
                    type_='general',
                    title='Seller Application Rejected',
                    message=(
                        f"Your seller application was rejected. {admin_notes}"
                        if admin_notes else
                        'Your seller application was rejected. Please contact support for details.'
                    ),
                    related_id=request_id,
                    data={'account_type': 'seller', 'status': 'rejected'}
                )
                EmailService.send_application_status_email(
                    req.get('email'),
                    account_type='seller',
                    status='rejected',
                    admin_notes=admin_notes
                )
            flash('Seller request rejected.', 'info')
        else:
            flash('Failed to reject request.', 'error')
    except Exception as e:
        flash('An error occurred while rejecting the request.', 'error')
    
    return redirect(url_for('admin.seller_requests'))

@admin_bp.route('/seller-requests/<int:request_id>/details')
@login_required
@admin_required
def seller_request_details(request_id):
    """Get seller request details (AJAX endpoint)"""
    try:
        req = SellerRequest.get_by_id(request_id)
        if not req:
            return jsonify({'error': 'Request not found'}), 404
        
        # Format the dates (already parsed to datetime by _enrich_with_profile)
        requested_at = req['requested_at'].strftime('%B %d, %Y at %I:%M %p') if req.get('requested_at') else 'N/A'
        reviewed_at = req['reviewed_at'].strftime('%B %d, %Y at %I:%M %p') if req.get('reviewed_at') else 'N/A'
        
        # Status badge color
        status_color = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger'
        }.get(req.get('status', 'pending'), 'secondary')
        
        # Build HTML
        html = f"""
        <div class="row">
            <div class="col-md-4 text-center">
                {f'<img src="/uploads/{req["profile_image"]}" alt="Profile" class="rounded-circle mb-3" style="width: 120px; height: 120px; object-fit: cover;">' if req.get('profile_image') else '<div class="avatar-circle bg-primary text-white mx-auto mb-3" style="width: 120px; height: 120px; font-size: 3em; line-height: 120px;">' + req['first_name'][0].upper() + '</div>'}
                <h5>{req['first_name']} {req['last_name']}</h5>
                <p class="text-muted">@{req['username']}</p>
                <p><a href="mailto:{req['email']}" class="text-decoration-none">{req['email']}</a></p>
            </div>
            <div class="col-md-8">
                <h6 class="border-bottom pb-2 mb-3">Business Information</h6>
                <div class="row mb-3">
                    <div class="col-sm-5"><strong>Business Name:</strong></div>
                    <div class="col-sm-7">{req['business_name']}</div>
                </div>
                <div class="row mb-3">
                    <div class="col-sm-5"><strong>Business Phone:</strong></div>
                    <div class="col-sm-7">{req['business_phone']}</div>
                </div>
                <div class="row mb-3">
                    <div class="col-sm-5"><strong>Business Address:</strong></div>
                    <div class="col-sm-7">{req['business_address']}</div>
                </div>
                {f'<div class="row mb-3"><div class="col-sm-5"><strong>Tax ID:</strong></div><div class="col-sm-7">{req["tax_id"]}</div></div>' if req.get('tax_id') else ''}
                {f'<div class="row mb-3"><div class="col-sm-5"><strong>Business Permit:</strong></div><div class="col-sm-7"><a href="/uploads/{req["business_permit"]}" target="_blank" class="btn btn-sm btn-outline-primary"><i class="fas fa-file-download"></i> View Document</a></div></div>' if req.get('business_permit') else ''}
                
                <h6 class="border-bottom pb-2 mb-3 mt-4">Business Description</h6>
                <p>{req['business_description']}</p>
                
                <h6 class="border-bottom pb-2 mb-3 mt-4">Request Status</h6>
                <div class="row mb-2">
                    <div class="col-sm-5"><strong>Status:</strong></div>
                    <div class="col-sm-7"><span class="badge bg-{status_color}">{req['status'].title()}</span></div>
                </div>
                <div class="row mb-2">
                    <div class="col-sm-5"><strong>Requested At:</strong></div>
                    <div class="col-sm-7">{requested_at}</div>
                </div>
                {f'<div class="row mb-2"><div class="col-sm-5"><strong>Reviewed At:</strong></div><div class="col-sm-7">{reviewed_at}</div></div>' if req.get('reviewed_at') else ''}
                {f'<div class="row mb-2"><div class="col-sm-5"><strong>Admin Notes:</strong></div><div class="col-sm-7"><div class="alert alert-info mb-0">{req["admin_notes"]}</div></div></div>' if req.get('admin_notes') else ''}
            </div>
        </div>
        """
        
        return jsonify({'html': html})
    except Exception as e:
        import traceback
        error_msg = f"Server error: {str(e)}\n{traceback.format_exc()}"
        return jsonify({'error': error_msg}), 500


@admin_bp.route('/rider-requests')
@login_required
@admin_required
def rider_requests():
    """Manage rider applications"""
    status = (request.args.get('status', 'pending') or 'pending').lower()
    allowed_statuses = {'pending', 'approved', 'rejected', 'all'}
    if status not in allowed_statuses:
        status = 'pending'
    
    rider_apps = Rider.get_all_applications(status if status != 'all' else None) or []
    status_counts = {
        'pending': Rider.get_applications_count(status='pending'),
        'approved': Rider.get_applications_count(status='approved'),
        'rejected': Rider.get_applications_count(status='rejected'),
        'all': Rider.get_applications_count()
    }
    
    return render_template(
        'admin/rider_requests.html',
        requests=rider_apps,
        current_status=status,
        status_counts=status_counts
    )


@admin_bp.route('/rider-requests/<int:application_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_rider_request(application_id):
    """Approve a rider application"""
    form = AdminNotesForm(request.form)
    if form.validate_on_submit():
        admin_notes = form.admin_notes.data.strip() if form.admin_notes.data else None
    else:
        if form.errors and len(form.errors) == 1 and 'csrf_token' in form.errors:
            admin_notes = request.form.get('admin_notes', '').strip() or None
        else:
            flash('Invalid form data.', 'error')
            return redirect(url_for('admin.rider_requests'))

    try:
        application = Rider.get_application_by_id(application_id)
        if not application:
            flash('Rider request not found.', 'error')
            return redirect(url_for('admin.rider_requests'))

        # Update application status
        Rider.update_application_status(application_id, 'approved', admin_notes)

        # Activate the rider account - this changes user role to 'rider'
        user_id = application.get('user_id')
        if user_id:
            Rider.activate_rider_account(user_id)

            # Notify approved rider in-app and via email
            user = User.get_by_id(user_id)
            Notification.create(
                user_id=user_id,
                role='rider',
                type_='general',
                title='Rider Application Approved',
                message='Your rider application has been approved. You can now access rider features.',
                related_id=application_id,
                data={'account_type': 'rider', 'status': 'approved'}
            )
            if user and user.get('email'):
                EmailService.send_application_status_email(
                    user.get('email'),
                    account_type='rider',
                    status='approved',
                    admin_notes=admin_notes
                )

        AuditLogger.log_rider_approval(
            application_id,
            session.get('user_id'),
            f"{application.get('first_name', '')} {application.get('last_name', '')}".strip()
        )
        flash('Rider request approved successfully! The user can now log in as a rider.', 'success')
    except Exception as e:
        flash('An error occurred while approving the rider request.', 'error')

    return redirect(url_for('admin.rider_requests'))


@admin_bp.route('/rider-requests/<int:application_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_rider_request(application_id):
    """Reject a rider application"""
    form = RejectNotesForm(request.form)
    if form.validate_on_submit():
        admin_notes = form.admin_notes.data.strip()
    else:
        if form.errors and len(form.errors) == 1 and 'csrf_token' in form.errors:
            admin_notes = request.form.get('admin_notes', '').strip()
        else:
            admin_notes = None
    
    if not admin_notes:
        flash('Please provide a reason for rejection.', 'error')
        return redirect(url_for('admin.rider_requests'))
    
    try:
        application = Rider.get_application_by_id(application_id)
        if not application:
            flash('Rider request not found.', 'error')
            return redirect(url_for('admin.rider_requests'))
        
        Rider.update_application_status(application_id, 'rejected', admin_notes)

        # Notify rejected rider in-app and via email
        user_id = application.get('user_id')
        user = User.get_by_id(user_id) if user_id else None
        if user_id:
            Notification.create(
                user_id=user_id,
                role='user',
                type_='general',
                title='Rider Application Rejected',
                message=f'Your rider application was rejected. Reason: {admin_notes}',
                related_id=application_id,
                data={'account_type': 'rider', 'status': 'rejected'}
            )
        if user and user.get('email'):
            EmailService.send_application_status_email(
                user.get('email'),
                account_type='rider',
                status='rejected',
                admin_notes=admin_notes
            )

        AuditLogger.log_rider_rejection(
            application_id,
            session.get('user_id'),
            f"{application.get('first_name', '')} {application.get('last_name', '')}".strip(),
            admin_notes
        )
        flash('Rider request rejected.', 'info')
    except Exception as e:
        flash('An error occurred while rejecting the rider request.', 'error')
    
    return redirect(url_for('admin.rider_requests'))


@admin_bp.route('/rider-requests/<int:application_id>/details')
@login_required
@admin_required
def rider_request_details(application_id):
    """Get rider application details"""
    try:
        application = Rider.get_application_by_id(application_id)
        if not application:
            return jsonify({'error': 'Request not found'}), 404
        
        # Dates already parsed to datetime by _enrich_with_profile
        created_at = application.get('created_at')
        reviewed_at = application.get('reviewed_at')
        created_str = created_at.strftime('%B %d, %Y at %I:%M %p') if created_at else 'N/A'
        reviewed_str = reviewed_at.strftime('%B %d, %Y at %I:%M %p') if reviewed_at else None
        
        status_colors = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger'
        }
        status_badge = status_colors.get(application.get('status', 'pending'), 'secondary')
        
        def build_doc_row(label, path):
            if not path:
                return ''
            url = path if str(path).startswith(('http://', 'https://', '/')) else url_for('static', filename=path)
            return f"""
            <div class="row mb-2">
                <div class="col-sm-5"><strong>{label}:</strong></div>
                <div class="col-sm-7">
                    <a href="{url}" target="_blank" class="btn btn-sm btn-outline-primary">
                        <i class="fas fa-file-download"></i> View Document
                    </a>
                </div>
            </div>
            """
        
        profile_photo = application.get('profile_photo_path')
        profile_photo_tag = ''
        if profile_photo:
            profile_url = profile_photo if str(profile_photo).startswith(('http://', 'https://', '/')) else url_for('static', filename=profile_photo)
            profile_photo_tag = f'<img src="{profile_url}" alt="Rider Photo" class="rounded-circle mb-3" style="width: 120px; height: 120px; object-fit: cover;">'
        else:
            initials = (application.get('first_name', 'R')[:1] or 'R').upper()
            profile_photo_tag = f'<div class="avatar-circle bg-primary text-white mx-auto mb-3" style="width: 120px; height: 120px; font-size: 3em; line-height: 120px;">{initials}</div>'
        
        html = f"""
        <div class="row">
            <div class="col-md-4 text-center">
                {profile_photo_tag}
                <h5>{application.get('first_name', '')} {application.get('last_name', '')}</h5>
                <p class="text-muted">@{application.get('username', '')}</p>
                <p><a href="mailto:{application.get('email', '')}" class="text-decoration-none">{application.get('email', '')}</a></p>
                <p><strong>Phone:</strong> {application.get('phone', 'N/A')}</p>
            </div>
            <div class="col-md-8">
                <h6 class="border-bottom pb-2 mb-3">Vehicle Information</h6>
                <div class="row mb-2">
                    <div class="col-sm-5"><strong>Vehicle Type:</strong></div>
                    <div class="col-sm-7">{application.get('vehicle_type', 'N/A').replace('_', ' ').title()}</div>
                </div>
                <div class="row mb-2">
                    <div class="col-sm-5"><strong>Vehicle Model:</strong></div>
                    <div class="col-sm-7">{application.get('vehicle_model', 'N/A')}</div>
                </div>
                <div class="row mb-2">
                    <div class="col-sm-5"><strong>Plate Number:</strong></div>
                    <div class="col-sm-7">{application.get('vehicle_plate_number', 'N/A')}</div>
                </div>
                
                <h6 class="border-bottom pb-2 mb-3 mt-4">Documents</h6>
                {build_doc_row("Government ID", application.get('government_id_path'))}
                {build_doc_row("Vehicle Registration", application.get('vehicle_registration_path'))}
                {build_doc_row("NBI / Police Clearance", application.get('clearance_path'))}
                
                <h6 class="border-bottom pb-2 mb-3 mt-4">Request Status</h6>
                <div class="row mb-2">
                    <div class="col-sm-5"><strong>Status:</strong></div>
                    <div class="col-sm-7"><span class="badge bg-{status_badge}">{application.get('status', 'pending').title()}</span></div>
                </div>
                <div class="row mb-2">
                    <div class="col-sm-5"><strong>Submitted At:</strong></div>
                    <div class="col-sm-7">{created_str}</div>
                </div>
                {f'<div class="row mb-2"><div class="col-sm-5"><strong>Reviewed At:</strong></div><div class="col-sm-7">{reviewed_str}</div></div>' if reviewed_str else ''}
                {f'<div class="row mb-2"><div class="col-sm-5"><strong>Admin Notes:</strong></div><div class="col-sm-7"><div class="alert alert-info mb-0">{application.get("admin_notes")}</div></div></div>' if application.get('admin_notes') else ''}
            </div>
        </div>
        """
        
        return jsonify({'html': html})
    except Exception as e:
        import traceback
        error_msg = f"Server error: {str(e)}\n{traceback.format_exc()}"
        return jsonify({'error': error_msg}), 500

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Manage users"""
    role_filter = request.args.get('role')
    status_filter = request.args.get('status')
    search_query = request.args.get('search', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page
    
    db = Database()
    query = db.client.table('profiles').select('*')
    
    if role_filter:
        query = query.eq('role', role_filter)
    
    if status_filter:
        query = query.eq('status', status_filter)
    
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.or_(f"first_name.ilike.{search_pattern},last_name.ilike.{search_pattern},email.ilike.{search_pattern},username.ilike.{search_pattern}")
    
    count_query = db.client.table('profiles').select('*', count='exact')
    if role_filter:
        count_query = count_query.eq('role', role_filter)
    if status_filter:
        count_query = count_query.eq('status', status_filter)
    if search_query:
        count_query = count_query.or_(f"first_name.ilike.{search_pattern},last_name.ilike.{search_pattern},email.ilike.{search_pattern},username.ilike.{search_pattern}")
    
    count_result = count_query.execute()
    total = count_result.count if hasattr(count_result, 'count') else 0
    
    users_data = query.order('created_at', desc=True).range(offset, offset + per_page - 1).execute()
    users = users_data.data or []
    for u in users:
        if isinstance(u.get('created_at'), str):
            try:
                u['created_at'] = datetime.fromisoformat(u['created_at'])
            except (ValueError, TypeError):
                u['created_at'] = None
    
    # Calculate pagination
    total_pages = (total + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    
    # Get statistics for the stats cards
    total_users = User.get_users_count()
    active_users = User.get_users_count(status='active')
    inactive_users = User.get_users_count(status='inactive')
    pending_users = User.get_users_count(status='pending')
    admin_users = User.get_users_count(role='admin')

    # Get recent users for sidebar
    recent_users = User.get_all_users(limit=5)

    return render_template('admin/users.html',
                         users=users,
                         current_role=role_filter,
                         current_status=status_filter,
                         current_page=page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         prev_page=page-1 if has_prev else None,
                         next_page=page+1 if has_next else None,
                         total_users=total_users,
                         active_users=active_users,
                         inactive_users=inactive_users,
                         pending_users=pending_users,
                         admin_users=admin_users,
                         recent_users=recent_users)

@admin_bp.route('/users/<user_id>/update-status', methods=['POST'])
@login_required
@admin_required
def update_user_status(user_id):
    """Update user status (active/inactive/banned)"""
    new_status = request.form.get('status')
    reason = (request.form.get('reason') or '').strip()
    
    # Prevent admin from changing their own status
    if str(user_id) == str(session['user_id']):
        flash('You cannot change your own status.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    # Validate status
    valid_statuses = ['active', 'inactive', 'banned']
    if new_status not in valid_statuses:
        flash('Invalid status.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    try:
        user = User.get_by_id(user_id)
        previous_status = (user.get('status') or '').strip().lower() if user else ''
        user_role = (user.get('role') or '').strip().lower() if user else ''

        User.update_status(user_id, new_status)

        # Buyer approval/rejection notifications.
        if user and user_role == 'user':
            if new_status == 'active' and previous_status != 'active':
                Notification.create(
                    user_id=user_id,
                    role='user',
                    type_='general',
                    title='Buyer Account Approved',
                    message='Your buyer account has been approved. You can now log in to Pawfect Finds.',
                    data={'account_type': 'user', 'status': 'approved'}
                )
                email_sent = EmailService.send_application_status_email(
                    user.get('email'),
                    account_type='user',
                    status='approved'
                )
                current_app.logger.info(
                    'Buyer approval email dispatch user_id=%s email=%s sent=%s',
                    user_id,
                    user.get('email'),
                    email_sent
                )
            elif new_status == 'inactive' and previous_status == 'pending':
                rejection_message = (
                    f'Your buyer account was rejected. Reason: {reason}'
                    if reason else
                    'Your buyer account was rejected. Please contact support for details.'
                )
                Notification.create(
                    user_id=user_id,
                    role='user',
                    type_='general',
                    title='Buyer Account Rejected',
                    message=rejection_message,
                    data={'account_type': 'user', 'status': 'rejected'}
                )
                EmailService.send_application_status_email(
                    user.get('email'),
                    account_type='user',
                    status='rejected',
                    admin_notes=reason or None
                )

        flash(f'User status updated to {new_status}.', 'success')
    except Exception as e:
        flash('Failed to update user status.', 'error')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/users/<user_id>/update-role', methods=['POST'])
@login_required
@admin_required
def update_user_role(user_id):
    """Update user role"""
    new_role = request.form.get('role')
    
    # Prevent admin from changing their own role
    if str(user_id) == str(session['user_id']):
        flash('You cannot change your own role.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    # Validate role
    valid_roles = ['user', 'seller', 'admin']
    if new_role not in valid_roles:
        flash('Invalid role.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    try:
        User.update_role(user_id, new_role)
        flash(f'User role updated to {new_role}.', 'success')
    except Exception as e:
        flash('Failed to update user role.', 'error')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/users/<user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user"""
    # Prevent admin from deleting themselves
    if str(user_id) == str(session['user_id']):
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    try:
        User.delete(user_id)
        flash('User deleted successfully.', 'success')
    except Exception as e:
        flash('Failed to delete user. User may have associated data.', 'error')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/products')
@login_required
@admin_required
def manage_products():
    """Manage all products"""
    category_filter = request.args.get('category')
    status_filter = request.args.get('status')
    search_query = request.args.get('search', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page

    db = Database()
    products_data = db.client.table('products').select('*').order('created_at', desc=True).execute()
    all_products = products_data.data or []
    
    # Get categories for filter
    categories_data = db.client.table('categories').select('*').execute()
    all_categories = categories_data.data or []
    
    # Filter in Python for complex conditions
    filtered = all_products
    if category_filter:
        filtered = [p for p in filtered if str(p.get('category_id')) == category_filter]
    if status_filter:
        filtered = [p for p in filtered if p.get('status') == status_filter]
    if search_query:
        sq = search_query.lower()
        filtered = [p for p in filtered if sq in (p.get('name', '') or '').lower() or sq in (p.get('description', '') or '').lower()]
    
    total = len(filtered)
    
    # Enrich with category and seller names
    profile_ids = list(set(str(p.get('seller_id')) for p in filtered if p.get('seller_id')))
    profiles_map = {}
    for pid in profile_ids:
        pp = db.client.table('profiles').select('username').eq('id', pid).limit(1).execute()
        if pp.data:
            profiles_map[pid] = pp.data[0].get('username', 'Unknown')
    
    cat_map = {str(c.get('id')): c.get('name', '') for c in all_categories}
    
    paginated = filtered[offset:offset + per_page]
    products = []
    for p in paginated:
        p['category_name'] = cat_map.get(str(p.get('category_id')), '')
        p['seller_name'] = profiles_map.get(str(p.get('seller_id')), 'Unknown')
        if isinstance(p.get('created_at'), str):
            try:
                p['created_at'] = datetime.fromisoformat(p['created_at'])
            except (ValueError, TypeError):
                p['created_at'] = None
        products.append(p)
    
    categories = all_categories
    
    # Calculate pagination
    total_pages = (total + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages

    return render_template('admin/products.html',
                         products=products,
                         categories=categories,
                         current_category=int(category_filter) if category_filter else None,
                         current_status=status_filter,
                         current_page=page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         prev_page=page-1 if has_prev else None,
                         next_page=page+1 if has_next else None)

@admin_bp.route('/products/<int:product_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_product_status(product_id):
    """Toggle product status (active/inactive)"""
    try:
        # Get current product status
        product = Product.get_by_id(product_id)
        if not product:
            flash('Product not found.', 'error')
            return redirect(url_for('admin.manage_products'))

        new_status = 'inactive' if product.get('status') == 'active' else 'active'
        Product.update(product_id, status=new_status)

        status_text = "activated" if new_status == 'active' else "deactivated"
        flash(f'Product {status_text} successfully!', 'success')

    except Exception as e:
        flash('Failed to update product status.', 'error')

    return redirect(url_for('admin.manage_products'))

@admin_bp.route('/products/<int:product_id>/remove', methods=['POST'])
@login_required
@admin_required
def remove_product(product_id):
    """Remove a product"""
    try:
        # Check if product exists
        product = Product.get_by_id(product_id)
        if not product:
            flash('Product not found.', 'error')
            return redirect(url_for('admin.manage_products'))

        # Delete the product
        Product.delete(product_id)
        flash('Product removed successfully!', 'success')

    except Exception as e:
        flash('Failed to remove product.', 'error')

    return redirect(url_for('admin.manage_products'))

@admin_bp.route('/products/<int:product_id>/details')
@login_required
@admin_required
def product_details(product_id):
    """Get product details for modal (AJAX endpoint)"""
    try:
        product = Product.get_by_id(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Format the dates
        ca = product.get('created_at')
        if isinstance(ca, str):
            try:
                ca = datetime.fromisoformat(ca.replace('Z', '+00:00'))
            except ValueError:
                ca = None
        created_at = ca.strftime('%B %d, %Y at %I:%M %p') if ca else 'N/A'
        ua = product.get('updated_at')
        if isinstance(ua, str):
            try:
                ua = datetime.fromisoformat(ua.replace('Z', '+00:00'))
            except ValueError:
                ua = None
        updated_at = ua.strftime('%B %d, %Y at %I:%M %p') if ua else 'N/A'
        
        # Status badge color
        status_color = {
            'active': 'success',
            'inactive': 'secondary',
            'out_of_stock': 'danger'
        }.get(product.get('status', 'inactive'), 'secondary')
        
        # Stock badge color
        stock_qty = product.get('stock_quantity', 0)
        stock_color = 'danger' if stock_qty == 0 else 'warning' if stock_qty <= 5 else 'success'
        
        # Build images HTML
        images_html = ''
        if product.get('images') and len(product['images']) > 0:
            images_html = '<div class="row">'
            for img in product['images']:
                images_html += f'''
                    <div class="col-4 mb-2">
                        <img src="/uploads/{img['image_url']}" class="img-thumbnail" style="width: 100%; height: 100px; object-fit: cover;" alt="Product Image">
                    </div>
                '''
            images_html += '</div>'
        else:
            # Use main image if no additional images
            main_img = product.get('image_url', '')
            if main_img:
                images_html = f'<img src="/uploads/{main_img}" class="img-fluid rounded" style="max-height: 300px; object-fit: cover;" alt="Product Image">'
            else:
                images_html = '<p class="text-muted">No images available</p>'
        
        # Build HTML
        html = f"""
        <div class="row">
            <div class="col-md-5">
                <h6 class="mb-3">Product Images</h6>
                {images_html}
            </div>
            <div class="col-md-7">
                <h5 class="mb-3">{product['name']}</h5>
                
                <div class="row mb-2">
                    <div class="col-sm-4"><strong>Category:</strong></div>
                    <div class="col-sm-8">{product['category_name']}</div>
                </div>
                
                <div class="row mb-2">
                    <div class="col-sm-4"><strong>Seller:</strong></div>
                    <div class="col-sm-8">{product['seller_username']}</div>
                </div>
                
                <div class="row mb-2">
                    <div class="col-sm-4"><strong>Price:</strong></div>
                    <div class="col-sm-8">₱{product['price']:,.2f}</div>
                </div>
                
                <div class="row mb-2">
                    <div class="col-sm-4"><strong>Stock Quantity:</strong></div>
                    <div class="col-sm-8">
                        <span class="badge bg-{stock_color}">{stock_qty} units</span>
                    </div>
                </div>
                
                <div class="row mb-2">
                    <div class="col-sm-4"><strong>Status:</strong></div>
                    <div class="col-sm-8">
                        <span class="badge bg-{status_color}">{product['status'].replace('_', ' ').title()}</span>
                    </div>
                </div>
                
                <div class="row mb-2">
                    <div class="col-sm-4"><strong>Created At:</strong></div>
                    <div class="col-sm-8">{created_at}</div>
                </div>
                
                <div class="row mb-3">
                    <div class="col-sm-4"><strong>Updated At:</strong></div>
                    <div class="col-sm-8">{updated_at}</div>
                </div>
                
                <hr>
                <h6>Description</h6>
                <p class="text-muted">{product.get('description', 'No description available')}</p>
            </div>
        </div>
        """
        
        return jsonify({'html': html})
    except Exception as e:
        import traceback
        error_msg = f"Server error: {str(e)}\n{traceback.format_exc()}"
        return jsonify({'error': error_msg}), 500

@admin_bp.route('/orders')
@login_required
@admin_required
def manage_orders():
    """View all orders"""
    status_filter = request.args.get('status')
    search_query = request.args.get('search', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page

    db = Database()
    orders_data = db.client.table('orders').select('*').order('created_at', desc=True).execute()
    all_orders = orders_data.data or []
    
    if status_filter and status_filter != 'all':
        all_orders = [o for o in all_orders if o.get('status') == status_filter]
    
    if search_query:
        sq = search_query.lower()
        all_orders = [o for o in all_orders if sq in str(o.get('id', '')).lower()]
    
    total = len(all_orders)
    
    paginated = all_orders[offset:offset + per_page]
    
    # Enrich with customer and seller info
    uid_set = set()
    for o in paginated:
        if o.get('user_id'): uid_set.add(o['user_id'])
        if o.get('seller_id'): uid_set.add(o['seller_id'])
    
    profiles_map = {}
    for uid in uid_set:
        pp = db.client.table('profiles').select('username, email').eq('id', uid).limit(1).execute()
        if pp.data:
            profiles_map[uid] = pp.data[0]
    
    orders = []
    for o in paginated:
        cust = profiles_map.get(o.get('user_id', ''), {})
        sel = profiles_map.get(o.get('seller_id', ''), {})
        o['customer_username'] = cust.get('username', 'Unknown')
        o['seller_username'] = sel.get('username', 'Unknown')
        if isinstance(o.get('created_at'), str):
            try:
                o['created_at'] = datetime.fromisoformat(o['created_at'])
            except (ValueError, TypeError):
                o['created_at'] = None
        orders.append(o)
    
    # Calculate pagination
    total_pages = (total + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages

    return render_template('admin/orders.html',
                         orders=orders,
                         current_status=status_filter,
                         current_page=page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         prev_page=page-1 if has_prev else None,
                         next_page=page+1 if has_next else None)

@admin_bp.route('/orders/<order_id>/force-cancel', methods=['POST'])
@login_required
@admin_required
def force_cancel_order(order_id):
    """Force cancel an order (admin only)"""
    try:
        # Get order details
        order = Order.get_by_id(order_id)
        if not order:
            flash('Order not found.', 'error')
            return redirect(url_for('admin.manage_orders'))

        # Check if order can be cancelled (order is a dict, so use dict access)
        order_status = order.get('status') if isinstance(order, dict) else order.status
        if order_status in ['delivered', 'cancelled']:
            flash('Cannot cancel a delivered or already cancelled order.', 'error')
            return redirect(url_for('admin.manage_orders'))

        # Force cancel the order
        if not Order.update_status(order_id, 'cancelled'):
            flash('Failed to cancel order.', 'error')
            return redirect(url_for('admin.manage_orders'))

        db = Database()
        order_items_data = db.client.table('order_items').select('*').eq('order_id', order_id).execute()
        order_items = order_items_data.data or []
        for item in order_items:
            product = db.client.table('products').select('stock_quantity').eq('id', item['product_id']).limit(1).execute()
            if product.data:
                new_qty = int(product.data[0].get('stock_quantity', 0) or 0) + int(item.get('quantity', 0) or 0)
                db.client.table('products').update({'stock_quantity': new_qty}).eq('id', item['product_id']).execute()

        flash('Order has been force cancelled successfully.', 'success')

    except Exception as e:
        import traceback
        current_app.logger.error(f"Error force cancelling order {order_id}: {str(e)}\n{traceback.format_exc()}")
        flash('Failed to cancel order.', 'error')

    return redirect(url_for('admin.manage_orders'))

@admin_bp.route('/orders/<order_id>/restore', methods=['POST'])
@login_required
@admin_required
def restore_order(order_id):
    """Restore a cancelled order (admin only)"""
    try:
        # Get order details
        order = Order.get_by_id(order_id)
        if not order:
            flash('Order not found.', 'error')
            return redirect(url_for('admin.manage_orders'))

        # Check if order is cancelled (order is a dict, so use dict access)
        order_status = order.get('status') if isinstance(order, dict) else order.status
        if order_status != 'cancelled':
            flash('Only cancelled orders can be restored.', 'error')
            return redirect(url_for('admin.manage_orders'))

        # Restore the order to pending status
        if not Order.update_status(order_id, 'pending'):
            flash('Failed to restore order.', 'error')
            return redirect(url_for('admin.manage_orders'))

        db = Database()
        order_items_data = db.client.table('order_items').select('*').eq('order_id', order_id).execute()
        order_items = order_items_data.data or []
        for item in order_items:
            product = db.client.table('products').select('stock_quantity').eq('id', item['product_id']).limit(1).execute()
            if product.data:
                new_qty = max(0, int(product.data[0].get('stock_quantity', 0) or 0) - int(item.get('quantity', 0) or 0))
                db.client.table('products').update({'stock_quantity': new_qty}).eq('id', item['product_id']).execute()

        flash('Order has been restored successfully.', 'success')

    except Exception as e:
        import traceback
        current_app.logger.error(f"Error restoring order {order_id}: {str(e)}\n{traceback.format_exc()}")
        flash('Failed to restore order.', 'error')

    return redirect(url_for('admin.manage_orders'))

@admin_bp.route('/orders/<order_id>/details')
@login_required
@admin_required
def order_details(order_id):
    """Get order details for modal (AJAX endpoint)"""
    try:
        db = Database()
        
        order_data = db.client.table('orders').select('*').eq('id', order_id).limit(1).execute()
        order = order_data.data[0] if order_data.data else None
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Get customer and seller info
        cust_data = db.client.table('profiles').select('username, first_name, last_name, email').eq('id', order.get('user_id', '')).limit(1).execute()
        cust = cust_data.data[0] if cust_data.data else {}
        sel_data = db.client.table('profiles').select('username, first_name, last_name').eq('id', order.get('seller_id', '')).limit(1).execute()
        sel = sel_data.data[0] if sel_data.data else {}
        
        order['customer_username'] = cust.get('username', 'Unknown')
        order['customer_first_name'] = cust.get('first_name', '')
        order['customer_last_name'] = cust.get('last_name', '')
        order['customer_email'] = cust.get('email', '')
        order['seller_username'] = sel.get('username', 'Unknown')
        order['seller_first_name'] = sel.get('first_name', '')
        order['seller_last_name'] = sel.get('last_name', '')
        
        oi_data = db.client.table('order_items').select('*').eq('order_id', order_id).execute()
        order_items = oi_data.data or []
        for item in order_items:
            p_data = db.client.table('products').select('name, image_url').eq('id', item.get('product_id')).limit(1).execute()
            if p_data.data:
                item['product_name'] = p_data.data[0].get('name', 'Unknown')
                item['image_url'] = p_data.data[0].get('image_url', '')
            else:
                item['product_name'] = 'Unknown'
                item['image_url'] = ''
        
        # Format dates
        co = order.get('created_at')
        if isinstance(co, str):
            try:
                co = datetime.fromisoformat(co.replace('Z', '+00:00'))
            except ValueError:
                co = None
        created_at = co.strftime('%B %d, %Y at %I:%M %p') if co else 'N/A'
        uo = order.get('updated_at')
        if isinstance(uo, str):
            try:
                uo = datetime.fromisoformat(uo.replace('Z', '+00:00'))
            except ValueError:
                uo = None
        updated_at = uo.strftime('%B %d, %Y at %I:%M %p') if uo else 'N/A'
        
        # Status badge color
        status_colors = {
            'pending': 'warning',
            'confirmed': 'primary',
            'preparing': 'info',
            'shipped': 'info',
            'picked_up': 'info',
            'on_the_way': 'info',
            'out_for_delivery': 'info',
            'delivered': 'success',
            'cancelled': 'danger'
        }
        status_color = status_colors.get(order.get('status', 'pending'), 'secondary')
        
        # Build order items HTML
        items_html = ''
        for item in (order_items or []):
            items_html += f"""
                <tr>
                    <td>
                        <div class="d-flex align-items-center">
                            <img src="{'/' + item['image_url'] if item.get('image_url') else '/static/placeholder.png'}" 
                                 class="me-2" style="width: 40px; height: 40px; object-fit: cover;" alt="Product">
                            <div>{item['product_name']}</div>
                        </div>
                    </td>
                    <td>₱{float(item['unit_price']):,.2f}</td>
                    <td>{item['quantity']}</td>
                    <td><strong>₱{float(item['unit_price']) * item['quantity']:,.2f}</strong></td>
                </tr>
            """
        
        # Build HTML
        html = f"""
        <div class="row">
            <div class="col-md-6">
                <h6 class="border-bottom pb-2 mb-3"><i class="fas fa-info-circle"></i> Order Information</h6>
                <div class="row mb-2">
                    <div class="col-sm-5"><strong>Order ID:</strong></div>
                    <div class="col-sm-7">#{order['id']}</div>
                </div>
                <div class="row mb-2">
                    <div class="col-sm-5"><strong>Status:</strong></div>
                    <div class="col-sm-7"><span class="badge bg-{status_color}">{order['status'].replace('_', ' ').title()}</span></div>
                </div>
                <div class="row mb-2">
                    <div class="col-sm-5"><strong>Total Amount:</strong></div>
                    <div class="col-sm-7"><h5 class="mb-0">₱{float(order['total_amount']):,.2f}</h5></div>
                </div>
                <div class="row mb-2">
                    <div class="col-sm-5"><strong>Payment Method:</strong></div>
                    <div class="col-sm-7"><span class="badge bg-info">{order['payment_method'].upper()}</span></div>
                </div>
                <div class="row mb-2">
                    <div class="col-sm-5"><strong>Payment Status:</strong></div>
                    <div class="col-sm-7"><span class="badge bg-secondary">{order.get('payment_status', 'pending').title()}</span></div>
                </div>
                <div class="row mb-2">
                    <div class="col-sm-5"><strong>Created:</strong></div>
                    <div class="col-sm-7">{created_at}</div>
                </div>
                <div class="row mb-2">
                    <div class="col-sm-5"><strong>Updated:</strong></div>
                    <div class="col-sm-7">{updated_at}</div>
                </div>
            </div>
            <div class="col-md-6">
                <h6 class="border-bottom pb-2 mb-3"><i class="fas fa-user"></i> Customer Information</h6>
                <div class="row mb-2">
                    <div class="col-sm-5"><strong>Name:</strong></div>
                    <div class="col-sm-7">{order['customer_first_name']} {order['customer_last_name']}</div>
                </div>
                <div class="row mb-2">
                    <div class="col-sm-5"><strong>Username:</strong></div>
                    <div class="col-sm-7">@{order['customer_username']}</div>
                </div>
                <div class="row mb-2">
                    <div class="col-sm-5"><strong>Email:</strong></div>
                    <div class="col-sm-7">{order['customer_email']}</div>
                </div>
                <h6 class="border-bottom pb-2 mb-3 mt-4"><i class="fas fa-store"></i> Seller Information</h6>
                <div class="row mb-2">
                    <div class="col-sm-5"><strong>Name:</strong></div>
                    <div class="col-sm-7">{order['seller_first_name']} {order['seller_last_name']}</div>
                </div>
                <div class="row mb-2">
                    <div class="col-sm-5"><strong>Username:</strong></div>
                    <div class="col-sm-7">@{order['seller_username']}</div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <h6 class="border-bottom pb-2 mb-3"><i class="fas fa-map-marker-alt"></i> Shipping Address</h6>
                <p>{order.get('shipping_address', 'N/A')}</p>
            </div>
        </div>
        
        {f'<div class="row mt-3"><div class="col-12"><h6 class="border-bottom pb-2 mb-3"><i class="fas fa-sticky-note"></i> Notes</h6><p>{order["notes"]}</p></div></div>' if order.get('notes') else ''}
        
        <div class="row mt-4">
            <div class="col-12">
                <h6 class="border-bottom pb-2 mb-3"><i class="fas fa-shopping-bag"></i> Order Items</h6>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th>Price</th>
                                <th>Quantity</th>
                                <th>Subtotal</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                        <tfoot>
                            <tr>
                                <td colspan="3" class="text-end"><strong>Total:</strong></td>
                                <td><strong>₱{float(order['total_amount']):,.2f}</strong></td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </div>
        </div>
        """
        
        return jsonify({'html': html})
    except Exception as e:
        import traceback
        error_msg = f"Server error: {str(e)}\n{traceback.format_exc()}"
        return jsonify({'error': error_msg}), 500

@admin_bp.route('/orders/<order_id>/update-status', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    """Update order status (admin override)"""
    try:
        from app.models.notification import Notification
        from app.services.websocket_service import socketio
        
        order = Order.get_by_id(order_id)
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        
        new_status = request.form.get('status')
        if not new_status or new_status not in ['pending', 'confirmed', 'preparing', 'shipped', 'picked_up', 'on_the_way', 'out_for_delivery', 'delivered', 'cancelled']:
            return jsonify({'success': False, 'message': 'Invalid status'}), 400
        
        # Update order status
        if Order.update_status(order_id, new_status):
            # Create notification for customer
            Notification.create(
                order['user_id'],
                'customer',
                'order_status_update',
                f'Order #{order_id} Status Updated',
                f'Your order status has been updated to: {new_status.replace("_", " ").title()}',
                related_id=order_id
            )
            
            # Create notification for seller
            Notification.create(
                order['seller_id'],
                'seller',
                'order_status_update',
                f'Order #{order_id} Status Updated',
                f'Order status has been updated to: {new_status.replace("_", " ").title()}',
                related_id=order_id
            )
            
            # Emit WebSocket event
            socketio.emit('order_status_updated', {
                'order_id': order_id,
                'status': new_status,
                'updated_by': 'admin'
            }, room=f'order_{order_id}')
            
            # Log admin action
            AuditLogger.log(
                session['user_id'],
                'order_status_update',
                f'Updated order #{order_id} status to {new_status}',
                {'order_id': order_id, 'old_status': order.get('status'), 'new_status': new_status}
            )
            
            return jsonify({'success': True, 'message': 'Order status updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update order status'}), 500
            
    except Exception as e:
        import traceback
        current_app.logger.error(f"Error updating order status: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

@admin_bp.route('/orders/<order_id>/assign-rider', methods=['POST'])
@login_required
@admin_required
def assign_rider_to_order(order_id):
    """Assign a rider to an order (admin)"""
    try:
        from app.models.delivery import Delivery
        from app.models.notification import Notification
        from app.services.websocket_service import socketio
        
        order = Order.get_by_id(order_id)
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        
        rider_id = request.form.get('rider_id', type=int)
        if not rider_id:
            return jsonify({'success': False, 'message': 'Rider ID is required'}), 400
        
        # Verify rider exists and is active
        rider = User.get_by_id(rider_id)
        if not rider or rider.get('role') != 'rider':
            return jsonify({'success': False, 'message': 'Invalid rider'}), 400
        
        # Assign rider using Delivery model
        if Delivery.assign_rider(order_id, rider_id, 'Assigned by admin'):
            # Update order status directly to picked_up (no assigned_to_rider intermediate state)
            if order.get('status') in ['pending', 'confirmed', 'preparing', 'shipped']:
                Order.update_status(order_id, 'picked_up', rider_id=rider_id)
            
            # Create notifications
            Notification.create(
                rider_id,
                'rider',
                'order_assigned',
                f'New Delivery Assignment',
                f'You have been assigned to deliver order #{order_id}',
                related_id=order_id
            )
            
            Notification.create(
                order['seller_id'],
                'seller',
                'rider_assigned',
                f'Rider Assigned to Order #{order_id}',
                f'A rider has been assigned to deliver order #{order_id}',
                related_id=order_id
            )
            
            # Emit WebSocket event
            socketio.emit('rider_assigned', {
                'order_id': order_id,
                'rider_id': rider_id
            }, room=f'order_{order_id}')
            
            # Log admin action
            AuditLogger.log(
                session['user_id'],
                'rider_assignment',
                f'Assigned rider {rider_id} to order #{order_id}',
                {'order_id': order_id, 'rider_id': rider_id}
            )
            
            return jsonify({
                'success': True, 
                'message': f'Rider {rider.get("first_name")} {rider.get("last_name")} assigned successfully'
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to assign rider'}), 500
            
    except Exception as e:
        import traceback
        current_app.logger.error(f"Error assigning rider: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

@admin_bp.route('/orders/bulk-action', methods=['POST'])
@login_required
@admin_required
def bulk_order_action():
    """Handle bulk actions on orders (admin)"""
    try:
        action = request.form.get('action')
        order_ids = request.form.getlist('order_ids')
        
        if not action or not order_ids:
            return jsonify({'success': False, 'message': 'Action and order IDs are required'}), 400
        
        if action not in ['update_status', 'assign_rider', 'cancel', 'export']:
            return jsonify({'success': False, 'message': 'Invalid action'}), 400
        
        success_count = 0
        errors = []
        
        if action == 'update_status':
            new_status = request.form.get('status')
            if not new_status:
                return jsonify({'success': False, 'message': 'Status is required'}), 400
            
            for order_id_str in order_ids:
                try:
                    order_id = int(order_id_str)
                    if Order.update_status(order_id, new_status):
                        success_count += 1
                    else:
                        errors.append(f"Order #{order_id}: Failed to update")
                except Exception as e:
                    errors.append(f"Order #{order_id_str}: {str(e)}")
        
        elif action == 'cancel':
            for order_id_str in order_ids:
                try:
                    order_id = int(order_id_str)
                    order = Order.get_by_id(order_id)
                    if order and order.get('status') not in ['delivered', 'cancelled']:
                        if Order.update_status(order_id, 'cancelled'):
                            db = Database()
                            items_data = db.client.table('order_items').select('*').eq('order_id', order_id).execute()
                            for item in (items_data.data or []):
                                prod = db.client.table('products').select('stock_quantity').eq('id', item['product_id']).limit(1).execute()
                                if prod.data:
                                    new_qty = int(prod.data[0].get('stock_quantity', 0) or 0) + int(item.get('quantity', 0) or 0)
                                    db.client.table('products').update({'stock_quantity': new_qty}).eq('id', item['product_id']).execute()
                            success_count += 1
                        else:
                            errors.append(f"Order #{order_id}: Failed to cancel")
                    else:
                        errors.append(f"Order #{order_id}: Cannot cancel")
                except Exception as e:
                    errors.append(f"Order #{order_id_str}: {str(e)}")
        
        # Log bulk action
        AuditLogger.log(
            session['user_id'],
            'bulk_order_action',
            f'Bulk {action} on {len(order_ids)} orders',
            {'action': action, 'order_ids': order_ids, 'success_count': success_count}
        )
        
        message = f'{success_count} order(s) processed successfully'
        if errors:
            message += f'. {len(errors)} error(s) occurred.'
        
        return jsonify({
            'success': success_count > 0,
            'message': message,
            'success_count': success_count,
            'errors': errors[:10]  # Limit errors shown
        })
        
    except Exception as e:
        import traceback
        current_app.logger.error(f"Error in bulk action: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

@admin_bp.route('/orders/<order_id>/refund', methods=['POST'])
@login_required
@admin_required
def process_refund(order_id):
    """Process refund for an order (admin)"""
    try:
        from app.models.notification import Notification
        
        order = Order.get_by_id(order_id)
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        
        refund_amount = request.form.get('refund_amount', type=float)
        refund_reason = request.form.get('refund_reason', '').strip()
        
        if not refund_amount or refund_amount <= 0:
            return jsonify({'success': False, 'message': 'Invalid refund amount'}), 400
        
        if refund_amount > float(order.get('total_amount', 0)):
            return jsonify({'success': False, 'message': 'Refund amount cannot exceed order total'}), 400
        
        # Update payment status to refunded
        Order.update_payment_status(order_id, 'refunded')
        
        # Update order status if needed
        if order.get('status') != 'cancelled':
            Order.update_status(order_id, 'cancelled')
        
        db = Database()
        items_data = db.client.table('order_items').select('*').eq('order_id', order_id).execute()
        for item in (items_data.data or []):
            prod = db.client.table('products').select('stock_quantity').eq('id', item['product_id']).limit(1).execute()
            if prod.data:
                new_qty = int(prod.data[0].get('stock_quantity', 0) or 0) + int(item.get('quantity', 0) or 0)
                db.client.table('products').update({'stock_quantity': new_qty}).eq('id', item['product_id']).execute()
        
        # Create notification for customer
        Notification.create(
            order['user_id'],
            'customer',
            'refund_processed',
            f'Refund Processed for Order #{order_id}',
            f'Your refund of ₱{refund_amount:,.2f} has been processed. Reason: {refund_reason or "N/A"}',
            related_id=order_id
        )
        
        # Log admin action
        AuditLogger.log(
            session['user_id'],
            'refund_processed',
            f'Processed refund of ₱{refund_amount:,.2f} for order #{order_id}',
            {'order_id': order_id, 'refund_amount': refund_amount, 'reason': refund_reason}
        )
        
        return jsonify({
            'success': True,
            'message': f'Refund of ₱{refund_amount:,.2f} processed successfully'
        })
        
    except Exception as e:
        import traceback
        current_app.logger.error(f"Error processing refund: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

@admin_bp.route('/riders/available')
@login_required
@admin_required
def get_available_riders():
    """Get list of available riders for admin assignment"""
    try:
        from app.models.rider_availability import RiderAvailability
        
        riders = RiderAvailability.get_available_riders()
        
        # Format response
        riders_list = []
        for rider in riders:
            riders_list.append({
                'id': rider.get('id'),
                'first_name': rider.get('first_name', ''),
                'last_name': rider.get('last_name', ''),
                'phone': rider.get('phone', 'N/A'),
                'email': rider.get('email', ''),
                'current_lat': rider.get('current_lat'),
                'current_lng': rider.get('current_lng')
            })
        
        return jsonify({'riders': riders_list})
        
    except Exception as e:
        import traceback
        current_app.logger.error(f"Error getting available riders: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'riders': [], 'error': 'Failed to fetch riders'}), 500

@admin_bp.route('/commission-report')
@login_required
@admin_required
def commission_report():
    """Admin commission report (5% of PRODUCT PRICE ONLY) with date/status filters and printable page."""
    db = Database()
    start = request.args.get('start')
    end = request.args.get('end')
    status = request.args.get('status', 'delivered')
    
    query = db.client.table('orders').select('*').order('created_at', desc=True).limit(500)
    if status and status != 'all':
        query = query.eq('status', status)
    if start:
        query = query.gte('created_at', start)
    if end:
        query = query.lte('created_at', end)
    
    orders_data = query.execute()
    rows = orders_data.data or []
    
    seller_ids = list(set(str(o.get('seller_id')) for o in rows if o.get('seller_id')))
    seller_map = {}
    for sid in seller_ids:
        sp = db.client.table('profiles').select('first_name, last_name').eq('id', sid).limit(1).execute()
        if sp.data:
            seller_map[sid] = sp.data[0]
    
    for r in rows:
        product_total = float(r.get('product_total') or 0)
        stored_commission = float(r.get('admin_commission') or 0)
        r['commission'] = stored_commission if stored_commission > 0 else round(product_total * 0.05, 2)
        r['product_total'] = product_total
        sel = seller_map.get(str(r.get('seller_id', '')), {})
        r['seller_name'] = f"{sel.get('first_name','')} {sel.get('last_name','')}".strip()
    
    total_sales = round(sum(float(r.get('product_total') or 0) for r in rows), 2)
    total_commission = round(sum(float(r.get('commission') or 0) for r in rows), 2)
    
    return render_template('admin/commission_report.html', rows=rows, total_sales=total_sales, total_commission=total_commission, start=start, end=end, status=status)

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """Analytics and reports"""
    db = Database()
    analytics_data = {}

    orders_data = (db.client.table('orders').select('*').execute().data) or []
    active_orders = [o for o in orders_data if o.get('status') != 'cancelled']

    analytics_data['total_orders'] = len(orders_data)
    analytics_data['total_revenue'] = sum(float(o.get('total_amount', 0) or 0) for o in active_orders)

    now = datetime.now()
    thirty_days_ago = (now - timedelta(days=30)).isoformat()
    sixty_days_ago = (now - timedelta(days=60)).isoformat()

    current_count = sum(1 for o in orders_data if (o.get('created_at') or '') >= thirty_days_ago)
    previous_count = sum(1 for o in orders_data if sixty_days_ago <= (o.get('created_at') or '') < thirty_days_ago)
    previous_count = previous_count or 1
    analytics_data['growth_rate'] = ((current_count - previous_count) / previous_count) * 100

    analytics_data['avg_rating'] = 4.2
    analytics_data['top_products'] = []
    analytics_data['conversion_rate'] = 3.5

    avg_val = 0.0
    if active_orders:
        avg_val = sum(float(o.get('total_amount', 0) or 0) for o in active_orders) / len(active_orders)
    analytics_data['avg_order_value'] = avg_val
    analytics_data['retention_rate'] = 65.0

    active_sellers = len(set(str(o.get('seller_id')) for o in active_orders if o.get('seller_id') and (o.get('created_at') or '') >= thirty_days_ago))
    analytics_data['active_sellers'] = active_sellers

    seven_days_ago = (now - timedelta(days=7)).isoformat()
    recent_orders = sum(1 for o in orders_data if (o.get('created_at') or '') >= seven_days_ago)
    profiles_data = (db.client.table('profiles').select('created_at').gte('created_at', seven_days_ago).execute().data) or []
    recent_users = len(profiles_data)
    products_data = (db.client.table('products').select('*').gte('created_at', seven_days_ago).execute().data) or []
    recent_products = len(products_data)
    analytics_data['recent_activity'] = [
        {'type': 'orders', 'count': recent_orders},
        {'type': 'users', 'count': recent_users},
        {'type': 'products', 'count': recent_products}
    ]

    six_months_ago = (now - timedelta(days=180)).isoformat()
    monthly_map = {}
    for o in orders_data:
        if o.get('status') == 'cancelled':
            continue
        created = o.get('created_at', '')
        if created >= six_months_ago:
            try:
                dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                key = dt.strftime('%Y-%m')
                label = dt.strftime('%b')
                if key not in monthly_map:
                    monthly_map[key] = {'label': label, 'revenue': 0.0, 'orders': 0}
                monthly_map[key]['revenue'] += float(o.get('total_amount', 0) or 0)
                monthly_map[key]['orders'] += 1
            except Exception:
                pass

    sorted_months = sorted(monthly_map.keys())
    analytics_data['monthly_labels'] = [monthly_map[m]['label'] for m in sorted_months]
    analytics_data['monthly_revenue'] = [monthly_map[m]['revenue'] for m in sorted_months]
    analytics_data['monthly_users'] = []

    return render_template('admin/analytics.html', analytics=analytics_data)

@admin_bp.route('/system-settings', methods=['GET', 'POST'])
@login_required
@admin_required
def system_settings():
    """System settings and configuration"""
    from app.utils.settings import Settings
    
    db = Database()
    
    if request.method == 'POST':
        form = SystemSettingsForm()
        
        if form.validate_on_submit():
            try:
                # Save all settings to database
                settings_to_save = {
                    'site_name': form.site_name.data,
                    'site_description': form.site_description.data,
                    'admin_email': form.admin_email.data,
                    'support_email': form.support_email.data,
                    'maintenance_mode': form.maintenance_mode.data,
                    'max_products_per_seller': str(form.max_products_per_seller.data) if form.max_products_per_seller.data else '100',
                    'order_auto_cancel_days': str(form.order_auto_cancel_days.data) if form.order_auto_cancel_days.data else '7',
                    'featured_products_limit': str(form.featured_products_limit.data) if form.featured_products_limit.data else '10',
                    'default_currency': form.default_currency.data,
                    'timezone': form.timezone.data,
                    'require_email_verification': form.require_email_verification.data,
                    'session_lifetime': str(form.session_lifetime.data) if form.session_lifetime.data else '60',
                    'max_login_attempts': str(form.max_login_attempts.data) if form.max_login_attempts.data else '5',
                    'enable_cod': form.enable_cod.data,
                    'enable_card': form.enable_card.data,
                    'payment_provider': form.payment_provider.data if form.payment_provider.data else 'none',
                    'payment_public_key': form.payment_public_key.data if form.payment_public_key.data else '',
                    'smtp_host': form.smtp_host.data if form.smtp_host.data else '',
                    'smtp_port': str(form.smtp_port.data) if form.smtp_port.data else '587',
                    'smtp_tls': form.smtp_tls.data,
                    'email_from': form.email_from.data if form.email_from.data else '',
                    'email_theme': form.email_theme.data if form.email_theme.data else 'default'
                }
                
                Settings.set_multiple(settings_to_save)
                flash('System settings updated successfully!', 'success')
                return redirect(url_for('admin.system_settings'))
            except Exception as e:
                flash(f'Error saving settings: {str(e)}', 'error')
    
    # Load current settings from database
    current_settings = Settings.get_all()
    
    # Convert integer fields to integers for the form
    if current_settings:
        for key in ['max_products_per_seller', 'order_auto_cancel_days', 'featured_products_limit', 'session_lifetime', 'max_login_attempts', 'smtp_port']:
            if key in current_settings and current_settings[key]:
                try:
                    current_settings[key] = int(current_settings[key])
                except (ValueError, TypeError):
                    pass
    
    form = SystemSettingsForm(data=current_settings)
    
    cats_data = db.client.table('categories').select('*').order('name').execute()
    categories = cats_data.data or []
    
    return render_template('admin/system_settings.html',
                         categories=categories,
                         form=form)

@admin_bp.route('/bulk-actions', methods=['POST'])
@login_required
@admin_required
def bulk_actions():
    """Handle bulk actions for users/products"""
    action = request.form.get('bulk_action')
    selected_items = request.form.getlist('selected_items')
    
    if not selected_items:
        flash('No items selected.', 'error')
        return redirect(request.referrer or url_for('admin.dashboard'))
    
    # Keep as strings to support UUID primary keys
    try:
        selected_ids = [str(id) for id in selected_items]
    except (ValueError, TypeError):
        flash('Invalid selection.', 'error')
        return redirect(request.referrer or url_for('admin.dashboard'))
    
    success_count = 0
    
    if action == 'activate_users':
        for user_id in selected_ids:
            if user_id != session['user_id']:  # Don't affect current admin
                try:
                    user = User.get_by_id(user_id)
                    previous_status = (user.get('status') or '').strip().lower() if user else ''
                    user_role = (user.get('role') or '').strip().lower() if user else ''

                    User.update_status(user_id, 'active')

                    # Notify buyer approval when transitioned to active from any non-active state.
                    if user and user_role == 'user' and previous_status != 'active':
                        Notification.create(
                            user_id=user_id,
                            role='user',
                            type_='general',
                            title='Buyer Account Approved',
                            message='Your buyer account has been approved. You can now log in to Pawfect Finds.',
                            data={'account_type': 'user', 'status': 'approved'}
                        )
                        email_sent = EmailService.send_application_status_email(
                            user.get('email'),
                            account_type='user',
                            status='approved'
                        )
                        current_app.logger.info(
                            'Bulk buyer approval email dispatch user_id=%s email=%s sent=%s',
                            user_id,
                            user.get('email'),
                            email_sent
                        )

                    success_count += 1
                except Exception:
                    current_app.logger.exception('Failed bulk activate for user_id=%s', user_id)
        flash(f'{success_count} users activated.', 'success')
    
    elif action == 'deactivate_users':
        for user_id in selected_ids:
            if user_id != session['user_id']:  # Don't affect current admin
                try:
                    user = User.get_by_id(user_id)
                    previous_status = (user.get('status') or '').strip().lower() if user else ''
                    user_role = (user.get('role') or '').strip().lower() if user else ''

                    User.update_status(user_id, 'inactive')

                    # Treat pending -> inactive as rejection for buyer applications.
                    if user and user_role == 'user' and previous_status == 'pending':
                        Notification.create(
                            user_id=user_id,
                            role='user',
                            type_='general',
                            title='Buyer Account Rejected',
                            message='Your buyer account was not approved. Please contact support for details.',
                            data={'account_type': 'user', 'status': 'rejected'}
                        )
                        EmailService.send_application_status_email(
                            user.get('email'),
                            account_type='user',
                            status='rejected'
                        )

                    success_count += 1
                except Exception:
                    current_app.logger.exception('Failed bulk deactivate for user_id=%s', user_id)
        flash(f'{success_count} users deactivated.', 'info')
    
    elif action == 'ban_users':
        for user_id in selected_ids:
            if user_id != session['user_id']:  # Don't affect current admin
                try:
                    User.update_status(user_id, 'banned')
                    success_count += 1
                except:
                    pass
        flash(f'{success_count} users banned.', 'warning')
    
    elif action == 'deactivate_products':
        for product_id in selected_ids:
            try:
                Product.update(product_id, status='inactive')
                success_count += 1
            except:
                pass
        flash(f'{success_count} products deactivated.', 'info')
    
    elif action == 'activate_products':
        for product_id in selected_ids:
            try:
                Product.update(product_id, status='active')
                success_count += 1
            except:
                pass
        flash(f'{success_count} products activated.', 'success')
    
    return redirect(request.referrer or url_for('admin.dashboard'))

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    """Detailed reports page"""
    db = Database()
    
    now = datetime.now()
    twelve_months_ago = (now - timedelta(days=365)).isoformat()
    
    orders_data = (db.client.table('orders').select('*').gte('created_at', twelve_months_ago).execute().data) or []
    
    monthly_map = {}
    for o in orders_data:
        if o.get('status') == 'cancelled':
            continue
        created = o.get('created_at', '')
        try:
            dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
            key = dt.strftime('%Y-%m')
            if key not in monthly_map:
                monthly_map[key] = {'orders': 0, 'revenue': 0.0}
            monthly_map[key]['orders'] += 1
            monthly_map[key]['revenue'] += float(o.get('total_amount', 0) or 0)
        except Exception:
            pass
    sorted_months_desc = sorted(monthly_map.keys(), reverse=True)
    monthly_revenue = [{'month': m, 'orders': monthly_map[m]['orders'], 'revenue': monthly_map[m]['revenue']} for m in sorted_months_desc]
    
    profiles_data = (db.client.table('profiles').select('created_at').gte('created_at', twelve_months_ago).execute().data) or []
    user_monthly = {}
    for p in profiles_data:
        created = p.get('created_at', '')
        try:
            dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
            key = dt.strftime('%Y-%m')
            user_monthly[key] = user_monthly.get(key, 0) + 1
        except Exception:
            pass
    user_growth = [{'month': m, 'new_users': user_monthly[m]} for m in sorted(user_monthly.keys(), reverse=True)]
    
    order_status_map = {}
    for o in orders_data:
        s = o.get('status', 'unknown')
        order_status_map[s] = order_status_map.get(s, 0) + 1
    order_status_stats = [{'status': k, 'count': v} for k, v in sorted(order_status_map.items(), key=lambda x: x[1], reverse=True)]
    
    product_performance = []
    
    return render_template('admin/reports.html',
                         monthly_revenue=monthly_revenue,
                         user_growth=user_growth,
                         product_performance=product_performance,
                         order_status_stats=order_status_stats)

@admin_bp.route('/categories/add', methods=['POST'])
@login_required
@admin_required
def add_category():
    """Add new category"""
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        description = form.description.data.strip() if form.description.data else None
        
        db = Database()
        try:
            db.client.table('categories').insert({'name': name, 'description': description, 'is_active': True}).execute()
            flash('Category added successfully!', 'success')
        except Exception as e:
            flash('Failed to add category. Name may already exist.', 'error')
    else:
        flash('Please correct the errors in the form.', 'error')
    
    return redirect(url_for('admin.system_settings'))

@admin_bp.route('/categories/<int:category_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_category(category_id):
    """Toggle category active status"""
    db = Database()
    try:
        current_data = db.client.table('categories').select('is_active').eq('id', category_id).limit(1).execute()
        current = current_data.data[0] if current_data.data else None
        if current:
            new_status = not current.get('is_active', True)
            db.client.table('categories').update({'is_active': new_status}).eq('id', category_id).execute()
            status_text = "activated" if new_status else "deactivated"
            flash(f'Category {status_text} successfully!', 'success')
        else:
            flash('Category not found.', 'error')
    except Exception as e:
        flash('Failed to update category status.', 'error')
    
    return redirect(url_for('admin.system_settings'))


@admin_bp.route('/ban-user', methods=['POST'])
@login_required
@admin_required
def ban_user():
    """Ban a user"""
    user_id = request.form.get('user_id')
    if not user_id:
        flash('User ID not provided.', 'error')
        return redirect(url_for('admin.manage_users'))

    try:
        user_id = str(user_id)
    except (ValueError, TypeError):
        flash('Invalid user ID.', 'error')
        return redirect(url_for('admin.manage_users'))

    # Prevent admin from banning themselves
    if str(user_id) == str(session['user_id']):
        flash('You cannot ban yourself.', 'error')
        return redirect(url_for('admin.manage_users'))

    try:
        User.update_status(user_id, 'banned')
        flash('User banned successfully.', 'warning')
    except Exception as e:
        flash('Failed to ban user.', 'error')

    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/revoke-seller', methods=['POST'])
@login_required
@admin_required
def revoke_seller():
    """Revoke seller status from a user"""
    user_id = request.form.get('user_id')
    if not user_id:
        flash('User ID not provided.', 'error')
        return redirect(url_for('admin.manage_users'))

    try:
        user_id = str(user_id)
    except (ValueError, TypeError):
        flash('Invalid user ID.', 'error')
        return redirect(url_for('admin.manage_users'))

    # Prevent admin from revoking their own seller status (though admin is not seller)
    if str(user_id) == str(session['user_id']):
        flash('You cannot revoke your own seller status.', 'error')
        return redirect(url_for('admin.manage_users'))

    try:
        User.update_role(user_id, 'user')
        flash('Seller status revoked successfully.', 'info')
    except Exception as e:
        flash('Failed to revoke seller status.', 'error')

    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/unban-user', methods=['POST'])
@login_required
@admin_required
def unban_user():
    """Unban a user"""
    user_id = request.form.get('user_id')
    if not user_id:
        flash('User ID not provided.', 'error')
        return redirect(url_for('admin.manage_users'))

    try:
        user_id = str(user_id)
    except (ValueError, TypeError):
        flash('Invalid user ID.', 'error')
        return redirect(url_for('admin.manage_users'))

    # Prevent admin from unbanning themselves
    if str(user_id) == str(session['user_id']):
        flash('You cannot unban yourself.', 'error')
        return redirect(url_for('admin.manage_users'))

    try:
        User.update_status(user_id, 'active')
        flash('User unbanned successfully.', 'success')
    except Exception as e:
        flash('Failed to unban user.', 'error')

    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/user/<user_id>/details')
@login_required
@admin_required
def user_details(user_id):
    """Get user details for modal"""
    try:
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        first_name = user.get('first_name') or ''
        last_name = user.get('last_name') or ''
        username = user.get('username') or ''
        avatar_initial = first_name[0].upper() if first_name else (username[0].upper() if username else '?')
        full_name = f"{first_name} {last_name}".strip()
        if not full_name:
            full_name = username

        db = Database()
        orders_data = db.client.table('orders').select('id', count='exact').eq('user_id', user_id).execute()
        orders_count = orders_data.count if hasattr(orders_data, 'count') else len(orders_data.data or [])

        products_count = 0
        if user.get('role') == 'seller':
            prod_data = db.client.table('products').select('id', count='exact').eq('seller_id', user_id).execute()
            products_count = prod_data.count if hasattr(prod_data, 'count') else len(prod_data.data or [])

        created_at = user.get('created_at')
        created_at_str = ''
        if created_at:
            try:
                dt = datetime.fromisoformat(str(created_at).replace('Z', '+00:00'))
                created_at_str = dt.strftime('%B %d, %Y')
            except Exception:
                created_at_str = str(created_at)
        else:
            created_at_str = 'Unknown'

        status = user.get('status') or 'active'
        status_class = 'success' if status == 'active' else 'danger' if status == 'banned' else 'secondary'

        html = f"""
        <div class="row">
            <div class="col-md-4 text-center">
                <div class="avatar-circle bg-primary text-white mx-auto mb-3" style="width: 80px; height: 80px; font-size: 2em;">
                    {avatar_initial}
                </div>
                <h5>{full_name}</h5>
                <p class="text-muted">@{username}</p>
            </div>
            <div class="col-md-8">
                <div class="row">
                    <div class="col-sm-6">
                        <strong>Email:</strong> {user.get('email') or 'N/A'}
                    </div>
                    <div class="col-sm-6">
                        <strong>Role:</strong> <span class="badge bg-secondary">{user.get('role', '').title()}</span>
                    </div>
                    <div class="col-sm-6">
                        <strong>Status:</strong> <span class="badge bg-{status_class}">{status.title()}</span>
                    </div>
                    <div class="col-sm-6">
                        <strong>Joined:</strong> {created_at_str}
                    </div>
                    <div class="col-sm-6">
                        <strong>Orders:</strong> {orders_count}
                    </div>
                    {'<div class="col-sm-6"><strong>Products:</strong> ' + str(products_count) + '</div>' if user.get('role') == 'seller' else ''}
                </div>
            </div>
        </div>
        """

        return jsonify({'html': html})
    except Exception as e:
        import traceback
        error_msg = f"Server error: {str(e)}\n{traceback.format_exc()}"
        return jsonify({'error': error_msg}), 500

@admin_bp.route('/add-user', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """Add a new user"""
    from app.forms import SignupForm

    form = SignupForm()
    if form.validate_on_submit():
        try:
            # Create new user
            user_data = {
                'first_name': form.first_name.data,
                'last_name': form.last_name.data,
                'username': form.username.data,
                'email': form.email.data,
                'password': form.password.data,
                'phone': form.phone.data,
                'address': form.address.data,
                'role': 'user',  # Default role
                'status': 'active'
            }

            User.create(user_data)
            flash('User created successfully!', 'success')
            return redirect(url_for('admin.manage_users'))

        except Exception as e:
            flash('Failed to create user. Email or username may already exist.', 'error')

    return render_template('admin/add_user.html', form=form)

@admin_bp.route('/audit-logs')
@login_required
@admin_required
def audit_logs():
    """View audit logs with filtering"""
    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page
    
    # Get filters
    action_filter = request.args.get('action', '').strip()
    user_filter = request.args.get('user', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()
    
    # Convert date strings to datetime objects
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
    user_filter_id = int(user_filter) if user_filter.isdigit() else None
    
    # Get logs
    logs = AuditLogger.get_logs(
        limit=per_page,
        offset=offset,
        action_filter=action_filter if action_filter else None,
        user_filter=user_filter_id,
        date_from=date_from_obj,
        date_to=date_to_obj
    )
    
    # Get total count for pagination
    total_logs = AuditLogger.get_log_count(
        action_filter=action_filter if action_filter else None,
        user_filter=user_filter_id,
        date_from=date_from_obj,
        date_to=date_to_obj
    )
    
    total_pages = (total_logs + per_page - 1) // per_page
    
    return render_template('admin/audit_logs.html',
                         logs=logs,
                         page=page,
                         total_pages=total_pages,
                         total_logs=total_logs,
                         action_filter=action_filter,
                         user_filter=user_filter,
                         date_from=date_from,
                         date_to=date_to)

@admin_bp.route('/export/users')
@login_required
@admin_required
def export_users():
    """Export users to CSV"""
    try:
        role_filter = request.args.get('role', '').strip()
        status_filter = request.args.get('status', '').strip()
        search_query = request.args.get('search', '').strip()
        
        db = Database()
        query = db.client.table('profiles').select('*').order('created_at', desc=True)
        if role_filter:
            query = query.eq('role', role_filter)
        if status_filter:
            query = query.eq('status', status_filter)
        if search_query:
            sq = f"%{search_query}%"
            query = query.or_(f"username.ilike.{sq},email.ilike.{sq},first_name.ilike.{sq},last_name.ilike.{sq}")
        
        result = query.execute()
        users = result.data or []
        
        filename = ExportHelper.generate_filename('users_export')
        AuditLogger.log_action('EXPORT_USERS', f"Exported {len(users)} users to CSV", session.get('user_id'))
        return ExportHelper.export_users_csv(users, filename)
    except Exception as e:
        import traceback
        print(f"Export error: {str(e)}")
        print(traceback.format_exc())
        flash('Failed to export users.', 'error')
        return redirect(url_for('admin.manage_users'))

@admin_bp.route('/export/orders')
@login_required
@admin_required
def export_orders():
    """Export orders to CSV"""
    try:
        status_filter = request.args.get('status', '').strip()
        search_query = request.args.get('search', '').strip()
        
        db = Database()
        order_query = db.client.table('orders').select('*').order('created_at', desc=True)
        if status_filter:
            order_query = order_query.eq('status', status_filter)
        orders_data = order_query.execute()
        orders = orders_data.data or []
        for o in orders:
            cust = db.client.table('profiles').select('first_name, last_name, email').eq('id', o.get('user_id', '')).limit(1).execute()
            if cust.data:
                o['customer_name'] = f"{cust.data[0].get('first_name', '')} {cust.data[0].get('last_name', '')}".strip()
                o['customer_email'] = cust.data[0].get('email', '')
        
        if search_query:
            sq = search_query.lower()
            orders = [o for o in orders if sq in str(o.get('order_number', '')).lower() or sq in o.get('customer_name', '').lower() or sq in o.get('customer_email', '').lower()]
        
        filename = ExportHelper.generate_filename('orders_export')
        AuditLogger.log_action('EXPORT_ORDERS', f"Exported {len(orders)} orders to CSV", session.get('user_id'))
        return ExportHelper.export_orders_csv(orders, filename)
    except Exception as e:
        import traceback
        print(f"Export error: {str(e)}")
        print(traceback.format_exc())
        flash('Failed to export orders.', 'error')
        return redirect(url_for('admin.manage_orders'))

@admin_bp.route('/export/audit-logs')
@login_required
@admin_required
def export_audit_logs():
    """Export audit logs to CSV"""
    try:
        # Get filters
        action_filter = request.args.get('action', '').strip()
        date_from = request.args.get('date_from', '').strip()
        date_to = request.args.get('date_to', '').strip()
        
        # Convert dates
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
        
        # Get all logs matching filters
        logs = AuditLogger.get_logs(
            limit=10000,  # Large limit for export
            offset=0,
            action_filter=action_filter if action_filter else None,
            date_from=date_from_obj,
            date_to=date_to_obj
        )
        
        if not logs:
            logs = []
        
        # Generate filename
        filename = ExportHelper.generate_filename('audit_logs_export')
        
        # Log export action
        AuditLogger.log_action(
            'EXPORT_AUDIT_LOGS',
            f"Exported {len(logs)} audit logs to CSV",
            session.get('user_id')
        )
        
        return ExportHelper.export_audit_logs_csv(logs, filename)

    except Exception as e:
        import traceback
        print(f"Export error: {str(e)}")
        print(traceback.format_exc())
        flash('Failed to export audit logs.', 'error')
        return redirect(url_for('admin.audit_logs'))

@admin_bp.route('/rider-payouts')
@login_required
@admin_required
def rider_payouts():
    """View and manage rider payout requests"""
    status_filter = request.args.get('status', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page
    
    db = Database()
    
    payout_query = db.client.table('payout_requests').select('*').order('requested_at', desc=True)
    if status_filter:
        payout_query = payout_query.eq('status', status_filter)
    
    try:
        payouts_data = payout_query.range(offset, offset + per_page - 1).execute()
        payouts = payouts_data.data or []
    except Exception:
        payouts = []
    
    for p in payouts:
        rider = db.client.table('profiles').select('first_name, last_name, email, username').eq('id', p.get('rider_id', '')).limit(1).execute()
        if rider.data:
            p['first_name'] = rider.data[0].get('first_name', '')
            p['last_name'] = rider.data[0].get('last_name', '')
            p['email'] = rider.data[0].get('email', '')
            p['username'] = rider.data[0].get('username', '')
    
    try:
        all_payouts = db.client.table('payout_requests').select('status, amount').execute()
        all_p = all_payouts.data or []
    except Exception:
        all_p = []
    stats = {
        'pending_amount': sum(float(p.get('amount', 0) or 0) for p in all_p if p.get('status') == 'pending'),
        'pending_count': sum(1 for p in all_p if p.get('status') == 'pending'),
        'approved_amount': sum(float(p.get('amount', 0) or 0) for p in all_p if p.get('status') == 'approved'),
        'approved_count': sum(1 for p in all_p if p.get('status') == 'approved'),
        'paid_amount': sum(float(p.get('amount', 0) or 0) for p in all_p if p.get('status') == 'paid'),
        'paid_count': sum(1 for p in all_p if p.get('status') == 'paid'),
    }
    
    total = len(all_p)
    total_pages = (total + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    
    return render_template('admin/payouts.html',
                         payouts=payouts,
                         stats=stats,
                         status_filter=status_filter,
                         current_page=page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         prev_page=page-1 if has_prev else None,
                         next_page=page+1 if has_next else None)

@admin_bp.route('/rider-payouts/<int:payout_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_payout(payout_id):
    """Approve a payout request"""
    try:
        db = Database()
        payout_data = db.client.table('payout_requests').select('*').eq('id', payout_id).limit(1).execute()
        payout = payout_data.data[0] if payout_data.data else None
        
        if not payout:
            flash('Payout request not found.', 'error')
            return redirect(url_for('admin.rider_payouts'))
        
        rider_id = payout.get('rider_id')
        amount = payout.get('amount', 0)
        
        db.client.table('payout_requests').update({'status': 'approved', 'approved_at': datetime.now().isoformat()}).eq('id', payout_id).execute()
        
        flash('Payout request approved.', 'success')
    except Exception as e:
        current_app.logger.error(f"Error approving payout: {e}")
        flash('Failed to approve payout request. The payout_requests table may not exist yet.', 'error')
    
    return redirect(url_for('admin.rider_payouts'))

@admin_bp.route('/rider-payouts/<int:payout_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_payout(payout_id):
    """Reject a payout request"""
    try:
        admin_notes = request.form.get('admin_notes', '').strip()
        db = Database()
        db.client.table('payout_requests').update({'status': 'rejected', 'admin_notes': admin_notes}).eq('id', payout_id).execute()
        flash('Payout request rejected.', 'success')
    except Exception as e:
        flash('Failed to reject payout request. The payout_requests table may not exist yet.', 'error')
    
    return redirect(url_for('admin.rider_payouts'))

@admin_bp.route('/rider-payouts/<int:payout_id>/mark-paid', methods=['POST'])
@login_required
@admin_required
def mark_payout_paid(payout_id):
    """Mark a payout as paid"""
    try:
        admin_notes = request.form.get('admin_notes', '').strip()
        db = Database()
        
        payout_data = db.client.table('payout_requests').select('*').eq('id', payout_id).limit(1).execute()
        payout = payout_data.data[0] if payout_data.data else None
        
        if not payout:
            flash('Payout request not found.', 'error')
            return redirect(url_for('admin.rider_payouts'))
        
        db.client.table('payout_requests').update({'status': 'paid', 'paid_at': datetime.now().isoformat(), 'admin_notes': admin_notes}).eq('id', payout_id).execute()
        
        flash('Payout marked as paid.', 'success')
    except Exception as e:
        current_app.logger.error(f"Error marking payout as paid: {e}")
        flash('Failed to mark payout as paid. The payout_requests table may not exist yet.', 'error')
    
    return redirect(url_for('admin.rider_payouts'))
