# Rider Registration System

## Overview
This document describes the complete rider registration and onboarding process for the Pawfect Finds e-commerce delivery platform.

## Registration Flow

### 1. Account Creation
**Route:** `/rider/register`

New riders visit the registration portal and complete a comprehensive form that includes:

- **Personal Information**
  - Full name (first and last)
  - Email address
  - Phone number
  - Password (with confirmation)

- **Address Information**
  - House/Unit number
  - Street
  - Barangay
  - City (required)
  - Province
  - Postal code
  - Country

- **Vehicle Information**
  - Vehicle type (motorcycle, bicycle, car, scooter)
  - Plate number (optional)
  - Vehicle model (optional)

- **Required Documents**
  - Government ID (Driver's License or National ID) - **Required**
  - Profile photo - **Required**
  - Vehicle registration (OR/CR) - Optional
  - NBI or Police Clearance - Optional

### 2. Background Verification
**Admin Route:** `/rider/admin/applications`

After submission, the application enters the verification queue:

1. Admin reviews all submitted documents
2. Verification team checks:
   - Authenticity of government ID
   - Profile photo quality
   - Vehicle documentation (if provided)
   - Background clearance (if provided)
3. Admin can:
   - **Approve** - Move to next stage
   - **Reject** - Provide reason for rejection
   - Request additional information

**Application Statuses:**
- `pending` - Just submitted, awaiting review
- `under_review` - Being actively reviewed
- `approved` - Passed verification
- `rejected` - Did not pass verification

### 3. Training & Orientation
**Route:** `/rider/training`

Once approved, riders must complete a comprehensive training program:

#### Training Modules

**Module 1: Platform Overview**
- Understanding the delivery platform
- Real-time order updates via Socket.IO
- Dashboard features
- Earnings tracking

**Module 2: Using the Rider Dashboard**
- Going online/offline
- Accepting orders
- Managing deliveries
- Status updates

**Module 3: Delivery Protocols**
- Pickup procedures
- Delivery procedures
- Safety guidelines
- Product handling (especially pet products)

**Module 4: Customer Service Excellence**
- Professional conduct
- Communication standards
- Handling special situations
- Complaint resolution

**Module 5: Earnings & Performance**
- Payment structure
- Performance metrics
- Tips for success
- Bonus opportunities

### 4. Account Approval & Activation
**Route:** `/rider/training/complete`

After completing all training modules:
1. Rider clicks "Complete Training & Activate Account"
2. System:
   - Marks training as completed
   - Updates user role from `user` to `rider`
   - Creates rider availability record
   - Activates rider account
3. Rider is redirected to their dashboard
4. Can immediately start accepting delivery orders

## Real-time Features (Socket.IO)

Once active, riders benefit from real-time updates:

- **Instant Order Notifications:** New delivery opportunities appear immediately
- **Order Status Updates:** Real-time status changes
- **Availability Tracking:** Online/offline status management
- **Live Location Updates:** GPS tracking during deliveries

## Database Schema

### rider_applications
```sql
- id (PRIMARY KEY)
- user_id (FOREIGN KEY → users.id)
- vehicle_type (VARCHAR)
- vehicle_plate_number (VARCHAR)
- vehicle_model (VARCHAR)
- government_id (VARCHAR) - File path
- vehicle_registration (VARCHAR) - File path
- profile_photo (VARCHAR) - File path
- clearance (VARCHAR) - File path
- status (ENUM: pending, under_review, approved, rejected)
- admin_notes (TEXT)
- created_at (TIMESTAMP)
- reviewed_at (TIMESTAMP)
```

### rider_training
```sql
- id (PRIMARY KEY)
- user_id (FOREIGN KEY → users.id, UNIQUE)
- status (ENUM: not_started, in_progress, completed)
- completed_at (TIMESTAMP)
- training_score (INT)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### rider_availability
```sql
- id (PRIMARY KEY)
- rider_id (FOREIGN KEY → users.id, UNIQUE)
- is_online (BOOLEAN)
- is_available (BOOLEAN)
- current_latitude (DECIMAL)
- current_longitude (DECIMAL)
- last_online (TIMESTAMP)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### rider_documents
```sql
- id (PRIMARY KEY)
- rider_id (FOREIGN KEY → users.id)
- document_type (VARCHAR)
- document_path (VARCHAR)
- status (ENUM: pending, verified, rejected)
- expiry_date (DATE)
- uploaded_at (TIMESTAMP)
- verified_at (TIMESTAMP)
- notes (TEXT)
```

### rider_performance
```sql
- id (PRIMARY KEY)
- rider_id (FOREIGN KEY → users.id)
- total_deliveries (INT)
- completed_deliveries (INT)
- cancelled_deliveries (INT)
- average_rating (DECIMAL)
- total_earnings (DECIMAL)
- on_time_delivery_rate (DECIMAL)
- last_delivery_date (TIMESTAMP)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

## API Endpoints

### Public Endpoints
- `GET /rider/register` - Display registration form
- `POST /rider/register` - Submit registration
- `GET /rider/application-status/<id>` - View application status

### Authenticated Rider Endpoints
- `GET /rider/my-application` - View own application
- `GET /rider/training` - Access training modules
- `POST /rider/training/complete` - Complete training

### Admin Endpoints
- `GET /rider/admin/applications` - List all applications
- `POST /rider/admin/application/<id>/review` - Approve/reject

## File Uploads

Documents are stored in:
- `/static/uploads/rider_documents/` - IDs, vehicle docs, clearance
- `/static/uploads/rider_profiles/` - Profile photos

Files are processed with:
- Unique filename generation (UUID + email hash)
- Image optimization (resizing, compression)
- Format conversion (all photos → JPEG)
- Security validation (file type checking)

## Setup Instructions

1. **Run Database Migration:**
   ```bash
   mysql -u root -p pawfect_findsdatabase < database/rider_registration_schema.sql
   ```

2. **Create Upload Directories:**
   ```bash
   mkdir -p static/uploads/rider_documents
   mkdir -p static/uploads/rider_profiles
   ```

3. **Verify Blueprint Registration:**
   Check that `rider_registration_controller` is imported and registered in `app/__init__.py`

4. **Test the Flow:**
   - Visit `/rider/register`
   - Submit an application
   - Log in as admin to review
   - Complete training as rider

## Integration with Existing System

The rider registration system integrates seamlessly with:

- **User Authentication** - Uses existing auth system
- **File Upload System** - Uses existing upload infrastructure  
- **WebSocket (Socket.IO)** - Real-time order notifications
- **Dashboard** - Existing rider dashboard (`/rider/dashboard`)
- **Delivery Management** - Existing order acceptance flow

## Security Features

- CSRF protection on all forms
- File upload validation
- Role-based access control
- Admin-only application review
- Secure password hashing
- Document encryption (recommended)

## Future Enhancements

- Email notifications for status changes
- SMS verification
- Video training modules
- Training quizzes with scoring
- Document expiry tracking
- Background check API integration
- Automated document verification (OCR)
- Multi-language support

## Support

For issues or questions:
- Check application logs
- Review error messages
- Contact system administrator
- Refer to main project documentation
