from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from werkzeug.utils import secure_filename
from sqlalchemy import and_, or_, func, text
from app import db
from app.models.models import Product, ProductImage, OrderItem, Order, Category, Notification, User, Review
from app.utils.auth import role_required, get_current_user, api_role_required
from app.services.websocket_service import socketio
from app.services.database import Database
import uuid
import json
import os
from datetime import datetime, timedelta

seller_bp = Blueprint('seller_routes', __name__)

@seller_bp.route('/dashboard')
@role_required('seller')
def dashboard():
    """Seller dashboard with sales analytics"""
    user = get_current_user()
    
    # Get dashboard statistics
    total_products = Product.query.filter_by(seller_id=user['id']).count()
    active_products = Product.query.filter_by(seller_id=user['id'], status='active').count()
    
    # Get recent orders and orders for the template
    orders = OrderItem.query.filter_by(seller_id=user['id']).join(Order).order_by(
        Order.created_at.desc()
    ).limit(10).all()
    
    # Get pending orders
    pending_orders = OrderItem.query.filter_by(
        seller_id=user['id'], 
        status='pending'
    ).count()
    
    # Get products for the products section
    products = Product.query.filter_by(seller_id=user['id']).order_by(
        Product.created_at.desc()
    ).all()
    
    # Calculate monthly sales
    thirty_days_ago = datetime.now() - timedelta(days=30)
    monthly_sales = db.session.query(func.sum(OrderItem.total_price * 50)).filter(  # Convert to PHP
        OrderItem.seller_id == user['id'],
        OrderItem.created_at >= thirty_days_ago
    ).scalar() or 0
    
    # Get sales data for the last 12 months for the graph
    twelve_months_ago = datetime.now() - timedelta(days=365)
    
    # Get monthly sales data (MySQL compatible)
    monthly_sales_data = db.session.query(
        func.date_format(Order.created_at, '%Y-%m-01').label('month'),
        func.sum(OrderItem.total_price * 50).label('total_sales'),  # Convert to PHP
        func.count(OrderItem.id).label('order_count')
    ).join(OrderItem).filter(
        OrderItem.seller_id == user['id'],
        Order.created_at >= twelve_months_ago
    ).group_by(
        func.date_format(Order.created_at, '%Y-%m-01')
    ).order_by('month').all()
    
    # Get top selling products
    top_products = db.session.query(
        Product,
        func.sum(OrderItem.quantity).label('total_quantity'),
        func.sum(OrderItem.total_price * 50).label('total_revenue')
    ).join(OrderItem).filter(
        Product.seller_id == user['id'],
        OrderItem.created_at >= twelve_months_ago
    ).group_by(Product.id).order_by(
        func.sum(OrderItem.quantity).desc()
    ).limit(5).all()
    
    # Get low stock products
    low_stock_products = Product.query.filter(
        Product.seller_id == user['id'],
        Product.stock_quantity <= 5,
        Product.status == 'active'
    ).all()
    
    # Format data for the chart
    sales_labels = []
    sales_amounts = []
    sales_counts = []
    
    # Initialize with zero values for all months
    for i in range(12):
        month = (datetime.now() - timedelta(days=30 * (11 - i))).strftime('%b %Y')
        sales_labels.append(month)
        sales_amounts.append(0)
        sales_counts.append(0)
    
    # Fill in actual data
    for data in monthly_sales_data:
        # data.month is now a string from date_format, convert to datetime
        try:
            month_date = datetime.strptime(data.month, '%Y-%m-%d')
            month_str = month_date.strftime('%b %Y')
            if month_str in sales_labels:
                idx = sales_labels.index(month_str)
                sales_amounts[idx] = float(data.total_sales or 0)
                sales_counts[idx] = data.order_count
        except (ValueError, AttributeError):
            # Skip if date parsing fails
            continue
    
    # Get filter parameters
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    
    # Base query
    query = Product.query.filter_by(seller_id=user['id'])
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f'%{search}%'),
                Product.description.ilike(f'%{search}%'),
                Product.sku.ilike(f'%{search}%')
            )
        )
    
    if status:
        query = query.filter_by(status=status)
    
    # Paginate
    products_paginated = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    
    return render_template('seller/dashboard.html',
                         total_products=total_products,
                         active_products=active_products,
                         orders=orders,
                         products=products,
                         pending_orders=pending_orders,
                         monthly_sales=monthly_sales,
                         low_stock_products=low_stock_products,
                         sales_labels=sales_labels,
                         sales_amounts=sales_amounts,
                         sales_counts=sales_counts,
                         top_products=top_products,
                         seller=user)

@seller_bp.route('/product/add', methods=['GET', 'POST'])
@role_required('seller')
def add_product():
    """Add new product"""
    user = get_current_user()
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        category_id = request.form.get('category_id', type=int)
        price = request.form.get('price', type=float)
        stock_quantity = request.form.get('stock_quantity', type=int)
        sku = request.form.get('sku', '').strip()
        weight = request.form.get('weight', type=float)
        dimensions = request.form.get('dimensions', '').strip()
        brand = request.form.get('brand', '').strip()
        age_group = request.form.get('age_group', 'all_ages')
        pet_type = request.form.get('pet_type')
        
        # Get variation data - NEW CUSTOM VARIATIONS SYSTEM
        has_variations = request.form.get('has_variations') == 'on'
        variation_names = request.form.getlist('variation_names') if has_variations else []
        variation_images = request.files.getlist('variation_images') if has_variations else []
        
        # DEBUG: Log variation data
        print(f"[VARIATIONS DEBUG] has_variations checkbox: {request.form.get('has_variations')}")
        print(f"[VARIATIONS DEBUG] has_variations boolean: {has_variations}")
        print(f"[VARIATIONS DEBUG] variation_names: {variation_names}")
        print(f"[VARIATIONS DEBUG] variation_images count: {len(variation_images)}")
        
        # Validation
        errors = []
        
        if not name:
            errors.append('Product name is required.')
        
        if not category_id:
            errors.append('Category is required.')
        
        if not price or price <= 0:
            errors.append('Valid price is required.')
        
        if not stock_quantity or stock_quantity < 0:
            errors.append('Valid stock quantity is required.')
        
        if not pet_type:
            errors.append('Pet type is required.')
        
        # Check if SKU already exists
        if sku:
            existing_sku = Product.query.filter_by(sku=sku).first()
            if existing_sku:
                errors.append('SKU already exists.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            categories = Category.query.filter_by(status='active').all()
            return render_template('seller/add_product.html', categories=categories)
        
        try:
            # Create product
            product = Product(
                seller_id=user['id'],
                category_id=category_id,
                name=name,
                description=description,
                price=price,
                stock_quantity=stock_quantity,
                sku=sku or None,
                weight=weight,
                dimensions=dimensions,
                brand=brand,
                age_group=age_group,
                pet_type=pet_type,
                status='active'
            )
            
            db.session.add(product)
            db.session.flush()  # Get product ID
            
            # Get image order from frontend
            image_order_json = request.form.get('image_order', '{}')
            try:
                image_order = json.loads(image_order_json) if image_order_json else {}
            except (json.JSONDecodeError, ValueError):
                image_order = {}
            
            # Handle image uploads - Upload to Supabase for web+mobile sync
            uploaded_files = request.files.getlist('images')
            if uploaded_files and uploaded_files[0].filename:
                from app.services.supabase_storage import get_storage_manager
                from config.config import Config
                
                # Get Supabase storage manager
                storage_manager = get_storage_manager()
                
                # Also save locally for web app compatibility
                upload_folder = os.path.join(Config.UPLOAD_FOLDER, 'products')
                os.makedirs(upload_folder, exist_ok=True)
                
                # Create list of files in order
                files_list = [f for f in uploaded_files[:5] if f and f.filename]  # Max 5 images
                
                for i, file in enumerate(files_list):
                    # Generate unique filename
                    filename = f"{product.id}_{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}"
                    
                    # Save locally for web app
                    local_file_path = os.path.join(upload_folder, filename)
                    file.save(local_file_path)
                    
                    # Upload to Supabase for mobile app
                    file.seek(0)  # Reset file pointer
                    supabase_url = storage_manager.upload_product_image(
                        file, product.id, filename
                    )
                    
                    # Get the original order from the image_order map
                    original_position = image_order.get(str(i), i) if image_order else i
                    
                    # Create product image record with Supabase URL
                    # If Supabase upload failed, fall back to local URL
                    image_url = supabase_url or f'uploads/products/{filename}'
                    
                    product_image = ProductImage(
                        product_id=product.id,
                        image_url=image_url,
                        is_primary=(i == 0),  # First image is primary
                        alt_text=f"{name} image",
                        display_order=i  # Store the actual display order
                    )
                    db.session.add(product_image)
            
            # Handle product variations if enabled
            if has_variations:
                from app.models.product_variant import ProductVariant
                from config.config import Config
                
                print(f"[VARIATIONS DEBUG] Creating {len(variation_names)} variations for product {product.id}")
                
                # Create variations for each custom variation entry
                for idx, var_name in enumerate(variation_names):
                    var_name = var_name.strip()
                    if not var_name:  # Skip empty names
                        print(f"[VARIATIONS DEBUG] Skipping variation {idx} - empty name")
                        continue
                    
                    print(f"[VARIATIONS DEBUG] Creating variation {idx}: {var_name}")
                    
                    # Handle variation image if provided
                    image_url = None
                    if idx < len(variation_images):
                        var_image = variation_images[idx]
                        if var_image and var_image.filename:
                            upload_folder = os.path.join(Config.UPLOAD_FOLDER, 'variations')
                            os.makedirs(upload_folder, exist_ok=True)
                            
                            # Generate unique filename
                            filename = f"{product.id}_{uuid.uuid4().hex[:8]}_{secure_filename(var_image.filename)}"
                            file_path = os.path.join(upload_folder, filename)
                            
                            var_image.save(file_path)
                            image_url = f'uploads/variations/{filename}'
                            print(f"[VARIATIONS DEBUG] Saved image for variation {idx}: {image_url}")
                    
                    # Create product variant
                    result = ProductVariant.create(
                        product_id=product.id,
                        name=var_name,
                        price=price,
                        stock_quantity=stock_quantity,
                        image_url=image_url,
                        display_order=idx + 1
                    )
                    print(f"[VARIATIONS DEBUG] Created variant ID: {result['id'] if isinstance(result, dict) else result.get('id')}")
            
            db.session.commit()
            flash('Product added successfully!', 'success')
            return redirect(url_for('seller.products'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error adding product: {str(e)}")
            flash('Failed to add product. Please try again.', 'error')
    
    categories = Category.query.filter_by(status='active').all()
    return render_template('seller/add_product.html', categories=categories)

@seller_bp.route('/product/edit/<int:product_id>', methods=['GET', 'POST'])
@role_required('seller')
def edit_product(product_id):
    """Edit product"""
    user = get_current_user()
    product = Product.query.filter_by(
        id=product_id,
        seller_id=user['id']
    ).first_or_404()
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        category_id = request.form.get('category_id', type=int)
        price = request.form.get('price', type=float)
        stock_quantity = request.form.get('stock_quantity', type=int)
        sku = request.form.get('sku', '').strip()
        weight = request.form.get('weight', type=float)
        dimensions = request.form.get('dimensions', '').strip()
        brand = request.form.get('brand', '').strip()
        age_group = request.form.get('age_group', 'all_ages')
        pet_type = request.form.get('pet_type')
        status = request.form.get('status', 'active')
        
        # Validation
        errors = []
        
        if not name:
            errors.append('Product name is required.')
        
        if not category_id:
            errors.append('Category is required.')
        
        if not price or price <= 0:
            errors.append('Valid price is required.')
        
        if not stock_quantity or stock_quantity < 0:
            errors.append('Valid stock quantity is required.')
        
        if not pet_type:
            errors.append('Pet type is required.')
        
        # Check if SKU already exists (exclude current product)
        if sku:
            existing_sku = Product.query.filter(
                Product.sku == sku,
                Product.id != product_id
            ).first()
            if existing_sku:
                errors.append('SKU already exists.')
        
        # Get variation data - NEW CUSTOM VARIATIONS SYSTEM
        has_variations = request.form.get('has_variations') == 'on'
        variation_names = request.form.getlist('variation_names') if has_variations else []
        variation_images = request.files.getlist('variation_images') if has_variations else []
        
        # DEBUG: Log variation data
        print(f"[VARIATIONS DEBUG - EDIT] has_variations checkbox: {request.form.get('has_variations')}")
        print(f"[VARIATIONS DEBUG - EDIT] has_variations boolean: {has_variations}")
        print(f"[VARIATIONS DEBUG - EDIT] variation_names: {variation_names}")
        print(f"[VARIATIONS DEBUG - EDIT] variation_images count: {len(variation_images)}")
        
        if errors:
            for error in errors:
                flash(error, 'error')
            categories = Category.query.filter_by(status='active').all()
            return render_template('seller/edit_product.html', 
                                 product=product, categories=categories)
        
        try:
            # Update product
            product.name = name
            product.description = description
            product.category_id = category_id
            product.price = price
            product.stock_quantity = stock_quantity
            product.sku = sku or None
            product.weight = weight
            product.dimensions = dimensions
            product.brand = brand
            product.age_group = age_group
            product.pet_type = pet_type
            product.status = status
            
            # Get image order from frontend
            image_order_json = request.form.get('image_order', '{}')
            try:
                image_order = json.loads(image_order_json) if image_order_json else {}
            except (json.JSONDecodeError, ValueError):
                image_order = {}
            
            # Handle image uploads - Check if replacing existing images
            uploaded_files = request.files.getlist('images')
            if uploaded_files and uploaded_files[0].filename:
                # If new images are uploaded, replace all existing ones
                from app.services.supabase_storage import get_storage_manager
                from config.config import Config
                
                # Delete existing images
                ProductImage.query.filter_by(product_id=product.id).delete()
                db.session.flush()
                
                # Get Supabase storage manager
                storage_manager = get_storage_manager()
                
                upload_folder = os.path.join(Config.UPLOAD_FOLDER, 'products')
                os.makedirs(upload_folder, exist_ok=True)
                
                # Create list of files in order
                files_list = [f for f in uploaded_files[:5] if f and f.filename]  # Max 5 images
                
                for i, file in enumerate(files_list):
                    # Generate unique filename
                    filename = f"{product.id}_{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}"
                    
                    # Save locally for web app
                    local_file_path = os.path.join(upload_folder, filename)
                    file.save(local_file_path)
                    
                    # Upload to Supabase for mobile app
                    file.seek(0)  # Reset file pointer
                    supabase_url = storage_manager.upload_product_image(
                        file, product.id, filename
                    )
                    
                    # Use Supabase URL if available, otherwise fall back to local
                    image_url = supabase_url or f'uploads/products/{filename}'
                    
                    # Create product image record with display_order
                    product_image = ProductImage(
                        product_id=product.id,
                        image_url=image_url,
                        is_primary=(i == 0),  # First image is primary
                        alt_text=f"{product.name} image",
                        display_order=i  # Store the actual display order
                    )
                    db.session.add(product_image)
            else:
                # No new images uploaded - check if existing images were reordered
                if image_order and len(image_order) > 0:
                    # Update display order of existing images
                    existing_images = ProductImage.query.filter_by(product_id=product.id).all()
                    
                    # Create a mapping of image_id to new order
                    for new_order, image_id in image_order.items():
                        # Find the image and update its display_order
                        img = next((i for i in existing_images if i.id == int(image_id)), None)
                        if img:
                            img.display_order = int(new_order)
                            img.is_primary = (int(new_order) == 0)  # Mark first as primary
                    
                    # Update remaining images that weren't in the reorder
                    current_orders = set(int(k) for k in image_order.keys())
                    unordered_images = [img for img in existing_images if img.display_order not in current_orders]
                    next_order = len(image_order)
                    for img in unordered_images:
                        img.display_order = next_order
                        img.is_primary = False
                        next_order += 1
            
            # Handle product variations if enabled
            if has_variations:
                from app.models.product_variant import ProductVariant
                from config.config import Config
                
                # Delete existing variants first
                ProductVariant.delete_by_product(product.id)
                
                # Create new variations for each custom variation entry
                for idx, var_name in enumerate(variation_names):
                    var_name = var_name.strip()
                    if not var_name:  # Skip empty names
                        continue
                    
                    # Handle variation image if provided
                    image_url = None
                    if idx < len(variation_images):
                        var_image = variation_images[idx]
                        if var_image and var_image.filename:
                            upload_folder = os.path.join(Config.UPLOAD_FOLDER, 'variations')
                            os.makedirs(upload_folder, exist_ok=True)
                            
                            # Generate unique filename
                            filename = f"{product.id}_{uuid.uuid4().hex[:8]}_{secure_filename(var_image.filename)}"
                            file_path = os.path.join(upload_folder, filename)
                            
                            var_image.save(file_path)
                            image_url = f'uploads/variations/{filename}'
                    
                    # Create product variant
                    ProductVariant.create(
                        product_id=product.id,
                        name=var_name,
                        price=price,
                        stock_quantity=stock_quantity,
                        image_url=image_url,
                        display_order=idx + 1
                    )
            else:
                # If variations are disabled, delete any existing variants
                from app.models.product_variant import ProductVariant
                ProductVariant.delete_by_product(product.id)
            
            db.session.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('seller.products'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating product: {str(e)}")
            flash(f'Failed to update product: {str(e)}', 'error')
    
    categories = Category.query.filter_by(status='active').all()
    return render_template('seller/edit_product.html', 
                         product=product, categories=categories)

@seller_bp.route('/product/delete/<int:product_id>', methods=['POST'])
@role_required('seller')
def delete_product(product_id):
    """Delete product"""
    user = get_current_user()
    product = Product.query.filter_by(
        id=product_id,
        seller_id=user['id']
    ).first_or_404()
    
    # Check if product has orders
    has_orders = OrderItem.query.filter_by(product_id=product_id).first()
    
    try:
        if has_orders:
            # Soft delete - just mark as inactive
            product.status = 'inactive'
            flash('Product marked as inactive (has existing orders).', 'warning')
        else:
            # Hard delete
            db.session.delete(product)
            flash('Product deleted successfully!', 'success')
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('Failed to delete product.', 'error')

@seller_bp.route('/product/<int:product_id>/variations', methods=['GET'])
def get_product_variations(product_id):
    """Get product variations via API"""
    try:
        from app.models.product_variant import ProductVariant
        from flask import current_user
        
        # Check if product exists and belongs to current seller
        product = Product.query.filter_by(id=product_id).first()
        if not product:
            return jsonify({
                'success': False,
                'error': 'Product not found',
                'has_variations': False,
                'variants': []
            }), 200  # Return 200 for consistency with error handling
        
        # Verify ownership if user is logged in
        if current_user.is_authenticated and hasattr(current_user, 'seller_id'):
            if product.seller_id != current_user.seller_id:
                return jsonify({
                    'success': False,
                    'error': 'Unauthorized',
                    'has_variations': False,
                    'variants': []
                }), 200  # Return 200 for consistency
        
        variants = ProductVariant.get_by_product(product_id, status='active')
        
        if variants:
            # Format variations for frontend
            formatted_variants = [{
                'id': v['id'],
                'name': v['name'],
                'price': float(v['price']),
                'image_url': v.get('image_url'),
                'attributes': v.get('attributes', {})
            } for v in variants]
            
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
        }), 200  # Return 200 so fetch succeeds and error is handled on frontend

@seller_bp.route('/product/<int:product_id>/images', methods=['GET'])
def get_product_images(product_id):
    """Get product images via API"""
    try:
        # Check if product exists
        product = Product.query.filter_by(id=product_id).first()
        if not product:
            return jsonify({
                'success': False,
                'error': 'Product not found',
                'images': []
            }), 200
        
        # Verify ownership if user is logged in
        if current_user.is_authenticated and hasattr(current_user, 'seller_id'):
            if product.seller_id != current_user.seller_id:
                return jsonify({
                    'success': False,
                    'error': 'Unauthorized',
                    'images': []
                }), 200
        
        # Get images ordered by display_order
        images = ProductImage.query.filter_by(product_id=product_id).order_by(
            ProductImage.display_order.asc()
        ).all()
        
        if images:
            # Format images for frontend
            formatted_images = [{
                'id': img.id,
                'image_url': img.image_url,
                'is_primary': img.is_primary,
                'display_order': img.display_order,
                'alt_text': img.alt_text
            } for img in images]
            
            return jsonify({
                'success': True,
                'images': formatted_images
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
@seller_bp.route('/orders')
@role_required('seller')
def orders():
    """View all orders for the seller with real-time updates"""
    user = get_current_user()
    status = request.args.get('status')

    # Debug logging
    current_app.logger.info(f"Seller orders request - User ID: {user['id']}, Username: {user.get('username', 'N/A')}, Status filter: {status}")

    # Check if this user has any products
    products_count = db_service.execute_query('SELECT COUNT(*) as count FROM products WHERE seller_id = %s', (user['id'],), fetch=True, fetchone=True)
    current_app.logger.info(f"Seller {user['id']} has {products_count['count'] if products_count else 0} products")

    # Use direct SQL query for better reliability
    db_service = Database()

    # Base query to get orders where seller has items
    base_query = """
        SELECT DISTINCT o.*,
               u.first_name as customer_first_name,
               u.last_name as customer_last_name,
               u.email as customer_email,
               u.phone as customer_phone
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        LEFT JOIN users u ON o.user_id = u.id
        WHERE oi.seller_id = %s
    """
    params = [user['id']]

    if status and status in ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']:
        base_query += " AND o.status = %s"
        params.append(status)

    # Get total count
    count_query = f"SELECT COUNT(DISTINCT o.id) as total FROM ({base_query}) as subquery"
    count_result = db_service.execute_query(count_query, tuple(params), fetch=True, fetchone=True)
    total_count = count_result['total'] if count_result else 0

    # Add ordering and pagination
    base_query += " ORDER BY o.created_at DESC"

    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 15
    offset = (page - 1) * per_page

    base_query += " LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    # Execute query
    orders_data = db_service.execute_query(base_query, tuple(params), fetch=True) or []

    # Debug logging
    current_app.logger.info(f"Seller {user['id']} - Found {len(orders_data)} orders")
    if orders_data:
        for order in orders_data[:3]:  # Log first 3 orders
            current_app.logger.info(f"  Order {order['id']}: status={order['status']}, customer={order['customer_first_name']} {order['customer_last_name']}")

    # Add items_count and items to each order
    for order in orders_data:
        # Get items count
        items_count_result = db_service.execute_query(
            "SELECT COUNT(*) as count FROM order_items WHERE order_id = %s AND seller_id = %s",
            (order['id'], user['id']),
            fetch=True, fetchone=True
        )
        order['items_count'] = items_count_result['count'] if items_count_result else 0

        # Get order items with product details
        items_result = db_service.execute_query(
            """
            SELECT oi.*, p.name, p.image_url, pv.name as variant_name
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            LEFT JOIN product_variants pv ON oi.variant_id = pv.id
            WHERE oi.order_id = %s AND oi.seller_id = %s
            """,
            (order['id'], user['id']),
            fetch=True
        )
        order['items'] = items_result if items_result else []

    # Get status counts
    status_counts_query = """
        SELECT o.status, COUNT(DISTINCT o.id) as count
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        WHERE oi.seller_id = %s
        GROUP BY o.status
    """
    status_counts_result = db_service.execute_query(status_counts_query, (user['id'],), fetch=True) or []
    status_counts = {row['status']: row['count'] for row in status_counts_result}

    # Create a simple pagination object
    class SimplePagination:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_next = page < self.pages
            self.has_prev = page > 1

    orders_paginated = SimplePagination(orders_data, page, per_page, total_count)
    
    status_counts = {status: count for status, count in status_counts}
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return JSON for AJAX requests
        orders_json = []
        for order in orders_data:
            orders_json.append({
                'id': order['id'],
                'order_number': order.get('order_number'),
                'status': order['status'],
                'status_display': order['status'].replace('_', ' ').title(),
                'total_amount': float(order['total_amount']) if order.get('total_amount') else 0,
                'created_at': order['created_at'].isoformat() if hasattr(order['created_at'], 'isoformat') else str(order['created_at']),
                'updated_at': order.get('updated_at').isoformat() if order.get('updated_at') and hasattr(order['updated_at'], 'isoformat') else None,
                'customer_first_name': order['customer_first_name'],
                'customer_last_name': order['customer_last_name'],
                'customer_email': order['customer_email'],
                'customer_phone': order['customer_phone'],
                'customer_name': f"{order['customer_first_name']} {order['customer_last_name']}",
                'items_count': order['items_count']
            })

        return jsonify({
            'success': True,
            'orders': orders_json,
            'has_next': orders_paginated.has_next,
            'has_prev': orders_paginated.has_prev,
            'page': orders_paginated.page,
            'pages': orders_paginated.pages,
            'per_page': orders_paginated.per_page,
            'total': orders_paginated.total,
            'status_counts': status_counts
        })
    
    return render_template('seller/orders.html', 
                         orders=orders_paginated.items,
                         pagination=orders_paginated,
                         status_counts=status_counts,
                         current_status=status,
                         current_page=page)

@seller_bp.route('/order/<int:order_id>/update-status', methods=['POST'])
@role_required('seller')
def update_order_status(order_id):
    """Update order status with real-time notifications"""
    user = get_current_user()
    order = Order.query.get_or_404(order_id)
    
    # Verify the order belongs to this seller
    if order.seller_id != user['id']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    status = request.form.get('status')
    if not status or status not in ['pending', 'confirmed', 'ready_for_pickup', 'shipped', 'delivered', 'cancelled']:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400
    
    try:
        previous_status = order.status
        order.status = status
        order.updated_at = datetime.utcnow()
        
        # If order is confirmed or ready for pickup, notify available riders
        if (status in ['confirmed', 'ready_for_pickup']) and (previous_status not in ['confirmed', 'ready_for_pickup']):
            # Get order details for notification
            order_data = {
                'id': order.id,
                'order_number': order.order_number,
                'total_amount': float(order.total_amount) if order.total_amount else 0,
                'pickup_address': {
                    'name': user.business_name or 'Store',
                    'address': f"{user.address or 'Pickup Location'}, {user.city or ''}, {user.province or ''}",
                    'contact': user.phone or ''
                },
                'delivery_address': {
                    'name': order.shipping_address.recipient_name,
                    'address': f"{order.shipping_address.street_address}, {order.shipping_address.city}, {order.shipping_address.province}",
                    'contact': order.shipping_address.contact_number
                },
                'items': [{
                    'name': item.product.name,
                    'quantity': item.quantity,
                    'price': float(item.price) if item.price else 0
                } for item in order.items],
                'items_count': len(order.items),
                'created_at': order.created_at.isoformat() if order.created_at else datetime.utcnow().isoformat(),
                'status': status  # Include status in the notification
            }
            
            # Notify all available riders
            from app.services.rider_websocket import notify_riders_new_order
            try:
                notify_riders_new_order(order_data)
                current_app.logger.info(f'Notified riders about order {order.id} status: {status}')
            except Exception as e:
                current_app.logger.error(f'Error notifying riders: {str(e)}')
        
        db.session.commit()
        
        # Create notification for customer
        notification = Notification(
            user_id=order.user_id,
            title=f'Order #{order.id} Updated',
            message=f'Your order status has been updated to: {status.replace("_", " ").title()}',
            type='order_status',
            related_id=order.id
        )
        db.session.add(notification)
        db.session.commit()
        
        # Emit socket event for real-time update
        socketio.emit('order_status_updated', {
            'order_id': order.id,
            'status': status,
            'status_display': status.replace("_", " ").title(),
            'updated_at': order.updated_at.isoformat()
        }, room=f'seller_{user['id']}')
        
        return jsonify({
            'success': True, 
            'message': 'Order status updated successfully',
            'status': status,
            'status_display': status.replace("_", " ").title()
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error updating order status: {str(e)}')
        return jsonify({'success': False, 'message': 'Failed to update order status'}), 500

@seller_bp.route('/update-profile', methods=['POST'])
@role_required('seller')
def update_profile():
    """Update seller profile"""
    user = get_current_user()
    
    # Get form data
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    city = request.form.get('city', '').strip()
    state = request.form.get('state', '').strip()
    zip_code = request.form.get('zip_code', '').strip()
    
    # Validation
    if not first_name or not last_name:
        flash('First name and last name are required.', 'error')
        return redirect(url_for('seller.profile'))
    
    try:
        # Update user
        user.first_name = first_name
        user.last_name = last_name
        user.phone = phone
        user.address = address
        user.city = city
        user.state = state
        user.zip_code = zip_code
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to update profile.', 'error')
    
    return redirect(url_for('seller.profile'))

@seller_bp.route('/products')
@role_required('seller')
def products():
    """List seller products"""
    user = get_current_user()
    page = request.args.get('page', 1, type=int)
    products = Product.query.filter_by(seller_id=user['id']).paginate(per_page=20, page=page)
    return render_template('seller/products.html', products=products)

@seller_bp.route('/analytics')
@role_required('seller')
def analytics():
    """Seller analytics"""
    user = get_current_user()
    
    # Get date range from query params
    days = request.args.get('days', 365, type=int)  # Default to 12 months
    start_date = datetime.now() - timedelta(days=days)
    
    # Sales analytics - last 12 months
    sales_data = db.session.query(
        func.date(OrderItem.created_at).label('date'),
        func.sum(OrderItem.total_price).label('total_sales'),
        func.count(OrderItem.id).label('order_count')
    ).filter(
        OrderItem.seller_id == user['id'],
        OrderItem.created_at >= start_date
    ).group_by(func.date(OrderItem.created_at)).order_by(
        func.date(OrderItem.created_at)
    ).all()
    
    # Calculate total revenue and orders
    total_revenue = sum(item.total_sales or 0 for item in sales_data)
    total_orders = sum(item.order_count or 0 for item in sales_data)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Get all products for this seller
    all_products = Product.query.filter_by(seller_id=user['id']).all()
    total_products = len(all_products)
    
    # Top products with complete data
    top_products = db.session.query(
        Product.id,
        Product.name,
        Product.price,
        func.sum(OrderItem.quantity).label('total_sold'),
        func.sum(OrderItem.total_price).label('total_revenue'),
        func.avg(Review.rating).label('avg_rating')
    ).outerjoin(OrderItem, OrderItem.product_id == Product.id).outerjoin(
        Review, Review.product_id == Product.id
    ).filter(
        Product.seller_id == user['id'],
        OrderItem.created_at >= start_date if OrderItem.created_at is not None else True
    ).group_by(Product.id, Product.name, Product.price).order_by(
        func.sum(OrderItem.total_price).desc()
    ).limit(10).all()
    
    # Order status distribution
    order_status = db.session.query(
        OrderItem.status,
        func.count(OrderItem.id).label('count')
    ).filter(
        OrderItem.seller_id == user['id'],
        OrderItem.created_at >= start_date
    ).group_by(OrderItem.status).all()
    
    # Format order status for template
    order_status_breakdown = [{'status': status, 'count': count} for status, count in order_status]
    
    # Revenue trends formatted for chart (by month)
    revenue_trends = []
    for item in sales_data:
        revenue_trends.append({
            'month': item.date.strftime('%b') if item.date else 'Unknown',
            'revenue': float(item.total_sales or 0),
            'orders': item.order_count or 0
        })
    
    # Format products for template
    product_performance = []
    for product in top_products:
        product_performance.append({
            'name': product.name,
            'price': float(product.price or 0),
            'total_sold': product.total_sold or 0,
            'total_revenue': float(product.total_revenue or 0),
            'avg_rating': float(product.avg_rating or 0) if product.avg_rating else None
        })
    
    # Get top customers
    customer_insights = db.session.query(
        User.first_name,
        User.last_name,
        User.email,
        func.count(OrderItem.id).label('total_orders'),
        func.sum(OrderItem.total_price).label('total_spent'),
        func.max(OrderItem.created_at).label('last_order_date')
    ).join(Order, Order.customer_id == User.id).join(
        OrderItem, OrderItem.order_id == Order.id
    ).filter(
        OrderItem.seller_id == user['id'],
        OrderItem.created_at >= start_date
    ).group_by(User.id, User.first_name, User.last_name, User.email).order_by(
        func.sum(OrderItem.total_price).desc()
    ).limit(10).all()
    
    # Format customer insights
    formatted_customers = []
    for customer in customer_insights:
        formatted_customers.append({
            'first_name': customer.first_name or 'Unknown',
            'last_name': customer.last_name or '',
            'email': customer.email,
            'total_orders': customer.total_orders or 0,
            'total_spent': float(customer.total_spent or 0),
            'last_order_date': customer.last_order_date
        })
    
    # Get recent orders
    recent_orders_data = db.session.query(
        Order.id,
        User.first_name,
        User.last_name,
        Order.created_at,
        func.sum(OrderItem.total_price).label('total_amount'),
        OrderItem.status
    ).join(OrderItem, OrderItem.order_id == Order.id).join(
        User, Order.customer_id == User.id
    ).filter(
        OrderItem.seller_id == user['id'],
        OrderItem.created_at >= start_date
    ).group_by(Order.id, User.first_name, User.last_name, Order.created_at, OrderItem.status).order_by(
        Order.created_at.desc()
    ).limit(10).all()
    
    # Format recent orders
    recent_orders = []
    for order in recent_orders_data:
        recent_orders.append({
            'id': order.id,
            'customer_name': f"{order.first_name} {order.last_name}",
            'order_date': order.created_at,
            'total_amount': float(order.total_amount or 0),
            'status': order.status
        })
    
    return render_template('seller/analytics.html',
                         revenue_trends=revenue_trends,
                         product_performance=product_performance,
                         order_status_breakdown=order_status_breakdown,
                         total_revenue=total_revenue,
                         total_orders=total_orders,
                         avg_order_value=avg_order_value,
                         total_products=total_products,
                         customer_insights=formatted_customers,
                         recent_orders=recent_orders,
                         sales_data=sales_data,
                         days=days)

@seller_bp.route('/api/analytics/realtime')
@api_role_required('seller')
def analytics_realtime():
    """Real-time analytics API endpoint for seller"""
    user = get_current_user()
    seller_id = user['id']
    db_service = Database()
    
    try:
        # Total revenue - based on order_items (which has correct seller_id)
        revenue_result = db_service.execute_query("""
            SELECT COALESCE(SUM(oi.total_price), 0) as total_revenue
            FROM order_items oi
            WHERE oi.seller_id = %s
        """, (seller_id,), fetch=True, fetchone=True)
        
        # Today's revenue
        today_revenue_result = db_service.execute_query("""
            SELECT COALESCE(SUM(oi.total_price), 0) as revenue
            FROM order_items oi
            WHERE oi.seller_id = %s AND DATE(oi.created_at) = CURDATE()
        """, (seller_id,), fetch=True, fetchone=True)
        
        # This month's revenue
        month_revenue_result = db_service.execute_query("""
            SELECT COALESCE(SUM(oi.total_price), 0) as revenue
            FROM order_items oi
            WHERE oi.seller_id = %s AND MONTH(oi.created_at) = MONTH(NOW()) 
            AND YEAR(oi.created_at) = YEAR(NOW())
        """, (seller_id,), fetch=True, fetchone=True)
        
        # Order counts - get distinct orders where this seller has items
        orders_result = db_service.execute_query("""
            SELECT 
                COUNT(DISTINCT o.id) as total_orders,
                SUM(CASE WHEN o.status = 'pending' THEN 1 ELSE 0 END) as pending_orders,
                SUM(CASE WHEN o.status = 'confirmed' THEN 1 ELSE 0 END) as confirmed_orders,
                SUM(CASE WHEN o.status = 'delivered' THEN 1 ELSE 0 END) as delivered_orders,
                SUM(CASE WHEN o.status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_orders
            FROM orders o
            WHERE o.id IN (
                SELECT DISTINCT order_id FROM order_items WHERE seller_id = %s
            )
        """, (seller_id,), fetch=True, fetchone=True)
        
        # Product stats
        products_result = db_service.execute_query("""
            SELECT 
                COUNT(*) as total_products,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_products,
                SUM(CASE WHEN stock_quantity <= 10 THEN 1 ELSE 0 END) as low_stock_items
            FROM products
            WHERE seller_id = %s
        """, (seller_id,), fetch=True, fetchone=True)
        
        # Commission calculation
        commission_rate = float(current_app.config.get('SELLER_COMMISSION_RATE', 0.05))
        
        # Get product revenue for accurate commission
        product_revenue = float(revenue_result.get('total_revenue', 0) or 0)
        total_revenue = float(revenue_result.get('total_revenue', 0) or 0)
        
        # Commission is 5% of product revenue ONLY
        commission_due = round(product_revenue * commission_rate, 2)
        net_revenue = round(product_revenue - commission_due, 2)
        
        return jsonify({
            'success': True,
            'total_revenue': round(total_revenue, 2),
            'today_revenue': round(float(today_revenue_result.get('revenue', 0) or 0), 2),
            'month_revenue': round(float(month_revenue_result.get('revenue', 0) or 0), 2),
            'orders': {
                'total': int(orders_result.get('total_orders', 0) or 0),
                'pending': int(orders_result.get('pending_orders', 0) or 0),
                'confirmed': int(orders_result.get('confirmed_orders', 0) or 0),
                'delivered': int(orders_result.get('delivered_orders', 0) or 0),
                'cancelled': int(orders_result.get('cancelled_orders', 0) or 0)
            },
            'products': {
                'total': int(products_result.get('total_products', 0) or 0),
                'active': int(products_result.get('active_products', 0) or 0),
                'low_stock': int(products_result.get('low_stock_items', 0) or 0)
            },
            'financial': {
                'gross_revenue': round(product_revenue, 2),
                'commission_rate': commission_rate * 100,
                'commission_due': commission_due,
                'net_revenue': net_revenue
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in analytics_realtime: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@seller_bp.route('/bundles')
@role_required('seller')
def bundles():
    """Seller bundles management"""
    user = get_current_user()
    # TODO: Implement bundles functionality
    return render_template('seller/bundles.html')

# Real-time alert count endpoints
@seller_bp.route('/inventory/alerts/count', methods=['GET'])
@role_required('seller')
def get_low_stock_alerts_count():
    """Get count of low stock alerts in real-time"""
    try:
        user = get_current_user()
        
        # Get all products for this seller with low stock
        low_stock_products = Product.query.filter_by(
            seller_id=user['id'],
            status='active'
        ).filter(
            Product.stock <= Product.reorder_level
        ).all()
        
        count = len(low_stock_products) if low_stock_products else 0
        
        return jsonify({
            'success': True,
            'count': count,
            'new_alerts': [{'id': p.id, 'name': p.name, 'stock': p.stock} for p in (low_stock_products[:5] if low_stock_products else [])]
        })
    except Exception as e:
        current_app.logger.error(f'Error getting low stock alerts: {str(e)}')
        return jsonify({'success': False, 'count': 0, 'error': str(e)}), 500

@seller_bp.route('/orders/count', methods=['GET'])
@api_role_required('seller')
def get_pending_orders_count():
    """Get count of pending orders in real-time"""
    try:
        user = get_current_user()
        current_app.logger.info(f"orders/count endpoint called by user {user['id']}")
        
        db_service = Database()
        
        # Get pending orders for this seller
        # Count distinct orders where seller has items and status is pending/confirmed
        result = db_service.execute_query("""
            SELECT COUNT(DISTINCT o.id) as count
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            WHERE oi.seller_id = %s
            AND o.status IN ('pending', 'confirmed')
        """, (user['id'],), fetch=True, fetchone=True)
        
        count = result['count'] if result else 0
        current_app.logger.info(f"Pending orders count for seller {user['id']}: {count}")
        
        return jsonify({
            'success': True,
            'count': count
        })
    except Exception as e:
        current_app.logger.error(f'Error getting pending orders count: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'count': 0, 'error': str(e)}), 500