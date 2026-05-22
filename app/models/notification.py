from app.services.database import Database
from datetime import datetime
from flask import current_app
import json

class Notification:
    TABLE_NAME = 'notifications'
    
    @staticmethod
    def create(user_id, role, type_, title, message, related_id=None, data=None):
        db = Database()
        try:
            notification_data = {
                'user_id': user_id,
                'role': role,
                'type': type_,
                'title': title,
                'message': message,
                'related_id': related_id,
                'data': json.dumps(data) if isinstance(data, (dict, list)) else None,
                'is_read': False
            }
            
            db.insert(Notification.TABLE_NAME, notification_data)
            return True
        except Exception as e:
            current_app.logger.error(f"Error creating notification: {e}")
            return False

    @staticmethod
    def list_for_user(user_id, role, limit=20, offset=0):
        db = Database()
        try:
            response = db.client.table(Notification.TABLE_NAME).select('*').eq('user_id', user_id).eq('role', role).order('is_read').order('created_at', desc=True).limit(limit).range(offset, offset + limit - 1).execute()
            return response.data if response.data else []
        except:
            return []

    @staticmethod
    def unread_count(user_id, role):
        db = Database()
        try:
            response = db.client.table(Notification.TABLE_NAME).select('*', count='exact').eq('user_id', user_id).eq('role', role).eq('is_read', False).execute()
            return response.count if response.count else 0
        except:
            return 0

    @staticmethod
    def mark_read(notification_id, user_id):
        db = Database()
        try:
            db.update(Notification.TABLE_NAME, data={'is_read': True}, filters={'id': notification_id, 'user_id': user_id})
            return True
        except:
            return False

    @staticmethod
    def mark_all_read(user_id, role):
        db = Database()
        try:
            response = db.client.table(Notification.TABLE_NAME).update({'is_read': True}).eq('user_id', user_id).eq('role', role).execute()
            return True
        except:
            return False
