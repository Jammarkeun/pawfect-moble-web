"""
Rider WebSocket helper functions.
Note: Actual Socket.IO handlers are registered in app.py to avoid conflicts.
"""
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Store active rider connections
active_riders = {}

def send_pending_orders_to_rider(rider_id):
    """Send all pending orders to a specific rider"""
    # Implementation moved to app.py rider_online handler
    pass

def notify_riders_new_order(order_data):
    """Notify all online riders about a new order"""
    # Implementation moved to where orders are created
    pass
