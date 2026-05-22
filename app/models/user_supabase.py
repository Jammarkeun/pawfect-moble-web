"""
User Model for Supabase (using 'profiles' table)

This replaces the MySQL-based user.py model.
Copy this content to app/models/user.py
"""

from app.services.database import Database
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    """User model for handling user operations with Supabase profiles table"""
    
    # Table name in Supabase
    TABLE_NAME = 'profiles'
    
    def __init__(self):
        self.db = Database()
    
    @classmethod
    def create(cls, username, email, password, first_name, last_name, phone=None,
               address=None, country=None, city=None, province=None,
               house_number=None, street=None, barangay=None, postal_code=None,
               id_picture=None, profile_image=None, role='user'):
        """Create a new user in profiles table"""
        db = Database()

        # Check if user already exists
        if cls.get_by_email(email) or cls.get_by_username(username):
            return None

        password_hash = generate_password_hash(password)

        user_data = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'address': address,
            'country': country or 'Philippines',
            'city': city or 'Manila',
            'province': province,
            'house_number': house_number,
            'street': street,
            'barangay': barangay,
            'postal_code': postal_code,
            'id_picture': id_picture,
            'profile_image': profile_image,
            'role': role,
            'status': 'active'
        }
        
        # Insert and return the created user
        new_user = db.insert(cls.TABLE_NAME, user_data)
        return new_user
    
    @classmethod
    def get_by_id(cls, user_id):
        """Get user by ID from profiles table"""
        db = Database()
        return db.select_one(cls.TABLE_NAME, filters={'id': user_id})
    
    @classmethod
    def get_by_email(cls, email):
        """Get user by email from profiles table"""
        db = Database()
        return db.select_one(cls.TABLE_NAME, filters={'email': email})
    
    @classmethod
    def get_by_username(cls, username):
        """Get user by username from profiles table"""
        db = Database()
        return db.select_one(cls.TABLE_NAME, filters={'username': username})
    
    @classmethod
    def authenticate(cls, email, password):
        """Authenticate user by email and password"""
        user = cls.get_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            return user
        return None
    
    @classmethod
    def update(cls, user_id, **kwargs):
        """Update user information in profiles table"""
        db = Database()

        # Build update data
        allowed_fields = [
            'username', 'email', 'first_name', 'last_name', 'phone', 'address', 
            'profile_image', 'country', 'city', 'province', 'house_number', 
            'street', 'barangay', 'postal_code'
        ]
        
        update_data = {}
        for field, value in kwargs.items():
            if field in allowed_fields:
                update_data[field] = value

        if not update_data:
            return False

        db.update(cls.TABLE_NAME, data=update_data, filters={'id': user_id})
        return True
    
    @classmethod
    def update_password(cls, user_id, new_password):
        """Update user password"""
        db = Database()
        password_hash = generate_password_hash(new_password)
        db.update(cls.TABLE_NAME, data={'password_hash': password_hash}, filters={'id': user_id})
        return True
    
    @classmethod
    def update_role(cls, user_id, new_role):
        """Update user role (admin function)"""
        db = Database()
        db.update(cls.TABLE_NAME, data={'role': new_role}, filters={'id': user_id})
        return True
    
    @classmethod
    def update_status(cls, user_id, status):
        """Update user status (admin function)"""
        db = Database()
        db.update(cls.TABLE_NAME, data={'status': status}, filters={'id': user_id})
        return True
    
    @classmethod
    def get_all_users(cls, role=None, status=None, limit=None, offset=0):
        """Get all users with optional filters from profiles table"""
        db = Database()
        
        # For complex queries, use the client directly
        query = db.client.table(cls.TABLE_NAME).select('*')
        
        if role:
            query = query.eq('role', role)
        
        if status:
            query = query.eq('status', status)
        
        query = query.order('created_at', desc=True)
        
        if limit:
            query = query.limit(limit).range(offset, offset + limit - 1)
        
        response = query.execute()
        return response.data
    
    @classmethod
    def get_users_count(cls, role=None, status=None):
        """Get count of users with optional filters"""
        db = Database()
        
        query = db.client.table(cls.TABLE_NAME).select('*', count='exact')
        
        if role:
            query = query.eq('role', role)
        
        if status:
            query = query.eq('status', status)
        
        response = query.execute()
        return response.count
    
    @classmethod
    def delete(cls, user_id):
        """Delete a user (admin function)"""
        db = Database()
        db.delete(cls.TABLE_NAME, filters={'id': user_id})
        return True
    
    @classmethod
    def get_sellers(cls):
        """Get all sellers"""
        return cls.get_all_users(role='seller', status='active')
    
    @classmethod
    def get_customers(cls):
        """Get all customers"""
        return cls.get_all_users(role='user', status='active')
