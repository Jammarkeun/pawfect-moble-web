from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from app.models.user import User
from app.models.seller_request import SellerRequest
from app.models.rider import Rider
from app.utils.decorators import anonymous_required, login_required
from app.forms import LoginForm, SignupForm, OTPVerificationForm, PasswordResetRequestForm, PasswordResetForm, ChangePasswordForm
from app.services.email_service import EmailService
from app.services.location_service import location_service
import secrets
import hashlib
import json
import os
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

# Load Philippine regions data
with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'ph_regions.json'), 'r', encoding='utf-8') as f:
    PH_REGIONS = json.load(f)

@auth_bp.route('/api/ph/regions', methods=['GET'])
def get_ph_regions():
    """Proxy to PSGC regions, falling back to bundled data if needed."""
    try:
        regions = location_service.get_regions()
    except Exception as exc:  # pragma: no cover - network fallback
        current_app.logger.warning('Falling back to bundled region data: %s', exc)
        regions = PH_REGIONS.get('regions', [])
    return jsonify({
        'success': True,
        'data': regions
    })

@auth_bp.route('/api/ph/provinces', defaults={'region_code': None}, methods=['GET'])
@auth_bp.route('/api/ph/provinces/<region_code>', methods=['GET'])
def get_ph_provinces(region_code):
    """Get provinces optionally filtered by region."""
    region_code = region_code or request.args.get('region_code')
    try:
        provinces = location_service.get_provinces(region_code)
        return jsonify({'success': True, 'data': provinces})
    except Exception as e:  # pragma: no cover - defensive
        current_app.logger.exception('Failed to load provinces')
        return jsonify({'success': False, 'message': str(e)}), 400

@auth_bp.route('/api/ph/cities/<province_code>', methods=['GET'])
def get_ph_cities(province_code):
    """Get cities/municipalities for a specific province code."""
    try:
        cities = location_service.get_cities(province_code)
        return jsonify({'success': True, 'data': cities})
    except Exception as e:
        current_app.logger.exception('Failed to load cities for %s', province_code)
        return jsonify({'success': False, 'message': str(e)}), 400

@auth_bp.route('/api/ph/barangays/<city_code>', methods=['GET'])
def get_ph_barangays(city_code):
    """Get barangays for a specific city/municipality code."""
    try:
        barangays = location_service.get_barangays(city_code)
        return jsonify({'success': True, 'data': barangays})
    except Exception as e:
        current_app.logger.exception('Failed to load barangays for %s', city_code)
        return jsonify({'success': False, 'message': str(e)}), 400

@auth_bp.route('/login', methods=['GET', 'POST'])
@anonymous_required
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip()
        password = form.password.data
        
        try:
            user = User.authenticate(email, password)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Login error: {e}")
            flash('Unable to connect to authentication service. Please try again.', 'error')
            return render_template('auth/login.html', form=form)
        if user:
            if user['status'] != 'active':
                if user['status'] == 'pending':
                    return render_template('auth/approval_pending.html', account_type='user', request_data={})
                flash('Your account has been deactivated. Please contact support.', 'error')
                return render_template('auth/login.html', form=form)
            
            # Check if user has a pending seller or rider application
            from app.models.seller_request import SellerRequest
            from app.models.rider import Rider
            
            seller_request = SellerRequest.get_by_user_id(user['id'])
            rider_application = Rider.get_application_by_user(user['id'])
            
            # Block login if they have pending seller request (non-admin accounts only)
            if user['role'] != 'admin' and seller_request and seller_request['status'] == 'pending':
                return render_template('auth/approval_pending.html', 
                                     account_type='seller',
                                     request_data=seller_request)
            
            # Block login if they have pending rider application (non-admin accounts only)
            if user['role'] != 'admin' and rider_application and rider_application['status'] == 'pending':
                return render_template('auth/approval_pending.html',
                                     account_type='rider',
                                     request_data=rider_application)
            
            session['user_id'] = user['id']
            role = user.get('role', 'user')
            session['user_role'] = 'user' if role == 'customer' else role
            session.permanent = True
            
            # Redirect based on role
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif role == 'seller':
                return redirect(url_for('seller.dashboard'))
            elif role == 'rider':
                # Mark rider as available when they log in
                from app.services.database import Database
                from datetime import datetime
                
                db = Database()
                
                # Check if rider exists in availability table
                rider_check = db.select_one('rider_availability', filters={'rider_id': user['id']})
                
                if rider_check:
                    # Update existing rider
                    db.update('rider_availability',
                             data={'is_online': True, 'is_available': True, 'last_online': datetime.utcnow().isoformat()},
                             filters={'rider_id': user['id']})
                else:
                    # Insert new rider
                    db.insert('rider_availability',
                             {'rider_id': user['id'], 'is_online': True, 'is_available': True, 'last_online': datetime.utcnow().isoformat()})
                
                return redirect(url_for('rider.dashboard'))
            else:
                return redirect(url_for('public.browse_products'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/signup', methods=['GET', 'POST'])
@anonymous_required
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data.strip()
        password = form.password.data
        first_name = form.first_name.data.strip()
        last_name = form.last_name.data.strip()
        phone = form.phone.data.strip()
        account_type = getattr(form, 'account_type', None).data if hasattr(form, 'account_type') else 'user'

        # Extra validation for seller / rider specific fields
        if account_type == 'seller':
            missing = []
            if not (form.business_name.data or '').strip():
                missing.append('business name')
            if not (form.business_description.data or '').strip():
                missing.append('business description')
            if not (form.business_address.data or '').strip():
                missing.append('business address')
            if not (form.business_phone.data or '').strip():
                missing.append('business phone')
            if not (form.business_permit.data and getattr(form.business_permit.data, 'filename', None)):
                missing.append('business permit')
            if missing:
                flash('Please complete all required seller details: ' + ', '.join(missing) + '.', 'error')
                return render_template('auth/signup_multi_step.html', form=form)

        if account_type == 'rider':
            missing = []
            if not (form.vehicle_type.data or '').strip():
                missing.append('vehicle type')
            if not (form.rider_government_id.data and getattr(form.rider_government_id.data, 'filename', None)):
                missing.append('government ID')
            if not (form.rider_profile_photo.data and getattr(form.rider_profile_photo.data, 'filename', None)):
                missing.append('profile photo')
            if missing:
                flash('Please complete all required rider details: ' + ', '.join(missing) + '.', 'error')
                return render_template('auth/signup_multi_step.html', form=form)

        # Structured address fields
        house_number = getattr(form, 'house_number', None).data.strip() if hasattr(form, 'house_number') and form.house_number.data else ''
        street = getattr(form, 'street', None).data.strip() if hasattr(form, 'street') and form.street.data else ''
        barangay = getattr(form, 'barangay', None).data.strip() if hasattr(form, 'barangay') and form.barangay.data else ''
        province = getattr(form, 'province', None).data.strip() if hasattr(form, 'province') and form.province.data else ''
        postal_code = getattr(form, 'postal_code', None).data.strip() if hasattr(form, 'postal_code') and form.postal_code.data else ''
        address = form.address.data.strip()
        country = form.country.data
        city = form.city.data.strip()
        id_picture = form.id_picture.data

        # Seller / rider document uploads (stored as paths in session)
        seller_business_permit_path = None
        rider_files = {}

        # Check if user exists
        if User.email_exists(email):
            flash('An account with this email already exists.', 'error')
            return render_template('auth/signup_multi_step.html', form=form)

        import os
        from werkzeug.utils import secure_filename
        from PIL import Image
        import uuid

        # Handle seller business permit if applicable
        if account_type == 'seller' and form.business_permit.data and getattr(form.business_permit.data, 'filename', None):
            uploads_dir = os.path.join('static', 'uploads', 'business_permits')
            os.makedirs(uploads_dir, exist_ok=True)
            file_ext = os.path.splitext(form.business_permit.data.filename)[1].lower()
            if file_ext not in ['.jpg', '.jpeg', '.png', '.gif', '.pdf']:
                file_ext = '.jpg'
            unique_filename = f"{uuid.uuid4().hex}_{email.replace('@', '_')}{file_ext}"
            business_permit_path = os.path.join(uploads_dir, unique_filename)

            # If image, process; if pdf, save directly
            if file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
                try:
                    image = Image.open(form.business_permit.data)
                    if image.mode in ('RGBA', 'LA', 'P'):
                        image = image.convert('RGB')
                    max_size = (1200, 1200)
                    image.thumbnail(max_size, Image.Resampling.LANCZOS)
                    image.save(business_permit_path, 'JPEG', quality=85, optimize=True)
                    seller_business_permit_path = f"uploads/business_permits/{unique_filename}"
                except Exception:
                    filename = secure_filename(form.business_permit.data.filename)
                    if filename:
                        fallback_path = os.path.join(uploads_dir, f"{uuid.uuid4().hex}_{filename}")
                        form.business_permit.data.save(fallback_path)
                        seller_business_permit_path = f"uploads/business_permits/{os.path.basename(fallback_path)}"
            else:
                form.business_permit.data.save(business_permit_path)
                seller_business_permit_path = f"uploads/business_permits/{unique_filename}"

        # Handle rider documents if applicable
        if account_type == 'rider':
            rider_uploads_base = os.path.join('static', 'uploads', 'rider_documents')
            rider_profiles_dir = os.path.join('static', 'uploads', 'rider_profiles')
            os.makedirs(rider_uploads_base, exist_ok=True)
            os.makedirs(rider_profiles_dir, exist_ok=True)
            unique_prefix = f"{uuid.uuid4().hex}_{email.replace('@', '_')}"

            # Government ID
            if form.rider_government_id.data and getattr(form.rider_government_id.data, 'filename', None):
                gov_id_file = form.rider_government_id.data
                file_ext = os.path.splitext(gov_id_file.filename)[1].lower()
                gov_id_filename = f"{unique_prefix}_gov_id{file_ext}"
                gov_id_path = os.path.join(rider_uploads_base, gov_id_filename)
                gov_id_file.save(gov_id_path)
                rider_files['government_id'] = f"uploads/rider_documents/{gov_id_filename}"

            # Vehicle registration (optional)
            if form.rider_vehicle_registration.data and getattr(form.rider_vehicle_registration.data, 'filename', None):
                vr_file = form.rider_vehicle_registration.data
                file_ext = os.path.splitext(vr_file.filename)[1].lower()
                vr_filename = f"{unique_prefix}_vehicle_reg{file_ext}"
                vr_path = os.path.join(rider_uploads_base, vr_filename)
                vr_file.save(vr_path)
                rider_files['vehicle_registration'] = f"uploads/rider_documents/{vr_filename}"

            # Profile photo
            if form.rider_profile_photo.data and getattr(form.rider_profile_photo.data, 'filename', None):
                photo_file = form.rider_profile_photo.data
                try:
                    image = Image.open(photo_file)
                    if image.mode in ('RGBA', 'LA', 'P'):
                        image = image.convert('RGB')
                    max_size = (400, 400)
                    image.thumbnail(max_size, Image.Resampling.LANCZOS)
                    photo_filename = f"{unique_prefix}_profile.jpg"
                    photo_path = os.path.join(rider_profiles_dir, photo_filename)
                    image.save(photo_path, 'JPEG', quality=85, optimize=True)
                    rider_files['profile_photo'] = f"uploads/rider_profiles/{photo_filename}"
                except Exception:
                    filename = secure_filename(form.rider_profile_photo.data.filename)
                    if filename:
                        fallback_path = os.path.join(rider_profiles_dir, f"{uuid.uuid4().hex}_{filename}")
                        form.rider_profile_photo.data.save(fallback_path)
                        rider_files['profile_photo'] = f"uploads/rider_profiles/{os.path.basename(fallback_path)}"

            # Clearance (optional)
            if form.rider_clearance.data and getattr(form.rider_clearance.data, 'filename', None):
                clearance_file = form.rider_clearance.data
                file_ext = os.path.splitext(clearance_file.filename)[1].lower()
                clearance_filename = f"{unique_prefix}_clearance{file_ext}"
                clearance_path = os.path.join(rider_uploads_base, clearance_filename)
                clearance_file.save(clearance_path)
                rider_files['clearance'] = f"uploads/rider_documents/{clearance_filename}"

        # Generate OTP and store in session
        import random
        otp_code = str(random.randint(100000, 999999))
        # Compose full address fallback string
        full_address = address or ", ".join([v for v in [house_number + ((" " + street) if street else ''),
                                                          (("Barangay " + barangay) if barangay else ''),
                                                          city, province, postal_code, country] if v]).strip(', ')
        
        session['signup_data'] = {
            'email': email,
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'address': full_address,
            'country': country,
            'city': city,
            'province': province,
            'postal_code': postal_code,
            'house_number': house_number,
            'street': street,
            'barangay': barangay,
            'account_type': account_type or 'user',
            # Seller extra data
            'seller_business_name': (form.business_name.data or '').strip() if account_type == 'seller' else None,
            'seller_business_description': (form.business_description.data or '').strip() if account_type == 'seller' else None,
            'seller_business_address': (form.business_address.data or '').strip() if account_type == 'seller' else None,
            'seller_business_phone': (form.business_phone.data or '').strip() if account_type == 'seller' else None,
            'seller_tax_id': (form.tax_id.data or '').strip() if account_type == 'seller' else None,
            'seller_business_permit': seller_business_permit_path if account_type == 'seller' else None,
            # Rider extra data
            'rider_vehicle_type': form.vehicle_type.data if account_type == 'rider' else None,
            'rider_vehicle_plate_number': (form.vehicle_plate_number.data or '').strip() if account_type == 'rider' else None,
            'rider_vehicle_model': (form.vehicle_model.data or '').strip() if account_type == 'rider' else None,
            'rider_government_id': rider_files.get('government_id') if account_type == 'rider' else None,
            'rider_vehicle_registration': rider_files.get('vehicle_registration') if account_type == 'rider' else None,
            'rider_profile_photo': rider_files.get('profile_photo') if account_type == 'rider' else None,
            'rider_clearance': rider_files.get('clearance') if account_type == 'rider' else None,
            'otp_code': otp_code
        }

        # Handle file upload for ID picture
        id_picture_filename = None
        if id_picture and hasattr(id_picture, 'filename') and id_picture.filename:
            import os
            from werkzeug.utils import secure_filename
            from PIL import Image
            import uuid

            # Create uploads directory if it doesn't exist
            uploads_dir = os.path.join('static', 'uploads', 'id_pictures')
            os.makedirs(uploads_dir, exist_ok=True)

            # Generate unique filename
            file_ext = os.path.splitext(id_picture.filename)[1].lower()
            if file_ext not in ['.jpg', '.jpeg', '.png', '.pdf']:
                file_ext = '.jpg'  # Default to jpg if unknown extension
            unique_filename = f"{uuid.uuid4().hex}_{email.replace('@', '_')}{file_ext}"
            id_picture_path = os.path.join(uploads_dir, unique_filename)

            try:
                # Open and process the image
                image = Image.open(id_picture)

                # Convert to RGB if necessary (for PNG with transparency)
                if image.mode in ('RGBA', 'LA', 'P'):
                    image = image.convert('RGB')

                # Resize to a reasonable size (max 800x800, maintain aspect ratio)
                max_size = (800, 800)
                image.thumbnail(max_size, Image.Resampling.LANCZOS)

                # Save as JPEG with good quality
                image.save(id_picture_path, 'JPEG', quality=85, optimize=True)
                id_picture_filename = f"uploads/id_pictures/{unique_filename}"

                # Also create a profile image version (smaller size)
                profile_image = image.copy()
                profile_max_size = (400, 400)
                profile_image.thumbnail(profile_max_size, Image.Resampling.LANCZOS)

                # Create profile image directory if it doesn't exist
                profile_dir = os.path.join('static', 'uploads', 'profiles')
                os.makedirs(profile_dir, exist_ok=True)

                # Generate profile image filename
                profile_filename = f"{uuid.uuid4().hex}_{email.replace('@', '_')}_profile.jpg"
                profile_path = os.path.join(profile_dir, profile_filename)
                profile_image.save(profile_path, 'JPEG', quality=85, optimize=True)
                profile_image_filename = f"uploads/profiles/{profile_filename}"

            except Exception as e:
                # Fallback to original upload if processing fails
                filename = secure_filename(id_picture.filename)
                if filename:
                    fallback_filename = f"{uuid.uuid4().hex}_{filename}"
                    fallback_path = os.path.join(uploads_dir, fallback_filename)
                    id_picture.save(fallback_path)
                    id_picture_filename = f"uploads/id_pictures/{fallback_filename}"

        # Store file info in session
        session['signup_data']['id_picture'] = id_picture_filename
        if 'profile_image_filename' in locals():
            session['signup_data']['profile_image'] = profile_image_filename

        # Send OTP email via Email Service
        sent = EmailService.send_otp_email(email, otp_code)
        if not sent:
            flash('We could not send the verification code. Please try again later.', 'error')
            return render_template('auth/signup_multi_step.html', form=form)
        
        # Redirect to OTP verification
        return redirect(url_for('auth.verify_otp', email=email))
    elif request.method == 'POST':
        flash('Please correct the errors in the form.', 'error')

    return render_template('auth/signup_multi_step.html', form=form)

@auth_bp.route('/verify-otp/<email>', methods=['GET', 'POST'])
@anonymous_required
def verify_otp(email):
    form = OTPVerificationForm()
    # If the signup session is missing, the OTP cannot be verified.
    # Show a clear message and ask the user to restart registration.
    if request.method == 'POST' and 'signup_data' not in session:
        current_app.logger.info(f"Signup session missing during OTP verify for {email}")
        flash('Session expired. Please register again.', 'error')
        return redirect(url_for('auth.signup'))
    
    if form.validate_on_submit():
        otp_code = form.otp_code.data
        
        # Debug logging
        current_app.logger.info(f"OTP verification attempt for {email}")
        current_app.logger.info(f"Entered OTP: {otp_code}")
        current_app.logger.info(f"Session signup_data exists: {'signup_data' in session}")
        if 'signup_data' in session:
            current_app.logger.info(f"Stored OTP: {session['signup_data'].get('otp_code')}")
            current_app.logger.info(f"Email match: {session['signup_data'].get('email') == email}")
        
        # Check if OTP matches
        if 'signup_data' in session and session['signup_data'].get('otp_code') == otp_code:
            # Create user account
            signup_data = session['signup_data']
            
            try:
                # Create user account (Supabase Auth handles email uniqueness)
                user = User.create(
                    username=signup_data['email'].split('@')[0],
                    email=signup_data['email'],
                    password=signup_data['password'],
                    first_name=signup_data['first_name'],
                    last_name=signup_data['last_name'],
                    phone=signup_data['phone'],
                    address=signup_data['address'],
                    country=signup_data['country'],
                    city=signup_data['city'],
                    province=signup_data.get('province'),
                    house_number=signup_data.get('house_number'),
                    street=signup_data.get('street'),
                    barangay=signup_data.get('barangay'),
                    postal_code=signup_data.get('postal_code'),
                    id_picture=signup_data.get('id_picture'),
                    profile_image=signup_data.get('profile_image')
                )

                current_app.logger.info(f'User created successfully: {signup_data["email"]}')
                account_type = signup_data.get('account_type', 'user')

                # Regular buyers now require admin approval before first login.
                if account_type == 'user':
                    User.update_status(user['id'], 'pending')

                # Create seller request or rider application if needed
                pending_request_data = None
                if account_type == 'seller':
                    try:
                        applicant_name = f"{signup_data.get('first_name', '').strip()} {signup_data.get('last_name', '').strip()}".strip()
                        pending_request_data = SellerRequest.create(
                            user_id=user['id'],
                            applicant_name=applicant_name or None,
                            business_name=signup_data.get('seller_business_name'),
                            business_description=signup_data.get('seller_business_description'),
                            business_address=signup_data.get('seller_business_address'),
                            business_phone=signup_data.get('seller_business_phone'),
                            tax_id=signup_data.get('seller_tax_id'),
                            business_permit=signup_data.get('seller_business_permit')
                        ) or SellerRequest.get_by_user_id(user['id'])
                    except Exception:
                        current_app.logger.exception('Failed to create seller request during signup')
                        pending_request_data = SellerRequest.get_by_user_id(user['id'])

                if account_type == 'rider':
                    try:
                        application_id = Rider.create_application(
                            user_id=user['id'],
                            vehicle_type=signup_data.get('rider_vehicle_type'),
                            vehicle_plate_number=signup_data.get('rider_vehicle_plate_number'),
                            vehicle_model=signup_data.get('rider_vehicle_model'),
                            government_id_path=signup_data.get('rider_government_id'),
                            vehicle_registration_path=signup_data.get('rider_vehicle_registration'),
                            profile_photo_path=signup_data.get('rider_profile_photo'),
                            clearance_path=signup_data.get('rider_clearance')
                        )
                        pending_request_data = Rider.get_application_by_id(application_id) if application_id else Rider.get_application_by_user(user['id'])
                    except Exception:
                        current_app.logger.exception('Failed to create rider application during signup')
                        pending_request_data = Rider.get_application_by_user(user['id'])

                # Clear signup data from session
                session.pop('signup_data', None)

                # Surface proper completion view
                if account_type in ('seller', 'rider'):
                    flash('Application submitted successfully! Our admins will review it shortly.', 'info')
                    return render_template(
                        'auth/approval_pending.html',
                        account_type=account_type,
                        request_data=pending_request_data or {}
                    )
                elif account_type == 'user':
                    flash('Account created! Your buyer account is pending admin approval.', 'info')
                    return render_template(
                        'auth/approval_pending.html',
                        account_type='user',
                        request_data={}
                    )
                else:
                    flash('Account created successfully! Please login.', 'success')
                    return redirect(url_for('auth.signup_complete', account_type=account_type))
            except Exception as e:
                current_app.logger.exception(f'Error creating account after OTP verification: {str(e)}')
                error_msg = str(e)
                flash(f'Account creation failed: {error_msg[:150]}', 'error')
                current_app.logger.error(f'Full error: {error_msg}')
        else:
            flash('Invalid OTP code. Please try again.', 'error')
    
    return render_template('auth/otp_verification.html', form=form, email=email)

@auth_bp.route('/resend-otp', methods=['POST'])
@anonymous_required
def resend_otp():
    if 'signup_data' in session:
        import random
        otp_code = str(random.randint(100000, 999999))
        session['signup_data']['otp_code'] = otp_code
        
        # Send OTP email via Email Service
        email = session['signup_data']['email']
        if EmailService.send_otp_email(email, otp_code):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to send email'})
    
    return jsonify({'success': False, 'error': 'No signup data found'})

@auth_bp.route('/test-otp', methods=['GET', 'POST'])
def test_otp():
    """Test route for OTP functionality - for development only"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if not email:
            return jsonify({'success': False, 'error': 'Email is required'})
        
        import random
        otp_code = str(random.randint(100000, 999999))
        
        # Test email sending via Email Service
        success = EmailService.send_otp_email(email, otp_code)
        
        return jsonify({
            'success': success,
            'otp_code': otp_code,
            'message': 'OTP sent successfully' if success else 'Failed to send OTP'
        })
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>OTP Test</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input[type="email"] { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .result { margin-top: 20px; padding: 10px; border-radius: 4px; }
            .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        </style>
    </head>
    <body>
        <h2>🔧 OTP Test Page</h2>
        <p>This page helps you test the OTP email functionality.</p>
        
        <form id="otpForm">
            <div class="form-group">
                <label for="email">Test Email Address:</label>
                <input type="email" id="email" name="email" required placeholder="your@email.com">
            </div>
            <button type="submit">Send Test OTP</button>
        </form>
        
        <div id="result"></div>
        
        <script>
            document.getElementById('otpForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const email = document.getElementById('email').value;
                const resultDiv = document.getElementById('result');
                
                resultDiv.innerHTML = '<p>🔄 Sending OTP...</p>';
                
                try {
                    const formData = new FormData();
                    formData.append('email', email);
                    
                    const response = await fetch('/auth/test-otp', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        resultDiv.innerHTML = `
                            <div class="result success">
                                <h3>✅ Success!</h3>
                                <p><strong>OTP Code:</strong> ${data.otp_code}</p>
                                <p>Check your email: ${email}</p>
                                <p>Also check the console output and otp_codes.txt file</p>
                            </div>
                        `;
                    } else {
                        resultDiv.innerHTML = `
                            <div class="result error">
                                <h3>❌ Failed</h3>
                                <p>Error: ${data.error || 'Unknown error'}</p>
                            </div>
                        `;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `
                        <div class="result error">
                            <h3>❌ Error</h3>
                            <p>Network error: ${error.message}</p>
                        </div>
                    `;
                }
            });
        </script>
    </body>
    </html>
    '''

@auth_bp.route('/signup-complete')
@anonymous_required
def signup_complete():
    account_type = request.args.get('account_type', 'user')
    return render_template('auth/signup_complete.html', account_type=account_type)


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('public.landing'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    user = User.get_by_id(session['user_id'])
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        # Update profile
        update_data = {
            'first_name': request.form.get('first_name', '').strip(),
            'last_name': request.form.get('last_name', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'address': request.form.get('address', '').strip()
        }
        
        # Remove empty values
        update_data = {k: v for k, v in update_data.items() if v}
        
        if User.update(session['user_id'], **update_data):
            flash('Profile updated successfully!', 'success')
        else:
            flash('Failed to update profile.', 'error')
        
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html', user=user)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.get_by_id(session['user_id'])
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('auth.login'))
        
        # Verify current password
        if not User.authenticate(user['email'], form.current_password.data):
            flash('Current password is incorrect.', 'error')
            return render_template('auth/change_password.html', form=form)
        
        # Update password
        if User.update_password(session['user_id'], form.new_password.data):
            flash('Password changed successfully!', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('Failed to change password.', 'error')
    
    return render_template('auth/change_password.html', form=form)

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@anonymous_required
def forgot_password():
    """Password reset request"""
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        email = form.email.data.strip()
        user = User.get_by_email(email)
        
        if user:
            # Generate reset token
            token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            # Store token in database (you might want to create a separate table for this)
            # For now, we'll use a simple approach
            session[f'reset_token_{user["id"]}'] = {
                'token_hash': token_hash,
                'expires': (datetime.now() + timedelta(hours=1)).isoformat()
            }
            
            # In a real application, you'd send an email here
            flash(f'Password reset instructions have been sent to {email}. Reset link (for demo): /auth/reset-password/{user["id"]}/{token}', 'info')
        else:
            # Don't reveal whether email exists or not
            flash(f'If an account with {email} exists, password reset instructions have been sent.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', form=form)

@auth_bp.route('/reset-password/<int:user_id>/<token>', methods=['GET', 'POST'])
@anonymous_required
def reset_password(user_id, token):
    """Password reset form"""
    # Verify token
    session_key = f'reset_token_{user_id}'
    if session_key not in session:
        flash('Invalid or expired reset token.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    token_data = session[session_key]
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    if (token_hash != token_data['token_hash'] or 
        datetime.now() > datetime.fromisoformat(token_data['expires'])):
        flash('Invalid or expired reset token.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.update_password(user_id, form.password.data):
            # Clear the reset token
            session.pop(session_key, None)
            flash('Password reset successfully! Please log in with your new password.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Failed to reset password.', 'error')
    
    return render_template('auth/reset_password.html', form=form)


# OAuth Social Login Routes

@auth_bp.route('/oauth/<provider>')
@anonymous_required
def oauth_login(provider):
    """Initiate OAuth login flow"""
    from app.utils.oauth import get_oauth_provider
    
    oauth = get_oauth_provider(provider)
    
    if not oauth:
        flash(f'{provider.title()} login is not configured.', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        authorization_url = oauth.get_authorization_url()
        return redirect(authorization_url)
    except Exception as e:
        current_app.logger.error(f"OAuth error: {str(e)}")
        flash('Failed to initiate social login.', 'error')
        return redirect(url_for('auth.login'))


@auth_bp.route('/oauth/<provider>/callback')
@anonymous_required
def oauth_callback(provider):
    """Handle OAuth callback"""
    from app.utils.oauth import get_oauth_provider, verify_oauth_state
    from app.services.database import Database
    import uuid
    
    # Verify state token for CSRF protection
    state = request.args.get('state')
    if not state or not verify_oauth_state(state):
        flash('Invalid OAuth state. Please try again.', 'error')
        return redirect(url_for('auth.login'))
    
    # Check for errors from OAuth provider
    error = request.args.get('error')
    if error:
        error_description = request.args.get('error_description', 'Unknown error')
        flash(f'OAuth error: {error_description}', 'error')
        return redirect(url_for('auth.login'))
    
    # Get authorization code
    code = request.args.get('code')
    if not code:
        flash('Authorization code not received.', 'error')
        return redirect(url_for('auth.login'))
    
    oauth = get_oauth_provider(provider)
    if not oauth:
        flash(f'{provider.title()} login is not configured.', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        # Exchange code for access token
        access_token = oauth.get_access_token(code)
        if not access_token:
            flash('Failed to get access token.', 'error')
            return redirect(url_for('auth.login'))
        
        # Get user info from provider
        user_info = oauth.get_user_info(access_token)
        if not user_info or not user_info.get('email'):
            flash('Failed to get user information from provider.', 'error')
            return redirect(url_for('auth.login'))
        
        email = user_info['email']
        provider_id = user_info.get('provider_id')
        
        # Check if user exists
        user = User.get_by_email(email)
        
        if user:
            # User exists, log them in
            if user['status'] != 'active':
                if user['status'] == 'pending':
                    return render_template('auth/approval_pending.html', account_type='user', request_data={})
                flash('Your account has been deactivated. Please contact support.', 'error')
                return redirect(url_for('auth.login'))
            
            session['user_id'] = user['id']
            role = user.get('role', 'user')
            session['user_role'] = 'user' if role == 'customer' else role
            session.permanent = True
            
            flash(f'Welcome back, {user["first_name"]}!', 'success')
            
            # Redirect based on role
            if role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif role == 'seller':
                return redirect(url_for('seller.dashboard'))
            elif role == 'rider':
                return redirect(url_for('rider.dashboard'))
            else:
                return redirect(url_for('public.browse_products'))
        
        else:
            # Create new user account
            db = Database()
            
            # Generate a random password (user won't need it for OAuth)
            random_password = str(uuid.uuid4())
            password_hash = hashlib.sha256(random_password.encode()).hexdigest()
            
            # Prepare user data
            first_name = user_info.get('first_name', email.split('@')[0])
            last_name = user_info.get('last_name', '')
            profile_picture = user_info.get('profile_picture')
            
            # Insert user into profiles table
            import uuid
            user_id = str(uuid.uuid4())
            profile_data = {
                'id': user_id,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'role': 'user',
                'status': 'active',
                'oauth_provider': provider,
                'oauth_provider_id': provider_id,
                'profile_image': profile_picture,
                'created_at': datetime.utcnow().isoformat()
            }
            new_user = db.insert('profiles', profile_data)
            
            if new_user:
                # Log them in
                session['user_id'] = new_user.get('id', user_id)
                session['user_role'] = 'user'
                session.permanent = True
                
                flash(f'Welcome to Pawfect Finds, {first_name}!', 'success')
                return redirect(url_for('public.browse_products'))
            else:
                flash('Failed to create account. Please try again.', 'error')
                return redirect(url_for('auth.login'))
    
    except Exception as e:
        current_app.logger.error(f"OAuth callback error: {str(e)}", exc_info=True)
        flash('An error occurred during social login. Please try again.', 'error')
        return redirect(url_for('auth.login'))


@auth_bp.route('/api/send-otp', methods=['POST'])
def api_send_otp():
    """API endpoint for mobile app OTP sending"""
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()

    if not email or '@' not in email:
        return jsonify({'success': False, 'message': 'Valid email is required'}), 400

    import random
    otp_code = str(random.randint(100000, 999999))

    from app.services.database import Database
    db = Database()
    now = datetime.utcnow()

    db.supabase.from_('verification_codes').delete().eq('email', email).execute()
    db.supabase.from_('verification_codes').insert({
        'email': email,
        'code': otp_code,
        'expires_at': (now + timedelta(minutes=10)).isoformat(),
        'verified': False,
    }).execute()

    sent = EmailService.send_otp_email(email, otp_code)
    if not sent:
        return jsonify({'success': False, 'message': 'Failed to send OTP email'}), 500

    return jsonify({'success': True, 'message': 'OTP sent to email'})


@auth_bp.route('/api/verify-otp', methods=['POST'])
def api_verify_otp():
    """API endpoint for mobile app OTP verification"""
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    otp_code = (data.get('otp') or '').strip()

    if not email or not otp_code:
        return jsonify({'success': False, 'message': 'Email and OTP are required'}), 400

    from app.services.database import Database
    db = Database()
    now = datetime.utcnow()

    result = db.supabase.from_('verification_codes') \
        .select('*') \
        .eq('email', email) \
        .eq('code', otp_code) \
        .eq('verified', False) \
        .gte('expires_at', now.isoformat()) \
        .execute()

    if not result.data:
        return jsonify({'success': False, 'message': 'Invalid or expired OTP'}), 400

    db.supabase.from_('verification_codes') \
        .update({'verified': True}) \
        .eq('id', result.data[0]['id']) \
        .execute()

    return jsonify({'success': True, 'message': 'OTP verified successfully'})
