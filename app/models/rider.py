from app.services.database import Database
from datetime import datetime

class Rider:
    """Rider model using Supabase"""
    
    TABLE_NAME = 'rider_applications'
    
    @classmethod
    def create_application(cls, user_id, vehicle_type, vehicle_plate_number=None, 
                          vehicle_model=None, government_id_path=None, 
                          vehicle_registration_path=None, profile_photo_path=None, 
                          clearance_path=None):
        """Create a new rider application"""
        db = Database()
        
        data = {
            'user_id': user_id,
            'vehicle_type': vehicle_type,
            'vehicle_plate_number': vehicle_plate_number,
            'vehicle_model': vehicle_model,
            'government_id_path': government_id_path,
            'vehicle_registration_path': vehicle_registration_path,
            'profile_photo_path': profile_photo_path,
            'clearance_path': clearance_path,
            'status': 'pending'
        }

        data = {k: v for k, v in data.items() if v is not None}

        while True:
            try:
                result = db.insert(cls.TABLE_NAME, data)
                return result['id'] if result else None
            except Exception as e:
                error_message = str(e)
                if 'Could not find the' in error_message and "column of 'rider_applications'" in error_message:
                    import re
                    missing_columns = re.findall(r"Could not find the '([^']+)' column of 'rider_applications'", error_message)
                    if not missing_columns:
                        raise
                    for col in missing_columns:
                        data.pop(col, None)
                    if not data:
                        raise
                    continue
                raise
    
    @classmethod
    def get_application_by_user(cls, user_id):
        """Get rider application by user ID"""
        db = Database()
        try:
            response = db.client.table(cls.TABLE_NAME).select('*').eq('user_id', user_id).order('created_at', desc=True).limit(1).execute()
            return response.data[0] if response.data else None
        except:
            return None
    
    @classmethod
    def get_application_by_id(cls, application_id):
        """Get rider application by ID"""
        db = Database()
        return db.select_one(cls.TABLE_NAME, filters={'id': application_id})
    
    @classmethod
    def update_application_status(cls, application_id, status, admin_notes=None):
        """Update application status"""
        db = Database()
        
        data = {'status': status}
        if admin_notes:
            data['admin_notes'] = admin_notes
        
        db.update(cls.TABLE_NAME, data=data, filters={'id': application_id})
        return True
    
    @classmethod
    def complete_training(cls, user_id):
        """Mark training as completed for a rider"""
        db = Database()
        
        data = {
            'user_id': user_id,
            'status': 'completed'
        }
        
        try:
            db.insert('rider_training', data)
        except:
            db.update('rider_training', data={'status': 'completed'}, filters={'user_id': user_id})
        
        return True
    
    @classmethod
    def get_training_status(cls, user_id):
        """Get training status for a rider"""
        db = Database()
        return db.select_one('rider_training', filters={'user_id': user_id})
    
    @classmethod
    def activate_rider_account(cls, user_id):
        """Activate rider account after approval and training"""
        from app.models.user import User
        User.update_role(user_id, 'rider')
        
        db = Database()
        data = {
            'rider_id': user_id,
            'is_online': False,
            'is_available': False
        }
        
        try:
            db.insert('rider_availability', data)
        except:
            pass
        
        return True
    
    @classmethod
    def get_all_applications(cls, status=None, limit=None, offset=0):
        """Get all rider applications"""
        db = Database()
        
        try:
            query = db.client.table(cls.TABLE_NAME).select('*')
            
            if status:
                query = query.eq('status', status)
            
            query = query.order('created_at', desc=True)
            
            if limit:
                query = query.limit(limit).range(offset, offset + limit - 1)
            
            response = query.execute()
            return response.data if response.data else []
        except:
            return []
    
    @classmethod
    def get_applications_count(cls, status=None):
        """Get count of applications"""
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
    def get_rider_profile(cls, user_id):
        """Get complete rider profile"""
        from app.models.user import User
        return User.get_by_id(user_id)
