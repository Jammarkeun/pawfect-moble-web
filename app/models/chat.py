from app.services.database import Database
from datetime import datetime
import uuid

class ChatRoom:
    """ChatRoom model using Supabase"""
    TABLE_NAME = 'chat_rooms'

    @classmethod
    def get_or_create_room(cls, participant1_id, participant2_id, order_id=None):
        db = Database()
        # Look for existing room between these participants
        try:
            rooms = db.client.table(cls.TABLE_NAME).select('*') \
                .or_(f'participant1_id.eq.{participant1_id},participant2_id.eq.{participant1_id}') \
                .execute()
            for room in (rooms.data or []):
                participants = {room.get('participant1_id'), room.get('participant2_id')}
                if participant2_id in participants:
                    return room
        except Exception:
            pass

        # Create new room
        room_data = {
            'id': str(uuid.uuid4())[:8],
            'participant1_id': participant1_id,
            'participant2_id': participant2_id,
            'order_id': order_id,
            'created_at': datetime.utcnow().isoformat()
        }
        return db.insert(cls.TABLE_NAME, room_data)

    @classmethod
    def get_room(cls, room_id):
        db = Database()
        return db.select_one(cls.TABLE_NAME, filters={'id': room_id})

    @classmethod
    def get_user_rooms(cls, user_id, role):
        db = Database()
        try:
            rooms = db.client.table(cls.TABLE_NAME).select('*') \
                .or_(f'participant1_id.eq.{user_id},participant2_id.eq.{user_id}') \
                .order('created_at', desc=True) \
                .execute()
            result = rooms.data if rooms.data else []
            for room in result:
                other_id = room['participant2_id'] if room['participant1_id'] == user_id else room['participant1_id']
                other = db.select_one('profiles', filters={'id': other_id})
                room['other_user'] = other or {}
                # Get last message
                msgs = db.client.table('chat_messages').select('*').eq('room_id', room['id']).order('created_at', desc=True).limit(1).execute()
                room['last_message'] = msgs.data[0] if msgs.data else None
            return result
        except Exception:
            return []

class ChatMessage:
    """ChatMessage model using Supabase"""
    TABLE_NAME = 'chat_messages'

    @classmethod
    def send_message(cls, room_id, sender_id, message, message_type='text', image_url=None):
        db = Database()
        msg_data = {
            'id': str(uuid.uuid4())[:8],
            'room_id': room_id,
            'sender_id': sender_id,
            'message': message,
            'message_type': message_type,
            'image_url': image_url,
            'created_at': datetime.utcnow().isoformat(),
            'is_read': False
        }
        return db.insert(cls.TABLE_NAME, msg_data)

    @classmethod
    def get_messages(cls, room_id, limit=50, offset=0):
        db = Database()
        try:
            msgs = db.client.table(cls.TABLE_NAME).select('*').eq('room_id', room_id) \
                .order('created_at', desc=False) \
                .range(offset, offset + limit - 1) \
                .execute()
            return msgs.data if msgs.data else []
        except Exception:
            return []

    @classmethod
    def mark_as_read(cls, room_id, user_id):
        db = Database()
        try:
            db.client.table(cls.TABLE_NAME).update({'is_read': True}) \
                .eq('room_id', room_id).neq('sender_id', user_id) \
                .execute()
        except Exception:
            pass
        return True

    @classmethod
    def get_unread_count(cls, user_id, role=None):
        db = Database()
        try:
            rooms = db.client.table('chat_rooms').select('id') \
                .or_(f'participant1_id.eq.{user_id},participant2_id.eq.{user_id}') \
                .execute()
            room_ids = [r['id'] for r in (rooms.data or [])]
            if not room_ids:
                return 0
            count = db.client.table(cls.TABLE_NAME).select('*', count='exact') \
                .in_('room_id', room_ids).eq('is_read', False).neq('sender_id', user_id) \
                .execute()
            return count.count if hasattr(count, 'count') else 0
        except Exception:
            return 0

class Chat:
    """Chat alias using ChatRoom/ChatMessage"""
    @classmethod
    def get_or_create_room(cls, *args, **kwargs):
        return ChatRoom.get_or_create_room(*args, **kwargs)

    @classmethod
    def get_room(cls, room_id):
        return ChatRoom.get_room(room_id)

    @classmethod
    def get_user_rooms(cls, user_id, role):
        return ChatRoom.get_user_rooms(user_id, role)

    @classmethod
    def send_message(cls, *args, **kwargs):
        return ChatMessage.send_message(*args, **kwargs)

    @classmethod
    def get_messages(cls, room_id, limit=50, offset=0):
        return ChatMessage.get_messages(room_id, limit, offset)

    @classmethod
    def mark_as_read(cls, room_id, user_id):
        return ChatMessage.mark_as_read(room_id, user_id)

    @classmethod
    def get_unread_count(cls, user_id, role=None):
        return ChatMessage.get_unread_count(user_id, role)
