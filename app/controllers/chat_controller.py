"""
Chat controller for live customer support.
Handles chat room creation, messaging, and support agent interface.
"""
from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for, flash
from app.models.chat import ChatRoom, ChatMessage
from app.utils.decorators import login_required
from app.utils.error_handler import handle_errors, get_logger
from app.services.websocket_service import socketio as sio
from app.services.chat_notifications import notify_new_chat_message
from app.services.database import Database
from datetime import datetime

chat_bp = Blueprint('chat', __name__)
logger = get_logger(__name__)

ROLE_TO_SENDER_ROLE = {
    'user': 'customer',
    'seller': 'seller',
    'admin': 'admin',
    'support': 'admin',
    'rider': 'rider'
}


@chat_bp.route('/support')
@login_required
def support_chat():
    """Main customer support chat page - redirect directly to room"""
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    
    # If admin/support, redirect to admin rooms list instead of creating a room
    if user_role in ['admin', 'support']:
        return redirect(url_for('chat.admin_rooms'))

    from app.models.user import User

    # Sellers should be routed to a seller-admin chat
    if user_role == 'seller':
        return redirect(url_for('chat.seller_to_admin'))

    # Riders could share the same support channel as customers for now
    if user_role in ['user', 'rider']:
        admins = User.get_all_users(role='admin')
        if not admins:
            flash('No support agent available right now. Please try again later.', 'error')
            return redirect(url_for('public.browse_products'))

        admin = admins[0]
        room_id = ChatRoom.find_or_create_conversation(
            participant1_id=user_id,
            participant2_id=admin['id'],
            conversation_type='customer_admin',
            subject="Support Chat"
        )
        if room_id:
            return redirect(url_for('chat.view_room', room_id=room_id))

        flash('Failed to create support chat. Please try again.', 'error')
        return redirect(url_for('public.browse_products'))

    # Fallback: Get or create legacy chat room
    rooms = ChatRoom.get_user_rooms(user_id)
    if rooms:
        room = rooms[0]
        return redirect(url_for('chat.view_room', room_id=room['id']))

    room_id = ChatRoom.create(user_id, "Support Request")
    if room_id:
        return redirect(url_for('chat.view_room', room_id=room_id))

    flash('Failed to create chat room. Please try again.', 'error')
    return redirect(url_for('public.browse_products'))


@chat_bp.route('/rooms')
@login_required
def my_rooms():
    """View all user's chat rooms (excluding archived ones)"""
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    rooms = ChatRoom.get_user_rooms(user_id)
    
    # Filter out archived rooms
    rooms = [r for r in rooms if r.get('status') != 'archived']
    
    def _room_display_name(room):
        name = _get_chat_partner_name(room, user_id, user_role)
        if name:
            return name
        if room.get('conversation_type') == 'customer_admin':
            return 'Support Team'
        return room.get('subject') or f"Chat #{room.get('id')}"
    
    for room in rooms:
        room['display_name'] = _room_display_name(room)
        room['last_message_preview'] = room.get('last_message') or 'No messages yet'
        room['last_message_time_display'] = room.get('last_message_time')
    
    return render_template('chat/rooms.html', rooms=rooms)


def _get_chat_partner_name(room, current_user_id, current_role):
    """Return human-readable name for the other participant."""
    if not room:
        return None
    
    def _format(first, last):
        first = (first or '').strip()
        last = (last or '').strip()
        full = f"{first} {last}".strip()
        return full or None
    
    participant1_id = room.get('participant1_id') or room.get('user_id')
    participant2_id = room.get('participant2_id')
    
    if current_user_id and participant1_id and current_user_id == participant1_id:
        return _format(room.get('p2_first_name'), room.get('p2_last_name')) or room.get('other_participant_first_name')
    if current_user_id and participant2_id and current_user_id == participant2_id:
        return _format(room.get('p1_first_name'), room.get('p1_last_name')) or room.get('other_participant_first_name')
    
    # For admins/support who can view any room, default to participant1 (customer)
    if current_role in ['admin', 'support']:
        return _format(room.get('p1_first_name'), room.get('p1_last_name'))
    
    return None


@chat_bp.route('/room/<int:room_id>')
@login_required
def view_room(room_id):
    """View specific chat room"""
    user_id = session.get('user_id')
    room = ChatRoom.get_by_id(room_id)
    
    if not room:
        return render_template('error.html', error="Chat room not found"), 404
    
    # Check if user has access to this room
    user_role = session.get('user_role')
    participant1_id = room.get('participant1_id') or room.get('user_id')
    participant2_id = room.get('participant2_id')
    
    # User must be a participant or admin
    is_participant = (participant1_id == user_id) or (participant2_id == user_id)
    if not is_participant and user_role not in ['admin', 'support']:
        return render_template('error.html', error="Access denied"), 403
    
    # Mark messages as read
    ChatMessage.mark_as_read(room_id, user_id)
    
    # Get messages
    messages = ChatMessage.get_messages(room_id)
    
    # Determine if user is support/admin (for backward compatibility)
    is_support = user_role in ['admin', 'support']
    
    chat_partner_name = _get_chat_partner_name(room, user_id, user_role)
    chat_title = chat_partner_name or room.get('subject') or f"Chat #{room_id}"
    
    return render_template(
        'chat/room.html',
        room=room,
        messages=messages,
        is_support=is_support,
        chat_title=chat_title
    )


@chat_bp.route('/admin/rooms')
@login_required
def admin_rooms():
    """Support agent interface - view all active rooms"""
    user_role = session.get('user_role')
    
    if user_role not in ['admin', 'support']:
        return render_template('error.html', error="Access denied"), 403
    
    rooms = ChatRoom.get_active_rooms()
    
    return render_template('chat/admin_rooms.html', rooms=rooms)


@chat_bp.route('/admin/messages')
@login_required
def admin_messages():
    """Admin interface - view all seller messages"""
    user_role = session.get('user_role')
    
    if user_role not in ['admin', 'support']:
        return render_template('error.html', error="Access denied"), 403
    
    rooms = ChatRoom.get_seller_admin_rooms()
    
    return render_template('chat/admin_messages.html', rooms=rooms)


# API Endpoints

@chat_bp.route('/api/room/create', methods=['POST'])
@login_required
@handle_errors("Failed to create chat room")
def api_create_room():
    """API: Create new chat room"""
    user_id = session.get('user_id')
    data = request.get_json()
    
    subject = data.get('subject', 'Support Request')
    
    room_id = ChatRoom.create(user_id, subject)
    
    if room_id:
        room = ChatRoom.get_by_id(room_id)
        logger.info(f"Created chat room {room_id} for user {user_id}")
        return jsonify({'success': True, 'room_id': room_id, 'room': room})
    else:
        return jsonify({'success': False, 'error': 'Failed to create chat room'}), 500


@chat_bp.route('/api/room/<int:room_id>/messages', methods=['GET'])
@login_required
@handle_errors("Failed to fetch messages")
def api_get_messages(room_id):
    """API: Get messages for a room"""
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    
    room = ChatRoom.get_by_id(room_id)
    
    if not room:
        return jsonify({'success': False, 'error': 'Room not found'}), 404
    
    # Check access - user must be participant
    participant1_id = room.get('participant1_id') or room.get('user_id')
    participant2_id = room.get('participant2_id')
    is_participant = (participant1_id == user_id) or (participant2_id == user_id)
    
    if not is_participant and user_role not in ['admin', 'support']:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    messages = ChatMessage.get_messages(room_id)
    
    return jsonify({'success': True, 'messages': messages})


@chat_bp.route('/api/room/<int:room_id>/send', methods=['POST'])
@login_required
@handle_errors("Failed to send message")
def api_send_message(room_id):
    """API: Send message to room"""
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    data = request.get_json()
    
    message_text = data.get('message', '').strip()
    
    if not message_text:
        return jsonify({'success': False, 'error': 'Message cannot be empty'}), 400
    
    room = ChatRoom.get_by_id(room_id)
    
    if not room:
        return jsonify({'success': False, 'error': 'Room not found'}), 404
    
    # Check access - user must be participant
    participant1_id = room.get('participant1_id') or room.get('user_id')
    participant2_id = room.get('participant2_id')
    is_participant = (participant1_id == user_id) or (participant2_id == user_id)
    
    if not is_participant and user_role not in ['admin', 'support']:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    # Determine if this is a support message (for backward compatibility)
    is_support = user_role in ['admin', 'support']
    sender_role = ROLE_TO_SENDER_ROLE.get(user_role, 'customer')
    
    message_id = ChatMessage.create(
        room_id,
        user_id,
        message_text,
        is_support,
        sender_role=sender_role
    )
    
    if message_id:
        logger.info(f"Message sent to room {room_id} by user {user_id}")
        
        # Get user info for real-time broadcast
        from app.models.user import User
        sender = User.get_by_id(user_id)
        sender_name = f"{(sender.get('first_name','') or '').strip()} {(sender.get('last_name','') or '').strip()}".strip() if sender else 'User'
        
        message_data = {
            'id': message_id,
            'room_id': room_id,
            'user_id': user_id,
            'user_name': sender_name or 'User',
            'user_role': user_role,
            'message': message_text,
            'is_support': is_support,
            'sender_role': sender_role,
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to participants of this chat room via WebSocket
        sio.emit('new_message', message_data, room=f'chat_{room_id}')
        
        # Notify other participants/admins
        try:
            notify_new_chat_message(room, user_id, sender_name, message_text, message_data['timestamp'])
        except Exception as e:
            logger.warning(f"Failed to create notifications: {e}")
            
        return jsonify({'success': True, 'message_id': message_id})
    else:
        return jsonify({'success': False, 'error': 'Failed to send message'}), 500


@chat_bp.route('/api/room/<int:room_id>/close', methods=['POST'])
@login_required
@handle_errors("Failed to close room")
def api_close_room(room_id):
    """API: Close chat room"""
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    
    room = ChatRoom.get_by_id(room_id)
    
    if not room:
        return jsonify({'success': False, 'error': 'Room not found'}), 404
    
    # Only participant or admin can close
    participant1_id = room.get('participant1_id') or room.get('user_id')
    participant2_id = room.get('participant2_id')
    is_participant = (participant1_id == user_id) or (participant2_id == user_id)
    
    if not is_participant and user_role not in ['admin', 'support']:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    if ChatRoom.update_status(room_id, 'closed'):
        logger.info(f"Chat room {room_id} closed by user {user_id}")
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Failed to close room'}), 500


@chat_bp.route('/api/room/<int:room_id>/delete', methods=['POST'])
@login_required
def api_delete_room(room_id):
    """API: Delete/archive chat room for current user"""
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    
    room = ChatRoom.get_by_id(room_id)
    
    if not room:
        return jsonify({'success': False, 'error': 'Room not found'}), 404
    
    # Only participant or admin can delete
    participant1_id = room.get('participant1_id') or room.get('user_id')
    participant2_id = room.get('participant2_id')
    is_participant = (participant1_id == user_id) or (participant2_id == user_id)
    
    if not is_participant and user_role not in ['admin', 'support']:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    # Mark room as archived
    try:
        db = Database()
        db.execute_query(
            "UPDATE chat_rooms SET status = 'archived', updated_at = NOW() WHERE id = %s",
            (room_id,)
        )
        logger.info(f"Chat room {room_id} archived by user {user_id}")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Failed to delete room {room_id}: {e}")
        return jsonify({'success': False, 'error': 'Failed to delete room'}), 500


@chat_bp.route('/api/room/<int:room_id>/mark-read', methods=['POST'])
@login_required
@handle_errors("Failed to mark messages as read")
def api_mark_read(room_id):
    """API: Mark messages as read"""
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    
    room = ChatRoom.get_by_id(room_id)
    
    if not room:
        return jsonify({'success': False, 'error': 'Room not found'}), 404
    
    # Check access - user must be participant1 or participant2
    if room.get('participant1_id') != user_id and room.get('participant2_id') != user_id:
        if user_role not in ['admin', 'support']:
            return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    if ChatMessage.mark_as_read(room_id, user_id):
        # Emit WebSocket event to update read status
        sio.emit('messages_read', {
            'user_id': user_id,
            'room_id': room_id
        }, room=f'chat_{room_id}')
        
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Failed to mark as read'}), 500


@chat_bp.route('/api/unread-count', methods=['GET'])
@login_required
@handle_errors("Failed to get unread count")
def api_unread_count():
    """API: Get unread message count"""
    user_id = session.get('user_id')
    count = ChatMessage.get_unread_count(user_id, session.get('user_role'))
    
    return jsonify({'success': True, 'count': count})


# ============================================
# NEW MULTI-PARTICIPANT CHAT ROUTES
# ============================================

@chat_bp.route('/customer/seller/<int:seller_id>')
@login_required
def customer_to_seller(seller_id):
    """Start or view chat with a seller (customer only)"""
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    
    if user_role != 'user':
        flash('Only customers can chat with sellers.', 'error')
        return redirect(url_for('public.browse_products'))
    
    # Verify seller exists
    from app.models.user import User
    seller = User.get_by_id(seller_id)
    if not seller or seller.get('role') != 'seller':
        flash('Seller not found.', 'error')
        return redirect(url_for('public.browse_products'))
    
    # Find or create conversation
    room_id = ChatRoom.find_or_create_conversation(
        participant1_id=user_id,
        participant2_id=seller_id,
        conversation_type='customer_seller',
        subject=f"Chat with {seller.get('first_name', '')} {seller.get('last_name', '')}"
    )
    
    if room_id:
        return redirect(url_for('chat.view_room', room_id=room_id))
    else:
        flash('Failed to create chat room.', 'error')
        return redirect(url_for('public.browse_products'))


@chat_bp.route('/seller/admin')
@login_required
def seller_to_admin():
    """Start or view chat with admin (seller only)"""
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    
    if user_role != 'seller':
        flash('Only sellers can chat with admin.', 'error')
        return redirect(url_for('public.browse_products'))
    
    # Get first admin user
    from app.models.user import User
    admins = User.get_all_users(role='admin')
    if not admins:
        flash('No admin available.', 'error')
        return redirect(url_for('seller.dashboard'))
    
    admin = admins[0]
    
    # Find or create conversation
    room_id = ChatRoom.find_or_create_conversation(
        participant1_id=user_id,
        participant2_id=admin['id'],
        conversation_type='seller_admin',
        subject="Chat with Admin"
    )
    
    if room_id:
        return redirect(url_for('chat.view_room', room_id=room_id))
    else:
        flash('Failed to create chat room.', 'error')
        return redirect(url_for('seller.dashboard'))


@chat_bp.route('/seller/rider/<int:rider_id>')
@login_required
def seller_to_rider(rider_id):
    """Start or view chat with a rider (seller only)"""
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    
    if user_role != 'seller':
        flash('Only sellers can chat with riders.', 'error')
        return redirect(url_for('public.browse_products'))
    
    # Verify rider exists
    from app.models.user import User
    rider = User.get_by_id(rider_id)
    if not rider or rider.get('role') != 'rider':
        flash('Rider not found.', 'error')
        return redirect(url_for('seller.dashboard'))
    
    # Find or create conversation
    room_id = ChatRoom.find_or_create_conversation(
        participant1_id=user_id,
        participant2_id=rider_id,
        conversation_type='seller_rider',
        subject=f"Chat with Rider: {rider.get('first_name', '')} {rider.get('last_name', '')}"
    )
    
    if room_id:
        return redirect(url_for('chat.view_room', room_id=room_id))
    else:
        flash('Failed to create chat room.', 'error')
        return redirect(url_for('seller.dashboard'))


@chat_bp.route('/customer/rider/<int:rider_id>')
@login_required
def customer_to_rider(rider_id):
    """Start or view chat with a rider (customer only)"""
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    
    if user_role != 'user':
        flash('Only customers can chat with riders.', 'error')
        return redirect(url_for('public.browse_products'))
    
    # Verify rider exists
    from app.models.user import User
    rider = User.get_by_id(rider_id)
    if not rider or rider.get('role') != 'rider':
        flash('Rider not found.', 'error')
        return redirect(url_for('user.orders'))
    
    # Find or create conversation
    room_id = ChatRoom.find_or_create_conversation(
        participant1_id=user_id,
        participant2_id=rider_id,
        conversation_type='customer_rider',
        subject=f"Chat with Rider: {rider.get('first_name', '')} {rider.get('last_name', '')}"
    )
    
    if room_id:
        return redirect(url_for('chat.view_room', room_id=room_id))
    else:
        flash('Failed to create chat room.', 'error')
        return redirect(url_for('user.orders'))


@chat_bp.route('/api/conversations')
@login_required
def api_get_conversations():
    """API: Get all conversations for current user, grouped by type"""
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    
    conversations = {
        'customer_seller': [],
        'seller_admin': [],
        'seller_rider': [],
        'customer_rider': [],
        'customer_admin': []
    }
    
    # Get all user's conversations
    all_rooms = ChatRoom.get_user_rooms(user_id)
    
    for room in all_rooms:
        conv_type = room.get('conversation_type', 'customer_admin')
        if conv_type in conversations:
            conversations[conv_type].append(room)
    
    return jsonify({'success': True, 'conversations': conversations})


@chat_bp.route('/api/start-conversation', methods=['POST'])
@login_required
@handle_errors("Failed to start conversation")
def api_start_conversation():
    """API: Start a new conversation"""
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    data = request.get_json()
    
    participant2_id = data.get('participant2_id', type=int)
    conversation_type = data.get('conversation_type')
    related_order_id = data.get('related_order_id', type=int)
    subject = data.get('subject')
    
    if not participant2_id or not conversation_type:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    # Validate conversation type based on user role
    valid_types = {
        'user': ['customer_seller', 'customer_rider', 'customer_admin'],
        'seller': ['seller_admin', 'seller_rider', 'customer_seller'],
        'admin': ['seller_admin', 'customer_admin'],
        'rider': ['seller_rider', 'customer_rider']
    }
    
    if conversation_type not in valid_types.get(user_role, []):
        return jsonify({'success': False, 'error': 'Invalid conversation type for your role'}), 400
    
    # Find or create conversation
    room_id = ChatRoom.find_or_create_conversation(
        participant1_id=user_id,
        participant2_id=participant2_id,
        conversation_type=conversation_type,
        related_order_id=related_order_id,
        subject=subject
    )
    
    if room_id:
        room = ChatRoom.get_by_id(room_id)
        return jsonify({'success': True, 'room_id': room_id, 'room': room})
    else:
        return jsonify({'success': False, 'error': 'Failed to create conversation'}), 500


@chat_bp.route('/api/order/<int:order_id>/chat')
@login_required
def api_get_order_chat(order_id):
    """API: Get or create chat room for an order"""
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    
    from app.models.order import Order
    from app.services.database import Database
    order = Order.get_by_id(order_id)
    
    if not order:
        return jsonify({'success': False, 'error': 'Order not found'}), 404
    
    # Check if user has access to this order
    if user_role == 'user' and order.get('user_id') != user_id:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    if user_role == 'seller' and order.get('seller_id') != user_id:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    # Determine conversation type and participants
    if user_role == 'user':
        # Customer wants to chat with seller - get seller_id from order_items
        conversation_type = 'customer_seller'
        db = Database()
        seller_item = db.execute_query(
            "SELECT DISTINCT seller_id FROM order_items WHERE order_id = %s LIMIT 1",
            (order_id,),
            fetch=True,
            fetchone=True
        )
        if seller_item and seller_item.get('seller_id'):
            participant2_id = seller_item.get('seller_id')
        else:
            participant2_id = order.get('seller_id')
    elif user_role == 'seller':
        # Seller wants to chat with customer
        conversation_type = 'customer_seller'
        participant2_id = order.get('user_id')
    else:
        return jsonify({'success': False, 'error': 'Invalid user role for order chat'}), 400
    
    # Find or create conversation
    room_id = ChatRoom.find_or_create_conversation(
        participant1_id=user_id,
        participant2_id=participant2_id,
        conversation_type=conversation_type,
        related_order_id=order_id,
        subject=f"Order #{order.get('order_number', order_id)}"
    )
    
    if room_id:
        room = ChatRoom.get_by_id(room_id)
        return jsonify({'success': True, 'room_id': room_id, 'room': room})
    else:
        return jsonify({'success': False, 'error': 'Failed to create chat room'}), 500


@chat_bp.route('/api/order/<int:order_id>/rider-chat')
@login_required
def api_get_rider_chat(order_id):
    """API: Get or create chat room between customer and rider"""
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    
    from app.models.order import Order
    order = Order.get_by_id(order_id)
    
    if not order:
        return jsonify({'success': False, 'error': 'Order not found'}), 404
    
    # Only customers and riders can use this endpoint
    if user_role not in ['user', 'rider']:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    # Customer wants to chat with rider
    if user_role == 'user':
        if order.get('user_id') != user_id:
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        
        if not order.get('rider_id'):
            return jsonify({'success': False, 'error': 'No rider assigned to this order yet'}), 400
        
        participant2_id = order.get('rider_id')
    
    # Rider wants to chat with customer
    elif user_role == 'rider':
        if order.get('rider_id') != user_id:
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        
        participant2_id = order.get('user_id')
    
    else:
        return jsonify({'success': False, 'error': 'Invalid user role'}), 400
    
    # Find or create conversation with rider
    room_id = ChatRoom.find_or_create_conversation(
        participant1_id=user_id,
        participant2_id=participant2_id,
        conversation_type='customer_rider',
        related_order_id=order_id,
        subject=f"Order #{order.get('order_number', order_id)} - Delivery"
    )
    
    if room_id:
        room = ChatRoom.get_by_id(room_id)
        return jsonify({'success': True, 'room_id': room_id, 'room': room})
    else:
        return jsonify({'success': False, 'error': 'Failed to create chat room'}), 500


