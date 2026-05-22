"""
Audit Logger Utility
Tracks all admin actions for security and accountability
"""

from app.services.database import Database
from flask import request, session
from datetime import datetime
import json


class AuditLogger:
    """Utility class for logging admin actions to system_logs table"""
    
    @staticmethod
    def log_action(action, details=None, user_id=None, category='admin'):
        """
        Log an admin action to the system_logs table
        
        Args:
            action (str): The action performed (e.g., 'APPROVE_SELLER_REQUEST')
            details (str or dict): Additional details about the action
            user_id (int): User ID performing the action (defaults to session user)
            category (str): Category of the action (admin, seller, user, etc.)
        
        Returns:
            bool: True if logging successful, False otherwise
        """
        try:
            db = Database()
            
            # Get user_id from session if not provided
            if user_id is None:
                user_id = session.get('user_id')
            
            # Convert dict details to JSON string
            if isinstance(details, dict):
                details = json.dumps(details)
            
            # Get request metadata
            ip_address = request.remote_addr if request else None
            user_agent = request.headers.get('User-Agent') if request else None
            
            # Insert log into database
            query = """
                INSERT INTO system_logs (user_id, action, details, ip_address, user_agent, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            db.execute_query(
                query,
                (user_id, f"{category.upper()}_{action}", details, ip_address, user_agent, datetime.now()),
                fetch=False
            )
            
            return True
            
        except Exception as e:
            # Don't fail the main operation if logging fails
            print(f"Audit logging error: {str(e)}")
            return False
    
    @staticmethod
    def log_seller_approval(request_id, user_id, applicant_name):
        """Log seller request approval"""
        return AuditLogger.log_action(
            'APPROVE_SELLER_REQUEST',
            f"Approved seller request #{request_id} for {applicant_name}",
            user_id
        )
    
    @staticmethod
    def log_seller_rejection(request_id, user_id, applicant_name, reason):
        """Log seller request rejection"""
        return AuditLogger.log_action(
            'REJECT_SELLER_REQUEST',
            {
                'request_id': request_id,
                'applicant': applicant_name,
                'reason': reason
            },
            user_id
        )
    
    @staticmethod
    def log_rider_approval(application_id, user_id, applicant_name):
        """Log rider application approval"""
        return AuditLogger.log_action(
            'APPROVE_RIDER_REQUEST',
            f"Approved rider application #{application_id} for {applicant_name}",
            user_id
        )
    
    @staticmethod
    def log_rider_rejection(application_id, user_id, applicant_name, reason):
        """Log rider application rejection"""
        return AuditLogger.log_action(
            'REJECT_RIDER_REQUEST',
            {
                'application_id': application_id,
                'applicant': applicant_name,
                'reason': reason
            },
            user_id
        )
    
    @staticmethod
    def log_user_status_change(target_user_id, username, old_status, new_status, admin_id):
        """Log user status change"""
        return AuditLogger.log_action(
            'UPDATE_USER_STATUS',
            {
                'user_id': target_user_id,
                'username': username,
                'old_status': old_status,
                'new_status': new_status
            },
            admin_id
        )
    
    @staticmethod
    def log_user_role_change(target_user_id, username, old_role, new_role, admin_id):
        """Log user role change"""
        return AuditLogger.log_action(
            'UPDATE_USER_ROLE',
            {
                'user_id': target_user_id,
                'username': username,
                'old_role': old_role,
                'new_role': new_role
            },
            admin_id
        )
    
    @staticmethod
    def log_order_status_change(order_id, order_number, old_status, new_status, admin_id):
        """Log order status change"""
        return AuditLogger.log_action(
            'UPDATE_ORDER_STATUS',
            {
                'order_id': order_id,
                'order_number': order_number,
                'old_status': old_status,
                'new_status': new_status
            },
            admin_id
        )
    
    @staticmethod
    def log_product_status_change(product_id, product_name, old_status, new_status, admin_id):
        """Log product status change"""
        return AuditLogger.log_action(
            'UPDATE_PRODUCT_STATUS',
            {
                'product_id': product_id,
                'product_name': product_name,
                'old_status': old_status,
                'new_status': new_status
            },
            admin_id
        )
    
    @staticmethod
    def log_bulk_action(action_type, count, details, admin_id):
        """Log bulk actions"""
        return AuditLogger.log_action(
            f'BULK_{action_type}',
            {
                'count': count,
                'details': details
            },
            admin_id
        )
    
    @staticmethod
    def log_login(user_id, username, success=True):
        """Log user login attempt"""
        return AuditLogger.log_action(
            'LOGIN_SUCCESS' if success else 'LOGIN_FAILED',
            f"User {username} login {'successful' if success else 'failed'}",
            user_id,
            category='auth'
        )
    
    @staticmethod
    def log_settings_change(setting_name, old_value, new_value, admin_id):
        """Log system settings change"""
        return AuditLogger.log_action(
            'UPDATE_SETTINGS',
            {
                'setting': setting_name,
                'old_value': old_value,
                'new_value': new_value
            },
            admin_id
        )
    
    @staticmethod
    def get_logs(limit=100, offset=0, action_filter=None, user_filter=None, date_from=None, date_to=None):
        """
        Retrieve audit logs with filtering and pagination
        
        Args:
            limit (int): Maximum number of logs to return
            offset (int): Offset for pagination
            action_filter (str): Filter by action type
            user_filter (int): Filter by user ID
            date_from (datetime): Filter logs from this date
            date_to (datetime): Filter logs until this date
        
        Returns:
            list: List of log entries
        """
        try:
            db = Database()
            
            query = """
                SELECT sl.*, u.username, u.first_name, u.last_name, u.email
                FROM system_logs sl
                LEFT JOIN users u ON sl.user_id = u.id
                WHERE 1=1
            """
            params = []
            
            if action_filter:
                query += " AND sl.action LIKE %s"
                params.append(f"%{action_filter}%")
            
            if user_filter:
                query += " AND sl.user_id = %s"
                params.append(user_filter)
            
            if date_from:
                query += " AND sl.created_at >= %s"
                params.append(date_from)
            
            if date_to:
                query += " AND sl.created_at <= %s"
                params.append(date_to)
            
            query += " ORDER BY sl.created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            logs = db.execute_query(query, tuple(params), fetch=True)
            return logs if logs else []
            
        except Exception as e:
            print(f"Error retrieving logs: {str(e)}")
            return []
    
    @staticmethod
    def get_log_count(action_filter=None, user_filter=None, date_from=None, date_to=None):
        """Get total count of logs matching filters"""
        try:
            db = Database()
            
            query = "SELECT COUNT(*) as count FROM system_logs WHERE 1=1"
            params = []
            
            if action_filter:
                query += " AND action LIKE %s"
                params.append(f"%{action_filter}%")
            
            if user_filter:
                query += " AND user_id = %s"
                params.append(user_filter)
            
            if date_from:
                query += " AND created_at >= %s"
                params.append(date_from)
            
            if date_to:
                query += " AND created_at <= %s"
                params.append(date_to)
            
            result = db.execute_query(query, tuple(params) if params else None, fetch=True, fetchone=True)
            return result['count'] if result else 0
            
        except Exception as e:
            print(f"Error counting logs: {str(e)}")
            return 0
