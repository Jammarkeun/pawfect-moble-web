"""
Create chat tables for live customer support.
Run this script to set up the database tables for the chat system.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.database import Database


def create_chat_tables():
    """Create chat_rooms and chat_messages tables"""
    db = Database()
    
    # Create chat_rooms table
    print("Creating chat_rooms table...")
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS chat_rooms (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            subject VARCHAR(255) NOT NULL DEFAULT 'Support Request',
            status ENUM('active', 'closed', 'archived') NOT NULL DEFAULT 'active',
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_status (status),
            INDEX idx_updated_at (updated_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    print("✓ chat_rooms table created")
    
    # Create chat_messages table
    print("Creating chat_messages table...")
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            room_id INT NOT NULL,
            user_id INT NOT NULL,
            message TEXT NOT NULL,
            is_support TINYINT(1) NOT NULL DEFAULT 0,
            is_read TINYINT(1) NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL,
            FOREIGN KEY (room_id) REFERENCES chat_rooms(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_room_id (room_id),
            INDEX idx_created_at (created_at),
            INDEX idx_is_read (is_read)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    print("✓ chat_messages table created")
    
    print("\n✓ Chat tables created successfully!")


def drop_chat_tables():
    """Drop chat tables (for rollback)"""
    db = Database()
    
    print("Dropping chat tables...")
    db.execute_query("DROP TABLE IF EXISTS chat_messages")
    db.execute_query("DROP TABLE IF EXISTS chat_rooms")
    print("✓ Chat tables dropped")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'drop':
        drop_chat_tables()
    else:
        create_chat_tables()
