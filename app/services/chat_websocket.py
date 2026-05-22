"""
WebSocket handlers for real-time chat functionality.
Provides instant messaging between customers and support agents.
"""
from flask_socketio import emit, join_room, leave_room
from flask import session, request
from app.models.chat import ChatMessage, ChatRoom
from app.services.chat_notifications import notify_new_chat_message
from app.utils.error_handler import get_logger
from datetime import datetime

logger = get_logger(__name__)
ROLE_TO_SENDER_ROLE = {
    'user': 'customer',
    'seller': 'seller',
    'admin': 'admin',
    'support': 'admin',
    'rider': 'rider'
}

def init_chat_websocket(socketio):
    """Initialize chat WebSocket event handlers"""

    @socketio.on('join_chat_room')
    def handle_join_room(data):
        """Join a chat room"""
        try:
            room_id = data.get('room_id')
            user_id = session.get('user_id')
            user_role = session.get('user_role')

            logger.info(f"[JOIN] Attempt - room_id={room_id}, user_id={user_id}, user_role={user_role}")

            if not room_id or not user_id:
                logger.warning(f"[JOIN] Rejected - missing room_id or user_id")
                emit('error', {'message': 'Invalid room or user'})
                return

            # Verify access to room
            room = ChatRoom.get_by_id(room_id)

            if not room:
                logger.warning(f"[JOIN] Rejected - room {room_id} not found")
                emit('error', {'message': 'Room not found'})
                return

            # Check if user is a participant in this room (new multi-participant schema)
            participant1_id = room.get('participant1_id') or room.get('user_id')
            participant2_id = room.get('participant2_id')

            is_participant = (participant1_id == user_id) or (participant2_id == user_id)
            is_admin = user_role in ['admin', 'support']
            is_rider = user_role == 'rider'

            logger.info(f"[JOIN] Room participants: p1={participant1_id}, p2={participant2_id}, requesting_user={user_id}, role={user_role}")

            if not is_participant and not is_admin and not is_rider:
                logger.warning(f"[JOIN] Rejected - access denied for user {user_id} role {user_role}")
                emit('error', {'message': 'Access denied'})
                return

            # Join the room
            join_room(f'chat_{room_id}')

            logger.info(f"[JOIN] SUCCESS - User {user_id} (role={user_role}) joined chat_{room_id}")

            emit('joined_room', {
                'room_id': room_id,
                'message': 'Successfully joined chat room',
                'user_role': user_role
            })

            # Notify others in the room
            emit('user_joined', {
                'user_id': user_id,
                'user_role': user_role,
                'timestamp': datetime.now().isoformat()
            }, room=f'chat_{room_id}', skip_sid=request.sid)

        except Exception as e:
            logger.error(f"[JOIN] Error joining chat room: {str(e)}", exc_info=True)
            emit('error', {'message': 'Failed to join room'})

    @socketio.on('leave_chat_room')
    def handle_leave_room(data):
        """Leave a chat room"""
        try:
            room_id = data.get('room_id')
            user_id = session.get('user_id')
            user_role = session.get('user_role')

            if not room_id:
                return

            leave_room(f'chat_{room_id}')

            logger.info(f"User {user_id} left chat room {room_id}")

            # Notify others
            emit('user_left', {
                'user_id': user_id,
                'user_role': user_role,
                'timestamp': datetime.now().isoformat()
            }, room=f'chat_{room_id}')

        except Exception as e:
            logger.error(f"Error leaving chat room: {str(e)}", exc_info=True)

    @socketio.on('send_chat_message')
    def handle_send_message(data):
        """Handle incoming chat message"""
        try:
            data = data or {}
            room_id = data.get('room_id')
            message_text = data.get('message', '').strip()
            user_id = session.get('user_id')
            user_role = session.get('user_role')

            if not room_id or not message_text or not user_id:
                emit('error', {'message': 'Invalid message data'})
                return

            # Verify access
            room = ChatRoom.get_by_id(room_id)

            if not room:
                emit('error', {'message': 'Room not found'})
                return

            # Check if user is a participant in this room (new multi-participant schema)
            participant1_id = room.get('participant1_id') or room.get('user_id')
            participant2_id = room.get('participant2_id')

            is_participant = (participant1_id == user_id) or (participant2_id == user_id)
            is_admin = user_role in ['admin', 'support']
            is_rider = user_role == 'rider'

            if not is_participant and not is_admin and not is_rider:
                emit('error', {'message': 'Access denied'})
                return

            # Save message to database
            is_support = user_role in ['admin', 'support', 'rider']
            sender_role = ROLE_TO_SENDER_ROLE.get(user_role, 'customer')
            message_id = ChatMessage.create(
                room_id,
                user_id,
                message_text,
                is_support,
                sender_role=sender_role
            )

            if not message_id:
                emit('error', {'message': 'Failed to save message'})
                return

            # Get user info
            from app.models.user import User
            user = User.get_by_id(user_id)

            # Broadcast message to room
            message_data = {
                'id': message_id,
                'room_id': room_id,
                'user_id': user_id,
                'user_name': f"{user.get('first_name', '')} {user.get('last_name', '')}" if user else 'User',
                'first_name': user.get('first_name', '') if user else '',
                'last_name': user.get('last_name', '') if user else '',
                'user_role': user_role,
                'message': message_text,
                'is_support': is_support,
                'sender_role': sender_role,
                'timestamp': datetime.now().isoformat()
            }

            logger.info(f"Message {message_id} sent to room {room_id} by user {user_id}")

            # Broadcast to entire room including sender
            emit('new_message', message_data, room=f'chat_{room_id}')

            # Notify offline participants/admins
            try:
                notify_new_chat_message(room, user_id, message_data['user_name'], message_text, message_data['timestamp'])
            except Exception as notify_err:
                logger.warning(f"Failed to send chat notifications (WS): {notify_err}")

        except Exception as e:
            logger.error(f"Error sending chat message: {str(e)}", exc_info=True)
            emit('error', {'message': 'Failed to send message'})

    @socketio.on('subscribe_notifications')
    def handle_subscribe_notifications(data):
        """Subscribe the socket to per-user rooms for notifications."""
        try:
            data = data or {}
            user_id = data.get('user_id') or session.get('user_id')
            role = data.get('role') or session.get('user_role')

            if not user_id:
                emit('error', {'message': 'Authentication required'})
                return

            join_room(f'user_{user_id}')

            if role == 'seller':
                join_room(f'seller_{user_id}')
            elif role == 'rider':
                join_room(f'rider_{user_id}')

            emit('subscribed_notifications', {
                'user_id': user_id,
                'role': role
            }, room=request.sid)

            logger.info(f"[NOTIF] User {user_id} subscribed to notifications (role={role})")

        except Exception as e:
            logger.error(f"[NOTIF] Failed to subscribe notifications: {str(e)}", exc_info=True)
            emit('error', {'message': 'Failed to subscribe to notifications'})

    @socketio.on('typing_chat')
    def handle_typing(data):
        """Handle typing indicator"""
        try:
            room_id = data.get('room_id')
            user_id = session.get('user_id')
            user_role = session.get('user_role')
            is_typing = data.get('is_typing', False)

            if not room_id or not user_id:
                return

            # Get user info
            from app.models.user import User
            user = User.get_by_id(user_id)

            # Broadcast typing status to room (except sender)
            emit('user_typing', {
                'user_id': user_id,
                'user_name': f"{user.get('first_name', '')} {user.get('last_name', '')}" if user else 'User',
                'user_role': user_role,
                'is_typing': is_typing
            }, room=f'chat_{room_id}', skip_sid=request.sid)

        except Exception as e:
            logger.error(f"Error handling typing indicator: {str(e)}", exc_info=True)

    @socketio.on('mark_chat_read')
    def handle_mark_read(data):
        """Mark messages as read"""
        try:
            room_id = data.get('room_id')
            user_id = session.get('user_id')
            user_role = session.get('user_role')

            if not room_id or not user_id:
                return

            # Verify access
            room = ChatRoom.get_by_id(room_id)

            if not room:
                return

            # Check if user is a participant in this room (new multi-participant schema)
            participant1_id = room.get('participant1_id') or room.get('user_id')
            participant2_id = room.get('participant2_id')

            is_participant = (participant1_id == user_id) or (participant2_id == user_id)
            is_admin = user_role in ['admin', 'support']
            is_rider = user_role == 'rider'

            if not is_participant and not is_admin and not is_rider:
                return

            is_support = user_role in ['admin', 'support', 'rider']
            ChatMessage.mark_as_read(room_id, user_id)

            # Notify room that messages were read
            emit('messages_read', {
                'user_id': user_id,
                'user_role': user_role,
                'room_id': room_id
            }, room=f'chat_{room_id}')

        except Exception as e:
            logger.error(f"Error marking messages as read: {str(e)}", exc_info=True)

    @socketio.on('get_unread_count')
    def handle_get_unread_count():
        """Get unread message count for current user"""
        try:
            user_id = session.get('user_id')
            if not user_id:
                return

            from app.models.chat import ChatMessage
            count = ChatMessage.get_unread_count(user_id)
            
            emit('unread_count_update', {
                'count': count,
                'user_id': user_id
            }, room=request.sid)

        except Exception as e:
            logger.error(f"Error getting unread count: {str(e)}", exc_info=True)