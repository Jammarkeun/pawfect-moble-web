from flask import Blueprint, request, session, render_template, redirect, url_for, flash, jsonify
from app.forms import RiderRegistrationForm
from app.models.user import User
from app.models.rider import Rider
from app.utils.decorators import login_required
from werkzeug.utils import secure_filename
from PIL import Image
import os
import uuid

rider_registration_bp = Blueprint('rider_registration', __name__)

@rider_registration_bp.route('/become-rider')
@login_required
def become_rider():
    """Landing page for becoming a rider"""
    user_id = session.get('user_id')
    user = User.get_by_id(user_id)
    
    # Check if user already has an application
    existing_application = Rider.get_application_by_user(user_id)
    
    # Check if user is already a rider
    if user and user['role'] == 'rider':
        flash('You are already a rider!', 'info')
        return redirect(url_for('rider.dashboard'))
    
    return render_template('rider/become_rider.html', 
                         user=user, 
                         existing_application=existing_application)

@rider_registration_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """Legacy rider registration route.

    New rider registrations are now handled during account signup.
    This route is kept only to view existing rider application status for old users.
    """
    user_id = session.get('user_id')
    existing_application = Rider.get_application_by_user(user_id)
    if existing_application:
        return redirect(url_for('rider_registration.my_application'))

    flash('New rider registrations are now handled during account signup. Please create a new account and choose "Rider" during signup.', 'info')
    return redirect(url_for('public.browse_products'))


@rider_registration_bp.route('/application-status/<int:application_id>')
def application_status(application_id):
    """View rider application status"""
    application = Rider.get_application_by_id(application_id)
    
    if not application:
        flash('Application not found.', 'error')
        return redirect(url_for('public.browse_products'))
    
    return render_template('rider/application_status.html', application=application)


@rider_registration_bp.route('/my-application')
@login_required
def my_application():
    """View logged-in rider's application"""
    user_id = session.get('user_id')
    application = Rider.get_application_by_user(user_id)
    
    if not application:
        flash('No rider application found.', 'info')
        return redirect(url_for('rider_registration.register'))
    
    return render_template('rider/application_status.html', application=application)


@rider_registration_bp.route('/training')
@login_required
def training():
    """Rider training and orientation page"""
    user_id = session.get('user_id')
    application = Rider.get_application_by_user(user_id)
    
    if not application:
        flash('Please complete your rider application first.', 'warning')
        return redirect(url_for('rider_registration.register'))
    
    if application['status'] != 'approved':
        flash('Your application must be approved before starting training.', 'warning')
        return redirect(url_for('rider_registration.my_application'))
    
    training_status = Rider.get_training_status(user_id)
    
    return render_template('rider/training.html', 
                         application=application, 
                         training_status=training_status)


@rider_registration_bp.route('/training/complete', methods=['POST'])
@login_required
def complete_training():
    """Mark training as completed"""
    user_id = session.get('user_id')
    application = Rider.get_application_by_user(user_id)
    
    if not application or application['status'] != 'approved':
        return jsonify({'success': False, 'message': 'Invalid request'}), 400
    
    try:
        Rider.complete_training(user_id)
        
        # Activate rider account
        Rider.activate_rider_account(user_id)
        
        # Update session
        session['user_role'] = 'rider'
        
        flash('Congratulations! Your rider account has been activated.', 'success')
        return jsonify({
            'success': True, 
            'message': 'Training completed successfully',
            'redirect_url': url_for('rider.dashboard')
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# Admin routes for managing applications
@rider_registration_bp.route('/admin/applications')
@login_required
def admin_applications():
    """Admin view for all rider applications"""
    # Check if user is admin
    if session.get('user_role') != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('public.browse_products'))
    
    status_filter = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    applications = Rider.get_all_applications(status=status_filter, limit=per_page, offset=offset)
    total_count = Rider.get_applications_count(status=status_filter)
    total_pages = (total_count + per_page - 1) // per_page
    
    return render_template('rider/admin_applications.html',
                         applications=applications,
                         current_page=page,
                         total_pages=total_pages,
                         status_filter=status_filter)


@rider_registration_bp.route('/admin/application/<int:application_id>/review', methods=['POST'])
@login_required
def admin_review_application(application_id):
    """Admin review and approve/reject application"""
    if session.get('user_role') != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    action = request.form.get('action')  # 'approve' or 'reject'
    admin_notes = request.form.get('admin_notes', '')
    
    if action not in ['approve', 'reject']:
        return jsonify({'success': False, 'message': 'Invalid action'}), 400
    
    try:
        status = 'approved' if action == 'approve' else 'rejected'
        Rider.update_application_status(application_id, status, admin_notes)
        
        flash(f'Application has been {status}.', 'success')
        return jsonify({
            'success': True,
            'message': f'Application {status} successfully',
            'redirect_url': url_for('rider_registration.admin_applications')
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
