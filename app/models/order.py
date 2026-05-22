from app.services.database import Database
from app.models.cart import Cart
from datetime import datetime
import time

class Order:
    """Order model using Supabase"""
    TABLE_NAME = 'orders'

    @classmethod
    def create_from_cart(cls, user_id, shipping_address, payment_method='cod', notes=None):
        db = Database()
        cart_items = Cart.get_user_cart(user_id)
        if not cart_items:
            return None

        # Group items by seller
        seller_items = {}
        for item in cart_items:
            product = db.select_one('products', filters={'id': item['product_id']})
            if not product:
                continue
            seller_id = product.get('seller_id')
            if seller_id not in seller_items:
                seller_items[seller_id] = {'items': [], 'total': 0.0, 'delivery_fee': 0}
            seller_items[seller_id]['items'].append({
                'product_id': item['product_id'],
                'quantity': item['quantity'],
                'price': float(item.get('price', 0)),
                'product_name': product.get('name', '')
            })
            seller_items[seller_id]['total'] += float(item.get('price', 0)) * int(item.get('quantity', 1))

        order_ids = []
        for seller_id, data in seller_items.items():
            order_id = int(time.time() * 1000) % 100000000
            order_data = {
                'id': order_id,
                'user_id': user_id,
                'seller_id': seller_id,
                'order_number': f'ORD{int(time.time() * 1000)}',
                'status': 'pending',
                'total_amount': round(data['total'] + data['delivery_fee'], 2),
                'delivery_fee': data['delivery_fee'],
                'product_total': round(data['total'], 2),
                'payment_method': payment_method,
                'payment_status': 'pending',
                'shipping_address': shipping_address,
                'notes': notes,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            new_order = db.insert(cls.TABLE_NAME, order_data)
            if new_order:
                # Create order items
                for item in data['items']:
                    db.insert('order_items', {
                        'order_id': order_id,
                        'product_id': item['product_id'],
                        'quantity': item['quantity'],
                        'unit_price': item['price'],
                        'product_name': item['product_name'],
                        'total_price': round(item['price'] * item['quantity'], 2)
                    })
                    db.update('products',
                             data={'stock_quantity': db.client.table('products').select('stock_quantity').eq('id', item['product_id']).execute().data[0].get('stock_quantity', 0) - item['quantity']},
                             filters={'id': item['product_id']})
                order_ids.append(order_id)

        if order_ids:
            Cart.clear_cart(user_id)
            # Insert notifications for sellers
            for seller_id in seller_items:
                db.insert('notifications', {
                    'user_id': seller_id,
                    'type': 'new_order',
                    'title': 'New Order Received',
                    'message': f'You have received a new order!',
                    'created_at': datetime.utcnow().isoformat(),
                    'is_read': False
                })
        return order_ids

    @classmethod
    def get_by_id(cls, order_id):
        db = Database()
        order = db.select_one(cls.TABLE_NAME, filters={'id': order_id})
        if order:
            order = cls._parse_dates(order)
            items = db.select('order_items', filters={'order_id': order_id})
            order['items'] = [cls._normalize_item(i) for i in items]
            if order.get('user_id'):
                user = db.select_one('profiles', filters={'id': order['user_id']})
                order['user'] = user or {}
            delivery = db.select_one('deliveries', filters={'order_id': order_id})
            order['delivery'] = delivery or None
        return order

    @staticmethod
    def _normalize_item(item):
        """Add 'price_at_time' alias for 'unit_price' used in templates."""
        if isinstance(item, dict) and 'unit_price' in item and 'price_at_time' not in item:
            item['price_at_time'] = item['unit_price']
        return item

    @staticmethod
    def _parse_dates(obj):
        from datetime import datetime
        for key in list(obj.keys()):
            val = obj.get(key)
            if isinstance(val, str) and 'T' in val and ('+' in val or 'Z' in val):
                try:
                    obj[key] = datetime.fromisoformat(val.replace('Z', '+00:00'))
                except:
                    pass
        return obj

    @classmethod
    def list_for_user(cls, user_id, limit=None, offset=0):
        db = Database()
        try:
            query = db.client.table(cls.TABLE_NAME).select('*').eq('user_id', user_id).order('created_at', desc=True)
            if limit:
                query = query.range(offset, offset + limit - 1)
            orders = query.execute()
            result = orders.data if orders.data else []
            for order in result:
                cls._parse_dates(order)
                items = db.select('order_items', filters={'order_id': order['id']})
                order['items'] = [cls._normalize_item(i) for i in items]
            return result
        except Exception:
            return []

    @classmethod
    def list_for_seller(cls, seller_id, status=None, search=None, limit=None, offset=0):
        db = Database()
        try:
            query = db.client.table(cls.TABLE_NAME).select('*').eq('seller_id', seller_id)
            if status:
                query = query.eq('status', status)
            query = query.order('created_at', desc=True)
            if limit:
                query = query.range(offset, offset + limit - 1)
            orders = query.execute()
            result = orders.data if orders.data else []
            for order in result:
                cls._parse_dates(order)
                items = db.select('order_items', filters={'order_id': order['id']})
                order['items'] = [cls._normalize_item(i) for i in items]
                if order.get('user_id'):
                    user = db.select_one('profiles', filters={'id': order['user_id']})
                    order['user'] = user or {}
            return result
        except Exception:
            return []

    @classmethod
    def update_status(cls, order_id, status, rider_id=None):
        db = Database()
        data = {'status': status, 'updated_at': datetime.utcnow().isoformat()}
        if rider_id:
            data['rider_id'] = rider_id
        db.update(cls.TABLE_NAME, data=data, filters={'id': order_id})

        # Notify customer
        order = cls.get_by_id(order_id)
        if order:
            db.insert('notifications', {
                'user_id': order['user_id'],
                'type': 'order_status',
                'title': f'Order {status.replace("_", " ").title()}',
                'message': f'Your order #{order_id} status has been updated to {status}',
                'created_at': datetime.utcnow().isoformat(),
                'is_read': False
            })
        return True

    @classmethod
    def update_payment_status(cls, order_id, payment_status):
        db = Database()
        db.update(cls.TABLE_NAME, data={'payment_status': payment_status, 'updated_at': datetime.utcnow().isoformat()}, filters={'id': order_id})
        return True

    @classmethod
    def count(cls, status=None):
        db = Database()
        try:
            query = db.client.table(cls.TABLE_NAME).select('*', count='exact')
            if status:
                query = query.eq('status', status)
            result = query.execute()
            return result.count if hasattr(result, 'count') else 0
        except Exception:
            return 0

    @classmethod
    def get_seller_id(cls, order_id):
        order = cls.get_by_id(order_id)
        return order.get('seller_id') if order else None

    @classmethod
    def get_order_status(cls, order_id):
        order = cls.get_by_id(order_id)
        return order.get('status', 'pending') if order else 'pending'

    @classmethod
    def get_available_deliveries(cls, limit=50):
        db = Database()
        try:
            query = db.client.table(cls.TABLE_NAME).select('*').eq('status', 'ready_for_delivery').order('created_at', desc=True)
            if limit:
                query = query.limit(limit)
            orders = query.execute()
            result = orders.data if orders.data else []
            for order in result:
                items = db.select('order_items', filters={'order_id': order['id']})
                order['items'] = [cls._normalize_item(i) for i in items]
                if order.get('user_id'):
                    user = db.select_one('profiles', filters={'id': order['user_id']})
                    order['user_address'] = (user or {}).get('address', '')
            return result
        except Exception:
            return []

    @staticmethod
    def _notify_seller_new_order(order_id, seller_id):
        db = Database()
        db.insert('notifications', {
            'user_id': seller_id,
            'type': 'new_order',
            'title': 'New Order',
            'message': f'New order #{order_id} has been placed',
            'created_at': datetime.utcnow().isoformat(),
            'is_read': False
        })
