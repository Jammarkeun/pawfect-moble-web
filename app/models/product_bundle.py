from app.services.database import Database
from datetime import datetime
import uuid

class ProductBundle:
    """Product bundle model using Supabase"""
    TABLE_NAME = 'product_bundles'
    ITEMS_TABLE = 'bundle_items'

    @classmethod
    def create(cls, seller_id, name, description=None, discount_percent=0, status='active'):
        db = Database()
        data = {
            'id': str(uuid.uuid4())[:8],
            'seller_id': seller_id,
            'name': name,
            'description': description,
            'discount_percent': discount_percent,
            'status': status,
            'created_at': datetime.utcnow().isoformat()
        }
        return db.insert(cls.TABLE_NAME, data)

    @classmethod
    def get_by_id(cls, bundle_id):
        db = Database()
        bundle = db.select_one(cls.TABLE_NAME, filters={'id': bundle_id})
        if bundle:
            bundle['items'] = cls.get_items(bundle_id)
            bundle['total_price'] = cls.calculate_total(bundle_id)
        return bundle

    @classmethod
    def get_by_seller(cls, seller_id, status='active'):
        db = Database()
        try:
            query = db.client.table(cls.TABLE_NAME).select('*').eq('seller_id', seller_id)
            if status:
                query = query.eq('status', status)
            query = query.order('created_at', desc=True)
            bundles = query.execute()
            result = bundles.data if bundles.data else []
            for bundle in result:
                bundle['items'] = cls.get_items(bundle['id'])
                bundle['total_price'] = cls.calculate_total(bundle['id'])
            return result
        except Exception:
            return []

    @classmethod
    def get_items(cls, bundle_id):
        db = Database()
        try:
            items = db.client.table(cls.ITEMS_TABLE).select('*').eq('bundle_id', bundle_id).execute()
            result = items.data if items.data else []
            for item in result:
                product = db.select_one('products', filters={'id': item.get('product_id')})
                item['product'] = product or {}
            return result
        except Exception:
            return []

    @classmethod
    def add_item(cls, bundle_id, product_id, quantity=1):
        db = Database()
        existing = db.select_one(cls.ITEMS_TABLE, filters={'bundle_id': bundle_id, 'product_id': product_id})
        if existing:
            db.update(cls.ITEMS_TABLE, data={'quantity': int(existing.get('quantity', 0)) + quantity}, filters={'id': existing['id']})
            return existing
        return db.insert(cls.ITEMS_TABLE, {
            'id': str(uuid.uuid4())[:8],
            'bundle_id': bundle_id,
            'product_id': product_id,
            'quantity': quantity
        })

    @classmethod
    def remove_item(cls, item_id):
        db = Database()
        db.delete(cls.ITEMS_TABLE, filters={'id': item_id})
        return True

    @classmethod
    def clear_items(cls, bundle_id):
        db = Database()
        items = db.select(cls.ITEMS_TABLE, filters={'bundle_id': bundle_id})
        for item in items:
            db.delete(cls.ITEMS_TABLE, filters={'id': item['id']})
        return True

    @classmethod
    def update(cls, bundle_id, **kwargs):
        db = Database()
        allowed = ['name', 'description', 'discount_percent', 'status']
        update_data = {k: v for k, v in kwargs.items() if k in allowed}
        if not update_data:
            return False
        db.update(cls.TABLE_NAME, data=update_data, filters={'id': bundle_id})
        return True

    @classmethod
    def delete(cls, bundle_id):
        db = Database()
        cls.clear_items(bundle_id)
        db.delete(cls.TABLE_NAME, filters={'id': bundle_id})
        return True

    @classmethod
    def calculate_total(cls, bundle_id):
        db = Database()
        bundle = db.select_one(cls.TABLE_NAME, filters={'id': bundle_id})
        if not bundle:
            return 0
        items = cls.get_items(bundle_id)
        total = 0.0
        for item in items:
            product = item.get('product', {})
            price = float(product.get('price', 0))
            qty = int(item.get('quantity', 1))
            total += price * qty
        discount = float(bundle.get('discount_percent', 0))
        if discount > 0:
            total = total * (1 - discount / 100)
        return round(total, 2)
