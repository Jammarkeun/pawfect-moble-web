"""
EXAMPLE: Refactored User Model for Supabase

This is an example of how to update your user.py model file to work with Supabase.
Compare this with your current app/models/user.py to see the differences.

Key changes:
1. Use db.select() instead of raw SQL SELECT
2. Use db.insert() instead of raw SQL INSERT
3. Use db.update() instead of raw SQL UPDATE
4. Use db.delete() instead of raw SQL DELETE
5. Use db.select_one() for single records
"""

from app.services.database import Database
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    """User model for handling user operations with Supabase"""
    
    def __init__(self):
        self.db = Database()
    
    @classmethod
    def create(cls, username, email, password, first_name, last_name, phone=None,
               address=None, country=None, city=None, province=None,
               house_number=None, street=None, barangay=None, postal_code=None,
               id_picture=None, profile_image=None, role='user'):
        """Create a new user"""
        db = Database()

        # Check if user already exists
        if cls.get_by_email(email) or cls.get_by_username(username):
            return None

        password_hash = generate_password_hash(password)

        # BEFORE (MySQL):
        # query = '''INSERT INTO users (...) VALUES (%s, %s, ...)'''
        # user_id = db.execute_query(query, (...))
        
        # AFTER (Supabase):
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
        new_user = db.insert('users', user_data)
        return new_user
    
    @classmethod
    def get_by_id(cls, user_id):
        """Get user by ID"""
        db = Database()
        
        # BEFORE (MySQL):
        # query = "SELECT * FROM users WHERE id = %s"
        # return db.execute_query(query, (user_id,), fetch=True, fetchone=True)
        
        # AFTER (Supabase):
        return db.select_one('users', filters={'id': user_id})
    
    @classmethod
    def get_by_email(cls, email):
        """Get user by email"""
        db = Database()
        
        # BEFORE (MySQL):
        # query = "SELECT * FROM users WHERE email = %s"
        # return db.execute_query(query, (email,), fetch=True, fetchone=True)
        
        # AFTER (Supabase):
        return db.select_one('users', filters={'email': email})
    
    @classmethod
    def get_by_username(cls, username):
        """Get user by username"""
        db = Database()
        
        # BEFORE (MySQL):
        # query = "SELECT * FROM users WHERE username = %s"
        # return db.execute_query(query, (username,), fetch=True, fetchone=True)
        
        # AFTER (Supabase):
        return db.select_one('users', filters={'username': username})
    
    @classmethod
    def authenticate(cls, email, password):
        """Authenticate user by email and password"""
        user = cls.get_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            return user
        return None
    
    @classmethod
    def update(cls, user_id, **kwargs):
        """Update user information"""
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

        # BEFORE (MySQL):
        # query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
        # db.execute_query(query, values)
        
        # AFTER (Supabase):
        db.update('users', data=update_data, filters={'id': user_id})
        return True
    
    @classmethod
    def update_password(cls, user_id, new_password):
        """Update user password"""
        db = Database()
        password_hash = generate_password_hash(new_password)
        
        # BEFORE (MySQL):
        # query = "UPDATE users SET password_hash = %s WHERE id = %s"
        # db.execute_query(query, (password_hash, user_id))
        
        # AFTER (Supabase):
        db.update('users', data={'password_hash': password_hash}, filters={'id': user_id})
        return True
    
    @classmethod
    def update_role(cls, user_id, new_role):
        """Update user role (admin function)"""
        db = Database()
        
        # BEFORE (MySQL):
        # query = "UPDATE users SET role = %s WHERE id = %s"
        # db.execute_query(query, (new_role, user_id))
        
        # AFTER (Supabase):
        db.update('users', data={'role': new_role}, filters={'id': user_id})
        return True
    
    @classmethod
    def update_status(cls, user_id, status):
        """Update user status (admin function)"""
        db = Database()
        
        # BEFORE (MySQL):
        # query = "UPDATE users SET status = %s WHERE id = %s"
        # db.execute_query(query, (status, user_id))
        
        # AFTER (Supabase):
        db.update('users', data={'status': status}, filters={'id': user_id})
        return True
    
    @classmethod
    def get_all_users(cls, role=None, status=None, limit=None, offset=0):
        """Get all users with optional filters"""
        db = Database()
        
        # BEFORE (MySQL):
        # query = "SELECT * FROM users WHERE 1=1"
        # if role: query += " AND role = %s"
        # ...
        # return db.execute_query(query, params, fetch=True)
        
        # AFTER (Supabase):
        # For complex queries, use the client directly
        query = db.client.table('users').select('*')
        
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
        
        # BEFORE (MySQL):
        # query = "SELECT COUNT(*) as count FROM users WHERE 1=1"
        # ...
        # result = db.execute_query(query, params, fetch=True, fetchone=True)
        # return result['count'] if result else 0
        
        # AFTER (Supabase):
        query = db.client.table('users').select('*', count='exact')
        
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
        
        # BEFORE (MySQL):
        # query = "DELETE FROM users WHERE id = %s"
        # db.execute_query(query, (user_id,))
        
        # AFTER (Supabase):
        db.delete('users', filters={'id': user_id})
        return True
    
    @classmethod
    def get_sellers(cls):
        """Get all sellers"""
        return cls.get_all_users(role='seller', status='active')
    
    @classmethod
    def get_customers(cls):
        """Get all customers"""
        return cls.get_all_users(role='user', status='active')


# ============================================
# ADDITIONAL EXAMPLES FOR COMPLEX QUERIES
# ============================================

class UserAdvanced:
    """Advanced examples for complex Supabase queries"""
    
    @classmethod
    def search_users(cls, search_term):
        """Search users by name or email"""
        db = Database()
        
        # Use ilike for case-insensitive search
        response = db.client.table('users') \
            .select('*') \
            .or_(f'first_name.ilike.%{search_term}%,last_name.ilike.%{search_term}%,email.ilike.%{search_term}%') \
            .execute()
        
        return response.data
    
    @classmethod
    def get_users_with_orders(cls):
        """Get users with their order count"""
        db = Database()
        
        # Join with orders table
        response = db.client.table('users') \
            .select('*, orders(count)') \
            .execute()
        
        return response.data
    
    @classmethod
    def get_active_sellers_with_products(cls):
        """Get active sellers with their product count"""
        db = Database()
        
        response = db.client.table('users') \
            .select('id, username, email, products(count)') \
            .eq('role', 'seller') \
            .eq('status', 'active') \
            .execute()
        
        return response.data
    
    @classmethod
    def get_users_by_date_range(cls, start_date, end_date):
        """Get users created within a date range"""
        db = Database()
        
        response = db.client.table('users') \
            .select('*') \
            .gte('created_at', start_date) \
            .lte('created_at', end_date) \
            .order('created_at', desc=True) \
            .execute()
        
        return response.data


# ============================================
# USAGE EXAMPLES
# ============================================

"""
# Create a new user
user = User.create(
    username='john_doe',
    email='john@example.com',
    password='securepassword',
    first_name='John',
    last_name='Doe',
    phone='1234567890',
    role='user'
)

# Get user by email
user = User.get_by_email('john@example.com')

# Authenticate user
user = User.authenticate('john@example.com', 'securepassword')

# Update user
User.update(user['id'], first_name='Jane', last_name='Smith')

# Get all active sellers
sellers = User.get_all_users(role='seller', status='active')

# Search users
results = UserAdvanced.search_users('john')

# Delete user
User.delete(user['id'])
"""
