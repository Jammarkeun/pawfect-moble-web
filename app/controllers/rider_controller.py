from flask import Blueprint, request, session, jsonify, current_app, render_template, flash, redirect, url_for
from functools import wraps
from app.utils.decorators import login_required
from app.services.database import Database
from datetime import datetime
import traceback
import os

rider_bp = Blueprint('rider', __name__)

def rider_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_role') != 'rider':
            return jsonify({
                'success': False,
                'message': 'Access denied. Riders only.',
                'error_type': 'authentication_error'
            }), 403
        return f(*args, **kwargs)
    return decorated_function

@rider_bp.route('/available-orders')
@login_required
@rider_required
def available_orders():
    """API endpoint to get available orders for pickup"""
    try:
        from app.services.database import Database
        from datetime import datetime
        
        db = Database()
        rider_id = session['user_id']
        current_app.logger.info(f'Fetching available orders for rider {rider_id}')
        
        # Mark rider as available
        try:
            # Check if rider exists in availability table
            rider_check = db.execute_query(
                "SELECT id FROM rider_availability WHERE rider_id = %s",
                (rider_id,),
                fetch=True
            )
            
            if rider_check:
                # Update existing rider
                db.execute_query(
                    """
                    UPDATE rider_availability 
                    SET is_online = 1, 
                        is_available = 1, 
                        last_online = %s 
                    WHERE rider_id = %s
                    """,
                    (datetime.utcnow(), rider_id)
                )
            else:
                # Insert new rider
                db.execute_query(
                    """
                    INSERT INTO rider_availability 
                    (rider_id, is_online, is_available, last_online)
                    VALUES (%s, 1, 1, %s)
                    """,
                    (rider_id, datetime.utcnow())
                )
                
        except Exception as e:
            current_app.logger.error(f'Error updating rider availability: {str(e)}')
        
        # Get available orders (not assigned to any rider and in a ready state)
        try:
            # Get available orders using raw SQL - include customer information
            query = """
                SELECT
                    o.id,
                    o.status,
                    o.seller_id,
                    o.user_id,
                    o.total_amount,
                    o.created_at,
                    o.updated_at,
                    o.shipping_address,
                    u.first_name as seller_first_name,
                    u.last_name as seller_last_name,
                    u.phone as seller_phone,
                    u.address as seller_address,
                    c.first_name as customer_first_name,
                    c.last_name as customer_last_name,
                    c.phone as customer_phone,
                    c.address as customer_address,
                    c.house_number,
                    c.street,
                    c.barangay,
                    c.city,
                    c.province,
                    c.country,
                    (SELECT COUNT(*) FROM order_items WHERE order_id = o.id) as item_count,
                    (SELECT SUM(quantity * price_at_time) FROM order_items WHERE order_id = o.id) as calculated_total
                FROM orders o
                JOIN users u ON o.seller_id = u.id
                LEFT JOIN users c ON o.user_id = c.id
                WHERE o.status IN ('confirmed', 'preparing', 'shipped')
                AND o.rider_id IS NULL
                ORDER BY o.created_at ASC
            """
            
            available_orders = db.execute_query(query, fetch=True) or []
            current_app.logger.info(f'Found {len(available_orders)} available orders')
            
            # Process orders
            orders_list = []
            for order in available_orders:
                try:
                    # Generate order number from ID
                    order_number = f'ORD-{order["id"]:05d}'
                    
                    # Get seller information
                    seller_info = {
                        'name': f"{order.get('seller_first_name', '')} {order.get('seller_last_name', '')}".strip() or 'Unknown Seller',
                        'address': order.get('seller_address', 'Not specified'),
                        'phone': order.get('seller_phone', 'Not specified')
                    }
                    
                    # Get customer information
                    customer_name = f"{order.get('customer_first_name', '')} {order.get('customer_last_name', '')}".strip() or 'Customer'
                    customer_phone = order.get('customer_phone', 'Not specified')
                    
                    # Build shipping address - prefer order.shipping_address, else compose from customer fields
                    shipping_address = order.get('shipping_address', '').strip()
                    if not shipping_address:
                        # Compose address from customer fields
                        parts = []
                        hn = order.get('house_number', '') or ''
                        st = order.get('street', '') or ''
                        if hn or st:
                            parts.append((hn + (' ' + st if st else '')).strip())
                        if order.get('barangay'):
                            parts.append('Barangay ' + order['barangay'])
                        if order.get('city'):
                            parts.append(order['city'])
                        if order.get('province'):
                            parts.append(order['province'])
                        if order.get('country'):
                            parts.append(order['country'])
                        shipping_address = ', '.join([p for p in parts if p]) or 'Address not specified'
                    
                    # Calculate total amount (use calculated_total if available, otherwise use total_amount)
                    total_amount = 0
                    if 'calculated_total' in order and order['calculated_total'] is not None:
                        try:
                            total_amount = float(order['calculated_total'])
                        except (ValueError, TypeError):
                            total_amount = float(order.get('total_amount', 0))
                    
                    # Format order data
                    order_data = {
                        'id': order['id'],
                        'order_number': order_number,
                        'status': order.get('status', 'unknown'),
                        'total_amount': total_amount,
                        'item_count': order.get('item_count', 0),
                        'created_at': order.get('created_at').isoformat() if order.get('created_at') else None,
                        'seller': seller_info,
                        'customer_name': customer_name,
                        'customer_phone': customer_phone,
                        'shipping_address': shipping_address
                    }
                    orders_list.append(order_data)
                    
                except Exception as e:
                    current_app.logger.error(f'Error processing order {order.get("id", "unknown")}: {str(e)}')
                    continue
            
            return jsonify({
                'success': True,
                'orders': orders_list
            })
            
        except Exception as e:
            current_app.logger.error(f'Error fetching available orders: {str(e)}', exc_info=True)
            return jsonify({
                'success': False,
                'message': 'Failed to fetch available orders',
                'error': str(e)
            }), 500
            
    except Exception as e:
        current_app.logger.error(f'Unexpected error in available_orders: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred',
            'error': str(e)
        }), 500


@rider_bp.route('/delivery/accept', methods=['POST'])
@login_required
@rider_required
def accept_delivery():
    """Accept a delivery order - First come first serve (with race condition protection)"""
    try:
        rider_id = session['user_id']
        order_id = request.form.get('order_id')
        
        if not order_id:
            return jsonify({'success': False, 'message': 'Order ID is required'}), 400
        
        db = Database()
        conn = db.connect()
        try:
            cursor = conn.cursor(dictionary=True)

            # 🔒 CRITICAL: Use FOR UPDATE to prevent double-assignment
            # Accept orders with status: confirmed, preparing, or shipped (matching available_orders query)
            cursor.execute("""
                SELECT id FROM orders 
                WHERE id = %s 
                AND status IN ('confirmed', 'preparing', 'shipped')
                AND (rider_id IS NULL OR rider_id = 0)
                FOR UPDATE
            """, (order_id,))
            order_check = cursor.fetchone()
            if not order_check:
                conn.rollback()
                current_app.logger.warning(f"Order {order_id} not available - may already be assigned or wrong status")
                return jsonify({
                    'success': False,
                    'message': 'Order is no longer available. It may have been assigned to another rider or the status has changed.'
                }), 409

            # Assign rider - system uses first-come-first-serve, so go directly to picked_up status
            # (No intermediate 'assigned_to_rider' status needed since rider self-accepts)
            cursor.execute("""
                UPDATE orders 
                SET rider_id = %s, status = 'picked_up', updated_at = NOW()
                WHERE id = %s
            """, (rider_id, order_id))
            
            # Verify the update was successful
            if cursor.rowcount == 0:
                conn.rollback()
                current_app.logger.error(f"Failed to update order {order_id} - rowcount is 0")
                return jsonify({
                    'success': False,
                    'message': 'Failed to assign order. Please try again.'
                }), 500

            # Create delivery record (use INSERT IGNORE or check if exists first)
            try:
                cursor.execute("""
                    INSERT INTO deliveries (order_id, rider_id, status, assigned_at)
                    VALUES (%s, %s, 'assigned', NOW())
                    ON DUPLICATE KEY UPDATE 
                        rider_id = VALUES(rider_id),
                        status = 'assigned',
                        assigned_at = NOW()
                """, (order_id, rider_id))
            except Exception as delivery_error:
                # If delivery record creation fails, log but don't fail the whole operation
                # since the order is already assigned
                current_app.logger.warning(f"Delivery record creation issue for order {order_id}: {delivery_error}")
                # Check if delivery already exists
                cursor.execute("""
                    SELECT id FROM deliveries WHERE order_id = %s
                """, (order_id,))
                if not cursor.fetchone():
                    # Only rollback if delivery doesn't exist and we couldn't create it
                    conn.rollback()
                    current_app.logger.error(f"Failed to create delivery record for order {order_id}")
                    return jsonify({
                        'success': False,
                        'message': 'Failed to create delivery record. Please contact support.'
                    }), 500

            conn.commit()

            # ✅ Notify other riders via GLOBAL socketio
            try:
                from app.services.websocket_service import socketio as ws_socketio
                if ws_socketio and hasattr(ws_socketio, 'emit'):
                    ws_socketio.emit('order_taken', {
                        'order_id': order_id,
                        'rider_id': rider_id
                    }, room='available_orders')
                    current_app.logger.info(f"Emitted order_taken event for order {order_id}")
                else:
                    current_app.logger.warning("SocketIO not available, skipping notification")
            except Exception as e:
                current_app.logger.error(f"Error emitting socketio event: {e}")

            return jsonify({'success': True, 'message': 'Delivery accepted successfully!'})

        except Exception as e:
            conn.rollback()
            current_app.logger.error(f"DB error in accept_delivery: {e}")
            return jsonify({'success': False, 'message': 'Database error'}), 500
        finally:
            conn.close()

    except Exception as e:
        current_app.logger.error(f"Unexpected error in accept_delivery: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@rider_bp.route('/order/<int:order_id>/details')
@login_required
@rider_required
def order_details(order_id):
    """Get detailed information about an order (for modal)"""
    try:
        current_app.logger.info(f"Fetching details for order ID: {order_id}")
        db = Database()

        # First check if order exists at all
        existence_check = db.execute_query("SELECT id, status, rider_id FROM orders WHERE id = %s", (order_id,), fetchone=True)
        if not existence_check:
            current_app.logger.warning(f"Order {order_id} does not exist in database")
            return jsonify({'success': False, 'message': 'Order not found'}), 404

        current_app.logger.info(f"Order {order_id} exists with status: {existence_check['status']}, rider_id: {existence_check['rider_id']}")

        order_query = """
            SELECT o.*,
                   CONCAT('ORD-', LPAD(o.id, 5, '0')) as order_number,
                   COALESCE(c.first_name, '') as customer_first_name,
                   COALESCE(c.last_name, 'Customer') as customer_last_name,
                   COALESCE(c.phone, 'N/A') as customer_phone,
                   COALESCE(c.email, 'N/A') as customer_email,
                   COALESCE(c.address, '') as customer_address,
                   c.house_number, c.street, c.barangay, c.city, c.province, c.country
            FROM orders o
            LEFT JOIN users c ON o.user_id = c.id
            WHERE o.id = %s
        """
        order = db.execute_query(order_query, (order_id,), fetchone=True)

        if not order:
            current_app.logger.error(f"Order {order_id} exists but detailed query returned no results")
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        
        order = dict(order)
        order['customer_name'] = f"{order['customer_first_name']} {order['customer_last_name']}".strip() or 'Customer'
        # Prefer order.shipping_address; else compose from user's structured fields
        if not order.get('shipping_address'):
            parts = []
            hn = order.get('house_number') or ''
            st = order.get('street') or ''
            if hn or st:
                parts.append((hn + (' ' + st if st else '')).strip())
            if order.get('barangay'):
                parts.append('Barangay ' + order['barangay'])
            if order.get('city'):
                parts.append(order['city'])
            if order.get('province'):
                parts.append(order['province'])
            if order.get('country'):
                parts.append(order['country'])
            order['shipping_address'] = ', '.join([p for p in parts if p])
        
        items_query = """
            SELECT oi.*, 
                   oi.price_at_time,
                   p.name, 
                   p.image_url
            FROM order_items oi
            LEFT JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = %s
        """
        items = db.execute_query(items_query, (order_id,), fetch=True) or []
        
        # Render HTML via template for cleaner structure
        html = render_template(
            'rider/partials/order_details.html',
            order=order,
            items=items
        )
        
        return jsonify({'success': True, 'html': html})
        
    except Exception as e:
        current_app.logger.error(f"Error fetching order details: {e}")
        return jsonify({'success': False, 'message': 'Failed to load order details'}), 500

@rider_bp.route('/delivery/update', methods=['POST'])
@login_required
@rider_required
def update_delivery():
    """Update delivery status and handle Proof of Delivery (POD)."""
    try:
        from app.services.websocket_service import socketio as ws_socketio
        from app.models.notification import Notification
        db = Database()
        rider_id = session.get('user_id')
        form = request.form

        delivery_id = form.get('delivery_id')
        order_id = form.get('order_id')
        new_status = (form.get('status') or '').lower().strip()
        # Normalize common aliases from UI
        aliases = {
            'on the way': 'on_the_way',
            'on-the-way': 'on_the_way',
            'ontheway': 'on_the_way',
            'in_transit': 'on_the_way',
            'in-transit': 'on_the_way',
            'complete': 'delivered',
            'completed': 'delivered',
            'done': 'delivered',
            'success': 'delivered',
            'fail': 'failed',
            'failed_delivery': 'failed'
        }
        new_status = aliases.get(new_status, new_status)
        notes = form.get('notes')
        recipient_name = form.get('recipient_name')
        cod_collected = form.get('cod_collected')
        delivered_lat = form.get('delivered_lat')
        delivered_lng = form.get('delivered_lng')
        failure_reason = form.get('failure_reason')

        if not new_status or new_status not in ['picked_up','on_the_way','delivered','failed']:
            return jsonify({'success': False, 'message': 'Invalid status'}), 400
        if new_status == 'failed' and not (form.get('failure_reason') or '').strip():
            return jsonify({'success': False, 'message': 'Failure reason is required when marking as failed'}), 400

        # Resolve delivery by order if delivery_id not provided
        if not delivery_id and order_id:
            row = db.execute_query("SELECT id FROM deliveries WHERE order_id = %s", (order_id,), fetch=True, fetchone=True)
            if row:
                delivery_id = row['id']

        if not delivery_id:
            return jsonify({'success': False, 'message': 'Delivery not found'}), 404

        # Handle uploads
        proof_photo_url = None
        signature_url = None
        upload_base = os.path.join('static', 'uploads', 'pod')
        os.makedirs(upload_base, exist_ok=True)

        if 'proof_photo' in request.files and getattr(request.files['proof_photo'], 'filename', ''):
            f = request.files['proof_photo']
            ext = os.path.splitext(f.filename)[1].lower() or '.jpg'
            filename = f"proof_{delivery_id}_{int(datetime.utcnow().timestamp())}{ext}"
            path = os.path.join(upload_base, filename)
            f.save(path)
            proof_photo_url = f"uploads/pod/{filename}"
        if 'signature' in request.files and getattr(request.files['signature'], 'filename', ''):
            f = request.files['signature']
            ext = os.path.splitext(f.filename)[1].lower() or '.png'
            filename = f"sign_{delivery_id}_{int(datetime.utcnow().timestamp())}{ext}"
            path = os.path.join(upload_base, filename)
            f.save(path)
            signature_url = f"uploads/pod/{filename}"

        # Build update parts
        set_parts = ["status = %s"]
        params = [new_status]
        if new_status == 'picked_up':
            set_parts.append("picked_up_at = NOW()")
        elif new_status == 'on_the_way':
            set_parts.append("on_the_way_at = NOW()")
        elif new_status == 'delivered':
            set_parts.append("delivered_at = NOW()")
        elif new_status == 'failed':
            set_parts.append("failed_at = NOW()")
        if notes:
            set_parts.append("delivery_notes = %s")
            params.append(notes)
        if recipient_name:
            set_parts.append("recipient_name = %s")
            params.append(recipient_name)
        if cod_collected:
            try:
                float(cod_collected)
                set_parts.append("cod_collected = %s")
                params.append(cod_collected)
            except Exception:
                pass
        if delivered_lat and delivered_lng:
            set_parts.append("delivered_lat = %s")
            set_parts.append("delivered_lng = %s")
            params.extend([delivered_lat, delivered_lng])
        if failure_reason and new_status == 'failed':
            set_parts.append("failure_reason = %s")
            params.append(failure_reason)
        if proof_photo_url:
            set_parts.append("proof_photo_url = %s")
            params.append(proof_photo_url)
        if signature_url:
            set_parts.append("signature_url = %s")
            params.append(signature_url)
        if new_status == 'delivered':
            set_parts.append("pod_submitted_at = NOW()")

        params.append(delivery_id)
        db.execute_query(f"UPDATE deliveries SET {', '.join(set_parts)} WHERE id = %s", params)

        # Update linked order
        order_row = db.execute_query("SELECT d.order_id AS order_id, o.payment_method AS payment_method, o.user_id AS user_id, o.seller_id AS seller_id FROM deliveries d JOIN orders o ON d.order_id = o.id WHERE d.id = %s", (delivery_id,), fetch=True, fetchone=True)
        if order_row:
            oid = order_row['order_id']
            buyer_id = order_row.get('user_id')
            seller_id = order_row.get('seller_id')
            if new_status == 'picked_up':
                db.execute_query("UPDATE orders SET status = 'picked_up', updated_at = NOW() WHERE id = %s", (oid,))
            elif new_status == 'on_the_way':
                db.execute_query("UPDATE orders SET status = 'on_the_way', updated_at = NOW() WHERE id = %s", (oid,))
            elif new_status == 'delivered':
                db.execute_query("UPDATE orders SET status = 'delivered', payment_status = CASE WHEN payment_method = 'cod' THEN 'paid' ELSE payment_status END, updated_at = NOW() WHERE id = %s", (oid,))
            elif new_status == 'failed':
                db.execute_query("UPDATE orders SET status = 'cancelled', updated_at = NOW() WHERE id = %s", (oid,))

            # Create notifications for buyer and seller
            try:
                title_map = {
                    'picked_up': 'Order picked up',
                    'on_the_way': 'Order on the way',
                    'delivered': 'Order delivered',
                    'failed': 'Delivery failed'
                }
                reason_txt = (failure_reason or '').strip()
                msg_map = {
                    'picked_up': f'Your order #{oid} has been picked up by the rider.',
                    'on_the_way': f'Your order #{oid} is now on the way.',
                    'delivered': f'Your order #{oid} has been delivered.',
                    'failed': f'Delivery for order #{oid} has failed.' + (f' Reason: {reason_txt}' if reason_txt else '')
                }
                title = title_map.get(new_status, 'Order update')
                message = msg_map.get(new_status, f'Order #{oid} status updated to {new_status}.')
                data_payload = {'order_id': oid, 'status': new_status, 'delivery_id': int(delivery_id)}
                if buyer_id:
                    Notification.create(buyer_id, 'user', 'order_status', title, message, related_id=oid, data=data_payload)
                if seller_id:
                    Notification.create(seller_id, 'seller', 'order_status', title, f'Order #{oid}: {message}', related_id=oid, data=data_payload)
            except Exception:
                pass

            # Emit socket events to buyer and seller rooms
            try:
                if ws_socketio and hasattr(ws_socketio, 'emit'):
                    if buyer_id:
                        ws_socketio.emit('order_status_updated', {'order_id': oid, 'status': new_status}, room=f'user_{buyer_id}')
                        ws_socketio.emit('notification', {'title': title, 'message': message, 'type': 'order_status', 'data': data_payload}, room=f'user_{buyer_id}')
                    if seller_id:
                        ws_socketio.emit('order_status_updated', {'order_id': oid, 'status': new_status}, room=f'seller_{seller_id}')
                        ws_socketio.emit('notification', {'title': title, 'message': f'Order #{oid}: {message}', 'type': 'order_status', 'data': data_payload}, room=f'seller_{seller_id}')
            except Exception:
                pass

        # Rider availability on delivery completion
        if new_status in ['delivered','failed']:
            try:
                db.execute_query("""
                    INSERT INTO rider_availability (rider_id, is_online, is_available, last_online)
                    VALUES (%s, 1, 1, NOW())
                    ON DUPLICATE KEY UPDATE is_online = 1, is_available = 1, last_online = NOW()
                """, (rider_id,))
            except Exception:
                pass

        # Notify via websockets
        try:
            if ws_socketio and hasattr(ws_socketio, 'emit'):
                ws_socketio.emit('delivery_status_update', {
                    'delivery_id': int(delivery_id),
                    'order_id': int(order_id) if order_id else None,
                    'status': new_status,
                    'recipient_name': recipient_name,
                    'cod_collected': float(cod_collected) if cod_collected else None
                }, broadcast=True)
        except Exception:
            pass

        return jsonify({'success': True, 'message': 'Delivery updated'})
    except Exception as e:
        current_app.logger.error(f"Error in update_delivery: {e}")
        return jsonify({'success': False, 'message': 'Failed to update delivery'}), 500

@rider_bp.route('/my-deliveries')
@login_required
@rider_required
def my_deliveries():
    """List rider accepted deliveries."""
    db = Database()
    rider_id = session.get('user_id')
    status = request.args.get('status')
    query = """
        SELECT d.*, o.shipping_address, o.total_amount,
               CONCAT('ORD-', LPAD(o.id, 5, '0')) as order_number,
               CONCAT(c.first_name, ' ', c.last_name) as customer_name,
               c.phone as customer_phone
        FROM deliveries d
        JOIN orders o ON d.order_id = o.id
        JOIN users c ON o.user_id = c.id
        WHERE d.rider_id = %s
    """
    params = [rider_id]
    if status:
        query += " AND d.status = %s"
        params.append(status)
    query += " ORDER BY d.assigned_at DESC"
    deliveries = db.execute_query(query, tuple(params), fetch=True) or []
    return render_template('rider/my_deliveries.html', deliveries=deliveries)

@rider_bp.route('/analytics-data')
@login_required
@rider_required
def analytics_data():
    db = Database()
    rider_id = session.get('user_id')
    # Deliveries per last 7 days
    deliveries_by_day = db.execute_query(
        """
        SELECT DATE(assigned_at) as day, COUNT(*) as count
        FROM deliveries
        WHERE rider_id = %s AND assigned_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        GROUP BY DATE(assigned_at)
        ORDER BY day ASC
        """,
        (rider_id,), fetch=True
    ) or []
    # Earnings per last 7 days
    earnings_by_day = db.execute_query(
        """
        SELECT DATE(created_at) as day, COALESCE(SUM(total_earning),0) as amount
        FROM rider_earnings
        WHERE rider_id = %s AND created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        GROUP BY DATE(created_at)
        ORDER BY day ASC
        """,
        (rider_id,), fetch=True
    ) or []
    # Status counts
    status_counts = db.execute_query(
        """
        SELECT status, COUNT(*) as count
        FROM deliveries
        WHERE rider_id = %s
        GROUP BY status
        """,
        (rider_id,), fetch=True
    ) or []
    return jsonify({ 'success': True, 'deliveries_by_day': deliveries_by_day, 'earnings_by_day': earnings_by_day, 'status_counts': status_counts })

@rider_bp.route('/api/analytics/realtime')
@login_required
@rider_required
def analytics_realtime():
    """Real-time analytics API endpoint for rider"""
    rider_id = session.get('user_id')
    db = Database()
    
    try:
        # Total earnings
        earnings_result = db.execute_query("""
            SELECT COALESCE(SUM(total_earning), 0) as total_earnings
            FROM rider_earnings
            WHERE rider_id = %s
        """, (rider_id,), fetchone=True)
        
        # Today's earnings
        today_earnings_result = db.execute_query("""
            SELECT COALESCE(SUM(total_earning), 0) as earnings
            FROM rider_earnings
            WHERE rider_id = %s AND DATE(created_at) = CURDATE()
        """, (rider_id,), fetchone=True)
        
        # This month's earnings
        month_earnings_result = db.execute_query("""
            SELECT COALESCE(SUM(total_earning), 0) as earnings
            FROM rider_earnings
            WHERE rider_id = %s AND MONTH(created_at) = MONTH(NOW())
            AND YEAR(created_at) = YEAR(NOW())
        """, (rider_id,), fetchone=True)
        
        # Delivery counts
        deliveries_result = db.execute_query("""
            SELECT 
                COUNT(*) as total_deliveries,
                SUM(CASE WHEN status = 'assigned' THEN 1 ELSE 0 END) as assigned,
                SUM(CASE WHEN status = 'picked_up' THEN 1 ELSE 0 END) as picked_up,
                SUM(CASE WHEN status = 'on_the_way' THEN 1 ELSE 0 END) as on_the_way,
                SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as delivered,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN status IN ('assigned', 'picked_up', 'on_the_way') THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as completed
            FROM deliveries
            WHERE rider_id = %s
        """, (rider_id,), fetchone=True)
        
        # Today's deliveries
        today_deliveries_result = db.execute_query("""
            SELECT 
                COUNT(*) as count,
                SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as completed_today
            FROM deliveries
            WHERE rider_id = %s AND DATE(assigned_at) = CURDATE()
        """, (rider_id,), fetchone=True)
        
        # Rating
        rating_result = db.execute_query("""
            SELECT 
                COALESCE(AVG(rating), 0) as avg_rating,
                COUNT(*) as total_ratings
            FROM rider_performance
            WHERE rider_id = %s
        """, (rider_id,), fetchone=True)
        
        return jsonify({
            'success': True,
            'earnings': {
                'total': round(float(earnings_result.get('total_earnings', 0) or 0), 2),
                'today': round(float(today_earnings_result.get('earnings', 0) or 0), 2),
                'this_month': round(float(month_earnings_result.get('earnings', 0) or 0), 2)
            },
            'deliveries': {
                'total': int(deliveries_result.get('total_deliveries', 0) or 0),
                'assigned': int(deliveries_result.get('assigned', 0) or 0),
                'picked_up': int(deliveries_result.get('picked_up', 0) or 0),
                'on_the_way': int(deliveries_result.get('on_the_way', 0) or 0),
                'delivered': int(deliveries_result.get('delivered', 0) or 0),
                'failed': int(deliveries_result.get('failed', 0) or 0),
                'pending': int(deliveries_result.get('pending', 0) or 0),
                'completed': int(deliveries_result.get('completed', 0) or 0)
            },
            'today': {
                'deliveries': int(today_deliveries_result.get('count', 0) or 0),
                'completed': int(today_deliveries_result.get('completed_today', 0) or 0)
            },
            'rating': {
                'average': round(float(rating_result.get('avg_rating', 0) or 0), 2),
                'total_ratings': int(rating_result.get('total_ratings', 0) or 0)
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in analytics_realtime: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@rider_bp.route('/api/update-location', methods=['POST'])
@login_required
@rider_required
def update_location():
    """Update rider's current location"""
    try:
        data = request.get_json()
        rider_id = session['user_id']
        
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        accuracy = data.get('accuracy')
        
        if latitude is None or longitude is None:
            return jsonify({'success': False, 'message': 'Missing latitude or longitude'}), 400
        
        db = Database()
        
        # Check if rider has an active delivery
        active_delivery = db.execute_query("""
            SELECT id FROM deliveries
            WHERE rider_id = %s AND status IN ('assigned', 'picked_up', 'on_the_way')
            LIMIT 1
        """, (rider_id,), fetchone=True)
        
        if active_delivery:
            # Update delivery location
            db.execute_query("""
                UPDATE deliveries
                SET on_the_way_at = NOW()
                WHERE id = %s AND status IN ('picked_up', 'on_the_way')
            """, (active_delivery['id'],))
        
        # Update or insert rider availability with GPS coordinates
        db.execute_query("""
            INSERT INTO rider_availability (rider_id, current_latitude, current_longitude, last_online, is_online)
            VALUES (%s, %s, %s, NOW(), 1)
            ON DUPLICATE KEY UPDATE
                current_latitude = VALUES(current_latitude),
                current_longitude = VALUES(current_longitude),
                last_online = NOW(),
                is_online = 1
        """, (rider_id, latitude, longitude))
        
        current_app.logger.info(f"Location updated for rider {rider_id}: ({latitude}, {longitude})")
        
        return jsonify({
            'success': True,
            'message': 'Location updated successfully',
            'location': {
                'latitude': latitude,
                'longitude': longitude,
                'accuracy': accuracy,
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error updating location: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@rider_bp.route('/earnings')
@login_required
@rider_required
def earnings():
    """Rider earnings and payouts page"""
    try:
        db = Database()
        rider_id = session.get('user_id')
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('status', '')
        per_page = 15
        
        # Get all earnings for counting
        count_query = "SELECT COUNT(*) as total FROM rider_earnings WHERE rider_id = %s"
        if status_filter:
            count_query += f" AND status = '{status_filter}'"
        
        count_result = db.execute_query(count_query, (rider_id,), fetchone=True) or {'total': 0}
        total_count = count_result.get('total', 0)
        total_pages = (total_count + per_page - 1) // per_page
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get paginated earnings
        earnings_list = []
        try:
            query = """
                SELECT re.*, CONCAT('ORD-', LPAD(re.order_id, 5, '0')) as order_number
                FROM rider_earnings re
                WHERE re.rider_id = %s
            """
            params = [rider_id]
            
            if status_filter:
                query += " AND re.status = %s"
                params.append(status_filter)
            
            query += " ORDER BY re.created_at DESC LIMIT %s OFFSET %s"
            params.extend([per_page, offset])
            
            earnings_list = db.execute_query(query, tuple(params), fetch=True) or []
        except Exception as e:
            current_app.logger.error(f"Error fetching earnings: {e}")
        
        # Calculate totals
        total_earnings = 0.00
        pending_earnings = 0.00
        paid_earnings = 0.00
        
        try:
            totals_query = """
                SELECT 
                    COALESCE(SUM(total_earning), 0) as total,
                    COALESCE(SUM(CASE WHEN status='pending' THEN total_earning ELSE 0 END), 0) as pending,
                    COALESCE(SUM(CASE WHEN status='paid' THEN total_earning ELSE 0 END), 0) as paid
                FROM rider_earnings
                WHERE rider_id = %s
            """
            totals = db.execute_query(totals_query, (rider_id,), fetchone=True) or {}
            total_earnings = float(totals.get('total', 0))
            pending_earnings = float(totals.get('pending', 0))
            paid_earnings = float(totals.get('paid', 0))
        except Exception as e:
            current_app.logger.error(f"Error calculating totals: {e}")
        
        # Get payout method
        payout_method = None
        try:
            user_query = "SELECT payout_method FROM users WHERE id = %s"
            user_result = db.execute_query(user_query, (rider_id,), fetchone=True) or {}
            payout_method = user_result.get('payout_method')
        except Exception:
            pass
        
        # Create a simple pagination object for template compatibility
        class SimplePagination:
            def __init__(self, page, pages, prev_num, next_num, has_prev, has_next):
                self.page = page
                self.pages = pages
                self.prev_num = prev_num if has_prev else None
                self.next_num = next_num if has_next else None
                self.has_prev = has_prev
                self.has_next = has_next
        
        pagination = SimplePagination(
            page=page,
            pages=total_pages,
            prev_num=page - 1 if page > 1 else None,
            next_num=page + 1 if page < total_pages else None,
            has_prev=page > 1,
            has_next=page < total_pages
        )
        
        return render_template('rider/earnings.html',
                             rider_id=rider_id,
                             earnings=earnings_list,
                             pagination=pagination,
                             status_filter=status_filter,
                             total_earnings=total_earnings,
                             pending_earnings=pending_earnings,
                             paid_earnings=paid_earnings,
                             payout_method=payout_method)
    except Exception as e:
        current_app.logger.error(f"Error in earnings page: {e}")
        flash('An error occurred while loading earnings.', 'error')
        
        # Return with minimal pagination
        class EmptyPagination:
            page = 1
            pages = 1
            prev_num = None
            next_num = None
            has_prev = False
            has_next = False
        
        return render_template('rider/earnings.html',
                             rider_id=session.get('user_id'),
                             earnings=[],
                             pagination=EmptyPagination(),
                             status_filter='',
                             total_earnings=0.00,
                             pending_earnings=0.00,
                             paid_earnings=0.00,
                             payout_method=None)

@rider_bp.route('/set-payout-method', methods=['POST'])
@login_required
@rider_required
def set_payout_method():
    """Set or update rider's payout method"""
    try:
        db = Database()
        rider_id = session.get('user_id')
        payout_method = request.form.get('payout_method', '').strip()
        
        if not payout_method:
            flash('Please select a payout method.', 'error')
            return redirect(url_for('rider.earnings'))
        
        # Build update query based on payout method
        if payout_method == 'bank_transfer':
            bank_name = request.form.get('bank_name', '').strip()
            account_number = request.form.get('account_number', '').strip()
            account_name = request.form.get('account_name', '').strip()
            
            if not all([bank_name, account_number, account_name]):
                flash('Please provide all bank details.', 'error')
                return redirect(url_for('rider.earnings'))
            
            update_query = """
                UPDATE users 
                SET payout_method = %s, bank_name = %s, account_number = %s, account_name = %s
                WHERE id = %s
            """
            db.execute_query(update_query, (payout_method, bank_name, account_number, account_name, rider_id))
            
        elif payout_method == 'gcash':
            gcash_number = request.form.get('gcash_number', '').strip()
            gcash_name = request.form.get('gcash_name', '').strip()
            
            if not all([gcash_number, gcash_name]):
                flash('Please provide GCash details.', 'error')
                return redirect(url_for('rider.earnings'))
            
            update_query = """
                UPDATE users 
                SET payout_method = %s, gcash_number = %s, gcash_name = %s
                WHERE id = %s
            """
            db.execute_query(update_query, (payout_method, gcash_number, gcash_name, rider_id))
            
        elif payout_method == 'cash_pickup':
            pickup_location = request.form.get('pickup_location', '').strip()
            
            update_query = """
                UPDATE users 
                SET payout_method = %s, pickup_location = %s
                WHERE id = %s
            """
            db.execute_query(update_query, (payout_method, pickup_location, rider_id))
        
        flash('Payout method updated successfully!', 'success')
        return redirect(url_for('rider.earnings'))
        
    except Exception as e:
        current_app.logger.error(f"Error setting payout method: {e}")
        flash('An error occurred while updating payout method.', 'error')
        return redirect(url_for('rider.earnings'))

@rider_bp.route('/request-payout', methods=['POST'])
@login_required
@rider_required
def request_payout():
    """Request a payout of pending earnings"""
    try:
        db = Database()
        rider_id = session.get('user_id')
        amount = request.form.get('amount', '0')
        payout_method = request.form.get('payout_method', '').strip()
        
        try:
            amount = float(amount)
        except ValueError:
            flash('Invalid amount entered.', 'error')
            return redirect(url_for('rider.earnings'))
        
        if amount <= 0:
            flash('Amount must be greater than zero.', 'error')
            return redirect(url_for('rider.earnings'))
        
        # Check payout method is selected
        if not payout_method:
            flash('Please select a payout method.', 'error')
            return redirect(url_for('rider.earnings'))
        
        # Validate payout method
        valid_methods = ['bank_transfer', 'gcash', 'cash_pickup']
        if payout_method not in valid_methods:
            flash('Invalid payout method selected.', 'error')
            return redirect(url_for('rider.earnings'))
        
        # Check pending earnings
        pending_query = """
            SELECT COALESCE(SUM(total_earning), 0) as pending
            FROM rider_earnings
            WHERE rider_id = %s AND status = 'pending'
        """
        pending_result = db.execute_query(pending_query, (rider_id,), fetchone=True) or {}
        pending_amount = float(pending_result.get('pending', 0))
        
        if amount > pending_amount:
            flash(f'Requested amount exceeds pending earnings (₱{pending_amount:.2f}).', 'error')
            return redirect(url_for('rider.earnings'))
        
        # Create payout request with payout method
        from datetime import datetime
        insert_query = """
            INSERT INTO payout_requests (rider_id, amount, payout_method, status, requested_at)
            VALUES (%s, %s, %s, 'pending', NOW())
        """
        db.execute_query(insert_query, (rider_id, amount, payout_method))
        
        flash(f'Payout request of ₱{amount:.2f} submitted successfully!', 'success')
        return redirect(url_for('rider.earnings'))
        
    except Exception as e:
        current_app.logger.error(f"Error requesting payout: {e}")
        flash('An error occurred while requesting payout.', 'error')
        return redirect(url_for('rider.earnings'))

@rider_bp.route('/dashboard')
@login_required
@rider_required
def dashboard():
    """Rider dashboard page"""
    try:
        db = Database()
        rider_id = session.get('user_id')
        
        deliveries = []
        try:
            deliveries_query = """
                SELECT d.*, o.shipping_address, o.total_amount,
                       CONCAT('ORD-', LPAD(o.id, 5, '0')) as order_number,
                       CONCAT(c.first_name, ' ', c.last_name) as customer_name,
                       c.phone as customer_phone
                FROM deliveries d
                JOIN orders o ON d.order_id = o.id
                JOIN users c ON o.user_id = c.id
                WHERE d.rider_id = %s
                ORDER BY d.assigned_at DESC
                LIMIT 20
            """
            deliveries = db.execute_query(deliveries_query, (rider_id,), fetch=True) or []
        except Exception as e:
            current_app.logger.error(f"Error fetching deliveries: {e}")
        
        stats = {'pending_deliveries': 0, 'completed_deliveries': 0, 'monthly_earnings': 0.00, 'avg_rating': 0.0}
        try:
            stats_query = """
                SELECT 
                    COUNT(CASE WHEN status IN ('assigned', 'picked_up', 'on_the_way') THEN 1 END) as pending_deliveries,
                    COUNT(CASE WHEN status = 'delivered' THEN 1 END) as completed_deliveries
                FROM deliveries 
                WHERE rider_id = %s
            """
            stats_result = db.execute_query(stats_query, (rider_id,), fetchone=True)
            if stats_result:
                stats.update(stats_result)
        except Exception as e:
            current_app.logger.error(f"Error fetching stats: {e}")
        
        # Earnings calculation this month
        try:
            earnings_query = """
                SELECT COALESCE(SUM(total_earning),0) AS monthly_earnings
                FROM rider_earnings
                WHERE rider_id = %s AND MONTH(created_at) = MONTH(NOW()) AND YEAR(created_at) = YEAR(NOW())
            """
            er = db.execute_query(earnings_query, (rider_id,), fetchone=True) or {}
            if er.get('monthly_earnings') is not None:
                stats['monthly_earnings'] = float(er['monthly_earnings'])
        except Exception:
            pass
        
        # Pending payout (pending earnings not yet paid out)
        pending_payout = 0.00
        try:
            payout_query = """
                SELECT COALESCE(SUM(total_earning),0) AS pending_payout
                FROM rider_earnings
                WHERE rider_id = %s AND status = 'pending'
            """
            pp = db.execute_query(payout_query, (rider_id,), fetchone=True) or {}
            if pp.get('pending_payout') is not None:
                pending_payout = float(pp['pending_payout'])
        except Exception:
            pass

        return render_template('rider/dashboard.html',
                             rider_id=rider_id,
                             deliveries=deliveries,
                             pending_payout=pending_payout,
                             **stats)
                           
    except Exception as e:
        current_app.logger.error(f"Error in rider dashboard: {e}")
        flash('An error occurred while loading the dashboard.', 'error')
        return render_template('rider/dashboard.html',
                             rider_id=session.get('user_id'),
                             deliveries=[],
                             pending_deliveries=0,
                             completed_deliveries=0,
                             monthly_earnings=0.00,
                             avg_rating=0.0)