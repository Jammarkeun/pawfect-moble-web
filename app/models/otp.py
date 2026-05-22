import random
import string
from datetime import datetime, timedelta
from app.services.database import Database

class OTP:
    """OTP model using Supabase"""
    
    TABLE_NAME = 'otp_codes'
    
    def __init__(self):
        self.db = Database()
        self.otp_length = 6
        self.otp_expiry_minutes = 10
    
    def generate_otp(self, email):
        """Generate and store a new OTP for the given email"""
        otp_code = ''.join(random.choices(string.digits, k=self.otp_length))
        
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(minutes=self.otp_expiry_minutes)
        
        try:
            # Delete old OTPs
            self.db.delete(self.TABLE_NAME, filters={'email': email})
            
            # Insert new OTP
            data = {
                'email': email,
                'otp_code': otp_code,
                'created_at': created_at.isoformat(),
                'expires_at': expires_at.isoformat(),
                'is_used': False
            }
            
            result = self.db.insert(self.TABLE_NAME, data)
            return otp_code if result else None
            
        except Exception as e:
            print(f"Error generating OTP: {str(e)}")
            return None
    
    def verify_otp(self, email, otp_code):
        """Verify if the provided OTP is valid for the given email"""
        try:
            response = self.db.client.table(self.TABLE_NAME).select('id').eq('email', email).eq('otp_code', otp_code).eq('is_used', False).gt('expires_at', datetime.utcnow().isoformat()).limit(1).execute()
            
            if response.data:
                otp_id = response.data[0]['id']
                self.db.update(self.TABLE_NAME, data={'is_used': True}, filters={'id': otp_id})
                return True
            return False
            
        except Exception as e:
            print(f"Error verifying OTP: {str(e)}")
            return False
