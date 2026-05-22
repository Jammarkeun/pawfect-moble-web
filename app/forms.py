from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, FloatField, SelectField, HiddenField, TelField, RadioField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    account_type = RadioField(
        'Account Type',
        choices=[('user', 'User'), ('seller', 'Seller'), ('rider', 'Rider')],
        default='user',
        validators=[DataRequired()]
    )
    # Base user fields
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    phone = TelField('Phone', validators=[DataRequired(), Length(max=20)])
    # Structured address fields (PH)
    house_number = StringField('House/Unit No.', validators=[Optional(), Length(max=50)])
    street = StringField('Street', validators=[Optional(), Length(max=150)])
    barangay = StringField('Barangay', validators=[Optional(), Length(max=100)])
    province = StringField('Province', validators=[Optional(), Length(max=100)])
    postal_code = StringField('Postal Code', validators=[Optional(), Length(max=20)])
    address = TextAreaField('Complete Address', validators=[Optional(), Length(max=500)])
    country = SelectField('Country', choices=[
        ('Philippines', 'Philippines'),
        ('United States', 'United States'),
        ('Canada', 'Canada'),
        ('Australia', 'Australia'),
        ('United Kingdom', 'United Kingdom'),
        ('Japan', 'Japan'),
        ('South Korea', 'South Korea'),
        ('Singapore', 'Singapore'),
        ('Malaysia', 'Malaysia'),
        ('Thailand', 'Thailand'),
        ('Indonesia', 'Indonesia'),
        ('Vietnam', 'Vietnam'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    id_picture = FileField('ID Picture', validators=[DataRequired(message='ID picture is required'), FileAllowed(['jpg', 'png', 'jpeg', 'pdf'], 'Images and PDF files only!')])

    # Seller-specific fields (validated in controller when account_type == 'seller')
    business_name = StringField('Business Name', validators=[Optional(), Length(max=100)])
    business_description = TextAreaField('Business Description', validators=[Optional(), Length(max=1000)])
    business_address = TextAreaField('Business Address', validators=[Optional(), Length(max=500)])
    business_phone = TelField('Business Phone', validators=[Optional(), Length(max=20)])
    tax_id = StringField('Tax ID', validators=[Optional(), Length(max=50)])
    business_permit = FileField('Business Permit', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'pdf'], 'Images and PDF files only!')])

    # Rider-specific fields (validated in controller when account_type == 'rider')
    vehicle_type = SelectField('Vehicle Type', choices=[
        ('', 'Select vehicle type'),
        ('motorcycle', 'Motorcycle'),
        ('bicycle', 'Bicycle'),
        ('car', 'Car'),
        ('scooter', 'Scooter')
    ], validators=[Optional()])
    vehicle_plate_number = StringField('Vehicle Plate Number', validators=[Optional(), Length(max=20)])
    vehicle_model = StringField('Vehicle Model', validators=[Optional(), Length(max=100)])
    rider_government_id = FileField("Government ID (Driver's License or National ID)",
                                   validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'pdf'], 'Images and PDF files only!')])
    rider_profile_photo = FileField('Profile Photo',
                                   validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    rider_vehicle_registration = FileField('Vehicle Registration (OR/CR)',
                                          validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'pdf'], 'Images and PDF files only!')])
    rider_clearance = FileField('NBI or Police Clearance',
                               validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'pdf'], 'Images and PDF files only!')])

    submit = SubmitField('Create Account')

class OTPVerificationForm(FlaskForm):
    otp_code = StringField('OTP Code', validators=[DataRequired(), Length(min=6, max=6, message='OTP code must be 6 digits')])
    submit = SubmitField('Verify Email')

class BecomeSellerForm(FlaskForm):
    business_name = StringField('Business Name', validators=[DataRequired(), Length(max=100)])
    business_description = TextAreaField('Business Description', validators=[DataRequired(), Length(min=10)])
    business_address = TextAreaField('Business Address', validators=[DataRequired(), Length(min=5)])
    business_phone = TelField('Business Phone', validators=[DataRequired(), Length(min=6, max=20)])
    tax_id = StringField('Tax ID', validators=[Optional(), Length(max=50)])
    business_permit = FileField('Business Permit', validators=[DataRequired(message='Business permit is required'), FileAllowed(['jpg', 'png', 'jpeg', 'pdf'], 'Images and PDF files only!')])

class CheckoutForm(FlaskForm):
    shipping_address = TextAreaField('Shipping Address', validators=[Optional(), Length(min=5)])
    # Optional structured fields for prefill/edit
    house_number = StringField('House/Unit No.', validators=[Optional(), Length(max=50)])
    street = StringField('Street', validators=[Optional(), Length(max=150)])
    barangay = StringField('Barangay', validators=[Optional(), Length(max=100)])
    city = StringField('City', validators=[Optional(), Length(max=100)])
    province = StringField('Province', validators=[Optional(), Length(max=100)])
    postal_code = StringField('Postal Code', validators=[Optional(), Length(max=20)])
    payment_method = SelectField('Payment Method', choices=[('cod', 'Cash on Delivery'), ('online', 'Online Payment')], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])

class ReviewForm(FlaskForm):
    product_id = HiddenField('Product ID', validators=[DataRequired()])
    rating = SelectField('Rating', choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5')], validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[Optional(), Length(max=1000)])

class CartUpdateForm(FlaskForm):
    cart_id = HiddenField('Cart ID', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0, max=999)])

class CartAddForm(FlaskForm):
    product_id = HiddenField('Product ID', validators=[DataRequired()])
    variant_id = HiddenField('Variant ID', validators=[Optional()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1, max=999)])

class SellerProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=200)])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    stock_quantity = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    image = FileField('Product Image', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    status = SelectField('Status', choices=[('active','Active'),('inactive','Inactive'),('out_of_stock','Out of Stock')], validators=[Optional()])

class OrderStatusForm(FlaskForm):
    status = SelectField('Status', choices=[('pending','Pending'),('confirmed','Confirmed'),('preparing','Preparing'),('shipped','Shipped'),('on_the_way','On the way'),('delivered','Delivered'),('cancelled','Cancelled')], validators=[DataRequired()])

class AdminNotesForm(FlaskForm):
    admin_notes = TextAreaField('Admin Notes', validators=[Optional(), Length(max=1000)])

class RejectNotesForm(FlaskForm):
    admin_notes = TextAreaField('Admin Notes', validators=[DataRequired(), Length(min=3)])

class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])

class SystemSettingsForm(FlaskForm):
    site_name = StringField('Site Name', validators=[DataRequired(), Length(max=100)])
    site_description = TextAreaField('Site Description', validators=[Optional(), Length(max=500)])
    admin_email = StringField('Admin Email', validators=[DataRequired(), Email()])
    support_email = StringField('Support Email', validators=[DataRequired(), Email()])
    maintenance_mode = RadioField('Maintenance Mode', 
                                 choices=[('0', 'Disabled'), ('1', 'Enabled')], 
                                 default='0', validators=[DataRequired()])
    max_products_per_seller = IntegerField('Max Products per Seller', 
                                          validators=[Optional(), NumberRange(min=1, max=10000)])
    order_auto_cancel_days = IntegerField('Auto Cancel Orders After (Days)', 
                                         validators=[Optional(), NumberRange(min=1, max=365)])
    featured_products_limit = IntegerField('Featured Products Limit', 
                                          validators=[Optional(), NumberRange(min=1, max=100)])
    default_currency = SelectField('Default Currency', 
                                  choices=[('USD', 'USD'), ('EUR', 'EUR'), ('PHP', 'PHP')], 
                                  validators=[DataRequired()])
    timezone = SelectField('Timezone', 
                          choices=[('UTC', 'UTC'), ('America/New_York', 'Eastern Time'), 
                                  ('America/Chicago', 'Central Time'), ('America/Los_Angeles', 'Pacific Time'),
                                  ('Europe/London', 'London'), ('Asia/Manila', 'Manila')], 
                          validators=[DataRequired()])
    require_email_verification = RadioField('Require Email Verification',
                                           choices=[('0', 'No'), ('1', 'Yes')],
                                           default='1', validators=[Optional()])
    session_lifetime = IntegerField('Session Lifetime (minutes)',
                                   validators=[Optional(), NumberRange(min=5, max=1440)])
    max_login_attempts = IntegerField('Max Login Attempts',
                                     validators=[Optional(), NumberRange(min=1, max=10)])
    enable_cod = RadioField('Enable Cash on Delivery',
                           choices=[('0', 'No'), ('1', 'Yes')],
                           default='1', validators=[Optional()])
    enable_card = RadioField('Enable Card Payments',
                            choices=[('0', 'No'), ('1', 'Yes')],
                            default='0', validators=[Optional()])
    payment_provider = SelectField('Payment Provider',
                                  choices=[('stripe', 'Stripe'), ('paypal', 'PayPal'), 
                                          ('paymongo', 'PayMongo'), ('none', 'None')],
                                  validators=[Optional()])
    payment_public_key = StringField('Payment Public Key', validators=[Optional(), Length(max=200)])
    smtp_host = StringField('SMTP Host', validators=[Optional(), Length(max=100)])
    smtp_port = IntegerField('SMTP Port', validators=[Optional(), NumberRange(min=1, max=65535)])
    smtp_tls = RadioField('SMTP TLS',
                         choices=[('0', 'No'), ('1', 'Yes')],
                         default='1', validators=[Optional()])
    email_from = StringField('Email From Address', validators=[Optional(), Email()])
    email_theme = SelectField('Email Theme',
                             choices=[('default', 'Default'), ('modern', 'Modern'), ('minimal', 'Minimal')],
                             validators=[Optional()])

# Additional forms for enhanced authentication
class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Change Password', id='password_submit')

# Seller application form (same as BecomeSellerForm but renamed for clarity)
class SellerApplicationForm(FlaskForm):
    business_name = StringField('Business Name', validators=[DataRequired(), Length(max=100)])
    business_description = TextAreaField('Business Description', validators=[DataRequired(), Length(min=10)])
    business_address = TextAreaField('Business Address', validators=[DataRequired(), Length(min=5)])
    business_phone = TelField('Business Phone', validators=[DataRequired(), Length(min=6, max=20)])
    tax_id = StringField('Tax ID', validators=[Optional(), Length(max=50)])

# Search and filter forms
class SearchForm(FlaskForm):
    query = StringField('Search', validators=[Optional(), Length(max=200)])
    category = SelectField('Category', coerce=int, validators=[Optional()])
    min_price = FloatField('Min Price', validators=[Optional(), NumberRange(min=0)])
    max_price = FloatField('Max Price', validators=[Optional(), NumberRange(min=0)])
    sort = SelectField('Sort By', choices=[
        ('relevance', 'Relevance'),
        ('price_low', 'Price: Low to High'),
        ('price_high', 'Price: High to Low'),
        ('rating', 'Rating'),
        ('newest', 'Newest'),
        ('name', 'Name')
    ], validators=[Optional()])

class ProfileUpdateForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    phone = TelField('Phone', validators=[Optional(), Length(max=20)])
    # Structured address
    house_number = StringField('House/Unit No.', validators=[Optional(), Length(max=50)])
    street = StringField('Street', validators=[Optional(), Length(max=150)])
    barangay = StringField('Barangay', validators=[Optional(), Length(max=100)])
    city = StringField('City', validators=[Optional(), Length(max=100)])
    province = StringField('Province', validators=[Optional(), Length(max=100)])
    postal_code = StringField('Postal Code', validators=[Optional(), Length(max=20)])
    country = StringField('Country', validators=[Optional(), Length(max=100)])
    address = TextAreaField('Complete Address', validators=[Optional(), Length(max=500)])
    profile_image = FileField('Profile Image', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Update Profile')

class RiderRegistrationForm(FlaskForm):
    """Form for rider registration with document upload (for existing users)"""
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    phone = TelField('Phone', validators=[DataRequired(), Length(max=20)])
    
    # Address fields
    house_number = StringField('House/Unit No.', validators=[Optional(), Length(max=50)])
    street = StringField('Street', validators=[Optional(), Length(max=150)])
    barangay = StringField('Barangay', validators=[Optional(), Length(max=100)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    province = StringField('Province', validators=[Optional(), Length(max=100)])
    postal_code = StringField('Postal Code', validators=[Optional(), Length(max=20)])
    address = TextAreaField('Complete Address', validators=[Optional(), Length(max=500)])
    country = SelectField('Country', choices=[
        ('Philippines', 'Philippines'),
        ('United States', 'United States'),
        ('Canada', 'Canada'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    
    # Vehicle information
    vehicle_type = SelectField('Vehicle Type', choices=[
        ('motorcycle', 'Motorcycle'),
        ('bicycle', 'Bicycle'),
        ('car', 'Car'),
        ('scooter', 'Scooter')
    ], validators=[DataRequired()])
    vehicle_plate_number = StringField('Vehicle Plate Number', validators=[DataRequired(), Length(max=20)])
    vehicle_model = StringField('Vehicle Model', validators=[DataRequired(), Length(max=100)])
    
    # Document uploads
    government_id = FileField('Government ID (Driver\'s License or National ID)', 
                             validators=[DataRequired(message='Government ID is required'), 
                                       FileAllowed(['jpg', 'png', 'jpeg', 'pdf'], 'Images and PDF files only!')])
    vehicle_registration = FileField('Vehicle Registration (OR/CR)', 
                                    validators=[Optional(), 
                                              FileAllowed(['jpg', 'png', 'jpeg', 'pdf'], 'Images and PDF files only!')])
    profile_photo = FileField('Profile Photo', 
                             validators=[DataRequired(message='Profile photo is required'), 
                                       FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    clearance = FileField('NBI or Police Clearance', 
                         validators=[Optional(), 
                                   FileAllowed(['jpg', 'png', 'jpeg', 'pdf'], 'Images and PDF files only!')])
    
    submit = SubmitField('Submit Application')
