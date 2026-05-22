"""
Supabase Storage Integration for Pawfect Finds Web App

Handles uploading product images to Supabase Storage so they're accessible
to both the web app and the mobile app.
"""

import os
from typing import Optional, Tuple
from werkzeug.datastructures import FileStorage

try:
    from supabase import create_client, Client
except ImportError:
    raise ImportError("supabase-py not installed. Install with: pip install supabase")

class SupabaseStorageManager:
    """Manages image uploads to Supabase Storage."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_SERVICE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables")
        
        self.client: Optional[Client] = None
        self._connect()
    
    def _connect(self) -> None:
        """Connect to Supabase."""
        try:
            self.client = create_client(self.url, self.key)
        except Exception as e:
            print(f"ERROR: Failed to connect to Supabase: {e}")
            raise
    
    def upload_product_image(
        self, 
        file: FileStorage, 
        product_id: int, 
        filename: str
    ) -> Optional[str]:
        """
        Upload product image to Supabase Storage.
        
        Args:
            file: FileStorage object from Flask request
            product_id: Product ID for organizing in storage
            filename: Original filename (will be sanitized)
        
        Returns:
            Public URL of uploaded image, or None if failed
        """
        if not file or not file.filename:
            return None
        
        try:
            # Read file content
            file_content = file.read()
            if not file_content:
                return None
            
            # Create storage path
            bucket = "products"
            file_path = f"{product_id}/{filename}"
            
            # Upload to Supabase
            response = self.client.storage.from_bucket(bucket).upload(
                file_path,
                file_content,
                {"cacheControl": "3600", "upsert": "true"}
            )
            
            if response:
                # Return public URL
                public_url = f"{self.url}/storage/v1/object/public/{bucket}/{file_path}"
                print(f"[✓] Uploaded to Supabase: {public_url}")
                return public_url
            else:
                print(f"[!] Upload response was empty")
                return None
        
        except Exception as e:
            print(f"[ERROR] Failed to upload to Supabase: {e}")
            return None
    
    def upload_variation_image(
        self,
        file: FileStorage,
        product_id: int,
        variant_id: int,
        filename: str
    ) -> Optional[str]:
        """Upload product variant image to Supabase Storage."""
        if not file or not file.filename:
            return None
        
        try:
            file_content = file.read()
            if not file_content:
                return None
            
            bucket = "product-variants"
            file_path = f"{product_id}/{variant_id}/{filename}"
            
            response = self.client.storage.from_bucket(bucket).upload(
                file_path,
                file_content,
                {"cacheControl": "3600", "upsert": "true"}
            )
            
            if response:
                public_url = f"{self.url}/storage/v1/object/public/{bucket}/{file_path}"
                print(f"[✓] Uploaded variant image: {public_url}")
                return public_url
            return None
        
        except Exception as e:
            print(f"[ERROR] Failed to upload variant image: {e}")
            return None
    
    def delete_image(self, bucket: str, file_path: str) -> bool:
        """Delete image from Supabase Storage."""
        try:
            self.client.storage.from_bucket(bucket).remove([file_path])
            print(f"[✓] Deleted from Supabase: {bucket}/{file_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to delete from Supabase: {e}")
            return False


# Singleton instance
_storage_manager: Optional[SupabaseStorageManager] = None

def get_storage_manager() -> SupabaseStorageManager:
    """Get or create Supabase storage manager."""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = SupabaseStorageManager()
    return _storage_manager
