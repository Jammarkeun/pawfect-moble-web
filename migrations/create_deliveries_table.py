from app.services.database import Database
def create_deliveries_table():
    db = None
    try:
        db = Database()
        with db.connection.cursor() as cursor:
            # Create deliveries table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS deliveries (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    order_id INT NOT NULL,
                    rider_id INT NOT NULL,
                    status VARCHAR(50) NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                    FOREIGN KEY (rider_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_order_rider (order_id, rider_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            db.connection.commit()
            print("Successfully created 'deliveries' table")
    except Exception as e:
        print(f"Error creating deliveries table: {e}")
        if db and hasattr(db, 'connection'):
            db.connection.rollback()
    finally:
        if db:
            try:
                db.disconnect()
            except:
                pass

if __name__ == "__main__":
    create_deliveries_table()
