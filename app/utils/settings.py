"""
System settings utility functions
Provides convenient access to system-wide configuration settings
"""

from app.services.database import Database
import logging


class Settings:
    """System settings manager"""
    
    @staticmethod
    def get(key, default=None):
        """
        Get a single setting value by key
        
        Args:
            key: Setting key to retrieve
            default: Default value if setting not found
            
        Returns:
            Setting value or default
        """
        db = Database()
        try:
            result = db.execute_query(
                "SELECT setting_value FROM system_settings WHERE setting_key = %s",
                (key,), fetch=True, fetchone=True
            )
            if result:
                return result['setting_value']
            return default
        except Exception as e:
            logging.error(f"Failed to get setting {key}: {e}")
            return default
    
    @staticmethod
    def get_all():
        """
        Get all settings as a dictionary
        
        Returns:
            Dictionary of all settings {key: value}
        """
        db = Database()
        try:
            results = db.execute_query(
                "SELECT setting_key, setting_value FROM system_settings",
                fetch=True
            )
            if results:
                return {row['setting_key']: row['setting_value'] for row in results}
            return {}
        except Exception as e:
            logging.error(f"Failed to get all settings: {e}")
            return {}
    
    @staticmethod
    def set(key, value):
        """
        Set a single setting value
        
        Args:
            key: Setting key to update
            value: New value for the setting
            
        Returns:
            True if successful, False otherwise
        """
        db = Database()
        try:
            # Check if setting exists
            check = db.execute_query(
                "SELECT id FROM system_settings WHERE setting_key = %s",
                (key,), fetch=True, fetchone=True
            )
            
            if check:
                # Update existing setting
                db.execute_query(
                    "UPDATE system_settings SET setting_value = %s WHERE setting_key = %s",
                    (str(value), key)
                )
            else:
                # Insert new setting
                db.execute_query(
                    "INSERT INTO system_settings (setting_key, setting_value) VALUES (%s, %s)",
                    (key, str(value))
                )
            return True
        except Exception as e:
            logging.error(f"Failed to set setting {key}: {e}")
            return False
    
    @staticmethod
    def set_multiple(settings_dict):
        """
        Set multiple settings at once
        
        Args:
            settings_dict: Dictionary of settings to update {key: value}
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for key, value in settings_dict.items():
                Settings.set(key, value)
            return True
        except Exception as e:
            logging.error(f"Failed to set multiple settings: {e}")
            return False
    
    @staticmethod
    def get_bool(key, default=False):
        """
        Get a boolean setting value
        
        Args:
            key: Setting key to retrieve
            default: Default value if setting not found
            
        Returns:
            Boolean value
        """
        value = Settings.get(key)
        if value is None:
            return default
        return str(value).lower() in ('1', 'true', 'yes', 'on')
    
    @staticmethod
    def get_int(key, default=0):
        """
        Get an integer setting value
        
        Args:
            key: Setting key to retrieve
            default: Default value if setting not found
            
        Returns:
            Integer value
        """
        value = Settings.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def get_float(key, default=0.0):
        """
        Get a float setting value
        
        Args:
            key: Setting key to retrieve
            default: Default value if setting not found
            
        Returns:
            Float value
        """
        value = Settings.get(key)
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
