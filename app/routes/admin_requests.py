# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.utils.auth import role_required, get_current_user
from app.models.seller_request import SellerRequest
from app.models.rider import Rider
from app.models.user import User
from app.services.email_service import EmailService
from datetime import datetime

admin_requests_bp = Blueprint('admin_requests', __name__, url_prefix='/admin')

# ===================== SELLER REQUESTS =====================

@admin_requests_bp.route('/seller-requests')
@role_required('admin')
def seller_requests():
    """View all seller requests"""
    status_filter = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    
    # Get all requests
    all_requests = SellerRequest.get_all_requests()
    
    # Filter by status if provided
    if status_filter:
        all_requests = [req for req in all_requests if req.get('status') == status_filter]
    
    # Simple pagination
    per_page = 10
    total = len(all_requests)
    start = (page - 1) * per_page
    end = start + per_page
    requests_page = all_requests[start:end]
    
    # Get user details for each request
    requests_with_users = []
    for req in requests_page:
        user = User.get_by_id(req['user_id'])
        requests_with_users.append({
            'request': req,
            'user': user
        })
    
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('admin/seller_requests.html',
                         requests_with_users=requests_with_users,
                         status_filter=status_filter,
                         page=page,
                         total_pages=total_pages,
                         total=total)

@admin_requests_bp.route('/seller-requests/<int:request_id>/details')
@role_required('admin')
def seller_request_details(request_id):
    """View detailed seller request information"""
    seller_req = SellerRequest.get_by_id(request_id)
    if not seller_req:
        flash('Seller request not found.', 'error')
        return redirect(url_for('admin_requests.seller_requests'))
    
    user = User.get_by_id(seller_req['user_id'])
    
    return render_template('admin/seller_request_details.html',
                         request_data=seller_req,
                         user_data=user)

@admin_requests_bp.route('/seller-requests/<int:request_id>/approve', methods=['POST'])
@role_required('admin')
def approve_seller_request(request_id):
    """Approve a seller request"""
    admin = get_current_user()
    seller_req = SellerRequest.get_by_id(request_id)
    
    if not seller_req:
        return jsonify({'success': False, 'message': 'Request not found'}), 404
    
    if seller_req.get('status') != 'pending':
        return jsonify({'success': False, 'message': 'Only pending requests can be approved'}), 400
    
    try:
        admin_notes = request.form.get('admin_notes', '')
        
        # Approve the request using the model method
        SellerRequest.approve_request(request_id, admin_notes)
        
        # Get user email for notification
        user = User.get_by_id(seller_req['user_id'])
        
        # Send approval email
        try:
            EmailService.send_seller_approval_email(
                email=user['email'],
                first_name=user['first_name'],
                business_name=seller_req['business_name']
            )
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            # Don't fail the approval if email fails, just log it
        
        flash(f"Seller request for {seller_req['business_name']} has been approved!", 'success')
        return redirect(url_for('admin_requests.seller_requests'))
        
    except Exception as e:
        flash(f"Error approving request: {str(e)}", 'error')
        return redirect(url_for('admin_requests.seller_request_details', request_id=request_id))

@admin_requests_bp.route('/seller-requests/<int:request_id>/reject', methods=['POST'])
@role_required('admin')
def reject_seller_request(request_id):
    """Reject a seller request"""
    admin = get_current_user()
    seller_req = SellerRequest.get_by_id(request_id)
    
    if not seller_req:
        return jsonify({'success': False, 'message': 'Request not found'}), 404
    
    if seller_req.get('status') != 'pending':
        return jsonify({'success': False, 'message': 'Only pending requests can be rejected'}), 400
    
    try:
        admin_notes = request.form.get('admin_notes', 'Your seller request was not approved.')
        
        # Reject the request
        SellerRequest.reject_request(request_id, admin_notes)
        
        # Get user email for notification
        user = User.get_by_id(seller_req['user_id'])
        
        # Send rejection email
        try:
            EmailService.send_seller_rejection_email(
                email=user['email'],
                first_name=user['first_name'],
                reason=admin_notes
            )
        except Exception as e:
            print(f"Error sending email: {str(e)}")
        
        flash(f"Seller request has been rejected.", 'success')
        return redirect(url_for('admin_requests.seller_requests'))
        
    except Exception as e:
        flash(f"Error rejecting request: {str(e)}", 'error')
        return redirect(url_for('admin_requests.seller_request_details', request_id=request_id))

# ===================== RIDER REQUESTS =====================

@admin_requests_bp.route('/rider-requests')
@role_required('admin')
def rider_requests():
    """View all rider requests"""
    status_filter = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    
    # Get all applications
    all_applications = Rider.get_all_applications()
    
    # Filter by status if provided
    if status_filter:
        all_applications = [app for app in all_applications if app.get('status') == status_filter]
    
    # Simple pagination
    per_page = 10
    total = len(all_applications)
    start = (page - 1) * per_page
    end = start + per_page
    apps_page = all_applications[start:end]
    
    # Get user details for each application
    apps_with_users = []
    for app in apps_page:
        user = User.get_by_id(app['user_id'])
        apps_with_users.append({
            'application': app,
            'user': user
        })
    
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('admin/rider_requests.html',
                         apps_with_users=apps_with_users,
                         status_filter=status_filter,
                         page=page,
                         total_pages=total_pages,
                         total=total)

@admin_requests_bp.route('/rider-requests/<int:application_id>/details')
@role_required('admin')
def rider_request_details(application_id):
    """View detailed rider application information"""
    application = Rider.get_application_by_id(application_id)
    if not application:
        flash('Rider application not found.', 'error')
        return redirect(url_for('admin_requests.rider_requests'))
    
    user = User.get_by_id(application['user_id'])
    
    return render_template('admin/rider_request_details.html',
                         application_data=application,
                         user_data=user)

@admin_requests_bp.route('/rider-requests/<int:application_id>/approve', methods=['POST'])
@role_required('admin')
def approve_rider_request(application_id):
    """Approve a rider application"""
    admin = get_current_user()
    application = Rider.get_application_by_id(application_id)
    
    if not application:
        return jsonify({'success': False, 'message': 'Application not found'}), 404
    
    if application.get('status') != 'pending':
        return jsonify({'success': False, 'message': 'Only pending applications can be approved'}), 400
    
    try:
        admin_notes = request.form.get('admin_notes', '')
        
        # Update application status to approved
        Rider.update_application_status(application_id, 'approved', admin_notes)
        
        # Get user
        user = User.get_by_id(application['user_id'])
        
        # Send approval email
        try:
            EmailService.send_rider_approval_email(
                email=user['email'],
                first_name=user['first_name'],
                vehicle_type=application.get('vehicle_type')
            )
        except Exception as e:
            print(f"Error sending email: {str(e)}")
        
        flash(f"Rider application has been approved!", 'success')
        return redirect(url_for('admin_requests.rider_requests'))
        
    except Exception as e:
        flash(f"Error approving application: {str(e)}", 'error')
        return redirect(url_for('admin_requests.rider_request_details', application_id=application_id))

@admin_requests_bp.route('/rider-requests/<int:application_id>/reject', methods=['POST'])
@role_required('admin')
def reject_rider_request(application_id):
    """Reject a rider application"""
    admin = get_current_user()
    application = Rider.get_application_by_id(application_id)
    
    if not application:
        return jsonify({'success': False, 'message': 'Application not found'}), 404
    
    if application.get('status') != 'pending':
        return jsonify({'success': False, 'message': 'Only pending applications can be rejected'}), 400
    
    try:
        admin_notes = request.form.get('admin_notes', 'Your rider application was not approved.')
        
        # Update application status to rejected
        Rider.update_application_status(application_id, 'rejected', admin_notes)
        
        # Get user
        user = User.get_by_id(application['user_id'])
        
        # Send rejection email
        try:
            EmailService.send_rider_rejection_email(
                email=user['email'],
                first_name=user['first_name'],
                reason=admin_notes
            )
        except Exception as e:
            print(f"Error sending email: {str(e)}")
        
        flash(f"Rider application has been rejected.", 'success')
        return redirect(url_for('admin_requests.rider_requests'))
        
    except Exception as e:
        flash(f"Error rejecting application: {str(e)}", 'error')
        return redirect(url_for('admin_requests.rider_request_details', application_id=application_id))
