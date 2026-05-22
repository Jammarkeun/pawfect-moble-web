from app.services.database import Database
from gotrue.errors import AuthApiError

class User:
    """User model using Supabase Auth + profiles table"""
    
    TABLE_NAME = 'profiles'
    
    def __init__(self):
        self.db = Database()
    
    @classmethod
    def create(cls, username, email, password, first_name, last_name, phone=None,
               address=None, country=None, city=None, province=None,
               house_number=None, street=None, barangay=None, postal_code=None,
               id_picture=None, profile_image=None, role='user'):
        """Create user in Supabase Auth + profiles table"""
        db = Database()
        email = email.strip().lower()

        existing_auth_user = cls.get_auth_user_by_email(email)
        existing_profile = cls.get_by_email(email)

        if existing_auth_user and existing_profile:
            raise Exception(f'Email already exists: {email}')

        try:
            # Step 1: Create or recover auth user
            if existing_auth_user:
                user_id = existing_auth_user.id
                print(f"✓ Existing auth user found for {email}, recovering profile creation.")
            else:
                try:
                    auth_response = db.client.auth.sign_up({
                        'email': email,
                        'password': password
                    })
                    
                    if not auth_response.user:
                        raise Exception(f"Supabase Auth failed to create user for {email}")
                    
                    user_id = auth_response.user.id
                    print(f"✓ Auth user created: {user_id}")
                except Exception as auth_error:
                    auth_error_text = str(auth_error).lower()
                    if 'already registered' in auth_error_text or 'email already exists' in auth_error_text:
                        existing_auth_user = cls.get_auth_user_by_email(email)
                        if existing_auth_user:
                            user_id = existing_auth_user.id
                            print(f"✓ Existing auth user recovered after signup failure for {email}")
                        else:
                            raise Exception(f"Authentication failed: {str(auth_error)}")
                    else:
                        raise Exception(f"Authentication failed: {str(auth_error)}")
            
            # Step 2: Create profile (OPTIONAL - if it fails, we still have the auth user)
            profile_data = {
                'id': user_id,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
                'role': role,
                'status': 'active'
            }
            
            # Add optional fields only if provided
            if address:
                profile_data['address'] = address
            if country:
                profile_data['country'] = country
            if city:
                profile_data['city'] = city
            if province:
                profile_data['province'] = province
            if house_number:
                profile_data['house_number'] = house_number
            if street:
                profile_data['street'] = street
            if barangay:
                profile_data['barangay'] = barangay
            if postal_code:
                profile_data['postal_code'] = postal_code
            if id_picture:
                profile_data['id_picture'] = id_picture
            if profile_image:
                profile_data['avatar_url'] = profile_image
            
            try:
                print(f"Inserting profile with {len(profile_data)} fields...")
                db.insert(cls.TABLE_NAME, profile_data)
                print(f"✓ Profile created with all fields")
                return profile_data
            except Exception as full_insert_error:
                print(f"⚠ Full profile insert failed: {str(full_insert_error)[:100]}")
                existing_profile = db.select_one(cls.TABLE_NAME, filters={'email': email}) or db.select_one(cls.TABLE_NAME, filters={'id': user_id})
                if existing_profile:
                    print("✓ Existing profile found after full insert failure")
                    return existing_profile
                # Try with minimal fields
                try:
                    minimal_data = {
                        'id': user_id,
                        'email': email,
                        'first_name': first_name,
                        'last_name': last_name,
                    }
                    db.insert(cls.TABLE_NAME, minimal_data)
                    print(f"✓ Minimal profile created")
                    return minimal_data
                except Exception as min_error:
                    print(f"⚠ Even minimal insert failed: {str(min_error)[:100]}")
                    existing_profile = db.select_one(cls.TABLE_NAME, filters={'email': email}) or db.select_one(cls.TABLE_NAME, filters={'id': user_id})
                    if existing_profile:
                        print("✓ Existing profile found after minimal insert failure")
                        return existing_profile
                    # Return minimal user data even if profile insert fails
                    # At least the auth user exists and can login
                    print(f"✓ BUT: Auth user {user_id} exists and can login")
                    return {
                        'id': user_id,
                        'email': email,
                        'first_name': first_name,
                        'last_name': last_name,
                    }
                    
        except Exception as e:
            print(f"❌ USER CREATE ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    @classmethod
    def get_by_id(cls, user_id):
        """Get user by ID from profiles table"""
        db = Database()
        user = db.select_one(cls.TABLE_NAME, filters={'id': user_id})
        if user:
            # Normalize role: Flutter app uses 'customer', web templates use 'user'
            if user.get('role') == 'customer':
                user['role'] = 'user'
        return user
    
    @classmethod
    def get_by_email(cls, email):
        """Get user by email from profiles table"""
        if not email:
            return None
        email = email.strip().lower()
        db = Database()
        return db.select_one(cls.TABLE_NAME, filters={'email': email})

    @classmethod
    def get_auth_user_by_email(cls, email):
        """Get Supabase Auth user by email."""
        if not email:
            return None
        email = email.strip().lower()
        db = Database()

        try:
            if hasattr(db.client.auth, 'admin') and hasattr(db.client.auth.admin, 'get_user_by_email'):
                return db.client.auth.admin.get_user_by_email(email)
        except Exception:
            pass

        return None

    @classmethod
    def email_exists(cls, email):
        """Check whether an email is already registered in profiles or Supabase Auth."""
        if not email:
            return False
        email = email.strip().lower()
        db = Database()

        if db.select_one(cls.TABLE_NAME, filters={'email': email}):
            return True

        return bool(cls.get_auth_user_by_email(email))

    @classmethod
    def authenticate(cls, email, password):
        """Authenticate using Supabase Auth"""
        db = Database()
        
        try:
            auth_response = db.client.auth.sign_in_with_password({
                'email': email,
                'password': password
            })
            
            if auth_response.user:
                profile = cls.get_by_id(auth_response.user.id)
                return profile
            return None
        except AuthApiError as e:
            print(f"Auth error: {e}")
            return None
        except Exception as e:
            print(f"Error authenticating: {e}")
            return None
    
    @classmethod
    def update(cls, user_id, **kwargs):
        """Update user profile"""
        db = Database()
        
        allowed_fields = [
            'first_name', 'last_name', 'phone', 'address', 'avatar_url'
        ]
        
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_data:
            return False
        
        db.update(cls.TABLE_NAME, data=update_data, filters={'id': user_id})
        return True
    
    @classmethod
    def update_password(cls, user_id, new_password):
        """Update password via Supabase Auth"""
        db = Database()
        try:
            db.client.auth.admin.update_user_by_id(user_id, {'password': new_password})
            return True
        except Exception as e:
            print(f"Error updating password: {e}")
            return False
    
    @classmethod
    def update_role(cls, user_id, new_role):
        """Update user role"""
        db = Database()
        db.update(cls.TABLE_NAME, data={'role': new_role}, filters={'id': user_id})
        return True
    
    @classmethod
    def update_status(cls, user_id, status):
        """Update user status"""
        db = Database()
        db.update(cls.TABLE_NAME, data={'status': status}, filters={'id': user_id})
        return True
    
    @classmethod
    def get_all_users(cls, role=None, status=None, limit=None, offset=0):
        """Get all users with filters"""
        db = Database()
        
        try:
            query = db.client.table(cls.TABLE_NAME).select('*')
            
            if role:
                query = query.eq('role', role)
            
            if status:
                query = query.eq('status', status)
            
            query = query.order('created_at', desc=True)
            
            if limit:
                query = query.limit(limit).range(offset, offset + limit - 1)
            
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    @classmethod
    def get_users_count(cls, role=None, status=None):
        """Get count of users"""
        db = Database()
        
        try:
            query = db.client.table(cls.TABLE_NAME).select('*', count='exact')
            
            if role:
                query = query.eq('role', role)
            
            if status:
                query = query.eq('status', status)
            
            response = query.execute()
            return response.count if response.count else 0
        except Exception as e:
            print(f"Error counting users: {e}")
            return 0
    
    @classmethod
    def delete(cls, user_id):
        """Delete user"""
        db = Database()
        try:
            db.client.auth.admin.delete_user(user_id)
            db.delete(cls.TABLE_NAME, filters={'id': user_id})
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    @classmethod
    def get_sellers(cls):
        """Get all sellers"""
        return cls.get_all_users(role='seller', status='active')
    
    @classmethod
    def get_customers(cls):
        """Get all customers"""
        return cls.get_all_users(role='customer', status='active')
