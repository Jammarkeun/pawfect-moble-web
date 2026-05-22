from app.services.database import Database
import json

class ProductVariant:
    """Model for product variants using Supabase"""
    
    TABLE_NAME = 'product_variants'
    
    @classmethod
    def create(cls, product_id, name, price, sku=None, sale_price=None, stock_quantity=0, 
               image_url=None, attributes=None, display_order=0):
        """Create a new product variant"""
        db = Database()
        
        data = {
            'product_id': product_id,
            'name': name,
            'sku': sku,
            'price': price,
            'sale_price': sale_price,
            'stock_quantity': stock_quantity,
            'image_url': image_url,
            'attributes': json.dumps(attributes) if attributes else None,
            'display_order': display_order
        }
        
        result = db.insert(cls.TABLE_NAME, data)
        return result
    
    @classmethod
    def get_by_id(cls, variant_id):
        """Get variant by ID"""
        db = Database()
        variant = db.select_one(cls.TABLE_NAME, filters={'id': variant_id})
        if variant and variant.get('attributes'):
            try:
                variant['attributes'] = json.loads(variant['attributes'])
            except:
                variant['attributes'] = {}
        return variant
    
    @classmethod
    def get_by_product(cls, product_id, status='active'):
        """Get all variants for a product"""
        db = Database()
        try:
            query = db.client.table(cls.TABLE_NAME).select('*').eq('product_id', product_id)
            if status:
                query = query.eq('status', status)
            query = query.order('display_order').order('id')
            response = query.execute()
            
            variants = response.data if response.data else []
            for v in variants:
                if v.get('attributes'):
                    try:
                        v['attributes'] = json.loads(v['attributes'])
                    except:
                        v['attributes'] = {}
            return variants
        except:
            return []
    
    @classmethod
    def update(cls, variant_id, **kwargs):
        """Update variant"""
        db = Database()
        allowed = ['name', 'sku', 'price', 'sale_price', 'stock_quantity', 'image_url', 'attributes', 'display_order', 'status']
        
        data = {}
        for k, v in kwargs.items():
            if k in allowed:
                if k == 'attributes' and isinstance(v, dict):
                    v = json.dumps(v)
                data[k] = v
        
        if not data:
            return False
        
        db.update(cls.TABLE_NAME, data=data, filters={'id': variant_id})
        return True
    
    @classmethod
    def delete(cls, variant_id):
        """Delete a variant"""
        db = Database()
        db.delete(cls.TABLE_NAME, filters={'id': variant_id})
        return True
    
    @classmethod
    def delete_by_product(cls, product_id):
        """Delete all variants for a product"""
        db = Database()
        db.delete(cls.TABLE_NAME, filters={'product_id': product_id})
        return True
