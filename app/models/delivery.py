from app.services.database import Database
from datetime import datetime
import uuid

class Delivery:
    """Delivery model using Supabase"""
    TABLE_NAME = 'deliveries'

    @classmethod
    def create(cls, order_id, rider_id, pickup_address, delivery_address):
        db = Database()
        delivery_data = {
            'id': str(uuid.uuid4())[:8],
            'order_id': order_id,
            'rider_id': rider_id,
            'status': 'assigned',
            'pickup_address': pickup_address,
            'delivery_address': delivery_address,
            'assigned_at': datetime.utcnow().isoformat(),
            'created_at': datetime.utcnow().isoformat()
        }
        return db.insert(cls.TABLE_NAME, delivery_data)

    @classmethod
    def get_by_id(cls, delivery_id):
        db = Database()
        return db.select_one(cls.TABLE_NAME, filters={'id': delivery_id})

    @classmethod
    def get_by_order(cls, order_id):
        db = Database()
        return db.select_one(cls.TABLE_NAME, filters={'order_id': order_id})

    @classmethod
    def get_by_rider(cls, rider_id, status=None):
        db = Database()
        try:
            query = db.client.table(cls.TABLE_NAME).select('*').eq('rider_id', rider_id)
            if status:
                query = query.eq('status', status)
            query = query.order('created_at', desc=True)
            deliveries = query.execute()
            return deliveries.data if deliveries.data else []
        except Exception:
            return []

    @classmethod
    def update_status(cls, delivery_id, status, **kwargs):
        db = Database()
        data = {'status': status, 'updated_at': datetime.utcnow().isoformat()}
        data.update(kwargs)
        db.update(cls.TABLE_NAME, data=data, filters={'id': delivery_id})
        return True

    @classmethod
    def assign_rider(cls, order_id, rider_id):
        db = Database()
        order = db.select_one('orders', filters={'id': order_id})
        if not order:
            return False
        db.update('orders', data={'rider_id': rider_id, 'status': 'assigned', 'updated_at': datetime.utcnow().isoformat()}, filters={'id': order_id})
        delivery = cls.create(order_id, rider_id, '', order.get('shipping_address', ''))
        return delivery is not None

    @classmethod
    def get_active_delivery(cls, rider_id):
        db = Database()
        try:
            deliveries = db.client.table(cls.TABLE_NAME).select('*').eq('rider_id', rider_id).in_('status', ['assigned', 'picked_up', 'in_transit']).execute()
            return deliveries.data[0] if deliveries.data else None
        except Exception:
            return None

    @classmethod
    def complete_delivery(cls, delivery_id, proof_image=None):
        db = Database()
        data = {'status': 'delivered', 'proof_image': proof_image, 'completed_at': datetime.utcnow().isoformat(), 'updated_at': datetime.utcnow().isoformat()}
        db.update(cls.TABLE_NAME, data=data, filters={'id': delivery_id})
        delivery = cls.get_by_id(delivery_id)
        if delivery:
            db.update('orders', data={'status': 'delivered', 'updated_at': datetime.utcnow().isoformat()}, filters={'id': delivery['order_id']})
        return True

    @classmethod
    def calculate_earnings(cls, delivery_id):
        db = Database()
        delivery = cls.get_by_id(delivery_id)
        if not delivery:
            return 0
        order = db.select_one('orders', filters={'id': delivery['order_id']})
        if order:
            return float(order.get('shipping_fee', 0)) * 0.8
        return 0
