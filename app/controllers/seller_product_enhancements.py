"""
Seller Product Enhancements Controller
Handles: bulk upload, variants, cloning, inventory management, bundles
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from app.utils.decorators import login_required, seller_required
from app.models.user import User
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.product_bundle import ProductBundle
from app.models.inventory import Inventory
from app.services.email_service import EmailService
from app.services.database import Database
from datetime import datetime
from werkzeug.utils import secure_filename
import os

seller_enhancements_bp = Blueprint('seller_enhancements', __name__)

# ==================== PRODUCT VARIANTS ====================

@seller_enhancements_bp.route('/product/<int:product_id>/variants')
@login_required
@seller_required
def manage_variants(product_id):
    """Manage variants for a product"""
    seller_id = session['user_id']
    
    product = Product.get_by_id(product_id)
    
    if not product or product['seller_id'] != seller_id:
        flash('Product not found or unauthorized', 'error')
        return redirect(url_for('seller.products'))
    
    variants = ProductVariant.get_by_product(product_id, status=None)
    
    return render_template('seller/product_variants.html', product=product, variants=variants)

@seller_enhancements_bp.route('/product/<int:product_id>/variant/add', methods=['POST'])
@login_required
@seller_required
def add_variant(product_id):
    """Add a new variant to a product"""
    seller_id = session['user_id']
    
    product = Product.get_by_id(product_id)
    
    if not product or product['seller_id'] != seller_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        data = request.get_json() or request.form.to_dict()
        
        variant = ProductVariant.create(
            product_id=product_id,
            name=data.get('name'),
            price=float(data.get('price', 0)),
            sku=data.get('sku'),
            sale_price=float(data.get('sale_price')) if data.get('sale_price') else None,
            stock_quantity=int(data.get('stock_quantity', 0)),
            image_url=data.get('image_url'),
            attributes=data.get('attributes', {}),
            display_order=int(data.get('display_order', 0))
        )
        
        return jsonify({'success': True, 'variant': variant})
        
    except Exception as e:
        current_app.logger.error(f"Add variant error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@seller_enhancements_bp.route('/variant/<int:variant_id>/edit', methods=['POST'])
@login_required
@seller_required
def edit_variant(variant_id):
    """Edit a variant"""
    seller_id = session['user_id']
    
    variant = ProductVariant.get_by_id(variant_id)
    if not variant:
        return jsonify({'success': False, 'error': 'Variant not found'}), 404
    
    product = Product.get_by_id(variant['product_id'])
    if not product or product['seller_id'] != seller_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        data = request.get_json() or request.form.to_dict()
        
        update_data = {}
        for field in ['name', 'sku', 'price', 'sale_price', 'stock_quantity', 'image_url', 'display_order', 'status']:
            if field in data:
                update_data[field] = data[field]
        
        if 'attributes' in data:
            update_data['attributes'] = data['attributes']
        
        success = ProductVariant.update(variant_id, **update_data)
        
        return jsonify({'success': success})
        
    except Exception as e:
        current_app.logger.error(f"Edit variant error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@seller_enhancements_bp.route('/variant/<int:variant_id>/delete', methods=['POST'])
@login_required
@seller_required
def delete_variant(variant_id):
    """Delete a variant"""
    seller_id = session['user_id']
    
    variant = ProductVariant.get_by_id(variant_id)
    if not variant:
        return jsonify({'success': False, 'error': 'Variant not found'}), 404
    
    product = Product.get_by_id(variant['product_id'])
    if not product or product['seller_id'] != seller_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        success = ProductVariant.delete(variant_id)
        return jsonify({'success': success})
    except Exception as e:
        current_app.logger.error(f"Delete variant error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== INVENTORY MANAGEMENT ====================

@seller_enhancements_bp.route('/inventory')
@login_required
@seller_required
def inventory_dashboard():
    """Inventory management dashboard"""
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

@seller_enhancements_bp.route('/inventory/alerts')
@login_required
@seller_required
def low_stock_alerts():
    """View low stock alerts"""
    seller_id = session['user_id']
    
    alerts = Inventory.get_low_stock_alerts(seller_id, acknowledged=request.args.get('show_all') == '1')
    
    return render_template('seller/low_stock_alerts.html', alerts=alerts)

@seller_enhancements_bp.route('/inventory/alert/<int:alert_id>/acknowledge', methods=['POST'])
@login_required
@seller_required
def acknowledge_alert(alert_id):
    """Acknowledge a low stock alert"""
    try:
        success = Inventory.acknowledge_alert(alert_id)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@seller_enhancements_bp.route('/inventory/bulk-update', methods=['POST'])
@login_required
@seller_required
def bulk_stock_update():
    """Bulk update stock quantities"""
    seller_id = session['user_id']
    
    try:
        data = request.get_json()
        updates = data.get('updates', [])
        
        # Validate seller owns all products
        for update in updates:
            product = Product.get_by_id(update['product_id'])
            if not product or product['seller_id'] != seller_id:
                return jsonify({'success': False, 'error': f"Unauthorized for product {update['product_id']}"}), 403
        
        results = Inventory.bulk_update_stock(updates, created_by=seller_id)
        
        return jsonify({'success': True, 'results': results})
        
    except Exception as e:
        current_app.logger.error(f"Bulk stock update error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@seller_enhancements_bp.route('/inventory/product/<int:product_id>/history')
@login_required
@seller_required
def stock_history(product_id):
    """View stock movement history for a product"""
    seller_id = session['user_id']
    
    product = Product.get_by_id(product_id)
    
    if not product or product['seller_id'] != seller_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    history = Inventory.get_product_history(product_id, limit=100)
    
    if request.headers.get('Accept') == 'application/json':
        return jsonify({'success': True, 'history': history})
    
    return render_template('seller/stock_history.html', product=product, history=history)

@seller_enhancements_bp.route('/inventory/product/<int:product_id>/threshold', methods=['POST'])
@login_required
@seller_required
def update_threshold(product_id):
    """Update low stock threshold for a product"""
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

@seller_enhancements_bp.route('/inventory/valuation')
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

# ==================== PRODUCT BUNDLES ====================

@seller_enhancements_bp.route('/bundles')
@login_required
@seller_required
def bundles_list():
    """List all bundles"""
    seller_id = session['user_id']
    
    bundles = ProductBundle.get_by_seller(seller_id, status=None)
    products = Product.list(seller_id=seller_id, status='active')
    
    return render_template('seller/bundles.html', bundles=bundles, products=products)

@seller_enhancements_bp.route('/bundle/add', methods=['POST'])
@login_required
@seller_required
def add_bundle():
    """Create a new bundle"""
    seller_id = session['user_id']
    
    try:
        data = request.form.to_dict()
        
        # Parse bundle items JSON
        import json
        bundle_items = json.loads(data.get('bundle_items', '[]'))
        
        bundle = ProductBundle.create(
            seller_id=seller_id,
            name=data.get('bundle_name'),
            description=data.get('bundle_description'),
            bundle_price=float(data.get('bundle_price', 0)),
            discount_percentage=float(data.get('discount_percentage', 0)) if data.get('discount_percentage') else None,
            image_url=data.get('image_url')
        )
        
        # Add items to bundle
        if bundle and bundle_items:
            for item in bundle_items:
                ProductBundle.add_item(
                    bundle['id'],
                    item.get('product_id'),
                    item.get('variant_id'),
                    item.get('quantity', 1)
                )
        
        flash('Bundle created successfully', 'success')
        
    except Exception as e:
        current_app.logger.error(f"Add bundle error: {e}")
        flash('Error creating bundle', 'error')
    
    return redirect(url_for('seller_enhancements.bundles_list'))

@seller_enhancements_bp.route('/bundle/<int:bundle_id>/edit', methods=['POST'])
@login_required
@seller_required
def edit_bundle(bundle_id):
    """Edit a bundle"""
    seller_id = session['user_id']
    
    bundle = ProductBundle.get_by_id(bundle_id)
    
    if not bundle or bundle['seller_id'] != seller_id:
        flash('Bundle not found or unauthorized', 'error')
        return redirect(url_for('seller_enhancements.bundles_list'))
    
    try:
        data = request.form.to_dict()
        
        success = ProductBundle.update(
            bundle_id,
            name=data.get('bundle_name'),
            description=data.get('bundle_description'),
            bundle_price=float(data.get('bundle_price', 0)),
            discount_percentage=float(data.get('discount_percentage', 0)) if data.get('discount_percentage') else None,
            status=data.get('status', 'active')
        )
        
        if success:
            flash('Bundle updated successfully', 'success')
        else:
            flash('Failed to update bundle', 'error')
            
    except Exception as e:
        current_app.logger.error(f"Edit bundle error: {e}")
        flash('Error updating bundle', 'error')
    
    return redirect(url_for('seller_enhancements.bundles_list'))

@seller_enhancements_bp.route('/bundle/<int:bundle_id>/delete', methods=['POST'])
@login_required
@seller_required
def delete_bundle(bundle_id):
    """Delete a bundle"""
    seller_id = session['user_id']
    
    bundle = ProductBundle.get_by_id(bundle_id)
    
    if not bundle or bundle['seller_id'] != seller_id:
        flash('Bundle not found or unauthorized', 'error')
        return redirect(url_for('seller_enhancements.bundles_list'))
    
    try:
        success = ProductBundle.delete(bundle_id)
        
        if success:
            flash('Bundle deleted successfully', 'success')
        else:
            flash('Failed to delete bundle', 'error')
            
    except Exception as e:
        current_app.logger.error(f"Delete bundle error: {e}")
        flash('Error deleting bundle', 'error')
    
    return redirect(url_for('seller_enhancements.bundles_list'))

# ==================== REORDER SUGGESTIONS ====================

@seller_enhancements_bp.route('/inventory/reorder-suggestions')
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
