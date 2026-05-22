"""
OAuth authentication utilities for Google and Facebook login.
Provides helper functions for OAuth flows and user data extraction.
"""
import os
import requests
import secrets
from typing import Dict, Optional, Any
from urllib.parse import urlencode
from flask import session, url_for, request
from app.utils.error_handler import get_logger

logger = get_logger(__name__)


class OAuthProvider:
    """Base OAuth provider class"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    def get_authorization_url(self) -> str:
        """Get authorization URL for OAuth flow"""
        raise NotImplementedError
    
    def get_access_token(self, code: str) -> Optional[str]:
        """Exchange authorization code for access token"""
        raise NotImplementedError
    
    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from provider"""
        raise NotImplementedError


class GoogleOAuth(OAuthProvider):
    """Google OAuth provider"""
    
    AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    def get_authorization_url(self) -> str:
        """Get Google OAuth authorization URL"""
        # Generate state token for CSRF protection
        state = secrets.token_urlsafe(32)
        session['oauth_state'] = state
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'openid email profile',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        return f"{self.AUTHORIZATION_URL}?{urlencode(params)}"
    
    def get_access_token(self, code: str) -> Optional[str]:
        """Exchange authorization code for access token"""
        try:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri
            }
            
            response = requests.post(self.TOKEN_URL, data=data, timeout=10)
            response.raise_for_status()
            
            token_data = response.json()
            return token_data.get('access_token')
            
        except Exception as e:
            logger.error(f"Error getting Google access token: {str(e)}", exc_info=True)
            return None
    
    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from Google"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(self.USERINFO_URL, headers=headers, timeout=10)
            response.raise_for_status()
            
            user_data = response.json()
            
            # Normalize user data
            return {
                'provider': 'google',
                'provider_id': user_data.get('id'),
                'email': user_data.get('email'),
                'first_name': user_data.get('given_name', ''),
                'last_name': user_data.get('family_name', ''),
                'profile_picture': user_data.get('picture'),
                'email_verified': user_data.get('verified_email', False)
            }
            
        except Exception as e:
            logger.error(f"Error getting Google user info: {str(e)}", exc_info=True)
            return None


class FacebookOAuth(OAuthProvider):
    """Facebook OAuth provider"""
    
    AUTHORIZATION_URL = "https://www.facebook.com/v18.0/dialog/oauth"
    TOKEN_URL = "https://graph.facebook.com/v18.0/oauth/access_token"
    USERINFO_URL = "https://graph.facebook.com/v18.0/me"
    
    def get_authorization_url(self) -> str:
        """Get Facebook OAuth authorization URL"""
        # Generate state token for CSRF protection
        state = secrets.token_urlsafe(32)
        session['oauth_state'] = state
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': state,
            'scope': 'email,public_profile'
        }
        
        return f"{self.AUTHORIZATION_URL}?{urlencode(params)}"
    
    def get_access_token(self, code: str) -> Optional[str]:
        """Exchange authorization code for access token"""
        try:
            params = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'redirect_uri': self.redirect_uri
            }
            
            response = requests.get(self.TOKEN_URL, params=params, timeout=10)
            response.raise_for_status()
            
            token_data = response.json()
            return token_data.get('access_token')
            
        except Exception as e:
            logger.error(f"Error getting Facebook access token: {str(e)}", exc_info=True)
            return None
    
    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from Facebook"""
        try:
            params = {
                'access_token': access_token,
                'fields': 'id,email,first_name,last_name,picture.type(large)'
            }
            
            response = requests.get(self.USERINFO_URL, params=params, timeout=10)
            response.raise_for_status()
            
            user_data = response.json()
            
            # Normalize user data
            picture_url = None
            if 'picture' in user_data and 'data' in user_data['picture']:
                picture_url = user_data['picture']['data'].get('url')
            
            return {
                'provider': 'facebook',
                'provider_id': user_data.get('id'),
                'email': user_data.get('email'),
                'first_name': user_data.get('first_name', ''),
                'last_name': user_data.get('last_name', ''),
                'profile_picture': picture_url,
                'email_verified': user_data.get('email') is not None
            }
            
        except Exception as e:
            logger.error(f"Error getting Facebook user info: {str(e)}", exc_info=True)
            return None


def get_oauth_provider(provider_name: str) -> Optional[OAuthProvider]:
    """
    Get OAuth provider instance by name.
    
    Args:
        provider_name: Either 'google' or 'facebook'
    
    Returns:
        OAuth provider instance or None if not configured
    """
    provider_name = provider_name.lower()
    
    if provider_name == 'google':
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            logger.warning("Google OAuth not configured")
            return None
        
        redirect_uri = url_for('auth.oauth_callback', provider='google', _external=True)
        return GoogleOAuth(client_id, client_secret, redirect_uri)
    
    elif provider_name == 'facebook':
        client_id = os.getenv('FACEBOOK_APP_ID')
        client_secret = os.getenv('FACEBOOK_APP_SECRET')
        
        if not client_id or not client_secret:
            logger.warning("Facebook OAuth not configured")
            return None
        
        redirect_uri = url_for('auth.oauth_callback', provider='facebook', _external=True)
        return FacebookOAuth(client_id, client_secret, redirect_uri)
    
    return None


def verify_oauth_state(state: str) -> bool:
    """Verify OAuth state token for CSRF protection"""
    stored_state = session.pop('oauth_state', None)
    return stored_state and secrets.compare_digest(stored_state, state)
