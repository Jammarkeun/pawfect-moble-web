"""
Notification Service
Handles creation and broadcasting of notifications to users
"""
from app.models.models import Notification
from app import db, socketio
import logging

logger = logging.getLogger(__name__)

def create_notification(user_id, title, message, notif_type='general', related_id=None):
    """
    Create a notification in the database and emit it via WebSocket.
    
    Args:
        user_id: ID of the user to notify
        title: Notification title
        message: Notification message
        notif_type: Type of notification (order_status, seller_application, product_review, delivery_update, general)
        related_id: Related ID (order_id, application_id, etc.)
    
    Returns:
        Notification object or None
    """
    try:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notif_type,
            related_id=related_id,
            is_read=False
        )
        
        db.session.add(notification)
        db.session.commit()
        
        logger.info(f"[NOTIF] Created notification for user {user_id}: {title}")
        
        # Emit via WebSocket if available
        emit_notification(user_id, notification)
        
        return notification
    except Exception as e:
        logger.error(f"[NOTIF] Failed to create notification: {str(e)}", exc_info=True)
        db.session.rollback()
        return None

def emit_notification(user_id, notification):
    """
    Emit a notification to a specific user via WebSocket.
    
    Args:
        user_id: ID of the user to send notification to
        notification: Notification object
    """
    try:
        data = {
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.type,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat() if notification.created_at else None,
            'related_id': notification.related_id
        }
        
        # Emit to the user's room
        socketio.emit(
            'notification',
            data,
            room=f'user_{user_id}',
            skip_sid=None
        )
        
        logger.info(f"[NOTIF] Emitted notification to user {user_id}")
    except Exception as e:
        logger.error(f"[NOTIF] Failed to emit notification: {str(e)}", exc_info=True)

def notify_order_status_change(order_id, user_id, status):
    """
    Notify user about order status change.
    
    Args:
        order_id: ID of the order
        user_id: ID of the user to notify
        status: New order status
    """
    status_display = status.replace('_', ' ').title()
    title = 'Order Status Updated'
    message = f'Your order #{order_id} is now {status_display}'
    
    return create_notification(
        user_id=user_id,
        title=title,
        message=message,
        notif_type='order_status',
        related_id=order_id
    )

def notify_seller_application_status(application_id, user_id, status):
    """
    Notify user about seller application status.
    
    Args:
        application_id: ID of the application
        user_id: ID of the user to notify
        status: Application status (approved, rejected, pending)
    """
    status_display = status.replace('_', ' ').title()
    title = 'Application Status Updated'
    message = f'Your seller application has been {status_display}'
    
    return create_notification(
        user_id=user_id,
        title=title,
        message=message,
        notif_type='seller_application',
        related_id=application_id
    )

def notify_product_review(order_item_id, user_id, reviewer_name):
    """
    Notify user about a new product review.
    
    Args:
        order_item_id: ID of the order item reviewed
        user_id: ID of the user to notify
        reviewer_name: Name of the reviewer
    """
    title = 'New Product Review'
    message = f'{reviewer_name} has reviewed your product'
    
    return create_notification(
        user_id=user_id,
        title=title,
        message=message,
        notif_type='product_review',
        related_id=order_item_id
    )

def notify_delivery_update(order_id, user_id, update_message):
    """
    Notify user about delivery update.
    
    Args:
        order_id: ID of the order
        user_id: ID of the user to notify
        update_message: Specific delivery update message
    """
    title = 'Delivery Update'
    message = update_message
    
    return create_notification(
        user_id=user_id,
        title=title,
        message=message,
        notif_type='delivery_update',
        related_id=order_id
    )

def get_user_notifications(user_id, limit=10, unread_only=False):
    """
    Get notifications for a specific user.
    
    Args:
        user_id: ID of the user
        limit: Number of notifications to return
        unread_only: If True, return only unread notifications
    
    Returns:
        List of notifications
    """
    try:
        query = Notification.query.filter_by(user_id=user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
        return notifications
    except Exception as e:
        logger.error(f"[NOTIF] Failed to get notifications: {str(e)}", exc_info=True)
        return []

def get_unread_count(user_id):
    """
    Get count of unread notifications for a user.
    
    Args:
        user_id: ID of the user
    
    Returns:
        Number of unread notifications
    """
    try:
        count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
        return count
    except Exception as e:
        logger.error(f"[NOTIF] Failed to get unread count: {str(e)}", exc_info=True)
        return 0

def mark_as_read(notification_id, user_id):
    """
    Mark a notification as read.
    
    Args:
        notification_id: ID of the notification
        user_id: ID of the user
    
    Returns:
        True if successful, False otherwise
    """
    try:
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=user_id
        ).first()
        
        if notification:
            notification.is_read = True
            db.session.commit()
            logger.info(f"[NOTIF] Marked notification {notification_id} as read")
            return True
        
        return False
    except Exception as e:
        logger.error(f"[NOTIF] Failed to mark notification as read: {str(e)}", exc_info=True)
        db.session.rollback()
        return False

def mark_all_as_read(user_id):
    """
    Mark all notifications as read for a user.
    
    Args:
        user_id: ID of the user
    
    Returns:
        True if successful, False otherwise
    """
    try:
        Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()
        logger.info(f"[NOTIF] Marked all notifications as read for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"[NOTIF] Failed to mark all notifications as read: {str(e)}", exc_info=True)
        db.session.rollback()
        return False

def delete_notification(notification_id, user_id):
    """
    Delete a notification.
    
    Args:
        notification_id: ID of the notification
        user_id: ID of the user
    
    Returns:
        True if successful, False otherwise
    """
    try:
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=user_id
        ).first()
        
        if notification:
            db.session.delete(notification)
            db.session.commit()
            logger.info(f"[NOTIF] Deleted notification {notification_id}")
            return True
        
        return False
    except Exception as e:
        logger.error(f"[NOTIF] Failed to delete notification: {str(e)}", exc_info=True)
        db.session.rollback()
        return False
