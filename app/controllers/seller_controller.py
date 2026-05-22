# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
import json
from app.utils.decorators import login_required, seller_required
from app.models.user import User
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.product_bundle import ProductBundle
from app.models.order import Order
# FIXED: Import socketio from app directly
from app import socketio  # ← Use this instead of from app.services.websocket_service
from app.models.seller_request import SellerRequest
from app.services.database import Database
from app.forms import SellerProductForm, OrderStatusForm, SellerApplicationForm
from app.models.delivery import Delivery
from app.models.rider_availability import RiderAvailability
from app.models.notification import Notification
from datetime import datetime, timedelta
import traceback

seller_bp = Blueprint('seller', __name__)


@seller_bp.route('/dashboard')
@login_required
@seller_required
def dashboard():
    seller_id = session['user_id']
    seller = User.get_by_id(seller_id)
    db = Database()
    
    # --- Product stats ---
    all_products = db.client.table('products').select('id, status, stock_quantity').eq('seller_id', seller_id).execute()
    all_products = all_products.data or []
    product_stats = {
        'total_products': len(all_products),
        'active_products': sum(1 for p in all_products if p.get('status') == 'active'),
        'out_of_stock': sum(1 for p in all_products if int(p.get('stock_quantity', 0)) == 0),
    }
    
    # --- Order stats ---
    seller_orders = db.client.table('orders').select('*').eq('seller_id', seller_id).execute()
    seller_orders = seller_orders.data or []
    total_revenue = sum(float(o.get('total_amount', 0)) for o in seller_orders if o.get('status') != 'cancelled')
    order_stats = {
        'total_orders': len(seller_orders),
        'total_revenue': total_revenue,
        'pending_orders': sum(1 for o in seller_orders if o.get('status') == 'pending'),
        'processing_orders': sum(1 for o in seller_orders if o.get('status') == 'processing'),
        'delivered_orders': sum(1 for o in seller_orders if o.get('status') == 'delivered'),
        'completed_orders': sum(1 for o in seller_orders if o.get('status') == 'completed'),
    }
    
    # --- Recent orders ---
    recent_orders = Order.list_for_seller(seller_id, limit=10)
    for order in recent_orders:
        items = order.get('items', [])
        order['items_count'] = len(items)
        uid = order.get('user_id')
        if uid:
            profile = db.select_one('profiles', filters={'id': uid})
            order['customer_name'] = f"{profile.get('first_name') or ''} {profile.get('last_name') or ''}".strip() if profile else 'Unknown'
        else:
            order['customer_name'] = 'Unknown'
    
    # --- Top selling products ---
    product_sales = {}
    for o in seller_orders:
        oid = o.get('id')
        if not oid:
            continue
        oitems = db.select('order_items', filters={'order_id': oid})
        for oi in oitems:
            pid = oi.get('product_id')
            if pid is None:
                continue
            qty = int(oi.get('quantity', 0))
            if pid not in product_sales:
                product_sales[pid] = {'total_sold': 0, 'revenue': 0.0}
            product_sales[pid]['total_sold'] += qty
            product_sales[pid]['revenue'] += float(oi.get('unit_price', 0)) * qty
    
    # Fetch product details for top sold products
    all_seller_products = db.client.table('products').select('id, name, price, image_url').eq('seller_id', seller_id).execute()
    all_seller_products = all_seller_products.data or []
    product_map = {p['id']: p for p in all_seller_products}
    top_products = []
    for pid, sales in sorted(product_sales.items(), key=lambda x: x[1]['total_sold'], reverse=True)[:5]:
        p = product_map.get(pid, {})
        top_products.append({
            'id': pid,
            'name': p.get('name', 'Unknown'),
            'price': float(p.get('price', 0)),
            'image_url': p.get('image_url'),
            'total_sold': sales['total_sold'],
            'total_revenue': round(sales['revenue'], 2)
        })
    
    # --- Revenue trends (last 12 months) ---
    now = datetime.now()
    month_keys = []
    for i in range(11, -1, -1):
        m = now.month - i
        y = now.year
        while m < 1:
            m += 12
            y -= 1
        month_keys.append(f"{y:04d}-{m:02d}")
    totals = {k: 0.0 for k in month_keys}
    for o in seller_orders:
        if o.get('status') == 'cancelled':
            continue
        created = o.get('created_at')
        if isinstance(created, str):
            try:
                created = datetime.fromisoformat(created.replace('Z', '+00:00'))
            except:
                continue
        key = created.strftime('%Y-%m')
        if key in totals:
            totals[key] += float(o.get('total_amount', 0))
    sales_labels = [datetime.strptime(k, '%Y-%m').strftime('%b %Y') for k in month_keys]
    sales_amounts = [round(totals[k], 2) for k in month_keys]
    
    # --- Order status breakdown ---
    status_counts = {}
    for o in seller_orders:
        s = o.get('status', 'Unknown')
        status_counts[s] = status_counts.get(s, 0) + 1
    order_status_breakdown = [{'status': k, 'count': v} for k, v in status_counts.items()] or [{'status': 'No data', 'count': 1}]
    
    # --- Top customers ---
    customer_data = {}
    for o in seller_orders:
        uid = o.get('user_id')
        if not uid:
            continue
        if uid not in customer_data:
            customer_data[uid] = {'total_spent': 0.0, 'order_count': 0}
        customer_data[uid]['order_count'] += 1
        customer_data[uid]['total_spent'] += float(o.get('total_amount', 0))
    top_customers = []
    for uid, cd in sorted(customer_data.items(), key=lambda x: x[1]['total_spent'], reverse=True)[:5]:
        profile = db.select_one('profiles', filters={'id': uid})
        top_customers.append({
            'id': uid,
            'first_name': profile.get('first_name', '') if profile else '',
            'last_name': profile.get('last_name', '') if profile else '',
            'email': profile.get('email', '') if profile else '',
            'order_count': cd['order_count'],
            'total_spent': round(cd['total_spent'], 2)
        })
    
    # --- Financial overview ---
    commission_rate = float(current_app.config.get('SELLER_COMMISSION_RATE', 0.05))
    commission_due = round(total_revenue * commission_rate, 2)
    net_revenue = round(total_revenue - commission_due, 2)
    financial_overview = {
        'gross_revenue': total_revenue,
        'commission_rate': commission_rate * 100,
        'commission_due': commission_due,
        'net_revenue': net_revenue,
        'pending_orders': order_stats['pending_orders'],
        'delivered_orders': order_stats['delivered_orders']
    }
    
    return render_template('seller/dashboard.html', 
                         seller=seller,
                         product_stats=product_stats,
                         order_stats=order_stats,
                         orders=recent_orders,
                         top_products=top_products,
                         top_customers=top_customers,
                         sales_labels=sales_labels,
                         sales_amounts=sales_amounts,
                         order_status_breakdown=order_status_breakdown,
                         financial_overview=financial_overview)

@seller_bp.route('/products')
@login_required
@seller_required
def products():
    seller_id = session['user_id']
    # Support status filter including draft
    status_filter = request.args.get('status')
    category_filter = request.args.get('category')
    
    products = Product.list(
        seller_id=seller_id, 
        status=status_filter if status_filter else None,
        category_id=category_filter if category_filter else None
    )
    
    # Attach variants to each product
    for product in products:
        product['variants'] = ProductVariant.get_by_product(product['id'], status=None)
    
    db = Database()
    try:
        cat_result = db.client.table('categories').select('*').eq('status', 'active').execute()
        categories = cat_result.data or []
    except Exception:
        categories = []
    
    return render_template('seller/products.html', 
                         products=products, 
                         categories=categories,
                         selected_status=status_filter,
                         selected_category=category_filter)

@seller_bp.route('/products/add', methods=['POST'])
@login_required
@seller_required
def add_product():
    seller_id = session['user_id']

    # Get categories to populate form choices
    db = Database()
    try:
        cat_result = db.client.table('categories').select('id, name').eq('status', 'active').execute()
        categories = cat_result.data or []
    except Exception:
        categories = []

    # Handle multiple image uploads (not using form for images)
    images = request.files.getlist('images')
    
    # Validate minimum 3 images
    if len(images) < 3:
        flash('Please upload at least 3 images for your product.', 'error')
        return redirect(url_for('seller.products'))
    
    # Validate other form fields
    name = request.form.get('name', '').strip()
    category_id = request.form.get('category_id')
    description = request.form.get('description', '').strip()
    price = request.form.get('price')
    stock_quantity = request.form.get('stock_quantity')
    
    if not name or not category_id or not price or not stock_quantity:
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('seller.products'))
    
    try:
        from werkzeug.utils import secure_filename
        import os
        from flask import current_app
        from PIL import Image
        import uuid
        
        # Process all images
        image_urls = []
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'products')
        os.makedirs(upload_dir, exist_ok=True)
        
        for img_file in images:
            if img_file and img_file.filename:
                filename = secure_filename(img_file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                upload_path = os.path.join(upload_dir, unique_filename)
                
                try:
                    # Open and process image
                    image = Image.open(img_file)
                    
                    # Convert to RGB if necessary (for JPEG compatibility)
                    if image.mode in ("RGBA", "P"):
                        image = image.convert("RGB")
                    
                    # Save with optimization
                    if filename.lower().endswith(('.jpg', '.jpeg')):
                        image.save(upload_path, 'JPEG', optimize=True, quality=85)
                    elif filename.lower().endswith('.png'):
                        image.save(upload_path, 'PNG', optimize=True)
                    else:
                        # For other formats, convert to JPEG
                        new_filename = unique_filename.rsplit('.', 1)[0] + '.jpg'
                        upload_path = os.path.join(upload_dir, new_filename)
                        unique_filename = new_filename
                        image.save(upload_path, 'JPEG', optimize=True, quality=85)
                    
                    image_urls.append(f"/static/uploads/products/{unique_filename}")
                except Exception as img_error:
                    print(f"Image processing error: {img_error}")
                    flash(f'Failed to process image {filename}. Please try different images.', 'error')
                    return redirect(url_for('seller.products'))
        
        # Ensure we have at least 3 valid images
        if len(image_urls) < 3:
            flash('Failed to process enough images. Please upload at least 3 valid images.', 'error')
            return redirect(url_for('seller.products'))
        
        # Get image order from form if provided
        image_order_json = request.form.get('image_order', '[]')
        try:
            image_order = json.loads(image_order_json) if image_order_json else list(range(len(image_urls)))
        except:
            image_order = list(range(len(image_urls)))
        
        # Create product with first image as primary
        product = Product.create(
            seller_id=seller_id,
            category_id=int(category_id),
            name=name,
            description=description if description else None,
            price=float(price),
            stock_quantity=int(stock_quantity),
            image_url=image_urls[0],
            image_urls=image_urls
        )
        
        # Update display_order if custom order was provided
        if product and image_order and image_order != list(range(len(image_urls))):
            product_id = product.get('id') if isinstance(product, dict) else product.id
            # Get the images that were just created
            images = Product.get_images(product_id)
            if images and len(images) > 0:
                # Create mapping of image URLs to their IDs
                image_id_map = {img['image_url']: img['id'] for img in images}
                # Build order list using IDs
                image_id_order = []
                for idx, order_pos in enumerate(image_order):
                    if idx < len(image_urls):
                        image_id = image_id_map.get(image_urls[idx])
                        if image_id:
                            image_id_order.append({'id': image_id, 'position': order_pos})
                # Update display order
                if image_id_order:
                    Product.update_image_display_order(product_id, image_id_order)
        
        flash('Product created successfully with multiple images!', 'success')
    except Exception as e:
        print(f"Product creation error: {e}")
        import traceback
        traceback.print_exc()
        flash('Failed to create product. Please try again.', 'error')

    return redirect(url_for('seller.products'))

@seller_bp.route('/products/<int:product_id>/edit', methods=['POST'])
@login_required
@seller_required
def edit_product(product_id):
    seller_id = session['user_id']
    product = Product.get_by_id(product_id)
    if not product or product['seller_id'] != seller_id:
        flash('Product not found or unauthorized.', 'error')
        return redirect(url_for('seller.products'))

    # Get form data
    name = request.form.get('name', '').strip()
    category_id = request.form.get('category_id')
    description = request.form.get('description', '').strip()
    price = request.form.get('price')
    stock_quantity = request.form.get('stock_quantity')
    status = request.form.get('status', 'active')
    
    # Handle new image uploads
    new_images = request.files.getlist('images')
    image_order_json = request.form.get('image_order', '[]')
    
    # Parse image order
    try:
        image_order = json.loads(image_order_json) if image_order_json else []
    except:
        image_order = []
    
    # DETAILED LOGGING
    print(f"\n{'='*50}")
    print(f"EDIT PRODUCT POST REQUEST - Product ID: {product_id}")
    print(f"  image_order_json from form: {repr(image_order_json)}")
    print(f"  image_order parsed: {image_order}")
    print(f"  image_order type: {type(image_order)}")
    print(f"  image_order length: {len(image_order) if image_order else 0}")
    print(f"  new_images count: {len(new_images)}")
    print(f"  new_images with filenames: {sum(1 for img in new_images if img.filename)}")
    print(f"{'='*50}\n")
    
    try:
        # If new images are uploaded, validate minimum 3
        if new_images and any(img.filename for img in new_images):
            valid_images = [img for img in new_images if img and img.filename]
            
            if len(valid_images) < 3:
                flash('Please upload at least 3 images when updating product images.', 'error')
                return redirect(url_for('seller.products'))
            
            from werkzeug.utils import secure_filename
            import os
            from flask import current_app
            from PIL import Image
            import uuid
            
            # Process new images
            image_urls = []
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'products')
            os.makedirs(upload_dir, exist_ok=True)
            
            for img_file in valid_images:
                filename = secure_filename(img_file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                upload_path = os.path.join(upload_dir, unique_filename)
                
                try:
                    image = Image.open(img_file)
                    if image.mode in ("RGBA", "P"):
                        image = image.convert("RGB")
                    
                    if filename.lower().endswith(('.jpg', '.jpeg')):
                        image.save(upload_path, 'JPEG', optimize=True, quality=85)
                    elif filename.lower().endswith('.png'):
                        image.save(upload_path, 'PNG', optimize=True)
                    else:
                        new_filename = unique_filename.rsplit('.', 1)[0] + '.jpg'
                        upload_path = os.path.join(upload_dir, new_filename)
                        unique_filename = new_filename
                        image.save(upload_path, 'JPEG', optimize=True, quality=85)
                    
                    image_urls.append(f"/static/uploads/products/{unique_filename}")
                except Exception as img_error:
                    print(f"Image processing error for {filename}: {img_error}")
                    import traceback
                    traceback.print_exc()
            
            # Check if we successfully processed enough images
            if len(image_urls) < 3:
                flash(f'Failed to process enough images. Only {len(image_urls)} of {len(valid_images)} images were successfully processed. Please try different images.', 'error')
                return redirect(url_for('seller.products'))
            
            # Delete old images and add new ones
            Product.delete_all_images(product_id)
            Product.add_images(product_id, image_urls)
            
            # Update display_order if custom order was provided
            if image_order and image_order != list(range(len(image_urls))):
                images = Product.get_images(product_id)
                if images and len(images) > 0:
                    image_id_map = {img['image_url']: img['id'] for img in images}
                    image_id_order = []
                    for idx, order_pos in enumerate(image_order):
                        if idx < len(image_urls):
                            image_id = image_id_map.get(image_urls[idx])
                            if image_id:
                                image_id_order.append({'id': image_id, 'position': order_pos})
                    if image_id_order:
                        Product.update_image_display_order(product_id, image_id_order)
        else:
            # No new images uploaded - check if existing images need reordering
            print(f"  No new images uploaded")
            print(f"  Checking if image_order needs processing: {image_order}")
            if image_order and len(image_order) > 0:
                print(f"  ✓ Updating image order for product {product_id}: {image_order}")
                Product.update_image_display_order(product_id, image_order)
                print(f"  ✓ Product.update_image_display_order() call completed")
            else:
                print(f"  ✗ image_order is empty or None - no reordering needed")

        
        # Update product details
        Product.update(product_id,
                      name=name,
                      category_id=int(category_id),
                      description=description if description else None,
                      price=float(price),
                      stock_quantity=int(stock_quantity),
                      status=status)
        
        flash('Product updated successfully!', 'success')
    except Exception as e:
        print(f"Product update error: {e}")
        import traceback
        traceback.print_exc()
        flash('Failed to update product.', 'error')

    return redirect(url_for('seller.products'))

@seller_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@login_required
@seller_required
def delete_product(product_id):
    seller_id = session['user_id']
    product = Product.get_by_id(product_id)
    if not product or product['seller_id'] != seller_id:
        flash('Product not found or unauthorized.', 'error')
        return redirect(url_for('seller.products'))
    try:
        Product.delete(product_id)
        flash('Product deleted.', 'info')
    except Exception as e:
        # If hard delete fails due to FK constraints (product in orders), soft-delete
        try:
            Product.update(product_id, status='inactive')
            flash('Product archived (inactive) because it has existing orders.', 'warning')
        except Exception:
            flash('Failed to delete product.', 'error')
    return redirect(url_for('seller.products'))

@seller_bp.route('/products/<int:product_id>/variants', methods=['GET'])
@login_required
@seller_required
def product_variants(product_id):
    """Manage variants for a product"""
    seller_id = session['user_id']
    product = Product.get_by_id(product_id)
    
    if not product or product['seller_id'] != seller_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    variants = ProductVariant.get_by_product(product_id, status=None)
    return jsonify(variants)

@seller_bp.route('/products/<int:product_id>/variants/add', methods=['POST'])
@login_required
@seller_required
def add_variant(product_id):
    """Add a variant to a product"""
    seller_id = session['user_id']
    product = Product.get_by_id(product_id)
    
    if not product or product['seller_id'] != seller_id:
        flash('Product not found or unauthorized.', 'error')
        return redirect(url_for('seller.products'))
    
    try:
        import json
        
        name = request.form.get('variant_name')
        sku = request.form.get('variant_sku') or None
        price = float(request.form.get('variant_price'))
        sale_price = float(request.form.get('variant_sale_price')) if request.form.get('variant_sale_price') else None
        stock = int(request.form.get('variant_stock', 0))
        
        # Parse attributes (e.g., color, size)
        attributes = {}
        if request.form.get('variant_color'):
            attributes['color'] = request.form.get('variant_color')
        if request.form.get('variant_size'):
            attributes['size'] = request.form.get('variant_size')
        
        ProductVariant.create(
            product_id=product_id,
            name=name,
            sku=sku,
            price=price,
            sale_price=sale_price,
            stock_quantity=stock,
            attributes=attributes
        )
        flash('Variant added successfully!', 'success')
    except Exception as e:
        flash(f'Failed to add variant: {str(e)}', 'error')
    
    return redirect(url_for('seller.products'))

@seller_bp.route('/bundles')
@login_required
@seller_required
def bundles():
    """Manage product bundles"""
    seller_id = session['user_id']
    bundles = ProductBundle.get_by_seller(seller_id, status=None)
    products = Product.list(seller_id=seller_id, status='active')
    
    return render_template('seller/bundles.html', bundles=bundles, products=products)

@seller_bp.route('/bundles/add', methods=['POST'])
@login_required
@seller_required
def add_bundle():
    """Create a new bundle"""
    seller_id = session['user_id']
    
    try:
        import json
        
        name = request.form.get('bundle_name')
        description = request.form.get('bundle_description')
        bundle_price = float(request.form.get('bundle_price'))
        discount = float(request.form.get('discount_percentage')) if request.form.get('discount_percentage') else None
        
        # Parse items JSON
        items_json = request.form.get('bundle_items', '[]')
        items = json.loads(items_json) if items_json else []
        
        ProductBundle.create(
            seller_id=seller_id,
            name=name,
            description=description,
            bundle_price=bundle_price,
            discount_percentage=discount,
            items=items
        )
        flash('Bundle created successfully!', 'success')
    except Exception as e:
        flash(f'Failed to create bundle: {str(e)}', 'error')
    
    return redirect(url_for('seller.bundles'))

@seller_bp.route('/bundles/<int:bundle_id>/delete', methods=['POST'])
@login_required
@seller_required
def delete_bundle(bundle_id):
    """Delete a bundle"""
    seller_id = session['user_id']
    bundle = ProductBundle.get_by_id(bundle_id)
    
    if not bundle or bundle['seller_id'] != seller_id:
        flash('Bundle not found or unauthorized.', 'error')
        return redirect(url_for('seller.bundles'))
    
    try:
        ProductBundle.delete(bundle_id)
        flash('Bundle deleted successfully.', 'success')
    except Exception as e:
        flash(f'Failed to delete bundle: {str(e)}', 'error')
    
    return redirect(url_for('seller.bundles'))

@seller_bp.route('/orders')
@login_required
@seller_required
def orders():
    seller_id = session['user_id']
    status_param = (request.args.get('status') or '').strip()
    status = status_param if status_param not in ('', 'all') else None
    search_query = request.args.get('search', '').strip()
    
    # Get orders with additional details
    orders = Order.list_for_seller(seller_id, status=status, search=search_query or None)
    
    # Add rider info and delivery status to orders
    db = Database()
    for order in orders:
        # Get delivery info if exists
        delivery = db.execute_query(
            """
            SELECT d.*, 
                   u.first_name as rider_first_name, 
                   u.last_name as rider_last_name,
                   u.phone as rider_phone
            FROM deliveries d
            LEFT JOIN users u ON d.rider_id = u.id
            WHERE d.order_id = %s
            """,
            (order['id'],),
            fetch=True,
            fetchone=True
        )
        
        if delivery:
            order['rider_id'] = delivery['rider_id']
            order['rider_name'] = f"{delivery.get('rider_first_name', '')} {delivery.get('rider_last_name', '')}".strip() or 'Unknown Rider'
            order['rider_phone'] = delivery.get('rider_phone', '')
            order['delivery_status'] = delivery.get('status', 'pending')
            order['assigned_at'] = delivery.get('assigned_at')
            order['picked_up_at'] = delivery.get('picked_up_at')
            order['delivered_at'] = delivery.get('delivered_at')
        else:
            order['rider_name'] = None
            order['rider_phone'] = None
            order['delivery_status'] = None
            
        # Add order items count
        order['item_count'] = len(order.get('items', []))
    
    # Get available statuses for the status filter
    statuses_query = db.execute_query(
        """
        SELECT DISTINCT o.status 
        FROM orders o
        INNER JOIN order_items oi ON o.id = oi.order_id
        WHERE oi.seller_id = %s 
        ORDER BY o.status
        """,
        (seller_id,),
        fetch=True
    )
    status_choices = sorted({row['status'] for row in statuses_query if row.get('status')})
    
    return render_template('seller/orders.html', 
                         orders=orders, 
                         status=status_param,
                         statuses=status_choices,
                         search_query=search_query)

@seller_bp.route('/orders/count')
@login_required
@seller_required
def get_orders_count():
    """Get count of pending orders for the seller (API endpoint)"""
    seller_id = session['user_id']
    
    db = Database()
    try:
        # Get order IDs where this seller has items
        items = db.client.table('order_items').select('order_id').eq('seller_id', seller_id).execute()
        order_ids = list(set(int(i['order_id']) for i in (items.data or []) if i.get('order_id')))
        if not order_ids:
            return jsonify({'success': True, 'count': 0})
        # Count distinct pending orders
        result = db.client.table('orders').select('id', count='exact').in_('id', order_ids).eq('status', 'pending').execute()
        count = result.count if hasattr(result, 'count') else 0
    except Exception:
        count = 0
    
    return jsonify({
        'success': True,
        'count': int(count)
    })

@seller_bp.route('/available-riders')
@seller_required
@login_required
def get_available_riders():
    """Get list of available riders for order assignment"""
    try:
        # Get available riders using the RiderAvailability model
        available_riders = RiderAvailability.get_available_riders()
        
        # Format the response
        riders_list = []
        for rider in available_riders:
            riders_list.append({
                'id': rider['id'],
                'name': f"{rider.get('first_name', '')} {rider.get('last_name', '')}".strip(),
                'phone': rider.get('phone', ''),
                'current_lat': rider.get('current_lat'),
                'current_lng': rider.get('current_lng'),
                'is_available': True,  # Since we're getting available riders
                'current_deliveries': 0  # You might want to add this to your query if needed
            })
            
        return jsonify(riders_list)
        
    except Exception as e:
        current_app.logger.error(f"Error getting available riders: {e}")
        return jsonify({'error': 'Failed to fetch available riders'}), 500

@seller_bp.route('/assign-rider', methods=['POST'])
@login_required
@seller_required
def assign_rider():
    order_id = request.form.get('order_id')
    rider_id = request.form.get('rider_id')
    delivery_notes = request.form.get('delivery_notes', '')
    
    if not order_id or not rider_id:
        flash('Missing required parameters.', 'error')
        return redirect(url_for('seller.orders'))
        
    try:
        # Check if order exists and belongs to seller
        order = Order.get_by_id(order_id)
        if not order or order['seller_id'] != session['user_id']:
            flash('Order not found or unauthorized.', 'error')
            return redirect(url_for('seller.orders'))

        # Allow re-assignment if rider is already assigned
        if Delivery.assign_rider(order_id, rider_id, delivery_notes):
            # Get rider details for notification
            rider = User.get_by_id(rider_id)
            rider_name = f"{rider['first_name']} {rider['last_name']}" if rider else 'a rider'
            
            if order.get('rider_id'):
                flash(f'Rider changed to {rider_name} successfully. The rider has been notified.', 'success')
            else:
                flash(f'Rider {rider_name} assigned successfully. The rider has been notified.', 'success')
                
            # Update order status directly to picked_up (first-come-first-serve model)
            if order.get('status') in ['ready_for_delivery', 'shipped', 'confirmed']:
                Order.update_status(order_id, 'picked_up', rider_id=rider_id)
        else:
            flash('Failed to assign rider. Please try again.', 'error')
            
    except Exception as e:
        current_app.logger.error(f"Error in assign_rider: {e}")
        flash('An error occurred while assigning the rider. Please try again.', 'error')
    
    return redirect(url_for('seller.orders'))

# Add this to your seller_controller.py in the update_order_status function
# Replace the 'confirmed' status handling section

@seller_bp.route('/orders/<int:order_id>/details')
@login_required
@seller_required
def get_order_details(order_id):
    """API endpoint to get order details for dashboard modal"""
    seller_id = session['user_id']
    
    try:
        db = Database()
        
        # Verify seller has items in this order before fetching details
        seller_has_items = db.execute_query("""
            SELECT COUNT(*) as count FROM order_items 
            WHERE order_id = %s AND seller_id = %s
        """, (order_id, seller_id), fetch=True, fetchone=True)
        
        if not seller_has_items or seller_has_items['count'] == 0:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Get order with items
        order = Order.get_by_id(order_id)
        
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        customer = db.execute_query("""
            SELECT email, phone
            FROM users
            WHERE id = %s
        """, (order['user_id'],), fetch=True, fetchone=True)

        # Filter order items to only show items from this seller
        filtered_items = [item for item in order.get('items', []) if item.get('seller_id') == seller_id]

        order_context = dict(order)
        order_context['customer_name'] = f"{order.get('customer_first_name', '')} {order.get('customer_last_name', '')}".strip() or 'N/A'
        order_context['customer_email'] = customer.get('email') if customer else order.get('customer_email')
        order_context['customer_phone'] = customer.get('phone') if customer else order.get('customer_phone')
        order_context['items'] = filtered_items
        order_context['items_count'] = len(filtered_items)
        html = render_template(
            'seller/order_detail_modal.html',
            order=order_context
        )
        return jsonify({'success': True, 'html': html})
        
    except Exception as e:
        current_app.logger.error(f"Error fetching order details: {e}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': 'Failed to load order details'}), 500

@seller_bp.route('/orders/<int:order_id>/pod', methods=['GET'])
@login_required
@seller_required
def view_order_pod(order_id):
    """View Proof of Delivery (POD) for a delivered order"""
    seller_id = session['user_id']
    
    try:
        db = Database()
        
        # Verify seller has items in this order before fetching POD
        seller_has_items = db.execute_query("""
            SELECT COUNT(*) as count FROM order_items 
            WHERE order_id = %s AND seller_id = %s
        """, (order_id, seller_id), fetch=True, fetchone=True)
        
        if not seller_has_items or seller_has_items['count'] == 0:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Get order and verify it exists
        order = Order.get_by_id(order_id)
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        # Check if order is delivered
        if order.get('status') != 'delivered':
            return jsonify({'success': False, 'error': 'POD is only available for delivered orders'}), 400
        
        # Get delivery information with POD
        delivery = db.execute_query("""
            SELECT d.*, 
                   CONCAT(r.first_name, ' ', r.last_name) as rider_name,
                   r.phone as rider_phone
            FROM deliveries d
            LEFT JOIN users r ON d.rider_id = r.id
            WHERE d.order_id = %s
            ORDER BY d.delivered_at DESC
            LIMIT 1
        """, (order_id,), fetch=True, fetchone=True)
        
        if not delivery:
            return jsonify({'success': False, 'error': 'Delivery information not found'}), 404
        
        # Format POD data
        pod_data = {
            'delivery_id': delivery.get('id'),
            'rider_name': delivery.get('rider_name', 'N/A'),
            'rider_phone': delivery.get('rider_phone', 'N/A'),
            'recipient_name': delivery.get('recipient_name', 'N/A'),
            'delivered_at': delivery.get('delivered_at').strftime('%B %d, %Y at %I:%M %p') if delivery.get('delivered_at') else 'N/A',
            'delivered_lat': delivery.get('delivered_lat'),
            'delivered_lng': delivery.get('delivered_lng'),
            'cod_collected': float(delivery.get('cod_collected', 0)) if delivery.get('cod_collected') else None,
            'delivery_notes': delivery.get('delivery_notes', ''),
            'proof_photo_url': f"/static/{delivery.get('proof_photo_url')}" if delivery.get('proof_photo_url') else None,
            'signature_url': f"/static/{delivery.get('signature_url')}" if delivery.get('signature_url') else None,
            'pod_submitted_at': delivery.get('pod_submitted_at').strftime('%B %d, %Y at %I:%M %p') if delivery.get('pod_submitted_at') else None
        }
        
        # Build HTML for POD display
        html = render_template('seller/pod_view.html', pod=pod_data, order=order)
        
        return jsonify({'success': True, 'html': html, 'pod': pod_data})
        
    except Exception as e:
        current_app.logger.error(f"Error fetching POD: {e}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': 'Failed to load POD information'}), 500

@seller_bp.route('/orders/update-status', methods=['POST'])
@login_required
@seller_required
def update_order_status():
    order_id = request.form.get('order_id')
    status = request.form.get('status')
    seller_id = session['user_id']
    current_app.logger.info(f"Attempting to update order {order_id} status to {status}")
    
    try:
        # Fetch order to get customer info for notification
        order = Order.get_by_id(order_id)
        if not order:
            current_app.logger.error(f"Order {order_id} not found")
            flash('Order not found.', 'error')
            return redirect(url_for('seller.orders'))
        
        # Check if this seller has items in this order
        db = Database()
        seller_items = db.execute_query(
            """
            SELECT COUNT(*) as count FROM order_items 
            WHERE order_id = %s AND seller_id = %s
            """,
            (order_id, seller_id),
            fetch=True,
            fetchone=True
        )
        
        has_items = seller_items and seller_items.get('count', 0) > 0
        
        current_app.logger.info(f"Order {order_id}: Current seller_id: {seller_id}, Has items in order: {has_items}")
        
        if not has_items:
            current_app.logger.warning(f"Unauthorized access attempt to order {order_id} by seller {seller_id}")
            flash('You are not authorized to update this order.', 'error')
            return redirect(url_for('seller.orders'))

        # Log the status update
        current_app.logger.info(f"Updating order {order_id} from {order.get('status')} to {status}")
        
        # Handle different status updates
        if status == 'confirmed':
            success = Order.update_status(order_id, 'confirmed')
            if success:
                # Notify customer (user)
                try:
                    Notification.create(order['user_id'], 'user', 'order_status', 'Order confirmed', f"Your order #{order_id} is confirmed.", related_id=order_id, data={'order_id': int(order_id), 'status': 'confirmed'})
                    current_app.socketio.emit('notification', {'title': 'Order confirmed', 'message': f'Your order #{order_id} is confirmed.', 'type': 'order_status', 'data': {'order_id': int(order_id), 'status': 'confirmed'}}, room=f"user_{order['user_id']}")
                    current_app.socketio.emit('order_status_updated', {'order_id': int(order_id), 'status': 'confirmed'}, room=f"user_{order['user_id']}")
                except Exception:
                    pass
                # Get order details for rider broadcast
                order_details = {
                    'id': order_id,
                    'order_id': order_id,
                    'order_number': order.get('order_number', f"ORD-{str(order_id).zfill(5)}"),
                    'total_amount': float(order.get('total_amount', 0)),
                    'item_count': len(order.get('items', [])),
                    'created_at': order.get('created_at').strftime('%Y-%m-%d %H:%M:%S') if hasattr(order.get('created_at'), 'strftime') else str(order.get('created_at', '')),
                    'shipping_address': order.get('shipping_address', ''),
                    'status': 'confirmed',
                    'seller_id': order['seller_id'],
                    'customer_name': f"{order.get('customer_first_name', '')} {order.get('customer_last_name', '')}".strip() or 'Customer',
                    'customer_phone': order.get('customer_phone', ''),
                    'payment_method': order.get('payment_method', 'COD'),
                    'payment_status': order.get('payment_status', 'pending')
                }
                
                try:
                    # Use socketio imported at the top of the file
                    current_app.logger.info(f"🔔 Emitting WebSocket events for order {order_id}")
                    
                    # Event 1: Legacy event for riders_room
                    current_app.socketio.emit('new_order_confirmed', 
                                {'order': order_details},
                                room='riders_room')
                    current_app.logger.info(f"✓ Emitted new_order_confirmed to riders_room")
                    
                    # Event 2: New event for available_orders room
                    current_app.socketio.emit('new_available_order',
                                  {'order': order_details},
                                  room='available_orders')
                    current_app.logger.info(f"✓ Emitted new_available_order to available_orders")
                    
                    # Event 3: Broadcast as fallback
                    current_app.socketio.emit('new_delivery_opportunity', 
                                  {'order': order_details}, 
                                  broadcast=True)
                    # Also push a notification to riders room
                    current_app.socketio.emit('notification', {'title': 'New order available', 'message': f'Order #{order_id} is available for delivery.', 'type': 'rider_notice', 'data': {'order_id': int(order_id)}}, room='riders')
                    current_app.logger.info(f"✓ Broadcasted new_delivery_opportunity")
                    
                    current_app.logger.info(f"✅ Successfully notified riders about order {order_id}")
                except Exception as e:
                    current_app.logger.error(f"❌ Error notifying riders: {str(e)}\n{traceback.format_exc()}")
                
                flash('Order confirmed and riders have been notified.', 'success')
            else:
                current_app.logger.error(f"Failed to update order {order_id} status to {status}")
                flash('Failed to update order status. Please try again.', 'error')
                
        elif status == 'ready_for_delivery':
            success = Order.update_status(order_id, 'ready_for_delivery')
            if success:
                # Get order details for notification
                order_details = {
                    'id': order_id,
                    'order_id': order_id,
                    'order_number': order.get('order_number', f"ORD-{str(order_id).zfill(5)}"),
                    'total_amount': float(order.get('total_amount', 0)),
                    'item_count': len(order.get('items', [])),
                    'created_at': order.get('created_at').strftime('%Y-%m-%d %H:%M:%S') if hasattr(order.get('created_at'), 'strftime') else str(order.get('created_at', '')),
                    'shipping_address': order.get('shipping_address', ''),
                    'status': 'ready_for_delivery',
                    'seller_id': order['seller_id']
                }
                
                try:
                    # Use socketio imported at the top of the file
                    current_app.logger.info(f"🔔 Notifying riders about order {order_id} ready for delivery")
                    
                    # Notify riders about ready for delivery order
                    current_app.socketio.emit('new_available_order', {'order': order_details}, room='available_orders')
                    current_app.socketio.emit('new_delivery_available', {'order': order_details}, broadcast=True)
                    
                    current_app.logger.info(f"✅ Notified riders about order {order_id} ready for delivery")
                    flash('Order marked as ready for delivery. Available riders have been notified.', 'success')
                except Exception as e:
                    current_app.logger.error(f"❌ Error notifying riders: {str(e)}\n{traceback.format_exc()}")
                    flash('Order status updated, but there was an error notifying riders.', 'warning')
            else:
                current_app.logger.error(f"Failed to update order {order_id} status to {status}")
                flash('Failed to update order status. Please try again.', 'error')
                
        elif status == 'preparing':
            success = Order.update_status(order_id, 'preparing')
            if success:
                try:
                    Notification.create(order['user_id'], 'user', 'order_status', 'Order preparing', f"Your order #{order_id} is preparing.", related_id=order_id, data={'order_id': int(order_id), 'status': 'preparing'})
                    current_app.socketio.emit('notification', {'title': 'Order preparing', 'message': f'Your order #{order_id} is preparing.', 'type': 'order_status', 'data': {'order_id': int(order_id), 'status': 'preparing'}}, room=f"user_{order['user_id']}")
                    current_app.socketio.emit('order_status_updated', {'order_id': int(order_id), 'status': 'preparing'}, room=f"user_{order['user_id']}")
                    flash('Order marked as preparing.', 'success')
                except Exception:
                    flash('Order updated to preparing.', 'success')
            else:
                flash('Failed to update order status.', 'error')

        elif status == 'cancelled':
            # Require reason and notify user
            reason = request.form.get('reason') or request.form.get('cancel_reason')
            if not reason:
                flash('Reason is required to cancel an order.', 'error')
                return redirect(url_for('seller.orders'))
            if Order.update_status(order_id, 'cancelled'):
                try:
                    Notification.create(order['user_id'], 'user', 'order_status', 'Order cancelled', f"Your order #{order_id} was cancelled. Reason: {reason}", related_id=order_id, data={'order_id': int(order_id), 'status': 'cancelled', 'reason': reason})
                    socketio.emit('notification', {'title': 'Order cancelled', 'message': f'Your order #{order_id} was cancelled. Reason: {reason}', 'type': 'order_status', 'data': {'order_id': int(order_id), 'status': 'cancelled'}}, room=f"user_{order['user_id']}")
                    socketio.emit('order_status_updated', {'order_id': int(order_id), 'status': 'cancelled'}, room=f"user_{order['user_id']}")
                except Exception:
                    pass
                flash('Order cancelled.', 'success')
            else:
                flash('Failed to cancel order.', 'error')

        elif status == 'shipped':
            # If order doesn't have a rider assigned yet, try to auto-assign one
            if not order.get('rider_id'):
                try:
                    all_riders = Delivery.get_all_riders_with_availability()
                    available_riders = [r for r in all_riders if r['current_deliveries'] < 5]
                    
                    if available_riders:
                        first_rider = available_riders[0]
                        if Delivery.create(order_id, first_rider['id'], 'Auto-assigned on ship'):
                            current_app.logger.info(f"Auto-assigned rider {first_rider['id']} to order {order_id}")
                            flash('Order status updated, rider auto-assigned, and customer notified.', 'success')
                        else:
                            current_app.logger.warning(f"Failed to auto-assign rider to order {order_id}")
                            flash('Order status updated but failed to auto-assign rider.', 'warning')
                    else:
                        current_app.logger.warning(f"No available riders for order {order_id}")
                        flash('No available riders. Please assign manually.', 'warning')
                except Exception as e:
                    current_app.logger.error(f"Error in auto-assigning rider: {str(e)}")
                    flash('Order status updated, but there was an error assigning a rider.', 'warning')
            else:
                # Just update status if rider is already assigned
                if Order.update_status(order_id, status):
                    flash('Order status updated and customer notified.', 'success')
                else:
                    flash('Failed to update order status. Please try again.', 'error')
        
        elif status == 'delivered':
            # Mark order as delivered and update delivery status
            if Order.update_status(order_id, 'delivered'):
                try:
                    # Update delivery status as well
                    db = Database()
                    db.execute_query(
                        """
                        UPDATE deliveries 
                        SET status = 'delivered', delivered_at = NOW()
                        WHERE order_id = %s
                        """,
                        (order_id,)
                    )
                    
                    # Notify customer
                    Notification.create(order['user_id'], 'user', 'order_status', 'Order delivered', f"Your order #{order_id} has been delivered.", related_id=order_id, data={'order_id': int(order_id), 'status': 'delivered'})
                    current_app.socketio.emit('notification', {'title': 'Order delivered', 'message': f'Your order #{order_id} has been delivered.', 'type': 'order_status', 'data': {'order_id': int(order_id), 'status': 'delivered'}}, room=f"user_{order['user_id']}")
                    current_app.socketio.emit('order_status_updated', {'order_id': int(order_id), 'status': 'delivered'}, room=f"user_{order['user_id']}")
                    
                    flash('Order marked as delivered and customer notified.', 'success')
                except Exception as e:
                    current_app.logger.error(f"Error marking order as delivered: {str(e)}")
                    flash('Order marked as delivered, but there was an error notifying customer.', 'warning')
            else:
                flash('Failed to mark order as delivered.', 'error')
        
        else:
            # For other status updates
            if Order.update_status(order_id, status):
                flash('Order status updated and customer notified.', 'success')
            else:
                flash('Failed to update order status. Please try again.', 'error')
                
    except Exception as e:
        current_app.logger.error(f"Error in update_order_status: {str(e)}", exc_info=True)
        flash('Failed to update order status. Please try again.', 'error')

    return redirect(url_for('seller.orders'))



# ... (rest of the code remains the same)
def order_details(order_id):
    order = Order.get_by_id(order_id)
    if not order or order['seller_id'] != session['user_id']:
        return jsonify({'error': 'Order not found or unauthorized.'}), 404
    
    # Add customer details
    user = User.get_by_id(order['user_id'])
    if user:
        order['customer_name'] = f"{user['first_name']} {user['last_name']}"
        order['customer_email'] = user['email']
        order['customer_phone'] = user['phone'] or ''
    else:
        order['customer_name'] = 'Unknown'
        order['customer_email'] = ''
        order['customer_phone'] = ''
    
    order['items_count'] = len(order['items'])
    
    html = render_template('seller/order_detail_modal.html', order=order)
    return jsonify({'html': html})

# Seller application route (for regular users to become sellers)
@seller_bp.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    """Apply to become a seller"""
    user = User.get_by_id(session['user_id'])
    
    # Check if user is already a seller
    if user['role'] == 'seller':
        flash('You are already a seller.', 'info')
        return redirect(url_for('seller.dashboard'))
    
    # Check if user has a pending application
    existing_request = SellerRequest.get_by_user_id(session['user_id'])
    if existing_request and existing_request['status'] == 'pending':
        flash('You already have a pending seller application.', 'info')
        return render_template('seller/application_pending.html', request=existing_request)
    
    form = SellerApplicationForm()
    if form.validate_on_submit():
        try:
            SellerRequest.create(
                user_id=session['user_id'],
                business_name=form.business_name.data.strip(),
                business_description=form.business_description.data.strip(),
                business_address=form.business_address.data.strip(),
                business_phone=form.business_phone.data.strip(),
                tax_id=form.tax_id.data.strip() if form.tax_id.data else None
            )
            flash('Your seller application has been submitted! We will review it and get back to you.', 'success')
            return redirect(url_for('public.browse_products'))
        except Exception as e:
            flash('Failed to submit application. Please try again.', 'error')
    
    return render_template('seller/apply.html', form=form)

@seller_bp.route('/analytics')
@login_required
@seller_required
def analytics():
    """Detailed seller analytics"""
    seller_id = session['user_id']
    db = Database()
    
    # Revenue trends (last 12 months)
    revenue_trends = db.execute_query("""
        SELECT DATE_FORMAT(created_at, '%Y-%m') as month,
               COUNT(*) as orders,
               SUM(total_amount) as revenue,
               AVG(total_amount) as avg_order_value
        FROM orders 
        WHERE seller_id = %s 
          AND created_at >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
        GROUP BY DATE_FORMAT(created_at, '%Y-%m')
        ORDER BY month ASC
    """, (seller_id,), fetch=True)
    
    # Product performance
    product_performance = db.execute_query("""
        SELECT p.name, p.price, p.stock_quantity,
               COUNT(oi.id) as times_ordered,
               SUM(oi.quantity) as total_sold,
               SUM(oi.quantity * oi.price_at_time) as total_revenue,
               AVG(r.rating) as avg_rating,
               COUNT(r.id) as review_count
        FROM products p
        LEFT JOIN order_items oi ON p.id = oi.product_id
        LEFT JOIN reviews r ON p.id = r.product_id
        WHERE p.seller_id = %s
        GROUP BY p.id
        ORDER BY total_revenue DESC
    """, (seller_id,), fetch=True)
    
    # Customer insights
    customer_insights = db.execute_query("""
        SELECT u.first_name, u.last_name, u.email,
               COUNT(o.id) as total_orders,
               SUM(o.total_amount) as total_spent,
               MAX(o.created_at) as last_order_date
        FROM users u
        JOIN orders o ON u.id = o.user_id
        WHERE o.seller_id = %s
        GROUP BY u.id
        ORDER BY total_spent DESC
        LIMIT 20
    """, (seller_id,), fetch=True)
    
    # Order status breakdown - ensure we get a list of dicts
    order_status_breakdown = db.execute_query("""
        SELECT status, COUNT(*) as count
        FROM orders
        WHERE seller_id = %s
        GROUP BY status
    """, (seller_id,), fetch=True) or []
    
    # Convert query results to a more manageable format
    def process_query_result(rows):
        if not rows:
            return []
        result = []
        for row in rows:
            if isinstance(row, dict):
                processed = {}
                for k, v in row.items():
                    if hasattr(v, '__float__'):
                        processed[k] = float(v)
                    else:
                        processed[k] = v
                result.append(processed)
            else:
                # Handle case where rows are tuples
                result.append(dict(zip(['status', 'count'], row)))
        return result

    # Process all query results
    revenue_trends = process_query_result(revenue_trends)
    product_performance = process_query_result(product_performance)
    customer_insights = process_query_result(customer_insights)
    order_status_breakdown = process_query_result(order_status_breakdown)
    
    return render_template('seller/analytics.html',
                         revenue_trends=revenue_trends,
                         product_performance=product_performance,
                         customer_insights=customer_insights,
                         order_status_breakdown=order_status_breakdown)

@seller_bp.route('/api/analytics/realtime')
@login_required
@seller_required
def analytics_realtime():
    """Real-time analytics API endpoint for seller"""
    seller_id = session['user_id']
    db = Database()
    
    try:
        # Fetch ALL order_items for this seller
        all_items = db.client.table('order_items').select('*').eq('seller_id', seller_id).execute()
        all_items = all_items.data or []
        
        total_revenue = sum(float(i.get('total_price', 0)) for i in all_items)
        
        now = datetime.now()
        today_revenue = sum(float(i.get('total_price', 0)) for i in all_items
                          if i.get('created_at') and isinstance(i['created_at'], str)
                          and i['created_at'].startswith(now.strftime('%Y-%m-%d')))
        month_revenue = sum(float(i.get('total_price', 0)) for i in all_items
                          if i.get('created_at') and isinstance(i['created_at'], str)
                          and i['created_at'].startswith(now.strftime('%Y-%m')))
        
        # Fetch orders with items from this seller
        item_order_ids = list(set(int(i['order_id']) for i in all_items if i.get('order_id')))
        all_orders = db.client.table('orders').select('id, status').in_('id', item_order_ids).execute() if item_order_ids else []
        all_orders = all_orders.data or []
        
        total_orders = len(all_orders)
        pending_orders = sum(1 for o in all_orders if o.get('status') == 'pending')
        confirmed_orders = sum(1 for o in all_orders if o.get('status') == 'confirmed')
        delivered_orders = sum(1 for o in all_orders if o.get('status') == 'delivered')
        cancelled_orders = sum(1 for o in all_orders if o.get('status') == 'cancelled')
        
        # Product stats
        all_products = db.client.table('products').select('id, status, stock_quantity').eq('seller_id', seller_id).execute()
        all_products = all_products.data or []
        total_products = len(all_products)
        active_products = sum(1 for p in all_products if p.get('status') == 'active')
        low_stock_items = sum(1 for p in all_products if int(p.get('stock_quantity', 0)) <= 10)
        
        # Commission calculation
        commission_rate = float(current_app.config.get('SELLER_COMMISSION_RATE', 0.05))
        commission_due = round(total_revenue * commission_rate, 2)
        net_revenue = round(total_revenue - commission_due, 2)
        
        return jsonify({
            'success': True,
            'total_revenue': round(total_revenue, 2),
            'today_revenue': round(today_revenue, 2),
            'month_revenue': round(month_revenue, 2),
            'orders': {
                'total': total_orders,
                'pending': pending_orders,
                'confirmed': confirmed_orders,
                'delivered': delivered_orders,
                'cancelled': cancelled_orders
            },
            'products': {
                'total': total_products,
                'active': active_products,
                'low_stock': low_stock_items
            },
            'financial': {
                'gross_revenue': round(total_revenue, 2),
                'commission_rate': commission_rate * 100,
                'commission_due': commission_due,
                'net_revenue': net_revenue
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in analytics_realtime: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@seller_bp.route('/inventory')
@login_required
@seller_required
def inventory():
    """Inventory management dashboard"""
    from app.models.inventory import Inventory
    seller_id = session['user_id']
    
    # Get stock summary
    stock_summary = Inventory.get_stock_summary(seller_id)
    
    # Get low stock alerts
    low_stock_alerts = Inventory.get_low_stock_alerts(seller_id, acknowledged=False)
    
    # Get products with stock info
    products = Product.list(seller_id=seller_id, status=None)
    
    # Calculate inventory valuation
    db = Database()
    valuation = db.execute_query("""
        SELECT 
            SUM(stock_quantity * COALESCE(cost_price, price)) as total_value,
            SUM(stock_quantity * price) as retail_value,
            COUNT(*) as total_skus
        FROM products
        WHERE seller_id = %s AND status != 'inactive'
    """, (seller_id,), fetch=True, fetchone=True) or {}
    
    return render_template('seller/inventory_dashboard.html',
                         stock_summary=stock_summary,
                         low_stock_alerts=low_stock_alerts,
                         products=products,
                         valuation=valuation)

@seller_bp.route('/inventory/update-stock', methods=['POST'])
@login_required
@seller_required
def update_stock():
    """Update product stock quantity"""
    try:
        product_id = int(request.form.get('product_id'))
        new_stock = int(request.form.get('stock_quantity'))
        
        if new_stock < 0:
            flash('Stock quantity cannot be negative.', 'error')
            return redirect(url_for('seller.inventory'))
        
        # Verify product belongs to current seller
        seller_id = session['user_id']
        product = Product.get_by_id(product_id)
        
        if not product or product['seller_id'] != seller_id:
            flash('Product not found or unauthorized.', 'error')
            return redirect(url_for('seller.inventory'))
        
        # Update stock
        Product.update(product_id, stock_quantity=new_stock)
        flash(f'Stock updated for "{product["name"]}"', 'success')
        
    except (ValueError, TypeError):
        flash('Invalid input.', 'error')
    except Exception as e:
        flash('Failed to update stock.', 'error')
    
    return redirect(url_for('seller.inventory'))

@seller_bp.route('/bulk-stock-update', methods=['POST'])
@login_required
@seller_required
def bulk_stock_update():
    """Bulk update stock quantities"""
    seller_id = session['user_id']
    
    try:
        updates = request.get_json()
        if not updates:
            return jsonify({'error': 'No updates provided'}), 400
        
        success_count = 0
        for update in updates:
            product_id = int(update['product_id'])
            new_stock = int(update['stock_quantity'])
            
            # Verify ownership
            product = Product.get_by_id(product_id)
            if product and product['seller_id'] == seller_id and new_stock >= 0:
                Product.update(product_id, stock_quantity=new_stock)
                success_count += 1
        
        return jsonify({
            'success': True,
            'message': f'{success_count} products updated successfully'
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to update stock quantities'}), 500

@seller_bp.route('/reports')
@login_required
@seller_required
def reports():
    """Sales reports for seller"""
    seller_id = session['user_id']
    db = Database()
    
    # Date range from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Default to last 30 days if no range provided
    if not start_date or not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Sales summary for the period
    sales_summary = db.execute_query("""
        SELECT 
            COUNT(*) as total_orders,
            SUM(total_amount) as total_revenue,
            AVG(total_amount) as avg_order_value,
            MIN(total_amount) as min_order,
            MAX(total_amount) as max_order
        FROM orders
        WHERE seller_id = %s 
          AND DATE(created_at) BETWEEN %s AND %s
    """, (seller_id, start_date, end_date), fetch=True, fetchone=True)
    
    # Daily sales breakdown
    daily_sales = db.execute_query("""
        SELECT DATE(created_at) as date,
               COUNT(*) as orders,
               SUM(total_amount) as revenue
        FROM orders
        WHERE seller_id = %s 
          AND DATE(created_at) BETWEEN %s AND %s
        GROUP BY DATE(created_at)
        ORDER BY date ASC
    """, (seller_id, start_date, end_date), fetch=True)
    
    # Product sales in period
    product_sales = db.execute_query("""
        SELECT p.name, 
               COUNT(oi.id) as times_ordered,
               SUM(oi.quantity) as quantity_sold,
               SUM(oi.quantity * oi.price_at_time) as revenue
        FROM products p
        JOIN order_items oi ON p.id = oi.product_id
        JOIN orders o ON oi.order_id = o.id
        WHERE p.seller_id = %s 
          AND DATE(o.created_at) BETWEEN %s AND %s
        GROUP BY p.id
        ORDER BY revenue DESC
    """, (seller_id, start_date, end_date), fetch=True)
    
    return render_template('seller/reports.html',
                         sales_summary=sales_summary,
                         daily_sales=daily_sales,
                         product_sales=product_sales,
                         start_date=start_date,
                         end_date=end_date)

# ==================== INVENTORY ENHANCEMENTS ====================

@seller_bp.route('/inventory/alerts')
@login_required
@seller_required
def inventory_alerts():
    """View low stock alerts"""
    from app.models.inventory import Inventory
    seller_id = session['user_id']
    alerts = Inventory.get_low_stock_alerts(seller_id, acknowledged=request.args.get('show_all') == '1')
    return render_template('seller/low_stock_alerts.html', alerts=alerts)

@seller_bp.route('/inventory/alerts/count')
@login_required
@seller_required
def low_stock_alerts_count():
    """Get count of low stock alerts (for real-time updates)"""
    from datetime import datetime, timezone
    from app.models.inventory import Inventory
    seller_id = session['user_id']
    
    try:
        # Get unacknowledged alerts
        alerts = Inventory.get_low_stock_alerts(seller_id, acknowledged=False)
        
        # Check for new alerts (created in last 5 minutes)
        five_mins_ago = datetime.now(timezone.utc)
        new_alerts = []
        for a in (alerts or []):
            created = a.get('created_at')
            if created:
                if isinstance(created, str):
                    try:
                        created = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    except:
                        continue
                if created > five_mins_ago:
                    new_alerts.append(a)
        
        return jsonify({
            'success': True,
            'count': len(alerts) if alerts else 0,
            'new_alerts': [{'id': a['id'], 'product_name': a['product_name']} for a in new_alerts] if new_alerts else []
        })
    except Exception as e:
        current_app.logger.error(f"low_stock_alerts_count error: {e}", exc_info=True)
        return jsonify({'success': False, 'count': 0, 'new_alerts': []})

@seller_bp.route('/inventory/alert/<int:alert_id>/acknowledge', methods=['POST'])
@login_required
@seller_required
def acknowledge_alert(alert_id):
    """Acknowledge a low stock alert"""
    from app.models.inventory import Inventory
    try:
        success = Inventory.acknowledge_alert(alert_id)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@seller_bp.route('/inventory/valuation')
@login_required
@seller_required
def inventory_valuation():
    """Inventory valuation report"""
    seller_id = session['user_id']
    db = Database()
    
    # Detailed valuation by product
    products = db.execute_query("""
        SELECT 
            p.id,
            p.name,
            p.sku,
            p.stock_quantity,
            p.cost_price,
            p.price as retail_price,
            (p.stock_quantity * COALESCE(p.cost_price, p.price)) as cost_value,
            (p.stock_quantity * p.price) as retail_value,
            ((p.price - COALESCE(p.cost_price, 0)) / NULLIF(p.price, 0) * 100) as margin_percent,
            c.name as category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.seller_id = %s AND p.status != 'inactive'
        ORDER BY cost_value DESC
    """, (seller_id,), fetch=True) or []
    
    # Summary
    summary = db.execute_query("""
        SELECT 
            SUM(stock_quantity * COALESCE(cost_price, price)) as total_cost_value,
            SUM(stock_quantity * price) as total_retail_value,
            SUM(stock_quantity) as total_units,
            COUNT(*) as total_products
        FROM products
        WHERE seller_id = %s AND status != 'inactive'
    """, (seller_id,), fetch=True, fetchone=True) or {}
    
    return render_template('seller/inventory_valuation.html', products=products, summary=summary)

@seller_bp.route('/inventory/reorder-suggestions')
@login_required
@seller_required
def reorder_suggestions():
    """Generate reorder suggestions based on sales velocity"""
    seller_id = session['user_id']
    db = Database()
    
    # Calculate products needing reorder based on sales velocity
    suggestions = db.execute_query("""
        SELECT 
            p.id,
            p.name,
            p.sku,
            p.stock_quantity as current_stock,
            p.low_stock_threshold,
            COALESCE(sales.avg_daily_sales, 0) as avg_daily_sales,
            COALESCE(sales.last_30_days_sales, 0) as last_30_days_sales,
            COALESCE(FLOOR(p.stock_quantity / NULLIF(sales.avg_daily_sales, 0)), 999) as days_until_stockout,
            COALESCE(CEIL(sales.avg_daily_sales * 30), 10) as suggested_reorder_qty
        FROM products p
        LEFT JOIN (
            SELECT 
                oi.product_id,
                AVG(oi.quantity) as avg_daily_sales,
                SUM(oi.quantity) as last_30_days_sales
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            WHERE o.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                AND o.status NOT IN ('cancelled', 'refunded')
            GROUP BY oi.product_id
        ) sales ON p.id = sales.product_id
        WHERE p.seller_id = %s 
            AND p.status = 'active'
            AND (p.stock_quantity <= p.low_stock_threshold OR sales.avg_daily_sales > 0)
        ORDER BY days_until_stockout ASC, avg_daily_sales DESC
        LIMIT 50
    """, (seller_id,), fetch=True) or []
    
    return render_template('seller/reorder_suggestions.html', suggestions=suggestions)

@seller_bp.route('/inventory/product/<int:product_id>/history')
@login_required
@seller_required
def stock_history(product_id):
    """View stock movement history for a product"""
    from app.models.inventory import Inventory
    seller_id = session['user_id']
    
    product = Product.get_by_id(product_id)
    
    if not product or product['seller_id'] != seller_id:
        flash('Product not found or unauthorized', 'error')
        return redirect(url_for('seller.inventory'))
    
    history = Inventory.get_product_history(product_id, limit=100)
    
    if request.headers.get('Accept') == 'application/json':
        return jsonify({'success': True, 'history': history})
    
    return render_template('seller/stock_history.html', product=product, history=history)

@seller_bp.route('/inventory/product/<int:product_id>/threshold', methods=['POST'])
@login_required
@seller_required
def update_threshold(product_id):
    """Update low stock threshold for a product"""
    from app.models.inventory import Inventory
    seller_id = session['user_id']
    
    product = Product.get_by_id(product_id)
    
    if not product or product['seller_id'] != seller_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        threshold = int(request.form.get('threshold') or request.json.get('threshold', 10))
        success = Inventory.update_low_stock_threshold(product_id, threshold)
        
        return jsonify({'success': success})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@seller_bp.route('/product/<int:product_id>/variations', methods=['GET'])
def get_product_variations(product_id):
    """Get product variations via API for frontend display"""
    try:
        # Check if product exists
        product = Product.get_by_id(product_id)
        if not product:
            return jsonify({
                'success': False,
                'error': 'Product not found',
                'has_variations': False,
                'variants': []
            }), 200

        # Get active variants for this product
        variants = ProductVariant.get_by_product(product_id, status='active')
        
        if variants:
            # Format variations for frontend
            formatted_variants = []
            for v in variants:
                # Use variant image if available, otherwise use product image as fallback
                var_image = v.get('image_url')
                if not var_image:
                    var_image = product.get('image_url') or '/static/img/placeholder.png'
                
                # Ensure image_url has proper path prefix
                if var_image and not var_image.startswith(('/', 'http')):
                    var_image = '/' + var_image if var_image else '/static/img/placeholder.png'
                
                formatted_variants.append({
                    'id': v['id'],
                    'name': v['name'],
                    'price': float(v['price']),
                    'image_url': var_image,
                    'attributes': v.get('attributes', {})
                })
            
            return jsonify({
                'success': True,
                'has_variations': True,
                'variants': formatted_variants
            }), 200
        else:
            return jsonify({
                'success': True,
                'has_variations': False,
                'variants': []
            }), 200
            
    except Exception as e:
        print(f"Error fetching variations: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'has_variations': False,
            'variants': []
        }), 200


@seller_bp.route('/product/<int:product_id>/images', methods=['GET'])
def get_product_images(product_id):
    """Get product images via API for frontend display"""
    try:
        # Check if product exists
        product = Product.get_by_id(product_id)
        if not product:
            return jsonify({
                'success': False,
                'error': 'Product not found',
                'images': []
            }), 200
        
        # Get images ordered by display_order
        images = Product.get_images(product_id)
        
        if images:
            return jsonify({
                'success': True,
                'images': images
            }), 200
        else:
            return jsonify({
                'success': True,
                'images': []
            }), 200
    except Exception as e:
        print(f"Error fetching product images: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'images': []
        }), 200
