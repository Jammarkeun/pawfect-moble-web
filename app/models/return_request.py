from app.services.database import Database
from datetime import datetime
import uuid

class ReturnRequest:
    """Return request model using Supabase"""
    TABLE_NAME = 'return_requests'

    @classmethod
    def create(cls, order_id, user_id, product_id, reason, description=None, quantity=1):
        db = Database()
        data = {
            'id': str(uuid.uuid4())[:8],
            'order_id': order_id,
            'user_id': user_id,
            'product_id': product_id,
            'reason': reason,
            'description': description,
            'quantity': quantity,
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat()
        }
        return db.insert(cls.TABLE_NAME, data)

    @classmethod
    def get_by_id(cls, return_id):
        db = Database()
        req = db.select_one(cls.TABLE_NAME, filters={'id': return_id})
        if req:
            user = db.select_one('profiles', filters={'id': req.get('user_id')})
            req['user'] = user or {}
        return req

    @classmethod
    def get_by_user(cls, user_id, status=None, limit=None, offset=0):
        db = Database()
        try:
            query = db.client.table(cls.TABLE_NAME).select('*').eq('user_id', user_id).order('created_at', desc=True)
            if status:
                query = query.eq('status', status)
            if limit:
                query = query.range(offset, offset + limit - 1)
            return query.execute().data or []
        except Exception:
            return []

    @classmethod
    def get_by_seller(cls, seller_id, status=None, limit=None, offset=0):
        db = Database()
        try:
            query = db.client.table(cls.TABLE_NAME).select('*').order('created_at', desc=True)
            if status:
                query = query.eq('status', status)
            if limit:
                query = query.range(offset, offset + limit - 1)
            requests = query.execute().data or []
            # Filter by seller's products
            seller_products = db.client.table('products').select('id').eq('seller_id', seller_id).execute()
            seller_product_ids = [p['id'] for p in (seller_products.data or [])]
            return [r for r in requests if r.get('product_id') in seller_product_ids]
        except Exception:
            return []

    @classmethod
    def get_all(cls, status=None, limit=None, offset=0):
        db = Database()
        try:
            query = db.client.table(cls.TABLE_NAME).select('*').order('created_at', desc=True)
            if status:
                query = query.eq('status', status)
            if limit:
                query = query.range(offset, offset + limit - 1)
            return query.execute().data or []
        except Exception:
            return []

    @classmethod
    def update_status(cls, return_id, status, admin_notes=None, refund_amount=None):
        db = Database()
        data = {'status': status, 'updated_at': datetime.utcnow().isoformat()}
        if admin_notes:
            data['admin_notes'] = admin_notes
        if refund_amount is not None:
            data['refund_amount'] = refund_amount
        db.update(cls.TABLE_NAME, data=data, filters={'id': return_id})
        req = cls.get_by_id(return_id)
        if req:
            db.insert('notifications', {
                'user_id': req['user_id'],
                'type': 'return_update',
                'title': f'Return Request {status.title()}',
                'message': f'Your return request #{return_id} has been {status}',
                'created_at': datetime.utcnow().isoformat(),
                'is_read': False
            })
        return True

    @classmethod
    def count(cls, status=None, user_id=None, seller_id=None):
        db = Database()
        try:
            query = db.client.table(cls.TABLE_NAME).select('*', count='exact')
            if status:
                query = query.eq('status', status)
            if user_id:
                query = query.eq('user_id', user_id)
            if seller_id:
                seller_products = db.client.table('products').select('id').eq('seller_id', seller_id).execute()
                seller_product_ids = [p['id'] for p in (seller_products.data or [])]
                if not seller_product_ids:
                    return 0
                query = query.in_('product_id', seller_product_ids)
            result = query.execute()
            return result.count if hasattr(result, 'count') else 0
        except Exception:
            return 0
