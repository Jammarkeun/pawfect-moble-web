from app.services.database import Database
from datetime import datetime
import uuid

class Inventory:
    """Inventory model using Supabase"""
    TABLE_NAME = 'inventory_transactions'

    @classmethod
    def add_stock(cls, product_id, quantity, reason=None):
        db = Database()
        product = db.select_one('products', filters={'id': product_id})
        if not product:
            return False
        new_stock = int(product.get('stock_quantity', 0)) + int(quantity)
        db.update('products', data={'stock_quantity': new_stock}, filters={'id': product_id})
        db.insert(cls.TABLE_NAME, {
            'id': str(uuid.uuid4())[:8],
            'product_id': product_id,
            'quantity': quantity,
            'type': 'add',
            'reason': reason or 'manual_adjustment',
            'created_at': datetime.utcnow().isoformat()
        })
        return True

    @classmethod
    def reduce_stock(cls, product_id, quantity, reason=None):
        db = Database()
        product = db.select_one('products', filters={'id': product_id})
        if not product:
            return False
        new_stock = max(0, int(product.get('stock_quantity', 0)) - int(quantity))
        db.update('products', data={'stock_quantity': new_stock}, filters={'id': product_id})
        db.insert(cls.TABLE_NAME, {
            'id': str(uuid.uuid4())[:8],
            'product_id': product_id,
            'quantity': quantity,
            'type': 'reduce',
            'reason': reason or 'sale',
            'created_at': datetime.utcnow().isoformat()
        })
        return True

    @classmethod
    def get_transactions(cls, product_id, limit=None):
        db = Database()
        try:
            query = db.client.table(cls.TABLE_NAME).select('*').eq('product_id', product_id).order('created_at', desc=True)
            if limit:
                query = query.limit(limit)
            result = query.execute()
            return result.data if result.data else []
        except Exception:
            return []

    @classmethod
    def get_low_stock_products(cls, seller_id=None, threshold=10):
        db = Database()
        try:
            query = db.client.table('products').select('*').lte('stock_quantity', threshold)
            if seller_id:
                query = query.eq('seller_id', seller_id)
            result = query.execute()
            return result.data if result.data else []
        except Exception:
            return []

    @classmethod
    def set_low_stock_alert(cls, product_id, threshold):
        db = Database()
        db.update('products', data={'low_stock_threshold': threshold}, filters={'id': product_id})
        return True

    @classmethod
    def get_low_stock_alerts(cls, seller_id=None, acknowledged=False):
        db = Database()
        try:
            products = cls.get_low_stock_products(seller_id)
            alerts = []
            for p in products:
                qty = int(p.get('stock_quantity', 0))
                threshold = int(p.get('low_stock_threshold', 10))
                alerts.append({
                    'id': p['id'],
                    'product_name': p.get('name', 'Unknown'),
                    'current_stock': qty,
                    'threshold_quantity': threshold,
                    'alert_sent': qty <= threshold,
                    'acknowledged': True,
                    'created_at': p.get('updated_at')
                })
            return alerts
        except Exception:
            return []

    @classmethod
    def get_stock_level(cls, product_id):
        db = Database()
        product = db.select_one('products', filters={'id': product_id})
        return int(product.get('stock_quantity', 0)) if product else 0


class Wishlist:
    """Wishlist model using Supabase"""
    TABLE_NAME = 'wishlist'

    @classmethod
    def add_item(cls, user_id, product_id):
        db = Database()
        existing = db.select_one(cls.TABLE_NAME, filters={'user_id': user_id, 'product_id': product_id})
        if existing:
            return True
        db.insert(cls.TABLE_NAME, {
            'id': str(uuid.uuid4())[:8],
            'user_id': user_id,
            'product_id': product_id,
            'created_at': datetime.utcnow().isoformat()
        })
        return True

    @classmethod
    def remove_item(cls, user_id, product_id):
        db = Database()
        db.delete(cls.TABLE_NAME, filters={'user_id': user_id, 'product_id': product_id})
        return True

    @classmethod
    def get_user_wishlist(cls, user_id):
        db = Database()
        try:
            items = db.client.table(cls.TABLE_NAME).select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            result = items.data if items.data else []
            for item in result:
                product = db.select_one('products', filters={'id': item['product_id']})
                item['product'] = product or {}
            return result
        except Exception:
            return []

    @classmethod
    def is_in_wishlist(cls, user_id, product_id):
        db = Database()
        item = db.select_one(cls.TABLE_NAME, filters={'user_id': user_id, 'product_id': product_id})
        return item is not None

    @classmethod
    def count(cls, user_id):
        db = Database()
        try:
            result = db.client.table(cls.TABLE_NAME).select('*', count='exact').eq('user_id', user_id).execute()
            return result.count if hasattr(result, 'count') else 0
        except Exception:
            return 0

    @classmethod
    def get_count(cls, user_id):
        """Alias for count()"""
        return cls.count(user_id)
