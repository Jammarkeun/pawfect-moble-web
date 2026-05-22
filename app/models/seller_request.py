from app.services.database import Database
from datetime import datetime

class SellerRequest:
    """Seller request model using Supabase"""
    
    TABLE_NAME = 'seller_requests'
    
    def __init__(self):
        self.db = Database()
    
    @classmethod
    def create(cls, user_id, business_name, business_description, business_address, business_phone, tax_id=None, business_permit=None, applicant_name=None):
        """Create a new seller request"""
        db = Database()
        
        existing = cls.get_by_user_id(user_id)
        if existing and existing.get('status') == 'pending':
            return None
        
        data = {
            'user_id': user_id,
            'applicant_name': applicant_name,
            'business_name': business_name,
            'business_description': business_description,
            'business_address': business_address,
            'business_phone': business_phone,
            'tax_id': tax_id,
            'business_permit': business_permit,
            'status': 'pending'
        }

        # Remove unset optional values up front.
        data = {k: v for k, v in data.items() if v is not None}

        while True:
            try:
                return db.insert(cls.TABLE_NAME, data)
            except Exception as e:
                error_message = str(e)
                if 'Could not find the' in error_message and "column of 'seller_requests'" in error_message:
                    import re
                    missing_columns = re.findall(r"Could not find the '([^']+)' column of 'seller_requests'", error_message)
                    if not missing_columns:
                        raise
                    for col in missing_columns:
                        data.pop(col, None)
                    if not data:
                        raise
                    continue
                raise
    
    @classmethod
    def get_by_id(cls, request_id):
        """Get seller request by ID"""
        db = Database()
        return db.select_one(cls.TABLE_NAME, filters={'id': request_id})
    
    @classmethod
    def get_by_user_id(cls, user_id):
        """Get seller request by user ID"""
        db = Database()
        try:
            response = db.client.table(cls.TABLE_NAME).select('*').eq('user_id', user_id).order('requested_at', desc=True).limit(1).execute()
            return response.data[0] if response.data else None
        except:
            return None
    
    @classmethod
    def get_all_requests(cls, status=None, limit=None, offset=0):
        """Get all seller requests"""
        db = Database()
        
        try:
            query = db.client.table(cls.TABLE_NAME).select('*')
            
            if status:
                query = query.eq('status', status)
            
            query = query.order('requested_at', desc=True)
            
            if limit:
                query = query.limit(limit).range(offset, offset + limit - 1)
            
            response = query.execute()
            return response.data if response.data else []
        except:
            return []
    
    @classmethod
    def get_pending_requests(cls):
        """Get all pending seller requests"""
        return cls.get_all_requests(status='pending')
    
    @classmethod
    def approve_request(cls, request_id, admin_notes=None):
        """Approve a seller request"""
        db = Database()
        
        request = cls.get_by_id(request_id)
        if not request or request.get('status') != 'pending':
            return False
        
        db.update(cls.TABLE_NAME, 
                 data={'status': 'approved', 'admin_notes': admin_notes},
                 filters={'id': request_id})
        
        from app.models.user import User
        User.update_role(request['user_id'], 'seller')
        
        return True
    
    @classmethod
    def reject_request(cls, request_id, admin_notes=None):
        """Reject a seller request"""
        db = Database()
        
        db.update(cls.TABLE_NAME,
                 data={'status': 'rejected', 'admin_notes': admin_notes},
                 filters={'id': request_id})
        return True
    
    @classmethod
    def get_requests_count(cls, status=None):
        """Get count of seller requests"""
        db = Database()
        
        try:
            query = db.client.table(cls.TABLE_NAME).select('*', count='exact')
            
            if status:
                query = query.eq('status', status)
            
            response = query.execute()
            return response.count if response.count else 0
        except:
            return 0
    
    @classmethod
    def delete(cls, request_id):
        """Delete a seller request"""
        db = Database()
        db.delete(cls.TABLE_NAME, filters={'id': request_id})
        return True
