"""
Helper utilities for broadcasting chat message notifications.

This centralizes the logic that:
- figures out the other chat participant
- creates database notifications
- emits Socket.IO notification events to the right rooms
"""
from datetime import datetime
from typing import Dict, Optional, Tuple

from app.models.notification import Notification
from app.models.user import User
from app.services.websocket_service import socketio as sio


def _role_from_room(room: Dict, participant_id: Optional[int]) -> Optional[str]:
    """Best-effort lookup of a participant's role based on the hydrated room dict."""
    if not participant_id or not room:
        return None

    participant1_id = room.get('participant1_id') or room.get('user_id')
    participant2_id = room.get('participant2_id')

    if participant_id == participant1_id:
        return (
            room.get('p1_role')
            or room.get('participant1_role')
            or room.get('other_participant_role')
        )

    if participant_id == participant2_id:
        return (
            room.get('p2_role')
            or room.get('participant2_role')
            or room.get('other_participant_role')
        )

    return None


def _resolve_other_participant(room: Dict, sender_id: int) -> Tuple[Optional[int], Optional[str]]:
    """Return the other participant's id & role based on the stored room data."""
    if not room:
        return (None, None)

    participant1_id = room.get('participant1_id') or room.get('user_id')
    participant2_id = room.get('participant2_id')

    other_id = None
    if sender_id == participant1_id and participant2_id:
        other_id = participant2_id
    elif sender_id == participant2_id and participant1_id:
        other_id = participant1_id
    else:
        # Sender might be an admin/support member that's not stored as a participant.
        if participant1_id and participant1_id != sender_id:
            other_id = participant1_id
        elif participant2_id and participant2_id != sender_id:
            other_id = participant2_id

    other_role = _role_from_room(room, other_id)
    if other_id and not other_role:
        other_user = User.get_by_id(other_id)
        other_role = other_user.get('role') if other_user else None

    return (other_id, other_role)


def notify_new_chat_message(
    room: Dict,
    sender_id: int,
    sender_name: str,
    message_text: str,
    timestamp: Optional[str] = None
) -> None:
    """
    Create Notification rows and emit Socket.IO events for chat messages.

    Args:
        room: Chat room dict (result of ChatRoom.get_by_id).
        sender_id: ID of the user who sent the message.
        sender_name: Friendly display name of the sender.
        message_text: Message body (will be truncated for notifications).
        timestamp: ISO timestamp string; defaults to now().
    """
    if not room:
        return

    message_preview = (message_text or '').strip()
    if len(message_preview) > 120:
        message_preview = f"{message_preview[:117]}..."
    timestamp = timestamp or datetime.utcnow().isoformat()

    other_id, other_role = _resolve_other_participant(room, sender_id)

    if other_id:
        Notification.create(
            other_id,
            (other_role or 'user'),
            'message',
            f'New message from {sender_name}',
            message_preview,
            related_id=room.get('id'),
            data={'room_id': room.get('id'), 'from_user_id': sender_id}
        )

        sio.emit(
            'notification',
            {
                'type': 'message',
                'title': f'New message from {sender_name}',
                'message': message_preview,
                'room_id': room.get('id'),
                'timestamp': timestamp
            },
            room=f'user_{other_id}'
        )

    # Always ping admins for customer-admin/support rooms.
    if room.get('conversation_type') == 'customer_admin':
        admins = User.get_all_users(role='admin') or []
        for admin in admins:
            admin_id = admin.get('id')
            if not admin_id or admin_id == sender_id:
                continue

            Notification.create(
                admin_id,
                'admin',
                'message',
                'New support message',
                f'{sender_name}: {message_preview}',
                related_id=room.get('id'),
                data={'room_id': room.get('id'), 'from_user_id': sender_id}
            )

            sio.emit(
                'notification',
                {
                    'type': 'message',
                    'title': 'New support message',
                    'message': f'{sender_name}: {message_preview}',
                    'room_id': room.get('id'),
                    'timestamp': timestamp
                },
                room=f'user_{admin_id}'
            )

