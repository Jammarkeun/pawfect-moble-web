from app.services.database import Database
from datetime import datetime, timedelta

class RiderAvailability:
    TABLE_NAME = 'rider_availability'
    
    @staticmethod
    def get_available_riders(max_distance_km=20, min_online_minutes_ago=10):
        """Get list of all online riders"""
        db = Database()
        time_threshold = (datetime.utcnow() - timedelta(minutes=min_online_minutes_ago)).isoformat()
        
        try:
            response = db.client.table(RiderAvailability.TABLE_NAME).select('*, profiles!inner(*)').eq('is_online', True).gte('last_online', time_threshold).execute()
            return response.data if response.data else []
        except:
            return []
    
    @staticmethod
    def set_availability(rider_id, is_available=True, lat=None, lng=None):
        """Update rider's availability"""
        db = Database()
        
        data = {
            'rider_id': rider_id,
            'is_online': True,
            'is_available': True,
            'last_online': datetime.utcnow().isoformat()
        }
        
        if lat is not None:
            data['current_lat'] = lat
        if lng is not None:
            data['current_lng'] = lng
        
        try:
            existing = db.select_one(RiderAvailability.TABLE_NAME, filters={'rider_id': rider_id})
            if existing:
                db.update(RiderAvailability.TABLE_NAME, data=data, filters={'rider_id': rider_id})
            else:
                db.insert(RiderAvailability.TABLE_NAME, data)
            return True
        except:
            return False
    
    @staticmethod
    def update_location(rider_id, lat, lng):
        """Update rider's current location"""
        db = Database()
        
        data = {
            'current_lat': lat,
            'current_lng': lng,
            'last_online': datetime.utcnow().isoformat()
        }
        
        try:
            existing = db.select_one(RiderAvailability.TABLE_NAME, filters={'rider_id': rider_id})
            if existing:
                db.update(RiderAvailability.TABLE_NAME, data=data, filters={'rider_id': rider_id})
            else:
                data['rider_id'] = rider_id
                db.insert(RiderAvailability.TABLE_NAME, data)
            return True
        except:
            return False
        
    @staticmethod
    def get_by_rider_id(rider_id):
        """Get rider availability by rider ID"""
        db = Database()
        return db.select_one(RiderAvailability.TABLE_NAME, filters={'rider_id': rider_id})
