# -*- coding: utf-8 -*-
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import logging
import re
from typing import Optional, List, Dict, Any

# Load environment variables
load_dotenv()

class Database:
    """Database service class for Supabase operations"""
    
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Only initialize once
        if Database._client is not None:
            self.client = Database._client
            return
            
        # Load directly from environment variables
        self.supabase_url = os.getenv('SUPABASE_URL', '')
        # Use SERVICE_ROLE key to bypass RLS (Row Level Security)
        self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY', '')
        self.client: Optional[Client] = None
        
        if self.supabase_url and self.supabase_key:
            try:
                self.client = create_client(self.supabase_url, self.supabase_key)
                Database._client = self.client
                logging.info(f"Supabase client initialized successfully for URL: {self.supabase_url[:40]}...")
            except Exception as e:
                logging.error(f"Failed to initialize Supabase client: {e}")
        else:
            logging.error(f"Supabase env vars missing — URL set: {bool(self.supabase_url)}, KEY set: {bool(self.supabase_key)}")

    def init_app(self, app):
        """Initialize with Flask app"""
        url = app.config.get('SUPABASE_URL')
        key = app.config.get('SUPABASE_SERVICE_KEY')
        if url and key and not self.client:
            try:
                self.client = create_client(url, key)
                logging.info(f"Supabase re-initialized via init_app")
            except Exception as e:
                logging.error(f"Failed to initialize Supabase in app context: {e}")
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = False, fetchone: bool = False, commit: bool = True):
        """
        Translates raw SQL to Supabase API calls.
        Supports: SELECT (simple, WHERE, ORDER BY, LIMIT, OFFSET, COUNT),
                  INSERT, UPDATE, DELETE.
        For complex queries (JOINs, GROUP BY), logs a warning and returns empty.
        """
        if not self.client:
            raise Exception("Supabase client not initialized. Check your SUPABASE_URL and SUPABASE_KEY.")
        
        query = query.strip()
        query_upper = query.upper()
        
        try:
            if query_upper.startswith('SELECT'):
                results = self._execute_select(query)
                if fetchone:
                    return results[0] if results else {}
                return results
            elif query_upper.startswith('INSERT'):
                return self._execute_insert(query)
            elif query_upper.startswith('UPDATE'):
                return self._execute_update(query)
            elif query_upper.startswith('DELETE'):
                return self._execute_delete(query)
            else:
                logging.warning(f"Unsupported SQL statement type: {query[:50]}...")
                if fetch:
                    return {} if fetchone else []
                return None
        except Exception as e:
            logging.error(f"execute_query failed for: {query[:80]}... Error: {e}")
            if fetch:
                return {} if fetchone else []
            return None

    def _parse_select(self, query: str) -> dict:
        """Parse a simple SELECT SQL into components."""
        result = {
            'columns': '*',
            'table': None,
            'where': {},
            'order_by': None,
            'order_dir': 'asc',
            'limit': None,
            'offset': None,
            'is_count': False,
            'has_join': False,
            'has_group_by': False,
        }
        
        # Check for JOIN or GROUP BY (complex queries fallback)
        if re.search(r'\bJOIN\b', query, re.IGNORECASE):
            result['has_join'] = True
        if re.search(r'\bGROUP\s+BY\b', query, re.IGNORECASE):
            result['has_group_by'] = True
        
        # Check if it's a COUNT query
        count_match = re.search(r'SELECT\s+COUNT\s*\(\s*(?:\*|1)\s*\)', query, re.IGNORECASE)
        if count_match:
            result['is_count'] = True
        
        # Extract columns (everything between SELECT and FROM)
        columns_match = re.search(r'SELECT\s+(.*?)\s+FROM', query, re.IGNORECASE)
        if columns_match:
            cols = columns_match.group(1).strip()
            if not result['is_count']:
                result['columns'] = cols
        
        # Extract table name (first table after FROM, before WHERE/JOIN/ORDER/LIMIT)
        table_match = re.search(r'FROM\s+(\w+)', query, re.IGNORECASE)
        if table_match:
            result['table'] = table_match.group(1)
        
        # Extract WHERE conditions
        where_match = re.search(r'WHERE\s+(.+?)(?:\s+ORDER\s+BY|\s+LIMIT|\s+OFFSET|\s*$)', query, re.IGNORECASE)
        if where_match:
            where_clause = where_match.group(1).strip()
            # Parse simple conditions (col = 'val' or col = val)
            conditions = re.findall(r"(\w+)\s*=\s*'([^']*)'", where_clause)
            conditions += re.findall(r"(\w+)\s*=\s*(\d+)", where_clause)
            conditions += re.findall(r"(\w+)\s*!=\s*'([^']*)'", where_clause)
            conditions += re.findall(r"(\w+)\s*!=\s*(\d+)", where_clause)
            for col, val in conditions:
                if val.isdigit():
                    val = int(val)
                result['where'][col] = val
        
        # Extract ORDER BY
        order_match = re.search(r'ORDER\s+BY\s+(\w+(?:\.\w+)?)\s*(ASC|DESC)?', query, re.IGNORECASE)
        if order_match:
            result['order_by'] = order_match.group(1)
            if order_match.group(2):
                result['order_dir'] = order_match.group(2).lower()
        
        # Extract LIMIT
        limit_match = re.search(r'LIMIT\s+(\d+)', query, re.IGNORECASE)
        if limit_match:
            result['limit'] = int(limit_match.group(1))
        
        # Extract OFFSET
        offset_match = re.search(r'OFFSET\s+(\d+)', query, re.IGNORECASE)
        if offset_match:
            result['offset'] = int(offset_match.group(1))
        
        return result

    def _execute_select(self, query: str) -> List[Dict]:
        """Execute a SELECT query via Supabase API."""
        parsed = self._parse_select(query)
        
        if not parsed['table']:
            logging.error(f"Cannot parse table from SELECT: {query[:60]}...")
            return []
        
        # For complex queries with JOINs or GROUP BY, try RPC or return empty
        if parsed['has_join'] or parsed['has_group_by']:
            logging.warning(f"Complex SELECT (JOIN/GROUP BY) not supported in execute_query, returning empty: {query[:80]}...")
            return []
        
        table = parsed['table']
        
        try:
            if parsed['is_count']:
                # Use the model methods or a simple count
                query_builder = self.client.table(table).select('*', count='exact')
                for col, val in parsed['where'].items():
                    query_builder = query_builder.eq(col, val)
                response = query_builder.execute()
                return [{'count': len(response.data)}]
            
            query_builder = self.client.table(table).select(parsed['columns'])
            
            # Apply WHERE filters
            # Handle != conditions separately
            for col, val in parsed['where'].items():
                if isinstance(val, str) and val.startswith('!'):
                    query_builder = query_builder.neq(col, val[1:])
                else:
                    query_builder = query_builder.eq(col, val)
            
            # Apply ORDER BY
            if parsed['order_by']:
                col = parsed['order_by']
                if '.' in col:
                    col = col.split('.')[-1]
                if parsed['order_dir'] == 'desc':
                    query_builder = query_builder.order(col, desc=True)
                else:
                    query_builder = query_builder.order(col)
            
            # Apply LIMIT
            if parsed['limit']:
                query_builder = query_builder.limit(parsed['limit'])
            
            # Apply OFFSET
            if parsed['offset']:
                query_builder = query_builder.offset(parsed['offset'])
            
            response = query_builder.execute()
            return [Database._parse_response(row) for row in response.data]
        except Exception as e:
            logging.error(f"Supabase query failed for {table}: {e}")
            return []

    def _execute_insert(self, query: str) -> Optional[Dict]:
        """Execute an INSERT query via Supabase API."""
        table_match = re.search(r'INSERT\s+INTO\s+(\w+)', query, re.IGNORECASE)
        if not table_match:
            logging.error(f"Cannot parse table from INSERT: {query[:60]}...")
            return None
        
        table = table_match.group(1)
        
        # Extract columns and values
        cols_match = re.search(r'\((.*?)\)\s*VALUES\s*\((.*?)\)', query, re.IGNORECASE)
        if not cols_match:
            logging.error(f"Cannot parse columns/values from INSERT: {query[:60]}...")
            return None
        
        columns = [c.strip() for c in cols_match.group(1).split(',')]
        values_str = cols_match.group(2).strip()
        
        # Parse values (handles strings, numbers)
        values = []
        for val in re.findall(r"'([^']*)'|(\d+(?:\.\d+)?)", values_str):
            if val[0] != '':
                values.append(val[0])
            else:
                values.append(float(val[1]) if '.' in val[1] else int(val[1]))
        
        data = dict(zip(columns, values))
        
        try:
            response = self.client.table(table).insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logging.error(f"Supabase insert failed for {table}: {e}")
            return None

    def _execute_update(self, query: str) -> Optional[List[Dict]]:
        """Execute an UPDATE query via Supabase API."""
        table_match = re.search(r'UPDATE\s+(\w+)', query, re.IGNORECASE)
        if not table_match:
            logging.error(f"Cannot parse table from UPDATE: {query[:60]}...")
            return None
        
        table = table_match.group(1)
        
        # Extract SET clause
        set_match = re.search(r'SET\s+(.+?)(?:\s+WHERE|\s*$)', query, re.IGNORECASE)
        if not set_match:
            logging.error(f"Cannot parse SET from UPDATE: {query[:60]}...")
            return None
        
        # Parse set pairs
        set_pairs = re.findall(r"(\w+)\s*=\s*'([^']*)'", set_match.group(1))
        set_pairs += re.findall(r"(\w+)\s*=\s*([\d.]+)", set_match.group(1))
        
        data = {}
        for col, val in set_pairs:
            if val.replace('.', '').isdigit():
                data[col] = float(val) if '.' in val else int(val)
            else:
                data[col] = val
        
        # Extract WHERE conditions
        where = {}
        where_match = re.search(r'WHERE\s+(.+?)$', query, re.IGNORECASE)
        if where_match:
            conditions = re.findall(r"(\w+)\s*=\s*'([^']*)'", where_match.group(1))
            conditions += re.findall(r"(\w+)\s*=\s*(\d+)", where_match.group(1))
            for col, val in conditions:
                where[col] = int(val) if val.isdigit() else val
        
        try:
            query_builder = self.client.table(table).update(data)
            for col, val in where.items():
                query_builder = query_builder.eq(col, val)
            response = query_builder.execute()
            return response.data
        except Exception as e:
            logging.error(f"Supabase update failed for {table}: {e}")
            return None

    def _execute_delete(self, query: str) -> Optional[List[Dict]]:
        """Execute a DELETE query via Supabase API."""
        table_match = re.search(r'DELETE\s+FROM\s+(\w+)', query, re.IGNORECASE)
        if not table_match:
            logging.error(f"Cannot parse table from DELETE: {query[:60]}...")
            return None
        
        table = table_match.group(1)
        
        # Extract WHERE conditions
        where = {}
        where_match = re.search(r'WHERE\s+(.+?)$', query, re.IGNORECASE)
        if where_match:
            conditions = re.findall(r"(\w+)\s*=\s*'([^']*)'", where_match.group(1))
            conditions += re.findall(r"(\w+)\s*=\s*(\d+)", where_match.group(1))
            for col, val in conditions:
                where[col] = int(val) if val.isdigit() else val
        
        try:
            query_builder = self.client.table(table).delete()
            for col, val in where.items():
                query_builder = query_builder.eq(col, val)
            response = query_builder.execute()
            return response.data
        except Exception as e:
            logging.error(f"Supabase delete failed for {table}: {e}")
            return None
    
    @staticmethod
    def _parse_response(obj):
        """Recursively convert ISO datetime strings in Supabase responses to Python datetime objects."""
        from datetime import datetime
        if isinstance(obj, dict):
            result = {}
            for key, val in obj.items():
                if isinstance(val, str):
                    if val.endswith(('Z', '+00:00')) and 'T' in val and len(val) >= 20:
                        try:
                            result[key] = datetime.fromisoformat(val.replace('Z', '+00:00'))
                        except:
                            result[key] = val
                    else:
                        result[key] = val
                elif isinstance(val, list):
                    result[key] = [Database._parse_response(item) if isinstance(item, dict) else item for item in val]
                elif isinstance(val, dict):
                    result[key] = Database._parse_response(val)
                else:
                    result[key] = val
            return result
        return obj

    # Supabase-native methods
    def select(self, table: str, columns: str = "*", filters: Dict[str, Any] = None) -> List[Dict]:
        """Select data from a table"""
        if not self.client:
            raise Exception("Supabase client not initialized")
        
        query = self.client.table(table).select(columns)
        
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        response = query.execute()
        return [Database._parse_response(row) for row in response.data]
    
    def select_one(self, table: str, columns: str = "*", filters: Dict[str, Any] = None) -> Optional[Dict]:
        """Select single row from a table"""
        results = self.select(table, columns, filters)
        return results[0] if results else None
    
    def insert(self, table: str, data: Dict[str, Any]) -> Dict:
        """Insert data into a table"""
        if not self.client:
            raise Exception("Supabase client not initialized")
        
        response = self.client.table(table).insert(data).execute()
        return response.data[0] if response.data else None
    
    def update(self, table: str, data: Dict[str, Any], filters: Dict[str, Any]) -> List[Dict]:
        """Update data in a table"""
        if not self.client:
            raise Exception("Supabase client not initialized")
        
        query = self.client.table(table).update(data)
        
        for key, value in filters.items():
            query = query.eq(key, value)
        
        response = query.execute()
        return response.data
    
    def delete(self, table: str, filters: Dict[str, Any]) -> List[Dict]:
        """Delete data from a table"""
        if not self.client:
            raise Exception("Supabase client not initialized")
        
        query = self.client.table(table).delete()
        
        for key, value in filters.items():
            query = query.eq(key, value)
        
        response = query.execute()
        return response.data
    
    def rpc(self, function_name: str, params: Dict[str, Any] = None) -> Any:
        """Call a Supabase RPC function"""
        if not self.client:
            raise Exception("Supabase client not initialized")
        
        response = self.client.rpc(function_name, params or {}).execute()
        return response.data
    
    # Legacy compatibility methods
    def connect(self):
        """Legacy method - Supabase uses persistent connection"""
        return self.client
    
    def get_connection(self):
        """Legacy method - returns self for context manager compatibility"""
        return self
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        pass
    
    def disconnect(self):
        """Legacy method - Supabase manages connections automatically"""
        pass
    
    def create_database(self):
        """Not applicable for Supabase - database is managed via dashboard"""
        logging.info("Supabase database is managed via the Supabase dashboard")
    
    def create_tables(self):
        """Not applicable for Supabase - tables should be created via SQL editor or migrations"""
        logging.info("Supabase tables should be created via SQL editor or migrations in the dashboard")
    
    def insert_default_categories(self):
        """Insert default categories if they don't exist"""
        categories = [
            {'name': 'Dog Food & Treats', 'description': 'Premium dog food and healthy treats'},
            {'name': 'Cat Litter & Accessories', 'description': 'Cat litter, toys, and accessories'},
            {'name': 'Aquariums & Fish Supplies', 'description': 'Fish tanks, filters, and aquarium supplies'},
            {'name': 'Bird Feeders & Food', 'description': 'Bird cages, feeders, and bird food'},
            {'name': 'Pet Grooming Products', 'description': 'Shampoos, brushes, and grooming tools'},
            {'name': 'Pet Health & Wellness', 'description': 'Vitamins, supplements, and health products'}
        ]
        
        for category in categories:
            try:
                existing = self.select_one('categories', filters={'name': category['name']})
                if not existing:
                    # Don't include is_active if column doesn't exist
                    self.insert('categories', category)
            except Exception as e:
                logging.error(f"Failed to insert category {category['name']}: {e}")
    
    def create_default_admin(self):
        """Create default admin user in profiles table"""
        from werkzeug.security import generate_password_hash
        
        admin_email = 'admin@pawfectfinds.com'
        
        try:
            # Use profiles table instead of users
            existing = self.select_one('profiles', filters={'email': admin_email})
            
            if not existing:
                admin_data = {
                    'username': 'admin',
                    'email': admin_email,
                    'password_hash': generate_password_hash('admin123'),
                    'first_name': 'Admin',
                    'last_name': 'User',
                    'phone': '1234567890',
                    'address': 'Admin Office',
                    'role': 'admin',
                    'status': 'active'
                }
                self.insert('profiles', admin_data)
                logging.info("Default admin created successfully")
        except Exception as e:
            logging.error(f"Failed to create default admin: {e}")
    
    # Placeholder methods for backward compatibility
    def ensure_user_address_fields(self):
        """Supabase schema changes should be done via migrations"""
        pass
    
    def ensure_deliveries_table(self):
        """Supabase tables should be created via SQL editor"""
        pass
    
    def ensure_deliveries_fields(self):
        """Supabase schema changes should be done via migrations"""
        pass
    
    def ensure_notifications_table(self):
        """Supabase tables should be created via SQL editor"""
        pass
    
    def ensure_notifications_fields(self):
        """Supabase schema changes should be done via migrations"""
        pass
    
    def ensure_system_settings_table(self):
        """Supabase tables should be created via SQL editor"""
        pass
    
    def ensure_rider_tables(self):
        """Supabase tables should be created via SQL editor"""
        pass
