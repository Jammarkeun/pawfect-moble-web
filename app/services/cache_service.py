import json
import pickle
from datetime import datetime, timedelta
from functools import wraps

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from app.services.database import Database


class CacheService:
    """Caching service with Redis and database fallback"""
    
    def __init__(self):
        self.redis_client = None
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host='localhost',
                    port=6379,
                    db=0,
                    decode_responses=False,
                    socket_connect_timeout=2
                )
                # Test connection
                self.redis_client.ping()
                print("✓ Redis connected successfully")
            except (redis.ConnectionError, redis.TimeoutError) as e:
                print(f"✗ Redis connection failed: {e}. Using database fallback.")
                self.redis_client = None
        else:
            print("✗ Redis not installed. Using database fallback.")
    
    def get(self, key):
        """Get value from cache"""
        # Try Redis first
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    return pickle.loads(value)
            except Exception as e:
                print(f"Redis get error: {e}")
        
        # Fallback to database
        return self._get_from_db(key)
    
    def set(self, key, value, ttl=3600):
        """
        Set value in cache with TTL (time to live) in seconds
        Default TTL: 1 hour
        """
        # Try Redis first
        if self.redis_client:
            try:
                pickled_value = pickle.dumps(value)
                self.redis_client.setex(key, ttl, pickled_value)
                return True
            except Exception as e:
                print(f"Redis set error: {e}")
        
        # Fallback to database
        return self._set_in_db(key, value, ttl)
    
    def delete(self, key):
        """Delete key from cache"""
        # Try Redis first
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception as e:
                print(f"Redis delete error: {e}")
        
        # Fallback to database
        self._delete_from_db(key)
        return True
    
    def exists(self, key):
        """Check if key exists in cache"""
        if self.redis_client:
            try:
                return self.redis_client.exists(key) > 0
            except Exception:
                pass
        
        return self._exists_in_db(key)
    
    def clear_pattern(self, pattern):
        """Clear all keys matching pattern (e.g., 'product:*')"""
        if self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                return True
            except Exception as e:
                print(f"Redis clear_pattern error: {e}")
        
        # For database fallback, clear similar keys
        self._clear_pattern_in_db(pattern)
        return True
    
    def increment(self, key, amount=1):
        """Increment a numeric value"""
        if self.redis_client:
            try:
                return self.redis_client.incrby(key, amount)
            except Exception:
                pass
        
        # Database fallback
        current = self.get(key) or 0
        new_value = current + amount
        self.set(key, new_value)
        return new_value
    
    def get_many(self, keys):
        """Get multiple values at once"""
        if self.redis_client:
            try:
                values = self.redis_client.mget(keys)
                return [pickle.loads(v) if v else None for v in values]
            except Exception:
                pass
        
        return [self.get(key) for key in keys]
    
    def set_many(self, mapping, ttl=3600):
        """Set multiple key-value pairs at once"""
        if self.redis_client:
            try:
                pipe = self.redis_client.pipeline()
                for key, value in mapping.items():
                    pickled_value = pickle.dumps(value)
                    pipe.setex(key, ttl, pickled_value)
                pipe.execute()
                return True
            except Exception:
                pass
        
        for key, value in mapping.items():
            self.set(key, value, ttl)
        return True
    
    # Database fallback methods
    def _get_from_db(self, key):
        """Get from database cache table"""
        db = Database()
        try:
            result = db.execute_query(
                "SELECT cache_value FROM cache_entries WHERE cache_key = %s AND expires_at > NOW()",
                (key,),
                fetch=True,
                fetchone=True
            )
            if result:
                return pickle.loads(result['cache_value'].encode('latin1'))
        except Exception as e:
            print(f"DB cache get error: {e}")
        return None
    
    def _set_in_db(self, key, value, ttl):
        """Set in database cache table"""
        db = Database()
        try:
            pickled_value = pickle.dumps(value)
            expires_at = datetime.now() + timedelta(seconds=ttl)
            
            db.execute_query("""
                INSERT INTO cache_entries (cache_key, cache_value, expires_at)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    cache_value = VALUES(cache_value),
                    expires_at = VALUES(expires_at)
            """, (key, pickled_value.decode('latin1'), expires_at))
            return True
        except Exception as e:
            print(f"DB cache set error: {e}")
            return False
    
    def _delete_from_db(self, key):
        """Delete from database cache table"""
        db = Database()
        try:
            db.execute_query("DELETE FROM cache_entries WHERE cache_key = %s", (key,))
        except Exception:
            pass
    
    def _exists_in_db(self, key):
        """Check if key exists in database cache"""
        db = Database()
        try:
            result = db.execute_query(
                "SELECT 1 FROM cache_entries WHERE cache_key = %s AND expires_at > NOW()",
                (key,),
                fetch=True,
                fetchone=True
            )
            return result is not None
        except Exception:
            return False
    
    def _clear_pattern_in_db(self, pattern):
        """Clear keys matching pattern from database"""
        db = Database()
        try:
            # Convert Redis pattern to SQL LIKE pattern
            sql_pattern = pattern.replace('*', '%').replace('?', '_')
            db.execute_query("DELETE FROM cache_entries WHERE cache_key LIKE %s", (sql_pattern,))
        except Exception:
            pass


# Global cache instance
cache = CacheService()


def cached(ttl=3600, key_prefix=''):
    """
    Decorator for caching function results
    
    Usage:
        @cached(ttl=1800, key_prefix='products')
        def get_products():
            # expensive operation
            return products
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}"
            if args:
                cache_key += f":{':'.join(str(arg) for arg in args)}"
            if kwargs:
                cache_key += f":{':'.join(f'{k}={v}' for k, v in sorted(kwargs.items()))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator


def invalidate_cache(pattern):
    """
    Helper function to invalidate cache by pattern
    
    Usage:
        invalidate_cache('products:*')  # Clear all product caches
    """
    cache.clear_pattern(pattern)
