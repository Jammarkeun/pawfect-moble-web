import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

def get_db_connection():
    """Create and return a database connection"""
    load_dotenv()
    
    # Get database configuration from environment variables or use defaults
    db_host = os.getenv('DB_HOST', 'localhost')
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    db_name = os.getenv('DB_NAME', 'pawfect_finds')
    
    # Create connection string
    db_uri = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
    engine = create_engine(db_uri)
    return engine

def update_confirmed_orders_status():
    """
    Update orders that have a rider_id but status is still 'confirmed' to 'assigned_to_rider'
    """
    engine = get_db_connection()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Find orders with rider_id but status is 'confirmed'
        query = """
            SELECT id, rider_id, status 
            FROM orders 
            WHERE rider_id IS NOT NULL 
            AND status = 'confirmed'
        """
        
        result = session.execute(text(query))
        orders_to_update = result.fetchall()
        
        if not orders_to_update:
            print("No orders found with rider_id and status 'confirmed'.")
            return
            
        print(f"Found {len(orders_to_update)} orders to update:")
        
        # Update each order
        for order in orders_to_update:
            update_query = """
                UPDATE orders 
                SET status = 'assigned_to_rider' 
                WHERE id = :order_id
            """
            session.execute(text(update_query), {'order_id': order.id})
            print(f"Updated order ID {order.id}: status from 'confirmed' to 'assigned_to_rider'")
        
        # Commit the changes
        session.commit()
        print("\nSuccessfully updated all orders.")
        
    except Exception as e:
        session.rollback()
        print(f"Error updating orders: {str(e)}")
        raise
    finally:
        session.close()

if __name__ == '__main__':
    update_confirmed_orders_status()
