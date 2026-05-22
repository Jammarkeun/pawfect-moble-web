# Seller & Rider Approval Workflow

## Overview
This document describes the complete approval workflow for sellers and riders registering on Pawfect Finds.

## Flow Diagram

```
User Registers
    ↓
Multi-Step Form (3 Steps)
    ↓
Form Submitted → OTP Email Sent
    ↓
User Enters OTP Code
    ↓
Account Created (auth user + profile)
    ↓
For SELLER/RIDER:
├─ Seller Request/Rider Application created with 'pending' status
├─ User redirected to "Waiting for Approval" page
└─ Email sent: "Your application has been submitted"
    ↓
ADMIN REVIEW PHASE:
├─ Admin views seller/rider requests at:
│  ├─ /admin/seller-requests (all sellers)
│  ├─ /admin/rider-requests (all riders)
│  └─ Filters by: pending, approved, rejected
│
├─ Admin clicks "View" to see full application details
├─ Admin reviews documents and information
├─ Admin chooses to:
│  ├─ APPROVE
│  │  ├─ Application status → 'approved'
│  │  ├─ User role → 'seller' or 'rider'
│  │  ├─ User can NOW LOGIN
│  │  └─ Email sent: "Congratulations! You're approved!"
│  │
│  └─ REJECT
│     ├─ Application status → 'rejected'
│     ├─ Admin enters rejection reason
│     └─ Email sent: "Your application was not approved"
    ↓
For BUYER ACCOUNTS:
├─ Account created as 'user' role
├─ Status set to 'pending'
├─ Redirected to "Waiting for Approval" page
└─ Admin approves in Users section, can then login
```

## User Registration Workflow

### Step 1: Multi-Step Form Completion
- User selects account type: Buyer / Seller / Rider
- Step 1: Personal info (name, email, password, phone)
- Step 2: Location (country, city, province, etc.)
- Step 3: ID Picture + Type-Specific Fields
  - **Seller**: business_name, business_description, business_address, business_phone, tax_id, business_permit
  - **Rider**: vehicle_type, vehicle_plate_number, vehicle_model, govt_id, profile_photo, vehicle_registration, clearance

### Step 2: Form Submission & OTP
- Form validates all required fields
- Backend creates auth user (Supabase Auth)
- Backend stores signup_data in session
- OTP code generated (6-digit)
- Email sent with OTP code
- User redirected to OTP verification page

### Step 3: OTP Verification
- User enters OTP code
- Code verified against session['signup_data']['otp_code']
- On match:
  - User profile created in 'profiles' table
  - For Seller: SellerRequest created with status='pending'
  - For Rider: Rider application created with status='pending'
  - For Buyer: User created with status='pending'
  - Session cleared
  - User redirected to approval_pending.html

### Step 4: Waiting for Approval
- User sees "Approval Pending" message
- Message shows what happens next
- For Sellers/Riders: "Our admin team will review your application"
- For Buyers: "Your account is pending admin approval"
- User **CANNOT LOGIN** until approved

## Admin Approval Process

### Viewing Seller Requests
**URL**: `/admin/seller-requests`

**Features**:
- Filter by status: all, pending, approved, rejected
- Table shows:
  - User name & email
  - Business name & phone
  - Application status
  - Submitted date
  - Action buttons

**Actions for Pending Requests**:
- **View**: Click to see full details
- **Approve**: Approve immediately or add notes
- **Reject**: Reject with reason

### Viewing Seller Request Details
**URL**: `/admin/seller-requests/<id>/details`

**Shows**:
- Personal Information: name, email, phone, account status
- Business Information: business name, phone, tax ID, description, address
- Documents: business permit (downloadable)
- Admin Notes (if any previous notes)
- Action Buttons (Approve/Reject)

**Actions**:
1. Review all information and documents
2. Click "Approve" or "Reject"
3. Optionally add admin notes
4. Submit

**On Approve**:
- SellerRequest.status → 'approved'
- User.role → 'seller'
- User CAN NOW LOGIN
- Email sent: "Congratulations! Your seller application is approved!"

**On Reject**:
- SellerRequest.status → 'rejected'
- User.role stays 'user' (cannot be seller)
- User CANNOT become seller without reapplying
- Email sent: "Your seller application was not approved. Reason: [reason]"

### Viewing Rider Requests
**URL**: `/admin/rider-requests`

**Same workflow as seller requests but for riders**
- Filters: all, pending, approved, rejected
- Shows vehicle type, application date
- Documents: govt ID, vehicle registration, profile photo, clearance

### Viewing Rider Request Details
**URL**: `/admin/rider-requests/<id>/details`

**Shows**:
- Personal Information
- Vehicle Information: type, model, plate number
- Documents: govt ID, vehicle registration, profile photo, clearance
- Admin Notes
- Approve/Reject buttons

**On Approve**:
- Rider application status → 'approved'
- User.role → 'rider'
- User CAN NOW LOGIN
- Email sent: "Congratulations! Your rider application is approved!"

**On Reject**:
- Rider application status → 'rejected'
- User.role stays 'user'
- User cannot be rider without reapplying
- Email sent: "Your rider application was not approved."

## Email Notifications

### After Registration (Before Approval)
- **To**: user@example.com
- **Subject**: "Verify your email"
- **Content**: OTP code for verification

### After OTP Verification
- **To**: user@example.com
- **Subject**: "Application Received" (if seller/rider)
- **Content**: "Your application has been submitted. We'll notify you once reviewed."

### When Seller Approved
- **To**: seller@example.com
- **Subject**: "🎉 Your Seller Application is Approved!"
- **Content**: 
  - Congratulations message
  - Next steps (login, complete profile, add products)
  - Login button

### When Seller Rejected
- **To**: seller@example.com
- **Subject**: "Seller Application Status Update"
- **Content**:
  - Application was not approved
  - Reason for rejection
  - Can reapply

### When Rider Approved
- **To**: rider@example.com
- **Subject**: "🚀 Your Rider Application is Approved!"
- **Content**:
  - Welcome to rider network
  - Vehicle type confirmed
  - Next steps
  - Login button

### When Rider Rejected
- **To**: rider@example.com
- **Subject**: "Rider Application Status Update"
- **Content**:
  - Application was not approved
  - Reason for rejection
  - Can reapply

## Database Schema

### seller_requests table
```
- id (primary key)
- user_id (foreign key to profiles)
- business_name (string)
- business_description (text)
- business_address (text)
- business_phone (string)
- tax_id (string, optional)
- business_permit (string - file path)
- status (enum: pending, approved, rejected)
- admin_notes (text, optional)
- requested_at (timestamp)
```

### rider_applications table
```
- id (primary key)
- user_id (foreign key to profiles)
- vehicle_type (string)
- vehicle_plate_number (string)
- vehicle_model (string)
- government_id_path (string - file path)
- vehicle_registration_path (string - file path)
- profile_photo_path (string - file path)
- clearance_path (string - file path)
- status (enum: pending, approved, rejected)
- admin_notes (text, optional)
- created_at (timestamp)
```

### profiles table (updated)
```
- id (primary key)
- email (unique)
- first_name
- last_name
- phone
- role (enum: user, seller, rider, admin)
- status (enum: active, pending, inactive)
- ... other fields
```

## Status Mapping

### User Roles
- **user** (buyer): Can browse and purchase products
- **seller**: Can manage products and orders (after approval)
- **rider**: Can accept deliveries (after approval)
- **admin**: Can manage platform

### User Status
- **active**: Account is active and can login
- **pending**: Account created but awaiting approval
- **inactive**: Account disabled

### Request Status
- **pending**: Awaiting admin review
- **approved**: Request approved, user role updated, can login
- **rejected**: Request rejected, user cannot assume that role

## Login Restrictions

**User can login only if**:
- Account exists (Supabase Auth user created)
- User status is 'active'
- For sellers: SellerRequest.status must be 'approved' AND User.role must be 'seller'
- For riders: Rider application.status must be 'approved' AND User.role must be 'rider'

## Implementation Code References

### Controller
- [app/controllers/admin_requests_controller.py](../app/controllers/admin_requests_controller.py)
- Routes:
  - GET `/admin/seller-requests`
  - GET `/admin/seller-requests/<id>/details`
  - POST `/admin/seller-requests/<id>/approve`
  - POST `/admin/seller-requests/<id>/reject`
  - Same for rider (change endpoint to `/admin/rider-requests`)

### Models
- [app/models/seller_request.py](../app/models/seller_request.py)
  - `approve_request(request_id, admin_notes)`
  - `reject_request(request_id, admin_notes)`
- [app/models/rider.py](../app/models/rider.py)
  - `update_application_status(application_id, status, admin_notes)`

### Email Service
- [app/services/email_service.py](../app/services/email_service.py)
- Methods:
  - `send_seller_approval_email(email, first_name, business_name)`
  - `send_seller_rejection_email(email, first_name, reason)`
  - `send_rider_approval_email(email, first_name, vehicle_type)`
  - `send_rider_rejection_email(email, first_name, reason)`

### Templates
- Admin views:
  - [templates/admin/seller_request_details.html](../templates/admin/seller_request_details.html)
  - [templates/admin/rider_request_details.html](../templates/admin/rider_request_details.html)
- User-facing:
  - [templates/auth/approval_pending.html](../templates/auth/approval_pending.html)

## Testing Workflow

1. **Register as Seller**:
   - Go to `/auth/signup`
   - Select "Seller"
   - Fill 3-step form
   - Verify OTP
   - Should see "Application Under Review" page
   - Cannot login yet

2. **Admin Approves**:
   - Go to `/admin/seller-requests`
   - Find pending seller
   - Click "View" or "Approve"
   - Add optional notes
   - Click "Approve Seller"
   - Should see success message

3. **Seller Can Now Login**:
   - Go to `/auth/login`
   - Use registered email & password
   - Should login successfully
   - Should have 'seller' role access

4. **Check Email**:
   - Seller should receive approval email
   - Email should say "Congratulations! Your seller application is approved!"
   - Email should have login button

## Future Enhancements

- [ ] Bulk approve/reject requests
- [ ] Email templates in admin panel
- [ ] Approval verification document checklist
- [ ] Approval timeline tracking
- [ ] Appeal process for rejected applications
- [ ] Seller/Rider suspension capability
- [ ] Performance ratings for approved users
