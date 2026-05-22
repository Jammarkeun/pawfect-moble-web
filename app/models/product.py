from app.services.database import Database
import re
from datetime import datetime

class Product:
    """Product model for product operations with Supabase"""
    
    TABLE_NAME = 'products'
    
    @classmethod
    def generate_slug(cls, name, product_id=None):
        """Generate a unique URL-friendly slug from product name"""
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
        
        # Check for uniqueness
        db = Database()
        base_slug = slug
        counter = 1
        while True:
            filters = {'slug': slug}
            existing = db.select_one(cls.TABLE_NAME, filters=filters)
            
            if not existing or (product_id and existing.get('id') == product_id):
                break
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug
    
    @classmethod
    def create(cls, seller_id, category_id, name, description, price, stock_quantity, image_url=None, image_urls=None,
               sku=None, slug=None, sale_price=None, sale_start_date=None, sale_end_date=None,
               meta_title=None, meta_description=None, meta_keywords=None, status='active'):
        """Create a new product with optional multiple images"""
        db = Database()
        
        # Only include columns that exist in Supabase products table
        product_data = {
            'seller_id': seller_id,
            'category_id': category_id,
            'name': name,
            'sku': sku,
            'description': description,
            'price': price,
            'stock_quantity': stock_quantity,
            'image_url': image_url,
            'status': status,
        }
        # Remove None values so Supabase uses defaults
        product_data = {k: v for k, v in product_data.items() if v is not None}
        
        new_product = db.insert(cls.TABLE_NAME, product_data)
        
        # If multiple images provided, add them to product_images table
        if new_product and image_urls and len(image_urls) > 0:
            cls.add_images(new_product['id'], image_urls)
        
        return cls.get_by_id(new_product['id']) if new_product else None
    
    @classmethod
    def get_by_id(cls, product_id):
        """Get product by ID with related data"""
        db = Database()
        
        # Get product
        product = db.select_one(cls.TABLE_NAME, filters={'id': product_id})
        
        if product:
            # Get category name
            if product.get('category_id'):
                category = db.select_one('categories', filters={'id': product['category_id']})
                product['category_name'] = category.get('name', 'Unknown') if category else 'Unknown'
            else:
                product['category_name'] = 'Unknown'
            
            # Get seller info from profiles table
            if product.get('seller_id'):
                seller = db.select_one('profiles', filters={'id': product['seller_id']})
                if seller:
                    product['seller_username'] = seller.get('username', 'Unknown')
                    product['seller_verified'] = seller.get('is_verified', False)
                    product['seller_verification_level'] = seller.get('verification_level', 'none')
                else:
                    product['seller_username'] = 'Unknown'
                    product['seller_verified'] = False
                    product['seller_verification_level'] = 'none'
            
            # Get images
            product['images'] = cls.get_images(product_id)
            
            # Calculate effective price
            product['effective_price'] = cls.get_effective_price(product)
        
        return product
    
    @classmethod
    def update(cls, product_id, **kwargs):
        """Update product"""
        db = Database()
        allowed = ['category_id', 'name', 'sku', 'description', 'price', 'stock_quantity', 'image_url', 'status']
        
        update_data = {}
        for k, v in kwargs.items():
            if k in allowed and v is not None:
                update_data[k] = v
        
        if not update_data:
            return False
        
        db.update(cls.TABLE_NAME, data=update_data, filters={'id': product_id})
        return True
    
    @classmethod
    def delete(cls, product_id):
        """Delete product"""
        db = Database()
        db.delete(cls.TABLE_NAME, filters={'id': product_id})
        return True
    
    @classmethod
    def get_effective_price(cls, product):
        """Get the effective price considering scheduled sales"""
        if not product.get('sale_price'):
            return float(product.get('price', 0))
        
        now = datetime.now()
        sale_start = product.get('sale_start_date')
        sale_end = product.get('sale_end_date')
        
        # Check if sale is active
        if sale_start and now < sale_start:
            return float(product['price'])
        if sale_end and now > sale_end:
            return float(product['price'])
        
        return float(product['sale_price'])
    
    @classmethod
    def list(cls, category_id=None, search=None, seller_id=None, status='active', limit=None, offset=0):
        """List products with filters"""
        db = Database()
        
        try:
            if not db.client:
                raise Exception("Supabase client not initialized. Check SUPABASE_URL and SUPABASE_SERVICE_KEY env vars.")
            # Build query
            query = db.client.table(cls.TABLE_NAME).select('*')
            
            if status:
                query = query.eq('status', status)
            if category_id:
                query = query.eq('category_id', category_id)
            if seller_id:
                query = query.eq('seller_id', seller_id)
            if search:
                query = query.ilike('name', f'%{search}%')
            
            query = query.order('created_at', desc=True)
            
            if limit:
                query = query.limit(limit).range(offset, offset + limit - 1)
            
            response = query.execute()
            products = [Database._parse_response(row) for row in (response.data or [])]
            
            # Enrich each product with related data
            for product in products:
                # Get category name
                if product.get('category_id'):
                    category = db.select_one('categories', filters={'id': product['category_id']})
                    product['category_name'] = category.get('name', 'Unknown') if category else 'Unknown'
                else:
                    product['category_name'] = 'Unknown'
                
                # Get seller info from profiles table
                if product.get('seller_id'):
                    seller = db.select_one('profiles', filters={'id': product['seller_id']})
                    if seller:
                        product['seller_username'] = seller.get('username', 'Unknown')
                        product['seller_verified'] = seller.get('is_verified', False)
                        product['seller_verification_level'] = seller.get('verification_level', 'none')
                    else:
                        product['seller_username'] = 'Unknown'
                        product['seller_verified'] = False
                        product['seller_verification_level'] = 'none'
                else:
                    product['seller_username'] = 'Unknown'
                    product['seller_verified'] = False
                    product['seller_verification_level'] = 'none'
                
                # Get images
                product['images'] = cls.get_images(product['id'])
                
                # Calculate effective price
                product['effective_price'] = cls.get_effective_price(product)
            
            return products
        except Exception as e:
            print(f"Error listing products: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @classmethod
    def count(cls, category_id=None, search=None, seller_id=None, status='active'):
        """Count products with filters"""
        db = Database()
        
        try:
            if not db.client:
                return 0
            query = db.client.table(cls.TABLE_NAME).select('*', count='exact')
            
            if status:
                query = query.eq('status', status)
            if category_id:
                query = query.eq('category_id', category_id)
            if seller_id:
                query = query.eq('seller_id', seller_id)
            if search:
                query = query.ilike('name', f'%{search}%')
            
            response = query.execute()
            return response.count if response.count else 0
        except Exception as e:
            print(f"Error counting products: {e}")
            return 0
    
    @classmethod
    def add_images(cls, product_id, image_urls, set_first_as_primary=True):
        """Add multiple images to a product"""
        db = Database()
        
        try:
            for idx, image_url in enumerate(image_urls):
                is_primary = (idx == 0 and set_first_as_primary)
                image_data = {
                    'product_id': product_id,
                    'image_url': image_url,
                    'display_order': idx,
                    'is_primary': is_primary
                }
                db.insert('product_images', image_data)
        except Exception:
            pass
        
        # Update the main product table with the primary image
        if image_urls and set_first_as_primary:
            db.update(cls.TABLE_NAME, 
                     data={'image_url': image_urls[0]}, 
                     filters={'id': product_id})
        
        return True
    
    @classmethod
    def get_images(cls, product_id):
        """Get all images for a product, ordered by display_order"""
        db = Database()
        
        try:
            if not db.client:
                return []
            query = db.client.table('product_images').select('*') \
                .eq('product_id', product_id) \
                .order('display_order') \
                .order('created_at')
            
            response = query.execute()
            return response.data if response.data else []
        except Exception:
            return []
    
    @classmethod
    def delete_image(cls, image_id):
        """Delete a specific product image"""
        db = Database()
        db.delete('product_images', filters={'id': image_id})
        return True
    
    @classmethod
    def delete_all_images(cls, product_id):
        """Delete all images for a product"""
        db = Database()
        
        try:
            # Get all images for this product
            images = db.select('product_images', filters={'product_id': product_id})
            
            # Delete each image
            for image in images:
                db.delete('product_images', filters={'id': image['id']})
            
            return True
        except Exception as e:
            print(f"Error deleting images: {e}")
            return False
    
    @classmethod
    def update_image_display_order(cls, product_id, image_order):
        """Update display_order for product images
        
        Args:
            product_id: The product ID
            image_order: List of image IDs in desired order, or list of dicts with 'id' and 'position'
        """
        db = Database()
        
        if not image_order:
            return True
        
        print(f"Updating display order for product {product_id}: {image_order}")
        
        # Handle different formats of image_order
        for position, item in enumerate(image_order):
            if isinstance(item, dict):
                image_id = item.get('id')
                order_pos = item.get('position', position)
            else:
                image_id = item
                order_pos = position
            
            print(f"  Setting image {image_id} to order {order_pos}")
            
            # Update using Supabase
            db.update('product_images', 
                     data={'display_order': order_pos}, 
                     filters={'id': image_id, 'product_id': product_id})
        
        return True
    
    @classmethod
    def set_primary_image(cls, product_id, image_id):
        """Set a specific image as the primary image for a product"""
        db = Database()
        
        try:
            # First, unset all primary flags for this product
            images = db.select('product_images', filters={'product_id': product_id})
            for image in images:
                db.update('product_images', 
                         data={'is_primary': False}, 
                         filters={'id': image['id']})
            
            # Set the specified image as primary
            db.update('product_images', 
                     data={'is_primary': True}, 
                     filters={'id': image_id})
            
            # Update the main product table
            image = db.select_one('product_images', filters={'id': image_id})
            
            if image:
                db.update(cls.TABLE_NAME, 
                         data={'image_url': image['image_url']}, 
                         filters={'id': product_id})
            
            return True
        except Exception as e:
            print(f"Error setting primary image: {e}")
            return False
