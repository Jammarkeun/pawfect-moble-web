"""
Supabase Database Utility
Direct Supabase connection for database operations
"""
from supabase import create_client, Client
from contextlib import contextmanager
import os
from typing import Optional, Dict, List, Any

class Database:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL', '')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY', '') or os.getenv('SUPABASE_KEY', '')
        self.client: Optional[Client] = None
        
        if self.supabase_url and self.supabase_key:
            self.client = create_client(self.supabase_url, self.supabase_key)
    
    @contextmanager
    def get_connection(self):
        """Get Supabase client (compatibility method)"""
        if not self.client:
            raise Exception("Supabase client not initialized")
        yield self.client
    
    @contextmanager
    def get_cursor(self, dictionary=True):
        """Compatibility method - Supabase doesn't use cursors"""
        if not self.client:
            raise Exception("Supabase client not initialized")
        yield self.client, self.client
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = True):
        """Basic SELECT query executor via Supabase."""
        if not self.client:
            return []
        import re
        table_match = re.search(r'FROM\s+(\w+)', query, re.IGNORECASE)
        if not table_match:
            return []
        table = table_match.group(1)
        try:
            q = self.client.table(table).select('*')
            limit_match = re.search(r'LIMIT\s+(\d+)', query, re.IGNORECASE)
            if limit_match:
                q = q.limit(int(limit_match.group(1)))
            response = q.execute()
            return response.data or []
        except Exception as e:
            return []
    
    def execute_many(self, query: str, params_list: List[tuple]):
        """Execute multiple queries - use Supabase batch operations instead"""
        raise NotImplementedError("Use Supabase batch operations instead")
    
    def get_one(self, table: str, filters: Dict[str, Any] = None):
        """Get single row from table"""
        if not self.client:
            return None
        
        query = self.client.table(table).select("*")
        
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        response = query.limit(1).execute()
        return response.data[0] if response.data else None
    
    def get_last_insert_id(self, cursor):
        """Not applicable for Supabase - returns are handled in insert response"""
        return None

# Global database instance
db = Database()
