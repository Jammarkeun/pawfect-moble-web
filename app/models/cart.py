from app.services.database import Database

class Cart:
    """Cart model using Supabase"""
    
    TABLE_NAME = 'cart_items'

    @classmethod
    def add_item(cls, user_id, product_id, quantity=1, variant_id=None):
        db = Database()
        existing = cls.get_item(user_id, product_id, variant_id)
        if existing:
            new_qty = existing['quantity'] + quantity
            db.update(cls.TABLE_NAME, data={'quantity': new_qty}, filters={'id': existing['id']})
            return True
        
        data = {
            'user_id': user_id,
            'product_id': product_id,
            'quantity': quantity,
        }
        if variant_id is not None:
            data['variant_id'] = variant_id
        db.insert(cls.TABLE_NAME, data)
        return True

    @classmethod
    def update_item(cls, cart_id, quantity):
        db = Database()
        if quantity <= 0:
            return cls.remove_item_by_id(cart_id)
        db.update(cls.TABLE_NAME, data={'quantity': quantity}, filters={'id': cart_id})
        return True

    @classmethod
    def remove_item(cls, user_id, product_id):
        db = Database()
        db.delete(cls.TABLE_NAME, filters={'user_id': user_id, 'product_id': product_id})
        return True

    @classmethod
    def remove_item_by_id(cls, cart_id):
        db = Database()
        db.delete(cls.TABLE_NAME, filters={'id': cart_id})
        return True

    @classmethod
    def clear_cart(cls, user_id):
        db = Database()
        db.delete(cls.TABLE_NAME, filters={'user_id': user_id})
        return True

    @classmethod
    def get_item(cls, user_id, product_id, variant_id=None):
        db = Database()
        try:
            filters = {'user_id': user_id, 'product_id': product_id}
            if variant_id is not None:
                filters['variant_id'] = variant_id
            items = db.select(cls.TABLE_NAME, filters=filters)
            return items[0] if items else None
        except:
            return None

    @classmethod
    def get_count(cls, user_id):
        db = Database()
        try:
            response = db.client.table(cls.TABLE_NAME).select('*', count='exact').eq('user_id', user_id).execute()
            return response.count if response.count else 0
        except:
            return 0

    @classmethod
    def get_user_cart(cls, user_id):
        db = Database()
        try:
            # Get cart items
            cart_items = db.select(cls.TABLE_NAME, filters={'user_id': user_id})
            
            if not cart_items:
                return []
            
            # Enrich with product details
            result = []
            for item in cart_items:
                from app.models.product import Product
                product = Product.get_by_id(item['product_id'])
                if product:
                    result.append({
                        'id': item['id'],
                        'quantity': item['quantity'],
                        'variant_id': item.get('variant_id'),
                        'product_id': product['id'],
                        'name': product['name'],
                        'price': product['price'],
                        'image_url': product.get('image_url'),
                        'stock_quantity': product['stock_quantity'],
                        'seller_id': product['seller_id']
                    })
            
            return result
        except:
            return []

    @classmethod
    def get_total(cls, user_id):
        cart_total = cls.get_cart_total(user_id)
        return cart_total['total']
        
    @classmethod
    def get_cart_total(cls, user_id, include_shipping=True):
        items = cls.get_user_cart(user_id)
        if not items:
            return {
                'subtotal': 0.0,
                'shipping_fees': {},
                'total': 0.0
            }
            
        subtotal = sum(float(item.get('price', 0)) * item.get('quantity', 0) for item in items)
        
        if not include_shipping:
            return {
                'subtotal': subtotal,
                'shipping_fees': {},
                'total': subtotal
            }
        
        seller_items = {}
        for item in items:
            seller_id = item['seller_id']
            if seller_id not in seller_items:
                seller_items[seller_id] = {
                    'items': [],
                    'subtotal': 0.0
                }
            seller_items[seller_id]['items'].append(item)
            seller_items[seller_id]['subtotal'] += float(item.get('price', 0)) * item.get('quantity', 0)
        
        shipping_fees = {}
        for seller_id, data in seller_items.items():
            shipping_fee = round(data['subtotal'] * 0.50, 2)
            shipping_fees[seller_id] = shipping_fee
        
        total = subtotal + sum(shipping_fees.values())
        
        return {
            'subtotal': subtotal,
            'shipping_fees': shipping_fees,
            'total': total
        }
